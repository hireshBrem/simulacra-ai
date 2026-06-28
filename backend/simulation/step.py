"""
Step-based Simulation Model.
"""
import os
import uuid
from datetime import timedelta

from agents.loader import load_agent
from agents.memory import append_memory
from agents.runner import (
    generate_memory_reflection,
    run_conversation_turn,
    run_simulation_decision,
)
from simulation.perception import perceive_agent, perception_summary
from simulation.retrieval import memories_text, retrieve_memories
from simulation.state import (
    ZONES,
    default_activity_for_zone,
    format_sim_time,
    load_state,
    parse_sim_time,
    save_state,
)


def simulation_step(max_agents: int = 4, tick_minutes: int = 5, use_llm: bool = True) -> dict:
    """
    Advance the persistent SF simulation by one tick.
    """
    state = load_state()
    state["tick_minutes"] = tick_minutes

    current_time = parse_sim_time(state["current_time"]) + timedelta(minutes=tick_minutes)
    state["current_time"] = format_sim_time(current_time)
    state["step_number"] += 1

    events: list[dict] = [{
        "type": "tick_started",
        "step": state["step_number"],
        "current_time": state["current_time"],
    }]

    events.extend(_advance_encounters(state, use_llm=use_llm))

    for agent_state in _select_active_agents(state, max_agents):
        if agent_state.get("active_encounter_id"):
            continue

        perception = perceive_agent(agent_state, state)
        query = perception_summary(perception)
        relevant_memories = retrieve_memories(agent_state["agent_id"], query, limit=5)
        memory_context = memories_text(relevant_memories)

        events.append({
            "type": "agent_observed",
            "agent_id": agent_state["agent_id"],
            "agent_name": agent_state["name"],
            "zone": agent_state["zone"],
            "summary": query,
        })

        decision = _decide(agent_state, perception, query, memory_context, use_llm)
        events.append({
            "type": "agent_planned",
            "agent_id": agent_state["agent_id"],
            "agent_name": agent_state["name"],
            "action_type": decision["action_type"],
            "inner_monologue": decision.get("inner_monologue", ""),
            "public_action": decision.get("public_action", ""),
            "emotional_state": decision.get("emotional_state", "neutral"),
        })

        events.extend(_execute_decision(state, agent_state, decision))
        agent_state["last_active_step"] = state["step_number"]

    save_state(state)
    events.append({
        "type": "tick_done",
        "step": state["step_number"],
        "current_time": state["current_time"],
    })
    return {"state": state, "events": events}


def run_simulation_steps(steps: int = 1, max_agents: int = 4, tick_minutes: int = 5, use_llm: bool = True) -> dict:
    all_events: list[dict] = []
    result = {}
    for _ in range(max(1, steps)):
        result = simulation_step(max_agents=max_agents, tick_minutes=tick_minutes, use_llm=use_llm)
        all_events.extend(result["events"])
    return {"state": result["state"], "events": all_events}


def _select_active_agents(state: dict, max_agents: int) -> list[dict]:
    agents = sorted(state["agents"].values(), key=lambda a: _agent_sort_key(a["agent_id"]))
    if not agents:
        return []
    max_agents = max(1, min(max_agents, len(agents)))
    start = state["step_number"] % len(agents)
    rotated = agents[start:] + agents[:start]
    return rotated[:max_agents]


def _agent_sort_key(agent_id: str) -> tuple[int, str]:
    suffix = agent_id.removeprefix("agent-")
    return (int(suffix), agent_id) if suffix.isdigit() else (10**9, agent_id)


def _decide(agent_state: dict, perception: dict, query: str, memory_context: str, use_llm: bool) -> dict:
    if use_llm and os.getenv("GROQ_API_KEY"):
        try:
            agent = load_agent(agent_state["agent_id"])
            decision = run_simulation_decision(
                agent=agent,
                perception=query,
                relevant_memories=memory_context,
                valid_zones=list(ZONES.keys()),
                nearby_agents=perception["nearby_agents"],
                date=perception["current_time"].split()[0],
            )
            return _normalize_decision(agent_state, decision)
        except Exception:
            pass

    return _fallback_decision(agent_state, perception)


def _normalize_decision(agent_state: dict, decision: dict) -> dict:
    action_type = decision.get("action_type", "continue_routine")
    if action_type not in {"continue_routine", "move", "observe", "start_conversation", "reflect"}:
        action_type = "continue_routine"

    target_zone = decision.get("target_zone") or agent_state["zone"]
    if target_zone not in ZONES:
        target_zone = agent_state["zone"]

    return {
        "action_type": action_type,
        "target_zone": target_zone,
        "target_agent_id": decision.get("target_agent_id", ""),
        "public_action": decision.get("public_action", agent_state.get("current_activity", "")),
        "inner_monologue": decision.get("inner_monologue", ""),
        "emotional_state": decision.get("emotional_state", "neutral"),
        "memory_entry": decision.get("memory_entry", ""),
    }


