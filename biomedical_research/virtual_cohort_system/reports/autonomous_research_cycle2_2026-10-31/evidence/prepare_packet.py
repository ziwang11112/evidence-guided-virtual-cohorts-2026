"""Prepare authored source metadata only; never generate patient rows or model code."""
from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKET = HERE / "packet"
PROJECT = HERE.parents[2]
DATE = "2026-10-31"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PROJECT))
from cohort_harness.contracts import validate_evidence, validate_task

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_text(rel, body):
    path = PACKET / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")
    return path

def write_json(rel, body):
    return write_text(rel, json.dumps(body, ensure_ascii=False, indent=2, allow_nan=False))

def decimal_product(value, multiplier, divisor="1", offset="0"):
    return float(Decimal(str(value)) * Decimal(multiplier) / Decimal(divisor) + Decimal(offset))

SUMMARIES = {
"JANSEN2013": """# Jansen 2013: source summary

[Original](https://onlinelibrary.wiley.com/doi/10.1111/joim.12010); DOI 10.1111/joim.12010. Authored extraction; no article body.

Population: unrelated western-European Lifelines adults, oldest family members favored for GWAS. Diabetes, significant anemia and missing HbA1c/erythrocytes/FPG excluded; eligible n=2921. HbA1c immunoassay is IFCC-standardized; fresh fasting-plasma glucose uses hexokinase/G6PD. Explicit age limits and fasting hours remain unknown.

| Table 1 | Mean / SD |
|---|---|
| Age, years | 55.5 / 9.9 |
| BMI, kg/m² | 26.5 / 4.1 |
| FPG, mmol/L | 5.1 / 0.5 |
| HbA1c, % | 5.6 / 0.3 |
| HbA1c, mmol/mol | 38 / 3 |

Table 1 reports 1176 males (40.3%). Spreads are SDs. Rounded unit summaries remain distinct.

Table 2 separately adjusts each predictor for age/gender: BMI→HbA1c 0.13 (CI 0.10–0.16); FPG→HbA1c 2.29 (2.07–2.51), HbA1c mmol/mol. Row-specific n and CI confidence level are unconfirmed.

Quarantined Table 3 II: age/gender/FPG coefficients 0.08/0.35/2.25, R²20.5%; sample n, coding, intercept/residual law unresolved. III additionally conditions on BMI/MCH/MCHC/smoking/alcohol. Do not reduce it by deleting terms.

Locators: Methods; Tables 1–3/footnotes; Appendix A3–A4. One bounded header/method recheck found no confidence level; genotype call-rate 95% is unrelated.
""",
"PANI2008": """# Pani 2008: source summary

[Original](https://pmc.ncbi.nlm.nih.gov/articles/PMC2551641/); DOI 10.2337/dc08-0577. Authored extraction; no article body.

NHANES 2001–2004 n=3270, age≥25, no self-reported diabetes, FPG<126 mg/dL. Analyses account for complex survey design/weights. NGSP/DCCT-standardized HbA1c HPLC; hexokinase glucose; fasting hours unspecified.

Results before Table 2: HbA1c age coefficient 0.010 percentage points/year, adjusted sex/BMI/FPG; P<0.001, coefficient SE unreported.

| Table 1 age | n | HbA1c mean, % | SE, % |
|---|---:|---:|---:|
| <40 | 1037 | 5.20 | 0.01 |
| 40–44 | 330 | 5.28 | 0.02 |
| 45–49 | 322 | 5.37 | 0.02 |
| 50–54 | 261 | 5.40 | 0.02 |
| 55–59 | 198 | 5.44 | 0.02 |
| 60–64 | 283 | 5.46 | 0.03 |
| 65–69 | 198 | 5.50 | 0.03 |
| ≥70 | 641 | 5.51 | 0.02 |

These SEs are not individual SDs. Do not use SE×sqrt(n) to manufacture survey dispersion.

FOS is a different population and adjustment set: its 0.012 slope also adjusts 2-hour glucose. FOS retains diabetic-range OGTT results and is separate from its NGT subgroup. Demographic spread labeling and percentile discrepancies remain quarantined. Appendix coefficients/intercept/residual scale were not recovered. NHANES overlaps Liu's survey years; no independent replication claim.
""",
"LIU2015": """# Liu 2015: contextual source summary

[Original](https://pmc.ncbi.nlm.nih.gov/articles/PMC4454807/); DOI 10.1210/jc.2014-4454. Authored extraction; no article body.

NHANES 1999–2008, fasting adults≥20, no diabetes by history/medication/FPG≥126 mg/dL, no anemia. Pregnancy remains in primary analyses. HbA1c assays are NGSP-certified; FPG uses hexokinase. Fasting hours unspecified.

Methods, Calculating the hemoglobin glycation index: random training n=831 from eligible n=8310; HbA1c(%)=3.7+0.017×FPG(mg/dL). This is one univariate projection, retained together as context, not a joint-model intercept and slope. HGI=observed−predicted HbA1c. Subsequent n=7323 follows exclusions.

Table 1 overall HbA1c 5.3±0.01%, FPG 96.5±0.2 mg/dL, age44.6±0.3years: spreads are SEs. Table 3 age coefficient 0.006 concerns HGI with additional erythrocyte, demographic, lipid, year and obesity adjustment. Table 2 reports Kendall tau against inflammation, not HbA1c–FPG Pearson correlation.

These results are contextual only in this packet. Training and later analysis populations must not be mixed; residual SD is unavailable. Survey years overlap Pani/NHANES. Do not add its univariate FPG coefficient to Pani's adjusted age coefficient to create a multivariable equation.
""",
"NGSP": """# NGSP: measurement conversion guidance

[Official page](https://ngsp.org/ifccngsp.asp), The IFCC and NGSP, Table 2.

NGSP HbA1c (%) = 0.09148 × IFCC HbA1c (mmol/mol) + 2.152.

The multiplier applies to slopes, SDs, SEs and slope-CI endpoints; the offset applies only to levels/intercepts. Variances multiply by the squared multiplier. These are algebraic derivations from the published conversion, not independent clinical observations.

The packet keeps original and converted values distinct. Published rounded percent and IFCC marginals need not coincide exactly. FPG is not eAG. Assay/selection/transport differences remain unresolved by unit conversion.

A separate protocol normalization fixes glucose at 18.0 mg/dL per mmol/L. This conventional rounded factor is a declared task rule, not fitted, and is not attributed to NGSP as a fasting-glucose model.
""",
}

