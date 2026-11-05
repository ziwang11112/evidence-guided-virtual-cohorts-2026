"""Seal original reporting artifacts after actual numerical/content/visual review."""
from pathlib import Path
import re
import runner

R=Path(__file__).resolve().parent
P=R.parents[1]
runner.closure_gate()
audit=runner.READ(R/'review/INDEPENDENT_NUMERICAL_REVIEW.json')
assert audit['independent_review_complete'] and audit['findings']['arithmetic_discrepancies']==0
paths=[R/'RESULTS.md',R/'RESULTS_ZH.md',P/'manuscript/CROSS_TASK_RESULTS_INSERT_2026-11-05.md']
zh=paths[1].read_text(encoding='utf-8');ms=paths[2].read_text(encoding='utf-8')
assert '百分点' in zh and '性别、BMI和血糖' in zh and '情景数据' in zh
assert 'versus42.8466' not in ms and 'versus 42.8466' in ms
broken=[];count=0
for path in paths:
    for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if '://' in link or link.startswith('#'):continue
        count+=1
        if not (path.parent/link.split('#')[0]).resolve().exists():broken.append((str(path),link))
assert not broken,broken
runner.WRITE(R/'review/REPORT_REVIEW_RESOLUTION.json',{
 'status':'all_three_requested_text_corrections_applied',
 'review_sha256':runner.SHA(R/'review/REPORT_REVIEW.json'),
 'scope':'Chinese HbA1c units/adjustment clarification, current-output use scoped to assumption-dependent scenarios, one English spacing correction. No numbers, models, evaluation or tolerances changed.',
 'corrected_report_sha256':{str(p.relative_to(P)):runner.SHA(p) for p in paths},
 'local_links_checked':count,'broken_links':broken})
artifacts=paths+[R/'STATE.json',R/'BATCH_CLOSURE.json',R/'evaluation/RESULTS.json',
 R/'evaluation/ALL_ENDPOINTS.csv',R/'evaluation/PRIMARY_SUMMARY.csv',R/'evaluation/EVIDENCE_USAGE_SUMMARY.json',
 R/'review/INDEPENDENT_NUMERICAL_REVIEW.md',R/'review/INDEPENDENT_NUMERICAL_REVIEW.json',
 R/'review/SCIENTIFIC_RESULT_INTERPRETATION.md',R/'review/SCIENTIFIC_RESULT_INTERPRETATION.json',
 R/'review/REPORT_REVIEW.md',R/'review/REPORT_REVIEW.json',R/'review/REPORT_REVIEW_RESOLUTION.json',
 R/'figures/LAYOUT_REVIEW.md',R/'report_results.py']
artifacts+=list((R/'figures').glob('*.png'))+list((R/'figures').glob('*.pdf'))+list((R/'figures').glob('*.svg'))
runner.WRITE(R/'COMPLETION.json',{'status':'complete_independently_reviewed_closed',
 'created_utc':runner.now(),'decision':'Close batch; simplify demonstrated use and integrate all-construction manuscript results; no further tuning of these exposed references.',
 'successful_final_tables':18,'final_rows_per_table':3000,'physical_attempts':24,
 'independently_recomputed_outputs':513,'comparison_scope':'existing exposed sample aggregates',
 'artifacts':{str(p.relative_to(P)):runner.SHA(p) for p in artifacts},
 'github_sync_this_unit':'not_performed; local results and insert only',
 'background_or_new_experiment_started':False})
print({'status':'complete','local_links_checked':count,'final_artifacts':len(artifacts)})
