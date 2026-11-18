"""Prepare a new editorial edition; closed experiments are read-only inputs."""
from pathlib import Path
import hashlib,json,shutil
W=Path(__file__).resolve().parent
P=W.parents[1]
M=P/'manuscript'
B=M/'methods_draft_v33_2026-11-17'
F=M/'paper_figures_v33_2026-11-17'
B.mkdir(exist_ok=True); F.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=[M/'DRAFT_v0_32.md',M/'POSITIONING_ANALYSIS_DRIVEN_2026-11-16.md']
for folder in [M/'methods_draft_v32_2026-11-16',M/'paper_figures_v32_2026-11-16',
 P/'work/pns_evidence_content_control_2026-11-16',P/'work/iron_evidence_content_control_2026-11-16',
 P/'work/evidence_composition_pilot_2026-11-16',P/'work/pns_joint_evidence_2026-11-16',
 P/'work/lifestyle_application_2026-11-11']:
 protected.extend(p for p in folder.rglob('*') if p.is_file())
binding=W/'INPUT_BINDINGS.json'
if binding.exists():
 old=json.loads(binding.read_text())
 assert all(sha(P/r)==h for r,h in old['files'].items())
else:
 binding.write_text(json.dumps({'files':{p.relative_to(P).as_posix():sha(p) for p in protected}},indent=2)+'\n')
for f in ['build_review_copy.py','compile_review.py']:
 text=(M/'methods_draft_v32_2026-11-16'/f).read_text(encoding='utf-8')
 text=text.replace('v0.32','v0.33').replace('v0_32','v0_33').replace('v32','v33').replace('16 NOVEMBER 2026','17 NOVEMBER 2026')
 if not (B/f).exists():(B/f).write_text(text,encoding='utf-8')
text=(P/'work/manuscript_integration_v32_2026-11-16/figures.py').read_text(encoding='utf-8')
text=text[:text.index('def main():')]
text=text.replace("OUT=P/'manuscript/paper_figures_v32_2026-11-16'","OUT=P/'manuscript/paper_figures_v33_2026-11-17'")
text=text.replace("name='fig4-joint-evidence'","name='figS1-search-followup'")
(W/'support_plots.py').write_text(text,encoding='utf-8')
(B/'OVERLEAF_README.md').write_text('''# v0.33 editorial edition

Main document: `paper.tex`. Select **LuaLaTeX** in Overleaf; compile twice.
The ZIP is self-contained: manuscript plus vector PDF figures.
This is a single-column scientific reading draft, without a venue page limit.
Source Markdown and plotting provenance are maintained in the project repository.
No patient-level real or synthetic records are in this archive.
Author information and submission declarations still require completion.
''',encoding='utf-8')
(W/'STATE.json').write_text(json.dumps({'status':'authoring','version':'v0.33','new_experiments':False,
 'api_calls':0,'scope':'Integrate closed PNS and iron content controls; revise narrative and figures; build and inspect.'},indent=2)+'\n')
print(json.dumps({'protected_files':len(protected),'build':str(B),'figures':str(F)}))