POPS = {
"JANSEN2013": "Lifelines western-European unrelated adults selected for GWAS, oldest family members preferred; n=2921 eligible; excludes self-reported diabetes or FPG>=7.0 mmol/L, significant anemia, and missing HbA1c/erythrocytes/FPG. Table 2 row-specific n unknown; Table 3 complete-case n unresolved.",
"PANI2008": "Pani NHANES 2001-2004 n=3270, adults age>=25, no self-reported diabetes, FPG<126 mg/dL, HbA1c available. Complex survey design and weights. FOS context is different and is not pooled. NHANES overlaps Liu1999-2008.",
"LIU2015": "NHANES1999-2008 fasting age>=20; excludes diabetes by history/medication/FPG>=126 mg/dL and anemia. Training n=831 of8310; later analysis n=7323; pregnancy retained. Overlaps Pani NHANES; contextual only.",
"NGSP": "Official measurement standardization guidance, not a cohort or target population."
}
MEAS = {
"JANSEN2013": "HbA1c IFCC-standardized turbidimetric inhibition immunoassay; FPG fresh fasting venous plasma, hexokinase/G6PD. Table1 spreads SD; coefficients HbA1c mmol/mol. Hours fasted unspecified.",
"PANI2008": "HbA1c NGSP/DCCT standardized HPLC, percent; glucose hexokinase, mg/dL. Table1 spreads SE. Cross-sectional age coefficient percent/year. Hours fasted unspecified.",
"LIU2015": "HbA1c NGSP-certified assays, percent; glucose hexokinase mg/dL. Table1 spreads SE; HGI is observed minus predicted HbA1c. Univariate equation retained as context.",
"NGSP": "NGSP percent=0.09148*IFCC mmol/mol+2.152. Unit guidance only, not biological calibration or FPG/eAG equivalence."
}
IDENTIFIERS = {
"JANSEN2013": "Jansen2013 DOI10.1111/joim.12010; PMID23121487; authored summary of original, independent source audit completed, root admission pending",
"PANI2008": "Pani2008 DOI10.2337/dc08-0577; PMC2551641; authored summary of original, independent source audit completed, root admission pending",
"LIU2015": "Liu2015 DOI10.1210/jc.2014-4454; PMC4454807; contextual authored summary, root admission pending",
"NGSP": "NGSP official https://ngsp.org/ifccngsp.asp; measurement conversion guidance; root admission pending"
}
COHORTS = {
"JANSEN2013":["Lifelines"],
"PANI2008":["NHANES","NHANES2001-2004","Framingham-Offspring-context-only"],
"LIU2015":["NHANES","NHANES1999-2008"],
"NGSP":[]
}

