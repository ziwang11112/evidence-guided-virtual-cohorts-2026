"""Fixed C5 execution schedule. No scientific formulas or Agent-code imports."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from cohort_harness import execution, lifecycle
from cohort_harness.contracts import require
from work.c5.method import adapter
from work.c5.setup_tasks import write_new, verify_source_commitment


SCIENCE_FILES = ['generator.py', 'evidence.json', 'model_spec.json', 'decision.md', 'checks.json', 'derivation_check.json']


def now():
    return datetime.now(timezone.utc).isoformat()


def scientific_bindings(root):
    verify_source_commitment(root)
    paths = ['PROTOCOL.md', 'source_commitment.json', 'INITIAL_AUTHOR_COMMITMENT.json',
             'EXPOSURE_NOTE.md',
             'method/adapter.py', 'setup_tasks.py', 'run_unit.py', 'author/request_decisions.json',
             'author/extension_task_template.json', 'visible/output_contract.json', 'visible/analysis_plan.md',
             'visible/request_transcript.md', 'visible/initial_source_packet.json', 'visible/final_source_packet.json']
    for b in ['b/p', 'b/j']:
        lifecycle.verify_candidate(root / b, 'candidates/c0')
        paths.extend([b + '/task.json', b + '/registry.json', b + '/candidates/c0/freeze.json'])
        paths.extend(b + '/candidates/c0/' + f for f in SCIENCE_FILES)
    paths.extend('author/extension/' + f for f in SCIENCE_FILES)
    return {p: lifecycle.sha256(root / p) for p in paths}


def seal(root):
    require(not (root / 'RUN_PLAN.json').exists(), 'Run plan already frozen')
    require(not (root / 'b/p/executions').exists() and not (root / 'b/j/executions').exists(),
            'Cannot freeze after execution')
    plan = {'schema_version': 1, 'unit': 'c5', 'created_utc': now(), 'bindings': scientific_bindings(root),
            'harness': {p.name: lifecycle.sha256(p) for p in (root.parents[1] / 'cohort_harness').glob('*.py')},
            'runs': lifecycle.read_json(root / 'visible/output_contract.json')['runs'],
            'max_scientific_executions': 9}
    write_new(root / 'RUN_PLAN.json', plan)
    return {'plan_sha256': lifecycle.sha256(root / 'RUN_PLAN.json'), 'planned_runs': 9}


def verify_plan(root):
    plan = lifecycle.read_json(root / 'RUN_PLAN.json')
    require(plan['bindings'] == scientific_bindings(root), 'Frozen scientific or procedural inputs changed')
    for name, value in plan['harness'].items():
        require(lifecycle.sha256(root.parents[1] / 'cohort_harness' / name) == value, 'Harness changed')
    return plan


def record_execution(bundle, item):
    receipt = execution.verify_execution(bundle, item['run_id'])
    record = {**item, 'status': receipt['status'], 'bundle': str(bundle),
              'execution_sha256': lifecycle.sha256(bundle / 'executions' / item['run_id'] / 'execution.json')}
    if receipt['status'] == 'success':
        path = bundle / 'executions' / item['run_id'] / 'output/generated.csv'
        record.update(path=str(path), sha256=lifecycle.sha256(path), n_rows=2000)
    return record


def make_authorization(root, decision, parent_bundle, parent_run, destination, child_task_id):
    return {'schema_version': 1, 'authorization_id': 'c5_' + destination.replace('/', '_'),
            'destination': destination, 'max_extensions': 1,
            'parent': {'bundle': parent_bundle, 'run_id': parent_run,
                       'execution_sha256': lifecycle.sha256(root / parent_bundle / 'executions' / parent_run / 'execution.json')},
            'source': {'bundle': 'b/j', 'registry_sha256': lifecycle.sha256(root / 'b/j/registry.json')},
            'decision_sha256': adapter.digest(decision), 'child_task_id': child_task_id,
            'child_budget': {'source_queries': 0, 'source_downloads': 0, 'revisions': 0}}


def _run(root):
    plan = verify_plan(root)
    write_new(root / 'EXECUTION_STARTED.json', {'created_utc': now(), 'plan_sha256': lifecycle.sha256(root / 'RUN_PLAN.json')})
    decisions = lifecycle.read_json(root / 'author/request_decisions.json')['requests']
    add = next(x for x in decisions if x['request_id'] == '2')
    require(add['decision']['action'] == 'extend', 'Author did not authorize a scientific extension; stop without fabricating one')
    records = []
    for item in plan['runs']:
        verify_plan(root)
        try:
            if item['arm'] in {'parent', 'joint'}:
                bundle = root / ('b/p' if item['arm'] == 'parent' else 'b/j')
                execution.run_candidate(bundle, 'candidates/c0', item['run_id'], item['seed'])
            else:
                require(all(r['status'] == 'success' for r in records), 'Earlier failure blocks extension')
                destination = 't/e' + str(item['replicate'])
                authorization = make_authorization(root, add['decision'], 'b/p', item['parent_run_id'],
                                                   destination, 'c5_extend_' + str(item['replicate']))
                adapter.prepare_transition(root, destination, raw_request=add['raw_request'], decision=add['decision'],
                                           authorization=authorization, authorization_sha256=adapter.digest(authorization))
                bundle = root / destination / 'child'
                candidate = bundle / 'candidates/c0'
                candidate.mkdir(parents=True)
                for name in SCIENCE_FILES:
                    (candidate / name).write_bytes((root / 'author/extension' / name).read_bytes())
                    require(lifecycle.sha256(candidate / name) == plan['bindings']['author/extension/' + name],
                            'Extension scientific bytes changed')
                lifecycle.freeze_candidate(bundle, 'candidates/c0')
                transition_sha256 = lifecycle.sha256(root / destination / 'transition.json')
                adapter.execute_extension(root, destination, transition_sha256=transition_sha256,
                                          candidate='candidates/c0', run_id=item['run_id'], seed=item['seed'])
                adapter.verify_preservation(root, destination, item['run_id'], transition_sha256=transition_sha256)
            result = record_execution(bundle, item)
        except Exception as error:
            result = {**item, 'status': 'controller_or_execution_failure', 'error_type': type(error).__name__, 'error': str(error)}
            if 'bundle' in locals() and (bundle / 'executions' / item['run_id'] / 'execution.json').is_file():
                result['execution_sha256'] = lifecycle.sha256(bundle / 'executions' / item['run_id'] / 'execution.json')
        records.append(result)
        write_new(root / 'run_records' / (item['run_id'] + '.json'), result)
        print(json.dumps({'run_id': item['run_id'], 'status': result['status']}), flush=True)
        if result['status'] != 'success':
            remaining = [{**x, 'status': 'not_attempted_after_failure', 'failed_dependency': item['run_id']}
                         for x in plan['runs'][len(records):]]
            write_new(root / 'terminal_failure_manifest.json', {'created_utc': now(), 'records': records + remaining,
                       'analytic_truth_revealed': False, 'scientific_retries': 0})
            return {'status': 'closed_execution_failure', 'runs_attempted': len(records)}
    output_fields = ['run_id', 'arm', 'replicate', 'seed', 'parent_run_id', 'n_rows', 'path', 'sha256']
    manifest = {'schema_version': 1, 'fixture_id': 'c5_artificial_dynamic_extension', 'committed_utc': now(),
                'all_final_outputs_committed': True,
                'outputs': [{k: r[k] for k in output_fields} for r in records]}
    write_new(root / 'final_output_manifest.json', manifest)
    return {'status': 'nine_outputs_committed', 'manifest_sha256': lifecycle.sha256(root / 'final_output_manifest.json')}


def run(root):
    try:
        return _run(root)
    except Exception as error:
        # A preflight/integrity abort is not a completed nine-slot evaluation.
        # Never overwrite a prior abort, manufacture output or retry a started run.
        value = {'status': 'preflight_or_integrity_abort', 'created_utc': now(),
                 'error_type': type(error).__name__, 'error': str(error),
                 'execution_started_marker_exists': (root / 'EXECUTION_STARTED.json').exists(),
                 'existing_terminal_records': sorted(p.name for p in (root / 'run_records').glob('*.json')),
                 'analytic_reveal_authorized': False, 'requires_manual_closeout': True}
        path = root / 'CONTROLLER_ABORT.json'
        if not path.exists():
            write_new(path, value)
        return value


def route_only(root):
    verify_plan(root)
    require((root / 'final_output_manifest.json').is_file(), 'Final outputs must exist before using completed-table requests')
    requests = lifecycle.read_json(root / 'author/request_decisions.json')['requests']
    results = []
    for item in requests:
        if item['request_id'] == '2':
            continue
        require(item['decision']['action'] != 'extend', 'Only one extension request authorized')
        destination = 'routes/r' + item['request_id']
        auth = make_authorization(root, item['decision'], 't/e1/child', 'extended_r1', destination, 'c5_route_' + item['request_id'])
        result = adapter.prepare_transition(root, destination, raw_request=item['raw_request'], decision=item['decision'],
                                            authorization=auth, authorization_sha256=adapter.digest(auth))
        adapter.verify_transition(root, destination, transition_sha256=lifecycle.sha256(root / destination / 'transition.json'))
        require(result['child_bundle'] is None and not result['execution_permitted'], 'Route unexpectedly permits generation')
        results.append({'request_id': item['request_id'], 'action': result['action'], 'status': result['status'], 'generated_tables': 0})
    write_new(root / 'ROUTING_RESULTS.json', {'requests': results})
    return {'routing_results': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['seal', 'run', 'route'])
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    value = {'seal': seal, 'run': run, 'route': route_only}[args.phase](root)
    print(json.dumps(value))
