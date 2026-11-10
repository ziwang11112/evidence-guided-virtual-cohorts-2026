"""Prepare a separate v26 article/Overleaf build without modifying prior editions."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
old=P/'manuscript/methods_draft_v25_2026-11-08'
new=P/'manuscript/methods_draft_v26_2026-11-09'
new.mkdir(exist_ok=True)
builder=(old/'build_review_copy.py').read_text(encoding='utf-8')
builder=builder.replace('v0.25','v0.26').replace('DRAFT_v0_25','DRAFT_v0_26').replace('overleaf_v25','overleaf_v26')
a=builder.index('MAIN_STEMS ='); b=builder.index('FILES =',a)
builder=builder[:a]+'''MAIN_STEMS = ['fig1-agent-loop.drawio', 'fig1-agent-method.drawio',
              'fig3-analysis-utility', 'fig2-evidence-results', 'fig3-iron-utility', 'fig3-cross-task']
SUPPLEMENT_STEMS = ['fig4-summary-results', 'figS3-dispersion', 'figS4-analysis-use',
                    'figS5-prospective-wave', 'fig2-hrs-comparison']
'''+builder[b:]
builder=builder.replace('SUPPLEMENT_TABLES = 7','SUPPLEMENT_TABLES = 8')
builder=builder.replace("body += [r'\\begingroup',r'\\small',r'\\renewcommand{\\arraystretch}{1.22}',", "body += [r'\\FloatBarrier',r'\\begingroup',r'\\small',r'\\renewcommand{\\arraystretch}{1.22}',")
builder=builder.replace("if heading.startswith('S13.'):", "if heading.startswith(('S6.', 'S7.', 'S8.', 'S13.')):")
builder=builder.replace("3:'paper_figures_v19_2026-11-06'", "3:'paper_figures_v26_2026-11-09', 5:'paper_figures_v19_2026-11-06'")
(new/'build_review_copy.py').write_text(builder,encoding='utf-8')
compiler=(old/'compile_review.py').read_text(encoding='utf-8').replace('overleaf_v25','overleaf_v26')
(new/'compile_review.py').write_text(compiler,encoding='utf-8')
(new/'OVERLEAF_README.md').write_text('''# Methods development edition v0.26

Import this ZIP as a new Overleaf project. Set paper.tex as the main document, choose LuaLaTeX, and compile twice. All eleven figure PDFs are included. The 11-point single-column article has no imposed page limit. Author and affiliation details remain unconfirmed.

This edition prioritizes the scientific utility of complete Agent-generated cohorts, then the relationship-evidence comparison. It retains the iron/lipid mismatches, earlier prospective failures, complete statistical comparisons, reference exposure, and supplied-information boundaries. Historical predictive utility and later controller capabilities are separated in Supplements S14-S15.

The revision uses existing aggregate results. It does not generate a new clinical cohort or refit a target. Sources and experiment-level provenance remain in the full Markdown manuscript and public research repository. Seed ranges do not measure source or transport uncertainty.
''',encoding='utf-8')
print(str(new))
