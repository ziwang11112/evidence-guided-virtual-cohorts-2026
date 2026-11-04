"""Bind unchanged v0.7 figures to existing aggregate reports; never reads row tables."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
PROJECT = OUT.parents[1]
STORY = PROJECT / 'manuscript/story_package_2026-11-03'
UTILITY = PROJECT / 'manuscript/utility_package_2026-11-03'


def project_source(relative):
    """Resolve local work/ or public reports/ layout, then verify hashes normally.

    An existing requested path always wins. A content/hash mismatch must fail;
    it must never trigger a search for another copy that happens to match.
    """
    relative = Path(relative)
    candidates = [PROJECT / relative]
    if relative.parts and relative.parts[0] in {'work', 'reports'}:
        alternate = 'reports' if relative.parts[0] == 'work' else 'work'
        candidates.append(PROJECT / alternate / Path(*relative.parts[1:]))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError('No source found in the explicit layouts: ' +
                            ', '.join(str(path) for path in candidates))


HRS = project_source('work/hrs_public_example_2026-11-03')

# Two historical public JSON exports changed only CRLF to LF. These exact pairs
# were checked against parsed local/export equality and the original-byte manifest.
# This is a documented byte transformation, not alternate-source selection.
PUBLIC_CRLF_EXPORTS = {
    'reports/information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json': {
        'original_sha256': 'd64b7cd5bd1097a4ea51b84b00a3721d54c092cc87db85da9418bdd24bd187a0',
        'export_sha256': '6f55901630fc0a0e5071b8e878d53230255c8c68b8d42f302a7f2cf842a36a9f',
    },
    'reports/information_revision_ablation_2026-11-03/INDEPENDENT_RECOMPUTE.json': {
        'original_sha256': '9e36d2e746b21f5c948a5d7f87090cf5a9dd00c81fe34c1feed33725de8d6961',
        'export_sha256': 'e051a2b590c365ff6faef721ba2232aea404c249eddd7c6ba49a6d6bc40264fb',
    },
}
SOURCE_BYTE_EQUIVALENCES = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify_source_digest(path, expected):
    actual = digest(path)
    if actual == expected:
        return
    relative = path.relative_to(PROJECT).as_posix()
    mapping = PUBLIC_CRLF_EXPORTS.get(relative)
    assert mapping and expected == mapping['original_sha256'] and actual == mapping['export_sha256'], (
        f'Source hash mismatch for {relative}: expected {expected}; observed {actual}')
    exported = path.read_bytes()
    assert b'\r' not in exported, 'Pinned public JSON must use LF line endings only'
    original_bytes = exported.replace(b'\n', b'\r\n')
    assert hashlib.sha256(original_bytes).hexdigest() == expected
    assert json.loads(exported) == json.loads(original_bytes)
    public_manifest = path.parent / 'PUBLIC_PACKAGE_MANIFEST.json'
    matches = [item for item in read_json(public_manifest)['files']
               if item['export'] == path.name]
    assert len(matches) == 1
    assert matches[0]['original_sha256'] == expected
    assert matches[0]['original_bytes'] == len(original_bytes)
    SOURCE_BYTE_EQUIVALENCES[relative] = {
        'path': relative, 'original_audited_sha256': expected, 'export_sha256': actual,
        'transformation': 'CRLF to LF only; reversible original-byte hash and parsed JSON equality verified',
        'public_original_byte_manifest': public_manifest.relative_to(PROJECT).as_posix(),
        'public_original_byte_manifest_sha256': digest(public_manifest),
    }


def record(path):
    return {'path': path.relative_to(PROJECT).as_posix(),
            'sha256': digest(path), 'bytes': path.stat().st_size}


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def resolve_pointer(document, pointer):
    item = document
    for segment in pointer.strip('/').split('/'):
        key = segment.replace('~1', '/').replace('~0', '~')
        item = item[int(key)] if isinstance(item, list) else item[key]
    return item


def main():
    SOURCE_BYTE_EQUIVALENCES.clear()
    story_manifest = read_json(STORY / 'DISPLAY_PROVENANCE.json')
    utility_manifest = read_json(UTILITY / 'NUMERIC_MANIFEST.json')
    hrs_manifest = read_json(HRS / 'figures/FIGURE_MANIFEST.json')
    utility_data = read_json(UTILITY / 'AGGREGATE_SOURCE.json')
    main_report = project_source(utility_manifest['sources']['main']['path'])
    main_audit_path = project_source(utility_manifest['sources']['main_audit']['path'])
    historical_report = project_source(utility_manifest['sources']['historical']['path'])
    historical_audit_path = project_source(utility_manifest['sources']['historical_audit']['path'])
    main_data, historical_data = read_json(main_report), read_json(historical_report)
    hrs_data = read_json(HRS / 'summary/AGGREGATE_RESULTS.json')
    hrs_audit = read_json(HRS / 'FINAL_RESULT_REVIEW.json')
    verify_source_digest(main_report, read_json(main_audit_path)['result_sha256'])
    verify_source_digest(historical_report, read_json(historical_audit_path)['report_sha256'])
    assert hrs_audit['status'] == 'pass'
    hrs_audit_bindings = {r['path'].replace('\\', '/'): r['sha256'] for r in hrs_audit['bindings']}
    assert hrs_audit_bindings['summary/AGGREGATE_RESULTS.json'] == digest(HRS / 'summary/AGGREGATE_RESULTS.json')
    for item in utility_manifest['sources'].values():
        verify_source_digest(project_source(item['path']), item['sha256'])
    assert digest(UTILITY / 'AGGREGATE_SOURCE.json') == utility_manifest['outputs']['AGGREGATE_SOURCE.json']['sha256']

    # Verify every retained cross-sectional seed against the exact original pointer.
    # This is aggregate-value identity checking, not new statistical analysis.
    checks = {}
    for name, document in [('main_experiment', main_data), ('historical_information_experiment', historical_data)]:
        panels = utility_data[name]['panels']
        seed_count = 0
        series_count = 0
        for panel in panels:
            for series in panel['series']:
                series_count += 1
                assert len(series['seeds']) == 3
                for point in series['seeds']:
                    assert point['value'] == resolve_pointer(document, point['pointer'])
                    seed_count += 1
        checks[name] = {'panels': len(panels), 'seed_statistics': seed_count,
                        'constructor_mean_markers': series_count}
    assert checks['main_experiment']['seed_statistics'] == 216
    assert checks['historical_information_experiment']['seed_statistics'] == 90
    assert main_data['planned_constructions'] == 24
    assert main_data['scheduled_final_slots'] == main_data['unique_successful_table_contents'] == 72
    assert historical_data['attempts'] == 42
    assert historical_data['distinct_table_hashes'] == 24
    assert hrs_data['counts']['valid_comparison_tables'] == 6
    assert hrs_data['counts']['total_physical_generations'] == 9
    assert hrs_data['counts']['invalid_initial_comparator_tables'] == 3

    figures = [
        ('Figure 1', 'fig1_method', STORY, 'figure1-evidence-to-analysis.drawio', 'method_schematic', None),
        ('Figure 2', 'fig2_external_evidence', UTILITY, 'figure1_main_scientific_utility', 'aggregate_data_plot', 'main_experiment'),
        ('Figure 3', 'fig3_summary_assisted', UTILITY, 'figure2_chns_information_conditions', 'aggregate_data_plot', 'historical_information_experiment'),
        ('Figure 4', 'fig4_longitudinal', HRS, 'focal_longitudinal_relationships', 'aggregate_data_plot', 'hrs_focal'),
        ('Figure S1', 'figS1_longitudinal_all_effects', HRS, 'all_16_fixed_effects', 'aggregate_data_plot', 'hrs_all_fixed_effects'),
    ]
    (OUT / 'figures').mkdir(exist_ok=True)
    (OUT / 'data').mkdir(exist_ok=True)
    bindings = []
    for number, stem, origin, source_stem, identity, data_key in figures:
        asset_bindings = []
        for ext in ['svg', 'png']:
            source = origin / 'figures' / (source_stem + '.' + ext)
            target = OUT / 'figures' / (stem + '.' + ext)
            if origin == STORY:
                expected = story_manifest['outputs']['figures/' + source.name]
            elif origin == UTILITY:
                expected = utility_manifest['outputs']['figures/' + source.name]['sha256']
            else:
                expected = hrs_manifest['files'][source.name]
            assert digest(source) == expected, source
            shutil.copyfile(source, target)
            assert source.read_bytes() == target.read_bytes()
            asset_bindings.append({'source': record(source), 'copy': record(target), 'byte_identical': True})
        bindings.append({'number': number, 'stem': stem, 'production_identity': identity,
                         'aggregate_key': data_key, 'operation': 'unchanged byte copy',
                         'assets': asset_bindings})

    copy_data = [
        (UTILITY / 'AGGREGATE_SOURCE.json', 'cross_sectional_aggregate_source.json'),
        (HRS / 'summary/fixed_effects_all_seeds.csv', 'hrs_all_fixed_effects.csv'),
        (HRS / 'summary/fixed_effects_summary.csv', 'hrs_fixed_effect_summary.csv'),
        (HRS / 'summary/distributions_summary.csv', 'hrs_distribution_summary.csv'),
    ]
    data_bindings = []
    for source, filename in copy_data:
        if source.is_relative_to(HRS):
            assert hrs_audit_bindings[source.relative_to(HRS).as_posix()] == digest(source)
        target = OUT / 'data' / filename
        shutil.copyfile(source, target)
        assert digest(source) == digest(target)
        data_bindings.append({'source': record(source), 'copy': record(target), 'byte_identical': True})

    hrs_rows = read_csv(HRS / 'summary/fixed_effects_all_seeds.csv')
    assert len(hrs_rows) == 96 and len({r['term'] for r in hrs_rows}) == 16
    assert {r['arm'] for r in hrs_rows} == {'native', 'agent'}
    assert {r['seed'] for r in hrs_rows} == {'6101', '6102', '6103'}
    assert digest(HRS / hrs_manifest['input']['path']) == hrs_manifest['input']['sha256']
    focal_terms = ['age60:hba1c_U65', 'age60:hba1c_O65']
    selected = [r for r in hrs_rows if r['term'] in focal_terms]
    assert len(selected) == 12
    focal_path = OUT / 'data/hrs_focal_plotted_values.csv'
    with focal_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(hrs_rows[0]))
        writer.writeheader()
        writer.writerows(selected)
    assert read_csv(focal_path) == selected
    summaries = read_csv(HRS / 'summary/fixed_effects_summary.csv')
    distributions = read_csv(HRS / 'summary/distributions_summary.csv')
    assert len(summaries) == 32 and len(distributions) == 54
    checks['hrs'] = {'focal_seed_estimates': 12, 'focal_source_estimates': 2,
                     'all_effect_seed_estimates': 96, 'all_effect_mean_markers': 32,
                     'distribution_summary_rows': 54, 'distribution_metrics_per_arm': 27}

    source_paths = [STORY / 'DISPLAY_PROVENANCE.json', UTILITY / 'NUMERIC_MANIFEST.json',
                    HRS / 'figures/FIGURE_MANIFEST.json', main_report, main_audit_path,
                    historical_report, historical_audit_path, HRS / 'summary/AGGREGATE_RESULTS.json',
                    HRS / 'FINAL_RESULT_REVIEW.json', HRS / 'RESULTS.md',
                    HRS / 'recovery_v1/INCIDENT_AND_CORRECTION.md', HRS / 'plot_results.py']
    source_paths.extend(sorted({PROJECT / item['public_original_byte_manifest']
                                for item in SOURCE_BYTE_EQUIVALENCES.values()}))
    payload = {
        'schema_version': 'integrated_figure_package_v0.7',
        'date': '2026-11-03',
        'scope': 'Four main figures and one supplement; unchanged reused figures and retained aggregate records only.',
        'main_figures': 4, 'supplementary_figures': 1,
        'new_plot_or_diagram': False,
        'new_generations': 0, 'new_scientific_fits': 0,
        'patient_rows_read': 0, 'generated_rows_read': 0,
        'inferential_pooling': False,
        'sources': [record(p) for p in source_paths],
        'source_byte_equivalences': list(SOURCE_BYTE_EQUIVALENCES.values()),
        'figure_bindings': bindings,
        'aggregate_copies': data_bindings,
        'new_focal_payload': {'file': record(focal_path), 'selection': {'term_in': focal_terms},
                              'source': record(HRS / 'summary/fixed_effects_all_seeds.csv'),
                              'operation': 'Exact row selection; no values transformed; all arms and seeds retained.'},
        'display_counts': checks,
        'experiment_counts': {
            'main': {'cases': 2, 'agent_constructions': 20, 'statistical_constructions': 4,
                     'final_tables': 72, 'rows_per_table': 3000, 'seeds': [5101, 5102, 5103]},
            'historical': {'agent_constructions': 6, 'final_tables': 18, 'rows_per_table': 3000,
                           'physical_executions': 42, 'trial_executions': 6, 'initial_final_deliveries': 36,
                           'distinct_tables_overall': 24, 'distinct_delivery_tables': 18,
                           'final_initial_byte_duplicates': 18, 'seeds': [4101, 4102, 4103]},
            'hrs': dict(hrs_data['counts'], agent_constructions=1, published_law_constructions=1,
                        visits_per_subject=4, visit_years=[0, 2, 4, 6], seeds=[6101, 6102, 6103])},
        'uncertainty': {
            'Figure 2': 'Three-seed minima/maxima; CHNS selected-sample CR1-t 95% reference intervals and ENSANUT equal-cell empirical cluster-resampling stability bands.',
            'Figure 3': 'Three-seed minima/maxima; CHNS CR1-t reference intervals for three coefficients; no unavailable correlation intervals invented.',
            'Figure 4': 'Per-seed model-conditional 95% Wald intervals. Source bounds are exported coefficient plus/minus 1.959963984540054 times exported SE.',
            'Figure S1': 'Three-seed minima/maxima; no confidence intervals; same tables as Figure 4.'},
        'limitations': [
            'Figure 1 describes the external-evidence protocol; supplied-summary and HRS conditions receive relevant aggregate reference values.',
            'E0/E1, L/R, and HRS have different authors, protocols, information, and evaluation settings; no cross-study causal contrast or pooled ranking.',
            'R target-summary inputs include accompanying uncertainty/design/quality metadata; the 30 plotted/evaluated statistics are not a full count of available information.',
            'HRS reference coefficients were inputs; three invalid initial comparator tables remain documented as our implementation failure.',
            'HRS Figure S1 repeats Figure 4 data and does not create additional replicates.',
            'Native-size visual inspection does not establish final journal-layout readability.'
        ],
        'visual_review': {'inspected': ['Figure 1 PNG', 'Figure 2 PNG', 'Figure 3 PNG', 'Figure 4 PNG', 'Figure S1 PNG'],
                          'result': 'All panels and labels visible; no clipping seen at native export sizes.',
                          'final_journal_render_completed': False},
        'verification': {'all_copied_assets_byte_identical': True,
                         'cross_sectional_seed_pointer_checks': 306,
                         'source_audit_bindings_verified': ['main', 'historical', 'HRS'],
                         'new_focal_payload_exact_rows': 12},
        'outputs': {p.relative_to(OUT).as_posix(): {'sha256': digest(p), 'bytes': p.stat().st_size}
                    for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'NUMERIC_MANIFEST.json'}
    }
    (OUT / 'NUMERIC_MANIFEST.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'pass', 'unchanged_figure_files': 10,
                      'cross_sectional_seed_pointer_checks': 306,
                      'hrs_focal_rows': 12, 'hrs_all_effect_rows': 96,
                      'outputs_bound': len(payload['outputs'])}))


if __name__ == '__main__':
    main()
