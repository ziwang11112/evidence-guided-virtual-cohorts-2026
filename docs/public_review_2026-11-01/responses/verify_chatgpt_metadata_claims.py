"""Pure metadata-only counterexamples; no data or candidate execution.

Usage: python verify_chatgpt_metadata_claims.py --repository PATH_TO_CHECKOUT
The pinned modules are checked before import. The report is printed to stdout;
the script does not write report files or Python bytecode into the checkout.
"""
from pathlib import Path
import sys,subprocess,json,copy,argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repository',type=Path,required=True)
E=parser.parse_args().repository.resolve()
H='7f4b38c0c0dfa8da4bbd8df3d5ee754399600562'
PREFIX='biomedical_research/virtual_cohort_system/'
sys.dont_write_bytecode=True
sys.path.insert(0,str(E/PREFIX))
for name in ['source_replay.py','source_checks.py','contracts.py','lifecycle.py','execution.py']:
    rel=PREFIX+'cohort_harness/'+name
    pinned=subprocess.check_output(['git','-C',str(E),'show',H+':'+rel])
    local=(E/rel).read_bytes()
    assert pinned.replace(b'\r\n',b'\n')==local.replace(b'\r\n',b'\n'),name
from cohort_harness.source_replay import _check_metadata
item={'id':'e','kind':'ols_coefficient','variables':['y','x'],'adjustment':['z'],'unit':'u','estimate':0.5,'selection':'group equals 1; Y regressed on X adjusting for Z'}
operator={'kind':'ols_coefficient','unit':'u','selection':[{'column':'group','op':'eq','value':1}],'missing_policy':'error','outcome':'y','predictors':['x','z'],'term':'x','include_intercept':True}
base={'id':'c','evidence_id':'e','status':'computed','operator':operator,'assumption_ids':[],'reason':'Metadata-only invented validation probe.'}
results=[]
for label,changes in [('baseline',{}),('wrong_coefficient_term',{'term':'z'}),('reversed_outcome_and_exposure',{'outcome':'x','predictors':['y','z'],'term':'y'}),('omitted_source_filter',{'selection':[]})]:
    check=copy.deepcopy(base);check['operator'].update(changes)
    _,aligned=_check_metadata(check,{'e':item},set(),[])
    results.append({'case':label,'accepted':True,'aligned':aligned,'declared_status':check['status']})
qitem={'id':'e','kind':'quantile','variables':['x'],'adjustment':[],'unit':'u','estimate':1,'selection':'all','q':0.25,'method':'linear'}
qcheck=copy.deepcopy(base);qcheck['operator']={'kind':'quantile','unit':'u','selection':[],'missing_policy':'error','column':'x','q':0.75,'method':'linear'}
try:
    _check_metadata(qcheck,{'e':qitem},set(),[])
    results.append({'case':'wrong_quantile_probability_control','rejected':False})
except ValueError as exc:
    results.append({'case':'wrong_quantile_probability_control','rejected':True,'message':str(exc)})
assert all(x.get('aligned') is True for x in results[:4]) and results[-1]['rejected']
out={'pinned_commit':H,'scope':'Pure metadata validation only; no participant/generated rows, generators, source reconstructions or target calculations.','results':results}
print(json.dumps(out,indent=2))
