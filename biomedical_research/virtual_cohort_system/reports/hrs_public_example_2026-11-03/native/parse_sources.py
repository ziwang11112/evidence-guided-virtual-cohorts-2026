"""Parse pinned, byte-verified public aggregates. Does not fit or sample."""
import hashlib
import json
from pathlib import Path
import re

UNIT = Path(__file__).resolve().parents[1]
SUMMARY = 'HRSmodels_20200902_fullDemoTable.txt'
CODE = 'RCTSim2_postGitHub_20200728.R'
PREAMBLE = 'RCTSim1_postGitHub_20200728.R'
ESTIMATION = 'HRS_sim_data_code_postGitHub_20200728.R'
NUMBER = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'


def parse():
    manifest = json.loads((UNIT / 'sources/SOURCE_MANIFEST.json').read_text())
    texts, records = {}, {}
    for item in manifest['files']:
        raw = (UNIT / item['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Source SHA256 mismatch')
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if blob != item['git_blob_sha1']:
            raise ValueError('Source Git blob mismatch')
        name = Path(item['path']).name
        texts[name] = raw.decode(item['encoding'])
        records[name] = item

    def loc(name, literal):
        text = texts[name]
        start = text.index(literal)
        return {'source_file': name, 'url': records[name]['url'],
                'line_start': text[:start].count('\n') + 1,
                'line_end': text[:start + len(literal)].count('\n') + 1}

    def scalar(name, pattern):
        match = re.search(pattern, texts[name], re.MULTILINE)
        if match is None:
            raise ValueError('Missing source pattern: ' + pattern)
        return {'value': float(match.group(1)), 'source': loc(name, match.group(0))}

    def coef_section(start, end, expected):
        block = texts[SUMMARY].split(start, 1)[1]
        if end:
            block = block.split(end, 1)[0]
        result = {}
        for line in block.splitlines():
            match = re.match(r'^\s*(\S+)\s+(' + NUMBER + r')\s+(' + NUMBER + r')\s+', line)
            if match and match.group(1) in expected:
                result[match.group(1)] = {'estimate': float(match.group(2)),
                                          'standard_error': float(match.group(3)),
                                          'source': loc(SUMMARY, line)}
        if set(result) != set(expected):
            raise ValueError('Missing or extra coefficient terms')
        return result

    n = int(re.search(r'^\[1\] (\d+)', texts[SUMMARY]).group(1))
    cells = []
    for match in re.finditer(r'^\s*\d+\s+(Agecat\d)\s+(Female|Male)\s+(White|Black)\s+(\d+)\s+([\d.]+)\s*$', texts[SUMMARY], re.MULTILINE):
        cells.append({'age_category': match.group(1), 'sex': match.group(2).lower(),
                      'race': match.group(3).lower(), 'count': int(match.group(4)),
                      'printed_proportion': float(match.group(5)),
                      'probability': int(match.group(4)) / n,
                      'source': loc(SUMMARY, match.group(0))})
    if len(cells) != 28 or sum(x['count'] for x in cells) != n:
        raise ValueError('Demographic count mismatch')
    bounds = {}
    for label, following, key in [('Age_Low =', 'Age_High =', 'lower'), ('Age_High =', ')) %>% group_by', 'upper')]:
        block = texts[CODE].split(label, 1)[1].split(following, 1)[0]
        for match in re.finditer(r'agecat == "(Agecat\d)" ~ (\d+)', block):
            bounds.setdefault(match.group(1), {})[key] = int(match.group(2))
            bounds[match.group(1)][key + '_source'] = loc(CODE, match.group(0))
    if set(bounds) != {x['age_category'] for x in cells} or any('upper' not in x or 'lower' not in x for x in bounds.values()):
        raise ValueError('Age bounds mismatch')
    cses = coef_section('lm(formula = cses', 'Linear mixed model', ['(Intercept)', 'base.age60', 'raceBlack'])
    gamma = coef_section('glm(formula = hba1c', 'Call:\nmultinom', ['(Intercept)', 'base.age60', 'sexMale', 'raceBlack', 'educHS', 'educLessThanHS', 'cses'])
    memterms = ['(Intercept)', 'age60', 'hba1c_U65', 'hba1c_O65', 'raceBlack', 'educHS', 'educLessThanHS', 'sexMale', 'cses', 'age60:hba1c_U65', 'age60:hba1c_O65', 'age60:raceBlack', 'age60:educHS', 'age60:educLessThanHS', 'age60:sexMale', 'age60:cses']
    memory = coef_section('Fixed effects:', None, memterms)
    multiblock = texts[SUMMARY].split('multinom(formula', 1)[1].split('Residual Deviance:', 1)[0]
    coefblock, seblock = multiblock.split('Coefficients:', 1)[1].split('Std. Errors:', 1)
    education = {'reference': 'College', 'terms': ['(Intercept)', 'base.age60', 'sexMale', 'raceBlack', 'cses'], 'coefficients': {}, 'standard_errors': {}, 'sources': {}}
    for category in ['HS', 'LessThanHS']:
        for block, field in [(coefblock, 'coefficients'), (seblock, 'standard_errors')]:
            match = re.search(r'^' + category + r'\s+(.+)$', block, re.MULTILINE)
            values = list(map(float, match.group(1).split()))
            if len(values) != len(education['terms']):
                raise ValueError('Multinomial coefficient count mismatch')
            education[field][category] = values
            education['sources'][category + '_' + field] = loc(SUMMARY, match.group(0))
    random = {}
    for key, pattern in [
        ('intercept_sd', r'ID\s+\(Intercept\)\s+' + NUMBER + r'\s+(' + NUMBER + ')'),
        ('slope_sd', r'^\s+age60\s+' + NUMBER + r'\s+(' + NUMBER + ')'),
        ('correlation', r'^\s+age60\s+' + NUMBER + r'\s+' + NUMBER + r'\s+(' + NUMBER + ')'),
        ('residual_sd', r'^ Residual\s+' + NUMBER + r'\s+(' + NUMBER + ')'),
        ('printed_intercept_variance', r'ID\s+\(Intercept\)\s+(' + NUMBER + ')'),
        ('printed_slope_variance', r'^\s+age60\s+(' + NUMBER + ')'),
        ('printed_residual_variance', r'^ Residual\s+(' + NUMBER + ')')]:
        random[key] = scalar(SUMMARY, pattern)
    source_analysis_obs = int(re.search(r'Number of obs: (\d+)', texts[SUMMARY]).group(1))
    hrs_call = texts[PREAMBLE].split('nDF = \'n_hrs\'', 1)[1]
    visits = re.search(r'n.obs = (\d+), time.int = (\d+)', hrs_call)
    nvisits, interval = map(int, visits.groups())
    age_center = scalar(CODE, r'base.age60 = \(base.age-(' + NUMBER + r')\)/10')
    age_scale = scalar(CODE, r'base.age60 = \(base.age-60\)/(' + NUMBER + ')')
    knot = scalar(CODE, r'hba1c.c = hba1c-(' + NUMBER + ')')
    rules = {
        'sampling': 'Draw demographic cells independently with replacement, probability count/total; draw continuous uniform age within cell bounds.',
        'cses': 'Conditional normal with reported linear mean and residual SD.',
        'education': 'Multinomial logistic: logits College=0, HS=X beta_HS, LessThanHS=X beta_LessThanHS; softmax.',
        'hba1c': 'Gamma log mean: mu=exp(X beta); shape=1/dispersion, scale=mu*dispersion.',
        'memory': 'Fixed-effects mean plus correlated zero-mean Gaussian subject intercept and age60 slope plus independent Gaussian visit residual.',
        'random_covariance': 'Off diagonal = intercept_sd*slope_sd*correlation; diagonal = SD squared, following RCTSim1. Printed variances retained separately, not substituted.',
        'knots': 'hba1c_U65=min(hba1c-knot,0), hba1c_O65=max(hba1c-knot,0).',
        'time': 'age=baseline_age+visit_time; age60=(age-center)/scale. Baseline covariates repeat unchanged across visits.',
        'range': 'No clipping, posthoc moment forcing, truncation, or rank reordering in the native law.'}
    evidence = {
        'schema_version': 'hrs-public-evidence-v1', 'source_commit': manifest['commit'],
        'registration_status': 'parsed public evidence; pending coordinator approval',
        'scope': 'HRS recipient-stage, cohort-specific pre-imputation generation; excludes ARIC, pooling and MICE.',
        'source_manifest': 'sources/SOURCE_MANIFEST.json',
        'study': {'n_subjects': n, 'n_source_longitudinal_observations': source_analysis_obs,
                  'visit_times': list(range(0, nvisits * interval, interval)),
                  'visit_source': loc(PREAMBLE, visits.group(0)),
                  'n_subjects_source': loc(SUMMARY, '[1] ' + str(n))},
        'demographic_cells': cells, 'age_bins': bounds,
        'transforms': {'age_center': age_center, 'age_scale': age_scale, 'hba1c_knot': knot},
        'cses': {'coefficients': cses, 'residual_sd': scalar(SUMMARY, r'Residual standard error: (' + NUMBER + ')')},
        'education': education,
        'hba1c': {'coefficients': gamma, 'dispersion': scalar(SUMMARY, r'Dispersion parameter for Gamma family taken to be (' + NUMBER + ')')},
        'memory': {'coefficients': memory, 'random': random}, 'generation_rules': rules,
        'analysis': {'formula': 'mem_s ~ age60*(hba1c_U65+hba1c_O65+race+educ+sex+cses)+(1+age60|subject_id)',
                     'method': 'Gaussian linear mixed model; REML; source lme4 optimizer bobyqa',
                     'focal_terms': ['age60:hba1c_U65', 'age60:hba1c_O65'],
                     'source': loc(CODE, 'lmer(mem.s ~  age60*(hba1c_U65 + hba1c_O65 + race + educ + sex + cses) +')},
        'diagnostic_definitions': {'unit': 'One baseline record per subject, visit_time=0',
           'sd': 'Sample SD, denominator n-1', 'hba1c_below': '<6.5', 'hba1c_above': '>=6.5',
           'categorical_denominator': 'All baseline subjects; subgroup HbA1c means/SD use only subgroup members',
           'baseline_memory_source': loc(ESTIMATION, 'filter(assessNo<=1)'),
           'synthetic_baseline_source': loc(CODE, "tabhrs = df1$df %>% distinct(ID,.keep_all = TRUE) %>% summarise("),
           'threshold_source': loc(ESTIMATION, 'hba1c_O65only = ifelse(hba1c>=6.5, hba1c, NA)')},
        'factor_coding': {'sex': {'reference': 'female', 'Male': 'male'}, 'race': {'reference': 'white', 'Black': 'black'}, 'educ': {'reference': 'College', 'levels': ['College', 'HS', 'LessThanHS']}},
        'limitations': [
          'Printed coefficients, SDs and correlation are rounded; raw fitted objects are not supplied. This reconstructs the published rounded rule, not bitwise author output.',
          'Distribution families, dependency ordering, normal residuals and balanced visits are source authors modeling choices; they are not identified from marginal summaries alone.',
          'Native code uses [80,100] for its oldest age bin despite generic paper wording about five-year groups.',
          'Source original model has 43500 observations; balanced synthetic design has 46036. No claim to reproduce missing follow-up mechanism.',
          'A new NumPy random stream, canonical field names and string IDs are implementation adapters. Unused native age70 jitter is omitted.',
          'Reported model estimates and Table2/3 statistics are permitted source information, not hidden test outcomes.']}
    columns = {'id': {'dtype': 'string', 'unique': True}, 'subject_id': {'dtype': 'string'},
               'visit_time': {'dtype': 'number', 'unit': 'years after baseline', 'allowed_values': evidence['study']['visit_times']},
               'baseline_age': {'dtype': 'number', 'unit': 'years'}, 'age': {'dtype': 'number', 'unit': 'years'},
               'age60': {'dtype': 'number', 'unit': 'decades centered at 60 years'},
               'sex': {'dtype': 'category', 'levels': ['female', 'male']},
               'race': {'dtype': 'category', 'levels': ['white', 'black']},
               'educ': {'dtype': 'category', 'levels': ['College', 'HS', 'LessThanHS']},
               'cses': {'dtype': 'number', 'unit': 'source composite score'},
               'hba1c': {'dtype': 'number', 'unit': 'percent', 'strictly_positive': True},
               'mem_s': {'dtype': 'number', 'unit': 'source standardized delayed recall score'}}
    schema = {'schema_version': 'hrs-output-v1', 'columns': columns, 'n_subjects': n,
              'n_rows': n * nvisits, 'required_column_order': list(columns),
              'baseline_constant_fields': ['baseline_age', 'sex', 'race', 'educ', 'cses', 'hba1c'],
              'constraints': ['Exactly one row per subject and visit time', 'age=baseline_age+visit_time', 'age60=(age-60)/10', 'No missing values']}
    return evidence, schema


def main():
    evidence, schema = parse()
    for name, value in [('HRS_SOURCE_EVIDENCE.json', evidence), ('HRS_DATA_SCHEMA.json', schema)]:
        path = UNIT / 'sources' / name
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
    print(json.dumps({'subjects': evidence['study']['n_subjects'], 'cells': len(evidence['demographic_cells']), 'memory_terms': len(evidence['memory']['coefficients']), 'sampling_executed': False}))


if __name__ == '__main__':
    main()
