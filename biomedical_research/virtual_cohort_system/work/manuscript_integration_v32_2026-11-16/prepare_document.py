"""Insert aggregate numerical tables and prepare a new standalone LaTeX edition."""
from pathlib import Path
import json,re,shutil
import pandas as pd

W=Path(__file__).resolve().parent
P=W.parents[1]
M=P/'manuscript'
OUT=M/'methods_draft_v32_2026-11-16'
SOURCE=M/'DRAFT_v0_32.md'
text=SOURCE.read_text(encoding='utf8')

def replace_block(marker,caption,table):
    global text
    if marker in text:
        text=text.replace(marker,table)
    else:
        start=text.index(caption)
        a=text.index('\n|',start)+1
        b=text.index('\n\n',a)
        text=text[:a]+table+text[b:]

l=pd.read_csv(P/'work/lifestyle_application_2026-11-11/ANALYSIS_CONTRASTS.csv')
l=l[l.stratum=='pooled']
rows=['| Trait and contrast | Real estimate [95% interval] | Agent 1 | Agent 2 |',
      '|---|---|---|---|']
traits={'bmi':'BMI','total_cholesterol':'Total cholesterol','hdl_cholesterol':'HDL'}
contrasts={'urban_minus_pastoralist':'urban − pastoralist','urban_minus_rural':'urban − rural','rural_minus_pastoralist':'rural − pastoralist'}
for trait,label in traits.items():
    for contrast,cname in contrasts.items():
        z=l[(l.trait==trait)&(l.contrast==contrast)]
        real=z[z.dataset_id=='real'].iloc[0]
        vals=[z[z.dataset_id.str.startswith('LIFESTYLE_'+a+'_')].raw_estimate.mean() for a in ['A1','A2']]
        rows.append(f'| {label}: {cname} | {real.raw_estimate:.3f} [{real.raw_lower:.3f}, {real.raw_upper:.3f}] | {vals[0]:.3f} | {vals[1]:.3f} |')
replace_block('@@LIFESTYLE_TABLE@@','**Table S1.','\n'.join(rows))

c=pd.read_csv(P/'work/evidence_composition_pilot_2026-11-16/analysis/cell_summary.csv')
rows=['| Task | Evidence | Primary range | Primary MAE | Source checks |', '|---|---|---|---|---|']
cnames={'none':'Basic','anchor_only':'Basic + A','bridge_only':'Basic + B','combined':'Basic + A + B'}
for r in c.itertuples():
    error='Not identified' if pd.isna(r.primary_MAE_if_identified) else f'{r.primary_MAE_if_identified:.5f}'
    rows.append(f'| {r.family.title()} | {cnames[r.condition]} | {r.primary_mean_min:.4f} to {r.primary_mean_max:.4f} | {error} | {r.source_checks_passed}/{r.source_checks_total} |')
replace_block('@@COMPOSITION_TABLE@@','**Table S2.','\n'.join(rows))

a=json.loads((P/'work/pns_joint_evidence_2026-11-16/analysis/arm_results.json').read_text())
ref=json.loads((P/'work/pns_joint_evidence_2026-11-16/analysis/REFERENCE_USED.json').read_text())
index={(r['arm'],r['estimand']):r for r in a}
rows=['| Analysis | Reference | Original mean | Added mean | Original / added MAE |','|---|---|---|---|---|']
metrics={'residual_correlation':'Residual correlation','bmi_sbp':'BMI–SBP (mmHg/5 kg/m²)','bmi_dbp':'BMI–DBP (mmHg/5 kg/m²)','sbp.sd_population':'SBP SD (mmHg)','dbp.sd_population':'DBP SD (mmHg)'}
for metric,label in metrics.items():
    rv=ref['PNS'][metric]['value']
    original=index['ORIGINAL',metric];added=index['AUGMENTED',metric]
    rows.append(f"| {label} | {rv:.4f} | {original['author_mean']:.4f} | {added['author_mean']:.4f} | {original['author_mean_absolute_reference_difference']:.5f} / {added['author_mean_absolute_reference_difference']:.5f} |")
replace_block('@@PNS_TABLE@@','**Table S3.','\n'.join(rows))

