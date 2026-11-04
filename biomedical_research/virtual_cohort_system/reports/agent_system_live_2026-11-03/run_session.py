"""Declared live integration runner. Never chooses or changes scientific parameters."""
from pathlib import Path
import argparse,importlib.util,json,sys,hashlib
from datetime import datetime,timezone
P=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(P))
from cohort_harness import execution,lifecycle,semantic_feedback_v1
ROOT=Path(__file__).resolve().parent
PROTOCOL_HASH='4e95e8e32bf4e33b18502ea6051481400cf6ef4886acade990184119284dc7d0'
DIAGNOSTIC_HASH='eea5a4a06738f3fe9e9cb44a7024b6294cde3bb5f389c6b764554ecf1d95e8fe'
STAGES={'initial_trial':[7300],'initial_delivery':[7301,7302,7303],
        'revision_trial':[7310],'final_delivery':[7301,7302,7303]}
def read(p):return lifecycle.read_json(p)
def write(p,v):execution._write(p,v)
def timestamp():return datetime.now(timezone.utc).isoformat()
def setup(key):
    assert key in {'A','B'}
    assert lifecycle.sha256(ROOT/'PROTOCOL.json')==PROTOCOL_HASH
    protocol=read(ROOT/'PROTOCOL.json')
    bundle=Path(protocol['bundles'][key])
    local=ROOT/'sessions'/key
    local.mkdir(parents=True,exist_ok=True)
    assert read(bundle/'RUN_RULES.json')['protocol_sha256']==PROTOCOL_HASH
    return bundle,local
def freeze(key,candidate,parent=None,revision=None):
    bundle,local=setup(key)
    preflight=semantic_feedback_v1.preflight(bundle,candidate)
    candidate_path=bundle/'candidates'/execution._name(candidate)
    if (candidate_path/'freeze.json').exists():
        return lifecycle.verify_candidate(bundle,candidate_path)
    parent_receipt=bundle/'candidates'/execution._name(parent)/'freeze.json' if parent else None
    result=lifecycle.freeze_candidate(bundle,candidate_path,
           parent_receipt=parent_receipt,revision=read(Path(revision)) if revision else None)
    write(local/(candidate+'_preflight.json'),preflight)
    return result
def run(key,candidate,stage):
    bundle,local=setup(key)
    assert stage in STAGES
    name=execution._name(candidate)
    candidate_rel='candidates/'+name
    frozen=lifecycle.verify_candidate(bundle,candidate_rel)
    initial_file=local/'initial_family.json'
    freeze_sha=lifecycle.sha256(bundle/candidate_rel/'freeze.json')
    if stage.startswith('initial_'):
        assert frozen['revision_index']==0 and frozen['parent'] is None,'Initial stage requires an initial candidate'
        family={'candidate':candidate_rel,'freeze_sha256':freeze_sha}
        if initial_file.exists():
            assert read(initial_file)==family,'Initial trial/delivery candidates differ'
        else:
            write(initial_file,family)
    else:
        assert initial_file.exists(),'Final stage lacks initial family'
        initial=read(initial_file)
        for initial_seed in STAGES['initial_delivery']:
            assert (local/(key.lower()+'_initial_delivery_'+str(initial_seed)+'_result.json')).exists(),'Initial deliveries not complete'
        if candidate_rel==initial['candidate']:
            assert freeze_sha==initial['freeze_sha256']
            decision=read(bundle/'FINAL_DECISION.json')
            assert decision['choice']=='retain' and decision['candidate']==candidate_rel,'Retention must be explicit'
        else:
            assert frozen['revision_index']==1 and frozen['parent']['candidate']==initial['candidate'],'Final must be a direct revision'
            assert frozen['parent']['sha256']==initial['freeze_sha256'],'Final parent receipt mismatch'
        final_family=local/'final_family.json'
        family={'candidate':candidate_rel,'freeze_sha256':freeze_sha}
        if final_family.exists():
            assert read(final_family)==family,'Revision trial/final delivery candidates differ'
        else:
            write(final_family,family)
    binding=local/(stage+'_binding.json')
    if binding.exists():
        assert read(binding)['candidate']==candidate_rel
    else:
        write(binding,{'candidate':candidate_rel,'created_utc':timestamp(),
                      'candidate_sha256':lifecycle.sha256(bundle/candidate_rel/'freeze.json')})
    path=ROOT/'evaluation/generated_diagnostics.py'
    assert lifecycle.sha256(path)==DIAGNOSTIC_HASH
    spec=importlib.util.spec_from_file_location('live_generated_diagnostics',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    results=[]
    for seed in STAGES[stage]:
        run_id=key.lower()+'_'+stage+'_'+str(seed)
        event=local/(run_id+'_reserved.json')
        # A reserved attempt is never silently retried, including a previous crash.
        assert not event.exists(),'Attempt already reserved: '+run_id
        assert len(list(local.glob('*_reserved.json')))<8,'Per-request attempt budget exhausted'
        write(event,{'run_id':run_id,'seed':seed,'stage':stage,'candidate':candidate_rel,
                     'created_utc':timestamp(),'charged':True})
        record={'run_id':run_id,'seed':seed,'stage':stage,'candidate':candidate_rel}
        try:
            receipt=execution.run_candidate(bundle,candidate_rel,run_id,seed,timeout_seconds=30,
                                           memory_mb=1536,output_bytes=20_000_000,log_bytes=100_000)
            execution.verify_execution(bundle,run_id)
            record.update(status=receipt['status'],execution_status=receipt['status'],generator_executed=receipt['generator_executed'],
                          error=receipt.get('error'))
            if receipt['status']=='success':
                feedback_id=run_id+'_source'
                feedback=semantic_feedback_v1.collect_feedback(bundle,candidate_rel,run_id,feedback_id)
                table=bundle/'executions'/run_id/'output/generated.csv'
                diagnostics=module.diagnose_csv(table,key)
                out=bundle/'author_feedback';out.mkdir(exist_ok=True)
                write(out/(run_id+'_diagnostics.json'),diagnostics)
                record.update(table_sha256=lifecycle.sha256(table),
                              source_feedback=str(bundle/'semantic_feedback_v1'/feedback_id/'feedback.json'),
                              diagnostics=str(out/(run_id+'_diagnostics.json')),
                              source_feedback_status=feedback.get('status'))
        except Exception as err:
            record.update(status='wrapper_error',error=type(err).__name__+': '+str(err))
        write(local/(run_id+'_result.json'),record)
        results.append(record)
    return results
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=['freeze','run'])
    ap.add_argument('--request',choices=['A','B'],required=True)
    ap.add_argument('--candidate',required=True)
    ap.add_argument('--stage',choices=list(STAGES))
    ap.add_argument('--parent');ap.add_argument('--revision')
    args=ap.parse_args()
    if args.action=='freeze':
        result=freeze(args.request,args.candidate,args.parent,args.revision)
        print(json.dumps({'status':'frozen','request':args.request,'candidate':args.candidate,'route':result.get('route')},indent=2))
    else:
        if args.stage is None:ap.error('--stage required')
        print(json.dumps(run(args.request,args.candidate,args.stage),indent=2))
if __name__=='__main__':main()
