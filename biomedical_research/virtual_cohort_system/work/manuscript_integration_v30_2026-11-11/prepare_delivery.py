"""Prepare a versioned reading-edition build; never alter experiment artifacts."""
from pathlib import Path
import hashlib
import json

PROJECT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANUSCRIPT = PROJECT / 'manuscript'
OLD = MANUSCRIPT / 'methods_draft_v29_2026-11-11'
NEW = MANUSCRIPT / 'methods_draft_v30_2026-11-11'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    NEW.mkdir(exist_ok=True)
    preserve = [MANUSCRIPT / 'DRAFT_v0_29.md', OLD / 'paper.pdf',
                OLD / 'overleaf_v29.zip', OLD / 'paper.tex', OLD / 'BUILD_QA.json']
    for stage in ('request_only_repeatability_2026-11-11', 'scientific_check_revision_2026-11-11'):
        for name in ('PROTOCOL.md', 'RESULTS.md', 'STATE.json', 'EVALUATION.json',
                     'ANALYSIS_RESULTS.csv', 'MANUSCRIPT_INSERT.md'):
            path = PROJECT / 'work' / stage / name
            if path.exists():
                preserve.append(path)
    preserve.extend((MANUSCRIPT / 'paper_figures_v29_2026-11-11').glob('*'))
    bindings = {p.relative_to(PROJECT).as_posix(): digest(p) for p in preserve if p.is_file()}
    receipt = HERE / 'REVISION_FACTS.json'
    if receipt.exists():
        old = json.loads(receipt.read_text(encoding='utf8'))
        assert old['preserved_inputs'] == bindings, 'A preserved input changed since preparation.'
    else:
        receipt.write_text(json.dumps({'version': '0.30', 'base_version': '0.29',
            'preserved_inputs': bindings, 'new_api_calls': 0, 'new_generated_tables': 0,
            'new_patient_analyses': 0, 'public_sync': False}, indent=2) + '\n', encoding='utf8')
    for name in ('build_review_copy.py', 'compile_review.py', 'verify_review_copy.py', 'OVERLEAF_README.md'):
        content = (OLD / name).read_text(encoding='utf8')
        content = content.replace('v0.29', 'v0.30').replace('v0_29', 'v0_30').replace('v29', 'v30')
        content = content.replace('work/manuscript_revision_v30_2026-11-11/',
                                  'work/manuscript_integration_v30_2026-11-11/')
        if name == 'build_review_copy.py':
            content = content.replace("'S20.', 'S21.'", "'S20.', 'S21.', 'S22.', 'S23.'")
        (NEW / name).write_text(content, encoding='utf8')
    (HERE / 'STATE.json').write_text(json.dumps({
        'status': 'integrating_completed_results', 'manuscript_version': '0.30',
        'scope': 'Application and scientific-analysis utility; no evidence-indirectness pivot.',
        'new_api_calls': 0, 'new_generated_tables': 0, 'new_patient_analyses': 0,
        'public_sync': False, 'old_frozen_artifacts_preserved': True,
        'pending': ['content integration', 'figure and numeric audit', 'PDF and standalone ZIP build',
                    'visual review', 'current-focus update']}, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'build_directory': str(NEW), 'preserved_files': len(bindings)}))

if __name__ == '__main__':
    main()
