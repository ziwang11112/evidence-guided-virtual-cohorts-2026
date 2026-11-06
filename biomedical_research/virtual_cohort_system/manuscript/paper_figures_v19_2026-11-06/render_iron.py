"""Regenerate the iron-status figure from recorded aggregate inputs.

Run beside fig3-iron-inputs.json with Python and matplotlib. To verify all
frozen inputs against their exact Git blobs, add --verify-repo <checkout>.
"""
import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import re
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import NullLocator, ScalarFormatter


HERE = Path(__file__).resolve().parent
STEM = "fig3-iron-utility"
INK, MUTED, RULE = "#253146", "#526279", "#D9E0E9"
A, B = "#3A66AB", "#BD5A29"
COLORS = {"A": A, "B": B}
MARKERS = {"A": "o", "B": "^"}


def verify_blobs(config, repo):
    blobs = {}
    for name, item in config["inputs"].items():
        spec = f"{config['scientific_commit']}:{item['path']}"
        raw = subprocess.check_output(["git", "-C", str(repo), "show", spec])
        if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise ValueError(f"Frozen input differs: {item['path']}")
        blobs[name] = raw
    pattern = (r"low Hb/low raw ferritin (\d+); low Hb/other ferritin (\d+); "
               r"other Hb/low ferritin (\d+); other/other (\d+)")
    cells = list(map(int, re.search(pattern, blobs["packet"].decode()).groups()))
    if cells != config["source_cells"]["counts"]:
        raise ValueError("Source threshold counts differ")
    measured = json.loads(blobs["target"])["estimands"]
    for metric, entries in config["measured_reference"].items():
        if any(measured[metric][k] != v for k, v in entries.items()):
            raise ValueError(f"Survey estimate or interval differs: {metric}")
    deliveries = json.loads(blobs["synthetic"])
    if set(deliveries) != set(config["deliveries"]) or len(deliveries) != 6:
        raise ValueError("Unexpected sealed table set")
    for key, tab in config["deliveries"].items():
        frozen = deliveries[key]
        if tab["rows"] != frozen["rows"] or any(
                val != frozen["estimands"][k]["estimate"] for k, val in tab["estimands"].items()):
            raise ValueError(f"Delivery differs: {key}")
    rules = config["target_rules"]
    if (rules["law_a_low_ferritin_weight"] != [2,3]
            or rules["law_a_independent_hb_fraction"] != [1,5]
            or b"2.0 / 3.0" not in blobs["law_a"]
            or b"rng.random(n) < 0.2" not in blobs["law_a"]):
        raise ValueError("Law A rule differs from the sealed program")


def stage_probabilities(config):
    """Return exact cell probabilities; order is both, Hb-only, ferritin-only, neither."""
    counts = config["source_cells"]["counts"]
    source = [F(v, sum(counts)) for v in counts]
    weight = F(*config["target_rules"]["law_a_low_ferritin_weight"])
    independently_drawn = F(*config["target_rules"]["law_a_independent_hb_fraction"])
    scaled = [v*w for v,w in zip(source, (weight, 1, weight, 1))]
    weighted = [v/sum(scaled) for v in scaled]
    hb_low = weighted[0] + weighted[1]
    ferritin_low = weighted[0] + weighted[2]
    independent = [hb_low*ferritin_low, hb_low*(1-ferritin_low),
                   (1-hb_low)*ferritin_low, (1-hb_low)*(1-ferritin_low)]
    mixed = [(1-independently_drawn)*v + independently_drawn*w
             for v,w in zip(weighted, independent)]
    return source, weighted, mixed


def measures(cells):
    both, hb_only, ferritin_only, neither = cells
    return float(both*neither/(hb_only*ferritin_only)), float(100*both)


