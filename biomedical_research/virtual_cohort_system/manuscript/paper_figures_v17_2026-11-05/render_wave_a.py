"""Render Figure S5 and Table S7 using only frozen aggregate Wave A outputs."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
STEM = "figS5-prospective-wave"
RELEASE = Path("scaleup_2026-11-01/production_release")
AGGREGATE = "evaluation/PUBLISHABLE_AGGREGATES.json"
PINS = {AGGREGATE: "889ed586f8bbe3564594c6fd73dd2fbef316037dc36e0629f49f4f30151bbf36"}
CASES = {"K01": "HAALSI", "K02": "Turkana"}
CONSTRUCTORS = ("A01", "A02", "A03", "A04", "A05", "S01")
SEEDS = (2101, 2102, 2103)
# The final two fields give display limits and ticks in the native endpoint unit.
PANELS = (
    ("K01", "K01-GLUCOSE-BMI", "(a)  BMI–glucose", "BMI–glucose slope", "mmol/L per 5 kg/m² BMI", (-.045, .62), (0, .2, .4, .6)),
    ("K01", "K01-GLUCOSE-AGE", "(b)  Age–glucose", "Age–glucose slope", "mmol/L per 10 years", (-.038, .325), (0, .1, .2, .3)),
    ("K01", "K01-SEX-BMI", "(c)  BMI slope by sex", "Female − male BMI slope", "mmol/L per 5 kg/m² BMI", (-.465, .235), (-.4, -.2, 0, .2)),
    ("K02", "K02-HDL-BMI", "(d)  BMI–HDL", "BMI–HDL slope", "mg/dL per 5 kg/m² BMI", (-9.05, .65), (-8, -6, -4, -2, 0)),
    ("K02", "K02-TC-BMI", "(e)  BMI–total cholesterol", "BMI–total cholesterol slope", "mg/dL per 5 kg/m² BMI", (-4.75, 16.6), (-4, 0, 4, 8, 12, 16)),
    ("K02", "K02-LIPID-RESIDUAL", "(f)  Residual correlation", "Residual TC–HDL correlation", "Pearson correlation", (-.035, .615), (0, .2, .4, .6)),
)
INK, AGENT, STAT, BAND, REF = "#283448", "#4266AD", "#8071BA", "#E8EBF0", "#515D70"


def load_source(relative):
    for directory in (PROJECT / "work", PROJECT / "reports", PROJECT.parents[1] / "reports"):
        path = directory / RELEASE / relative
        if path.is_file():
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != PINS[relative]:
                raise ValueError(f"Frozen aggregate hash mismatch: {relative}")
            return json.loads(raw)
    raise FileNotFoundError(relative)


def collect():
    data = load_source(AGGREGATE)
    if data["target_rows_or_ids_emitted"]:
        raise ValueError("Unexpected aggregate provenance")
    final = [s for s in data["target_slots"] if s["stage"] == "final"]
    if len(final) != 36 or not all(s["stage_verified_success"] for s in final):
        raise ValueError("Expected 36 valid final reporting slots")
    index = {(s["case"], s["constructor"], int(s["seed"])): s for s in final}
    panels = []
    for case, key, heading, description, unit, limits, ticks in PANELS:
        ref = data["references"][case]["estimands"][key]
        entries = {}
        for constructor in CONSTRUCTORS:
            values = [index[case, constructor, seed]["analysis"]["estimands"][key]["estimate"] for seed in SEEDS]
            signs = [index[case, constructor, seed]["comparison"][key]["direction_agrees"] for seed in SEEDS]
            entries[constructor] = {"values": values, "same_point_sign": sum(signs)}
        bounds = [ref["estimate"]] + [v for e in entries.values() for v in e["values"]]
        if ref["interval"]["status"] == "available":
            bounds.extend([ref["interval"]["lower"], ref["interval"]["upper"]])
        if not limits[0] < min(bounds) <= max(bounds) < limits[1]:
            raise ValueError(f"Plot bounds would clip {key}")
        panels.append({"case": case, "endpoint": key, "heading": heading, "description": description,
                       "display_unit": unit, "native_unit": ref["unit"], "reference": ref["estimate"],
                       "reference_interval": ref["interval"], "constructors": entries,
                       "limits": limits, "ticks": ticks})
    decisions = {}
    for case in CASES:
        row = data["aggregate"]["cases"][f"{case}:final"]
        decisions[case] = {"agents_passing": row["agent_pass_counts"]["0.1"],
                           "agent_denominator": row["agent_denominator"], "s01_pass": row["statistical_reference_pass"]["0.1"]}
    return panels, decisions


def display_number(value):
    return f"{value:.3f}".replace("-", "−")


def display_range(values):
    return f"[{display_number(min(values))}, {display_number(max(values))}]"


def write_table(panels):
    lines = ["**Table S7. Reference and generated estimates for the six Wave A analyses.**",
             "", "| Case | Adjusted analysis | Sample | Agent range (same sign / 15) | S01 range (same sign / 3) |",
             "|---|---|---:|---|---|"]
    for p in panels:
        agent = [v for key in CONSTRUCTORS[:5] for v in p["constructors"][key]["values"]]
        matches = sum(p["constructors"][key]["same_point_sign"] for key in CONSTRUCTORS[:5])
        stat = p["constructors"]["S01"]
        lines.append(f"| {CASES[p['case']]} | {p['description']} | {display_number(p['reference'])} | "
                     f"{display_range(agent)} ({matches}/15) | {display_range(stat['values'])} ({stat['same_point_sign']}/3) |")
    lines += ["", "Ranges span the three fixed draws from each of five agent laws (A01–A05) or one prescribed statistical law (S01). "
              "Counts give agreement with the sign of the measured-sample point estimate. Each generated target table contains 5,000 virtual people. "
              "HAALSI glucose is in mmol/L per 5 kg/m² BMI or per 10 years of age. Its third analysis compares female and male BMI slopes with common age adjustment. "
              "Turkana lipid slopes are in mg/dL per 5 kg/m² BMI, adjusted for age and recorded sex. Residual correlation removes age, recorded sex and BMI from both lipids.",
              "", "At the prespecified 0.10 resolution, 3/5 HAALSI agent laws and 0/5 Turkana agent laws passed all three analyses on all three draws. "
              "Slope discrepancies were divided by the measured outcome sample SD. The correlation used absolute discrepancy. S01 failed in both cases. "
              "HAALSI’s zero-effect scenario also passed on all three endpoints. At least 4/5 passing agent laws were required for case reliability."]
    (HERE / "tableS7-wave-a-scientific-use.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render(panels):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.3, "text.color": INK,
                         "xtick.color": INK, "ytick.color": INK, "axes.labelcolor": INK,
                         "svg.fonttype": "none", "pdf.fonttype": 42, "svg.hashsalt": "wave-a-v17"})
    fig, axes = plt.subplots(2, 3, figsize=(7.15, 5.18))
    fig.subplots_adjust(left=.067, right=.987, top=.864, bottom=.165, wspace=.24, hspace=.86)
    for number, (ax, p) in enumerate(zip(axes.ravel(), panels)):
        ax.set_xlim(p["limits"])
        ax.set_ylim(5.56, -.56)
        ax.set_xticks(p["ticks"])
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, pos: f"{value:g}".replace("-", "−")))
        ax.set_yticks(range(6), labels=CONSTRUCTORS)
        ax.tick_params(axis="y", length=0, labelsize=7.8, pad=3, labelleft=number % 3 == 0)
        ax.tick_params(axis="x", labelsize=7.8, length=2.3, width=.6, pad=2, color="#A5ADBA")
        ax.spines[["left", "right", "top"]].set_visible(False)
        ax.spines["bottom"].set_color("#A5ADBA")
        ax.spines["bottom"].set_linewidth(.65)
        ax.set_axisbelow(True)
        ax.grid(axis="x", lw=.55, color="#EFF1F4")
        ax.set_title(p["heading"], loc="left", fontweight="bold", fontsize=8.8, pad=4.7)
        ax.set_xlabel(p["display_unit"], fontsize=7.8, labelpad=3)
        ci = p["reference_interval"]
        if ci["status"] == "available":
            ax.axvspan(ci["lower"], ci["upper"], color=BAND, zorder=0)
        ax.axvline(0, linestyle=":", linewidth=.7, color="#909AA8", zorder=1)
        ax.axvline(p["reference"], color=REF, linewidth=1, linestyle=(0, (3, 2)), zorder=2)
        ax.axhline(4.5, color="#CCD2D9", linewidth=.55, zorder=1)
        for y, constructor in enumerate(CONSTRUCTORS):
            estimates = p["constructors"][constructor]["values"]
            color, shape = (STAT, "s") if constructor == "S01" else (AGENT, "o")
            ax.hlines(y, min(estimates), max(estimates), linewidth=1.2, color=color, zorder=3)
            ax.scatter(estimates, [y-.13, y, y+.13], s=10, color=color, marker=shape, edgecolor="white", linewidth=.25, zorder=4)
    fig.text(.067, .948, "HAALSI glucose", size=11, weight="bold")
    fig.text(.29, .949, "Prospectively admitted target  ·  n = 4,394", size=8.4)
    fig.text(.067, .489, "Turkana lipids", size=11, weight="bold")
    fig.text(.29, .490, "Prior investigator exposure to study context  ·  n = 397", size=8.4)
    legend = [Line2D([], [], color=AGENT, marker="o", markersize=3.6, lw=1, label="Agent draws"),
              Line2D([], [], color=STAT, marker="s", markersize=3.6, lw=1, label="S01 draws"),
              Line2D([], [], color=REF, linestyle=(0, (3, 2)), lw=1, label="Sample estimate"),
              Patch(facecolor=BAND, edgecolor="none", label="Sample HC3 sensitivity band")]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(.52, .013), ncol=4, frameon=False,
               handlelength=1.65, handletextpad=.45, columnspacing=1.05, fontsize=7.8)
    date = datetime(2026, 11, 5, tzinfo=timezone.utc)
    metadata = {"pdf": {"Title": "Wave A scientific-use analyses", "Creator": "Matplotlib", "CreationDate": date, "ModDate": date},
                "svg": {"Title": "Wave A scientific-use analyses", "Creator": "Matplotlib", "Date": "2026-11-05"},
                "png": {"Title": "Wave A scientific-use analyses", "Software": "Matplotlib"}}
    hashes = {}
    for ext in ("pdf", "svg", "png"):
        path = HERE / f"{STEM}.{ext}"
        fig.savefig(path, dpi=350, facecolor="white", metadata=metadata[ext])
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    plt.close(fig)
    return hashes


if __name__ == "__main__":
    panels, decisions = collect()
    write_table(panels)
    outputs = render(panels)
    table = HERE / "tableS7-wave-a-scientific-use.md"
    outputs[table.name] = hashlib.sha256(table.read_bytes()).hexdigest()
    binding = {"figure": "S5", "table": "S7", "frozen_sources_sha256": PINS,
               "input": {"local_project_relative": f"work/{RELEASE.as_posix()}/{AGGREGATE}",
                         "public_repository_relative": f"reports/{RELEASE.as_posix()}/{AGGREGATE}", "sha256": PINS[AGGREGATE]},
               "cases": CASES, "seeds": SEEDS, "target_tables": 36, "displayed_seed_estimates": 108,
               "target_rows_per_table": 5000, "panels": panels, "decisions_at_0.10": decisions,
               "figure_inches": [7.15, 5.18], "matplotlib_version": matplotlib.__version__, "output_sha256": outputs}
    (HERE / f"{STEM}.binding.json").write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")

