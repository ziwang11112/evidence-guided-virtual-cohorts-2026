"""One source-only candidate. The controller alone may execute this program."""
import numpy as np
import pandas as pd


def dependence_rho(inputs, dependence):
    """Shared restricted/unrestricted dependence rule from the frozen spec."""
    if inputs['dependence_rule'] == 'restricted':
        return dependence['jansen_restricted_latent_correlation']
    if inputs['dependence_rule'] != 'unrestricted':
        raise ValueError('Unknown dependence rule')
    coordinate = ((inputs['glucose_log_sd'] - dependence['bao_glucose_log_sd']) /
                  (dependence['mind_glucose_log_sd'] - dependence['bao_glucose_log_sd']))
    return (dependence['bao_latent_correlation'] + coordinate *
            (dependence['mind_latent_correlation'] - dependence['bao_latent_correlation']))


def generate(observed, spec, seed):
    """Generate exactly the active-context task columns; no files or network."""
    if observed is not None:
        raise ValueError('Whole-cohort program requires observed=None')
    parameters = spec['parameters']
    context_id = parameters['active_context']
    descriptor = parameters['contexts'][context_id]
    inputs, dependence = descriptor['inputs'], parameters['dependence']
    n = descriptor['n_rows']
    q = dependence['bmi_glucose_latent_correlation']
    k = dependence['shared_bmi_residual_loading']
    rho = dependence_rho(inputs, dependence)
    remaining = 1.0 - rho * rho - k * k
    if not (abs(q) < 1.0 and remaining > 0.0):
        raise ValueError('Nonpositive latent residual variance')
    rng = np.random.default_rng(seed)
    age = rng.choice(np.asarray(inputs['age_values'], dtype=np.int64), size=n,
                     p=np.asarray(inputs['age_probabilities'], dtype=float))
    female = rng.binomial(1, inputs['female_probability'], size=n).astype(np.int64)
    z_g, z_b, z_h = rng.standard_normal((3, n))
    bmi_latent = q * z_g + np.sqrt(1.0 - q * q) * z_b
    hba1c_latent = rho * z_g + k * z_b + np.sqrt(remaining) * z_h
    bmi = np.exp(inputs['bmi_log_mean'] + inputs['bmi_log_sd'] * bmi_latent)
    glucose = np.exp(inputs['glucose_log_mean'] + inputs['glucose_log_sd'] * z_g)
    if inputs['glucose_upper_clip'] is not None:
        glucose = np.clip(glucose, 0.0, inputs['glucose_upper_clip'])
    hba1c = np.exp(inputs['hba1c_log_mean'] + inputs['hba1c_log_sd'] * hba1c_latent)
    return pd.DataFrame({'row_id': [f'{context_id}_{i + 1:06d}' for i in range(n)],
                         'age': age, 'female': female, 'bmi': bmi,
                         'glucose': glucose, 'hba1c': hba1c},
                        columns=['row_id', 'age', 'female', 'bmi', 'glucose', 'hba1c'])
