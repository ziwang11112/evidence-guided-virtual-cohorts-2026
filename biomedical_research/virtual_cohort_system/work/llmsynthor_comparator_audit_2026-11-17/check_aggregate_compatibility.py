"""Construct mathematical counterexamples from the same published summaries."""

import hashlib
import json
import math
from fractions import Fraction
from itertools import product
from pathlib import Path
from statistics import NormalDist

import numpy as np


ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
IRON_PACKET = WORK / "iron_evidence_content_control_2026-11-16/inputs/JOINT.json"
BP_PACKET = WORK / "pns_evidence_content_control_2026-11-16/inputs/JOINT.json"


def iron_example(evidence):
    joint = evidence["joint_statistics"][0]
    counts = joint["cells"]
    total = joint["n"]
    a, b, c, d = [
        Fraction(counts[key], total)
        for key in ("both_low", "only_hb_low", "only_ferritin_low", "neither_low")
    ]
    assert a + b + c + d == 1
    hb_low, ferritin_low = a + b, a + c
    summaries = {row["id"]: row for row in evidence["marginal_statistics"]}
    assert hb_low == Fraction(summaries["HB_LOW"]["count"], total)
    assert ferritin_low == Fraction(summaries["FERRITIN_LOW"]["count"], total)

    # Define continuous ranks U and V. The first coupling chooses a threshold
    # cell, then draws independently from its two rank intervals.
    hb_bounds = [(0, hb_low), (hb_low, 1)]
    ferritin_bounds = [(0, ferritin_low), (ferritin_low, 1)]
    cell_weights = ((a, b), (c, d))
    expected_product = sum(
        cell_weights[i][j] * sum(hb_bounds[i]) * sum(ferritin_bounds[j]) / 4
        for i, j in product(range(2), repeat=2)
    )
    independent_ranks = 12 * expected_product - 3
    assert independent_ranks == 3 * (a - hb_low * ferritin_low)

    # The second coupling rearranges intervals of U by translation. Each
    # pair (start on U, start on V, mass) occupies the same threshold cell.
    blocks = [(0, 0, a), (a, ferritin_low, b), (hb_low, a, c),
              (hb_low + c, ferritin_low + b, d)]
    for axis in (0, 1):
        boundary = Fraction(0)
        for block in sorted(blocks, key=lambda entry: entry[axis]):
            assert block[axis] == boundary
            boundary += block[2]
        assert boundary == 1
    for (i, j), (u, v, mass) in zip(product(range(2), repeat=2), blocks):
        assert hb_bounds[i][0] <= u <= u + mass <= hb_bounds[i][1]
        assert ferritin_bounds[j][0] <= v <= v + mass <= ferritin_bounds[j][1]
        assert mass == cell_weights[i][j]
    translated_ranks = 1 - 6 * sum(mass * (u - v) ** 2 for u, v, mass in blocks)
    translated_product = sum(
        mass * u * v + (u + v) * mass ** 2 / 2 + mass ** 3 / 3
        for u, v, mass in blocks
    )
    assert translated_ranks == 12 * translated_product - 3
    assert independent_ranks != translated_ranks

    # Keep both full continuous marginals identical across the two couplings.
    # Hb can be uniform on [12 - 6*P(low Hb), 18 - 6*P(low Hb)].
    # A lognormal ferritin marginal can also match the admitted geometric mean.
    geometric_mean = summaries["FERRITIN_GM"]["value"]
    ferritin_mu = math.log(geometric_mean)
    ferritin_sd = (
        (math.log(joint["cutoffs"]["ferritin_ug_l"]) - ferritin_mu)
        / NormalDist().inv_cdf(float(ferritin_low))
    )
    assert ferritin_sd > 0
    assert math.isclose(
        NormalDist().cdf((math.log(joint["cutoffs"]["ferritin_ug_l"]) - ferritin_mu) / ferritin_sd),
        float(ferritin_low), abs_tol=1e-14,
    )
    return {
        "source_count": total,
        "cells": counts,
        "common_crude_or": float(a * d / (b * c)),
        "common_joint_low_fraction": float(a),
        "common_hb_low_fraction": float(hb_low),
        "common_ferritin_low_fraction": float(ferritin_low),
        "common_ferritin_geometric_mean_ug_l": geometric_mean,
        "within_cell_independence_spearman": float(independent_ranks),
        "interval_rearrangement_spearman": float(translated_ranks),
        "scope": "Two admissible mathematical examples, with identical continuous marginals. Values are neither estimated patient correlations nor claimed sharp bounds.",
    }


def bp_example(evidence):
    fields = ["sbp", "dbp", "bmi", "age"]
    correlation = np.eye(len(fields))
    for row in evidence["relationships"]:
        i, j = fields.index(row["x"]), fields.index(row["y"])
        correlation[i, j] = correlation[j, i] = row["value"]
    marginals = {row["variable"]: row for row in evidence["marginal_statistics"]}
    age_mean = evidence["population"]["mean_age_years"]
    mean = np.array([marginals[k]["mean"] for k in fields[:3]] + [age_mean])
    # The source does not give the age SD. Both examples use the same
    # illustrative value, which keeps the discrete support above age 40.
    sd = np.array([marginals[k]["sample_sd"] for k in fields[:3]] + [5.0])
    transform = np.diag(sd) @ np.linalg.cholesky(correlation)
    expected_covariance = np.diag(sd) @ correlation @ np.diag(sd)
    threshold = 140.0  # Example cutoff only, in mmHg.
    examples = []
    for high_mass in (0.5, 0.8):
        high = math.sqrt((1 - high_mass) / high_mass)
        low = -1 / high
        latent = np.array(list(product([low, high], [-1, 1], [-1, 1], [-1, 1])))
        support = mean + latent @ transform.T
        weights = np.repeat([(1 - high_mass) / 8, high_mass / 8], 8)
        computed_mean = weights @ support
        centered = support - computed_mean
        covariance = (centered * weights[:, None]).T @ centered
        np.testing.assert_allclose(computed_mean, mean, rtol=0, atol=1e-12)
        np.testing.assert_allclose(covariance, expected_covariance, rtol=0, atol=1e-12)
        assert np.all(support[:, 0] > support[:, 1]) and np.all(support[:, 1:] > 0)
        assert np.min(support[:, 3]) >= 40
        examples.append({
            "sbp_support_mmhg": sorted(set(support[:, 0].tolist())),
            "mass_at_or_above_140": float(weights[support[:, 0] >= threshold].sum()),
        })
    assert examples[0]["mass_at_or_above_140"] != examples[1]["mass_at_or_above_140"]
    return {
        "fields": fields,
        "common_means": mean.tolist(),
        "common_sd": sd.tolist(),
        "common_pearson_matrix": correlation.tolist(),
        "examples": examples,
        "scope": "Moment counterexamples, not biomedical models, patient estimates, or reconstructions of adjusted Table 5/6 regressions. The 5-year age SD is an equal illustrative choice across examples.",
    }


def main():
    iron = json.loads(IRON_PACKET.read_text(encoding="utf-8"))["approved_source_evidence"]
    bp = json.loads(BP_PACKET.read_text(encoding="utf-8"))["additional_study_evidence"]
    result = {
        "source_packet_sha256": {
            path.relative_to(WORK).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (IRON_PACKET, BP_PACKET)
        },
        "iron": iron_example(iron),
        "blood_pressure": bp_example(bp),
        "model_calls": 0,
        "cohort_tables_generated": 0,
        "target_rows_or_references_read": False,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
