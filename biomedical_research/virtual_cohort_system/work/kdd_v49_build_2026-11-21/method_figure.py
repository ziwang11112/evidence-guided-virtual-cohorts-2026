"""Create the editable method figure using the original-paper task and published aggregate results."""

import argparse
import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.special import expit, ndtr
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "work/original_paper_capability_2026-11-17"
OUT = ROOT / "manuscript/kdd_draft_v49_2026-11-21/figures/agent-model-authorship.drawio"
INK, BLUE, RUST, PLUM = "#162B43", "#21618B", "#AD512D", "#695181"
MUTED, GRID, LINE = "#455D70", "#DCE3E8", "#8195A3"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def iron_trace():
    names = ["P1_IRON_A1", "P1_IRON_A2", "P1_IRON_A3"]
    labels = ["Clayton copula", "Latent iron-store mixture", "Saturating Hb response"]
    signatures = ["joint_prob(theta)", "np.maximum(0.0, knot-z)", "expit(spec['restriction_exponent']"]
    logs = {entry["episode_id"]: entry for entry in read_json(RUN / "audit/TRACE_SUMMARY.json")}
    with (RUN / "analysis/author_results.csv").open(encoding="utf-8", newline="") as f:
        rows = {(row["episode_id"], row["estimand"]): row for row in csv.DictReader(f)}

    results = []
    endpoints = ["odds_ratio", "spearman"]
    for name, label, signature in zip(names, labels, signatures, strict=True):
        candidate = RUN / "episodes" / name / "candidates/v001"
        assert signature in (candidate / "generator.py").read_text(encoding="utf-8")
        log = logs[name]
        assert log["model"] == "gpt-6.1-sol"
        for tool in ("read_provided_paper", "literature_search", "submit_candidate", "run_candidate", "finalize"):
            assert log["tool_counts"][tool] >= 1
        assert all(int(rows[name, key]["available_seeds"]) == 3 for key in endpoints)
        results.append((label, [float(rows[name, key]["seed_mean"]) for key in endpoints]))
    reference = []
    for key in endpoints:
        measured = {float(rows[name, key]["reference"]) for name in names}
        assert len(measured) == 1
        reference.append(measured.pop())
    results.append(("Measured US sample", reference))
    counts = read_json(RUN / "episodes/P1_IRON_A2/candidates/v001/model_spec.json")["source_cells_a_b_c_d"]
    assert counts == read_json(RUN / "episodes/P1_IRON_A1/candidates/v001/model_spec.json")["dependence"]["crude_or_expression"]
    return counts, results


def model_profiles():
    """Display one analytic component of each archived law, on its own scale."""
    def spec(i):
        return read_json(RUN / f"episodes/P1_IRON_A{i}/candidates/v001/model_spec.json")

    a, b, c = (spec(i) for i in (1, 2, 3))
    hb = a["hemoglobin"]
    means, sds = np.array(hb["means_g_dl"]), np.array(hb["sds_g_dl"])
    lo, hi = hb["support_g_dl"]
    cdf_low, cdf_high = ndtr((lo-means)/sds), ndtr((hi-means)/sds)
    ph = np.dot(hb["weights"], (ndtr((12-means)/sds)-cdf_low)/(cdf_high-cdf_low))
    pf = a["ferritin"]["probability_below_15"]
    n11, n10, n01, n00 = a["dependence"]["crude_or_expression"]
    odds = n11*n00/(n10*n01)
    def fit(theta):
        joint = (ph**(-theta) + pf**(-theta) - 1)**(-1/theta)
        return joint*(1-ph-pf+joint) - odds*(ph-joint)*(pf-joint)
    theta = brentq(fit, 1e-5, 5.0)
    quantiles = np.linspace(0.01, 1, 33)
    diagonal = (2*quantiles**(-theta)-1)**(-1/theta)
    z = np.linspace(0.0, 6.0, 45)
    means, sds = np.log(b["store_geometric_means"]), b["store_log_sds"]
    mix = b["store_mixture_probability"]
    density = mix*norm.pdf(z,means[0],sds[0]) + (1-mix)*norm.pdf(z,means[1],sds[1])
    log_stores = np.linspace(-1,5,45)
    response = expit(c["restriction_exponent"]*(log_stores-np.log(c["restriction_halfpoint_ug_l"])))
    return [diagonal, density, response]


