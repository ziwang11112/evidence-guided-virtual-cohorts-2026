"""Verify v0.37 against published project aggregates, with no model or patient access."""
import itertools
import json
import math
import re
import statistics
from pathlib import Path

import check_v35


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "manuscript/kdd_draft_v37_2026-11-19"
WORK = ROOT / "work"
CHNS = WORK / "chns_iron_conditional_holdout_2026-11-19"
IRON = WORK / "original_paper_iron_sensitivity_2026-11-19"


def read(folder, stem):
    return json.loads((folder / (stem + ".json")).read_text(encoding="utf-8"))


def rows(appendix, label):
    body = appendix.split(r"\label{" + label + "}", 1)[1].split(r"\end{tabular}", 1)[0]
    return {
        cells[0]: cells[1:]
        for line in body.splitlines() if "&" in line and line.endswith(r"\\")
        for cells in [[s.strip().strip("$") for s in line[:-2].strip().split("&")]]
    }


def verify_iron(appendix):
    laws = read(IRON, "SCIENTIFIC_RESULTS")["laws"]
    entries = rows(appendix, "tab:ironprospective")
    expected_numerical = 0
    keys = {"Statistical": "statistical"}
    for i, role in itertools.product(range(1, 4), ["primary", "ordinary", "directed"]):
        keys[f"P{i} {role}"] = f"P{i}" if role == "primary" else f"P{i}_{role}"
    for label, key in keys.items():
        law = laws.get(key, {})
        a, b, state = entries[label]
        expected_state = "incomplete" if "spearman" not in law else "pass" if law["tier2"] else "fail"
        assert state == expected_state, label
        for cell, field in ((a, "odds_ratio"), (b, "spearman")):
            value = law.get(field)
            if value is None:
                assert cell == "--", (key, field)
            else:
                assert cell == f"{value:.3f}", (key, field)
                expected_numerical += 1
    return expected_numerical


def verify_chns(main, appendix):
    result = read(CHNS, "RESULTS")
    models = read(CHNS, "SOURCE_CLOSURE")["models"]
    partition = read(CHNS, "PARTITION")
    decomposition = read(CHNS, "RANK_COMPONENTS")
    source_ratio = read(CHNS, "A_SUPPLEMENT")["estimate"]
    measured = result["reference"]
    assert partition["people_households_communities_disjoint"]
    assert partition["parts"]["A"]["n"] + partition["parts"]["B"]["n"] == 2205
    assert measured["n"] == sum(measured["cells"]) == 1082
    assert partition["parts"]["B"]["communities"] == measured["communities"] == 107
    joint, hb_only, ferritin_only, neither = measured["cells"]
    ref_or = joint * neither / (hb_only * ferritin_only)
    assert math.isclose(ref_or, measured["odds_ratio"])
    (both_a, hb_a), (ferritin_a, neither_a) = read(CHNS, "A_TABLES")["table_1"]["counts"]
    assert f"{both_a * neither_a / (hb_a * ferritin_a):.3f}" in main
    held = decomposition["heldout"]
    assert math.isclose(held["rho"], measured["rank"], abs_tol=1e-12)
    local_ref = held["within_bands_low_mid_high"][1]
    for law in [held, *decomposition["fixed_laws"].values()]:
        total = law["between_hb_bands"] + sum(law["within_bands_low_mid_high"])
        assert math.isclose(total, law["rho"], abs_tol=1e-12)
    entries = rows(appendix, "tab:chns")
    final_ranks, final_odds, base_errors, local_c, local_e = [], [], [], [], []
    gains = {"ordinary": [], "workflow": []}
    source_better = rank_better = local_better = passes = 0
    changed, unchanged = 0, 0
    for parent in result["pairs"]:
        original, control, augmented = [models[parent + suffix] for suffix in ("", "_control", "_evidence")]
        sig = lambda model: {r["seed"]: r["hash"] for r in model["runs"] if r["status"] == "success"}
        init, ctl, aug = (sig(m) for m in (original, control, augmented))
        assert len(init) == 3 and init.keys() == ctl.keys() == aug.keys()
        unchanged += sum(init[k] == ctl[k] for k in init)
        changed += sum(ctl[k] != aug[k] for k in init)
        c, e = (m["metrics"] for m in (control, augmented))
        rank = measured["rank"]
        gain = abs(c["rank"] - rank) - abs(e["rank"] - rank)
        loc = [abs(decomposition["fixed_laws"][parent + suffix]["within_bands_low_mid_high"][1] - local_ref)
               for suffix in ("_control", "_evidence")]
        arm = parent[:-1]
        gains[arm].append(gain)
        final_ranks.append(e["rank"])
        final_odds.append(e["odds_ratio"])
        base_errors.append(abs(c["rank"] - rank))
        local_c.append(loc[0])
        local_e.append(loc[1])
        source_better += abs(math.log(e["ratio"] / source_ratio)) < abs(math.log(c["ratio"] / source_ratio))
        rank_better += gain > 0
        local_better += loc[1] < loc[0]
        passes += (abs(e["rank"] - rank) <= .10 and 1 / 1.50 <= e["odds_ratio"] / ref_or <= 1.50
                   and 1 / 1.20 <= e["odds_ratio"] / c["odds_ratio"] <= 1.20)
        label = ("Ordinary " if arm == "ordinary" else "Guided ") + parent[-1]
        vals = [c["rank"], e["rank"], gain, e["odds_ratio"], *loc]
        expected = [f"{v:+.4f}" if i == 2 else f"{v:.4f}" for i, v in enumerate(vals)]
        assert entries[label] == expected, (label, entries[label], expected)
    assert (unchanged, changed, source_better, rank_better, local_better, passes) == (18, 18, 5, 1, 6, 6)
    for arm, values in gains.items():
        arm_result = result["arms"][arm]
        assert math.isclose(statistics.median(values), arm_result["median_incremental_gain"])
        assert not arm_result["material_benefit_rule_pass"]
        assert f"{statistics.median(values):.4f}" in main
    for values, decimals in [(final_ranks, 3), (final_odds, 3), (measured["rank_interval"], 3),
                             (measured["odds_interval"], 3)]:
        assert f"{min(values):.{decimals}f}--{max(values):.{decimals}f}" in main
    for value, places in [(local_ref, 5), (held["between_hb_bands"], 5), (max(base_errors), 3),
                          (statistics.median(local_c), 5), (statistics.median(local_e), 5)]:
        assert f"{value:.{places}f}" in main
    assert "one of six" in main and "post hoc decomposition" in main
    return {"paired_table_cells": 36, "source_fit_closer": source_better, "global_closer": rank_better,
            "exploratory_component_closer": local_better, "final_use_passes": passes}


def main():
    main_tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    appendix = (PAPER / "appendix.tex").read_text(encoding="utf-8")
    check_v35.PAPER = PAPER
    check_v35.main()
    n = verify_iron(appendix)
    chns = verify_chns(main_tex, appendix)
    figures = re.findall(r"\\includegraphics\[[^]]+\]\{([^}]+)\}", main_tex + appendix)
    assert len(set(figures)) == len(figures) == 7
    assert all((PAPER / f).is_file() for f in figures)
    print(json.dumps({"inherited_numeric_cells": 89 + n, "chns": chns, "figures": len(figures)}, indent=2))


if __name__ == "__main__":
    main()
