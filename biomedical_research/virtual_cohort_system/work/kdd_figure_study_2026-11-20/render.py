"""Draw the two scientific figure studies using only aggregate plotting inputs."""
import json
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

OUT = Path(__file__).resolve().parent
INK = "#202D40"
MUTED = "#485970"
RULE = "#C9D1DC"
BLUE = "#255996"
RUST = "#A84725"
BAND = "#D1DEEF"
PAPER = "#FFFFFF"
mpl.rcParams.update({"font.family":"Arial", "font.size":9, "pdf.fonttype":42,
                     "axes.labelcolor":INK,"xtick.color":MUTED,"ytick.color":MUTED,
                     "text.color":INK,"axes.edgecolor":RULE,"figure.facecolor":PAPER,
                     "axes.facecolor":PAPER,"savefig.facecolor":PAPER})


def heading(fig,title,subtitle):
    fig.text(.048,.942,title,ha="left",va="center",fontsize=16,fontweight="bold")
    fig.text(.049,.877,subtitle,ha="left",va="center",fontsize=9.1,color=MUTED)


def iron(iron_data):
    fig=plt.figure(figsize=(8.15,5.05))
    heading(fig,"Low biomarker ranks cluster more strongly in the virtual cohorts",
            "Akwa Ibom, Nigeria   |   Measured mothers and source-calibrated virtual cohorts")
    scheme=LinearSegmentedColormap.from_list("percent",["#9B432C","#E9B9A5","#FCFAF5","#98B7D9","#174C83"])
    scale=Normalize(vmin=0, vmax=50)
    keys=("measured","agent","statistical")
    titles=("Measured","Agent-generated","Statistical generator")
    for i,(k,title) in enumerate(zip(keys,titles,strict=True)):
        left=.102+.295*i
        z=iron_data[k]
        c=np.asarray(z["grid_hb_by_fe"])
        percentages=100*c/c.sum(axis=1,keepdims=True)
        ax=fig.add_axes([left,.365,.220,.355])
        im=ax.imshow(percentages.T,origin="lower",vmin=0,vmax=50,cmap=scheme,aspect="equal")
        ax.set_xticks(range(4),["Q1","Q2","Q3","Q4"])
        ax.set_yticks(range(4),["Q1","Q2","Q3","Q4"] if i==0 else [""]*4)
        if i==0:ax.set_ylabel("Ferritin quartile",fontsize=9)
        ax.tick_params(length=0,pad=3,labelsize=8.3)
        ax.set_xticks(np.arange(-.5,4),minor=True);ax.set_yticks(np.arange(-.5,4),minor=True)
        ax.tick_params(which="minor",length=0);ax.grid(which="minor",color="white",linewidth=1.8)
        for sp in ax.spines.values():sp.set_visible(False)
        for x,y in np.ndindex(4,4):
            val=percentages[x,y]
            col="white" if val>43 or val<8 else INK
            ax.text(x,y,f"{val:.1f}",ha="center",va="center",fontsize=9.1,
                    color=col,fontweight="bold" if x==y==0 else "normal")
        center=left+.110
        fig.text(center,.797,title,ha="center",va="center",fontsize=11,fontweight="bold")
        secondary = "603 mothers" if k=="measured" else ("Program 1 · 36,000 pairs" if k=="agent" else "Gaussian copula · 36,000 pairs")
        fig.text(center,.755,secondary,ha="center",fontsize=8,color=MUTED)
        fig.text(center,.241, f"Rank {z['rank']:.3f}     OR {z['odds']:.2f}",
                 ha="center",fontsize=9.2,fontweight="bold")
    fig.text(.508,.29,"Hemoglobin quartile within each cohort",ha="center",fontsize=9)
    ci=iron_data["measured_cluster_intervals"]
    lo_r,hi_r=ci["reference_rank"]
    lo_o,hi_o=ci["reference_odds_ratio"]
    fig.text(.508,.204,f"Measured 95% cluster-bootstrap intervals    rank {lo_r:.3f} to {hi_r:.3f}    ·    OR {lo_o:.2f} to {hi_o:.2f}",
             ha="center",fontsize=7.7,color=MUTED)
    cax=fig.add_axes([.348,.155,.325,.018])
    colorbar=fig.colorbar(mpl.cm.ScalarMappable(norm=scale,cmap=scheme),cax=cax,orientation="horizontal",ticks=[0,12.5,25,37.5,50])
    colorbar.ax.tick_params(length=2,pad=2,labelsize=7.6)
    colorbar.outline.set_visible(False)
    fig.text(.049,.085,"Cells show the percentage in a ferritin quartile among people in that hemoglobin quartile (each column sums to 100% before rounding).",fontsize=7.8)
    fig.text(.049,.050,"Q1 is lowest. Quartiles use average ranks within each cohort. OR uses fixed cutoffs of Hb <12 g/dL and ferritin <15 µg/L.",fontsize=7.8,color=MUTED)
    return fig


