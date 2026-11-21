"""Paper figures generated only from the released aggregates."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/"figures"
NAVY="#18324f"; BLUE="#285b90"; PURPLE="#654384"; RUST="#ae4b2e"; GRAY="#6a7b90"
PALE="#dce6f0"; CREAM="#fffaf2"; GRID="#dde4eb"
plt.rcParams.update({"font.family":"Arial","font.size":8.2,"text.color":NAVY,"axes.labelcolor":NAVY,
                     "xtick.color":"#43596f","ytick.color":"#43596f","axes.edgecolor":"#9fadc0",
                     "axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42})
RANKS=LinearSegmentedColormap.from_list("rank",["#2a4b73","#6682aa","#aabbd5","#e4eaf1","#f8f5f0"])
def read(name):
    return json.loads((HERE/name).read_text(encoding="utf-8"))


def save(fig,name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT/(name+".png"),dpi=190,facecolor="white")
    fig.savefig(OUT/(name+".pdf"),facecolor="white")
    plt.close(fig)


def use_figure():
    result=read("RESULTS.json")["estimates"]["all"]["scales"]["1.0"]
    sessions=read("DECISION_CLOSURE.json")["sessions"]
    stats=read("STATISTICAL_DECISION.json")["ranking"]
    order=["mean_nonhdl","tc_high","mean_ratio","hdl_low","rank_tc_hdl","nonhdl160"]
    names=["Non-HDL mean","High TC (%)","Mean TC/HDL","Low HDL (%)","TC–HDL rank corr.","Non-HDL ≥160 (%)"]
    fig=plt.figure(figsize=(8.60,3.25))
    left=fig.add_axes([.204,.255,.279,.532])
    right=fig.add_axes([.551,.255,.308,.532])
    table=fig.add_axes([.867,.255,.125,.532])
    mat=[]
    for k in order:
        ranks=[]
        for arm in ("reduced","full"):
            choices={s["decision"]["ranking"].index(k)+1 for s in sessions.values() if s["valid"] and s["arm"]==arm}
            assert len(choices)==1
            ranks.append(choices.pop())
        ranks.append(stats.index(k)+1)
        mat.append(ranks)
    left.imshow(mat,cmap=RANKS,vmin=1,vmax=6,aspect="auto",interpolation="nearest")
    for i,row in enumerate(mat):
        for j,v in enumerate(row):
            left.text(j,i,str(v),ha="center",va="center",color="white" if v<=2 else NAVY,weight="bold",size=8.8)
    for i in np.arange(.5,5.7,1): left.axhline(i,color="white",lw=1.4)
    for j in (.5,1.5): left.axvline(j,color="white",lw=1.4)
    left.set(yticks=range(6),yticklabels=names,xticks=range(3),xticklabels=["Base\npacket","+ Pairing\nscenarios","Statistical\nrule"])
    left.tick_params(length=0,pad=4)
    for sp in left.spines.values():sp.set_visible(False)
    right.set(ylim=(5.5,-.5),xlim=(-13.1,2.1),yticks=[],xticks=[-12,-8,-4,0])
    right.set_axisbelow(True);right.grid(axis="x",color=GRID,lw=.55)
    right.axvspan(-1,1,color=PALE,zorder=0);right.axvline(0,ls=":",lw=1,color=GRAY)
    table.set(xlim=(0,1),ylim=(5.5,-.5));table.axis("off")
    for i,k in enumerate(order):
        e=result[k];lo,hi=np.array(e["difference_ci"])/e["tolerance"];point=e["difference"]/e["tolerance"]
        color=RUST if e["status"]=="contradicted" else BLUE
        right.plot([lo,hi],[i,i],lw=1.45,color=color)
        right.plot([lo,hi],[i,i],linestyle="none",marker="|",color=color,ms=4.2)
        right.plot(point,i,marker="o" if e["status"]=="contradicted" else "D",mfc=color if e["status"]=="contradicted" else "white",mec=color,ms=4.3)
        digits=2 if k in ("mean_ratio","rank_tc_hdl") else 1
        table.text(.5,i,f"{e['virtual']:.{digits}f} → {e['measured']:.{digits}f}",ha="center",va="center",fontsize=7.2)
    right.spines["left"].set_visible(False)
    right.set_xlabel("Virtual minus measured, in units of tolerance",fontsize=8)
    fig.text(.028,.918,"A   Which analysis came first?",size=11,weight="bold")
    fig.text(.551,.918,"B   What did the target show?",size=11,weight="bold")
    fig.text(.028,.837,"Rank 1 = highest priority",fontsize=8,color=GRAY)
    fig.text(.925,.837,"Virtual → measured",ha="center",size=7.2,color=GRAY)
    fig.text(.028,.056,"Four GPT sessions per packet. All four agreed on the full ordering within each arm.",size=7.6,color=GRAY)
    fig.text(.55,.056,"Shading = planning tolerance. Bars = 95% reference intervals.",size=7.5,color=GRAY)
    save(fig,"decisions-before-disclosure")


def feasibility_figure():
    audit=read("PAIRING_AUDIT.json")
    rows=audit["three_frames_and_two_nested_counties"]
    sites=["mekelle","workers","Virginia"]
    labels=["Mekelle residents","Haramaya staff","Virginia screening"]
    fig=plt.figure(figsize=(8.6,3.12))
    a=fig.add_axes([.185,.245,.347,.54])
    b=fig.add_axes([.665,.245,.306,.54])
    outer=audit["outer"];inner=audit["feasible_ranges"]["numerical"]
    a.axvspan(*outer,color="#e7e7ec",zorder=0)
    a.axvspan(*inner,color="#e0e8f4",zorder=1)
    for k in outer:
        a.axvline(k,color=PURPLE,ls=":",lw=1.25,zorder=2)
    for i,site in enumerate(sites):
        d=rows[site];y=2-i
        pp=d["pct"];lo,hi=d["ci"];col=RUST if site=="Virginia" else BLUE
        a.plot([lo,hi],[y,y],lw=2,color=col,zorder=4)
        a.plot([lo,hi],[y,y],ls="none",marker="|",ms=5,color=col,zorder=4)
        a.plot(pp,y,"D",ms=4.8,color=col,zorder=4)
        a.text(pp,y+.19,f"{pp:.1f}%",ha="center",fontsize=7,weight="bold",color=col)
    a.set(yticks=[2,1,0],yticklabels=labels,ylim=(-.55,2.65),xlim=(6.5,53),xticks=[10,20,30,40,50],
          xlabel="Non-HDL ≥160 mg/dL (%)")
    a.tick_params(axis="y",length=0)
    a.spines["left"].set_visible(False)
    for i,site in enumerate(sites):
        d=rows[site];y=2-i
        x=d["target_minus_source_TC_mg_dl"];z=d["source_minus_target_HDL_mg_dl"]
        for dx,offset,col in ((x,-.105,BLUE),(z,.105,PURPLE)):
            b.barh(y+offset,dx,height=.16,color=col,alpha=.88)
        b.plot(x+z,y,"D",ms=4.2,mfc="white",mec=NAVY,mew=1)
        b.text(38.2,y,f"{x+z:+.1f}",ha="right",va="center",fontsize=7.7,weight="bold")
    b.set(yticks=[2,1,0],yticklabels=["Mekelle","Haramaya","Virginia"],ylim=(-.55,2.65),xlim=(-9,39.5),
          xticks=[-5,0,10,20,30],xlabel="Measured minus source mean (mg/dL)")
    b.tick_params(axis="y",length=0);b.spines["left"].set_visible(False)
    b.axvline(0,color="#8697aa",lw=.75)
    fig.text(.027,.927,"A   Could re-pairing reach the measured rate?",size=10,weight="bold")
    fig.text(.593,.927,"B   Where did the difference in means arise?",size=10,weight="bold")
    fig.text(.027,.821,"Feasible mixtures 9.38–41.41%  ·  outer limits 9.02–41.54%",size=7.2,color=GRAY)
    fig.text(.60,.822,"TC shift",color=BLUE,size=7.7,weight="bold");fig.text(.71,.822,"−HDL shift",color=PURPLE,size=7.7,weight="bold")
    fig.add_artist(Line2D([.858],[.836],transform=fig.transFigure,marker="D",ms=4.0,mec=NAVY,mfc="white",linestyle="none"))
    fig.text(.871,.822,"Net change",color=NAVY,size=7.6)
    fig.text(.027,.050,"Points and 95% intervals refer to measured samples. The shaded region describes possible joint models with fixed source marginals.",size=7.5,color=GRAY)
    save(fig,"where-pairing-can-help")


if __name__=="__main__":
    use_figure()
    feasibility_figure()
