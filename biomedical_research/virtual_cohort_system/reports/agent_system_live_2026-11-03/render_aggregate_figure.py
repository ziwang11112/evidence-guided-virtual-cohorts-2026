"""Plot all non-intercept prespecified effects from the closed aggregate report."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / "evaluation/REPORT.json").read_text(encoding="utf-8"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "svg.hashsalt": "live-agent-2026-11-03"})
panels = [("A", "bmi"), ("A", "age"), ("A", "female"),
          ("B", "bmi"), ("B", "glucose"), ("B", "age"), ("B", "female")]
fig, axes = plt.subplots(2, 4, figsize=(15, 7.5))
for ax, (request, term) in zip(axes.flat, panels):
    ref = report["reference"][request]["coefficients"][term]
    ax.axvspan(ref["lower"], ref["upper"], color="#d1d5db", alpha=.8)
    ax.axvline(ref["value"], color="#374151", linewidth=1.5)
    ax.axvline(0, color="#94a3b8", linestyle=":", linewidth=1)
    slots = [s for s in report["slots"] if s["request"] == request and s["stage"] == "final"]
    for i, slot in enumerate(slots):
        c = slot["analysis"]["coefficients"][term]
        ax.errorbar(c["value"], i, xerr=[[c["value"] - c["lower"]], [c["upper"] - c["value"]]],
                    color="#087f8c", marker="o", markersize=5, capsize=3, linewidth=1.5)
    ax.set_yticks([0, 1, 2], ["7301", "7302", "7303"])
    ax.set_ylim(2.6, -.6)
    ax.set_title(f"{request}: {term}" + (" (primary)" if term == "bmi" else ""), loc="left", weight="bold")
    ax.set_xlabel({"bmi": "HbA1c pp / (kg/m²)", "age": "HbA1c pp / year",
                   "female": "HbA1c pp", "glucose": "HbA1c pp / (mmol/L)"}[term])
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=.15)
axes.flat[-1].axis("off")
axes.flat[-1].legend(handles=[
    Patch(facecolor="#d1d5db", label="CHNS reference: CR1-t 95% CI"),
    Line2D([0], [0], color="#374151", label="CHNS point estimate"),
    Line2D([0], [0], color="#087f8c", marker="o", label="Generated: HC3-t 95% CI")],
    loc="upper left", frameon=False, fontsize=10)
axes.flat[-1].text(0, .51,
    "A: HbA1c ~ BMI + age + female\nB: add glucose to this analysis\n\n"
    "Initial models were retained.\nSix delivery tables; three seeds each.\n"
    "No target results supplied to authors.\n\n"
    "Synthetic intervals exclude model,\nsource and transport uncertainty.",
    transform=axes.flat[-1].transAxes, va="top", linespacing=1.5)
fig.suptitle("Live Agent generation: scientific usefulness depends on the analysis", x=.055, ha="left", fontsize=16, weight="bold")
fig.text(.055, .91, "Previously exposed CHNS development reference (n = 6,631); generated n = 3,000 per table. No new confirmation.", fontsize=11)
fig.subplots_adjust(left=.055, right=.985, top=.83, bottom=.10, hspace=.54, wspace=.42)
fig.text(.055, .02, "All seven non-intercept effects shown. Intercepts and full distribution/rank diagnostics are retained in REPORT.json. Exact equality is not a success criterion.", fontsize=10)
fig.savefig(ROOT / "ANALYSIS_UTILITY.png", dpi=150)
fig.savefig(ROOT / "ANALYSIS_UTILITY.svg", metadata={"Date": None})
plt.close(fig)
print("Rendered from closed aggregate REPORT.json; no individual data read or generator execution.")
