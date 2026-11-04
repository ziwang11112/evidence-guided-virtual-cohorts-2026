"""Strict line-based parsing of pinned source summaries; never sample or fit.

All section markers must occur exactly once; row duplicates are errors.
splitlines() gives identical model boundaries for LF and CRLF inputs.
"""
import hashlib
import json
from pathlib import Path
import re

UNIT = Path(__file__).resolve().parents[1]
SUMMARY = 'HRSmodels_20200902_fullDemoTable.txt'
NUM = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
TERMS = {
    'hba1c': ['(Intercept)', 'base.age60', 'sexMale', 'raceBlack', 'educHS', 'educLessThanHS', 'cses'],
    'cses': ['(Intercept)', 'base.age60', 'raceBlack'],
    'memory': ['(Intercept)', 'age60', 'hba1c_U65', 'hba1c_O65', 'raceBlack', 'educHS', 'educLessThanHS', 'sexMale', 'cses', 'age60:hba1c_U65', 'age60:hba1c_O65', 'age60:raceBlack', 'age60:educHS', 'age60:educLessThanHS', 'age60:sexMale', 'age60:cses'],
    'education': ['(Intercept)', 'base.age60', 'sexMale', 'raceBlack', 'cses']}


def verified_sources():
    manifest = json.loads((UNIT / 'sources/SOURCE_MANIFEST.json').read_text())
    texts, records = {}, {}
    for row in manifest['files']:
        raw = (UNIT / row['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('SHA256 mismatch')
        if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != row['git_blob_sha1']:
            raise ValueError('Git blob mismatch')
        name = Path(row['path']).name
        texts[name], records[name] = raw.decode(row['encoding']), row
    return texts, records


def parse_table(text, url):
    lines = text.splitlines()

    def unique(prefix, low=0, high=None):
        high = len(lines) if high is None else high
        if prefix == 'Estimate Std. Error':
            found = [i for i in range(low, high) if lines[i].split()[:3] == ['Estimate', 'Std.', 'Error']]
        else:
            found = [i for i in range(low, high) if lines[i].strip().startswith(prefix)]
        if len(found) != 1:
            raise ValueError(f'Expected exactly one boundary {prefix!r}, got {len(found)}')
        return found[0]

    def locator(index):
        return {'source_file': SUMMARY, 'url': url, 'line_start': index + 1, 'line_end': index + 1}

    gamma_start = unique('glm(formula = hba1c')
    edu_start = unique('multinom(formula = educ')
    cses_start = unique('lm(formula = cses')
    memory_start = unique('Linear mixed model fit by REML')
    if not 0 < gamma_start < edu_start < cses_start < memory_start < len(lines):
        raise ValueError('Wrong model section order')
    ranges = {'hba1c': (gamma_start, edu_start), 'education': (edu_start, cses_start),
              'cses': (cses_start, memory_start), 'memory': (memory_start, len(lines))}

    def regression(name):
        low, high = ranges[name]
        heading = unique('Fixed effects:' if name == 'memory' else 'Coefficients:', low, high)
        header = unique('Estimate Std. Error', heading + 1, high)
        # Exact whitespace-independent header recognition, not broad downstream scanning.
        if name != 'memory':
            stops = [i for i in range(header + 1, high) if lines[i].strip() == '---']
            if len(stops) != 1:
                raise ValueError('Missing coefficient table terminator')
            end = stops[0]
        else:
            end = high
        result = {}
        for i in range(header + 1, end):
            line = lines[i].strip()
            if not line:
                continue
            parts = line.split()
            term = parts[0]
            if term not in TERMS[name] or len(parts) < 4:
                raise ValueError(f'Unexpected {name} coefficient row at {i+1}: {line}')
            if term in result:
                raise ValueError(f'Duplicate {name} coefficient {term}')
            if any(re.fullmatch(NUM, token) is None for token in parts[1:4]):
                raise ValueError('Nonnumeric coefficient row')
            result[term] = {'estimate': float(parts[1]), 'standard_error': float(parts[2]), 'source': locator(i)}
        if list(result) != TERMS[name]:
            raise ValueError(f'Wrong {name} coefficient membership/order')
        return result

    result = {name: {'coefficients': regression(name)} for name in ['hba1c', 'cses', 'memory']}
    elo, ehi = ranges['education']
    coef_heading = unique('Coefficients:', elo, ehi)
    se_heading = unique('Std. Errors:', elo, ehi)
    last = unique('Residual Deviance:', elo, ehi)
    if not coef_heading < se_heading < last:
        raise ValueError('Wrong education table order')
    education = {'reference': 'College', 'terms': TERMS['education'], 'coefficients': {}, 'standard_errors': {}, 'sources': {}}
    for key, lo, hi in [('coefficients', coef_heading, se_heading), ('standard_errors', se_heading, last)]:
        entries = [(i, lines[i].split()) for i in range(lo + 1, hi) if lines[i].strip()]
        if not entries or entries[0][1] != TERMS['education']:
            raise ValueError('Wrong education term header')
        for i, parts in entries[1:]:
            category = parts[0]
            if category not in ['HS', 'LessThanHS'] or category in education[key] or len(parts) != 6:
                raise ValueError('Unexpected/duplicate education row')
            education[key][category] = list(map(float, parts[1:]))
            education['sources'][category + '_' + key] = locator(i)
        if list(education[key]) != ['HS', 'LessThanHS']:
            raise ValueError('Missing education category')
    result['education'] = education

    def scalar(name, prefix, pattern):
        lo, hi = ranges[name]
        i = unique(prefix, lo, hi)
        match = re.search(pattern, lines[i])
        if match is None:
            raise ValueError('Scalar not found within correct model range')
        return {'value': float(match.group(1)), 'source': locator(i)}
    result['hba1c']['dispersion'] = scalar('hba1c', '(Dispersion parameter for Gamma family', r'be (' + NUM + ')')
    result['cses']['residual_sd'] = scalar('cses', 'Residual standard error:', r'error: (' + NUM + ')')
    lo, hi = ranges['memory']
    rlo, rhi = unique('Random effects:', lo, hi), unique('Number of obs:', lo, hi)
    random = {}
    rows = {'intercept': r'^\s*ID\s+\(Intercept\)\s+(' + NUM + r')\s+(' + NUM + r')\s*$',
            'slope': r'^\s*age60\s+(' + NUM + r')\s+(' + NUM + r')\s+(' + NUM + r')\s*$',
            'residual': r'^\s*Residual\s+(' + NUM + r')\s+(' + NUM + r')\s*$'}
    for name, pattern in rows.items():
        matches = [(i, re.fullmatch(pattern, lines[i])) for i in range(rlo + 1, rhi)]
        matches = [(i, m) for i, m in matches if m is not None]
        if len(matches) != 1:
            raise ValueError('Missing/duplicate random effects row')
        i, match = matches[0]
        values = list(map(float, match.groups()))
        prefix = 'intercept' if name == 'intercept' else name
        random['printed_' + prefix + '_variance'] = {'value': values[0], 'source': locator(i)}
        random[prefix + '_sd'] = {'value': values[1], 'source': locator(i)}
        if name == 'slope':
            random['correlation'] = {'value': values[2], 'source': locator(i)}
    result['memory']['random'] = random
    result['model_ranges'] = {k: {'start': lo + 1, 'end_inclusive': hi} for k, (lo, hi) in ranges.items()}
    return result


def main():
    texts, records = verified_sources()
    result = parse_table(texts[SUMMARY], records[SUMMARY]['url'])
    destination = Path(__file__).resolve().parent / 'PARSED_SOURCE_MODELS.json'
    with destination.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'coefficient_pairs': 36, 'model_ranges': result['model_ranges'], 'generation_calls': 0}))


if __name__ == '__main__':
    main()
