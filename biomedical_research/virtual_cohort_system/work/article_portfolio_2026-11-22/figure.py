"""Draw the registered authoring comparison and the post-outcome iron rank calculation."""
from collections import Counter
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
WORK = HERE.parent


def read(p):
    return json.loads(p.read_text(encoding="utf8"))


def make():
    lipid=read(WORK/"article_pairing_2026-11-22/RESULTS.json")["primary"]
    lung=read(WORK/"article_lung_pairing_2026-11-22/RESULTS.json")["primary"]
    iron=read(HERE/"iron/RESULTS.json")
    audit=read(HERE/"iron/RANK_AUDIT.json")
    counts=[(lipid["ordinary_material"],lipid["alternative_material"]),
            (lung["ordinary_material"],lung["targeted_material"]),
            (iron["primary"]["ordinary"],iron["primary"]["targeted"])]
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"pdf.fonttype":42,
                         "axes.spines.right":False,"axes.spines.top":False,
                         "axes.spines.left":False,"text.color":"#202631","xtick.color":"#414754","ytick.color":"#202631"})
    initial,ordinary,targeted="#6D7785","#345B9A","#BA4A28"
    fig,(a,b)=plt.subplots(1,2,figsize=(12.2,4.55),gridspec_kw={"width_ratios":[1,1.22]})
    fig.subplots_adjust(left=.105,bottom=.255,right=.965,top=.77,wspace=.49)
    for ax in (a,b):
        ax.set_axisbelow(True)
        ax.tick_params(axis="y",length=0,pad=7)
        ax.spines["bottom"].set_color("#A4ABB4")
        ax.tick_params(axis="x",color="#A4ABB4",length=3)
    a.set_title("A   How often did a second model change the analysis?",loc="left",fontsize=12.5,fontweight="bold",pad=23,x=-.24)
    a.text(-.24,1.045,"Matched author blocks per article",transform=a.transAxes,fontsize=10,color="#525B68")
    for k,(n,m) in enumerate(counts):
        for value,dy,color,mark in [(n,.13,ordinary,"o"),(m,-.13,targeted,"s")]:
            a.hlines(2-k+dy,0,value,color=color,alpha=.32,linewidth=2)
            a.scatter(value,2-k+dy,s=55,c=color,marker=mark,zorder=3)
            a.annotate(f"{value}/12",(value,2-k+dy),xytext=(7,0),textcoords="offset points",va="center",color=color,fontsize=9,fontweight="bold")
    a.set(xlim=(-.3,14),ylim=(-.46,2.45),xticks=[0,3,6,9,12],yticks=[2,1,0],yticklabels=["Lipids","Lung function","Iron status"],xlabel="Blocks crossing the prespecified change threshold")
    a.grid(axis="x",color="#E1E4EA",linewidth=.7)
    a.legend(handles=[Line2D([],[],color=ordinary,marker="o",lw=0,label="Ordinary second model"),
                      Line2D([],[],color=targeted,marker="s",lw=0,label="Targeted search")],
             loc="upper left",bbox_to_anchor=(-.25,-.28),ncol=2,frameon=False,handletextpad=.25,columnspacing=.8,fontsize=8.5)
    b.set_title("B   What changed in the iron models?",loc="left",fontsize=12.5,fontweight="bold",pad=23,x=-.06)
    b.text(-.06,1.045,"Every model gives the same crude odds ratio, 6.65.",transform=b.transAxes,fontsize=10,color="#525B68")
    low,high=audit["sharp_minimum"],audit["sharp_maximum"]
    exp=audit["conditional_random_pairing_expected_rho"]
    b.axvspan(low,high,color="#F1F3F7",zorder=0)
    for value in (low,high):
        b.axvline(value,color="#88919F",linestyle=(0,(3,3)),linewidth=1)
    for y,(role,col) in enumerate([("alternative",targeted),("ordinary",ordinary),("initial",initial)]):
        vals=Counter(round(v["requested"],8) for key,v in iron["models"].items() if key.endswith("_"+role) and v["usable"])
        clusters=[]
        for val in sorted(vals):
            if clusters and val-clusters[-1][-1]<.045:
                clusters[-1].append(val)
            else:
                clusters.append([val])
        for cluster in clusters:
            for i,val in enumerate(cluster):
                number=vals[val]
                ypos=y+.16*(i-(len(cluster)-1)/2)
                b.scatter(val,ypos,s=50+20*number,c=col,edgecolor="white",linewidth=.9,zorder=3)
                if number>1:
                    b.annotate(str(number),(val,ypos),ha="center",va="center",fontsize=8.5,color="white",fontweight="bold")
    b.set(xlim=(-.53,1.025),ylim=(-.58,2.56),yticks=[0,1,2],yticklabels=["Targeted","Ordinary","Initial"],
          xticks=[-.4,0,.25,.5,.75,.93],xticklabels=["−0.4","0","0.25","0.5","0.75","0.93"],
          xlabel="Continuous hemoglobin–ferritin Spearman correlation")
    b.tick_params(axis="y",pad=5)
    b.text(.01,-.36,"Shading spans the attainable range with the selected columns.\nNumerals count models with the same three-seed average.",
           transform=b.transAxes,fontsize=8.5,va="top",color="#555D69")
    assert low < exp < high
    fig.savefig(HERE/"article-comparison.pdf",bbox_inches="tight",pad_inches=.18,metadata={"Title":"Pairing choices and scientific analyses in three articles"})
    fig.savefig(HERE/"article-comparison.png",dpi=180,bbox_inches="tight",pad_inches=.18)
    plt.close(fig)


if __name__=="__main__":
    make()
