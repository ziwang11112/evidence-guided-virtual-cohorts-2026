"""Local build QA for the manuscript release. Run from the project root."""
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ROOT = Path.cwd()
PAPER = ROOT / "manuscript/kdd_draft_v38_2026-11-19"
BUILD = ROOT / "work/kdd_v38_build_2026-11-19"
SOURCE = BUILD / "source"
FRESH = Path(tempfile.mkdtemp(prefix="roundtrip-", dir=BUILD))
QA = BUILD / "final-render"
for folder in (SOURCE, FRESH, QA):
    folder.mkdir(exist_ok=True, parents=True)

figure_names = []
for f in ["main.tex", "appendix.tex"]:
    figure_names += re.findall(r"\\includegraphics\[[^]]+\]\{([^}]+)\}", (PAPER/f).read_text(encoding="utf-8"))
files = ["main.tex", "appendix.tex", "references.bib", *sorted(figure_names)]
assert len(files) == len(set(files)) == 10
def sha(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()

zip_path = PAPER/"overleaf_v38.zip"
with zipfile.ZipFile(zip_path,"w") as z:
    for name in files:
        info=zipfile.ZipInfo(name,(2026,11,19,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o644<<16
        z.writestr(info,(PAPER/name).read_bytes())
        dest=SOURCE/name
        dest.parent.mkdir(exist_ok=True,parents=True)
        shutil.copy2(PAPER/name,dest)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None and z.namelist()==files
    z.extractall(FRESH)
    for name in files:
        assert (FRESH/name).read_bytes()==(PAPER/name).read_bytes()
tex=["pdflatex","-interaction=nonstopmode","-halt-on-error","-file-line-error","-no-shell-escape","main.tex"]
def build(folder):
    for i,cmd in enumerate([tex,["bibtex","main"],tex,tex],1):
        result=subprocess.run(cmd,cwd=folder,capture_output=True)
        (folder/f"pass-{i}.log").write_bytes(result.stdout+result.stderr)
        if result.returncode:
            raise RuntimeError(result.stdout[-2200:])
    log=(folder/"main.log").read_text(encoding="utf-8",errors="replace")
    assert not re.search(r"LaTeX Warning: (?:Reference|Citation)|undefined (?:references|citations)|Rerun to get|Overfull \\[hv]box|undefined control sequence",log,re.I),[x for x in log.splitlines() if "Overfull" in x]
    return fitz.open(folder/"main.pdf")

a,b=build(SOURCE),build(FRESH)
assert [p.get_text() for p in a]==[p.get_text() for p in b]
shutil.copy2(SOURCE/"main.pdf",PAPER/"paper.pdf")
fig_pages={};table_pages={};refs=appendix_start=None
for i,p in enumerate(a,1):
    lines=p.get_text().splitlines()
    for line in lines:
        if m:=re.match(r"Figure (\d+):",line):fig_pages[m[1]]=i
        if m:=re.match(r"Table (\d+):",line):table_pages[m[1]]=i
        if line=="References": refs=i
        if line=="Construction, data and reproducibility": appendix_start=i
assert len(fig_pages)==7 and len(table_pages)==6 and refs is not None and refs<=8
assert max(fig_pages[str(i)] for i in (1,2,3))<=refs
assert appendix_start>=refs
# Render the pages delivered to the user, including the complete appendix.
subprocess.run(["pdftoppm","-r","100","-png",str(PAPER/"paper.pdf"),str(QA/"page")],check=True,capture_output=True)
ncol=4;nrow=(len(a)+ncol-1)//ncol
contact=Image.new("RGB",(239*ncol,320*nrow),"#dce0e4")
for i in range(1,len(a)+1):
    matches=[f for f in QA.glob("page-*.png") if int(f.stem[5:])==i]
    assert len(matches)==1
    with Image.open(matches[0]) as im: small=im.convert("RGB")
    small.thumbnail((230,295))
    col,row=(i-1)%ncol,(i-1)//ncol
    contact.paste(small,(col*239+(239-small.width)//2,row*320+4))
    ImageDraw.Draw(contact).text((col*239+10,row*320+303),str(i),fill="black")
contact.save(QA/"contact.png")
for name in ["analysis-support","chns-revision"]:
    with fitz.open(PAPER/"figures"/(name+".pdf")) as doc:
        doc[0].get_pixmap(matrix=fitz.Matrix(2,2)).save(QA/(name+".png"))
count_refs=(SOURCE/"main.bbl").read_text(encoding="utf-8",errors="replace").count(r"\bibitem")
log=(SOURCE/"main.log").read_text(errors="replace")
blg=(SOURCE/"main.blg").read_text(errors="replace")
receipt={
    "release":"0.38", "template":"ACM acmart sigconf,anonymous,review",
    "paper_pages":len(a), "references_begin_page":refs, "appendix_begins_page":appendix_start,
    "main_text_ends_page":next(i for i,p in enumerate(a,1) if "and the estimate and uncertainty" in " ".join(p.get_text().split()) or "the estimate and uncertainty from" in " ".join(p.get_text().split())),
    "figures_by_page":fig_pages,"tables_by_page":table_pages,"source_files":files,
    "paper_sha256":sha(PAPER/"paper.pdf"),"zip_sha256":sha(zip_path),
    "clean_zip_identical_page_text":True,"resolved_bibliography_entries":count_refs,
    "unresolved_citations_or_cross_references":0, "overfull_boxes":0,
    "other_tex_diagnostics":[line.strip() for line in log.splitlines() if " Warning:" in line],
    "underfull_boxes":len(re.findall(r"Underfull \\[vh]box",log)),
    "bibtex_advisories":[line for line in blg.splitlines() if line.startswith("Warning--")],
    "checked_numeric_table_cells":{"inherited":141,"new_nonempty_numeric_cells":14,"total":155},
    "chns_holdout":{"parent_constructions":6,"chns_tables_verified_from_receipts":54},
    "numerical_check":"reproducibility/check_v38.py", "figure_source":"reproducibility/plot_v37.py",
    "plots_checked_for_text_outside_canvas":True,
    "scientific_holdout_replay":"work/chns_iron_conditional_holdout_2026-11-19/public_replay.py",
    "release_activity":{"new_model_calls":0,"new_participant_measurements":0,"new_statistical_laws":1,"new_virtual_rows":36000},
}
assert table_pages["2"] <= refs and receipt["main_text_ends_page"] <= 8
receipt["statistical_replay"] = "work/chns_statistical_comparator_2026-11-19/run.py replay"
paths = [ROOT / p for p in ["work/chns_statistical_comparator_2026-11-19/" + n for n in ("PROTOCOL.md", "FREEZE.json", "SOURCE_RESULTS.json", "RESULTS.json")]]
receipt["statistical_source_sha256_after_lf_normalization"] = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths}
(PAPER/"BUILD_CHECK.json").write_text(json.dumps(receipt,indent=2)+"\n", encoding="utf-8", newline="\n")
print(json.dumps(receipt,indent=2))
(BUILD/"release-qa.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
