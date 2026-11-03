"""Plot stored source aggregates only; never read tables or target/reference files.

Run: python -B plot_source_fidelity.py
Inputs: ../INITIAL_SOURCE_AGGREGATES.json
Outputs: source_fidelity_initial.png and source_fidelity_initial.svg beside script.
No statistics are estimated: means and extrema are read directly from the input.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, FormatStrFormatter


HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "INITIAL_SOURCE_AGGREGATES.json"
PANELS = (
    ("Q_J_bmi", "A", "Jansen: adjusted BMI coefficient",
     "IFCC HbA1c (mmol/mol) per kg/m²", "%.3f"),
    ("Q_J_fpg", "B", "Jansen: adjusted glucose coefficient",
     "IFCC HbA1c (mmol/mol) per mmol/L glucose", "%.2f"),
    ("Q_B_pearson", "C", "Bao: Pearson correlation",
     "Fasting plasma glucose–HbA1c Pearson r", "%.3f"),
    ("Q_M_spearman", "D", "MIND: Spearman correlation",
     "Fasting serum glucose–HbA1c Spearman ρ", "%.3f"),
)
COLORS = {"A01": "#187D83", "A02": "#B45F26"}


def main() -> None:
    raw = INPUT.read_bytes()
    data = json.loads(raw)
    expected = {(a, check) for a in COLORS for check, *_ in PANELS}
    rows = {(row["constructor"], row["check"]): row for row in data["groups"]}
    if set(rows) != expected or len(data["groups"]) != len(expected):
        raise ValueError("Exactly two initial constructions and four checks required")
    for row in rows.values():
        if row["n_fixed_seeds"] != 3:
            raise ValueError("This figure requires three fixed seeds per check")
        if not row["generated_min"] <= row["generated_mean"] <= row["generated_max"]:
            raise ValueError("Stored extrema do not bracket the stored mean")

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "axes.titlesize": 11.5, "axes.labelsize": 10,
        "xtick.labelsize": 9.5, "ytick.labelsize": 10.5,
        "axes.edgecolor": "#A9B0B7", "axes.labelcolor": "#2B343B",
        "text.color": "#202B33", "xtick.color": "#4B565E",
        "ytick.color": "#2B343B", "svg.fonttype": "none",
        "savefig.facecolor": "white",
    })
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 6.7))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.23,
                        top=0.81, wspace=0.29, hspace=0.68)
    fig.text(0.09, 0.956, "Initial constructions: source-statistic comparison",
             fontsize=16, weight="bold", ha="left")
    fig.text(0.09, 0.911,
             "Stored means and min–max ranges from three fixed seeds · 3,000 rows per source draw",
             fontsize=10.5, color="#4B565E", ha="left")

    for ax, (check, letter, title, unit, fmt) in zip(axes.flat, PANELS):
        selected = [rows[(a, check)] for a in COLORS]
        points = {r["published_point"] for r in selected}
        if len(points) != 1:
            raise ValueError("Constructions must use the same published point")
        published = selected[0]["published_point"]
        ax.axvline(published, color="#66727B", lw=1.35,
                   linestyle=(0, (4, 3)), zorder=1)
        for y, row in zip((1, 0), selected):
            mean, lo, hi = (row[k] for k in
                            ("generated_mean", "generated_min", "generated_max"))
            ax.errorbar(mean, y, xerr=[[mean - lo], [hi - mean]],
                        fmt="o", color=COLORS[row["constructor"]],
                        markersize=7, elinewidth=2.3, capsize=4,
                        capthick=1.5, zorder=3)
        if check in {"Q_B_pearson", "Q_M_spearman"}:
            # Shared display limits only: these are not scientific thresholds.
            ax.set_xlim(0.20, 0.70)
            ax.set_xticks([0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
            ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        else:
            lo = min([published] + [r["generated_min"] for r in selected])
            hi = max([published] + [r["generated_max"] for r in selected])
            padding = (hi - lo) * 0.22
            ax.set_xlim(lo - padding, hi + padding)
            ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
            ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.set_ylim(-0.55, 1.55)
        ax.set_yticks([1, 0], ["A01", "A02"])
        ax.tick_params(axis="y", length=0, pad=8)
        ax.tick_params(axis="x", length=3)
        ax.set_axisbelow(True)
        ax.grid(axis="x", color="#E8ECEF", linewidth=0.7)
        for spine in ("left", "right", "top"):
            ax.spines[spine].set_visible(False)
        ax.set_xlabel(unit, labelpad=9)
        ax.set_title(f"{letter}  {title}", loc="left", pad=23,
                     weight="semibold")
        ax.text(0, 1.045, "Published point = " + (fmt % published),
                transform=ax.transAxes, color="#5C6871", fontsize=9.5)

    legend = [
        Line2D([], [], color="#33434D", marker="o", markersize=6,
               lw=2, label="Mean with three-seed min–max"),
        Line2D([], [], color="#66727B", linestyle=(0, (4, 3)), lw=1.35,
               label="Published point (uncertainty not shown)"),
    ]
    fig.legend(handles=legend, loc="lower left", bbox_to_anchor=(0.082, 0.08),
               frameon=False, ncol=2, fontsize=10, handlelength=2.6,
               columnspacing=3)
    fig.text(0.09, 0.047,
             "Ranges are not confidence intervals. All four branches retained; paired repeats add no distinct laws.",
             fontsize=9.5, color="#4B565E")
    description = (
        "Aggregate-only initial source comparison; fixed-seed ranges are not CIs. "
        "No source uncertainty is inferred. Input SHA256: "
        + hashlib.sha256(raw).hexdigest()
    )
    fig.savefig(HERE / "source_fidelity_initial.png", dpi=240,
                metadata={"Description": description, "Software": "matplotlib"})
    fig.savefig(HERE / "source_fidelity_initial.svg",
                metadata={"Description": description, "Creator": "matplotlib"})
    plt.close(fig)
    print(json.dumps({"input": str(INPUT), "input_sha256": hashlib.sha256(raw).hexdigest(),
                      "output_png": str(HERE / "source_fidelity_initial.png"),
                      "output_svg": str(HERE / "source_fidelity_initial.svg"),
                      "scientific_statistics_reestimated": False}))


if __name__ == "__main__":
    main()
