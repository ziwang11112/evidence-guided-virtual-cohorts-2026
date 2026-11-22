"""Plot all matched changes in screening with the common first estimate visible."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent


def main():
    results = json.loads((HERE / "RESULTS.json").read_text(encoding="utf-8"))
    audited = json.loads((HERE / "VERIFICATION.json").read_text(encoding="utf-8"))
    assert results["primary"] == audited["primary_verified"]
    blocks = sorted(results["blocks"])
    ink, muted, blue, rust = "#1c3042", "#526777", "#225f89", "#a84a29"

    fig = plt.figure(figsize=(8.5, 4.9), facecolor="white")
    grid = fig.add_gridspec(1, 2, width_ratios=[1.25, 6.4], left=.055,
                            right=.965, bottom=.24, top=.76, wspace=.06)
    labels = fig.add_subplot(grid[0])
    ax = fig.add_subplot(grid[1], sharey=labels)
    labels.set_xlim(0, 1)
    labels.set_ylim(len(blocks)-.45, -.55)
    labels.set_axis_off()
    labels.text(.02, 1.06, "Block", transform=labels.transAxes, fontsize=8, color=muted)
    labels.text(.96, 1.06, "Initial", ha="right", transform=labels.transAxes, fontsize=8, color=muted)

    fig.text(.055, .928, "How much can the screening estimate change?",
             color=ink, fontsize=15, fontweight="bold")
    fig.text(.055, .876, "Mwanza lipid survey  ·  non-HDL cholesterol ≥160 mg/dL", color=muted, fontsize=10)
    ax.axvspan(-4, 4, color="#e9eff4", zorder=-3)
    ax.axvline(0, color="#647784", lw=.85, zorder=-1)
    for edge in (-4, 4):
        ax.axvline(edge, color="#778b9c", lw=.7, ls=(0, (3, 3)), zorder=-1)
    max_shift = 4
    for i, block in enumerate(blocks):
        first = results["models"][f"{block}_initial"]
        labels.text(.02, i, block, ha="left", va="center", color=ink, fontsize=8.3)
        first_label = f"{first['percent']:.2f}%" if first["usable"] else "—"
        labels.text(.96, i, first_label, ha="right", va="center", color=muted, fontsize=8.3)
        row = results["blocks"][block]
        points = []
        for arm, marker, color, dy in [("ordinary", "o", blue, -.075), ("alternative", "D", rust, .075)]:
            if row[arm]["both_valid"]:
                delta = row[arm]["second_pct"] - row[arm]["first_pct"]
                max_shift = max(max_shift, abs(delta))
                points.append((delta, i+dy))
                ax.scatter(delta, i+dy, s=28, marker=marker, facecolor=color,
                           edgecolors="white", linewidths=.6, zorder=3)
        if len(points) == 2:
            ax.plot(*zip(*points), color="#a0adba", lw=.85, zorder=1)
    extent = 2 * (int(max_shift / 2) + 1) + .5
    ax.set_xlim(-extent, extent)
    ax.set_xticks([v for v in range(-16, 17, 4) if -extent < v < extent])
    ax.tick_params(axis="x", labelsize=8, colors=ink, length=3)
    ax.tick_params(axis="y", left=False, labelleft=False)
    for side in ("top", "left", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#9eacb8")
    ax.set_xlabel("Second estimate minus initial estimate (percentage points)", color=ink, fontsize=9)
    ax.legend(handles=[Line2D([], [], marker=m, color=c, ls="", markersize=5.5, label=t)
                       for m, c, t in (("o", blue, "Ordinary second model"),
                                       ("D", rust, "Search for an alternative pairing"))],
              loc="lower left", bbox_to_anchor=(0, 1.025), ncol=2, frameon=False,
              borderaxespad=0, columnspacing=2, handletextpad=.3, fontsize=8)
    n_valid = sum(m["usable"] for m in results["models"].values())
    fig.text(.055, .087, f"{n_valid}/{len(results['models'])} programs passed the source and generation checks.",
             color=ink, fontsize=8.5)
    fig.text(.055, .046, "Shading marks ±4 points. Success also required a shift over 2 points in the pooled direction at every seed.",
             color=muted, fontsize=8)
    fig.savefig(HERE / "matched-screening.png", dpi=190, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
