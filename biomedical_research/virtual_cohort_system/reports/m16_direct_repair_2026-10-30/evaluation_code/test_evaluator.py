"""Invented data only: wrapper arithmetic, preservation and pre-reference gates."""
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("m16_evaluator", HERE / "evaluator.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)
REAL_PROJECT = ev.PROJECT
sys.path.insert(0, str(REAL_PROJECT))
from cohort_harness.lifecycle import freeze_candidate


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def binding(path):
    return {"path": str(path), "sha256": ev.sha(path)}


def invented():
    records = []
    for g, (race, sex) in enumerate(ev.load_estimands().GROUPS):
        for j in range(50):
            age = 20 + ((j * 7 + g * 3) % 37)
            bmi = 19 + ((j * 11 + g * 5) % 43) / 2
            b, a, m, r = (bmi - 28) / 5, (age - 40) / 10, sex == "male", race == "Black"
            records.append({"sample_id": f"fixture{g}{j:02}", "race": race, "sex": sex,
                            "age": age, "bmi": bmi,
                            "urate": 4 + .4*b - .15*a + .5*m + .2*r,
                            "SDMVSTRA": str(1 + j % 5), "SDMVPSU": str(1 + j % 2),
                            "SEQN": g*50+j, "WTMEC2YR": 100 + j})
    return pd.DataFrame(records)


def task():
    columns = []
    for name, kind, role, unit in [("sample_id", "string", "identifier", ""),
                                   ("race", "category", "observed", ""),
                                   ("sex", "category", "observed", ""),
                                   ("age", "number", "observed", "years"),
                                   ("bmi", "number", "observed", "kg/m2"),
                                   ("urate", "number", "generated", "mg/dL")]:
        item = {"name": name, "kind": kind, "role": role, "unit": unit, "nullable": False}
        if name in ("race", "sex"):
            item["categories"] = ["White", "Black"] if name == "race" else ["male", "female"]
        columns.append(item)
    return {"schema_version": 1, "task_id": "invented-m16-test", "mode": "enrichment",
            "population": "Invented engineering fixture; no actual participants", "row_id": "sample_id",
            "n_rows": 200, "columns": columns,
            "information_policy": {"mode": "prior_only", "excluded_cohorts": [], "allowed_tools": []},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 2}}


@pytest.fixture
def release_fixture(tmp_path, monkeypatch):
    run = tmp_path / "run"
    run.mkdir()
    project = tmp_path / "project"
    checker = project / "cohort_harness/self_consistency.py"
    checker.parent.mkdir(parents=True)
    checker.write_text("# Invented binding fixture; never executed.\n", encoding="utf-8")
    monkeypatch.setattr(ev, "PROJECT", project)
    for name in ("PROTOCOL.md", "controller.py"):
        (run/name).write_text("Invented fixture only\n", encoding="utf-8")
    ref = invented()
    ref_path = run / "private/reference.csv"
    ref_path.parent.mkdir()
    ref.to_csv(ref_path, index=False)
    observed = ref.loc[:, ["sample_id", "race", "sex", "age", "bmi"]]
    bundles = []
    for bid in ev.BUILDERS:
        bundle = run / "visible" / bid / "bundle"
        bundle.mkdir(parents=True)
        builder_task = task()
        builder_task["task_id"] += "-" + bid
        write_json(bundle / "task.json", builder_task)
        write_json(bundle / "registry.json", {"artifacts": []})
        observed.to_csv(bundle / "observed.csv", index=False)
        bundles.append(bundle)
    prelaunch = run / "prelaunch.json"
    files = {"PROTOCOL.md": ev.sha(run/"PROTOCOL.md"), "controller.py": ev.sha(run/"controller.py")}
    for bundle in bundles:
        for name in ("task.json", "observed.csv"):
            files[(bundle/name).relative_to(run).as_posix()] = ev.sha(bundle/name)
    write_json(prelaunch, {"files": files, "engine_files": {str(checker): ev.sha(checker)},
                          "reference": binding(ref_path), "reference_weight_column": "WTMEC2YR",
                          "registry_prefixes": {bid: [] for bid in ev.BUILDERS}})
    release = {"schema_version": 1, "kind": "m16_target_evaluation_release", "evaluation_authorized": True,
               "controller_checks": {k: True for k in ev.REQUIRED_CHECKS},
               "protocol": binding(run/"PROTOCOL.md"), "controller": binding(run/"controller.py"),
               "prelaunch": binding(prelaunch), "self_checker": binding(checker),
               "evaluator": binding(HERE/"evaluator.py"), "estimands": binding(ev.FROZEN_PATH),
               "reference": binding(ref_path), "reference_weight_column": "WTMEC2YR", "builders": []}
    for idx, bundle in enumerate(bundles):
        bid = ev.BUILDERS[idx]
        builder = {"id": bid, "bundle_path": str(bundle), "status": "complete",
                   "task_sha256": ev.sha(bundle/"task.json"), "observed_sha256": ev.sha(bundle/"observed.csv")}
        shifts = ((.3, .1), (0, .2), (.5, .5))[idx]
        for stage, shift in zip(("initial", "final"), shifts):
            candidate = bundle / "candidates" / stage
            (candidate/"audit").mkdir(parents=True)
            write_json(candidate/"evidence.json", {"schema_version": 1, "sources": [], "items": []})
            write_json(candidate/"model_spec.json", {"parameters": {}, "assumptions": [], "parameter_provenance": {}})
            write_json(candidate/"audit/construction.json", {"fixture": "Test binding only"})
            write_json(candidate/"audit/revision_plan.json", {"stage": stage, "fixture": True})
            precommit = {"builder": bid, "candidate": "candidates/"+stage,
                         "generated_exists": False, "created_utc": datetime.now(timezone.utc).isoformat(),
                         "prelaunch_sha256": ev.sha(prelaunch),
                         "files": {name: ev.sha(candidate/name) for name in ev.PREAUTHOR_FILES}}
            receipt_path = run / "commitments" / bid / (stage+".json")
            write_json(receipt_path, precommit)
            (candidate/"audit/preauthoring_commitment.json").write_bytes(receipt_path.read_bytes())
            gen = ref.loc[:, list(ev.load_estimands().BASE_COLUMNS)].copy()
            gen["urate"] += shift
            gen.to_csv(candidate/"generated.csv", index=False)
            (candidate/"decision.md").write_text("Invented test fixture.\n", encoding="utf-8")
            write_json(candidate/"checks.json", {"scope": "fixture_only", "records": [
                {"name": "fixture", "status": "not_computable", "detail": "No biomedical assertion"}], "artifacts": []})
            if stage == "initial":
                freeze_candidate(bundle, candidate)
            else:
                freeze_candidate(bundle, candidate, parent_receipt=bundle/"candidates/initial/freeze.json",
                                 revision={"kind": "retain" if shifts[0] == shifts[1] else "revise",
                                           "reason": "Invented fixture", "addressed_findings": [],
                                           "remaining_limitations": ["Not clinical data"]})
            builder[stage] = {"candidate": "candidates/"+stage, "freeze_sha256": ev.sha(candidate/"freeze.json"),
                              "table_sha256": ev.sha(candidate/"generated.csv"), "preauthoring": binding(receipt_path)}
        release["builders"].append(builder)
    path = run / "release.json"
    write_json(path, release)
    return run, path, release, ref


