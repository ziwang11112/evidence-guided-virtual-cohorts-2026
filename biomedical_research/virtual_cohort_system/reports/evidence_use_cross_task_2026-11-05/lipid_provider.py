"""Generated-only lipid estimates; no reference loading or model parameters.

Reuses the existing K02 estimator and its fixed eligibility/design. The two
lipids arrive in mmol/L; only an explicitly declared unit conversion occurs.
This does not claim assay or population equivalence.
"""
from pathlib import Path
import importlib.util
import math
import numpy as np

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
ESTIMATOR = PROJECT / 'work/scaleup_2026-11-01/analysis/k02_analysis.py'
LIPID_TO_MG_DL = 38.67


def _module():
    definition = importlib.util.spec_from_file_location('cross_task_k02_estimator', ESTIMATOR)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module


def _record(identifier, value, unit, n, reason=None):
    ok = value is not None and math.isfinite(float(value))
    return {'id': identifier, 'value': float(value) if ok else None,
            'unit': unit, 'status': 'computed' if ok else 'unavailable',
            'n': n, 'reason': None if ok else (reason or 'nonfinite')}


def generated_statistics(frame, expected_rows=3000):
    required = ['id', 'age', 'sex', 'bmi', 'total_cholesterol', 'hdl_cholesterol']
    if len(frame) != expected_rows or set(frame.columns) != set(required):
        raise ValueError('Wrong delivered row count or lipid schema')
    if frame['id'].isna().any() or frame['id'].duplicated().any():
        raise ValueError('Missing or duplicate identifiers')
    converted = frame.copy(deep=True)
    for col in ('total_cholesterol', 'hdl_cholesterol'):
        converted[col] = converted[col] * LIPID_TO_MG_DL
    result = _module().analyze_frame(converted, role='generated')
    if result['selection']['eligible_rows'] != expected_rows:
        raise ValueError('Delivered table contains rows outside fixed eligibility')
    rows = []
    for key, endpoint in result['estimands'].items():
        rows.append(_record(key, endpoint['estimate'], endpoint['unit'], expected_rows,
                            endpoint.get('reason')))
    diagnostics = []
    for col, unit in [('age', 'year'), ('bmi', 'kg/m^2'),
                      ('total_cholesterol', 'mg/dL'), ('hdl_cholesterol', 'mg/dL')]:
        y = converted[col].to_numpy(dtype=float)
        diagnostics.append(_record(col+'.mean', np.mean(y), unit, expected_rows))
        diagnostics.append(_record(col+'.sd_sample', np.std(y, ddof=1), unit, expected_rows))
        for q in (.1, .5, .9):
            diagnostics.append(_record(col+'.q'+str(int(q*100)),
                                       np.quantile(y, q, method='linear'), unit, expected_rows))
    x = np.column_stack([np.ones(expected_rows), (converted.age.to_numpy()-50)/10,
                         converted.sex.eq('F').to_numpy(dtype=float),
                         (converted.bmi.to_numpy()-25)/5])
    full_rank = np.linalg.matrix_rank(x) == 4
    for col in ('total_cholesterol', 'hdl_cholesterol'):
        rms = None
        if full_rank:
            y = converted[col].to_numpy(dtype=float)
            residual = y - x @ np.linalg.lstsq(x, y, rcond=None)[0]
            rms = np.sqrt(np.mean(residual**2))
        diagnostics.append(_record(col+'.conditional_rms', rms, 'mg/dL', expected_rows,
                                   'rank_deficient_design'))
    diagnostics.append(_record('sex.F_fraction', converted.sex.eq('F').mean(), '1', expected_rows))
    duplicate_n = int(converted.drop(columns=['id']).duplicated().sum())
    return {'analyses': rows, 'diagnostics': diagnostics, 'n': expected_rows,
            'quality': {'duplicate_measurement_rows': duplicate_n,
                        'full_design_rank': int(np.linalg.matrix_rank(x)),
                        'reference_read': False,
                        'unit_conversion': 'TC/HDL mmol/L times 38.67 to mg/dL; no assay harmonization'}}
