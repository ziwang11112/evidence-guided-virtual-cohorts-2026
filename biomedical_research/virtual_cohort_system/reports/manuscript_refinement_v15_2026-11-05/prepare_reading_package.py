"""Prepare a new reading edition; retain old drafts and scientific outputs."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;P=R.parents[1];M=P/'manuscript'
F=M/'paper_figures_v15_2026-11-05';B=M/'conference_draft_v15_2026-11-05'
F.mkdir(exist_ok=True);B.mkdir(exist_ok=True)
old=M/'paper_figures_v14_2026-11-05'
copies={'fig1-agent-framework.drawio':'fig1-agent-framework.drawio',
        'fig5-open-retrieval':'figS1-open-retrieval',
        'fig4-longitudinal-use':'figS2-longitudinal-use',
        'figS1-analysis-use':'figS4-analysis-use'}
reuse=[]
for src,dst in copies.items():
    for ext in ('.pdf','.svg','.png'):
        a,b=old/(src+ext),F/(dst+ext);shutil.copyfile(a,b)
        reuse.append(dict(source=str(a.relative_to(P)),destination=str(b.relative_to(P)),
                          sha256=hashlib.sha256(b.read_bytes()).hexdigest(),identical=a.read_bytes()==b.read_bytes()))
(R/'FIGURE_REUSE.json').write_text(json.dumps(reuse,indent=2)+'\n')
builder=(M/'conference_draft_v14_2026-11-05/build_reading_copy.py').read_text(encoding='utf-8')
builder=builder.replace('DRAFT_v0_14.md','DRAFT_v0_15.md').replace('paper_figures_v14_2026-11-05','paper_figures_v15_2026-11-05')
a=builder.index('FILES = ');b=builder.index('HERE.mkdir',a)
builder=builder[:a]+'''FILES = ['fig1-agent-framework.drawio','fig2-evidence-results','fig3-cross-task',
         'fig4-summary-results','figS1-open-retrieval','figS2-longitudinal-use',
         'figS3-dispersion','figS4-analysis-use']
'''+builder[b:]
builder=builder.replace('v0.14 --- 5 November 2026','v0.15 --- 5 November 2026')
builder=builder.replace("'main_figure_count':7", "'main_figure_count':4").replace("'supplementary_figure_count':1", "'supplementary_figure_count':4")
builder=builder.replace("'main_table_count':3", "'main_table_count':1").replace("'supplementary_table_count':4", "'supplementary_table_count':6")
(B/'build_reading_copy.py').write_text(builder,encoding='utf-8',newline='\n')
(B/'README.md').write_text('''# Conference-style reading edition v0.15

This is a locally compiled reading edition, not an official venue template or an uploaded Overleaf project. The body prioritizes four scientific figures; complete earlier displays and numeric tables remain in the supplement. Venue recommendations are separate from scientific results.

Upload `overleaf_v15.zip` into Overleaf, select `paper.tex` and LuaLaTeX, and compile twice. For this repository layout, `python build_reading_copy.py` rebuilds TeX from the adjacent Markdown draft and figure PDFs, then `lualatex -interaction=nonstopmode -halt-on-error paper.tex` compiles it. The standalone ZIP compiles the supplied TeX directly.

No participant-level data, third-party original papers, experimental rerun or new reference estimate is included in this editorial edition. Authorship, declarations and venue-specific requirements remain to be completed.
''',encoding='utf-8')
shutil.copyfile(B/'README.md',B/'OVERLEAF_README.md')
print(json.dumps({'preserved_figure_exports':len(reuse),'new_builder':str(B/'build_reading_copy.py')}))
