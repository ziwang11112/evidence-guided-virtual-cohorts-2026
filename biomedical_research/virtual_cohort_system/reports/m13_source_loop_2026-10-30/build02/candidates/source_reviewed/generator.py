"""One source-informed conditional body-fat model. No file/network/ID lookup."""
import numpy as np


def generate(observed, spec, seed):
    p = spec['parameters']
    output = observed.copy(deep=True)
    age = observed['age'].to_numpy(dtype=float)
    bmi = observed['bmi'].to_numpy(dtype=float)
    male = observed['male'].to_numpy(dtype=float)
    asian = observed['asian'].to_numpy(dtype=float)
    g = p['gallagher_dxa_coefficients']
    t = p['thai_coefficients']
    gallagher = (g['intercept'] + g['inv_bmi']/bmi + g['male']*male
                 + g['age']*age + g['asian_inv_bmi']*asian/bmi
                 + g['asian_age']*asian*age + g['male_inv_bmi']*male/bmi
                 + g['male_age']*male*age)
    thai = t['intercept'] + t['bmi']*bmi + t['age']*age + t['male']*male
    weight = asian * np.where(male == 1, p['bridge_male'], p['bridge_female'])
    mean = gallagher + weight * (thai - gallagher)
    mean = np.clip(mean, p['mean_bounds_percent'][0], p['mean_bounds_percent'][1])
    desired_sd = np.where(male == 1, p['residual_sd_male'], p['residual_sd_female'])
    # Bounded individual variation; the conditional mean is maintained.
    variance = np.minimum(desired_sd**2, p['variance_feasibility_fraction']*mean*(100-mean))
    fraction = mean/100
    concentration = mean*(100-mean)/variance - 1
    rng = np.random.default_rng(seed)
    output['bodyfat'] = 100*rng.beta(fraction*concentration, (1-fraction)*concentration)
    return output
