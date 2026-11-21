"""Verify the published audit from aggregate results and sealed program files.
Run with Python 3.10 or later. No API, participant rows, or scientific packages are needed.
"""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def close(x, y):
    assert math.isclose(x, y, abs_tol=1e-8, rel_tol=1e-9), (x, y)


def main():
    freeze = read("FREEZE.json")
    authors = read("AUTHORS.json")["records"]
    results = read("SENSITIVITY.json")["authors"]
    audit = read("VERIFICATION.json")
    ranks = read("LIPID_HEATMAP.json")
    n = ranks["n"]
    assert ranks["seed"] == freeze["seeds"][0]
    assert set(authors) == set(results) == set(freeze["authors"])
    assert len(authors) == 4 and len(freeze["seeds"]) == 3
    assert freeze["source_only"] and not freeze["patient_references_used"]
    price = freeze["model"]
    costs = []
    gaps = []
    for key, rec in authors.items():
        assert rec["returned_model"] == price["model"] and rec["status"] == "received"
        for name, digest in rec["law"].items():
            text = (HERE / "laws" / key / name).read_text(encoding="utf-8").encode()
            assert hashlib.sha256(text).hexdigest() == digest, (key, name)
        usage = rec["usage"]
        ordinary_input = usage["input"] - usage["cached"] - usage["cache_write"]
        amount = (price["input_rate"] * ordinary_input + price["cache_write_rate"] * usage["cache_write"] +
                  price["cached_rate"] * usage["cached"] + price["output_rate"] * usage["output"]) / 1_000_000
        close(amount, rec["tariff_cost_usd"])
        costs.append(amount)
        result = results[key]
        scenarios = {}
        for scenario in ("a", "b"):
            draws = result["runs"][scenario]
            assert [row["seed"] for row in draws] == freeze["seeds"]
            assert len({row["permutation_hash"] for row in draws}) == 3
            scores = [row["score"] for row in draws]
            for score in scores:
                assert score["n"] == n and score["invalid_order"] == 0
                close(score["mean"], 128.7711)
                assert abs(score["mean_ratio"] - 3.66) <= .02
                close(score["percent"], 100 * score["tail_count"] / n)
            pooled_ratio = statistics.mean(score["mean_ratio"] for score in scores)
            assert 3.655 <= pooled_ratio < 3.665
            reported = result["scenarios"][scenario]
            assert reported["pass"]
            close(pooled_ratio, reported["mean_ratio"])
            scenarios[scenario] = [s["percent"] for s in scores]
            close(statistics.mean(scenarios[scenario]), reported["percent"])
            panel = ranks["panels"][key][scenario]
            grid = panel["tc_by_hdl"]
            assert ranks["bins"] == len(grid) and all(len(row) == ranks["bins"] for row in grid)
            assert all(sum(row) == n // ranks["bins"] for row in grid)
            assert all(sum(col) == n // ranks["bins"] for col in zip(*grid))
            assert scores[0]["tail_count"] == panel["tail_n"]
        deltas = [b - a for a, b in zip(scenarios["a"], scenarios["b"])]
        gap = statistics.mean(deltas)
        assert abs(gap) > 4 and all(d * (1 if gap > 0 else -1) > 2 for d in deltas)
        assert result["material"] and result["both_pass"]
        close(abs(gap), result["gap_pp"])
        gaps.append(abs(gap))
    close(sum(costs), audit["tariff_usd"])
    assert sum(costs) <= freeze["cap_usd"] and audit["verified_author_draws"] == 24
    assert audit["material_authors"] == len(authors) and not audit["uses_target_inputs"]
    ctrl = read("CONTROL.json")["constructive_examples"]
    controls = [ctrl[c]["score"] for c in ("low", "high")]
    assert all(s["invalid_order"] == 0 and 3.655 <= s["mean_ratio"] < 3.665 for s in controls)
    span = controls[1]["percent"] - controls[0]["percent"]
    bounds = audit["unrestricted_outer_percent"]
    close(span, audit["feasible_span_pp"])
    close(span / (bounds[1] - bounds[0]), audit["feasible_span_fraction_of_outer"])
    with (HERE / "LIFESTYLE_PAIRING.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    keys = {(r["author"], r["seed"], r["trait"], r["contrast"]) for r in rows}
    assert len(keys) == len(rows) == 54
    assert len({key[:2] for key in keys}) == 6 and len({key[2:] for key in keys}) == 9
    max_shifts = []
    for r in rows:
        shift = float(r["authored"]) - float(r["expected_after_repairing"])
        close(shift, float(r["pairing_contribution"]))
        scaled = abs(shift) / float(r["real_real_mad"])
        close(scaled, float(r["absolute_change_in_real_real_units"]))
        max_shifts.append(scaled)
    iron = read("../chns_statistical_comparator_2026-11-19/RESULTS.json")["results"]
    gains = []
    ref = iron["reference"]["rank"]
    for p in iron["pairs"]:
        gains.append(abs(p["repairing_expectation"]["rank"] - ref) - abs(p["agent"]["rank"] - ref))
    assert len(gains) == 6 and min(gains) > 0 and round(statistics.median(gains), 4) == .0612
    print(f"4 authors, 24 tables. Gaps {min(gaps):.2f} to {max(gaps):.2f} pp. Tariff USD {sum(costs):.7f}.")
    print(f"Two numerical examples span {span:.5f} pp. Nine lifestyle comparisons on six tables. "
          f"Maximum scaled change {max(max_shifts):.4f}. Six paired CHNS checks passed.")


if __name__ == "__main__":
    main()
