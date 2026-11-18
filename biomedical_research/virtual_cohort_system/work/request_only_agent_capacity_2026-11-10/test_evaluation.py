"""New evaluation gating/accounting tests; no clinical data or generators."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import pytest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import evaluate_pilot as e

def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v),encoding='utf-8')

def fixture(tmp_path,monkeypatch):
    monkeypatch.setattr(e,'ROOT',tmp_path)
    ids=['PNS_BASE','PNS_WORKFLOW','LIPID_WORKFLOW','LIPID_BASE']
    eps=[{'episode_id':v,'case_id':'PNS' if v.startswith('PNS') else 'lipids','arm':'ordinary' if v.endswith('BASE') else 'workflow'} for v in ids]
    put(tmp_path/'PLAN.json',{'episodes':eps,'evaluation_seeds':[54001,54003,54007]})
    for ep in eps:
        put(tmp_path/'episodes'/ep['episode_id']/'OUTCOME.json',{'episode_id':ep['episode_id'],'selected_candidate':None,'status':'call_limit','calls_reserved':2,'known_tariff_cost_usd':.2,'accounted_usd':.3})
    rows=[{**ep,'candidate_id':None,'candidate_manifest_sha256':None,'outcome_status':'call_limit','files':e.history(tmp_path/'episodes'/ep['episode_id'])} for ep in eps]
    put(tmp_path/'CONSTRUCTION_CLOSURE.json',{'episodes':rows,'plan_sha256':e.sha(tmp_path/'PLAN.json'),'evaluation_seeds':[54001,54003,54007],'all_episodes_closed':True})
    snapshot=tmp_path/'_host/ref.json'
    put(snapshot,{'references':{case:{'test':{'id':'test','unit':'unit','value':2.0,'uncertainty':{'status':'unavailable'}}} for case in ['PNS','lipids']}})
    monkeypatch.setattr(e,'SNAPSHOT',snapshot);monkeypatch.setattr(e,'SNAPSHOT_SHA',e.sha(snapshot))
    return eps

def test_evaluator_refuses_missing_global_closure(tmp_path,monkeypatch):
    monkeypatch.setattr(e,'ROOT',tmp_path)
    with pytest.raises(FileNotFoundError):e.evaluate()

def test_all_unavailable_slots_kept(tmp_path,monkeypatch):
    eps=fixture(tmp_path,monkeypatch)
    slots=[{**ep,'seed':s,'status':'unavailable','statistics':None} for ep in eps for s in [54001,54003,54007]]
    put(tmp_path/'FINAL_TABLES.json',{'construction_closure_sha256':e.sha(tmp_path/'CONSTRUCTION_CLOSURE.json'),'slots':slots})
    result=e.evaluate();assert result['counts']['unavailable_tables']==12
    assert result['counts']['model_calls']==8
    assert result['costs']['accounted_usd']==pytest.approx(1.2)
    assert all(s['mean'] is None for s in e.read(tmp_path/'EVALUATION.json')['summaries'])

def test_mean_absolute_difference_not_difference_of_mean(tmp_path,monkeypatch):
    slots=[{'seed':s,'status':'success','statistics':{'analyses':[{'id':'test','value':v}],'diagnostics':[]}}
           for s,v in zip([54001,54003,54007],[0.,2.,4.])]
    summary=e.summarize_values(slots,'test',2.)
    assert summary['mean']==2
    assert summary['mean_absolute_reference_difference']==pytest.approx(4/3)

def test_changed_closed_history_blocks_evaluation(tmp_path,monkeypatch):
    eps=fixture(tmp_path,monkeypatch)
    put(tmp_path/'episodes'/eps[0]['episode_id']/'OUTCOME.json',{'status':'changed'})
    with pytest.raises(AssertionError):e.verify()

def test_failed_episode_does_not_reopen_uncertain_runtime(tmp_path,monkeypatch):
    fixture(tmp_path,monkeypatch)
    def forbidden(*args,**kwargs):raise RuntimeError('Do not reopen a pending failed tool session')
    monkeypatch.setattr(e.runtime,'ToolRuntime',forbidden)
    slots=e.draw()
    assert len(slots)==12 and all(s['status']=='unavailable' for s in slots)

def test_duplicate_final_slot_rejected(tmp_path,monkeypatch):
    eps=fixture(tmp_path,monkeypatch)
    slots=[{**ep,'seed':s,'status':'unavailable','statistics':None} for ep in eps for s in [54001,54003,54007]]
    slots[-1]=slots[0]
    put(tmp_path/'FINAL_TABLES.json',{'construction_closure_sha256':e.sha(tmp_path/'CONSTRUCTION_CLOSURE.json'),'slots':slots})
    with pytest.raises(AssertionError):e.evaluate()

def test_failed_table_statistics_are_not_averaged(tmp_path,monkeypatch):
    slots=[{'seed':s,'status':'failed','statistics':{'analyses':[{'id':'test','value':999}],'diagnostics':[]}} for s in [54001,54003,54007]]
    assert e.summarize_values(slots,'test',2.)['mean'] is None
