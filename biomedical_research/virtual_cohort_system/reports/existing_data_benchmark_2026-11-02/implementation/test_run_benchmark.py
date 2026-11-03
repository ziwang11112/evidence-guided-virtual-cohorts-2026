"""Invented metadata/results only; process/runtime boundary explicitly mocked."""
import copy
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("benchmark_under_test", Path(__file__).with_name("run_benchmark.py"))
b = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(b)


def reference():
    return {"estimands": {k: {"status": "computed", "coefficient": 10.0, "unit": "toy",
            "interval": {"status": "available", "lower": 8.0, "upper": 12.0}}
            for k in ("E1", "E2", "E3")}}


def slots():
    out = []
    for identifier in b.IDS:
        values = (8.0, 10.0, 12.0) if identifier.startswith("E0") else (9.0, 10.0, 11.0)
        for seed, value in zip(b.SEEDS, values):
            out.append({"constructor": identifier, "seed": seed, "status": "success",
                        "analysis": {"estimands": {k: {"status": "computed", "coefficient": value}
                                     for k in ("E1", "E2", "E3")}}})
    return out


@pytest.fixture
def release(tmp_path):
    root = tmp_path / "evcB"; root.mkdir()
    artifact_paths = [Path(b.__file__), b.ANALYSIS_MODULE, b.ANALYSIS_PLAN, b.RUNTIME_CHECK, b.RUNTIME_IDENTITY,
                      Path(b.execution.__file__), Path(b.lifecycle.__file__), Path(b.contracts.__file__), b.PROJECT / "cohort_harness/_worker.py"]
    for identifier in b.IDS:
        folder = root / identifier
        (folder / "sources").mkdir(parents=True)
        (folder / "input").mkdir()
        (folder / b.CANDIDATE).mkdir(parents=True)
        b.write(folder / "task.json", {"mode": "whole_cohort", "n_rows": 3000})
        b.write(folder / "registry.json", {"invented": True})
        b.write(folder / "sources/evidence_packet.json", {"arm": identifier[:2], "invented": True})
        (folder / "sources/NGSP_UNITS.md").write_text("invented unit guide", encoding="utf-8")
        b.write(folder / "input/compiled_evidence.json", {"arm": identifier[:2]})
        for name in ("task.json", "registry.json", "sources/evidence_packet.json", "sources/NGSP_UNITS.md", "input/compiled_evidence.json"):
            artifact_paths.append(folder / name)
    ref = tmp_path / "invented_reference.json"; b.write(ref, {"reference": reference()})
    independent = tmp_path / "invented_independent.json"; b.write(independent, {"invented": True})
    manifest = {"schema_version": 1, "kind": "existing_chns_benchmark_release", "status": "released",
                "bundle_root": str(root.resolve()), "artifacts": [b.binding(p) for p in artifact_paths],
                "evaluation": {"analysis_module": b.binding(b.ANALYSIS_MODULE), "analysis_plan": b.binding(b.ANALYSIS_PLAN),
                               "reference_report": b.binding(ref), "independent_reference_report": b.binding(independent)},
                "runtime_check": b.binding(b.RUNTIME_CHECK), "runtime_identity": b.binding(b.RUNTIME_IDENTITY)}
    manifest["approval"] = {"decision": "approved", "independent": True, "reviewer_id": "invented-reviewer",
                            "producer_id": "invented-producer", "approved_sha256": b.release_digest(manifest)}
    path = tmp_path / "release.json"; b.write(path, manifest)
    return path, root, ref


def make_candidate(root, identifier="E0_A01"):
    bundle = root / identifier
    for name in b.FILES:
        path = bundle / b.CANDIDATE / name
        if name == "evidence.json":
            path.write_bytes((bundle / "input/compiled_evidence.json").read_bytes())
        else:
            path.write_text("invented " + name, encoding="utf-8")
    return bundle


def bind_candidate(release, monkeypatch):
    path, root, _ = release
    b.init(path)
    bundle = make_candidate(root)
    def freeze(bundle, candidate):
        b.write(bundle / candidate / "freeze.json", {"invented": True})
        return {"route": "generator.py"}
    monkeypatch.setattr(b.lifecycle, "freeze_candidate", freeze)
    monkeypatch.setattr(b.lifecycle, "verify_candidate", lambda *a: {"route": "generator.py"})
    review = root / "review.json"
    b.write(review, {"schema_version": 1, "constructor": "E0_A01", "decision": "approved", "independent": True,
                     "producer_id": "invented-author", "reviewer_id": "invented-reviewer", "files": b.candidate_review_files(bundle)})
    b.freeze_constructor(path, "E0_A01", review)
    return bundle


