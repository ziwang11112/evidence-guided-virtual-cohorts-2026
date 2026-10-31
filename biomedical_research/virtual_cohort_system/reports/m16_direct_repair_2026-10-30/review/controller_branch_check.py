"""Controller guard checks in a temporary invented filesystem; adapters deliberately stubbed."""
from pathlib import Path
import importlib.util
import hashlib
import json
import sys
import tempfile

SOURCE=Path(__file__).resolve().parent.parent/'controller.py'
module_spec=importlib.util.spec_from_file_location('m16_controller_review',SOURCE)
controller=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(controller)


def main():
    results=[]
    with tempfile.TemporaryDirectory(prefix='m16-controller-invented-') as temp:
        controller.R=Path(temp)
        controller.verify_inputs=lambda:'invented-prelaunch'
        controller.verify_precommit=lambda *args:None
        controller.validate_bundle=lambda *args:None
        controller.verify_candidate=lambda *args:None
        controller.freeze_candidate=lambda *args,**kwargs:{'route':'direct_rows'}
        # Captures branches only, not a claim that lifecycle/contracts were integration-tested.
        def write(path,value):
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(value),encoding='utf-8')
        def rejected(call,text,label):
            try:call()
            except ValueError as exc:assert text in str(exc),(label,str(exc));results.append(label)
            else:raise AssertionError(label+' accepted')
        b,c=controller.paths('b1','initial');c.mkdir(parents=True)
        (c/'generated.csv').write_text('key,y\ninvented,1\n',encoding='utf-8')
        (c/'freeze.json').write_text('{}',encoding='utf-8')
        plan={'id':'one','evidence_id':'invented','status':'approximate','operator':{'kind':'mean'},'assumption_ids':['invented'],'reason':'invented'}
        write(c/'model_spec.json',{'parameters':{'source_check_plan':[plan]}})
        actual={**plan,'table':{'path':'other.csv','sha256':controller.sha256(c/'generated.csv'),'origin':'agent_supplied_simulation'}}
        write(c/'source_checks.json',{'checks':[actual]})
        rejected(lambda:controller.freeze('b1','initial'),'frozen authored table','alternate source table rejected')
        actual['table']['path']='generated.csv';actual['operator']={'kind':'sd'}
        write(c/'source_checks.json',{'checks':[actual]})
        rejected(lambda:controller.freeze('b1','initial'),'preauthoring plan','changed source definition rejected')
        actual['operator']=plan['operator'];actual['table']['sha256']='0'*64
        write(c/'source_checks.json',{'checks':[actual]})
        rejected(lambda:controller.freeze('b1','initial'),'frozen authored table','stale generated table hash rejected')
        final=b/'candidates/final/freeze.json';write(final,{})
        rejected(lambda:controller.precommit('b1','revision1'),'terminal','post-terminal revision commitment rejected')
        rejected(lambda:controller.feedback('b1','initial'),'terminal freeze','post-terminal editing feedback rejected')
        # A different builder isolates the precommit-order branch without deleting prior artifacts.
        write(controller.R/'commitments/b2/final.json',{})
        rejected(lambda:controller.precommit('b2','revision1'),'Final already committed','revision after final commitment rejected')
        controller.validate_task=lambda *args:None
        controller.validate_evidence=lambda *args:[]
        controller.validate_spec=lambda *args:None
        controller.validate_self_consistency_spec=lambda *args:None
        b3,c3=controller.paths('b3','final')
        write(b3/'task.json',{});write(c3/'evidence.json',{})
        write(c3/'model_spec.json',{'parameters':{'construction':{},'source_check_plan':[plan]}})
        write(c3/'audit/construction.json',{})
        write(c3/'audit/revision_plan.json',{'stage':'final','action':'retain','parent_candidate':'initial','findings':[],'reason':'invented'})
        write(controller.R/'commitments/b3/revision1.json',{})
        rejected(lambda:controller.precommit('b3','final'),'Cannot bypass','committed intermediate revision cannot be bypassed')
        # CLI failures preserve a readable failure artifact without executing diagnostics.
        def failure(*args):raise RuntimeError('invented diagnostic failure')
        controller.feedback=failure
        argv=sys.argv;sys.argv=['controller.py','feedback','--builder','b3','--stage','final']
        try:
            try:controller.main()
            except RuntimeError as exc:assert str(exc)=='invented diagnostic failure'
            else:raise AssertionError('expected failure')
        finally:sys.argv=argv
        files=list((controller.R/'operational_failures').glob('*.json'))
        assert len(files)==1
        record=json.loads(files[0].read_text())
        assert record['action']=='feedback' and record['stage']=='final' and record['target_outcomes_read'] is False
        results.append('CLI operational failure receipt preserved')
    report={'status':'PASS','scope':'Branch tests in temporary invented filesystem; validation/lifecycle/execution adapters stubbed, not end-to-end integration',
            'controller_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'checks':results,'target_rows_accessed':False}
    with Path(__file__).with_name('CONTROLLER_BRANCH_CHECK.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report))


if __name__=='__main__':main()
