import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generator requires observed=None.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    female = rng.random(n) < spec['female_probability']
    town = rng.random(n) < spec['town_linked_probability']
    age = spec['age_lower'] + rng.gamma(spec['age_gamma_shape'], spec['age_gamma_scale'], n)
    bad = age > spec['age_upper']
    while bad.any():
        age[bad] = spec['age_lower'] + rng.gamma(spec['age_gamma_shape'], spec['age_gamma_scale'], int(bad.sum()))
        bad = age > spec['age_upper']
    bmi_mean = (spec['bmi_rural_male_mean'] + spec['bmi_female_increment'] * female
                + spec['bmi_town_increment'] * town
                + spec['bmi_age_slope'] * (age-spec['age_center']))
    bmi_sd = np.where(town, spec['bmi_town_sd'], spec['bmi_rural_sd'])
    excess_mean = bmi_mean - spec['bmi_shift']
    logvar = np.log1p((bmi_sd/excess_mean)**2)
    bmi = spec['bmi_shift'] + np.exp(np.log(excess_mean)-logvar/2 + np.sqrt(logvar)*rng.standard_normal(n))
    a = age - spec['age_center']
    b = bmi - spec['bmi_center']
    f = female.astype(float)-spec['female_probability']
    # Log-BMI predictor: same reference local derivative, only polynomial
    # growth in BMI. Unlike exp(positive*lognormal BMI), all moments exist.
    tc_bmi_predictor = spec['bmi_center'] * np.log(bmi/spec['bmi_center'])
    tc_mean = spec['tc_reference_mean'] * np.exp(
        (spec['tc_bmi_local_slope']*tc_bmi_predictor + spec['tc_age_local_slope']*a
         + spec['tc_female_increment']*f + spec['tc_town_increment']*town)/spec['tc_reference_mean'])
    hd_mean = spec['hdl_reference_mean'] * np.exp(
        (spec['hdl_bmi_local_slope']*b + spec['hdl_age_local_slope']*a
         + spec['hdl_female_increment']*f + spec['hdl_town_increment']*town)/spec['hdl_reference_mean'])
    # Concentration model, not independently noisy TC and HDL assays.
    # On this spec's entire support min(tc_mean)>2.89 and max(hd_mean)<1.55.
    # Thus subtraction defines a strictly positive non-HDL mean without caps.
    nh_mean = tc_mean-hd_mean
    if np.any(nh_mean <= 0):
        raise ValueError('Invalid specification: non-HDL conditional mean must be positive.')
    # Preserve v000's hypothetical reference TC variance and TC-HDL covariance.
    # reference_tc_hdl_log_correlation is an ASSUMED reference calibration,
    # NOT the log-error correlation of the new non-HDL/HDL pair.
    mt = spec['tc_reference_mean']
    mh = spec['hdl_reference_mean']
    mn = mt-mh
    st = np.sqrt(np.log1p(spec['tc_reference_cv']**2))
    sh = np.sqrt(np.log1p(spec['hdl_conditional_cv']**2))
    vt = (mt*spec['tc_reference_cv'])**2
    vh = (mh*spec['hdl_conditional_cv'])**2
    cth = mt*mh*np.expm1(spec['reference_tc_hdl_log_correlation']*st*sh)
    vn = vt+vh-2*cth
    sn = np.sqrt(np.log1p(vn/(mn*mn)))
    rho_nh = np.log1p((cth-vh)/(mn*mh))/(sn*sh)
    if not (vn > 0 and abs(rho_nh) < 1):
        raise ValueError('Invalid reference covariance calibration.')
    z1 = rng.standard_normal(n)
    z2 = rng.standard_normal(n)
    nonhdl = nh_mean*np.exp(sn*z1-sn*sn/2)
    hdl = hd_mean*np.exp(sh*(rho_nh*z1+np.sqrt(1-rho_nh*rho_nh)*z2)-sh*sh/2)
    total = hdl+nonhdl
    return pd.DataFrame({
        'id': ['FIC%06d' % (i+1) for i in range(n)],
        'age': age,
        'sex': np.where(female, 'F', 'M'),
        'bmi': bmi,
        'total_cholesterol': total,
        'hdl_cholesterol': hdl
    }, columns=['id','age','sex','bmi','total_cholesterol','hdl_cholesterol'])