def _fallback_decision(agent_state: dict, perception: dict) -> dict:
    step = perception["step_number"]
    nearby = perception["nearby_agents"]
    if nearby and step % 4 == 0:
        target = sorted(nearby, key=lambda a: _agent_sort_key(a["agent_id"]))[0]
        return {
            "action_type": "start_conversation",
            "target_zone": agent_state["zone"],
            "target_agent_id": target["agent_id"],
            "public_action": f"{agent_state['name']} starts a grounded conversation with {target['name']} about what is happening nearby.",
            "inner_monologue": "It is worth checking in while we are in the same place.",
            "emotional_state": "curious",
            "memory_entry": "",
        }

    hour = parse_sim_time(perception["current_time"]).hour
    target_zone = _routine_zone(agent_state, hour)
    if target_zone != agent_state["zone"]:
        return {
            "action_type": "move",
            "target_zone": target_zone,
            "target_agent_id": "",
            "public_action": default_activity_for_zone(target_zone, hour),
            "inner_monologue": "The next part of the day pulls me somewhere else.",
            "emotional_state": "focused",
            "memory_entry": "",
        }

    if step % 7 == 0:
        return {
            "action_type": "reflect",
            "target_zone": agent_state["zone"],
            "target_agent_id": "",
            "public_action": f"{agent_state['name']} pauses and thinks through the day so far.",
            "inner_monologue": "I should make sense of the pattern of the day before moving on.",
            "emotional_state": "reflective",
            "memory_entry": f"I paused in {agent_state['zone']} and thought about how my day was unfolding around my work, commute, and neighborhood obligations.",
        }

    return {
        "action_type": "observe",
        "target_zone": agent_state["zone"],
        "target_agent_id": "",
        "public_action": agent_state.get("current_activity") or default_activity_for_zone(agent_state["zone"], hour),
        "inner_monologue": "I am taking in what is happening around me.",
        "emotional_state": agent_state.get("current_mood", "neutral"),
        "memory_entry": "",
    }


def _routine_zone(agent_state: dict, hour: int) -> str:
    if hour < 8:
        return agent_state["home_zone"]
    if hour == 8 or hour == 17:
        return "transit_commons"
    if 9 <= hour < 17:
        suffix = _agent_sort_key(agent_state["agent_id"])[0]
        work_zones = ["neighborhood_work", "civic_market", "service_corridor"]
        return work_zones[suffix % len(work_zones)]
    return agent_state["home_zone"]


def _execute_decision(state: dict, agent_state: dict, decision: dict) -> list[dict]:
    action_type = decision["action_type"]
    agent_state["current_mood"] = decision.get("emotional_state", "neutral")
    events: list[dict] = []

    if action_type == "move":
        old_zone = agent_state["zone"]
        new_zone = decision["target_zone"]
        agent_state["zone"] = new_zone
        agent_state["current_activity"] = decision.get("public_action") or default_activity_for_zone(new_zone)
        events.append({
            "type": "agent_moved",
            "agent_id": agent_state["agent_id"],
            "agent_name": agent_state["name"],
            "from_zone": old_zone,
            "to_zone": new_zone,
            "activity": agent_state["current_activity"],
            "emotional_state": agent_state["current_mood"],
        })
    elif action_type == "start_conversation":
        events.extend(_start_encounter(state, agent_state, decision))
    elif action_type == "reflect":
        entry = decision.get("memory_entry") or (
            f"I reflected on being in {agent_state['zone']} while {agent_state.get('current_activity', 'moving through the day')}."
        )
        append_memory(agent_state["agent_id"], entry, state["current_time"])
        events.append({
            "type": "reflection_saved",
            "agent_id": agent_state["agent_id"],
            "agent_name": agent_state["name"],
            "entry": entry,
        })
    else:
        agent_state["current_activity"] = decision.get("public_action") or agent_state.get("current_activity", "")
        if action_type == "observe" and decision.get("memory_entry"):
            append_memory(agent_state["agent_id"], decision["memory_entry"], state["current_time"])
            events.append({
                "type": "memory_saved",
                "agent_id": agent_state["agent_id"],
                "agent_name": agent_state["name"],
                "entry": decision["memory_entry"],
            })

    return events


