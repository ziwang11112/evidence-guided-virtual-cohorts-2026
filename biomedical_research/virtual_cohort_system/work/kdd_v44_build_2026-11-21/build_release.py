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
PAPER = ROOT / "manuscript/kdd_draft_v44_2026-11-21"
BUILD = Path(__file__).resolve().parent
assert BUILD.name == "kdd_v44_build_2026-11-21"
SOURCE = BUILD / "source"
FRESH = Path(tempfile.mkdtemp(prefix="roundtrip-", dir=BUILD))
QA = BUILD / "final-render"
for folder in (SOURCE, FRESH, QA):
    folder.mkdir(exist_ok=True, parents=True)

figure_names = []
for f in ["main.tex", "appendix.tex"]:
    figure_names += re.findall(r"\\includegraphics\[[^]]+\]\{([^}]+)\}", (PAPER/f).read_text(encoding="utf-8"))
files = ["main.tex", "appendix.tex", "references.bib", *sorted(figure_names)]
assert len(files) == len(set(files)) == 20
def sha(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()

zip_path = PAPER/"overleaf_v44.zip"
with zipfile.ZipFile(zip_path,"w") as z:
    for name in files:
        info=zipfile.ZipInfo(name,(2026,11,21,0,0,0))
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
assert len(fig_pages)==17 and len(table_pages)==9 and refs is not None and refs<=8
assert max(fig_pages[str(i)] for i in (1,2,3,4,5,6))<=refs
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
for name in ["evidence-and-pairing","lifestyle-main","pairing-attribution","nonhdl-selection","lipid-rank-maps","decisions-before-disclosure","where-pairing-can-help","historical-means-and-pairing","bilateral-grip-transfer","grip-correlation-sensitivity"]:
    with fitz.open(PAPER/"figures"/(name+".pdf")) as doc:
        doc[0].get_pixmap(matrix=fitz.Matrix(2,2)).save(QA/(name+".png"))

def write_report(name, obj):
    (PAPER/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")

receipt={"release":"0.44","template":"ACM acmart sigconf,anonymous,review",
         "paper_pages":len(a),"references_begin_page":refs,"appendix_begins_page":appendix_start,
         "figures_by_page":fig_pages,"tables_by_page":table_pages,
         "paper_sha256":sha(PAPER/"paper.pdf"),"overleaf_sha256":sha(zip_path),
         "resolved_bibliography_entries":(SOURCE/"main.bbl").read_text(encoding="utf-8").count(r"\bibitem"),
         "source_files":files,"clean_zip_identical_page_text":True,"overfull_boxes":0,
         "unresolved_citations_or_cross_references":0,
         "reproduction":"work/bilateral_grip_transfer_2026-11-21/verify.py --public-only","editable_main_figure":"figures/evidence-and-pairing.drawio"}
write_report("BUILD_CHECK.json",receipt)
print(json.dumps(receipt,indent=2))
