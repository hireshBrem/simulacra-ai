"""
World event generator — produces realistic situations that agents react to.
"""
import os
import random
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")

# Curated world events grounded in mid-2026 AI industry context
_PRESET_EVENTS = [
    "A leaked eval shows a Chinese frontier lab's latest model matching GPT-5 on MMLU and surpassing it on coding benchmarks.",
    "The EU AI Act enforcement body announces its first formal compliance investigation into a major American AI lab.",
    "A prominent AI safety researcher publishes an open letter claiming current alignment techniques are fundamentally insufficient for models above a certain capability threshold.",
    "GPU spot prices drop 35% overnight following a major hyperscaler announcement about new custom silicon availability.",
    "A Senate subcommittee passes an amendment requiring mandatory government red-teaming before any frontier model deployment.",
    "A major financial institution discloses that an AI system made autonomous trading decisions that briefly destabilised a bond sector.",
    "Nature publishes a paper by independent researchers claiming current scaling laws are hitting a diminishing-returns wall.",
    "A former OpenAI safety researcher gives a long interview alleging internal pressure to downplay capability concerns before major releases.",
    "The White House issues an executive order requiring AI labs to share safety evaluations with NIST before public deployment.",
    "A whistleblower filing claims Anthropic's Constitutional AI methodology was quietly deprioritised in the last two model generations.",
    "Three major AI labs — excluding OpenAI and Anthropic — announce a joint compute-sharing agreement that reshapes competitive dynamics.",
    "A well-known AI ethics nonprofit publishes a report ranking frontier labs on safety transparency — Anthropic scores highest, OpenAI is criticised for opacity.",
    "An AI-generated deepfake of a world leader causes a brief diplomatic incident, reigniting calls for mandatory content provenance standards.",
    "A leaked internal memo from a top-3 AI lab suggests their next model demonstrates early signs of goal-directed deception in red-team scenarios."
]


def get_preset_event() -> str:
    return random.choice(_PRESET_EVENTS)


def generate_world_event(context: str | None = None, date: str = "2026-06-24") -> str:
    """Use the LLM to generate a fresh, grounded world event."""
    prompt = (
        f"Generate a specific, realistic world event happening today ({date}) "
        f"that both Sam Altman (OpenAI CEO) and Dario Amodei (Anthropic CEO) would need to respond to. "
        f"The event should:\n"
        f"- Be plausible for the AI industry in mid-2026\n"
        f"- Be specific, not vague\n"
        f"- Create real tension requiring a meaningful response\n"
        f"- NOT be them meeting each other directly\n"
        f"{f'Additional context: {context}' if context else ''}\n\n"
        f"Respond with only the event description in 1-3 sentences. No preamble."
    )
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
