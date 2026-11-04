"""Redraw two use-case figures from byte-pinned, existing aggregate results.

No records, generator execution, clinical fits, uncertainty calculation or
result selection is performed. Both local work/ and public reports/ layouts
are supported; a selected profile must match every pinned input exactly.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
CSV_PATH = "manuscript/integrated_figures_v07_2026-11-03/data/hrs_focal_plotted_values.csv"
CSV_SHA = "45f80eb1ce04a4b765e2ca4f49a3cf644aa00250ef499c293b6cbf65d310645e"
REPORT_PATH = "evidence_to_generation_2026-11-04/evaluation/REPORT.json"
REPORT_SHA = "2dfe84dca528adcc4edc6035b1f70ffbf13df72697ef82ac273344660824e2c6"
SENS_PATH = "evidence_to_generation_2026-11-04/SENSITIVITY_REVIEW.json"
SENS_SHA = "1680b49b947b64be5ccb8413b959845bb9e984982af0452b7c28b3e6081846ee"
BLUE = "#1678A6"
PURPLE = "#7E6AA2"
GRAY = "#737D86"
ORANGE = "#B55A16"
INK = "#243543"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value, _position):
    return "0" if abs(value) < 1e-12 else f"{value:.3g}".replace("-", "−")


def axis_style(ax):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#B1BAC1")
    ax.tick_params(axis="y", length=0)
    ax.xaxis.set_major_formatter(FuncFormatter(number))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=3, steps=[1, 2, 2.5, 5, 10]))


def save(fig, name):
    stem = HERE / name
    fig.savefig(stem.with_suffix(".svg"), metadata={"Date": None, "Creator": "render_use_cases.py; frozen aggregates"})
    fig.savefig(stem.with_suffix(".png"), dpi=300, metadata={"Software": "Matplotlib; frozen aggregate redraw"})
    fig.savefig(stem.with_suffix(".pdf"), metadata={"CreationDate": None, "ModDate": None,
        "Title": name, "Creator": "render_use_cases.py"})
    plt.close(fig)
    return {stem.with_suffix(ext).name: sha(stem.with_suffix(ext)) for ext in (".svg", ".png", ".pdf")}


def figure4(rows):
    terms = ["age60:hba1c_U65", "age60:hba1c_O65"]
    keys = {(r["arm"], r["seed"], r["term"]) for r in rows}
    assert keys == {(arm, seed, term) for arm in ("native", "agent")
                    for seed in (6101, 6102, 6103) for term in terms}
    assert len(rows) == 12
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.2))
    fig.subplots_adjust(left=.105, right=.985, top=.75, bottom=.23, wspace=.24)
    fig.legend(handles=[
        Line2D([], [], marker="o", color=BLUE, lw=1, markersize=3.5, label="Agent construction"),
        Line2D([], [], marker="s", color=PURPLE, lw=1, markersize=3.5, label="Published-law reconstruction"),
        Line2D([], [], color=GRAY, ls=(0, (3, 2)), lw=1, label="Source coefficient")],
        loc="upper center", bbox_to_anchor=(.52, .995), frameon=False, ncol=3,
        columnspacing=1.4, handlelength=1.9, fontsize=7.2)
    bindings = []
    for index, (ax, term) in enumerate(zip(axes, terms)):
        selected = [r for r in rows if r["term"] == term]
        sources = {r["exported_coefficient"] for r in selected}
        assert len(sources) == 1
        source = next(iter(sources))
        ax.axvline(0, color="#D2D7DB", lw=.6, zorder=0)
        ax.axvline(source, color=GRAY, lw=1, ls=(0, (3, 2)), zorder=1)
        plotted = []
        for arm, color, marker, offset in (("native", PURPLE, "s", 3.5), ("agent", BLUE, "o", 0)):
            for i, seed in enumerate((6101, 6102, 6103)):
                r = next(r for r in selected if r["arm"] == arm and r["seed"] == seed)
                assert r["wald_lower"] <= r["estimate"] <= r["wald_upper"]
                y = offset + (2-i)
                ax.errorbar(r["estimate"], y,
                    xerr=[[r["estimate"]-r["wald_lower"]], [r["wald_upper"]-r["estimate"]]],
                    fmt=marker, ms=3.7, color=color, lw=.95, capsize=2, zorder=3)
                plotted.append(dict(r))
        ax.set_ylim(-.55, 6.05)
        ax.set_xlim(-.082, .082)
        ax.set_yticks([5.5, 4.5, 3.5, 2, 1, 0],
                     ["6101", "6102", "6103", "6101", "6102", "6103"] if index == 0 else [""]*6)
        ax.set_xticks([-.08, -.04, 0, .04, .08])
        ax.xaxis.set_major_formatter(FuncFormatter(number))
        ax.set_xlabel("Mixed-model interaction coefficient", labelpad=3)
        ax.set_title(f"({chr(97+index)})  HbA1c spline {'< 6.5%' if index == 0 else '≥ 6.5%'}", loc="left", fontsize=8, pad=4)
        if index == 0:
            ax.set_ylabel("Seed", labelpad=4)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#B1BAC1")
        ax.tick_params(axis="y", length=0)
        bindings.append({"panel": chr(97+index), "term": term,
            "source_coefficient": source,
            "source_standard_error_recorded_not_plotted": selected[0]["exported_source_se"],
            "published_original_coefficient": selected[0]["published_original_coefficient"],
            "published_synthetic_coefficient": selected[0]["published_synthetic_coefficient"],
            "coefficient_rows": plotted})
    return bindings, save(fig, "fig4-longitudinal")


def figure5(report, sensitivity):
    slots = sorted((s for s in report["slots"] if s["stage"] == "final"), key=lambda s: s["seed"])
    assert [s["seed"] for s in slots] == [7401, 7402, 7403]
    assert all(s["status"] == "success" and s["aliased_initial"] for s in slots)
    assert len({s["table_sha256"] for s in slots}) == 3
    assert all(s["analysis"]["n"] == 3000 for s in slots)
    assert sensitivity["status"] == "PASS" and len(sensitivity["cases"]) == 2
    assert sensitivity["random_draws"] == 0 and not sensitivity["generator_executed"]
    fig = plt.figure(figsize=(7, 4.4))
    fig.legend(handles=[
        Line2D([], [], marker="o", color=BLUE, lw=1, markersize=3.5, label="Generated estimate / 95% interval"),
        Patch(facecolor="#DCE0E3", edgecolor=GRAY, label="Reference estimate / 95% interval"),
        Line2D([], [], marker="D", color=ORANGE, lw=0, markersize=4, label="Analytical scenario")],
        loc="upper center", bbox_to_anchor=(.51, 1.002), frameon=False, ncol=3,
        columnspacing=1, handlelength=1.4, fontsize=6.9)
    fig.text(.08, .904, "Primary: HbA1c ~ BMI + glucose + age + female", fontsize=8.2, weight="bold", color=INK)
    fig.text(.08, .455, "Secondary: HbA1c ~ BMI + age + female", fontsize=8.2, weight="bold", color=INK)
    display = {"bmi": ("BMI", "per kg/m²"), "glucose": ("Glucose", "per mmol/L"),
               "age": ("Age", "per year"), "female": ("Female − male", "difference")}
    bindings = []
    counter = 0
    for row, terms in enumerate((["bmi", "glucose", "age", "female"], ["bmi", "age", "female"])):
        key = "B" if row == 0 else "A"
        for col, term in enumerate(terms):
            ax = fig.add_axes([.095+col*.23, .615-row*.45, .17, .22])
            ref = report["reference"][key]["coefficients"][term]
            ax.axvspan(ref["lower"], ref["upper"], color="#DCE0E3", alpha=.85, zorder=0)
            ax.axvline(ref["value"], color=GRAY, ls=(0, (3, 2)), lw=1, zorder=1)
            ax.axvline(0, color="#BCC3C8", lw=.6, zorder=0)
            entries = []
            for y, slot in enumerate(slots):
                analysis = slot["analysis"] if row == 0 else slot["analysis"]["descriptive_secondary"]
                c = analysis["coefficients"][term]
                assert c["lower"] <= c["value"] <= c["upper"]
                ax.errorbar(c["value"], y,
                    xerr=[[c["value"]-c["lower"]], [c["upper"]-c["value"]]],
                    fmt="o", color=BLUE, ms=3.8, capsize=2, lw=1, zorder=3)
                entries.append({"seed": slot["seed"], "table_sha256": slot["table_sha256"],
                    **{k:c[k] for k in ("value", "lower", "upper", "standard_error", "unit")},
                    "source_locator": f"slots[stage=final,seed={slot['seed']}].analysis."+
                        ("" if row == 0 else "descriptive_secondary.")+f"coefficients.{term}"})
            ax.set_yticks(range(3), [str(s["seed"]) if col == 0 else "" for s in slots])
            if col == 0:
                ax.set_ylabel("Seed", labelpad=3)
            ax.set_ylim(2.55, -.55)
            ax.set_title(f"({chr(97+counter)})  {display[term][0]}", loc="left", fontsize=7.7, pad=5)
            ax.set_xlabel(display[term][1], labelpad=3)
            axis_style(ax)
            bindings.append({"panel": chr(97+counter), "reference_analysis_key": key, "term": term,
                "reference": {k:ref[k] for k in ("value", "lower", "upper", "standard_error", "unit")},
                "reference_locator": f"reference.{key}.coefficients.{term}", "generated": entries})
            counter += 1
    ax = fig.add_axes([.795, .165, .16, .22])
    points = []
    for case in sensitivity["cases"]:
        assert case["status"] == "PASS" and case["secondary_projection_unchanged"]
        rho = case["declared_latent_BMI_glucose"]
        value = case["primary"][case["primary_order"].index("bmi")]
        ax.plot(rho, value, marker="D", color=ORANGE, ms=4.5, ls="none")
        ax.annotate(f"{value:+.4f}".replace("-", "−"), (rho, value),
                    xytext=(0, 7 if value > 0 else -13), textcoords="offset points", ha="center", fontsize=6.6, color=ORANGE)
        points.append({"latent_bmi_glucose_correlation": rho, "primary_bmi_coefficient": value,
            "secondary_bmi_coefficient": case["secondary"][case["secondary_order"].index("bmi")],
            "source_locator": f"cases[declared_latent_BMI_glucose={rho}].primary[primary_order=bmi]"})
    ax.axhline(0, color="#BCC3C8", lw=.6)
    ax.set_xlim(.02, .48)
    ax.set_ylim(-.03, .054)
    ax.set_xticks([.1, .4], ["0.10", "0.40"])
    ax.set_yticks([-.02, 0, .02, .04])
    ax.yaxis.set_major_formatter(FuncFormatter(number))
    ax.set_xlabel("BMI–glucose ρ", labelpad=3)
    ax.set_title("(h)  BMI sensitivity", loc="left", fontsize=7.7, pad=5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#B1BAC1")
    assert len(bindings) == 7 and sum(len(b["generated"]) for b in bindings) == 21
    assert [p["latent_bmi_glucose_correlation"] for p in points] == [.1, .4]
    return {"coefficients": bindings, "sensitivity": points,
        "delivered_model_latent_correlation": sensitivity["baseline_latent_BMI_glucose"],
        "reference_n": report["reference"]["B"]["n"],
        "reference_clusters": report["reference"]["B"]["cluster_count"]}, save(fig, "fig5-scientific-use")


def main():
    profile = "local_work" if (PROJECT / "work").is_dir() else "public_reports"
    root = "work" if profile == "local_work" else "reports"
    pins = {CSV_PATH: CSV_SHA, f"{root}/{REPORT_PATH}": REPORT_SHA, f"{root}/{SENS_PATH}": SENS_SHA}
    for relative, expected in pins.items():
        actual = sha(PROJECT / relative)
        if actual != expected:
            raise RuntimeError(f"Frozen input hash mismatch: {relative}: {actual}")
    with (PROJECT / CSV_PATH).open(encoding="utf-8-sig", newline="") as stream:
        rows = [{k:(v if k in ("arm", "term") else int(v) if k == "seed" else float(v))
                 for k,v in row.items()} for row in csv.DictReader(stream)]
    report = json.loads((PROJECT / root / REPORT_PATH).read_text(encoding="utf-8"))
    sensitivity = json.loads((PROJECT / root / SENS_PATH).read_text(encoding="utf-8"))
    matplotlib.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.4,
        "axes.labelsize": 7.2, "xtick.labelsize": 6.9, "ytick.labelsize": 6.9,
        "axes.linewidth": .6, "svg.fonttype": "none", "pdf.fonttype": 42,
        "svg.hashsalt": "conference-use-cases-v10-2026-11-04"})
    h, out4 = figure4(rows)
    c, out5 = figure5(report, sensitivity)
    binding = {"schema": "conference_use_case_bindings_v10", "input_profile": profile,
        "input_sha256": pins, "script_sha256": sha(Path(__file__)),
        "matplotlib_version": matplotlib.__version__,
        "individual_records_read": False, "generator_executed": False, "statistical_analysis_rerun": False,
        "figure4": {"dimensions_inches": [7, 2.2], "panels": h,
            "counts": {"constructions": 2, "seeds_per_construction": 3, "focal_terms": 2, "estimates": 12, "source_coefficients": 2},
            "source_interval": "No source interval constructed; supplied coefficient line only",
            "generated_interval": "Stored mixed-model Wald intervals, conditional on generated data",
            "scope": "Published HRS example reconstruction, not independent HRS patient validation"},
        "figure5": {"dimensions_inches": [7, 4.4], **c,
            "counts": {"constructions": 1, "delivered_tables": 3, "rows_per_table": 3000, "effects": 7, "generated_estimates": 21, "analytical_scenarios": 2},
            "reference_interval": "95% community-cluster CR1-t; exposed CHNS sample",
            "generated_interval": "95% HC3-t; conditional on model and draw; omits source/structural/transport uncertainty",
            "sensitivity_display": "Two precomputed points, no interpolation, new draws or calibrated uncertainty",
            "scope": "Developmental analysis with an exposed reference; not new confirmation or equivalence"},
        "output_sha256": {**out4, **out5}}
    (HERE / "FIG45_NUMERIC_BINDINGS.json").write_text(json.dumps(binding, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"profile": profile, "outputs": list(binding["output_sha256"]), "figure4_estimates": 12, "figure5_estimates": 21, "analytic_points": 2}))


if __name__ == "__main__":
    main()
