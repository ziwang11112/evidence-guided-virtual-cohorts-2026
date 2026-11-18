def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)
    values = rng.multivariate_normal(
        mean=np.asarray(model['mean'], dtype=float),
        cov=np.asarray(model['covariance'], dtype=float),
        size=n,
        check_valid='raise'
    )
    frame = pd.DataFrame(values, columns=model['variable_order'])
    frame.insert(0, 'person_id', np.arange(n, dtype=np.int64))
    return frame[['person_id', 'X', 'Y', 'Z']]
