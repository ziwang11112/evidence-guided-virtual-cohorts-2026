"""Plot all three matched sets of scientific models and the measured reference."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
load=lambda f: json.loads((ROOT/f).read_text(encoding="utf8"))


def plot(destination):
    laws=load("SCIENTIFIC_RESULTS.json")["laws"]
    target=load("REVEAL.json")["result"]
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9.2,"pdf.fonttype":42,"axes.spines.top":False,"axes.spines.right":False})
    fig,axs=plt.subplots(1,2,figsize=(7.15,3.05))
    colors=["#273E77","#9C6420","#794381"]
    markers=["o","s","^"]
    lines=[Line2D([],[],marker=m,color=c,linestyle="none",label=l,markersize=5.6) for m,c,l in zip(markers,colors,["Primary","Ordinary alternative","Sensitivity-directed"])]
    lines.append(Line2D([],[],marker="D",color="#454C57",linestyle="none",label="Statistical",markersize=5.2))
    fig.legend(handles=lines,loc="lower center",bbox_to_anchor=(.5,.005),frameon=False,ncol=4,columnspacing=1.05,handletextpad=.25,fontsize=8.3)
    for j,(ax,key,label) in enumerate(zip(axs,["odds_ratio","spearman"],["Crude anemia odds ratio","Hemoglobin–ferritin Spearman ρ"])):
        ax.set_title(["a","b"][j]+"   "+label,loc="left",weight="bold",fontsize=10.1,pad=10)
        for i,p in enumerate(["P1","P2","P3"]):
            for offset,n,m,c in zip([-.17,0,.17],[p,p+"_ordinary",p+"_directed"],markers,colors):
                row=laws.get(n,{})
                if row.get(key) is None:continue
                v=row[key]; ax.scatter(v,i+offset,s=33,marker=m,facecolors=c if row["tier2"] else "white",edgecolors=c,zorder=4,linewidths=1.05)
                if key=="spearman":ax.plot([v-1.96*row["rank_mcse"],v+1.96*row["rank_mcse"]],[i+offset]*2,color=c,lw=.9,zorder=2)
        s=laws.get("statistical",{})
        if s.get(key) is not None:ax.scatter(s[key],3,marker="D",s=29,c="#454C57",zorder=4)
        val=target["weighted"][j]; ci=target["weighted_cluster_bootstrap"][j]["percentile95"]
        if val is not None:
            if ci:ax.plot(ci,[4,4],color="#1F2937",lw=1.6,zorder=2)
            ax.scatter(val,4,marker="x",s=41,c="#1F2937",linewidths=1.4,zorder=4)
        else:ax.text(.03,4,"No low ferritin",transform=ax.get_yaxis_transform(),fontsize=8,va="center")
        if j==0:
            ax.axvline(173*1082/(85*331),ls="--",lw=1,color="#737986",zorder=0)
            ax.set_xlim(5.5,7.5); ax.set_xticks([5.5,6,6.5,7,7.5]); ax.set_xlabel("Odds ratio")
        else:ax.set_xlabel("Rank correlation")
        ax.axhline(3.5,lw=.65,color="#C5CBD4")
        ax.set_yticks([0,1,2,3,4],["Parent 1","Parent 2","Parent 3","Statistical","Measured"])
        ax.set_ylim(4.45,-.5);ax.grid(axis="x",alpha=.25);ax.tick_params(axis="y",length=0,pad=4)
        ax.spines["left"].set_visible(False);ax.spines["bottom"].set_color("#858993")
        ax.tick_params(axis="both",labelsize=8)
    fig.subplots_adjust(left=.105,right=.985,top=.85,bottom=.28,wspace=.50)
    fig.savefig(destination,bbox_inches="tight",pad_inches=.045)
    plt.close(fig)


if __name__=="__main__":
    import sys
    plot(sys.argv[1])
