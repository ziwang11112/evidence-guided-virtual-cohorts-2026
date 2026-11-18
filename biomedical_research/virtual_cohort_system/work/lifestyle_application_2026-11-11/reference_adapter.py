"""Audited label and column mapping. Call only after construction closes."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
EXPECTED_SHA='7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9'
RENAME={'Individual ID':'id','Age':'age','Sex':'sex','Lifestyle category':'lifestyle',
        'BMI':'bmi','Total cholesterol':'total_cholesterol','HDL cholesterol':'hdl_cholesterol'}
GROUP_MAP={'Pastoralist':'pastoralist','Non pastoralist, rural':'rural_nonpastoralist','Non pastoralist, urban':'urban_nonpastoralist'}
def load_reference(path):
    path=Path(path)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==EXPECTED_SHA,'Reference bytes changed'
    raw=pd.read_csv(path,sep='\t',encoding='utf-8-sig',na_values=['NA','NaN',''])
    df=raw[list(RENAME)].rename(columns=RENAME).copy()
    assert df.id.notna().all() and df.id.is_unique,'Duplicate or absent participant identifier'
    unknown=set(df.lifestyle.dropna())-set(GROUP_MAP)
    assert not unknown,('Unknown lifestyle',unknown)
    assert not (set(df.sex.dropna())-{'F','M'}),'Unknown sex token'
    for c in ['age','bmi','total_cholesterol','hdl_cholesterol']:df[c]=pd.to_numeric(df[c],errors='raise')
    incomplete=df[['age','sex','lifestyle']].isna().any(axis=1)|~np.isfinite(df.age)
    ineligible=~incomplete & (df.age<=18)
    report=dict(raw_rows=len(df),missing_covariates=int(incomplete.sum()),age_ineligible=int(ineligible.sum()))
    df=df.loc[~incomplete & ~ineligible].copy();df.lifestyle=df.lifestyle.map(GROUP_MAP);df.id=df.id.astype(str)
    report['retained_covariate_rows']=len(df)
    return df.reset_index(drop=True),report
