from pathlib import Path
import json, hashlib

R = Path(__file__).resolve().parent.parent
W = R.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf-8') as f: json.dump(v,f,indent=2)

b=W/'evcUseH03'
write(R/'review/H03_SOURCE_PROPOSAL.json',{
 'decision':'PASS_TO_IMPLEMENT_WITH_PROVENANCE_ANNOTATIONS','reviewer_id':'/root',
 'author_id':'/root/cross_h03_author','new_target_reads':0,'generated_rows':0,
 'parameter_change_requested':False,
 'bindings':{n:sha(b/n) for n in ['SOURCE_REVIEW_REQUEST.md','PROPOSED_CONSTRUCTION.md','PROPOSAL_ALGEBRA.json','SEARCH_LEDGER.json','task.json','request.json','registry.json']},
 'review_sha256':sha(R/'review/H03_SOURCE_PROPOSAL.md'),
 'independent_algebra_sha256':sha(R/'review/H03_ANALYTIC_RECHECK.json')})

b=W/'evcUseL01'
decision=json.loads((b/'FINAL_DECISION.json').read_text())
feedback=R/'sessions/L01/feedback_l01_initial_9100.json'
assert decision['action']=='retain'
assert decision['feedback_hashes']=={'l01_initial_9100':sha(feedback)}
fb=json.loads(feedback.read_text())
assert fb['generated_status']=='complete' and fb['semantic_status']=='complete'
write(R/'review/L01_FINAL_REVIEW.json',{
 'approved':True,'scientific_code_spec_consistency':True,'finite_moments_supported':True,
 'source_semantics_reviewed':True,'target_results_used':False,'reviewer_id':'/root',
 'candidate_freeze_sha256':sha(b/'candidates/initial/freeze.json'),
 'decision_sha256':sha(b/'FINAL_DECISION.json'),
 'prior_candidate_review_sha256':sha(R/'review/L01_CANDIDATE_REVIEW.json'),
 'finding':'Actual author retained reviewed frozen candidate after successful trial and generated-only diagnostics; all source comparisons unavailable. No claim of source replay, target validity, or revision gain. No numerical edits.'})
print('Recorded H03 proposal review and L01 final decision review; no sampling or reference reads.')
