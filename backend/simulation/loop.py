"""
Simulation Model — orchestrates agent turns, encounters, and conversations.
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from agents.loader import load_all_agents
from agents.memory import append_memory
from agents.runner import run_agent_action, run_conversation_turn, generate_memory_reflection
from simulation.participants import select_encounter_agents
from simulation.world import get_preset_event, generate_world_event

SIM_LOGS_PATH = Path(os.getenv("SIM_LOGS_PATH", "../sim-logs"))


def _save_log(data: dict) -> None:
    SIM_LOGS_PATH.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{ts}_{data['type']}_{data['turn_id']}.json"
    (SIM_LOGS_PATH / filename).write_text(json.dumps(data, indent=2))


def run_world_event_turn(event: str | None = None, use_llm_event: bool = False) -> dict:
    """
    Each agent independently reacts to a shared world event.
    No direct interaction — parallel solo responses.
    """
    date = datetime.now().strftime("%Y-%m-%d")

    if event is None:
        event = generate_world_event(date=date) if use_llm_event else get_preset_event()

    agents = load_all_agents()
    turn_id = str(uuid.uuid4())[:8]
    agent_actions = []

    for agent in agents:
        action = run_agent_action(agent, event, date)

        if action.get("memory_entry"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            append_memory(agent.agent_id, action["memory_entry"], timestamp)

        agent_actions.append({
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            **action
        })

    result = {
        "turn_id": turn_id,
        "type": "world_event",
        "date": date,
        "world_event": event,
        "agent_actions": agent_actions
    }
    _save_log(result)
    return result


def run_encounter(
    topic: str | None = None,
    exchanges: int = 4,
    agent_ids: list[str] | None = None,
) -> dict:
    """
    Two agents encounter each other and hold a Conversation.
    Exchanges alternate speaker turns; both agents update their Memory Streams.
    """
    date = datetime.now().strftime("%Y-%m-%d")
    agents = load_all_agents()

    agent1, agent2 = select_encounter_agents(agents, agent_ids)

    if topic is None:
        topic = generate_world_event(date=date)

    situation = (
        f"{agent1.name} and {agent2.name} have ended up on a call together. "
        f"The topic at hand: {topic}"
    )

    history: list[dict] = []
    conversation: list[dict] = []

    for i in range(exchanges):
        speaker = agent1 if i % 2 == 0 else agent2
        listener = agent2 if i % 2 == 0 else agent1

        result = run_conversation_turn(speaker, listener.name, situation, history, date)

        turn = {
            "exchange": i + 1,
            "speaker_id": speaker.agent_id,
            "speaker_name": speaker.name,
            "internal_state": result.get("internal_state", ""),
            "utterance": result.get("utterance", "")
        }
        conversation.append(turn)
        history.append({"speaker": speaker.name, "utterance": result.get("utterance", "")})

    # Each agent writes their own Memory Stream entry about the encounter
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    memories = {}
    for agent in [agent1, agent2]:
        other = agent2 if agent == agent1 else agent1
        exchange_summary = (
            f"Had a call with {other.name} about: {topic}. "
            f"Key exchange: {conversation[-1]['utterance'][:100]}..."
        )
        memory_entry = generate_memory_reflection(agent, exchange_summary, date)
        append_memory(agent.agent_id, memory_entry, timestamp)
        memories[agent.agent_id] = memory_entry

    result = {
        "turn_id": str(uuid.uuid4())[:8],
        "type": "encounter",
        "date": date,
        "topic": topic,
        "participants": [
            {"agent_id": agent1.agent_id, "name": agent1.name},
            {"agent_id": agent2.agent_id, "name": agent2.name}
        ],
        "conversation": conversation,
        "memory_entries": memories
    }
    _save_log(result)
    return result


def get_simulation_log(limit: int = 20) -> list[dict]:
    """Return recent simulation turns from saved log files."""
    SIM_LOGS_PATH.mkdir(parents=True, exist_ok=True)
    files = sorted(SIM_LOGS_PATH.glob("*.json"), reverse=True)[:limit]
    logs = []
    for f in files:
        try:
            logs.append(json.loads(f.read_text()))
        except Exception:
            pass
    return logs