def _start_encounter(state: dict, agent_state: dict, decision: dict) -> list[dict]:
    target_id = decision.get("target_agent_id", "")
    target = state["agents"].get(target_id)
    if not target:
        return []
    if target.get("zone") != agent_state.get("zone"):
        return []
    if target.get("active_encounter_id") or agent_state.get("active_encounter_id"):
        return []

    encounter_id = str(uuid.uuid4())[:8]
    participant_ids = [agent_state["agent_id"], target_id]
    topic = decision.get("public_action") or f"{agent_state['name']} and {target['name']} cross paths in {agent_state['zone']}."
    state["active_encounters"][encounter_id] = {
        "encounter_id": encounter_id,
        "participant_ids": participant_ids,
        "participant_names": [agent_state["name"], target["name"]],
        "zone": agent_state["zone"],
        "topic": topic,
        "exchange": 0,
        "max_exchanges": 4,
        "history": [],
        "started_step": state["step_number"],
    }
    for participant_id in participant_ids:
        state["agents"][participant_id]["active_encounter_id"] = encounter_id

    return [{
        "type": "encounter_start",
        "encounter_id": encounter_id,
        "topic": topic,
        "zone": agent_state["zone"],
        "participants": [
            {"agent_id": agent_state["agent_id"], "name": agent_state["name"]},
            {"agent_id": target["agent_id"], "name": target["name"]},
        ],
    }]


def _advance_encounters(state: dict, use_llm: bool) -> list[dict]:
    events: list[dict] = []
    for encounter_id, encounter in list(state["active_encounters"].items()):
        if encounter["exchange"] >= encounter["max_exchanges"]:
            events.extend(_end_encounter(state, encounter_id))
            continue

        speaker_id = encounter["participant_ids"][encounter["exchange"] % len(encounter["participant_ids"])]
        listener_id = next(pid for pid in encounter["participant_ids"] if pid != speaker_id)
        speaker_state = state["agents"][speaker_id]
        listener_state = state["agents"][listener_id]

        result = _conversation_turn(speaker_state, listener_state, encounter, state, use_llm)
        utterance = result.get("utterance", "")
        internal_state = result.get("internal_state", "")
        encounter["exchange"] += 1
        encounter["history"].append({"speaker": speaker_state["name"], "utterance": utterance})

        events.append({
            "type": "agent_utterance",
            "encounter_id": encounter_id,
            "exchange": encounter["exchange"],
            "speaker_id": speaker_id,
            "speaker_name": speaker_state["name"],
            "internal_state": internal_state,
            "utterance": utterance,
        })

        if encounter["exchange"] >= encounter["max_exchanges"]:
            events.extend(_end_encounter(state, encounter_id))

    return events


def _conversation_turn(speaker_state: dict, listener_state: dict, encounter: dict, state: dict, use_llm: bool) -> dict:
    if use_llm and os.getenv("GROQ_API_KEY"):
        try:
            speaker = load_agent(speaker_state["agent_id"])
            situation = f"{speaker_state['name']} and {listener_state['name']} are talking in {encounter['zone']}. Topic: {encounter['topic']}"
            return run_conversation_turn(
                speaker=speaker,
                listener_name=listener_state["name"],
                situation=situation,
                history=encounter["history"],
                date=state["current_time"].split()[0],
            )
        except Exception:
            pass

    if encounter["history"]:
        utterance = f"That makes sense. From where I am in the city, I see it through my own work and neighborhood routines."
    else:
        utterance = f"I noticed you here and wanted to ask how this is landing for you today."
    return {
        "internal_state": "I want to keep the conversation grounded and brief.",
        "utterance": utterance,
    }


def _end_encounter(state: dict, encounter_id: str) -> list[dict]:
    encounter = state["active_encounters"].pop(encounter_id, None)
    if not encounter:
        return []

    events: list[dict] = []
    transcript = "\n".join(f"{row['speaker']}: {row['utterance']}" for row in encounter["history"])
    for participant_id in encounter["participant_ids"]:
        participant = state["agents"][participant_id]
        participant["active_encounter_id"] = None
        other_names = [name for name in encounter["participant_names"] if name != participant["name"]]
        summary = f"Had a conversation with {', '.join(other_names)} in {encounter['zone']}. Topic: {encounter['topic']}. {transcript[-300:]}"
        entry = _memory_after_encounter(participant_id, summary, state["current_time"])
        events.append({
            "type": "memory_saved",
            "agent_id": participant_id,
            "agent_name": participant["name"],
            "entry": entry,
        })

    events.append({
        "type": "encounter_end",
        "encounter_id": encounter_id,
        "participants": [
            {"agent_id": pid, "name": state["agents"][pid]["name"]}
            for pid in encounter["participant_ids"]
        ],
    })
    return events


def _memory_after_encounter(agent_id: str, summary: str, timestamp: str) -> str:
    if os.getenv("GROQ_API_KEY"):
        try:
            entry = generate_memory_reflection(load_agent(agent_id), summary, timestamp.split()[0])
            append_memory(agent_id, entry, timestamp)
            return entry
        except Exception:
            pass

    entry = summary
    append_memory(agent_id, entry, timestamp)
    return entry
