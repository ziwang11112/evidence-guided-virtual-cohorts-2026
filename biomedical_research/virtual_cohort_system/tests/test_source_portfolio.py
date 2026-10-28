"""Verified-replay aggregation tests on invented data; backend remains mocked."""
import copy
import shutil

import pytest

from cohort_harness import source_portfolio as portfolio
from cohort_harness import source_replay as replay
from cohort_harness.lifecycle import freeze_candidate, read_json
from test_source_replay import bundle, fake_backend, write


def executed(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch)
    for i, seed in enumerate([11, 12]):
        replay.run_source_replay(root, candidate, f"initial_{i}", seed)
    return root, candidate


def test_verified_portfolio_retains_units_discrepancies_and_binding(tmp_path, monkeypatch):
    root, candidate = executed(tmp_path, monkeypatch)
    result = portfolio.summarize_source_portfolio(root, candidate, ["initial_0", "initial_1"], [11, 12])
    first = result["checks"][0]
    assert first["summary"]["mean"] == 5
    assert first["summary"]["mean_signed_discrepancy"] == -2
    assert first["summary"]["generator_seed_draw_sd"] == 0
    assert first["summary"]["discrepancy_pattern"] == "below_in_all_draws"
    assert len(result["schedule"]) == 2
    assert result["parent"]["candidate"] == "candidates/initial"
    assert result["scope"] == "verified_source_generator_seed_diagnostics_only"


@pytest.mark.parametrize("ids,seeds", [(["initial_0"], [11]),
    (["initial_0", "initial_0"], [11, 12]), (["initial_0", "initial_1"], [11, 11]),
    (["initial_0", "initial_1"], [12, 11]), (["initial_0", "initial_1"], [True, 12])])
def test_invalid_or_changed_schedule_rejected(tmp_path, monkeypatch, ids, seeds):
    root, candidate = executed(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        portfolio.summarize_source_portfolio(root, candidate, ids, seeds)


def test_failed_execution_not_dropped(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch, returncode=1)
    replay.run_source_replay(root, candidate, "failed", 11)
    with pytest.raises(ValueError, match="must succeed"):
        portfolio.summarize_source_portfolio(root, candidate, ["failed", "not_run"], [11, 12])


def test_tampered_feedback_rejected_before_summary(tmp_path, monkeypatch):
    root, candidate = executed(tmp_path, monkeypatch)
    path = root / "source_replays/initial_0/replay.json"
    report = read_json(path)
    report["contexts"][0]["checks"][0]["value"] = 7
    write(path, report)
    with pytest.raises(ValueError, match="recomputed"):
        portfolio.summarize_source_portfolio(root, candidate, ["initial_0", "initial_1"], [11, 12])


def test_pairing_preserves_tradeoff_and_rejects_changed_evidence(tmp_path, monkeypatch):
    root, candidate = executed(tmp_path, monkeypatch)
    other = root / "candidates/final"
    shutil.copytree(candidate, other)
    (other / "freeze.json").unlink()
    # Fictional source mean target 7, slope target 2. Mean improves, slope worsens.
    spec = read_json(other / "model_spec.json")
    spec["parameters"]["slope"] = 3
    write(other / "model_spec.json", spec)
    freeze_candidate(root, other)
    for i, seed in enumerate([11, 12]):
        replay.run_source_replay(root, other, f"final_{i}", seed)
    result = portfolio.compare_source_portfolios(root, candidate, other,
        ["initial_0", "initial_1"], ["final_0", "final_1"], [11, 12])
    assert result["comparisons"][0]["paired_summary"]["n_lower"] == 2
    assert result["comparisons"][1]["paired_summary"]["n_higher"] == 2
    third = root / "candidates/changed"
    shutil.copytree(other, third)
    (third / "freeze.json").unlink()
    evidence = read_json(third / "evidence.json")
    evidence["items"][0]["estimate"] = 99
    write(third / "evidence.json", evidence)
    freeze_candidate(root, third)
    for i, seed in enumerate([11, 12]):
        replay.run_source_replay(root, third, f"changed_{i}", seed)
    with pytest.raises(ValueError, match="unchanged evidence"):
        portfolio.compare_source_portfolios(root, candidate, third,
            ["initial_0", "initial_1"], ["changed_0", "changed_1"], [11, 12])


def test_undefined_check_is_retained_not_averaged_away(tmp_path, monkeypatch):
    root, candidate = executed(tmp_path, monkeypatch)
    original = portfolio.verify_source_replay
    # Deliberately inject an otherwise verified not-computable return to test
    # aggregation semantics; actual replay undefined-estimator paths tested elsewhere.
    def undefined(*args, **kwargs):
        report = copy.deepcopy(original(*args, **kwargs))
        if args[1] == "initial_1":
            c = report["contexts"][0]["checks"][0]
            c.pop("value"); c.pop("difference")
            c.update(status="not_computable", computation_error="invented degeneracy")
        return report
    monkeypatch.setattr(portfolio, "verify_source_replay", undefined)
    result = portfolio.summarize_source_portfolio(root, candidate, ["initial_0", "initial_1"], [11, 12])
    assert result["checks"][0]["summary"] is None
    assert len(result["checks"][0]["runs"]) == 2
    assert result["checks"][1]["summary"] is not None


def test_changed_source_assumption_text_cannot_hide_behind_same_id(tmp_path, monkeypatch):
    root, candidate = executed(tmp_path, monkeypatch)
    other = root / "candidates/changed_context"
    shutil.copytree(candidate, other)
    (other / "freeze.json").unlink()
    spec = read_json(other / "model_spec.json")
    for assumption in spec["assumptions"]:
        if assumption["id"] == "A1":
            assumption["description"] = "Different interpretation of the same invented source rows."
    write(other / "model_spec.json", spec)
    freeze_candidate(root, other)
    for i, seed in enumerate([11, 12]):
        replay.run_source_replay(root, other, f"changed_{i}", seed)
    with pytest.raises(ValueError, match="source interpretation assumptions"):
        portfolio.compare_source_portfolios(root, candidate, other,
            ["initial_0", "initial_1"], ["changed_0", "changed_1"], [11, 12])
