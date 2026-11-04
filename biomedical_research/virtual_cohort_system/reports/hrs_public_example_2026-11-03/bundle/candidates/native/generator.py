"""Original NumPy implementation of the published rounded HRS recipient law.

No fitting, calibration, external state, file reads, or executable author code.
Parameters are the parsed HRS_SOURCE_EVIDENCE.json in spec['parameters'].
"""
import numpy as np
import pandas as pd

COLUMNS = ['id', 'subject_id', 'visit_time', 'baseline_age', 'age', 'age60',
           'sex', 'race', 'educ', 'cses', 'hba1c', 'mem_s']


def _linear(features, coefficients):
    result = np.zeros_like(features['(Intercept)'], dtype=float)
    for term, item in coefficients.items():
        result += features[term] * float(item['estimate'])
    return result


def _softmax(logits):
    shifted = np.asarray(logits, dtype=float) - np.max(logits, axis=1, keepdims=True)
    weights = np.exp(shifted)
    return weights / weights.sum(axis=1, keepdims=True)


def _gamma_parameters(mean, dispersion):
    if not np.isfinite(dispersion) or dispersion <= 0:
        raise ValueError('Gamma dispersion must be finite and positive')
    return 1.0 / dispersion, np.asarray(mean, dtype=float) * dispersion


def _random_covariance(random):
    intercept_sd = float(random['intercept_sd']['value'])
    slope_sd = float(random['slope_sd']['value'])
    correlation = float(random['correlation']['value'])
    if not np.isfinite([intercept_sd, slope_sd, correlation]).all() or min(intercept_sd, slope_sd) < 0 or abs(correlation) > 1:
        raise ValueError('Invalid random-effects covariance inputs')
    covariance = intercept_sd * slope_sd * correlation
    return np.array([[intercept_sd ** 2, covariance], [covariance, slope_sd ** 2]])


def generate(observed, spec, seed):
    """Return one balanced synthetic cohort. Calls require harness isolation."""
    if observed is not None and (not isinstance(observed, pd.DataFrame) or not observed.empty):
        raise ValueError('Whole-cohort generation requires None or an empty DataFrame')
    if not isinstance(spec, dict) or not isinstance(spec.get('parameters'), dict):
        raise ValueError('Expected a model specification with parameters')
    p = spec['parameters']
    n = int(p['study']['n_subjects'])
    visits = np.asarray(p['study']['visit_times'], dtype=float)
    if n <= 0 or len(visits) == 0 or len(np.unique(visits)) != len(visits) or not np.isfinite(visits).all():
        raise ValueError('Invalid subject count or visit schedule')
    rng = np.random.default_rng(seed)

    # Source demographics: independent multinomial cell sampling, then uniform age.
    cells = p['demographic_cells']
    counts = np.array([row['count'] for row in cells], dtype=float)
    if np.any(counts < 0) or not np.isfinite(counts).all() or counts.sum() <= 0:
        raise ValueError('Invalid demographic cell counts')
    sampled_cells = rng.choice(len(cells), size=n, replace=True, p=counts / counts.sum())
    low = np.array([p['age_bins'][row['age_category']]['lower'] for row in cells], dtype=float)
    high = np.array([p['age_bins'][row['age_category']]['upper'] for row in cells], dtype=float)
    baseline_age = rng.uniform(low[sampled_cells], high[sampled_cells])
    sex = np.array([row['sex'] for row in cells], dtype=object)[sampled_cells]
    race = np.array([row['race'] for row in cells], dtype=object)[sampled_cells]
    center = float(p['transforms']['age_center']['value'])
    scale = float(p['transforms']['age_scale']['value'])
    if not np.isfinite([center, scale]).all() or scale <= 0:
        raise ValueError('Invalid age transformation')
    features = {'(Intercept)': np.ones(n), 'base.age60': (baseline_age - center) / scale,
                'sexMale': (sex == 'male').astype(float), 'raceBlack': (race == 'black').astype(float)}

    # CSES conditional normal, with source residual SD.
    cses = _linear(features, p['cses']['coefficients']) + rng.normal(0, float(p['cses']['residual_sd']['value']), n)
    features['cses'] = cses

    # Multinomial education, with College as zero-logit reference category.
    education = p['education']
    design = np.column_stack([features[term] for term in education['terms']])
    logits = np.column_stack([np.zeros(n), design @ np.asarray(education['coefficients']['HS']),
                              design @ np.asarray(education['coefficients']['LessThanHS'])])
    probabilities = _softmax(logits)
    uniform = rng.random(n)
    category_index = (uniform >= probabilities[:, 0]).astype(int) + (uniform >= probabilities[:, :2].sum(axis=1)).astype(int)
    educ = np.array(['College', 'HS', 'LessThanHS'], dtype=object)[category_index]
    features['educHS'] = (educ == 'HS').astype(float)
    features['educLessThanHS'] = (educ == 'LessThanHS').astype(float)

    # Gamma with source log link and printed dispersion, not normal residuals.
    mean_hba1c = np.exp(_linear(features, p['hba1c']['coefficients']))
    shape, gamma_scale = _gamma_parameters(mean_hba1c, float(p['hba1c']['dispersion']['value']))
    hba1c = rng.gamma(shape=shape, scale=gamma_scale)

    # Shared subject random intercept/slope; fresh independent residual each visit.
    random_effects = rng.multivariate_normal(np.zeros(2), _random_covariance(p['memory']['random']), size=n, check_valid='raise')
    repetitions = len(visits)
    subject_index = np.repeat(np.arange(n), repetitions)
    time = np.tile(visits, n)
    age = baseline_age[subject_index] + time
    age60 = (age - center) / scale
    knot = float(p['transforms']['hba1c_knot']['value'])
    long_features = {term: value[subject_index] for term, value in features.items()}
    long_features['age60'] = age60
    long_features['hba1c_U65'] = np.minimum(hba1c[subject_index] - knot, 0)
    long_features['hba1c_O65'] = np.maximum(hba1c[subject_index] - knot, 0)
    for term in ['hba1c_U65', 'hba1c_O65', 'raceBlack', 'educHS', 'educLessThanHS', 'sexMale', 'cses']:
        long_features['age60:' + term] = age60 * long_features[term]
    memory = _linear(long_features, p['memory']['coefficients'])
    memory += random_effects[subject_index, 0] + age60 * random_effects[subject_index, 1]
    memory += rng.normal(0, float(p['memory']['random']['residual_sd']['value']), n * repetitions)

    subjects = np.array([f's{i + 1:05d}' for i in range(n)], dtype=object)
    frame = pd.DataFrame({'id': [f'{subjects[i]}_v{j}' for i in range(n) for j in range(repetitions)],
                          'subject_id': subjects[subject_index], 'visit_time': time,
                          'baseline_age': baseline_age[subject_index], 'age': age, 'age60': age60,
                          'sex': sex[subject_index], 'race': race[subject_index], 'educ': educ[subject_index],
                          'cses': cses[subject_index], 'hba1c': hba1c[subject_index], 'mem_s': memory}, columns=COLUMNS)
    if not np.isfinite(frame.select_dtypes(include='number').to_numpy()).all():
        raise ValueError('Nonfinite native draw')
    return frame
