"""Targeted routing mocks only: no generator, reference read, WSL call or clinical rows."""
from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile
import types
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bounded_controller_test", HERE.parent / "run_session.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_read = module.lifecycle.read_json
real_write = module.execution._write
real_sha = module.lifecycle.sha256
checks = []


def rejects(function, label):
    try:
        function()
    except (ValueError, FileExistsError):
        checks.append({"check": label, "status": "PASS"})
        return
    raise AssertionError("Did not reject: " + label)


class Fixture:
    def __init__(self, directory):
        self.bundle = directory / "bundle"
        self.local = directory / "session"
        self.bundle.mkdir(parents=True)
        self.local.mkdir()
        self.calls = []
        self.feedback_calls = []
        self.fail = False
        self.feedback_fail = False
        self.diagnostic_fail = False
        for name in ("c1", "c2", "other"):
            destination = self.bundle / "candidates" / name
            destination.mkdir(parents=True)
            real_write(destination / "freeze.json", {"mock": name})
        self.initial_sha = real_sha(self.bundle / "candidates/c1/freeze.json")
        def verify(bundle, relative):
            relative = str(relative)
            parent = {"candidate": "candidates/c1", "receipt_path": "candidates/c1/freeze.json",
                      "sha256": self.initial_sha} if relative == "candidates/c2" else None
            return {"candidate": relative, "revision_index": 1 if parent else 0,
                    "parent": parent, "route": "program"}
        module.setup = lambda key: (self.bundle, self.local)
        module.lifecycle = types.SimpleNamespace(read_json=real_read, verify_candidate=verify,
            sha256=lambda path: real_sha(path) if Path(path).exists() else "0" * 64)
        def execute(bundle, relative, run_id, seed, **kwargs):
            self.calls.append(run_id)
            if self.fail:
                raise RuntimeError("Invented executor failure")
            return {"status": "success", "generator_executed": False}
        module.execution = types.SimpleNamespace(_write=real_write, _name=lambda name: name,
            run_candidate=execute, verify_execution=lambda *args: {})
        def feedback(*args):
            self.feedback_calls.append(args)
            if self.feedback_fail:
                raise RuntimeError("Invented source feedback failure")
            return {"status": "complete"}
        module.semantic_feedback_v1 = types.SimpleNamespace(collect_feedback=feedback,
            preflight=lambda *args: {"scope": "mock", "reference_read": False})
        def diagnose(*args):
            if self.diagnostic_fail:
                raise RuntimeError("Invented diagnostic failure")
            return {"mock": True, "reference_read": False}
        module.load_diagnostics = lambda: types.SimpleNamespace(diagnose_csv=diagnose)
        module.freeze("B", "c1")

    def initial(self):
        module.run("B", "c1", "initial_trial")
        module.run("B", "c1", "initial_delivery")


