"""
Reusable behavioral scenario experiments across the full agent population.
"""
import json
import os
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

from agents.loader import Agent, load_all_agents
from agents.runner import run_behavioral_scenario

SIM_LOGS_PATH = Path(os.getenv("SIM_LOGS_PATH", "../sim-logs"))

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


def build_agent_scenario_response(agent: Agent, prompt: str, response_mode: str, date: str) -> dict:
    result = run_behavioral_scenario(agent, prompt, response_mode, date)
    response = {
        "agent_id": agent.agent_id,
        "agent_name": agent.name,
        "response": result.get("response", ""),
    }
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
) -> dict:
    if response_mode not in VALID_RESPONSE_MODES:
        raise ValueError(f"Unsupported response_mode: {response_mode}")

    scenario = default_behavioral_scenario()
    title = title or scenario["title"]
    prompt = prompt or scenario["prompt"]
    date = datetime.now().strftime("%Y-%m-%d")
    experiment_id = str(uuid.uuid4())[:8]

    responses = [
        build_agent_scenario_response(agent, prompt, response_mode, date)
        for agent in load_all_agents()
    ]

    result = {
        "experiment_id": experiment_id,
        "type": "behavioral_scenario",
        "date": date,
        "title": title,
        "prompt": prompt,
        "response_mode": response_mode,
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
