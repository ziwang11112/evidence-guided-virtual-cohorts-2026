"""Scientific-use figures from retained aggregates; no rows, fitting or evaluation.

Run this script to rebuild the two figure derivatives, their exact plotting
payload and numeric manifest. Work and public reports layouts are supported.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
COLORS = {"basic": "#9674AE", "relational": "#007F79", "statistical": "#555D68"}
MAIN_SHA = "1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb"
HISTORY_SHA = "d64b7cd5bd1097a4ea51b84b00a3721d54c092cc87db85da9418bdd24bd187a0"
MAIN_DEFINITIONS = {
    "CHNS2009": [("E1", "BMI", "Age, sex", "per kg/m²"),
                 ("E2", "Glucose", "Age, sex", "per mmol/L"),
                 ("E3", "Age", "Sex, BMI, glucose", "per year")],
    "ENSANUT2018": [("Q1_age10", "Age", "Sex, BMI, glucose", "per 10 years"),
                    ("Q2_bmi5", "BMI", "Age, sex", "per 5 kg/m²"),
                    ("Q3_bmi5", "BMI", "Age, sex, glucose", "per 5 kg/m²")],
}
HISTORY_DEFINITIONS = [
    ("E1", "BMI", "Age, sex", "HbA1c percentage points\nper kg/m²"),
    ("E2", "Glucose", "Age, sex", "HbA1c percentage points\nper mmol/L"),
    ("E3", "Age", "Sex, BMI, glucose", "HbA1c percentage points\nper year"),
    ("glucose_hba1c_pearson", "Glucose–HbA1c", "Pearson correlation", "Correlation coefficient"),
    ("glucose_hba1c_spearman", "Glucose–HbA1c", "Spearman correlation", "Rank correlation coefficient"),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def source_path(unit, filename):
    for parent in ("work", "reports"):
        path = PROJECT / parent / unit / filename
        if path.is_file():
            return path
    raise FileNotFoundError(f"No retained aggregate {unit}/{filename}")


def close(left, right):
    return math.isclose(left, right, abs_tol=1e-12, rel_tol=1e-10)


def validate_series(series):
    values = [row["value"] for row in series["seeds"]]
    assert len(values) == 3 and all(math.isfinite(v) for v in values)
    assert close(series["mean"], statistics.mean(values))
    assert close(series["range"][0], min(values)) and close(series["range"][1], max(values))


def build_payload():
    paths = {
        "main": source_path("main_study_freeze_2026-11-03", "final_evaluation/RESULTS.json"),
        "main_audit": source_path("main_study_freeze_2026-11-03", "independent_audit/RESULTS.json"),
        "historical": source_path("information_revision_ablation_2026-11-03", "COMPLETE_RESULTS.json"),
        "historical_audit": source_path("information_revision_ablation_2026-11-03", "INDEPENDENT_RECOMPUTE.json"),
    }
    assert sha(paths["main"]) == MAIN_SHA and sha(paths["historical"]) == HISTORY_SHA
    result, audit, historical, haudit = (load(paths[key]) for key in ("main", "main_audit", "historical", "historical_audit"))
    assert audit["status"] == "matched" and audit["result_sha256"] == MAIN_SHA
    assert haudit["status"] == "pass" and haudit["report_sha256"] == HISTORY_SHA
    assert result["unique_successful_table_contents"] == result["complete_analysis_slots"] == 72
    panels = []
    ordered = [(arm, f"A{i:02d}") for arm in ("E0", "E1") for i in range(1, 6)] + [("E0", "S01"), ("E1", "S01")]
    for case, definitions in MAIN_DEFINITIONS.items():
        for endpoint, predictor, adjustment, unit in definitions:
            ref = result["references"][case][endpoint]
            panel = {"panel": chr(65 + len(panels)), "case": case, "endpoint": endpoint,
                     "predictor": predictor, "adjustment": adjustment, "display_unit": unit,
                     "reference": ref, "reference_pointer": f"/references/{case}/{endpoint}", "series": []}
            for arm, author in ordered:
                identity = f"{case}_{arm}_{author}"
                summaries = [(i, item) for i, item in enumerate(result["construction_summaries"]) if item["constructor_id"] == identity]
                assert len(summaries) == 1
                si, summary = summaries[0]
                endpoints = [(i, item) for i, item in enumerate(summary["endpoints"]) if item["id"] == endpoint]
                assert len(endpoints) == 1
                ei, effect = endpoints[0]
                assert effect["complete"]
                series = {"constructor": identity, "label": arm + " " + author, "condition": arm,
                          "kind": summary["constructor_kind"], "mean": effect["mean_effect"],
                          "range": effect["seed_effect_range"],
                          "summary_pointer": f"/construction_summaries/{si}/endpoints/{ei}", "seeds": []}
                for ri, row in enumerate(result["all_scheduled_slots"]):
                    if row["constructor_id"] != identity:
                        continue
                    matches = [(i, e) for i, e in enumerate(row["analyses"]) if e["id"] == endpoint]
                    assert len(matches) == 1 and row["analysis_status"] == "complete"
                    ai, item = matches[0]
                    series["seeds"].append({"seed": row["seed"], "value": item["value"],
                                            "pointer": f"/all_scheduled_slots/{ri}/analyses/{ai}/value"})
                series["seeds"].sort(key=lambda row: row["seed"])
                assert [x["seed"] for x in series["seeds"]] == [5101, 5102, 5103]
                validate_series(series)
                panel["series"].append(series)
            panels.append(panel)
    hpanels = []
    for endpoint, predictor, adjustment, label in HISTORY_DEFINITIONS:
        panel = {"panel": chr(65 + len(hpanels)), "endpoint": endpoint, "predictor": predictor,
                 "adjustment": adjustment, "axis_label": label, "series": []}
        for constructor in ("L01", "L02", "L03", "R01", "R02", "R03"):
            matched = [(i, row) for i, row in enumerate(historical["constructor_stage_statistics"])
                       if row["constructor"] == constructor and row["stage"] == "final" and row["id"] == endpoint]
            assert len(matched) == 1
            index, row = matched[0]
            assert row["n_successful_seeds"] == 3
            series = {"constructor": constructor, "label": constructor, "condition": constructor[0], "kind": "agent",
                      "mean": row["mean"], "range": row["range"],
                      "summary_pointer": f"/constructor_stage_statistics/{index}",
                      "seeds": [{"seed": seed, "value": row["seed_values"][str(seed)],
                                 "pointer": f"/constructor_stage_statistics/{index}/seed_values/{seed}"} for seed in (4101, 4102, 4103)]}
            validate_series(series)
            if "reference" in panel:
                assert close(panel["reference"]["value"], row["reference"])
            panel["series"].append(series)
            if constructor == "L01":
                panel["reference"] = {"value": row["reference"], "interval": None}
                panel["reference_pointer"] = f"/constructor_stage_statistics/{index}/reference"
                if endpoint in ("E1", "E2", "E3"):
                    runs = [(i, r) for i, r in enumerate(historical["runs"]) if r["constructor"] == constructor
                            and r["stage"] == "final" and r["purpose"] == "delivery" and r["seed"] == 4101]
                    assert len(runs) == 1
                    ri, run = runs[0]
                    items = [(i, item) for i, item in enumerate(run["statistics"]["analyses"]) if item["id"] == endpoint]
                    assert len(items) == 1
                    ai, item = items[0]
                    assert close(item["reference"], row["reference"])
                    panel["reference"]["interval"] = item["reference_interval"]
                    panel["interval_pointer"] = f"/runs/{ri}/statistics/analyses/{ai}/reference_interval"
        hpanels.append(panel)
    assert len(panels) == 6 and sum(len(s["seeds"]) for panel in panels for s in panel["series"]) == 216
    assert len(hpanels) == 5 and sum(len(s["seeds"]) for panel in hpanels for s in panel["series"]) == 90
    return {"purpose": "Publication display derivative of immutable aggregate results; no new scientific evaluation.",
            "sources": {key: {"path": str(path.relative_to(PROJECT)).replace('\\', '/'), "sha256": sha(path)} for key, path in paths.items()},
            "main_experiment": {"case_count": 2, "constructors": 24, "agent_constructors": 20, "final_tables": 72,
                                "seed_ids": [5101, 5102, 5103], "n_per_table": 3000, "panels": panels},
            "historical_information_experiment": {"case_count": 1, "constructors": 6, "final_tables": 18,
                                                  "seed_ids": [4101, 4102, 4103], "n_per_table": 3000,
                                                  "reference_sha256": historical["reference_sha256"], "panels": hpanels},
            "interpretation": {"main": "External-literature E0/E1 development comparison, all six primary endpoints.",
                               "historical": "Separate historical L/R development experiment; R receives all 30 target summaries, including plotted effects and correlations. Final stages only.",
                               "uncertainty": "Seed ranges are not CIs. CHNS reference shading is a community-cluster CR1-t 95% interval; ENSANUT shading is an empirical cluster-resampling stability band for its equal-cell standard.",
                               "no_pooling": "No inferential pooling, cross-protocol causal contrasts or selection of best authors.",
                               "custom_statistical_supplement": "Not plotted here; retained in its separate published supplementary results."}}


def axes_style(ax, panel, ys):
    ref = panel["reference"]
    interval = ref.get("interval")
    if interval is not None:
        ax.axvspan(interval["lower"], interval["upper"], color="#B4BEC7", alpha=.30, linewidth=0, zorder=0)
    ax.axvline(ref["value"], color="#263647", linewidth=1, zorder=1)
    ax.axvline(0, color="#A5ADB5", linestyle=":", linewidth=.65, zorder=0)
    all_values = [0, ref["value"]] + [point["value"] for series in panel["series"] for point in series["seeds"]]
    if interval is not None:
        all_values += [interval["lower"], interval["upper"]]
    low, high = min(all_values), max(all_values)
    padding = max((high - low) * .065, 1e-6)
    ax.set_xlim(low - padding, high + padding)
    ax.set_ylim(max(ys) + .65, min(ys) - .65)
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.ticklabel_format(axis="x", style="plain", useOffset=False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#E5E9ED", linewidth=.5, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#C5CCD3")


def draw_series(ax, series, y):
    if series["kind"] == "statistical":
        color, marker, size = COLORS["statistical"], "D", 23
    else:
        color = COLORS["basic"] if series["condition"] in ("E0", "L") else COLORS["relational"]
        marker, size = "|", 62
    ax.hlines(y, series["range"][0], series["range"][1], color=color, linewidth=1.1, zorder=2)
    for j, point in enumerate(series["seeds"]):
        ax.scatter(point["value"], y + (j - 1) * .15, s=11, color=color, alpha=.60, edgecolors="none", zorder=3)
    ax.scatter(series["mean"], y, s=size, marker=marker, color=color, linewidths=1.5, zorder=4)


def shared_legend(main):
    labels = ("E0: marginal/basic evidence", "E1: additional relations") if main else ("L: external literature", "R: literature + target summaries")
    handles = [Line2D([0], [0], color=COLORS["basic"], marker="o", linestyle="", markersize=4, label=labels[0]),
               Line2D([0], [0], color=COLORS["relational"], marker="o", linestyle="", markersize=4, label=labels[1]),
               Line2D([0], [0], color="#263647", linewidth=1, label="Sample-reference estimate"),
               Patch(facecolor="#B4BEC7", alpha=.30, label="Reference uncertainty"),
               Line2D([0], [0], color="#6C7782", marker="o", linestyle="", alpha=.6, markersize=3, label="Individual final seed"),
               Line2D([0], [0], color="#6C7782", marker="|", linestyle="", markersize=7, label="Agent constructor mean"),
               Line2D([0], [0], color="#6C7782", linewidth=1.1, label="Seed minimum–maximum")]
    if main:
        handles.append(Line2D([0], [0], color=COLORS["statistical"], marker="D", linestyle="", markersize=4, label="Prescribed statistical mean"))
    return handles


def save_figure(fig, name):
    folder = HERE / "figures"
    folder.mkdir(exist_ok=True)
    for extension in ("png", "svg"):
        fig.savefig(folder / f"{name}.{extension}", dpi=360, facecolor="white")
    plt.close(fig)


def plot_main(payload):
    panels = payload["main_experiment"]["panels"]
    fig, axes = plt.subplots(2, 3, figsize=(190 / 25.4, 200 / 25.4), sharey="row")
    fig.subplots_adjust(left=.14, right=.985, bottom=.19, top=.88, hspace=.50, wspace=.26)
    ys = [0, 1, 2, 3, 4, 5.5, 6.5, 7.5, 8.5, 9.5, 11.2, 12.2]
    for index, (ax, panel) in enumerate(zip(axes.flat, panels)):
        axes_style(ax, panel, ys)
        for y, series in zip(ys, panel["series"]):
            draw_series(ax, series, y)
        ax.set_yticks(ys, [series["label"] for series in panel["series"]])
        if index % 3:
            ax.tick_params(labelleft=False)
        case = "CHNS 2009" if panel["case"] == "CHNS2009" else "ENSANUT 2018"
        ax.set_title(f"{panel['panel']}  {case} · {panel['predictor']}\nAdjusted: {panel['adjustment']}", loc="left", pad=7)
        ax.set_xlabel("HbA1c percentage points\n" + panel["display_unit"], labelpad=4)
        for boundary in (4.75, 10.35):
            ax.axhline(boundary, color="#D6DDE3", linewidth=.6)
    fig.suptitle("Scientific analyses of evidence-generated cohorts", x=.14, ha="left", y=.985, fontsize=11, fontweight="bold", color="#1C3042")
    fig.text(.14, .947, "Main experiment · all six prespecified effects · all constructions and final seeds", fontsize=7.5, color="#526575")
    fig.legend(handles=shared_legend(True), loc="lower center", bbox_to_anchor=(.55, .052), ncol=3,
               frameon=False, fontsize=6.5, columnspacing=1.2, handlelength=1.7)
    fig.text(.14, .017, "Seed ranges are not confidence intervals. Reference shading is case-specific uncertainty, not an acceptance region.", fontsize=6.2, color="#526575")
    save_figure(fig, "figure1_main_scientific_utility")


def plot_history(payload):
    panels = payload["historical_information_experiment"]["panels"]
    fig, axes = plt.subplots(2, 3, figsize=(190 / 25.4, 155 / 25.4))
    fig.subplots_adjust(left=.11, right=.985, bottom=.22, top=.875, hspace=.66, wspace=.30)
    ys = [0, 1, 2, 3.5, 4.5, 5.5]
    for ax, panel in zip(axes.flat, panels):
        axes_style(ax, panel, ys)
        for y, series in zip(ys, panel["series"]):
            draw_series(ax, series, y)
        ax.set_yticks(ys, [series["label"] for series in panel["series"]])
        ax.set_title(f"{panel['panel']}  {panel['predictor']}\n" + ("Adjusted: " if panel["endpoint"] in ("E1", "E2", "E3") else "") + panel["adjustment"], loc="left", pad=7)
        ax.set_xlabel(panel["axis_label"], labelpad=4)
        ax.axhline(2.75, color="#D6DDE3", linewidth=.6)
    text_ax = axes[1, 2]
    text_ax.axis("off")
    text_ax.text(0, .98, "Separate information\nexperiment", transform=text_ax.transAxes,
                 fontsize=8, fontweight="bold", va="top", color="#1C3042")
    text_ax.text(0, .76,
                 "L: external literature\nR: L + 30 target summaries\n\n3 authors per condition\n3 final seeds per author\n3,000 rows per table\n\nR tests supplied-summary\ncalibration. Authors are separate\nfrom the main E0/E1 experiment.",
                 transform=text_ax.transAxes, fontsize=7.2, linespacing=1.45, va="top", color="#526575")
    fig.suptitle("Scientific use with and without target summaries", x=.11, ha="left", y=.985, fontsize=11, fontweight="bold", color="#1C3042")
    fig.text(.11, .947, "Historical CHNS experiment · final stages of all six Agent constructions", fontsize=7.5, color="#526575")
    fig.legend(handles=shared_legend(False), loc="lower center", bbox_to_anchor=(.54, .065), ncol=3,
               frameon=False, fontsize=6.5, columnspacing=1.1, handlelength=1.7)
    fig.text(.11, .020, "All displayed R statistics were supplied for calibration. Correlation reference intervals were unavailable; none are added.", fontsize=6.2, color="#526575")
    save_figure(fig, "figure2_chns_information_conditions")


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.titlesize": 8,
                         "axes.labelsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7,
                         "svg.fonttype": "none", "svg.hashsalt": "evidence-guided-utility-2026-11-03"})
    payload = build_payload()
    source = HERE / "AGGREGATE_SOURCE.json"
    source.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    plot_main(payload)
    plot_history(payload)
    outputs = [source, HERE / "CAPTIONS.md", *sorted((HERE / "figures").glob("*"))]
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(),
                "activity": "Plot-only aggregation of retained reports; zero patient/generated-row reads, fits or scientific evaluations.",
                "script_sha256": sha(Path(__file__)), "sources": payload["sources"],
                "plotted_values": {"main_seed_values": 216, "main_constructor_means": 72,
                                   "historical_seed_values": 90, "historical_constructor_means": 30,
                                   "total_seed_values": 306, "total_mean_markers": 102},
                "source_pointers": "Every seed, mean/range and reference in AGGREGATE_SOURCE.json records its originating JSON pointer.",
                "figures": {"figure1_main_scientific_utility": {"panels": 6, "width_mm": 190, "height_mm": 200,
                                                               "source": "main", "reference_uncertainty": "CHNS CR1-t 95% interval; ENSANUT equal-cell empirical stability band."},
                            "figure2_chns_information_conditions": {"data_panels": 5, "width_mm": 190, "height_mm": 155,
                                                                    "source": "historical", "reference_uncertainty": "CHNS CR1-t 95% intervals for regressions; none for correlations."}},
                "outputs": {str(path.relative_to(HERE)).replace('\\', '/'): {"sha256": sha(path), "bytes": path.stat().st_size} for path in outputs},
                "inferential_pooling": False, "new_reference_or_generator_evaluations": 0,
                "limitations": payload["interpretation"]}
    (HERE / "NUMERIC_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"figures": 2, "seed_values": 306, "mean_markers": 102, "new_scientific_evaluations": 0}))


if __name__ == "__main__":
    main()
