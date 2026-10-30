"""Invented data only. No prepared participant, reference or candidate file reads."""
import copy
import importlib.util
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from analysis import (DesignError, PRIMARY, compare_points, domain_df, evaluate_generated,
                      evaluate_reference, mean_taylor, points, total_covariance, wls_taylor)
from gates import GateError, validate_schedule


def design(ids, strata, psus, weights):
    return pd.DataFrame({"stratum": strata, "psu": psus, "weight": weights}, index=ids)


def test_manual_full_design_mean_domain_keeps_empty_psus():
    d = design(["a", "outside_a", "b", "outside_b"], [1, 1, 2, 2], [1, 2, 1, 2], [1., 2., 3., 4.])
    y = pd.Series([2., 4.], index=["a", "b"])
    w = d.loc[y.index, "weight"]
    fit = mean_taylor(y, w, d)
    # Weighted mean 3.5, influence totals [-3/8,0] and [3/8,0].
    # Each two-PSU stratum contributes (3/8)^2, so V=18/64.
    assert fit["estimate"] == 3.5
    assert fit["variance"] == pytest.approx(18/64)
    assert fit["ci_df"] == 0  # two represented PSUs minus two represented strata
    with pytest.raises(DesignError, match="Singleton"):
        mean_taylor(y, w, d.loc[y.index])


def test_manual_multivariate_wls_covariance_with_third_zero_psu():
    d = design(list("abcde"), [1, 1, 2, 2, 2], [1, 2, 1, 2, 3], [1.]*5)
    X = pd.DataFrame({"intercept": 1., "x": [0., 1., 2., 3.]}, index=list("abcd"))
    y = pd.Series([1., 2., 2., 4.], index=X.index)
    fit = wls_taylor(X, y, d.loc[X.index, "weight"], d)
    assert fit["beta"] == pytest.approx([.9, .9])
    # B^-1=[[.7,-.3],[-.3,.2]], residuals [.1,.2,-.7,.4].
    # Influence rows [.07,-.03],[.08,-.02],[-.07,-.07],[-.08,.12].
    # Stratum 1 diff outer product + 3/2 centered outer products in stratum 2,
    # where the third PSU has influence [0,0]. These constants are hand-derived.
    assert fit["covariance"] == pytest.approx(np.array([[.0058, -.0032], [-.0032, .0278]]), abs=1e-13)
    # Dropping e falsely changes the PSU universe, although e has no domain values.
    incomplete = wls_taylor(X, y, d.loc[X.index, "weight"], d.loc[X.index])
    assert incomplete["covariance"] == pytest.approx(np.array([[.0002, -.0018], [-.0018, .0362]]), abs=1e-13)
    assert not np.allclose(fit["covariance"], incomplete["covariance"])


def test_psu_nesting_vector_covariance_and_permutation():
    d = design(list("abcd"), [1, 1, 2, 2], [1, 2, 1, 2], [1.]*4)
    u = pd.DataFrame([[1., 2.], [3., 4.], [5., 8.]], index=list("abc"))
    # h1 difference [-2,-2], h2 difference [5,8].
    expected = np.array([[29., 44.], [44., 68.]])
    assert total_covariance(u, d) == pytest.approx(expected)
    assert total_covariance(u.iloc[::-1], d.iloc[::-1]) == pytest.approx(expected)


def test_strict_alignment_unknown_ids_and_full_design_singletons():
    d = design(list("abcd"), [1]*4, [1, 1, 2, 2], [1.]*4)
    X = pd.DataFrame({"intercept": 1., "x": range(4)}, index=d.index)
    y = pd.Series([1., 2., 2., 4.], index=d.index)
    with pytest.raises(DesignError, match="index"):
        wls_taylor(X, y.iloc[::-1], d.weight, d)
    with pytest.raises(DesignError, match="weights differ"):
        wls_taylor(X, y, d.weight*2, d)
    with pytest.raises(DesignError, match="outside"):
        total_covariance(pd.DataFrame({"u": [1.]}, index=["unknown"]), d)
    with pytest.raises(DesignError, match="Singleton"):
        total_covariance(pd.DataFrame({"u": [1.]}, index=["a"]), d.assign(psu=1))


def invented_case():
    rng = np.random.default_rng(74012)
    n = 400
    ids = pd.Index([f"invented_{i}" for i in range(n)])
    x = pd.DataFrame({"age": rng.integers(20, 80, n), "sex": rng.integers(1, 3, n),
                      "bmi": rng.uniform(18, 40, n), "glucose_mg_dl": rng.uniform(75, 140, n)}, index=ids)
    d = design(pd.Index(range(n+40)), np.tile(np.arange(20), 22), np.tile(np.repeat([1, 2], 20), 11), rng.uniform(.5, 3, n+40))
    mapping = pd.Series(np.arange(n), index=ids)
    w = pd.Series(d.loc[mapping, "weight"].to_numpy(), index=ids)
    A, B, F, G = (x.age-50)/10, (x.bmi-25)/5, (x.sex == 2).astype(float), np.log(x.glucose_mg_dl/100)
    y = np.exp(2+.1*A+.2*B+.1*F+.3*G-.04*B*B+.03*F*B+rng.normal(0, .3, n))
    return x, y, w, d, mapping


