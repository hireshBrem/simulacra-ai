import os
from pathlib import Path
from datetime import datetime

SIM_DATA_PATH = Path(os.getenv("SIM_DATA_PATH", "../sim-data"))


def get_recent_memories(agent_id: str, n: int = 10) -> str:
    """Return the last n entries from an agent's Memory Stream."""
    path = SIM_DATA_PATH / agent_id / "MEMORY.md"
    content = path.read_text().strip()

    # Split on timestamp pattern — each entry starts with [YYYY-...
    entries = []
    current: list[str] = []
    for line in content.split("\n"):
        if line.startswith("[") and current:
            entries.append("\n".join(current).strip())
            current = [line]
        elif line:
            current.append(line)
    if current:
        entries.append("\n".join(current).strip())

    return "\n\n".join(entries[-n:])


def append_memory(agent_id: str, entry: str, timestamp: str | None = None) -> None:
    """Append a new entry to an agent's Memory Stream."""
    path = SIM_DATA_PATH / agent_id / "MEMORY.md"
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(path, "a") as f:
        f.write(f"\n\n[{timestamp}] {entry.strip()}")