def decorate(ax):
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=2.5, color=RULE, pad=2, labelcolor=MUTED)
    for sp in ["top","right","left"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(RULE)


def label_panel(ax, letter, title):
    ax.set_title(f"{letter}   {title}", loc="left", fontsize=8.25, weight="bold",
                 color=INK, pad=5)


def plot_steps(ax, stage_metrics, i):
    """Solid line traces law A; law B retains its source summary throughout."""
    decorate(ax)
    ax.spines["bottom"].set_visible(False)
    for y in (stage_metrics[0][i], stage_metrics[-1][i]):
        ax.axhline(y, color=RULE, linewidth=0.5, zorder=0)
    y = [m[i] for m in stage_metrics]
    # Marker styles separate overlapping laws at the original table and in OR.
    ax.plot([0,1,2],[y[0]]*3, color=B, linestyle=(0,(3,2)), linewidth=1.15,
            marker="^", markerfacecolor=B, markeredgecolor="white",
            markeredgewidth=0.35, ms=5.5, zorder=2)
    ax.plot([0,1,2],y, color=A, linewidth=1.15, marker="o", ms=4.5,
            markerfacecolor="white", markeredgecolor=A, markeredgewidth=1.15, zorder=3)
    ax.set_xlim(-0.25,2.24)
    ax.set_xticks([0,1,2], ["Zhu source","Weight low-ferritin\ncells by ⅔","Redraw 20%\nof Hb values"])
    ax.tick_params(axis="x", length=0, pad=1.25, labelcolor=INK)
    ax.set_yticks([])
    if i == 0:
        ax.set_ylim(3.99,7.34)
    else:
        ax.set_ylim(5.8,11.6)
    for x, val in enumerate(y):
        text = f"{val:.3f}" if i==0 else f"{val:.3f}%"
        offset = -8 if x==0 else 5
        va = "top" if offset<0 else "bottom"
        ax.annotate(text,(x,val),xytext=(0,offset),textcoords="offset points",
                    ha="center",va=va,fontsize=7.25,color=A if x else INK,
                    bbox={"facecolor":"white","edgecolor":"none","pad":0.2,"alpha":0.9})
    ax.annotate(f"{y[0]:.3f}"+("%" if i else ""),(2,y[0]),xytext=(0,4),
                textcoords="offset points",ha="center",va="bottom",
                fontsize=7.25,color=B)


def plot_deliveries(ax,key,cfg,i):
    reference=cfg["measured_reference"][key]
    scale=100 if key=="joint_prevalence" else 1
    decorate(ax)
    low,high=[v*scale for v in reference["ci95"]]
    x=reference["estimate"]*scale
    ax.grid(axis="x",color=RULE,lw=.56)
    ax.plot([low,high],[2,2],lw=1.7,color=INK,solid_capstyle="butt")
    ax.scatter([x],[2],s=20,color=INK,marker="D",zorder=4)
    for author,row in (("A",1),("B",0)):
        for seed,shift in zip((5101,5102,5103),(-.14,0,.14)):
            xvalue=cfg["deliveries"][f"{author}_{seed}"]["estimands"][key]*scale
            ax.scatter(xvalue,row+shift,s=19,color=COLORS[author],
                       edgecolors="white",linewidths=.35,marker=MARKERS[author],zorder=4)
    ax.set_ylim(-.45,2.35)
    ax.set_yticks([2,1,0],["NHANES","Law A","Law B"] if i==0 else ["","",""])
    ax.tick_params(axis="y",length=0,labelcolor=INK)
    if i==0:
        ax.set_xscale("log")
        ax.set_xlim(4,37)
        ax.set_xticks([5,10,20,30])
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xlabel("Odds ratio (log scale)")
    elif i==1:
        ax.set_xlim(5.6,10.9)
        ax.set_xticks([6,7,8,9,10])
        ax.set_xlabel("Both low (%)")
    else:
        ax.set_xlim(.12,.5)
        ax.set_xticks([.2,.3,.4,.5])
        ax.set_xlabel("Spearman correlation")


def draw(cfg):
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.25,
                         "axes.labelsize":7.25,"axes.labelcolor":INK,"xtick.labelsize":7,
                         "ytick.labelsize":7,"pdf.fonttype":42,"axes.linewidth":.7,
                         "pdf.compression":6})
    fig=plt.figure(figsize=(7,3.8),facecolor="white")
    fig.text(.015,.983,"Model implications of the target rules",ha="left",va="top",
             fontsize=9.5,color=INK,weight="bold")
    handles=[Line2D([0],[0],color=A,marker="o",mfc="white",ms=4.1,lw=1.2,
                    label="Law A (two changes)"),
             Line2D([0],[0],color=B,marker="^",ms=4.2,lw=1.1,ls="--",label="Law B (source retained)")]
    fig.legend(handles=handles,loc="upper right",bbox_to_anchor=(.992,1.0),ncols=2,
               frameon=False,handlelength=1.2,columnspacing=1.0,
               handletextpad=.4,fontsize=7.0,labelcolor=INK)
    fig.add_artist(Line2D([.015,.985],[.91,.91],transform=fig.transFigure,color=RULE,lw=.7))
    upper=fig.add_gridspec(1,2,left=.039,right=.983,bottom=.612,top=.806,wspace=.16)
    m=[measures(c) for c in stage_probabilities(cfg)]
    for i,title in enumerate(("Threshold odds ratio","Joint low prevalence")):
        ax=fig.add_subplot(upper[0,i]);plot_steps(ax,m,i);label_panel(ax,"ab"[i],title)
    fig.text(.015,.466,"Analyses of the same six delivered tables",ha="left",va="top",
             fontsize=9.5,color=INK,weight="bold")
    handle=Line2D([0],[0],color=INK,marker="D",ms=4.0,lw=1.4,
                  label="NHANES estimate and 95% survey CI")
    fig.legend(handles=[handle],loc="upper right",bbox_to_anchor=(.992,.48),
               frameon=False,handlelength=1.8,fontsize=7.05,labelcolor=INK,handletextpad=.45)
    fig.add_artist(Line2D([.015,.985],[.399,.399],transform=fig.transFigure,color=RULE,lw=.7))
    lower=fig.add_gridspec(1,3,left=.085,right=.976,bottom=.113,top=.308,wspace=.21)
    for i,(key,title) in enumerate((("odds_ratio","Threshold association"),
                     ("joint_prevalence","Joint burden"),("spearman","Continuous ranks"))):
        ax=fig.add_subplot(lower[0,i]);plot_deliveries(ax,key,cfg,i);label_panel(ax,"cde"[i],title)
    fig.savefig(HERE/(STEM+".pdf"),metadata={"Title":"Iron status in source-based models and delivered cohorts",
                "Author":None,"CreationDate":None,"ModDate":None})
    fig.savefig(HERE/(STEM+".png"),dpi=300)
    plt.close(fig)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-repo",type=Path)
    args=parser.parse_args()
    config=json.loads((HERE/"fig3-iron-inputs.json").read_text(encoding="utf-8"))
    if args.verify_repo:
        verify_blobs(config,args.verify_repo)
    draw(config)

