"""Bind feasibility inputs before outcome access; never deserialize outcomes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

P = Path(__file__).resolve().parents[2]
S = P / 'work/analysis-utility-preparation-2026-10-29'
O = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    active = json.loads((S / 'ACTIVE_PROTOCOL.json').read_text())
    campaign = S / active['active_campaign']
    assert sha(campaign) == active['sha256']
    checked = {}
    for case in ['nhanes_insulin', 'pns_hba1c']:
        b = S / 'bundles' / case
        m = json.loads((b / 'input_manifest.json').read_text())
        for rel, expected in m['files'].items():
            assert sha(b / rel) == expected, (case, rel)
        checked[case] = {'input_manifest_sha256': sha(b / 'input_manifest.json'),
                         'files_verified': len(m['files']),
                         'source_search': 'Previously curated external evidence; no new retrieval by builders'}
    bind = [S / 'ACTIVE_PROTOCOL.json', campaign, S / 'prompts/feasibility.md',
            S / 'methods/analytical_points.py', P / 'work/m2-runtime-config.json']
    bind += [S / 'protocols' / (c + '.json') for c in ['nhanes_insulin','pns_hba1c','endpoint_evidence_map']]
    bind += sorted((P / 'cohort_harness').glob('*.py'))
    data = {
        'schema_version': 'm10-launch-1', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'primary_claim': 'Feasibility and scientific analytical utility of evidence-guided virtual data',
        'ordinary_agent_competitor_required': False,
        'construction_schedule': [{'case_id': c, 'construction_id': k, 'bundle_path': str(O/k)}
                                  for c,k in [('nhanes_insulin','ia'),('nhanes_insulin','ib'),
                                              ('pns_hba1c','ha'),('pns_hba1c','hb')]],
        'residual_seeds': [92101,92102,92103], 'expected_final_tables': 12,
        'source_replay_seeds': [91101,91102,91103],
        'construction_separation': 'Fresh-context subagents (fork_turns=none); procedural allowlist only; not filesystem isolation',
        'model_metadata': {'provider_environment': 'Codex collaboration runtime',
                           'settings': 'Inherited caller model and reasoning settings; no override',
                           'exact_backend_identifier': None,
                           'reason_exact_identifier_unavailable': 'No verified per-subagent backend identifier supplied by runtime',
                           'token_usage': None, 'cost': None},
        'generation_execution': 'Existing WSL/bubblewrap adapter only, with frozen candidates; no local fallback',
        'controller_outcomes_read_at_launch': False,
        'evaluation_rule': 'Freeze all four constructions and all scheduled generation receipts before reserved real outcome analysis; no feedback to builders',
        'selection_rule': 'Each builder must record its source-only rule before source diagnostics and final selection before target execution; retain every construction',
        'limits': {'candidate_versions': 3, 'revisions': 2, 'literature_queries': 0, 'literature_downloads': 0},
        'inputs': checked,
        'bindings': [{'path': str(p), 'sha256': sha(p)} for p in bind],
        'historical_protocol': 'M9 original30-table schedule preserved but superseded; common.md dispatch status is historical',
        'limitations': ['No claim of independence from model pretraining',
                       'Two model constructions are not independent biological cohorts',
                       'Three residual draws do not estimate evidence uncertainty',
                       'No numerical equivalence margin or overall superiority criterion invented after results']
    }
    dest = O / 'launch.json'
    with dest.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(json.dumps({'path': str(dest), 'sha256': sha(dest), 'inputs': checked}))

if __name__ == '__main__':
    main()
