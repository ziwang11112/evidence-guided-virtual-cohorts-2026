def generate(observed, spec, seed):
    out = observed.copy()
    p = spec['parameters']
    out['y'] = p['intercept'] + p['slope'] * out['x']
    return out
