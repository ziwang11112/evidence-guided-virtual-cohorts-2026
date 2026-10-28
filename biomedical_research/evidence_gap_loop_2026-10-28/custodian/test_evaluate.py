"""Independent algebra and contract checks on synthetic fixtures only."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import evaluate as ev
from build_packet import zero_guard

def expect_rejection(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("Invalid input was accepted")

def main():
    rng = np.random.default_rng(392081)
    rows = []
    for h in range(8):
        for j in range(3):
            for k in range(7):
                rows.append({"row_id": f"toy_{h}_{j}_{k}", "stratum": str(h), "psu": str(j), "weight": str(1+(h+k)%5)})
    spine = pd.DataFrame(rows)
    # Entire third PSU in each stratum excluded from target domain.
    domain = spine[spine.psu != "2"].reset_index(drop=True)
    n = len(domain)
    observed = pd.DataFrame({"row_id": domain.row_id, "bmi": rng.uniform(19, 45, n).astype(str),
                             "age": rng.integers(20, 80, n).astype(str), "sex": rng.integers(1, 3, n).astype(str)})
    ev.valid_observed(observed)
    X = ev.matrices(observed)["B"]
    y = 70 + X@np.array([1.3, -.27, .11, -.18])+rng.normal(0, 2, n)
    w = ev.number(domain, "weight")
    beta, covariance, diagnostic = ev.taylor_fit(X, y, domain, spine)
    expected = np.linalg.lstsq(X*np.sqrt(w)[:, None], y*np.sqrt(w), rcond=None)[0]
    np.testing.assert_allclose(beta, expected, atol=1e-11)
    # Independently build PSU score sums including the entirely empty PSU.
    residual = y-X@expected
    bread_inverse = np.linalg.inv(X.T@np.diag(w)@X)
    meat = np.zeros((4, 4))
    for h in range(8):
        cluster_scores = []
        for j in range(3):
            m = (domain.stratum == str(h)) & (domain.psu == str(j))
            cluster_scores.append(np.sum(X[m]*((w*residual)[m, None]), axis=0))
        scores = np.vstack(cluster_scores)
        centered = scores-scores.mean(axis=0)
        meat += 1.5*centered.T@centered
    np.testing.assert_allclose(covariance, bread_inverse@meat@bread_inverse, atol=1e-11)
    assert diagnostic["full_psus"] == 24 and diagnostic["domain_psus"] == 16
    assert diagnostic["design_df"] == 8 and diagnostic["residual_df"] == 5
    assert np.linalg.eigvalsh(covariance).min() > -1e-10
    generated = observed.copy()
    generated["hdl"] = y.astype(str)
    np.testing.assert_array_equal(ev.match_generated(observed, generated.iloc[::-1]), y)
    changed = generated.copy()
    changed.loc[0, "age"] = str(float(changed.loc[0, "age"])+1)
    expect_rejection(lambda: ev.match_generated(observed, changed))
    extra = generated.assign(hidden_source="bad")
    expect_rejection(lambda: ev.match_generated(observed, extra))
    expect_rejection(lambda: ev.match_generated(observed, generated.iloc[:-1]))
    nonpositive = generated.copy()
    nonpositive.loc[0, "hdl"] = "0"
    expect_rejection(lambda: ev.match_generated(observed, nonpositive))
    expect_rejection(lambda: ev.validate_release({}))
    spec = json.loads((Path(__file__).parent/"analysis_spec.json").read_text())
    result = ev.analyze(observed, y, domain, spine, spec)
    assert len(result["endpoints"]) == 8
    # Exactly recover a pure quadratic curvature contrast at BMI 35 versus 25.
    XC = ev.matrices(observed)["C"]
    qy = XC@np.array([60, -.4, .3, .2, .5])
    qb, qc, qd = ev.taylor_fit(XC, qy, domain, spine)
    assert abs(ev.contrast(qb, qc, [0, 0, 4, 0, 0], qd["residual_df"])["estimate"]-1.2) < 1e-10
    synthetic = np.frombuffer(bytes.fromhex("00000000000000004110000000000000c1100000000000004120000000000000"), dtype="S8")
    np.testing.assert_array_equal(zero_guard(synthetic), [0, 1, -1, 2])
    report = {"passed": True, "data_used": "Synthetic fixtures only; no project outcome records accessed",
              "checks": ["WLS agrees with independent weighted least squares", "Taylor covariance agrees with manual PSU score sums including empty domain PSU",
                         "Domain-based regression degrees of freedom", "Positive semidefinite covariance", "Generated reordering preserves alignment",
                         "Changed covariates, extra columns, missing rows and nonpositive targets rejected", "Unreleased evaluation rejected",
                         "All eight endpoints returned", "Quadratic slope contrast exact recovery", "IBM SAS zero encoding guard"]}
    ev.save(Path(__file__).parent/"synthetic_test_report.json", report)
    print(json.dumps(report))

if __name__ == "__main__":
    main()
