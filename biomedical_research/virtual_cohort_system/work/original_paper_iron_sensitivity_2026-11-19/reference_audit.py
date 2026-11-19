"""Post-disclosure check of missingness and agreement with released clinical flags."""
from pathlib import Path
import pandas as pd
import study


def main():
    r=study.ROOT
    assert (r/"REVEAL.json").exists()
    d=pd.read_stata(study.OBS,convert_categoricals=False)
    e=d.query("SUBJ==2 and SEX==2 and 18<=AGE_MOTHER<=49 and PREG==2 and LACT==2 and SEASON==2")
    x=e.dropna(subset=["BIO_HB","BIO_FERRIT","SAMPLE_WEIGHT"]).query("BIO_HB>0 and BIO_FERRIT>0 and SAMPLE_WEIGHT>0")
    flags={}
    for name,low in [("ANEMIA",x.BIO_HB<12),("FERRIT_LOW",x.BIO_FERRIT<15)]:
        ok=x[name].isin([1,2])
        flags[name]={"valid_published_flags":int(ok.sum()),"threshold_vs_flag_disagreements":int(((x.loc[ok,name]==1)!=low[ok]).sum())}
    study.write(r/"REFERENCE_FIELD_AUDIT.json",{"time_utc":study.sandbox.now(),"post_disclosure":True,
        "n_eligible":len(e),"missing_Hb":int(e.BIO_HB.isna().sum()),"missing_ferritin":int(e.BIO_FERRIT.isna().sum()),
        "complete":len(x),"flags":flags,"unit_basis":"release codebook, Bio file pp. 6–7","new_or_adjusted_estimands":0})


if __name__=="__main__":main()
