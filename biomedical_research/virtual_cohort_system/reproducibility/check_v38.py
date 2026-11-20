"""Check the six manuscript tables against archived, published study aggregates."""
import json
from pathlib import Path
from statistics import median

import check_v37


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "manuscript/kdd_draft_v38_2026-11-19"
OLD = ROOT / "work/chns_iron_conditional_holdout_2026-11-19"
NEW = ROOT / "work/chns_statistical_comparator_2026-11-19"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    check_v37.PAPER = PAPER
    check_v37.main()
    main_tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    appendix = (PAPER / "appendix.tex").read_text(encoding="utf-8")
    report = read(NEW / "RESULTS.json")["results"]
    source = read(NEW / "SOURCE_RESULTS.json")["results"]
    archived = read(OLD / "RESULTS.json")
    ranks = read(OLD / "RANK_COMPONENTS.json")["fixed_laws"]
    rows = check_v37.rows(main_tex, "tab:chnsattribution")
    fixed = report["statistical_draws"]
    direct = report["direct_A"]
    pairs = report["pairs"]
    columns = [("rank",4), ("rank_error",4), ("odds_ratio",3), ("abs_log_odds_error",3)]
    assert rows["Direct A threshold counts"] == ["---","---",f"{direct['odds_ratio']:.3f}",f"{direct['abs_log_odds_error']:.3f}"]
    assert rows["Statistical model, independent within Hb band"] == [f"{fixed[key]:.{digits}f}" for key,digits in columns]
    for label, key in [("Agent records, original pairing","agent"),
                       ("Agent records, expected after within-band re-pairing","repairing_expectation")]:
        expected = []
        for field, digits in columns:
            v = [p[key][field] for p in pairs]
            expected.append(f"{min(v):.{digits}f}--{max(v):.{digits}f}")
        assert rows[label] == expected, (label, rows[label], expected)
    ref = archived["reference"]
    reductions = []
    for parent, pair in archived["pairs"].items():
        rank = pair["estimates"]["control"]["rank"]
        perm = ranks[parent + "_control"]["between_hb_bands"]
        reductions.append(abs(perm - ref["rank"]) - abs(rank - ref["rank"]))
    assert min(reductions) > 0 and f"{median(reductions):.4f}" in main_tex
    for val in [min(reductions), max(reductions), source["population"]["rank"], *(r["rank"] for r in source["runs"])]:
        assert f"{val:.4f}" in appendix
    assert f"{source['population']['rank']:.4f}" in main_tex
    assert all(report["statistical_target_margins"].values())
    assert set(p["parent"] for p in pairs) == set(archived["pairs"])
    print(json.dumps({"v38_new_numeric_table_cells":14, "all_numeric_table_cells":155,
                      "analytic_and_three_seed_values_checked": True, "paired_reductions": len(reductions)}))


if __name__ == "__main__":
    main()
