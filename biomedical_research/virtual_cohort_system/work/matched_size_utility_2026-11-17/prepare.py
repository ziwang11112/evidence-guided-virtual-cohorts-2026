"""Schema-only preflight, explicit RNG inventory and pre-execution freeze."""
import sys
import platform
import scipy
from common import *

def preflight():
    records=get_inputs(); frames, exclusions=load_frames(records); pools=make_pools(frames)
    virtual=sorted(n for n in frames if n!='real')
    assert len(virtual)==6
    counts={t:strata_counts(pools[t]['real']) for t in TRAITS}
    available=[]
    for t in TRAITS:
        assert len(pools[t]['real'])==EXPECTED_N[t], 'Reference eligibility mismatch: '+t
        assert sum(counts[t])==EXPECTED_N[t]
        for name in ['real']+virtual:
            if name!='real':
                assert len(frames[name])==1226 and len(pools[t][name])==1226
            cells=strata_counts(pools[t][name])
            available.append(dict(trait=t,dataset_id=name,n=len(pools[t][name]),cells=cells,
                missing_required_cells=[i for i,(needed,found) in enumerate(zip(counts[t],cells)) if needed>0 and found==0]))
    streams=[]
    for ti,t in enumerate(TRAITS):
        for rep in range(N_REPLICATES):
            for si,role in enumerate(['R_A','R_B']+virtual):
                streams.append(dict(trait=t,replicate=rep,stream=role,stream_index=si,
                    dataset_id='real' if si<2 else role,spawn_key=[ti,rep,si]))
    assert len(streams)==12000 and len({tuple(r['spawn_key']) for r in streams})==12000
    binding_files=[PROTOCOL]+[OLD/n for n in ['PROTOCOL.md','analysis_operator.py','reference_adapter.py','FINAL_TABLES.json',
        'EVALUATION_INPUTS.json','CONSTRUCTION_CLOSURE.json','ANALYSIS_RESULTS.json','ANALYSIS_CONTRASTS.csv']]
    binding_files += [Path(r['path']).resolve() for r in records]
    bindings={str(f.relative_to(ROOT)).replace('\\','/'):sha(f) for f in binding_files}
    write_new(HERE/'INPUT_BINDINGS.json',dict(files=bindings,records=records))
    write_new(HERE/'PREFLIGHT.json',dict(created_utc=now(),schema_only=True,reference_exclusions=exclusions,
        expected_n=EXPECTED_N,strata=[list(x) for x in STRATA],reference_counts=counts,availability=available,
        virtual_ids=virtual,inputs=7,available_virtual_slots=6,
        versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,scipy=scipy.__version__)))
    write_new(HERE/'STREAM_MAP.json',dict(root_seed=ROOT_SEED,bit_generator='PCG64',strata_order=[list(x) for x in STRATA],
        replicas=N_REPLICATES,streams=streams))
    print(json.dumps(dict(status='preflight_complete_no_resampling',real_counts=EXPECTED_N,
        required_missing_cells=sum(len(r['missing_required_cells']) for r in available),stream_count=len(streams))))

def freeze():
    assert not (HERE/'RUN_STARTED.json').exists()
    tests=read(HERE/'TEST_RECEIPT.json');assert tests['passed']
    review=read(HERE/'IMPLEMENTATION_REVIEW.json');assert review['ready_to_freeze']
    files=read(HERE/'INPUT_BINDINGS.json')['files'].copy()
    for name in ['common.py','prepare.py','run.py','summarize.py','independent_review.py','test_wrapper.py','PROTOCOL.md',
                 'INPUT_BINDINGS.json','PREFLIGHT.json','STREAM_MAP.json','TEST_RECEIPT.json','IMPLEMENTATION_REVIEW.json']:
        f=HERE/name;files[str(f.relative_to(ROOT)).replace('\\','/')]=sha(f)
    for name,value in files.items():assert sha(ROOT/name)==value
    write_new(HERE/'FREEZE.json',dict(created_utc=now(),status='frozen_before_resampling',files=files,
        n_replicates=500,root_seed=16161,planned_trait_sample_evaluations=12000,max_wall_seconds=3600,
        independent_replay_replicates=[0,249,499],new_agent_calls=0,new_generated_cohorts=0,
        sampling_scope='Conditional empirical participant resampling; not independent cohorts or clinical equivalence'))
    print(json.dumps(dict(status='frozen',bound_files=len(files),planned_evaluations=12000)))

if __name__=='__main__':
    {'preflight':preflight,'freeze':freeze}[sys.argv[1]]()