class Diagram:
    def __init__(self):
        self.xml = ET.Element("mxfile", host="app.diagrams.net", compressed="false")
        page = ET.SubElement(self.xml, "diagram", id="method", name="Authorship and evaluation")
        model = ET.SubElement(page, "mxGraphModel", grid="0", page="1", pageWidth="1270",
                              pageHeight="430", background="#ffffff", adaptiveColors="auto")
        self.root = ET.SubElement(model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.count = 0

    def vertex(self, x, y, w, h, style, value="", name=None):
        self.count += 1
        ident = name or f"v{self.count}"
        cell = ET.SubElement(self.root, "mxCell", id=ident, parent="1", vertex="1",
                             style=style + ";html=1;", value=value)
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h),
                      attrib={"as": "geometry"})
        return ident

    def rect(self, x, y, w, h, fill, border="none", name=None, rounded=False):
        return self.vertex(x, y, w, h, f"rounded={int(rounded)};arcSize=6;strokeWidth=1.5;"
                           f"fillColor={fill};strokeColor={border};", name=name)

    def label(self, x, y, w, h, value, size=20, color=INK, bold=False, align="left"):
        return self.vertex(x, y, w, h, "text;whiteSpace=nowrap;overflow=visible;strokeColor=none;"
                           f"fillColor=none;verticalAlign=middle;align={align};spacing=0;"
                           f"fontFamily=Arial;fontSize={size};fontStyle={int(bold)};fontColor={color}", value)

    def path(self, points, color, width=2, arrow=False):
        self.count += 1
        style = f"html=1;endArrow={'block' if arrow else 'none'};endFill=1;endSize=7;startArrow=none;strokeColor={color};strokeWidth={width};rounded=0;"
        cell = ET.SubElement(self.root, "mxCell", id=f"e{self.count}", parent="1", edge="1", style=style)
        geo = ET.SubElement(cell, "mxGeometry", relative="1", attrib={"as": "geometry"})
        def pt(parent, xy, role=None):
            attrs = {"x": str(xy[0]), "y": str(xy[1])}
            if role:
                attrs["as"] = role
            ET.SubElement(parent, "mxPoint", attrs)
        pt(geo, points[0], "sourcePoint")
        pt(geo, points[-1], "targetPoint")
        if len(points) > 2:
            inner = ET.SubElement(geo, "Array", attrib={"as": "points"})
            for point in points[1:-1]:
                pt(inner, point)

    def connect(self, source, target):
        self.count += 1
        edge = ET.SubElement(self.root, "mxCell", id=f"e{self.count}", edge="1", parent="1",
                             source=source, target=target, style="html=1;edgeStyle=orthogonalEdgeStyle;"
                             "endArrow=block;endFill=1;endSize=7;strokeWidth=2;strokeColor=#546B7F;")
        ET.SubElement(edge, "mxGeometry", relative="1", attrib={"as": "geometry"})

    def mark(self, x, y, color, diamond=False):
        style = f"shape={'rhombus' if diamond else 'ellipse'};aspect=fixed;fillColor={color};strokeColor={color};"
        self.vertex(x-5, y-5, 10, 10, style)


