"""Source/code-only audit: algebra on declared laws, never generator execution."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
closure=read(ROOT/'CONSTRUCTION_CLOSURE.json')
assert closure['all_episodes_closed']
records=[];checks=[];calls=0;cost=0.;unknown=0
for author in ['LIFESTYLE_A1','LIFESTYLE_A2']:
    ep=ROOT/'episodes'/author;c=ep/'candidates/v001'
    row=next(x for x in closure['episodes'] if x['episode_id']==author)
    checks.extend(dict(check=author+':closure:'+n,passed=sha(ep/n)==h) for n,h in row['files'].items())
    out=read(ep/'OUTCOME.json');s=read(c/'model_spec.json');manifest=read(c/'manifest.json')
    checks.extend(dict(check=author+':candidate:'+n,passed=sha(c/n)==h) for n,h in manifest['files'].items())
    assert out['selected_candidate']=='v001'
    calls+=out['calls_receipted'];cost+=out['known_tariff_cost_usd'];unknown+=out['unknown_usage_calls']
    keys=('published_age_sex_counts','latent_gaussian_correlation') if author=='LIFESTYLE_A1' else ('printed_counts','latent_correlation')
    raw=np.array(s[keys[0]],float);quotas=raw*s['n']/raw.sum()
    allocation=np.floor(quotas).astype(int)
    idx=np.argsort(-(quotas-allocation).ravel(),kind='stable')
    allocation.ravel()[idx[:s['n']-allocation.sum()]]+=1
    bounds=np.array(s['age_bounds'],float);mid=bounds.mean(1);var=np.diff(bounds,axis=1).ravel()**2/12
    if author=='LIFESTYLE_A1':
        a,m,b=s['oldest_triangular'];mid[-1]=(a+m+b)/3;var[-1]=(a*a+m*m+b*b-a*m-a*b-m*b)/18
    weights=[];mean_age=[];female_prop=[];age_var=[];sex_var=[];age_sex_cov=[]
    for g in range(3):
        w=allocation[:,g*2:g*2+2].astype(float);w/=w.sum();weights.append(w)
        am=(w*mid[:,None]).sum();pf=w[:,1].sum()
        mean_age.append(am);female_prop.append(pf)
        age_var.append((w*(var+mid**2)[:,None]).sum()-am**2)
        sex_var.append(pf*(1-pf));age_sex_cov.append((w[:,1]*mid).sum()-am*pf)
    eig=np.linalg.eigvalsh(s[keys[1]])
    check_laws=[]
    if author=='LIFESTYLE_A1':
        for trait,p in s['traits'].items():
            bygroup=[]
            for g in range(3):
                ba=p['age_slope'];bf=p['female_main_effect']+p['female_interaction'][g]
                mu=p['group_marginal_means'][g];sd=p['group_marginal_sds'][g]
                vals=[mu+ba*(a-mean_age[g])+bf*(f-female_prop[g]) for a in [bounds[:,0].min(),bounds[:,1].max()] for f in [0,1]]
                vmu=ba*ba*age_var[g]+bf*bf*sex_var[g]+2*ba*bf*age_sex_cov[g]
                cv2=(sd*sd-vmu)/(mu*mu+vmu)
                bygroup.append(dict(group=g,conditional_mean_lower=min(vals),conditional_mean_upper=max(vals),
                                    covariate_mean_variance=float(vmu),multiplicative_cv_squared=float(cv2)))
            check_laws.append(dict(component=trait,groups=bygroup))
        mathematically_valid=all(g['conditional_mean_lower']>0 and g['multiplicative_cv_squared']>0 for t in check_laws for g in t['groups']) and eig.min()>0
    else:
        for trait in ['bmi','hdl','tc']:
            p=s[trait];bygroup=[]
            for g in range(3):
                ba=p['age_slope'];bf=p['female_effect']+p['female_interaction'][g];mu=p['group_means'][g]
                vals=[mu+ba*(a-mean_age[g])+bf*(f-female_prop[g]) for a in [bounds[:,0].min(),bounds[:,1].max()] for f in [0,1]]
                bygroup.append(dict(group=g,conditional_mean_lower=min(vals),conditional_mean_upper=max(vals)))
            item=dict(component=trait,groups=bygroup)
            if trait in ['bmi','hdl']:
                ba=p['age_slope'];bf=p['female_effect']+p['female_interaction'][0]
                vmu=ba*ba*age_var[0]+bf*bf*sex_var[0]+2*ba*bf*age_sex_cov[0]
                item['pastoral_conditional_variance']=p['pastoral_marginal_sd']**2-vmu
            check_laws.append(item)
        nh=[]
        for g in range(3):
            v=[]
            for a in [bounds[:,0].min(),bounds[:,1].max()]:
                for f in [0,1]:
                    m=[]
                    for tr in ['tc','hdl']:
                        p=s[tr];m.append(p['group_means'][g]+p['age_slope']*(a-mean_age[g])+(p['female_effect']+p['female_interaction'][g])*(f-female_prop[g]))
                    v.append(m[0]-m[1])
            nh.append(dict(group=g,conditional_mean_lower=min(v),conditional_mean_upper=max(v)))
        check_laws.append(dict(component='nonhdl',groups=nh))
        mathematically_valid=all(g['conditional_mean_lower']>0 for t in check_laws for g in t['groups']) and all(t.get('pastoral_conditional_variance',1)>0 for t in check_laws) and eig.min()>0
    checks.append(dict(check=author+':positive-law-parameters-and-SPD',passed=bool(mathematically_valid)))
    records.append(dict(author=author,selected_candidate='v001',submissions=out['tool_usage']['candidates'],
        diagnostic_trials=out['tool_usage']['executions'],revisions=0,model_calls=out['calls_receipted'],cost_usd=out['known_tariff_cost_usd'],
        actual_models=sorted({x['returned_model'] for x in out['actual_usage_by_call']}),
        scope='Independent reading of generator.py, model_spec.json, notes.json, final selection, and captured public sources; no final draws or real comparisons inspected',
        hashes={n:sha(c/n) for n in ['generator.py','model_spec.json','notes.json','manifest.json']},
        correlation_eigenvalues=eig.tolist(),analytic_bounds=check_laws,
        finite_moment_assessment='Pass for this fixed declared law: compact age support, positive bounded conditional means/scales, Gaussian-lognormal innovations, and finite sums. This is analytic inspection, not certification from finite draws.',
        physiology='BMI/HDL/non-HDL positive; TC=HDL+non-HDL implies TC>HDL by construction. Does not model possible inconsistent independent assay readouts.',
        demography='Deterministic largest-remainder rescaling of published 1360 cells to1226; age sampling and top-bin bound are explicit assumptions. Stratum frequencies do not fluctuate across seeds.',
        mean_variance_handling=('Derives group lognormal CV from specified marginal variance after removing demographic mean variance; source SD not blindly substituted as residual SD.' if author=='LIFESTYLE_A1' else 'Subtracts assumed demographic mean variance from pastoral marginal variance for BMI/HDL conditional SDs; other heterogeneity and lipid scales are explicit assumptions.'),
        source_findings=[
            'Pastoralist BMI/HDL marginal anchors and BMI percentage comparisons exist in the captured Lea article.',
            'Interpreting reported BMI percentage comparisons as unadjusted marginal mean ratios is an acknowledged extra assumption, not independently verified operator equivalence.',
            'TC/non-HDL levels, most scale changes, age/sex slopes, interaction sizes and latent residual correlations remain assumed.',
            ('Omuse Table3 SDR values and their non-regression meaning agree with the captured table; qualitative use does not estimate Turkana slopes.' if author=='LIFESTYLE_A1' else 'Rural Kenyan Maasai Table1 BMI/HDL sex-specific means agree with the captured table; the resulting female HDL effect is an explicitly assumed transfer across populations/assays.')
        ]))
records[1]['minor_arithmetic_note']=dict(
    claim='rural BMI = urban BMI /1.0843',declared_value=read(ROOT/'episodes/LIFESTYLE_A2/candidates/v001/model_spec.json')['bmi']['group_means'][1],
    exact_division=21.927031/1.0843,
    interpretation='The stated approximate derivation differs by about0.00055kg/m2; record as minor numeric transcription/rounding discrepancy, do not silently alter frozen candidate.')
failures=[x['check'] for x in checks if not x['passed']]
report=dict(status='pass_with_declared_assumptions' if not failures else 'require_inspection',
    created_utc=datetime.now(timezone.utc).isoformat(),construction_closure_sha256=sha(ROOT/'CONSTRUCTION_CLOSURE.json'),
    launch_freeze_sha256=sha(ROOT/'LAUNCH_FREEZE.json'),checks=len(checks),failed_checks=failures,
    target_results_inspected=False,final_virtual_rows_inspected=False,generator_executed_by_reviewer=False,
    current_run_code_source_only=True,personally_blind_to_all_prior_project_context=False,
    model_calls=calls,known_tariff_cost_usd=cost,unknown_usage_calls=unknown,records=records,
    decision='Proceed to the predeclared comparison of all final tables. Retained v001 after trial is not a demonstrated revision gain. No scientific parameter or program was changed by this audit.',
    caveats=['Published-source reconstruction does not independently validate source assumptions or transfer.',
             'Similar assumptions by two same-model authors are not independent empirical confirmation.',
             'Original measurement missingness and evidence uncertainty are absent from the complete virtual rows.'])
with (ROOT/'review/CONSTRUCTION_CODE_REVIEW.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False)
print(json.dumps(dict(status=report['status'],checks=len(checks),failures=failures,model_calls=calls,cost_usd=cost,unknown_usage_calls=unknown,
    audit_sha256=sha(ROOT/'review/CONSTRUCTION_CODE_REVIEW.json'))))
