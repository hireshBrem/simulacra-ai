import os
from pathlib import Path
from dataclasses import dataclass

SIM_DATA_PATH = Path(os.getenv("SIM_DATA_PATH", "../sim-data"))


@dataclass
class Agent:
    agent_id: str
    name: str
    role: str       # full ROLE.md content
    memory: str     # full MEMORY.md content


def load_agent(agent_id: str) -> Agent:
    agent_dir = SIM_DATA_PATH / agent_id
    role = (agent_dir / "ROLE.md").read_text()
    memory = (agent_dir / "MEMORY.md").read_text()

    # Extract name from "# Role: Name" header
    name = role.split("\n")[0].replace("# Role:", "").strip()

    return Agent(agent_id=agent_id, name=name, role=role, memory=memory)


def load_all_agents() -> list[Agent]:
    agents = []
    if SIM_DATA_PATH.exists():
        for d in sorted(SIM_DATA_PATH.iterdir(), key=_agent_sort_key):
            if d.is_dir() and d.name.startswith("agent-"):
                agents.append(load_agent(d.name))
    return agents


def _agent_sort_key(path: Path) -> tuple[int, str]:
    if path.name.startswith("agent-"):
        suffix = path.name.removeprefix("agent-")
        if suffix.isdigit():
            return (int(suffix), path.name)
    return (10**9, path.name)
