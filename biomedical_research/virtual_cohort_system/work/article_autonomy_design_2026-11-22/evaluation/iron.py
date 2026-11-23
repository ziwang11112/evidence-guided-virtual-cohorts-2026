"""Evaluator-only aggregate audit of the Zhu iron development case.

Input columns are already normalized by a separately checked unit mapping.
Only aggregate summaries are retained. Source references are transcribed from
the article. This module imports no generation or earlier evaluation code.
"""

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


# Table IV, published p. 150. Each tuple corresponds to a folate/B12 row:
# depleted ferritin, number with anemia, number without anemia.
TABLE_IV = (
    (False, 45, 687), (False, 17, 166), (True, 96, 187), (True, 26, 48),
    (False, 22, 166), (False, 1, 63), (True, 43, 68), (True, 8, 28),
)
CELLS = [
    sum(row[col] for row in TABLE_IV if row[0] == depleted)
    for col in (1, 2) for depleted in (True, False)
]
TOTAL = sum(CELLS)
CRUDE_OR = CELLS[0] * CELLS[3] / (CELLS[1] * CELLS[2])
ADJUSTED_OR = 6.448
CELL_ORDER = ["anemic_depleted", "anemic_replete", "nonanemic_depleted", "nonanemic_replete"]
MEASUREMENTS = ("hb_g_l", "ferritin_ug_l")


def check_source_claims(claims):
    """Audit analyst-transcribed explicit source claims only, never auto-infer prose."""
    checks = {}
    if "source_crude_or" in claims:
        claim = claims["source_crude_or"]
        value, digits = claim["value"], claim["decimal_places"]
        if type(digits) is not int or not 0 <= digits <= 12 or not math.isfinite(value):
            raise ValueError("Invalid source_crude_or value or decimal_places")
        checks["source_crude_or_matches_table_iv_at_stated_precision"] = (
            abs(float(value) - CRUDE_OR) <= 0.5 * 10 ** -digits + 1e-12
        )
    for key, factors, expected in [
        ("anemia_cutoff", {"g/l": 1, "g/dl": 10}, 120),
        ("depletion_cutoff", {"ug/l": 1, "ng/ml": 1, "mg/l": 1000, "ug/ml": 1000}, 15),
    ]:
        if key in claims:
            claim = claims[key]
            unit = claim["unit"].strip().lower().replace("μ", "u").replace("µ", "u").replace(" ", "")
            factor = factors.get(unit)
            checks[key + "_equivalent"] = bool(
                factor is not None and claim["comparison"] == "<"
                and math.isclose(claim["value"] * factor, expected, abs_tol=1e-9)
            )
    if "source_spearman_assertion" in claims:
        status = claims["source_spearman_assertion"]
        if status not in ("not_identified", "reported", "determined_by_summaries"):
            raise ValueError("Unknown source_spearman_assertion")
        checks["continuous_rank_correlation_support"] = status == "not_identified"
    return checks


def comparison(generated, source):
    return {"generated": generated, "source": source,
            "difference": None if generated is None else generated - source}


def gm(x):
    return float(np.exp(np.log(x).mean())) if len(x) else None


def evaluate(frame, claims=None):
    if not all(column in frame for column in MEASUREMENTS):
        raise ValueError("Both canonical columns required: hb_g_l and ferritin_ug_l")
    values = frame.loc[:, list(MEASUREMENTS)].apply(pd.to_numeric, errors="coerce")
    finite = np.isfinite(values.to_numpy())
    positive = values.to_numpy() > 0
    invalid = ~(finite & positive)
    report = {
        "source_doi": "10.1024/0300-9831/a000014", "n_generated": len(frame),
        "n_source": TOTAL, "cell_order": CELL_ORDER,
        "source_threshold_cells": CELLS, "source_crude_or": CRUDE_OR,
        "source_adjusted_or_table_v": ADJUSTED_OR,
        "source_continuous_spearman": None,
        "invalid_or_nonpositive_by_column": dict(zip(MEASUREMENTS, invalid.sum(axis=0).tolist())),
        "source_claim_checks": None if claims is None else check_source_claims(claims),
    }
    if len(frame) == 0 or invalid.any():
        report["status"] = "invalid table; no complete-case substitution"
        return report
    hb, fe = (values[name].to_numpy() for name in MEASUREMENTS)
    n = len(hb)
    anemic = hb < 120
    depleted = fe < 15
    cells = [
        int(np.count_nonzero(a & d))
        for a in (anemic, ~anemic) for d in (depleted, ~depleted)
    ]
    denom = cells[1] * cells[2]
    crude = cells[0] * cells[3] / denom if denom else None
    or_status = "finite" if denom else ("positive_infinity" if cells[0] * cells[3] else "undefined")
    ranks = values.rank(method="average")
    rho = float(ranks.iloc[:, 0].corr(ranks.iloc[:, 1])) if ranks.nunique().min() > 1 else None
    differences = [(c / n - s / TOTAL) * 100 for c, s in zip(cells, CELLS)]
    report.update({
        "status": "computed", "generated_threshold_cells": cells,
        "cell_proportion_difference_pp": differences,
        "cell_total_variation": sum(map(abs, differences)) / 200,
        "crude_or": comparison(crude, CRUDE_OR), "crude_or_status": or_status,
        "continuous_spearman_on_virtual_rows": rho,
        "table_i_hb_geometric_mean_g_l": comparison(gm(hb), 129.9),
        "table_i_ferritin_geometric_mean_ug_l": comparison(gm(fe), 17.4),
        "hb_tied_beyond_first": n - len(np.unique(hb)),
        "ferritin_tied_beyond_first": n - len(np.unique(fe)),
        "table_iii": {},
    })
    # Cell proportions accommodate synthetic sample sizes different from 1671.
    # Published geometric means and depletion percentages are rounded summaries.
    for band, keep, source_n, source_gm, source_pct in [
        ("hb_below_100", hb < 100, 53, 1.3, 94.3),
        ("hb_100_to_below_120", (hb >= 100) & anemic, 205, 5.9, 60.0),
        ("hb_at_least_120", ~anemic, 1413, 22.3, 23.4),
    ]:
        count = int(keep.sum())
        report["table_iii"][band] = {
            "n_generated": count,
            "percentage_in_band": comparison(100 * count / n, 100 * source_n / TOTAL),
            "ferritin_geometric_mean_ug_l": comparison(gm(fe[keep]), source_gm),
            "depleted_percentage": comparison(100 * float(depleted[keep].mean()) if count else None,
                                              source_pct),
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path)
    parser.add_argument("--claims", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    claims = json.loads(args.claims.read_text(encoding="utf-8")) if args.claims else None
    data = evaluate(pd.read_csv(args.table), claims)
    out = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out, end="")


if __name__ == "__main__":
    main()
