"""Controlled arithmetic fixtures, not patient or scientific validation."""
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location('lipid_provider', Path(__file__).with_name('lipid_provider.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def frame():
    # Orthogonal residuals make adjusted slopes and residual dependence known.
    rng = np.random.default_rng(17)
    n = 48
    age = np.linspace(20, 70, n)
    female = np.tile([0, 1], n//2)
    bmi = 23 + rng.normal(0, 2, n)
    x = np.column_stack([np.ones(n), (age-50)/10, female, (bmi-25)/5])
    residual = rng.normal(size=(n, 2))
    residual -= x @ np.linalg.lstsq(x, residual, rcond=None)[0]
    q, _ = np.linalg.qr(residual)
    tc = x @ np.array([170., 3., 4., 8.]) + 6*q[:, 0]
    hdl = x @ np.array([55., 1., 2., -4.]) + 4*(.3*q[:, 0]+np.sqrt(.91)*q[:, 1])
    return pd.DataFrame({'id': [str(i) for i in range(n)], 'age': age,
                         'sex': np.where(female, 'F', 'M'), 'bmi': bmi,
                         'total_cholesterol': tc/38.67, 'hdl_cholesterol': hdl/38.67})


def test_known_adjusted_slopes_residual_relation_and_units():
    data = frame()
    before = data.copy(deep=True)
    out = p.generated_statistics(data, len(data))
    actual = {r['id']: r for r in out['analyses']}
    assert actual['K02-TC-BMI']['value'] == pytest.approx(8.)
    assert actual['K02-HDL-BMI']['value'] == pytest.approx(-4.)
    assert actual['K02-LIPID-RESIDUAL']['value'] == pytest.approx(.3)
    assert actual['K02-TC-BMI']['unit'] == 'mg/dL per 5 kg/m^2'
    assert len(out['diagnostics']) == 23
    pd.testing.assert_frame_equal(data, before)


def test_duplicate_id_and_ineligible_rows_are_not_silently_removed():
    data = frame()
    data.loc[1, 'id'] = data.loc[0, 'id']
    with pytest.raises(ValueError, match='duplicate'):
        p.generated_statistics(data, len(data))
    data = frame()
    data.loc[0, 'hdl_cholesterol'] = -1
    with pytest.raises(ValueError, match='eligibility'):
        p.generated_statistics(data, len(data))


def test_constant_covariate_keeps_unavailable_endpoints():
    data = frame()
    data['sex'] = 'F'
    out = p.generated_statistics(data, len(data))
    assert len(out['analyses']) == 3
    assert all(row['status'] == 'unavailable' for row in out['analyses'])
    assert all(row['status'] == 'unavailable' for row in out['diagnostics']
               if row['id'].endswith('conditional_rms'))
