"""Invented engineering fixtures only; no patient or historical result reads."""
from __future__ import annotations

import copy
import importlib.util
import itertools
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


@pytest.fixture(scope="module")
def primary():
    return module("invented_pilot_evaluator", "pilot_evaluation_v1.py")


@pytest.fixture(scope="module")
def independent():
    return module("invented_pilot_independent", "independent_pilot_recompute.py")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def invented_frame():
    """Deterministic arithmetic fixture, not a scientific generator or draw."""
    i = np.arange(3000)
    age = 35. + i % 40
    female = ((i // 40) % 2).astype(float)
    bmi = 19. + .8 * (i % 19) + .03 * ((i // 19) % 3)
    glucose = 4. + .2 * (i % 13)
    hba1c = 3. + .03 * age + .1 * female + .02 * bmi + .25 * glucose + .01 * (i % 7)
    return pd.DataFrame({"row_id": [f"invented-{j}" for j in i], "age": age, "female": female,
                         "bmi": bmi, "glucose": glucose, "hba1c": hba1c})


@pytest.fixture
def case(tmp_path, primary):
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    reference = {"estimands": {key: {"status": "computed", "coefficient": 2., "unit": unit,
                    "interval": {"status": "available", "lower": 1., "upper": 3.}}
                for key, unit in (("E1", "%/(kg/m^2)"), ("E2", "%/(mmol/L)"), ("E3", "%/year"))},
                 "diagnostics": {"fixture": "invented_reference_aggregate_not_patient_data"}}
    first, second = tmp_path / "invented_reference.json", tmp_path / "invented_independent_reference.json"
    write(first, {"reference": reference})
    write(second, {"reference": reference})
    policy = tmp_path / "policy.json"
    write(policy, primary.POLICY)
    environment = tmp_path / "environment.json"
    write(environment, primary.analysis_environment())
    f2 = PROJECT / "work/chns_admission_2026-11-01/f2"
    release = {"evaluator": primary.binding(HERE / "pilot_evaluation_v1.py"), "target_seeds": [1701, 1702, 1703],
               "n_rows": 3000, "target_context": "target", "evaluation": {
                    "analysis_module": primary.binding(f2 / "evaluation/chns_f2_evaluation.py"),
                    "analysis_plan": primary.binding(f2 / "analysis_plan.json"),
                    "reference_report": primary.binding(first), "independent_reference_report": primary.binding(second),
                    "independent_recompute": primary.binding(HERE / "independent_pilot_recompute.py"),
                    "policy": primary.binding(policy), "analysis_environment": primary.binding(environment)}}
    write(ledger / "release.json", release)
    slots = [{"constructor": c, "version": v, "role": "target", "context_id": "target",
              "run_id": f"{c}_{v}_target_{s}", "seed": s, "n_rows": 3000,
              "bundle": str(tmp_path / "bundles" / c / v), "candidate": f"candidates/{v}",
              "status": "not_run", "output_sha256": None, "execution_sha256": None, "error": "invented_unrun"}
             for c, v, s in itertools.product(primary.CONSTRUCTORS, primary.VERSIONS, release["target_seeds"])]
    inventory = {"schema_version": 1, "kind": "developmental_pilot_closed_inventory", "status": "closed",
                 "scientific_closed": True, "release_sha256": primary.canonical_release_sha256(release),
                 "scientific_freeze_sha256": "a" * 64, "inventory_sha256": "b" * 64,
                 "authorization": {"fixture": "invented_trusted_gate"}, "slots": slots}
    annotations = {}
    for c, v in itertools.product(primary.CONSTRUCTORS, primary.VERSIONS):
        folder = tmp_path / "annotations" / c / v
        sidecar = folder / "analysis_evidence.json"
        assessment = folder / "support_assessment.json"
        feedback = folder / "source_event.json"
        labels = [{"id": a, "assessment": "unassessed", "rationale": "Invented fixture declares this use unassessed.",
                   "assumption_ids": ["invented_assumption"], "gaps": [{"id": "invented_gap", "description": "Fixture gap"}]}
                  for a in primary.ANALYSIS_IDS.values()]
        write(sidecar, {"schema_version": 1, "analyses": labels})
        write(assessment, {"fixture": "invented_independent_support_review"})
        write(feedback, {"kind": "sources_closed", "payload": {"key": f"{c}/{v}",
              "feedback": {"packet": {"checks": [{"check_id": "invented_source", "status": "unavailable", "reason": "fixture"}]}},
              "slots": [], "eligibility": {"fixture": True}}})
        annotations[f"{c}/{v}"] = {"candidate_binding": {"bundle": str(folder), "candidate": "candidates/invented", "parent": {}},
            "analysis_evidence": primary.binding(sidecar), "support_assessment": primary.binding(assessment),
            "source_feedback": [primary.binding(feedback)], "source_feedback_format": "pilot_source_closure_event_v1", "unavailable_reason": None}
    inventory["scientific_annotations"] = annotations
    def gate(received, sha):
        assert received == ledger.resolve()
        assert sha == release["evaluator"]["sha256"]
        return copy.deepcopy(inventory)
    return {"ledger": ledger, "release": release, "inventory": inventory, "gate": gate,
            "reference_paths": [first, second], "reference": reference}


def successful(case, primary, indexes=None, frame=None):
    frame = invented_frame() if frame is None else frame
    indexes = range(18) if indexes is None else indexes
    for index in indexes:
        slot = case["inventory"]["slots"][index]
        run = Path(slot["bundle"]) / "executions" / slot["run_id"]
        (run / "output").mkdir(parents=True)
        frame.to_csv(run / "output/generated.csv", index=False)
        write(run / "execution.json", {"kind": "invented_receipt", "run_id": slot["run_id"]})
        slot.update(status="success", output_sha256=primary.sha(run / "output/generated.csv"),
                    execution_sha256=primary.sha(run / "execution.json"), error=None)


def forbid_reference_access(monkeypatch, case):
    paths = {p.resolve() for p in case["reference_paths"]}
    original = Path.open
    def guarded(path, *args, **kwargs):
        if path.resolve() in paths:
            raise AssertionError("Reference accessed before successful closure/binding checks")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded)


@pytest.mark.parametrize("defect", ["gate", "closure", "missing_slot", "duplicate_slot", "release_linkage"])
def test_no_reference_access_before_authenticated_complete_closure(case, primary, monkeypatch, defect):
    gate = case["gate"]
    if defect == "gate":
        def gate(*args):
            raise ValueError("invented unauthorized")
    elif defect == "closure":
        case["inventory"]["scientific_closed"] = False
    elif defect == "missing_slot":
        case["inventory"]["slots"].pop()
    elif defect == "duplicate_slot":
        case["inventory"]["slots"][-1] = copy.deepcopy(case["inventory"]["slots"][0])
    else:
        case["inventory"]["release_sha256"] = "c" * 64
    forbid_reference_access(monkeypatch, case)
    with pytest.raises(ValueError):
        primary.evaluate(case["ledger"], controller_gate=gate)
    assert not (case["ledger"] / "evaluation").exists()


@pytest.mark.parametrize("file", ["output/generated.csv", "execution.json"])
def test_changed_successful_output_or_receipt_stops_before_reference(case, primary, monkeypatch, file):
    successful(case, primary, indexes=[0])
    slot = case["inventory"]["slots"][0]
    path = Path(slot["bundle"]) / "executions" / slot["run_id"] / file
    path.write_text("changed", encoding="utf-8")
    forbid_reference_access(monkeypatch, case)
    with pytest.raises(ValueError):
        primary.evaluate(case["ledger"], controller_gate=case["gate"])


def test_all_three_endpoints_all_eighteen_slots_and_independent_diagnostics(case, primary, independent):
    successful(case, primary)
    result = primary.evaluate(case["ledger"], controller_gate=case["gate"])
    report = primary.read(result["report"])
    assert len(report["slots"]) == report["reserved_target_slots"] == 18
    assert set(report["endpoints"]) == {"E1", "E2", "E3"}
    assert report["independent_constructions"] == 2
    assert report["equivalence_margin"] is report["overall_success_rule"] is None
    diagnostic = report["slots"][0]["analysis"]["diagnostics"]
    assert sum(len(x) for x in diagnostic["marginal"].values()) == 25
    assert len(diagnostic["joint"]) == 2
    extra = report["slots"][0]["generated_only_diagnostics"]
    assert len(extra["pearson_pairs"]) == 10
    assert extra["reference_status"] == "unavailable_no_reference_supplement"
    assert len(report["scientific_annotations"]) == 6
    for endpoint in report["endpoints"].values():
        for constructor in endpoint["constructors"].values():
            assert all(v["analysis_support"]["assessment"] == "unassessed" for v in constructor["versions"].values())
    assert report["slots"][0]["analysis"]["estimands"]["E3"]["status"] == "computed"
    assert report["slots"][0]["analysis_support"]["E3"]["assessment"] == "unassessed"
    assert all(a["source_discrepancy_reports"][0]["report"]["feedback"]["packet"]["checks"][0]["status"] == "unavailable"
               for a in report["scientific_annotations"].values())
    check = independent.recompute(case["ledger"], verified_controller_gate=case["gate"])
    assert check["status"] == "matched", independent.read(check["report"])["disagreements"][:10]
    with pytest.raises(FileExistsError):
        primary.evaluate(case["ledger"], controller_gate=case["gate"])
    with pytest.raises(FileExistsError):
        independent.recompute(case["ledger"], verified_controller_gate=case["gate"])


def test_missing_seed_keeps_denominator_and_withholds_paired_summary(case, primary, independent):
    successful(case, primary, indexes=[0, 1])
    result = primary.evaluate(case["ledger"], controller_gate=case["gate"])
    report = primary.read(result["report"])
    for endpoint in report["endpoints"].values():
        a = endpoint["constructors"]["A01"]
        assert a["versions"]["initial"]["valid_seed_count"] == 2
        assert a["versions"]["initial"]["mean_absolute_discrepancy"] is None
        assert a["changes"]["source_feedback_minus_initial"]["mean_absolute_discrepancy_change"] is None
    assert report["failed_or_unrun_slots"] == 16
    assert independent.recompute(case["ledger"], verified_controller_gate=case["gate"])["status"] == "matched"


def test_absolute_before_average_and_complete_pair_requirement(primary):
    ref = {"estimands": {e: {"status": "computed", "coefficient": 2., "unit": "invented"} for e in primary.ENDPOINTS}}
    slots = []
    for c, v, seed in itertools.product(primary.CONSTRUCTORS, primary.VERSIONS, [1, 2, 3]):
        value = {1: 1., 2: 2., 3: 3.}[seed] if v == "initial" else 2.
        slots.append({"constructor": c, "version": v, "seed": seed, "status": "success",
                      "analysis_support": {e: {"assessment": "unassessed"} for e in primary.ENDPOINTS},
                      "analysis": {"estimands": {e: {"status": "computed", "coefficient": value} for e in primary.ENDPOINTS}}})
    summary = primary.summarize(ref, slots, [1, 2, 3])
    a = summary["endpoints"]["E1"]["constructors"]["A01"]
    assert a["versions"]["initial"]["mean_absolute_discrepancy"] == pytest.approx(2 / 3)
    assert a["versions"]["initial"]["mean_signed_discrepancy"] == 0
    assert a["changes"]["source_feedback_minus_initial"]["mean_absolute_discrepancy_change"] == pytest.approx(-2 / 3)


def test_tail_ties_duplicates_and_invalid_rows_without_deletion(primary, independent):
    frame = invented_frame()
    frame.loc[1, list(primary.VARIABLES)] = frame.loc[0, list(primary.VARIABLES)].to_numpy()
    frame.loc[2, "glucose"] = 0
    frame.loc[3, "bmi"] = np.nan
    actual = primary.generated_diagnostics(frame)
    expected = independent.added_diagnostics({k: frame[k].to_numpy() for k in primary.VARIABLES})
    assert independent.differences(expected, actual) == []
    assert actual["duplicate_rows_after_first"] == 1
    assert actual["invalid_rows"] == 2
    assert actual["n_rows"] == 3000
    assert actual["domain_violations_by_variable"]["glucose"] == 1
    assert actual["nonfinite_by_variable"]["bmi"] == 1
    assert all(x is None for x in actual["pearson_pairs"].values())


def test_singular_design_withholds_endpoint_not_rows(case, primary, independent):
    frame = invented_frame()
    frame["bmi"] = frame["age"]
    successful(case, primary, indexes=[0], frame=frame)
    report = primary.read(primary.evaluate(case["ledger"], controller_gate=case["gate"])["report"])
    row = next(s for s in report["slots"] if s["status"] == "success")
    assert row["analysis"]["n"] == 3000
    assert row["analysis"]["estimands"]["E1"]["status"] == "unavailable"
    assert row["analysis"]["estimands"]["E2"]["status"] == "computed"
    assert independent.recompute(case["ledger"], verified_controller_gate=case["gate"])["status"] == "matched"


def test_independent_recompute_detects_report_arithmetic_tampering(case, primary, independent):
    primary.evaluate(case["ledger"], controller_gate=case["gate"])
    path = case["ledger"] / "evaluation/REPORT.json"
    report = primary.read(path)
    report["endpoints"]["E3"]["constructors"]["A02"]["versions"]["initial"]["mean_absolute_discrepancy"] = 0.
    write(path, report)
    completion = case["ledger"] / "evaluation/COMPLETION.json"
    commitment = primary.read(completion)
    commitment["report"] = primary.binding(path)
    write(completion, commitment)
    result = independent.recompute(case["ledger"], verified_controller_gate=case["gate"])
    assert result["status"] == "disagreement" and result["disagreement_count"] > 0


def test_reference_binding_failure_reserves_failure_without_retry(case, primary):
    case["reference_paths"][0].write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError):
        primary.evaluate(case["ledger"], controller_gate=case["gate"])
    assert (case["ledger"] / "evaluation/FAILURE.json").exists()
    assert not (case["ledger"] / "evaluation/REPORT.json").exists()
    with pytest.raises(FileExistsError):
        primary.evaluate(case["ledger"], controller_gate=case["gate"])


@pytest.mark.parametrize("defect", ["missing_version", "changed_sidecar", "changed_source_report"])
def test_scientific_annotation_failures_precede_reference(case, primary, monkeypatch, defect):
    if defect == "missing_version":
        del case["inventory"]["scientific_annotations"]["A02/source_feedback"]
    else:
        record = case["inventory"]["scientific_annotations"]["A01/initial"]
        item = record["analysis_evidence"] if defect == "changed_sidecar" else record["source_feedback"][0]
        Path(item["path"]).write_text("changed", encoding="utf-8")
    forbid_reference_access(monkeypatch, case)
    with pytest.raises(ValueError):
        primary.evaluate(case["ledger"], controller_gate=case["gate"])
    assert not (case["ledger"] / "evaluation").exists()


@pytest.mark.parametrize("route", ["primary", "independent"])
def test_live_environment_mismatch_precedes_reference(case, primary, independent, monkeypatch, route):
    if route == "independent":
        primary.evaluate(case["ledger"], controller_gate=case["gate"])
    target = primary if route == "primary" else independent
    environment = target.analysis_environment()
    environment["numpy"] = "invented_changed_version"
    monkeypatch.setattr(target, "analysis_environment", lambda: environment)
    forbid_reference_access(monkeypatch, case)
    with pytest.raises(ValueError, match="environment"):
        if route == "primary":
            primary.evaluate(case["ledger"], controller_gate=case["gate"])
        else:
            independent.recompute(case["ledger"], verified_controller_gate=case["gate"])
    assert not (case["ledger"] / ("evaluation" if route == "primary" else "independent_evaluation")).exists()


@pytest.mark.parametrize("route", ["primary", "independent"])
@pytest.mark.parametrize("file", ["output/generated.csv", "execution.json"])
@pytest.mark.parametrize("phase", ["before_analysis", "after_analysis"])
def test_post_gate_identity_change_is_fatal(case, primary, independent, monkeypatch, route, file, phase):
    successful(case, primary, indexes=[0])
    if route == "independent":
        primary.evaluate(case["ledger"], controller_gate=case["gate"])
    target = primary if route == "primary" else independent
    slot = case["inventory"]["slots"][0]
    changed = Path(slot["bundle"]) / "executions" / slot["run_id"] / file
    function = "read_target_bytes" if phase == "before_analysis" else "analyze_generated" if route == "primary" else "analyze"
    original = getattr(target, function)
    def mutate(*args, **kwargs):
        if phase == "before_analysis":
            changed.write_text("invented_mutation", encoding="utf-8")
            return original(*args, **kwargs)
        result = original(*args, **kwargs)
        changed.write_text("invented_mutation", encoding="utf-8")
        return result
    monkeypatch.setattr(target, function, mutate)
    with pytest.raises(target.IntegrityError):
        if route == "primary":
            primary.evaluate(case["ledger"], controller_gate=case["gate"])
        else:
            independent.recompute(case["ledger"], verified_controller_gate=case["gate"])
    out = case["ledger"] / ("evaluation" if route == "primary" else "independent_evaluation")
    assert (out / "FAILURE.json").exists()
    assert not (out / "REPORT.json").exists()
    assert not (out / "COMPLETION.json").exists()


def test_fractional_task_age_is_counted_and_withheld_without_row_removal(case, primary, independent):
    frame = invented_frame()
    frame.loc[0, "age"] = 35.5
    successful(case, primary, indexes=[0], frame=frame)
    report = primary.read(primary.evaluate(case["ledger"], controller_gate=case["gate"])["report"])
    row = next(s for s in report["slots"] if s["status"] == "success")
    assert row["generated_only_diagnostics"]["fractional_age_rows"] == 1
    assert row["generated_only_diagnostics"]["domain_violations_by_variable"]["age"] == 1
    assert row["analysis"]["n"] == 3000 and row["analysis"]["gate_reason"] == "nonintegral_age_task_violation"
    assert all(e["status"] == "unavailable" for e in row["analysis"]["estimands"].values())
    assert independent.recompute(case["ledger"], verified_controller_gate=case["gate"])["status"] == "matched"


@pytest.mark.parametrize("defect,reason", [("duplicate_id", "generated_row_identifiers_invalid"),
                                           ("missing_column", "generated_csv_layout_invalid"),
                                           ("nonnumeric", "generated_csv_parse_failed")])
def test_expected_output_errors_retain_aggregate_reasons(case, primary, independent, defect, reason):
    frame = invented_frame()
    if defect == "duplicate_id":
        frame.loc[1, "row_id"] = frame.loc[0, "row_id"]
    elif defect == "missing_column":
        frame = frame.drop(columns="bmi")
    else:
        frame["bmi"] = frame["bmi"].astype(object)
        frame.loc[0, "bmi"] = "invented_invalid_number"
    successful(case, primary, indexes=[0], frame=frame)
    report = primary.read(primary.evaluate(case["ledger"], controller_gate=case["gate"])["report"])
    row = next(s for s in report["slots"] if s["status"] == "success")
    assert row["analysis_error"]["code"] == reason
    assert row["analysis"] is None
    assert independent.recompute(case["ledger"], verified_controller_gate=case["gate"])["status"] == "matched"
