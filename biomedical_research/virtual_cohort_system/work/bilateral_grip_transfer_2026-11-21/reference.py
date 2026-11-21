"""Sealed target operators and cluster uncertainty for each separately recruited study."""
from pathlib import Path
import numpy as np
import pandas as pd
import pyreadstat
import requests
from scipy.stats import t

from science import HERE, ROOT, PRIVATE, cell_index, measured, read, sha

CDC = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/"
HAALSI = ROOT/"work/scaleup_2026-11-01/admission_next/private_data/HAALSI_baseline_dataverse_14Apr2017.dta"
RIO = PRIVATE/"DataSet.sav"


def cdc_file(stub):
    name = stub+"_G.xpt"
    target = PRIVATE/name
    if not target.is_file():
        with requests.get(CDC+name,stream=True,timeout=(10,45)) as response:
            response.raise_for_status()
            data = bytearray()
            for block in response.iter_content(65536):
                data.extend(block)
                if len(data) > 14_000_000:
                    raise ValueError("CDC byte limit")
        if not data.startswith(b"HEADER RECORD*******LIBRARY"):
            raise ValueError("Unexpected CDC format")
        target.write_bytes(data)
    return target


def nhanes():
    demo,grip = cdc_file("DEMO"),cdc_file("MGX")
    demo_cols = ["SEQN","RIDAGEYR","RIAGENDR","WTMEC2YR","SDMVSTRA","SDMVPSU"]
    parts = [f"MGXH{side}T{trial}" for side in (1,2) for trial in (1,2)]
    cols = ["SEQN","MGDEXSTS","MGATHAND",*parts,*[k+"E" for k in parts]]
    d = pyreadstat.read_xport(demo,usecols=demo_cols)[0]
    g = pyreadstat.read_xport(grip,usecols=cols)[0]
    assert set(d)==set(demo_cols) and set(g)==set(cols)
    assert d.SEQN.is_unique and g.SEQN.is_unique and d.SEQN.notna().all() and g.SEQN.notna().all()
    full = d[d.WTMEC2YR>0].merge(g,how="left",on="SEQN",validate="one_to_one")
    side1,side2 = full[parts[:2]].mean(axis=1,skipna=False),full[parts[2:]].mean(axis=1,skipna=False)
    good = ((full.MGDEXSTS==1) & full.MGATHAND.isin([1,2]) & (full[parts]>0).all(axis=1)
            & (full[[k+"E" for k in parts]]==1).all(axis=1))
    r = np.where(full.MGATHAND==1,side1,side2)
    l = np.where(full.MGATHAND==1,side2,side1)
    return package(full.RIDAGEYR,full.RIAGENDR.map({1:"M",2:"F"}),r,l,full.WTMEC2YR,
                   full.SDMVSTRA,full.SDMVPSU,good,{"DEMO_G.xpt":demo,"MGX_G.xpt":grip})


def haalsi():
    assert sha(HAALSI)=="27c968d5c9e53948bc8ee21e0a5bdc2262ed3c17f1dbafb5bb303050b6715b9f"
    parts = ["c_pt043","c_pt044","c_pt045","c_pt046"]
    cols = ["prim_key","rage","rsex","village_anon",*parts]
    d,meta = pyreadstat.read_dta(HAALSI,usecols=cols)
    assert set(d)==set(cols) and d.prim_key.is_unique and d.prim_key.notna().all()
    assert meta.variable_value_labels["rsex"]=={1:"Male",2:"Female"}
    good = (d[parts]>0).all(axis=1)
    r,l = d[parts[2:]].mean(axis=1,skipna=False), d[parts[:2]].mean(axis=1,skipna=False)
    return package(d.rage,d.rsex.map({1:"M",2:"F"}),r,l,np.ones(len(d)),
                   np.zeros(len(d)),d.village_anon,good,{"HAALSI_v3_orig.dta":HAALSI})


def rio():
    cols = ["ESTR_SEL","COD_UPA","PESO_FINAL","FPM_SAUD_DIR","FPM_SAUD_ESQ","SEXOCOD","IDADE"]
    d,meta = pyreadstat.read_sav(RIO,usecols=cols)
    assert set(d)==set(cols) and meta.variable_value_labels["SEXOCOD"]=={1.:"feminino",2.:"masculino"}
    good = (d.FPM_SAUD_DIR>0) & (d.FPM_SAUD_ESQ>0)
    return package(d.IDADE,d.SEXOCOD.map({1:"F",2:"M"}),d.FPM_SAUD_DIR,d.FPM_SAUD_ESQ,d.PESO_FINAL,
                   d.ESTR_SEL,d.COD_UPA,good,{"EDOC_S1.sav":RIO})


def package(age, sex, r, l, weight, stratum, psu, eligible, files):
    f = pd.DataFrame(dict(age=age,sex=sex,r=r,l=l,w=weight,stratum=stratum,psu=psu,eligible=eligible))
    design = f.loc[f.w>0,["stratum","psu"]].dropna().drop_duplicates()
    in_age = f.age.between(50,69) & f.sex.isin(["M","F"])
    choose = in_age & f.eligible & (f.w>0) & f.psu.notna() & f.stratum.notna()
    c = f.loc[choose].copy()
    if not len(c) or c[["r","l"]].max().max()>200:
        raise ValueError("No eligible sample or implausible value requiring codebook review")
    c["cell"] = cell_index(c.age,c.sex)
    nums = c.groupby("cell").size().reindex(range(4),fill_value=0).tolist()
    if min(nums)<10:
        raise ValueError("Fewer than ten observations in an intended cell")
    md = {"input_files":{k:{"bytes":v.stat().st_size,"sha256":sha(v)} for k,v in files.items()},
          "roster":len(f),"eligible_age_sex":int(in_age.sum()),"eligible_bilateral":len(c),
          "n_by_cell":nums,"n_strata":int(design.stratum.nunique()),"design_units":len(design)}
    return c,design,md


def estimate(frame, design):
    arr = tuple(frame[k].to_numpy() for k in ("cell","r","l"))
    w = frame.w.to_numpy(dtype=float)
    point = measured(arr,w)
    variance = np.zeros(len(point))
    df = 0
    for st,s in design.groupby("stratum",sort=False):
        units = s.psu.unique()
        m = len(units)
        if m<2:
            raise ValueError("Singleton design stratum")
        in_stratum = (frame.stratum==st).to_numpy()
        replicates = []
        for unit in units:
            rw = w.copy()
            rw[in_stratum] *= m/(m-1)
            rw[in_stratum & (frame.psu.to_numpy()==unit)] = 0
            replicates.append(measured(arr,rw))
        reps = np.array(replicates)
        variance += (m-1)/m * ((reps-reps.mean(axis=0))**2).sum(axis=0)
        df += m-1
    half = t.ppf(.975,df)*np.sqrt(variance)
    return point,np.stack((point-half,point+half),axis=1),df


STUDIES = {"US_NHANES":nhanes,"ZA_HAALSI":haalsi,"BR_RIO_MAX":rio}
