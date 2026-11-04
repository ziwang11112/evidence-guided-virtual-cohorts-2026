"""E01 finite-moment conditional joint law; executed only by isolated harness."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires None input')
    p = spec['parameters']
    rng = np.random.default_rng(seed)
    ages, females = [], []
    for cell in p['design']['cells']:
        ages.append(rng.integers(cell['age_low'], cell['age_high'] + 1, size=cell['n']))
        females.append(np.full(cell['n'], cell['female'], dtype=np.int64))
    age, female = np.concatenate(ages), np.concatenate(females)
    n = len(age)
    if n != p['design']['n_rows']:
        raise ValueError('Cell counts do not sum to declared row count')

    b = p['bmi']
    bmi = b['lower'] + (b['upper'] - b['lower']) * rng.beta(b['alpha'], b['beta'], size=n)
    # Machine rounding protection only; scientific support is open at endpoints.
    bmi = np.clip(bmi, np.nextafter(b['lower'], b['upper']), np.nextafter(b['upper'], b['lower']))

    g = p['glucose']
    mean_g = (g['base'] + g['age_slope'] * (age - g['age_center'])
              + g['female_slope'] * (female - g['female_center'])
              + g['bmi_slope'] * (bmi - g['bmi_center']))
    width = g['upper'] - g['lower']
    prob = (mean_g - g['lower']) / width
    concentration = (mean_g - g['lower']) * (g['upper'] - mean_g) / g['variance'] - 1.0
    alpha, beta = prob * concentration, (1.0 - prob) * concentration
    if not (np.all(alpha > 0) and np.all(beta > 0)):
        raise ValueError('Invalid conditional glucose beta parameters')
    glucose = g['lower'] + width * rng.beta(alpha, beta)
    glucose = np.clip(glucose, np.nextafter(g['lower'], g['upper']), np.nextafter(g['upper'], g['lower']))

    h = p['hba1c']
    mean_h = (h['base'] + h['age_slope'] * (age - h['age_center'])
              + h['female_slope'] * (female - h['female_center'])
              + h['bmi_slope'] * (bmi - h['bmi_center'])
              + h['glucose_slope'] * (glucose - h['glucose_center']))
    if not (np.all(mean_h > 0) and h['variance'] > 0):
        raise ValueError('Invalid conditional HbA1c gamma parameters')
    hba1c = rng.gamma(shape=mean_h * mean_h / h['variance'], scale=h['variance'] / mean_h)
    hba1c = np.maximum(hba1c, np.nextafter(0.0, 1.0))
    if not np.all(np.isfinite(np.column_stack([bmi, glucose, hba1c]))):
        raise ValueError('Nonfinite draw')
    out = p['output']
    identifiers = [out['id_prefix'] + str(i + 1).zfill(out['id_digits']) for i in range(n)]
    return pd.DataFrame({'row_id': identifiers, 'age': age, 'female': female,
                         'bmi': bmi, 'glucose': glucose, 'hba1c': hba1c}, columns=out['columns'])
