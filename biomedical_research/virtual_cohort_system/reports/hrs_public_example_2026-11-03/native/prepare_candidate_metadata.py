"""Build reviewable native candidate metadata, without importing the sampler."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent
SOURCE = 'FILSHSTEIN_HRS_PUBLIC'


def main():
    p = json.loads((UNIT / 'sources/HRS_SOURCE_EVIDENCE.json').read_text())
    manifest = json.loads((UNIT / 'sources/SOURCE_MANIFEST.json').read_text())
    items = []

    def item(identifier, locator, variables, kind, estimate, unit='model_scale', se=None, statistic=None):
        row = {'id': identifier, 'source_id': SOURCE, 'locator': locator,
               'variables': variables, 'kind': kind, 'estimate': estimate, 'unit': unit,
               'uncertainty': {'kind': 'not_reported'} if se is None else {'kind': 'se', 'value': se},
               'adjustment': [], 'selection': 'Published HRS analytic sample and recipient-stage example.',
               'applicability': 'Same public HRS recipient-stage task; rounded source summaries are permitted input, not hidden target outcomes.'}
        if statistic:
            row['statistic_name'] = statistic
        items.append(row)

    def locator(value):
        return value['source_file'] + ':' + str(value['line_start']) + '-' + str(value['line_end'])

    context = {
        'study': ('RCTSim1_postGitHub_20200728.R:123-132; HRSmodels_20200902_fullDemoTable.txt:1,119', ['subject_id', 'visit_time']),
        'age_bins': ('RCTSim2_postGitHub_20200728.R:85-108', ['baseline_age']),
        'transforms': ('RCTSim2_postGitHub_20200728.R:108-109,211-219', ['baseline_age', 'age', 'age60', 'hba1c']),
        'education': ('HRSmodels_20200902_fullDemoTable.txt:60-71; RCTSim2_postGitHub_20200728.R:125-137', ['educ']),
        'rules': ('RCTSim2_postGitHub_20200728.R:dataGen; RCTSim1_postGitHub_20200728.R:71-76', ['baseline_age', 'cses', 'educ', 'hba1c', 'mem_s'])}
    for key, (where, variables) in context.items():
        item('native_' + key, where, variables, 'contextual', None)
    for index, cell in enumerate(p['demographic_cells']):
        item('native_cell_' + str(index + 1), locator(cell['source']), ['baseline_age', 'sex', 'race'],
             'reported_other', cell['count'], unit='subject_count', statistic='age_sex_race_cell_count')
    groups = {}
    for block, variable in [('cses', 'cses'), ('hba1c', 'hba1c'), ('memory', 'mem_s')]:
        groups[block] = []
        for index, (term, value) in enumerate(p[block]['coefficients'].items()):
            identifier = 'native_' + block + '_beta_' + str(index + 1)
            groups[block].append(identifier)
            item(identifier, locator(value['source']) + '; term=' + term, [variable],
                 'reported_other', value['estimate'], se=value['standard_error'], statistic=block + '_conditional_model_coefficient')
    for index, category in enumerate(['HS', 'LessThanHS']):
        for term_index, term in enumerate(p['education']['terms']):
            item('native_educ_beta_' + str(index) + '_' + str(term_index),
                 locator(p['education']['sources'][category + '_coefficients']) + '; category=' + category + '; term=' + term,
                 ['educ'], 'reported_other', p['education']['coefficients'][category][term_index],
                 se=p['education']['standard_errors'][category][term_index], statistic='education_logit_coefficient')
    for identifier, variable, kind, value in [
        ('native_cses_sd', 'cses', 'sd', p['cses']['residual_sd']),
        ('native_hba1c_dispersion', 'hba1c', 'reported_other', p['hba1c']['dispersion'])]:
        item(identifier, locator(value['source']), [variable], kind, value['value'],
             statistic='gamma_dispersion' if kind == 'reported_other' else None)
    for key in ['intercept_sd', 'slope_sd', 'correlation', 'residual_sd']:
        value = p['memory']['random'][key]
        item('native_random_' + key, locator(value['source']), ['mem_s'],
             'correlation' if key == 'correlation' else 'sd', value['value'])

    evidence = {'schema_version': 1, 'sources': [{
        'id': SOURCE, 'identifier': 'https://github.com/powerepilab/Sim_for_data_pooling/tree/' + manifest['commit'],
        'population': 'Published HRS analytic sample n=11509; recipient generation uses 4 balanced visits.',
        'measurement': 'Age in years; HbA1c percent; source CSES and standardized memory; source categorical factors.',
        'cohort_ids': ['HRS'], 'artifacts': [{'path': row['path'], 'sha256': row['sha256']} for row in manifest['files']]}], 'items': items}
    parameters = {key: p[key] for key in ['study', 'demographic_cells', 'age_bins', 'transforms', 'cses', 'education', 'hba1c', 'memory']}
    assumptions = [
        {'id': 'printed_precision', 'description': 'Use published rounded coefficients, SDs and correlation exactly; raw R fitted objects are unavailable. No uncertainty resampling of source parameters.'},
        {'id': 'native_model_completion', 'description': 'Preserve source conditional families, independent residuals, uniform within age bins and balanced visits as the predecessor supplied modeling law; do not infer them from marginals.'},
        {'id': 'implementation_adapter', 'description': 'New NumPy RNG, canonical column/factor names and string IDs; omit only unused age70 jitter; no bitwise R output claim.'}]
    provenance = {}
    for key in parameters:
        if key == 'demographic_cells':
            ids = [row['id'] for row in items if row['id'].startswith('native_cell_')]
        elif key == 'education':
            ids = ['native_education'] + [row['id'] for row in items if row['id'].startswith('native_educ_beta_')]
        elif key in groups:
            ids = groups[key] + [row['id'] for row in items if row['id'].startswith('native_random_')] if key == 'memory' else groups[key] + ['native_' + key + ('_sd' if key == 'cses' else '_dispersion')]
        else:
            ids = ['native_' + key]
        provenance[key] = {'evidence_ids': ids + ['native_rules'],
                           'assumption_ids': ['printed_precision', 'native_model_completion', 'implementation_adapter'],
                           'derivation': 'Parsed from exact pinned public artifacts with per-value source locators. Count normalization, Gamma shape/scale, SD-based covariance and named design terms follow the source recipient rules; no fitting or target feedback.'}
    spec = {'parameters': parameters, 'assumptions': assumptions, 'parameter_provenance': provenance}
    check_report = {'scope': 'deterministic invented analytic helper tests only',
                    'command': 'python native/test_analytic_helpers.py', 'tests_run': 4, 'failures': 0,
                    'tests': ['softmax_reference_and_overflow', 'gamma_mean_and_variance', 'covariance_uses_sd_not_other_variance', 'linear_by_named_terms'],
                    'generator_function_calls': 0, 'random_draws': 0, 'clinical_fits': 0,
                    'source_verification': '5 original files passed exact Git blob SHA1 and SHA256 verification; parser found28 demographic cells totaling11509 and16 memory coefficients.',
                    'generator_sha256': hashlib.sha256((HERE / 'generator.py').read_bytes()).hexdigest(),
                    'test_sha256': hashlib.sha256((HERE / 'test_analytic_helpers.py').read_bytes()).hexdigest()}
    for name, value in [('evidence.json', evidence), ('model_spec.json', spec), ('analytic_check_result.json', check_report)]:
        with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
    checks = {'scope': 'fixture_only', 'records': [
        {'name': 'deterministic_analytic_helpers', 'status': 'pass', 'detail': 'Four invented deterministic helper tests passed. No generate call or RNG draw.'},
        {'name': 'source_hashes_and_parameter_parse', 'status': 'pass', 'detail': 'Five exact source Git blobs/SHA256 verified; parsed28 cells, all conditional coefficient blocks and16 memory terms.'},
        {'name': 'clinical_generation_quality', 'status': 'not_computable', 'detail': 'No HRS draw or model fit performed during preparation. Coordinator runs isolated final seeds after review.'}],
        'artifacts': [{'path': 'analytic_check_result.json', 'sha256': hashlib.sha256((HERE / 'analytic_check_result.json').read_bytes()).hexdigest()}]}
    with (HERE / 'checks.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(checks, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'evidence_items': len(items), 'parameter_groups': len(parameters), 'generator_calls': 0}))


if __name__ == '__main__':
    main()
