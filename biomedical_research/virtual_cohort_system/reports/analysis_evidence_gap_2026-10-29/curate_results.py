"""Create an inspection-only package without rows, full papers or runtime."""
from pathlib import Path
import json
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import read_json, sha256

C = P / 'reports/analysis_evidence_gap_2026-10-29'
records = []


def normalize(data, protected=False):
    changes = 0
    if not protected:
        text = data.decode('utf-8-sig')
        replacements = [(str(E), '<local_m7>'), (str(P), '<project>'),
                        (str(P.parents[1]), '<workspace>'), ('<local_codex>', '<local_codex>'),
                        ('<local_python_runtime>', '<local_python_runtime>')]
        for original, replacement in replacements:
            forward = original.replace('\\', '/')
            forms = {forward} | {forward.replace('/', '\\' * n) for n in (1, 2, 4, 8)}
            for form in sorted(forms, key=len, reverse=True):
                changes += text.count(form)
                text = text.replace(form, replacement)
        data = text.encode('utf-8')
    return data, changes


def copy(relative, destination=None):
    src, dst = E / relative, C / (destination or relative)
    # Scientific program/spec bytes and frozen candidate receipt bytes stay exact.
    protected = src.name in {'generator.py', 'model_spec.json', 'freeze.json'}
    data, changes = normalize(src.read_bytes(), protected)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open('xb') as stream:
        stream.write(data)
    records.append({'source_relative': relative, 'curated_relative': dst.relative_to(C).as_posix(),
                    'original_sha256': sha256(src), 'copied_sha256': sha256(dst),
                    'path_replacements': changes, 'scientific_bytes_preserved': protected})


def new(relative, data):
    path = C / relative
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    record = read_json(E / 'retention_freeze.json')
    if record['status'] != 'passed' or not record['scientific_bytes_unchanged']:
        raise ValueError('Retention is not frozen')
    C.mkdir(parents=True, exist_ok=False)
    for relative in ['baseline_import.json', 'source_admission.json', 'visible_attachment.json',
                     'stage_decision.json', 'retention_freeze.json', 'prepare_bundle.py',
                     'finish_visible_setup.py', 'admit_sources.py', 'record_stage_decision.py',
                     'freeze_retention.py', 'curate_results.py', 'finalize_validation.py']:
        copy(relative)
    for name in ['candidate_evidence.json', 'evidence_gap_map.md', 'retrieval_log.md',
                 'source_artifact_manifest.json', 'supplement_retry_log.jsonl',
                 'build_retained_candidate.py', 'validate_retention.py']:
        copy('research/' + name)
    for name in ['interface_review.md', 'FULL_HARNESS_TESTS.json', 'CUSTODIAN_AUDIT.md',
                 'CUSTODIAN_AUDIT_CHECKS.json', 'RETENTION_AUDIT.md', 'RETENTION_AUDIT_CHECKS.json']:
        copy('review/' + name)
    # Custodian metadata, methods and corrections only, never its table or raw files.
    for name in ['analysis_protocol.json', 'custodian_lock.json', 'custody_qa_receipt.json',
                 'download_hash_log.json', 'evaluate_committed.py', 'method_validation.json',
                 'novelty_audit.json', 'preparation_amendment.json', 'preparation_receipt_attempt1.json',
                 'preparation_receipt.json', 'prepare_case.py', 'protocol_freeze_attempt1.json',
                 'protocol_freeze.json', 'setup_protocol.py', 'survey_analysis.py', 'validate_methods.py']:
        copy('custodian/' + name, 'methods/' + name)
    for name in ['measurement_note.md', 'preparation_counts.json', 'task_metadata.json', 'input_hashes.json']:
        copy('visible/nhanes_tg_f/' + name, 'visible_metadata/' + name)
    copy('agent_bundle/task.json', 'builder/task.json')
    copy('agent_bundle/registry.json', 'builder/registry.json')
    for label in ['baseline', 'evidence_augmented']:
        prefix = 'agent_bundle/candidates/' + label + '/'
        for name in ['generator.py', 'model_spec.json', 'evidence.json', 'analysis_evidence.json',
                     'decision.md', 'checks.json', 'freeze.json', 'source_replay.json', 'source_checks.json']:
            copy(prefix + name, 'candidates/' + label + '/' + name)
        if label == 'evidence_augmented':
            copy(prefix + 'revision.json', 'candidates/' + label + '/revision.json')
            for src in sorted((E / prefix / 'research_audit').glob('*')):
                if src.is_file() and src.suffix in {'.json', '.jsonl', '.md'}:
                    copy(src.relative_to(E).as_posix(), 'candidates/' + label + '/research_audit/' + src.name)
    readme = '''# M7 inspection package

Analysis-specific evidence declarations, source review, a frozen scientific no-op and a reserved public-data case. No new scientific generator run, source replay or target evaluation was performed.

The two candidate generator/specification files are byte-identical. New literature is recorded as partial/contextual evidence, not as calibrated target parameters. Maps were constructed after the source search; this is not a preregistered autonomous search-policy trial.

This reduced archive excludes participant/observed/hidden tables, source-context rows, full articles, runtime settings, caches and unsuccessful pytest scratch directories. Prior candidate check artifacts are historical and are not all duplicated here. Full freeze verification/replay requires the original local bundle and omitted inputs. The custodian evaluator is planned and not released; its known rank-failure/reporting issue is recorded in the audit. Unexecuted controller drafts are not exported.

`curation_provenance.json` binds original and copied files. Some copied metadata/code paths are normalized; internal historical hashes still describe the original local bytes. Frozen candidate receipts and scientific code/specification files are preserved verbatim. `file_manifest.json` hashes every other file in this package. No one-command replay claim is made.

See the project-level MILESTONE_7_RESULTS.md and m7_validation.json for status and scope.
'''
    (C / 'README.md').write_text(readme, encoding='utf-8')
    new('curation_provenance.json', {'scope': 'inspection_only', 'records': records})
    new('file_manifest.json', {p.relative_to(C).as_posix(): sha256(p)
                              for p in sorted(C.rglob('*')) if p.is_file()})
    print(json.dumps({'files': sum(p.is_file() for p in C.rglob('*')), 'copied_records': len(records),
                      'normalized_files': sum(r['original_sha256'] != r['copied_sha256'] for r in records)}))


if __name__ == '__main__':
    main()
