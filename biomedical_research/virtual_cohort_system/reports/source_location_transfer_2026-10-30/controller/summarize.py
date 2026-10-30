"""Summarize released M11 results; no generator changes."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
OUT=HERE/"results"
report=json.loads((OUT/"analysis.json").read_text())
errors=pd.read_csv(OUT/"errors.csv")
paired=pd.read_csv(OUT/"paired_changes.csv")
summary=errors.groupby(["family","arm"],sort=False).median(numeric_only=True).drop(columns="seed")
summary.to_csv(OUT/"median_error_summary.csv")
points=pd.DataFrame([{**{k:x[k] for k in ["family","arm","seed"]},**x["points"]} for x in report["generated"]])
points.to_csv(OUT/"all_analytical_points.csv",index=False)
families=["ha","hb"]
source=[]
for family in families:
    c=json.loads((HERE/family/"candidates/calibrated_primary/calibration.json").read_text())
    source.append(np.mean([abs(x["offset"]) for x in c["sex"].values()]))
plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
fig,axs=plt.subplots(1,2,figsize=(10.5,4.8))
x=np.arange(2); width=.34
axs[0].bar(x-width/2,source,width,label="Initial",color="#537da8")
axs[0].bar(x+width/2,[0,0],width,label="Source calibrated",color="#d0884c")
axs[0].set_title("Source: fitted sex medians")
axs[0].set_ylabel("Mean absolute discrepancy (HbA1c percentage points)")
axs[0].set_ylim(0,.30)
axs[0].text(.02,.94,"Pooled source draws; fitted constraint",transform=axs[0].transAxes,va="top",fontsize=9)
for i,arm in enumerate(["initial","calibrated_primary"]):
    groups=[errors.loc[errors.family.eq(f)&errors.arm.eq(arm),"sex_median_mae"].to_numpy() for f in families]
    med=np.array([np.median(v) for v in groups]); low=med-np.array([min(v) for v in groups]); high=np.array([max(v) for v in groups])-med
    axs[1].bar(x+(i-.5)*width,med,width,color=["#537da8","#d0884c"][i],yerr=[low,high],capsize=3,label=["Initial","Source calibrated"][i])
axs[1].set_title("New target: weighted sex medians")
axs[1].set_ylim(0,.30)
axs[1].text(.02,.94,"Median and range of 3 residual draws",transform=axs[1].transAxes,va="top",fontsize=9)
for ax in axs:
    ax.set_xticks(x,["Inherited family A","Inherited family B"])
    ax.grid(axis="y",alpha=.18); ax.set_axisbelow(True)
axs[0].legend(loc="upper right",bbox_to_anchor=(1,.83),frameon=False)
fig.suptitle("Better source fit did not improve target HbA1c levels",fontsize=14)
fig.text(.5,.015,"NHANES 2021–2023, n=5,378; WTPH2YR. Lower is better. Ranges are Monte Carlo variation, not confidence intervals.",ha="center",fontsize=8.5)
fig.tight_layout(rect=[0,.06,1,.94])
fig.savefig(OUT/"source_vs_target.png",dpi=180)
fig.savefig(OUT/"source_vs_target.svg")
plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(10.5,4.8),sharey=True)
for ax,family in zip(axs,families):
    labels=[]; real=[]; initial=[]; calibrated=[]
    med=points.loc[points.family.eq(family)].groupby("arm").median(numeric_only=True)
    for sex in ["male","female"]:
        for lo,hi in [(20,39),(40,59),(60,79)]:
            key=f"mean_{sex}_{lo}_{hi}"
            labels.append(f"{sex[0].upper()} {lo}–{hi}")
            real.append(report["reference"][key]);initial.append(med.loc["initial",key]);calibrated.append(med.loc["calibrated_primary",key])
    xx=np.arange(6)
    for segment in [slice(0,3),slice(3,6)]:
        first=segment.start==0
        ax.plot(xx[segment],np.array(real)[segment],"o-",color="#222222",label="Measured reference" if first else None)
        ax.plot(xx[segment],np.array(initial)[segment],"s--",color="#537da8",label="Initial" if first else None)
        ax.plot(xx[segment],np.array(calibrated)[segment],"^--",color="#d0884c",label="Source calibrated" if first else None)
    ax.axvline(2.5,color="#bbbbbb",linewidth=.7)
    ax.set_xticks(xx,labels,rotation=35,ha="right")
    ax.set_title("Inherited family "+family[-1].upper())
    ax.grid(axis="y",alpha=.18)
axs[0].set_ylabel("Weighted cell mean HbA1c (%)")
axs[1].legend(frameon=False,fontsize=9)
fig.suptitle("Age–sex analysis reuse: level discrepancies remained",fontsize=14)
fig.text(.5,.015,"Same frozen tables; generated points are medians over 3 residual draws. Descriptive estimates; no confidence intervals shown.",ha="center",fontsize=8.5)
fig.tight_layout(rect=[0,.07,1,.94])
fig.savefig(OUT/"age_sex_reuse.png",dpi=180)
fig.savefig(OUT/"age_sex_reuse.svg")
plt.close(fig)
print(summary.round(6).to_string())
