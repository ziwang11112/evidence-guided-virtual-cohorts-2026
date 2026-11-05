"""Non-frozen progress snapshot from actual run ledgers; no reference/result fitting."""
from pathlib import Path
import json
import runner

R=Path(__file__).resolve().parent
p=runner.ensure_control()
records=[]
for aid,a in p['authors'].items():
    b=Path(a['bundle']); folder=R/'sessions'/aid
    rec={'author_id':aid,'case_id':a['case_id'],
         'source_proposal_present':(b/'SOURCE_REVIEW_REQUEST.md').exists(),
         'source_review_present':(R/f'review/{aid}_SOURCE_PROPOSAL.json').exists(),
         'candidate_present':(b/'candidates/initial/generator.py').exists(),
         'candidate_review_present':(R/f'review/{aid}_CANDIDATE_REVIEW.json').exists(),
         'attempts':0,'successful_executions':0,'finals':0,'successful_finals':0,'closed':False}
    if folder.exists():
        s=runner.Session(aid); rec.update(s.status())
        good=[e for e in s.selected('result') if e['status']=='success']
        final_ids={e['run_id'] for e in s.selected('attempt') if e['purpose']=='final'}
        rec['successful_executions']=len(good)
        rec['successful_finals']=sum(e['run_id'] in final_ids for e in good)
    records.append(rec)
state={'status':'bounded_author_construction_and_delivery_in_progress',
       'updated_utc':runner.now(),'frozen':True,'authors':records,
       'scientific_constructions_submitted':sum(r['candidate_present'] for r in records),
       'generation_attempts':sum(r['attempts'] for r in records),
       'final_tables':sum(r['successful_finals'] for r in records),
       'new_patient_data_downloads':0,
       'target_comparison_started':(R/'evaluation/EVALUATION_STARTED.json').exists(),
       'next':'Complete all six candidate reviews, author trial decisions and three fixed final draws; only after terminal closure evaluate all scheduled endpoints and independently recompute.'}
review_path=R/'review/INDEPENDENT_NUMERICAL_REVIEW.json'
if all(r['closed'] for r in records) and review_path.exists():
    review=runner.READ(review_path)
    if review.get('independent_review_complete') is True and review['findings']['arithmetic_discrepancies']==0:
        state.update(status='complete_independently_recomputed_closed_to_further_tuning',
          independent_generated_outputs_recomputed=review['coverage']['independently_computed_generated_outputs'],
          matched_reference_comparisons=review['coverage']['available_reference_comparisons'],
          generated_only_diagnostics=review['coverage']['unavailable_unmatched_reference_comparisons'],
          final_decision='Close batch; simplify empirical claims to analysis-specific assumption-dependent utility; retain whole-cohort method objective and continue manuscript integration.',
          results='RESULTS.md',manuscript_insert='../../manuscript/CROSS_TASK_RESULTS_INSERT_2026-11-05.md',
          next='Integrate reviewed all-construction results and figures into the next draft. Do not regenerate, retune exposed cases or start a new experiment automatically from this completed state.')
with (R/'STATE.json').open('w',encoding='utf-8') as f: json.dump(state,f,indent=2)
print(json.dumps({k:state[k] for k in ('scientific_constructions_submitted','generation_attempts','final_tables','target_comparison_started')}))
