"""Compare both publications without treating blocks from different papers as pairs."""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE=Path(__file__).resolve().parent
LIPID=HERE.parent/"article_pairing_2026-11-22"
BLUE="#245d86";RUST="#a74d29";INK="#203646";MUTED="#536777"


def read(path):return json.loads(path.read_text(encoding="utf8"))


def outcomes():
    lipid=read(LIPID/"RESULTS.json");lung=read(HERE/"RESULTS.json")
    assert lipid["primary"]==read(LIPID/"VERIFICATION.json")["primary_verified"]
    assert lung["primary"]==read(HERE/"VERIFICATION.json")["primary"]
    for tag,data,threshold in (("Lipids",lipid,4),("Lung function",lung,5)):
        sets=[]
        for name,arms in sorted(data["blocks"].items()):
            row={}
            for arm,item in arms.items():
                row[arm]=None
                if tag=="Lipids" and item["both_valid"]:
                    row[arm]=item["second_pct"]-item["first_pct"]
                if tag=="Lung function" and item["valid"]:
                    row[arm]=item["gap_pp"]
            sets.append((name,row))
        pr=data["primary"]
        yield tag,threshold,sets,(pr["ordinary_material"],pr["alternative_material"] if tag=="Lipids" else pr["targeted_material"])


def main():
    series=list(outcomes())
    peak=max([6]+[abs(v) for _,_,rows,_ in series for name,row in rows for v in row.values() if v is not None])
    step=5 if peak<=30 else 10
    limit=(math.ceil(peak/step)*step)+.8
    fig,axes=plt.subplots(1,2,figsize=(9.4,4.8),sharex=True,sharey=True)
    fig.subplots_adjust(left=.085,right=.98,top=.74,bottom=.22,wspace=.12)
    fig.text(.065,.93,"Does a different pairing change the screening estimate?",
             fontsize=15,fontweight="bold",color=INK)
    plots=[Line2D([],[],ls="",marker=m,color=c,label=l,markersize=5.8)
           for m,c,l in (("o",BLUE,"Ordinary second model"),("D",RUST,"Search for an alternative pairing"))]
    fig.legend(handles=plots,loc="upper left",bbox_to_anchor=(.061,.901),ncol=2,
               frameon=False,fontsize=9,columnspacing=2,handletextpad=.35,borderaxespad=0)
    for ax,(title,threshold,rows,count) in zip(axes,series,strict=True):
        subtitle="Non-HDL ≥160 mg/dL" if title=="Lipids" else "FEV1/FVC <0.70"
        ax.set_title(title+"   ·   "+subtitle,loc="left",pad=12,color=INK,fontsize=11,fontweight="bold")
        ax.axvspan(-threshold,threshold,color="#edf1f5",zorder=-3)
        for x in (-threshold,threshold):ax.axvline(x,color="#748da0",ls=(0,(3,3)),lw=.8,zorder=-2)
        ax.axvline(0,color="#81919d",lw=.8,zorder=-1)
        for i,(n,row) in enumerate(rows):
            coords=[]
            for arm,delta,symbol,color in (("ordinary",-.07,"o",BLUE),("alternative",.07,"D",RUST)):
                point=row[arm]
                if point is not None:
                    coords.append((point,i+delta))
                    ax.scatter(point,i+delta,s=28,marker=symbol,color=color,edgecolor="white",linewidth=.5,zorder=3)
            if len(coords)==2:ax.plot(*zip(*coords),color="#abb9c2",lw=.85,zorder=1)
        ax.set_xlim(-limit,limit);ax.set_ylim(len(rows)-.5,-.5)
        ax.set_xticks(range(-int(limit//step)*step,int(limit//step)*step+1,step))
        ax.set_yticks(np.arange(len(rows)),[name for name,row in rows])
        ax.tick_params(length=2,colors=INK,labelsize=8)
        for s in ("top","left","right"):ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color("#95a4af")
        ax.text(.01,-.17,f"Material shifts  ·  ordinary {count[0]}/12, targeted {count[1]}/12",
                transform=ax.transAxes,color=INK,fontsize=8.6)
    fig.text(.53,.088,"Change from the shared starting estimate (percentage points)",ha="center",color=INK,fontsize=9.3)
    fig.text(.065,.034,"Shading marks each study's prespecified margin. Missing points indicate ineligible pairs. Blocks are matched only within a paper.",
             color=MUTED,fontsize=8.1)
    fig.savefig(HERE/"two-article-screening.png",dpi=190,facecolor="white")
    plt.close(fig)


if __name__=="__main__":main()
