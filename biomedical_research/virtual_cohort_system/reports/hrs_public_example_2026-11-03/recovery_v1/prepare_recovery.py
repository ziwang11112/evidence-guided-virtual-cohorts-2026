"""Prepare a source-only correction and independently audit it. No generation."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from parse_source_corrected import parse_table, verified_sources, SUMMARY
from independent_source_audit import audit

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    texts, records = verified_sources()
    raw_text, url = texts[SUMMARY], records[SUMMARY]['url']
    parsed = parse_table(raw_text, url)
    independent_parsed = audit(parsed)
    lf = '\n'.join(raw_text.splitlines()) + '\n'
    crlf = lf.replace('\n', '\r\n')
    assert parse_table(lf, url) == parse_table(crlf, url) == parsed
    failures_rejected = []
    gamma_first = raw_text.splitlines()[41]
    variants = {
        'duplicate_gamma_coefficient': lf.replace(gamma_first + '\n', gamma_first + '\n' + gamma_first + '\n', 1),
        'missing_gamma_coefficient': lf.replace(gamma_first + '\n', '', 1),
        'missing_model_boundary': lf.replace('multinom(formula = educ', 'NOT_A_MODEL(formula = educ', 1),
        'duplicate_model_boundary': lf + '\nmultinom(formula = educ\n',
        'missing_table_terminator': lf.replace('---\n', '', 1),
        'unexpected_gamma_term': lf.replace(gamma_first + '\n', gamma_first.replace('(Intercept)', 'UNEXPECTED_TERM') + '\n', 1),
    }
    for name, text in variants.items():
        try:
            parse_table(text, url)
        except ValueError:
            failures_rejected.append(name)
        else:
            raise AssertionError('Malformed source unexpectedly accepted: ' + name)

    # Use the preserved source packet only for unchanged metadata. Every scientific
    # coefficient/SE is checked independently against the original, pinned bytes.
    original_packet_path = UNIT / 'sources/HRS_SOURCE_EVIDENCE.json'
    original_packet = json.loads(original_packet_path.read_text())
    corrected_packet = deepcopy(original_packet)
    corrected_packet['hba1c']['coefficients'] = parsed['hba1c']['coefficients']
    for key in original_packet:
        if key != 'hba1c':
            assert corrected_packet[key] == original_packet[key]
    assert corrected_packet['hba1c']['dispersion'] == original_packet['hba1c']['dispersion']
    source_audit = audit(corrected_packet)

    original_candidate = UNIT / 'bundle/candidates/native'
    spec = json.loads((original_candidate / 'model_spec.json').read_text())
    old_spec = deepcopy(spec)
    spec['parameters']['hba1c']['coefficients'] = parsed['hba1c']['coefficients']
    spec['parameter_provenance']['hba1c']['derivation'] = (
        'Recovery v1 corrects the initial CRLF-sensitive extraction defect. Seven HbA1c coefficients and SEs are now taken only from the Gamma coefficient table at original export lines42-48, using mandatory section boundaries and duplicate rejection, and independently audited by direct source-line token reads. Other model parameters and generator bytes are unchanged; no generated outcome was used to select values.')
    for key in spec['parameters']:
        if key != 'hba1c':
            assert spec['parameters'][key] == old_spec['parameters'][key]
    assert spec['parameters']['hba1c']['dispersion'] == old_spec['parameters']['hba1c']['dispersion']
    assert spec['assumptions'] == old_spec['assumptions']
    evidence = json.loads((original_candidate / 'evidence.json').read_text())
    old_evidence = deepcopy(evidence)
    updated_ids = []
    for index, (term, values) in enumerate(parsed['hba1c']['coefficients'].items(), start=1):
        identifier = f'native_hba1c_beta_{index}'
        entry = next(x for x in evidence['items'] if x['id'] == identifier)
        entry['estimate'] = values['estimate']
        entry['uncertainty'] = {'kind':'se','value':values['standard_error']}
        entry['locator'] = f"{SUMMARY}:{values['source']['line_start']}-{values['source']['line_end']}; term={term}"
        updated_ids.append(identifier)
    assert evidence['sources'] == old_evidence['sources']
    for before, after in zip(old_evidence['items'], evidence['items']):
        if before['id'] not in updated_ids:
            assert before == after
    candidate_audit = audit(corrected_packet, spec, evidence)
    deltas = []
    for term, value in parsed['hba1c']['coefficients'].items():
        before = old_spec['parameters']['hba1c']['coefficients'][term]
        deltas.append({'term':term,'initial_estimate':before['estimate'],'corrected_estimate':value['estimate'],
                       'initial_SE':before['standard_error'],'corrected_SE':value['standard_error'],
                       'initial_source_line':before['source']['line_start'],'corrected_source_line':value['source']['line_start']})
    destination = HERE / 'native_candidate'
    destination.mkdir(exist_ok=False)
    generator_bytes = (original_candidate / 'generator.py').read_bytes()
    (destination / 'generator.py').write_bytes(generator_bytes)
    assert digest(destination / 'generator.py') == digest(original_candidate / 'generator.py')
    dump(HERE / 'sources/HRS_SOURCE_EVIDENCE.json', corrected_packet)
    dump(destination / 'model_spec.json', spec)
    dump(destination / 'evidence.json', evidence)
    report = {'created_utc':datetime.now(timezone.utc).isoformat(),'status':'pass',
              'scope':'Corrected source extraction and candidate metadata only. No generator import/call, new data generation, clinical fit or generated-row reading.',
              'initial_native_preflight_status':'OVERTURNED: extraction completeness/shape checks did not establish model-specific coefficient fidelity.',
              'independent_source_audit':source_audit,'independent_candidate_audit':candidate_audit,
              'newline_and_failure_tests':{'LF_CRLF_equal':True,'malformed_inputs_rejected':failures_rejected},
              'changes':deltas,'unchanged':{'generator_byte_identical':True,'generator_sha256':digest(destination / 'generator.py'),
                 'non_hba1c_parameter_groups':True,'hba1c_dispersion':True,'assumptions':True,'source_artifact_list':True,'other_evidence_items':True},
              'input_hashes':{'initial_source_packet':digest(original_packet_path),'initial_native_model_spec':digest(original_candidate / 'model_spec.json'),
                 'initial_native_evidence':digest(original_candidate / 'evidence.json'),
                 'original_parameter_export':digest(UNIT / 'sources/original' / SUMMARY)},
              'corrected_hashes':{'source_packet':digest(HERE / 'sources/HRS_SOURCE_EVIDENCE.json'),'model_spec':digest(destination / 'model_spec.json'),
                 'evidence':digest(destination / 'evidence.json'),'strict_parser':digest(HERE / 'parse_source_corrected.py'),
                 'independent_audit':digest(HERE / 'independent_source_audit.py')},
              'generation_budget':'No recovery attempt executed here. Initial six attempts remain spent; coordinator plans a separate three-native-attempt recovery ledger.'}
    dump(HERE / 'REPAIR_AUDIT.json', report)
    dump(destination / 'repair_audit.json', report)
    checks = {'scope':'source_only','records':[
        {'name':'all_active_source_coefficients_and_SEs','status':'pass','detail':'Independent direct-line extraction from exact pinned source verified all36 coefficient/SE pairs, model-specific locators,28 cells, dispersion, CSES SD and memory covariance inputs.'},
        {'name':'newline_and_duplicate_boundary_regressions','status':'pass','detail':'LF and CRLF give identical output; six malformed-boundary/duplicate/missing/unexpected-row fixtures are rejected without sampling.'},
        {'name':'recovery_scope','status':'pass','detail':'Only seven HbA1c coefficient/SE/provenance records and their source locators changed. Generator bytes, other parameters, dispersion and assumptions match preserved native candidate.'},
        {'name':'initial_native_preflight','status':'fail','detail':'Original PASS is overturned: CRLF-sensitive boundary failure silently mixed models. All original files and attempts remain preserved.'},
        {'name':'recovery_generated_quality','status':'not_computable','detail':'No recovery table or clinical fit has been produced. Requires coordinator release and separate bounded recovery ledger.'}],
        'artifacts':[{'path':'repair_audit.json','sha256':digest(destination / 'repair_audit.json')}]}
    dump(destination / 'checks.json', checks)
    (destination / 'SPEC.md').write_text('# Recovery v1 correction\n\nThe initial native preflight PASS was overturned after a CRLF section-boundary extraction defect was discovered. This package corrects only the seven Gamma HbA1c coefficients and SEs/provenance from the original pinned source. The generator bytes and scientific law are unchanged. See repair_audit.json and the recovery incident record.\n\n' + (original_candidate / 'SPEC.md').read_text(), encoding='utf-8', newline='\n')
    (destination / 'decision.md').write_text('# Native source-extraction recovery v1\n\nThe initial native package is invalid for the intended published HRS law: a CRLF-sensitive extraction boundary allowed later CSES/memory coefficient rows to overwrite seven Gamma HbA1c terms. The initial preparation PASS is overturned. Preserve the original six-attempt run and its outcomes; this is a separately identified technical recovery.\n\nCorrect the seven HbA1c coefficients, their SEs and source locators using only the pinned original Gamma table at lines 42–48. Mandatory model boundaries, duplicate rejection, LF/CRLF regression checks and an independent direct-line audit verify the correction. The full 36 source coefficient/SE pairs and all remaining active model parameters were checked. The generator remains byte-identical; no family, dispersion, covariance convention, sampling procedure or other model parameter changes. No output-based optimization or selection is performed.\n\nThe recovery author did not read generated rows, execute a generator or fit a clinical model. Root reported the initial failure; those outcomes are diagnostic context rather than a target used to choose corrections. Recovery generation, if released, has a new three-native-attempt ledger and leaves initial attempts spent. See SPEC.md and repair_audit.json.\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status':'pass','coefficient_SE_pairs':36,'malformed_inputs_rejected':len(failures_rejected),'candidate':str(destination),'corrected_hba1c':[v['estimate'] for v in parsed['hba1c']['coefficients'].values()],'generator_sha256':digest(destination/'generator.py'),'generation_calls':0},indent=2))


if __name__ == '__main__':
    main()
