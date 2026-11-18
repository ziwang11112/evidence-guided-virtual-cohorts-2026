"""New economy boundary checks only: no API, credentials, or author code execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import socket
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


client = module("independent_economy_client", "provider_client.py")
stages = module("independent_economy_execution", "execute_stages.py")
evaluation = module("independent_economy_evaluation", "evaluate_stages.py")
controller = module("independent_economy_controller", "run_economy.py")


class EconomyBoundaries(unittest.TestCase):
    def setUp(self):
        self.network = patch.object(socket.socket, "connect", side_effect=AssertionError("network forbidden"))
        self.network.start()
        self.addCleanup(self.network.stop)

    def test_unchanged_approved_input_bytes(self):
        manifest = json.loads((ROOT / "INPUT_ASSEMBLY.json").read_text(encoding="utf-8"))
        for rel, record in manifest["copied_files"].items():
            with self.subTest(path=rel):
                current = (ROOT / rel).read_bytes()
                self.assertEqual(current, Path(record["from"]).read_bytes())
                self.assertEqual(hashlib.sha256(current).hexdigest(), record["sha256"])

    def test_provider_and_total_budget_restrictions(self):
        self.assertEqual(set(client.CONFIGS), {"OA_SOL", "OA_ASTRA", "DS_PRO"})
        self.assertEqual(client.CAPS, {"openai": 8.0, "deepseek": 2.0})
        self.assertEqual(sum(client.CAPS.values()), 10)

    def test_ledger_accumulates_both_phases_and_unknown_charge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [("initial/a", "openai", 2, 1), ("review/b", "openai", 3, None),
                    ("initial/c", "deepseek", 1, .2)]
            for name, provider, reserve, cost in rows:
                folder = root / "calls" / name
                folder.mkdir(parents=True)
                (folder / "reservation.json").write_text(json.dumps({"provider": provider, "reserved_usd": reserve}))
                (folder / "receipt.json").write_text(json.dumps({"tariff_cost_usd": cost}))
            unfinished = root / "calls" / "review/d"
            unfinished.mkdir(parents=True)
            (unfinished / "reservation.json").write_text(json.dumps({"provider": "openai", "reserved_usd": .5}))
            self.assertEqual(client.ledger_accounted(root, "openai"), 4.5)
            self.assertEqual(client.ledger_accounted(root, "deepseek"), .2)

    def test_over_budget_does_not_dispatch_or_create_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(client, "credentials", return_value={"openai": "fake", "deepseek": "fake"}), \
                 patch.object(client, "ledger_accounted", return_value=7.99), \
                 patch.object(client.requests, "post", side_effect=AssertionError("API forbidden")) as post:
                with self.assertRaisesRegex(ValueError, "budget exhausted before dispatch"):
                    client.call_once(root, "review/fixture", "OA_SOL", "offline fixture")
                post.assert_not_called()
                self.assertFalse((root / "calls").exists())

    def test_existing_call_is_never_dispatched_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "calls/review/fixture").mkdir(parents=True)
            with patch.object(client, "credentials", return_value={"openai": "fake", "deepseek": "fake"}), \
                 patch.object(client.requests, "post", side_effect=AssertionError("API forbidden")) as post:
                with self.assertRaises(FileExistsError):
                    client.call_once(root, "review/fixture", "OA_SOL", "offline fixture")
                post.assert_not_called()

    def test_seeds_and_table_count_are_disjoint_and_fixed(self):
        self.assertEqual(stages.SLOTS, {"diagnostic": 6, "evaluation": 36})
        self.assertEqual(stages.MAX_TABLES, 42)
        self.assertEqual(stages.N_ROWS, 3000)
        self.assertFalse(set(stages.SEEDS["diagnostic"]) & set(stages.SEEDS["evaluation"]))
        self.assertEqual(stages.SEEDS["diagnostic"], [41001, 41003, 41007])
        self.assertEqual(stages.SEEDS["evaluation"], [42001, 42003, 42007])

    def test_schedule_rejects_benchmark_substitution_and_duplicate_arm(self):
        rows = []
        branches = []
        for case in stages.CASES:
            for suffix, model, role in [("A", "OA_SOL", "paired_parent"), ("B", "OA_SOL", "benchmark"),
                                        ("C", "OA_ASTRA", "benchmark"), ("D", "DS_PRO", "benchmark")]:
                rows.append({"parent_id": case + suffix, "case_id": case, "model_config": model, "role": role})
            for arm in ["feedback", "second_look"]:
                branches.append({"branch_id": case + arm, "parent_id": case + "A", "arm": arm})
        stages.schedule(rows, branches)
        changed = [dict(b) for b in branches]
        changed[0]["parent_id"] = rows[1]["parent_id"]
        with self.assertRaises(Exception):
            stages.schedule(rows, changed)
        changed = [dict(b) for b in branches]
        changed[0]["arm"] = changed[1]["arm"]
        with self.assertRaises(Exception):
            stages.schedule(rows, changed)

    def test_ordinary_review_cannot_read_diagnostic_payload(self):
        initial = {"branches": [{"branch_id": "ordinary", "parent_id": "A", "arm": "second_look"}]}
        with patch.object(evaluation.host, "verify_initial", return_value=initial), \
             patch.object(evaluation.host, "verify_diagnostic_reports", return_value={"reports": {}}), \
             patch.object(evaluation.host, "read", side_effect=AssertionError("payload must not be read")) as read:
            with self.assertRaisesRegex(Exception, "Ordinary second-look"):
                evaluation.feedback_for("ordinary")
            read.assert_not_called()

    def test_feedback_rejects_another_parents_payload(self):
        initial = {"branches": [{"branch_id": "feedback", "parent_id": "A", "arm": "feedback"}]}
        with patch.object(evaluation.host, "verify_initial", return_value=initial), \
             patch.object(evaluation.host, "verify_diagnostic_reports", return_value={"reports": {"A": {"path": "unused"}}}), \
             patch.object(evaluation.host, "safe", return_value=Path("unused")), \
             patch.object(evaluation.host, "read", return_value={"parent_id": "B"}):
            with self.assertRaisesRegex(Exception, "Feedback parent mismatch"):
                evaluation.feedback_for("feedback")

    def test_reference_read_requires_closed_evaluation(self):
        with patch.object(evaluation.host, "verify_stage_closure", side_effect=ValueError("not closed")) as gate, \
             patch.object(evaluation.host, "read", side_effect=AssertionError("reference must not be read")) as read:
            with self.assertRaisesRegex(ValueError, "not closed"):
                evaluation.references_after_evaluation()
            gate.assert_called_once_with("evaluation")
            read.assert_not_called()

    def test_review_payloads_share_exact_parent_and_only_feedback_suffix_differs(self):
        plan = json.loads((ROOT / "RUN_PLAN.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "REVIEW_INSTRUCTION.txt").write_bytes((ROOT / "REVIEW_INSTRUCTION.txt").read_bytes())
            parents = []
            reports = {}
            payloads = {}
            for parent in plan["parents"]:
                record = dict(parent, status="sealed", candidate_path="unused")
                parents.append(record)
                prompt = root / parent["prompt_path"]
                prompt.parent.mkdir(parents=True, exist_ok=True)
                prompt.write_bytes((ROOT / parent["prompt_path"]).read_bytes())
                artifact_path = root / "calls/initial" / parent["parent_id"] / "artifact.json"
                artifact_path.parent.mkdir(parents=True)
                artifact = {"model_spec": {"fixture_parent": parent["parent_id"]}, "generator_py": "# inert fixture",
                            "decision_record": {"fixture": "same parent"}}
                artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
                if parent["role"] == "paired_parent":
                    payload = {"parent_id": parent["parent_id"], "generated_fixture": "no target values"}
                    diag = root / "_host_only/diagnostic_reports" / (parent["parent_id"] + ".json")
                    diag.parent.mkdir(parents=True, exist_ok=True)
                    diag.write_text(json.dumps(payload), encoding="utf-8")
                    reports[parent["parent_id"]] = {"path": diag.relative_to(root).as_posix(), "sha256": client.sha(diag)}
                    payloads[parent["parent_id"]] = payload
            (root / "DIAGNOSTIC_CLOSURE.json").write_text("{}")
            branches = {b["branch_id"]: b for b in plan["branches"]}
            calls = []
            def own_feedback(branch_id):
                calls.append(branch_id)
                branch = branches[branch_id]
                self.assertEqual(branch["arm"], "feedback")
                return payloads[branch["parent_id"]]
            with patch.object(controller, "U", root), patch.object(controller, "verify", return_value=plan), \
                 patch.object(evaluation.host, "verify_initial", return_value={"records": parents, "branches": plan["branches"]}), \
                 patch.object(evaluation.host, "verify_stage_closure", return_value={}), \
                 patch.object(evaluation.host, "verify_diagnostic_reports", return_value={"reports": reports}), \
                 patch("evaluate_stages.feedback_for", side_effect=own_feedback), redirect_stdout(StringIO()):
                controller.prepare_reviews()
            inputs = json.loads((root / "REVIEW_INPUTS.json").read_text(encoding="utf-8"))
            self.assertEqual(len(inputs["rows"]), 4)
            self.assertEqual(set(calls), {b["branch_id"] for b in plan["branches"] if b["arm"] == "feedback"})
            for parent in payloads:
                pair = {r["arm"]: r for r in inputs["rows"] if r["parent_id"] == parent}
                ordinary = (root / pair["second_look"]["prompt_path"]).read_text(encoding="utf-8")
                feedback = (root / pair["feedback"]["prompt_path"]).read_text(encoding="utf-8")
                prefix, suffix = feedback.split("\n\nRECORDED_OBSERVATIONS_OF_YOUR_OWN_GENERATOR\n")
                self.assertEqual(prefix, ordinary)
                self.assertEqual(json.loads(suffix), payloads[parent])
                self.assertEqual(pair["feedback"]["initial_artifact_sha256"], pair["second_look"]["initial_artifact_sha256"])
                self.assertIsNone(pair["second_look"]["diagnostic_path"])

    def test_candidate_reuse_rejects_host_modified_scientific_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "calls/initial/fixture"
            source.mkdir(parents=True)
            artifact = {"model_spec": {"x": 1}, "generator_py": "# inert fixture", "decision_record": {"unchanged": True}}
            (source / "artifact.json").write_text(json.dumps(artifact), encoding="utf-8")
            (root / "task.json").write_text("{}")
            with patch.object(controller, "U", root):
                candidate = controller.copy_candidate("initial", "fixture", "task.json")
                (root / candidate / "generator.py").write_text("# host modification")
                with self.assertRaises(AssertionError):
                    controller.copy_candidate("initial", "fixture", "task.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