def lifestyle(x):
    fig=plt.figure(figsize=(8.15,6.1))
    heading(fig,"Can a virtual cohort reproduce the same lifestyle comparison?",
            "Turkana   |   Age- and sex-adjusted group differences, with the group-by-sex sample sizes matched for each outcome")
    legend=[Line2D([0],[0],color=INK,lw=1.45,ls=(0,(3,1.4)),label="Real A − real B"),
            Line2D([0],[0],color=BLUE,lw=1.8,label="Virtual − real B (median curve)"),
            Patch(facecolor=BAND,edgecolor="none",label="Range of six virtual curves")]
    fig.legend(handles=legend,loc="center left",bbox_to_anchor=(.05,.823),ncol=3,fontsize=8.3,
               handlelength=1.8,columnspacing=2.2,frameon=False,borderaxespad=0)
    groups=[("rural_minus_pastoralist","Rural − pastoralist"),("urban_minus_pastoralist","Urban − pastoralist"),
            ("urban_minus_rural","Urban − rural")]
    traits=[("bmi","BMI","kg/m²",[-2,-1,0,1,2]),("total_cholesterol","Total\ncholesterol","mg/dL",[-40,-20,0,20,40]),
            ("hdl_cholesterol","HDL\ncholesterol","mg/dL",[-20,-10,0,10,20])]
    positions=[.165,.443,.721]
    for j,(_,label) in enumerate(groups):
        fig.text(positions[j]+.113,.762,label,ha="center",fontsize=10.2,fontweight="bold")
    for i,(trait,display,unit,ticks) in enumerate(traits):
        y=.571-.205*i
        t=x["traits"][trait]
        xs=np.asarray(t["x_grid"])
        fig.text(.049,y+.100,display,fontsize=10,fontweight="bold",va="center",linespacing=1.10)
        fig.text(.049,y+.041,unit,fontsize=8,color=MUTED,va="center")
        for j,(contrast,_) in enumerate(groups):
            ax=fig.add_axes([positions[j],y,.225,.151])
            c=t["facets"][contrast]
            ratio=lambda name: np.asarray(c[name],dtype=float)/x["n_per_stream"]
            ax.axhline(.5,lw=.5,color=RULE,ls=":")
            ax.axvline(0,lw=.8,color=RUST,ls=(0,(2,2)),alpha=.75)
            ax.fill_between(xs,ratio("virtual_min_ecdf_n"),ratio("virtual_max_ecdf_n"),
                            color=BAND,step="post",lw=0)
            ax.step(xs,ratio("virtual_median_ecdf_n"),where="post",color=BLUE,lw=1.4)
            ax.step(xs,ratio("real_ecdf_n"),where="post",color=INK,lw=1.2,ls=(0,(3,1.5)))
            ax.set(xlim=(xs[0],xs[-1]),ylim=(-.025,1.025),xticks=ticks,yticks=[0,.5,1])
            ax.set_yticklabels(["0%", "50%", "100%"] if j==0 else [""]*3)
            ax.spines[["top","right"]].set_visible(False)
            ax.tick_params(axis="both",labelsize=7.1,length=2,pad=2)
    fig.text(.558,.100,"Signed difference between two estimates of the same adjusted group effect (row units)",ha="center",fontsize=8.7)
    fig.text(.049,.055,"A curve gives the share of 500 resamples at or below each signed difference. A leftward shift means smaller estimated group effects.",fontsize=7.7)
    fig.text(.049,.022,"The band spans six fixed tables from two constructors (three seeds each). Each virtual comparison shares its real B resample with the real–real comparison.",fontsize=7.5,color=MUTED)
    return fig


if __name__=="__main__":
    data=json.loads((OUT/"plot_inputs.json").read_text(encoding="utf-8"))
    with PdfPages(OUT/"scientific-figure-studies.pdf",metadata={"Title":"What the virtual cohorts reproduce","Author":"Research team"}) as pdf:
        for figure,name in [(iron(data["iron"]),"iron-quartiles"),(lifestyle(data["lifestyle"]),"lifestyle-resampling")]:
            pdf.savefig(figure)
            figure.savefig(OUT/(name+".png"),dpi=160)
            plt.close(figure)
