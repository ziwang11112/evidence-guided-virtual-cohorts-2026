"""Create the fixed analytical answer file, without any cohort sampling."""
from fractions import Fraction as F
import json
from math import sqrt
from pathlib import Path


def main():
    mu = [F(12), F(-7), F(40)]
    sd = [F(3), F(5), F(8)]
    correlation = [[F(1), F(45, 100), F(-25, 100)],
                   [F(45, 100), F(1), F(35, 100)],
                   [F(-25, 100), F(35, 100), F(1)]]
    covariance = [[sd[i] * sd[j] * correlation[i][j] for j in range(3)] for i in range(3)]
    a, b, c = covariance[0][0], covariance[0][1], covariance[1][1]
    d, e, f = covariance[0][2], covariance[1][2], covariance[2][2]
    determinant_pair = a * c - b * b
    beta1 = (c * d - b * e) / determinant_pair
    beta2 = (a * e - b * d) / determinant_pair
    residual_variance = f - d * beta1 - e * beta2
    determinant_full = determinant_pair * residual_variance
    assert a > 0 and determinant_pair > 0 and determinant_full > 0
    assert residual_variance > 0
    old_slope = b / a
    old_intercept = mu[1] - old_slope * mu[0]
    intercept = mu[2] - beta1 * mu[0] - beta2 * mu[1]
    rational_answers = {"A1_slope_x1": old_slope, "A1_intercept": old_intercept,
                        "A2_slope_x1": beta1, "A2_slope_x2": beta2,
                        "A2_intercept": intercept, "A3_residual_variance": residual_variance}
    truth = {
        "schema_version": 1, "fixture_id": "c5_artificial_dynamic_extension",
        "source_kind": "EXPLICITLY ARTIFICIAL exact population constraints, not patient data",
        "population_id": "C5-ARTIFICIAL-GAUSSIAN-POPULATION-1",
        "distribution": "joint multivariate normal; fully identified by the public final packet",
        "variables": ["x1", "x2", "x3"], "means": list(map(float, mu)),
        "standard_deviations": list(map(float, sd)),
        "correlation": [list(map(float, row)) for row in correlation],
        "covariance": [list(map(float, row)) for row in covariance],
        "analytical_answers": {**{key: float(value) for key, value in rational_answers.items()},
                               "A3_residual_sd": sqrt(float(residual_variance))},
        "exact_rational_answers": {key: str(value) for key, value in rational_answers.items()},
        "conditional": {"slopes": [float(beta1), float(beta2)], "intercept": float(intercept),
                        "residual_variance": float(residual_variance),
                        "residual_sd": sqrt(float(residual_variance)),
                        "distribution": "Gaussian with conditional mean linear in x1,x2 and independent residual"},
        "positive_definiteness_certificate": {
            "leading_principal_minor_1": str(a),
            "leading_principal_minor_2": str(determinant_pair),
            "leading_principal_minor_3": str(determinant_full),
            "all_strictly_positive": True},
        "analytical_derivations": {
            "covariance": "Sigma_ij = reported Pearson rho_ij * reported SD_i * reported SD_j",
            "A1": "slope=Sigma_12/Sigma_11; intercept=mu_2-slope*mu_1",
            "A2": "beta=inverse(Sigma_[1,2],[1,2]) * Sigma_[1,2],3; intercept=mu_3-beta^T mu_[1,2]",
            "A3": "variance=Sigma_33-Sigma_3,[1,2] inverse(Sigma_[1,2],[1,2]) Sigma_[1,2],3; SD=sqrt(variance)"},
        "interpretation": "Known invented mathematics; no hidden clinical outcomes, independent scientific evidence, or target-patient truth. No rows were generated to obtain these answers."
    }
    destination = Path(__file__).with_name("analytic_truth.json")
    destination.write_text(json.dumps(truth, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Analytical truth prepared; exact positive-definiteness and nonzero-residual checks passed. No rows generated.")


if __name__ == "__main__":
    main()
