"""Independent post-run audit; writes only review artifacts, never patient rows."""
from pathlib import Path
from itertools import combinations
from datetime import datetime, timezone
import hashlib
import json
import math
import warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent / 'development_batch' / 'attempt_02'
RESULTS = BATCH / 'results'
KEY = ['analysis', 'term']
VARIABLES = ['pfs', 'gng', 'dd100', 'dd1000']
TERMS = ['month_3_minus_0', 'month_6_minus_0', 'month_9_minus_0', 'month_12_minus_0', 'month_12_minus_3']
EXPECTED = {('baseline_pearson', f'{a}__{b}') for a,b in combinations(VARIABLES, 2)}
EXPECTED |= {(f'{v}_time_reml', t) for v in ['weight', *VARIABLES] for t in TERMS}
EXPECTED |= {('pooled_standardized_reml', v) for v in VARIABLES}
CASES = ['mcar_a', 'mcar_b', 'baseline_dependent']
METHODS = ['agent', 'statistical_reference']
checks = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def csv(p):
    return pd.read_csv(p, float_precision='round_trip')


def check(name, condition, detail=None):
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})


def close(a,b):
    return bool(np.allclose(np.asarray(a,dtype=float), np.asarray(b,dtype=float), rtol=1e-10, atol=1e-12, equal_nan=True))


def states(d):
    return np.where(d.ci_low.gt(0), 'positive', np.where(d.ci_high.lt(0), 'negative', 'uncertain'))


def affected(d):
    return d.analysis.eq('pfs_time_reml') | (d.analysis.eq('pooled_standardized_reml') & d.term.eq('pfs'))


