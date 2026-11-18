"""Invented reporting fixtures; no biomedical files or generation."""
import copy
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('repair_report',Path(__file__).with_name('evaluate.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fixture():
    protocol={'required_analyses':[{'id':'a','analysis_unit':'u'}],'required_diagnostics':[{'id':'d','unit':'v'}]}
    payload={'analyses':[{'id':'a','unit':'u','value':2.0,'status':'computed'}],
             'diagnostics':[{'id':'d','unit':'v','value':4.0,'status':'computed'}]}
    return protocol,payload

def test_missing_or_duplicate_endpoints_rejected():
    p,v=fixture();v['analyses']=[]
    with pytest.raises(ValueError):m.endpoints(v,p)
    p,v=fixture();v['analyses']*=2
    with pytest.raises(ValueError):m.endpoints(v,p)

def test_failed_execution_keeps_all_endpoints():
    p,_=fixture();x=m.endpoints(None,p)
    assert len(x['analyses'])==len(x['diagnostics'])==1
    assert all(r['value'] is None and r['status']=='unavailable' for rows in x.values() for r in rows)

def test_no_omission_of_failed_stage_or_changed_scientific_result():
    p,v=fixture();a={'candidate':'baseline','status':'success','run_id':'b1','seed':1,**m.endpoints(v,p)}
    failed={'candidate':'baseline','status':'error','run_id':'b2','seed':2,**m.endpoints(None,p)}
    revised=copy.deepcopy(a);revised.update(candidate='revised',run_id='r1');revised['analyses'][0]['value']=40
    stages=m.summarize([a,failed,revised],['baseline','revised'],'revised')
    assert len(stages)==2 and stages[0]['analyses'][0]['attempted']==2
    assert stages[0]['analyses'][0]['available']==1 and stages[1]['analyses'][0]['mean']==40

def test_duplicate_analysis_actions_reject():
    e={'action':{'kind':'analysis','run_id':'r','adapter':'a'},'result':{'status':'success','result':{'result':{}}}}
    with pytest.raises(ValueError):m.one_analysis({'actions':{'1':e,'2':e}},'r','a')

def test_bad_unit_rejects_even_matching_id():
    p,v=fixture();v['analyses'][0]['unit']='wrong'
    with pytest.raises(ValueError):m.endpoints(v,p)

@pytest.mark.parametrize('stages',[[],['other'],['other','baseline'],['baseline','baseline'],['baseline','r1','r2']])
def test_skipped_reordered_or_extra_baseline_rejects(stages):
    with pytest.raises(ValueError):m.check_stages(stages,'baseline',2)

def test_baseline_first_is_admitted():
    m.check_stages(['baseline','revised'],'baseline',2)
