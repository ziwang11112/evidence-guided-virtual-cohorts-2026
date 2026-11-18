"""Prepare six fresh construction packets from previously curated evidence only."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
WORKSPACE = PROJECT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.contracts import validate_task

AUTHORS = ['HA','HB','HC','LA','LB','LC']

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():raise FileExistsError(dst)
    shutil.copyfile(src,dst)

def main():
    if (ROOT/'PROTOCOL.json').exists() or (ROOT/'bundles').exists():
        raise RuntimeError('Do not reset a prepared pilot')
    old=PROJECT/'work/evidence_use_cross_task_2026-11-05'
    base_skill=Path('D:/Codex/home/skills/evidence-cohort-generation')
    # Original instructions copied for all authors; operational contract below
    # narrows submission/execution in this construction-stage comparison.
    copy(base_skill/'SKILL.md',ROOT/'common/base_skill/SKILL.md')
    copy(base_skill/'references/harness-interface.md',ROOT/'common/base_skill/references/harness-interface.md')
    for f in (PROJECT/'experimental_skills/analysis-guided-cohort').rglob('*.md'):
        copy(f,ROOT/'skills/analysis-guided-cohort'/f.relative_to(PROJECT/'experimental_skills/analysis-guided-cohort'))
    guide=ROOT/'skills/analysis-guided-cohort/SKILL.md'
    with guide.open('a',encoding='utf8') as f:
        f.write('\n## Stable criteria and evidence-bearing actions\n\nKeep each requested analysis ID stable through the rubric and check record. Link a consequential choice to the criterion, the actual source or calculation, and the next action. After a change, name which dependent checks need repeating; a statement of intent is not a completed calculation. These workflow patterns are attributed in the pilot reuse note.\n')
    common_manifest={}
    for family,old_id in [('H','H01'),('L','L01')]:
        original=WORKSPACE/('evcUse'+old_id)
        curated=read(original/'CURATED_INPUTS.json')['sources']
        for entry in curated:
            assert sha(original/entry['path'])==entry['sha256']
        common_manifest[family]={'source_ids':sorted({x['source_id'] for x in curated}),
            'files':[{k:e[k] for k in ('path','source_id','sha256')} for e in curated]}
        for arm in ['A','B','C']:
            author=family+arm;bundle=ROOT/'bundles'/author;bundle.mkdir(parents=True)
            task=read(original/'task.json');task['task_id']='rubric-construction-pilot-2026-11-09-'+author
            task['information_policy']['allowed_tools']=['admitted_source_read','retained_analytic_calculation','contract_validation']
            task['budget']={'source_queries':0,'source_downloads':0,'revisions':0}
            validate_task(task);write(bundle/'task.json',task)
            write(bundle/'request.json',read(original/'request.json'))
            registry=[]
            for entry in curated:
                copy(original/entry['path'],bundle/entry['path'])
                registry.append({**entry,'origin':'curator'})
            write(bundle/'registry.json',{'artifacts':registry})
            if family=='L':copy(original/'input/population_metadata.json',bundle/'input/population_metadata.json')
            if arm!='A':copy(ROOT/'rubrics'/('GLYCEMIA.md' if family=='H' else 'LIPIDS.md'),bundle/'TASK_RUBRIC.md')
            allowed=['task.json','request.json','registry.json','sources/','input/ (when present)',
                'your four files under output/',
                '../../common/base_skill/SKILL.md and its linked interface reference']
            if arm!='A':allowed.append('TASK_RUBRIC.md')
            if arm=='C':allowed.append('../../skills/analysis-guided-cohort/SKILL.md and its linked procedure/rubric references')
            prompt=f'''# Scientific construction task {author}

Generate a whole virtual cohort for task.json and request.json using only the admitted source evidence. The full scientific questions are visible. No participant inputs or target statistics are supplied. This is a new developmental construction, not a request to recover an older model.

Read and apply the common base_skill instructions and all additional guidance supplied in your allowed-read list. When TASK_RUBRIC.md is supplied, use its criteria unchanged; if a reusable procedure skill is also supplied, apply it to those criteria rather than deriving a replacement rubric. If guidance cannot be applied, record why. For this pilot the following shared submission/execution contract replaces the full candidate-bundle submission steps: deliver exactly output/generator.py, output/model_spec.json, output/SOURCE_USE.json and output/DECISION.md. The root handles staging and isolated execution; do not call the old harness CLIs or create an old-style freeze. No source-feedback collector or literature adapter is available in this first construction pass. All arms use this same contract.

Allowed reads: {', '.join(allowed)}. Read the actual admitted content. Do not open old author bundles, other pilot author bundles, evaluation references, project READMEs/results, protocol/review files or external literature. A fresh context and these instructions are procedural boundaries, not technical filesystem isolation.

Choose the scientific law, relationships, scales, parameters and assumptions yourself. No desired sign, target value, preferred distribution, forced interaction or required revision is supplied. Use the requested units, population and all requested analyses. A missing relation may be represented by a justified explicit assumption; do not silently describe it as reported evidence. Distinguish source fit from population transfer.

Program ABI: synchronous generate(observed, specification, seed) returning a pandas DataFrame with the exact ordered task columns and exactly3000 rows. observed is None. The full model_spec.json object is passed unchanged; put scientific parameters in it and actually use them. Use NumPy/Pandas/standard library only (SciPy is unavailable in the worker). No filesystem, network or process access in the generator; no import-time execution beyond imports/definitions. A default_rng(seed) is appropriate. Return finite schema-valid measurements and unique string identifiers. Justify tails and support. Specify the complete law and source/assumption links in model_spec.json; no fixed schema beyond a JSON object is imposed here.

SOURCE_USE.json: record selected source IDs/locators, actual numerical uses or reasons declined, assumptions, and entries for all three requested analysis IDs. Include check results only if actually computed, with their artifacts. DECISION.md: concise scientific choices, unavailable checks and permitted uses. You may execute deterministic algebra as inline commands and retain the exact command and result in DECISION.md; do not create additional files, sample rows or import/execute the generator on the host. Do not claim a simulation or clinical validation was performed.

One construction response only, with ordinary pre-submission self-checking. No study-level numerical feedback, extra evidence, independently authored reviewer or output-informed revision is supplied. Three later fixed seed draws will be made from sealed bytes; do not optimize a seed. Prefer a concise complete deliverable to a long proposal. Record tools/actions actually used in DECISION.md. Finish with paths and unresolved issues. Token telemetry is not exposed by this interface; do not invent token counts or cost.
'''
            (bundle/'REQUEST.md').write_text(prompt,encoding='utf8')
    write(ROOT/'CURATED_INPUTS.json',common_manifest)
    copy(old/'ENDPOINT_CONTRACT.json',ROOT/'ENDPOINT_CONTRACT.json')
    p={'kind':'rubric_case_construction_pilot_v1','date':'2026-11-09','authors':AUTHORS,
       'seeds':[9301,9302,9303],'n_rows':3000,'max_final_tables':18,
       'limits':{'timeout_seconds':45,'memory_mb':1536,'output_bytes':20000000,'log_bytes':50000},
       'revision_rounds':0,'sampling_trials_before_seal':0,
       'cases':{'H':'ENSANUT2018','L':'Turkana'},
       'arms':{'A':'current_skill_construction','B':'current_skill_plus_supplied_task_rubric','C':'current_skill_plus_same_rubric_and_reusable_procedures'},
       'authoring':'One fresh inherited-model author per arm and case; source-only construction in minimal shared interface.',
       'source_access':'Fixed previously curated inputs only; no new acquisition.',
       'feedback':'None during this construction-stage pilot; no legacy or semantic source collector is invoked.',
       'reference_read_after':'All six authors closed and final artifact bytes sealed; root has historical aggregate exposure.',
       'development_only':True,'new_patient_reads':False,
       'budget_comparison':'Same author-response count, source access, tools, output route and draw schedule. Actual token use not instrumented or enforced; not an exact compute-matched superiority test.',
       'scope_limitations':['One author per arm/case confounds arm with author variation.','Repeated seeds are draws from a single authored law, not independent author replications.','Same previously exposed references; no new clinical confirmation.','No test of autonomous rubric induction or feedback revision.'],
       'operational_schema':'Minimal four-artifact construction interface shared by all arms; not exact replay of previous full controller workflow.'}
    write(ROOT/'PROTOCOL.json',p)
    oldp=read(old/'PROTOCOL.json');write(ROOT/'REFERENCE_BINDINGS.json',oldp['references'])
    print(json.dumps({'authors':6,'cases':2,'max_tables':18,'sources':{k:len(v['files']) for k,v in common_manifest.items()},'new_downloads':0}))

if __name__=='__main__':main()
