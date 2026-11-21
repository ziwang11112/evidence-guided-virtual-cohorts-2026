"""Check the cross-cohort feasibility figure using only public study summaries."""
import json
from math import isclose
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check():
    audit = read(HERE / "PAIRING_AUDIT.json")
    old = WORK / "kdd_v40_pairing_review_2026-11-20"
    previous = read(WORK / "nonhdl_external_2026-11-20/REPLAY_RESULTS.json")["cohorts"]
    measured = read(HERE / "RESULTS.json")["estimates"]
    source_mean = read(HERE / "PACKET.json")["cases"]["mean_nonhdl"]["source_report"]["point"]
    outer_low, outer_high = read(old / "VERIFICATION.json")["unrestricted_outer_percent"]
    assert audit["outer"] == [outer_low, outer_high]
    authors = read(old / "SENSITIVITY.json")["authors"]
    bounds = {k: sorted(s["percent"] for s in v["scenarios"].values()) for k, v in authors.items()}
    numerical = read(old / "CONTROL.json")["constructive_examples"]
    lower, upper = sorted(r["score"]["percent"] for r in numerical.values())
    assert {**bounds, "numerical": [lower, upper]} == audit["feasible_ranges"]
    assert isclose(audit["width_covered_by_control"], (upper - lower) / (outer_high - outer_low))
    rows = audit["three_frames_and_two_nested_counties"]
    assert set(rows) == {"Virginia", "Buckingham", "Louisa", *previous}
    for name, row in rows.items():
        if name in previous:
            ref = previous[name]["reference"]
            count, mean, rate = ref["n"], ref["mean_mg_dl"], ref["tail_pct"]
            interval = previous[name]["reference_ci"]["tail_pct"]
        else:
            region = measured["all" if name == "Virginia" else name]
            nominal = region["scales"]["1.0"]
            count = region["n"]
            mean = nominal["mean_nonhdl"]["measured"]
            rate, interval = (nominal["nonhdl160"][k] for k in ("measured", "measured_ci"))
        assert count == row["n"] and isclose(rate, row["pct"]) and row["ci"] == interval
        assert isclose(mean - source_mean, row["target_minus_source_nonHDL_mg_dl"], abs_tol=1e-10)
        component_sum = row["target_minus_source_TC_mg_dl"] + row["source_minus_target_HDL_mg_dl"]
        assert isclose(mean - source_mean, component_sum, abs_tol=1e-10)
        n_bracket = sum(left <= rate <= right for left, right in bounds.values())
        assert n_bracket == row["agent_pairs_bracketing_point"]
        near = max(outer_low - rate, rate - outer_high, 0.)
        interval_near = max(outer_low - interval[1], interval[0] - outer_high, 0.)
        assert isclose(near, row["unrestricted_lower_bound_on_error_pp_at_point"])
        assert isclose(interval_near, row["minimum_distance_of_ci_to_outer_pp"])
        assert (near > 2) == row["unattainable_even_at_plusminus_2pp_for_point"]
        assert (interval_near > 2) == row["unattainable_even_at_plusminus_2pp_for_whole_ci"]
        assert (lower <= interval[0] <= interval[1] <= upper) == row["achievable_by_mixture_interval_contains_ci"]
    print("Three samples and two nested counties agree with released estimates, bounds and feasibility classifications.")


if __name__ == "__main__":
    check()
