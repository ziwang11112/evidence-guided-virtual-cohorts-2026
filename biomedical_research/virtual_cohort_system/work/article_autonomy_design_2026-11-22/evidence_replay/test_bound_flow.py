"""Check a fresh v2 session with the default entry point and no network."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_flow import ARTICLE, ID, REQUEST, SOURCE, load, proposal
from evidence_replay import bound_flow, flow
from run_with_evidence_replay import send_new_design


class TestFreshBoundFlow(unittest.TestCase):
    def test_units_declared_once_and_revised_rows_rechecked(self):
        fact = deepcopy(SOURCE)
        del fact["operator"]["units"]
        design = {"population": "Whole study population",
                  "columns": [{"name": "z", "unit": "u"}],
                  "analyses": ["Mean Z"], "evidence": {"evidence_checks": [fact]},
                  "model_plan": "One column", "limitations": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def reply(session, stage, prompt, cap):
                if stage == "design":
                    self.assertIn("list of objects with name and unit", prompt)
                    return design
                if stage == "build":
                    return proposal(2.0)
                self.assertEqual(stage, "review")
                feedback = load(root / "source_feedback_sent.json")
                row = feedback["runs"][0]["checks"][0]
                self.assertEqual((row["id"], row["value"], row["status"]),
                                 (ID, 2.0, "outside_precision"))
                self.assertIn("outside_precision", prompt)
                return {"action":"revise", "candidate":proposal(4.2),
                        "reason":"Use Table 1.", "dispositions":{ID:"Corrected mean."},
                        "conclusions":"Recheck the corrected mean."}

            with patch.object(flow, "_send", side_effect=reply) as transport:
                result = bound_flow.run(root, ARTICLE, REQUEST, send=send_new_design)
            self.assertEqual([call.args[1] for call in transport.call_args_list],
                             ["design", "build", "review"])
            self.assertEqual(load(root / "design_as_authored.json"), design)
            self.assertNotIn("units", fact["operator"])
            log = load(root / "unit_bindings.json")["items"][0]
            self.assertEqual((log["status"], log["unit_sources"]["z"]),
                             ("bound_from_design", "columns[0].unit"))
            self.assertEqual(result["final_numerically_recomputed"], 3)
            for table in result["runs"]:
                self.assertEqual(table["checks"][0]["status"], "within_precision")
                self.assertAlmostEqual(table["checks"][0]["value"], 4.2)


if __name__ == "__main__":
    unittest.main()
