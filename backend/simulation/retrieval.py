"""
Lightweight Memory Stream retrieval for markdown memories.
"""
import math
import re
from pathlib import Path

from agents.memory import SIM_DATA_PATH

_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]*")


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _WORD_RE.findall(text)}


def parse_memory_entries(agent_id: str) -> list[dict]:
    path = Path(SIM_DATA_PATH) / agent_id / "MEMORY.md"
    content = path.read_text().strip()
    entries: list[dict] = []
    current: list[str] = []

    for line in content.splitlines():
        if line.startswith("[") and current:
            entries.append(_entry_from_lines(current))
            current = [line]
        elif line.strip():
            current.append(line)

    if current:
        entries.append(_entry_from_lines(current))

    return [entry for entry in entries if entry["content"]]


def _entry_from_lines(lines: list[str]) -> dict:
    raw = "\n".join(lines).strip()
    timestamp = ""
    content = raw
    if raw.startswith("[") and "]" in raw:
        timestamp, content = raw[1:].split("]", 1)
        content = content.strip()
    return {
        "timestamp": timestamp,
        "content": content,
        "raw": raw,
    }


def retrieve_memories(agent_id: str, query: str, limit: int = 5) -> list[dict]:
    query_tokens = _tokens(query)
    entries = parse_memory_entries(agent_id)
    total = len(entries)
    scored = []

    for index, entry in enumerate(entries):
        entry_tokens = _tokens(entry["content"])
        overlap = len(query_tokens & entry_tokens)
        recency = (index + 1) / max(total, 1)
        importance = _importance_hint(entry["content"])
        score = overlap * 2.0 + recency + importance
        if score > 0:
            scored.append({**entry, "score": round(score, 4)})

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]


def memories_text(memories: list[dict]) -> str:
    if not memories:
        return "No strongly relevant memories found."
    return "\n".join(f"- {m['content']}" for m in memories)


def _importance_hint(content: str) -> float:
    lowered = content.lower()
    markers = [
        "worried",
        "important",
        "remember",
        "conversation",
        "call",
        "agreed",
        "left me",
        "wondering",
        "housing",
        "work",
        "family",
        "risk",
    ]
    hits = sum(1 for marker in markers if marker in lowered)
    return math.log1p(hits)
