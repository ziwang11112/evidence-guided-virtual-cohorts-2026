"""Prepare a separate v28 manuscript build without modifying frozen editions."""
from pathlib import Path

P = Path(__file__).resolve().parents[2]
old = P / 'manuscript/methods_draft_v27_2026-11-09'
new = P / 'manuscript/methods_draft_v28_2026-11-10'
new.mkdir(exist_ok=True)
for name in ['build_review_copy.py', 'compile_review.py', 'verify_review_copy.py']:
    s = (old / name).read_text(encoding='utf-8')
    s = s.replace('v0.27', 'v0.28').replace('DRAFT_v0_27', 'DRAFT_v0_28').replace('overleaf_v27', 'overleaf_v28')
    if name == 'build_review_copy.py':
        s = s.replace("'fig3-iron-utility', 'fig3-cross-task']", "'fig3-iron-utility', 'fig3-cross-task', 'fig7-attribution', 'fig8-pns-utility']")
        s = s.replace('SUPPLEMENT_TABLES = 10', 'SUPPLEMENT_TABLES = 11')
        s = s.replace("'S16.', 'S17.'", "'S16.', 'S17.', 'S18.'")
        s = s.replace('All numerical displays are pre-existing figure PDFs.', 'Numerical displays combine preserved figures with new plots of frozen aggregate results.')
    if name == 'verify_review_copy.py':
        s = s.replace('range(1,7)', 'range(1,9)').replace('range(1,11)', 'range(1,12)')
        s = s.replace('work/manuscript_revision_v27_2026-11-09/REVISION_FACTS.json', 'work/manuscript_revision_v28_2026-11-10/REVISION_FACTS.json')
        s = s.replace("sha(HERE.parent/'DRAFT_v0_26.md')==facts['input_sha256']", "sha(HERE.parent/'DRAFT_v0_27.md')==facts['input_sha256']")
    (new / name).write_text(s, encoding='utf-8')
(new / 'OVERLEAF_README.md').write_text('''# Methods development draft v0.28

Import this ZIP into Overleaf, set paper.tex as the main document, select LuaLaTeX and compile twice. This is a local editable package, not an already-created online project. The single-column article is a reading/development edition with no imposed page limit, not a verified conference submission format.

This revision integrates the completed blood-pressure task and a retrospective parameter-to-analysis attribution audit. It retains all prior main and supplementary results and adds two vector result figures. Thirteen figures are included. The source-statistic, declared-parameter, model-implied, generated-estimate and measured-reference objects remain distinct. No calibrated reliability label or cross-provider convergence has been demonstrated.

All scientific generators and revealed target comparisons remain frozen. No new clinical experiment, generation campaign or paid-model call was performed for this revision. Cross-provider pilot design is a separate research protocol, not a reported result. Author, affiliation and submission declarations remain pending.
''', encoding='utf-8')
print(new)
