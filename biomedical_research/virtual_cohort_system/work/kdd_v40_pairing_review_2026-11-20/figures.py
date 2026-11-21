"""Render the three KDD review figures from released aggregate results only."""
import json
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
OUT=HERE/"figures"
INK="#182c44"; BLUE="#23578a"; RUST="#a74b30"; DUST="#67778a"; FAINT="#dae2ea"; PURPLE="#654787"
mpl.rcParams.update({"font.family":"Arial","font.size":9,"pdf.fonttype":42,"text.color":INK,
                     "axes.labelcolor":INK,"axes.edgecolor":"#bac5d2","axes.spines.right":False,"axes.spines.top":False,
                     "xtick.color":"#4a5f72","ytick.color":"#3f536a","axes.titlecolor":INK})
HEAT=LinearSegmentedColormap.from_list("rank_density",["#fbf9f5","#dde7f3","#8daed1","#4d72a0","#34335f"])
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(fig,name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT/(name+".pdf"))
    fig.savefig(OUT/(name+".png"),dpi=175,facecolor="white")
    plt.close(fig)

def title(ax,letter,name):
    ax.set_title(letter+"   "+name,loc="left",fontsize=10,fontweight="bold",pad=11)

def pairing():
    fig=plt.figure(figsize=(8.65,3.12))
    a=fig.add_axes([.113,.255,.31,.51]); b=fig.add_axes([.56,.255,.414,.51])
    d=read(WORK/"chns_statistical_comparator_2026-11-19/RESULTS.json")["results"]
    ref=d["reference"]
    a.axvspan(*ref["rank_interval"],color=FAINT,alpha=.52,zorder=0)
    a.axvline(ref["rank"],color=DUST,ls=":",lw=1.5)
    parents=d["pairs"]
    for i,p in enumerate(parents):
        x=p["repairing_expectation"]["rank"];y=p["agent"]["rank"]; height=len(parents)-1-i
        a.plot([x,y],[height,height],color="#a8b7c7",lw=1.8,zorder=1)
        a.plot(x,height,"o",ms=5.4,mec=RUST,mfc="white",mew=1.25)
        a.plot(y,height,"o",ms=5.4,color=BLUE)
    a.set(yticks=list(reversed(range(len(parents)))),yticklabels=["Ordinary 1","Ordinary 2","Ordinary 3","Guided 1","Guided 2","Guided 3"],
          ylim=(-.55,5.55),xlim=(.231,.38),xticks=[.24,.28,.32,.36],xlabel="Hemoglobin–ferritin rank correlation")
    a.spines["left"].set_visible(False);a.tick_params(axis="y",length=0,labelsize=8)
    title(a,"A","Iron  ·  within-band pairing")
    a.legend(handles=[Line2D([],[],ls="none",marker="o",mfc="white",mec=RUST,label="Re-paired"),
                      Line2D([],[],ls="none",marker="o",color=BLUE,label="Authored")],loc="lower left",
             bbox_to_anchor=(-.025,-.53),frameon=False,ncol=2,fontsize=8,handlelength=.9)
    life=pd.read_csv(HERE/"LIFESTYLE_PAIRING.csv")
    mat=life.pivot_table(index="trait",columns="contrast",values="absolute_change_in_real_real_units",aggfunc="max").loc[
        ["bmi","total_cholesterol","hdl_cholesterol"],["rural_minus_pastoralist","urban_minus_pastoralist","urban_minus_rural"]].to_numpy()
    b.imshow(mat,cmap=HEAT,vmin=0,vmax=.20,aspect="auto",interpolation="nearest")
    for i in range(3):
        for j in range(3):
            b.text(j,i,f"{100*mat[i,j]:.1f}%",ha="center",va="center",fontweight="bold",color="white" if mat[i,j]>.12 else INK)
    b.set(xticks=[0,1,2],xticklabels=["Rural vs\npastoralist","Urban vs\npastoralist","Urban vs\nrural"],
          yticks=[0,1,2],yticklabels=["BMI","Total chol.","HDL"])
    b.tick_params(length=0,labelsize=8,pad=4)
    for sp in b.spines.values():sp.set_visible(False)
    for q in (.5,1.5):
        b.axvline(q,color="white",lw=1.6);b.axhline(q,color="white",lw=1.6)
    title(b,"B","Lifestyle  ·  age pairing within groups")
    fig.text(.56,.065,"Maximum shift as a share of the real–real discrepancy",fontsize=8.1,color=DUST)
    save(fig,"pairing-attribution")

