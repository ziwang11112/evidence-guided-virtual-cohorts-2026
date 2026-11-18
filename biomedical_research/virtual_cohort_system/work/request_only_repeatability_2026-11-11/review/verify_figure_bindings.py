"""Read-only figure/data checks; writes only the independent QA record."""
from pathlib import Path
import csv
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

evaluation = json.loads((ROOT / 'EVALUATION.json').read_text(encoding='utf-8'))
rows = list(csv.DictReader((ROOT / 'figures/primary_analyses.csv').open(encoding='utf-8-sig', newline='')))
lookup = {(r['episode_id'], r['analysis_id']): r for r in evaluation['summaries']}
assert len(rows) == 36
checks = []
def check(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})
    assert condition, name

for row in rows:
    key = row['episode_id'], row['analysis_id']
    source = lookup[key]
    for field in ['case_id', 'arm', 'unit']:
        check(f'{key}:{field}', row[field] == source[field])
    check(f'{key}:available_seeds', int(row['available_seeds']) == source['available_seeds'] == 3)
    for field in ['mean', 'minimum', 'maximum', 'mean_absolute_reference_difference']:
        check(f'{key}:{field}', float(row[field]) == source[field])
    check(f'{key}:reference_value', float(row['reference_value']) == source['reference']['value'])
check('primary_unique_pairs', len({(r['episode_id'], r['analysis_id']) for r in rows}) == 36)
check('all_twelve_authors', len({r['episode_id'] for r in rows}) == 12)
check('all_six_primary_analyses', len({(r['case_id'], r['analysis_id']) for r in rows}) == 6)
check('all_final_slots_delivered', evaluation['counts']['successful_tables'] == evaluation['counts']['final_slots'] == 36)
check('all_model_calls', sum(r['calls_reserved'] for r in evaluation['episodes']) == evaluation['counts']['model_calls'] == 331)
check('known_cost', abs(sum(r['known_tariff_cost_usd'] for r in evaluation['episodes']) - evaluation['costs']['known_tariff_usd']) < 1e-12)
check('no_unknown_usage', sum(r['unknown_usage_calls'] for r in evaluation['episodes']) == 0)

files = [ROOT / 'figures' / (name + ext)
         for name in ['primary_analyses', 'delivery_resources']
         for ext in ['.pdf', '.png', '.svg']]
files += [ROOT / 'review/figure_renders' / (name + '.png')
          for name in ['primary_analyses', 'delivery_resources']]
record = {
    'completed_utc': datetime.now(timezone.utc).isoformat(),
    'reviewer': '/root/repeatability_figure_qa',
    'status': 'PASS',
    'numeric_checks_passed': len(checks),
    'checks': checks,
    'evaluation_sha256': sha(ROOT / 'EVALUATION.json'),
    'files': {str(p.relative_to(ROOT)): sha(p) for p in files},
    'actual_pdf_renderer': 'Poppler pdftoppm; 160 dpi; each actual PDF rendered to a PNG',
    'visual_inspection': {
        'actual_pdf_renders_seen': 2,
        'original_pngs_seen': 2,
        'clipped_text': False,
        'overlapping_elements': False,
        'unreadable_glyphs': False,
        'axes_and_units_legible': True,
        'all_authors_and_analyses_present': True,
        'seed_and_scenario_variation_caveat_present': True,
        'reference_uncertainty_not_equivalence_claim': True,
        'resource_axes_start_at_zero': True,
        'delivery_not_scientific_validity': True,
    },
    'recommendations': [],
    'resolved_recommendation': 'Four BMI arrow titles were replaced with explicit association labels by the root; both latest actual PDFs were rerendered and inspected, along with both latest original PNGs.',
    'scope': 'Aggregate plotting and rendered artifacts only. No API calls, generator execution, patient rows, new sources or modifications to production artifacts.',
}
(ROOT / 'review/FIGURE_VISUAL_REVIEW.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps({'status': record['status'], 'numeric_checks': len(checks)}))
