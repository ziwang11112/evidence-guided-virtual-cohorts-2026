"""Verify the KDD v0.40 scientific comparisons using only the public aggregates."""
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from xml.etree import ElementTree

import check_v39


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "manuscript/kdd_draft_v40_2026-11-20"
WORK = ROOT / "work"
LIPIDS = WORK / "nonhdl_external_2026-11-20"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def tables(directory):
    tex = "\n".join((directory / name).read_text(encoding="utf-8") for name in ("main.tex", "appendix.tex"))
    blocks = re.findall(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", tex, flags=re.DOTALL)
    return {re.search(r"\\label\{([^}]+)\}", block)[1]: block for block in blocks}


def check_iron_figure():
    results = read(WORK / "original_paper_iron_sensitivity_2026-11-19/SCIENTIFIC_RESULTS.json")
    laws = [value for name, value in results["laws"].items() if name != "statistical"]
    assert len(laws) == 7
    cells = {node.get("id"): node for node in ElementTree.parse(PAPER / "figures/evidence-and-pairing.drawio").iter("mxCell")}
    counts = laws[0]["extracted_cells"]
    assert all(law["extracted_cells"] == counts for law in laws)
    assert [cells[f"count{i}{j}"].get("value") for i in range(2) for j in range(2)] == [f"{n:,}" for n in counts]
    assert cells["or"].get("value").endswith(f"{counts[0]*counts[3]/(counts[1]*counts[2]):.2f}")
    for metric, digits in (("odds_ratio", 2), ("spearman", 3)):
        values = [law[metric] for law in laws]
        label = f"{min(values):.{digits}f} to {max(values):.{digits}f}"
        assert cells[metric + "-range"].get("value").endswith(label)
        assert all(metric + f"-{i}" in cells for i in range(len(laws)))


def check_lifestyle(main):
    with (WORK / "matched_size_utility_2026-11-17/CONTRAST_SUMMARIES.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    urban = [r for r in rows if r["trait"] == "bmi" and r["contrast"] == "urban_minus_pastoralist"]
    real = [float(r["absolute_mean"]) for r in urban if r["comparison"] == "real_real"]
    virtual = [float(r["absolute_mean"]) for r in urban if r["comparison"] == "virtual_real"]
    rural = [-float(r["signed_mean"]) for r in rows if r["comparison"] == "virtual_real" and r["trait"] == "total_cholesterol" and r["contrast"] == "rural_minus_pastoralist"]
    assert len(real) == 1 and len(virtual) == len(rural) == 6
    for value in (f"{real[0]:.3f}", f"{min(virtual):.3f} to {max(virtual):.3f}", f"{min(rural):.2f}--{max(rural):.2f}"):
        assert value in main, value


def check_lipids(main):
    closure = read(LIPIDS / "MODEL_CLOSURE.json")
    reference_open = read(LIPIDS / "REFERENCE_OPEN.json")
    result = read(LIPIDS / "REPLAY_RESULTS.json")
    verify = read(LIPIDS / "REPLAY_VERIFICATION.json")
    assert not closure["target_results_opened"] and closure["time_utc"] < reference_open["first_access_utc"]
    assert verify["unaltered_program_model_and_decision"] and verify["raw_failure_preserved"] and not result["raw_agent_usable"]
    assert verify["numerically_recomputed_draws"] == 6 and verify["separate_measured_readers"]
    digest = hashlib.sha256((LIPIDS / "REPLAY_RESULTS.json").read_text(encoding="utf-8").encode()).hexdigest()
    assert verify["replay_results_sha256"] == digest
    source = read(LIPIDS / "SOURCE.json")
    mean = (source["tc_mean"]["estimate"] - source["hdl_mean"]["estimate"]) * source["cholesterol_mg_dl_per_mmol_l"]
    for arm in closure["arms"].values():
        runs = arm["runs"]
        pooled = arm["pooled"]
        assert arm["usable"] and [r["seed"] for r in runs] == [40711, 40727, 40739]
        assert sum(r["estimates"]["tail_count"] for r in runs) == pooled["tail_count"]
        assert sum(r["estimates"]["n"] for r in runs) == pooled["n"]
        assert math.isclose(100 * pooled["tail_count"] / pooled["n"], pooled["tail_pct"])
        assert all(math.isclose(r["estimates"]["mean_mg_dl"], mean) for r in runs)
        assert f"{pooled['tail_pct']:.2f}" in main and f"{mean:.2f}" in main
    for site, scores in result["cohorts"].items():
        ref = scores["reference"]
        assert f"{ref['tail_count']} of {ref['n']:,}" in main
        assert math.isclose(ref["tail_pct"], 100 * ref["tail_count"] / ref["n"])
        assert f"{ref['mean_mg_dl']:.2f}" in main and f"{ref['tail_pct']:.2f}" in main
        for name, arm in scores["arms"].items():
            rate = closure["arms"][name]["pooled"]["tail_pct"]
            assert math.isclose(rate - ref["tail_pct"], arm["tail_gap_pp"])
            lower, upper = [rate - x for x in reversed(scores["reference_ci"]["tail_pct"])]
            assert all(math.isclose(a,b) for a,b in zip((lower,upper),arm["tail_gap_interval_pp"],strict=True))
            state = "outside" if lower > 2 or upper < -2 else "within" if lower >= -2 and upper <= 2 else "unresolved"
            assert state == arm["planning_status"]
            if name == "agent":
                assert f"{lower:.2f}" in main and f"{upper:.2f}" in main
    return {site: z["arms"]["agent"]["planning_status"] for site, z in result["cohorts"].items()}


def main():
    check_v39.main()
    current = tables(PAPER)
    assert len(current) == 7 and current == tables(check_v39.PAPER)
    main_tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    assert re.findall(r"\\label\{(fig:[^}]+)\}", main_tex) == ["fig:method", "fig:lifestyle-main", "fig:nonhdl"]
    check_iron_figure()
    check_lifestyle(main_tex)
    decisions = check_lipids(main_tex)
    print(json.dumps({"release": "0.40", "inherited_table_cells_verified": 178, "main_figure_generator_laws": 7,
                      "lifestyle_virtual_tables": 6, "frozen_external_draws": 6, "external_planning_results": decisions}))


if __name__ == "__main__":
    main()
