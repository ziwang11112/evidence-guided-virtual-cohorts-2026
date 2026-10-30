"""Controller-curated evidence admission and visible bundle assembly.

Only reads published source artifacts and visible covariates; never opens a
custodian reference. Admission decisions follow the root's independent review
of the primary tables and methods on 2026-10-29. Not a generator or evaluator.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.contracts import validate_task, validate_input, validate_evidence
from analytical_points import normalize_visible


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def restriction(item):
    sid, iid = item['source_id'], item['id']
    if iid.startswith('ship_healthy_'):
        return 'withheld_numeric_conflict', 'SHIP Table 3 disagrees with abstract/Par23 for older-group upper limits. Preserve original proposal; exclude the full healthy-reference family pending resolution.'
    if sid == 'direct2017' and not iid.endswith('_baseline_HbA1c'):
        return 'prospective_structure_only', 'Follow-up HbA1c equation with additional covariates; not a direct contemporaneous age/sex/BMI equation.'
    if sid == 'fhs2022' and 'longitudinal' in iid:
        return 'longitudinal_standardized_context', 'Repeated-measure standardized log-insulin association; not a cross-sectional raw coefficient.'
    if sid == 'fhs2022' and 'cross_sectional' in iid:
        return 'standardized_missing_covariates', 'Requires outcome/predictor scale information and omitted adjustment variables; waist is not BMI.'
    if sid == 'fhs2022' and 'insulin_' in iid:
        return 'source_assay_units_only', 'Reported pmol/L; no unverified common assay conversion to task uU/mL.'
    if sid == 'macad2011' and '_std_' in iid:
        return 'standardized_GEE_missing_covariates', 'Conditional on clamp/clearance/waist variables; not an unadjusted BMI effect.'
    if sid == 'macad2011' and iid.endswith('_iqr'):
        return 'IQR_width_only', 'IQR is a width, not SD or quartile endpoint; any distributional conversion is an assumption.'
    if sid == 'hoorn2020' and iid.endswith('_coef'):
        return 'conditional_adjustment_restricted', 'Includes fasting/postload glucose, waist/hip and lifestyle; do not transplant to a three-covariate model.'
    if sid == 'dasa2024':
        return 'selected_healthy_reference_only', 'Healthy BMI/glycemia/medication-selected and statistically truncated source; not a target-population tail constraint.'
    return 'source_context_quantitative', 'Use only with the recorded source population, measurement, selection, scale and adjustment; target transport remains an assumption.'


def main():
    evidence_root = ROOT / 'evidence'
    proposal = json.loads((evidence_root/'candidate_packet.json').read_text(encoding='utf-8'))
    for source in proposal['sources']:
        assert digest(evidence_root/source['path']) == source['sha256'], source['source_id']
    outcomes = []
    for case, filename in [('nhanes_insulin','fasting_insulin_evidence.json'),('pns_hba1c','hba1c_evidence.json')]:
        original = json.loads((evidence_root/filename).read_text(encoding='utf-8'))
        task = json.loads((ROOT/case/'task.json').read_text(encoding='utf-8'))
        validate_task(task)
        validate_evidence(original,task)
        decisions = []
        included = []
        for item in original['items']:
            status, reason = restriction(item)
            decisions.append({'evidence_id':item['id'], 'status':status, 'reason':reason})
            if status != 'withheld_numeric_conflict':
                included.append(item)
        admitted = original | {'items':included}
        validate_evidence(admitted,task)
        dest = ROOT/'bundles'/case
        if dest.exists():
            raise FileExistsError('Assembly is append-only; use a new version rather than overwrite '+str(dest))
        dest.mkdir(parents=True)
        visible = ROOT/case/'visible'
        for name in ['observed.csv','task_metadata.json','field_map.json']:
            shutil.copy2(visible/name,dest/name)
        shutil.copy2(ROOT/case/'task.json',dest/'task.json')
        observed = pd.read_csv(dest/'observed.csv',dtype={task['row_id']:'string'})
        validate_input(observed,task)
        normalized = normalize_visible(observed,case)
        assert len(normalized) == task['n_rows']
        registry=[]
        for source in admitted['sources']:
            for artifact in source['artifacts']:
                src=evidence_root/artifact['path']; target=dest/artifact['path']
                assert digest(src)==artifact['sha256']
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(src,target)
                registry.append({'source_id':source['id'],'path':artifact['path'],
                                 'sha256':artifact['sha256'],'origin':'curator','screening':'approved'})
        write_json(dest/'registry.json',{'artifacts':registry})
        write_json(dest/'admitted_evidence.json',admitted)
        admission={'status':'curator_admitted_with_item_restrictions',
                   'reviewer':'root controller; separate from source extraction agent',
                   'review_basis':'Primary source tables, SHIP Par20/Par23, model methods and scale/selection footnotes independently read; source and proposal hashes verified; existing task schema validation passed.',
                   'original_proposal_sha256':digest(evidence_root/filename),
                   'admitted_count':len(included),'withheld_count':len(original['items'])-len(included),
                   'items':decisions,'source_overlap':proposal['overlap'],
                   'limitations':'Admission verifies traceable extraction and use restrictions, not target transport or joint identification. Source-check operators may not support adjusted/standardized statistics.',
                   'target_outcomes_read':False,'scientific_generator_executed':False}
        write_json(dest/'source_admission.json',admission)
        (dest/'USE_BOUNDARY.md').write_text('''# Shared evidence construction input

Use only this bundle and the separately supplied common/arm instructions. The same bundle bytes must be supplied to every construction arm. Admitted numeric evidence is in admitted_evidence.json; source_admission.json supplies mandatory interpretation restrictions and quarantined IDs. Full texts provide context; unadmitted numbers need separate curator review and cannot silently become calibration targets. The generator may declare assumptions, but must not relabel a prohibited or incompatible reported coefficient as a directly supported target effect.

Target outcomes, exact reserved analyses, raw survey files, ID links, design weights and other constructions are unavailable. Source and observed inputs are local; no autonomous retrieval was tested by preparing this curated packet. Hashing is integrity protection, not confidentiality or proof of scientific validity. No required association direction or generator family is supplied.
''',encoding='utf-8')
        files={f.relative_to(dest).as_posix():digest(f) for f in sorted(dest.rglob('*')) if f.is_file()}
        write_json(dest/'input_manifest.json',{'scope':'shared builder input only; no outcomes or construction', 'files':files})
        outcomes.append({'case':case,'n_rows':task['n_rows'],'sources':len(admitted['sources']),
                         'proposed_items':len(original['items']),'admitted_items':len(included),
                         'withheld_items':len(original['items'])-len(included),'visible_contract':'passed',
                         'analysis_adapter':'passed','bundle':str(dest.relative_to(ROOT))})
    write_json(ROOT/'review/source_admission_summary.json',{'cases':outcomes,'target_outcomes_read':False,'generation_run':False})
    print(json.dumps(outcomes))


if __name__ == '__main__':
    main()
