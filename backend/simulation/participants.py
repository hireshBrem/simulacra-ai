import random

from agents.loader import Agent


def select_encounter_agents(
    agents: list[Agent],
    agent_ids: list[str] | None = None,
) -> tuple[Agent, Agent]:
    if len(agents) < 2:
        raise ValueError("Need at least 2 agents for an Encounter.")

    if agent_ids is None:
        agent1, agent2 = random.sample(agents, 2)
        return agent1, agent2

    if len(agent_ids) != 2:
        raise ValueError("Encounter requires exactly 2 agent IDs.")
    if agent_ids[0] == agent_ids[1]:
        raise ValueError("Encounter participants must be different agents.")

    by_id = {agent.agent_id: agent for agent in agents}
    missing = [agent_id for agent_id in agent_ids if agent_id not in by_id]
    if missing:
        raise ValueError(f"Unknown agent ID(s): {', '.join(missing)}")

    return by_id[agent_ids[0]], by_id[agent_ids[1]]
