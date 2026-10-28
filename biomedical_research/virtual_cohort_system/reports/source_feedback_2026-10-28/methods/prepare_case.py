"""Custodian-only preparation. Freezes protocol before reading participant tables.

Never prints outcome values, distributions, coefficients, or other evaluations.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import platform
import sys
import urllib.request
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import scipy
import pyreadstat

HERE = pathlib.Path(__file__).resolve().parent
PILOT = HERE.parent.parent
VISIBLE = PILOT / "visible" / "nhanes_tg_j_v2"

def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def write_json(path, obj):
    pathlib.Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")

def now():
    return datetime.now(timezone.utc).isoformat()

PROTOCOL = {
  "version": "1.1",
  "preparation_amendment": "Before any target analyses or builder access, supersede v1 preparation because pandas 3.0.3 XPORT reader decoded 325 true zero fasting weights as 5.397605346934028e-79. ReadStat 1.3.7 correctly decodes 2711 positive and 325 zero weights, matching official documentation. Statistical analysis plan unchanged.",
  "case_id": "nhanes_2017_2018_reference_fasting_tg_whole_column",
  "purpose": "Exploratory evidence-guided virtual-column analytical utility; no exact individual recovery claim.",
  "selection_before_outcome_analysis": {
    "cycle": "2017-2018", "files": ["DEMO_J", "BMX_J", "TRIGLY_J"],
    "target": "LBXTR reference-method fasting serum triglycerides, mg/dL",
    "domain": "RIDAGEYR 20 through 79 inclusive; RIAGENDR in 1,2; finite positive BMXBMI and LBXTR; finite positive WTSAF2YR; nonmissing SDMVSTRA and SDMVPSU; MEC examined RIDSTATR=2",
    "age_rationale": "Exclude topcoded age 80+ so age association has an unambiguous year scale.",
    "fasting": "Use WTSAF2YR>0. TRIGLY_J documentation assigns zero to participants not meeting 8 to <24 hour fasting or without qualifying lab specimen. No inclusion/reweighting of zero-weight records.",
    "missingness": "Complete cases form a prespecified analysis domain. No outcome imputation, item-nonresponse reweighting, outlier removal, winsorization, or data-selected transformation. Inference does not establish representativeness after item nonresponse.",
    "survey_universe": "All linked records with WTSAF2YR>0 and valid design variables remain in the variance-design table, including observations outside the complete-case adult domain. Their estimating-function contributions are zero."
  },
  "visible": {"schema": ["record_id", "age", "sex", "bmi"], "id": "Opaque random-order IDs; SEQN mapping stays custodial", "sex": "1=male, 2=female, as recorded by NHANES RIAGENDR", "age_unit": "years", "bmi_unit": "kg/m^2", "output": "Append finite positive tg_mg_dl; preserve all input cells and row order"},
  "transforms": {"outcome": "natural logarithm of TG in mg/dL", "rationale": "A priori multiplicative concentration/ratio estimand. No outcome distribution inspection used to choose transformation.", "B": "(bmi-25)/5", "A": "(age-50)/10", "F": "1 if sex=2 else 0"},
  "models": {
    "adjusted": "log(TG)=intercept+b_B*B+b_A*A+b_F*F+error",
    "curvature": "log(TG)=intercept+b_B*B+b_A*A+b_F*F+b_Q*B^2+error",
    "interaction": "log(TG)=intercept+b_B*B+b_A*A+b_F*F+b_I*B*F+error"
  },
  "endpoints": [
    {"id": "adjusted_bmi_per5", "tier": "primary", "model": "adjusted", "contrast": "b_B", "meaning": "TG geometric-mean ratio per 5 kg/m^2 higher BMI, adjusted for age and sex"},
    {"id": "adjusted_age_per10", "tier": "reserved_secondary", "model": "adjusted", "contrast": "b_A", "meaning": "TG ratio per 10 years, adjusted for BMI and sex"},
    {"id": "adjusted_female_vs_male", "tier": "reserved_secondary", "model": "adjusted", "contrast": "b_F", "meaning": "Female/male TG ratio, adjusted for BMI and age"},
    {"id": "bmi_curvature_second_difference", "tier": "reserved_secondary", "model": "curvature", "contrast": "2*b_Q", "meaning": "log(TG at BMI35)-2*log(TG at BMI30)+log(TG at BMI25), age/sex held constant"},
    {"id": "bmi_sex_interaction", "tier": "reserved_secondary", "model": "interaction", "contrast": "b_I", "meaning": "Female minus male log-TG slope per 5 kg/m^2; exponentiation is a ratio of BMI ratios"}
  ],
  "estimation": {
    "point": "Weighted least squares using WTSAF2YR (normalized by its domain mean for numerical stability; invariant to global weight rescaling)",
    "variance": "With-replacement first-stage Taylor linearization. H=sum_domain(w*x*x'); score_i=domain_i*w_i*x_i*(y_i-x_i'b); u_hj=sum_i_in_PSU(score_i). Meat=sum_h m_h/(m_h-1)*sum_j (u_hj-mean_j(u_hj))*(u_hj-mean_j(u_hj))'. V=H^-1 Meat H^-1. Include every positive-weight design PSU, even with zero domain score; no finite population correction.",
    "interval": "Two-sided 95% t interval with df equal to represented-domain PSUs minus represented-domain strata; report df and full design support. No parameter-count subtraction; this is an explicit NHANES nominal design-df convention.",
    "singleton": "If a full-design stratum has fewer than two PSUs or domain design df<=0, stop and report non-estimable; no automatic lonely-PSU fix.",
    "implementation": "Python NumPy/pandas/SciPy custom implementation; validate against analytic invented fixtures, WLS point estimate, weight rescaling and PSD covariance. R not found in PATH or standard installation locations; no claim of R survey cross-validation."
  },
  "comparison": {
    "gate": "No evaluation until root confirms every initial/final generated target table is committed and its hashes are recorded. Custodian evaluates all committed outputs using identical frozen models, domain, rows, weights and survey design.",
    "report": "Reference and each generated endpoint: log-scale coefficient, SE, 95% interval, exp-scale ratio interval and direction category (positive, negative, or interval includes zero). Report signed difference and absolute log-scale error, initial-to-final changes for matched seeds, and summaries across seeds.",
    "limits": "Same-person generated and reference estimates are dependent; do not use independent-sample difference intervals. No scientific pass threshold is chosen. No equivalence or absence-of-association claim follows from nonsignificance. CI overlap or a generated point falling inside a reference CI is descriptive, not a calibrated coverage/equivalence test. Secondary intervals are unadjusted exploratory intervals. Draw variation is simulation sensitivity, not source/model/transport uncertainty. No post-evaluation builder revision."
  },
  "boundary": {"type": "procedural only, not OS isolation", "builder_excluded": ["custodian directory", "NHANES outcome tables or APIs", "NHANES-derived studies as construction evidence", "previous target outcome results"], "release": "Only observed.csv, task_metadata.json, README.md, preparation_counts.json, and visible input hashes may be shared before commitment; protocol may be inspected by controller without outcomes."},
  "official_documentation": [
    "https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/datafiles/TRIGLY_J.htm",
    "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.htm",
    "https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/datafiles/DEMO_J.htm",
    "https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx",
    "https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx"
  ]
}

def main():
    if (HERE / "protocol_freeze.json").exists():
        raise SystemExit("Already frozen; do not overwrite this case")
    VISIBLE.mkdir(parents=True, exist_ok=False)
    (HERE / "raw").mkdir(exist_ok=False)
    (HERE / "documentation").mkdir(exist_ok=False)
    write_json(HERE / "analysis_protocol.json", PROTOCOL)
    write_json(HERE / "protocol_freeze.json", {"frozen_utc": now(), "before_download_and_table_read": True,
        "files": {p.name:digest(p) for p in [HERE / "analysis_protocol.json", pathlib.Path(__file__).resolve(), HERE / "survey_analysis.py", HERE / "evaluate_committed.py"]}})
    provenance=[]
    for name in ["DEMO_J", "BMX_J", "TRIGLY_J"]:
        url=f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/{name}.xpt"
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 public academic data audit"})
        with urllib.request.urlopen(req, timeout=90) as response:
            raw=response.read()
            record={"name":name,"requested_url":url,"resolved_url":response.url,"content_type":response.headers.get("Content-Type"),"downloaded_utc":now(),"bytes":len(raw)}
        if not raw.startswith(b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"):
            raise RuntimeError(f"{name} is not SAS XPORT; rejecting response without parsing")
        path=HERE/"raw"/(name+".xpt")
        path.write_bytes(raw)
        record["sha256"]=digest(path)
        record["xport_magic_verified"]=True
        provenance.append(record)
    for i,url in enumerate(PROTOCOL["official_documentation"]):
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90) as response:
            raw=response.read()
            path=HERE/"documentation"/f"official_{i+1}.html"
            path.write_bytes(raw)
            provenance.append({"requested_url":url,"resolved_url":response.url,"downloaded_utc":now(),"bytes":len(raw),"sha256":digest(path),"path":str(path.relative_to(HERE))})
    write_json(HERE/"data_provenance.json",provenance)
    demo=pyreadstat.read_xport(str(HERE/"raw"/"DEMO_J.xpt"))[0]
    bmi=pyreadstat.read_xport(str(HERE/"raw"/"BMX_J.xpt"))[0]
    tg=pyreadstat.read_xport(str(HERE/"raw"/"TRIGLY_J.xpt"))[0]
    assert int(tg.WTSAF2YR.eq(0).sum()) == 325, "Official documented zero-weight count mismatch"
    assert int(tg.WTSAF2YR.gt(0).sum()) == 2711, "Official positive-weight count mismatch"
    for frame in [demo,bmi,tg]:
        assert frame.SEQN.is_unique and frame.SEQN.notna().all()
    merged=tg[["SEQN","WTSAF2YR","LBXTR"]].merge(demo[["SEQN","RIDAGEYR","RIAGENDR","RIDSTATR","SDMVSTRA","SDMVPSU"]],on="SEQN",how="left",validate="one_to_one").merge(bmi[["SEQN","BMXBMI"]],on="SEQN",how="left",validate="one_to_one")
    good_design=np.isfinite(merged[["WTSAF2YR","SDMVSTRA","SDMVPSU"]]).all(axis=1)&merged.WTSAF2YR.gt(0)
    full=merged.loc[good_design].copy().reset_index(drop=True)
    adult=full.RIDAGEYR.between(20,79)&full.RIDSTATR.eq(2)&full.RIAGENDR.isin([1,2])
    good_bmi=np.isfinite(full.BMXBMI)&full.BMXBMI.gt(0)
    good_tg=np.isfinite(full.LBXTR)&full.LBXTR.gt(0)
    domain=adult&good_bmi&good_tg
    full["eligible"]=domain.astype(int)
    indices=np.flatnonzero(domain)
    indices=indices[np.random.default_rng(20261028).permutation(len(indices))]
    full["record_id"]=""
    full.loc[indices,"record_id"]=[f"TGJ{i:05d}" for i in range(1,len(indices)+1)]
    full.to_csv(HERE/"design_with_hidden_outcome.csv",index=False)
    observed=full.loc[indices,["record_id","RIDAGEYR","RIAGENDR","BMXBMI"]].rename(columns={"RIDAGEYR":"age","RIAGENDR":"sex","BMXBMI":"bmi"}).reset_index(drop=True)
    observed[["age","sex"]]=observed[["age","sex"]].astype(int)
    observed.to_csv(VISIBLE/"observed.csv",index=False)
    support=full[["SDMVSTRA","SDMVPSU"]].drop_duplicates()
    domain_support=full.loc[domain,["SDMVSTRA","SDMVPSU"]].drop_duplicates()
    assert (support.groupby("SDMVSTRA").size()>=2).all()
    counts={"raw_file_rows":{"DEMO_J":len(demo),"BMX_J":len(bmi),"TRIGLY_J":len(tg)},"positive_weight_valid_design_rows":len(full),"adult_20_79_valid_demographic_rows":int(adult.sum()),"adult_invalid_or_missing_BMI":int((adult&~good_bmi).sum()),"adult_invalid_or_missing_TG":int((adult&~good_tg).sum()),"eligible_complete_rows":len(observed),"eligible_sex_counts":{str(k):int(v) for k,v in observed.sex.value_counts().sort_index().items()},"full_design_strata":support.SDMVSTRA.nunique(),"full_design_PSUs":len(support),"domain_strata":domain_support.SDMVSTRA.nunique(),"domain_PSUs":len(domain_support),"nominal_domain_df":len(domain_support)-domain_support.SDMVSTRA.nunique(),"outcome_values_or_reference_statistics_released":False}
    write_json(VISIBLE/"preparation_counts.json",counts)
    metadata={"case_id":PROTOCOL["case_id"],"n_rows":len(observed),"mode":"enrichment","row_id":"record_id","observed_file":"observed.csv","observed_schema":[{"name":"record_id","kind":"string","unit":"","role":"identifier"},{"name":"age","kind":"integer","unit":"years","role":"observed"},{"name":"sex","kind":"category","unit":"","categories":[1,2],"mapping":{"1":"male","2":"female"},"role":"observed"},{"name":"bmi","kind":"number","unit":"kg/m^2","role":"observed"}],"generated_column":{"name":"tg_mg_dl","kind":"number","unit":"mg/dL","strictly_positive":True,"nullable":False},"population":"NHANES 2017-2018 fasting subsample, MEC-examined adults aged 20-79 with available positive BMI and reference-method TG; full TG column hidden.","scientific_question":"Can source-guided TG generation support the association of BMI with log fasting TG, adjusted for age and sex, while retaining plausible relationships with the observed covariates?","primary_analysis":"Natural log TG regressed on BMI per 5 kg/m^2, age per 10 years, and female indicator; custodian uses NHANES fasting survey weights, strata and PSUs.","requirements":["Preserve every observed value and row order.","Generate the entire tg_mg_dl column; do not recover individual public records.","Use only controller-approved external evidence; NHANES-derived studies and outcome files are excluded.","Represent unsupported relationships and transport assumptions explicitly; preserve initial and final candidate outputs before target evaluation."],"information_boundary":"Procedural holdout only; file tools are not OS-isolated. Do not inspect custodian paths or attempt public-record linkage.","protocol_sha256":digest(HERE/"analysis_protocol.json")}
    write_json(VISIBLE/"task_metadata.json",metadata)
    (VISIBLE/"README.md").write_text("# New public fasting-triglyceride case\n\nOnly this visible folder is builder input. `observed.csv` contains opaque record IDs, age in years, sex (1 male; 2 female), and BMI in kg/m². Append the positive `tg_mg_dl` column in mg/dL while preserving every input cell and row order.\n\nThe source-data population is the NHANES 2017–2018 positive-weight fasting subsample, adults aged 20–79 with complete required measurements. A separate custodian retains the entire reference TG column, SEQN mapping, survey weights, strata and PSUs. Only preparation counts are released here. The intended primary use is the adjusted BMI relation on a prespecified natural-log TG scale; further relationships are reserved for evaluation.\n\nDo not read the custodian directory, fetch NHANES outcome tables, link records, inspect previous outcome results, or use NHANES-derived studies as construction evidence. This is procedural holdout, not OS-level isolation. External evidence and assumptions must be documented; source replay is not target validation.\n",encoding="utf-8")
    write_json(VISIBLE/"input_hashes.json",{"created_utc":now(),"files":{p.name:digest(p) for p in sorted(VISIBLE.iterdir()) if p.is_file()}})
    write_json(HERE/"preparation_receipt.json",{"completed_utc":now(),"protocol_freeze_sha256":digest(HERE/"protocol_freeze.json"),"protocol_sha256":digest(HERE/"analysis_protocol.json"),"hidden_table_sha256":digest(HERE/"design_with_hidden_outcome.csv"),"visible_input_hashes_sha256":digest(VISIBLE/"input_hashes.json"),"provenance_sha256":digest(HERE/"data_provenance.json"),"environment":{"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,"pandas":pd.__version__,"scipy":scipy.__version__,"pyreadstat":pyreadstat.__version__},"target_analyses_run":False})
    print(json.dumps({"status":"prepared_no_outcome_analysis","visible_folder":str(VISIBLE),"counts":counts,"protocol_sha256":digest(HERE/"analysis_protocol.json")}))

if __name__=="__main__":
    main()
