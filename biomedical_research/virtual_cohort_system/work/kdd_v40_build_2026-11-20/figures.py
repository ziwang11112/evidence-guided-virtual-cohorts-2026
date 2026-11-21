"""Build an editable method figure and two scientific comparisons from frozen aggregate results."""
import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
FIG=ROOT/"manuscript/kdd_draft_v40_2026-11-20/figures"
WORK=ROOT/"work"
INK="#20334B";MUTED="#516379";BLUE="#285C92";RUST="#A74A2C";LIGHT="#CDDDF0"
plt.rcParams.update({"font.family":"Arial","pdf.fonttype":42,"font.size":10,"text.color":INK,"axes.labelcolor":INK,
    "xtick.color":MUTED,"ytick.color":MUTED,"axes.spines.right":False,"axes.spines.top":False,"axes.edgecolor":"#B9C5D3"})
def read(p):
    return json.loads(p.read_text(encoding="utf8"))
def method():
    data=read(WORK/"original_paper_iron_sensitivity_2026-11-19/SCIENTIFIC_RESULTS.json")["laws"]
    laws=[v for k,v in data.items() if k!="statistical"]
    counts=laws[0]["extracted_cells"];assert all(v["extracted_cells"]==counts for v in laws)
    x=ET.parse(ROOT/"manuscript/kdd_draft_v39_2026-11-20/figures/evidence-and-pairing.drawio")
    model=x.find(".//mxGraphModel");parent=model.find("root");model.set("pageHeight","298")
    keep=True
    for cell in list(parent):
        uid=cell.get("id")
        if uid=="outcome":keep=False
        if not keep:parent.remove(cell)
    def text(key,value,x,y,w,h,size=19,color=INK,bold=False,align="left"):
        style=f"text;html=1;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;fontFamily=Arial;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};spacing=0;whiteSpace=nowrap;"
        c=ET.SubElement(parent,"mxCell",id=key,value=value,style=style,vertex="1",parent="1")
        ET.SubElement(c,"mxGeometry",{"as":"geometry","x":str(x),"y":str(y),"width":str(w),"height":str(h)})
    def line(key,x1,y1,x2,y2,clr,width=1):
        c=ET.SubElement(parent,"mxCell",id=key,value="",style=f"endArrow=none;startArrow=none;strokeColor={clr};strokeWidth={width};",edge="1",parent="1")
        g=ET.SubElement(c,"mxGeometry",{"relative":"1","as":"geometry"})
        for xx,yy,where in ((x1,y1,"sourcePoint"),(x2,y2,"targetPoint")):
            ET.SubElement(g,"mxPoint",{"x":str(xx),"y":str(yy),"as":where})
    def dot(key,xx,yy,col):
        c=ET.SubElement(parent,"mxCell",id=key,value="",style=f"ellipse;html=1;fillColor={col};strokeColor=#FFFFFF;strokeWidth=1;",vertex="1",parent="1")
        ET.SubElement(c,"mxGeometry",{"as":"geometry","x":str(xx-4.2),"y":str(yy-4.2),"width":"8.4","height":"8.4"})
    cells={c.get("id"):c for c in parent}
    cells["canvas"].find("mxGeometry").set("height","298")
    d={"sample":"Zhu et al.  ·  1,671 women","table-title":"Published counts","choice-title":"Agent chooses a pairing",
       "result-title":"Two analyses of the same records","or":f"Crude odds ratio   {counts[0]*counts[3]/(counts[1]*counts[2]):.2f}",
       "bands":"Source table collapsed to four cells","pairtitle":"Same values within a threshold cell",
       "panel0":"Pairing 1","panel1":"Pairing 2","schematic":"Illustration  ·  columns ordered by rank"}
    for i,key in enumerate(("count00","count01","count10","count11")):d[key]=f"{counts[i]:,}"
    for key,val in d.items():cells[key].set("value",val)
    for metric,title,scale,ticks,y in (("odds_ratio","Threshold odds ratio",(5.8,7.5),(6,6.5,7),101),
                                      ("spearman","Continuous rank correlation",(-.5,.6),(-.5,0,.5),218)):
        vals=[v[metric] for v in laws]; mapx=lambda v:734+(v-scale[0])/(scale[1]-scale[0])*393
        text(metric+"-title",title,713,y-46,430,25,20,bold=True)
        line(metric+"-axis",734,y+8,1127,y+8,"#ADBCCB",1.3)
        if metric=="odds_ratio":
            c=counts[0]*counts[3]/(counts[1]*counts[2]);line("source-odds",mapx(c),y-12,mapx(c),y+10,RUST,2)
        else:line("rank-zero",mapx(0),y-12,mapx(0),y+10,"#788BA1",1.3)
        for k,v in enumerate(ticks):
            xx=mapx(v);line(f"{metric}-tick-{k}",xx,y+8,xx,y+14,MUTED)
            text(f"{metric}-label-{k}",f"{v:g}",xx-24,y+14,48,19,15,MUTED,align="center")
        for j,v in enumerate(vals):dot(f"{metric}-{j}",mapx(v),y-1-(j%3)*4,BLUE)
        rng=(f"{min(vals):.2f} to {max(vals):.2f}" if metric=="odds_ratio" else f"{min(vals):.3f} to {max(vals):.3f}")
        text(metric+"-range","Seven generators   "+rng,713,y+35,429,24,18,BLUE)
    ET.indent(x)
    x.write(FIG/"evidence-and-pairing.drawio",encoding="utf-8",xml_declaration=True)
