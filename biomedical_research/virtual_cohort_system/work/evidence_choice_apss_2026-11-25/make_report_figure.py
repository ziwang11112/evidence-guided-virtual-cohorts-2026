"""Render the APSS results from the published aggregate only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import numpy as np


ROOT = Path(__file__).resolve().parent
STYLES = {
    "ordinary": ("#325F94", "o", "Ordinary instruction", 0.14),
    "targeted": ("#B6532B", "D", "Analysis-specific instruction", -0.14),
}


def render(aggregate, destination):
    if aggregate["stage"] != "measured" or aggregate["reference"] is None:
        raise ValueError("The measured evaluation aggregate is required")
    slots = sorted(aggregate["slots"], key=lambda s: (s["block"], s["arm"]))
    blocks = sorted({s["block"] for s in slots})
    expected = {(block, arm) for block in blocks for arm in STYLES}
    if len(blocks) != 4 or len(slots) != 8 or {(s["block"], s["arm"]) for s in slots} != expected:
        raise ValueError("Expected one ordinary and one targeted construction in each of four blocks")
    for slot in slots:
        draws = slot["draws"]
        complete = len(draws) == 3 and len({d["seed"] for d in draws}) == 3 and all(d["available"] for d in draws)
        if slot["all_three_available"] != complete:
            raise ValueError("Inconsistent construction status")
    valid = sum(s["all_three_available"] for s in slots)
    if valid == 0:
        print("No implementation delivered all three draws. No figure produced.")
        return
    ref = aggregate["reference"]
    low, high = ref["paired_participant_bootstrap"]["tail_pct_interval"]
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.labelcolor": "#27354A",
        "xtick.color": "#48566A", "ytick.color": "#48566A", "text.color": "#182D47",
        "pdf.fonttype": 42, "ps.fonttype": 42, "axes.unicode_minus": False,
    })
    fig, (left, right) = plt.subplots(ncols=2, figsize=(8.1, 3.72), sharey=True)
    fig.subplots_adjust(left=.135, right=.97, top=.73, bottom=.29, wspace=.21)
    fig.text(.02, .930, "Source agreement and BMI underreporting", fontsize=15, fontweight="bold")
    fig.text(.02, .866, "Australian pre-exercise screening study  ·  Four independent constructions per instruction",
             fontsize=9.2, color="#46566B")

    left.set_title("A   Published obesity classifications", loc="left", fontsize=10.2, fontweight="bold", pad=9)
    right.set_title("B   Underreported BMI by >2 kg/m²", loc="left", fontsize=10.2, fontweight="bold", pad=9)
    right.axvspan(low, high, facecolor="#DDE1E8", alpha=.8, zorder=0)
    right.axvline(ref["tail_pct"], color="#3C4656", lw=1, zorder=2)
    left.axvline(3, color="#8291A4", lw=1, ls=(0, (3, 2)), zorder=1)

    positions = {b: i for i, b in enumerate(reversed(blocks))}
    published = [3.]
    predictions = [high, ref["tail_pct"]]
    for slot in slots:
        color, marker, _, offset = STYLES[slot["arm"]]
        ypos = positions[slot["block"]] + offset
        if not slot["all_three_available"]:
            n = sum(d["available"] for d in slot["draws"])
            left.text(.018, ypos, f"{n}/3 draws", transform=left.get_yaxis_transform(),
                      color=color, va="center", ha="left", fontsize=7)
            continue
        for ax, metric, extent in (
            (left, "source_joint_tv_pp", published),
            (right, "tail_pct", predictions),
        ):
            values = np.array([row[metric] for row in slot["draws"]])
            if not np.isfinite(values).all() or not ((values >= 0) & (values <= 100)).all():
                raise ValueError(f"Unexpected range on {metric}")
            extent.extend(values.tolist())
            ax.hlines(ypos, values.min(), values.max(), color=color, linewidth=1.8, zorder=3)
            ax.plot(np.median(values), ypos, marker=marker, markersize=5.9,
                    markerfacecolor=color, markeredgecolor="white", markeredgewidth=.45, zorder=4)

    left.set_yticks([positions[b] for b in blocks], [f"Block {b}" for b in blocks])
    left.set_xlabel("Four-cell total variation (percentage points)", fontsize=8.3)
    right.set_xlabel("Participants with online minus measured BMI < −2 (%)", fontsize=8.3)
    for ax, extent in [(left, published), (right, predictions)]:
        limit = max(max(extent) * 1.09, 4.)
        ax.set_xlim(-.018 * limit, limit)
        ax.set_ylim(-.47, 3.47)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=3))
        ax.grid(axis="x", color="#E8EBEF", linewidth=.6, zorder=-1)
        for block in blocks[:-1]:
            ax.axhline(positions[block] - .5, color="#EBEDF1", lw=.55, zorder=-1)
        for name in ("top", "right", "left"):
            ax.spines[name].set_visible(False)
        ax.spines["bottom"].set_color("#A9B2BF")
        ax.tick_params(axis="y", length=0, pad=5)
        ax.tick_params(axis="x", length=3, labelsize=8)
    handles = [Line2D([], [], color=c, lw=1.4, marker=m, markersize=5,
                      linestyle="-", label=label) for c, m, label, _ in STYLES.values()]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(.015,.112), frameon=False,
               ncol=2, columnspacing=1.6, fontsize=8.2)
    fig.text(.02, .083, f"Markers show three-seed medians and segments show ranges. {valid}/8 constructions were complete. The dashed line marks the 3-point source tolerance.", fontsize=7.2)
    ref_text = (f"The solid line marks the measured rate of {ref['tail_count']}/{ref['n']} ({ref['tail_pct']:.2f}%). "
                f"Shading shows its participant-bootstrap 95% interval ({low:.2f}–{high:.2f}%).")
    fig.text(.02, .031, ref_text, fontsize=7.65)
    fig.savefig(destination.with_suffix(".pdf"), metadata={"Title": "APSS source agreement and BMI underreporting"})
    fig.savefig(destination.with_suffix(".png"), dpi=210)
    plt.close(fig)


if __name__ == "__main__":
    data = json.loads((ROOT / "MEASURED_EVALUATION.json").read_text(encoding="utf-8"))
    render(data, ROOT / "apss-estimates")
