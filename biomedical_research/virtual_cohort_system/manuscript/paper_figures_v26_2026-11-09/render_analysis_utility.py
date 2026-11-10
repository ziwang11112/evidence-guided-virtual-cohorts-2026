"""Figure 3: all primary analyses from the frozen open-evidence replication.

Reads aggregate results, the aggregate endpoint CSV and endpoint metadata only.
Never opens participant/generated row tables, imports generators, refits models
or creates additional scientific results. Run from any working directory.
"""
from pathlib import Path
from statistics import mean
import csv
import hashlib
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
BATCH = PROJECT / "work/core_workflow_replication_2026-11-04"
if not BATCH.exists():
    BATCH = PROJECT / "reports/core_workflow_replication_2026-11-04"
EVAL = BATCH / "evaluation_v2"
EXPECTED_HASHES = {
    "evaluation_v2/RESULTS.json": "61994088354f290a3e7f6f6b85aac71498e6892093c71167cc021ea2722658ca",
    "evaluation_v2/ALL_ENDPOINTS.csv": "35f0dc5eae4d64be8ed292e0121ce3c30b977c8e48ceaf132c8409aa8b909d40",
    "evaluation_v2/EVALUATION_COMPLETED.json": "1ace017e9ed11c08a44b727682bd3085f3cdce0b4318c69c60948d44902c879a",
    "ENDPOINT_CONTRACT.json": "b35b3a681b716eeb258ed56234e5ad694a01e30ceb3243fb9f7b7bfa6f73fdbf",
}
NAVY = "#19334D"
BLUE = "#356BA6"
PURPLE = "#7B5AA6"
REFERENCE = "#606A77"
GRID = "#E9EDF1"
DIMENSIONS = (7.2, 4.8)
MIN_FONT = 8.5
PANELS = [
    dict(case="CHNS2009", endpoint="E1", title="BMI association",
         adjustment="Age + sex adjusted", unit="HbA1c pp per kg/m²",
         ticks=[0, .02, .04, .06], xmax=.071),
    dict(case="CHNS2009", endpoint="E2", title="Glucose association",
         adjustment="Age + sex adjusted", unit="HbA1c pp per mmol/L",
         ticks=[0, .2, .4], xmax=.55),
    dict(case="CHNS2009", endpoint="E3", title="Age association",
         adjustment="Sex + BMI + glucose adjusted", unit="HbA1c pp per year",
         ticks=[0, .005, .010], xmax=.0108),
    dict(case="ENSANUT2018", endpoint="Q1_age10", title="Age association",
         adjustment="Sex + BMI + glucose adjusted", unit="HbA1c pp per 10 years",
         ticks=[0, .04, .08, .12], xmax=.124),
    dict(case="ENSANUT2018", endpoint="Q2_bmi5", title="BMI association",
         adjustment="Age + sex adjusted", unit="HbA1c pp per 5 kg/m²",
         ticks=[0, .04, .08], xmax=.105),
    dict(case="ENSANUT2018", endpoint="Q3_bmi5", title="BMI association",
         adjustment="Age + sex + glucose adjusted", unit="HbA1c pp per 5 kg/m²",
         ticks=[0, .04, .08], xmax=.105),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def same(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-13, abs_tol=1e-15), (a, b)


def main():
    for relative, expected in EXPECTED_HASHES.items():
        assert sha(BATCH / relative) == expected, relative
    completed = read(EVAL / "EVALUATION_COMPLETED.json")
    for name, expected in completed["outputs"].items():
        assert sha(EVAL / name) == expected, name
    data = read(EVAL / "RESULTS.json")
    contract = read(BATCH / "ENDPOINT_CONTRACT.json")
    planned = {(case, item["id"]) for case, spec in contract["cases"].items()
               for item in spec["analyses"]}
    assert planned == {(p["case"], p["endpoint"]) for p in PANELS}
    slots = data["all_final_slots"]
    assert len(slots) == 12
    assert len({s["table_sha256"] for s in slots}) == 12
    assert {s["author_id"] for s in slots} == {"C01", "C02", "E01", "E02"}
    assert all(s["n"] == 3000 and s["scheduled"] and s["output_route"] == "generator.py"
               and s["analysis_status"] == "complete"
               and s["execution_status"] == "success" for s in slots)
    assert data["new_clinical_reads_or_fits"] is False
    with (EVAL / "ALL_ENDPOINTS.csv").open(encoding="utf-8", newline="") as stream:
        csv_records = list(csv.DictReader(stream))
    primary_csv = {(r["case_id"], r["author_id"], int(r["seed"]), r["endpoint"]): r
                   for r in csv_records if r["category"] == "analyses"}
    assert len(primary_csv) == 36

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": MIN_FONT,
        "axes.labelsize": MIN_FONT, "axes.titlesize": 9.2,
        "xtick.labelsize": MIN_FONT, "ytick.labelsize": MIN_FONT,
        "text.color": NAVY, "axes.labelcolor": NAVY,
        "xtick.color": REFERENCE, "ytick.color": NAVY,
        "svg.fonttype": "none", "pdf.fonttype": 42,
        "svg.hashsalt": "fig3-analysis-utility-v26-2026-11-09",
    })
    fig = plt.figure(figsize=DIMENSIONS, facecolor="white")
    fig.text(.018, .965, "CHNS 2009", fontsize=10.2, fontweight="bold", va="center")
    fig.text(.018, .505, "ENSANUT 2018", fontsize=10.2, fontweight="bold", va="center")
    records, panel_metadata, summary_metadata = [], [], []
    for index, spec in enumerate(PANELS):
        row, col = divmod(index, 3)
        x, bottom = [.075, .407, .739][col], [.617, .157][row]
        ax = fig.add_axes([x, bottom, .242, .235])
        top = bottom + .235
        fig.text(x-.010, top+.063, f"{chr(97+index)}  {spec['title']}",
                 fontsize=9.2, fontweight="bold")
        fig.text(x-.010, top+.026, spec["adjustment"],
                 fontsize=MIN_FONT, color=REFERENCE)
        summaries = sorted(
            (r for r in data["all_author_endpoint_summaries"]
             if (r["case_id"], r["endpoint"]) == (spec["case"], spec["endpoint"])),
            key=lambda r: r["author_id"])
        assert len(summaries) == 2
        reference = summaries[0]["reference"]
        assert reference == summaries[1]["reference"]
        band = reference["interval"]
        assert band["status"] == "available" and band["equivalence_margin"] is False
        assert 0 <= band["lower"] <= reference["value"] <= band["upper"] < spec["xmax"]
        if row == 0:
            assert "CR1_t" in band["meaning"] and "95%" in band["meaning"]
            interval_kind = "CHNS community-cluster CR1-t 95% interval"
        else:
            assert "empirical" in band["meaning"] and "399" in band["meaning"]
            interval_kind = "ENSANUT empirical cluster-resampling stability band"
        for order, (summary, color) in enumerate(zip(summaries, [BLUE, PURPLE])):
            selected = sorted((s for s in slots if s["author_id"] == summary["author_id"]),
                              key=lambda s: s["seed"])
            assert [s["seed"] for s in selected] == [8101, 8102, 8103]
            analyses = [next(a for a in s["analyses"] if a["id"] == spec["endpoint"])
                        for s in selected]
            values = [a["value"] for a in analyses]
            same(mean(values), summary["slot_mean"])
            same(min(values), summary["slot_range"][0])
            same(max(values), summary["slot_range"][1])
            assert all(a["reference"] == reference and a["unit"] == summary["unit"]
                       for a in analyses)
            assert all(0 < value < spec["xmax"] for value in values)
            y = 2.40 - order*1.10
            seed_y = [y+.15, y, y-.15]
            mean_y = y-.36
            ax.scatter(values, seed_y, s=14, marker="o", facecolor="white",
                       edgecolor=color, linewidth=.95, zorder=5)
            ax.plot([min(values), max(values)], [mean_y, mean_y],
                    color=color, linewidth=1.45, zorder=3)
            ax.scatter([mean(values)], [mean_y], s=18, marker="D", color=color, zorder=4)
            for slot, analysis, ordinate in zip(selected, analyses, seed_y):
                csv_record = primary_csv[(spec["case"], slot["author_id"], slot["seed"], analysis["id"])]
                same(csv_record["generated_value"], analysis["value"])
                same(csv_record["reference_value"], reference["value"])
                assert csv_record["unit"] == analysis["unit"]
                records.append(dict(
                    panel=chr(97+index), case=spec["case"], endpoint=analysis["id"],
                    author=slot["author_id"], seed=slot["seed"],
                    generated_value=analysis["value"], author_mean=mean(values),
                    seed_min=min(values), seed_max=max(values),
                    reference_value=reference["value"], reference_lower=band["lower"],
                    reference_upper=band["upper"], original_unit=analysis["unit"],
                    displayed_unit=spec["unit"], adjustment=spec["adjustment"],
                    reference_interval_kind=interval_kind,
                    reference_interval_meaning=band["meaning"],
                    seed_plot_y=ordinate, author_mean_plot_y=mean_y,
                    table_sha256=slot["table_sha256"]))
            summary_metadata.append(dict(
                case=spec["case"], endpoint=spec["endpoint"], author=summary["author_id"],
                mean=mean(values), minimum=min(values), maximum=max(values),
                seed_count=len(values)))
        # Different line types retain the distinction between the two interval constructions.
        reference_style = "-" if row == 0 else (0, (2.1, 1.3))
        ax.plot([band["lower"], band["upper"]], [.10, .10],
                color=REFERENCE, linewidth=1.45, linestyle=reference_style, zorder=3)
        ax.plot([band["lower"], band["lower"]], [-.02, .22], color=REFERENCE, lw=1)
        ax.plot([band["upper"], band["upper"]], [-.02, .22], color=REFERENCE, lw=1)
        ax.scatter([reference["value"]], [.10], s=19, marker="s",
                   color=REFERENCE, zorder=4)
        ax.axvline(0, color="#ADB6C2", lw=.8, zorder=1)
        ax.grid(axis="x", color=GRID, lw=.65, zorder=0)
        ax.set_axisbelow(True)
        ax.set_xlim(-spec["xmax"]*.025, spec["xmax"])
        ax.set_ylim(-.25, 2.78)
        ax.set_xticks(spec["ticks"])
        ax.xaxis.set_major_formatter(FuncFormatter(
            lambda value, position: "0" if abs(value) < 1e-14 else f"{value:g}"))
        ax.set_yticks([2.27, 1.17, .10],
                     [summaries[0]["author_id"], summaries[1]["author_id"], "Ref."])
        for label, color in zip(ax.get_yticklabels(), [BLUE, PURPLE, REFERENCE]):
            label.set_color(color)
        ax.tick_params(axis="y", length=0, pad=3)
        ax.tick_params(axis="x", length=2.5, pad=3)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#ADB6C2")
        ax.spines["bottom"].set_linewidth(.65)
        ax.set_xlabel(spec["unit"], labelpad=3)
        panel_metadata.append(dict(
            panel=chr(97+index), **spec, reference=reference,
            interval_kind=interval_kind, reference_line_style=reference_style,
            x_limits=list(ax.get_xlim()), zero_visible=True))
    legend = [
        Line2D([], [], marker="o", markersize=3.8, markerfacecolor="white",
               color=REFERENCE, lw=0, label="Three seeds"),
        Line2D([], [], marker="D", markersize=3.8, color=REFERENCE,
               lw=1.3, label="Mean + seed range"),
        Line2D([], [], marker="s", markersize=3.8, color=REFERENCE,
               lw=1.3, label="Reference + interval"),
    ]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5, .014),
               ncol=3, frameon=False, fontsize=MIN_FONT,
               handlelength=1.85, columnspacing=1.6)
    assert len(records) == 36 and len(summary_metadata) == 12
    assert len({r["table_sha256"] for r in records}) == 12
    assert {(r["case"], r["author"], r["seed"], r["endpoint"]) for r in records} == set(primary_csv)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    out_of_bounds = []
    for text in fig.findobj(matplotlib.text.Text):
        if not text.get_visible() or not text.get_text():
            continue
        assert text.get_fontsize() >= MIN_FONT
        extent = text.get_window_extent(renderer)
        if (extent.x0 < -1 or extent.x1 > fig.bbox.width+1
                or extent.y0 < -1 or extent.y1 > fig.bbox.height+1):
            out_of_bounds.append(text.get_text())
    assert not out_of_bounds, out_of_bounds
    outputs = {}
    for extension in ("png", "svg", "pdf"):
        target = HERE / f"fig3-analysis-utility.{extension}"
        metadata = {"Date": None} if extension == "svg" else (
            {"CreationDate": None, "ModDate": None} if extension == "pdf" else {})
        fig.savefig(target, dpi=300, facecolor="white", metadata=metadata)
        outputs[target.name] = {"sha256": sha(target), "bytes": target.stat().st_size}
    plt.close(fig)
    csv_path = HERE / "FIGURE_DATA.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    outputs[csv_path.name] = {"sha256": sha(csv_path), "bytes": csv_path.stat().st_size}
    qa = dict(
        figure="Figure 3", schema_version="v26_analysis_utility_figure_qa",
        aggregate_inputs_only=True, generated_or_patient_rows_read=False,
        new_clinical_analysis=False, new_generation=False,
        dimensions_inches=list(DIMENSIONS), png_dimensions_pixels=[2160,1440],
        png_dpi=300, minimum_font_points=MIN_FONT,
        palette={"navy":NAVY, "construction_1":BLUE, "construction_2":PURPLE,
                 "reference":REFERENCE, "grid":GRID},
        input_hashes=EXPECTED_HASHES, renderer_sha256=sha(Path(__file__)),
        coverage={"case_requests":2, "panels":6, "scientific_authors":4,
                  "frozen_tables":12, "seed_estimates":36,
                  "author_mean_range_summaries":12, "reference_points_and_intervals":6,
                  "rows_per_frozen_table":3000,
                  "unplotted_prespecified_diagnostic_estimates":330},
        numeric_checks={"all_36_seed_values_crosschecked_against_aggregate_CSV":True,
                        "all_12_means_ranges_reconciled_with_frozen_summary":True,
                        "all_references_consistent_across_authors_and_seeds":True,
                        "complete_endpoint_contract_coverage":True,
                        "all_plot_coordinates_inside_limits":True,
                        "zero_on_every_axis":True},
        layout_checks={"visible_text_out_of_bounds":out_of_bounds,
                       "minimum_font_check":True,
                       "visual_png_review":"pending",
                       "rendered_pdf_review":"pending"},
        independence_note="Seeds are repeated draws from fixed laws, not clinical replications or transport uncertainty.",
        reference_note="CHNS CR1-t 95% community-cluster intervals and ENSANUT empirical cluster-resampling stability bands have distinct meanings; neither is an equivalence or acceptance region.",
        panels=panel_metadata, author_summaries=summary_metadata, outputs=outputs)
    (HERE/"FIGURE_QA.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",
                                      encoding="utf-8")
    print(json.dumps({"status":"PASS", "coverage":qa["coverage"],
                      "dimensions_inches":qa["dimensions_inches"]},indent=2))


if __name__ == "__main__":
    main()

