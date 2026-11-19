"""Plot the same six parent models before and after one additional source statistic."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

ROOT=Path(__file__).resolve().parent


def read(n):
    return json.loads((ROOT/n).read_text(encoding="utf8"))


def draw():
    result=read("RESULTS.json")
    supplement=read("A_SUPPLEMENT.json")
    ordered=[f"{arm}{i}" for arm in ("ordinary","workflow") for i in range(1,4)]
    if not any(v.get("complete") for v in result["pairs"].values()):
        return
    ref=result["reference"]
    fig, axes=plt.subplots(1,2,figsize=(8.8,3.7),sharey=True)
    fig.subplots_adjust(left=.16,right=.985,top=.74,bottom=.22,wspace=.23)
    panels=[("conditional_ratio",supplement["estimate"],supplement["province_stratified_community_bootstrap_95pct"],
             "A   Supplied conditional statistic","Within-band ferritin geometric-mean ratio"),
            ("rank",ref["rank"],ref["rank_interval"],"B   Held-out scientific analysis","Whole-cohort Hb–ferritin Spearman correlation")]
    for ax,(field,target,ci,title,xlab) in zip(axes,panels):
        ax.axvspan(ci[0],ci[1],color="#DCE5EF",alpha=.70,lw=0)
        ax.axvline(target,color="#465C79",lw=1.2)
        ax.axhline(2.5,color="#C8CCD3",lw=.7)
        for j,p in enumerate(ordered):
            row=result["pairs"][p]
            if not row.get("complete"):
                ax.text(.02,j,"incomplete",transform=ax.get_yaxis_transform(),va="center",fontsize=8,color="#777")
                continue
            xs=[row["estimates"][arm][field] for arm in ("initial","control","evidence")]
            if xs[1] is None or xs[2] is None:
                ax.text(.02,j,"undefined",transform=ax.get_yaxis_transform(),va="center",fontsize=8,color="#777")
                continue
            ax.plot(xs[1:], [j,j],color="#918A90",lw=1.6,zorder=2)
            if xs[0] is not None:
                ax.plot(xs[0],j-.16,"|",ms=7,mew=1.2,color="#494550",zorder=3)
            ax.scatter(xs[1],j,s=31,facecolor="white",edgecolor="#5C4B8A",linewidth=1.45,zorder=4)
            ax.scatter(xs[2],j,s=22,color="#C04F2B",zorder=5)
        ax.set_title(title,fontsize=10.5,fontweight="bold",loc="left",pad=10)
        ax.set_xlabel(xlab,fontsize=8.5,labelpad=6)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.spines[["top","right","left"]].set_visible(False)
        ax.spines["bottom"].set_color("#A4A3AD")
        ax.tick_params(axis="both",length=0,labelsize=8.5,pad=5)
    axes[0].set_yticks(range(6),["Ordinary  1","Ordinary  2","Ordinary  3","Workflow  1","Workflow  2","Workflow  3"])
    axes[0].set_ylim(5.6,-.65)
    legend=[Line2D([],[],marker="|",ls="",color="#494550",label="Initial law"),
            Line2D([],[],marker="o",ms=5.5,ls="",mfc="white",mec="#5C4B8A",label="Revision, original evidence"),
            Line2D([],[],marker="o",ms=5.5,ls="",color="#C04F2B",label="Revision, added evidence"),
            Line2D([],[],lw=5,color="#DCE5EF",label="Measured 95% interval")]
    fig.legend(handles=legend,loc="upper center",bbox_to_anchor=(.54,.975),ncol=4,frameon=False,fontsize=8,handlelength=1.15,columnspacing=1.5)
    for ext in ("pdf","png"):
        fig.savefig(ROOT/("conditional_iron."+ext),dpi=230,bbox_inches="tight",pad_inches=.12)
    plt.close(fig)


if __name__=="__main__":
    draw()
