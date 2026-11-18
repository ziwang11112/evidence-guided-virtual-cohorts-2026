"""Verify manuscript tables and plot coordinates against retained aggregate outputs."""
import hashlib
import json
from pathlib import Path
import re
from unittest.mock import patch
import zipfile

import fitz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import plot_analyses

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W = ROOT / "work"
M = ROOT / "manuscript"
PACKAGE = M / "kdd_draft_v34_2026-11-18"
draft_path = M / "DRAFT_v0_34.md"
draft = draft_path.read_text(encoding="utf-8")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def table(label):
    match = re.search(r"^\*\*Table " + label + r"\..*\n\n((?:\|.*\n)+)", draft, re.M)
    assert match, label
    return [line.strip("|").strip().split(" | ") for line in match[1].splitlines()[2:]]

def plot_axes(draw):
    with patch.object(plot_analyses, "save") as save:
        draw()
    return save.call_args.args[0]

def check_paper():
    df = pd.read_csv(W / "original_paper_capability_2026-11-17/analysis/seed_results.csv")
    assert len(df) == 99 and df.status.eq("computed").all()
    groups = df.groupby(["estimand","episode_id"]).value.agg(["mean","min","max","count"])
    assert len(groups) == 33 and groups["count"].eq(3).all()
    ref = df.groupby("estimand").reference.first()
    order = ["bmi_sbp","bmi_dbp","residual_correlation","sbp.sd_population","dbp.sd_population",
             "sbp_below_dbp_fraction","odds_ratio","joint_prevalence","spearman","low_hb_fraction","low_ferritin_fraction"]
    rows = table("S8")
    assert len(rows) == len(order)
    for k,row in zip(order,rows):
        g = groups.loc[k]
        m = 100 if k.endswith("fraction") or k == "joint_prevalence" else 1
        assert row[1:] == [f"{v*m:.3f}" for v in [*g["mean"],ref[k]]]
    fig = plot_axes(plot_analyses.paper_estimates)
    for ax,k in zip(fig.axes,[*order[:3],*order[6:9]]):
        m = 100 if k == "joint_prevalence" else 1
        points = [dots.get_offsets()[0,0] for dots in ax.collections]
        np.testing.assert_allclose(points, groups.loc[k]["mean"]*m, rtol=1e-12)
        np.testing.assert_allclose(ax.lines[0].get_xdata(), ref[k]*m,rtol=1e-12)
        np.testing.assert_allclose([line.get_xdata() for line in ax.lines[1:]],groups.loc[k][["min","max"]]*m,rtol=1e-12)
    plt.close(fig)
    return {"seed_endpoints":len(df),"constructor_endpoints":len(groups),"supplement_rows":len(rows),"primary_panels":6}

def check_lifestyle():
    df = pd.read_csv(W / "matched_size_utility_2026-11-17/DIFFERENCES.csv")
    assert len(df) == 31500 and df.status.eq("computed").all()
    df["absolute"] = df.difference.abs()
    g = df.groupby(["trait","contrast","stream"]).agg(signed=("difference","mean"), absolute=("absolute","mean"), n=("difference","size"))
    assert len(g) == 63 and g.n.eq(500).all()
    rows = table("S7")
    assert len(rows) == 9
    fig = plot_axes(plot_analyses.matched_lifestyle)
    traits = ["bmi","total_cholesterol","hdl_cholesterol"]
    contrasts = ["rural_minus_pastoralist","urban_minus_pastoralist","urban_minus_rural"]
    for i,(ax,t) in enumerate(zip(fig.axes,traits)):
        for j,c in enumerate(contrasts):
            block = g.loc[(t,c),:].sort_index()
            v = block.drop("R_A")
            r = block.loc["R_A","absolute"]
            assert rows[3*i+j][1:] == [f"{r:.3f}",f"{v.absolute.min():.3f} to {v.absolute.max():.3f}",f"{v.signed.min():.3f} to {v.signed.max():.3f}"]
            dots = ax.collections[3*j:3*j+3]
            xs = np.concatenate([np.asarray(d.get_offsets()[:,0]) for d in dots])
            np.testing.assert_allclose(xs,[r,*v.absolute],rtol=1e-12)
    plt.close(fig)
    return {"paired_differences":len(df),"matched_point_coordinates":len(g),"supplement_rows":len(rows),"contrasts":9}

