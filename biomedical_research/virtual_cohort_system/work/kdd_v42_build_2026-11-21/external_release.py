"""Package the linked edition and check its scientific pages against the anonymous PDF."""
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import fitz

root = Path(__file__).resolve().parents[2]
paper = root / "manuscript/kdd_draft_v42_2026-11-21"
build = Path(__file__).resolve().parent
receipt = json.loads((paper/"BUILD_CHECK.json").read_text(encoding="utf-8"))
wrapper = (paper/"external_review.tex").read_text(encoding="utf-8").replace(r"\input{main.tex}",r"\input{scientific.tex}")
archive = paper / "overleaf_external_review_v42.zip"
with zipfile.ZipFile(archive,"w") as z:
    for name in ["main.tex",*receipt["source_files"]]:
        if name=="main.tex" and name in z.namelist():
            dest,data="scientific.tex",(paper/name).read_bytes()
        else:
            dest,data=name,(wrapper.encode() if name=="main.tex" else (paper/name).read_bytes())
        i=zipfile.ZipInfo(dest,(2026,11,21,0,0,0))
        i.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(i,data)

folder=Path(tempfile.mkdtemp(prefix="linked-",dir=build))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    z.extractall(folder)
tex=["pdflatex","-interaction=nonstopmode","-halt-on-error","-file-line-error","-no-shell-escape","main.tex"]
for idx,cmd in enumerate([tex,["bibtex","main"],tex,tex]):
    out=subprocess.run(cmd,cwd=folder,capture_output=True)
    (folder/f"pass{idx}.log").write_bytes(out.stdout+out.stderr)
    if out.returncode:raise RuntimeError(out.stdout[-1500:])
log=(folder/"main.log").read_text(encoding="utf-8",errors="replace")
assert not re.search(r"LaTeX Warning: (?:Reference|Citation)|undefined (?:references|citations)|Rerun to get|Overfull \\[hv]box",log,re.I)
out=folder/"main.pdf"
with fitz.open(out) as a,fitz.open(paper/"paper.pdf") as b:
    assert len(a)==len(b)
    # The publisher's main title and body begin below the two margin links, retained only for review.
    for i,(x,y) in enumerate(zip(a,b,strict=True)):
        rect=fitz.Rect(0,58 if i==0 else 0,x.rect.width,x.rect.height)
        assert x.get_pixmap(clip=rect).samples==y.get_pixmap(clip=rect).samples,(i+1,"page mismatch")
    links={k["uri"] for k in a[0].get_links() if "uri" in k and "github.com" in k["uri"]}
    assert len(links)==4,links
    a[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(build/"final-render/external-first.png")
shutil.copy2(out,paper/"external_review.pdf")
rec={"release":"0.42","scientific_body_render_equal_each_page":True,"text_page_one_below_points":58,
     "repository_links":sorted(links),"external_pdf_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
     "external_zip_sha256":hashlib.sha256(archive.read_bytes()).hexdigest()}
(paper/"EXTERNAL_REVIEW_CHECK.json").write_text(json.dumps(rec,indent=2)+"\n",encoding="utf-8",newline="\n")
print("External review edition verified with four repository links.")
