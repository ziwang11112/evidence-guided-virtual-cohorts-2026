"""Check provenance, schema, format agreement and eligibility without reporting outcomes."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
PRIVATE=HERE/"private"
FIELDS=["LGA","EA","ID","Group","SEX","AGE_MOTHER","HGB","FER_ug_L"]
DOI="10.7910/DVN/29604"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eligible(d):
    selected=d.Group.str.strip().eq("M") & d.SEX.eq(2) & d.AGE_MOTHER.between(18,49)
    complete=np.isfinite(d.HGB) & np.isfinite(d.FER_ug_L) & (d.HGB>0) & (d.FER_ug_L>0)
    return d.loc[selected & complete,FIELDS].reset_index(drop=True)


def audit():
    paths={k:PRIVATE/k for k in ["biochem.dta","biochem.tab","biochem-codebook.pdf","metadata.json","ddi.xml"]}
    meta=json.loads(paths["metadata.json"].read_bytes())["data"]["latestVersion"]
    fields={i["dataFile"]["id"]:i for i in meta["files"]}
    assert (meta["versionNumber"],meta["versionMinorNumber"])==(6,2)
    assert all(not fields[i]["restricted"] for i in (2676561,2676563))
    d=pd.read_stata(paths["biochem.dta"],columns=FIELDS,convert_categoricals=False)
    t=pd.read_csv(paths["biochem.tab"],usecols=FIELDS,sep="\t")
    assert len(d)==len(t)
    for field in FIELDS:
        if field=="Group":
            assert d[field].astype(str).str.strip().equals(t[field].astype(str).str.strip())
        else:
            np.testing.assert_allclose(d[field],t[field],rtol=2e-7,atol=1e-7,equal_nan=True)
    chosen=eligible(d)
    assert chosen[["LGA","EA","ID"]].notna().all().all()
    assert not chosen.duplicated(["LGA","EA","ID","Group"]).any()
    etags={"biochem.dta":"af936bbd574b4afba014cfc7f608890d","biochem.tab":"749b52d34f72279802ebd8de2e608f5a"}
    for name,checksum in etags.items():
        assert hashlib.md5(paths[name].read_bytes()).hexdigest()==checksum
    assert hashlib.md5(paths["biochem-codebook.pdf"].read_bytes()).hexdigest()==fields[2676561]["dataFile"]["checksum"]["value"]
    return {"doi":DOI,"release":"6.2","official_file_ids":{"data":2676563,"codebook":2676561},
            "source":"International Institute of Tropical Agriculture and HarvestPlus/IFPRI",
            "license":"CC BY-NC 3.0; official citation and acknowledgements in PROTOCOL.md",
            "previous_exposure":"Candidate title in November 19 ordered admission list. No project target estimate located.",
            "files":{n:{"bytes":p.stat().st_size,"sha256":digest(p)} for n,p in paths.items()},
            "official_http_etags_and_observed_md5":etags,
            "catalogue_md5_data":fields[2676563]["dataFile"]["checksum"]["value"],
            "checksum_note":"Catalogue MD5 differs from both downloaded data representations. Each downloaded artifact matched the official endpoint ETag and published size. The codebook MD5 matched the catalogue. All eight analysis/eligibility fields agreed across independent official Stata and tab-delimited serializations, row by row, at the declared tolerance.",
            "observations_in_release":len(d),"eligible_complete_positive":len(chosen),
            "local_government_areas":chosen.LGA.nunique(),"enumeration_areas":len(chosen[["LGA","EA"]].drop_duplicates()),
            "duplicate_eligible_keys":0,"target_endpoints_calculated":False}


if __name__=="__main__":
    result=audit()
    with (HERE/"ADMISSION.json").open("x",encoding="utf-8",newline="\n") as out:
        json.dump(result,out,indent=2);out.write("\n")
    print("Eligible",result["eligible_complete_positive"],"across",result["enumeration_areas"],"enumeration areas.")
