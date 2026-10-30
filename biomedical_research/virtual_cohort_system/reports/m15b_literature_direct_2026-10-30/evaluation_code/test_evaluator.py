"""Invented algebraic fixtures only: no paper, target, or generated-table reads."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluator as ev


def invented_frame() -> pd.DataFrame:
    rows = []
    for group, (race, sex) in enumerate(ev.GROUPS):
        for j in range(50):
            b = ((j % 10) - 4.5) / 3
            a = ((j // 10) - 2) * 0.3
            m, r = int(sex == "male"), int(race == "Black")
            rows.append({"sample_id": f"invented-{group}-{j:02d}", "race": race, "sex": sex,
                         "age": 40 + 10*a, "bmi": 28 + 5*b,
                         "urate": 6 + 0.8*b - 0.35*a + 0.5*m - 0.25*r,
                         "SDMVSTRA": 1 + j % 2, "SDMVPSU": 1 + (j // 2) % 2})
    return pd.DataFrame(rows)


def records(frame: pd.DataFrame) -> dict:
    return {row["estimand"]: row for row in ev.evaluate_table(frame, reference=True)}


def candidate(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[:, ev.BASE_COLUMNS].copy()


def test_exact_algebraic_coefficients_and_all_24_estimands():
    result = records(invented_frame())
    assert len(result) == 24
    assert sum(row["family"] == "global_coefficient" for row in result.values()) == 4
    assert sum(row["family"] == "group_reverse_coefficient" for row in result.values()) == 4
    assert sum(row["family"] == "group_summary" for row in result.values()) == 16
    assert result["global_bmi"]["value"] == pytest.approx(0.8)
    assert result["global_age"]["value"] == pytest.approx(-0.35)
    assert result["global_curvature"]["value"] == pytest.approx(0.0, abs=1e-12)
    assert result["global_interaction"]["value"] == pytest.approx(0.0, abs=1e-12)
    for race, sex in ev.GROUPS:
        row = result[f"reverse_{race}_{sex}"]
        assert row["value"] == pytest.approx(6.25)
        assert row["n"] == 50 and row["rank"] == 3
    for row in result.values():
        assert row["status"] == "ok"
        assert row["n_complete"] == row["n"]
        assert row["units"] and row["rank"] is not None


@pytest.mark.parametrize(("term", "expected"), [("curvature", 0.9), ("interaction", -0.7)])
def test_separate_quadratic_and_interaction_models(term, expected):
    frame = invented_frame()
    b = (frame["bmi"] - 28) / 5
    m = (frame["sex"] == "male").astype(float)
    frame["urate"] += expected * (b*b if term == "curvature" else b*m)
    result = records(frame)
    assert result[f"global_{term}"]["value"] == pytest.approx(expected)
    assert result[f"global_{term}"]["rank"] == 6
    assert result[f"global_{term}"]["n_parameters"] == 6


def test_hand_known_sample_sd_and_linear_quantiles():
    frame = invented_frame().iloc[:4].copy()
    frame["urate"] = [0.0, 2.0, 4.0, 10.0]
    result = records(frame)
    assert result["mean_White_male"]["value"] == 4.0
    assert result["sd_White_male"]["value"] == pytest.approx(np.sqrt(56.0/3.0))
    assert result["median_White_male"]["value"] == 3.0
    assert result["q90_White_male"]["value"] == pytest.approx(8.2)


def test_missing_group_retains_every_failed_estimand():
    frame = invented_frame()
    frame = frame.loc[~((frame["race"] == "Black") & (frame["sex"] == "female"))]
    result = records(frame)
    missing = [row for row in result.values() if row["race"] == "Black" and row["sex"] == "female"]
    assert len(result) == 24 and len(missing) == 5
    for row in missing:
        assert row["n"] == row["n_complete"] == row["rank"] == 0
        assert row["value"] is None and row["status"] == "insufficient_n"


def test_rank_deficiency_and_nonfinite_never_drop_rows():
    constant_age = invented_frame()
    constant_age["age"] = 40.0
    result = records(constant_age)
    for key in ev.GLOBAL_IDS:
        assert result[key]["status"] == "rank_deficient"
        assert result[key]["n"] == 200 and result[key]["rank"] < result[key]["n_parameters"]
    assert result["reverse_White_male"]["status"] == "rank_deficient"
    nonfinite = invented_frame()
    nonfinite.loc[0, "urate"] = np.inf
    result = records(nonfinite)
    assert len(result) == 24
    assert result["global_bmi"]["status"] == "nonfinite"
    assert result["global_bmi"]["n"] == 200 and result["global_bmi"]["n_complete"] == 199
    assert result["global_bmi"]["rank"] == 5
    assert result["reverse_White_male"]["rank"] is None
    assert result["mean_White_male"]["value"] is None
    assert result["mean_White_female"]["status"] == "ok"
    json.dumps(list(result.values()), allow_nan=False)


def test_singleton_sd_fails_while_other_summaries_are_defined():
    result = records(invented_frame().iloc[:1])
    assert result["sd_White_male"]["status"] == "insufficient_n"
    for statistic in ("mean", "median", "q90"):
        assert result[f"{statistic}_White_male"]["status"] == "ok"


def test_pair_preserves_id_values_order_and_fixed_quota():
    reference = invented_frame()
    generated = candidate(reference)
    result = ev.compare_tables(reference, generated)
    assert len(result) == 24
    assert all(row["difference_generated_minus_measured"] == 0.0 for row in result)
    with pytest.raises(ev.EvaluationError, match="rows and order"):
        ev.compare_tables(reference, generated.iloc[::-1])
    changed = generated.copy()
    changed.loc[0, "bmi"] += 0.001
    with pytest.raises(ev.EvaluationError, match="bmi"):
        ev.compare_tables(reference, changed)
    with pytest.raises(ev.EvaluationError, match="200"):
        ev.compare_tables(reference.iloc[:-1], generated.iloc[:-1])


def test_row_order_invariance_and_id_preservation():
    reference = invented_frame()
    generated = candidate(reference)
    generated["urate"] += 0.05 * ((generated["bmi"] - 28) / 5)
    order = np.random.default_rng(214).permutation(len(reference))
    permuted = reference.iloc[order]
    assert ev.evaluate_table(reference, reference=True) == ev.evaluate_table(permuted, reference=True)
    assert ev.compare_tables(reference, generated) == ev.compare_tables(permuted, generated.iloc[order])
    assert ev.reference_sensitivity(reference) == ev.reference_sensitivity(permuted)


@pytest.mark.parametrize("mutation,match", [
    (lambda frame: frame.assign(race="white"), "race"),
    (lambda frame: frame.assign(sex="Male"), "sex"),
    (lambda frame: frame.assign(sample_id="duplicated"), "Duplicate sample_id"),
    (lambda frame: frame.assign(extra=1), "Unexpected"),
    (lambda frame: frame.drop(columns="urate"), "missing"),
])
def test_structural_failures(mutation, match):
    with pytest.raises(ev.EvaluationError, match=match):
        ev.evaluate_table(mutation(candidate(invented_frame())))


def test_joint_cluster_deletions_counts_range_and_positive_stability():
    reference = invented_frame()
    result = ev.reference_sensitivity(reference)
    assert result["kind"] == "descriptive_leave_one_joint_psu_out"
    assert len(result["summaries"]) == 4
    for summary in result["summaries"]:
        assert summary["omitted_psu_group_count"] == 4  # Not two repeated PSU labels.
        assert len(summary["deletions"]) == summary["finite_deletion_count"] == 4
        assert summary["rank_failure_count"] == summary["failed_deletion_count"] == 0
        for deletion in summary["deletions"]:
            assert deletion["n_omitted"] + deletion["n_retained"] == 200
            assert deletion["n_retained"] == deletion["n"]
            assert deletion["rank"] == deletion["n_parameters"]
        values = [deletion["value"] for deletion in summary["deletions"]]
        assert summary["range_min"] == min(values) and summary["range_max"] == max(values)
    primary = result["summaries"][0]
    assert primary["range_min"] == pytest.approx(0.8)
    assert primary["all_deletions_sign_stable_with_full"] is True
    serialized = json.dumps(result, allow_nan=False)
    for forbidden_key in ('"p_value"', '"ci_lower"', '"ci_upper"', '"standard_error"', '"confidence_level"'):
        assert forbidden_key not in serialized


def test_deletion_failures_retained_and_not_labeled_stable():
    reference = invented_frame()
    reference["SDMVSTRA"] = 1
    reference["SDMVPSU"] = np.where(reference["sex"] == "male", 1, 2)
    result = ev.reference_sensitivity(reference)
    for summary in result["summaries"]:
        assert summary["omitted_psu_group_count"] == 2
        assert summary["rank_failure_count"] == summary["failed_deletion_count"] == 2
        assert summary["range_min"] is summary["range_max"] is None
        assert summary["all_deletions_sign_stable_with_full"] is None
        assert summary["status"] == "incomplete"
        assert all(row["n_retained"] == row["n_omitted"] == 100 for row in summary["deletions"])


def test_private_weight_and_identifier_columns_are_ignored():
    frame = invented_frame()
    expected = ev.evaluate_table(frame, reference=True)
    expected_sensitivity = ev.reference_sensitivity(frame)
    frame["WTPH2YR"] = np.linspace(1, 1e9, len(frame))
    frame["SEQN"] = np.arange(70000, 70200)
    assert ev.evaluate_table(frame, reference=True) == expected
    assert ev.reference_sensitivity(frame) == expected_sensitivity


def test_missing_design_cell_rejected():
    reference = invented_frame()
    reference.loc[0, "SDMVPSU"] = np.nan
    with pytest.raises(ev.EvaluationError, match="design cells"):
        ev.reference_sensitivity(reference)


def test_cli_without_execute_does_not_read_any_input(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("Gate must not be reached without --execute")
    monkeypatch.setattr(ev, "verify_release", forbidden)
    args = ["--release-manifest", str(tmp_path / "missing.json"),
            "--reference", str(tmp_path / "missing-reference.csv"),
            "--initial", str(tmp_path / "missing-initial.csv"),
            "--final", str(tmp_path / "missing-final.csv"),
            "--output-dir", str(tmp_path / "output")]
    with pytest.raises(SystemExit) as caught:
        ev.main(args)
    assert caught.value.code == 2
    assert not (tmp_path / "output").exists()


def test_unreviewed_release_rejected_before_any_hash_or_reference_read(monkeypatch, tmp_path):
    manifest = tmp_path / "release.json"
    manifest.write_text(json.dumps({"schema_version": 1, "kind": "m15b_target_evaluation_release",
                                    "evaluation_authorized": True, "controller_checks": {}}))
    def forbidden(*args, **kwargs):
        raise AssertionError("No data hash/read before controller checks")
    monkeypatch.setattr(ev, "_check_hash", forbidden)
    with pytest.raises(ev.EvaluationError, match="controller check"):
        ev.verify_release(manifest, tmp_path / "ref.csv", tmp_path / "initial.csv", tmp_path / "final.csv")


def test_invented_csv_reader_preserves_leading_zero_ids_and_rejects_duplicate_headers(tmp_path):
    path = tmp_path / "invented.csv"
    path.write_text("sample_id,race,sex,age,bmi,urate\n001,White,male,40,28,6\n", encoding="utf-8")
    assert ev.read_analysis_table(path, reference=False).loc[0, "sample_id"] == "001"
    path.write_text("sample_id,race,sex,age,bmi,urate,urate\n001,White,male,40,28,6,6\n", encoding="utf-8")
    with pytest.raises(ev.EvaluationError, match="Duplicate CSV"):
        ev.read_analysis_table(path, reference=False)


def test_difference_and_direction_are_only_defined_for_estimable_records():
    reference = invented_frame()
    generated = candidate(reference)
    generated["urate"] += 0.2 * ((generated["bmi"] - 28) / 5)
    result = {row["estimand"]: row for row in ev.compare_tables(reference, generated)}
    assert result["global_bmi"]["difference_generated_minus_measured"] == pytest.approx(0.2)
    assert result["global_bmi"]["same_sign"] is True
    assert result["mean_White_male"]["same_sign"] is None
    generated.loc[0, "urate"] = np.nan
    result = {row["estimand"]: row for row in ev.compare_tables(reference, generated)}
    assert result["global_bmi"]["difference_generated_minus_measured"] is None
    assert result["global_bmi"]["same_sign"] is None


def invented_release(tmp_path):
    """Minimal fake lifecycle objects; these do not claim a genuine frozen bundle."""
    bundle = tmp_path / "invented-bundle"
    initial = bundle / "candidates" / "initial"
    final = bundle / "candidates" / "final"
    initial.mkdir(parents=True)
    final.mkdir(parents=True)
    (bundle / "task.json").write_text("{}")
    (bundle / "observed.csv").write_text("invented observed placeholder")
    reference_path = tmp_path / "invented-reference.csv"
    reference_path.write_text("invented reference placeholder")
    for directory in (initial, final):
        (directory / "generated.csv").write_text("invented candidate placeholder")
    commitments = {"task.json": ev._sha256(bundle / "task.json"),
                   "observed.csv": ev._sha256(bundle / "observed.csv")}
    receipts = {}
    for index, directory in enumerate((initial, final)):
        relative = "candidates/" + directory.name
        receipts[relative] = {"candidate": relative, "route": "generated.csv", "revision_index": index,
                              "commitments": {**commitments, relative + "/generated.csv":
                                              ev._sha256(directory / "generated.csv")},
                              "parent": None if index == 0 else {
                                  "candidate": "candidates/initial", "receipt_path": "candidates/initial/freeze.json"}}
        (directory / "freeze.json").write_text(json.dumps(receipts[relative]))
    manifest = {
        "schema_version": 1, "kind": "m15b_target_evaluation_release", "evaluation_authorized": True,
        "bundle_path": str(bundle), "reference_path": str(reference_path),
        "reference_sha256": ev._sha256(reference_path),
        "protocol_sha256": ev._sha256(Path(ev.__file__).resolve().parent.parent / "PROTOCOL.md"),
        "evaluator_sha256": ev._sha256(Path(ev.__file__)),
        "task_sha256": commitments["task.json"], "observed_sha256": commitments["observed.csv"],
        "controller_checks": {key: True for key in (
            "both_releases_verified", "source_feedback_binding_verified", "source_exposure_map_verified",
            "preservation_verified", "independent_code_review_complete")},
    }
    for directory in (initial, final):
        manifest[directory.name] = {"candidate": "candidates/" + directory.name,
                                    "table_sha256": ev._sha256(directory / "generated.csv"),
                                    "freeze_sha256": ev._sha256(directory / "freeze.json")}
    manifest_path = tmp_path / "invented-release.json"
    manifest_path.write_text(json.dumps(manifest))
    return manifest_path, reference_path, initial / "generated.csv", final / "generated.csv", receipts


def test_release_hash_order_with_explicitly_mocked_lifecycle(monkeypatch, tmp_path):
    manifest, reference, initial, final, receipts = invented_release(tmp_path)
    from cohort_harness import lifecycle
    lifecycle_calls, hash_calls = [], []
    def fake_verify(bundle, relative):
        lifecycle_calls.append(relative)
        return receipts[relative]
    real_hash = ev._check_hash
    def traced_hash(path, digest, label):
        hash_calls.append(label)
        real_hash(path, digest, label)
    monkeypatch.setattr(lifecycle, "verify_candidate", fake_verify)
    monkeypatch.setattr(ev, "_check_hash", traced_hash)
    ev.verify_release(manifest, reference, initial, final)
    assert lifecycle_calls == ["candidates/initial", "candidates/final"]
    assert hash_calls == ["protocol", "evaluator", "task", "observed", "initial freeze", "initial table",
                          "final freeze", "final table", "reference"]
    hash_calls.clear()
    (final.parent / "freeze.json").write_text("tampered invented freeze")
    with pytest.raises(ev.EvaluationError, match="final freeze"):
        ev.verify_release(manifest, reference, initial, final)
    assert "reference" not in hash_calls


def test_self_hash_tampering_stops_before_candidate_or_reference_access(monkeypatch, tmp_path):
    manifest, reference, initial, final, _ = invented_release(tmp_path)
    release = json.loads(manifest.read_text())
    release["evaluator_sha256"] = "0" * 64
    manifest.write_text(json.dumps(release))
    from cohort_harness import lifecycle
    def forbidden(*args, **kwargs):
        raise AssertionError("Candidate verifier must not be reached with changed evaluator")
    monkeypatch.setattr(lifecycle, "verify_candidate", forbidden)
    with pytest.raises(ev.EvaluationError, match="evaluator hash"):
        ev.verify_release(manifest, reference, initial, final)
