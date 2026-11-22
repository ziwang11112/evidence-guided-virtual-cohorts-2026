"""Plot the two evidence conditions, matched rules and measured survey intervals in native units."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import numpy as np

HERE=Path(__file__).resolve().parent
colors={"M":"#976c41","J":"#bd512b","stat":"#58616e","US":"#284e82","MW":"#795884"}
rows=[("physical_uniform","Feasible random"),("M","Agent · marginals"),("J","Agent · joint evidence"),
      ("source_gaussian","Statistical · joint evidence"),("US_NHANES","US measurement"),("MW_ALHS_Y1","Malawi measurement")]
positions=[5.0,4.05,3.1,2.15,.85,-.1]
panels=[("mean_individual_ratio_pct","A","Mean individual ratio","FEV₁/FVC (%)"),
        ("below_070_pct","B","Below 0.70","Adults (%)"),
        ("within_sex_pearson","C","Volume association","Within-sex Pearson r")]


def main():
    p=json.loads((HERE/"PREDICTIONS.json").read_text(encoding="utf-8"))["methods"]
    r=json.loads((HERE/"RESULTS.json").read_text(encoding="utf-8"))["reference"]
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"pdf.fonttype":42,"axes.edgecolor":"#acb8c8",
                         "xtick.color":"#37485f","ytick.color":"#37485f","text.color":"#192b42",
                         "axes.labelcolor":"#293d58","axes.spines.top":False,"axes.spines.right":False})
    fig,axs=plt.subplots(1,3,figsize=(7.10,2.55),sharey=True)
    fig.subplots_adjust(left=.196,right=.985,bottom=.24,top=.83,wspace=.23)
    for ax,(key,letter,title,xlabel) in zip(axs,panels,strict=True):
        ax.text(0,1.12,letter+"  "+title,transform=ax.transAxes,weight="bold",size=8.4,ha="left")
        ax.axhspan(-.50,1.35,color="#f1f4f8",zorder=0)
        ax.grid(axis="x",color="#e0e5eb",lw=.65)
        for y,(name,_) in zip(positions,rows,strict=True):
            if name in ("M","J"):
                vals=[p[f"{name}{i}"]["values"][key] for i in range(1,5)]
                for j,(val,offset) in enumerate(zip(vals,[-.21,-.07,.07,.21],strict=True)):
                    ax.plot(val,y+offset,marker="o",ms=3.3,mec=colors[name],mew=.65,
                            mfc="white" if name=="M" else colors[name],linestyle="none",zorder=4)
            elif name in r:
                rec=r[name]["estimates"][key]; point=rec["estimate"]; lo,hi=rec["ci"]
                us=name=="US_NHANES"
                color=colors["US" if us else "MW"]
                ax.errorbar(point,y,xerr=[[point-lo],[hi-point]],fmt="s" if us else "^",color=color,ms=4.1,
                            elinewidth=1.15,capsize=2,zorder=4)
            else:
                ax.plot(p[name]["values"][key],y,marker="D",ms=4,mfc="white",mec=colors["stat"],linestyle="none",zorder=3)
        ax.set_xlabel(xlabel,labelpad=3)
        ax.set_ylim(-.6,5.55)
        ax.tick_params(axis="both",labelsize=7.1,length=2.3)
        ax.tick_params(axis="y",length=0)
        ax.spines["left"].set_visible(False)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4,steps=[1,2,2.5,5,10]))
        ax.margins(x=.10)
    axs[0].set_yticks(positions,[s for _,s in rows])
    fig.text(.196,.032,"Each small circle is one author. Measured bars are pointwise 95% intervals.",size=7,color="#40526a")
    fig.savefig(HERE/"spirometry-uses.pdf",metadata={"Title":"Scientific uses of source-built spirometry cohorts","CreationDate":None,"ModDate":None})
    fig.savefig(HERE/"spirometry-uses.png",dpi=250,metadata={"Software":"matplotlib"})
    plt.close(fig)


if __name__=="__main__":
    main()