def test_mean_absolute_precedes_arm_mean():
    report = b.summarize(slots(), reference())
    row = report["endpoints"]["E1"]
    assert row["arm_mean_absolute_discrepancy"]["E0"] == pytest.approx(4 / 3)
    assert row["arm_mean_absolute_discrepancy"]["E1"] == pytest.approx(2 / 3)
    assert row["E1_minus_E0"] == pytest.approx(-2 / 3)
    assert report["both_addressed_projections_improve"] is True
    assert row["reference_interval_endpoint_sensitivity"]["lower"]["E1_minus_E0"] == 0
    assert row["reference_interval_endpoint_sensitivity"]["upper"]["E1_minus_E0"] == 0


@pytest.mark.parametrize("change", ["failed", "no_analysis", "missing_endpoint", "third_endpoint"])
def test_incomplete_cannot_receive_survivor_claim(change):
    items = slots()
    if change == "failed": items[0]["status"] = "failed"
    elif change == "no_analysis": items[0]["analysis"] = None
    else: items[0]["analysis"]["estimands"]["E3" if change == "third_endpoint" else "E1"]["status"] = "unavailable"
    report = b.summarize(items, reference())
    assert report["both_addressed_projections_improve"] is False
    assert report["complete_arms_all_three_endpoints"] is False
    assert report["reserved_slots"] == 30


def test_both_primary_endpoints_must_improve():
    items = slots()
    for item in items:
        if item["constructor"].startswith("E1"):
            item["analysis"]["estimands"]["E2"]["coefficient"] = 30
    report = b.summarize(items, reference())
    assert report["endpoints"]["E1"]["E1_minus_E0"] < 0
    assert report["endpoints"]["E2"]["E1_minus_E0"] > 0
    assert not report["both_addressed_projections_improve"]


@pytest.mark.parametrize("replacement", ["drop", "duplicate"])
def test_complete_slot_identity_required(replacement):
    items = slots()
    if replacement == "drop": items.pop()
    else: items[-1] = copy.deepcopy(items[0])
    with pytest.raises(ValueError, match="thirty distinct"):
        b.summarize(items, reference())


def test_reference_unopened_until_all_inventory_closed(release, monkeypatch):
    path, root, ref = release
    original_sha, original_read = b.sha, b.read
    accesses = []
    def hash_spy(p):
        if Path(p) == ref: accesses.append("hash")
        return original_sha(p)
    def read_spy(p):
        if Path(p) == ref: accesses.append("read")
        return original_read(p)
    monkeypatch.setattr(b, "sha", hash_spy); monkeypatch.setattr(b, "read", read_spy)
    b.init(path)
    with pytest.raises(b.contracts.ContractError): b.evaluate(path)
    assert accesses == []
    for identifier in b.IDS:
        b.close_constructor(path, identifier, "Invented authoring stop")
    assert accesses == []
    b.close_inventory(path)
    result = b.evaluate(path)
    assert accesses == ["hash", "read"]
    report = b.read(result["report"])
    assert len(report["slots"]) == 30
    assert all(x["status"] == "not_run" for x in report["slots"])
    assert report["execution_failures_or_unrun"] == 30
    assert not result["both_addressed_projections_improve"]
    with pytest.raises(FileExistsError): b.evaluate(path)
    assert accesses == ["hash", "read"]


def test_release_tamper_stops_before_reference(release):
    path, root, _ = release
    b.init(path)
    (root / "E0_A01/input/compiled_evidence.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Bound file changed"):
        b.close_constructor(path, "E0_A01", "stop")


def test_frozen_scientific_bytes_cannot_change(release, monkeypatch):
    bundle = bind_candidate(release, monkeypatch)
    (bundle / b.CANDIDATE / "generator.py").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="Frozen reviewed inputs changed"):
        b.run_constructor(release[0], "E0_A01")


def test_runtime_failure_consumes_all_three_without_dispatch(release, monkeypatch):
    bind_candidate(release, monkeypatch)
    monkeypatch.setattr(b, "_runtime", lambda *a: (_ for _ in ()).throw(RuntimeError("invented unavailable")))
    monkeypatch.setattr(b.execution, "run_candidate", lambda *a, **kw: pytest.fail("No local fallback or dispatch allowed"))
    report = b.run_constructor(release[0], "E0_A01")
    assert report["statuses"] == ["runtime_unavailable"] * 3
    with pytest.raises(ValueError, match="consumed"):
        b.run_constructor(release[0], "E0_A01")
    b.close_constructor(release[0], "E0_A01", "runtime failure retained")


def test_shell_exception_kept_and_other_slots_attempted_once(release, monkeypatch):
    bundle = bind_candidate(release, monkeypatch)
    monkeypatch.setattr(b, "_runtime", lambda *a: {"invented": True})
    seen = []
    def run(root, candidate, run_id, seed, **kwargs):
        seen.append(seed)
        assert kwargs["timeout_seconds"] == 180 and kwargs["runtime"] == b.execution.DEFAULT_RUNTIME
        raise OSError("invented shell dispatch failure")
    monkeypatch.setattr(b.execution, "run_candidate", run)
    report = b.run_constructor(release[0], "E0_A01")
    assert seen == list(b.SEEDS) and report["statuses"] == ["error"] * 3
    with pytest.raises(ValueError, match="consumed"):
        b.run_constructor(release[0], "E0_A01")
    b.close_constructor(release[0], "E0_A01", "all errors retained")