with tempfile.TemporaryDirectory(prefix="bounded_routing_") as temporary:
    base = Path(temporary)
    fixture = Fixture(base / "retain")
    rejects(lambda: module.freeze("B", "other"), "second independent construction rejected")
    rejects(lambda: module.run("B", "c1", "initial_delivery"), "delivery before trial rejected")
    module.run("B", "c1", "initial_trial")
    rejects(lambda: module.run("B", "c1", "initial_trial"), "reserved trial cannot be retried")
    rejects(lambda: module.run("B", "other", "initial_trial"), "initial candidate substitution rejected")
    rejects(lambda: module.run("B", "c2", "revision_trial"), "revision before initial deliveries rejected")
    module.run("B", "c1", "initial_delivery")
    real_write(fixture.bundle / "FINAL_DECISION.json", {"choice": "retain", "candidate": "candidates/c1"})
    aliases = module.run("B", "c1", "final_delivery")
    assert len(aliases) == 3 and all(row["physical_execution"] is False for row in aliases)
    assert len(fixture.calls) == 4 and len(fixture.feedback_calls) == 4
    assert len(list(fixture.local.glob("*_reserved.json"))) == 4
    checks.append({"check": "explicit retain aliases three deliveries with zero additional physical attempts", "status": "PASS"})
    rejects(lambda: module.run("B", "c1", "revision_trial"), "retained candidate revision trial rejected")
    rejects(lambda: module.run("B", "c1", "final_delivery"), "duplicate alias write rejected")

    fixture = Fixture(base / "revise")
    fixture.initial()
    revision = base / "revision.json"
    real_write(revision, {"mock": "revision record"})
    module.freeze("B", "c2", "c1", str(revision))
    fixture.fail = True
    result = module.run("B", "c2", "revision_trial")
    assert result[0]["status"] == "wrapper_error" and "Invented executor failure" in result[0]["error"]
    assert len(list(fixture.local.glob("*_reserved.json"))) == 5
    assert len(fixture.calls) == 5
    checks.append({"check": "executor failure consumes one slot and records error without fallback", "status": "PASS"})
    rejects(lambda: module.run("B", "c2", "revision_trial"), "failed attempt cannot be retried")
    fixture.fail = False
    real_write(fixture.bundle / "FINAL_DECISION.json", {"choice": "revise", "candidate": "candidates/c2"})
    result = module.run("B", "c2", "final_delivery")
    assert len(result) == 3 and len(fixture.calls) == 8
    assert len(list(fixture.local.glob("*_reserved.json"))) == 8
    checks.append({"check": "one direct revision consumes at most eight physical slots and uses only semantic_feedback_v1", "status": "PASS"})
    # Directly exercise the cap independently of the existing reserved-slot guard.
    changed = fixture.local / "b_final_delivery_7403_reserved.json"
    changed.rename(fixture.local / "preserved_eighth_reserved.json")
    old_stages = module.STAGES
    module.STAGES = {**old_stages, "final_delivery": [7404]}
    rejects(lambda: module.run("B", "c2", "final_delivery"), "ninth physical attempt blocked before executor")
    module.STAGES = old_stages
    assert len(fixture.calls) == 8
    assert not list(base.rglob("*.csv"))

    fixture = Fixture(base / "feedback_failure")
    fixture.feedback_fail = True
    fixture.diagnostic_fail = True
    fixture.initial()
    record = real_read(fixture.local / "b_initial_delivery_7401_result.json")
    assert record["status"] == record["execution_status"] == "success"
    assert record["execution_verified"] is True and record["table_sha256"] == "0" * 64
    assert record["source_feedback_status"] == record["diagnostics_status"] == "error"
    checks.append({"check": "successful tables remain bound when both source feedback and diagnostics fail", "status": "PASS"})
    real_write(fixture.bundle / "FINAL_DECISION.json", {"choice": "retain", "candidate": "candidates/c1"})
    module.run("B", "c1", "final_delivery")
    sys.path.insert(0, str(HERE))
    evspec = importlib.util.spec_from_file_location("bounded_evaluation_test", HERE / "evaluate_build.py")
    evaluator = importlib.util.module_from_spec(evspec)
    evspec.loader.exec_module(evaluator)
    evaluator.ROOT = fixture.local.parent
    evaluator.HERE = evaluator.ROOT / "evaluation"
    evaluator.controller = module
    evaluator.lifecycle = module.lifecycle
    evaluator.sha = module.lifecycle.sha256
    module.verify_control_manifest = lambda: {}
    evaluator.execution = types.SimpleNamespace(_write=real_write,
        verify_execution=lambda bundle, run_id: {"status": "success", "candidate": "candidates/c1",
                                                "limits": {"seed": int(run_id.rsplit('_', 1)[1])}})
    evaluator.build_closure("candidates/c1", "candidates/c1", True)
    slots, _ = evaluator.closure_gate(evaluator.ROOT / "LIVE_CLOSURE.json")
    assert len(slots) == 6 and all(row["table"] is not None for row in slots)
    checks.append({"check": "closure includes all successful deliveries despite feedback errors", "status": "PASS"})
    record_path = fixture.local / "b_initial_trial_7400_result.json"
    changed_record = real_read(record_path)
    changed_record["source_feedback_error"] += " altered after closure"
    record_path.write_text(json.dumps(changed_record), encoding="utf-8")
    rejects(lambda: evaluator.closure_gate(evaluator.ROOT / "LIVE_CLOSURE.json"),
            "postclosure result mutation rejected by exact digest bindings")

report = {"controller_sha256": hashlib.sha256((HERE.parent / "run_session.py").read_bytes()).hexdigest(),
          "checks": checks, "sandbox_executions": 0, "patient_rows_read": 0, "generated_tables": 0,
          "scope": "Targeted new controller routing mocks only; no historical campaign/test rerun and no scientific validity claim."}
destination = HERE / ("CONTROLLER_MOCK_CHECKS." + report["controller_sha256"][:12] + ".json")
with destination.open("x", encoding="utf-8") as stream:
    json.dump(report, stream, indent=2)
    stream.write("\n")
print(json.dumps(report, indent=2))
