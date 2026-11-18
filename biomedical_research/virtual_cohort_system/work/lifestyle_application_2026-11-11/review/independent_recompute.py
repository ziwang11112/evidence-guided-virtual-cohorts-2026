"""Independent post-closure numerical audit. No production analysis imports.

Execution requires explicit parent authorization, a source/code audit, and the
completed production result. Reads local rows only; exports aggregates only.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
TRAITS = ['bmi', 'total_cholesterol', 'hdl_cholesterol']
GROUPS = ['pastoralist', 'rural_nonpastoralist', 'urban_nonpastoralist']
COLUMNS = ['id', 'age', 'sex', 'lifestyle'] + TRAITS
REAL_COLUMNS = ['Individual ID', 'Age', 'Sex', 'Lifestyle category', 'BMI', 'Total cholesterol', 'HDL cholesterol']
REAL_GROUPS = dict(zip(['Pastoralist', 'Non pastoralist, rural', 'Non pastoralist, urban'], GROUPS))
CONTRASTS = [('rural_minus_pastoralist', [0.,1.,0.,0.,0.]),
             ('urban_minus_pastoralist', [0.,0.,1.,0.,0.]),
             ('urban_minus_rural', [0.,-1.,1.,0.,0.])]


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def parse_independently(path, real):
    rows = []
    ids = set()
    total = missing_cov = ineligible = 0
    missing = ('', 'NA', 'NaN', 'nan')
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        records = csv.reader(stream, delimiter='\t' if real else ',')
        header = next(records)
        names = REAL_COLUMNS if real else COLUMNS
        positions = [header.index(name) for name in names]
        if not real and header != COLUMNS:
            raise ValueError('Unexpected virtual schema/order')
        for row in records:
            if not row: continue
            total += 1
            values = [row[i].strip() if i < len(row) else '' for i in positions]
            identifier, age, sex, group, *outcomes = values
            if identifier in missing or identifier in ids: raise ValueError('Missing/duplicate id')
            ids.add(identifier)
            if sex not in ['F', 'M'] + list(missing): raise ValueError('Invalid sex')
            mapping = REAL_GROUPS if real else {g:g for g in GROUPS}
            if group not in list(mapping) + list(missing): raise ValueError('Invalid lifestyle')
            numeric = [np.nan if v in missing else float(v) for v in [age] + outcomes]
            age = numeric[0]
            incomplete = not math.isfinite(age) or sex in missing or group in missing
            if real and incomplete:
                missing_cov += 1
                continue
            if incomplete: raise ValueError('Incomplete generated covariates')
            if real and age <= 18:
                ineligible += 1
                continue
            rows.append([identifier, age, sex, mapping[group]] + numeric[1:])
    frame = pd.DataFrame(rows, columns=COLUMNS)
    report = dict(raw_rows=total, missing_covariates=missing_cov,
                  age_ineligible=ineligible, retained_covariate_rows=len(frame)) if real else None
    return frame, report


def fit_qr(x, y):
    if len(y) <= x.shape[1] or np.linalg.matrix_rank(x) != x.shape[1]:
        return None
    fitted = sm.OLS(y, x).fit(method='qr')
    if not np.isfinite(fitted.ssr) or fitted.ssr <= 1e-15:
        return None
    return fitted


def extract_contrasts(fit, trait, stratum, selected):
    rows = []
    for name, vector in CONTRASTS:
        row = dict(trait=trait, stratum=stratum, contrast=name, status='unavailable',
                   selected_by_paper_rule=selected)
        if fit is not None:
            c = np.array(vector[:fit.model.exog.shape[1]])
            comparison = fit.t_test(c)
            ci = comparison.conf_int(alpha=.05).ravel()
            row.update(status='computed', estimate=float(np.ravel(comparison.effect)[0]),
                       se=float(np.ravel(comparison.sd)[0]), lower=float(ci[0]), upper=float(ci[1]),
                       p_value=float(comparison.pvalue), n=int(fit.nobs), df=int(fit.df_resid))
        rows.append(row)
    return rows


def independent_analysis(frame):
    d = frame.loc[frame.age > 18].copy()
    out = dict(input_rows=len(frame), eligible_age_rows=len(d), age_excluded=len(frame)-len(d),
               hdl_above_tc_count=int(((d.hdl_cholesterol > d.total_cholesterol) &
                                      d.hdl_cholesterol.notna() & d.total_cholesterol.notna()).sum()),
               trait_status=[], group_summaries=[], interactions=[], contrasts=[])
    for trait in TRAITS:
        valid = d[trait].notna() & np.isfinite(d[trait]) & (d[trait] > 0)
        f = d.loc[valid]
        y = f[trait].to_numpy(float)
        sd = float(np.std(y, ddof=1)) if len(y) > 1 else None
        st = dict(trait=trait, n=len(y), missing=int(d[trait].isna().sum()),
                  nonfinite_nonmissing=int((d[trait].notna() & ~np.isfinite(d[trait])).sum()),
                  nonpositive=int((d[trait].notna() & np.isfinite(d[trait]) & (d[trait] <= 0)).sum()),
                  mean=float(np.mean(y)) if len(y) else None, sample_sd=sd)
        for g in GROUPS:
            values = f.loc[f.lifestyle == g, trait].to_numpy(float)
            out['group_summaries'].append(dict(trait=trait, lifestyle=g, n=len(values),
                mean=float(np.mean(values)) if len(values) else None,
                sd=float(np.std(values, ddof=1)) if len(values)>1 else None))
        if len(y)<=7 or sd is None or not np.isfinite(sd) or sd<=1e-12:
            st['status']='unavailable'
            out['interactions'].append(dict(trait=trait,status='unavailable'))
            for s in ['pooled','F','M']:out['contrasts'] += extract_contrasts(None,trait,s,None)
            out['trait_status'].append(st)
            continue
        z=(y-y.mean())/sd
        rural=(f.lifestyle==GROUPS[1]).to_numpy(float)
        urban=(f.lifestyle==GROUPS[2]).to_numpy(float)
        female=(f.sex=='F').to_numpy(float)
        x=np.column_stack([np.ones(len(f)),rural,urban,f.age.to_numpy(float),female])
        reduced=fit_qr(x,z)
        full=fit_qr(np.column_stack([x,rural*female,urban*female]),z)
        selected=None
        if reduced is not None and full is not None:
            lr,p,df=full.compare_lr_test(reduced)
            selected=bool(p<.05)
            out['interactions'].append(dict(trait=trait,status='computed',lr=float(max(0,lr)),
                p_value=float(p),df=int(df),selects_sex_specific=selected))
        else:out['interactions'].append(dict(trait=trait,status='unavailable'))
        out['contrasts'] += extract_contrasts(reduced,trait,'pooled',not selected if selected is not None else None)
        for s in ['F','M']:
            ix=(f.sex==s).to_numpy()
            out['contrasts'] += extract_contrasts(fit_qr(x[ix,:4],z[ix]),trait,s,selected)
        st.update(status='computed' if reduced is not None else 'unavailable',
                  selected_branch=('sex_specific' if selected else 'pooled') if selected is not None else 'unresolved')
        out['trait_status'].append(st)
        for c in out['contrasts']:
            if c['trait']==trait and c['status']=='computed':
                for key in ['estimate','se','lower','upper']:c['raw_'+key]=c[key]*sd
                c['raw_unit']='kg/m2' if trait=='bmi' else 'mg/dL'
    pooled=[c for c in out['contrasts'] if c['stratum']=='pooled']
    if len(pooled)==9 and all(c['status']=='computed' for c in pooled):
        for c,q in zip(pooled,multipletests([c['p_value'] for c in pooled],method='fdr_bh')[1]):
            c['q_subset_bh9']=float(q)
    else:
        for c in pooled:c['q_subset_bh9']=None
    return out


def main():
    if sys.argv[1:] != ['--authorized-after-results']:
        raise SystemExit('Requires explicit parent numerical-review authorization')
    output=ROOT/'review/INDEPENDENT_NUMERICAL_REVIEW.json'
    if output.exists():raise RuntimeError('Independent numerical audit is already closed')
    source_audit=ROOT/'review/CONSTRUCTION_CODE_REVIEW.json'
    assert source_audit.exists(),'Freeze source/code-only audit before numerical phase'
    inputs=read(ROOT/'EVALUATION_INPUTS.json')
    production=read(ROOT/'ANALYSIS_RESULTS.json')
    freeze=read(ROOT/'LAUNCH_FREEZE.json')
    checks=[];max_error=0.;numeric=0
    def check(label,value):checks.append(dict(check=label,passed=bool(value)))
    def compare(label,a,b):
        nonlocal max_error,numeric
        if a is None or b is None or isinstance(a,(str,bool)) or isinstance(b,(str,bool)):
            check(label,a==b);return
        error=abs(float(a)-float(b));numeric+=1;max_error=max(max_error,error)
        check(label,math.isfinite(error) and error<=1e-8+1e-9*abs(float(b)))
    def verify():
        for n,h in freeze['files'].items():check('freeze:'+n,sha(ROOT/n)==h)
        for n,h in freeze['external_files'].items():check('external:'+n,sha(n)==h)
        for n,h in inputs['files'].items():check('input-code:'+n,sha(ROOT/n)==h)
        for t in inputs['inputs']:
            if t['path']:check('input-table:'+t['dataset_id'],sha(t['path'])==t['sha256'])
    verify()
    prod={r['dataset_id']:r for r in production['results']}
    with (ROOT/'ANALYSIS_CONTRASTS.csv').open(encoding='utf-8',newline='') as stream: csv_rows=list(csv.DictReader(stream))
    csv_map={(r['dataset_id'],r['trait'],r['stratum'],r['contrast']):r for r in csv_rows}
    check('seven dataset slots',len(inputs['inputs'])==len(production['results'])==len(prod)==7)
    check('189 unique contrast slots exported',len(csv_rows)==len(csv_map)==189)
    rebuilt=[]
    for t in inputs['inputs']:
        name=t['dataset_id'];record=dict(dataset_id=name,kind=t['kind'])
        old=prod[name]
        if not t['path']:
            check(name+':unavailable-retained',old['status']==t['status'])
            record.update(status=t['status'],reason='Bound input unavailable; no replacement')
            rebuilt.append(record);continue
        f,exclusions=parse_independently(t['path'],t['kind']=='real_reference')
        if exclusions is not None:check(name+':reference_exclusions',exclusions==old.get('reference_exclusions'))
        actual=independent_analysis(f)
        record.update(status='computed',reference_exclusions=exclusions,analysis=actual)
        check(name+':computed',old['status']=='computed')
        expected=old['analysis']
        for key in ['input_rows','eligible_age_rows','age_excluded','hdl_above_tc_count']:compare(name+':'+key,actual[key],expected[key])
        for group,keys in [('trait_status',['n','missing','nonfinite_nonmissing','nonpositive','mean','sample_sd','status','selected_branch']),
                           ('group_summaries',['n','mean','sd']),('interactions',['status','lr','df','p_value','selects_sex_specific'])]:
            check(name+':'+group+':count',len(actual[group])==len(expected[group]))
            for i,(a,b) in enumerate(zip(actual[group],expected[group])):
                for key in keys:
                    if key in a or key in b:compare(f'{name}:{group}:{i}:{key}',a.get(key),b.get(key))
        for a,b in zip(actual['contrasts'],expected['contrasts']):
            identity=(name,a['trait'],a['stratum'],a['contrast'])
            check(str(identity)+':identity',all(a[k]==b[k] for k in ['trait','stratum','contrast']))
            check(str(identity)+':csvstatus',csv_map[identity]['status']==a['status'])
            for key in ['status','selected_by_paper_rule','estimate','se','lower','upper','p_value','n','df',
                        'raw_estimate','raw_se','raw_lower','raw_upper','raw_unit','q_subset_bh9']:
                if key in a or key in b:compare(str(identity)+':'+key,a.get(key),b.get(key))
            for key in ['estimate','se','lower','upper','p_value','n','df','raw_estimate','raw_se','raw_lower','raw_upper','q_subset_bh9']:
                if a.get(key) is not None:compare(str(identity)+':csv:'+key,a[key],float(csv_map[identity][key]))
        rebuilt.append(record)
    verify()
    issues=[c['check'] for c in checks if not c['passed']]
    report=dict(status='pass' if not issues else 'failed',created_utc=datetime.now(timezone.utc).isoformat(),
        algorithm='Independent positional CSV parsing; statsmodels QR OLS, t_test and likelihood comparisons; independent BH implementation',
        checks=len(checks),failed_checks=issues,numeric_values_compared=numeric,maximum_absolute_difference=max_error,
        datasets=len(rebuilt),records=rebuilt,raw_rows_exported=0,new_generations=0,new_api_calls=0,
        input_hashes_unchanged=not any('input-table:' in s for s in issues),
        hashes={n:sha(ROOT/n) for n in ['LAUNCH_FREEZE.json','EVALUATION_INPUTS.json','ANALYSIS_RESULTS.json','ANALYSIS_CONTRASTS.csv',
            'review/CONSTRUCTION_CODE_REVIEW.json','review/independent_recompute.py']})
    with output.open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False)
    print(json.dumps({k:report[k] for k in ['status','checks','failed_checks','numeric_values_compared','maximum_absolute_difference','datasets']}))
    if issues:raise SystemExit(1)


if __name__=='__main__':main()