def check_controls():
    spec = [("pns","residual_correlation",1,4),("pns","bmi_sbp",1,4),("pns","bmi_dbp",1,4),
            ("iron","odds_ratio",1,4),("iron","joint_prevalence",100,3),("iron","spearman",1,4)]
    rows = table("1")
    assert len(rows) == len(spec)
    for (case,key,m,dec),row in zip(spec,rows):
        df = pd.read_csv(W / f"{case}_evidence_content_control_2026-11-16/analysis/arm_results.csv")
        x = df[df.estimand == key].set_index("arm").author_mean_absolute_reference_difference
        assert row[1:] == [f"{x[arm]*m:.{dec}f}" for arm in ["SUMMARY","JOINT"]]
    return len(rows)

def check_publication():
    locations = [i for i,l in enumerate(draft.splitlines()) if "LLMSynthor" in l]
    assert len(locations)==2
    assert draft.splitlines().index("## 2. Related work") < locations[0] < draft.splitlines().index("## 3. From a research request to a virtual cohort")
    assert draft.splitlines().index("## References") < locations[1] < draft.splitlines().index("## Supplementary results")
    for _,path in re.findall(r"(\[[^\]\n]+\])\(([^)\n]+)\)",draft):
        if not path.startswith(("http://","https://")):
            assert (M/path).exists(),path
    inputs=json.loads((PACKAGE/"BUILD_INPUTS.json").read_text())
    assert inputs["source_sha256"]==sha(draft_path) and inputs["figure_count"]==5 and inputs["table_count"]==9
    assert {f["sha256"] for f in inputs["figures"]}=={sha(p) for p in (PACKAGE/"figures").glob("*.pdf")}
    archive=PACKAGE/"overleaf_v34.zip"
    with zipfile.ZipFile(archive) as z:
        assert sorted(z.namelist())==sorted(["paper.tex","OVERLEAF_README.md",*["figures/"+f["file"] for f in inputs["figures"]]])
        assert all(z.read(n)==(PACKAGE/n).read_bytes() for n in z.namelist())
    with fitz.open(PACKAGE/"paper.pdf") as doc, fitz.open(PACKAGE/"tmp/pdfs/standalone/paper.pdf") as second:
        pages=[p.get_text() for p in doc]
        assert pages==[p.get_text() for p in second]
        assert all(p.strip() for p in pages)
        refs_page=next(i+1 for i,p in enumerate(pages) if "Supplementary results" in p)
        for text in ["Table S7","Table S8","Figure 2","Figure 3","0.9373","17.790"]:
            assert text in "\n".join(pages),text
    for d in [PACKAGE, PACKAGE/"tmp/pdfs/standalone"]:
        log=(d/"build-pass-2.txt").read_text(encoding="utf-8",errors="replace")
        assert not re.search(r"Overfull|Missing character|LaTeX Warning|undefined references",log),d
    old_hash=sha(M/"DRAFT_v0_33.md")
    assert old_hash=="20ae7f87682a422db3e7c7af6b66962956634be861eb75789b340722130eeb3c"
    return {"pages":len(pages),"supplement_begins":refs_page,"figures":5,"tables":9,
            "independent_zip_compilation_text_identical":True,"final_log_overflow_or_missing_glyphs":0,
            "old_draft_sha256":old_hash,"pdf_sha256":sha(PACKAGE/"paper.pdf"),"zip_sha256":sha(archive)}

if __name__=="__main__":
    result={"original_paper":check_paper(),"matched_lifestyle":check_lifestyle(),"controlled_comparison_rows":check_controls(),
            "publication":check_publication(),"new_model_calls":0,"new_record_tables":0}
    (HERE/"QA.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
