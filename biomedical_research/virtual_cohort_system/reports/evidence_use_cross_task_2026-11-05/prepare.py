"""Prepare new source-only bundles. No model, generator, clinical fit or draw."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parent
P = ROOT.parents[1]
W = P.parents[1]
sys.path.insert(0, str(P))
from cohort_harness import lifecycle
from cohort_harness.contracts import validate_task
from cohort_harness.literature import run_literature


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return lifecycle.read_json(path)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(target)
    shutil.copyfile(source, target)


def main():
    bundles = {name: W/('evcUse'+name) for name in ['H01','H02','H03','L01','L02','L03']}
    if (ROOT/'PROTOCOL.json').exists() or any(path.exists() for path in bundles.values()):
        raise RuntimeError('Preparation already exists; do not reset bundles or budgets')
    h_template = W/'evcRepE01'
    h_sources = W/'evcIncE01'
    l_template = P/'work/scaleup_2026-11-01/case_k02/request'
    h_request = read(h_template/'request.json')
    l_metadata = read(ROOT/'admission/LIPID_CONSTRUCTOR_TASK_METADATA.json')
    h_task = read(h_template/'task.json')
    l_task = read(l_template/'task_template.json')
    h_registry = [r for r in read(h_sources/'registry.json')['artifacts']
                  if not r['source_id'].startswith('search-')]
    lipid_packets = sorted((ROOT/'admission/sources').glob('*_CURATOR_EXTRACTION.json'))
    if len(lipid_packets) != 3:
        raise RuntimeError('Expected the three reviewed lipid studies')
    endpoint_source = P/'work/core_workflow_replication_2026-11-04/ENDPOINT_CONTRACT.json'
    h_endpoints = read(endpoint_source)['cases']['ENSANUT2018']
    l_analyses = [
        {'id':'K02-HDL-BMI','unit':'mg/dL per 5 kg/m^2'},
        {'id':'K02-TC-BMI','unit':'mg/dL per 5 kg/m^2'},
        {'id':'K02-LIPID-RESIDUAL','unit':'1'}]
    l_diagnostics = []
    for col, unit in [('age','year'),('bmi','kg/m^2'),
                      ('total_cholesterol','mg/dL'),('hdl_cholesterol','mg/dL')]:
        l_diagnostics.extend({'id':col+'.'+suffix,'unit':unit}
                             for suffix in ['mean','sd_sample','q10','q50','q90'])
    l_diagnostics += [{'id':col+'.conditional_rms','unit':'mg/dL'}
                      for col in ['total_cholesterol','hdl_cholesterol']]
    l_diagnostics += [{'id':'sex.F_fraction','unit':'1'}]
    endpoints = {'schema_version':1, 'cases':{'ENSANUT2018':h_endpoints,
                'Turkana':{'analyses':l_analyses,'diagnostics':l_diagnostics}},
                 'reference_mapping':'Only identical published estimator definitions; unmatched aggregate diagnostics unavailable'}
    write(ROOT/'ENDPOINT_CONTRACT.json', endpoints)
    interface_docs = ['ANALYSIS_EVIDENCE.md','SEMANTIC_FEEDBACK_V1.md','WHOLE_COHORT_FEEDBACK.md',
                      'LITERATURE_ADAPTER.md','EXECUTION_ADAPTER.md','EVIDENCE_USE_V1.md']
    interface_files = []
    for name in interface_docs:
        source = P/'docs'/name
        copy(source, ROOT/'interfaces'/name)
        interface_files.append({'path':'interfaces/'+name,'source_sha256':sha(source),
                                'copy_sha256':sha(ROOT/'interfaces'/name),'omissions':None})
    source = P/'docs/EVIDENCE_ACTIONS_V1.md'
    text = source.read_text(encoding='utf-8-sig').split('## Current use and next integration')[0]
    (ROOT/'interfaces/EVIDENCE_ACTIONS_V1.md').write_text(text, encoding='utf-8')
    interface_files.append({'path':'interfaces/EVIDENCE_ACTIONS_V1.md','source_sha256':sha(source),
                            'copy_sha256':sha(ROOT/'interfaces/EVIDENCE_ACTIONS_V1.md'),
                            'omissions':'Historical use/next-integration and outcome paragraphs excluded'})
    write(ROOT/'INTERFACE_MANIFEST.json', {'files':interface_files,'purpose':'Constructor interface-only packet'})
    authors = {}
    for name, bundle in bundles.items():
        is_h = name.startswith('H')
        case = 'ENSANUT2018' if is_h else 'Turkana'
        task = json.loads(json.dumps(h_task if is_h else l_task))
        task['task_id'] = 'evidence-use-cross-task-2026-11-05-'+name
        task['n_rows'] = 3000
        if not is_h:
            for c in task['columns']:
                if c['name'] in ('bmi','total_cholesterol','hdl_cholesterol'):
                    c['minimum'] = 5e-324
        task['information_policy']['excluded_cohorts'] = [
            'CHNS','China Health and Nutrition Survey','ENSANUT','Encuesta Nacional de Salud y Nutricion',
            'Turkana target study','Lea et al. 2020 Turkana','10.1126/sciadv.abb1430','10.5061/dryad.2z34tmpjk']
        task['information_policy']['allowed_tools'] = [
            'literature.search','literature.fetch','admitted_source_read','contract_validation',
            'controller_source_feedback','retained_analytic_calculation']
        task['budget'] = {'source_queries':4,'source_downloads':2,'revisions':1}
        validate_task(task)
        bundle.mkdir()
        write(bundle/'task.json', task)
        if is_h:
            request = h_request
        else:
            request = {'mode':'whole_cohort','population':task['population'],'n_rows':3000,
                       'individual_input':False,'intended_analyses':l_metadata['analyses'],
                       'metadata':'input/population_metadata.json','desired_signs_or_values':None,
                       'estimator':'Unweighted OLS; M reference for sex, intercept, age10=(age-50)/10 and bmi5=(bmi-25)/5; Pearson residual TC-HDL after same full design',
                       'units':'Delivered lipids mmol/L; evaluation multiplies each by38.67 to mg/dL; slopes per5 BMI',
                       'diagnostics':l_diagnostics}
            copy(ROOT/'admission/LIPID_CONSTRUCTOR_TASK_METADATA.json',bundle/'input/population_metadata.json')
        write(bundle/'request.json',request)
        artifacts=[]
        provenance=[]
        if is_h:
            for record in h_registry:
                source=h_sources/record['path']
                if sha(source)!=record['sha256']: raise RuntimeError('Curated source bytes changed')
                copy(source,bundle/record['path'])
                artifacts.append({**record,'origin':'curator'})
                provenance.append({'path':record['path'],'source_id':record['source_id'],
                                   'sha256':record['sha256'],'admission':'Previously reviewed original/source extraction reused unchanged; no model or result copied'})
        else:
            for source in lipid_packets:
                data=read(source); path='sources/curated/'+source.name
                copy(source,bundle/path)
                artifacts.append({'source_id':data['curator_source_id'],'path':path,'sha256':sha(source),
                                  'origin':'curator','screening':'approved'})
                provenance.append({'path':path,'source_id':data['curator_source_id'],'sha256':sha(source),
                                   'admission':'Reviewed original-statistic curator extraction, not a full-text gateway receipt'})
        write(bundle/'registry.json',{'artifacts':artifacts})
        write(bundle/'CURATED_INPUTS.json',{'sources':provenance,'target_statistics_supplied':False})
        write(bundle/'SEARCH_LEDGER.json',{'author_id':name,'actions':[],
              'instruction':'Log actual optional acquisition and source choices; do not replace task-bound gateway session'})
        prompt = f'''# Scientific constructor {name}

Create full biomedical virtual data for the research request in request.json and task.json. All supplied individual-input fields are absent; choose the entire joint law. Do not inspect other author bundles, old candidates/results, current project summaries, evaluation files, patient records or work outside this allowlist. Fresh context is a procedural boundary, not tool isolation.

Allowed inputs: this bundle's task.json, request.json, registry.json, CURATED_INPUTS.json, input/, sources/, your own new candidates and gateway returns; the evidence-cohort-generation SKILL and harness interface; {ROOT.as_posix()}/interfaces/ documentation; static schema/API code cohort_harness/contracts.py, analysis_evidence.py and evidence_use_v1.py. Read the actual sources, not just their bibliographic labels. Curated extractions describe reported facts; you may qualify or decline their use. They do not assign target parameters.

You have at most four gateway query credits and two new original downloads, failed actions counted; admitted sources are already available. Optional search must address a concrete missing relationship/definition. Use cohort_harness.literature.run_literature with this bundle and its existing session. Do not bypass exclusions through another tool, reset the session, or retrieve patient records. Acquisition closes at first freeze. If no suitable further evidence is available, keep the assumption visible and construct within that scope.

Choose structure, parameters, transformations, dependence and variability yourself. A source slope, marginal SD, conditional SD, correlation and scale ratio are different constraints. State which quantity, if any, you assume transfers to the target and why. No desired sign, exact reference match, forced distribution family, or requirement to change a model is supplied. A review cannot identify missing target relations.

First produce SOURCE_REVIEW_REQUEST.md and PROPOSED_CONSTRUCTION.md with source locators, values/units/adjustment/selection/uncertainty and unresolved assumptions. Do not yet write a candidate or execute code generating rows. Obtain controller scientific review. Then write candidates/initial: evidence.json, model_spec.json, generator.py, decision.md, checks.json, analysis_evidence.json, whole_cohort_feedback.json, source_semantics_v1.json, evidence_use_v1.json. Each requested analysis must have an evidence-use decision; map actual parameters/checks/assumptions. Generator code must actually use its specification. Use finite-moment laws and schema-valid outputs, justify truncation or transformations scientifically. Record only checks actually executed. The generator entrypoint is generate(observed, specification, seed); root executes it in the existing isolated adapter. No local random draws or unsandboxed generator execution.

This pilot uses the program route. One initial trial9100, at most one revised/repair trial9110, then final draws9101/9102/9103 from one final frozen candidate. Errors consume slots. After initial trial source/generated-only feedback, retain or propose one concrete revision. Extraction/definition/implementation errors are valid reasons, as is qualified source feedback. Preserve the history and visibility of changed assumptions. If revision trial fails, a previously valid initial candidate may be retained with a documented reason before delivery. No changes after delivery starts. No target results enter feedback; unsupported source operators remain unavailable. No additional scenario draws.

Return concise scientific decisions and files, not private reasoning traces. Keep all failure records and limits. No training, paid APIs, HPC or new clinical acquisition.
'''
        (bundle/'AUTHOR_TASK.md').write_text(prompt,encoding='utf-8')
        init=run_literature(bundle,'init')
        if init.get('status')!='ok': raise RuntimeError(init)
        provider = (P/'work/main_study_freeze_2026-11-03/cases/ENSANUT2018/generated_feedback.py') if is_h else ROOT/'lipid_provider.py'
        profile=ROOT/'cases'/case/'profile.json'
        if not profile.exists():
            write(profile,{'case_id':case,'information_condition':'open_evidence',
                           'analysis_ids':[x['id'] for x in endpoints['cases'][case]['analyses']]})
        authors[name]={'bundle':str(bundle),'case_id':case,'provider':str(provider),'profile':str(profile),
                       'task_sha256':sha(bundle/'task.json'),'request_sha256':sha(bundle/'request.json'),
                       'analysis_ids':[x['id'] for x in endpoints['cases'][case]['analyses']],
                       'curated_source_ids':sorted({a['source_id'] for a in artifacts})}
    references={
        'ENSANUT2018':{'path':str(P/'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json'),
                      'selector':['references','ENSANUT2018']},
        'Turkana':{'path':str(P/'work/scaleup_2026-11-01/production_release/evaluation/PUBLISHABLE_AGGREGATES.json'),
                   'selector':['references','K02']}}
    for reference in references.values(): reference['sha256']=sha(reference['path'])
    protocol={'kind':'evidence_use_cross_task_v1','date':'2026-11-05','authors':authors,
              'trial_seeds':{'initial':9100,'revision':9110},'final_seeds':[9101,9102,9103],
              'limits':{'timeout_seconds':30,'memory_mb':1536,'output_bytes':20000000,'log_bytes':100000},
              'max_physical_executions':30,'max_feedback_revisions':1,'n_rows':3000,
              'acquisition':{'per_author_queries':4,'per_author_new_original_downloads':2,
                             'curated_sources_separate':True,'close_at':'initial freeze'},
              'references':references,'reference_read_after':'all six author sessions closed',
              'exposed_development':True,'new_patient_reads_planned':False,
              'feedback_adapter':'semantic_feedback_v1','evidence_use_adapter':'evidence_use_v1',
              'dependencies':[str(ROOT/'controller_evidence_use.py'),str(ROOT/'lipid_provider.py'),
                 str(P/'work/scaleup_2026-11-01/analysis/k02_analysis.py'),
                 str(P/'work/autonomous_research_cycle2_2026-10-31/analysis/analytical_engine.py')],
              'claim':'Final-data capability across two requests, not controlled workflow superiority',
              'repair_policy':'Optional second trial is shared by scientific revision and mechanical repair; no retries. Failed revision may retain already-valid initial before final draws. Final bytes fixed.'}
    write(ROOT/'PROTOCOL.json',protocol)
    print(json.dumps({'bundles':list(authors),'prepared_only':True,'generation_attempts':0}))


if __name__=='__main__': main()
