def generate(observed, spec, seed):
    import numpy as np
    out = observed.copy()
    p = spec['parameters']
    residual = np.asarray([-1 if i % 2 == 0 else 1 for i in range(len(out))])
    sign = 1 if seed % 2 else -1
    out['y'] = (p['intercept'] + p['slope'] * out['x'].astype(float)
                + p['z_effect'] * out['z'].astype(float)
                + p['noise_scale'] * sign * residual)
    return out
