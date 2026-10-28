"""Lifecycle checks using tiny artificial evidence and temporary directories."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from biomedical_research.population_framework import runner


GENERATE = '''import numpy as np
import pandas as pd

def generate(n, seed, evidence, context="target"):
    x = evidence["mu"] + np.arange(n, dtype=float) - (n - 1) / 2
    y = 2 * x + evidence.get("delta", 0)
    return pd.DataFrame({"x": x, "y": y})
'''


class RunnerLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.case_path = self.root / "case.json"
        self.case = {
            "schema_version": 1,
            "case_id": "artificial_fixture",
            "stages": {
                "initial": {"packet": "initial.json", "evidence": [{"id": "marginal"}]},
                "updated": {"packet": "updated.json", "evidence": [
                    {"id": "marginal"}, {"id": "new_relation"}]},
            },
            "contexts": {
                name: {"n": 8, "seeds": [11, 12], "schema": {
                    "x": {"type": "number"}, "y": {"type": "number"}}}
                for name in ("source", "target")
            },
            "checks": [
                {"id": "known_source_mean", "context": "source", "role": "source_fidelity",
                 "evidence_ids": ["marginal"], "stages": ["initial", "updated"],
                 "statistic": {"kind": "mean", "column": "x"},
                 "expected": 2., "tolerance_abs": 1e-12},
                {"id": "later_relation", "context": "source", "role": "source_fidelity",
                 "evidence_ids": ["new_relation"], "stages": ["updated"],
                 "statistic": {"kind": "ols_intercept", "x": "x", "y": "y"},
                 "expected": 7., "tolerance_abs": 1e-12},
            ],
        }
        self.save(self.case_path, self.case)
        self.save(self.root / "initial.json", {"mu": 2.})
        self.save(self.root / "updated.json", {"mu": 2., "delta": 7.})

    @staticmethod
    def save(path, obj):
        Path(path).write_text(json.dumps(obj), encoding="utf-8")

    def stage(self, name="initial", directory="run", parent=None):
        path = self.root / directory
        runner.stage(self.case_path, name, path, parent)
        return path

    def test_experimental_request_is_snapshotted_and_locked(self):
        template = self.root / "policy.md"
        template.write_text("Experimental policy v1", encoding="utf-8")
        run = self.root / "policy_run"
        runner.stage(self.case_path, "initial", run, request_template=template)
        template.write_text("Later policy", encoding="utf-8")
        self.assertEqual((run / "request.md").read_text(encoding="utf-8"), "Experimental policy v1")
        self.submit(run)
        (run / "request.md").write_text("Tampered request", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Delivered inputs changed"):
            runner.execute(run)

    def submit(self, run, code=GENERATE, updated=False, **overrides):
        evidence = [{"id": "marginal", "action": "use", "reason": "Artificial supplied mean."}]
        if updated:
            evidence.append({"id": "new_relation", "action": "use", "reason": "Artificial supplied intercept."})
        decision = {
            "action": "revise" if updated else "build",
            "model_family": "Deterministic artificial test fixture",
            "evidence_use": evidence,
            "assumptions": ["Test fixture only; no population interpretation."],
            "open_questions": [],
            "component_map": [{"id": "test_component", "functions": ["generate"],
                               "evidence_ids": [item["id"] for item in evidence],
                               "target_role": "Exercise the lifecycle only"}],
            "changes": ([{"component": "test_component", "evidence_ids": ["new_relation"],
                          "reason": "New artificial intercept supplied", "expected_effect": "Change y only"}]
                        if updated else []),
            "invariants": [],
            "influence_probes": [],
        }
        decision.update(overrides)
        (run / "generator.py").write_text(code, encoding="utf-8")
        self.save(run / "decision.json", decision)

    def initial_completed(self):
        run = self.stage()
        self.submit(run)
        self.assertEqual(runner.execute(run)["status"], "checks_passed")
        return run

    def test_two_stage_lifecycle_and_changed_evidence(self):
        initial = self.stage()
        self.submit(initial, influence_probes=[{"context": "target", "pointer": "/mu",
                    "delta": .125, "columns": ["x"], "expect": "changes"}])
        self.assertEqual(runner.execute(initial)["status"], "checks_passed")
        updated = self.stage("updated", "revision", initial)
        self.submit(updated, updated=True,
                    invariants=[{"context": "target", "columns": ["x"]}],
                    influence_probes=[{"context": "target", "pointer": "/delta",
                        "delta": .125, "columns": ["y"], "expect": "changes"}])
        self.assertEqual(runner.execute(updated)["status"], "checks_passed")
        delta = runner.read(updated / "evidence_delta.json")["changed_paths"]
        self.assertIn({"path": "/delta", "kind": "added"}, delta)
        report = runner.read(updated / "report.json")
        self.assertTrue(all(item["status"] == "pass" for item in report["invariants"]))
        self.assertFalse(report["real_target_outcomes_read_by_runner"])
        self.assertEqual(runner.verify(initial)["status"], "checks_passed")
        self.assertEqual(runner.verify(updated)["status"], "checks_passed")

    def test_initial_delivery_excludes_future_evidence_checks(self):
        run = self.stage()
        delivered = runner.read(run / "case.json")
        self.assertEqual(set(delivered["stages"]), {"initial"})
        self.assertNotIn("later_relation", [item["id"] for item in delivered["checks"]])
        self.assertNotIn("new_relation", json.dumps(delivered))

    def test_initial_delivery_excludes_future_values_in_unscoped_annotations(self):
        self.case["description"] = "Future-only artificial effect equals 153.887341."
        self.case["claim_limits"] = ["Future-only artificial correlation equals 0.783912641."]
        self.case["stages"]["initial"]["description"] = "Permitted initial-stage description."
        self.case["stages"]["initial"]["claim_limits"] = ["Permitted initial-stage limitation."]
        self.save(self.case_path, self.case)
        run = self.stage()
        delivered = runner.read(run / "case.json")
        serialized = json.dumps(delivered)
        self.assertNotIn("153.887341", serialized)
        self.assertNotIn("0.783912641", serialized)
        self.assertNotIn("Future-only", serialized)
        self.assertEqual(delivered["description"], "Permitted initial-stage description.")
        self.assertEqual(delivered["claim_limits"], ["Permitted initial-stage limitation."])

    def test_staged_inputs_cannot_change(self):
        run = self.stage()
        self.submit(run)
        self.save(run / "evidence.json", {"mu": 100})
        with self.assertRaisesRegex(ValueError, "Delivered inputs changed"):
            runner.execute(run)
        self.assertFalse((run / "samples").exists())

    def test_no_overwrite_and_committed_artifact_tamper_detection(self):
        run = self.initial_completed()
        original_manifest = (run / "manifest.json").read_bytes()
        with self.assertRaises(FileExistsError):
            runner.stage(self.case_path, "initial", run)
        with self.assertRaises(FileExistsError):
            runner.execute(run)
        self.assertEqual((run / "manifest.json").read_bytes(), original_manifest)
        with (run / "generator.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# Changed after commitment\n")
        with self.assertRaisesRegex(ValueError, "Committed run changed"):
            runner.verify(run)

    def test_engine_snapshot_is_local_and_tampering_is_detected(self):
        run = self.initial_completed()
        manifest = runner.read(run / "manifest.json")
        self.assertEqual(len(manifest["engine"]), 3)
        for relative, expected in manifest["engine"].items():
            self.assertFalse(Path(relative).is_absolute())
            self.assertEqual(runner.sha(run / relative), expected)
        # Verification must depend on the committed snapshot, not the current
        # source tree (which may have moved or changed for later runs).
        with patch.object(runner, "HERE", self.root / "unavailable_new_engine"):
            self.assertEqual(runner.verify(run)["status"], "checks_passed")
        snapshot = run / next(iter(manifest["engine"]))
        with snapshot.open("a", encoding="utf-8") as handle:
            handle.write("\n# Artificial snapshot tampering\n")
        with self.assertRaisesRegex(ValueError, "changed"):
            runner.verify(run)

    def test_failed_source_check_needs_revision(self):
        run = self.stage()
        self.submit(run, code=GENERATE.replace('x = evidence["mu"]', 'x = 1 + evidence["mu"]'))
        outcome = runner.execute(run)
        self.assertEqual(outcome["status"], "needs_revision")
        self.assertIn("known_source_mean", outcome["failed_checks"])
        self.assertEqual(runner.verify(run)["status"], "needs_revision")

    def test_exact_invariant_catches_changed_and_missing_columns(self):
        initial = self.initial_completed()
        for column in ("y", "missing_output"):
            with self.subTest(column=column):
                revised = self.stage("updated", f"revision_{column}", initial)
                self.submit(revised, updated=True,
                            invariants=[{"context": "target", "columns": [column]}])
                self.assertEqual(runner.execute(revised)["status"], "needs_revision")
                report = runner.read(revised / "report.json")
                self.assertTrue(all(item["status"] == "fail" for item in report["invariants"]))

    def test_no_op_automatically_checks_unclaimed_output_columns(self):
        initial = self.initial_completed()
        for changed in (False, True):
            with self.subTest(changed=changed):
                run = self.stage("initial", f"no_op_{changed}", initial)
                code = GENERATE.replace("y = 2 * x", "y = 1 + 2 * x") if changed else GENERATE
                self.submit(run, code=code, action="no_op",
                            invariants=[{"context": "target", "columns": ["x"]}])
                outcome = runner.execute(run)
                self.assertEqual(outcome["status"], "needs_revision" if changed else "checks_passed")
                report = runner.read(run / "report.json")
                self.assertTrue(all(item["passed"] for item in report["checks"]))
                claimed = [item for item in report["invariants"] if "origin" not in item]
                automatic = [item for item in report["invariants"] if item.get("origin") ==
                             "automatic_all_shared_output_columns_for_no_op"]
                self.assertTrue(claimed)
                self.assertTrue(all(item["status"] == "pass" for item in claimed))
                self.assertEqual(len(automatic), 4)  # Two contexts, two fixed seeds.
                for item in automatic:
                    self.assertIn("y", item["columns"])
                    self.assertEqual(item["status"], "fail" if changed else "pass")

    def test_input_unused_is_detected_by_numerical_probe(self):
        run = self.stage()
        self.submit(run, code=GENERATE.replace('evidence["mu"]', '2.'),
                    influence_probes=[{"context": "target", "pointer": "/mu", "delta": .5,
                                       "columns": ["x"], "expect": "changes"}])
        self.assertEqual(runner.execute(run)["status"], "needs_revision")
        report = runner.read(run / "report.json")
        self.assertTrue(all(item["passed"] for item in report["checks"]))
        self.assertFalse(report["influence_probes"][0]["passed"])
        self.assertEqual(report["influence_probes"][0]["max_abs_record_difference"], 0.)

    def test_categorical_influence_probes_use_exact_equality(self):
        for context in self.case["contexts"].values():
            context["schema"].update({
                "arm": {"type": "category", "values": ["a", "b"]},
                "fixed_arm": {"type": "category", "values": ["stable"]},
            })
        self.save(self.case_path, self.case)
        code = GENERATE.replace(
            'return pd.DataFrame({"x": x, "y": y})',
            'return pd.DataFrame({"x": x, "y": y, '
            '"arm": "b" if evidence["mu"] > 2.25 else "a", "fixed_arm": "stable"})')
        for wrong_expectation in (False, True):
            with self.subTest(wrong_expectation=wrong_expectation):
                run = self.stage(directory=f"categorical_{wrong_expectation}")
                self.submit(run, code=code, influence_probes=[
                    {"context": "target", "pointer": "/mu", "delta": .5,
                     "columns": ["arm"], "expect": "unchanged" if wrong_expectation else "changes"},
                    {"context": "target", "pointer": "/mu", "delta": .5,
                     "columns": ["fixed_arm"], "expect": "unchanged"},
                    {"context": "target", "pointer": "/mu", "delta": .5,
                     "columns": ["x", "arm"], "expect": "changes"},
                ])
                result = runner.execute(run)
                self.assertEqual(result["status"], "needs_revision" if wrong_expectation else "checks_passed")
                probes = runner.read(run / "report.json")["influence_probes"]
                self.assertIsNone(probes[0]["max_abs_record_difference"])
                self.assertEqual(probes[0]["equal_rows"], 0)
                self.assertEqual(probes[0]["passed"], not wrong_expectation)
                self.assertIsNone(probes[1]["max_abs_record_difference"])
                self.assertEqual(probes[1]["equal_rows"], 8)
                self.assertTrue(probes[1]["passed"])
                self.assertEqual(probes[2]["max_abs_record_difference"], .5)
                self.assertTrue(probes[2]["passed"])

    def test_generation_failure_preserves_failed_manifest(self):
        run = self.stage()
        self.submit(run, code='def generate(n, seed, evidence, context="target"):\n'
                             '    raise RuntimeError("intentional artificial failure")\n')
        result = runner.execute(run)
        self.assertEqual(result["status"], "failed")
        self.assertIn("intentional artificial failure", result["errors"][0]["message"])
        self.assertEqual(runner.verify(run)["status"], "failed")
        self.assertTrue((run / "feedback.json").exists())
        with self.assertRaises(FileExistsError):
            runner.execute(run)

    def test_invariant_row_count_mismatch_is_not_pass(self):
        initial = self.initial_completed()
        changed = deepcopy(self.case)
        changed["contexts"]["target"]["n"] = 10
        self.save(self.case_path, changed)
        revised = self.stage("updated", "revision", initial)
        self.submit(revised, updated=True, invariants=[{"context": "target", "columns": ["x"]}])
        self.assertEqual(runner.execute(revised)["status"], "needs_revision")
        report = runner.read(revised / "report.json")
        self.assertTrue(all(item["status"] == "not_testable" for item in report["invariants"]))


if __name__ == "__main__":
    unittest.main()
