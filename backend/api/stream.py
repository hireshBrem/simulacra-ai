"""
SSE streaming endpoints — yield simulation events in real-time as LLM calls complete.
Each event is a JSON-encoded SimEvent delivered as a text/event-stream.
"""
import asyncio
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from agents.loader import load_all_agents
from agents.memory import append_memory
from agents.runner import run_agent_action, run_conversation_turn, generate_memory_reflection
from simulation.participants import select_encounter_agents
from simulation.experiments import (
    VALID_RESPONSE_MODES,
    build_agent_scenario_response,
    default_behavioral_scenario,
    delivery_app_experience_lookup,
    save_behavioral_scenario_log,
    summarize_behavioral_scenario,
)
from simulation.step import iter_simulation_step_events
from simulation.world import get_preset_event, generate_world_event

router = APIRouter()

_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def _world_event_stream(event_text: str | None, use_llm_event: bool):
    date = datetime.now().strftime("%Y-%m-%d")

    if event_text is None:
        if use_llm_event:
            event_text = await asyncio.to_thread(generate_world_event, date=date)
        else:
            event_text = get_preset_event()

    yield _event({"type": "world_event", "content": event_text})

    agents = load_all_agents()
    for agent in agents:
        yield _event({"type": "agent_thinking", "agent_id": agent.agent_id, "agent_name": agent.name})

        action = await asyncio.to_thread(run_agent_action, agent, event_text, date)

        yield _event({"type": "agent_action", "agent_id": agent.agent_id, "agent_name": agent.name, **action})

        if action.get("memory_entry"):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            await asyncio.to_thread(append_memory, agent.agent_id, action["memory_entry"], ts)
            yield _event({
                "type": "memory_saved",
                "agent_id": agent.agent_id,
                "agent_name": agent.name,
                "entry": action["memory_entry"]
            })

    yield _event({"type": "done"})


async def _encounter_stream(topic: str | None, exchanges: int, agent_ids: list[str] | None):
    date = datetime.now().strftime("%Y-%m-%d")
    agents = load_all_agents()

    try:
        agent1, agent2 = select_encounter_agents(agents, agent_ids)
    except ValueError as e:
        yield _event({"type": "error", "message": str(e)})
        return

    if topic is None:
        topic = await asyncio.to_thread(generate_world_event, date=date)

    situation = f"{agent1.name} and {agent2.name} are on a call. Topic: {topic}"

    yield _event({
        "type": "encounter_start",
        "topic": topic,
        "participants": [
            {"agent_id": agent1.agent_id, "name": agent1.name},
            {"agent_id": agent2.agent_id, "name": agent2.name},
        ]
    })

    history: list[dict] = []
    for i in range(exchanges):
        speaker = agent1 if i % 2 == 0 else agent2
        listener = agent2 if i % 2 == 0 else agent1

        result = await asyncio.to_thread(
            run_conversation_turn, speaker, listener.name, situation, history, date
        )

        yield _event({
            "type": "agent_utterance",
            "exchange": i + 1,
            "speaker_id": speaker.agent_id,
            "speaker_name": speaker.name,
            "internal_state": result.get("internal_state", ""),
            "utterance": result.get("utterance", ""),
        })

        history.append({"speaker": speaker.name, "utterance": result.get("utterance", "")})

    # Each agent writes their own memory entry
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    for agent in [agent1, agent2]:
        other = agent2 if agent == agent1 else agent1
        summary = (
            f"Had a call with {other.name} about: {topic}. "
            f"Last thing said: {history[-1]['utterance'][:120]}..."
        )
        memory_entry = await asyncio.to_thread(generate_memory_reflection, agent, summary, date)
        await asyncio.to_thread(append_memory, agent.agent_id, memory_entry, ts)
        yield _event({
            "type": "memory_saved",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "entry": memory_entry,
        })

    yield _event({"type": "done"})


