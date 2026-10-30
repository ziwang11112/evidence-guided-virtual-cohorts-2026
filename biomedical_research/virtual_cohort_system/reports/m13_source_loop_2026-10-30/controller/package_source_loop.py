"""Curate source-only inputs, decisions and every diagnostic, without raw papers."""
from pathlib import Path
import hashlib
import json
import shutil

P=Path(__file__).resolve().parents[2]
W=P/'work/m13'
R=P/'reports/m13_source_loop_2026-10-30'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def cp(src,dst):
    dst=Path('\\\\?\\'+str(dst.resolve()))
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
    assert digest(src)==digest(dst)


def tree(src,dst):
    for f in src.rglob('*'):
        if f.is_file() and '__pycache__' not in f.parts:
            cp(f,dst/f.relative_to(src))


def package():
    for name in ['build01','build02']:
        assert json.loads((W/name/'agent_exchange/loop_completion.json').read_text())['promoted']
    before=json.loads((W/'engine_hashes_before.json').read_text())
    assert all(digest(P/'cohort_harness'/n)==sha for n,sha in before.items())
    R.mkdir(exist_ok=False)
    for f in ['controller_campaign.md','construction_request_template.txt','review_request_template.txt',
              'prepare_source_pilot.py','run_source_session.py','finish_review.py','summarize_source_runs.py',
              'package_source_loop.py','engine_hashes_before.json']:
        cp(W/f,R/'controller'/f)
    for f in ['candidate_audit.md','postrun_audit.json','protocol_review.md']:
        cp(W/f,R/'audits'/f)
    tree(W/'source_results',R/'results')
    for f in (W/'packet').iterdir():
        if f.is_file() and f.suffix in {'.json','.md'}:cp(f,R/'source_packet'/f.name)
    tree(W/'packet/screened_sources',R/'source_packet/screened_sources')
    for name in ['build01','build02']:
        b=W/name;out=R/name
        for f in ['task.json','registry.json','observed.csv']:cp(b/f,out/f)
        for folder in ['sources','allowed_inputs','agent_exchange','candidates','calibration_budget','scientific_loop']:
            tree(b/folder,out/folder)
        session=b/'cal/initial_fit'
        for f in session.iterdir():
            if f.is_file():cp(f,out/'cal/initial_fit'/f.name)
        for t in sorted(session.glob('t[0-9]*')):
            cp(t/'trial.json',out/'cal/initial_fit'/t.name/'trial.json')
            for replay in (t/'source_replays_v2').iterdir():
                if replay.is_dir():cp(replay/'replay.json',out/'cal/initial_fit'/t.name/'source_replays_v2'/replay.name/'replay.json')
    description='''# M13-A curated source-only review archive

This archive contains actual Agent candidates, source covariate inputs, all18 constraints, all18 numerical trial summaries, all720 diagnostic records, source replay reports, decisions, calibration/loop ledgers, and the failed pre-freeze source reconstruction with its repair. `observed.csv` files are invented qualification grids. `source_contexts/*.csv` are reconstructed numerical integration covariates. They are not patient records. No target dataset or target outcome is included.

Excluded: downloaded full paper/PDF/page-render cache; Python runtime/cache; duplicated nested execution child bundles; bulk source-generated row tables. The complete original runs remain in local `work/m13/build01` and `build02`. This is a curated review archive, not a complete receipt-verification filesystem: original `verify_calibration` / `verify_loop` calls need the omitted child execution bundles. Aggregate and candidate-file hashes remain directly checkable here. The independent audit recomputed statistics from the actual local generated source tables before curation; it is not a claim that those tables are present in this export.

For a fresh numerical reproduction, copy one build's task.json, registry.json, observed.csv, sources/, allowed_inputs/ and candidates/initial/ into a NEW bundle, preserving relative paths and bytes. Do not copy old calibration/loop ledgers into the new run. Use the unchanged project's `calibration_budget.create_budget` with allowed_inputs/controller_contract.json budget_limits, then `calibration.run_calibration` with the initial proposed_calibration_plan.json and a fresh session ID. Supply a trusted, installed WSL/bubblewrap runtime configuration; never import the generator on the host. Existing code/specification and source covariates are sufficient to regenerate the source tables. Reproduction is a new execution, not a rewrite of the original receipts. The controller scripts are retained as original task orchestration records; their local work paths require adaptation for a fresh destination.

The candidate builder/computation uses Python, NumPy and pandas as recorded in execution reports; covariate reconstruction scripts also use their explicitly imported numerical libraries. No model training or API credential is needed to rerun a frozen generator. Repeating the Agent construction itself requires an actual model invocation and can produce a different scientific model.

The planned target evaluator in audits/protocol_review.md has not been frozen or run. Source agreement is not evidence of target analytical utility. See ../../MILESTONE_13A_RESULTS.md for results and limits.
'''
    (R/'README.md').write_text(description,encoding='utf-8')
    files={f.relative_to(R).as_posix():digest(f) for f in sorted(R.rglob('*')) if f.is_file()}
    manifest={'scope':'real-source Agent loop; no target participant data','files':files,
              'core_engine_bytes_unchanged':before,'file_count':len(files),
              'source_execution_records_complete_in_original_work':True,
              'export_is_full_execution_receipt_archive':False,
              'raw_source_documents_or_patient_rows_exported':False}
    (R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'files':len(files),'bytes':sum(f.stat().st_size for f in R.rglob('*') if f.is_file()),
                     'engines_preserved':len(before),'directory':str(R)},indent=2))


if __name__=='__main__':package()