def make_diagram(check=False):
    counts, results = iron_trace()
    d = Diagram()

    # The cards depict the original-paper protocol. The comparison contracts are in the main table.
    d.rect(2, 2, 1242, 407, "#FFFFFF")
    for x, width, fill, border, ident in [
        (8, 226, "#F0F4F7", "#D0DCE3", "request"),
        (264, 351, "#E6F0F8", "#8DB2CA", "author"),
        (645, 245, "#F8EFE8", "#D9B7A5", "executor"),
        (920, 319, "#F2EFF6", "#CFBEDD", "evaluator"),
    ]:
        d.rect(x, 8, width, 120, fill, border, name=ident, rounded=True)
    for a, b in [("request","author"),("author","executor"),("executor","evaluator")]:
        d.connect(a,b)

    d.label(25, 16, 190, 33, "Study request", 27, INK, True)
    d.rect(209, 87, 19, 24, "#FFFFFF", LINE)
    d.rect(204, 83, 19, 24, "#FFFFFF", LINE)
    d.path([(208,91),(218,91)],LINE,1.3)
    d.path([(208,96),(217,96)],LINE,1.3)
    d.path([(208,101),(214,101)],LINE,1.3)
    d.label(25, 58, 208, 24, "Population and analyses", 18, MUTED)
    d.label(25, 85, 190, 24, "Starting article", 18, MUTED)

    d.label(282, 16, 322, 33, "Scientific agent", 27, BLUE, True)
    for end in [(594,22),(594,42)]:
        d.path([(566,32),end],BLUE,1.7)
        d.vertex(end[0]-4,end[1]-4,8,8,"shape=ellipse;fillColor=#FFFFFF;strokeColor=#21618B;strokeWidth=1.6")
    d.vertex(559,27,10,10,"shape=ellipse;fillColor=#21618B;strokeColor=#21618B")
    d.label(282, 55, 321, 25, "Read evidence  →  choose a joint law", 18, INK)
    d.label(282, 83, 320, 26, "Write sampler and parameter notes", 18, INK)

    d.label(662, 16, 200, 33, "Frozen program", 25, RUST, True)
    d.path([(865,31),(865,25),(868,22),(874,22),(877,25),(877,31)],RUST,1.9)
    d.rect(861,31,20,15,"#F8EFE8",RUST,rounded=True)
    d.path([(871,36),(871,41)],RUST,1.4)
    d.label(662, 55, 217, 25, "Run in isolation", 18, INK)
    d.label(662, 83, 217, 26, "Draw virtual records", 18, INK)

    d.label(937, 16, 279, 33, "Scientific analysis", 26, PLUM, True)
    d.label(937, 55, 155, 22, "Virtual records", 18, INK)
    d.label(937, 84, 159, 22, "Measured records", 18, PLUM)
    d.path([(1086,66),(1096,66),(1096,81),(1113,81)], LINE, 1.8)
    d.path([(1086,95),(1096,95),(1096,81),(1113,81)], LINE, 1.8)
    d.rect(1113, 59, 111, 45, "#FFFFFF", "#CABCD5", rounded=True)
    d.label(1113, 61, 111, 40, "Estimator", 18, INK, True, "center")

    d.label(12, 150, 293, 29, "A   Article evidence", 24, BLUE, True)
    d.label(330, 150, 354, 29, "B   Agent-authored models", 24, BLUE, True)
    d.label(724, 150, 510, 29, "C   Analyses on the resulting records", 24, BLUE, True)
    for left, right in [(12,297),(330,692),(723,1236)]:
        d.rect(left, 185, right-left, 2, GRID)
    d.rect(311, 199, 1.4, 201, GRID)
    d.rect(707, 199, 1.4, 201, GRID)

    d.label(14, 206, 105, 29, "Hb (g/dL)", 18, MUTED)
    d.label(124, 195, 170, 24, "Ferritin (µg/L)", 18, MUTED, align="center")
    d.label(121, 222, 84, 25, "&lt;15", 18, MUTED, align="center")
    d.label(206, 222, 84, 25, "≥15", 18, MUTED, align="center")
    d.rect(13, 253, 283, 38, "#E8F0F6")
    d.rect(13, 293, 283, 38, "#F2F5F8")
    for i, (y, label) in enumerate([(253, "&lt;12"),(293,"≥12")]):
        d.label(25,y,78,38,label,20,INK,True)
        for j in range(2):
            d.label(121+85*j,y,84,38,f"{counts[2*i+j]:,}",22,INK,True,"center")
    source_or = counts[0]*counts[3]/(counts[1]*counts[2])
    d.label(17, 350, 275, 30, f"Source odds ratio  {source_or:.2f}", 21, BLUE, True)

    d.label(332, 207, 350, 28, "Same article, three GPT sessions", 18, MUTED)
    ys=[257,294,331,376]
    profiles=model_profiles()
    for i, ((label, _), cy) in enumerate(zip(results,ys,strict=True)):
        if i < 3:
            d.label(334,cy-13,42,25,f"A{i+1}",18,RUST,True)
            profile=profiles[i]
            normal=(profile-profile.min())/(profile.max()-profile.min())
            xs=np.linspace(379,427,len(normal))
            points=[(round(x,2),round(cy+11-24*y,2)) for x,y in zip(xs,normal,strict=True)]
            d.path([(377,cy-14),(377,cy+13),(429,cy+13)],LINE,1)
            d.path(points,BLUE,2.4)
            d.label(441,cy-16,260,32,label,21,INK,True)
        else:
            d.rect(326,356,910,40,"#F3F0F6")
            d.label(335,cy-15,348,30,"Measured US women (n = 979)",20,PLUM,True)

    for j, (x,w,lim,title,ticks) in enumerate([
        (730,216,20,"Threshold odds ratio",(0,10,20)),
        (998,207,0.50,"Rank correlation",(0,0.25,0.50)),
    ]):
        d.label(x, 202, w+32, 28, title, 20, INK, True)
        for t in ticks:
            tx=x+w*t/lim
            d.rect(tx,242,1.3,149,GRID)
            tick=str(t) if j==0 else ("0" if t==0 else f"{t:.2f}")
            d.label(tx-23,392,46,21,tick,16,MUTED,align="center")
        for i, ((_, pair), cy) in enumerate(zip(results,ys,strict=True)):
            val=pair[j]
            px=x+w*val/lim
            color=PLUM if i==3 else RUST
            d.mark(px,cy,color,diamond=(i==3))
            d.label(px+10,cy-13,62,26,f"{val:.{2 if j==0 else 3}f}",18,color,True)

    ids=[c.get("id") for c in d.root.findall("mxCell")]
    assert len(ids)==len(set(ids))
    ET.indent(d.xml, space="  ")
    content = ET.tostring(d.xml, encoding="utf-8", xml_declaration=False)+b"\n"
    if check:
        if OUT.read_bytes() != content:
            raise ValueError("The published model diagram differs from its evidence trace.")
        print("Three archived model implementations and eight displayed estimates verified.")
    else:
        OUT.write_bytes(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare with the existing editable figure.")
    make_diagram(check=parser.parse_args().check)