def test_interruption_has_no_resume_and_closes_unfinished_slots(release, monkeypatch):
    bind_candidate(release, monkeypatch)
    monkeypatch.setattr(b, "_runtime", lambda *a: {"invented": True})
    monkeypatch.setattr(b.execution, "run_candidate", lambda *a, **kw: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt): b.run_constructor(release[0], "E0_A01")
    with pytest.raises(ValueError, match="consumed"): b.run_constructor(release[0], "E0_A01")
    closed = b.close_constructor(release[0], "E0_A01", "interrupted allocation retained")
    assert closed["statuses"] == ["interrupted_or_unrun_consumed"] * 3


def test_closed_inventory_mutation_is_rejected_before_reference(release):
    path, root, _ = release
    b.init(path)
    for identifier in b.IDS: b.close_constructor(path, identifier, "invented stop")
    b.close_inventory(path)
    p = root / "benchmark_control/constructors/E0_A01/CLOSED.json"
    obj = b.read(p); obj["reason"] = "changed"; p.write_bytes(b.canonical(obj))
    with pytest.raises(ValueError, match="Final inventory changed"):
        b.evaluate(path)


def test_two_freezes_or_closed_constructor_cannot_be_reused(release, monkeypatch):
    bind_candidate(release, monkeypatch)
    root = release[1]
    with pytest.raises(ValueError, match="already bound"):
        b.freeze_constructor(release[0], "E0_A01", root / "review.json")
    b.close_constructor(release[0], "E0_A01", "invented stop")
    with pytest.raises(ValueError, match="already closed"):
        b.run_constructor(release[0], "E0_A01")


def test_successful_receipts_bind_seed_parent_and_output(release, monkeypatch):
    bundle = bind_candidate(release, monkeypatch)
    monkeypatch.setattr(b, "_runtime", lambda *a: {"invented": True})
    receipts = {}
    def run(root, candidate, run_id, seed, **kwargs):
        folder = root / "executions" / run_id
        (folder / "output").mkdir(parents=True)
        (folder / "output/generated.csv").write_text("invented output bytes", encoding="utf-8")
        receipt = {"candidate": candidate, "candidate_freeze_sha256": b.sha(root / candidate / "freeze.json"),
                   "limits": {"seed": seed, **b.LIMITS}, "status": "success"}
        b.write(folder / "execution.json", receipt); receipts[run_id] = receipt
        return receipt
    monkeypatch.setattr(b.execution, "run_candidate", run)
    monkeypatch.setattr(b.execution, "verify_execution", lambda root, run_id: receipts[run_id])
    assert b.run_constructor(release[0], "E0_A01")["statuses"] == ["success"] * 3
    b.close_constructor(release[0], "E0_A01", "invented success")
    for identifier in b.IDS[1:]: b.close_constructor(release[0], identifier, "invented stop")
    b.close_inventory(release[0])
    output = bundle / "executions/initial_1701/output/generated.csv"
    output.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="Retained execution artifacts changed"):
        b.evaluate(release[0])


def test_evaluator_analyzes_each_new_output_after_closure(release, monkeypatch):
    from types import SimpleNamespace
    path, root, _ = release
    b.init(path)
    entries = slots()
    for entry in entries:
        entry["run_id"] = f"initial_{entry['seed']}"
        output = root / entry["constructor"] / "executions" / entry["run_id"] / "output/generated.csv"
        output.parent.mkdir(parents=True)
        output.write_text(str(entry["analysis"]["estimands"]["E1"]["coefficient"]), encoding="utf-8")
        entry["output_sha256"] = b.sha(output)
        entry.pop("analysis")
    inventory = {"slots": entries}
    b.write(root / "benchmark_control/FINAL_INVENTORY.json", inventory)
    monkeypatch.setattr(b, "_closed", lambda *a: inventory)  # Verified-closure boundary mocked explicitly.
    monkeypatch.setattr(b.lifecycle, "read_table", lambda p, *a, **kw: float(Path(p).read_text()))
    monkeypatch.setattr(b.contracts, "validate_output", lambda *a: None)
    calls = []
    def analyze(value, plan, reference=False):
        calls.append(value)
        return {"estimands": {k: {"status": "computed", "coefficient": value} for k in ("E1", "E2", "E3")}}
    monkeypatch.setattr(b, "_module", lambda *a: SimpleNamespace(analyze=analyze, compare_estimates=lambda r, g: {"invented": True}))
    outcome = b.evaluate(path)
    assert len(calls) == 30
    assert outcome["both_addressed_projections_improve"] is True
    report = b.read(outcome["report"])
    assert len(report["slots"]) == 30
    assert report["endpoints"]["E1"]["E1_minus_E0"] == pytest.approx(-2 / 3)