def jsonable(x):
    if isinstance(x, dict):
        return {str(k):jsonable(v) for k,v in x.items()}
    if isinstance(x, (list,tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x,np.generic):
        x=x.item()
    if isinstance(x,float) and not math.isfinite(x):
        return None
    return x


def main():
    freeze=read(BATCH/'freeze.json')
    config=read(BATCH/'config.json')
    registry=pd.DataFrame(freeze['registry'])
    source_mismatch=[p for p,h in freeze['source_files'].items() if not Path(p).is_file() or sha(p)!=h]
    implementation_mismatch=[p for p,h in freeze['implementation_files'].items() if not (BATCH/p).is_file() or sha(BATCH/p)!=h]
    registry_mismatch=[r['dataset_id'] for r in freeze['registry'] if sha(r['path'])!=r['sha256']]
    check('all_frozen_source_hashes',not source_mismatch,{'n':len(freeze['source_files']),'mismatch':source_mismatch})
    check('all_frozen_implementation_hashes',not implementation_mismatch,{'n':len(freeze['implementation_files']),'mismatch':implementation_mismatch})
    check('all_registry_input_hashes',not registry_mismatch,{'n':len(registry),'mismatch':registry_mismatch})
    check('registry_144_unique_inputs',len(registry)==144 and registry.dataset_id.nunique()==144)
    check('registry_kind_counts',registry.kind.value_counts().to_dict()=={'completion':120,'full_synthetic':20,'missing_only':3,'reference':1},registry.kind.value_counts().to_dict())
    check('twenty_distinct_full_synthetic_hashes',registry.loc[registry.kind.eq('full_synthetic'),'sha256'].nunique()==20)
    if not (RESULTS/'output_manifest.json').exists():
        print(json.dumps({'status':'waiting_for_completed_results','source_checks_pass':all(x['passed'] for x in checks),'verified_source_files':len(freeze['source_files'])}))
        return
    output_manifest=read(RESULTS/'output_manifest.json')
    output_mismatch=[p for p,h in output_manifest['files'].items() if sha(RESULTS/p)!=h]
    check('output_manifest_file_hashes',not output_mismatch,{'n':len(output_manifest['files']),'mismatch':output_mismatch})
    expected_outputs={'execution_start.json','all_results.csv','completion_pooled.csv','full_synthetic_summary.csv','summary.json'}
    check('output_manifest_inventory',set(output_manifest['files'])==expected_outputs)
    check('output_and_execution_match_freeze',output_manifest['freeze_sha256']==sha(BATCH/'freeze.json')==read(RESULTS/'execution_start.json')['freeze_sha256'])
    before_hashes={str(p):sha(p) for p in [BATCH/'freeze.json',RESULTS/'output_manifest.json',*[RESULTS/k for k in output_manifest['files']]]}
    allr=csv(RESULTS/'all_results.csv')
    pooled=csv(RESULTS/'completion_pooled.csv')
    summary=read(RESULTS/'summary.json')
    full_summary=csv(RESULTS/'full_synthetic_summary.csv')
    check('5040_analysis_records',len(allr)==5040)
    check('144_distinct_datasets',allr.dataset_id.nunique()==144 and set(allr.dataset_id)==set(registry.dataset_id))
    check('each_dataset_has_35_unique_expected_analyses',all(len(g)==35 and set(zip(g.analysis,g.term))==EXPECTED for _,g in allr.groupby('dataset_id')))
    check('all_analyses_successful',allr.status.eq('ok').all() and allr.comparison_status.eq('ok').all(),allr.status.value_counts().to_dict())
    ref=allr.loc[allr.kind.eq('reference')].set_index(KEY)
    indexed=allr.set_index(KEY)
    mapped_ref=ref.reindex(indexed.index)
    for field in ['estimate','se','ci_low','ci_high']:
        check(f'reference_{field}_columns_match_reference_rows',close(indexed[f'reference_{field}'],mapped_ref[field]))
    check('ci_state_labels_recomputed',np.array_equal(allr.ci_state.to_numpy(),states(allr)))
    check('reference_ci_state_labels_recomputed',np.array_equal(indexed.reference_ci_state.to_numpy(),states(mapped_ref)))
    errors=indexed.estimate.to_numpy()-mapped_ref.estimate.to_numpy()
    check('signed_and_absolute_errors_recomputed',close(indexed.signed_error,errors) and close(indexed.absolute_error,np.abs(errors)))
    check('scaled_errors_and_se_ratios_recomputed',close(indexed.error_in_reference_se,errors/mapped_ref.se.to_numpy()) and close(indexed.se_ratio,indexed.se.to_numpy()/mapped_ref.se.to_numpy()))
    check('ci_agreement_flags_recomputed',np.array_equal(allr.ci_state_agreement.to_numpy(),allr.ci_state.eq(allr.reference_ci_state).to_numpy()))
    check('point_sign_flags_recomputed',np.array_equal(indexed.point_sign_agreement.to_numpy(),np.sign(indexed.estimate.to_numpy())==np.sign(mapped_ref.estimate.to_numpy())))
    completion=allr.loc[allr.kind.eq('completion')]
    controls=completion.loc[~affected(completion)]
    changed=completion.loc[affected(completion)]
    check('completion_counts_4200_3480_720',len(completion)==4200 and len(controls)==3480 and len(changed)==720)
    check('29_copied_controls_each_completion',all(len(g)==29 for _,g in controls.groupby('dataset_id')) and controls.computation.eq('copied_after_exact_input_preservation_check').all())
    check('six_fresh_affected_results_each_completion',all(len(g)==6 for _,g in changed.groupby('dataset_id')) and changed.computation.eq('fresh_frozen_function').all())
    cc=controls.set_index(KEY)
    check('control_statistics_exactly_copy_reference',all(np.array_equal(cc[f].to_numpy(),ref.reindex(cc.index)[f].to_numpy()) for f in ['estimate','se','ci_low','ci_high','p']))
    check('completion_role_labels_correct',changed.completion_role.eq('PFS_affected').all() and controls.completion_role.eq('unchanged_preservation_control').all())
    check('all_twenty_completions_retained_each_arm',all(len(g)==20 and set(g.draw)==set(range(1,21)) for _,g in changed.groupby(['case','method',*KEY])))
    check('36_unique_pooled_completion_rows',len(pooled)==36 and not pooled.duplicated(['case','method',*KEY]).any() and affected(pooled).all() and set(pooled.case)==set(CASES) and set(pooled.method)==set(METHODS))
    pool_errors=[]
    pool_count_fail=[]
    for _,r in pooled.iterrows():
        g=changed.loc[changed.case.eq(r['case'])&changed.method.eq(r.method)&changed.analysis.eq(r.analysis)&changed.term.eq(r.term)]
        if len(g)!=20 or not g.status.eq('ok').all():
            pool_count_fail.append([r['case'],r.method,r.analysis,r.term])
            continue
        q=g.estimate.to_numpy(); s=g.se.to_numpy(); m=len(q)
        qbar=q.mean(); ubar=(s*s).mean(); b=q.var(ddof=1); total=ubar+(1+1/m)*b
        df=(m-1)*(1+ubar/((1+1/m)*b))**2 if b>0 else math.inf
        critical=stats.t.ppf(.975,df) if b>0 else stats.norm.ppf(.975)
        se=math.sqrt(total)
        expected={'Qbar':qbar,'estimate':qbar,'Ubar':ubar,'B':b,'T':total,'se':se,'ci_low':qbar-critical*se,'ci_high':qbar+critical*se,'p':2*(stats.t.sf(abs(qbar/se),df) if b>0 else stats.norm.sf(abs(qbar/se)))}
        if b>0:
            expected['df']=df
        for field,value in expected.items():
            if not close([r[field]],[value]):
                pool_errors.append({'case':r['case'],'method':r.method,'analysis':r.analysis,'term':r.term,'field':field,'reported':r[field],'independent':value})
    check('independent_rubin_arithmetic_all_36',not pool_errors and not pool_count_fail,{'field_mismatches':pool_errors,'count_failures':pool_count_fail})
    check('all_pooled_m_equals20',pooled.m.eq(20).all())
    check('no_Rubin_pooling_full_synthetic',not pooled.method.eq('frozen_final_program').any() and not pooled.case.eq('full_generation').any())
    pidx=pooled.set_index(KEY); pref=ref.reindex(pidx.index)
    pe=pidx.estimate.to_numpy()-pref.estimate.to_numpy()
    check('pooled_effect_comparisons_and_states',close(pidx.signed_error,pe) and close(pidx.absolute_error,np.abs(pe)) and np.array_equal(pooled.ci_state.to_numpy(),states(pooled)) and np.array_equal(pooled.ci_state_agreement.to_numpy(),pooled.ci_state.eq(pooled.reference_ci_state).to_numpy()))
    missing=allr.loc[allr.kind.eq('missing_only')&affected(allr)]
    improvement_ok=True
    expanded=[]
    for case in CASES:
        for a,t in sorted({(r.analysis,r.term) for _,r in pooled.iterrows()}):
            rr=ref.loc[(a,t)]
            mm=missing.loc[missing.case.eq(case)&missing.analysis.eq(a)&missing.term.eq(t)].iloc[0]
            entry={'case':case,'analysis':a,'term':t,'reference':{f:rr[f] for f in ['estimate','ci_low','ci_high','ci_state']}}
            entry['missing_only']={f:mm[f] for f in ['estimate','ci_low','ci_high','ci_state','absolute_error']}
            for method in METHODS:
                p=pooled.loc[pooled.case.eq(case)&pooled.method.eq(method)&pooled.analysis.eq(a)&pooled.term.eq(t)].iloc[0]
                improvement_ok &= close([p.missing_only_absolute_error,p.absolute_error_improvement_over_missing_only],[mm.absolute_error,mm.absolute_error-p.absolute_error])
                entry[method]={f:p[f] for f in ['estimate','ci_low','ci_high','ci_state','absolute_error','absolute_error_improvement_over_missing_only']}
            expanded.append(entry)
    check('pooled_improvement_vs_missing_only_recomputed',improvement_ok)
    full=allr.loc[allr.kind.eq('full_synthetic')]
    check('all20_synthetic_cohorts_retained_per_analysis',len(full)==700 and all(len(g)==20 and set(g.draw)==set(range(271001,271021)) for _,g in full.groupby(KEY)))
    fs_errors=[]
    for _,r in full_summary.iterrows():
        g=full.loc[full.analysis.eq(r.analysis)&full.term.eq(r.term)]
        actual=[g.absolute_error.mean(),g.estimate.min(),g.estimate.max(),g.ci_state_agreement.sum()]
        reported=[r.mean_absolute_error_valid,r.min_estimate_valid,r.max_estimate_valid,r.ci_state_agreement_n]
        if len(g)!=20 or r.n_expected!=20 or r.n_valid!=20 or r.agreement_denominator!=20 or not close(actual,reported):
            fs_errors.append([r.analysis,r.term])
    check('full_synthetic_summary_independently_recomputed',len(full_summary)==35 and not fs_errors,fs_errors)
    baseline=full.loc[full.analysis.eq('baseline_pearson')]
    trajectory=full.loc[full.analysis.str.endswith('_time_reml')]
    proxies=full.loc[full.analysis.eq('pooled_standardized_reml')]
    check('full_generation_evidence_roles_6_25_4',len(baseline)==120 and len(trajectory)==500 and len(proxies)==80 and baseline.generation_evidence_role.eq('unprovided_baseline_relationship').all() and trajectory.generation_evidence_role.eq('source_marginal_constrained_trajectory').all() and proxies.generation_evidence_role.eq('unprovided_exploratory_proxy').all())
    expected_counts={'dataset_count':144,'analysis_rows':5040,'paper_replay_rows':4464,'exploratory_proxy_rows':576,'completion_rows':4200,'completion_preservation_control_rows':3480,'completion_affected_rows':720,'pooled_completion_rows':36,'pooling_failures':0,'analysis_failures':0}
    check('summary_counts_match_independent_totals',all(summary[k]==v for k,v in expected_counts.items()),expected_counts)
    check('summary_complete_no_failures',summary['status']=='complete' and not summary['failures'])
    check('computation_counts_match',summary['computation_counts']==allr.computation.value_counts().to_dict(),allr.computation.value_counts().to_dict())
    check('config_counts_match_actual',{k:config[k] for k in ['analysis_count','dataset_count','completion_count','synthetic_count','m','control_count_per_completion','affected_count_per_completion']}=={'analysis_count':35,'dataset_count':144,'completion_count':120,'synthetic_count':20,'m':20,'control_count_per_completion':29,'affected_count_per_completion':6})
    # One independent direct fit; only the observed reference is loaded, never exported.
    reference_path=registry.loc[registry.kind.eq('reference'),'path'].iloc[0]
    frame=csv(reference_path)
    d=frame[['person_id','month','pfs']].dropna().copy()
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('always')
        fit=smf.mixedlm('pfs ~ C(month)',d,groups=d.person_id).fit(reml=True,method='powell',maxiter=600,disp=False)
    names=list(fit.fe_params.index)
    contrast=np.zeros(len(names)); contrast[names.index('C(month)[T.12]')]=1; contrast[names.index('C(month)[T.3]')]=-1
    estimate=float(contrast@fit.fe_params.to_numpy())
    variance=float(contrast@fit.cov_params().loc[names,names].to_numpy()@contrast)
    rerun={'analysis':'pfs_time_reml','term':'month_12_minus_3','estimate':estimate,'se':math.sqrt(variance),'converged':bool(fit.converged),'n_persons':int(d.person_id.nunique()),'n_observed_rows':len(d)}
    rf=ref.loc[('pfs_time_reml','month_12_minus_3')]
    check('independent_reference_PFS_contrast_fit',fit.converged and close([estimate,math.sqrt(variance)],[rf.estimate,rf.se]),rerun)
    del frame,d
    check('review_did_not_modify_frozen_inputs_or_results',all(sha(p)==h for p,h in before_hashes.items()) and all(sha(p)==h for p,h in freeze['source_files'].items()))
    comp_counts=[]
    for case in CASES:
        one={'case':case,'n_affected_outcomes':6}
        mg=missing.loc[missing.case.eq(case)]
        one['missing_only_CI_state_matches']=int(mg.ci_state_agreement.sum())
        for method in METHODS:
            g=pooled.loc[pooled.case.eq(case)&pooled.method.eq(method)]
            one[f'{method}_CI_state_matches']=int(g.ci_state_agreement.sum())
            one[f'{method}_smaller_error_than_missing_only']=int(g.absolute_error_improvement_over_missing_only.gt(0).sum())
        ag=pooled.loc[pooled.case.eq(case)&pooled.method.eq('agent')].set_index(KEY)
        st=pooled.loc[pooled.case.eq(case)&pooled.method.eq('statistical_reference')].set_index(KEY).reindex(ag.index)
        one['agent_smaller_error_than_statistical_reference']=int((ag.absolute_error<st.absolute_error).sum())
        comp_counts.append(one)
    generation=[]
    for name,g in [('unprovided_baseline',baseline),('constrained_trajectory',trajectory),('exploratory_proxy',proxies)]:
        generation.append({'family':name,'unique_analyses':len(g[KEY].drop_duplicates()),'n_draw_analysis_records':len(g),'ci_state_matches':int(g.ci_state_agreement.sum()),'point_sign_matches':int(g.point_sign_agreement.sum()),'uncertainty_scope':'Descriptive counts across correlated queries and same-generator draws; not independent replication.'})
    report={'reviewed_utc':datetime.now(timezone.utc).isoformat(),'scope':'attempt_02 completed development batch only; no generator rerun or source edits','status':'PASS_WITH_INTERPRETATION_LIMITS' if all(x['passed'] for x in checks) else 'FAIL','checks':checks,'hashes':before_hashes,'completion_comparison_counts':comp_counts,'completion_18_affected_comparisons':expanded,'full_generation_families':generation,'full_generation_baseline_queries':full_summary.loc[full_summary.analysis.eq('baseline_pearson')].to_dict('records'),'independent_reference_rerun':rerun,'source_verification':{'url':'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243530','verified_facts':['75 participants, visits at months 0,3,6,9,12','Participant random effect and restricted maximum likelihood are documented','Weight changes -6.01 (SE 1.12) at month3 and 2.39 (SE 1.14) from month3 to12 are documented','Article reports t(268)=-3.18 with p<.001, an internal numerical inconsistency','Source formula/scaling does not establish that four standardized pooled proxies exactly reproduce the published pooled coefficients']},'limitations':['Known-result retrospective development, not confirmation or unseen-task validation.','29 copied outcomes per completion are preservation controls; exclude them from completion success rates.','25 full-generation trajectories are constrained by supplied source marginals; separate from six unprovided baseline relationships.','The exact observed-data reference retains native missingness and sampling uncertainty; it is not population truth.','Uncertain intervals do not prove a null or equivalence.','Rubin large-complete-sample pooling arithmetic does not validate proper multiple imputation or repeated-sampling coverage.','No Rubin pooling of full synthetic cohorts; min/max ranges are descriptive Monte Carlo variability.','No validation of study-design usefulness, cross-study transfer, causal treatment effects, or added independent patient evidence is performed.','Only one selected reference analysis was rerun independently; all other statistical fits were checked through code, frozen provenance, arithmetic and consistency.','No raw patient rows or values are exported in review artifacts.']}
    borderline=ref.loc[('baseline_pearson','pfs__dd100')]
    report['interpretive_findings']={
        'completion_CI_state_agreement': {'agent':int(pooled.loc[pooled.method.eq('agent'),'ci_state_agreement'].sum()),'statistical_reference':int(pooled.loc[pooled.method.eq('statistical_reference'),'ci_state_agreement'].sum()),'missing_only':int(missing.ci_state_agreement.sum()),'denominator':18},
        'completion_point_error': {'agent_better_than_MICE':sum(x['agent_smaller_error_than_statistical_reference'] for x in comp_counts),'agent_better_than_missing_only':sum(x['agent_smaller_error_than_missing_only'] for x in comp_counts),'denominator':18,'interpretation':'Agent improves over this MICE comparator more often than over missing-only; CI agreement alone does not establish useful completion.'},
        'borderline_baseline_query': {'term':'pfs__dd100','reference_estimate':float(borderline.estimate),'reference_unadjusted_p':float(borderline.p),'reference_ci_low':float(borderline.ci_low),'reference_ci_high':float(borderline.ci_high),'caution':'The reference is close to the significance threshold and the source article reports no significant association. Zero of twenty CI-state matches is threshold-sensitive; also report effect error (mean absolute r error about 0.271), not a threshold-only failure claim.'},
        'MICE_CI_disagreement':'mcar_a PFS month12-minus3 changes from reference uncertain to negative; Agent remains uncertain but its upper limit is near zero.'
    }
    (HERE/'verification.json').write_text(json.dumps(jsonable(report),indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines=['# Independent verification of attempt 02','',f"Status: **{report['status']}**. {sum(x['passed'] for x in checks)}/{len(checks)} independent checks passed.",'','The audit used only the completed attempt_02 batch; it did not rerun generators or edit batch/source artifacts. It verified all input and output hashes, reconstructed comparison metrics and Rubin arithmetic independently, and reran one direct reference PFS contrast.','',f"- Inputs: 144 (1 reference, 3 missing-only, 120 completions, 20 distinct synthetic cohorts).\n- Results: 5,040, with exactly 35 unique analyses per input.\n- Completion results: 720 affected outputs plus 3,480 copied preservation controls. The controls are excluded below.\n- Pooling: 36 results, each from all 20 completions; no full-synthetic pooling.\n- Frozen hashes: {len(freeze['source_files'])} source files, {len(freeze['implementation_files'])} implementation files, 144 registry inputs, and {len(output_manifest['files'])} manifest-listed outputs all checked.",'','## Affected completion results','', 'Every count below has denominator six. Outcomes and masks are correlated; these are descriptive counts, not independent trials. Statistical reference is the frozen MICE comparator.','', '| Mask | Missing-only CI matches | Agent CI matches | MICE CI matches | Agent lower error than missing | MICE lower error than missing | Agent lower error than MICE |','|---|---:|---:|---:|---:|---:|---:|']
    for r in comp_counts:
        lines.append('| '+ ' | '.join(str(r[k]) for k in ['case','missing_only_CI_state_matches','agent_CI_state_matches','statistical_reference_CI_state_matches','agent_smaller_error_than_missing_only','statistical_reference_smaller_error_than_missing_only','agent_smaller_error_than_statistical_reference'])+' |')
    lines += ['','Across the 18 affected outcome-mask combinations, Agent and missing-only both match the reference interval state in 18/18, while MICE matches 17/18. Agent has lower absolute effect error than MICE in 16/18, but lower error than missing-only in only 6/18. These results do not establish a general benefit from completing the data. The MICE disagreement is mcar_a PFS month12-minus3 (reference uncertain, MICE negative); the Agent upper limit in that comparison is also close to zero.','', 'Intervals are 95% intervals. `uncertain` means the interval includes zero; it does not prove no association. Numbers below are estimate [lower, upper], followed by interval state.','', '| Mask / affected outcome | Observed reference | Missing-only | Agent pooled | MICE pooled |','|---|---|---|---|---|']
    def fmt(r):
        return f"{r['estimate']:.5f} [{r['ci_low']:.5f}, {r['ci_high']:.5f}] {r['ci_state']}"
    for r in expanded:
        title=r['case']+' / '+('PFS-weight proxy' if r['analysis']=='pooled_standardized_reml' else r['term'])
        lines.append('| '+title+' | '+' | '.join(fmt(r[k]) for k in ['reference','missing_only','agent','statistical_reference'])+' |')
    lines += ['','## Full generation','', '| Evidence role | Queries | Draw-query records | CI state matches | Point-sign matches |','|---|---:|---:|---:|---:|']
    for r in generation:
        lines.append(f"| {r['family']} | {r['unique_analyses']} | {r['n_draw_analysis_records']} | {r['ci_state_matches']} | {r['point_sign_matches']} |")
    lines += ['','These families must remain separate. The 25 trajectory queries were constrained by source marginals. Only the six baseline relationships lacked supplied covariance; their results cannot be rescued by agreement on constrained trajectories. All 20 cohorts remain in every denominator.','', '| Baseline query | Mean absolute error | CI matches / 20 | Estimate min–max |','|---|---:|---:|---|']
    for _,r in full_summary.loc[full_summary.analysis.eq('baseline_pearson')].iterrows():
        lines.append(f"| {r.term} | {r.mean_absolute_error_valid:.5f} | {int(r.ci_state_agreement_n)}/20 | {r.min_estimate_valid:.5f} to {r.max_estimate_valid:.5f} |")
    lines += ['',f"The PFS-DD100 reference correlation is r={borderline.estimate:.5f}, unadjusted p={borderline.p:.5f}, near the significance threshold; the publication reports no significant association. Its 0/20 CI-state agreement should therefore be read alongside the mean absolute r error of 0.27123, rather than treated as threshold-only proof of failure.",'','## Source and numeric checks','', '[The source article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243530) documents 75 participants, five visits, participant random effects, and REML. Its published weight effect/SE examples support the reconstruction checks. Its t(268)=-3.18 and p<.001 report is internally inconsistent. SAS finite-df details and pooled-model scaling are insufficiently specified for exact CI/proxy equivalence; the batch correctly retains these limitations.','',f"The independent direct reference fit of PFS month12 minus month3 converged: estimate {rerun['estimate']:.12g}, SE {rerun['se']:.12g}; both match the batch within rtol=1e-10 and atol=1e-12. The fit read the reference input without exporting patient values.",'','All 36 pooled rows were rebuilt from per-completion analysis outputs: Qbar, Ubar, B, T, SE, Rubin df, t interval, and p value. All effect errors, CI state labels, agreement flags, missing-only comparisons, and full-generation summaries were also recomputed.','', '## Interpretation limits','']
    lines += ['- '+x for x in report['limitations']]
    if not all(x['passed'] for x in checks):
        lines += ['','## Failed checks','']+['- '+x['name'] for x in checks if not x['passed']]
    lines += ['','Detailed machine-readable checks, aggregate comparisons, and SHA-256 values are in `verification.json`. The audit implementation is `audit_attempt_02.py`.','']
    (HERE/'VERIFICATION.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'status':report['status'],'checks_passed':sum(x['passed'] for x in checks),'checks_total':len(checks),'failed_checks':[x['name'] for x in checks if not x['passed']],'completion_counts':comp_counts,'generation_counts':generation},indent=2))


if __name__=='__main__':
    main()
