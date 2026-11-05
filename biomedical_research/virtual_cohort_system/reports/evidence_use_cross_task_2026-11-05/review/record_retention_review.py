"""Record a root-reviewed, unchanged author retention and exact artifact bindings.

The root must read the actual author decision before invoking this recorder.
It does not choose, modify, execute or judge a scientific model automatically.
"""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R))
import runner

p=argparse.ArgumentParser(); p.add_argument('author');p.add_argument('--decision-sha256',required=True)
a=p.parse_args();s=runner.Session(a.author);s.verify()
decision=s.bundle/'FINAL_DECISION.json'; d=runner.READ(decision)
assert runner.SHA(decision)==a.decision_sha256
assert d['candidate']=='candidates/initial' and d['action']=='retain'
assert d['feedback_hashes']=={f['run_id']:f['feedback']['sha256'] for f in s.selected('feedback')}
prior=R/f'review/{a.author}_CANDIDATE_REVIEW.json'
v=runner.READ(prior);s._review_flags(v)
runner.WRITE(R/f'review/{a.author}_FINAL_REVIEW.json',{
 'approved':True,'scientific_code_spec_consistency':True,'finite_moments_supported':True,
 'source_semantics_reviewed':True,'target_results_used':False,'reviewer_id':'/root',
 'candidate_freeze_sha256':runner.SHA(s.bundle/d['candidate']/'freeze.json'),
 'decision_sha256':runner.SHA(decision),'prior_candidate_review_sha256':runner.SHA(prior),
 'finding':'Root read actual author rationale and verified feedback/freeze bindings. Author retained unchanged independently reviewed law after a successful trial. No source fit, target validity or revision gain inferred from unavailable source comparisons; no new numeric edits or target reads.'})
print('Recorded independently checked retention:',a.author)
