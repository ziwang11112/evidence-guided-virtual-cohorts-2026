"""Score sealed source-only outputs using the already disclosed aggregate CHNS reference."""
import math
from statistics import median


def errors(rank, odds, ref):
    return {"rank": rank, "rank_error": None if rank is None else abs(rank - ref["rank"]),
            "odds_ratio": odds, "abs_log_odds_error": abs(math.log(odds / ref["odds_ratio"]))}


def compare(source_only, tables, archived, components):
    ref = archived["reference"]
    a, b, c, d = ref["cells"]
    assert math.isclose(a * d / (b * c), ref["odds_ratio"])
    (aa, ab), (ac, ad) = tables["table_1"]["counts"]
    direct = errors(None, aa * ad / (ab * ac), ref)
    pooled = source_only["pooled"]
    stat = errors(pooled["rank"], pooled["odds_ratio"], ref)
    analytic = errors(source_only["population"]["rank"], source_only["population"]["odds_ratio"], ref)
    assert math.isclose(direct["odds_ratio"], analytic["odds_ratio"])
    pairs = []
    gains = []
    for parent, pair in archived["pairs"].items():
        ctl = pair["estimates"]["control"]
        parts = components["fixed_laws"][parent + "_control"]
        expected = parts["between_hb_bands"]
        assert math.isclose(expected + sum(parts["within_bands_low_mid_high"]), ctl["rank"], abs_tol=1e-12)
        authored = errors(ctl["rank"], ctl["odds_ratio"], ref)
        repair = errors(expected, ctl["odds_ratio"], ref)
        gain = repair["rank_error"] - authored["rank_error"]
        gains.append(gain)
        pairs.append({"parent": parent, "agent": authored, "repairing_expectation": repair,
                      "within_parent_rank_error_reduction": gain,
                      "statistical_minus_agent_rank_error": stat["rank_error"] - authored["rank_error"]})
    assert len(pairs) == 6
    return {"design": "retrospective same-information modeling comparison; B was already open",
            "reference": ref, "direct_A": direct, "statistical_draws": stat, "statistical_population": analytic,
            "statistical_target_margins": {"rank_within_0.10": stat["rank_error"] <= .10,
                                          "odds_within_factor_1.50": stat["abs_log_odds_error"] <= math.log(1.50)},
            "pairs": pairs, "median_paired_rank_error_reduction": median(gains),
            "paired_improvements": sum(g > 0.0 for g in gains),
            "agent_rank_closer_than_statistical_draws": sum(p["agent"]["rank_error"] < stat["rank_error"] for p in pairs),
            "agent_odds_closer_than_statistical_draws": sum(p["agent"]["abs_log_odds_error"] < stat["abs_log_odds_error"] for p in pairs),
            "model_calls": 0, "new_statistical_laws": 1, "new_tables": len(source_only["runs"]),
            "new_virtual_rows": pooled["n"]}
