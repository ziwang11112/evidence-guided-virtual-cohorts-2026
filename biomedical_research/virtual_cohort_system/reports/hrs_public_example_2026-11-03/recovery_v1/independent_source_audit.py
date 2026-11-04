"""Independent source audit: direct pinned line/token reads, no model parser.

This module does not import parse_source_corrected or any generator.
Hardcoded line positions are valid only for the exact pinned source SHA256.
"""
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = '1e1418da2f3c912edf016d7189e064a7bd7fdddd9e370b0ac9c1e80e522677e9'
TERMS = {
    'hba1c': ['(Intercept)', 'base.age60', 'sexMale', 'raceBlack', 'educHS', 'educLessThanHS', 'cses'],
    'cses': ['(Intercept)', 'base.age60', 'raceBlack'],
    'memory': ['(Intercept)', 'age60', 'hba1c_U65', 'hba1c_O65', 'raceBlack', 'educHS', 'educLessThanHS', 'sexMale', 'cses', 'age60:hba1c_U65', 'age60:hba1c_O65', 'age60:raceBlack', 'age60:educHS', 'age60:educLessThanHS', 'age60:sexMale', 'age60:cses']}


def audit(packet, spec=None, evidence=None):
    raw = (UNIT / 'sources/original/HRSmodels_20200902_fullDemoTable.txt').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    lines = raw.decode('cp1252').splitlines()
    assert lines[32].startswith('glm(formula = hba1c')
    assert lines[60].startswith('multinom(formula = educ')
    assert lines[76].startswith('lm(formula = cses')
    assert lines[95].startswith('Formula: I(mem.s) ~ age60')
    pair_count = 0
    for group, positions in [('hba1c', range(42,49)), ('cses', range(85,88)), ('memory', range(114,130))]:
        assert list(packet[group]['coefficients']) == TERMS[group]
        for term, line_number in zip(TERMS[group], positions):
            fields = lines[line_number - 1].split()
            assert fields[0] == term
            expected, se = float(fields[1]), float(fields[2])
            value = packet[group]['coefficients'][term]
            assert value['estimate'] == expected, (group, term, value['estimate'], expected)
            assert value['standard_error'] == se, (group, term, 'SE')
            assert value['source']['line_start'] == value['source']['line_end'] == line_number
            pair_count += 1
    edu = packet['education']
    assert edu['reference'] == 'College'
    assert edu['terms'] == lines[63].split() == lines[68].split()
    for category, coef_line, se_line in [('HS',65,70), ('LessThanHS',66,71)]:
        coef_tokens, se_tokens = lines[coef_line-1].split(), lines[se_line-1].split()
        assert coef_tokens[0] == se_tokens[0] == category
        assert edu['coefficients'][category] == list(map(float, coef_tokens[1:]))
        assert edu['standard_errors'][category] == list(map(float, se_tokens[1:]))
        assert edu['sources'][category+'_coefficients']['line_start'] == coef_line
        assert edu['sources'][category+'_standard_errors']['line_start'] == se_line
        pair_count += 5
    assert packet['hba1c']['dispersion']['value'] == float(lines[51].split()[-1].rstrip(')'))
    assert packet['cses']['residual_sd']['value'] == float(lines[90].split()[3])
    random = packet['memory']['random']
    int_tokens, slope_tokens, residual_tokens = (lines[i-1].split() for i in [107,108,109])
    assert int_tokens[:2] == ['ID','(Intercept)'] and slope_tokens[0] == 'age60' and residual_tokens[0] == 'Residual'
    values = {'intercept_sd':float(int_tokens[3]), 'slope_sd':float(slope_tokens[2]),
              'correlation':float(slope_tokens[3]), 'residual_sd':float(residual_tokens[2]),
              'printed_intercept_variance':float(int_tokens[2]), 'printed_slope_variance':float(slope_tokens[1]),
              'printed_residual_variance':float(residual_tokens[1])}
    for key, expected in values.items():
        assert random[key]['value'] == expected
    if 'demographic_cells' in packet:
        cells = packet['demographic_cells']
        assert len(cells) == 28
        for number, cell in enumerate(cells, start=3):
            fields = lines[number-1].split()
            assert (cell['age_category'],cell['sex'],cell['race'],cell['count'],cell['printed_proportion']) == (fields[1],fields[2].lower(),fields[3].lower(),int(fields[4]),float(fields[5]))
            assert cell['probability'] == int(fields[4])/11509
        assert sum(x['count'] for x in cells) == packet['study']['n_subjects'] == 11509
        assert packet['study']['n_source_longitudinal_observations'] == 43500
        assert packet['study']['visit_times'] == [0,2,4,6]
        assert [(packet['age_bins']['Agecat'+str(i)]['lower'],packet['age_bins']['Agecat'+str(i)]['upper']) for i in range(7)] == [(50,55),(55,60),(60,65),(65,70),(70,75),(75,80),(80,100)]
        assert {k:v['value'] for k,v in packet['transforms'].items()} == {'age_center':60.0,'age_scale':10.0,'hba1c_knot':6.5}
    if spec is not None:
        assert all(spec['parameters'][key] == packet[key] for key in spec['parameters'])
    if evidence is not None:
        items = {x['id']:x for x in evidence['items']}
        for group in TERMS:
            for index, term in enumerate(TERMS[group], start=1):
                entry = items[f'native_{group}_beta_{index}']
                expected = packet[group]['coefficients'][term]
                assert entry['estimate'] == expected['estimate']
                assert entry['uncertainty'] == {'kind':'se','value':expected['standard_error']}
                first_locator = entry['locator'].split(';')[0]
                assert first_locator == f"HRSmodels_20200902_fullDemoTable.txt:{expected['source']['line_start']}-{expected['source']['line_end']}"
        for category_index, category in enumerate(['HS','LessThanHS']):
            for index, term in enumerate(edu['terms']):
                entry = items[f'native_educ_beta_{category_index}_{index}']
                assert entry['estimate'] == edu['coefficients'][category][index]
                assert entry['uncertainty'] == {'kind':'se','value':edu['standard_errors'][category][index]}
    return {'status':'pass','coefficient_SE_pairs':pair_count,'demographic_cells':28 if 'demographic_cells' in packet else 0,
            'independence':'Direct token reading at fixed lines of an exact SHA256-pinned export; no section parser imported.',
            'generator_calls':0,'clinical_fits':0}
