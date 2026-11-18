"""Read-only scientific claim reconciliation; writes only this new audit unit.

No provider calls, generator execution, patient/generated rows, reference fitting,
credential reads, or modification of frozen studies.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import csv,json,hashlib
R=Path(__file__).resolve().parent
P=R.parents[1]
W=P/'work'
S=W/'two_round_synthesis_2026-11-10'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvrows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def locator(relative,needle,meaning):
    p=P/relative;lines=p.read_text(encoding='utf-8').splitlines()
    hits=[i+1 for i,l in enumerate(lines) if needle in l]
    assert hits,(relative,needle)
    return {'path':relative,'sha256':sha(p),'line':hits[0],'needle':needle,'supports':meaning}
def main():
    attempts=csvrows(S/'ATTEMPTS.csv');analyses=csvrows(S/'ANALYSIS_RESULTS.csv')
    fixed=[]
    for x in analyses:
        if x['kind']=='initial' and x['analysis_id']=='bmi_sbp' and x['seed_mean']:
            u=json.loads(x['reference_uncertainty']);m=float(x['seed_mean'])
            fixed.append({'study':x['round'],'construction':x['version_id'],'model_config':x['model_config'],'mean':m,
                'inside_saved_reference_interval':u['lower']<=m<=u['upper'],'interval':u})
    autonomous=[];stages=[]
    names=['request_only_agent_pilot_2026-11-10','request_only_agent_repair_2026-11-10','request_only_agent_capacity_2026-11-10','request_only_repeatability_2026-11-11']
    for name in names:
        d=W/name;e=read(d/'EVALUATION.json');plan=read(d/'PLAN.json')
        stages.append({'study':name,'sessions':len(plan['episodes']),'counts':e['counts'],'evaluation_sha256':sha(d/'EVALUATION.json')})
        for x in e['summaries']:
            if x['case_id']=='PNS' and x['analysis_id']=='bmi_sbp':
                m=x['mean'];u=x['reference']['uncertainty']
                autonomous.append({'study':name,'construction':x['episode_id'],'mean':m,'available_seeds':x['available_seeds'],
                   'inside_saved_reference_interval':u['lower']<=m<=u['upper'] if m is not None else None,'interval':u})
    assert len(fixed)==9 and sum(x['inside_saved_reference_interval'] for x in fixed)==8
    assert sum(x['mean'] is not None for x in autonomous)==9
    assert sum(x['inside_saved_reference_interval'] is True for x in autonomous)==3
    lipid=[x for x in analyses if x['kind']=='initial' and x['analysis_id']=='K02-LIPID-RESIDUAL' and x['seed_mean']]
    groups=[]
    for roundset in [('R1',),('R1','R2')]:
        for claude in [False,True]:
            z=[x for x in lipid if x['round'] in roundset and (x['model_config']=='CL_FABLE')==claude]
            groups.append({'rounds':list(roundset),'group_definition':'Claude' if claude else 'non-Claude',
               'n':len(z),'mean_of_construction_means':sum(float(x['seed_mean']) for x in z)/len(z),
               'members':[{'round':x['round'],'construction':x['version_id'],'mean':float(x['seed_mean'])} for x in z],
               'not_a_copying_annotation':True})
    cbase='work/cross_model_api_pilot_2026-11-10/candidates/'
    locators=[
      locator(cbase+'LIPID_DS_PRO_C1/decision_record.json','Midpoint of the two reported Spearman correlations','The adopted0.14 is a rounded midpoint of0.106/0.171, not verbatim copying one source number.'),
      locator(cbase+'LIPID_DS_PRO_C1/decision_record.json','Spearman rank correlations are not Pearson','Explicit recognition of operator, adjustment and population mismatch.'),
      locator(cbase+'LIPID_DS_PRO_C1/model_spec.json','"pearson_correlation": 0.14','Actual encoded residual parameter0.14.'),
      locator(cbase+'LIPID_DS_PRO_C1/generator.py',"rho = float(resid['pearson_correlation'])",'Actual common-factor program realizes the selected residual Pearson correlation under its fixed law.'),
      locator(cbase+'LIPID_OA_SOL_C1/decision_record.json','deliberately not used as raw Pearson','Low-dependence counterexample: explicitly rejects substituting the source ranks.'),
      locator(cbase+'LIPID_OA_SOL_C1/decision_record.json','0.5*0.3=0.15','Chosen common-factor loadings independently imply0.15, with realized mean~0.139.'),
      locator(cbase+'LIPID_OA_SOL_C1/generator.py',"load = np.asarray(l['shared_factor_loading']",'Actual program uses common-factor error loadings, not the source rank directly.'),
      locator(cbase+'LIPID_CL_FABLE_C1/decision_record.json','Chosen 0.35','Claude selects a judgment compromise involving a part-whole argument and unresolved source scale.'),
      locator(cbase+'LIPID_CL_FABLE_C2/decision_record.json','The value 0.0 is this deliberate compromise','Non-copy comparison still uses Ghana evidence through an informal bridge; not absence of indirect evidence.'),
      locator(cbase+'LIPID_CL_FABLE_C2/generator.py','tc = hdl + non','Actual component construction induces TC-HDL correlation; structural change confounds any copied/noncopied split.'),
      locator(cbase+'LIPID_DS_PRO_C2/generator.py',"for attempt in range(int(lip['max_attempts_per_row']))",'Positivity selection means proposal correlation need not equal final residual correlation.'),
      locator('work/economy_feedback_pilot_2026-11-10/calls/initial/PNS_ASTRA/artifact.json','The nonzero BMI component','An actual nonzero adjustment bridge changes source-scaled slopes; scientific sophistication does not guarantee closer target agreement.'),
      locator('work/cross_model_api_pilot_2026-11-10/calls/LIPID_DS_PRO_C1_initial/prompt.txt','A reported unadjusted, differently adjusted','Prompt explicitly instructs preserving/acknowledging mismatch; acknowledgment is not spontaneous evidence of calibrated awareness.'),
      locator('work/cross_model_api_pilot_2026-11-10/calls/LIPID_DS_PRO_C1_initial/prompt.txt','You may make explicit assumptions','Completing a scenario with acknowledged assumptions is permitted, not automatically instruction violation.'),
      locator('work/two_round_synthesis_2026-11-10/RESULTS_SUMMARY.md','32 API requests','Exact two-round unit count28 initial attempts plus4 dependent reviews.'),
      locator('work/two_round_synthesis_2026-11-10/RESULTS_SUMMARY.md','21 complete initial API artifacts','Twenty-one complete artifacts but20 data-delivering initial laws; one execution failure.'),
    ]
    claims=[
      {'id':'C1','claim':'18 verbatim-adoption constructors;17 acknowledge mismatch','verdict':'not independently established as a reproducible count',
       'finding':'No reviewed annotation ledger defining these18/17 membership decisions was supplied or located in the bounded synthesis/provenance records. The two-round universe has21 complete initial artifacts and20 delivering laws, not18 total. Several exact source anchors coexist with transformations or assumptions within one construction; an any-number-copy label is not an analysis-level operator label.',
       'counterexample':'DeepSeek C1 maps an averaged/rounded Spearman value to residual Pearson. Sol C1 rejects that map yet chooses an assumed residual0.15. Claude also uses the same source ranks through a different compromise.',
       'required_before_publication':'A frozen construction-by-analysis annotation rule, exact eligible/failed denominators, inclusion list, code/notes locators and independent adjudication. Do not backfill18/17 from keyword counts or performance.'},
      {'id':'C2','claim':'DeepSeek uses unadjusted Ghana Spearman as adjusted residual (~.15 versus.51)','verdict':'supported with an important numerical/semantic correction',
       'finding':'R1 LIPID_DS_PRO_C1 encodes0.14 as residual Pearson after averaging0.106/0.171 and rounding. It openly labels the transfer assumption. The realized three-seed mean is0.15072223345205538; reference0.5120696931296308. This shows an acknowledged but unvalidated bridge, not verbatim adoption, concealment, or proof that the bridge solely caused error.'},
      {'id':'C3','claim':'Copied lipids~.13 versus noncopied~.35','verdict':'approximate numerical split reproducible only as a confounded model grouping',
       'finding':'First-round non-Claude six versus Claude two means are near.13/.36; across both rounds non-Claude nine average.121465 and Claude two.357538. There is no defensible copying label from these outcomes. Sol C1 is a direct counterexample to equating low residual correlation with rank substitution. Both Claude authors use judgment, changed dispersions and altered structures, while also citing indirect source evidence.',
       'required_interpretation':'Describe specific bridge/structure choices and results; do not claim copying causes attenuation or not-copying repairs it from this grouping.'},
      {'id':'C4','claim':'PNS fixed-packet9authors8withinCI versus autonomous9authors3','verdict':'numerically reproducible for a narrowly defined descriptive endpoint',
       'finding':'Eight of nine delivered fixed-packet BMI-SBP construction means fall inside the saved2.960887–4.119257 interval. Three of nine delivered autonomous means do so. This is not an all-endpoint success rate; the interval is conditional IID row-resampling stability, not a national design-based CI or equivalence margin.',
       'confounders':['Different model mixes: fixed-packet GPT configurations plusDeepSeek versus autonomous GPT Sol only.','Different source sets, search freedom, prompts, interfaces, resource ceilings and sequential stages.','Autonomous denominator excludes three nondelivered PNS sessions; fixed denominator excludes five nondelivered PNS initial attempts.','Source selection, bridge decisions and population assumptions co-vary; no randomized isolation of curation or indirectness.','Same already exposed clinical reference and shared source families; constructors are not independent clinical studies.']},
      {'id':'C5','claim':'Three tasks,about60constructions,four model families','verdict':'requires a scope ledger; not established by the named units',
       'finding':'The two API pilots cover2contexts(PNS,lipids),28initial attempts plus4dependent review sessions,5configurations spanning4provider families. Only3provider families deliver data; Gemini contributes delivery failures. The four request-only units add24initial authoring sessions,20 selected data-delivering laws. Combined this is56sessions=52initial attempts+4dependent reviews,40data-delivering initial laws, across the same2contexts. Adding the latest24dependent scientific-review sessions makes80sessions, not80independent constructions. There are3primary analyses per context,6across both; this is not3dataset tasks.',
       'scope_limit':'Older CHNS/iron/etc experiments exist but were not reannotated or re-counted here. A broader three-task/~60 claim may use another population of records; it cannot be validated by mixing those with API sessions without an explicit ledger.'}
    ]
    report={'status':'complete_bounded_audit','created_utc':datetime.now(timezone.utc).isoformat(),
      'scope':'Primary artifacts/code read in detail for5first-round lipid constructions(DeepSeekC1/C2,ClaudeC1/C2,SolC1) and1second-roundPNS Astra; full existing two-round audit maps consulted; all specified comparison aggregates enumerated. This is NOT a fresh annotation of60constructions.',
      'patient_or_generated_rows_read':False,'new_api_calls':0,'new_generator_runs':0,'clinical_refits':0,'credential_files_read':False,
      'input_bindings':{str(p.relative_to(P)):sha(p) for p in [S/'ATTEMPTS.csv',S/'ANALYSIS_RESULTS.csv',S/'LIPID_PARAMETER_MAP.json',S/'PNS_PARAMETER_MAP.json']},
      'claims':claims,'supporting_locators':locators,'fixed_pns_sbp_units':fixed,'autonomous_pns_sbp_all_attempts':autonomous,'lipid_model_group_summaries':groups,
      'request_only_stage_counts':stages,
      'two_round_counts':{'all_sessions':len(attempts),'initial_attempts':sum(x['kind']=='initial' for x in attempts),'dependent_reviews':sum(x['kind']=='review' for x in attempts),'initial_delivered_laws':sum(x['kind']=='initial' and x['law_delivery']=='delivered' for x in attempts),'initial_artifact_execution_failures':sum(x['kind']=='initial' and x['law_delivery']=='execution_failed' for x in attempts)},
      'scientific_takeaway':'Evidence indirectness is a useful organizing axis, but distinguish operator conversion, population transport, latent dependency completion, source selection and implementation. Acknowledged assumptions can be coherent scenario choices; annotations need to evaluate the bridge and intended claim, not merely the presence of a mismatch warning or source number. Existing records support examples and hypotheses, not a validated universal indirectness-error law.'}
    with (R/'local_claim_audit.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
    lines=['# Bounded local audit of the evidence-indirectness review','',
      'This is a read-only review of existing artifacts and aggregate results, not a new experiment or a completed annotation of60constructions. Six consequential programs/decision records were read directly; the existing two-round parameter maps and all comparison-unit aggregates were inspected. No patient/generated rows, API calls, generator executions, reference refits or credential files were used.','',
      '| Claim | Audit conclusion |','|---|---|']
    for c in claims:lines.append(f"| {c['claim']} | **{c['verdict']}**. {c['finding']} |")
    lines+=['','## Most useful corrected example','',
      'DeepSeek lipid C1 explicitly maps the average of two Ghana unadjusted Spearman correlations,0.106 and0.171, to an assumed adjusted Pearson residual correlation0.14. It acknowledges the scale, conditioning and population gaps. Its generated three-seed mean is0.1507 versus sample reference0.5121. This is an informative case of an acknowledged bridge that remains unvalidated. It is not verbatim copying and does not establish that the bridge alone caused the target mismatch.','',
      'GPT Sol lipid C1 explicitly refuses that rank-to-residual substitution. It nevertheless chooses shared-factor loadings0.5 and0.3, yielding assumed residual correlation0.15 and generated mean0.1388. Claude C1 instead chooses0.35 using an informal part-whole/source compromise; Claude C2 generates HDL+non-HDL, implying about0.3813. All have unverified bridges. Therefore “copied” versus“not copied” is not a valid binary explanation of the observed low/high split.','',
      'The common prompt already requires explicit unverified assumptions and warns against equating rank/unadjusted/source statistics with target conditional quantities. An acknowledgment rate therefore partly measures compliance with the prompt. It is not evidence of spontaneous metacognitive calibration, and use of an explicit scenario assumption was permitted.','',
      '## Exact PNS comparison units','',
      '| Source group | Stage | Construction | BMI–SBP mean | Inside saved reference interval |','|---|---|---|---:|---|']
    for x in fixed:lines.append(f"| Fixed packet | {x['study']} | {x['construction']} | {x['mean']:.6f} | {x['inside_saved_reference_interval']} |")
    for x in autonomous:
        m='unavailable' if x['mean'] is None else f"{x['mean']:.6f}"
        lines.append(f"| Autonomous | {x['study']} | {x['construction']} | {m} | {x['inside_saved_reference_interval']} |")
    lines+=['','The8/9versus3/9 contrast concerns only delivered BMI–SBP means, not all requested analyses. The saved interval is conditional IID row-resampling stability, not a design-based national confidence interval or equivalence margin. Model, source, budget, tool-interface and delivery-selection differences prevent a causal claim about curation or indirectness.','',
      '## Support and inspection boundary','',
      '| Artifact | Locator | Supports |','|---|---|---|']
    for x in locators:lines.append(f"| `{x['path']}` | Line{x['line']} | {x['supports']} |")
    lines+=['','Source hypotheses, derived quantities and assumed completions should be annotated per requested analysis, with separate axes for operator/adjustment mismatch, population/measurement transport, unreported joint dependence and implementation changes. Freeze these rules without using realized error to assign labels. Preserve failed deliveries and dependent review versions separately.','',
      '**Recommendation:** use indirectness to sharpen the scientific narrative and define a small reproducible annotation audit. Do not publish18/17, the copied/noncopied causal interpretation, or a three-task/~60-scale statement until exact eligible records and coding rules are supplied. The current evidence supports several informative examples and confounded descriptive contrasts; it does not yet establish a predictive indirectness score or general error mechanism.']
    with (R/'local_claim_audit.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    print(json.dumps({'status':report['status'],'audit_sha256':sha(R/'local_claim_audit.json'),'fixed_inside':sum(x['inside_saved_reference_interval'] for x in fixed),'fixed_delivered':len(fixed),'autonomous_inside':sum(x['inside_saved_reference_interval'] is True for x in autonomous),'autonomous_delivered':sum(x['mean'] is not None for x in autonomous),'claims':len(claims)}))
if __name__=='__main__':main()
