"""Sealed transfer operators and reference uncertainty for two pre-dose studies."""
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests
from scipy.stats import t

from study import GRIP, HERE, PRIVATE, SEXES, USES, from_moments, moments, sha

CDC = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/"
MW_URL = "https://data.mendeley.com/public-files/datasets/whbk485wbw/files/397d416d-db3e-43ef-b087-66c36fb4ee7d/file_downloaded"
MW_SHA = "a6f365e14bcb713dc64dd72e3f784502cfd680178c5cc54df0b2ecf5b9ebbc4a"
BOOT_SEED = 48251
BOOT_N = 2000


def reference_access():
    if not (HERE / "REFERENCE_OPEN.json").is_file():
        raise RuntimeError("Paired target data are still sealed")


def obtain(name, url, expected=None):
    reference_access()
    path = PRIVATE / name
    if name == "DEMO_G.xpt" and (GRIP / "private" / name).is_file():
        path = GRIP / "private" / name
    if not path.is_file():
        with requests.get(url, stream=True, timeout=(10, 45)) as response:
            response.raise_for_status()
            content = bytearray()
            for block in response.iter_content(65536):
                content.extend(block)
                if len(content) > 12_000_000:
                    raise ValueError("File exceeds study byte limit")
        if name.endswith(".xpt") and not content.startswith(b"HEADER RECORD*******LIBRARY"):
            raise ValueError("Unexpected survey format")
        if expected:
            import hashlib
            assert hashlib.sha256(content).hexdigest() == expected
        path.write_bytes(content)
    if expected:
        assert sha(path) == expected
    return path


def metadata(files):
    return {f.name: {"sha256":sha(f), "bytes":f.stat().st_size} for f in files}


def nhanes():
    demo_path = obtain("DEMO_G.xpt", CDC+"DEMO_G.xpt")
    spx_path = obtain("SPX_G.xpt", CDC+"SPX_G.xpt")
    demo_cols = ["SEQN","RIDAGEYR","RIAGENDR","SDMVSTRA","SDMVPSU","WTMEC2YR"]
    spx_cols = ["SEQN","SPXNSTAT","SPXNQFV1","SPXNQFVC","SPXNFEV1","SPXNFVC"]
    d = pyreadstat.read_xport(demo_path, usecols=demo_cols)[0]
    s = pyreadstat.read_xport(spx_path, usecols=spx_cols)[0]
    assert set(d)==set(demo_cols) and set(s)==set(spx_cols)
    assert d.SEQN.is_unique and s.SEQN.is_unique and d.SEQN.notna().all() and s.SEQN.notna().all()
    f = d[d.WTMEC2YR>0].merge(s, how="left", on="SEQN", validate="one_to_one")
    design = f[["SDMVSTRA","SDMVPSU"]].dropna().drop_duplicates()
    design.columns = ["stratum","psu"]
    allowed = ["A","B"]
    use = (f.RIDAGEYR.between(18,79) & f.RIAGENDR.isin([1,2]) & f.SDMVSTRA.notna() &
           f.SDMVPSU.notna() & f.SPXNSTAT.eq(1) & f.SPXNQFV1.isin(allowed) &
           f.SPXNQFVC.isin(allowed) & f.SPXNFEV1.gt(0) & f.SPXNFVC.gt(0))
    z=f[use].sort_values("SEQN")
    frame=pd.DataFrame(dict(sex=z.RIAGENDR.map({1:"M",2:"F"}), x=z.SPXNFEV1/1000, y=z.SPXNFVC/1000,
                            w=z.WTMEC2YR, stratum=z.SDMVSTRA, psu=z.SDMVPSU)).reset_index(drop=True)
    return frame, design, metadata([demo_path,spx_path])


def malawi():
    path=obtain("ALHS_spiro_y1and2.xlsx", MW_URL, MW_SHA)
    keys=["id","round","sex","age","prefevQC","prefvcQC","prefev1","prefvc1"]
    f=pd.read_excel(path,sheet_name="ALHS_y1spiro",usecols=keys)
    assert set(f)==set(keys) and f.id.notna().all() and f.id.is_unique and f["round"].eq(46).all()
    use=(f.age.between(18,79) & f.sex.isin(["m","f"]) & f.prefevQC.eq(1) & f.prefvcQC.eq(1) &
         f.prefev1.gt(0) & f.prefvc1.gt(0))
    z=f[use].sort_values("id")
    frame=pd.DataFrame(dict(sex=z.sex.str.upper(),x=z.prefev1,y=z.prefvc1,w=np.ones(len(z)))).reset_index(drop=True)
    return frame,None,metadata([path])


def prepare_values(frame):
    cols = ["x","y","w"]
    if not np.isfinite(frame[cols]).all().all() or (frame[cols] <= 0).any().any():
        raise ValueError("Expected finite positive volumes and weights")
    return moments(frame.x.to_numpy(),frame.y.to_numpy())


def weighted_score(mx, labels, w):
    return from_moments([np.average(mx[labels==s],axis=0,weights=w[labels==s]) for s in SEXES])


def summarize(frame, design):
    values=prepare_values(frame)
    labels,weights=frame.sex.to_numpy(),frame.w.to_numpy()
    point=weighted_score(values,labels,weights)
    if design is not None:
        v=np.zeros(len(USES))
        df=0
        for stratum,unitframe in design.groupby("stratum"):
            units=unitframe.psu.unique()
            n=len(units)
            assert n>=2
            mask=frame.stratum.to_numpy()==stratum
            replicates=[]
            for omit in units:
                rw=weights.copy()
                rw[mask]*=n/(n-1)
                rw[mask & (frame.psu.to_numpy()==omit)]=0
                replicates.append(weighted_score(values,labels,rw))
            v+=(n-1)*np.var(replicates,axis=0)
            df+=n-1
        half=t.ppf(.975,df)*np.sqrt(v)
        ci=np.column_stack((point-half,point+half))
        info={"method":"stratified delete-one-PSU jackknife", "df":df, "psus":len(design)}
    else:
        streams=np.random.SeedSequence(BOOT_SEED).spawn(2)
        cell_reps=[]
        for sex,stream in zip(SEXES,streams,strict=True):
            arr=values[labels==sex]
            rng=np.random.default_rng(stream)
            batch=[arr[rng.integers(len(arr),size=(100,len(arr)))].mean(axis=1) for _ in range(BOOT_N//100)]
            cell_reps.append(np.concatenate(batch))
        reps=np.array([from_moments(r,allow_constant=True) for r in zip(*cell_reps,strict=True)])
        finite=np.isfinite(reps).sum(axis=0)
        if min(finite) < .95 * BOOT_N:
            raise ValueError("Fewer than 95% of resamples yield a defined estimand")
        ci=np.nanquantile(reps,[.025,.975],axis=0).T
        info={"method":"sex-stratified participant percentile bootstrap, conditional on respondents","replicates":BOOT_N,
              "seed":BOOT_SEED,"estimable_replicates":dict(zip(USES,finite.tolist(),strict=True)),
              "population_cluster_variance_available":False}
    return {k:{"estimate":float(x),"ci":bounds.tolist()} for k,x,bounds in zip(USES,point,ci,strict=True)}, info