def test_reference_points_unchanged_models_contrasts_and_weight_scale():
    x, y, w, d, ids = invented_case()
    r = evaluate_reference(x, y, w, "nhanes_insulin", d, ids)
    p = points.evaluate_points(x, y, w, "nhanes_insulin")
    assert len(r["weighted"]) == 25
    for key, original in p.items():
        assert r["weighted"][key]["estimate"] == original["estimate"]
    q = evaluate_reference(x, y, 173*w, "nhanes_insulin", d.assign(weight=d.weight*173), ids)
    for key in PRIMARY:
        assert q["weighted"][key]["standard_error"] == pytest.approx(r["weighted"][key]["standard_error"])
        assert r["weighted"][key]["ci_df"] == 20-(5 if "curvature" in key or "slope" in key else 4)
    curve = r["weighted"][PRIMARY[2]]
    assert curve["standard_error"]**2 == pytest.approx(4*r["model_covariances"]["bmi_curve"][-1][-1])
    assert r["design"]["full_design_rows"] == 440 and r["design"]["domain_rows"] == 400
    with pytest.raises(DesignError, match="aligned"):
        evaluate_reference(x, y, w, "nhanes_insulin", d, ids.iloc[::-1])


def test_pns_full_sensitivity_without_fabricated_intervals_and_no_mean_sign_credit():
    x, _, w, _, _ = invented_case()
    y = 5+.2*(x.age-50)/10+.3*(x.bmi-25)/5
    r = evaluate_reference(x, y, w, "pns_hba1c")
    fake = evaluate_generated(x, y+.5, w, "pns_hba1c")
    assert set(r["unweighted_sensitivity"]) == set(r["weighted"])
    assert all("ci_lower" not in value and "standard_error" not in value for value in r["weighted"].values())
    comparison = compare_points(r["weighted"], fake["weighted"])
    assert all("point_direction_agreement" in comparison[k] for k in PRIMARY)
    assert "point_direction_agreement" not in comparison["weighted_arithmetic_mean"]
    assert all(v["clinical_conclusion_agreement"] == "not_assessed" for v in comparison.values())


def test_sparse_cells_rank_failure_and_df_failure_remain_visible():
    x, y, w, d, ids = invented_case()
    x["age"] = 30
    r = evaluate_reference(x, y, w, "nhanes_insulin", d, ids)
    assert all(r["weighted"][key]["status"] == "nonestimable" for key in PRIMARY)
    assert r["weighted"]["cell_age60_79_sex1_bmige30_mean"]["status"] == "nonestimable"
    assert r["weighted"]["weighted_arithmetic_mean"]["status"] == "estimated"


def schedule(tmp_path):
    m = {"schema_version": "m10-campaign-freeze-1", "status": "frozen_before_target_analysis",
         "target_outcomes_inspected": False, "frozen_utc": "2026-10-29T00:00:00Z",
         "residual_seeds": [92101, 92102, 92103], "cases": {"nhanes_insulin": {}, "pns_hba1c": {}}, "constructions": []}
    for cid, case in [("ia", "nhanes_insulin"), ("ib", "nhanes_insulin"), ("ha", "pns_hba1c"), ("hb", "pns_hba1c")]:
        bundle = tmp_path/cid
        c = {"construction_id": cid, "case_id": case, "bundle_path": str(bundle),
             "initial_candidate": str(bundle/"candidates/initial"), "selected_candidate": str(bundle/"candidates/final"),
             "final_selection_path": str(bundle/"final_selection.json"), "outputs": []}
        for seed in m["residual_seeds"]:
            run = f"t{seed}"
            c["outputs"].append({"seed": seed, "run_id": run, "path": str(bundle/"executions"/run/"output/generated.csv"),
                                 "receipt_path": str(bundle/"executions"/run/"execution.json"), "sha256": "a"*64, "receipt_sha256": "b"*64})
        m["constructions"].append(c)
    return m


def test_gate_requires_all_four_twelve_unique_slots_all_seeds(tmp_path):
    m = schedule(tmp_path)
    assert len(validate_schedule(m)) == 4  # repeated t92101 across bundles is valid
    bad = copy.deepcopy(m)
    bad["constructions"].pop()
    with pytest.raises(GateError, match="four"):
        validate_schedule(bad)
    bad = copy.deepcopy(m)
    bad["constructions"][0]["outputs"][2]["seed"] = 92101
    with pytest.raises(GateError, match="three"):
        validate_schedule(bad)
    bad = copy.deepcopy(m)
    bad["constructions"][0]["outputs"][2] = bad["constructions"][0]["outputs"][1].copy()
    bad["constructions"][0]["outputs"][2]["seed"] = 92103
    with pytest.raises(GateError, match="Duplicate"):
        validate_schedule(bad)


def test_cli_gate_failure_occurs_before_reference_loader(tmp_path, monkeypatch):
    import evaluate
    def refused(*args, **kwargs):
        raise GateError("incomplete campaign")
    def forbidden(*args, **kwargs):
        raise AssertionError("Target loader reached before gate")
    monkeypatch.setattr(evaluate, "verify_manifest", refused)
    monkeypatch.setattr(evaluate, "load_case", forbidden)
    with pytest.raises(GateError, match="incomplete"):
        evaluate.main(["--manifest", str(tmp_path/"invented.json"), "--output", str(tmp_path/"out")])
    assert not (tmp_path/"out").exists()
