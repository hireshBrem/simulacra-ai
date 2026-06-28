"""
Perception helpers for the SF Social Space.
"""
from simulation.state import ZONES


def perceive_agent(agent_state: dict, state: dict) -> dict:
    zone = agent_state["zone"]
    nearby_agents = [
        {
            "agent_id": other["agent_id"],
            "name": other["name"],
            "current_activity": other.get("current_activity", ""),
            "current_mood": other.get("current_mood", "neutral"),
        }
        for other in state["agents"].values()
        if other["agent_id"] != agent_state["agent_id"]
        and other.get("zone") == zone
    ]

    return {
        "zone": zone,
        "zone_description": ZONES.get(zone, zone),
        "nearby_agents": nearby_agents,
        "current_activity": agent_state.get("current_activity", ""),
        "current_mood": agent_state.get("current_mood", "neutral"),
        "recent_world_events": state.get("recent_world_events", [])[-3:],
        "current_time": state["current_time"],
        "step_number": state["step_number"],
    }


def perception_summary(perception: dict) -> str:
    nearby = ", ".join(a["name"] for a in perception["nearby_agents"]) or "no one nearby"
    events = "; ".join(e["content"] for e in perception["recent_world_events"]) or "no recent city-wide event"
    return (
        f"Time: {perception['current_time']}. "
        f"Place: {perception['zone']} ({perception['zone_description']}). "
        f"Current activity: {perception['current_activity']}. "
        f"Nearby: {nearby}. "
        f"Recent world context: {events}."
    )
