"""Paper figure from public study aggregates. The two markers are two survey periods."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

HERE=Path(__file__).resolve().parent
read=lambda name:json.loads((HERE/name).read_text(encoding="utf-8"))
INK="#20364e"; BLUE="#315b8e"; PLUM="#765186"; ORANGE="#a54a2e"; GREY="#62748a"; LIGHT="#dce3eb"
plt.rcParams.update({"font.family":"Arial","font.size":8,"text.color":INK,"axes.labelcolor":INK,
                     "axes.edgecolor":"#a9b5c0","xtick.color":GREY,"ytick.color":INK,
                     "axes.spines.right":False,"axes.spines.top":False,"pdf.fonttype":42})


def make_figure():
    result=read("RESULTS.json")
    audit=read("PAIRING_DIAGNOSTIC.json")
    rows=audit["by_pairing"]
    fig=plt.figure(figsize=(8.15,3.67))
    ax=fig.add_axes([.19,.26,.225,.51])
    bx=fig.add_axes([.64,.227,.32,.57])
    fig.text(.019,.926,"A   Did the two historical means help?",fontsize=10.4,weight="bold")
    fig.text(.495,.926,"B   Did the answer depend on the pairing?",fontsize=10.4,weight="bold")
    fig.text(.019,.835,"Fraction with non-HDL ≥160 mg/dL",size=7.45,color=GREY)
    ax.set(xlim=(18,38),ylim=(-.57,3.55),xticks=[20,25,30,35],yticks=[3,2,1,0],
           yticklabels=["Base model","With US means","2017–2018","2021–2023"])
    ax.set_axisbelow(True);ax.grid(axis="x",color=LIGHT,lw=.45)
    ax.axhline(1.5,color=LIGHT,lw=.7)
    vals=rows["nominal"]
    ax.scatter(vals["before_pct"],3,s=32,marker="o",color=BLUE,zorder=3)
    ax.scatter(vals["after_pct"],2,s=33,marker="s",color=PLUM,zorder=3)
    ax.text(vals["before_pct"]+.7,3.10,f"{vals['before_pct']:.2f}%",size=7.2,color=BLUE)
    ax.text(vals["after_pct"]+.28,2.27,f"{vals['after_pct']:.2f}%",size=7.2,color=PLUM,ha="center")
    for y,key in [(1,"J"),(0,"L")]:
        d=result["reference"][key]["estimates"]["nonhdl160"]
        ax.plot(d["ci"],[y,y],lw=1.3,color=INK,marker="|",ms=4.7)
        ax.plot(d["estimate"],y,marker="D",ms=4,color=INK)
        ax.text(d["estimate"],y+.24,f"{d['estimate']:.2f}%",size=7.15,ha="center")
    ax.set_xlabel("Screening prevalence (%)",labelpad=5,size=7.6)
    ax.tick_params(axis="y",length=0,pad=4)
    ax.spines["left"].set_visible(False)

    order=["nominal"]+[audit["ordered_within_author"][f"author{i}"][tag] for i in range(1,5) for tag in ("lower","higher")]
    names=["Original"]+[label for i in range(1,5) for label in (f"Author {i}  lower",f"             higher")]
    yvals=[0,1.65,2.58,4.1,5.03,6.55,7.48,9.0,9.93]
    bx.axvspan(-2.,2.,color="#eef0f4")
    bx.axvline(0,color="#8895a5",lw=.8)
    for x in (-10,-5,5,10,15):bx.axvline(x,color=LIGHT,lw=.4,zorder=0)
    for name,y in zip(order,yvals):
        j=rows[name]["gain"]["J"]["gain_pp"];l=rows[name]["gain"]["L"]["gain_pp"]
        bx.plot([j,l],[y,y],color="#8b99aa",lw=1.4)
        if abs(j-l)<.02:
            bx.plot(j,y,marker="o",ms=6.0,color=BLUE,mec=BLUE)
            bx.plot(l,y,marker="s",ms=3.0,mfc="white",mec=ORANGE,mew=1)
        else:
            bx.plot(j,y,marker="o",ms=4.3,color=BLUE)
            bx.plot(l,y,marker="s",ms=3.8,mfc="white",mec=ORANGE,mew=1.1)
    bx.set(xlim=(-13.2,17.0),ylim=(10.7,-.78),xticks=[-10,-5,0,5,10,15],yticks=yvals,yticklabels=names)
    bx.spines["left"].set_visible(False);bx.tick_params(axis="y",length=0,pad=4,labelsize=7.15)
    bx.set_xlabel("Reduction in absolute error (percentage points)",size=7.8,labelpad=4)
    fig.legend(handles=[Line2D([],[],marker="o",ms=4,color=BLUE,linestyle="none",label="2017–2018"),
                        Line2D([],[],marker="s",ms=3.8,mfc="white",mec=ORANGE,linestyle="none",label="2021–2023")],
               frameon=False,ncol=2,loc="center",bbox_to_anchor=(.787,.84),fontsize=7.2,columnspacing=1.2,handletextpad=.3)
    fig.text(.019,.071,"Bars are survey-design 95% intervals. Shading in B marks ±2 points. All four new authors and the rule gave the same estimates.",size=7.2,color=GREY)
    fig.text(.019,.024,"Lower and higher refer to each earlier author’s two source-only screening rates. Positive values in B indicate closer agreement.",size=7.2,color=GREY)
    folder=HERE/"figures";folder.mkdir(exist_ok=True)
    for ext in ("png","pdf"):
        fig.savefig(folder/("historical-means-and-pairing."+ext),dpi=200,facecolor="white")
    plt.close(fig)


if __name__=="__main__":
    make_figure()
