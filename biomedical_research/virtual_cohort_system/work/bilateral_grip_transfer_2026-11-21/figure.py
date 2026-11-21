"""Figures for the predeclared uses and the post-disclosure sensitivity analysis."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from science import HERE,USES,read
from sensitivity import gaussian_gap

INK="#23354c";BLUE="#325e92";PURPLE="#795883";ORANGE="#af542f";MUTED="#52647a"
SITES=("US_NHANES","ZA_HAALSI","BR_RIO_MAX")
NAMES=("US","South Africa","Brazil (max.)")
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.8,"axes.labelsize":7.9,"xtick.labelsize":7.2,
                     "ytick.labelsize":7.4,"axes.edgecolor":"#b1c0cf","axes.labelcolor":INK,
                     "xtick.color":MUTED,"ytick.color":MUTED,"pdf.fonttype":42,"ps.fonttype":42})


def save(fig,name):
    path=HERE/"figures";path.mkdir(exist_ok=True)
    for suffix in ("png","pdf"):
        fig.savefig(path/(name+"."+suffix),dpi=220,facecolor="white",metadata={"Creator":"Matplotlib"})
    plt.close(fig)


def main():
    preds=read(HERE/"PREDICTIONS.json")["methods"];res=read(HERE/"RESULTS.json")
    refs=res["reference"]
    fig=plt.figure(figsize=(7.12,3.12),layout=None)
    ax=fig.add_axes([.165,.255,.27,.572]);bx=fig.add_axes([.6,.30,.39,.47])
    fig.text(.012,.944,"A   How far apart are a person's hands?",weight="bold",fontsize=9.3,color=INK)
    fig.text(.514,.944,"B   Which analyses transfer?",weight="bold",fontsize=9.3,color=INK)
    fig.text(.012,.865,"Australian marker distributions fixed",color=MUTED,fontsize=7.2)
    fig.text(.514,.865,"Virtual estimates and measured values",color=MUTED,fontsize=7.2)
    y=np.array([6.6,5.55,4.5,3.45,2.05,1.,-.05])
    labels=("Independent","Authors, M","Authors, J","Ratio rule",*NAMES)
    ax.set(yticks=y,yticklabels=labels,xlim=(2.2,8.3),ylim=(-.7,7.12),xticks=[3,4,5,6,7,8])
    ax.axhline(2.76,lw=.55,color="#c4ccda");ax.set_axisbelow(True);ax.grid(axis="x",color="#dce4eb",lw=.48)
    for spine in ("left","right","top"):ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y",length=0,pad=3);ax.tick_params(axis="x",length=2)
    ax.scatter(preds["independent"]["values"][USES[0]],y[0],marker="x",s=32,color=MUTED,linewidths=1.2,zorder=3)
    ax.scatter(preds["M1"]["values"][USES[0]],y[1],marker="o",s=31,color=BLUE,zorder=3)
    js=[preds[f"J{i}"]["values"][USES[0]] for i in range(1,5)]
    for j,off in zip(js,(-.15,-.05,.05,.15)):
        ax.scatter(j,y[2]+off,marker="o",s=12,edgecolors=PURPLE,facecolors="white",zorder=3,linewidths=1)
    ax.scatter(preds["ratio_rule"]["values"][USES[0]],y[3],marker="s",s=24,facecolors="white",edgecolors=ORANGE,zorder=3)
    for site,yy in zip(SITES,y[4:]):
        es=refs[site]["estimates"][USES[0]]
        v=es["estimate"];lo,hi=es["ci"]
        ax.errorbar(v,yy,xerr=[[v-lo],[hi-v]],fmt="D",color=INK,capsize=2,ms=3.4,lw=1.05,zorder=3)
    ax.set_xlabel("Mean absolute gap (kg)",labelpad=3)
    bx.set_xlim(-.5,3.5);bx.set_ylim(3.5,-.5)
    bx.set_xticks(range(4),["Absolute\ngap, kg","Gap ≥5 kg,\n%","Both hands,\nmean kg","Rank\ncorr."])
    bx.set_yticks(range(4),["Virtual M",*NAMES]);bx.tick_params(length=0,pad=3)
    bx.xaxis.tick_top()
    for spine in bx.spines.values():spine.set_visible(False)
    colors={"within":"#c7d9ee","unresolved":"#e9edf1","outside":"#f3c8b4","virtual":"#f7f8fa"}
    for row in range(4):
        s=SITES[row-1] if row else None
        for col,k in enumerate(USES):
            v=refs[s]["estimates"][k]["estimate"] if row else preds["M1"]["values"][k]
            state=res["comparisons"][s]["fixed_prediction_comparisons"]["M1"][k]["status"] if row else "virtual"
            bx.add_patch(Rectangle((col-.5,row-.5),1,1,facecolor=colors[state],edgecolor="white",lw=1.8))
            fmt=".3f" if col==3 else ".2f"
            bx.text(col,row,format(v,fmt),ha="center",va="center",fontsize=8,color=INK,weight="bold" if not row else "normal")
    for x,lab,key in ((.544,"Within","within"),(.686,"Unresolved","unresolved"),(.861,"Outside","outside")):
        fig.add_artist(Rectangle((x,.215),.014,.025,transform=fig.transFigure,facecolor=colors[key],edgecolor="none"))
        fig.text(x+.02,.215,lab,fontsize=7.05,color=MUTED)
    fig.text(.012,.09,"M saw separate hand summaries. J also saw individual ratio statistics. Diamonds show measured estimates and 95% intervals.",fontsize=6.8,color=MUTED)
    fig.text(.012,.046,"Colors compare each measured interval to the M estimate at its use-specific tolerance. Brazil reports each hand’s maximum.",fontsize=6.8,color=MUTED)
    save(fig,"bilateral-grip-transfer")

    # Interpretation in a named parametric family, clearly separate from the prospective test.
    fig,ax=plt.subplots(figsize=(5.8,2.95));fig.subplots_adjust(left=.11,right=.96,bottom=.21,top=.8)
    sens=read(HERE/"SENSITIVITY.json");cells=read(HERE/"AU_SOURCE.json")["cells"]
    xx=np.linspace(0,.99,220);yy=np.array([gaussian_gap(q,cells) for q in xx])
    ax.axhspan(*sens["virtual_point_range_supporting_primary_use_in_both_cohorts_kg"],color="#e4ebf5")
    ax.plot(xx,yy,color=BLUE,lw=1.7)
    for x,align,dx,dy in ((.8,"right",-.03,.53),(.85,"left",.025,-.63)):
        v=gaussian_gap(x,cells);ax.plot(x,v,"o",color=PURPLE,ms=4)
        ax.text(x+dx,v+dy,f"ρ = {x:.2f}",ha=align,color=INK,fontsize=7.5)
    ax.set(xlabel="Hypothetical common within-cell correlation",ylabel="Mean absolute gap (kg)",xlim=(0,1),ylim=(1.5,8.4))
    ax.xaxis.grid(True,color="#e0e6ec",lw=.5);ax.set_axisbelow(True)
    for sp in ("top","right"):ax.spines[sp].set_visible(False)
    fig.text(.03,.93,"How precisely do the two primary studies constrain the pairing?",weight="bold",fontsize=9.4,color=INK)
    fig.text(.03,.845,"The shaded band meets the ±1 kg use margin across both complete measured intervals.",fontsize=7.1,color=MUTED)
    save(fig,"grip-correlation-sensitivity")


if __name__=="__main__":main()
