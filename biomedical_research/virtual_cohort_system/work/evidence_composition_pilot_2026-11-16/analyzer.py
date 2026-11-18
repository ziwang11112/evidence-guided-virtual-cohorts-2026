"""Unified table-only evaluator. Never import an author's generator on the host.

Reference values are host-only mathematical consequences, not patient truth.
OLS residualization is cross-checked by covariance algebra in verify_analysis.py.
"""
import numpy as np
import pandas as pd

VARIABLES = {
    'adjusted': ['X', 'Y', 'Z'],
    'longitudinal': ['X_visit1', 'Y_visit1', 'X_visit2', 'Y_visit2'],
}
ESTIMANDS = {
    'adjusted': ['partial_xy_given_z', 'marginal_xy', 'slope_x_on_z'],
    'longitudinal': ['change_correlation', 'same_visit_correlation', 'cross_visit_correlation'],
}
REFERENCE = {
    'adjusted': dict(zip(ESTIMANDS['adjusted'], [.21875, .5, .6])),
    'longitudinal': dict(zip(ESTIMANDS['longitudinal'], [-.6, .52, .64])),
}

def identified(family, condition, name):
    if condition == 'combined': return True
    if family == 'adjusted':
        return (name == 'marginal_xy' and condition == 'anchor_only') or (name == 'slope_x_on_z' and condition == 'bridge_only')
    return (name == 'same_visit_correlation' and condition == 'bridge_only') or (name == 'cross_visit_correlation' and condition == 'anchor_only')

def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if min(np.var(a), np.var(b)) <= 1e-14: raise ValueError('Degenerate analysis variable')
    return float(np.corrcoef(a, b)[0, 1])

def evaluate(frame, family):
    arr = frame[VARIABLES[family]].to_numpy(float)
    if len(arr) < 10 or not np.isfinite(arr).all(): raise ValueError('Invalid numeric table')
    means = arr.mean(axis=0); cov = np.cov(arr, rowvar=False, ddof=1)
    if np.linalg.eigvalsh(cov).min() < -1e-8: raise ValueError('Invalid sample covariance')
    result = {'means': means.tolist(), 'variances': np.diag(cov).tolist(), 'n': len(arr)}
    if family == 'adjusted':
        x, y, z = arr.T
        design = np.column_stack([np.ones(len(arr)), z])
        bx = np.linalg.lstsq(design, x, rcond=None)[0]
        by = np.linalg.lstsq(design, y, rcond=None)[0]
        result['analyses'] = dict(zip(ESTIMANDS[family], [corr(x-design@bx, y-design@by), corr(x,y), float(bx[1])]))
        result['source_statistics'] = {'xy': corr(x,y), 'xz': corr(x,z), 'yz': corr(y,z)}
    else:
        x1, y1, x2, y2 = arr.T
        result['analyses'] = dict(zip(ESTIMANDS[family], [corr(x2-x1,y2-y1), (corr(x1,y1)+corr(x2,y2))/2, corr(x1,y2)]))
        between_var = [float(cov[0,2]), float(cov[1,3])]
        if min(between_var) <= 0: raise ValueError('Nonpositive estimated between-person variance')
        between_corr = float((cov[0,3]+cov[2,1])/2/np.sqrt(between_var[0]*between_var[1]))
        result['source_statistics'] = {'between_correlation': between_corr, 'same_visit_correlation': result['analyses']['same_visit_correlation']}
        result['between_variances'] = between_var
        result['within_variances'] = [float(np.var(x2-x1,ddof=1)/2), float(np.var(y2-y1,ddof=1)/2)]
        result['cross_covariance_asymmetry'] = float(cov[0,3]-cov[2,1])
    return result

def source_checks(result, family, condition):
    checks = []
    def add(name, value, expected, tolerance):
        checks.append(dict(name=name,value=float(value),expected=expected,tolerance=tolerance,absolute_error=abs(value-expected),within_tolerance=bool(abs(value-expected)<=tolerance)))
    var = 1 if family == 'adjusted' else 5
    for name, mean, variance in zip(VARIABLES[family],result['means'],result['variances']):
        add('mean_'+name,mean,0,.12*np.sqrt(var))
        add('variance_'+name,variance,var,.12*var)
    s = result['source_statistics']
    if family == 'adjusted':
        if condition in ('anchor_only','combined'): add('source_A_xy',s['xy'],.5,.08)
        if condition in ('bridge_only','combined'):
            add('source_B_xz',s['xz'],.6,.08); add('source_B_yz',s['yz'],.6,.08)
    else:
        for j in range(2):
            add(f'between_variance_{j}',result['between_variances'][j],4,.48)
            add(f'within_variance_{j}',result['within_variances'][j],1,.12)
        if condition in ('anchor_only','combined'): add('source_A_between',s['between_correlation'],.8,.08)
        if condition in ('bridge_only','combined'): add('source_B_same_visit',s['same_visit_correlation'],.52,.08)
    return checks

def label_checks(record, family, condition):
    claims = {r['name']:r for r in record['requested_estimands']}
    rows=[]
    for name in ESTIMANDS[family]:
        r=claims[name]; truth=identified(family,condition,name)
        rows.append({'name':name,'expected_identified':truth,'declared_status':r['status'],
                     'identifiedness_correct':(r['status']=='identified')==truth,
                     'declared_value':r.get('value'),'basis':r['basis']})
    return rows
