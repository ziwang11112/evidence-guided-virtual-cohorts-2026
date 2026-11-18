import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator is for whole-cohort generation only.')
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
                + spec['bmi_age_slope'] * (age - spec['age_center']))
    bmi_sd = np.where(town, spec['bmi_town_sd'], spec['bmi_rural_sd'])
    excess_mean = bmi_mean - spec['bmi_shift']
    logvar = np.log1p((bmi_sd / excess_mean) ** 2)
    bmi = spec['bmi_shift'] + np.exp(np.log(excess_mean) - logvar/2 + np.sqrt(logvar)*rng.standard_normal(n))
    a = age - spec['age_center']
    b = bmi - spec['bmi_center']
    f = female.astype(float) - spec['female_probability']
    # Positive affine BMI contribution rather than exponential-of-lognormal.
    # With this spec BMI > 12, so tc_bmi_factor > 3.8 - .055*10 = 3.25.
    # Remaining predictors are bounded, and BMI has all polynomial moments.
    tc_bmi_factor = spec['tc_reference_mean'] + spec['tc_bmi_local_slope'] * b
    tc_mean = tc_bmi_factor * np.exp(
        (spec['tc_age_local_slope']*a + spec['tc_female_increment']*f
         + spec['tc_town_increment']*town) / spec['tc_reference_mean'])
    # The HDL BMI coefficient is negative; its mean is bounded above on the
    # specified support, so its original exponential link has finite moments.
    hd_mean = spec['hdl_reference_mean'] * np.exp(
        (spec['hdl_bmi_local_slope']*b + spec['hdl_age_local_slope']*a
         + spec['hdl_female_increment']*f + spec['hdl_town_increment']*town) / spec['hdl_reference_mean'])
    s_tc = np.sqrt(np.log1p(spec['tc_conditional_cv']**2))
    s_hd = np.sqrt(np.log1p(spec['hdl_conditional_cv']**2))
    z1 = rng.standard_normal(n)
    z2 = rng.standard_normal(n)
    rho = spec['log_error_correlation']
    total = tc_mean * np.exp(s_tc*z1 - s_tc*s_tc/2)
    hdl = hd_mean * np.exp(s_hd*(rho*z1 + np.sqrt(1-rho*rho)*z2) - s_hd*s_hd/2)
    values = np.column_stack([age, bmi, total, hdl])
    if not (np.isfinite(values).all() and (values > 0).all()):
        raise FloatingPointError('Nonfinite or nonpositive generated value; no rows removed.')
    return pd.DataFrame({
        'id': ['FIC%06d' % (i+1) for i in range(n)],
        'age': age,
        'sex': np.where(female, 'F', 'M'),
        'bmi': bmi,
        'total_cholesterol': total,
        'hdl_cholesterol': hdl
    }, columns=['id','age','sex','bmi','total_cholesterol','hdl_cholesterol'])
