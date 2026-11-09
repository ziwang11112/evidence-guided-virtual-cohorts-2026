"""Deterministic exact moment algebra only; no data generation or file discovery."""
from fractions import Fraction as Q
from pathlib import Path
import json

OUTPUT = Path(__file__).resolve().parent / "calculations.json"

def encoded(value):
    return {"exact": str(value), "decimal": float(value)}

def assess(x, y):
    r = Q(3, 10)
    determinant = 1 - r*r - x*x - y*y + 2*r*x*y
    va = 1 - x*x
    vb = 1 - y*y
    residual_cov = r - x*y
    # All declared scenarios have equal residual variances, so no rounding is needed.
    assert va == vb and va > 0
    residual_r = residual_cov / va
    minors = [Q(1), 1-r*r, determinant]
    assert all(m > 0 for m in minors)
    assert -1 <= residual_r <= 1
    return {
        "mean": [0, 0, 0],
        "variance": [1, 1, 1],
        "r_AB": encoded(r), "r_AC": encoded(x), "r_BC": encoded(y),
        "leading_principal_minors": [encoded(m) for m in minors],
        "positive_definite": True,
        "residual_variance_A": encoded(va),
        "residual_variance_B": encoded(vb),
        "residual_covariance": encoded(residual_cov),
        "U2": encoded(residual_r),
    }

results = {
    "method": "Exact Fraction arithmetic and Sylvester's criterion; no random draws",
    "candidate_independence": assess(Q(0), Q(0)),
    "illustrative_P1_P2_alternative": assess(Q(7, 10), Q(7, 10)),
    "P3_source_constrained_revision": assess(Q(3, 5), Q(3, 5)),
    "original_candidate_U2_minus_P3_source_U2": encoded(Q(3, 10) - Q(-3, 32)),
}
OUTPUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
