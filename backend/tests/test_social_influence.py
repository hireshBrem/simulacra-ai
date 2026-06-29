import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.loader import Agent
from simulation import experiments


def agent(agent_id: str, name: str, neighborhood: str) -> Agent:
    return Agent(
        agent_id=agent_id,
        name=name,
        role=(
            f"# Role: {name}\n\n"
            "## Identity\n"
            f"- **Location:** {neighborhood}, San Francisco, California\n"
        ),
        memory="",
    )


class SocialInfluenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.vote_path = Path(self.tmpdir.name) / "social_influence_votes.json"
        self.path_patch = patch.object(experiments, "SOCIAL_INFLUENCE_VOTES_PATH", self.vote_path)
        self.path_patch.start()

    def tearDown(self) -> None:
        self.path_patch.stop()
        self.tmpdir.cleanup()

    def test_neighborhood_is_read_from_role_location(self) -> None:
        self.assertEqual(experiments.agent_neighborhood(agent("agent-1", "Mateo", "Sunset")), "Sunset")

    def test_vote_file_groups_votes_by_neighborhood_and_clears(self) -> None:
        experiments.create_social_influence_vote_file("exp-1")
        experiments.append_social_influence_vote(
            experiment_id="exp-1",
            neighborhood="Mission",
            response={"agent_id": "agent-3", "agent_name": "Wei Chen", "vote": "Yes"},
        )
        experiments.append_social_influence_vote(
            experiment_id="exp-1",
            neighborhood="Mission",
            response={"agent_id": "agent-9", "agent_name": "Leilani Cruz", "vote": "No"},
        )

        self.assertEqual(experiments.social_influence_vote_counts("Mission"), {
            "yes": 1,
            "no": 1,
            "total": 2,
        })
        data = json.loads(self.vote_path.read_text())
        self.assertEqual(len(data["neighborhoods"]["Mission"]), 2)

        experiments.clear_social_influence_vote_file()
        self.assertEqual(json.loads(self.vote_path.read_text()), {})

    def test_experiment_passes_prior_same_neighborhood_votes_only(self) -> None:
        agents = [
            agent("agent-1", "Mateo", "Sunset"),
            agent("agent-2", "James", "Mission"),
            agent("agent-3", "Wei", "Sunset"),
        ]
        llm_results = [
            {"vote": "Yes", "reason": "One.", "response": "Yes - One."},
            {"vote": "No", "reason": "Two.", "response": "No - Two."},
            {"vote": "No", "reason": "Three.", "response": "No - Three."},
        ]

        with (
            patch.object(experiments, "load_all_agents", return_value=agents),
            patch.object(experiments, "run_behavioral_scenario", side_effect=llm_results),
            patch.object(experiments, "_save_log"),
        ):
            result = experiments.run_behavioral_scenario_experiment(
                prompt="Vote?",
                use_social_influence=True,
            )

        self.assertEqual(result["responses"][0]["neighborhood_votes_seen"], {
            "yes": 0,
            "no": 0,
            "total": 0,
        })
        self.assertEqual(result["responses"][1]["neighborhood_votes_seen"], {
            "yes": 0,
            "no": 0,
            "total": 0,
        })
        self.assertEqual(result["responses"][2]["neighborhood_votes_seen"], {
            "yes": 1,
            "no": 0,
            "total": 1,
        })
        self.assertEqual(json.loads(self.vote_path.read_text()), {})


if __name__ == "__main__":
    unittest.main()
