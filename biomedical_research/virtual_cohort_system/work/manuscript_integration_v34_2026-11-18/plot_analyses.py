"""Build the two KDD result figures from saved aggregate estimates."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullLocator
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "manuscript/paper_figures_v34_2026-11-18"
WORK = ROOT / "work"
COLORS = ("#315D9C", "#895490")
DARK = "#23354A"
GRAY = "#667181"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.4,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#A9B0BB", "axes.labelcolor": DARK,
                     "text.color": DARK, "xtick.color": GRAY, "ytick.color": GRAY,
                     "pdf.fonttype": 42, "svg.fonttype": "none"})

def save(fig, stem):
    for ext in ("pdf", "svg", "png"):
        fig.savefig(OUT / f"{stem}.{ext}", dpi=210, facecolor="white")
    plt.close(fig)

def paper_estimates():
    df = pd.read_csv(WORK / "original_paper_capability_2026-11-17/analysis/author_results.csv")
    panels = [
        ("bmi_sbp", "BMI and systolic pressure", "mmHg per 5 kg/m² BMI", 1),
        ("bmi_dbp", "BMI and diastolic pressure", "mmHg per 5 kg/m² BMI", 1),
        ("residual_correlation", "Paired pressure residuals", "Pearson correlation", 1),
        ("odds_ratio", "Joint deficiency association", "Odds ratio (log scale)", 1),
        ("joint_prevalence", "Both biomarkers low", "Prevalence (%)", 100),
        ("spearman", "Hemoglobin and ferritin", "Spearman correlation", 1),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(8.05, 4.28))
    fig.subplots_adjust(left=.097, right=.982, bottom=.13, top=.805, wspace=.38, hspace=1.43)
    for i, (ax, (key, label, unit, scale)) in enumerate(zip(axes.flat, panels)):
        d = df[df.estimand == key].sort_values("episode_id")
        assert len(d) == 3 and d.available_seeds.eq(3).all() and d.reference.nunique() == 1
        color = COLORS[i // 3]
        ref = d.reference.iloc[0] * scale
        ax.axvline(ref, color=DARK, ls=(0, (3, 2)), lw=1, zorder=1)
        for j, r in enumerate(d.itertuples()):
            ax.plot([r.seed_min * scale, r.seed_max * scale], [2-j]*2, color=color, lw=1.7)
            ax.scatter(r.seed_mean * scale, 2-j, color=color, s=25, zorder=3,
                       edgecolor="white", linewidth=.5)
        ax.set_ylim(-.55, 2.65)
        ax.set_yticks([2, 1, 0], ["Agent 1", "Agent 2", "Agent 3"] if i % 3 == 0 else [""]*3)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.set_xlabel(unit, fontsize=8)
        ax.set_title(f"{chr(97+i)}   {label}", loc="left", fontsize=8.8, fontweight="bold", pad=5)
        if key == "odds_ratio":
            ax.set_xscale("log")
            ticks = [5, 7, 10, 15, 20]
            ax.set_xlim(4.5, 21)
            ax.set_xticks(ticks, [str(v) for v in ticks])
            ax.xaxis.set_minor_locator(NullLocator())
        else:
            ax.locator_params(axis="x", nbins=4)
            ax.ticklabel_format(axis="x", useOffset=False)
        ax.grid(axis="x", color="#E2E6EC", lw=.55)
        ax.set_axisbelow(True)
    fig.text(.097,.947,"Blood pressure  /  Brazil",weight="bold",color=COLORS[0],size=10)
    fig.text(.097,.437,"Iron status  /  United States",weight="bold",color=COLORS[1],size=10)
    fig.legend(handles=[Line2D([],[],color=DARK,ls="--",lw=1,label="Measured sample"),
                        Line2D([],[],color=GRAY,marker="o",lw=1.5,ms=4,label="Virtual mean and three-draw range")],
               loc="upper right",bbox_to_anchor=(.99,1.01),ncol=2,frameon=False,fontsize=7.8)
    save(fig, "original-paper-estimates")

def matched_lifestyle():
    df = pd.read_csv(WORK / "matched_size_utility_2026-11-17/CONTRAST_SUMMARIES.csv")
    traits = [("bmi","BMI","kg/m²",1189), ("total_cholesterol","Total cholesterol","mg/dL",400),
              ("hdl_cholesterol","HDL","mg/dL",405)]
    contrasts = ["rural_minus_pastoralist", "urban_minus_pastoralist", "urban_minus_rural"]
    fig, axes = plt.subplots(1, 3, figsize=(8.05, 2.53))
    fig.subplots_adjust(left=.167, right=.983, bottom=.19, top=.72, wspace=.25)
    for i,(ax,(trait,title,unit,n)) in enumerate(zip(axes,traits)):
        for j,key in enumerate(contrasts):
            d = df[(df.trait == trait) & (df.contrast == key)].sort_values("stream")
            assert len(d) == 7 and d.absolute_n.eq(500).all() and d.unavailable.eq(0).all()
            real = d[d.comparison == "real_real"].iloc[0]
            ax.scatter(real.absolute_mean,2-j, color=DARK, marker="s",s=32,zorder=4)
            for k,stem in enumerate(["A1","A2"]):
                rows = d[d.stream.str.startswith("LIFESTYLE_"+stem+"_")]
                assert len(rows) == 3
                y = 2-j + (.2 if k == 0 else -.2) + np.array([-.046,0,.046])
                ax.scatter(rows.absolute_mean,y,marker=("o","^")[k],s=24, color=COLORS[k],
                           edgecolor="white",linewidth=.4,zorder=3)
        ax.set_xlim(left=0); ax.set_ylim(-.43,2.45)
        ax.set_yticks([2,1,0], ["Rural − pastoralist","Urban − pastoralist","Urban − rural"] if i==0 else [""]*3)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y",length=0)
        ax.grid(axis="x",lw=.55,color="#E2E6EC");ax.set_axisbelow(True)
        ax.locator_params(axis="x",nbins=4)
        ax.set_xlabel(unit)
        ax.set_title(f"{chr(97+i)}   {title}  ·  n = {n:,}",loc="left",fontsize=8.8,weight="bold",pad=8)
    handles=[Line2D([],[],ls="",marker=m,color=c,ms=5,label=t)
             for m,c,t in [("s",DARK,"Real–real"),("o",COLORS[0],"Virtual–real, Agent 1"),("^",COLORS[1],"Virtual–real, Agent 2")]]
    fig.legend(handles=handles,loc="upper center",bbox_to_anchor=(.54,1.0),frameon=False,ncol=3,fontsize=8.2)
    save(fig,"matched-lifestyle")

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    paper_estimates()
    matched_lifestyle()
