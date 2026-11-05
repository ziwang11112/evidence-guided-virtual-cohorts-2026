from pathlib import Path
import sys,json,math,ast
import numpy as np
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R))
import runner
b=Path(runner.protocol()['authors']['L02']['bundle']);c=b/'candidates/initial'
p=runner.READ(c/'model_spec.json')['parameters']
assert p['row_count']==3000 and p['female_probability']==.5
assert np.min(np.linalg.eigvalsh(np.array(p['latent_correlation'])))>0
for i,j,rho in [(1,2,.212),(1,3,-.100),(2,3,.106)]:
    assert abs(p['latent_correlation'][i][j]-2*math.sin(math.pi*rho/6))<1e-14
for var,sex,mean,sd in [('bmi','M',20.87,3.15),('bmi','F',22.28,3.85),('total_cholesterol','M',3.23,.92),('hdl_cholesterol','M',1.14,.38)]:
    assert abs(p['margins'][var][sex]['log_sd']-math.sqrt(math.log1p((sd/mean)**2)))<1e-14
ast.parse((c/'generator.py').read_text())
for x in runner.READ(c/'checks.json')['artifacts']:
    assert runner.SHA(c/x['path'])==x['sha256']
manifest=runner.READ(b/'INITIAL_DELIVERY_READY.json')
for x in manifest['files']: assert runner.SHA(b/x['path'])==x['sha256']
runner.WRITE(R/'review/L02_CANDIDATE_REVIEW.json',{
 'approved':True,'scientific_code_spec_consistency':True,'finite_moments_supported':True,
 'source_semantics_reviewed':True,'target_results_used':False,'reviewer_id':'/root',
 'candidate':'candidates/initial',
 'candidate_files':{n:runner.SHA(c/n) for n in runner.lifecycle._files(c)},
 'narrative_sha256':runner.SHA(R/'review/L02_CANDIDATE_REVIEW.md'),
 'review_scope':'Static code/spec/source trace and deterministic aggregate algebra; no generator execution/import or rows.'})
print('L02 static candidate review recorded.')
