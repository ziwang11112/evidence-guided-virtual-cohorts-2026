"""Guard checks using temporary metadata and opaque non-cohort placeholder bytes."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import run_evaluation as controller


def schedule_release():
    slots = []
    for stage in ("initial", "final"):
        for seed in controller.SEEDS:
            slots.append({"builder": "A", "stage": stage, "seed": seed, "status": "success",
                          "run_id": f"initial-{seed}", "stage_candidate": f"candidates/{stage}",
                          "execution_candidate": "candidates/initial", "receipt_sha256": "a"*64,
                          "output_sha256": "b"*64,
                          "retained_from": {"stage": "initial", "seed": seed} if stage == "final" else None})
    return {"schema": "ensanut_evaluation_release_v1", "issuer": "root", "status": "approved",
            "effects_authorized": True, "purpose": "fixed_target_evaluation_once", "release_id": "artificial-guard",
            "builders": [{"id": "A", "bundle": "bundles/A"}], "schedule": slots}


def freeze_pair():
    def frozen(stage):
        name = "candidates/"+stage
        return {"candidate": name, "revision": {"kind": "retain"}, "registry_snapshot": {"sha256": "r"},
                "commitments": {"task.json": "t", "sources/paper.pdf": "p",
                                **{name+"/"+key: key for key in ("generator.py", "model_spec.json", "evidence.json")},
                                name+"/decision.md": stage}}
    return frozen("initial"), frozen("final")


class EvaluationGuardTests(unittest.TestCase):
    def test_complete_retained_schedule_keeps_all_six_stage_seed_slots(self):
        builders, slots = controller.validate_schedule(schedule_release())
        self.assertEqual((len(builders), len(slots)), (1, 6))
        self.assertEqual(len({s["run_id"] for s in slots}), 3)

    def test_missing_duplicate_extra_and_wrong_seed_schedules_rejected(self):
        base = schedule_release()
        variants = [base["schedule"][:-1], base["schedule"]+[base["schedule"][0]],
                    base["schedule"][:-1]+[base["schedule"][0]]]
        wrong = copy.deepcopy(base["schedule"])
        wrong[0]["seed"] = 18101
        variants.append(wrong)
        for slots in variants:
            with self.assertRaises(controller.EvaluationError):
                controller.validate_schedule({**base, "schedule": slots})

    def test_effects_gate_rejects_before_any_binding_or_private_access(self):
        for changes in ({"effects_authorized": False}, {"issuer": "builder"}, {"status": "draft"}):
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root/"EVALUATION_RELEASE.json").write_text(json.dumps({**schedule_release(), **changes}))
                with patch.object(controller, "bound_bytes", side_effect=AssertionError("Binding access before approval")):
                    with self.assertRaises(controller.EvaluationError):
                        controller.verify_release(root)

    def test_builder_budget_and_distinct_bundle_enforced(self):
        release = schedule_release()
        for builders in ([], [{"id": x, "bundle": x} for x in "ABC"],
                          [{"id": "A", "bundle": "same"}, {"id": "B", "bundle": "same"}]):
            with self.assertRaises(controller.EvaluationError):
                controller.validate_schedule({**release, "builders": builders})

    def test_failed_receipt_must_not_release_an_output(self):
        release = schedule_release()
        release["schedule"][0]["status"] = "failed"
        with self.assertRaises(controller.EvaluationError):
            controller.validate_schedule(release)
        release["schedule"][0]["output_sha256"] = None
        controller.validate_schedule(release)

    def test_path_traversal_devices_and_absolute_paths_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for name in ("../private.csv", "a/../../private.csv", "C:/private.csv", "a\\b", "/absolute", "aux.txt", "a/CON", "a./b"):
                with self.subTest(name=name), self.assertRaises(controller.EvaluationError):
                    controller.safe_path(Path(temp), name)

    def test_mismatched_binding_hash_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/"note.json").write_text("{}")
            with self.assertRaisesRegex(controller.EvaluationError, "binding_hash_mismatch"):
                controller.bound_bytes(root, {"path": "note.json", "sha256": "0"*64}, {})

    def test_retention_allows_new_decision_but_rejects_scientific_or_source_change(self):
        initial, final = freeze_pair()
        controller.retained_identity(initial, final)
        for key in ("candidates/final/generator.py", "candidates/final/model_spec.json",
                    "candidates/final/evidence.json", "task.json", "sources/paper.pdf"):
            changed = copy.deepcopy(final)
            changed["commitments"][key] = "changed"
            with self.subTest(key=key), self.assertRaises(controller.EvaluationError):
                controller.retained_identity(initial, changed)

    def test_retention_requires_retain_decision_and_same_registry(self):
        initial, final = freeze_pair()
        final["revision"]["kind"] = "revise"
        with self.assertRaises(controller.EvaluationError):
            controller.retained_identity(initial, final)
        initial, final = freeze_pair()
        final["registry_snapshot"] = {"sha256": "changed"}
        with self.assertRaises(controller.EvaluationError):
            controller.retained_identity(initial, final)

    def test_existing_results_blocks_every_new_attempt_before_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/"analysis/results").mkdir(parents=True)
            with patch.object(controller, "verify_release", side_effect=AssertionError("repeat gate called")):
                with self.assertRaisesRegex(controller.EvaluationError, "results_exist_no_repeat"):
                    controller.run_authorized(root)

    def test_direct_output_and_unbound_parent_rejected_before_recursive_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            builder = {"bundle": "bundles/A", "initial_candidate": "candidates/initial", "final_candidate": "candidates/final"}
            for stage in ("initial", "final"):
                directory = root/builder["bundle"]/builder[stage+"_candidate"]
                directory.mkdir(parents=True)
                (directory/"generator.py").write_text("opaque program fixture")
                frozen = {"route": "generator.py", "candidate": builder[stage+"_candidate"],
                          "revision_index": 0 if stage == "initial" else 1,
                          "parent": None if stage == "initial" else {"candidate": builder["initial_candidate"],
                              "receipt_path": builder["initial_candidate"]+"/freeze.json", "sha256": builder["initial_freeze_sha256"]}}
                body = json.dumps(frozen).encode()
                (directory/"freeze.json").write_bytes(body)
                builder[stage+"_freeze_sha256"] = controller.digest(body)
            controller.preflight_freezes(root, builder, {})
            initial = root/builder["bundle"]/builder["initial_candidate"]
            (initial/"generated.csv").write_bytes(b"OPAQUE PLACEHOLDER: NOT COHORT DATA")
            with self.assertRaisesRegex(controller.EvaluationError, "only_frozen_program_candidates"):
                controller.preflight_freezes(root, builder, {})
            (initial/"generated.csv").unlink()
            final = root/builder["bundle"]/builder["final_candidate"]/"freeze.json"
            frozen = json.loads(final.read_bytes())
            frozen["parent"]["candidate"] = "candidates/unbound"
            body = json.dumps(frozen).encode()
            final.write_bytes(body)
            builder["final_freeze_sha256"] = controller.digest(body)
            with self.assertRaisesRegex(controller.EvaluationError, "final_parent_mismatch"):
                controller.preflight_freezes(root, builder, {})

    def test_import_is_inert_and_help_does_not_invoke_controller(self):
        path = Path(controller.__file__)
        source = path.read_text(encoding="utf-8")
        with patch.object(Path, "read_bytes", side_effect=AssertionError("import file read")), \
                patch.object(Path, "mkdir", side_effect=AssertionError("import write")):
            exec(compile(source, str(path), "exec"), {"__name__": "inert_import_check", "__file__": str(path)})
        with patch.object(controller, "run_authorized", side_effect=AssertionError("help ran evaluation")), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                controller.main(["--help"])
            self.assertEqual(caught.exception.code, 0)

    def test_success_metadata_gate_does_not_open_generated_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prefix = "bundles/A/executions/run1"
            run = root/prefix
            limits = {"seed": 18203, "timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 20000000, "log_bytes": 100000}
            columns = [{"name": c} for c in ("row_id", "age", "female", "bmi", "glucose", "hba1c")]
            task = {"task_id": "artificial-guard", "columns": columns}
            scientific = {"task.json": b"task metadata", "model_spec.json": b"spec metadata", "generator.py": b"program metadata"}
            scientific_hashes = {k: controller.digest(v) for k, v in scientific.items()}
            worker = b"opaque worker fixture"
            worker_hash = controller.digest(worker)
            bodies = {"input/"+k: v for k, v in scientific.items()}
            bodies.update({"input/worker.py": worker,
                "runtime_manifest.json": b"{}", "stdout.log": b"", "stderr.log": b"",
                "output/generated.csv": b"OPAQUE PLACEHOLDER: NOT A COHORT TABLE",
                "input_bindings.json": json.dumps({"candidate_freeze_sha256": "f"*64, "files": scientific_hashes}).encode(),
                "input/request.json": json.dumps({"schema_version": 1, "task_id": task["task_id"], **limits}).encode(),
                "launch.json": json.dumps({"runtime": {"backend": "artificial"}, "worker_sha256": worker_hash,
                                           "isolation": "curated_bubblewrap_mounts_no_network", "argv": ["frozen-command"]}).encode(),
                "output/worker_report.json": json.dumps({"status": "completed", "generator_started": True,
                                                        "rows": 2000, "columns": [c["name"] for c in columns]}).encode()})
            for name, body in bodies.items():
                path = run/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
            receipt = {"schema_version": 1, "kind": "generator_execution", "run_id": "run1", "status": "success",
                       "candidate": "candidates/initial", "candidate_freeze_sha256": "f"*64, "route": "generator.py",
                       "isolation_scope": "generator_process_only", "agent_isolation": "not_provided", "scientific_validity": "not_assessed",
                       "limits": limits, "generator_executed": True, "runtime": {"backend": "artificial"}, "error": None,
                       "process": {"returncode": 0, "host_timeout": False}, "files": {k: controller.digest(v) for k, v in bodies.items()}}
            receipt_body = json.dumps(receipt).encode()
            (run/"execution.json").write_bytes(receipt_body)
            slot = {"run_id": "run1", "seed": 18203, "status": "success", "execution_candidate": "candidates/initial",
                    "execution_freeze_sha256": "f"*64, "receipt_sha256": controller.digest(receipt_body),
                    "output_sha256": receipt["files"]["output/generated.csv"]}
            frozen = {"candidate": "candidates/initial", "commitments": {
                (k if k == "task.json" else "candidates/initial/"+k): v for k, v in scientific_hashes.items()}}
            api = SimpleNamespace(DEFAULT_RUNTIME={"backend": "artificial"}, _limits=lambda **kw: kw,
                                  _files=lambda p: list(bodies)+["execution.json"], _command=lambda *args: ["frozen-command"])
            original = Path.read_bytes
            def guarded(path):
                if path.name == "generated.csv":
                    raise AssertionError("CSV bytes accessed during metadata gate")
                return original(path)
            with patch.object(Path, "read_bytes", guarded):
                observed = controller.receipt_metadata(root, "bundles/A", slot, frozen, task, api,
                                                       {"project:cohort_harness/_worker.py": worker_hash})
            self.assertEqual(observed["status"], "success")
            # An extra output is rejected before any artifact read, even if receipt-bound.
            receipt["files"]["output/extra.csv"] = "0"*64
            receipt_body = json.dumps(receipt).encode()
            (run/"execution.json").write_bytes(receipt_body)
            slot["receipt_sha256"] = controller.digest(receipt_body)
            with patch.object(Path, "read_bytes", guarded), self.assertRaisesRegex(controller.EvaluationError, "unexpected_execution_artifacts"):
                controller.receipt_metadata(root, "bundles/A", slot, frozen, task, api, {})
            del receipt["files"]["output/extra.csv"]
            # A failed receipt returns without reading staged files or partial outputs.
            receipt["status"] = "failed"
            receipt_body = json.dumps(receipt).encode()
            (run/"execution.json").write_bytes(receipt_body)
            slot.update(status="failed", output_sha256=None, receipt_sha256=controller.digest(receipt_body))
            api._files = lambda p: (_ for _ in ()).throw(AssertionError("failed artifacts opened"))
            with patch.object(Path, "read_bytes", guarded):
                self.assertEqual(controller.receipt_metadata(root, "bundles/A", slot, frozen, task, api, {})["status"], "failed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
