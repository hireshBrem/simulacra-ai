from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from agents.loader import load_all_agents, load_agent
from agents.memory import get_recent_memories
from simulation.experiments import run_behavioral_scenario_experiment
from simulation.loop import run_world_event_turn, run_encounter, get_simulation_log
from simulation.state import load_state, reset_state
from simulation.step import run_simulation_steps, simulation_step

router = APIRouter()


# ── Agents ──────────────────────────────────────────────────────────────────

@router.get("/agents")
def list_agents():
    agents = load_all_agents()
    return [
        {
            "agent_id": a.agent_id,
            "name": a.name,
            "role_preview": a.role[:300] + "..."
        }
        for a in agents
    ]


@router.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    try:
        a = load_agent(agent_id)
        return {"agent_id": a.agent_id, "name": a.name, "role": a.role, "memory": a.memory}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")


@router.get("/agents/{agent_id}/memory")
def get_memory(agent_id: str, n: int = 10):
    try:
        return {"agent_id": agent_id, "memory_stream": get_recent_memories(agent_id, n)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")


# ── Simulation ───────────────────────────────────────────────────────────────

class WorldEventRequest(BaseModel):
    event: Optional[str] = None         # custom event description; omit to use a preset
    use_llm_event: bool = False          # if True and event is None, generate one with LLM


class EncounterRequest(BaseModel):
    topic: Optional[str] = None         # conversation topic; omit to auto-generate
    exchanges: int = 4                  # number of back-and-forth turns
    agent_ids: Optional[list[str]] = None  # exactly 2 IDs; omit to choose 2 agents


class SimulationStepRequest(BaseModel):
    max_agents: int = 0  # 0 means every Agent gets a turn this step
    tick_minutes: int = 5
    use_llm: bool = True


class SimulationRunRequest(SimulationStepRequest):
    steps: int = 1


class BehavioralScenarioRequest(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None
    response_mode: str = "yes_no_reason"
    use_delivery_app_experiences: bool = False


@router.post("/simulate/world-event")
def simulate_world_event(request: WorldEventRequest):
    """
    Each agent independently responds to a shared world event.
    Their reactions and memory entries are returned and saved.
    """
    try:
        return run_world_event_turn(
            event=request.event,
            use_llm_event=request.use_llm_event
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/encounter")
def simulate_encounter(request: EncounterRequest):
    """
    Two agents encounter each other and hold a Conversation.
    The full exchange and resulting memory entries are returned and saved.
    """
    try:
        return run_encounter(
            topic=request.topic,
            exchanges=request.exchanges,
            agent_ids=request.agent_ids,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/behavioral-scenarios")
def behavioral_scenario(request: BehavioralScenarioRequest):
    """Run one prompt across every agent and return the individual responses."""
    try:
        return run_behavioral_scenario_experiment(
            title=request.title,
            prompt=request.prompt,
            response_mode=request.response_mode,
            use_delivery_app_experiences=request.use_delivery_app_experiences,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulate/log")
def simulation_log(limit: int = 20):
    """Return recent simulation turns in reverse chronological order."""
    return get_simulation_log(limit=limit)


@router.get("/simulation/state")
def simulation_state():
    """Return the persistent step-based Simulation Model state."""
    return load_state()


@router.post("/simulation/reset")
def reset_simulation_state():
    """Reset the persistent step-based Simulation Model state."""
    return reset_state()


@router.post("/simulation/step")
def step_simulation(request: SimulationStepRequest):
    """Advance the persistent Simulation Model by one tick."""
    try:
        return simulation_step(
            max_agents=request.max_agents,
            tick_minutes=request.tick_minutes,
            use_llm=request.use_llm,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation/run")
def run_simulation(request: SimulationRunRequest):
    """Advance the persistent Simulation Model by multiple ticks."""
    try:
        return run_simulation_steps(
            steps=request.steps,
            max_agents=request.max_agents,
            tick_minutes=request.tick_minutes,
            use_llm=request.use_llm,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
