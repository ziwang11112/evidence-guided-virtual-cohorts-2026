"""Mocked aggregate fixtures only: no biomedical rows or actual reference reads."""
import json
from pathlib import Path
from unittest import mock
import pytest
import evaluator_v2 as e
import numpy as np

def test_reference_gate_is_first():
    with mock.patch.object(e.runner,'closure_gate',side_effect=RuntimeError('not closed')) as gate, mock.patch.object(e.runner,'READ',side_effect=AssertionError('must not read')) as read:
        with pytest.raises(RuntimeError,match='not closed'): e.evaluate()
        gate.assert_called_once();read.assert_not_called()

def test_endpoint_contract_rejects_units_and_omission():
    c={'analyses':[{'id':'A','unit':'u'}],'diagnostics':[]}
    with pytest.raises(Exception,match='unit'): e.validate({'analyses':[{'id':'A','unit':'v','status':'computed','value':1.0}],'diagnostics':[]},c)
    with pytest.raises(Exception,match='coverage'): e.validate({'analyses':[],'diagnostics':[]},c)

def test_missing_and_different_signs_remain_visible():
    p={'analyses':[{'id':'A','unit':'u','status':'computed','value':-2.0}], 'diagnostics':[{'id':'D','unit':'u','status':'unavailable','value':None}]}
    refs={'A':{'unit':'u','value':1.0},'D':{'unit':'u','value':4.0}}
    r=e.add_reference(p,refs)
    assert r['analyses'][0]['signed_difference']==-3.0
    assert r['analyses'][0]['generated_direction']=='negative'
    assert r['diagnostics'][0]['comparison_status']=='unavailable'

def test_mock_batch_keeps_direct_aliases_and_all_failed_slots(tmp_path):
    # Numbers are arbitrary software fixtures, not real scientific estimates.
    spec={'analyses':[{'id':'A','unit':'u'}],'diagnostics':[{'id':'D','unit':'u'}]}
    refs={c:{k:{'value':1.0,'unit':'u','status':'computed'} for k in ('A','D')} for c in ('CHNS2009','ENSANUT2018')}
    authors={a:{'case_id':'CHNS2009' if a.startswith('C') else 'ENSANUT2018'} for a in ('C01','C02','E01','E02')}
    protocol={'authors':authors,'reference':{'path':'MOCK_REFERENCE','sha256':'fixture'},'final_seeds':[8101,8102,8103]}
    class S:
        def __init__(self,aid):
            self.author=aid;self.folder=tmp_path/aid;self.bundle=tmp_path/aid
            self.contract={'external_author_id':'mock/'+aid}
        def verify(self):return True
        def events(self):return []
        def selected(self,kind):
            if kind=='closed':return [{'status':'mock_closed','reason':'fixture'}]
            if kind=='freeze':return []
            if kind=='decision':return []
            if self.author!='C01':return []
            if kind=='attempt':return [{'index':i,'purpose':'final','stage':'final','seed':v,'candidate':'candidates/initial','run_id':str(v)} for i,v in enumerate(protocol['final_seeds'],1)]
            if kind=='result':return [{'attempt_index':i,'status':'success','table':{'path':'MOCK_TABLE','sha256':'SAME_HASH'},'receipt':None,'output_route':'generated.csv','seed_role':'fixed_table_validation_slot'} for i in (1,2,3)]
            return []
    real_read=e.runner.READ
    def read(path):
        path=str(path)
        if path=='MOCK_REFERENCE':return {'references':refs}
        if path.endswith('EVALUATOR_V2_CORRECTION.json'):return {'bindings':[]}
        if path.endswith('ENDPOINT_CONTRACT.json'):return {'cases':{c:spec for c in refs}}
        if path.endswith('state.json'):return {'usage':{'queries':0,'downloads':0}}
        if path.endswith('inputs.json'):return {'original_source_ids':[]}
        return real_read(path)
    payload={k:[{**x,'status':'computed','value':np.float64(2.0)} for x in spec[k]] for k in spec}
    with mock.patch.object(e,'ROOT',tmp_path),mock.patch.object(e.runner,'closure_gate',return_value={'physical_attempts':3}),mock.patch.object(e.runner,'protocol',return_value=protocol),mock.patch.object(e.runner,'verify_bound'),mock.patch.object(e.runner,'READ',side_effect=read),mock.patch.object(e.runner,'SHA',return_value='mock_hash'),mock.patch.object(e.runner,'Session',S),mock.patch.object(e.runner,'generated_statistics',return_value=payload):
        e.evaluate()
        result=json.loads((tmp_path/'evaluation_v2/RESULTS.json').read_text())
        assert len(result['all_final_slots'])==12
        assert result['unique_final_table_hashes']==1
        assert sum(s['analysis_status']=='unavailable' for s in result['all_final_slots'])==9
        assert result['all_final_slots'][0]['seed_role']=='fixed_table_validation_slot'
        assert result['all_author_endpoint_summaries'][0]['unique_validated_table_hashes']==1
        with pytest.raises(Exception,match='reserved'):e.evaluate()


def test_real_scalar_boundary():
    for v in (1,1.2,np.float64(2.3),np.float32(2.5),np.int64(2)):
        assert e.finite(v)
    for v in (True,False,np.bool_(True),float("nan"),float("inf"),np.float64("nan"),"1",1+2j,None):
        assert not e.finite(v)
