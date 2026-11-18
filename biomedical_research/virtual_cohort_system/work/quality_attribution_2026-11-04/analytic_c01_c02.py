"""Deterministic law audit, not generator execution or patient-data analysis.

Read frozen specifications and existing aggregate displays only. Compute exact
first/second moments and OLS projections; approximate C01 population Spearman
with deterministic Gauss-Hermite integration, retaining convergence results.
No candidate import, random draw, row table, parameter change, or target fitting.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.special import ndtr, ndtri

W = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DISPLAY = W / 'biomedical_research/virtual_cohort_system/work/core_workflow_replication_2026-11-04/display'

def load_spec(author):
    p = W / f'evcRep{author}/candidates/initial/model_spec.json'
    raw = p.read_bytes()
    return json.loads(raw)['parameters'], {'path': str(p), 'sha256': hashlib.sha256(raw).hexdigest()}

def projection(cov, y, predictors):
    return np.linalg.solve(cov[np.ix_(predictors, predictors)], cov[predictors, y])

def c01_law(p):
    # Order A, B, G, H. Sex is independent with zero conditional offsets.
    assert p['conditional_female_offsets'] == [0., 0., 0.]
    ages = np.arange(p['age_bounds'][0], p['age_bounds'][1] + 1)
    pi = p['known_component_probability']
    corr = np.asarray(p['conditional_raw_correlation_matrix'])
    components = []
    for a in ages:
        m = np.asarray(p['background_means_at_reference_age']) + np.asarray(p['background_age_slopes']) * (a - p['background_reference_age'])
        components.append(((1-pi)/len(ages), float(a), m, np.asarray(p['background_conditional_sds'])))
        components.append((pi/len(ages), float(a), np.asarray(p['known_component_arithmetic_means']), np.asarray(p['known_component_arithmetic_sds'])))
    mean = np.zeros(4)
    second = np.zeros((4,4))
    for w, a, m, s in components:
        z = np.r_[a, m]
        within = np.zeros((4,4)); within[1:,1:] = corr * np.outer(s,s)
        mean += w*z; second += w*(within+np.outer(z,z))
    cov = second - np.outer(mean,mean)
    # Collapse duplicate known components for the continuous pair's mixture.
    pair_components = [(x[0], x[2][1:], x[3][1:]) for x in components[::2]]
    pair_components.append((pi, np.asarray(p['known_component_arithmetic_means'])[1:], np.asarray(p['known_component_arithmetic_sds'])[1:]))
    weights = np.asarray([x[0] for x in pair_components])
    rawmeans = np.asarray([x[1] for x in pair_components])
    rawsds = np.asarray([x[2] for x in pair_components])
    lv = np.log1p((rawsds/rawmeans)**2)
    ls = np.sqrt(lv); lm = np.log(rawmeans)-lv/2
    lc = np.log1p(corr[1,2]*(rawsds[:,0]/rawmeans[:,0])*(rawsds[:,1]/rawmeans[:,1]))
    lr = lc / (ls[:,0]*ls[:,1])
    ranks = []
    for order in (16,24,40,64):
        nodes, ghw = hermgauss(order); nodes = nodes*math.sqrt(2); ghw = ghw/math.sqrt(math.pi)
        x, y = np.meshgrid(nodes,nodes,indexing='ij'); productw = np.outer(ghw,ghw).reshape(-1)
        ef = 0.
        for j,w in enumerate(weights):
            lg = lm[j,0]+ls[j,0]*x.reshape(-1)
            lh = lm[j,1]+ls[j,1]*(lr[j]*x+math.sqrt(1-lr[j]**2)*y).reshape(-1)
            fg = ndtr((lg[:,None]-lm[None,:,0])/ls[None,:,0])@weights
            fh = ndtr((lh[:,None]-lm[None,:,1])/ls[None,:,1])@weights
            ef += w*float(productw@(fg*fh))
        ranks.append({'quadrature_order_each_dimension':order,'spearman':12*ef-3})
    return {'mean_order_A_B_G_H':mean.tolist(),'covariance_order_A_B_G_H':cov.tolist(),
            'E1_bmi_age_sex':float(projection(cov,3,[1,0])[0]),
            'E2_glucose_age_sex':float(projection(cov,3,[2,0])[0]),
            'E3_age_bmi_glucose_sex':float(projection(cov,3,[0,1,2])[0]),
            'fully_adjusted_bmi':float(projection(cov,3,[1,0,2])[0]),
            'glucose_hba1c_pearson':float(cov[2,3]/math.sqrt(cov[2,2]*cov[3,3])),
            'glucose_hba1c_spearman_quadrature':ranks,
            'hba1c_mean':float(mean[3]),'hba1c_sd':float(math.sqrt(cov[3,3])),
            'background_input_gh_correlation':float(corr[1,2]),
            'known_component_probability':pi}

def c02_law(p):
    # Order A, B, G, F, H. Integrate discrete age rather than replacing it by normal.
    aa=p['age']; b=p['bmi']; g=p['glucose']; h=p['hba1c']; R=np.asarray(p['latent_correlation'])
    ages=np.arange(aa['minimum'],aa['maximum']+1); n=len(ages)
    cuts=ndtri(np.linspace(0,1,n+1)); t=g['log_sd']*R[0,2]
    tilted=ndtr(cuts[1:]-t)-ndtr(cuts[:-1]-t)
    cag=(g['mean']-g['shift'])*(float(ages@tilted)-aa['mean'])
    cbg=b['mean']*(g['mean']-g['shift'])*math.expm1(b['log_sd']*g['log_sd']*R[1,2])
    cov=np.zeros((5,5)); cov[0,0]=aa['variance']; cov[1,1]=b['sd']**2; cov[2,2]=g['sd']**2
    cov[3,3]=p['female_probability']*(1-p['female_probability'])
    cov[0,2]=cov[2,0]=cag; cov[1,2]=cov[2,1]=cbg
    beta=np.asarray([p['coefficient_age'],p['coefficient_direct_bmi'],p['coefficient_glucose'],p['coefficient_female']])
    cov[:4,4]=cov[:4,:4]@beta; cov[4,:4]=cov[:4,4]
    residual=p['residual_half_width']**2/3
    cov[4,4]=float(beta@cov[:4,:4]@beta)+residual
    return {'covariance_order_A_B_G_F_H':cov.tolist(),
            'E1_bmi_age_sex':float(projection(cov,4,[1,0,3])[0]),
            'E2_glucose_age_sex':float(projection(cov,4,[2,0,3])[0]),
            'E3_age_bmi_glucose_sex':float(projection(cov,4,[0,1,2,3])[0]),
            'fully_adjusted_bmi':float(projection(cov,4,[1,0,2,3])[0]),
            'glucose_hba1c_pearson':float(cov[2,4]/math.sqrt(cov[2,2]*cov[4,4])),
            'hba1c_mean':h['mean'],'hba1c_sd':float(math.sqrt(cov[4,4])),
            'source_hba1c_sd':h['sd'],'residual_sd':math.sqrt(residual),
            'correlation_age_hba1c':float(cov[0,4]/math.sqrt(cov[0,0]*cov[4,4])),
            'correlation_logbmi_hba1c':p['coefficient_glucose']*(g['mean']-g['shift'])*g['log_sd']*R[1,2]/math.sqrt(cov[4,4]),
            'variance_identity_residual':float(cov[4,4]-h['sd']**2)}

def main():
    p1,h1=load_spec('C01');p2,h2=load_spec('C02')
    laws={'C01':c01_law(p1),'C02':c02_law(p2)}
    inputs=[h1,h2]
    for fn in ('PRIMARY_SUMMARY.csv','DIAGNOSTIC_SUMMARY.csv'):
        fp=DISPLAY/fn;inputs.append({'path':str(fp),'sha256':hashlib.sha256(fp.read_bytes()).hexdigest()})
    with (DISPLAY/'PRIMARY_SUMMARY.csv').open(encoding='utf-8-sig',newline='') as f:
        observed=[r for r in csv.DictReader(f) if r['author'] in laws]
    with (DISPLAY/'DIAGNOSTIC_SUMMARY.csv').open(encoding='utf-8-sig',newline='') as f:
        diagnostics=[r for r in csv.DictReader(f) if r['author'] in laws]
    mapping={'E1':'E1_bmi_age_sex','E2':'E2_glucose_age_sex','E3':'E3_age_bmi_glucose_sex'}
    comparisons=[]
    for r in observed:
        law=laws[r['author']][mapping[r['endpoint']]]
        comparisons.append({'author':r['author'],'quantity':r['endpoint'],'law':law,'frozen_seed_mean':float(r['generated_mean']),'reference':float(r['reference']),'law_minus_reference':law-float(r['reference']),'seed_mean_minus_law':float(r['generated_mean'])-law})
    for r in diagnostics:
        key=r['diagnostic']
        if key not in ('hba1c_mean','hba1c_sd','glucose_hba1c_pearson','glucose_hba1c_spearman'):continue
        if key=='glucose_hba1c_spearman':
            if r['author']!='C01':continue
            law=laws['C01']['glucose_hba1c_spearman_quadrature'][-1]['spearman']
        else:law=laws[r['author']][key]
        comparisons.append({'author':r['author'],'quantity':key,'law':law,'frozen_seed_mean':float(r['mean']),'reference':float(r['reference']),'law_minus_reference':law-float(r['reference']),'seed_mean_minus_law':float(r['mean'])-law})
    result={'scope':'Deterministic summary-only diagnostic; no random draws, candidate execution, participant records or fitting. Law-reference differences are descriptive, not a causal decomposition of error.','inputs':inputs,'laws':laws,'comparisons':comparisons}
    (OUT/'ANALYTIC_C01_C02.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (OUT/'ANALYTIC_C01_C02.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(comparisons[0]));wr.writeheader();wr.writerows(comparisons)
    print(json.dumps({'comparisons':comparisons,'C01_spearman_convergence':laws['C01']['glucose_hba1c_spearman_quadrature'],'C02_variance_residual':laws['C02']['variance_identity_residual']},indent=2))

if __name__=='__main__': main()
