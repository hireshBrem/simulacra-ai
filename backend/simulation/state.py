"""
Persistent state for the step-based Simulation Model.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from agents.loader import load_all_agents

SIM_DATA_PATH = Path(os.getenv("SIM_DATA_PATH", "../sim-data"))
STATE_PATH = Path(os.getenv("SIM_STATE_PATH", SIM_DATA_PATH / "SIM_STATE.json"))

TIME_FORMAT = "%Y-%m-%d %H:%M"

ZONES = {
    "west_side": "West Side homes and neighborhood routines",
    "north_side": "North Side streets, errands, and civic life",
    "civic_market": "Civic Center and Market Street public life",
    "neighborhood_work": "Mission and neighborhood workplaces",
    "transit_commons": "shared transit and commute spaces",
    "southeast": "Southeast San Francisco homes and services",
    "service_corridor": "Tenderloin and service corridor work",
}

AGENT_HOME_ZONES = {
    "agent-1": "west_side",
    "agent-2": "southeast",
    "agent-3": "civic_market",
    "agent-4": "north_side",
    "agent-5": "civic_market",
    "agent-6": "civic_market",
    "agent-7": "west_side",
    "agent-8": "southeast",
    "agent-9": "neighborhood_work",
    "agent-10": "north_side",
    "agent-11": "west_side",
    "agent-12": "southeast",
    "agent-13": "civic_market",
    "agent-14": "southeast",
    "agent-15": "neighborhood_work",
    "agent-16": "west_side",
    "agent-17": "north_side",
    "agent-18": "southeast",
    "agent-19": "service_corridor",
    "agent-20": "west_side",
    "agent-21": "civic_market",
    "agent-22": "neighborhood_work",
    "agent-23": "west_side",
    "agent-24": "southeast",
    "agent-25": "west_side",
    "agent-26": "neighborhood_work",
    "agent-27": "north_side",
    "agent-28": "southeast",
    "agent-29": "civic_market",
    "agent-30": "neighborhood_work",
}


def now_sim_time() -> str:
    return datetime.now().replace(second=0, microsecond=0).strftime(TIME_FORMAT)


def default_activity_for_zone(zone: str, hour: int = 8) -> str:
    if hour < 6:
        return "sleeping at home"
    if hour < 9:
        return "starting the day"
    if hour < 17:
        if zone in {"neighborhood_work", "service_corridor", "civic_market"}:
            return "working through daily obligations"
        return "handling errands and household responsibilities"
    if hour < 21:
        return "winding down after the day"
    return "settling in for the night"


def build_initial_state() -> dict:
    agents = load_all_agents()
    current_time = now_sim_time()
    hour = datetime.strptime(current_time, TIME_FORMAT).hour
    state_agents = {}
    for agent in agents:
        zone = AGENT_HOME_ZONES.get(agent.agent_id, "transit_commons")
        state_agents[agent.agent_id] = {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "zone": zone,
            "home_zone": zone,
            "current_activity": default_activity_for_zone(zone, hour),
            "current_mood": "neutral",
            "current_plan": [],
            "active_encounter_id": None,
            "last_active_step": -1,
        }

    return {
        "sim_id": "sf-live",
        "current_time": current_time,
        "step_number": 0,
        "tick_minutes": 5,
        "agents": state_agents,
        "active_encounters": {},
        "recent_world_events": [],
    }


def load_state() -> dict:
    if not STATE_PATH.exists():
        state = build_initial_state()
        save_state(state)
        return state
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


def reset_state() -> dict:
    state = build_initial_state()
    save_state(state)
    return state


def parse_sim_time(value: str) -> datetime:
    return datetime.strptime(value, TIME_FORMAT)


def format_sim_time(value: datetime) -> str:
    return value.strftime(TIME_FORMAT)
