"""Versioned evidence -> initial generator -> review -> revision control.

Owns schemas, provenance, state transitions and numerical output contracts only.
No biological dependence or parameters are implemented here. Static source
checks are defense in depth, NOT an execution sandbox.
"""
from __future__ import annotations
import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True, allow_nan=False)
        stream.write('\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_relative(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    require(path.is_relative_to(root), 'Path outside assigned run')
    return path


def validate_ledger(ledger):
    require(isinstance(ledger, dict) and isinstance(ledger.get('sources'), list) and ledger['sources'], 'Ledger needs nonempty sources list')
    require(isinstance(ledger.get('evidence'), list) and ledger['evidence'], 'Ledger needs nonempty evidence list')
    ids = [s.get('id') for s in ledger['sources']]
    require(all(isinstance(x, str) and x for x in ids) and len(ids) == len(set(ids)), 'Source IDs invalid')
    for source in ledger['sources']:
        for key in ['id', 'identifier', 'population', 'measurement', 'cohort_overlap', 'approved_artifacts']:
            require(key in source, 'Source field missing: ' + key)
        require(isinstance(source['approved_artifacts'], list) and source['approved_artifacts'], 'Approved source artifacts required')
    evidence_ids = []
    for item in ledger['evidence']:
        for key in ['id', 'source_id', 'locator', 'estimand', 'variables', 'adjustment', 'reported', 'uncertainty', 'applicability', 'model_use', 'bridge_assumptions']:
            require(key in item, 'Evidence field missing: ' + key)
        require(item['source_id'] in ids, 'Unknown source ID')
        require(isinstance(item['id'], str) and item['id'], 'Invalid evidence ID')
        evidence_ids.append(item['id'])
    require(len(evidence_ids) == len(set(evidence_ids)), 'Duplicate evidence ID')
    return set(ids), set(evidence_ids)


def validate_spec(spec, evidence_ids):
    parameters, provenance = spec.get('parameters'), spec.get('parameter_provenance')
    require(isinstance(parameters, dict) and parameters, 'Nonempty parameters dict required')
    require(isinstance(provenance, dict) and set(provenance) == set(parameters), 'Provenance keys must match parameter keys')
    assumptions = spec.get('assumptions')
    require(isinstance(assumptions, list), 'Assumptions list required')
    ids = []
    for assumption in assumptions:
        require(isinstance(assumption, dict) and isinstance(assumption.get('id'), str) and assumption['id'], 'Typed assumption ID required')
        require(isinstance(assumption.get('description'), str) and assumption['description'].strip(), 'Assumption description required')
        ids.append(assumption['id'])
    require(len(ids) == len(set(ids)), 'Duplicate assumption ID')
    for item in provenance.values():
        require(isinstance(item, dict), 'Typed parameter provenance required')
        for key in ['evidence_ids', 'assumption_ids']:
            require(isinstance(item.get(key), list), 'Provenance reference list required')
        require(item['evidence_ids'] or item['assumption_ids'], 'Parameter has no evidence or assumption link')
        require(set(item['evidence_ids']) <= evidence_ids, 'Unknown evidence reference')
        require(set(item['assumption_ids']) <= set(ids), 'Unknown assumption reference')
        require(isinstance(item.get('derivation'), str) and item['derivation'].strip(), 'Parameter derivation missing')


def gateway_registry(cfg):
    session = Path(cfg['literature_session'])
    state = read(session/'state.json')
    require(state['session_path'] == str(session.resolve()), 'Wrong literature session')
    require(state['config_sha256'] == sha(cfg['gateway_config']), 'Gateway config changed')
    data = (session/'audit.jsonl').read_bytes()
    registry = set()
    for line in data.splitlines():
        event = json.loads(line)
        if event.get('type') == 'artifact_approved' and event.get('status') == 'accepted':
            require(event.get('config_sha256') == state['config_sha256'], 'Wrong approved artifact config')
            artifact = event['artifact']
            p = checked_relative(session, artifact['session_relative_path'])
            registry.add((str(p), artifact['sha256']))
    return registry, {'session': str(session), 'config_sha256': state['config_sha256'],
        'audit_bytes': len(data), 'audit_prefix_sha256': hashlib.sha256(data).hexdigest(), 'usage': state['usage']}


def verify_gateway_snapshot(path):
    snapshot = read(path)
    data = (Path(snapshot['session'])/'audit.jsonl').read_bytes()
    require(len(data) >= snapshot['audit_bytes'] and hashlib.sha256(data[:snapshot['audit_bytes']]).hexdigest() == snapshot['audit_prefix_sha256'], 'Gateway audit history changed')


def validate_gaps(gaps, final=False):
    require(isinstance(gaps, list) and gaps, 'Gap policy requires nonempty gap records')
    ids = []
    for gap in gaps:
        for key in ['id', 'component', 'affected_analysis', 'evidence_status', 'consequence', 'next_action', 'status', 'resolution']:
            require(key in gap, 'Gap field missing: ' + key)
        require(gap['status'] in ['open', 'acted', 'resolved', 'unresolved', 'not_applicable'], 'Invalid gap status')
        require(isinstance(gap['id'], str) and gap['id'], 'Invalid gap ID')
        ids.append(gap['id'])
        if final:
            require(gap['status'] != 'open', 'Final gap requires explicit disposition')
            require(isinstance(gap['resolution'], str) and gap['resolution'].strip(), 'Final gap resolution required')
    require(len(ids) == len(set(ids)), 'Duplicate gap ID')


def validate_actions(actions, gaps, final=False):
    require(isinstance(actions, list) and actions, 'Gap policy requires action history')
    ids = {g['id'] for g in gaps}
    for action in actions:
        for key in ['gap_id', 'action', 'evidence_artifacts', 'model_change', 'reason']:
            require(key in action, 'Action field missing: ' + key)
        require(action['gap_id'] in ids, 'Action uses unknown gap')
        require(action['action'] in ['retrieve', 'reextract', 'source_check', 'revise', 'sensitivity', 'retain', 'stop'], 'Unsupported action')
        require(isinstance(action['reason'], str) and action['reason'].strip(), 'Action reason missing')
        require(isinstance(action['evidence_artifacts'], list), 'Evidence artifact list required')
        if action['action'] == 'retrieve':
            require(action['evidence_artifacts'], 'Retrieval claim requires actual artifact')
    if final:
        acted = {a['gap_id'] for a in actions}
        require(all(g['id'] in acted for g in gaps if g['status'] != 'not_applicable'), 'Final gap has no linked action or justified stop')


def source_check(path):
    """Conservative static check, followed by independent human/Agent review."""
    tree = ast.parse(Path(path).read_text(encoding='utf-8-sig'))
    allowed_imports = {'numpy', 'pandas', 'scipy', 'math', 'statistics', 'typing', '__future__'}
    blocked_names = {'open', 'exec', 'eval', 'compile', '__import__', 'input', 'breakpoint', 'getattr', 'setattr', 'globals', 'locals', 'vars'}
    blocked_attrs = {'read_csv', 'read_table', 'read_pickle', 'read_json', 'read_excel', 'read_parquet', 'to_csv', 'to_pickle', 'to_json', 'load', 'save', 'fromfile', 'tofile', 'memmap', 'read_text', 'read_bytes', 'write_text', 'write_bytes'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            require(all(x.name.split('.')[0] in allowed_imports for x in node.names), 'Unapproved import')
        if isinstance(node, ast.ImportFrom):
            require(node.level == 0 and (node.module or '').split('.')[0] in allowed_imports, 'Unapproved import-from')
        if isinstance(node, ast.Name):
            require(node.id not in blocked_names, 'Blocked dynamic/file function')
        if isinstance(node, ast.Attribute):
            require(not node.attr.startswith('__') and node.attr not in blocked_attrs, 'Blocked attribute/file access')
    require(any(isinstance(n, ast.FunctionDef) and n.name == 'generate' for n in tree.body), 'generate function missing')
    return {'static_check': 'pass', 'scope': 'Conservative AST checks; not a sandbox or proof of no side effects'}


def file_commitment(paths):
    return {str(Path(p).resolve()): sha(p) for p in paths}


def verify_commitment(manifest):
    for path, value in manifest.items():
        require(Path(path).is_file() and sha(path) == value, 'Committed file changed: ' + path)


def init(run, policy, observed, contract, protocol):
    run = Path(run).resolve()
    require(policy in ['ordinary', 'gap_policy'], 'Invalid policy')
    require(not (run/'run.json').exists(), 'Run already initialized')
    tool_dir = Path(__file__).resolve().parent/'tools'
    study = tool_dir.parent
    prompt_paths = [study/'BUILDER_GUIDE.md', study/'policies'/f'{policy}.md', run/'REQUEST.md', study/'shared/schema.json', study/'shared/target_description.md']
    write_new(run/'run.json', {'created_utc': now(), 'policy': policy, 'observed': str(Path(observed).resolve()),
        'contract': str(Path(contract).resolve()), 'protocol': str(Path(protocol).resolve()),
        'literature_session': str(run/'literature'), 'gateway_config': str(tool_dir/'gateway_config.json'),
        'commitment': file_commitment([observed, contract, protocol, __file__, tool_dir/'literature_gateway.py', tool_dir/'gateway_config.json'] + prompt_paths)})


def freeze_candidate(run, version):
    run = Path(run).resolve()
    require(version in ['initial', 'final'], 'Invalid version')
    cfg = read(run/'run.json')
    verify_commitment(cfg['commitment'])
    if version == 'final':
        require((run/'review_receipt.json').exists(), 'Final submission requires prior review')
        verify_commitment(read(run/'initial/freeze.json')['commitment'])
        verify_commitment(read(run/'review_receipt.json')['commitment'])
        verify_gateway_snapshot(run/'initial/gateway_snapshot.json')
    folder = run/version
    files = [folder/x for x in ['generator.py', 'model_spec.json', 'evidence.json', 'decision.md']]
    require(all(p.is_file() for p in files), 'Missing candidate artifact')
    ledger = read(folder/'evidence.json')
    _, evidence_ids = validate_ledger(ledger)
    source_check(folder/'generator.py')
    spec = read(folder/'model_spec.json')
    validate_spec(spec, evidence_ids)
    registry, snapshot = gateway_registry(cfg)
    linked = []
    for source in ledger['sources']:
        for artifact in source['approved_artifacts']:
            p = checked_relative(run, artifact['path'])
            require('approved' in p.parts and p.is_file() and sha(p) == artifact['sha256'], 'Invalid approved evidence commitment')
            require((str(p), artifact['sha256']) in registry, 'Evidence artifact not registered by gateway')
            linked.append(p)
    if cfg['policy'] == 'gap_policy':
        gaps = read(folder/'gaps.json')
        validate_gaps(gaps, final=version == 'final')
        files.append(folder/'gaps.json')
        actions = read(folder/'actions.json')
        validate_actions(actions, gaps, final=version == 'final')
        files.append(folder/'actions.json')
        for action in actions:
            for artifact in action['evidence_artifacts']:
                p = checked_relative(run, artifact['path'])
                require('approved' in p.parts and p.is_file() and sha(p) == artifact['sha256'], 'Action evidence artifact invalid')
                require((str(p), artifact['sha256']) in registry, 'Action artifact not registered by gateway')
                linked.append(p)
    if version == 'final':
        revision = read(folder/'revision.json')
        require(isinstance(revision.get('reason'), str) and revision['reason'].strip(), 'Revision/no-op reason required')
        changed = any(sha(run/'initial'/n) != sha(folder/n) for n in ['generator.py', 'model_spec.json'])
        require(revision.get('generator_or_spec_changed') is changed, 'Revision change claim disagrees with file hashes')
        files.append(folder/'revision.json')
    write_new(folder/'gateway_snapshot.json', snapshot)
    paths = files + linked + [folder/'gateway_snapshot.json']
    receipt = {'created_utc': now(), 'version': version, 'policy': cfg['policy'],
        'commitment': file_commitment(paths), 'run_commitment': cfg['commitment'],
        'run_sha256': sha(run/'run.json'),
        'static_check': source_check(folder/'generator.py'), 'scientific_claim': 'Submission accepted structurally; analytical validity not inferred'}
    write_new(folder/'freeze.json', receipt)
    return receipt


def record_review(run, review):
    run = Path(run).resolve()
    require((run/'initial/freeze.json').exists(), 'Review follows initial freeze')
    verify_commitment(read(run/'initial/freeze.json')['commitment'])
    obj = read(review)
    require(isinstance(obj.get('findings'), list) and isinstance(obj.get('summary'), str), 'Invalid review structure')
    require(isinstance(obj.get('execution_allowed'), bool), 'Review execution decision missing')
    for key, relative in [('generator_sha256','initial/generator.py'), ('model_spec_sha256','initial/model_spec.json'), ('evidence_sha256','initial/evidence.json'), ('candidate_freeze_sha256','initial/freeze.json')]:
        require(obj.get(key) == sha(run/relative), 'Review hash mismatch: '+key)
    write_new(run/'review_receipt.json', {'created_utc': now(), 'commitment': file_commitment([review, run/'initial/freeze.json']),
        'execution_allowed': obj['execution_allowed'], 'no_reference_feedback': True})


def frame(path):
    return pd.read_csv(path, dtype={'row_id': str}, float_precision='round_trip')


def output_check(observed, enriched, contract):
    columns = contract['observed_columns']
    added = contract['generated_columns']
    require(isinstance(enriched, pd.DataFrame), 'Generator did not return a frame')
    require(list(observed.columns) == columns and list(enriched.columns) == columns + [x['name'] for x in added], 'Output schema changed')
    require(len(enriched) == len(observed), 'Row count changed')
    require(observed.row_id.is_unique and observed.row_id.notna().all(), 'Bad row identifiers')
    pd.testing.assert_frame_equal(observed.reset_index(drop=True), enriched[columns].reset_index(drop=True), check_dtype=False, check_exact=True)
    for item in added:
        values = enriched[item['name']].to_numpy(float)
        require(np.isfinite(values).all(), 'Nonfinite generated values')
        if 'min_exclusive' in item:
            require((values > item['min_exclusive']).all(), 'Generated values outside contract')


def rng_equal(a, b):
    return a[0] == b[0] and np.array_equal(a[1], b[1]) and a[2:] == b[2:]


def execute(run, version):
    run = Path(run).resolve()
    cfg, frozen = read(run/'run.json'), read(run/version/'freeze.json')
    verify_commitment(cfg['commitment'])
    verify_commitment(frozen['commitment'])
    require(frozen['run_sha256'] == sha(run/'run.json'), 'Run receipt changed')
    verify_gateway_snapshot(run/version/'gateway_snapshot.json')
    require((run/'review_receipt.json').exists(), 'Independent review required before executing any submitted code')
    review = read(run/'review_receipt.json')
    verify_commitment(review['commitment'])
    require(review['execution_allowed'], 'Review contains execution-blocking issue')
    if version == 'final':
        require((run/'final_code_review.json').exists(), 'Final source/code review required')
        final_review = read(run/'final_code_review.json')
        require(final_review.get('execution_allowed') is True, 'Final code review blocks execution')
        require(final_review.get('generator_sha256') == sha(run/'final/generator.py'), 'Final review does not bind current code')
        require(final_review.get('model_spec_sha256') == sha(run/'final/model_spec.json'), 'Final review does not bind current specification')
        require(final_review.get('evidence_sha256') == sha(run/'final/evidence.json'), 'Final review does not bind evidence')
        require(final_review.get('candidate_freeze_sha256') == sha(run/'final/freeze.json'), 'Final review does not bind freeze receipt')
    destination = run/version/'outputs'
    require(not destination.exists(), 'Preserve prior execution')
    destination.mkdir()
    observed, contract = frame(cfg['observed']), read(cfg['contract'])
    spec = read(run/version/'model_spec.json')
    protocol = read(cfg['protocol'])
    rng = np.random.get_state()
    started = time.perf_counter()
    try:
        modspec = importlib.util.spec_from_file_location('candidate_' + run.name + '_' + version, run/version/'generator.py')
        module = importlib.util.module_from_spec(modspec)
        modspec.loader.exec_module(module)
        require(rng_equal(rng, np.random.get_state()), 'Import altered global RNG')
        records, generated_hashes = [], []
        for number, seed in enumerate(protocol['generation_seeds'], 1):
            def call():
                copied, settings = observed.copy(deep=True), copy.deepcopy(spec)
                result = module.generate(copied, settings, seed)
                pd.testing.assert_frame_equal(copied, observed, check_exact=True)
                require(settings == spec, 'Specification mutated')
                require(rng_equal(rng, np.random.get_state()), 'Global RNG mutated')
                output_check(observed, result, contract)
                return result
            enriched = call()
            if number == 1:
                pd.testing.assert_frame_equal(enriched, call(), check_exact=True)
            path = destination/f'draw_{number:02d}.csv'
            enriched.to_csv(path, index=False, float_format='%.17g')
            reread = frame(path)
            output_check(observed, reread, contract)
            for item in contract['generated_columns']:
                require(np.array_equal(enriched[item['name']].to_numpy(float), reread[item['name']].to_numpy(float)), 'Generated value round-trip changed')
            records.append({'seed': seed, 'path': str(path), 'sha256': sha(path), 'n_rows': len(enriched)})
            generated_hashes.append(hashlib.sha256(enriched[[x['name'] for x in contract['generated_columns']]].to_numpy(float).tobytes()).hexdigest())
        require(len(set(generated_hashes)) > 1, 'All draws identical; conditional variability absent')
        verify_commitment(cfg['commitment'])
        verify_commitment(frozen['commitment'])
        result = {'created_utc': now(), 'elapsed_seconds': time.perf_counter()-started, 'version': version,
            'draws': records, 'controller_sha256': sha(__file__), 'candidate_freeze_sha256': sha(run/version/'freeze.json'),
            'review_receipt_sha256': sha(run/'review_receipt.json'), 'final_code_review_sha256': sha(run/'final_code_review.json') if version == 'final' else None,
            'run_sha256': sha(run/'run.json'), 'unique_generated_vectors': len(set(generated_hashes)),
            'observed_cells_preserved': True, 'same_seed_reproducible': True,
            'scope': 'Residual draws of one Agent construction; target reference never read by controller'}
        write_new(destination/'execution.json', result)
        return result
    except Exception as exc:
        write_new(destination/'failure.json', {'created_utc': now(), 'type': type(exc).__name__, 'message': str(exc)})
        raise
    finally:
        np.random.set_state(rng)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init')
    for name in ['run', 'policy', 'observed', 'contract', 'protocol']:
        p.add_argument('--'+name, required=True)
    p = sub.add_parser('freeze')
    p.add_argument('--run', required=True); p.add_argument('--version', required=True, choices=['initial','final'])
    p = sub.add_parser('review')
    p.add_argument('--run', required=True); p.add_argument('--file', required=True)
    p = sub.add_parser('execute')
    p.add_argument('--run', required=True); p.add_argument('--version', required=True, choices=['initial','final'])
    args = parser.parse_args()
    if args.command == 'init':
        init(args.run, args.policy, args.observed, args.contract, args.protocol); result = {'initialized': args.run}
    elif args.command == 'freeze':
        result = freeze_candidate(args.run, args.version)
    elif args.command == 'review':
        record_review(args.run, args.file); result = {'review_recorded': args.run}
    else:
        result = execute(args.run, args.version)
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
