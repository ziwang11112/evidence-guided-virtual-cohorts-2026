"""Draw the main result from aggregate data only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parents[1] / "manuscript/kdd_draft_v47_2026-11-21/figures"
COLORS = {"US_NHANES": "#294d80", "ZA_HAALSI": "#795784", "M1": "#b65324", "independent": "#717984"}
LABELS = {"US_NHANES": "Measured US", "ZA_HAALSI": "Measured rural South Africa",
          "M1": "Agent pairing", "independent": "Independent pairing"}
MARK = {"US_NHANES": "s", "ZA_HAALSI": "^", "M1": "D", "independent": "o"}
DASH = {"US_NHANES": "-", "ZA_HAALSI": (0, (2.8, 1.6)), "M1": "-", "independent": (0, (4.2, 2.2))}


def main():
    d = json.loads((HERE / "GRIP_GROUPS.json").read_text(encoding="utf-8"))
    measured, models = d["measured"], d["method_scores"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "pdf.fonttype": 42,
                         "axes.labelcolor": "#263447", "xtick.color": "#445167", "ytick.color": "#445167",
                         "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#b6bec9"})
    fig = plt.figure(figsize=(7.08, 2.82))
    left = fig.add_axes([.069, .245, .365, .575])
    right = fig.add_axes([.615, .245, .369, .575])
    for x, letter, title in ((.005, "A", "How common are large grip differences?"),
                             (.496, "B", "Mean grip difference by sex and age")):
        fig.text(x, .925, letter, fontsize=11.2, weight="bold", color="#17263b", va="center")
        fig.text(x + .030, .925, title, fontsize=8.7, weight="bold", color="#17263b", va="center")
    keys = ("US_NHANES", "ZA_HAALSI", "M1", "independent")
    x = d["thresholds_kg"]
    left.axvline(5, color="#c2c9d2", lw=.8, zorder=0)
    for key in ("independent", "M1", "ZA_HAALSI", "US_NHANES"):
        record = measured[key]["groups"] if key in measured else models[key]
        left.plot(x, record["standardized"]["tail_pct"], color=COLORS[key], ls=DASH[key], lw=1.55,
                  marker=MARK[key], ms=3.1, mew=.8, mfc="white" if key == "independent" else COLORS[key],
                  markevery=[2, 5, 8, 11], zorder=2)
    left.set(xlim=(-.15, 12.2), ylim=(-2, 103), xticks=[0, 2, 5, 8, 10, 12], yticks=[0, 25, 50, 75, 100],
             xlabel="Absolute grip difference cutoff (kg)", ylabel="Adults at or above cutoff (%)")
    left.grid(axis="y", color="#e1e5eb", lw=.55)
    group_order = ["F50", "F60", "M50", "M60"]
    y = np.arange(len(group_order))[::-1]
    for yp, group in zip(y, group_order, strict=True):
        authored = models["M1"][group]["mean_gap_kg"]
        control = models["independent"][group]["mean_gap_kg"]
        right.plot([authored, control], [yp, yp], color="#c7cbd1", lw=1, zorder=1)
        for key, val in (("M1", authored), ("independent", control)):
            right.plot(val, yp, marker=MARK[key], ms=4.8, mfc="white" if key=="independent" else COLORS[key],
                       mec=COLORS[key], mew=1, ls="none", zorder=4)
        for key, offset in (("US_NHANES", .205), ("ZA_HAALSI", -.205)):
            rec = measured[key]["groups"][group]
            mid = rec["mean_gap_kg"]
            lo, hi = rec["mean_gap_ci"]
            right.errorbar(mid, yp + offset, xerr=[[mid-lo], [hi-mid]], fmt=MARK[key], ms=3.7,
                           color=COLORS[key], elinewidth=1.05, capsize=1.8, markeredgewidth=.9, zorder=3)
    right.set(xlim=(1.45, 10.08), ylim=(-.5, 3.53), xticks=[2, 4, 6, 8, 10], yticks=y,
              yticklabels=["Women 50–59", "Women 60–69", "Men 50–59", "Men 60–69"],
              xlabel="Mean absolute grip difference (kg)")
    right.spines["left"].set_visible(False)
    right.tick_params(axis="y", length=0, pad=5, labelsize=7.4)
    right.grid(axis="x", color="#e1e5eb", lw=.55)
    for ax in (left, right):
        ax.set_axisbelow(True)
        ax.tick_params(axis="x", labelsize=7.1, width=.65, length=3)
    left.tick_params(axis="y", labelsize=7.1, width=.65, length=3)
    handles = [Line2D([0], [0], color=COLORS[k], ls=DASH[k], marker=MARK[k], lw=1.5, ms=4.0,
                      mfc="white" if k=="independent" else COLORS[k], label=LABELS[k]) for k in keys]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .006), ncol=4, frameon=False,
               fontsize=7.35, handlelength=1.8, handletextpad=.45, columnspacing=1.6)
    fig.savefig(FIGURES / "grip-use-by-group.pdf", facecolor="white")
    fig.savefig(HERE / "grip-use-by-group.png", dpi=240, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
