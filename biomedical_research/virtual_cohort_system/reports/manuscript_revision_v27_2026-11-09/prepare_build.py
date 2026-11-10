"""Prepare separate v27 typesetting scripts; preserve previous editions."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
old=P/'manuscript/methods_draft_v26_2026-11-09'
new=P/'manuscript/methods_draft_v27_2026-11-09'
new.mkdir(exist_ok=True)
for name in ['build_review_copy.py','compile_review.py','verify_review_copy.py']:
    s=(old/name).read_text(encoding='utf-8')
    s=s.replace('v0.26','v0.27').replace('DRAFT_v0_26','DRAFT_v0_27').replace('overleaf_v26','overleaf_v27')
    if name=='build_review_copy.py':
        s=s.replace('MAIN_TABLES = 3','MAIN_TABLES = 5').replace('SUPPLEMENT_TABLES = 8','SUPPLEMENT_TABLES = 10')
        s=s.replace("if display_id in ('1','2') and n==2:","if display_id in ('2','3') and n==2:")
        s=s.replace("if display_id=='1' else", "if display_id=='2' else")
        s=s.replace("'S8.', 'S13.'", "'S8.', 'S13.', 'S16.', 'S17.'")
    if name=='verify_review_copy.py':
        s=s.replace("{'1','2','3'}|{'S'+str(i) for i in range(1,9)}", "{str(i) for i in range(1,6)}|{'S'+str(i) for i in range(1,11)}")
        s=s.replace('work/manuscript_focus_v26_2026-11-09/REVISION_FACTS.json', 'work/manuscript_revision_v27_2026-11-09/REVISION_FACTS.json')
        s=s.replace("sha(HERE.parent/'DRAFT_v0_25.md')==facts['input_sha256']", "sha(HERE.parent/'DRAFT_v0_26.md')==facts['input_sha256']")
    (new/name).write_text(s,encoding='utf-8')
(new/'OVERLEAF_README.md').write_text('''# Methods development edition v0.27

Import this ZIP as a new Overleaf project. Set paper.tex as the main document, choose LuaLaTeX, and compile twice. All eleven figure PDFs are included. The single-column 11-point article has no imposed page limit. Author and affiliation details remain unconfirmed.

This editorial revision defines the scientific properties evaluated, specifies actual review roles and budgets, and adds complete reference and reproducibility conditions. All pre-existing numerical results and figure assets remain unchanged. Tables distinguish execution and point-estimate agreement from unvalidated inferential uses. Source, model and transfer uncertainty are not represented by additional synthetic rows or seed ranges.

No new cohort was generated and no clinical reference was refitted. The public research archive retains its original versioned protocols; the paper does not turn them into one uniform current controller or claim that unknown historical model identities have been recovered.
''',encoding='utf-8')
print(str(new))
