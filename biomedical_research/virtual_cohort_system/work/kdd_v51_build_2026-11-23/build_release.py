"""Build and verify both v0.51 Overleaf editions. Run with Python from any directory."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

import fitz
from PIL import Image, ImageDraw

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parents[1]
PAPER = ROOT / "manuscript/kdd_draft_v51_2026-11-23"
PIN = "1193e8a1101950550d2d4ab97609507a2b4e5826"
OWNER = "github.com/ziwang11112/"
LIMIT = 8
TEX = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-no-shell-escape", "main.tex"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report(path, data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf8",newline="\n")


def read(name):
    return (PAPER/name).read_text(encoding="utf8")


def inputs():
    figures = []
    for name in ("main.tex", "appendix.tex"):
        figures.extend(re.findall(r"\\includegraphics\s*(?:\[[^]]+\])?\s*\{([^}]+)\}", read(name)))
    paths = ["main.tex","appendix.tex","grip_groups_table.tex","references.bib",*sorted(set(figures)),
             "figures/agent-model-authorship.drawio","figures/evidence-and-pairing.drawio"]
    return {name:(PAPER/name).read_bytes() for name in paths}


def build_zip(file, items, destination):
    with zipfile.ZipFile(file,"w") as z:
        for name,data in items.items():
            i=zipfile.ZipInfo(name,(2026,11,23,0,0,0))
            i.compress_type=zipfile.ZIP_DEFLATED
            i.external_attr=0o644<<16
            z.writestr(i,data)
    with zipfile.ZipFile(file) as z:
        assert z.testzip() is None and z.namelist()==list(items)
        z.extractall(destination)
    for name,data in items.items():
        assert (destination/name).read_bytes()==data


def compile_tex(folder):
    for i,cmd in enumerate([TEX, ["bibtex","main"], TEX, TEX, TEX]):
        out=subprocess.run(cmd,cwd=folder,capture_output=True)
        (folder/f"pass-{i+1}.log").write_bytes(out.stdout+out.stderr)
        if out.returncode:
            raise RuntimeError(str(folder)+"\n"+out.stdout[-1800:].decode("utf8","replace"))
    log=(folder/"main.log").read_text(encoding="utf8",errors="replace")
    warn=re.compile(r"LaTeX Warning: (?:Reference|Citation)|undefined (?:references|citations)|Rerun to get|Overfull \\[hv]box|undefined control sequence",re.I)
    warnings=[s for s in log.splitlines() if warn.search(s)]
    return warnings


def enumerate_layout(doc):
    fig, tab = {}, {}
    refs = None
    appendix = None
    for number,page in enumerate(doc,1):
        for line in page.get_text().splitlines():
            for pattern, found in ((r"Figure (\d+):",fig),(r"Table (\d+):",tab)):
                m=re.match(pattern,line)
                if m:
                    assert m[1] not in found,(number,line)
                    found[m[1]]=number
            if line=="References" and refs is None:
                matches=page.search_for("References")
                left=[r for r in matches if r.width>25]
                refs=(number,sorted(left,key=lambda r:(r.y0,r.x0))[0])
            if line=="Construction, data and reproducibility":
                appendix=number
    assert refs and appendix and appendix>=refs[0]
    expected = {}
    for kind,captions in (("figure",fig),("table",tab)):
        all_env=r"\\begin\{"+kind+r"\*?\}"
        main=len(re.findall(all_env,read("main.tex")))
        appendix_source=read("appendix.tex").replace(r"\input{grip_groups_table}",read("grip_groups_table.tex"))
        total=main+len(re.findall(all_env,appendix_source))
        assert set(captions)=={str(i+1) for i in range(total)},(kind,captions,total)
        expected[kind]=[captions[str(i+1)] for i in range(main)]
    number,heading=refs
    # A bibliography that starts at the top of the next left column can follow
    # a full eighth page of main text.
    contents_end=number-1 if heading.x0<170 and heading.y0<73 else number
    for pages in expected.values():
        if pages:
            contents_end=max(contents_end,max(pages))
    return {"paper_pages":len(doc),"last_main_content_page":contents_end,
            "references_begin_page":number,"appendix_begins_page":appendix,
            "figures_by_page":fig,"tables_by_page":tab,"main_figures_by_page":expected["figure"]}


def render(folder,doc):
    output=folder/"render"
    output.mkdir()
    subprocess.run(["pdftoppm","-r","88","-png",str(folder/"main.pdf"),str(output/"p")],
                   check=True,capture_output=True)
    contact=Image.new("RGB",(4*213,((len(doc)+3)//4)*281),"#dde0e4")
    for i,p in enumerate(sorted(output.glob("p-*.png"),key=lambda f:int(f.stem[2:]))):
        with Image.open(p) as f:
            img=f.convert("RGB")
        img.thumbnail((202,261))
        x=(i%4)*213;y=(i//4)*281
        contact.paste(img,(x+5,y+2))
        ImageDraw.Draw(contact).text((x+5,y+265),str(i+1),fill="black")
    contact.save(output/"contact.png")
    return output


def build(probe=False):
    run=Path(tempfile.mkdtemp(prefix="build-",dir=BUILD))
    print("Build directory",run,flush=True)
    items=inputs()
    assert OWNER not in items["main.tex"].decode()
    source=run/"anonymous";source.mkdir()
    for name,data in items.items():
        p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    first_warnings=compile_tex(source)
    with fitz.open(source/"main.pdf") as doc:
        layout=enumerate_layout(doc)
        print(json.dumps(layout),first_warnings,flush=True)
        if probe or first_warnings or layout["last_main_content_page"]>LIMIT:
            doc[0].get_pixmap().save(run/"first.png")
            doc[layout["references_begin_page"]-1].get_pixmap().save(run/"references.png")
    if probe:
        return
    assert not first_warnings,first_warnings
    assert layout["last_main_content_page"]<=LIMIT,layout
    archive=run/"overleaf_v51.zip";fresh=run/"clean-anonymous"
    build_zip(archive,items,fresh)
    wrapper=read("external_review.tex")
    assert wrapper.count(r"\input{main.tex}")==1
    assert len(set(re.findall("https://[^}]+",wrapper)))==4
    linked_items={"main.tex":wrapper.replace(r"\input{main.tex}",r"\input{scientific.tex}").encode(),
                  "scientific.tex":items["main.tex"],**{k:v for k,v in items.items() if k!="main.tex"}}
    external=run/"overleaf_external_review_v51.zip";folder=run/"clean-external"
    build_zip(external,linked_items,folder)
    with ThreadPoolExecutor(max_workers=2) as pool:
        warnings=list(pool.map(compile_tex,[fresh,folder]))
    assert not any(warnings),warnings
    with fitz.open(source/"main.pdf") as doc, fitz.open(fresh/"main.pdf") as check, fitz.open(folder/"main.pdf") as linked:
        assert len(doc)==len(check)==len(linked)
        urls=set()
        for idx,(a,b,c) in enumerate(zip(doc,check,linked,strict=True)):
            assert a.get_text()==b.get_text()
            assert a.get_pixmap().samples==b.get_pixmap().samples
            region=fitz.Rect(0,58 if idx==0 else 0,a.rect.width,a.rect.height)
            assert a.get_pixmap(clip=region).samples==c.get_pixmap(clip=region).samples,(idx+1,"body mismatch")
            assert all(OWNER not in k.get("uri","") for k in a.get_links())
            extra=[k["uri"] for k in c.get_links() if OWNER in k.get("uri","")]
            if idx>0:assert not extra
            urls.update(extra)
        assert len(urls)==4 and all(PIN in u for u in urls),urls
        render(source,doc)
        linked[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(run/"external-first.png")
    for src,name in ((source/"main.pdf","paper.pdf"),(folder/"main.pdf","external_review.pdf"),
                     (archive,archive.name),(external,external.name)):
        shutil.copyfile(src,PAPER/name)
    qa={"release":"0.51","template":"ACM acmart sigconf,anonymous,review",**layout,
        "kdd_research_main_content_limit":LIMIT,"cfp":"https://kdd2027.kdd.org/research-track-call-for-papers/",
        "clean_zip_identical_page_text":True,"clean_zip_identical_page_render":True,"overfull_boxes":0,
        "unresolved_citations_or_cross_references":0,
        "resolved_bibliography_entries":(source/"main.bbl").read_text(encoding="utf8").count(r"\bibitem"),
        "paper_sha256":sha(PAPER/"paper.pdf"),"overleaf_sha256":sha(archive),"source_files":list(items)}
    report(PAPER/"BUILD_CHECK.json",qa)
    report(PAPER/"EXTERNAL_REVIEW_CHECK.json",{"release":"0.51","scientific_body_render_equal_each_page":True,
          "text_page_one_below_points":58,"repository_links":sorted(urls),
          "external_pdf_sha256":sha(PAPER/"external_review.pdf"),"external_zip_sha256":sha(external)})
    print("Validated archives, page content, rendered pages and four pinned review links.",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--probe",action="store_true",help="Build one anonymous preview before packaging")
    build(parser.parse_args().probe)

