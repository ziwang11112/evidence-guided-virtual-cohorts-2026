"""Artificial-fixture checks only; no reference analysis or generated final draw."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import copy
import json
import tempfile
from unittest.mock import patch
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent/'stage1'
sys.path.insert(0,str(STAGE))
import runner
import source_checks

checks=[]
def record(name, passed): checks.append({'check':name,'pass':bool(passed)})
def raises(fn):
    try: fn()
    except (ValueError,FileExistsError): return True
    return False

with tempfile.TemporaryDirectory(dir=HERE) as tmp:
    with patch.object(runner,'ROOT',Path(tmp)), patch.object(runner,'verify_freeze',return_value={}), patch.object(runner.pd,'read_csv',side_effect=AssertionError('Reference read must never occur')) as reader:
        record('Incomplete inventory blocks before reference read',raises(lambda:runner.evaluate()) and not reader.called)

evidence=source_checks.read(STAGE/'packets/case_b/evidence.json')
task=dict(run_id='toy',lineage_id='toy',branch='ordinary')
decision=runner.decision_template(task,evidence)
decision['calibration_log']['examined_structures'] += [dict(id=f'rejected_{i}',source_seeds_evaluated=[810101,810102,810103],disposition='rejected',reason='Artificial-fixture alternative') for i in [1,2]]
record('Ordinary may use nine unique diagnostics across three structures',source_checks.validate_decision(decision,task,evidence)=={'target':20})
bad=copy.deepcopy(decision)
bad['calibration_log']['examined_structures'].append(dict(id='fourth',source_seeds_evaluated=[],disposition='rejected',reason='Artificial excess'))
record('Fourth candidate structure rejected',raises(lambda:source_checks.validate_decision(bad,task,evidence)))
bad=copy.deepcopy(decision)
bad['calibration_log']['examined_structures'][0]['source_seeds_evaluated']=[810101,810102,810103,999999]
record('Unscheduled calibration seed rejected',raises(lambda:source_checks.validate_decision(bad,task,evidence)))
record('Three scenarios share twenty total final outputs',source_checks.allocation(['a','b','c'])=={'a':7,'b':7,'c':6})

# Artificial constant-value fixture uses permitted means only to make a valid
# schema/table. It is never analyzed and is not a statistical cohort output.
evidence=source_checks.read(STAGE/'packets/case_a/evidence.json')
schema=source_checks.read(STAGE/'packets/case_a/schema.json')
n=schema['n_persons']
fixture=pd.DataFrame({'person_id':np.repeat(np.arange(1,n+1),5),'month':np.tile([0,3,6,9,12],n)})
for variable in schema['columns'][2:]: fixture[variable]=0.
for m in evidence['marginal_summaries']:
    mask=fixture.month.eq(m['month'])
    value=round(m['mean']) if m['variable']=='gng' else m['mean']
    fixture.loc[mask,m['variable']]=value
    positions=fixture.index[mask]
    fixture.loc[positions[m['n_observed']:],m['variable']]=np.nan
record('Artificial table satisfies declared support/counts',source_checks.validate_frame(fixture,schema,evidence,n))
post=fixture.copy()
post.loc[(post.person_id==1)&(post.month==3),'weight_kg']=181.
record('Ross postbaseline weight above180 is not excluded',source_checks.validate_frame(post,schema,evidence,n))
baseline=fixture.copy()
baseline.loc[(baseline.person_id==1)&(baseline.month==0),'weight_kg']=181.
record('Ross baseline eligibility above180 is rejected',raises(lambda:source_checks.validate_frame(baseline,schema,evidence,n)))

protocol=source_checks.read(STAGE/'protocol.json')
result=dict(protocol_version=protocol['version'],protocol_freeze_sha256=runner.sha(STAGE/'protocol_freeze.json'),scope='Artificial fixtures and pre-reference guard only; no reserved target read and no generated final data',checks=checks,all_checks_pass=all(x['pass'] for x in checks))
(HERE/f"prelaunch_guard_checks_{protocol['version']}.json").write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
if not result['all_checks_pass']: raise SystemExit(1)
