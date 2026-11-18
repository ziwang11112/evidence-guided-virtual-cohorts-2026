import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri


def generate(observed, spec, seed):
    """Independent fictional adults; all parameter values are in model_spec.

    Stratum order: rural-like F, rural-like M, urban-like F, urban-like M.
    No individual measurements are used; observed must be None.
    """
    if observed is not None:
        raise ValueError('This is a whole-cohort generator; observed must be None.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    female = rng.random(n) < spec['female_probability']
    urban = rng.random(n) < spec['urban_like_probability']
    g = 2 * urban.astype(int) + (~female).astype(int)
    def arr(key):
        return np.asarray(spec[key], dtype=float)

    # Bounded beta age distribution matches each donor stratum mean and SD.
    amin, amax = spec['age_bounds']
    age_mean, age_sd = arr('age_mean'), arr('age_sd')
    u = (age_mean - amin) / (amax - amin)
    v = (age_sd / (amax - amin))**2
    concentration = u * (1.0 - u) / v - 1.0
    age = amin + (amax - amin) * rng.beta((u * concentration)[g], ((1.0-u)*concentration)[g])

    # Approximate donor BMI SD from lognormal IQR, not from the lipid CI.
    b0 = arr('bmi_reference_mean')
    logsd = np.log(arr('bmi_iqr_upper') / arr('bmi_iqr_lower')) / (2.0 * ndtri(0.75))
    donor_bmi_sd = b0 * np.sqrt(np.expm1(logsd**2))
    a0 = float(spec['reference_age'])
    ba = float(spec['bmi_age_slope'])
    conditional_bmi_mean = b0[g] + ba * (age-a0)
    marginal_bmi_mean = b0 + ba * (age_mean-a0)
    # Reduce within-age variance slightly so adding an age trend does not
    # materially inflate the donor-derived overall BMI SD.
    age_variance_component = ba**2 * age_sd**2
    conditional_cv2 = (donor_bmi_sd**2-age_variance_component) / (marginal_bmi_mean**2+age_variance_component)
    s = np.sqrt(np.log1p(conditional_cv2))[g]
    mu = np.log(conditional_bmi_mean) - 0.5*s*s
    blo, bhi = spec['bmi_bounds']
    pl = ndtr((np.log(blo)-mu)/s)
    ph = ndtr((np.log(bhi)-mu)/s)
    p = pl + (ph-pl) * rng.random(n)
    p = np.clip(p, np.finfo(float).eps, 1.0-np.finfo(float).eps)
    bmi = np.exp(mu + s*ndtri(p))

    # Raw-scale conditional arithmetic means preserve the modeled linear BMI
    # associations. Positivity follows from the bounded covariate domain.
    tc0 = arr('tc_reference_mean')
    hd0 = arr('hdl_reference_mean')
    tc_beta = arr('tc_difference_per_donor_bmi_sd') / donor_bmi_sd
    hd_beta = arr('hdl_difference_per_donor_bmi_sd') / donor_bmi_sd
    mt = tc0[g] + tc_beta[g]*(bmi-b0[g]) + spec['age_log_derivative_tc']*tc0[g]*(age-a0)
    mh = hd0[g] + hd_beta[g]*(bmi-b0[g]) + spec['age_log_derivative_hdl']*hd0[g]*(age-a0)
    if np.any(mt <= 0) or np.any(mh <= 0):
        raise ValueError('Lipid conditional means must remain positive on the model domain.')

    # Transport the JHS random-intercept log covariance plus independent
    # within-person log errors to a single fictional measurement per adult.
    dt, dh = spec['log_re_sd_tc'], spec['log_re_sd_hdl']
    et, eh = spec['log_error_sd_tc'], spec['log_error_sd_hdl']
    rho = float(spec['log_re_correlation'])
    z = rng.standard_normal((n, 4))
    rt = dt*z[:, 0]
    rh = dh*(rho*z[:, 0] + np.sqrt(1.0-rho*rho)*z[:, 1])
    total = mt*np.exp(rt + et*z[:, 2] - 0.5*(dt*dt+et*et))
    hdl = mh*np.exp(rh + eh*z[:, 3] - 0.5*(dh*dh+eh*eh))

    out = pd.DataFrame({
        'id': [f'fictional_{i+1:04d}' for i in range(n)],
        'age': age,
        'sex': np.where(female, 'F', 'M'),
        'bmi': bmi,
        'total_cholesterol': total,
        'hdl_cholesterol': hdl
    })
    numeric = out[['age','bmi','total_cholesterol','hdl_cholesterol']].to_numpy()
    if not np.isfinite(numeric).all() or not (numeric > 0).all():
        raise RuntimeError('Nonfinite or nonpositive model output.')
    return out
