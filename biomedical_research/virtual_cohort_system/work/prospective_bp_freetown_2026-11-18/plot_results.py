"""Plot only released aggregates. See PLAN.md for the estimands and uncertainty."""
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, PercentFormatter

root = Path(__file__).resolve().parent
data = json.loads((root / "AGGREGATES.json").read_text(encoding="utf8"))
target = data["target"]
arms = data["arms"]
labels = ["Freetown release", "Source calculation", "Agent primary", "Agent alternative", "Statistical model"]
values = [target["estimates"],data["direct"],*[arms[k]["pooled"]["estimates"] for k in ("primary","alternative","statistical")]]
colors = ["#182B48","#787F89","#375DB5","#B34C36","#666399"]
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"pdf.fonttype":42})
fig, axs = plt.subplots(1,2,figsize=(9.6,4.25),sharey=True)
fig.subplots_adjust(left=.195,right=.97,bottom=.29,top=.82,wspace=.21)
for j,(ax,q,title) in enumerate(zip(axs,["Q1","Q2"],["Correlation of systolic and diastolic BP","Both pressures at or above cutoffs¹"])):
    ax.set_title(title,fontsize=12,loc="left",fontweight="bold",pad=15,color="#182B48")
    ax.text(-.045,1.18,chr(65+j),transform=ax.transAxes,fontweight="bold",fontsize=11,ha="right",color="#58677B")
    measured=values[0][q]
    interval=target["within_zone_intervals"][q]
    points=[v[q] for v in values if v[q] is not None]+list(interval)
    span=max(max(points)-min(points),.1 if q=="Q1" else .05)
    ax.set_xlim(min(points)-.22*span,max(points)+.72*span)
    ax.axvspan(*interval,color="#EAEDF3",zorder=0)
    ax.axvline(measured,color="#8292A7",lw=.8,ls=":",zorder=1)
    for idx,(v,c) in enumerate(zip(values,colors)):
        y=4-idx
        x=v[q]
        if x is None:
            ax.text(.02,y,"Undetermined",transform=ax.get_yaxis_transform(),va="center",fontsize=9,color="#747D89")
            continue
        if idx==0:
            ax.plot(interval,[y,y],c=c,lw=2,solid_capstyle="round",zorder=2)
        ax.plot(x,y,marker="D" if idx==0 else "o",ms=6,color=c,zorder=3)
        text=f"{x:.3f}" if q=="Q1" else f"{100*x:.1f}%"
        ax.annotate(text,(x,y),xytext=(7,6 if idx==0 else 0),textcoords="offset points",va="center",fontsize=9,color=c)
    ax.set_ylim(-.55,4.6)
    ax.set_yticks(range(4,-1,-1),labels)
    ax.tick_params(axis="y",length=0,pad=8)
    ax.spines[["left","top","right"]].set_visible(False)
    ax.spines["bottom"].set_color("#CBD0D7")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax.tick_params(axis="x",colors="#5E6877",length=3)
    if j==1:
        ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=0))
    ax.set_xlabel("Pearson correlation" if j==0 else "Share of screened adults",fontsize=9,color="#58677B")
fig.text(.02,.124,"Shading shows within-zone 95% bootstrap intervals for 1,244 Freetown records. Virtual estimates pool three draws per law.",fontsize=8.3,color="#4C5667")
fig.text(.02,.073,"¹ Systolic ≥140 mmHg and diastolic ≥90 mmHg in the same person. All 1,244 records agree on the two threshold indicators.",fontsize=8.3,color="#4C5667")
fig.text(.02,.026,"The deposited file does not document how its added pressure columns preserve the original pairing.",fontsize=8.3,color="#4C5667")
for suffix in ["png","pdf"]:
    fig.savefig(root/("prospective_pressure."+suffix),dpi=200,facecolor="white")
