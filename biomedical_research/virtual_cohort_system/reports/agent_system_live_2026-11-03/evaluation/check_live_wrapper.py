"""Bounded wrapper control-flow mocks. No generator, CSV, clinical data, or WSL execution."""
from pathlib import Path
import importlib.util, json, hashlib, tempfile, types

HERE=Path(__file__).resolve().parent
WRAPPER=HERE.parent/'run_session.py'
spec=importlib.util.spec_from_file_location('live_wrapper_review',WRAPPER)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
original_sha=mod.lifecycle.sha256
original_write=mod.execution._write
original_read=mod.lifecycle.read_json
checks=[]

def expect_raise(fn, kind, label):
    try: fn()
    except kind: checks.append({'check':label,'status':'PASS'});return
    raise AssertionError(label+' did not reject')

with tempfile.TemporaryDirectory(prefix='mock_wrapper_',dir=HERE) as temp:
    base=Path(temp);bundle=base/'bundle';bundle.mkdir()
    local=base/'session';local.mkdir()
    (bundle/'candidates/c1').mkdir(parents=True)
    original_write(bundle/'candidates/c1/freeze.json',{'mock':True})
    mod.setup=lambda key:(bundle,local)
    initial_hash=original_sha(bundle/'candidates/c1/freeze.json')
    def fake_verify(root,relative):
        return {'revision_index':1 if relative=='candidates/c2' else 0,'candidate':relative,
                'parent':{'candidate':'candidates/c1','sha256':initial_hash} if relative=='candidates/c2' else None}
    mod.lifecycle=types.SimpleNamespace(read_json=original_read,
        verify_candidate=fake_verify,
        sha256=lambda path:original_sha(path) if Path(path).exists() else '0'*64)
    calls=[]
    def fake_run(*args,**kwargs):
        calls.append(args[2]);return {'status':'success','generator_executed':False}
    mod.execution=types.SimpleNamespace(_name=lambda x:x,_write=original_write,
        run_candidate=fake_run,verify_execution=lambda *a,**k:{})
    mod.semantic_feedback_v1=types.SimpleNamespace(collect_feedback=lambda *a,**k:{'status':'complete'})
    # Import of the diagnostics is replaced by a no-read stub, not a fabricated data table.
    mod.importlib=types.SimpleNamespace(util=types.SimpleNamespace(
        spec_from_file_location=lambda *a:types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda m:None)),
        module_from_spec=lambda s:types.SimpleNamespace(diagnose_csv=lambda *a:{'mock':True,'reference_read':False})))
    results=mod.run('A','c1','initial_trial')
    assert results[0]['status']=='success' and len(calls)==1
    assert len(list(local.glob('*_reserved.json')))==1
    assert len(list(base.rglob('*.csv')))==0
    checks.append({'check':'successful attempt reserved before mocked execution and explicit v1 feedback','status':'PASS'})
    expect_raise(lambda:mod.run('A','c1','initial_trial'),AssertionError,'duplicate attempt rejected')
    expect_raise(lambda:mod.run('A','other','initial_trial'),AssertionError,'stage candidate substitution rejected')
    expect_raise(lambda:mod.run('A','c2','revision_trial'),AssertionError,'final stage before initial deliveries rejected')
    results=mod.run('A','c1','initial_delivery')
    assert len(results)==3 and len(calls)==4
    expect_raise(lambda:mod.run('A','other','revision_trial'),AssertionError,'unrelated fresh final candidate rejected')
    def fake_failure(*args,**kwargs):raise RuntimeError('invented executor failure')
    mod.execution.run_candidate=fake_failure
    results=mod.run('A','c2','revision_trial')
    assert results[0]['status']=='wrapper_error'
    assert len(list(local.glob('*_reserved.json')))==5
    checks.append({'check':'executor exception recorded and attempt charged','status':'PASS'})
    original_write(bundle/'FINAL_DECISION.json',{'choice':'retain','candidate':'candidates/c1'})
    expect_raise(lambda:mod.run('A','c1','final_delivery'),AssertionError,'final candidate differs from revision trial rejected')
    for i in range(3):original_write(local/f'placeholder{i}_reserved.json',{'mock':True})
    expect_raise(lambda:mod.run('A','c2','final_delivery'),AssertionError,'ninth attempt blocked before executor')
    assert len(calls)==4

report={'wrapper_sha256':hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
        'checks':checks,'patient_rows_read':0,'generated_tables':0,'sandbox_runs':0,
        'scope':'control-flow mocks only; does not validate lifecycle internals or scientific validity'}
destination=HERE/'WRAPPER_MOCK_CHECKS.json'
with destination.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps(report,indent=2))
