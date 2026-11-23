"""Draw the two primary BMI analyses using only the immutable aggregate report."""
from hashlib import sha256
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import StrMethodFormatter
import numpy as np


HERE = Path(__file__).resolve().parent
INK = "#172B42"
BLUE = "#265FAC"
RUST = "#9C492F"
MUTED = "#56677A"
BAND = "#E6ECF4"


def draw(report):
    plt.rcParams.update({"font.family":"Arial","font.size":9,"pdf.fonttype":42,
                         "axes.unicode_minus":True,"axes.labelcolor":INK,
                         "text.color":INK,"xtick.color":MUTED,"ytick.color":INK})
    fig, axes = plt.subplots(1,2,figsize=(9.0,4.95),sharey=True)
    fig.subplots_adjust(left=.119,right=.98,top=.735,bottom=.235,wspace=.225)
    fig.text(.032,.948,"Same virtual people, two BMI analyses",fontsize=18.5,fontweight="bold",va="center")
    n = report["measured"]["n_complete"]
    count = report["assigned"]
    fig.text(.034,.878,f"{n:,} measured participants  ·  {count} independently assigned GPT constructors  ·  primary models",
             fontsize=10.2,color=MUTED,va="center")
    authors = report["authors"]
    assert count == len(authors) and [a["slot"] for a in authors] == ["a01","a02","a03","a04","a05","a06"]
    positions = [6.25,5,4,3,2,1,0]
    labels = ["Measured"] + [entry["slot"].upper() for entry in authors]
    specs = [
        ("A","Mean signed BMI error","mean_difference","Self-reported minus measured BMI (kg/m²)",
         (-.45,.48),[-.4,-.2,0,.2,.4]),
        ("B","Under-reporting by more than 2 kg/m²","strictly_below_pct","Participants (%)",
         (0,21),[0,5,10,15,20]),
    ]
    for ax,(panel,title,key,xlabel,xlim,xticks) in zip(axes,specs):
        obs = report["measured"][key]
        lo,hi = report["measured"]["paired_bootstrap"]["interval_95"][key]
        tol = report["tolerances"][key]
        ax.set_xlim(*xlim)
        ax.set_ylim(-.55,6.82)
        ax.set_xticks(xticks)
        ax.axvspan(obs-tol,obs+tol,color=BAND,zorder=0)
        ax.axvline(obs,color=RUST,alpha=.44,ls=(0,(2,3)),lw=1,zorder=1)
        for y in positions[1:]:
            ax.axhline(y,color="#D5DEE8",lw=.46,zorder=.5)
        ax.axhline(5.62,color="#9CAAB9",lw=.75,zorder=1)
        ax.errorbar(obs,positions[0],xerr=[[obs-lo],[hi-obs]],fmt="D",markersize=5.7,
                    color=RUST,elinewidth=1.7,capsize=3,zorder=4)
        delta = xlim[1]-xlim[0]
        ax.text(hi+.028*delta,positions[0],f"{obs:.2f}"+("%" if key=="strictly_below_pct" else ""),
                fontweight="bold",va="center",color=RUST,fontsize=9)
        for y,author in zip(positions[1:],authors):
            runs = [r["science"][key] for r in author["tables"] if r["scenario"]=="primary" and r["score_status"]=="scored"]
            if len(runs) != 3:
                assert author["status"] != "three_primary_seeds_scored"
                ax.text(.45,y,"No table",transform=ax.get_yaxis_transform(),va="center",
                        fontsize=8,color=MUTED,style="italic",
                        bbox={"facecolor":"white","edgecolor":"none","pad":1.5},zorder=3)
                continue
            median = float(np.median(runs))
            assert np.isclose(median,author["primary_seed_median"][key],rtol=0,atol=1e-12)
            ax.errorbar(median,y,xerr=[[median-min(runs)],[max(runs)-median]],fmt="o",markersize=5.7,
                        color=BLUE,elinewidth=1.6,capsize=3,zorder=3)
            display = 0.0 if abs(median)<.005 else median
            ax.text(max(runs)+.025*delta,y,f"{display:.2f}"+("%" if key=="strictly_below_pct" else ""),
                    va="center",fontsize=8.4,color=BLUE)
        ax.text(0,1.095,panel,transform=ax.transAxes,size=11.5,fontweight="bold",va="center",color=BLUE)
        ax.text(.075,1.095,title,transform=ax.transAxes,size=11.4,fontweight="bold",va="center")
        ax.set_xlabel(xlabel,labelpad=7.0)
        ax.tick_params(axis="y",length=0,pad=7.5)
        ax.tick_params(axis="x",length=3,pad=4,labelsize=8)
        for side in ("left","right","top"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_edgecolor("#728498")
        ax.set_yticks(positions,labels=labels)
    axes[0].get_yticklabels()[0].set_fontweight("bold")
    axes[0].xaxis.set_major_formatter(StrMethodFormatter("{x:.1f}"))
    legend = [Line2D([],[],marker="D",ms=5.3,color=RUST,lw=1.5,label="Measured estimate and 95% bootstrap interval"),
              Line2D([],[],marker="o",ms=5.2,color=BLUE,lw=1.5,label="GPT median and range across three seeds"),
              Patch(color=BAND,label="Prespecified tolerance")]
    fig.legend(handles=legend,loc="lower center",bbox_to_anchor=(.5,.066),ncols=3,frameon=False,
               handlelength=1.7,fontsize=8.1,columnspacing=1.65,handletextpad=.55)
    fig.text(.5,.035,"Tolerance around the measured result: ±0.30 kg/m² for mean error and ±3 percentage points for under-reporting.",
             ha="center",fontsize=8.15,color=MUTED)
    return fig


if __name__=="__main__":
    source=HERE/"AGGREGATES.json"
    original=source.read_bytes()
    f=draw(json.loads(original))
    f.savefig(HERE/"FIGURE.png",dpi=220,facecolor="white")
    f.savefig(HERE/"FIGURE.pdf",facecolor="white",metadata={"Title":"Same virtual people, two BMI analyses",
              "Subject":"Source AGGREGATES.json SHA256 "+sha256(original).hexdigest()})
    plt.close(f)
    assert original==source.read_bytes()