def lifestyle():
    d=read(WORK/"kdd_figure_study_2026-11-20/plot_inputs.json")["lifestyle"]
    fig,ax=plt.subplots(1,2,figsize=(7.7,2.65))
    fig.subplots_adjust(left=.065,right=.985,top=.82,bottom=.31,wspace=.29)
    for i,(trait,contrast,title,axis) in enumerate([("bmi","urban_minus_pastoralist","Urban vs pastoralist · BMI","Effect difference (kg/m²)"),
               ("total_cholesterol","rural_minus_pastoralist","Rural vs pastoralist · total cholesterol","Effect difference (mg/dL)")]):
        t=d["traits"][trait]; f=t["facets"][contrast];xs=t["x_grid"]
        curve=lambda k:np.array(f[k])/d["n_per_stream"]
        a=ax[i];a.fill_between(xs,curve("virtual_min_ecdf_n"),curve("virtual_max_ecdf_n"),step="post",color=LIGHT)
        a.step(xs,curve("virtual_median_ecdf_n"),where="post",color=BLUE,lw=2)
        a.step(xs,curve("real_ecdf_n"),where="post",color=INK,ls="--",lw=1.5)
        a.axvline(0,color=RUST,ls=":",lw=1);a.set(xlabel=axis,xlim=(xs[0],xs[-1]),ylim=(-.02,1.02),yticks=[0,.5,1],yticklabels=["0%","50%","100%"])
        a.set_title(("A   " if i==0 else "B   ")+title,loc="left",fontweight="bold",fontsize=10.2)
        a.tick_params(labelsize=8);a.grid(axis="y",alpha=.15)
    handles=[Line2D([0],[0],color=INK,ls="--",label="Real vs real"),Line2D([0],[0],color=BLUE,label="Virtual vs real"),Patch(facecolor=LIGHT,label="Six virtual tables")]
    fig.legend(handles=handles,ncol=3,frameon=False,loc="lower center",bbox_to_anchor=(.5,-.005),fontsize=8.5)
    fig.savefig(FIG/"lifestyle-main.pdf");plt.close(fig)
def lipid():
    path=WORK/"nonhdl_external_2026-11-20";r=read(path/"REPLAY_RESULTS.json")["cohorts"];arms=read(path/"MODEL_CLOSURE.json")["arms"]
    assert (path/"REPLAY_VERIFICATION.json").exists() and all(v["usable"] for v in arms.values())
    fig,axes=plt.subplots(1,2,figsize=(7.7,2.42));fig.subplots_adjust(left=.16,right=.965,bottom=.29,top=.80,wspace=.28)
    for i,(key,title,axis) in enumerate((("mean_mg_dl","Mean non-HDL","mg/dL"),("tail_pct","At or above 160 mg/dL","Percent of participants"))):
        ax=axes[i]
        for j,(site,label) in enumerate((("mekelle","Mekelle"),("workers","Haramaya"))):
            ref=r[site]["reference"][key];lo,hi=r[site]["reference_ci"][key];y=1-j
            ax.errorbar(ref,y,xerr=[[ref-lo],[hi-ref]],fmt="D",markersize=5,color=INK,capsize=3,lw=1.6)
            for arm,dy,clr,shape in (("agent",.16,BLUE,"o"),("statistical",-.16,RUST,"^")):
                if arms[arm]["usable"]:ax.plot(arms[arm]["pooled"][key],y+dy,shape,ms=5.5,color=clr)
        ax.set(yticks=[1,0],yticklabels=["Mekelle","Haramaya"] if i==0 else [],ylim=(-.4,1.4),xlabel=axis)
        ax.set_title(("A   " if i==0 else "B   ")+title,loc="left",fontweight="bold",fontsize=11)
        ax.grid(axis="x",alpha=.2);ax.spines["left"].set_visible(False);ax.tick_params(axis="y",length=0)
    fig.legend(handles=[Line2D([],[],marker=m,ls="none",color=c,label=l) for m,c,l in (("D",INK,"Measured (95% interval)"),("o",BLUE,"Agent"),("^",RUST,"Statistical generator"))],loc="lower center",ncol=3,frameon=False,fontsize=8.5)
    fig.savefig(FIG/"nonhdl-two-cohorts.pdf");plt.close(fig)
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["method","lifestyle","lipid"])
    {"method":method,"lifestyle":lifestyle,"lipid":lipid}[parser.parse_args().action]()
