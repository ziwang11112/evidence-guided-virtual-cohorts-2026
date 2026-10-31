"""Independent public-artifact M16 audit. Never opens any private cohort file."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import ast
import csv
import hashlib
import json
import math

R = Path(__file__).resolve().parents[1]
P = R.parents[1]
REVIEW = R / 'review'
SCIENCE = ('evidence.json', 'model_spec.json', 'audit/construction.json', 'audit/revision_plan.json')
CHECKS = ('all_builders_closed', 'preauthorship_verified', 'feedback_binding_verified',
          'source_exposure_verified', 'preservation_verified', 'budgets_verified',
          'independent_code_review_complete')
STAGES = {'b1': ('initial', 'final'), 'b2': ('initial', 'revision1', 'final'), 'b3': ('initial', 'final')}
BINDINGS = {}
ASSERTIONS = 0


def safe(path):
    p = Path(path).resolve()
    if not p.is_relative_to(P) or p.is_relative_to(R / 'private') or p.name.lower() == 'reference.csv':
        raise AssertionError('Forbidden audit read: ' + str(p))
    return p


def sha(path):
    p = safe(path)
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    BINDINGS[str(p)] = h
    return h


def read(path):
    p = safe(path)
    sha(p)
    return json.loads(p.read_text(encoding='utf-8-sig'))


def expect(value, message):
    global ASSERTIONS
    ASSERTIONS += 1
    if not value:
        raise AssertionError(message)


def match(path, expected):
    expect(sha(path) == expected, 'Hash mismatch: ' + str(path))


def time(value):
    return datetime.fromisoformat(value)


def rows(path):
    p = safe(path)
    sha(p)
    with p.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        out = list(reader)
        return reader.fieldnames, out


def audit():
    pre = read(R / 'prelaunch.json')
    for rel, expected in pre['files'].items():
        match(R / rel, expected)
    for path, expected in pre['engine_files'].items():
        match(path, expected)
    # Parse, do not import or execute, the root authorizer.
    release_text = safe(R / 'release_target.py').read_text(encoding='utf-8')
    for node in ast.parse(release_text).body:
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'CHECKS' for x in node.targets):
            expect(ast.literal_eval(node.value) == CHECKS, 'Release assertion interface changed')
            break
    else:
        raise AssertionError('Release assertion interface missing')
    sha(R / 'release_target.py')
    base_header, observed = rows(R / 'visible/observed.csv')
    expect(base_header == ['sample_id', 'race', 'sex', 'age', 'bmi'], 'Observed schema')
    expect(len(observed) == 200 and len({x['sample_id'] for x in observed}) == 200, 'Observed unique rows')
    details = {}
    pending = []
    for bid, stages in STAGES.items():
        b = R / 'visible' / bid / 'bundle'
        task = read(b / 'task.json')
        expect(task['budget'] == {'source_queries': 8, 'source_downloads': 4, 'revisions': 2}, 'Task budgets')
        match(b / 'observed.csv', sha(R / 'visible/observed.csv'))
        reg = read(b / 'registry.json')
        expect(reg['artifacts'][:len(pre['registry_prefixes'][bid])] == pre['registry_prefixes'][bid], 'Seed prefix')
        for a in reg['artifacts']:
            match(b / a['path'], a['sha256'])
        actual_stages = {x.name for x in (b / 'candidates').iterdir() if x.is_dir()}
        expect(actual_stages == set(stages), 'Extra or missing candidate directories: ' + bid)
        source_plan = read(b / 'candidates/initial/model_spec.json')['parameters']['source_check_plan']
        expect(len(source_plan) == {'b1': 33, 'b2': 23, 'b3': 27}[bid], 'Source-check count')
        stage_rows = {}
        stage_details = {}
        for stage in stages:
            c = b / 'candidates' / stage
            if not (c / 'freeze.json').exists() or not (R / 'visible' / bid / 'feedback' / (stage + '.json')).exists():
                pending.append(bid + '/' + stage)
                continue
            freeze = read(c / 'freeze.json')
            expect(freeze['route'] == 'generated.csv' and not (c / 'generator.py').exists(), 'Direct route')
            expect(freeze['candidate'] == 'candidates/' + stage, 'Freeze identity')
            actual_files = {str(p.relative_to(b)).replace('\\', '/') for p in c.rglob('*') if p.is_file() and p.name != 'freeze.json'}
            expect(actual_files == set(freeze['candidate_files']), 'Frozen candidate file inventory')
            for path, expected in freeze['commitments'].items():
                match(b / path, expected)
            expect(freeze['registry_snapshot']['path'] == 'registry.json', 'Registry snapshot path')
            encoded_registry = json.dumps(reg['artifacts'], sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
            expect(hashlib.sha256(encoded_registry).hexdigest() == freeze['registry_snapshot']['sha256'], 'Canonical registry snapshot hash')
            expect(freeze['registry_snapshot']['artifact_count'] == len(reg['artifacts']), 'Frozen source registry count')
            receipt_path = R / 'commitments' / bid / (stage + '.json')
            receipt = read(receipt_path)
            match(c / 'audit/preauthoring_commitment.json', sha(receipt_path))
            expect(receipt['generated_exists'] is False, 'Rows preceded commitment')
            expect(receipt['builder'] == bid and receipt['candidate'] == 'candidates/' + stage, 'Commitment identity')
            expect(receipt['prelaunch_sha256'] == sha(R / 'prelaunch.json'), 'Prelaunch binding')
            expect(set(receipt['files']) == set(SCIENCE), 'Four committed files')
            expect(time(pre['created_utc']) < time(receipt['created_utc']) < time(freeze['created_utc']), 'Preauthorship chronology')
            for name, expected in receipt['files'].items():
                match(c / name, expected)
                expect(freeze['commitments']['candidates/' + stage + '/' + name] == expected, 'Freeze/commitment science binding')
            model = read(c / 'model_spec.json')
            construction = read(c / 'audit/construction.json')
            expect(model['parameters']['construction'] == construction, 'Embedded construction')
            expect(construction['interpretation'] == 'working_guides', 'Working-guide interpretation')
            expect(model['parameters']['source_check_plan'] == source_plan, 'Source plan drift')
            for name in SCIENCE[:3]:
                match(c / name, sha(b / 'candidates/initial' / name))
            recipes = read(c / 'source_checks.json')['checks']
            expect([{k:v for k,v in item.items() if k != 'table'} for item in recipes] == source_plan, 'Predeclared source recipes')
            table_hash = sha(c / 'generated.csv')
            for item in recipes:
                expected_table = None if item['status'] == 'not_computable' else {'path': 'generated.csv', 'sha256': table_hash, 'origin': 'agent_supplied_simulation'}
                expect(item['table'] == expected_table, 'Source table linkage')
            header, table = rows(c / 'generated.csv')
            expect(header == base_header + ['urate'] and len(table) == 200, 'Generated schema/rows')
            for i, (obs, gen) in enumerate(zip(observed, table)):
                expect({k:gen[k] for k in base_header} == obs, 'Observed cell/order differs at ' + str(i))
                expect(math.isfinite(float(gen['urate'])) and float(gen['urate']) >= 0, 'Generated finite bound')
            stage_rows[stage] = table
            plan = read(c / 'audit/revision_plan.json')
            checks = read(c / 'checks.json')
            for artifact in checks['artifacts']:
                match(c / artifact['path'], artifact['sha256'])
            if stage == 'initial':
                expect(plan['action'] == 'initial' and plan['parent_candidate'] is None, 'Initial lineage')
            else:
                parent = plan['parent_candidate']
                expected_parent = 'revision1' if bid == 'b2' and stage == 'final' else 'initial'
                expect(parent == expected_parent, 'Parent stage')
                pc = b / 'candidates' / parent
                expect(freeze['parent']['candidate'] == 'candidates/' + parent, 'Freeze parent')
                match(pc / 'freeze.json', freeze['parent']['sha256'])
                parent_feedback_path = R / 'visible' / bid / 'feedback' / (parent + '.json')
                parent_feedback = read(parent_feedback_path)
                match(c / 'audit/parent_feedback.json', sha(parent_feedback_path))
                artifact_hashes = {a['sha256'] for a in checks['artifacts']}
                expect(sha(parent_feedback_path) in artifact_hashes, 'Actual parent feedback not bound')
                for item in parent_feedback['self_reports'].values():
                    expect(item['sha256'] in artifact_hashes, 'Actual parent self-report not bound')
                parent_execution = read(b / 'executions' / (parent + '_direct_validation') / 'execution.json')
                expect(time(parent_execution['created_utc']) < time(receipt['created_utc']), 'Parent diagnostics preceded next commitment')
                if stage == 'final':
                    expect(plan['action'] == 'retain' and freeze['revision']['kind'] == 'retain', 'Terminal retain')
                    match(c / 'generated.csv', sha(pc / 'generated.csv'))
                else:
                    expect(plan['action'] == 'row_repair' and freeze['revision']['kind'] == 'revise', 'Revision repair')
            feedback_path = R / 'visible' / bid / 'feedback' / (stage + '.json')
            feedback = read(feedback_path)
            reservation = read(R / 'feedback_reservations' / bid / (stage + '.json'))
            slot = {'initial': 1, 'revision1': 2, 'final': 3}[stage]
            for obj in [feedback, reservation]:
                expect(obj['slot'] == slot and obj['terminal'] is (stage == 'final'), 'Feedback slot/terminal')
                expect(obj['freeze_sha256'] == sha(c / 'freeze.json'), 'Feedback freeze binding')
            expect(time(freeze['created_utc']) <= time(reservation['created_utc']), 'Frozen before feedback')
            expect(feedback['target_outcomes_read'] is False and feedback['rows_created_or_changed'] is False, 'Feedback no target access/mutation')
            expect(feedback['table_sha256'] == table_hash, 'Feedback table binding')
            expect(feedback['controller_sha256'] == sha(R / 'controller.py'), 'Feedback controller')
            expect(feedback['source_engine_sha256'] == sha(P / 'cohort_harness/source_checks.py'), 'Feedback source engine')
            reported = feedback['source_statistics']['checks']
            expect([{k:x.get(k) for k in source_plan[0]} for x in reported] == source_plan, 'Feedback source definitions')
            for label, item in feedback['self_reports'].items():
                match(item['path'], item['sha256'])
                report = read(item['path'])
                expect(report['status'] == 'computed' and report['table_contract'] == 'valid', 'Self-report status')
                expect(report['observed_preservation'] == 'exact_decoded_csv_cells', 'Self-report preservation')
                expect(report['interpretation'] == 'working_guides', 'Self-report interpretation')
                for key, path in {'task': b/'task.json', 'observed': b/'observed.csv', 'generated': c/'generated.csv', 'spec': c/'audit/construction.json'}.items():
                    expect(report['bindings'][key]['sha256'] == sha(path), 'Self binding: ' + key)
                expect(report['implementation']['self_consistency_sha256'] == sha(P/'cohort_harness/self_consistency.py'), 'Self implementation')
            if stage != 'initial':
                expect(feedback['self_reports']['current']['sha256'] == feedback['self_reports']['original']['sha256'], 'Original/current guide diagnostics differ')
            exroot = b / 'executions' / (stage + '_direct_validation')
            execution = read(exroot / 'execution.json')
            expect(execution['status'] == 'success' and execution['generator_executed'] is False, 'Direct validation execution')
            expect(execution['route'] == 'generated.csv' and execution['candidate_freeze_sha256'] == sha(c/'freeze.json'), 'Execution linkage')
            expect(time(reservation['created_utc']) <= time(execution['created_utc']), 'Reservation before execution')
            for path, expected in execution['files'].items():
                match(exroot / path, expected)
            expect(execution['files']['input/generated.csv'] == table_hash == execution['files']['output/generated.csv'], 'Execution table untouched')
            stage_details[stage] = {'preauthoring_created_utc': receipt['created_utc'], 'freeze_created_utc': freeze['created_utc'], 'feedback_slot': slot, 'terminal': stage == 'final', 'freeze_sha256': sha(c/'freeze.json'), 'table_sha256': table_hash, 'source_checks': len(source_plan), 'not_computable': sum(x['status']=='not_computable' for x in source_plan)}
        actual_reservations = {x.stem for x in (R/'feedback_reservations'/bid).glob('*.json')}
        expect(actual_reservations.issubset(set(stages)), 'Unscheduled feedback reservation')
        actual_runs = {x.name for x in (b/'executions').iterdir() if x.is_dir()}
        expect(actual_runs.issubset({x+'_direct_validation' for x in stages}), 'Unscheduled execution')
        if 'final' in stage_rows:
            expect(actual_reservations == set(stages) and actual_runs == {x+'_direct_validation' for x in stages}, 'Incomplete scheduled diagnostics')
            changes = sum(a['urate'] != z['urate'] for a,z in zip(stage_rows['initial'], stage_rows['final']))
            expect(changes == (12 if bid == 'b2' else 0), 'Changed outcome count')
        else:
            changes = None
        if bid == 'b2' and 'revision1' in stage_rows:
            inventory = [{'sample_id':a['sample_id'], 'old_urate':a['urate'], 'new_urate':z['urate']} for a,z in zip(stage_rows['initial'],stage_rows['revision1']) if a['urate']!=z['urate']]
            structural = read(b/'candidates/revision1/audit/structural_check.json')
            expect(len(inventory) == 12 and inventory == structural['changed_outcomes_local_inventory'], 'Actual twelve-edit inventory')
        details[bid] = {'stages': stage_details, 'initial_final_changed_outcome_cells': changes, 'scientific_parameter_changes': 0, 'observed_cells_per_stage_verified': 1000}
    source_audit = REVIEW/'SOURCE_EXPOSURE_CLOSURE.json'
    if not source_audit.exists():
        pending.append('source exposure closure')
    else:
        source = read(source_audit)
        expect(source['status'] == 'pass' and source['target_outcomes_read'] is False, 'Source exposure audit not passed')
        expect({x['builder'] for x in source['counts']} == set(STAGES), 'Source budget builder coverage')
        for item in source['counts']:
            bid = item['builder']
            expect((item['queries'], item['total_acquisition_attempts']) == {'b1':(2,3),'b2':(3,3),'b3':(4,2)}[bid], 'Full source query/acquisition charges')
            expect(item['queries'] <= 8 and item['total_acquisition_attempts'] <= 4 and item['new_originals_admitted'] <= 4, 'Source budget cap')
            first = time(details[bid]['stages']['initial']['preauthoring_created_utc'])
            expect(time(item['last_gateway_command_utc']) < first and time(item['last_controller_admission_utc']) < first, 'Source exposure precedes initial authorship commitment')
        for item in source['bindings']:
            match(item['path'], item['sha256'])
    for q, expected in {
        'independent_target_audit/recompute.py': 'c969c2141de94e7d31762ff86dca41a802f7e7deb800b79f7ba499cdb52d1f29',
        'independent_target_audit/test_recompute.py': '470e94e9b6743aca80dfb6af5aba15e0bbe174783bcb596df541448a51c7efd7',
        'independent_target_audit/frozen_independent.py': 'e2cd4b3cc7720c3d2bc42f5e67dae9c67595534091f1fe0631683f16fc1398da',
    }.items():
        match(R/q, expected)
    for name in ['INDEPENDENT_ADAPTER_REVIEW.md', 'B1_RETENTION_CHAIN_AUDIT.json', 'SELF_CHECK_INDEPENDENT_REVIEW.md', 'INDEPENDENT_SELF_CHECK.json', 'source_b1_initial.md', 'source_b2_initial.md', 'source_b2_revision1.md', 'source_b2_final.md', 'source_b3_initial.md', 'source_b3_final.md']:
        sha(REVIEW/name)
    failures = []
    for path in sorted((R/'operational_failures').glob('*.json')):
        failures.append({'path':str(path), 'record':read(path)})
    sha(__file__)
    return {'status':'pending' if pending else 'pass', 'target_outcomes_read':False,
            'pending':pending, 'assertions':ASSERTIONS, 'builders':details,
            'controller_operational_failures':failures,
            'checks':{k:not pending for k in CHECKS},
            'bindings':[{'path':p,'sha256':h} for p,h in sorted(BINDINGS.items())]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--close', action='store_true', help='Only after root confirms all final freezes ready')
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    try:
        result = audit()
        (REVIEW / ('CLOSURE_DETAIL_' + stamp + '.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        if args.close:
            expect(result['status'] == 'pass', 'Closure still pending')
            report = REVIEW/'FINAL_RELEASE_AUDIT.md'
            expect(report.exists(), 'Independent narrative report must exist before pass record')
            result['bindings'].append({'path':str(report.resolve()), 'sha256':sha(report)})
            with (REVIEW/'RELEASE_CHECKS.json').open('x',encoding='utf-8',newline='\n') as f:
                json.dump(result,f,indent=2);f.write('\n')
        event = {'utc':stamp, 'mode':'close' if args.close else 'inspect', 'status':result['status'], 'assertions':ASSERTIONS, 'pending':result['pending'], 'target_outcomes_read':False}
    except Exception as error:
        event = {'utc':stamp, 'mode':'close' if args.close else 'inspect', 'status':'failed', 'error_type':type(error).__name__, 'error':str(error), 'assertions_before_failure':ASSERTIONS, 'target_outcomes_read':False}
        with (REVIEW/'CLOSURE_AUDIT_ATTEMPTS.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(event)+'\n')
        raise
    with (REVIEW/'CLOSURE_AUDIT_ATTEMPTS.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(event)+'\n')
    print(json.dumps(event))


if __name__ == '__main__':
    main()
