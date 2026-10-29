"""Copy an explicit aggregate/code allowlist; never copy participant tables.

Run after the independent audit is complete. This is an inspection package,
not a standalone runnable copy of the frozen execution bundle.
"""
from pathlib import Path
import hashlib
import json
import re

E = Path(__file__).resolve().parent
P = E.parents[1]
OUT = P / 'reports/structure_robustness_2026-10-28'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    OUT.mkdir(exist_ok=False)
    mapping = {}
    def add(src, dst=None):
        path = E / src
        assert path.is_file(), path
        mapping[dst or src] = path

    for f in ['protocol.json', 'protocol_commitment.json', 'structure_plan_commitment.json',
              'evaluation_commitment.json', 'release_verification.json', 'controller.py',
              'release_guard.py', 'summarize_results.py', 'POSTRUN_AUDIT.md', 'curate_results.py',
              'finalize_validation.py']:
        add(f)
    for f in ['STRUCTURE_PLAN.json', 'REVISION_PLAN.json', 'INITIAL_READY.json', 'FINAL_READY.json',
              'task.json', 'registry.json', 'measurement_note.md', 'build_structures.py',
              'prepare_finals.py', 'freeze_initials.py', 'freeze_finals.py']:
        add('agent_bundle/' + f, 'builder/' + f)
    # Top-level candidate artifacts are code, specifications, aggregate feedback,
    # evidence records and freezes. Context CSVs and full sources stay local.
    for s in ('s1', 's2', 's3'):
        for stage in ('initial', 'final'):
            name = f'{s}_{stage}'
            for path in sorted((E / 'agent_bundle/candidates' / name).iterdir()):
                if path.is_file() and path.suffix in ('.py', '.json', '.md'):
                    add(path.relative_to(E).as_posix(), f'candidates/{name}/{path.name}')
    for path in sorted((E / 'source_feedback').glob('*.json')):
        add(path.relative_to(E).as_posix())
    for path in sorted((E / 'review').iterdir()):
        if path.is_file() and path.suffix in ('.py', '.json', '.md'):
            add(path.relative_to(E).as_posix())
    for f in ['analysis_protocol.json', 'protocol_freeze.json', 'methods_freeze.json',
              'methods_freeze_attempt1.json', 'preparation_decode_amendment.json',
              'custodian_lock.json', 'preparation_receipt.json', 'data_provenance.json',
              'fresh_overlap_inventory.json', 'guard_validation_receipt.json',
              'survey_analysis.py', 'evaluate_committed.py', 'prepare_case.py',
              'preparation_decode_attempt1.py', 'test_custodian_guard.py']:
        add('custodian/' + f, 'methods/' + f)
    for f in ['reference_analyses.json', 'endpoint_comparison.csv', 'direction_robustness.json',
              'nonestimable_sensitivities.json', 'report_notes.json', 'result_hashes.json',
              'release_receipt.json']:
        add('custodian/evaluation/' + f, 'evaluation/' + f)
    for f in ['structure_summary.csv', 'structure_summary.json', 'structural_robustness.png',
              'structural_robustness.pdf']:
        add('summaries/' + f, 'summaries/' + f)

    prefixes = [(str(P.parents[1]), '<LOCAL_WORKSPACE>'),
                (str(Path('<LOCAL_USER>')), '<LOCAL_USER>'),
                ('<LOCAL_LINUX_USER>', '<LOCAL_LINUX_USER>')]
    replacements = []
    for original, replacement in prefixes:
        for variant in {original, original.replace('\\', '/'), original.replace('\\', '\\\\')}:
            replacements.append((variant, replacement))
    replacements.sort(key=lambda x: -len(x[0]))
    records = []
    for relative, original in sorted(mapping.items()):
        data = original.read_bytes()
        exported = data
        changes = 0
        if original.suffix in ('.json', '.md', '.py', '.csv'):
            text = data.decode('utf-8-sig')
            for prefix, replacement in replacements:
                count = text.count(prefix)
                if count:
                    text = text.replace(prefix, replacement)
                    changes += count
            if changes:
                exported = text.encode('utf-8')
            # Unknown local paths must be reviewed rather than silently dropped.
            assert not re.search(r'(?i)[CD]:[\\/]|<LOCAL_LINUX_USER>|/mnt/[cd]/', text), relative
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(exported)
        records.append({'path': relative, 'original_sha256': sha(data),
                        'curated_sha256': sha(exported), 'path_replacements': changes})
    (OUT / 'curation_provenance.json').write_text(json.dumps({
        'scope': 'Explicit aggregate and implementation inspection allowlist; no participant rows.',
        'normalization': 'Local filesystem prefixes replaced only in copied inspection artifacts; original frozen files untouched. Original hashes inside receipts remain original hashes.',
        'records': records}, indent=2) + '\n', encoding='utf-8')
    (OUT / 'README.md').write_text('''# M5 structural alternatives: inspection package

The complete outcomes are reported, including source-fit failures and inconclusive target analyses. See the project-level MILESTONE_5_RESULTS.md.

This package contains all six candidate specifications/programs, aggregate source diagnostics, the locked analysis protocol, execution commitments, all released analysis results and independent audit. It excludes participant-level real/observed/generated tables, synthetic source-context rows, full-text papers, runtime configuration and temporary fixtures. The public data URLs and provenance are retained in methods/data_provenance.json; evidence records retain publication locators.

Local filesystem prefixes are replaced in copied inspection metadata where necessary. curation_provenance.json binds every original and copied hash and counts replacements. The original frozen trees and receipts remain unchanged locally. Hash fields inside copies still identify original artifacts. This is not a portable frozen execution bundle: omitted inputs, original directory layout, task registry, runtime and retained code versions are needed for full replay. No one-command reproduction from this folder is claimed.

Figures show survey uncertainty for the real reference and only simulation variation for generated data. Five draws are not five independent Agent builds or cohorts. S3 remains source-challenged; S2 has an unresolved BMI rank-association discrepancy. The alternative structures share source-informed assumptions.
''', encoding='utf-8')
    manifest = {p.relative_to(OUT).as_posix(): sha(p.read_bytes()) for p in sorted(OUT.rglob('*')) if p.is_file()}
    (OUT / 'file_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(manifest) + 1, 'normalized_files': sum(x['path_replacements'] > 0 for x in records)}))

if __name__ == '__main__':
    main()
