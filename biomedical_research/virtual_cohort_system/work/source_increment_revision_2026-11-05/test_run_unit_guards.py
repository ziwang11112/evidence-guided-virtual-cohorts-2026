"""Small controller-only tests. No generator, network, target, or clinical rows.

All mutations use temporary fixtures under this directory. Adapter/semantic
entry points are mocked; cached-reference reads/hashes raise a sentinel error.
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import inspect
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("source_increment_controller_test", HERE / "run_unit.py")
unit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(unit)


class ControllerGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="controller_fixture_", dir=HERE)
        self.root = Path(self.temporary.name).resolve()
        # Confirm the recursive cleanup target is this explicit local fixture.
        self.assertEqual(self.root.parent, HERE.resolve())
        self.addCleanup(self.temporary.cleanup)
        self.bundle = self.root / "bundle"
        self.candidate = "candidates/source_increment"
        (self.bundle / self.candidate).mkdir(parents=True)
        self.provider = self.root / "provider.py"
        self.endpoint = self.root / "endpoints.json"
        self.reference = self.root / "FORBIDDEN_REFERENCE.json"
        self.provider.write_text("# inert fixture only\n", encoding="utf-8")
        self.dump(self.endpoint, {"cases": {"ENSANUT2018": self.contract()}})
        for name in ("PROTOCOL.md", "PROTOCOL_CLARIFICATION_01.md", "CANDIDATE_REVIEW_GATE.json"):
            (self.root / name).write_text("fixture\n", encoding="utf-8")
        (self.bundle / self.candidate / "freeze.json").write_text("fixture freeze\n", encoding="utf-8")
        self.dump(self.root / "INPUT_MANIFEST.json", {
            "files": {}, "protocol_sha256": self.digest(self.root / "PROTOCOL.md")})
        self.commit = {
            "candidate": self.candidate,
            "freeze_sha256": self.digest(self.bundle / self.candidate / "freeze.json"),
            "candidate_review_sha256": self.digest(self.root / "CANDIDATE_REVIEW_GATE.json"),
            "protocol_sha256": self.digest(self.root / "PROTOCOL.md"),
            "clarification_sha256": self.digest(self.root / "PROTOCOL_CLARIFICATION_01.md"),
            "controller_sha256": self.digest(HERE / "run_unit.py"),
            "provider_sha256": self.digest(self.provider),
            "endpoint_contract_sha256": self.digest(self.endpoint),
            "reference_sha256_expected": "0" * 64,
            "seeds": list(unit.SEEDS), "n_rows": 3000,
        }
        self.dump(self.root / "FREEZE_COMMITMENT.json", self.commit)
        replacements = {
            "ROOT": self.root, "BUNDLE": self.bundle,
            "PROVIDER": self.provider, "PROVIDER_HASH": self.digest(self.provider),
            "ENDPOINTS": self.endpoint, "REFERENCE": self.reference,
            "REFERENCE_HASH": "0" * 64,
        }
        for key, value in replacements.items():
            self.enterContext(patch.object(unit, key, value))
        self.enterContext(patch.object(unit.lifecycle, "verify_candidate", return_value={"route": "generator.py"}))
        self.reference_accesses = []
        original_read, original_sha = unit.read, unit.sha

        def guarded_read(path):
            if Path(path) == self.reference:
                self.reference_accesses.append("parse")
                raise AssertionError("Reference parsed during fixture test")
            return original_read(path)

        def guarded_sha(path):
            if Path(path) == self.reference:
                self.reference_accesses.append("hash")
                raise AssertionError("Reference accessed before valid closure")
            return original_sha(path)

        self.enterContext(patch.object(unit, "read", side_effect=guarded_read))
        self.enterContext(patch.object(unit, "sha", side_effect=guarded_sha))

    @staticmethod
    def digest(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    @staticmethod
    def dump(path, value):
        Path(path).write_text(json.dumps(value), encoding="utf-8")

    @staticmethod
    def contract():
        return {"analyses": [{"id": "fixture_A", "unit": "1"}, {"id": "fixture_B", "unit": "1"}],
                "diagnostics": [{"id": "fixture_D", "unit": "1"}]}

    def payload(self):
        return {category: [{**row, "status": "computed", "value": np.float64(1.25)}
                           for row in rows]
                for category, rows in self.contract().items()}

    def adapter_mock(self, *, candidate=None, seed=None):
        def execute(bundle, candidate_arg, run_id, seed_arg, **kwargs):
            output = Path(bundle) / "executions" / run_id / "output"
            output.mkdir(parents=True)
            # Byte-binding placeholder; never parsed as a table.
            (output / "generated.csv").write_text("inert fixture bytes only\n", encoding="utf-8")
            receipt = {"status": "success", "candidate": candidate or candidate_arg,
                       "limits": {"seed": seed if seed is not None else seed_arg},
                       "route": "generator.py", "generator_executed": True,
                       "candidate_freeze_sha256": self.digest(self.bundle / self.candidate / "freeze.json")}
            self.dump(output.parent / "execution.json", receipt)
            return receipt

        execution_patch = self.enterContext(patch.object(unit.execution, "run_candidate", side_effect=execute))
        self.enterContext(patch.object(unit.execution, "verify_execution",
            side_effect=lambda bundle, rid: json.loads((Path(bundle) / "executions" / rid / "execution.json").read_text())))
        return execution_patch

    def test_unscheduled_and_nonnative_seeds_rejected_before_io(self):
        with patch.object(unit, "read", side_effect=AssertionError("Invalid seed reached file read")):
            for seed in (5299, 5304, 5301.0, "5301", True, np.int64(5301)):
                with self.subTest(seed=repr(seed)), self.assertRaisesRegex(ValueError, "seed|Seed"):
                    unit.run(seed)
        self.assertFalse((self.root / "attempts").exists())

    def test_duplicate_reservation_never_launches_adapter(self):
        execution_mock = self.adapter_mock()
        first = unit.run(5301)
        self.assertEqual(first["status"], "success")
        with self.assertRaises((FileExistsError, ValueError)):
            unit.run(5301)
        self.assertEqual(execution_mock.call_count, 1)

    def test_receipt_layout_matches_controller_bindings(self):
        self.adapter_mock()
        result = unit.run(5301)
        rid = result["run_id"]
        record = json.loads((self.root / "attempts" / f"{rid}.result.json").read_text())
        self.assertEqual(record["receipt_sha256"], self.digest(self.bundle / "executions" / rid / "execution.json"))
        self.assertEqual(record["table_sha256"], self.digest(self.bundle / "executions" / rid / "output" / "generated.csv"))
        self.assertTrue((self.root / "attempts" / f"{rid}.reserved.json").is_file())

    def test_wrong_receipt_candidate_rejected(self):
        self.adapter_mock(candidate="candidates/another_fixture")
        with self.assertRaises(ValueError):
            unit.run(5301)

    def test_wrong_receipt_seed_rejected(self):
        self.adapter_mock(seed=5302)
        with self.assertRaises(ValueError):
            unit.run(5301)

    def test_missing_or_open_closure_blocks_reference_access(self):
        with self.assertRaises((FileNotFoundError, ValueError)):
            unit.evaluate()
        self.dump(self.root / "CLOSURE.json", {"scientific_authoring_closed": False})
        with self.assertRaises(ValueError):
            unit.evaluate()
        self.assertEqual(self.reference_accesses, [])

    def test_incomplete_or_duplicate_closure_blocks_reference_access(self):
        closure = {"scientific_authoring_closed": True,
                   "freeze_commitment_sha256": self.digest(self.root / "FREEZE_COMMITMENT.json"),
                   "candidate": self.candidate, "slots": [], "physical_attempts": 0}
        for slots in ([], [{"seed": 5301, "run_id": "increment_5301_a1", "status": "failed"}] * 3):
            with self.subTest(slots=len(slots)):
                closure["slots"] = slots
                self.dump(self.root / "CLOSURE.json", closure)
                with self.assertRaises(ValueError):
                    unit.evaluate()
        self.assertEqual(self.reference_accesses, [])

    def test_changed_closed_result_blocks_reference_access(self):
        self.adapter_mock()
        for seed in unit.SEEDS:
            unit.run(seed)
        unit.close()
        path = self.root / "attempts" / "increment_5301_a1.result.json"
        path.write_text(path.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "artifact changed"):
            unit.evaluate()
        self.assertEqual(self.reference_accesses, [])

    def test_complete_mock_closure_reaches_only_guarded_reference_hash(self):
        self.adapter_mock()
        for seed in unit.SEEDS:
            unit.run(seed)
        unit.close()
        closed, _ = unit.verify_closed_unit()
        self.assertEqual([slot["seed"] for slot in closed["slots"]], list(unit.SEEDS))
        # Deliberately stop at the reference boundary, even for a valid fixture.
        with self.assertRaisesRegex(AssertionError, "Reference accessed"):
            unit.evaluate()
        self.assertEqual(self.reference_accesses, ["hash"])

    def test_numpy_real_values_and_unavailable_values_are_accepted(self):
        payload = self.payload()
        payload["analyses"][1]["value"] = np.float32(2.5)
        payload["diagnostics"][0].update(status="unavailable", value=None)
        unit.validate_payload(payload, self.contract())
        self.assertIs(type(payload["analyses"][0]["value"]), float)
        self.assertIs(type(payload["analyses"][1]["value"]), float)

    def test_missing_duplicate_extra_or_wrong_unit_endpoints_are_rejected(self):
        invalid = []
        payload = self.payload(); payload["analyses"].pop(); invalid.append(payload)
        payload = self.payload(); payload["analyses"][1] = copy.deepcopy(payload["analyses"][0]); invalid.append(payload)
        payload = self.payload(); payload["analyses"][1]["id"] = "unexpected"; invalid.append(payload)
        payload = self.payload(); payload["diagnostics"][0]["unit"] = "different"; invalid.append(payload)
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                unit.validate_payload(payload, self.contract())

    def test_boolean_and_nonfinite_values_are_rejected(self):
        for value in (True, np.bool_(True), float("nan"), np.float64("inf"), "1.25"):
            payload = self.payload(); payload["analyses"][0]["value"] = value
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                unit.validate_payload(payload, self.contract())

    def test_adapter_and_semantic_signatures_accept_controller_arguments(self):
        inspect.signature(unit.execution.run_candidate).bind(
            self.bundle, self.candidate, "fixture_5301", 5301,
            runtime=unit.execution.DEFAULT_RUNTIME, timeout_seconds=30,
            memory_mb=1536, output_bytes=20_000_000, log_bytes=100_000)
        inspect.signature(unit.execution.verify_execution).bind(self.bundle, "fixture_5301")
        inspect.signature(unit.lifecycle.freeze_candidate).bind(self.bundle, self.candidate)
        inspect.signature(unit.semantic.preflight).bind(self.bundle, self.candidate)
        inspect.signature(unit.semantic.collect_feedback).bind(self.bundle, self.candidate, "fixture_5301", "fixture_source")
        inspect.signature(unit.semantic.verify_feedback).bind(
            self.bundle, "fixture_source", candidate=self.candidate, run_id="fixture_5301")


if __name__ == "__main__":
    unittest.main(verbosity=2)
