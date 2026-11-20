"""Recalculate the comparison from public aggregates, without reading participant records."""
import math
from pathlib import Path
from statistics import median

from science import HERE, PARENTS, SEEDS, baseline_fit, baseline_indices, endpoints, marginals, pair, read


def close(x, y):
    return math.isclose(x, y, rel_tol=1e-10, abs_tol=1e-10)


def main():
    results = read(HERE / "RESULTS.json")
    closure = read(HERE / "DRAW_CLOSURE.json")
    reference = results["reference"]
    a, b, c, d = reference["cells"]
    assert sum((a, b, c, d)) == reference["n"]
    if b and c:
        assert close(a * d / (b * c), reference["odds_ratio"])
    bands, rho = baseline_fit()
    assert close(rho, closure["rho_statistical"])
    for seed, record in zip(SEEDS, closure["models"]["statistical"]["runs"], strict=True):
        groups = marginals(bands, seed)
        score = endpoints(pair(groups, baseline_indices(groups, rho, seed)))
        assert score["cells"] == record["estimates"]["cells"]
        for name in ("rank", "odds_ratio", "middle_ratio"):
            assert close(score[name], record["estimates"][name])
    rows = results["by_law"]
    ok = [name for name in PARENTS if rows[name]["usable"]]
    for name in ["statistical", *ok]:
        row = rows[name]
        assert close(row["absolute_rank_error"], abs(row["rank"] - reference["rank"]))
        assert close(row["odds_ratio"], rows["statistical"]["odds_ratio"])
    gain = rows["statistical"]["absolute_rank_error"] - median(rows[name]["absolute_rank_error"] for name in ok)
    assert close(gain, results["gain"])
    q = results["paired_bootstrap"]["gain"]
    guard_evaluable = min(reference["cells"]) >= 10 and reference["odds_ratio"] is not None and rows["statistical"]["odds_ratio"] is not None
    expected = {
        "four_authors": len(ok) >= 4,
        "point_gain_at_least_0.02": gain >= .02,
        "lower95_above_zero": q["percentile95"][0] > 0,
        "all_bootstrap_gain_finite": q["finite"] == 2000,
        "threshold_guard": bool(guard_evaluable and max(rows["statistical"]["odds_ratio"] / reference["odds_ratio"], reference["odds_ratio"] / rows["statistical"]["odds_ratio"]) <= 1.5),
    }
    assert results["decision_checks"] == expected
    assert results["prespecified_advantage_on_this_cohort"] == all(expected.values())
    print(f"Reproduced {len(SEEDS)} statistical draws, {len(ok)} author errors, D={gain:.6f} and all five decision checks.")


if __name__ == "__main__":
    main()
