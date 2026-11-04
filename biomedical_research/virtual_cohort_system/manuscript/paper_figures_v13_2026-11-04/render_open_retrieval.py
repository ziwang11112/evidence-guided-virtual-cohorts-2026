"""Draw Figure 5 from frozen aggregate results; no generation or participant reads.

Usage: python manuscript/paper_figures_v13_2026-11-04/render_open_retrieval.py
All six prespecified analyses, four authors and twelve final tables are retained.
The validation below compares stored summaries with the individual aggregate
estimates and independently formatted ALL_ENDPOINTS.csv; it does not refit data.
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
EVAL = BATCH / "evaluation_v2"
INPUTS = {
    "evaluation_v2/RESULTS.json": "61994088354f290a3e7f6f6b85aac71498e6892093c71167cc021ea2722658ca",
    "evaluation_v2/ALL_ENDPOINTS.csv": "35f0dc5eae4d64be8ed292e0121ce3c30b977c8e48ceaf132c8409aa8b909d40",
    "evaluation_v2/EVALUATION_COMPLETED.json": "1ace017e9ed11c08a44b727682bd3085f3cdce0b4318c69c60948d44902c879a",
    "ENDPOINT_CONTRACT.json": "b35b3a681b716eeb258ed56234e5ad694a01e30ceb3243fb9f7b7bfa6f73fdbf",
}
NAVY, BLUE, PURPLE, CORAL = "#182647", "#4169B1", "#8264B5", "#CF725E"
SLATE, GRID = "#5F6979", "#E8EBF0"
PANELS = [
    dict(case="CHNS2009", endpoint="E1", title="BMI association", adjustment="Age/sex adjusted",
         unit="HbA1c pp per kg/m²", ticks=[0, .02, .04, .06], xmax=.071),
    dict(case="CHNS2009", endpoint="E2", title="Glucose association", adjustment="Age/sex adjusted",
         unit="HbA1c pp per mmol/L", ticks=[0, .2, .4], xmax=.55),
    dict(case="CHNS2009", endpoint="E3", title="Age association", adjustment="Sex/BMI/glucose adjusted",
         unit="HbA1c pp per year", ticks=[0, .005, .010], xmax=.0108),
    dict(case="ENSANUT2018", endpoint="Q1_age10", title="Age association", adjustment="Sex/BMI/glucose adjusted",
         unit="HbA1c pp per 10 years", ticks=[0, .04, .08, .12], xmax=.124),
    dict(case="ENSANUT2018", endpoint="Q2_bmi5", title="BMI association", adjustment="Age/sex adjusted",
         unit="HbA1c pp per 5 kg/m²", ticks=[0, .04, .08], xmax=.105),
    dict(case="ENSANUT2018", endpoint="Q3_bmi5", title="BMI association", adjustment="Age/sex/glucose adjusted",
         unit="HbA1c pp per 5 kg/m²", ticks=[0, .04, .08], xmax=.105),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def same(a, b):
    assert math.isclose(a, b, rel_tol=1e-13, abs_tol=1e-15), (a, b)


def write_csv(path, records):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main():
    for relative, expected in INPUTS.items():
        assert sha(BATCH / relative) == expected, relative
    data = read_json(EVAL / "RESULTS.json")
    contract = read_json(BATCH / "ENDPOINT_CONTRACT.json")
    completed = read_json(EVAL / "EVALUATION_COMPLETED.json")
    for name, digest in completed["outputs"].items():
        assert sha(EVAL / name) == digest, name
    slots = data["all_final_slots"]
    assert len(slots) == 12 and len({s["table_sha256"] for s in slots}) == 12
    assert {s["author_id"] for s in slots} == {"C01", "C02", "E01", "E02"}
    assert all(s["analysis_status"] == "complete" and s["execution_status"] == "success" for s in slots)
    assert all(s["n"] == 3000 and s["scheduled"] and s["output_route"] == "generator.py" for s in slots)
    assert data["new_clinical_reads_or_fits"] is False
    expected_endpoints = {(case, item["id"]) for case, body in contract["cases"].items() for item in body["analyses"]}
    assert {(p["case"], p["endpoint"]) for p in PANELS} == expected_endpoints
    with (EVAL / "ALL_ENDPOINTS.csv").open(newline="", encoding="utf-8") as stream:
        all_csv = list(csv.DictReader(stream))
    # Verify every aggregate CSV estimate, including the retained diagnostics.
    slot_lookup = {(s["author_id"], s["seed"]): s for s in slots}
    for csv_row in all_csv:
        slot = slot_lookup[(csv_row["author_id"], int(csv_row["seed"]))]
        item = next(x for x in slot[csv_row["category"]] if x["id"] == csv_row["endpoint"])
        assert csv_row["case_id"] == slot["case_id"] and csv_row["unit"] == item["unit"]
        same(float(csv_row["generated_value"]), item["value"])
        same(float(csv_row["reference_value"]), item["reference"]["value"])
    csv_primary = {(r["author_id"], int(r["seed"]), r["endpoint"]): r for r in all_csv if r["category"] == "analyses"}
    assert len(all_csv) == 366 and len(csv_primary) == 36

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8.4,
        "axes.labelsize": 8.4, "axes.titlesize": 9.1,
        "xtick.labelsize": 8.3, "ytick.labelsize": 8.4,
        "text.color": NAVY, "axes.labelcolor": NAVY,
        "xtick.color": SLATE, "ytick.color": NAVY,
        "svg.fonttype": "none", "pdf.fonttype": 42,
        "svg.hashsalt": "fig5-open-retrieval-v13-2026-11-04",
    })
    fig = plt.figure(figsize=(7.2, 4.45), facecolor="white")
    fig.text(.018, .985, "4 Agent-authored laws  ·  12 final tables  ·  3,000 virtual rows per table",
             va="top", fontsize=9.0, color=NAVY)
    for title, y, uncertainty in [
        ("CHNS 2009", .920, "Reference: community-cluster 95% CI"),
        ("ENSANUT 2018", .470, "Reference: cluster-resampling stability band"),
    ]:
        fig.text(.018, y, title, va="center", fontsize=10, fontweight="bold")
        fig.text(.350, y, uncertainty, va="center", fontsize=8.4, color=SLATE)

    seed_rows, summary_rows, panels = [], [], []
    axes = []
    for i, spec in enumerate(PANELS):
        row, col = divmod(i, 3)
        x, bottom, width, height = [.075, .410, .745][col], [.585, .145][row], .238, .205
        ax = fig.add_axes([x, bottom, width, height])
        axes.append(ax)
        top = bottom + height
        fig.text(x-.010, top+.072, f"{chr(97+i)}  {spec['title']}", fontsize=9.1, fontweight="bold")
        fig.text(x-.010, top+.035, spec["adjustment"], fontsize=8.3, color=SLATE)
        rows = sorted([r for r in data["all_author_endpoint_summaries"]
                       if r["case_id"] == spec["case"] and r["endpoint"] == spec["endpoint"]],
                      key=lambda r: r["author_id"])
        assert len(rows) == 2
        ref = rows[0]["reference"]
        assert ref == rows[1]["reference"]
        band = ref["interval"]
        assert band["lower"] <= ref["value"] <= band["upper"]
        assert band["equivalence_margin"] is False
        for j, (r, color) in enumerate(zip(rows, [BLUE, PURPLE])):
            selected = sorted([s for s in slots if s["author_id"] == r["author_id"]], key=lambda s: s["seed"])
            assert [s["seed"] for s in selected] == [8101, 8102, 8103]
            points = [next(a for a in s["analyses"] if a["id"] == spec["endpoint"]) for s in selected]
            values = [a["value"] for a in points]
            same(mean(values), r["slot_mean"])
            same(min(values), r["slot_range"][0])
            same(max(values), r["slot_range"][1])
            assert all(a["reference"] == ref for a in points)
            assert all(0 < v < spec["xmax"] for v in values)
            y = 2.32 - j*1.05
            # Separate seed points vertically and place the mean/range just below.
            # All estimates remain on their exact horizontal coordinates.
            seed_y = [y+.16, y, y-.16]
            mean_y = y-.34
            ax.scatter(values, seed_y, s=13, marker="o", facecolor="white",
                       edgecolor=color, linewidth=.9, zorder=5)
            ax.plot(r["slot_range"], [mean_y, mean_y], color=color, linewidth=1.35, zorder=3)
            ax.scatter([r["slot_mean"]], [mean_y], s=17, marker="D", color=color, zorder=4)
            for s, a in zip(selected, points):
                csv_row = csv_primary[(s["author_id"], s["seed"], a["id"])]
                assert csv_row["case_id"] == spec["case"] and csv_row["unit"] == a["unit"]
                same(float(csv_row["generated_value"]), a["value"])
                same(float(csv_row["reference_value"]), ref["value"])
                seed_rows.append(dict(panel=chr(97+i), case=spec["case"], endpoint=a["id"],
                                      author=s["author_id"], seed=s["seed"], value=a["value"],
                                      original_unit=a["unit"], displayed_unit=spec["unit"],
                                      reference=ref["value"], table_sha256=s["table_sha256"]))
            summary_rows.append(dict(panel=chr(97+i), case=spec["case"], endpoint=spec["endpoint"],
                                     author=r["author_id"], mean=r["slot_mean"], seed_min=min(values),
                                     seed_max=max(values), reference=ref["value"], reference_lower=band["lower"],
                                     reference_upper=band["upper"], displayed_unit=spec["unit"],
                                     adjustment=spec["adjustment"], reference_interval_meaning=band["meaning"]))
        linestyle = "-" if row == 0 else (0, (2.0, 1.3))
        ax.plot([band["lower"], band["upper"]], [.08, .08], color=CORAL, lw=1.4, ls=linestyle, zorder=3)
        ax.plot([band["lower"], band["lower"]], [-.04, .20], color=CORAL, lw=1.0)
        ax.plot([band["upper"], band["upper"]], [-.04, .20], color=CORAL, lw=1.0)
        ax.scatter([ref["value"]], [.08], color=CORAL, marker="s", s=18, zorder=4)
        ax.axvline(0, color="#AEB6C2", lw=.7, zorder=1)
        ax.grid(axis="x", color=GRID, lw=.6, zorder=0)
        ax.set_axisbelow(True)
        ax.set_xlim(-spec["xmax"]*.025, spec["xmax"])
        ax.set_ylim(-.25, 2.70)
        ax.set_xticks(spec["ticks"])
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, pos: "0" if abs(v)<1e-14 else f"{v:g}"))
        ax.set_yticks([2.20, 1.15, .08], [rows[0]["author_id"], rows[1]["author_id"], "Ref."])
        for tick, color in zip(ax.get_yticklabels(), [BLUE, PURPLE, CORAL]):
            tick.set_color(color)
        ax.tick_params(axis="y", length=0, pad=3)
        ax.tick_params(axis="x", length=2.5, pad=3)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#AEB6C2")
        ax.spines["bottom"].set_linewidth(.6)
        ax.set_xlabel(spec["unit"], labelpad=3)
        panels.append(dict(**spec, reference=ref, x_limits=list(ax.get_xlim()),
                           seed_mean_range_is_confidence_interval=False))

    legend = [Line2D([], [], marker="o", markersize=3.8, markerfacecolor="white", color=SLATE,
                     lw=0, label="Three seeds"),
              Line2D([], [], marker="D", markersize=3.8, color=SLATE, lw=1.25, label="Mean + seed range"),
              Line2D([], [], marker="s", markersize=3.8, color=CORAL, lw=1.25, label="Sample reference + interval")]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5, -.004), ncol=3,
               frameon=False, fontsize=8.3, handlelength=1.9, columnspacing=1.4)
    assert len(seed_rows) == 36 and len(summary_rows) == 12
    assert len({r["table_sha256"] for r in seed_rows}) == 12
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    # The quantitative elements stay in bounds; endpoint sets and exact values
    # above are the substantive coverage check. This is layout QA only.
    texts = [t for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]
    for t in texts:
        assert t.get_fontsize() >= 8.3, t.get_text()
        extent = t.get_window_extent(renderer)
        assert extent.x0 >= -1 and extent.x1 <= fig.bbox.width + 1, t.get_text()
        assert extent.y0 >= -1 and extent.y1 <= fig.bbox.height + 1, t.get_text()

    outputs = {}
    for extension in ("svg", "pdf", "png"):
        path = HERE / f"fig5-open-retrieval.{extension}"
        metadata = {"Date": None} if extension == "svg" else ({"CreationDate": None, "ModDate": None} if extension == "pdf" else {})
        fig.savefig(path, dpi=300, facecolor="white", metadata=metadata)
        outputs[path.name] = dict(sha256=sha(path), bytes=path.stat().st_size)
    plt.close(fig)
    write_csv(HERE / "FIG5_SEED_VALUES.csv", seed_rows)
    write_csv(HERE / "FIG5_AUTHOR_SUMMARIES.csv", summary_rows)
    binding = dict(schema_version="paper_figure5_aggregate_bindings_v13", dimensions_inches=[7.2, 4.45],
                   minimum_font_points=8.3, minimum_font_at_7_06_inches=8.3*7.06/7.2,
                   input_sha256=INPUTS, builder_sha256=sha(Path(__file__)), aggregate_inputs_only=True,
                   new_generation=False, new_clinical_reads_or_fits=False,
                   coverage=dict(panels=6, authors=4, final_tables=12, primary_seed_estimates=36,
                                 author_endpoint_summaries=12, diagnostic_seed_estimates_not_plotted=330,
                                 aggregate_csv_estimates_verified=366, primary_csv_crosschecks=36),
                   seed_order_top_to_bottom=[8101, 8102, 8103], panels=panels,
                   seed_values=seed_rows, author_summaries=summary_rows,
                   interpretation="Three seeds describe sampling under each frozen law; not confidence intervals, independent clinical replication, or transport uncertainty.",
                   outputs=outputs)
    for name in ["FIG5_SEED_VALUES.csv", "FIG5_AUTHOR_SUMMARIES.csv"]:
        binding["outputs"][name] = dict(sha256=sha(HERE / name), bytes=(HERE / name).stat().st_size)
    (HERE / "FIG5_NUMERIC_BINDINGS.json").write_text(json.dumps(binding, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "coverage": binding["coverage"], "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
