"""Invented algebraic fixtures only. No experimental file is opened."""
import copy
import math

import pytest

import audit


def invented_rows(n_per_group=50, quadratic=0.0, interaction=0.0):
    rows = []
    for group_index, (race, sex) in enumerate(audit.GROUPS):
        for index in range(n_per_group):
            age = 22 + (index * 7 + group_index * 3) % 34
            bmi = 20 + (index * 11 + group_index * 5) % 27 + index / 100
            b, a = (bmi - 28) / 5, (age - 40) / 10
            m, r = int(sex == "male"), int(race == "Black")
            urate = 4 + 0.75 * b + 0.4 * a + 0.8 * m - 0.3 * r + quadratic * b ** 2 + interaction * b * m
            rows.append({"sample_id": f"invented-{group_index}-{index:03d}", "race": race, "sex": sex,
                         "age": str(age), "bmi": str(bmi), "urate": str(urate),
                         "SDMVSTRA": str(index % 3), "SDMVPSU": str(index % 2)})
    return rows


def candidate(rows):
    return [{key: row[key] for key in audit.CANDIDATE_COLUMNS} for row in rows]


def observed(rows):
    return [{key: row[key] for key in audit.OBSERVED_COLUMNS} for row in rows]


def test_known_forward_linear_coefficients_and_fixed_count():
    result = audit.estimate_table(invented_rows())
    assert len(result) == 24
    assert result["global.bmi"]["value"] == pytest.approx(0.75, abs=1e-12)
    assert result["global.age"]["value"] == pytest.approx(0.4, abs=1e-12)
    assert result["global.bmi"]["matrix_rank"] == 5
    assert result["global.curvature"]["matrix_rank"] == 6


def test_separate_quadratic_and_interaction_formulas():
    curvature = audit.estimate_table(invented_rows(quadratic=-0.35))
    interaction = audit.estimate_table(invented_rows(interaction=0.55))
    assert curvature["global.curvature"]["value"] == pytest.approx(-0.35, abs=1e-12)
    assert interaction["global.interaction"]["value"] == pytest.approx(0.55, abs=1e-12)


def test_known_reverse_fit_no_reciprocal_conversion():
    rows = invented_rows(n_per_group=8)
    for index, row in enumerate(rows):
        age = float(row["age"])
        urate = 2 + (index % 8) ** 2 / 5
        row["urate"] = str(urate)
        row["bmi"] = str(22 + 1.7 * urate - 0.08 * age)
    estimates = audit.estimate_table(rows)
    for race, sex in audit.GROUPS:
        assert estimates[f"group.{race}.{sex}.reverse"]["value"] == pytest.approx(1.7, abs=1e-12)


def test_stdlib_summaries_and_explicit_interpolation():
    rows = invented_rows(n_per_group=4)
    for index, row in enumerate(rows):
        row["urate"] = str([1, 2, 3, 10][index % 4])
    values = audit.estimate_table(rows)
    prefix = "group.White.male."
    assert values[prefix + "mean"]["value"] == 4
    assert values[prefix + "sd"]["value"] == pytest.approx(math.sqrt(50 / 3))
    assert values[prefix + "median"]["value"] == 2.5
    assert values[prefix + "q90"]["value"] == pytest.approx(7.9)
    assert audit.linear_quantile([10], 0.9) == 10


def test_failure_retention_and_no_missing_row_drop():
    rows = invented_rows(n_per_group=4)
    rows[0]["urate"] = "NaN"
    results = audit.estimate_table(rows)
    assert len(results) == 24
    assert results["global.bmi"]["value"] is None
    assert results["global.bmi"]["n"] == 16
    assert results["global.bmi"]["complete_n"] == 15
    assert results["group.White.male.mean"]["value"] is None
    assert results["group.Black.female.mean"]["status"] == "ok"
    singleton = audit.estimate_table(invented_rows(n_per_group=1))
    assert singleton["group.White.male.mean"]["status"] == "ok"
    assert singleton["group.White.male.sd"]["value"] is None
    assert singleton["global.bmi"]["value"] is None
    empty = audit.estimate_table([])
    assert len(empty) == 24 and all(item["value"] is None for item in empty.values())


