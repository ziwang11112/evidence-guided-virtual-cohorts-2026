"""Seal the final code and aggregate reporting package, verifying original freeze."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    destination=ROOT/'delivery_manifest.json'
    if destination.exists(): raise FileExistsError('Preserve delivery; create a new revision explicitly')
    frozen=json.loads((ROOT/'freeze_v1/outputs_freeze.json').read_text(encoding='utf-8'))
    for path,expected in frozen['files'].items():
        if sha(path)!=expected: raise ValueError('Frozen artifact changed: '+path)
    files=['README.md','PROTOCOL.md','RESULTS.md','run_generation.py','seal_experiment.py',
           'literature_gateway.py','test_literature_gateway.py','test_generation_contract.py',
           'present_results.py','finalize_delivery.py','shared/schema.json','shared/target_description.md',
           'agent_clean/REQUEST.md','agent_clean/EVIDENCE_LEDGER.json','agent_clean/SEARCH_LOG.md',
           'agent_clean/INITIAL_DECISION.md','agent_clean/ARTIFICIAL_CHECKS.json','agent_clean/check_initial_artificial.py',
           'agent_clean/REVIEW_RESPONSE.md','agent_clean/SOURCE_LOCATOR_CORRECTION.json',
           'agent_clean/initial/generator.py','agent_clean/initial/model_spec.json',
           'review/evaluate.py','review/analysis_spec.json','review/frozen_analysis.json','review/test_evaluate.py',
           'review/check_initial_generator.py','review/initial_source_code_checks.json','review/INITIAL_SOURCE_CODE_REVIEW.md',
           'review/GATEWAY_REVIEW.md','review/INCIDENTS.md','freeze_v1/outputs_freeze.json','freeze_v1/evaluation_manifest.json',
           'review/postrun/independent_audit.py','review/postrun/audit_results.json',
           'review/postrun/independently_recomputed_endpoints.csv','review/postrun/AUDIT_REPORT.md',
           'review/postrun/SOURCE_ROLE_AUDIT.md','review/postrun/POSTRUN_AUDIT.md','review/postrun/report_v3_checks.json',
           'results/evaluation_v1/evaluation.json','results/evaluation_v1/endpoints.csv','results/evaluation_v1/draw_summaries.csv',
           'results/report_v3/ALL_ANALYSES.md','results/report_v3/scientific_interpretation.csv',
           'results/report_v3/correlations.json','results/report_v3/initial_v1_analyses.png',
           'results/report_v3/initial_v1_analyses.pdf','results/report_v3/VISUAL_QA.md']
    obj={'created_utc':datetime.now(timezone.utc).isoformat(),
         'status':'Complete: bounded whole-variable enrichment pilot and independent audit',
         'observed_rows':1700,'full_design_rows':2711,'agent_constructions':1,'generated_draws':20,
         'reference_plus_generated_fits':84,'endpoint_records':168,
         'output_freeze_sha256':sha(ROOT/'freeze_v1/outputs_freeze.json'),
         'all_original_freeze_files_unchanged':True,
         'no_target_informed_parameter_revision':True,
         'final_presentation':'results/report_v3',
         'privacy':'Row-level real, observed, mapped and synthetic data remain local. Public source download instructions are separate.',
         'findings':'Broad BMI association retained; reserved BMI curvature and sex-slope difference not recovered.',
         'files':{p:sha(ROOT/p) for p in files}}
    with destination.open('x',encoding='utf-8') as handle:
        json.dump(obj,handle,indent=2);handle.write('\n')
    print(json.dumps({'files_sealed':len(files),'delivery_sha256':sha(destination),
                      'original_freeze_unchanged':True},indent=2))


if __name__=='__main__': main()
