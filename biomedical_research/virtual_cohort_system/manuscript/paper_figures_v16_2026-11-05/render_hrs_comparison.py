"""Render the HRS age-by-HbA1c comparison from two reviewed aggregate CSV files.

Run this file with Python and Matplotlib. It reads only the named aggregate
files under work/ (local workspace) or reports/ (public project layout).
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist, mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
STEM = "fig2-hrs-comparison"
STUDY = "hrs_public_example_2026-11-03"
SEEDS = (6101, 6102, 6103)
PINS = {
    "fixed_effects_all_seeds.csv": "c565718f80a1e8c63152c61fe8c44824e6e8457b8c6627a1c991b7c5e802323e",
    "fixed_effects_summary.csv": "a4e382af2ad2a447ba1f77598df8952ac4e93af8a95c7cc8e8779ec2098242aa",
}
BRANCHES = (
    ("age60:hba1c_U65", "(a)  HbA1c below 6.5%"),
    ("age60:hba1c_O65", "(b)  HbA1c at or above 6.5%"),
)
COLORS = {"source": "#364253", "agent": "#4266AD", "native": "#8071BA",
          "ink": "#283448", "axes": "#A5ADBA", "grid": "#EEF0F3"}


def load_aggregate(name):
    for prefix in ("work", "reports"):
        path = PROJECT / prefix / STUDY / "summary" / name
        if path.is_file():
            payload = path.read_bytes()
            digest = hashlib.sha256(payload).hexdigest()
            if digest != PINS[name]:
                raise ValueError(f"Aggregate changed: {name}")
            rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))
            return rows, {"file": path.relative_to(PROJECT).as_posix(), "sha256": digest}
    raise FileNotFoundError(f"Missing reviewed aggregate {name}")


def extract_panels():
    draws, draws_source = load_aggregate("fixed_effects_all_seeds.csv")
    summaries, summary_source = load_aggregate("fixed_effects_summary.csv")
    panels = []
    for term, title in BRANCHES:
        records = [row for row in draws if row["term"] == term]
        expected = {(arm, seed) for arm in ("agent", "native") for seed in SEEDS}
        if len(records) != 6 or {(r["arm"], int(r["seed"])) for r in records} != expected:
            raise ValueError(f"Incomplete arm/seed inventory for {term}")
        sources = {(float(r["exported_coefficient"]), float(r["exported_source_se"])) for r in records}
        if len(sources) != 1:
            raise ValueError(f"Conflicting exported values for {term}")
        estimate, se = sources.pop()
        margin = NormalDist().inv_cdf(.975) * se
        panel = {
            "term": term, "title": title,
            "source": {"estimate": estimate, "exported_se": se,
                       "lower": estimate - margin, "upper": estimate + margin},
            "arms": {},
        }
        for arm in ("agent", "native"):
            observations = []
            for r in sorted((r for r in records if r["arm"] == arm), key=lambda x: int(x["seed"])):
                observations.append({"seed": int(r["seed"]), "estimate": float(r["estimate"]),
                                     "se": float(r["se"]), "lower": float(r["wald_lower"]),
                                     "upper": float(r["wald_upper"])})
            estimates = [r["estimate"] for r in observations]
            matched = [r for r in summaries if r["term"] == term and r["arm"] == arm]
            if len(matched) != 1 or int(matched[0]["available_seeds"]) != 3:
                raise ValueError(f"Missing verified summary for {arm}, {term}")
            summary = matched[0]
            for value, key in ((mean(estimates), "mean_estimate"), (min(estimates), "min_estimate"),
                               (max(estimates), "max_estimate"), (estimate, "exported_coefficient")):
                if not math.isclose(value, float(summary[key]), rel_tol=0, abs_tol=1e-14):
                    raise ValueError(f"Aggregate reconciliation failed for {arm}, {term}, {key}")
            panel["arms"][arm] = {"draws": observations, "mean": mean(estimates),
                                  "range": [min(estimates), max(estimates)]}
        panels.append(panel)
    return panels, [draws_source, summary_source]


def draw_interval(ax, point, height, color, shape):
    lower, estimate, upper = point["lower"], point["estimate"], point["upper"]
    if not lower < estimate < upper:
        raise ValueError("Wald limits must enclose the point estimate")
    ax.errorbar(estimate, height, xerr=[[estimate - lower], [upper - estimate]],
                fmt=shape, color=color, ecolor=color, markersize=4.8, markeredgewidth=.6,
                elinewidth=.95, capsize=2.1, zorder=4, clip_on=False)


def render(panels):
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8.5, "text.color": COLORS["ink"],
        "axes.labelcolor": COLORS["ink"], "xtick.color": COLORS["ink"], "ytick.color": COLORS["ink"],
        "svg.fonttype": "none", "pdf.fonttype": 42, "svg.hashsalt": "evc-v16-hrs",
    })
    fig, axes = plt.subplots(1, 2, figsize=(7.05, 2.60), sharex=True, sharey=True)
    fig.subplots_adjust(left=.183, right=.982, top=.835, bottom=.245, wspace=.12)
    ticks = [-.08, -.04, 0, .04, .08]
    def tick_label(value, _):
        return "0" if abs(value) < 1e-10 else f"{value:.2f}".replace("-", "−")

    for index, (ax, panel) in enumerate(zip(axes, panels)):
        ax.set_xlim(-.085, .085)
        ax.set_ylim(.08, 3.56)
        ax.set_xticks(ticks)
        ax.xaxis.set_major_formatter(FuncFormatter(tick_label))
        ax.tick_params(axis="x", labelsize=8.3, length=2.6, width=.6, color=COLORS["axes"], pad=3)
        ax.set_yticks([3.03, 1.99, .76], labels=["Published source", "Agent law", "Reconstructed\npublished law"])
        ax.tick_params(axis="y", length=0, pad=7, labelsize=8.5, labelleft=index == 0)
        ax.spines[["left", "right", "top"]].set_visible(False)
        ax.spines["bottom"].set_color(COLORS["axes"])
        ax.spines["bottom"].set_linewidth(.65)
        ax.grid(axis="x", color=COLORS["grid"], lw=.6, zorder=0)
        ax.axvline(0, color="#9AA3B0", lw=.8, zorder=1)
        ax.set_title(panel["title"], loc="left", fontsize=10.3, fontweight="bold", pad=8)

        source = panel["source"]
        draw_interval(ax, source, 3.03, COLORS["source"], "D")
        source_label = f"{source['estimate']:+.4f}".replace("-", "−")
        ax.annotate(source_label, (source["estimate"], 3.03), xytext=(0, 6),
                    textcoords="offset points", ha="center", fontsize=8, color=COLORS["source"])
        for arm, height, shape in (("agent", 1.99, "o"), ("native", .76, "s")):
            for point, offset in zip(panel["arms"][arm]["draws"], (.24, 0, -.24)):
                draw_interval(ax, point, height + offset, COLORS[arm], shape)

    fig.text(.57, .06, "Age-by-HbA1c coefficient (memory-score units per decade per HbA1c percentage point)",
             ha="center", va="center", fontsize=8.5, color=COLORS["ink"])
    today = datetime(2026, 11, 5, tzinfo=timezone.utc)
    metadata = {
        "png": {"Software": "Matplotlib", "Title": "HRS age-by-HbA1c interactions"},
        "pdf": {"Title": "HRS age-by-HbA1c interactions", "Creator": "Matplotlib",
                "CreationDate": today, "ModDate": today},
        "svg": {"Title": "HRS age-by-HbA1c interactions", "Creator": "Matplotlib", "Date": "2026-11-05"},
    }
    output_hashes = {}
    for extension in ("png", "svg", "pdf"):
        output = HERE / f"{STEM}.{extension}"
        fig.savefig(output, dpi=350, facecolor="white", metadata=metadata[extension])
        output_hashes[output.name] = hashlib.sha256(output.read_bytes()).hexdigest()
    plt.close(fig)
    return output_hashes


if __name__ == "__main__":
    panels, inputs = extract_panels()
    hashes = render(panels)
    binding = {
        "figure": 2, "stem": STEM, "inputs": inputs,
        "native_arm_label": "Reconstructed published law (corrected valid attempts)",
        "estimate_unit": "memory-score units per decade of age per HbA1c percentage point",
        "subjects_per_valid_table": 11509, "visits_per_subject": 4, "valid_tables": 6,
        "terms": {"age60": "(age - 60)/10", "hba1c_U65": "min(HbA1c - 6.5, 0)",
                  "hba1c_O65": "max(HbA1c - 6.5, 0)"},
        "source_intervals": "Estimate plus/minus the 0.975 standard-normal quantile times exported SE",
        "draw_intervals": "Stored model-conditional 95% Wald limits in fixed_effects_all_seeds.csv",
        "draw_order_top_to_bottom": list(SEEDS), "panels": panels,
        "figure_inches": [7.05, 2.60], "png_dpi": 350, "matplotlib_version": matplotlib.__version__,
        "output_sha256": hashes,
    }
    (HERE / f"{STEM}.binding.json").write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    for panel in panels:
        print(panel["term"], panel["source"]["estimate"],
              panel["arms"]["agent"]["mean"], panel["arms"]["native"]["mean"])

