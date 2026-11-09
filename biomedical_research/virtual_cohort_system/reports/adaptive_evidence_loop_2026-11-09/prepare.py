"""Create a fresh source-only adaptive construction bundle; never reset it."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
WORKSPACE = PROJECT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.request_intake import prepare_request
from cohort_harness import lifecycle

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')

def main():
    old = WORKSPACE / 'evcUseL01'
    bundle = WORKSPACE / 'evcAdaptiveL02'
    task = read(old/'task.json')
    task['task_id'] = 'adaptive-evidence-lipid-development-2026-11-09'
    task['budget'] = {'source_queries': 32, 'source_downloads': 32, 'revisions': 1}
    task['information_policy']['allowed_tools'] += ['isolated_generation', 'generated_analysis', 'semantic_feedback_v1', 'descriptive_feedback_v1', 'web.fetch', 'native_web_discovery', 'literature.list-supplements', 'literature.fetch-supplement']
    old_request = read(old/'request.json')
    request = {
        'schema_version': 1,
        'purpose': 'Generate a whole virtual adult cohort from external published evidence and target-population methods metadata, to support the three requested scientific analyses. No individual input or target-result calibration is supplied.',
        'analyses': [json.dumps(a, sort_keys=True) for a in old_request['intended_analyses']],
        'task': task,
    }
    prepare_request(request, bundle)
    registry = []
    for e in read(old/'CURATED_INPUTS.json')['sources']:
        source = old/e['path']
        if sha(source) != e['sha256']: raise ValueError('Curated source changed')
        dest = bundle/e['path']; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        registry.append({'source_id': e['source_id'], 'path': e['path'], 'sha256': e['sha256'],
                         'origin': 'curator', 'screening': 'approved'})
    (bundle/'registry.json').write_text(json.dumps({'artifacts':registry},indent=2)+'\n',encoding='utf-8')
    (bundle/'input').mkdir()
    shutil.copyfile(old/'input/population_metadata.json',bundle/'input/population_metadata.json')
    shutil.copytree(PROJECT/'experimental_skills/analysis-guided-cohort',bundle/'skills/analysis-guided-cohort')
    shutil.copytree(Path('D:/Codex/home/skills/evidence-cohort-generation'),bundle/'skills/evidence-cohort-generation')
    lifecycle._registry(bundle)
    protocol = {
        'unit': 'adaptive_evidence_loop_2026-11-09', 'status':'prospective_protocol',
        'case':'existing lipid selected-adult context', 'bundle':str(bundle),
        'reason_selected':'Conditional joint evidence and source/target population mismatch make it useful for testing adaptive evidence-directed actions; no selection for a favorable outcome.',
        'purpose':'Operationally connect retrieval, Agent-authored generation, generated-data analysis, semantic feedback and voluntary revision; evaluate final data usefulness.',
        'author_count':1, 'fresh_context':True, 'author_independence':'procedural allowlist, not OS isolation',
        'candidate_cap':2, 'rows_per_output':3000, 'seeds':[9501,9502,9503],
        'execution_cap':6, 'max_actions':64, 'source_queries':32,'source_downloads':32,
        'source_budget_note':'Question-directed retrieval; paper count is not a sufficiency criterion. Generous shared legacy counters remain a transport ceiling. Public web additionally limits 64 MiB received and 40 HTTP requests. Native web discovery is external and separately logged; unmetered search traffic is not included in gateway byte totals.',
        'runtime_limits':{'timeout_seconds':45,'memory_mb':1536,'output_bytes':20000000,'log_bytes':50000},
        'agent_freedom':['search timing and query','evidence selection','model and parameter choices','program or direct rows','optional skills','new diagnostics','retain, revise, or stop'],
        'required_analyses':old_request['intended_analyses'],
        'required_diagnostics':old_request['diagnostics'],
        'stage_protocol':'Freeze each submitted candidate. Run all three predetermined seeds and retain all output/feedback. Revisions may use only admitted evidence and generated-only checks. No retry of a candidate/seed pair. No forced revision.',
        'feedback_entrypoint':'cohort_harness.adaptive_session_v2 (strict semantic v1 plus descriptive v1)',
        'source_feedback_interpretation':'Retain strict verdict and add calculation/definition-match/applicability diagnostics. Explicit conventional assumptions permit descriptive comparisons, not promotion to exact source replay or target validity.',
        'scientific_review':'Audit selected evidence locators, units, estimands and source applicability. Root does not supply scientific parameters or desired relation signs.',
        'evaluation':'After author finishes and final selection is sealed, apply the same requested analyses to all candidates/seeds and compare with existing frozen aggregate reference, including unfavorable analyses. Independently recompute.',
        'claims':['developmental existing-case exercise','not new clinical confirmation','seed spread is Monte Carlo variation, not a clinical CI','one adaptive author cannot establish general causal efficacy','direct rows repeated under seeds are the same table, not independent draws'],
        'stop':['Agent retains/stops','budget exhausted','integrity or infrastructure failure requires review','no new case or target calibration in this unit'],
        'privacy':'Individual generated/real rows and full third-party source artifacts stay local; reviewed original code/docs/aggregates only may be public.'
    }
    write(ROOT/'PROTOCOL.json', protocol)
    write(ROOT/'INITIAL_INPUTS.json', {p.relative_to(bundle).as_posix():sha(p) for p in bundle.rglob('*') if p.is_file()})
    write(ROOT/'STATE.json',{'phase':'bundle_prepared_awaiting_v2_review','clinical_executions':0,'target_results_given_to_author':False,'development_case':True})
    print(json.dumps({'bundle':str(bundle),'source_artifacts':len(registry),'clinical_executions':0}))

if __name__ == '__main__': main()
