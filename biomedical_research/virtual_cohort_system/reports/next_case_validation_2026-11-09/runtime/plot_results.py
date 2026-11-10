"""Post-reveal only: fixed analyses, all selected authors/seeds, no quality filter."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

U=Path(__file__).resolve().parent.parent
def main():
    r=json.loads((U/"RESULTS.json").read_text(encoding="utf-8"))
    out=U/"figures";out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
                         "axes.spines.right":False,"pdf.fonttype":42,"svg.fonttype":"none"})
    colors=["#315C8A","#8B6BB1","#BD7A3C","#B25E7B","#637588"]
    keys=["bmi_sbp","bmi_dbp","residual_correlation"]
    titles=["BMI–systolic BP association","BMI–diastolic BP association","Residual SBP–DBP dependence"]
    fig,axes=plt.subplots(1,3,figsize=(12.0,4.2))
    for ax,key,title in zip(axes,keys,titles):
        ref=r["reference_weighted"]["estimates"][key]
        band=r["reference_row_resampling_stability"]["intervals"][key]
        if band["low"] is not None:ax.axvspan(band["low"],band["high"],color="#DDE3EC",zorder=0)
        if ref is not None:ax.axvline(ref,color="#23354B",lw=1.4,linestyle="--")
        for i,author in enumerate(["A01","A02","A03","A04","A05"]):
            rows=[x for x in r["generated"] if x["author_id"]==author]
            vals=[x["analysis"]["estimates"][key] for x in rows]
            offsets=np.linspace(-.12,.12,len(vals))
            for offset,value in zip(offsets,vals):
                if value is not None:ax.scatter(value,i+offset,s=34,color=colors[i],edgecolor="white",linewidth=.5,zorder=3)
            good=[v for v in vals if v is not None]
            if good:ax.hlines(i,min(good),max(good),color=colors[i],lw=1.8,zorder=2)
            if len(good)<3:ax.text(.98,i,f"{len(good)}/3 estimable",transform=ax.get_yaxis_transform(),ha="right",va="center",fontsize=8)
        ax.set(yticks=range(5),yticklabels=["Author1","Author2","Author3","Author4","Author5"],title=title,ylim=(4.6,-.6))
        ax.set_xlabel("mmHg per 5 kg/m² BMI" if key!="residual_correlation" else "Adjusted residual correlation")
        ax.grid(axis="x",color="#EAECEF",lw=.6)
        if key=="residual_correlation":ax.set_xlim(-1,1)
    fig.suptitle("One generated cohort, three scientific analyses",fontsize=15,x=.055,ha="left")
    fig.text(.055,.03,"Dots: three fixed draws per selected author law. Dashed line: real weighted reference.\nShading: conditional row-resampling stability, not survey-design confidence. All authors retained.",fontsize=9,color="#465368")
    fig.subplots_adjust(left=.08,right=.99,top=.79,bottom=.24,wspace=.40)
    for ext in ["png","pdf","svg"]:fig.savefig(out/("pns_bp_analysis_utility."+ext),dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,3.9))
    for ax,role,title in zip(axes,["marginal","residual"],["Marginal variability","Conditional residual variability"]):
        ax.axvline(1,color="#23354B",ls="--",lw=1.2)
        for i,author in enumerate(["A01","A02","A03","A04","A05"]):
            rows=[x for x in r["comparisons"] if x["author_id"]==author]
            for endpoint,offset,marker in [("sbp",-.12,"o"),("dbp",.12,"s")]:
                values=[x["dispersion_ratios"][role+"_"+endpoint] for x in rows]
                vals=[x for x in values if x is not None]
                if vals:
                    ax.hlines(i+offset,min(vals),max(vals),color=colors[i],lw=1.3)
                    ax.scatter(vals,[i+offset]*len(vals),s=24,color=colors[i],marker=marker,alpha=.8)
        ax.set(yticks=range(5),yticklabels=["Author1","Author2","Author3","Author4","Author5"],title=title,ylim=(4.6,-.6),xlabel="Generated SD / real-reference SD")
        ax.grid(axis="x",color="#EAECEF",lw=.6)
    fig.text(.10,.04,"Circle: SBP. Square: DBP. Ratio1 denotes equal dispersion, not a statistical passing threshold.",fontsize=9)
    fig.subplots_adjust(left=.10,right=.98,top=.86,bottom=.23,wspace=.38)
    for ext in ["png","pdf","svg"]:fig.savefig(out/("pns_bp_dispersion."+ext),dpi=180)
    plt.close(fig)
    print(str(out))
if __name__=="__main__":main()
