import os
import unittest
from unittest.mock import patch

from agents.loader import Agent
from simulation import step


def agent(agent_id: str = "agent-1", name: str = "Mateo Rivera") -> Agent:
    return Agent(
        agent_id=agent_id,
        name=name,
        role=f"# Role: {name}",
        memory="",
    )


def agent_state(agent_id: str = "agent-1", name: str = "Mateo Rivera") -> dict:
    return {
        "agent_id": agent_id,
        "name": name,
        "zone": "west_side",
        "home_zone": "west_side",
        "current_activity": "winding down after the day",
        "current_mood": "neutral",
    }


def perception() -> dict:
    return {
        "nearby_agents": [],
        "current_time": "2026-06-28 17:02",
        "step_number": 1,
    }


class SimulationLlmDecisionTests(unittest.TestCase):
    def test_llm_mode_requires_groq_key_instead_of_falling_back(self) -> None:
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "GROQ_API_KEY is not set"):
                step._decide(agent_state(), perception(), "query", "memories", use_llm=True)

    def test_non_llm_mode_still_uses_fallback(self) -> None:
        decision = step._decide(agent_state(), perception(), "query", "memories", use_llm=False)

        self.assertEqual(decision["action_type"], "move")
        self.assertEqual(decision["target_zone"], "transit_commons")
        self.assertEqual(decision["public_action"], "winding down after the day")

    def test_llm_mode_uses_runner_decision(self) -> None:
        llm_decision = {
            "action_type": "observe",
            "target_zone": "west_side",
            "target_agent_id": "",
            "public_action": "Mateo checks the bus app before deciding whether to head home.",
            "inner_monologue": "The evening timing matters.",
            "emotional_state": "focused",
            "memory_entry": "",
        }

        with (
            patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}),
            patch.object(step, "load_agent", return_value=agent()),
            patch.object(step, "run_simulation_decision", return_value=llm_decision) as run_decision,
        ):
            decision = step._decide(agent_state(), perception(), "query", "memories", use_llm=True)

        self.assertEqual(decision["public_action"], llm_decision["public_action"])
        run_decision.assert_called_once()

    def test_llm_conversation_mode_requires_groq_key(self) -> None:
        encounter = {
            "zone": "west_side",
            "topic": "evening commute",
            "history": [],
        }
        state = {"current_time": "2026-06-28 17:02"}

        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "GROQ_API_KEY is not set"):
                step._conversation_turn(
                    agent_state(),
                    agent_state("agent-2", "James Park"),
                    encounter,
                    state,
                    use_llm=True,
                )


if __name__ == "__main__":
    unittest.main()