async def _simulation_stream(
    tick_seconds: float,
    event_delay: float,
    max_ticks: int,
    max_agents: int,
    tick_minutes: int,
    use_llm: bool,
):
    yield _event({"type": "simulation_started"})
    ticks_run = 0

    try:
        while max_ticks <= 0 or ticks_run < max_ticks:
            for event in iter_simulation_step_events(
                max_agents=max_agents,
                tick_minutes=tick_minutes,
                use_llm=use_llm,
            ):
                yield _event(event)
                await asyncio.sleep(max(0.0, event_delay))
            ticks_run += 1

            if max_ticks > 0 and ticks_run >= max_ticks:
                break
            await asyncio.sleep(max(0.1, tick_seconds))
    except asyncio.CancelledError:
        raise
    except Exception as e:
        yield _event({"type": "error", "message": str(e)})
        return

    yield _event({"type": "simulation_stopped", "ticks_run": ticks_run})
    yield _event({"type": "done"})


async def _behavioral_scenario_stream(
    title: str | None,
    prompt: str | None,
    response_mode: str,
    use_delivery_app_experiences: bool,
):
    if response_mode not in VALID_RESPONSE_MODES:
        yield _event({"type": "error", "message": f"Unsupported response_mode: {response_mode}"})
        return

    scenario = default_behavioral_scenario()
    title = title or scenario["title"]
    prompt = prompt or scenario["prompt"]
    date = datetime.now().strftime("%Y-%m-%d")
    experiment_id = str(uuid.uuid4())[:8]
    experience_lookup = delivery_app_experience_lookup(use_delivery_app_experiences)

    yield _event({
        "type": "behavioral_scenario_started",
        "experiment_id": experiment_id,
        "title": title,
        "prompt": prompt,
        "response_mode": response_mode,
        "use_delivery_app_experiences": use_delivery_app_experiences,
    })

    responses: list[dict] = []
    try:
        for agent in load_all_agents():
            response = await asyncio.to_thread(
                build_agent_scenario_response,
                agent,
                prompt,
                response_mode,
                date,
                experience_lookup.get(agent.agent_id, []),
            )
            responses.append(response)
            yield _event({
                "type": "behavioral_agent_response",
                "experiment_id": experiment_id,
                **response,
            })

        summary = summarize_behavioral_scenario(responses, response_mode)
        result = {
            "experiment_id": experiment_id,
            "type": "behavioral_scenario",
            "date": date,
            "title": title,
            "prompt": prompt,
            "response_mode": response_mode,
            "use_delivery_app_experiences": use_delivery_app_experiences,
            "responses": responses,
            "summary": summary,
        }
        await asyncio.to_thread(save_behavioral_scenario_log, result)
        yield _event({
            "type": "behavioral_scenario_summary",
            "experiment_id": experiment_id,
            "summary": summary,
        })
    except Exception as e:
        yield _event({"type": "error", "message": str(e)})
        return

    yield _event({"type": "done"})


@router.get("/stream/world-event")
async def stream_world_event(event: str | None = None, use_llm_event: bool = False):
    return StreamingResponse(
        _world_event_stream(event, use_llm_event),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )


@router.get("/stream/encounter")
async def stream_encounter(
    topic: str | None = None,
    exchanges: int = 4,
    agent_ids: list[str] | None = Query(default=None),
):
    return StreamingResponse(
        _encounter_stream(topic, exchanges, agent_ids),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )


@router.get("/stream/experiments/behavioral-scenarios")
async def stream_behavioral_scenario(
    title: str | None = None,
    prompt: str | None = None,
    response_mode: str = "yes_no_reason",
    use_delivery_app_experiences: bool = False,
):
    return StreamingResponse(
        _behavioral_scenario_stream(title, prompt, response_mode, use_delivery_app_experiences),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )


@router.get("/stream/simulation")
async def stream_simulation(
    tick_seconds: float = 2.0,
    event_delay: float = 4.0,
    max_ticks: int = 0,
    max_agents: int = 0,
    tick_minutes: int = 5,
    use_llm: bool = True,
):
    return StreamingResponse(
        _simulation_stream(tick_seconds, event_delay, max_ticks, max_agents, tick_minutes, use_llm),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )
