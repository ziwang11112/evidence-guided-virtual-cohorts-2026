"""Postclosure aggregate reporting; no model calls, row reads or law modifications.

Default output is PNG/SVG/CSV/Markdown. PDF is explicit opt-in after the host has
completed the PDF artifact-start requirement for the two figure families.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "request_only_repeatability_2026-11-11"
OUT = ROOT / "reporting"
STAGES = ("initial", "generic", "structured")
LABELS = {"initial": "Initial law", "generic": "Generic review", "structured": "Structured review"}
COLORS = {"initial": "#7C8797", "generic": "#3765AF", "structured": "#D37A35"}
PANELS = [
    ("PNS", "bmi_sbp", "BMI-SBP association", "mmHg per 5 kg/m²"),
    ("PNS", "bmi_dbp", "BMI-DBP association", "mmHg per 5 kg/m²"),
    ("PNS", "residual_correlation", "SBP-DBP residual dependence", "Pearson correlation"),
    ("lipids", "K02-TC-BMI", "BMI-TC association", "mg/dL per 5 kg/m²"),
    ("lipids", "K02-HDL-BMI", "BMI-HDL association", "mg/dL per 5 kg/m²"),
    ("lipids", "K02-LIPID-RESIDUAL", "TC-HDL residual dependence", "Pearson correlation"),
]
METRICS = {
    "PNS": [("bmi_sbp", "BMI-SBP"), ("bmi_dbp", "BMI-DBP"),
            ("residual_correlation", "Residual SBP-DBP"),
            ("sbp.sd_population", "SBP SD"), ("dbp.sd_population", "DBP SD"),
            ("sbp_below_dbp_fraction", "SBP < DBP fraction")],
    "lipids": [("K02-TC-BMI", "BMI-TC"), ("K02-HDL-BMI", "BMI-HDL"),
               ("K02-LIPID-RESIDUAL", "Residual TC-HDL"),
               ("total_cholesterol.sd_sample", "TC SD"),
               ("hdl_cholesterol.sd_sample", "HDL SD"),
               ("hdl_above_total_fraction", "HDL > TC fraction")],
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def close_enough(a, b):
    if a is None or b is None:
        return a is b
    return finite(a) and finite(b) and math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def load_closed_aggregates():
    """Never open any evaluation/reference values before the complete-closure gate."""
    plan = read(ROOT / "PLAN.json")
    episodes = plan["episodes"]
    ids = {e["episode_id"] for e in episodes}
    require(len(episodes) == len(ids) == 24, "Exactly 24 assigned review episodes are required")
    require(all((ROOT / "episodes" / eid / "OUTCOME.json").is_file() for eid in ids),
            "Refusing reporting before all 24 review outcomes exist")
    for name in ("CONSTRUCTION_CLOSURE.json", "FINAL_TABLES.json", "EVALUATION.json"):
        require((ROOT / name).is_file(), "Refusing reporting before " + name)
    closure = read(ROOT / "CONSTRUCTION_CLOSURE.json")
    require(closure.get("all_episodes_closed") is True, "Construction is not closed")
    require(len(closure["episodes"]) == 24 and {r["episode_id"] for r in closure["episodes"]} == ids,
            "Construction closure does not cover the full planned roster")
    require(closure["plan_sha256"] == sha(ROOT / "PLAN.json"), "Closure binds a different plan")
    seeds = plan["evaluation_seeds"]
    require(len(seeds) == len(set(seeds)) == 3 and closure["evaluation_seeds"] == seeds,
            "Unexpected final seed schedule")
    final_tables = read(ROOT / "FINAL_TABLES.json")
    require(final_tables["construction_closure_sha256"] == sha(ROOT / "CONSTRUCTION_CLOSURE.json"),
            "Final tables do not bind the completed closure")
    slots = final_tables["slots"]
    require(len(slots) == 72 and {(r["episode_id"], r["seed"]) for r in slots} ==
            {(eid, seed) for eid in ids for seed in seeds}, "All 72 final slots must be retained")
    require(all(r["status"] in {"success", "failed", "unavailable"} for r in slots),
            "Unexpected final-table status")

    # Clinical comparisons become readable only after all gates above pass.
    evaluation = read(ROOT / "EVALUATION.json")
    require(evaluation["counts"]["episodes"] == 24 and evaluation["counts"]["final_slots"] == 72,
            "Evaluation is not the complete 24-episode experiment")
    require(evaluation["final_tables_sha256"] == sha(ROOT / "FINAL_TABLES.json"),
            "Evaluation binds different final tables")
    require(evaluation["slots"] == slots, "Evaluation slot list differs from frozen final tables")
    require(len(evaluation["episodes"]) == 24 and
            {e["episode_id"] for e in evaluation["episodes"]} == ids, "Missing evaluated reviewer")
    for status, key in [("success", "successful_tables"), ("failed", "failed_tables"),
                        ("unavailable", "unavailable_tables")]:
        require(evaluation["counts"][key] == sum(s["status"] == status for s in slots),
                "Delivery count mismatch: " + key)

    baseline_bindings = read(ROOT / "BASELINE_BINDINGS.json")
    allowed_baseline_aggregates = {"EVALUATION.json", "FINAL_TABLES.json", "CONSTRUCTION_CLOSURE.json", "ANALYSIS_RESULTS.csv"}
    require(set(baseline_bindings["files"]) <= allowed_baseline_aggregates and
            "EVALUATION.json" in baseline_bindings["files"],
            "Reporter may bind only the named baseline aggregate artifacts, never row tables")
    for name, digest in baseline_bindings["files"].items():
        path = (OLD / name).resolve()
        require(path.is_relative_to(OLD.resolve()), "Invalid baseline aggregate binding")
        require(sha(path) == digest, "Initial aggregate changed: " + name)
    initial = read(OLD / "EVALUATION.json")
    require(initial["counts"]["episodes"] == 12 and initial["counts"]["final_slots"] == 36,
            "Unexpected initial experiment")
    require(evaluation["paired_initial_comparison"]["old_evaluation_sha256"] == sha(OLD / "EVALUATION.json"),
            "Paired comparison binds a different initial evaluation")
    mapping = read(ROOT / "_host_only/IMPORT_MAPPING.json")["pairs"]
    pairs = {m["pair_id"]: m for m in mapping}
    require(len(mapping) == len(pairs) == 12, "Twelve distinct initial laws required")
    ep_lookup = {e["episode_id"]: e for e in episodes}
    for pid in pairs:
        assigned = [e for e in episodes if e["pair_id"] == pid]
        require(len(assigned) == 2 and {e["arm"] for e in assigned} == {"generic", "structured"},
                "Each starting law must have both review arms")
        pairs[pid] = dict(pairs[pid], case_id=assigned[0]["case_id"])
        require(all(e["case_id"] == pairs[pid]["case_id"] for e in assigned), "Pair context mismatch")
    require(all(sum(p["case_id"] == case for p in pairs.values()) == 6 for case in METRICS),
            "Six starting laws required in each context")
    initial_lookup = {(r["episode_id"], r["analysis_id"]): r for r in initial["summaries"]}
    final_lookup = {(r["episode_id"], r["analysis_id"]): r for r in evaluation["summaries"]}
    require(len(initial_lookup) == len(initial["summaries"]), "Duplicate initial summary")
    require(len(final_lookup) == len(evaluation["summaries"]), "Duplicate final summary")
    rows = []
    for pid, pair in sorted(pairs.items()):
        case = pair["case_id"]
        for metric, _ in METRICS[case]:
            before = initial_lookup[(pair["old_episode_id"], metric)]
            for stage in STAGES:
                episode_id = pair["old_episode_id"] if stage == "initial" else pid + "_" + stage.upper()
                source = before if stage == "initial" else final_lookup[(episode_id, metric)]
                require(source["reference"] == before["reference"] and source["unit"] == before["unit"],
                        "Reference or unit changed within a pair")
                require({v["seed"] for v in source["values"]} == set(seeds), "Unexpected summary seeds")
                valid_values = [v["value"] for v in source["values"] if v["status"] == "success" and v["value"] is not None]
                require(all(finite(v) for v in valid_values), "Nonfinite aggregate cannot be plotted as a value")
                require(source["available_seeds"] == len(valid_values), "Summary availability mismatch")
                require(close_enough(source["mean"], mean(valid_values) if valid_values else None),
                        "Summary mean differs from its available seeds")
                rows.append(dict(source, pair_id=pid, stage=stage, episode_id=episode_id,
                                 initial_episode_id=pair["old_episode_id"], case_id=case))
    lookup = {(r["pair_id"], r["stage"], r["analysis_id"]): r for r in rows}
    paired = evaluation["paired_initial_comparison"]["rows"]
    paired_lookup = {(r["pair_id"], r["arm"], r["analysis_id"]): r for r in paired}
    require(len(paired_lookup) == len(paired), "Duplicate paired summary")
    for pid, pair in pairs.items():
        for metric, _ in METRICS[pair["case_id"]]:
            before = lookup[(pid, "initial", metric)]
            ref = before["reference"].get("value")
            for stage in ("generic", "structured"):
                after = lookup[(pid, stage, metric)]
                comparison = paired_lookup[(pid, stage, metric)]
                delta = None if before["mean"] is None or after["mean"] is None or ref is None else abs(after["mean"]-ref)-abs(before["mean"]-ref)
                require(close_enough(comparison["change_in_absolute_reference_difference"], delta),
                        "Paired absolute-reference-distance change mismatch")
    return plan, evaluation, initial, pairs, rows, lookup, paired_lookup


def setup_style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
        "axes.titleweight": "semibold", "text.color": "#243044", "axes.labelcolor": "#303B4D",
        "axes.edgecolor": "#D3D9E3", "axes.spines.top": False, "axes.spines.right": False,
        "svg.fonttype": "none", "pdf.fonttype": 42, "axes.unicode_minus": False})
    return plt


def save_figure(fig, stem, pdf):
    for ext in (["png", "svg", "pdf"] if pdf else ["png", "svg"]):
        fig.savefig(OUT / (stem+"."+ext), dpi=220, bbox_inches="tight", facecolor="white")


def draw_profiles(plt, pairs, lookup, pdf):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    fig, axes = plt.subplots(2, 3, figsize=(15.2, 9.6))
    offsets = {"initial": -.23, "generic": 0., "structured": .23}
    for index, (ax, (case, metric, title, unit)) in enumerate(zip(axes.flat, PANELS)):
        ids = [pid for pid, p in sorted(pairs.items()) if p["case_id"] == case]
        ref = lookup[(ids[0], "initial", metric)]["reference"]
        rv, unc = ref.get("value"), ref.get("uncertainty") or {}
        if unc.get("status") == "available" and finite(unc.get("lower")) and finite(unc.get("upper")):
            ax.axvspan(unc["lower"], unc["upper"], color="#BAC3D1", alpha=.22, zorder=0)
        if finite(rv):
            ax.axvline(rv, color="#263247", lw=1.2, ls=(0, (4, 3)), zorder=1)
        for y, pid in enumerate(ids):
            if y % 2:
                ax.axhspan(y-.48, y+.48, color="#F6F7FA", zorder=-1)
            for stage in STAGES:
                row = lookup[(pid, stage, metric)]
                level = y + offsets[stage]
                values = [v["value"] for v in row["values"] if v["status"] == "success" and v["value"] is not None]
                if not values:
                    ax.text(.02, level, LABELS[stage]+": unavailable", transform=ax.get_yaxis_transform(),
                            fontsize=7.1, color=COLORS[stage], va="center")
                    continue
                marker = "s" if stage == "initial" else "o"
                ax.plot([min(values), max(values)], [level, level], color=COLORS[stage], lw=1.5, alpha=.65, zorder=3)
                ax.scatter(values, [level]*len(values), marker=marker, facecolors="white", edgecolors=COLORS[stage], s=15, lw=.7, zorder=4)
                ax.scatter([row["mean"]], [level], marker=marker, c=COLORS[stage], s=31, edgecolors="white", lw=.5, zorder=5)
                if len(values) < 3:
                    ax.text(.985, level, f"{len(values)}/3", transform=ax.get_yaxis_transform(),
                            ha="right", va="center", fontsize=7, color=COLORS[stage])
        ax.set_ylim(5.55, -.55)
        ax.set_yticks(range(6), ids)
        ax.set_title(f"{chr(97+index)}   {title}", loc="left", fontsize=11.5, pad=12)
        ax.set_xlabel(unit, labelpad=7)
        ax.tick_params(length=0, pad=5)
        ax.xaxis.grid(True, color="#E4E9F0", lw=.6)
        ax.set_axisbelow(True)
        ax.text(.99, 1.025, "Blood pressure" if case == "PNS" else "Lipids", transform=ax.transAxes,
                ha="right", fontsize=8, color="#697489")
    fig.suptitle("Scientific analyses before and after Agent-led review", x=.06, y=.986,
                 ha="left", fontsize=19, weight="bold")
    fig.text(.06, .947, "12 starting laws · paired generic and structured review · all requested analyses", fontsize=11, color="#697489")
    handles = [Line2D([0], [0], marker="s" if s=="initial" else "o", color=COLORS[s], lw=1.5, label=LABELS[s]) for s in STAGES]
    handles += [Line2D([0], [0], color="#263247", ls="--", label="Existing sample reference"),
                Patch(facecolor="#BAC3D1", alpha=.3, label="Available reference uncertainty")]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(.51, .058), fontsize=8.8)
    fig.text(.06, .036, "Filled markers: three-seed means. Open markers / segments: individual estimates / range; partial availability is labeled.", fontsize=8.6, color="#697489")
    fig.text(.06, .019, "Seed variation includes encoded scenario draws; ranges are not confidence intervals. Same seed labels do not guarantee matched random events.", fontsize=8.6, color="#697489")
    fig.text(.06, .002, "Previously exposed sample references retain their original uncertainty conventions. R IDs identify paired starting laws, not clinical participants.", fontsize=8.6, color="#697489")
    fig.subplots_adjust(left=.085, right=.987, top=.88, bottom=.16, wspace=.32, hspace=.42)
    save_figure(fig, "paired_analysis_profiles", pdf)
    plt.close(fig)


def draw_changes(plt, pairs, comparisons, pdf):
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator, ScalarFormatter, FuncFormatter
    fig, axes = plt.subplots(2, 3, figsize=(15.2, 8.7))
    for index, (ax, (case, metric, title, unit)) in enumerate(zip(axes.flat, PANELS)):
        ids = [pid for pid, p in sorted(pairs.items()) if p["case_id"] == case]
        ax.axvline(0, color="#263247", lw=1.2, ls=(0, (4, 3)), zorder=1)
        for y, pid in enumerate(ids):
            if y % 2:
                ax.axhspan(y-.48, y+.48, color="#F6F7FA", zorder=-1)
            for stage, offset in [("generic", -.13), ("structured", .13)]:
                row = comparisons[(pid, stage, metric)]
                value = row["change_in_absolute_reference_difference"]
                if value is None:
                    ax.text(.02, y+offset, LABELS[stage]+": unavailable", transform=ax.get_yaxis_transform(),
                            va="center", fontsize=7.4, color=COLORS[stage])
                    continue
                ax.plot([0, value], [y+offset, y+offset], color=COLORS[stage], lw=1.3, alpha=.6)
                ax.scatter([value], [y+offset], c=COLORS[stage], s=34, edgecolors="white", lw=.5, zorder=3)
        ax.set_ylim(5.55, -.55)
        ax.set_yticks(range(6), ids)
        ax.set_title(f"{chr(97+index)}   {title}", loc="left", fontsize=11.5, pad=12)
        ax.set_xlabel("Change in absolute difference ("+unit+")", fontsize=9.1, labelpad=8)
        ax.tick_params(length=0, pad=5)
        ax.xaxis.grid(True, color="#E4E9F0", lw=.6)
        ax.set_axisbelow(True)
        ax.text(.99, 1.025, "Blood pressure" if case=="PNS" else "Lipids", transform=ax.transAxes,
                ha="right", fontsize=8, color="#697489")
        lo, hi = ax.get_xlim()
        span = max(abs(lo), abs(hi), 1e-12)
        ax.set_xlim(-span*1.06, span*1.06)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        formatter = ScalarFormatter(useOffset=False)
        formatter.set_powerlimits((-3, 4))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, pos: f"{value:.4f}") if span < .001 else formatter)
    fig.suptitle("Paired changes relative to each starting law", x=.06, y=.985, ha="left", fontsize=19, weight="bold")
    fig.text(.06, .942, "Negative: closer to the existing sample point · Positive: farther · Zero: unchanged point-distance", fontsize=11, color="#697489")
    handles=[Line2D([0],[0],marker="o",color=COLORS[s],lw=1.5,label=LABELS[s]) for s in ("generic","structured")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(.51,.055), fontsize=10)
    fig.text(.06,.033,"Each point is |final three-seed mean - reference| - |initial three-seed mean - reference|. No combined quality score is defined.",fontsize=8.7,color="#697489")
    fig.text(.06,.015,"Distance to a sample estimate is not population accuracy or a scientific-validity test. All endpoints, no-ops and unavailable outputs are retained.",fontsize=8.7,color="#697489")
    fig.text(.06,.000,"Both review policies share tools and starting artifacts; the structured prompt and completion gate form the treatment. Six endpoints are not six independent clinical tasks.",fontsize=8.5,color="#697489")
    fig.subplots_adjust(left=.085,right=.987,top=.875,bottom=.17,wspace=.32,hspace=.45)
    save_figure(fig,"paired_reference_distance_changes",pdf)
    plt.close(fig)


def write_csv(path, rows):
    require(bool(rows), "Refusing an empty reporting table")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value, digits=4):
    return "unavailable" if value is None else f"{value:.{digits}f}"


def tables(plan, evaluation, pairs, rows, lookup, comparisons):
    aggregate_rows, seed_rows = [], []
    for row in rows:
        ref = row["reference"]
        unc = ref.get("uncertainty") or {}
        aggregate_rows.append({k:row[k] for k in ["pair_id","case_id","stage","episode_id","initial_episode_id","analysis_id","unit","available_seeds","mean","minimum","maximum"]} | {
            "reference_value":ref.get("value"),"reference_uncertainty_status":unc.get("status"),
            "reference_interval_lower":unc.get("lower"),"reference_interval_upper":unc.get("upper"),
            "reference_uncertainty_kind":unc.get("kind")})
        for value in row["values"]:
            seed_rows.append({k:row[k] for k in ["pair_id","case_id","stage","episode_id","analysis_id","unit"]} | value)
    write_csv(OUT/"all_analysis_aggregates.csv",aggregate_rows)
    write_csv(OUT/"all_analysis_seed_estimates.csv",seed_rows)
    paired_rows = sorted(comparisons.values(), key=lambda r:(r["case_id"]!="PNS",r["pair_id"],r["analysis_id"],r["arm"]))
    write_csv(OUT/"all_paired_changes.csv",paired_rows)
    changes=evaluation["paired_initial_comparison"]["artifact_changes"]
    outcomes={r["episode_id"]:r for r in evaluation["episodes"]}
    resources=[]
    for episode in plan["episodes"]:
        eid=episode["episode_id"]; row=outcomes[eid]; usage=row.get("tool_usage")or{}
        slots=[s for s in evaluation["slots"] if s["episode_id"]==eid]
        delta=changes[eid]
        resources.append({"pair_id":episode["pair_id"],"case_id":episode["case_id"],"episode_id":eid,"review_arm":episode["arm"],
            "status":row["status"],"selected_candidate":row.get("selected_candidate"),
            "explicitly_retained_import":delta["explicitly_retained_import"],
            "code_bytes_changed":delta["changed_artifact_bytes"]["generator.py"],
            "spec_bytes_changed":delta["changed_artifact_bytes"]["model_spec.json"],
            "notes_bytes_changed":delta["changed_artifact_bytes"]["notes.json"],
            "tables_delivered":sum(s["status"]=="success" for s in slots),
            "tables_failed":sum(s["status"]=="failed" for s in slots),
            "tables_unavailable":sum(s["status"]=="unavailable" for s in slots),
            "model_calls":row["calls_reserved"],"queries":usage.get("queries",0),"downloads":usage.get("downloads",0),
            "new_submissions":usage.get("candidates_submitted",0),"trials":usage.get("executions",0),
            "scientific_inspections":usage.get("scientific_inspections",0),
            "known_tariff_usd":row["known_tariff_cost_usd"],"accounted_usd":row["accounted_usd"],
            "unknown_usage_calls":row["unknown_usage_calls"]})
    write_csv(OUT/"all_delivery_resources.csv",resources)
    descriptive=[]
    for case,metric,title,unit in PANELS:
        for stage in ("generic","structured"):
            selected=[r for r in comparisons.values() if r["case_id"]==case and r["analysis_id"]==metric and r["arm"]==stage]
            values=[r["change_in_absolute_reference_difference"] for r in selected if r["change_in_absolute_reference_difference"] is not None]
            descriptive.append({"case_id":case,"analysis_id":metric,"review_arm":stage,"unit":unit,
                "paired_laws_planned":6,"paired_laws_with_estimate":len(values),
                "mean_change_in_absolute_point_distance":mean(values)if values else None,
                "median_change_in_absolute_point_distance":median(values)if values else None,
                "minimum":min(values)if values else None,"maximum":max(values)if values else None})
    write_csv(OUT/"descriptive_paired_endpoint_profiles.csv",descriptive)
    text=["# Complete paired revision aggregate tables","",
        "Every starting law, both review branches, all prescribed seeds and unavailable slots are retained. Initial artifacts were frozen before this unit. No patient or generated row file is read by this reporter.","",
        f"Delivery: {evaluation['counts']['successful_tables']} successful, {evaluation['counts']['failed_tables']} failed and {evaluation['counts']['unavailable_tables']} unavailable final tables / 72 planned. Model calls: {evaluation['counts']['model_calls']}. Known token-tariff cost USD{evaluation['costs']['known_tariff_usd']:.7f}; accounted USD{evaluation['costs']['accounted_usd']:.7f}.","",
        "This is a paired developmental review study of twelve existing laws in two contexts. It is not a fresh end-to-end construction study or an independent clinical holdout. A completed program or closer sample estimate does not establish a valid population model.",""]
    for case,metrics in METRICS.items():
        text += [f"## {case}: all laws and stages","","| Starting law | Stage | "+" | ".join(label for _,label in metrics)+" |",
                 "|---|---|"+"---:|"*len(metrics)]
        ids=[pid for pid,pair in sorted(pairs.items())if pair["case_id"]==case]
        for pid in ids:
            for stage in STAGES:
                values=[]
                for metric,_ in metrics:
                    row=lookup[(pid,stage,metric)]
                    value=fmt(row["mean"])
                    if row["available_seeds"]<3:value+=f" ({row['available_seeds']}/3)"
                    values.append(value)
                text.append("| "+pid+" | "+LABELS[stage]+" | "+" | ".join(values)+" |")
        text.append("| Existing sample reference | - | "+" | ".join(fmt(lookup[(ids[0],"initial",m)]["reference"].get("value"))for m,_ in metrics)+" |")
        text += ["","Units in column order: "+"; ".join(lookup[(ids[0],"initial",m)]["unit"]for m,_ in metrics)+".","",
                 "Cells are means across available final seeds; partial availability is explicit. Full per-seed values, counts and intervals are in the CSV files. BP SD retains the population-SD convention; lipid SD retains the sample-SD convention. Fractions are proportions, not percentages. An unavailable reference is not zero.",""]
    text += ["## Every paired analytical change","",
             "Negative change in absolute distance means closer to the same existing sample point. This is computed from each law's three-seed mean, not an average of seed-level absolute errors, not an equivalence test and not a clinical accuracy certificate.","",
             "| Law | Review | Analysis | Unit | Initial mean | Final mean | Reference | Change in mean | Change in absolute distance | Available final seeds |",
             "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in paired_rows:
        text.append(f"| {row['pair_id']} | {row['arm']} | {row['analysis_id']} | {row['unit']} | {fmt(row['initial_mean'])} | {fmt(row['final_mean'])} | {fmt(row['reference_value'])} | {fmt(row['change_in_mean'])} | {fmt(row['change_in_absolute_reference_difference'])} | {row['final_available_seeds']}/3 |")
    text += ["","## Delivery, resources and artifact changes","",
             "| Session | Status | Selected | Tables delivered/failed/unavailable | API calls | Admitted search requests | Successful source downloads | New submissions | Trials | Completed review receipts | Known USD | Unknown calls |",
             "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in resources:
        text.append(f"| {row['episode_id']} | {row['status']} | {row['selected_candidate'] or 'none'} | {row['tables_delivered']}/{row['tables_failed']}/{row['tables_unavailable']} | {row['model_calls']} | {row['queries']} | {row['downloads']} | {row['new_submissions']} | {row['trials']} | {row['scientific_inspections']} | {row['known_tariff_usd']:.7f} | {row['unknown_usage_calls']} |")
    text += ["","Resource-counter semantics: `queries` denotes admitted search requests, including gateway errors, not all attempted calls. Ordinary/structured review made 22/36 search calls: 16/25 were admitted, including 2/4 gateway errors; 6/11 were locally rejected. `scientific_inspections` denotes completed review receipts: 13/12 from 18/25 inspection invocations. The remaining ordinary responses were 2 static-only and 3 invalid-contract responses; structured responses were 1 static-only and 12 invalid-contract responses. `downloads` denotes successful new full-source downloads (1/2). Absent audited tool-counter keys are zero, not unavailable. See the operational-count paragraph in [RESULTS, section 2](../RESULTS.md#2-what-was-integrated). These counts measure operations, not evidence quality.","",
             "Byte-change flags are in all_delivery_resources.csv. A changed filename, note or code byte does not prove a scientific repair. Independent law/source adjudication must determine mathematical correctness and the meaning of each change. Costs exclude human review and infrastructure and are not invoices.","",
             "## Starting-law lineage","","| Pair | Original author | Context |","|---|---|---|"]
    for pid,pair in sorted(pairs.items()):text.append(f"| {pid} | {pair['old_episode_id']} | {pair['case_id']} |")
    text += ["","The original construction policy is lineage, not the current review treatment. Initial-law scenario sampling and any new shared-parameter draws remain encoded uncertainty, not calibrated transport confidence. Same seed labels can consume different random events after revision. Neither seed tables nor endpoints count as independent clinical replications.","",
             "The common physiological diagnostics above are separate from Agent-selected rule checks. Easier self-selected rules, unavailable checks or richer documentation cannot alone demonstrate better final data. Preserve source-exposure records and reference limitations alongside these tables. No combined quality score or task-general superiority conclusion is computed.",""]
    (OUT/"AGGREGATE_TABLES.md").write_text("\n".join(text),encoding="utf-8")
    (OUT/"SUMMARY_STATS.json").write_text(json.dumps({"counts":evaluation["counts"],"costs":evaluation["costs"],
        "descriptive_paired_profiles":descriptive,"resource_rows":resources,
        "scope":"Aggregate reporting only; no scientific-validity classification or combined quality score"},indent=2),encoding="utf-8")
    return len(aggregate_rows),len(seed_rows),len(paired_rows)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pdf",action="store_true",help="Explicit PDF export only after host artifact-start step")
    args=parser.parse_args()
    plan,evaluation,initial,pairs,rows,lookup,comparisons=load_closed_aggregates()
    OUT.mkdir(exist_ok=True)
    plt=setup_style()
    draw_profiles(plt,pairs,lookup,args.pdf)
    draw_changes(plt,pairs,comparisons,args.pdf)
    aggregate_count,seed_count,paired_count=tables(plan,evaluation,pairs,rows,lookup,comparisons)
    manifest={"evaluation_sha256":sha(ROOT/"EVALUATION.json"),"plan_sha256":sha(ROOT/"PLAN.json"),
        "closure_sha256":sha(ROOT/"CONSTRUCTION_CLOSURE.json"),"final_tables_sha256":sha(ROOT/"FINAL_TABLES.json"),
        "initial_evaluation_sha256":sha(OLD/"EVALUATION.json"),"renderer_sha256":sha(Path(__file__)),
        "aggregate_rows":aggregate_count,"seed_estimates":seed_count,"paired_changes":paired_count,
        "patient_or_generated_rows_read":False,"pdf_export_requested":args.pdf,"visual_review":"pending",
        "files":{p.name:sha(p)for p in sorted(OUT.iterdir())if p.is_file() and p.name!="REPORTING_MANIFEST.json"}}
    (OUT/"REPORTING_MANIFEST.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps({"figure_families":2,"aggregate_rows":aggregate_count,"seed_estimates":seed_count,
                      "paired_changes":paired_count,"pdf_export":args.pdf,"output_directory":str(OUT)}))


if __name__=="__main__":
    main()