def prepare():
    PACKET.mkdir(parents=True, exist_ok=True)
    artifacts = []
    sources = []
    for sid, summary in SUMMARIES.items():
        rel = f"sources/{sid}/source_summary.md"
        path = write_text(rel, summary)
        artifact = {"path":rel,"sha256":digest(path)}
        artifacts.append({"source_id":sid,**artifact})
        sources.append({"id":sid,"identifier":IDENTIFIERS[sid],"population":POPS[sid],
                        "measurement":MEAS[sid],"cohort_ids":COHORTS[sid],"artifacts":[artifact]})

    items, normalized, dispositions = [], [], []
    def add(iid,sid,kind,value,variables,unit,locator,selection,applicability,
            adjustment=(),uncertainty=None,status="source_constraint_pending_root",
            derived_from=(),formula=None,extra=None):
        item={"id":iid,"source_id":sid,"locator":locator,"variables":list(variables),
              "kind":kind,"estimate":value,"unit":unit,
              "uncertainty":uncertainty or {"kind":"not_reported"},
              "adjustment":list(adjustment),"selection":selection,
              "applicability":applicability}
        items.append(item)
        record={"item_id":iid,"status":status,"representation":"derived" if derived_from else "reported",
                "derived_from":list(derived_from),"formula":formula}
        if extra: record.update(extra)
        normalized.append(record)
        dispositions.append({"item_id":iid,"status":status,"may_bind_model_without_root_admission":False})
        return iid

    jsel=POPS["JANSEN2013"]
    base_note="Source-context marginal only; does not identify joint dependence, support or residual distribution. Pending root admission."
    for var,mean,sd,unit,label in [
        ("age",55.5,9.9,"year","Age (years)"),
        ("bmi",26.5,4.1,"kg/m^2","BMI"),
        ("glucose",5.1,0.5,"mmol/L","Fasting plasma glucose"),
        ("hba1c",5.6,0.3,"%","HbA1c (%)"),
        ("hba1c",38.0,3.0,"mmol/mol","HbA1c (mmol/mol)")]:
        suffix={"%":"pct","mmol/mol":"ifcc","mmol/L":"mmol_L"}.get(unit,"task")
        for kind,val in [("mean",mean),("sd",sd)]:
            iid=f"J_T1_{var}_{kind}_{suffix}"
            add(iid,"JANSEN2013",kind,val,[var],unit,
                f"Table1 {label} row and SD footnote",jsel,base_note,
                extra={"reported_sample_n":2921,"spread_label":"SD",
                       "same_quantity_group":f"J_T1_{var}_{kind}"})
    add("J_T1_male_proportion_reported","JANSEN2013","proportion",0.403,["female"],"1",
        "Table1 Male (%) row",jsel,
        "P(female=0), NOT P(female=1); reported 40.3% (1176 males). Task female coding is 1=female,0=male, distinct from unknown regression coding.",
        extra={"event":{"female":0},"reported_count":1176,"reported_percent":40.3,"reported_sample_n":2921})
    add("J_T1_female_proportion_derived","JANSEN2013","proportion",0.597,["female"],"1",
        "Derived from Table1 reported male40.3%; fixed task binary coding",jsel,
        "P(female=1)=1-0.403; complement of rounded reported percentage, not an exact-count fraction. Not source regression coding.",
        derived_from=["J_T1_male_proportion_reported"],formula="1-0.403",
        extra={"event":{"female":1},"same_quantity_group":"J_T1_sex_composition"})
    for kind,val in [("mean",5.1),("sd",0.5)]:
        add(f"J_T1_glucose_{kind}_mg_dL_derived","JANSEN2013",kind,
            decimal_product(val,"18.0"),["glucose"],"mg/dL","Table1 FPG; fixed protocol glucose conversion",
            jsel,base_note+" Original retained; conventional rounded factor18.0 is fixed, not fitted.",
            derived_from=[f"J_T1_glucose_{kind}_mmol_L"],formula=f"{val}*18.0",
            extra={"same_quantity_group":f"J_T1_glucose_{kind}"})
    for kind,val,offset in [("mean",38.0,"2.152"),("sd",3.0,"0")]:
        add(f"J_T1_hba1c_{kind}_pct_from_ifcc","JANSEN2013",kind,
            decimal_product(val,"0.09148",offset=offset),["hba1c"],"%",
            "Table1 IFCC row; NGSP master equation",jsel,
            "Derived unit representation only. Keep separately from published rounded percent row; do not count both as independent constraints or force exact agreement.",
            status="alternative_unit_representation_not_independent",
            derived_from=[f"J_T1_hba1c_{kind}_ifcc"],formula=f"{val}*0.09148+{offset}",
            extra={"conversion_source":"NGSP","same_quantity_group":f"J_T1_hba1c_{kind}"})

    for var,b,lo,hi,unit,divisor in [
        ("bmi",0.13,0.10,0.16,"mmol/mol per kg/m^2","1"),
        ("glucose",2.29,2.07,2.51,"mmol/mol per mmol/L","18.0")]:
        orig=f"J_T2_{var}_slope_original"
        desc=(f"Separate HbA1c-on-{var} projection adjusted age/female (binary sex covariate); "
              "other Table2 predictors were not included together. Source gender numeric coding unknown, but adjustment for a binary complement spans the same intercept-adjusted covariate space. "
              f"Printed CI [{lo},{hi}], confidence level unspecified; uncertainty.kind=not_reported encodes absent level/SE, not absence of printed bounds. "
              "Table2 row-specific n unknown; do not substitute Table1 n or Table3 II.")
        add(orig,"JANSEN2013","ols_coefficient",b,["hba1c",var],unit,
            f"Table2 {var} row, header and separate-addition footnote; Statistical methods",
            jsel,desc,adjustment=["age","female"],
            extra={"outcome":"hba1c","predictor":var,"reported_ci":{"low":lo,"high":hi,"level":None},
                   "row_n":None,"same_quantity_group":f"J_T2_{var}_slope"})
        taskunit="% per kg/m^2" if var=="bmi" else "% per mg/dL"
        bb=decimal_product(b,"0.09148",divisor)
        ll=decimal_product(lo,"0.09148",divisor)
        hh=decimal_product(hi,"0.09148",divisor)
        add(f"J_T2_{var}_slope_task_derived","JANSEN2013","ols_coefficient",bb,
            ["hba1c",var],taskunit,f"Derived from {orig}; NGSP conversion; fixed glucose factor18.0 if applicable",
            jsel,desc+f" Derived task-unit CI [{ll},{hh}], level unknown; no affine offset on slopes.",
            adjustment=["age","female"],derived_from=[orig],
            formula=f"{b}*0.09148/{divisor}",
            extra={"outcome":"hba1c","predictor":var,"reported_ci":{"low":ll,"high":hh,"level":None},
                   "row_n":None,"conversion_source":"NGSP","same_quantity_group":f"J_T2_{var}_slope"})

    psel=POPS["PANI2008"]
    add("P_NHANES_age_slope","PANI2008","ols_coefficient",0.010,["hba1c","age"],"% per year",
        "Results paragraph immediately before Table2, following NHANES adjustment statement",psel,
        "Cross-sectional adjusted HbA1c age association. P<0.001; SE/CI not supplied here. Binary female mapping is adjustment only, no source sex coefficient inferred. Survey source; transport is unassessed. Do not merge with Liu univariate equation or FOS2h-adjusted estimate.",
        adjustment=["female","bmi","glucose"],extra={"outcome":"hba1c","predictor":"age","source_analysis":"complex-survey adjusted regression"})
    for key,label,nn,mean,se,low,high in [
        ("lt40","<40",1037,5.20,0.01,25,40),
        ("40_44","40-44",330,5.28,0.02,40,45),
        ("45_49","45-49",322,5.37,0.02,45,50),
        ("50_54","50-54",261,5.40,0.02,50,55),
        ("55_59","55-59",198,5.44,0.02,55,60),
        ("60_64","60-64",283,5.46,0.03,60,65),
        ("65_69","65-69",198,5.50,0.03,65,70),
        ("ge70",">=70",641,5.51,0.02,70,None)]:
        add(f"P_NHANES_hba1c_age_{key}_mean","PANI2008","mean",mean,["hba1c","age"],"%",
            f"Table1 NHANES nondiabetic subjects, age{label}, Mean+-SE",psel+f" Source age stratum {label}.",
            "Survey-weighted source age-stratum mean; SE is sampling uncertainty, not individual SD. No SE*sqrt(n) conversion. Separate source diagnostic, not an imposed target age curve.",
            uncertainty={"kind":"se","value":se},status="source_diagnostic_pending_root",
            extra={"stratum_n_unweighted":nn,"age_stratum_display":label,
                   "age_rule":{"minimum_inclusive":low,"maximum_exclusive":high},
                   "age_rule_note":"Half-open encoding of published integer-year age categories plus source age>=25; continuous-age boundary handling is a downstream assumption."})

    add("L_UNIVARIATE_EQUATION_CONTEXT","LIU2015","contextual",None,["hba1c","glucose"],"",
        "Methods: Calculating the hemoglobin glycation index",POPS["LIU2015"],
        "CONTEXT ONLY: HbA1c(%)=3.7+0.017*FPG(mg/dL), both terms from the same univariate training projection. No multivariable or residual-law identification; no independent replication because NHANES years overlap Pani. Never extract these numbers as a joint-model intercept/slope.",
        status="contextual_not_calibration")
    add("J_TABLE3_QUARANTINE","JANSEN2013","contextual",None,["hba1c","age","female","bmi","glucose"],"",
        "Table3 ModelsII/III; Table2 alcohol footnote; AppendixA3/A4",jsel,
        "Table3II coefficients, sex coding, intercept and residual law are quarantined; exact row n unresolved. ModelIII conditions on additional erythrocyte/lifestyle variables. See human summary; no Table3 numeric calibration items admitted.",
        status="quarantined_not_calibration")
    add("NGSP_UNIT_GUIDANCE","NGSP","contextual",None,["hba1c"],"",
        "Official IFCC and NGSP page, Table2",POPS["NGSP"],
        "Measurement guidance: NGSP%=0.09148*IFCC(mmol/mol)+2.152; slopes/SD/SE scale only, levels add offset. No biological relation or FPG/eAG model inferred.",
        status="unit_guidance_not_clinical_constraint")

    evidence={"schema_version":1,"sources":sources,"items":items}
    columns=[
        {"name":"row_id","kind":"string","unit":"","role":"identifier","nullable":False},
        {"name":"age","kind":"number","unit":"year","role":"generated","nullable":False},
        {"name":"female","kind":"integer","unit":"1","role":"generated","nullable":False,"minimum":0,"maximum":1},
        {"name":"bmi","kind":"number","unit":"kg/m^2","role":"generated","nullable":False},
        {"name":"glucose","kind":"number","unit":"mg/dL","role":"generated","nullable":False},
        {"name":"hba1c","kind":"number","unit":"%","role":"generated","nullable":False}]
    task={"schema_version":1,"task_id":"DRAFT_source_packet_schema_check_only",
          "mode":"whole_cohort","population":"DRAFT schema scaffold only; target is not frozen or defined by this file",
          "row_id":"row_id","n_rows":1,"columns":columns,
          "information_policy":{"mode":"published_evidence","excluded_cohorts":[],"allowed_tools":[]},
          "budget":{"source_queries":0,"source_downloads":0,"revisions":0}}
    write_json("evidence_template.json",evidence)
    write_json("schema_check_task_DRAFT.json",task)
    write_json("normalized_quantities.json",{
        "status":"pending_root_admission","task_columns":[c["name"] for c in columns],
        "column_coding":{"female":"1=female,0=male; protocol coding, not inferred source regression coding"},
        "records":normalized,
        "contextual_exclusion":"Liu equation and Table3 context have null estimates in evidence_template; no contextual numeric fields available for calibration.",
        "duplicate_representations":"same_quantity_group marks original/derived views of one quantity; not independent evidence or simultaneous exact constraints."})
    write_json("item_dispositions.json",{"status":"pending_root_admission","items":dispositions})
    write_json("conversion_rules.json",{
        "status":"fixed_nonfitted_normalization_rules",
        "glucose":{"from":"mmol/L","to":"mg/dL","multiplier":18.0,
                   "provenance":"Parent-authorized conventional rounded protocol rule; not fitted or an estimated source relationship",
                   "mean_sd_se_ci":"multiply by18.0","regression_predictor_slope":"divide by18.0 when predictor changes from mmol/L to mg/dL"},
        "hba1c":{"source_id":"NGSP","from":"IFCC mmol/mol","to":"NGSP %",
                  "multiplier":0.09148,"level_offset":2.152,"locator":"https://ngsp.org/ifccngsp.asp Table2",
                  "mean":"multiply by0.09148, add2.152","sd_se_outcome_slope":"multiply by0.09148; no offset",
                  "variance":"multiply by0.09148 squared"},
        "rounding":"Decimal arithmetic uses printed decimals; converted precision is algebraic, not extra measurement accuracy.",
        "unknown_ci_level":"Printed bounds preserved; no CI level or SE reconstructed."})
    write_json("registry_proposal_PENDING.json",{
        "status":"pending_root_admission",
        "is_harness_registry":False,
        "reason":"Harness registry requires screening=approved; only root may make admission. No curator approval is asserted.",
        "proposed_artifacts":[{**a,"proposed_origin":"curator","screening":"pending_root_admission"} for a in artifacts]})

    validate_task(task)
    ids=validate_evidence(evidence,task)
    for source in sources:
        for artifact in source["artifacts"]:
            assert digest(PACKET/artifact["path"])==artifact["sha256"]
    assert [c["name"] for c in task["columns"]]==["row_id","age","female","bmi","glucose","hba1c"]
    assert all(i["estimate"] is None for i in items if i["source_id"]=="LIU2015")
    assert not any(i["id"].startswith("J_TABLE3") and i["estimate"] is not None for i in items)
    assert all(i["uncertainty"]["kind"]=="se" for i in items if i["id"].startswith("P_NHANES_hba1c_age_"))
    assert all(i["uncertainty"]["kind"]=="not_reported" for i in items if i["id"].startswith("J_T2"))
    assert not any(x["kind"]=="ci" and x.get("level")==0.95 for x in [i["uncertainty"] for i in items])
    by_id={item["id"]:item for item in items}
    for key,expected in {
        "J_T1_glucose_mean_mg_dL_derived":91.8,
        "J_T1_glucose_sd_mg_dL_derived":9.0,
        "J_T2_bmi_slope_task_derived":0.0118924,
        "J_T2_glucose_slope_task_derived":2.29*0.09148/18.0,
        "J_T1_hba1c_mean_pct_from_ifcc":5.62824,
        "J_T1_hba1c_sd_pct_from_ifcc":0.27444,
    }.items():
        assert abs(by_id[key]["estimate"]-expected)<1e-12
    assert sum(record.get("stratum_n_unweighted",0) for record in normalized)==3270
    assert all(record["reported_ci"]["level"] is None for record in normalized if "reported_ci" in record)
    write_json("schema_check_receipt.json",{
        "status":"pass","admission_status":"pending_root_admission",
        "scope":"validate_task+validate_evidence+authored-source hashes+representation assertions only",
        "evidence_item_count":len(ids),"source_count":len(sources),
        "checks":["draft task schema","evidence schema","artifact hashes","column order","contextual null estimates",
                  "Pani SE preservation","unknown Jansen CI level preserved","fixed unit arithmetic",
                  "Pani unweighted age-stratum counts sum to3270"],
        "not_performed":["registry admission","candidate validation","generator execution","scientific source replay","target evaluation"],
        "task_is_scaffold":True,"candidate_created":False,
        "script_sha256":digest(Path(__file__)),
        "contracts_sha256":digest(PROJECT/"cohort_harness"/"contracts.py")})

    write_text("README.md","""# Source-only normalized packet

Status: **pending root admission**. This authored packet is reviewable evidence preparation, not an approved registry or a scientific generator.

- Four authored summaries: three already audited primary papers and NGSP unit guidance.
- evidence_template.json follows the harness evidence schema. Item dispositions and normalized_quantities.json preserve source/derived roles, exact printed CI bounds, unknown CI levels and sample sizes.
- schema_check_task_DRAFT.json exists only for mechanical validation. It supplies column names/units and a one-row placeholder; it does not define a target, sample size, population supports or generation plan.
- registry_proposal_PENDING.json deliberately is not a valid approved registry. Root must review admission before builder preparation.
- conversion_rules.json fixes glucose18.0 and the official HbA1c affine conversion. Original and converted values are duplicate representations, not independent evidence.
- Source summaries contain contextual exclusions in readable form. Liu's univariate equation is retained as a single contextual projection with a null estimate; Table3 II/III numbers are not numeric calibration items.
- Pani survey SEs remain SEs. Separate regressions retain their conditioning; no complete joint distribution, intercept, covariance or residual law is recovered.

No candidate, patient table, model generator, source body or target record is included.
""")
    ledger={
        "date":DATE,"packet_status":"pending_root_admission",
        "prior_audit_access":"See hashed GLYCEMIA_SOURCE_REVIEW.md and INDEPENDENT_SOURCE_AUDIT.md; their prior retrieval ledger is unchanged.",
        "incremental_primary_papers":0,
        "bounded_recheck":{"source":"Jansen2013 original DOI10.1111/joim.12010",
                          "purpose":"Check whether printed CI confidence level is explicitly stated",
                          "web_calls":1,"open_operations":2,"find_operations":2,
                          "find_terms":["95%","confidence"],
                          "finding":"Methods/header/footnote say CI without confidence level; confidence search no match; 95% pertains to genotype call rates.",
                          "correction":"CI level explicitly unknown; no95% inferred."},
        "direct_http_downloads":0,"direct_body_bytes":0,"web_traffic_bytes":"unmetered",
        "saved_source_article_pdf_xml_ipd_files":0,
        "local_access_note":"Mechanical schema/interface files and artificial example evidence only. An initial broad filename-only rg inventory exposed unrelated path names; no corresponding contents opened. No target/private/STATE data read.",
        "writes":"Only evidence/prepare_packet.py and evidence/packet/*",
        "tests":"Schema checks and metadata/unit arithmetic only; no scientific generator or patient rows."
    }
    write_json("preparation_ledger.json",ledger)
    audit_inputs=[{"path":f"../{name}","sha256":digest(HERE/name),"kind":"authored_source_audit_input"}
                  for name in ["GLYCEMIA_SOURCE_REVIEW.md","INDEPENDENT_SOURCE_AUDIT.md"]]
    files=[{"path":p.relative_to(PACKET).as_posix(),"sha256":digest(p),"bytes":p.stat().st_size}
           for p in sorted(PACKET.rglob("*")) if p.is_file() and p.name!="MANIFEST.json"]
    write_json("MANIFEST.json",{
        "packet_version":1,"status":"pending_root_admission","date":DATE,
        "authored_only":True,"primary_paper_count":3,"measurement_guidance_count":1,
        "audit_inputs":audit_inputs,"preparation_script":{"path":"../prepare_packet.py","sha256":digest(Path(__file__))},
        "files":files,"approval_asserted":False,
        "manifest_excludes_own_hash":True})
    print(json.dumps({"status":"prepared_schema_valid_pending_root_admission","packet":str(PACKET),
                      "sources":len(sources),"items":len(ids),"files":len(files)+1}))

if __name__=="__main__":
    prepare()

