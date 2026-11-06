"""Plot the three prespecified scientific analyses from reviewed aggregates."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter,LogLocator
BASE=Path(__file__).resolve().parent
SPECS=[("odds_ratio","Threshold association","Odds ratio (log scale)",1),("joint_prevalence","Joint burden","Both biomarkers low (%)",100),("spearman","Continuous dependence","Spearman correlation",1)]
COL=["#334155","#3A59AB","#C05B32"]

def main():
    tar=json.loads((BASE/"evaluation/TARGET.json").read_text())
    syn=json.loads((BASE/"evaluation/SYNTHETIC.json").read_text())
    fig,axes=plt.subplots(1,3,figsize=(9.7,2.55),layout="constrained",sharey=True)
    for i,(key,title,label,scale) in enumerate(SPECS):
        ax=axes[i];t=tar["estimands"][key]
        if t["estimate"] is not None: ax.scatter(t["estimate"]*scale,2,marker="D",s=27,color=COL[0],zorder=4)
        if t["ci95"]: ax.plot(np.array(t["ci95"])*scale,[2,2],lw=1.5,color=COL[0])
        for j,author in enumerate("AB"):
            row=1-j
            for k,seed in enumerate((5101,5102,5103)):
                v=syn[f"{author}_{seed}"]["estimands"][key]["estimate"]
                if v is not None: ax.scatter(v*scale,row+(k-1)*.09,s=22,color=COL[j+1],zorder=3,alpha=.85)
        if key=="odds_ratio":
            ax.set_xscale("log")
            ax.xaxis.set_major_locator(LogLocator(numticks=8,subs=(1,2,5)))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:g}"))
            ax.xaxis.set_minor_formatter(FuncFormatter(lambda *_:""))
        ax.set_yticks([2,1,0],labels=["NHANES","Law A","Law B"])
        ax.set_ylim(-.46,2.45)
        ax.set_xlabel(label,fontsize=9)
        ax.set_title("ABC"[i]+"   "+title,loc="left",fontweight="semibold",fontsize=10)
        ax.grid(axis="x",alpha=.22);ax.tick_params(length=0,labelsize=8)
        ax.spines[["top","left","right"]].set_visible(False)
        ax.spines["bottom"].set_color("#CBD5E1")
    path=BASE/"figures";path.mkdir(exist_ok=True)
    for fmt in ["pdf","png"]:fig.savefig(path/("IRON_UTILITY."+fmt),dpi=220,bbox_inches="tight")
    plt.close(fig)
if __name__=="__main__":main()
