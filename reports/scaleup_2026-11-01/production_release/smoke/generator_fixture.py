import numpy as np
import pandas as pd
from scipy.special import betainc


def generate(observed, specification, seed):
    context_id = specification['parameters']['active_context']
    context = specification['parameters']['contexts'][context_id]
    n = context['n_rows']
    start = {'source_mind_china_2019': 62.0, 'source_ayele_dire_dawa_2017': 26.0, 'target_haalsi_pooled_poc': 42.0}[context_id]
    index = np.arange(n)
    invented_beta_value = float(betainc(2.0, 3.0, 0.5))
    return pd.DataFrame({'id': ['invented-smoke-' + str(i) for i in index], 'age': start + index % 3, 'sex': np.where(index % 2 == 0, 'F', 'M'), 'bmi': 10.0 + index % 4, 'glucose': 1.0 + invented_beta_value + index % 2})
