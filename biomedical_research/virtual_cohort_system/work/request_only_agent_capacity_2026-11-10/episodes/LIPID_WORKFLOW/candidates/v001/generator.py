import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Generate an entirely fictional adult cohort; all lipids are in mmol/L."""
    if observed is not None:
        raise ValueError('This generator implements whole-cohort generation only.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    female = rng.random(n) < spec['p_female']
    sex = np.where(female, 'F', 'M')
    ap = spec['age']
    age = ap['lower'] + (ap['upper'] - ap['lower']) * rng.beta(ap['alpha'], ap['beta'], n)
    settled = rng.random(n) < spec['p_transition']
    bp = spec['bmi']
    bmi = np.empty(n)
    mean_h = np.empty(n)
    mean_n = np.empty(n)
    var_h = np.empty(n)
    var_n = np.empty(n)

    for label in ('F', 'M'):
        idx = np.flatnonzero(sex == label)
        p = spec['sex_parameters'][label]
        g = settled[idx].astype(float)
        age_delta = age[idx] - p['reference_age']
        bmi_center = p['reference_bmi'] + p['transition_bmi_difference'] * g
        bmi_mean = bmi_center + bp['age_slope'] * age_delta
        width = bp['upper'] - bp['lower']
        umean = (bmi_mean - bp['lower']) / width
        uvar = (bp['conditional_sd'] / width) ** 2
        concentration = umean * (1.0 - umean) / uvar - 1.0
        if np.any(concentration <= 0):
            raise ValueError('BMI beta moments are infeasible.')
        bmi[idx] = bp['lower'] + width * rng.beta(umean * concentration, (1.0 - umean) * concentration)

        # Transport the published per-SD effects to a modeled BMI SD, not a
        # claim that the Malawian empirical SD was known to equal this value.
        transported_sd = p['effect_transport_bmi_sd']
        beta_tc = ((1.0 - g) * p['tc_per_sd_rural'] + g * p['tc_per_sd_transition']) / transported_sd
        beta_h = ((1.0 - g) * p['hdl_per_sd_rural'] + g * p['hdl_per_sd_transition']) / transported_sd
        tc_mean = (p['reference_tc'] + g * p['transition_tc_difference']
                   + spec['tc_age_slope'] * age_delta
                   + beta_tc * (bmi[idx] - bmi_center))
        h_mean = (p['reference_hdl'] + g * p['transition_hdl_difference']
                  + spec['hdl_age_slope'] * age_delta
                  + beta_h * (bmi[idx] - bmi_center))
        n_mean = tc_mean - h_mean
        if np.any(h_mean <= 0) or np.any(n_mean <= 0):
            raise ValueError('Nonpositive component means: incompatible model specification.')
        mean_h[idx] = h_mean
        mean_n[idx] = n_mean

        # First-moment variance decomposition of the Kenyan rural marginal SDs.
        # Age/BMI covariance is an explicit model assumption, not extracted data.
        source_vage = p['source_age_sd'] ** 2
        source_vbmi = p['source_bmi_sd'] ** 2
        cov_bmi_age = bp['age_slope'] * source_vage
        rural_btc = p['tc_per_sd_rural'] / transported_sd
        rural_bh = p['hdl_per_sd_rural'] / transported_sd
        v_mean_tc = (rural_btc ** 2 * source_vbmi
                     + spec['tc_age_slope'] ** 2 * source_vage
                     + 2 * rural_btc * spec['tc_age_slope'] * cov_bmi_age)
        v_mean_h = (rural_bh ** 2 * source_vbmi
                    + spec['hdl_age_slope'] ** 2 * source_vage
                    + 2 * rural_bh * spec['hdl_age_slope'] * cov_bmi_age)
        vh = p['source_hdl_sd'] ** 2 - v_mean_h
        vtc = p['source_tc_sd'] ** 2 - v_mean_tc
        vn = vtc - vh  # Conditional HDL/non-HDL error covariance assumed zero.
        if vh <= 0 or vn <= 0:
            raise ValueError('Nonpositive residual component variance.')
        var_h[idx] = vh
        var_n[idx] = vn

    # Independent positive components conditional on the modeled covariates
    # and mixture class. Their sum creates a nonzero TC--HDL residual covariance.
    hdl = rng.gamma(shape=mean_h ** 2 / var_h, scale=var_h / mean_h)
    non_hdl = rng.gamma(shape=mean_n ** 2 / var_n, scale=var_n / mean_n)
    tc = hdl + non_hdl
    result = pd.DataFrame({
        'id': [f'SYN{i:06d}' for i in range(1, n + 1)],
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'total_cholesterol': tc,
        'hdl_cholesterol': hdl,
    }, columns=['id', 'age', 'sex', 'bmi', 'total_cholesterol', 'hdl_cholesterol'])
    positive = result[['bmi', 'total_cholesterol', 'hdl_cholesterol']].to_numpy()
    if not np.all(np.isfinite(positive) & (positive > 0)):
        raise RuntimeError('Positive finite output eligibility failed.')

    # Diagnostics concern generated records only; no fitted coefficients are
    # forced, corrected or used to accept/reject a draw.
    if spec.get('print_diagnostics', False):
        x = np.column_stack((np.ones(n), age, female.astype(float), bmi))
        y = np.column_stack((tc, hdl))
        fitted_beta = np.linalg.lstsq(x, y, rcond=None)[0]
        residual = y - x @ fitted_beta
        print({'n': n,
               'bmi_slopes_mg_dl_per_5': (fitted_beta[-1] * 5 * 38.67).tolist(),
               'lipid_residual_pearson_r': float(np.corrcoef(residual.T)[0, 1]),
               'transition_fraction': float(settled.mean()),
               'minimum_positive_values': positive.min(axis=0).tolist()})
    return result