def protect_reference(monkeypatch, reference_path):
    previous = Path.read_bytes
    calls = []
    def guarded(path):
        if path.resolve() == reference_path.resolve():
            calls.append(path)
            raise AssertionError("Reference read before gate completed")
        return previous(path)
    monkeypatch.setattr(Path, "read_bytes", guarded)
    return calls


def test_frozen_exact_and_known_coefficients():
    assert ev.sha(ev.FROZEN_PATH) == ev.FROZEN_SHA256
    frame = invented().drop(columns=["SEQN", "WTMEC2YR"])
    output = {r["estimand"]: r for r in ev.load_estimands().evaluate_table(frame, reference=True)}
    assert len(output) == 24
    assert output["global_bmi"]["value"] == pytest.approx(.4)
    assert output["global_age"]["value"] == pytest.approx(-.15)


def test_only_task_id_may_differ():
    first, second = task(), task()
    second["task_id"] = "different-session-identity"
    assert ev.task_semantics(first) == ev.task_semantics(second)
    second["population"] = "Different selected population"
    assert ev.task_semantics(first) != ev.task_semantics(second)


def test_full_real_lifecycle_gate_and_six_outputs(release_fixture):
    run, path, release, ref = release_fixture
    verified, raw = ev.verify_release(path, run=run)
    result = ev.evaluate_verified(verified, raw)
    assert len(result["candidate_comparisons"]) == 6
    assert sum(len(c["estimands"]) for c in result["candidate_comparisons"]) == 144
    assert len(result["reference_estimands"]) == 24
    assert len(result["initial_final_changes"]) == 72
    assert [x["changed_urate_rows"] for x in result["builder_outcomes"]] == [200, 200, 0]
    assert result["reference_sensitivity"]["summaries"][0]["omitted_psu_group_count"] == 10
    by_key = {(x["builder"], x["estimand"]): x for x in result["initial_final_changes"]}
    assert by_key["b1", "mean_White_male"]["direction"] == "lower"
    assert by_key["b2", "mean_White_male"]["direction"] == "higher"
    assert by_key["b3", "mean_White_male"]["direction"] == "unchanged"