def lipids():
    fig=plt.figure(figsize=(8.65,3.06))
    a=fig.add_axes([.19,.25,.235,.53]); b=fig.add_axes([.595,.25,.37,.53])
    old=WORK/"nonhdl_external_2026-11-20"
    sites=read(old/"REPLAY_RESULTS.json")["cohorts"]
    arms=read(old/"MODEL_CLOSURE.json")["arms"]
    for y,(site,rec) in zip([3,2],sites.items(),strict=True):
        x=rec["reference"]["tail_pct"];lo,hi=rec["reference_ci"]["tail_pct"]
        a.errorbar(x,y,xerr=[[x-lo],[hi-x]],fmt="D",color=INK,ms=4.5,capsize=3,lw=1.6)
    for y,arm,marker,c in [(1,"agent","o",BLUE),(0,"statistical","^",RUST)]:
        a.plot(arms[arm]["pooled"]["tail_pct"],y,marker,color=c,ms=5.8)
    a.set(yticks=[3,2,1,0],yticklabels=["Mekelle residents","Haramaya staff","Original agent","Statistical model"],
          ylim=(-.55,3.55),xlim=(15,28),xticks=[16,20,24,28],xlabel="At or above 160 mg/dL (%)")
    title(a,"A","Frozen point estimates")
    scenarios=read(HERE/"SENSITIVITY.json")["authors"]
    for j,(name,data) in enumerate(scenarios.items()):
        pos=4-j
        if not data["both_pass"]:
            b.text(10,pos,"Source checks failed",fontsize=8,color=RUST)
            continue
        left=data["scenarios"]["a"]["percent"];right=data["scenarios"]["b"]["percent"]
        b.plot([left,right],[pos,pos],color="#adbbca",lw=2.4)
        b.plot(left,pos,"o",color=BLUE,ms=5.3);b.plot(right,pos,"s",mfc="white",mec=PURPLE,mew=1.5,ms=5.2)
        b.text((left+right)/2,pos+.105,f"{abs(right-left):.1f} pp",ha="center",va="bottom",fontsize=7.3,color=INK)
    ctrl=read(HERE/"CONTROL.json")["constructive_examples"]
    endpoints=[ctrl[name]["score"]["percent"] for name in ("low","high")]
    b.plot(endpoints,[0,0],ls="--",lw=1.4,color=DUST,marker="|",ms=10,mew=1.4)
    b.set(yticks=[4,3,2,1,0],yticklabels=["Author 1","Author 2","Author 3","Author 4","Numerical examples"],
          ylim=(-.55,4.72),xlim=(5,45),xticks=[10,20,30,40],xlabel="At or above 160 mg/dL (%)")
    title(b,"B","Source-only sensitivity test")
    for ax in (a,b):
        ax.spines["left"].set_visible(False);ax.tick_params(axis="y",length=0,labelsize=8)
        ax.grid(axis="x",lw=.5,color=FAINT);ax.set_axisbelow(True)
    fig.text(.135,.042,"Bars on measured estimates are 95% intervals.",fontsize=7.8,color=DUST)
    fig.text(.55,.042,"Paired symbols show two scenarios from the same author.",fontsize=7.8,color=DUST)
    save(fig,"nonhdl-selection")

def heatmaps():
    d=read(HERE/"LIPID_HEATMAP.json");k=d["bins"];n=d["n"]
    fig,axes=plt.subplots(2,4,figsize=(8.05,4.12),sharex=True,sharey=True)
    fig.subplots_adjust(left=.122,right=.908,bottom=.145,top=.875,wspace=.16,hspace=.20)
    boundary=np.array(d["boundary_rank_coordinates"])*100
    for j,(name,obj) in enumerate(d["panels"].items()):
        for i,mode in enumerate(("a","b")):
            a=axes[i,j];rec=obj[mode]
            if "tc_by_hdl" not in rec:
                a.text(50,50,"Failed",ha="center");continue
            grid=np.array(rec["tc_by_hdl"]).T/(n/k**2)
            im=a.imshow(grid,extent=(0,100,0,100),origin="lower",cmap=HEAT,vmin=0,vmax=4,interpolation="nearest",aspect="auto")
            a.plot(boundary[:,0],boundary[:,1],lw=1.15,color="#ce5426")
            a.set(xticks=[0,50,100],yticks=[0,50,100],xlim=(0,100),ylim=(0,100))
            a.tick_params(labelsize=6.9,length=2,pad=2)
            a.text(.04,.92,f"{100*rec['tail_n']/n:.1f}%",ha="left",va="top",transform=a.transAxes,
                   fontsize=8.4,fontweight="bold",color=INK,bbox=dict(facecolor="white",edgecolor="none",alpha=.9,pad=1.4))
            if i==0:a.set_title("Author "+str(j+1),fontsize=9.4,fontweight="bold",pad=5)
    for i,t in enumerate(("Scenario A","Scenario B")):
        axes[i,0].set_ylabel(t+"\nHDL rank (%)",fontsize=8.4)
    fig.text(.51,.047,"Total cholesterol rank (%)",ha="center",fontsize=9.3)
    cb=fig.colorbar(im,cax=fig.add_axes([.935,.22,.013,.57]))
    cb.set_ticks([0,1,2,3,4],labels=["0","1","2","3","4+"]);cb.ax.tick_params(labelsize=7)
    cb.set_label("Density / independent pairing",fontsize=7.5,labelpad=3)
    save(fig,"lipid-rank-maps")

if __name__=="__main__":
    pairing();lipids();heatmaps()
