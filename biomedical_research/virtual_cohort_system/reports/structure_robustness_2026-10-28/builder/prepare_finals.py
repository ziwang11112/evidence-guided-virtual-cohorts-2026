"""One source-only revision/retention round. No generator execution permitted."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import math
import shutil
import sys

P=Path(__file__).resolve().parent
FEEDBACK=P.parent/'source_feedback'
sys.path.insert(0,str(P.parents[2]))
from cohort_harness.__main__ import validate_bundle
from cohort_harness.contracts import validate_spec,validate_evidence
from cohort_harness.lifecycle import verify_candidate,validate_program
from cohort_harness.source_checks import run_source_checks
from cohort_harness.source_replay import _check_metadata,_input_task

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,obj): Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

assert sha(FEEDBACK/'initial_compact.json')=='f3503e8c5ca13e1db4a851c0e6e79e0f9ee7f78fa42ffd2f4cb4b72084985a94'
compact=read(FEEDBACK/'initial_compact.json')
assert len(compact['checks'])==138
portfolios={}
report_paths={}
for sid in ['s1','s2','s3']:
    c=P/'candidates'/(sid+'_initial')
    verify_candidate(P,c)
    f=FEEDBACK/(sid+'_initial_portfolio.json')
    portfolio=read(f)
    listed=next(x for x in compact['portfolios'] if x['structure']==sid)
    assert sha(f)==listed['sha256']
    assert portfolio['parent']['freeze.json_sha256']==sha(c/'freeze.json')
    assert len(portfolio['checks'])==46
    assert [x['seed'] for x in portfolio['schedule']]==[76101,76102,76103]
    report_paths[sid]=[]
    for entry in portfolio['schedule']:
        path=P/'source_replays'/entry['replay_id']/'replay.json'
        assert sha(path)==entry['sha256']
        report=read(path)
        assert report['status']=='success'
        assert report['parent']['candidate']=='candidates/'+sid+'_initial'
        assert all(ctx['generation_link_verified'] for ctx in report['contexts'])
        assert sum(len(ctx['checks']) for ctx in report['contexts'])==46
        report_paths[sid].append(path)
    portfolios[sid]=portfolio

DECISIONS={
 's1':dict(kind='revise',reason='One source-conditioned sensitivity revision relaxes the common BMI slope into sex-specific slopes. It addresses excessive Bansal BMI dependence while retaining an algebraic anchor to the pooled Oh slope and marginal moments. This does not identify true sex-specific effects.',
   addressed_findings=['All 46 initial checks reviewed: 12 covariate-only checks and 34 outcome-related checks. Input-only agreement is construction fidelity, not TG validation.',
     'Bansal BMI Spearman 0.439490 versus 0.33; first/third TG-tertile BMI means 23.4466/28.3857 versus 24.2/27.6. These persistent discrepancies motivate a lower assumed female BMI response.',
     'Oh pooled BMI OLS 6.83398 versus 6.813 and sex-specific mean/SD summaries were already close. Preserve the published pooled slope analytically by balancing the unreported male/female slopes using published within-sex BMI variances and counts; recalculate residual CV from the same source moment formula.',
     'Keep age slopes unchanged. Bansal age Spearman 0.140326 versus 0.18 does not imply a uniquely larger conditional age effect: TG-tertile age mean separation already approximates the source and conditional age SDs differ.'],
   remaining_limitations=['Female slope 5.2 and derived male slope are unreported, assumption-dependent coefficients. Unknown age-BMI dependence, omitted variables and selection may cause the shared rank discrepancy; the change does not resolve that ambiguity.',
     'Reducing the female BMI slope lowers Bansal-context arithmetic location by approximately 4.68 mg/dL before floor/residual effects. Initial quantiles 79.039/115.560/168.450 were close to 81/115/169; location/quantile agreement may worsen.',
     'Oh threshold discrepancies, particularly the male tail, remain. Exact fitting of the single original female >500 observation is not justified.',
     'No final numerical compatibility claim before controller replay. All original source/assay/context/transport limitations remain.']),
 's2':dict(kind='retain',reason='Retain the nonlinear multiplicative structure with no code or parameter change. Its source tradeoffs are unresolved; available marginal and reverse-conditional summaries do not uniquely determine a defensible correction under unknown joint covariates.',
   addressed_findings=['All 46 initial checks reviewed: 12 covariate-only checks and 34 outcome-related checks; source input agreement is not outcome evidence.',
     'Bansal age Spearman 0.181453 versus 0.18 and quantiles 77.527/113.948/167.480 versus 81/115/169 are relatively close; conditional age SDs and means still have discrepancies.',
     'Bansal BMI Spearman 0.468363 versus 0.33 and TG-tertile BMI means 23.3836/25.9211/28.5292 versus 24.2/25.9/27.6 show excessive dependence.',
     'Oh means 140.171/95.734 versus 141.6/97.2, SDs 104.483/58.908 versus 107.7/61.0 and OLS 6.27378 versus 6.813 are modestly low; threshold discrepancies are retained.'],
   remaining_limitations=['Retention is not a compatibility pass. Strong BMI dependence persists beyond seed variation; unknown source joint distribution and model shape cannot be separated from these diagnostics alone.',
     'Reducing BMI response or increasing residual dispersion can change the already close source quantiles, age rank and Oh moments/slopes. No compensating biological effects or latent covariate correlations are invented.',
     'The age transition, BMI saturation, source assay proxy and target transport remain assumptions.']),
 's3':dict(kind='retain',reason='Retain this two-state gamma parameterization only as an explicitly source-challenged structural sensitivity. It is not declared numerically source-compatible. Aggregate feedback does not identify replacement state means, dispersions or probabilities without several new choices.',
   addressed_findings=['All 46 initial checks reviewed: 12 covariate-only checks and 34 outcome-related checks; all discrepancies remain visible.',
     'Oh means 142.026/97.098 and SDs 107.920/61.726 approximate 141.6/97.2 and 107.7/61.0, but pooled BMI OLS 5.76386 is below 6.813 and category shapes disagree.',
     'Bansal quantiles 70.021/99.931/182.092 versus 81/115/169 and lower-tertile fraction 0.438355 versus 0.327567 expose a substantial central-distribution mismatch, not Monte Carlo fluctuation.',
     'Bansal BMI Spearman 0.460650 versus 0.33 and TG-tertile BMI means 23.6054/25.8824/28.8951 versus 24.2/25.9/27.6 overstate dependence. Age rank is low and extreme-tertile age SDs differ.'],
   remaining_limitations=['This source challenge applies to the submitted parameterization, not to every latent mixture. No clinical two-state interpretation is established.',
     'Moving component means closer or changing overlap could affect median/IQR, thresholds, source moments and dependence simultaneously. The available aggregate evidence does not uniquely support a one-shot replacement.',
     'All final structures are retained for the fixed evaluation schedule; no model winner or target-feedback selection is made.']),
}


def category(row):
    c=row['check']
    if c.startswith('e_oh_') and any(c.endswith(suffix) for suffix in ['_age_mean','_age_sd','_bmi_mean','_bmi_sd']):
        return 'input_only'
    if c in ['e_bansal_age_mean','e_bansal_age_sd','e_bansal_bmi_mean','e_bansal_bmi_sd']:
        return 'input_only'
    if row['context']=='oh' and row['kind']=='ols_coefficient': return 'oh_conditional_slope'
    if row['context']=='oh' and row['kind'] in ['mean','sd']: return 'oh_tg_moments'
    if row['context']=='oh': return 'oh_tg_categories'
    if row['kind'] in ['median','quantile']: return 'bansal_tg_quantiles'
    if row['kind']=='spearman_correlation': return 'bansal_marginal_rank'
    if row['kind']=='proportion': return 'bansal_tg_categories'
    return 'bansal_covariates_conditional_on_tg'


NOTES={
 'input_only':'Approximate reconstruction agrees by design. These are fixed observed inputs and are not evidence that TG generation is valid.',
 'oh_conditional_slope':'Compare the same reduced age/sex-adjusted OLS estimand, subject to family-design approximation. Do not substitute fully adjusted or co-twin coefficients.',
 'oh_tg_moments':'Source arithmetic marginal mean or individual SD. Agreement does not imply correct rank dependence, conditional distribution or tails.',
 'oh_tg_categories':'Threshold differences persist and expose distribution shape. Cumulative categories are dependent; extreme-tail source counts are sparse.',
 'bansal_tg_quantiles':'Original quantiles retained with linear-estimator approximation; location and dispersion tradeoffs are considered together, not as an aggregate score.',
 'bansal_marginal_rank':'A marginal rank statistic, not a regression coefficient. Dependence discrepancies are larger than seed variation but source joint covariates and selection are unknown.',
 'bansal_tg_categories':'All reported category counts are retained through cumulative fractions; not independent confirmations and not exact theoretical quantile probabilities.',
 'bansal_covariates_conditional_on_tg':'Reverse-conditional mean/SD diagnostic uses generated TG groups. Differences can arise from covariate marginal shape, unknown dependence and TG law; they do not identify a unique biological coefficient.',
}

plan={'schema_version':1,'scope':'source-only one permitted revision/retention round',
 'initial_feedback_sha256':sha(FEEDBACK/'initial_compact.json'),
 'no_builder_generator_execution':True,'no_builder_source_replay_execution':True,'no_target_feedback':True,
 'decisions':DECISIONS,'shared_source_definitions':'Evidence, contexts, replay/check definitions and all shared source-assumption descriptions are fixed byte-for-byte.',
 'limits':'No pooled mixed-unit discrepancy score; no winner selection; 12 input-only checks per structure are separate from 34 TG-related diagnostics. Three fixed seeds estimate draw variability only.'}

for sid in ['s1','s2','s3']:
    src=P/'candidates'/(sid+'_initial')
    dst=P/'candidates'/(sid+'_final')
    if (dst/'freeze.json').exists(): raise RuntimeError('Final already frozen; no overwriting or second scientific revision')
    # Resume an interrupted static preparation only; scientific choices above are unchanged.
    shutil.copytree(src,dst,ignore=shutil.ignore_patterns('freeze.json'),dirs_exist_ok=True)
    for i,other in enumerate(['s1','s2','s3'],1):
        shutil.copyfile(FEEDBACK/(other+'_initial_portfolio.json'),dst/f'f{i}.json')
    shutil.copyfile(FEEDBACK/'initial_compact.json',dst/'all0.json')
    for i,path in enumerate(report_paths[sid],1):
        shutil.copyfile(path,dst/f'r{i}.json')
    spec=read(dst/'model_spec.json')
    if sid=='s1':
        reference=spec['parameters']['reference']
        female=5.2
        male_weight=1029*3.1**2/(1029*3.1**2+1643*3.2**2)
        male=(6.813-(1-male_weight)*female)/male_weight
        slopes=[male,female]
        spec['parameters']['bmi_slope']=slopes
        cvs=[]
        for i in range(2):
            v=(slopes[i]*reference['bmi_sd'][i])**2+(spec['parameters']['age_slope'][i]*reference['age_sd'][i])**2
            cvs.append(math.sqrt((reference['tg_sd'][i]**2-v)/(reference['tg_mean'][i]**2+v)))
        spec['parameters']['residual_cv']=cvs
        spec['assumptions'].append({'id':'A_s1_revision','description':'After complete initial source-only feedback, choose a female BMI slope 5.2 mg/dL per kg/m^2 as an explicit sensitivity to overstated Bansal BMI rank and tertile separation. This is not a reported or identified coefficient. Balance the unreported male slope using published sex counts and BMI variances so their variance-weighted pooled coefficient is 6.813 under the fixed independent-within-sex source context. Recalculate residual CV algebraically to keep the same marginal mean/SD anchors. Keep age slopes unchanged because its reverse-conditional age summaries give conflicting guidance. The change can worsen Bansal location/quantiles; no numerical improvement is claimed before replay.'})
        for a in spec['assumptions']:
            if a['id']=='A_structure':
                a['description']='s1 assumes an additive conditional arithmetic TG mean with sex-specific BMI and linear age slopes, a soft positive floor, and mean-one independent lognormal individual noise. Constant residual CV within sex permits heteroskedastic absolute TG. It imposes a sex-BMI interaction but no age-BMI interaction on the arithmetic-mean scale away from the floor. Sex-specific slopes, linear age response and transport are assumptions; neither source identifies the full conditional law.'
        spec['parameter_provenance']['bmi_slope']={'evidence_ids':['E_oh_bmi_age_sex_slope','E_oh_male_bmi_sd','E_oh_female_bmi_sd','E_oh_male_bmi_stratum_1_tg','E_oh_male_bmi_stratum_5_tg','E_oh_female_bmi_stratum_1_tg','E_oh_female_bmi_stratum_5_tg','E_bansal_spearman_bmi','E_bansal_tertile1_bmi_mean','E_bansal_tertile3_bmi_mean'],
            'assumption_ids':['A_oh_ols','A_oh_context','A_oh_table2','A_structure','A_s1_revision'],
            'derivation':f'Female 5.2 is a deliberately rounded source-conditioned assumption motivated by initial Spearman .439490 vs .33 and excessive reverse-conditional BMI separation; not a conversion of Spearman to a slope. Male=(6.813-(1-w)*5.2)/w={male:.12g}, w=(1029*3.1^2)/(1029*3.1^2+1643*3.2^2)={male_weight:.12g}. Published Table 2 qualitative sex difference motivates allowing heterogeneity without resolving its summary-type ambiguity. Algebra preserves the pooled source slope only under the declared approximate source covariate construction; actual replay remains required.'}
        spec['parameter_provenance']['residual_cv']['assumption_ids'].append('A_s1_revision')
        spec['parameter_provenance']['residual_cv']['derivation']='Reapply the original analytic independent-covariate moment formula using revised sex-specific BMI slopes and unchanged age slopes: Var(mu)=bBMI(sex)^2 Var(BMI)+bAge(sex)^2 Var(age); CV^2=(reportedTGVar-Var(mu))/(reportedMean^2+Var(mu)). No final generator or simulated TG moments were computed by the builder.'
        program=(dst/'generator.py').read_text()
        old='p["bmi_slope"] * (bmi - np.asarray(reference["bmi_mean"])[sex])'
        new='np.asarray(p["bmi_slope"])[sex] * (bmi - np.asarray(reference["bmi_mean"])[sex])'
        assert program.count(old)==1
        (dst/'generator.py').write_text(program.replace(old,new),encoding='utf-8')
        write(dst/'model_spec.json',spec)
        plan['s1_parameter_change']={'bmi_slope_before':[6.813,6.813],'bmi_slope_after':slopes,'residual_cv_after':cvs,'age_slope_unchanged':spec['parameters']['age_slope'],'male_variance_weight':male_weight,
            'expected_arithmetic_location_tradeoff_from_published_bmi_means':(female-6.813)*(25.9-23.0),'not_a_generator_execution':True}
    else:
        assert sha(dst/'generator.py')==sha(src/'generator.py')
        assert sha(dst/'model_spec.json')==sha(src/'model_spec.json')
    common_files=['evidence.json','source_replay.json','source_checks.json','sa.json','source_contexts/oh.csv','source_contexts/bansal.csv','ctx.json']
    for file in common_files: assert sha(dst/file)==sha(src/file)
    old_defs={a['id']:a['description'] for a in read(src/'sa.json')}
    new_defs={a['id']:a['description'] for a in spec['assumptions']}
    assert all(new_defs[k]==v for k,v in old_defs.items())
    outcome_review=[]
    own=[x for x in compact['checks'] if x['structure']==sid]
    for row in own:
        grp=category(row)
        outcome_review.append({**row,'review_class':grp,'review_note':NOTES[grp],'decision_context':DECISIONS[sid]['kind']})
    assert len(outcome_review)==46
    assert sum(x['review_class']=='input_only' for x in outcome_review)==12
    write(dst/'audit.json',{'scope':'complete initial source-only diagnostic review','input_only_checks':12,'outcome_related_checks':34,'checks':outcome_review,'decision':DECISIONS[sid],'no_mixed_unit_aggregate':True})
    write(dst/'revision.json',DECISIONS[sid])
    validate_program(dst/'generator.py')
    task=read(P/'task.json')
    evidence=read(dst/'evidence.json')
    evidence_ids=validate_evidence(evidence,task)
    validate_spec(spec,evidence_ids)
    syntax=ast.parse((dst/'generator.py').read_text())
    assert 'record_id' not in (dst/'generator.py').read_text()
    for context in read(dst/'source_replay.json')['contexts']:
        _input_task(dst,context,task,20_000_000)
        for check in context['checks']:
            _check_metadata(check,{e['id']:e for e in evidence['items']},{a['id'] for a in spec['assumptions']},context['assumption_ids'])
    report=run_source_checks(P,dst)
    assert all(x['status']=='not_computable' for x in report['checks'])
    write(dst/'nc.json',report)
    static={'scope':'final_static_source_only','candidate':sid+'_final','decision':DECISIONS[sid]['kind'],'generator_executed_by_builder':False,'source_replay_executed_by_builder':False,
            'checks':['Initial portfolio/report SHA256 matches admitted compact feedback and controller schedule.','All 46 source checks reviewed; 12 input-only checks explicitly separated.','No target evidence read.','Common source evidence/recipe/context and shared assumption descriptions preserved.','Generator AST/ABI, evidence/spec contracts and replay metadata/input contracts valid.','Retained code/spec byte identity verified for s2 and s3; s1 alters only sex-specific BMI application and specification.'],
            'limits':'No final numerical agreement or target validity claim; source replay is reserved for controller.',
            'preparation_repair':'The first preparation stopped at an assertion because a review-label string rule misclassified the Oh BMI age-adjusted OLS as input-only. The rule was corrected to exact marginal-summary suffixes and the count now verifies 12 input-only/34 outcome checks. No generator was executed or scientific parameter changed for this repair.'}
    write(dst/'static.json',static)
    review={'scope':'independent_source-only feedback review','all_138_summaries_reviewed':True,'conclusions':['All structures overstate Bansal BMI rank and TG-tertile BMI separation; missing joint distribution prevents unique causal attribution.','s1 sex-specific BMI change is a constructed sensitivity, not recovered biology.','s1 age effect should not be increased solely to chase rank because reverse-conditional age summaries conflict.','s2 retention is defensible with unresolved dependence mismatch.','s3 can be retained only as a source-challenged sensitivity; source discrepancy does not reject every latent-mixture model.'],'no_generator_execution':True}
    write(dst/'review.json',review)
    artifact_names=['static.json','review.json','audit.json','nc.json','ctx.json','all0.json','f1.json','f2.json','f3.json','r1.json','r2.json','r3.json']
    checks={'scope':'source_only','records':[
        {'name':'static_contract_checks','status':'pass','detail':'Final source/evidence/specification and static generator/replay contracts checked. No builder generator execution.'},
        {'name':'complete_initial_source_feedback_review','status':'pass','detail':'All 138 summaries reviewed across structures; this candidate audit retains all 46, separating 12 input-only and 34 TG-related checks. Actual admitted compact/portfolios and own three replay reports are bound.'},
        {'name':'shared_source_definition_integrity','status':'pass','detail':'Evidence, contexts, recipes and shared source assumptions are unchanged.'},
        {'name':'final_numerical_compatibility','status':'not_computable','detail':'No final replay performed by builder; source compatibility remains limited as documented rather than automatically passed.'},
        {'name':'target_validation','status':'not_computable','detail':'No target outcomes or target feedback supplied or accessed.'}],
        'artifacts':[{'path':file,'sha256':sha(dst/file)} for file in artifact_names]}
    write(dst/'checks.json',checks)
    decision=DECISIONS[sid]
    rationale='\n\n'.join(decision['addressed_findings'])
    limitations='\n\n'.join(decision['remaining_limitations'])
    changed='Only the BMI slopes and their moment-derived residual CVs change; age slopes, assay handling and all common source definitions remain fixed.' if sid=='s1' else 'Generator and model specification are byte-identical to the parent. This is a substantive no-op decision after full feedback review.'
    (dst/'decision.md').write_text(f'''# {sid}: final source-only {decision['kind']}

{decision['reason']}

{changed}

{rationale}

{limitations}

All three source portfolios arrived together and were reviewed in full. audit.json retains every model-specific check without a mixed-unit score; f1/f2/f3.json bind the exact received portfolios, all0.json the complete compact feedback, and r1/r2/r3.json the exact own initial replay reports. Twelve marginal covariate checks are construction checks, not TG validation. Repeated statistics share participants; repeated seeds quantify generator draw variation, not source or structural uncertainty.

Common extraction distinctions remain fixed: Oh Table 1 means versus individual SDs, Table 3 reduced conditional slope, unreplayed fully adjusted/mixed/co-twin estimands, and unresolved arithmetic/geometric Table 2 interpretation. Bansal quantiles, marginal Spearman and reverse-conditional covariate summaries are distinct estimands. Source assay equivalence remains assumed and the task assay equation remains technical metadata only.

This is the single permitted retain/revise round, parent-linked to {sid}_initial. All final structures will be evaluated under the precommitted schedule; none is selected as a winner. Final execution is controller-only. No target outcomes, target evaluation feedback, or prior candidates outside this own new case were accessed. Static validity is not numerical compatibility or target validity.
''',encoding='utf-8')
    assert validate_bundle(P,dst)['generator_executed'] is False

write(P/'REVISION_PLAN.json',plan)
print(json.dumps({'prepared':['s1_final','s2_final','s3_final'],'decisions':{k:v['kind'] for k,v in DECISIONS.items()},'s1_parameter_change':plan['s1_parameter_change'],'generator_executed_by_builder':False},indent=2))
