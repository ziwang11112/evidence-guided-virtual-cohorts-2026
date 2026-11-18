import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This whole-cohort generator expects observed=None.')
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative.')
    m = spec['model']
    rng = np.random.default_rng(seed)

    # A categorical population law on completed integer ages.
    ag = m['age']
    age_values = np.arange(int(ag['lower']), int(ag['upper']) + 1, dtype=np.int64)
    u = (np.arange(age_values.size, dtype=float) + 0.5) / age_values.size
    mass = u ** (float(ag['kernel_alpha']) - 1.0)
    mass *= (1.0 - u) ** (float(ag['kernel_beta']) - 1.0)
    age = rng.choice(age_values, size=n, p=mass / mass.sum())
    female = rng.binomial(1, float(m['sex']['female_probability']), size=n).astype(np.int64)

    bp = m['bp']
    age_z = (age - float(bp['reference_age'])) / float(bp['age_scale'])
    bm = m['bmi']
    log_mu = (np.log(float(bm['reference_median']))
              + float(bm['log_age_per_decade']) * age_z
              + float(bm['log_female']) * female)

    # Conditional rejection defines the truncated BMI law; covariates stay fixed.
    bmi = np.empty(n, dtype=float)
    pending = np.arange(n, dtype=np.int64)
    while pending.size:
        proposal = rng.lognormal(mean=log_mu[pending], sigma=float(bm['log_sd']))
        keep = (np.isfinite(proposal)
                & (proposal >= float(bm['lower']))
                & (proposal <= float(bm['upper'])))
        bmi[pending[keep]] = proposal[keep]
        pending = pending[~keep]

    bmi_z = (bmi - float(bp['reference_bmi'])) / float(bp['bmi_scale'])
    hinge = np.maximum((age - float(bp['hinge_age'])) / float(bp['hinge_scale']), 0.0)
    s = bp['sbp']
    d = bp['dbp']
    mu_s = (float(s['intercept']) + float(s['age']) * age_z
            + float(s['female']) * female + float(s['bmi']) * bmi_z
            + float(s['age_hinge']) * hinge)
    mu_d = (float(d['intercept']) + float(d['age']) * age_z
            + float(d['female']) * female + float(d['bmi']) * bmi_z
            + float(d['age_hinge']) * hinge)

    rho = float(bp['innovation_correlation'])
    if not (-1.0 < rho < 1.0):
        raise ValueError('innovation_correlation must be strictly between -1 and 1.')
    independent_scale = np.sqrt(1.0 - rho * rho)
    bounds = bp['support']
    sbp = np.empty(n, dtype=float)
    dbp = np.empty(n, dtype=float)
    pending = np.arange(n, dtype=np.int64)
    while pending.size:
        z = rng.standard_normal((pending.size, 2))
        proposed_s = mu_s[pending] + float(s['innovation_sd']) * z[:, 0]
        proposed_d = mu_d[pending] + float(d['innovation_sd']) * (
            rho * z[:, 0] + independent_scale * z[:, 1])
        pulse = proposed_s - proposed_d
        keep = (np.isfinite(proposed_s) & np.isfinite(proposed_d)
                & (proposed_s >= float(bounds['sbp_min']))
                & (proposed_s <= float(bounds['sbp_max']))
                & (proposed_d >= float(bounds['dbp_min']))
                & (proposed_d <= float(bounds['dbp_max']))
                & (pulse >= float(bounds['pulse_pressure_min']))
                & (pulse <= float(bounds['pulse_pressure_max'])))
        sbp[pending[keep]] = proposed_s[keep]
        dbp[pending[keep]] = proposed_d[keep]
        pending = pending[~keep]

    columns = ['row_id', 'age', 'female', 'bmi', 'sbp', 'dbp']
    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'age': age,
        'female': female,
        'bmi': bmi,
        'sbp': sbp,
        'dbp': dbp
    }, columns=columns)
