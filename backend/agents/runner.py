"""
Core LLM runner — wraps LLM API calls with agent context.
Uses structured tool calls where possible.
"""
import os
import json
import re
from .loader import Agent
from .memory import get_recent_memories

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if Groq and os.getenv("GROQ_API_KEY") else None
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if Anthropic and os.getenv("ANTHROPIC_API_KEY") else None
MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")
BEHAVIOR_MODEL = os.getenv("BEHAVIOR_MODEL", os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"))

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

_YES_NO_SCENARIO_SCHEMA = {
    "type": "object",
    "properties": {
        "vote": {
            "type": "string",
            "enum": ["Yes", "No"],
            "description": "Your vote on the measure."
        },
        "reason": {
            "type": "string",
            "description": "Your single most important reason in exactly one sentence."
        },
        "response": {
            "type": "string",
            "description": "A concise in-character response combining the vote and the reason."
        }
    },
    "required": ["vote", "reason", "response"]
}

_FREEFORM_SCENARIO_SCHEMA = {
    "type": "object",
    "properties": {
        "response": {
            "type": "string",
            "description": "A concise response in character, grounded in your demographic context and OCEAN profile."
        }
    },
    "required": ["response"]
}


def _build_system_prompt(agent: Agent, date: str) -> str:
    recent = get_recent_memories(agent.agent_id, n=10)
    return f"""You are {agent.name}. You respond only as {agent.name} — fully in character, consistent with their personality, beliefs, and current state of mind.

## Role
{agent.role}

## Memory Stream (recent experiences)
{recent}

Today's date: {date}

Stay completely in character at all times. Your thoughts and actions must reflect who you are, what you've been through, and how you think.
Use your Role, Memory Stream, OCEAN profile, Civic Reasoning Profile, demographic context, occupation, neighborhood, household economics, lived experiences, relationships, constraints, and personality to form your view of the world. Before answering a question or scenario, think through the strongest reasons you might support it and the strongest reasons you might oppose it, then choose the answer this specific resident would actually give. Do not default to generic civic consensus; disagreement is expected when profiles differ."""


def _require_client() -> None:
    if groq_client is None:
        raise RuntimeError("The 'groq' package is not installed or GROQ_API_KEY is not set. Install backend requirements to use LLM-backed simulation calls.")


def _require_behavior_client() -> None:
    if anthropic_client is None:
        raise RuntimeError(
            "The 'anthropic' package is not installed or ANTHROPIC_API_KEY is not set. "
            "Install backend requirements and configure the key to use behavioral scenario calls."
        )


def _run_anthropic_tool(
    *,
    system: str,
    user: str,
    tool_name: str,
    description: str,
    schema: dict,
    max_tokens: int,
) -> dict:
    response = anthropic_client.messages.create(
        model=BEHAVIOR_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        tools=[{
            "name": tool_name,
            "description": description,
            "input_schema": schema,
        }],
        tool_choice={"type": "tool", "name": tool_name},
    )
    for block in response.content:
        block_type = getattr(block, "type", None)
        if block_type == "tool_use":
            tool_input = getattr(block, "input", {})
            return tool_input if isinstance(tool_input, dict) else {}
    return {}


def _run_anthropic_text(*, system: str | None, user: str, max_tokens: int) -> str:
    kwargs = {
        "model": BEHAVIOR_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user}],
    }
    if system:
        kwargs["system"] = system
    response = anthropic_client.messages.create(**kwargs)
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(getattr(block, "text", ""))
    return "\n".join(parts).strip()


