"""Offline integration of author responses, isolated tables, replay and final review."""
import json
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from evidence_replay import flow


ARTICLE = "Development fixture. Table 1 reports a mean of 4.2 units of Z in the whole study population."
REQUEST = "Construct an illustrative cohort for this study and describe its mean Z."
ID = "whole_z_mean"
SOURCE = {
    "id": ID, "source": "Table 1", "claim": "Arithmetic mean of Z in the whole population",
    "population": "Whole study population", "provenance": "reported", "applicability": "same_population",
    "reference": {"value": 4.2, "decimals": 1, "unit": "u"},
    "operator": {"kind": "mean", "y": "z", "units": {"z": "u"}},
}

# The submitted diagnostic is deliberately constant. A real row replay can
# discriminate initial and revised datasets; simply rereading outputs cannot.
GENERATOR = """import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    n = int(spec['n'])
    return pd.DataFrame({'row_id': np.arange(n), 'z': np.full(n, spec['location'])})

def analyze(frame, spec):
    return {'authored_summary': 4.2}
"""


def proposal(location):
    return {"model_spec": {
        "population": "Whole study population",
        "location": location, "columns": [{"name": "z", "unit": "u"}],
        "outputs": [{"name": "authored_summary", "unit": "u", "meaning": "Self-reported summary"}],
        "alternatives": []},
        "generator_py": GENERATOR,
        "decision_record": {"structure": "Constant test column", "parameter_provenance": [],
                            "requested_estimands": [], "limitations": [], "checks_actually_performed": []}}


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


class TestSourceReplayFlow(unittest.TestCase):
    def exercise(self, action, verify_resume=False):
        calls = []
        # Avoid web access even if the speaker injection is accidentally ignored.
        with tempfile.TemporaryDirectory(prefix="replay_offline_") as folder, patch(
                "requests.sessions.Session.request", side_effect=AssertionError("Unexpected HTTP request")):
            root = Path(folder) / "episode"
            root.mkdir()
            sentinel = "held_out_answer_for_evaluator_only"
            (root / "evaluator_private.txt").write_text(sentinel, encoding="utf8")

            def speaker(session, stage, prompt, token_cap):
                self.assertEqual(Path(session).resolve(), root.resolve())
                self.assertNotIn(sentinel, prompt)
                self.assertNotIn(str(root), prompt)
                self.assertNotIn("final_source_replay.json", prompt)
                self.assertGreater(token_cap, 0)
                calls.append(stage)
                if stage == "design":
                    return {"population": "Whole study population", "columns": ["z"], "analyses": ["Mean Z"],
                            "evidence": {"evidence_checks": [SOURCE]}, "model_plan": "One column", "limitations": []}
                if stage == "build":
                    return proposal(2.0)
                self.assertEqual(stage, "review")
                self.assertTrue((root / "trial_source_replay.json").is_file())
                self.assertFalse((root / "final_source_replay.json").exists())
                self.assertIn(ID, prompt)
                self.assertIn("outside_precision", prompt)
                self.assertNotIn("local_error", prompt)
                self.assertNotIn("execution_trial", prompt)
                for final_seed in (823031, 823039, 823043):
                    self.assertNotIn(str(final_seed), prompt)
                reason = ("Use the published mean for Z." if action == "revise" else
                          "The trial mean is 2.0 and remains inconsistent with Table 1.")
                reply = {"action": action, "reason": reason, "conclusions": reason,
                         "dispositions": {ID: reason}}
                if action == "revise":
                    reply["candidate"] = proposal(4.2)
                return reply

            if verify_resume:
                def fake_post(url, **kwargs):
                    stage = ("design", "build", "review")[len(calls)]
                    body = json.loads(kwargs["data"])
                    answer = speaker(root, stage, body["input"], body["max_output_tokens"])
                    api = {"id":"offline-" + stage, "status":"completed", "model":body["model"],
                           "output":[{"type":"message", "content":[{"type":"output_text",
                                                                   "text":json.dumps(answer)}]}],
                           "usage":{"input_tokens":10, "output_tokens":15}}
                    response = Mock(status_code=200, headers={"x-request-id":"fixture-" + stage})
                    response.iter_content.return_value = [json.dumps(api).encode("utf8")]
                    return response

                with patch.object(flow.author.client, "credentials", return_value={"openai":"offline-test-key"}), patch(
                        "requests.post", side_effect=fake_post) as capture:
                    flow.run(root, ARTICLE, REQUEST)
                    self.assertEqual(capture.call_count, 3)
                with patch.object(flow.author.client, "credentials", side_effect=AssertionError("Resume requested a key")):
                    flow.run(root, ARTICLE, REQUEST)
                captures = sorted((root / "episodes/development/calls").iterdir())
                self.assertEqual(len(captures), 3)
                for folder in captures:
                    receipt = load(folder / "receipt.json")
                    self.assertEqual(receipt["status"], "received")
                    for name, field in [("request","request_sha256"), ("response_raw","response_raw_sha256"),
                                        ("reservation","reservation_sha256")]:
                        raw = (folder / (name + ".json")).read_bytes()
                        self.assertEqual(receipt[field], hashlib.sha256(raw).hexdigest())
                self.assertIn(json.dumps(load(root/"source_feedback_sent.json")),
                              load(captures[-1]/"request.json")["input"])
            else:
                flow.run(root, ARTICLE, REQUEST, send=speaker)
            self.assertEqual(calls, ["design", "build", "review"])
            trial = load(root / "trial_source_replay.json")
            final = load(root / "final_source_replay.json")
            self.assertEqual(trial["evidence_index"], final["evidence_index"])
            self.assertEqual(len(trial["runs"]), 1)
            self.assertEqual(len(final["runs"]), 3)
            for replay, value, status in [(trial, 2.0, "outside_precision"),
                                          (final, 4.2 if action == "revise" else 2.0,
                                           "within_precision" if action == "revise" else "outside_precision")]:
                for row in replay["runs"]:
                    self.assertEqual(row["scenario"], "primary")
                    self.assertEqual(len(row["checks"]), 1)
                    check = row["checks"][0]
                    self.assertEqual(check["id"], ID)
                    self.assertEqual(check["status"], status)
                    self.assertAlmostEqual(check["value"], value)

    def test_revised_candidate_rechecked_from_frozen_generated_rows_and_receipts(self):
        self.exercise("revise", verify_resume=True)

    def test_retained_disagreement_survives_final_replay(self):
        self.exercise("keep")


if __name__ == "__main__":
    unittest.main()