@pytest.mark.parametrize("fault", ["review", "protocol", "prelaunch_engine", "freeze", "model_commit", "missing_builder", "reference_commitment"])
def test_gate_failure_never_opens_reference(release_fixture, monkeypatch, fault):
    run, path, release, ref = release_fixture
    if fault == "review":
        release["controller_checks"]["budgets_verified"] = False
    elif fault == "protocol":
        (run/"PROTOCOL.md").write_text("changed", encoding="utf-8")
    elif fault == "prelaunch_engine":
        Path(release["self_checker"]["path"]).write_text("changed", encoding="utf-8")
        release["self_checker"] = binding(Path(release["self_checker"]["path"]))
    elif fault == "freeze":
        release["builders"][1]["initial"]["freeze_sha256"] = "0"*64
    elif fault == "model_commit":
        receipt = Path(release["builders"][0]["initial"]["preauthoring"]["path"])
        value = ev.load_json(receipt)
        value["generated_exists"] = True
        write_json(receipt, value)
        release["builders"][0]["initial"]["preauthoring"] = binding(receipt)
    elif fault == "reference_commitment":
        release["reference"]["sha256"] = "0"*64
    else:
        release["builders"].pop()
    write_json(path, release)
    calls = protect_reference(monkeypatch, Path(release["reference"]["path"]))
    with pytest.raises(ValueError):
        ev.verify_release(path, run=run)
    assert not calls


def test_reference_bytes_opened_once(release_fixture, monkeypatch):
    run, path, release, ref = release_fixture
    reference_path = Path(release["reference"]["path"]).resolve()
    previous = Path.read_bytes
    calls = []
    def counted(path):
        if path.resolve() == reference_path:
            calls.append(path)
        return previous(path)
    monkeypatch.setattr(Path, "read_bytes", counted)
    verified, raw = ev.verify_release(path, run=run)
    ev.evaluate_verified(verified, raw)
    assert len(calls) == 1


def test_failure_kept_without_replacement(release_fixture):
    run, path, release, ref = release_fixture
    builder = release["builders"][1]
    builder["status"] = "failed"
    builder.pop("final")
    failure = run / "failure_b2.json"
    write_json(failure, {"reason": "Invented terminal failure"})
    builder["failure_record"] = binding(failure)
    write_json(path, release)
    verified, raw = ev.verify_release(path, run=run)
    result = ev.evaluate_verified(verified, raw)
    assert len(result["candidate_comparisons"]) == 5
    assert len(result["builder_outcomes"]) == 3
    assert result["builder_outcomes"][1]["status"] == "failed"
    assert result["builder_outcomes"][1]["changed_urate_rows"] is None


def test_weight_mapping_changes_no_estimand():
    ref = invented()
    parsed = ev.parse_csv_bytes(ref.to_csv(index=False).encode(), reference=True)
    stripped = ref.drop(columns=["SEQN", "WTMEC2YR"])
    module = ev.load_estimands()
    assert module.evaluate_table(parsed, reference=True) == module.evaluate_table(stripped, reference=True)


def test_unexpected_and_duplicate_columns_rejected():
    ref = invented()
    ref["hidden_extra"] = 1
    with pytest.raises(ValueError, match="schema"):
        ev.parse_csv_bytes(ref.to_csv(index=False).encode(), reference=True)
    with pytest.raises(ValueError, match="Duplicate"):
        ev.parse_csv_bytes(b"sample_id,sample_id\na,a\n", reference=False)


def test_nonfinite_estimand_retained():
    module = ev.load_estimands()
    ref = invented().loc[:, list(module.BASE_COLUMNS)]
    ref.loc[0, "urate"] = np.nan
    records = module.evaluate_table(ref)
    assert len(records) == 24
    assert records[0]["status"] == "nonfinite"
    assert records[0]["value"] is None


def test_pairing_matches_frozen_compare(release_fixture):
    run, path, release, ref = release_fixture
    verified, raw = ev.verify_release(path, run=run)
    result = ev.evaluate_verified(verified, raw)
    parsed = ev.parse_csv_bytes(raw, reference=True)
    module = ev.load_estimands()
    for candidate in result["candidate_comparisons"]:
        builder = release["builders"][ev.BUILDERS.index(candidate["builder"])]
        gen = ev.parse_csv_bytes((Path(builder["bundle_path"])/builder[candidate["stage"]]["candidate"]/
                                  "generated.csv").read_bytes(), reference=False)
        assert candidate["estimands"] == module.compare_tables(parsed, gen)


def test_output_exclusive_and_csv_complete(release_fixture, tmp_path):
    run, path, release, ref = release_fixture
    verified, raw = ev.verify_release(path, run=run)
    result = ev.evaluate_verified(verified, raw)
    destination = tmp_path/"results"
    ev.write_results(destination, result)
    assert len(pd.read_csv(destination/"estimands.csv")) == 144
    assert len(pd.read_csv(destination/"initial_final_changes.csv")) == 72
    with pytest.raises(ValueError, match="no overwrite"):
        ev.write_results(destination, result)


def test_cli_disabled_without_read(tmp_path):
    with pytest.raises(SystemExit) as error:
        ev.main(["--release-manifest", str(tmp_path/"missing.json"), "--output-dir", str(tmp_path/"out")])
    assert error.value.code == 2
