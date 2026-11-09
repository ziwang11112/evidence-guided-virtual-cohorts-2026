"""Recalculate published aggregate relationships; no patient or generated rows.

This is an audit calculation, not a generator or source-to-target conversion.
"""
from pathlib import Path
import json
import itertools
import math
import numpy as np


def partial(a, b, c):
    return (a - b * c) / math.sqrt((1 - b*b) * (1 - c*c))


def main():
    # Liu2023 supplement Figure S1: TC-HDL, TC-BMI, HDL-BMI after
    # age/sex/batch adjustment. Same-row/common-design compatibility required.
    a, b, c = 0.16, 0.05, -0.35
    matrix = np.array([[1.0, a, b], [a, 1.0, c], [b, c, 1.0]])
    residual = matrix[:2, :2] - np.outer(matrix[:2, 2], matrix[2, :2])
    schur = residual[0, 1] / np.sqrt(residual[0, 0] * residual[1, 1])
    recursive = partial(a, b, c)
    assert np.linalg.eigvalsh(matrix).min() > 0
    assert abs(schur-recursive) < 1e-14

    # Sensitivity to NEAREST 0.01 rounding, not a confidence interval.
    box = [(x-0.005, x+0.005) for x in (a,b,c)]
    corners = list(itertools.product(*box))
    # f increases in a, increases in b when a*b-c>0,
    # and decreases in c when a*c-b<0 over this entire sign-definite box.
    assert box[0][0] > 0 and box[1][0] > 0 and box[2][1] < 0
    corner_values = [partial(*v) for v in corners]
    lower = partial(box[0][0], box[1][0], box[2][1])
    upper = partial(box[0][1], box[1][1], box[2][0])
    assert lower == min(corner_values) and upper == max(corner_values)
    corner_min_eigen = min(float(np.linalg.eigvalsh(
        [[1,x,y],[x,1,z],[y,z,1]]).min()) for x,y,z in corners)
    assert corner_min_eigen > 0
    result = {
        "source_doi": "10.1111/acel.13934",
        "locator": "Supplementary Figure S1",
        "input_correlations": {"TC_HDL": a, "TC_BMI": b, "HDL_BMI": c},
        "input_adjustment": ["age", "sex", "batch"],
        "derived_adjustment": ["age", "sex", "batch", "BMI"],
        "recursive_partial": recursive,
        "schur_complement_partial": float(schur),
        "absolute_implementation_difference": float(abs(schur-recursive)),
        "matrix_min_eigenvalue": float(np.linalg.eigvalsh(matrix).min()),
        "rounding_assumption": "each published value rounded independently to nearest 0.01",
        "rounding_only_bounds": [lower, upper],
        "rounding_box_min_corner_eigenvalue": corner_min_eigen,
        "sampling_confidence_interval": None,
        "unresolved": ["exact common analytic n", "batch encoding and common residual design", "Methods describes age/sex; Results and figure caption additionally specify batch", "source sampling uncertainty", "population and assay transport"],
        "interpretation": "Source-specific sensitivity calculation under stated compatibility assumptions; not a target-population constraint or clinical validation",
        "patient_rows_read": 0,
        "generated_rows": 0
    }
    Path(__file__).with_name("PARTIAL_RELATION_CHECK.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
