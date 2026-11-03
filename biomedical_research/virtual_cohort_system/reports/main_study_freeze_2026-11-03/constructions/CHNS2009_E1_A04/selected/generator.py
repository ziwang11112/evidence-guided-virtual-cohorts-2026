"""Bounded whole-cohort scenario; execution belongs only to the isolated controller."""
import math
import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort mode requires observed=None')
    p = spec['parameters']
    c, st = p['target_context'], p['structure']
    n = p['design']['n_rows']
    q = p['source_projection_constraints']
    unit = p['unit_mapping']['ngsp_multiplier']
    rho = st['bmi_glucose_rho']
    source_cov = rho * q['reference_bmi_sd'] * q['reference_glucose_sd']
    kb = source_cov / q['reference_bmi_sd']**2
    kg = source_cov / q['reference_glucose_sd']**2
    beta_b = (unit*q['bmi_ifcc'] - kb*unit*q['fpg_ifcc'])/(1-kb*kg)
    beta_g = unit*q['fpg_ifcc'] - kg*beta_b
    a, s = st['age_hba1c_coefficient'], st['female_hba1c_coefficient']
    pc, pf = c['class_probability'], c['female_probability']
    vd = pc*(1-pc)
    age_mean = (c['age_low']+c['age_high'])/2
    age_variance = ((c['age_high']-c['age_low']+1)**2-1)/12
    if c['age_kind'] != 'integer_uniform':
        raise ValueError('Target age must be integer uniform')
    vg = c['glucose_sd']**2
    if c['glucose_sd_mode'] == 'total':
        vg -= c['glucose_class_shift']**2*vd
    sg = math.sqrt(vg)
    u_loading = beta_b*c['bmi_sd'] + beta_g*sg*rho
    v_loading = beta_g*sg*math.sqrt(1-rho**2)
    vh = c['hba1c_sd']**2
    if c['hba1c_sd_mode'] == 'total':
        vh -= u_loading**2+v_loading**2+a*a*age_variance+s*s*pf*(1-pf)+c['hba1c_class_total_shift']**2*vd
    sh = math.sqrt(vh)
    rng = np.random.default_rng(seed)
    half = st['uniform_half_width']
    u = rng.uniform(-half, half, n)
    v = rng.uniform(-half, half, n)
    e = rng.uniform(-half, half, n)
    age = rng.integers(c['age_low'], c['age_high']+1, n)
    female = rng.binomial(1, pf, n)
    d = rng.binomial(1, pc, n)-pc
    bmi = c['bmi_mean']+c['bmi_sd']*u
    glucose = c['glucose_mean']+sg*(rho*u+math.sqrt(1-rho**2)*v)+c['glucose_class_shift']*d
    extra = c['hba1c_class_total_shift']-beta_g*c['glucose_class_shift']
    hba1c = c['hba1c_mean']+beta_b*(bmi-c['bmi_mean'])+beta_g*(glucose-c['glucose_mean'])+a*(age-age_mean)+s*(female-pf)+extra*d+sh*e
    result = pd.DataFrame({'row_id':[p['design']['row_id_prefix']+str(i+1).zfill(6) for i in range(n)],'age':age,'female':female,'bmi':bmi,'glucose':glucose,'hba1c':hba1c})
    return result[p['design']['columns']]
