"""Exercise v2's actual module loader on an invented executed table."""
from pathlib import Path
import sys
PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'tests'))
from test_analysis_use_v1 import prepared
from test_whole_cohort_feedback import execute_direct
from cohort_harness import adaptive_session_v2 as session
from cohort_harness.lifecycle import sha256

def test_actual_v2_loader_with_absolute_import_bridge(tmp_path):
    root,candidate=prepared(tmp_path);execute_direct(root,candidate)
    wrapper=Path(__file__).with_name('analysis_use_adapter.py')
    dependencies=[PROJECT/'cohort_harness/analysis_use_v1.py',PROJECT/'cohort_harness/analysis_evidence.py',root/'input/use_contract.json']
    config={'schema_version':2,'limits':{'actions':20,'candidates':2,'executions':2,'feedbacks':2,'analyses':2},
            'allowed_seeds':[7],'runtime':None,'execution_limits':{'timeout_seconds':45,'memory_mb':1536,'output_bytes':20000000,'log_bytes':50000},
            'web_evidence':{},'analysis_adapters':{'analysis_use':{'path':str(wrapper),'function':'analyze','sha256':sha256(wrapper),
            'dependencies':{str(p):sha256(p) for p in dependencies}}}}
    result=session._analysis(root,{'config':{'settings':config}},
           {'kind':'analysis','candidate':'candidates/initial','run_id':'run01','adapter':'analysis_use','analysis_id':'test'})
    assert result['result']['status']=='computed'
    assert result['result']['evidence_coverage']['requested_id_and_estimand_coverage']=='exact_pinned_contract'
    assert all(x['n_evaluated']==8 and x['n_violating']==0 for x in result['result']['coherence'])
