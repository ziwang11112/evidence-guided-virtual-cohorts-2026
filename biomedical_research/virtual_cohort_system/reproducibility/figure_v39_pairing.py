"""Build the editable first figure from the released CHNS aggregate tables."""
import json
from pathlib import Path
from statistics import median
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript/kdd_draft_v39_2026-11-20/figures/evidence-and-pairing.drawio"
DATA = ROOT / "work/chns_statistical_comparator_2026-11-19/RESULTS.json"
SOURCE = ROOT / "work/chns_iron_conditional_holdout_2026-11-19/A_TABLES.json"
INK, DIM, BLUE, WARM, GREY = "#19283F", "#465972", "#25569C", "#A74A20", "#C5CDD7"
WHITE = "#FFFFFF"


def build():
    tables = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = json.loads(DATA.read_text(encoding="utf-8"))["results"]
    file = ET.Element("mxfile", host="app.diagrams.net")
    page = ET.SubElement(file, "diagram", id="pairing-v39", name="Evidence and pairing")
    model = ET.SubElement(page, "mxGraphModel", page="0", grid="0", background=WHITE)
    graph = ET.SubElement(model, "root")
    ET.SubElement(graph, "mxCell", id="0")
    ET.SubElement(graph, "mxCell", id="1", parent="0")

    def cell(name, value, x, y, w, h, style):
        vertex = ET.SubElement(graph, "mxCell", id=name, value=str(value), parent="1",
                               vertex="1", style=style)
        ET.SubElement(vertex, "mxGeometry", x=str(x), y=str(y), width=str(w),
                      height=str(h), attrib={"as": "geometry"})

    def text(name, value, x, y, w, h, size=18, color=INK, bold=False, align="left"):
        style = (f"text;html=1;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;"
                 f"fontFamily=Arial;fontSize={size};fontColor={color};fontStyle={int(bold)};"
                 "spacing=0;spacingTop=0;spacingLeft=0;spacingRight=0;whiteSpace=nowrap;")
        cell(name, value, x,y,w,h,style)

    def rect(name, x,y,w,h, fill):
        cell(name,"",x,y,w,h,f"shape=rectangle;strokeColor=none;fillColor={fill};")

    def dot(name,x,y,r,edge,fill,width=2):
        cell(name,"",x-r,y-r,2*r,2*r,f"ellipse;strokeColor={edge};fillColor={fill};strokeWidth={width};")

    def line(name,x1,y1,x2,y2,color,thick=1.4,dashed=False):
        edge = ET.SubElement(graph,"mxCell",id=name,value="",parent="1",edge="1",
                             style=f"endArrow=none;startArrow=none;edgeStyle=none;rounded=0;strokeColor={color};strokeWidth={thick};dashed={int(dashed)};")
        g=ET.SubElement(edge,"mxGeometry",relative="1",attrib={"as":"geometry"})
        for which,x,y in (("sourcePoint",x1,y1),("targetPoint",x2,y2)):
            ET.SubElement(g,"mxPoint",x=str(x),y=str(y),attrib={"as":which})

    rect("canvas",0,0,1160,459,WHITE)
    for name,x,w,letter,title in [
        ("table",8,315,"A","Source evidence"),("choice",336,358,"B","Agent modeling choice"),
        ("result",710,441,"C","Effect on the analysis")]:
        text(name+"-letter",letter,x,4,26,36,23,BLUE,True)
        text(name+"-title",title,x+30,4,w-30,36,23,INK,True)
        line(name+"-rule",x,45,x+w,45,GREY)
    for x in (329,702):
        line("section"+str(x),x,57,x,293,"#E1E5EB")
    text("sample","CHNS A  ·  1,123 women",9,58,300,24,18,INK,True)
    text("fe-header","Ferritin (µg/L)",130,90,178,23,17,DIM,False,"center")
    for k,x,label in [(0,120,"&lt;15"),(1,220,"≥15")]:
        text("col"+str(k),label,x,116,90,24,17,DIM,True,"center")
    text("hb-units","Hb (g/dL)",10,116,111,24,17,DIM,True)
    counts=tables["table_1"]["counts"]
    for i,(label,y) in enumerate([("&lt;12",148),("≥12",182)]):
        rect("stripe"+str(i),9,y-1,302,32,("#EDF2F8","#F7F9FC")[i])
        text("hb"+str(i),label,14,y,92,29,18,INK,True)
        for j,xx in enumerate((120,220)):
            text("count"+str(i)+str(j),counts[i][j],xx,y,90,29,20,INK,True,"center")
    text("or","Counts imply OR  "+format(result["direct_A"]["odds_ratio"],".3f"),10,224,304,30,21,BLUE,True)
    text("bands","Plus summaries in three Hb bands",10,267,313,24,16,DIM)

    text("pairtitle","Same values in one Hb band",339,58,354,24,18,INK,True)
    for j,(label,x,order,color) in enumerate([
            ("Authored pairs",344,[0,2,1,3,4],BLUE),
            ("Re-paired",522,[3,0,4,1,2],WARM)]):
        text("panel"+str(j),label,x,94,165,25,18,color,True,"center")
        text("h"+str(j),"Hb",x+8,126,53,20,15,DIM,False,"center")
        text("f"+str(j),"Ferritin",x+95,126,69,20,15,DIM,False,"center")
        lx,rx=x+34,x+130
        for i,o in enumerate(order):
            line(f"pair-{j}-{i}",lx,157+18*i,rx,157+18*o,color,1.9)
        for i in range(5):
            dot(f"h-{j}-{i}",lx,157+18*i,4,color,WHITE)
            dot(f"f-{j}-{i}",rx,157+18*i,4,color,color)
    text("schematic","Illustration  ·  each column is ordered",340,267,357,24,16,DIM)

    text("outcome","Whole-cohort rank correlation",711,58,420,24,18,INK,True)
    x0,x1=779,1135
    xx=lambda z: x0+(x1-x0)*(z-.23)/.15
    ref=result["reference"]
    refx=xx(ref["rank"])
    lo,hi=map(xx,ref["rank_interval"])
    rect("reference-interval",lo,114,hi-lo,120,"#F1F3F7")
    line("ref",refx,108,refx,235,INK,1.5,True)
    text("reftext",f"Held-out B  {ref['rank']:.3f}",refx-63,88,132,20,15,INK,True,"center")
    results=sorted(result["pairs"],key=lambda p:p["parent"])
    for i,pair in enumerate(results):
        y=123+20*i
        parent=pair["parent"].replace("ordinary","O").replace("workflow","G")
        a=xx(pair["agent"]["rank"]);r=xx(pair["repairing_expectation"]["rank"])
        text("parent"+str(i),parent,715,y-10,45,20,16,DIM,False,"right")
        line("rank"+str(i),r,y,a,y,"#8295AC",2)
        dot("exp"+str(i),r,y,4.2,WARM,WHITE)
        dot("original"+str(i),a,y,4.2,BLUE,BLUE)
    line("axis",x0,237,x1,237,GREY)
    for tick in (.24,.28,.32,.36):
        x=xx(tick)
        line("tick"+str(tick),x,237,x,242,DIM,1.1)
        text("label"+str(tick),f"{tick:.2f}",x-18,242,36,18,14,DIM,False,"center")
    dot("legend-o",721,277,4.2,BLUE,BLUE)
    text("legend-o-l","Authored",733,263,79,27,16,INK)
    dot("legend-r",819,277,4.2,WARM,WHITE)
    text("legend-r-l","Re-pairing expectation",831,263,173,27,16,INK)
    rect("legend-b",1010,269,13,15,"#E3E7EE")
    text("legend-b-l","B 95% interval",1031,263,123,27,16,INK)
    external=json.loads((ROOT/"work/prospective_iron_dependence_2026-11-20/RESULTS.json").read_text(encoding="utf-8"))
    laws=external["by_law"]
    authors=median(v["rank"] for k,v in laws.items() if k.startswith("author") and v["usable"])
    line("external-rule",8,305,1152,305,GREY)
    text("external-letter","D",8,321,24,34,23,BLUE,True)
    text("external-title","Prospective external test",38,321,290,34,22,INK,True)
    text("external-cohort","Akwa Ibom  ·  603 mothers",10,369,304,24,18,INK,True)
    text("external-material","Same evidence and marginal values",10,402,313,24,16,DIM)
    text("external-rank-title","Whole-cohort rank correlation",340,320,534,29,18,INK,True)
    pos=lambda value: 514+(value+.10)*580
    ci=external["paired_bootstrap"]["reference_rank"]["percentile95"]
    for key,label,y,v,color in [
        ("measured","Measured",363,external["reference"]["rank"],INK),
        ("stat","Statistical law",388,laws["statistical"]["rank"],WARM),
        ("agent","Agent median",413,authors,BLUE)]:
        text("external-label-"+key,label,340,y-11,151,22,16,color,True)
        if key=="measured":
            line("external-ci",pos(ci[0]),y,pos(ci[1]),y,INK,2.2)
            for j,end in enumerate(ci):line("external-cap"+str(j),pos(end),y-5,pos(end),y+5,INK,1.7)
        dot("external-point-"+key,pos(v),y,4.1,color,WHITE if key=="stat" else color)
        text("external-value-"+key,f"{v:.3f}",804,y-11,64,22,16,color,True,"right")
    line("external-axis",pos(-.10),427,pos(.40),427,GREY)
    for tick in (-.1,0,.1,.2,.3,.4):
        x=pos(tick)
        line("external-tick"+str(tick),x,427,x,432,DIM,1.0)
        text("external-number"+str(tick),f"{tick:.1f}",x-19,432,38,18,14,DIM,False,"center")
    line("external-separator",893,323,893,435,"#E1E5EB")
    text("external-or-title","Threshold odds ratio",911,320,240,30,18,INK,True)
    for key,label,y,val,color in [
        ("obs","Measured",362,external["reference"]["odds_ratio"],INK),
        ("laws","Both methods",397,laws["statistical"]["odds_ratio"],BLUE)]:
        text("external-or-"+key,label,912,y,151,24,16,color)
        text("external-odds-"+key,f"{val:.2f}",1070,y,76,24,19,color,True,"right")
    ET.indent(file,space="  ")
    OUT.write_bytes(ET.tostring(file,encoding="utf-8",xml_declaration=True))


if __name__=="__main__":
    build()
