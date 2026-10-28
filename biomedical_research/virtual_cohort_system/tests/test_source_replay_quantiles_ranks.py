"""New statistic kinds through mocked replay; this does not establish isolation."""
from __future__ import annotations

import pandas as pd
import pytest

from cohort_harness import execution, source_checks, source_replay as replay
from cohort_harness.lifecycle import read_json, sha256, verify_candidate
from test_source_replay import bundle, fake_backend, write


def add_checks(plan, source, *, method="linear"):
    context = plan["contexts"][0]
    evidence_path = source.parent / "evidence.json"
    evidence = read_json(evidence_path)
    common = {**evidence["items"][0], "selection": "Four invented source-context rows"}
    definitions = [
        ("median", "median", {"column": "y", "method": "linear"}, {"method": method}, 4),
        ("lower", "quantile", {"column": "y", "q": 0.25, "method": "linear"}, {"q": 0.25, "method": method}, 1),
        ("upper", "quantile", {"column": "y", "q": 0.75, "method": "linear"}, {"q": 0.75, "method": method}, 8),
        ("rank", "spearman_correlation", {"x": "x", "y": "y"}, {}, 1),
    ]
    for name, kind, fields, evidence_fields, value in definitions:
        unit = "1" if kind == "spearman_correlation" else "y_unit"
        variables = ["x", "y"] if kind == "spearman_correlation" else ["y"]
        evidence["items"].append({**common, "id": name, "kind": kind, "estimate": value,
                                  "variables": variables, "unit": unit, **evidence_fields})
        context["checks"].append({
            "id": name, "evidence_id": name, "status": "approximate", "assumption_ids": [],
            "reason": "Invented source fixture; method unknown only when declared in evidence.",
            "operator": {"kind": kind, "unit": unit, "selection": [], "missing_policy": "error", **fields},
        })
    write(evidence_path, evidence)


@pytest.mark.parametrize("method", ["linear", "not_reported"])
def test_replay_links_new_statistics(tmp_path, monkeypatch, method):
    root, candidate = bundle(tmp_path, edit=lambda p, s: add_checks(p, s, method=method))
    fake_backend(monkeypatch)
    original = {name: sha256(candidate / name) for name in ("freeze.json", "generator.py", "model_spec.json")}
    report = replay.run_source_replay(root, candidate, "new", 17)
    assert report["schema_version"] == 2
    assert report["operator_engine_sha256"] == sha256(source_checks.__file__)
    records = {check["id"]: check for check in report["contexts"][0]["checks"]}
    # Source output is [1,1,7,11]. Median=(1+7)/2=4; upper quartile=7+.25*(11-7)=8.
    for name, expected in {"median": 4, "lower": 1, "upper": 8, "rank": 1}.items():
        record = records[name]
        assert record["value"] == pytest.approx(expected)
        assert record["difference"] == pytest.approx(0)
        assert record["status"] == "approximate"
        assert record["generation_link_verified"] is True
        assert record["n_used"] == 4
    assert len({check["generated_sha256"] for check in records.values()}) == 1
    assert original == {name: sha256(candidate / name) for name in original}
    assert replay.verify_source_replay(root, "new", candidate=candidate) == report
    verify_candidate(root, candidate)
    report["contexts"][0]["checks"][-2]["value"] = 0
    write(root / "source_replays/new/replay.json", report)
    with pytest.raises(ValueError, match="recomputed"):
        replay.verify_source_replay(root, "new", candidate=candidate)


@pytest.mark.parametrize("mutation", ["wrong_q", "bad_method", "unknown_exact", "pearson_as_spearman"])
def test_bad_new_definitions_fail_before_execution(tmp_path, monkeypatch, mutation):
    def edit(plan, source):
        add_checks(plan, source, method="not_reported" if mutation == "unknown_exact" else "linear")
        context = plan["contexts"][0]
        if mutation == "wrong_q":
            context["checks"][-2]["operator"]["q"] = 0.25
        elif mutation == "bad_method":
            context["checks"][-2]["operator"]["method"] = "nearest"
        elif mutation == "pearson_as_spearman":
            context["checks"][-1]["operator"]["kind"] = "correlation"
        else:
            context["assumption_ids"] = []
            for check in context["checks"]:
                check["status"] = "computed"
    root, candidate = bundle(tmp_path, edit=edit)
    monkeypatch.setattr(execution, "run_candidate", lambda *a, **k: pytest.fail("invalid definition must not execute"))
    with pytest.raises(ValueError):
        replay.run_source_replay(root, candidate, "bad", 2)
    assert not (root / "source_replays/bad").exists()


def test_constant_ranks_remain_not_computable(tmp_path, monkeypatch):
    def edit(plan, source):
        add_checks(plan, source)
        table = pd.read_csv(source)
        table["x"] = 1
        table.to_csv(source, index=False)
        plan["contexts"][0]["input"]["sha256"] = sha256(source)
    root, candidate = bundle(tmp_path, edit=edit)
    fake_backend(monkeypatch)
    report = replay.run_source_replay(root, candidate, "flat", 5)
    rank = report["contexts"][0]["checks"][-1]
    assert rank["status"] == "not_computable"
    assert rank["generation_link_verified"] is True
    assert "nonconstant ranks" in rank["computation_error"]
    assert "value" not in rank and "difference" not in rank
    assert replay.verify_source_replay(root, "flat", candidate=candidate) == report


@pytest.mark.parametrize("mutation", ["operator_hash", "historical_version"])
def test_replay_requires_recorded_code_version(tmp_path, monkeypatch, mutation):
    root, candidate = bundle(tmp_path, edit=add_checks)
    fake_backend(monkeypatch)
    report = replay.run_source_replay(root, candidate, "code", 5)
    if mutation == "operator_hash":
        report["operator_engine_sha256"] = "0" * 64
    else:
        report["schema_version"] = 1
        del report["operator_engine_sha256"]
    write(root / "source_replays/code/replay.json", report)
    with pytest.raises(ValueError, match="recorded engine version"):
        replay.verify_source_replay(root, "code", candidate=candidate)
