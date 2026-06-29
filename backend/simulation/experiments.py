"""
Reusable behavioral scenario experiments across the full agent population.
"""
import json
import os
import re
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

from agents.loader import Agent, load_all_agents
from agents.runner import run_behavioral_scenario

SIM_LOGS_PATH = Path(os.getenv("SIM_LOGS_PATH", "../sim-logs"))
DELIVERY_APP_EXPERIENCES_PATH = Path(
    os.getenv(
        "DELIVERY_APP_EXPERIENCES_PATH",
        Path(__file__).resolve().parents[1] / "delivery_app_experiences.json",
    )
)
SOCIAL_INFLUENCE_VOTES_PATH = Path(
    os.getenv(
        "SOCIAL_INFLUENCE_VOTES_PATH",
        Path(__file__).resolve().parents[1] / ".tmp" / "social_influence_votes.json",
    )
)

PROP_X_TITLE = "Prop X delivery fee cap"
PROP_X_PROMPT = (
    "San Francisco is voting on a measure that would cap food delivery app fees "
    "(DoorDash, Uber Eats) at 15%. As a resident, would you vote Yes or No? "
    "Give your single most important reason in one sentence."
)

VALID_RESPONSE_MODES = {"yes_no_reason", "freeform"}


def _save_log(data: dict) -> None:
    SIM_LOGS_PATH.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{ts}_{data['type']}_{data['experiment_id']}.json"
    (SIM_LOGS_PATH / filename).write_text(json.dumps(data, indent=2))


def save_behavioral_scenario_log(data: dict) -> None:
    _save_log(data)


def default_behavioral_scenario() -> dict:
    return {
        "title": PROP_X_TITLE,
        "prompt": PROP_X_PROMPT,
        "response_mode": "yes_no_reason",
    }


def load_delivery_app_experiences() -> dict[str, list[str]]:
    data = json.loads(DELIVERY_APP_EXPERIENCES_PATH.read_text())
    experiences: dict[str, list[str]] = {}
    for item in data:
        agent_id = str(item.get("agent_id", ""))
        agent_experiences = item.get("experiences", [])
        if agent_id and isinstance(agent_experiences, list):
            experiences[agent_id] = [str(experience) for experience in agent_experiences[:3]]
    return experiences


def delivery_app_experience_lookup(enabled: bool) -> dict[str, list[str]]:
    return load_delivery_app_experiences() if enabled else {}


def create_social_influence_vote_file(experiment_id: str) -> None:
    SOCIAL_INFLUENCE_VOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_social_influence_votes({
        "experiment_id": experiment_id,
        "neighborhoods": {},
    })


def clear_social_influence_vote_file() -> None:
    SOCIAL_INFLUENCE_VOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_social_influence_votes({})


def append_social_influence_vote(
    *,
    experiment_id: str,
    neighborhood: str,
    response: dict,
) -> None:
    data = _read_social_influence_votes()
    if data.get("experiment_id") != experiment_id:
        data = {"experiment_id": experiment_id, "neighborhoods": {}}

    neighborhoods = data.setdefault("neighborhoods", {})
    votes = neighborhoods.setdefault(neighborhood, [])
    votes.append({
        "agent_id": response.get("agent_id", ""),
        "agent_name": response.get("agent_name", ""),
        "vote": response.get("vote", ""),
    })
    _write_social_influence_votes(data)


def social_influence_vote_counts(neighborhood: str) -> dict:
    votes = _read_social_influence_votes().get("neighborhoods", {}).get(neighborhood, [])
    yes = sum(1 for vote in votes if vote.get("vote") == "Yes")
    no = sum(1 for vote in votes if vote.get("vote") == "No")
    return {"yes": yes, "no": no, "total": yes + no}


def social_influence_prompt_context(neighborhood: str, counts: dict) -> str:
    if counts.get("total", 0) <= 0:
        return f"No one else in {neighborhood} has voted yet."
    return (
        f"Before making your final decision, you are aware that in {neighborhood}, "
        "prior voters in this simulation have voted:\n"
        f"- Yes: {counts.get('yes', 0)}\n"
        f"- No: {counts.get('no', 0)}"
    )