def test_rank_failure_not_pseudoinverse_coefficient():
    rows = invented_rows()
    for row in rows:
        row["bmi"] = "28"
    result = audit.estimate_table(rows)
    assert result["global.bmi"]["status"] == "failure"
    assert result["global.bmi"]["matrix_rank"] < 5


def test_joint_psu_deletion_and_full_known_estimates():
    rows = invented_rows()
    result = audit.reference_psu_sensitivity(rows)
    assert len(result["deletions"]) == 6
    for record in result["deletions"]:
        assert record["omitted_n"] + record["remaining_n"] == 200
    bmi = result["ranges"]["global.bmi"]
    assert bmi["minimum"] == pytest.approx(0.75, abs=1e-12)
    assert bmi["maximum"] == pytest.approx(0.75, abs=1e-12)
    assert bmi["all_deletions_sign_stable_with_full"] is True
    assert bmi["failed_deletions"] == 0


def test_deletion_rank_failures_keep_sign_stability_unknown():
    rows = invented_rows()
    for row in rows:
        row["SDMVSTRA"] = "one"
        row["SDMVPSU"] = row["sex"]
    result = audit.reference_psu_sensitivity(rows)
    assert len(result["deletions"]) == 2
    for summary in result["ranges"].values():
        assert summary["rank_failed_deletions"] == 2
        assert summary["minimum"] is None
        assert summary["all_deletions_sign_stable_with_full"] is None


def test_identity_order_covariates_and_actual_changed_count():
    rows = invented_rows()
    first = candidate(rows)
    last = copy.deepcopy(first)
    result = audit.validate_identity_and_covariates(observed(rows), rows, first, last)
    assert result["changed_urate_rows"] == 0
    last[4]["urate"] = str(float(last[4]["urate"]) + 1)
    result = audit.validate_identity_and_covariates(observed(rows), rows, first, last)
    assert result["changed_urate_rows"] == 1
    last[4]["bmi"] = str(float(last[4]["bmi"]) + 1e-12)
    with pytest.raises(ValueError, match="numeric covariate changed"):
        audit.validate_identity_and_covariates(observed(rows), rows, first, last)
    with pytest.raises(ValueError, match="identity or row order"):
        audit.validate_identity_and_covariates(observed(rows), rows, list(reversed(first)), first)


def test_identical_candidates_have_one_unique_value_table():
    rows = invented_rows()
    report = audit.audit_rows(observed(rows), rows, candidate(rows), candidate(rows))
    assert report["unique_candidate_value_tables"] == 1
    assert len(report["comparisons"]) == 24
    assert report["preservation"]["changed_urate_rows"] == 0
    assert audit.compare_canonical_released_output(report, copy.deepcopy(report))["differences"] == []
    mapped = copy.deepcopy(report)
    mapped["estimates"]["initial"]["global.bmi"]["value"] += 0.01
    differences = audit.compare_canonical_released_output(report, mapped)["differences"]
    assert len(differences) == 1
    assert differences[0]["kind"] == "numeric_difference"


def test_permutation_invariance_and_unused_private_fields():
    rows = invented_rows()
    reference_result = audit.estimate_table(rows)
    for row in rows:
        row["WTPH2YR"] = "invented unused weight"
        row["SEQN"] = "invented unused identifier"
    assert audit.estimate_table(list(reversed(rows))) == reference_result


def test_cli_refuses_before_any_input_read(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("No input must be opened.")
    monkeypatch.setattr(audit.Path, "open", forbidden)
    monkeypatch.setattr(audit.Path, "read_text", forbidden)
    with pytest.raises(SystemExit):
        audit.main(["--release-manifest", "NONEXISTENT.json", "--output-dir", "NONEXISTENT"])


def test_quota_cannot_be_relaxed_in_default_benchmark():
    rows = invented_rows(n_per_group=5)
    with pytest.raises(ValueError, match="exactly 50"):
        audit.audit_rows(observed(rows), rows, candidate(rows), candidate(rows))


def test_no_inferential_fields_in_aggregate_report():
    rows = invented_rows()
    report = audit.audit_rows(observed(rows), rows, candidate(rows), candidate(rows))
    forbidden = {"pvalue", "p_value", "pvalues", "confidence_interval", "quality_score", "acceptance_threshold"}
    def inspect(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
    inspect(report)
