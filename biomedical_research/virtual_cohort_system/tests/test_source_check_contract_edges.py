"""Independent cross-record consistency checks for source-statistic replay."""
import hashlib
import json

import pandas as pd
import pytest

from cohort_harness.contracts import validate_evidence
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import freeze_candidate, verify_candidate
from cohort_harness.source_checks import run_source_checks


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def setup_demo(tmp_path):
    bundle = make_demo(tmp_path / "demo")
    candidate = bundle / "candidates" / "initial"
    return bundle, candidate


def bind_source_report(bundle, candidate):
    report = run_source_checks(bundle, candidate)
    report_path = candidate / "source_check_report.json"
    write(report_path, report)
    checks = read(candidate / "checks.json")
    checks["artifacts"].append({
        "path": report_path.name,
        "sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
    })
    write(candidate / "checks.json", checks)
    return report_path


def test_source_check_rejects_wrong_mean_variable_even_with_matching_units(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    plan = read(candidate / "source_checks.json")
    plan["checks"][0]["operator"]["column"] = "x"
    write(candidate / "source_checks.json", plan)
    with pytest.raises(ValueError):
        run_source_checks(bundle, candidate)


def test_source_check_rejects_omitted_declared_adjustment(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    evidence = read(candidate / "evidence.json")
    evidence["items"][1]["adjustment"] = ["z"]
    write(candidate / "evidence.json", evidence)
    with pytest.raises(ValueError):
        run_source_checks(bundle, candidate)


def test_direct_source_check_api_rejects_invalid_evidence(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    evidence = read(candidate / "evidence.json")
    evidence["items"].append(evidence["items"][0].copy())
    write(candidate / "evidence.json", evidence)
    with pytest.raises(ValueError):
        run_source_checks(bundle, candidate)


def test_direct_source_check_api_does_not_accept_boolean_schema_version(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    plan = read(candidate / "source_checks.json")
    plan["schema_version"] = True
    write(candidate / "source_checks.json", plan)
    with pytest.raises(ValueError):
        run_source_checks(bundle, candidate)


def test_source_table_must_still_match_declared_content_hash(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    table = candidate / "source_tables" / "invented.csv"
    content = pd.read_csv(table)
    content.loc[0, "y"] = 99
    content.to_csv(table, index=False)
    with pytest.raises(ValueError, match="hash"):
        run_source_checks(bundle, candidate)


def test_unimplemented_numeric_statistic_can_be_retained_as_not_computable(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    evidence = read(candidate / "evidence.json")
    evidence["items"][0].update(kind="reported_other", statistic_name="median", estimate=7)
    write(candidate / "evidence.json", evidence)
    plan = read(candidate / "source_checks.json")
    plan["checks"][0].update(status="not_computable", table=None, operator=None,
                              reason="The median operator is not implemented in this milestone.")
    write(candidate / "source_checks.json", plan)
    assert "E1" in validate_evidence(evidence, read(bundle / "task.json"))
    result = run_source_checks(bundle, candidate)
    first = result["checks"][0]
    assert first["status"] == "not_computable"
    assert "value" not in first


def test_unimplemented_statistic_cannot_be_relabelled_as_mean_for_execution(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    evidence = read(candidate / "evidence.json")
    evidence["items"][0].update(kind="reported_other", statistic_name="median", estimate=7)
    write(candidate / "evidence.json", evidence)
    with pytest.raises(ValueError):
        run_source_checks(bundle, candidate)


def test_percentage_evidence_and_operator_use_the_same_scale(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    evidence = read(candidate / "evidence.json")
    # Four of the seven declared y values exceed five.
    evidence["items"][0].update(kind="proportion", variables=["y"], estimate=400 / 7, unit="%")
    write(candidate / "evidence.json", evidence)
    plan = read(candidate / "source_checks.json")
    plan["checks"][0]["operator"] = {
        "kind": "proportion", "unit": "%", "selection": [], "missing_policy": "error",
        "event": {"column": "y", "op": "gt", "value": 5},
    }
    write(candidate / "source_checks.json", plan)
    result = run_source_checks(bundle, candidate)
    assert result["checks"][0]["value"] == pytest.approx(400 / 7)
    assert result["checks"][0]["difference"] == pytest.approx(0)


def test_freeze_rejects_source_report_stale_against_changed_evidence(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    bind_source_report(bundle, candidate)
    # The old report claims exact agreement with 7, while current evidence says 8.
    # Binding both current files must not certify that stale scientific check.
    evidence = read(candidate / "evidence.json")
    evidence["items"][0]["estimate"] = 8
    write(candidate / "evidence.json", evidence)
    with pytest.raises(ValueError):
        freeze_candidate(bundle, candidate)


@pytest.mark.parametrize("changed", ["model", "plan", "table", "report"])
def test_freeze_rechecks_source_report_content_not_just_its_file_hash(tmp_path, changed):
    bundle, candidate = setup_demo(tmp_path)
    report_path = bind_source_report(bundle, candidate)
    if changed == "model":
        spec = read(candidate / "model_spec.json")
        spec["parameters"]["intercept"] = 2
        write(candidate / "model_spec.json", spec)
    elif changed == "plan":
        plan = read(candidate / "source_checks.json")
        plan["checks"][0]["operator"]["missing_policy"] = "complete_cases"
        write(candidate / "source_checks.json", plan)
    elif changed == "table":
        table_path = candidate / "source_tables" / "invented.csv"
        table = pd.read_csv(table_path)
        table.loc[0, "y"] += 1
        table.to_csv(table_path, index=False)
        table_hash = hashlib.sha256(table_path.read_bytes()).hexdigest()
        plan = read(candidate / "source_checks.json")
        for check in plan["checks"]:
            check["table"]["sha256"] = table_hash
        write(candidate / "source_checks.json", plan)
        checks = read(candidate / "checks.json")
        for artifact in checks["artifacts"]:
            if artifact["path"] == "source_tables/invented.csv":
                artifact["sha256"] = table_hash
        write(candidate / "checks.json", checks)
    else:
        report = read(report_path)
        report["checks"][0]["value"] = 999
        report["checks"][0]["difference"] = 0
        write(report_path, report)
        checks = read(candidate / "checks.json")
        for artifact in checks["artifacts"]:
            if artifact["path"] == report_path.name:
                artifact["sha256"] = hashlib.sha256(report_path.read_bytes()).hexdigest()
        write(candidate / "checks.json", checks)
    with pytest.raises(ValueError):
        freeze_candidate(bundle, candidate)


def test_fresh_source_report_freezes_and_verifies_without_agent_code(tmp_path):
    bundle, candidate = setup_demo(tmp_path)
    bind_source_report(bundle, candidate)
    freeze_candidate(bundle, candidate)
    assert verify_candidate(bundle, candidate)

