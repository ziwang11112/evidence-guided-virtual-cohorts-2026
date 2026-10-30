"""Build an all-construction release gate without parsing target outcomes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

O = Path(__file__).resolve().parent
P = O.parents[1]
S = P / 'work/analysis-utility-preparation-2026-10-29'
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import verify_candidate
from cohort_harness.execution import verify_execution

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    launch = read(O/'launch.json')
    for item in launch['bindings']:
        require(sha(Path(item['path'])) == item['sha256'], item['path'])
    # A source-only implementation review must be completed before the gate.
    review = read(O/'implementation_review.json')
    require(review['target_outcomes_read'] is False, 'Review was not target-blind')
    require(review['ready_for_locked_evaluation'] is True, 'Review did not clear evaluation')
    cases = {
        'nhanes_insulin': {
            'observed_path': str(S/'nhanes_insulin/visible/observed.csv'),
            'reference_path': str(S/'nhanes_insulin/custodian/reference.csv'),
            'prepare_reader_path': str(S/'nhanes_insulin/prepare.py'),
            'demo_path': str(S/'nhanes_insulin/custodian/raw/DEMO_I.xpt'),
            'fasting_design_path': str(S/'nhanes_insulin/custodian/raw/GLU_I.xpt')},
        'pns_hba1c': {
            'observed_path': str(S/'pns_hba1c/visible/observed.csv'),
            'reference_path': str(S/'pns_hba1c/custodian/reference.csv'),
            'weights_path': str(S/'pns_hba1c/custodian/design_weights.csv'),
            'id_mapping_path': str(S/'pns_hba1c/custodian/id_mapping.csv')}
    }
    # Compare opaque reserved bytes against the original M9 preparation seals,
    # not just newly calculated release hashes.
    seals = {
        'nhanes_insulin': read(S/'nhanes_insulin/artifact_manifest.json')['artifacts'],
        'pns_hba1c': read(S/'pns_hba1c/custodian/integrity_manifest.json')['files']}
    for case, records in seals.items():
        expected = {str((S/case/r['path']).resolve()):r['sha256'] for r in records}
        for key in ['observed_path','reference_path','weights_path','id_mapping_path']:
            if key in cases[case]:
                p = Path(cases[case][key]).resolve()
                require(sha(p) == expected[str(p)], ('Original preparation seal changed', p))
    controller = [O/'launch.json', O/'runtime_preflight.json', O/'implementation_review.json',
                  Path(__file__).resolve(), O/'prepare_launch.py', O/'execution_locations.json',
                  O/'audit_current.py', O/'blind_review.json', O/'evaluator/CHECKS.json',
                  S/'ACTIVE_PROTOCOL.json', S/'protocols/campaign_feasibility_v2.json',
                  S/'nhanes_insulin/artifact_manifest.json',
                  S/'pns_hba1c/custodian/integrity_manifest.json']
    controller += [S/'bundles'/c/'input_manifest.json' for c in cases]
    bind = set(controller)
    bind.update(Path(x['path']) for x in launch['bindings'])
    bind.update(Path(x) for c in cases.values() for x in c.values())
    bind.update((O/'evaluator').glob('*.py'))
    bind.update([O/'evaluator/FREEZE_INTERFACE.md',O/'evaluator/INFERENCE.md'])
    constructions = []
    locations = read(O/'execution_locations.json')
    for scheduled in launch['construction_schedule']:
        location = locations['constructions'][scheduled['construction_id']]
        bundle = Path(location['bundle_path'])
        selection_path = Path(location['selection_path'])
        # Some builders keep an immutable pre-execution selection and a separate
        # status-enriched final record. Bind the actual earlier selection.
        if (bundle/'selection_pre_execution.json').exists():
            selection_path = bundle/'selection_pre_execution.json'
        selection = read(selection_path)
        require(selection['target_outcomes_read'] is False, 'Selection was not target-blind')
        name = selection['selected_candidate']
        candidate = Path(name)
        if not candidate.is_absolute():
            candidate = bundle/name if name.startswith('candidates/') else bundle/'candidates'/name
        candidate = candidate.resolve()
        require(candidate.is_relative_to(bundle/'candidates'), 'Candidate outside own bundle')
        receipt = verify_candidate(bundle, candidate)
        initial = candidate
        while read(initial/'freeze.json')['parent'] is not None:
            initial = bundle/read(initial/'freeze.json')['parent']['candidate']
        verify_candidate(bundle, initial)
        outputs = []
        for execution_path in sorted((bundle/'executions').glob('*/execution.json')):
            r = read(execution_path)
            # Keep all failed receipts on disk; only selected successful final draws meet release gate.
            if r.get('status') != 'success':
                continue
            seed = r.get('limits', {}).get('seed')
            if seed not in launch['residual_seeds']:
                continue
            if r.get('candidate') != candidate.relative_to(bundle).as_posix():
                continue
            run_id = execution_path.parent.name
            verify_execution(bundle, run_id)
            path = execution_path.parent/'output/generated.csv'
            outputs.append({'path': str(path), 'sha256': sha(path), 'seed': seed,
                            'receipt_path': str(execution_path), 'receipt_sha256': sha(execution_path),
                            'run_id': run_id})
        require(sorted(x['seed'] for x in outputs) == launch['residual_seeds'], (bundle, outputs))
        constructions.append({**scheduled, 'bundle_path':str(bundle), 'initial_candidate': str(initial),
                              'selected_candidate': str(candidate), 'final_selection_path': str(selection_path),
                              'outputs': outputs})
        bind.update([selection_path, bundle/'task.json', bundle/'observed.csv',
                     initial/'freeze.json', candidate/'freeze.json'])
        for extra in ['final_selection.json','execution_statuses.json']:
            if (bundle/extra).exists():
                bind.add(bundle/extra)
    m = {'schema_version':'m10-campaign-freeze-1','status':'frozen_before_target_analysis',
         'target_outcomes_inspected':False,'frozen_utc':datetime.now(timezone.utc).isoformat(),
         'residual_seeds':launch['residual_seeds'], 'cases':cases, 'constructions':constructions,
         'controller_binding_paths':[str(p) for p in controller],
         'bindings':[{'path':str(p),'sha256':sha(p)} for p in sorted(bind)]}
    out = O/'campaign_freeze.json'
    with out.open('x',encoding='utf-8') as f:
        json.dump(m,f,indent=2)
        f.write('\n')
    print(json.dumps({'manifest':str(out),'sha256':sha(out),'constructions':len(constructions),
                      'tables':sum(len(c['outputs']) for c in constructions),'bindings':len(bind)}))

if __name__ == '__main__':
    main()