def agent_neighborhood(agent: Agent) -> str:
    match = re.search(r"^\s*-\s*\*\*Location:\*\*\s*([^,\n]+)", agent.role, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown neighborhood"


def build_agent_scenario_response(
    agent: Agent,
    prompt: str,
    response_mode: str,
    date: str,
    delivery_app_experiences: list[str] | None = None,
    neighborhood_votes_context: str = "",
    neighborhood_votes_seen: dict | None = None,
) -> dict:
    delivery_app_experiences = delivery_app_experiences or []
    result = run_behavioral_scenario(
        agent,
        prompt,
        response_mode,
        date,
        delivery_app_experiences=delivery_app_experiences,
        neighborhood_votes_context=neighborhood_votes_context,
    )
    response = {
        "agent_id": agent.agent_id,
        "agent_name": agent.name,
        "response": result.get("response", ""),
    }
    if neighborhood_votes_seen is not None:
        response["neighborhood"] = agent_neighborhood(agent)
        response["neighborhood_votes_seen"] = neighborhood_votes_seen
    if delivery_app_experiences:
        response["delivery_app_experiences"] = delivery_app_experiences
    if response_mode == "yes_no_reason":
        response["vote"] = _normalize_vote(result.get("vote", ""))
        response["reason"] = _one_line(result.get("reason", ""))
        if not response["response"]:
            response["response"] = f"{response['vote']} - {response['reason']}"
    return response


def run_behavioral_scenario_experiment(
    title: str | None = None,
    prompt: str | None = None,
    response_mode: str = "yes_no_reason",
    use_delivery_app_experiences: bool = False,
    use_social_influence: bool = False,
) -> dict:
    if response_mode not in VALID_RESPONSE_MODES:
        raise ValueError(f"Unsupported response_mode: {response_mode}")

    scenario = default_behavioral_scenario()
    title = title or scenario["title"]
    prompt = prompt or scenario["prompt"]
    date = datetime.now().strftime("%Y-%m-%d")
    experiment_id = str(uuid.uuid4())[:8]
    experience_lookup = delivery_app_experience_lookup(use_delivery_app_experiences)
    use_vote_file = use_social_influence and response_mode == "yes_no_reason"

    responses = []
    if use_vote_file:
        create_social_influence_vote_file(experiment_id)
    try:
        for agent in load_all_agents():
            neighborhood = agent_neighborhood(agent)
            votes_seen = social_influence_vote_counts(neighborhood) if use_vote_file else None
            response = build_agent_scenario_response(
                agent,
                prompt,
                response_mode,
                date,
                experience_lookup.get(agent.agent_id, []),
                social_influence_prompt_context(neighborhood, votes_seen) if votes_seen is not None else "",
                votes_seen,
            )
            if use_social_influence:
                response["neighborhood"] = neighborhood
                if votes_seen is not None:
                    response["neighborhood_votes_seen"] = votes_seen
            responses.append(response)
            if use_vote_file:
                append_social_influence_vote(
                    experiment_id=experiment_id,
                    neighborhood=neighborhood,
                    response=response,
                )
    finally:
        if use_vote_file:
            clear_social_influence_vote_file()

    result = {
        "experiment_id": experiment_id,
        "type": "behavioral_scenario",
        "date": date,
        "title": title,
        "prompt": prompt,
        "response_mode": response_mode,
        "use_delivery_app_experiences": use_delivery_app_experiences,
        "use_social_influence": use_social_influence,
        "responses": responses,
        "summary": summarize_behavioral_scenario(responses, response_mode),
    }
    _save_log(result)
    return result


def summarize_behavioral_scenario(responses: list[dict], response_mode: str) -> dict:
    if response_mode != "yes_no_reason":
        return {
            "total": len(responses),
            "most_interesting": _most_interesting_response(responses, None),
        }

    split = Counter(response.get("vote", "No") for response in responses)
    yes = split.get("Yes", 0)
    no = split.get("No", 0)
    minority_vote = "Yes" if yes < no else "No" if no < yes else None

    return {
        "vote_split": {
            "yes": yes,
            "no": no,
            "total": len(responses),
        },
        "top_reasons": {
            "yes": _top_reasons(responses, "Yes"),
            "no": _top_reasons(responses, "No"),
        },
        "most_interesting": _most_interesting_response(responses, minority_vote),
    }


def _normalize_vote(value: str) -> str:
    return "Yes" if str(value).strip().lower().startswith("y") else "No"


def _one_line(value: str) -> str:
    return " ".join(str(value).split())


def _top_reasons(responses: list[dict], vote: str) -> list[dict]:
    grouped: dict[str, dict] = {}
    for response in responses:
        if response.get("vote") != vote:
            continue
        reason = response.get("reason") or response.get("response") or ""
        label = _reason_label(reason)
        if label not in grouped:
            grouped[label] = {"reason": label, "count": 0, "example": reason}
        grouped[label]["count"] += 1

    return sorted(grouped.values(), key=lambda item: (-item["count"], item["reason"]))[:3]


def _reason_label(reason: str) -> str:
    text = reason.lower()
    categories = [
        (("restaurant", "small business", "local business", "merchant"), "Protecting restaurants and local businesses"),
        (("fee", "commission", "15%", "cap", "cut"), "Limiting platform fees"),
        (("consumer", "customer", "cost", "price", "affordable", "affordability"), "Consumer affordability"),
        (("driver", "worker", "wage", "job", "pay", "labor"), "Worker pay and jobs"),
        (("regulation", "government", "market", "interfere", "unintended"), "Concern about government regulation or side effects"),
        (("delivery", "access", "convenience", "mobility", "elder", "disabled"), "Delivery access and convenience"),
        (("profit", "doordash", "uber", "platform", "corporate"), "Platform power and fairness"),
    ]
    for keywords, label in categories:
        if any(keyword in text for keyword in keywords):
            return label
    return "Practical household or neighborhood impact"


def _most_interesting_response(responses: list[dict], minority_vote: str | None) -> dict:
    candidates = [
        response for response in responses
        if minority_vote is None or response.get("vote") == minority_vote
    ] or responses
    if not candidates:
        return {}

    chosen = max(candidates, key=lambda response: len(response.get("reason") or response.get("response") or ""))
    vote_text = f" and represents the {minority_vote} side" if minority_vote else ""
    return {
        **chosen,
        "why_interesting": (
            f"It stands out because it gives the most specific lived-context rationale{vote_text}."
        ),
    }


def _read_social_influence_votes() -> dict:
    if not SOCIAL_INFLUENCE_VOTES_PATH.exists():
        return {}
    try:
        data = json.loads(SOCIAL_INFLUENCE_VOTES_PATH.read_text())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _write_social_influence_votes(data: dict) -> None:
    SOCIAL_INFLUENCE_VOTES_PATH.write_text(json.dumps(data, indent=2))