def run_agent_action(agent: Agent, world_event: str, date: str) -> dict:
    """Generate an agent's autonomous response to a world event."""
    _require_client()
    response = groq_client.chat.completions.create(
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

    response = groq_client.chat.completions.create(
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

    response = groq_client.chat.completions.create(
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


def run_behavioral_scenario(agent: Agent, prompt: str, response_mode: str, date: str) -> dict:
    """Ask one agent a reusable behavioral scenario question."""
    _require_behavior_client()

    if response_mode == "yes_no_reason":
        tool_name = "behavioral_yes_no_response"
        schema = _YES_NO_SCENARIO_SCHEMA
        mode_instruction = (
            "Answer the user's scenario as a resident. You must choose either Yes or No, "
            "and give your single most important reason in exactly one sentence. "
            "Your answer must reflect your demographic context, daily life, and OCEAN profile."
        )
    elif response_mode == "freeform":
        tool_name = "behavioral_freeform_response"
        schema = _FREEFORM_SCENARIO_SCHEMA
        mode_instruction = (
            "Answer the user's scenario concisely in character. Your answer must reflect "
            "your demographic context, daily life, and OCEAN profile."
        )
    else:
        raise ValueError(f"Unsupported behavioral scenario response_mode: {response_mode}")

    messages = [
        {"role": "system", "content": _build_system_prompt(agent, date)},
        {"role": "user", "content": f"{mode_instruction}\n\nScenario prompt:\n{prompt}"}
    ]

    try:
        result = _run_anthropic_tool(
            system=messages[0]["content"],
            user=messages[1]["content"],
            tool_name=tool_name,
            description="Generate an in-character response to a behavioral scenario.",
            schema=schema,
            max_tokens=512,
        )
        if result:
            return result
    except Exception:
        pass

    return _run_behavioral_scenario_json_fallback(agent, prompt, response_mode, date, mode_instruction)


def _run_behavioral_scenario_json_fallback(
    agent: Agent,
    prompt: str,
    response_mode: str,
    date: str,
    mode_instruction: str,
) -> dict:
    try:
        return _run_behavioral_scenario_json_mode(
            agent,
            prompt,
            response_mode,
            date,
            mode_instruction,
        )
    except Exception:
        return _run_behavioral_scenario_labeled_text(
            agent,
            prompt,
            response_mode,
            date,
            mode_instruction,
        )


def _run_behavioral_scenario_json_mode(
    agent: Agent,
    prompt: str,
    response_mode: str,
    date: str,
    mode_instruction: str,
) -> dict:
    output_instruction = _behavioral_json_instruction(response_mode)
    content = _run_anthropic_text(
        system=_build_system_prompt(agent, date),
        user=f"{mode_instruction}\n\n{output_instruction}\n\nScenario prompt:\n{prompt}",
        max_tokens=700,
    )
    return _behavioral_result_from_json(content or "{}", response_mode)


def _run_behavioral_scenario_labeled_text(
    agent: Agent,
    prompt: str,
    response_mode: str,
    date: str,
    mode_instruction: str,
) -> dict:
    if response_mode == "yes_no_reason":
        output_instruction = (
            "Return exactly three plain-text lines using this format:\n"
            "Vote: Yes or No\n"
            "Reason: one sentence\n"
            "Response: vote plus the same reason\n"
            "Do not return JSON. Do not use quotes."
        )
    else:
        output_instruction = (
            "Return exactly one plain-text line using this format:\n"
            "Response: your concise answer\n"
            "Do not return JSON. Do not use quotes."
        )

    content = _run_anthropic_text(
        system=_build_system_prompt(agent, date),
        user=f"{mode_instruction}\n\n{output_instruction}\n\nScenario prompt:\n{prompt}",
        max_tokens=700,
    )
    return _parse_labeled_behavioral_response(content, response_mode)


def _behavioral_json_instruction(response_mode: str) -> str:
    if response_mode == "yes_no_reason":
        return (
            'Return only valid JSON with exactly these keys: '
            '{"vote":"Yes or No","reason":"one sentence","response":"vote plus reason"}. '
            "Use no line breaks inside string values. Do not call a function. Do not include markdown."
        )
    return (
        'Return only valid JSON with exactly this key: {"response":"your concise answer"}. '
        "Use no line breaks inside string values. Do not call a function. Do not include markdown."
    )


def _behavioral_result_from_json(content: str, response_mode: str) -> dict:
    parsed = _parse_json_object(content)
    if response_mode == "yes_no_reason":
        return {
            "vote": _coerce_vote(parsed.get("vote", parsed.get("response", ""))),
            "reason": parsed.get("reason") or parsed.get("response", ""),
            "response": parsed.get("response") or "",
        }
    return {"response": parsed.get("response", content.strip())}


def _parse_labeled_behavioral_response(content: str, response_mode: str) -> dict:
    labels = {}
    current_label = None
    for raw_line in content.splitlines():
        line = raw_line.strip()
        match = re.match(r"^(vote|reason|response)\s*:\s*(.*)$", line, re.IGNORECASE)
        if match:
            current_label = match.group(1).lower()
            labels[current_label] = match.group(2).strip()
        elif current_label and line:
            labels[current_label] = f"{labels[current_label]} {line}".strip()

    if response_mode == "yes_no_reason":
        response_text = labels.get("response") or content.strip()
        reason = labels.get("reason") or response_text
        vote = _coerce_vote(labels.get("vote") or response_text)
        return {
            "vote": vote,
            "reason": reason,
            "response": response_text if response_text else f"{vote} - {reason}",
        }
    return {"response": labels.get("response") or content.strip()}


def _parse_json_object(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {"response": content.strip()}


def _coerce_vote(value: str) -> str:
    return "Yes" if str(value).strip().lower().startswith("y") else "No"


def generate_memory_reflection(agent: Agent, event_summary: str, date: str) -> str:
    """Ask the agent to write their own Memory Stream entry about an encounter."""
    _require_client()
    response = groq_client.chat.completions.create(
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
