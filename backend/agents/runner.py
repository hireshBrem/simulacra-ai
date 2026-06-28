"""
Core LLM runner — wraps Groq API calls with agent context.
Uses function calling for reliable structured output.
"""
import os
import json
from .loader import Agent
from .memory import get_recent_memories

try:
    from groq import Groq
except ImportError:
    Groq = None

client = Groq(api_key=os.getenv("GROQ_API_KEY")) if Groq else None
MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")

# Schema for an agent's autonomous action (solo world event)
_ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "inner_monologue": {
            "type": "string",
            "description": "Your private stream of consciousness — what you're actually thinking. 2-4 sentences."
        },
        "public_action": {
            "type": "string",
            "description": "What you do or say publicly in this moment. Be specific and vivid — not 'I reflect' but the actual tweet, statement, decision, or action."
        },
        "action_type": {
            "type": "string",
            "enum": ["tweet", "statement", "decision", "phone_call", "email", "meeting", "reflection", "announcement"],
            "description": "The form this action takes."
        },
        "memory_entry": {
            "type": "string",
            "description": "A concise journal entry for your Memory Stream. First person, past tense, specific. This is what you'll remember."
        },
        "emotional_state": {
            "type": "string",
            "description": "One or two words describing your current emotional state."
        }
    },
    "required": ["inner_monologue", "public_action", "action_type", "memory_entry", "emotional_state"]
}

# Schema for one turn in an agent-to-agent Conversation
_UTTERANCE_SCHEMA = {
    "type": "object",
    "properties": {
        "internal_state": {
            "type": "string",
            "description": "What you are privately thinking as you formulate your response. 1-2 sentences."
        },
        "utterance": {
            "type": "string",
            "description": "Exactly what you say, verbatim and in your own voice. Authentic to your communication style."
        }
    },
    "required": ["internal_state", "utterance"]
}

_SIMULATION_DECISION_SCHEMA = {
    "type": "object",
    "properties": {
        "action_type": {
            "type": "string",
            "enum": ["continue_routine", "move", "observe", "start_conversation", "reflect"],
            "description": "The next simulation action this agent should take."
        },
        "target_zone": {
            "type": "string",
            "description": "Destination zone if moving; otherwise keep this as the current zone."
        },
        "target_agent_id": {
            "type": "string",
            "description": "Agent ID to talk to if starting a conversation; otherwise an empty string."
        },
        "public_action": {
            "type": "string",
            "description": "What others could observe the agent doing. One specific sentence."
        },
        "inner_monologue": {
            "type": "string",
            "description": "Private reasoning in character. One or two sentences."
        },
        "emotional_state": {
            "type": "string",
            "description": "One or two words for the agent's current emotional state."
        },
        "memory_entry": {
            "type": "string",
            "description": "A concise first-person memory if this action is worth remembering; otherwise an empty string."
        }
    },
    "required": [
        "action_type",
        "target_zone",
        "target_agent_id",
        "public_action",
        "inner_monologue",
        "emotional_state",
        "memory_entry"
    ]
}


def _build_system_prompt(agent: Agent, date: str) -> str:
    recent = get_recent_memories(agent.agent_id, n=10)
    return f"""You are {agent.name}. You respond only as {agent.name} — fully in character, consistent with their personality, beliefs, and current state of mind.

## Role
{agent.role}

## Memory Stream (recent experiences)
{recent}

Today's date: {date}

Stay completely in character at all times. Your thoughts and actions must reflect who you are, what you've been through, and how you think."""


def _require_client() -> None:
    if client is None:
        raise RuntimeError("The 'groq' package is not installed. Install backend requirements to use LLM-backed simulation calls.")


def run_agent_action(agent: Agent, world_event: str, date: str) -> dict:
    """Generate an agent's autonomous response to a world event."""
    _require_client()
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": _build_system_prompt(agent, date)},
            {"role": "user", "content": f"World event: {world_event}\n\nGenerate your authentic response."}
        ],
        tools=[{
            "type": "function",
            "function": {
                "name": "generate_action",
                "description": "Generate your authentic response to the current situation.",
                "parameters": _ACTION_SCHEMA
            }
        }],
        tool_choice={"type": "function", "function": {"name": "generate_action"}}
    )
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        return json.loads(tool_calls[0].function.arguments)
    return {}


def run_conversation_turn(
    speaker: Agent,
    listener_name: str,
    situation: str,
    history: list[dict],
    date: str
) -> dict:
    """Generate one utterance in an agent-to-agent Conversation."""
    _require_client()
    history_text = "\n".join(
        f"{t['speaker']}: {t['utterance']}" for t in history
    ) if history else "(start of conversation)"

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        messages=[
            {"role": "system", "content": _build_system_prompt(speaker, date)},
            {"role": "user", "content": (
                f"You are speaking with {listener_name}.\n"
                f"Context: {situation}\n\n"
                f"Conversation so far:\n{history_text}\n\n"
                f"Now respond as {speaker.name}."
            )}
        ],
        tools=[{
            "type": "function",
            "function": {
                "name": "conversation_turn",
                "description": "Generate your next message in this conversation.",
                "parameters": _UTTERANCE_SCHEMA
            }
        }],
        tool_choice={"type": "function", "function": {"name": "conversation_turn"}}
    )
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        return json.loads(tool_calls[0].function.arguments)
    return {}


def run_simulation_decision(
    agent: Agent,
    perception: str,
    relevant_memories: str,
    valid_zones: list[str],
    nearby_agents: list[dict],
    date: str,
) -> dict:
    """Choose one step-level action for an agent in the persistent simulation."""
    _require_client()
    nearby_text = "\n".join(
        f"- {a['agent_id']}: {a['name']} ({a.get('current_activity', 'nearby')})"
        for a in nearby_agents
    ) or "No other agents are nearby."

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=700,
        messages=[
            {"role": "system", "content": _build_system_prompt(agent, date)},
            {"role": "user", "content": (
                "You are taking one small step in a long-running San Francisco social simulation.\n"
                "Prefer ordinary, situated behavior over dramatic reactions. Only start a conversation "
                "when someone nearby is plausibly worth talking to. Only move when the destination fits "
                "your routine, obligations, or current context.\n\n"
                f"Valid zones: {', '.join(valid_zones)}\n\n"
                f"Nearby agents:\n{nearby_text}\n\n"
                f"What you perceive:\n{perception}\n\n"
                f"Relevant memories:\n{relevant_memories}\n\n"
                "Choose your next action."
            )}
        ],
        tools=[{
            "type": "function",
            "function": {
                "name": "simulation_decision",
                "description": "Choose the agent's next step in the ongoing simulation.",
                "parameters": _SIMULATION_DECISION_SCHEMA
            }
        }],
        tool_choice={"type": "function", "function": {"name": "simulation_decision"}}
    )
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        return json.loads(tool_calls[0].function.arguments)
    return {}


def generate_memory_reflection(agent: Agent, event_summary: str, date: str) -> str:
    """Ask the agent to write their own Memory Stream entry about an encounter."""
    _require_client()
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=256,
        messages=[
            {"role": "system", "content": _build_system_prompt(agent, date)},
            {"role": "user", "content": (
                f"You just experienced: {event_summary}\n\n"
                f"Write one Memory Stream entry as you would actually remember this. "
                f"First person, past tense, specific. 1-3 sentences. No timestamp — just the text."
            )}
        ]
    )
    return response.choices[0].message.content.strip()
