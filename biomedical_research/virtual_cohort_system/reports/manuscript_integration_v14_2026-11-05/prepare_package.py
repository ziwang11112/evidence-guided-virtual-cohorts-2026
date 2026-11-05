"""Prepare the v0.14 reading package from original, already-reviewed figures.

No generator, clinical data reader, evaluator, or old artifact is executed or edited.
"""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parent
P = R.parents[1]
M = P / 'manuscript'
B = M / 'conference_draft_v14_2026-11-05'
F = M / 'paper_figures_v14_2026-11-05'
OLD = M / 'paper_figures_v13_2026-11-04'
RUN = P / 'work/evidence_use_cross_task_2026-11-05'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
B.mkdir(exist_ok=True)
F.mkdir(exist_ok=True)
records = []
stems = ['fig1-agent-framework.drawio', 'fig2-evidence-results', 'fig3-summary-results',
         'fig4-longitudinal-use', 'fig5-open-retrieval', 'figS1-analysis-use']
for stem in stems:
    for ext in ('.svg', '.pdf', '.png'):
        src, dst = OLD/(stem+ext), F/(stem+ext)
        shutil.copyfile(src, dst)
        records.append(dict(source=str(src.relative_to(P)), destination=str(dst.relative_to(P)),
                            sha256=sha(dst), bytes_preserved=src.read_bytes()==dst.read_bytes()))
for source, target in [('primary_analyses','fig6-cross-task'), ('dispersion','fig7-dispersion')]:
    for ext in ('.svg', '.pdf', '.png'):
        src, dst = RUN/'figures'/(source+ext), F/(target+ext)
        shutil.copyfile(src, dst)
        records.append(dict(source=str(src.relative_to(P)), destination=str(dst.relative_to(P)),
                            sha256=sha(dst), bytes_preserved=src.read_bytes()==dst.read_bytes()))
(R/'FIGURE_REUSE_MANIFEST.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
builder = (M/'conference_draft_v13_1_2026-11-04/build_reading_copy.py').read_text(encoding='utf-8')
builder = builder.replace('DRAFT_v0_13_1.md','DRAFT_v0_14.md').replace('paper_figures_v13_2026-11-04','paper_figures_v14_2026-11-05')
builder = builder.replace("'fig4-longitudinal-use','fig5-open-retrieval','figS1-analysis-use'", "'fig4-longitudinal-use','fig5-open-retrieval','fig6-cross-task','fig7-dispersion','figS1-analysis-use'")
builder = builder.replace('figure_count==6 and table_count==5','figure_count==8 and table_count==7')
builder = builder.replace('v0.13.1 --- 4 November 2026','v0.14 --- 5 November 2026')
builder = builder.replace("'main_figure_count':5", "'main_figure_count':7").replace("'supplementary_table_count':2", "'supplementary_table_count':4")
builder = builder.replace("r'\\begingroup\\small'", "r'\\begingroup\\fontsize{8.5}{10}\\selectfont'").replace("r'\\setlength{\\itemsep}{3pt}'", "r'\\setlength{\\itemsep}{1pt}'")
(B/'build_reading_copy.py').write_text(builder, encoding='utf-8', newline='\n')
(B/'README.md').write_text('''# Reading manuscript v0.14

This is a locally compiled, two-column reading copy of **Evidence-Guided Agents for Analyzable Virtual Biomedical Cohorts**, not an official submission template.

Upload `overleaf_v14.zip` to Overleaf, select `paper.tex` as the main file and LuaLaTeX as the compiler. Compile twice. Eight vector figure PDFs are included. The compiled PDF is included for comparison; no online project has been created by this package.

To rebuild from this repository layout, run `python build_reading_copy.py` in this folder, then `lualatex -interaction=nonstopmode -halt-on-error paper.tex` twice. The Python builder consumes the adjacent Markdown draft and reviewed figure package; it performs no data analysis. In the standalone Overleaf ZIP, edit and compile `paper.tex` directly.

The seven main figures and one supplementary figure preserve all constructions in their respective studies. The new glycemic/lipid batch is separate from the historical information contrast, summary reconstruction and longitudinal model example. The final manuscript still requires authorship, declarations and venue-specific editing.
''', encoding='utf-8')
shutil.copyfile(B/'README.md', B/'OVERLEAF_README.md')
(F/'README.md').write_text('''# Figures for manuscript v0.14

Figures 1–5 and S1 are byte-preserved from the preceding edition. Figures 6–7 are byte-preserved from the independently reviewed cross-task study; all six constructors and final seeds are shown. No clinical data or generated rows were read to prepare this package.

- [Figure 6: analysis results](fig6-cross-task.svg): association effects and residual dependence, in native units, compared with existing sample references.
- [Figure 7: dispersion](fig7-dispersion.svg): marginal and residual spread; agreement on one coefficient does not establish a complete distributional match.
- [New study plotting source](../../work/evidence_use_cross_task_2026-11-05/report_results.py) and [aggregate results](../../work/evidence_use_cross_task_2026-11-05/evaluation/RESULTS.json).
- [New study interpretation](../../work/evidence_use_cross_task_2026-11-05/RESULTS_ZH.md).
- [Preserved earlier figure package](../paper_figures_v13_2026-11-04/README.md).

Seed ranges represent Monte Carlo variation under fixed models. Reference bands retain their original uncertainty meaning; they are not equivalence thresholds. The TC reference slope interval crosses zero. These studies reuse exposed references and do not establish fresh clinical confirmation.
''', encoding='utf-8')
print(json.dumps({'figure_exports_copied':len(records),'all_bytes_preserved':all(r['bytes_preserved'] for r in records),'builder':str(B/'build_reading_copy.py')}))
