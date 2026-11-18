"""Read completed aggregate evaluations only; do not execute or rank constructors."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / 'request_only_agent_pilot_2026-11-10'


def summarize():
    old = json.loads((PREVIOUS / 'EVALUATION.json').read_text())
    new = json.loads((ROOT / 'EVALUATION.json').read_text())
    by_key = lambda payload: {(s['episode_id'], s['analysis_id']): s for s in payload['summaries']}
    before, after = by_key(old), by_key(new)
    assert set(before) == set(after)
    rows = []
    for key, b in before.items():
        a = after[key]
        assert a['reference'] == b['reference'] and a['unit'] == b['unit']
        rows.append(dict(episode_id=a['episode_id'], case_id=a['case_id'], arm=a['arm'],
                         analysis_id=a['analysis_id'], unit=a['unit'],
                         previous_available_seeds=b['available_seeds'],
                         repaired_available_seeds=a['available_seeds'],
                         previous_mean=b['mean'], repaired_mean=a['mean'],
                         reference=a['reference'].get('value'),
                         previous_mean_absolute_difference=b['mean_absolute_reference_difference'],
                         repaired_mean_absolute_difference=a['mean_absolute_reference_difference']))
    with (ROOT / 'ROUND_COMPARISON.csv').open('x', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summary = dict(
        previous_counts=old['counts'], repaired_counts=new['counts'],
        previous_costs=old['costs'], repaired_costs=new['costs'],
        combined_known_tariff_usd=old['costs']['known_tariff_usd']+new['costs']['known_tariff_usd'],
        input_hashes={str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in [PREVIOUS/'EVALUATION.json', ROOT/'EVALUATION.json']},
        interpretation='Fresh constructors and evidence choices; descriptive before/after only. '
                       'No paired causal repair effect, superiority test or independent clinical validation. '
                       'Unavailable analyses remain missing; no zero imputation or endpoint selection.',
        all_analysis_rows=rows)
    with (ROOT/'ROUND_COMPARISON.json').open('x', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, allow_nan=False)
    print(json.dumps({k: summary[k] for k in ['previous_counts','repaired_counts','combined_known_tariff_usd']}))


if __name__ == '__main__':
    summarize()