# Use already verified bibliography entries rather than shorthand titles.
old=(M/'DRAFT_v0_31.md').read_text(encoding='utf8')
refmap={1:4,2:5,3:1,4:2,6:6,7:3,8:29,9:32}
for new,prior in refmap.items():
    oldline=re.search(rf'^{prior}\. .+$',old,re.M).group(0)
    newline=re.sub(r'^\d+\.',str(new)+'.',oldline)
    text=re.sub(rf'^{new}\. .+$',lambda m:newline,text,flags=re.M)
# No generated placeholders or machine identifiers are allowed in the main narrative.
assert '@@' not in text
SOURCE.write_text(text,encoding='utf8')

for fname in ['build_review_copy.py','compile_review.py']:
    s=(M/'methods_draft_v31_2026-11-11'/fname).read_text(encoding='utf8')
    s=s.replace('v0.31','v0.32').replace('v0_31','v0_32').replace('overleaf_v31','overleaf_v32')
    s=s.replace('NOVEMBER 2026','16 NOVEMBER 2026')
    # Retained figure layout and typography; remove obsolete forced supplement breaks.
    s=s.replace("if heading.startswith(('S6.', 'S7.', 'S8.', 'S13.', 'S16.', 'S17.', 'S18.', 'S20.', 'S21.', 'S22.', 'S23.', 'S24.', 'S25.')):","if False:")
    s=s.replace("        if False:\n            body.append(r'\\clearpage')", "        if False:\n            body.append(r'\\clearpage')\n        if supplementary and heading.startswith('S3.'):\n            body.append(r'\\Needspace{23\\baselineskip}')")
    if fname=='build_review_copy.py':
        s=s.replace(r'\documentclass[11pt,letterpaper]{article}',r'\documentclass[11pt,letterpaper]{article}'+'\n'+r'\pdfvariable minorversion=7')
        s=s.replace(r'\emergencystretch=1em',r'\emergencystretch=3em')
        s=s.replace("    def code(m): return hold(r'\\texttt{'+tex_escape(m.group(1))+'}')", "    def code(m):\n        escaped=tex_escape(m.group(1))\n        for separator in [r'\\_', '/', '-']:\n            escaped=escaped.replace(separator,separator+r'\\allowbreak{}')\n        return hold(r'\\texttt{'+escaped+'}')")
        s=s.replace("r'\\renewcommand{\\thefigure}{S\\arabic{figure}}'", "r'\\renewcommand{\\thefigure}{S\\arabic{figure}}',r'\\renewcommand{\\theHfigure}{S\\arabic{figure}}'")
        s=s.replace("r'\\renewcommand{\\thetable}{S\\arabic{table}}'", "r'\\renewcommand{\\thetable}{S\\arabic{table}}',r'\\renewcommand{\\theHtable}{S\\arabic{table}}'")
    (OUT/fname).write_text(s,encoding='utf8')
(OUT/'OVERLEAF_README.md').write_text('''# Editable manuscript v0.32 — 16 November 2026

Upload the complete ZIP to a new Overleaf project, choose **LuaLaTeX**, and set `paper.tex` as the main document. Compile twice. The PDF figures are embedded vector assets; the project does not read local patient data or use a model API. Libertinus and the listed standard TeX packages are required.

This is a single-column methods development manuscript, not a journal- or conference-compliant final submission. No submission page limit has been imposed. Author and institutional details, declarations, biomedical interpretation and final venue formatting remain to be confirmed.

The paper separates source-rich lifestyle reconstruction, two artificial exact-moment tasks, and one developmental external-evidence blood-pressure comparison. Repeated draws are nested within constructions. All nine lifestyle contrasts and all three primary blood-pressure analyses plus both dispersion diagnostics are retained. Neither a blanket workflow advantage nor independent population generalization is claimed.

Figure 1 is the unchanged overview from the preceding edition. Figures 2–4 are freshly plotted from closed aggregates with a navy, blue, orange and purple palette. Real-sample intervals, model-construction variation and Monte Carlo ranges have distinct labels.

The unchanged v0.31 expanded edition and original experimental directories remain the historical record. This ZIP is the new focused manuscript, not a replacement for those experimental records. It contains no patient-level data, full third-party papers, keys or raw model conversations. Its release does not change dataset redistribution terms.
''',encoding='utf8')
print(json.dumps({'source':str(SOURCE),'words':len(text.split()),'main_words':len(text.split('## Supplementary results')[0].split()),'tables':6,'figures':4}))
