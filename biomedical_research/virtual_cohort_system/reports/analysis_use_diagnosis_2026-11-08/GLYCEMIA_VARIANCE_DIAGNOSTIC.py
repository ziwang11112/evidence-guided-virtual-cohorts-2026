"""Deterministic glycemia audit: frozen specifications + aggregate results only.

No generator import, random sampling, raw clinical/synthetic rows or clinical
reference refit. Existing references are exposed developmental comparisons.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
WORKSPACE = PROJECT.parents[1]
Q1 = PROJECT / "work/main_study_freeze_2026-11-03"
Q5 = PROJECT / "work/evidence_use_cross_task_2026-11-05"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def provenance(path):
    path = Path(path)
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def author_dir(author):
    return WORKSPACE / ("evcUse" + author)


def age_moments(bands):
    means = np.array([(lo + hi) / 2 for lo, hi in bands])
    variances = np.array([((hi-lo+1)**2-1)/12 for lo, hi in bands])
    mean = float(means.mean())
    return mean, float(np.mean(variances + (means-mean)**2))


def h03_budget():
    """Law-of-total-variance derivation independent of candidate execution."""
    path = author_dir("H03") / "candidates/initial/model_spec.json"
    p = read(path)["parameters"]
    d,b,g,h = [p[k] for k in ("design","bmi","glucose","hba1c")]
    am,av = age_moments(d["age_bands"])
    arm,arv = age_moments([h["reference_age_range"]])
    bv = b["sd"]**2; fv = .25
    ga,gb,gf = [g[k] for k in ("age_slope","bmi_slope","female_slope")]
    gv = g["sd"]**2
    g_explained = ga*ga*av + gb*gb*bv + gf*gf*fv
    g_residual = gv - g_explained
    concentration = (g["mean"]*(g["upper"]-g["mean"])-g_explained)/g_residual-1
    gm_ref = g["mean"] + ga*(arm-am)
    g_explained_ref = ga*ga*arv + gb*gb*bv + gf*gf*fv
    g_residual_ref = (gm_ref*(g["upper"]-gm_ref)-g_explained_ref)/(concentration+1)
    hrefv = ((h["reference_upper_quantile"]-h["reference_mean"])/h["normal_quantile_z"])**2
    ha,hbt,hft = [h[k] for k in ("age_slope","bmi_total_slope","female_total_slope")]
    rho = h["marginal_glucose_correlation"]
    # H variance across the full design equals the reference variance plus
    # the change in age and glucose-innovation components. BMI/sex cancel.
    delta_a = av-arv
    vpoly = np.array([hrefv+ha*ha*delta_a, 2*ha*ga*delta_a,
                      ga*ga*delta_a+g_residual-g_residual_ref])
    cov0 = ha*ga*av + hbt*gb*bv + hft*gf*fv
    cov1 = ga*ga*av + g_residual
    equation = np.array([cov1*cov1,2*cov0*cov1,cov0*cov0]) - rho*rho*gv*vpoly[::-1]
    candidates = np.roots(equation)
    valid = []
    for c in candidates:
        if abs(c.imag)>1e-12: continue
        c=float(c.real)
        vv=float(vpoly[0]+vpoly[1]*c+vpoly[2]*c*c)
        reference_explained = (ha+c*ga)**2*arv+hbt*hbt*bv+hft*hft*fv+c*c*g_residual_ref
        residual = hrefv-reference_explained
        if vv>0 and residual>0 and abs((cov0+cov1*c)/math.sqrt(gv*vv)-rho)<1e-10:
            valid.append((c,vv,residual,reference_explained))
    assert len(valid)==1
    c,hv,hrv,hex_ref=valid[0]
    components = {"age":(ha+c*ga)**2*av, "bmi":hbt*hbt*bv,
                  "female":hft*hft*fv, "glucose_innovation":c*c*g_residual,
                  "conditional_hba1c_innovation":hrv}
    assert abs(sum(components.values())-hv)<1e-12
    hb=hbt-c*gb; hf=hft-c*gf
    archived=read(author_dir("H03")/"candidates/initial/checks/independent_analytic_recheck.json")["actual"]
    comparisons={"age_mean":am,"age_variance":av,"glucose_beta_concentration":concentration,
                 "hba1c_glucose_coefficient":c,"hba1c_bmi_coefficient":hb,
                 "hba1c_female_coefficient":hf,"hba1c_conditional_variance":hrv,
                 "implied_marginal_hba1c_sd":math.sqrt(hv)}
    error=max(abs(value-archived[key]) for key,value in comparisons.items())
    assert error<1e-10
    return {"scope":"deterministic authored-law implications; no empirical or clinical fit",
            "age_mean":am,"age_variance":av,"reference_age_mean":arm,"reference_age_variance":arv,
            "bmi_variance":bv,"glucose_marginal_variance":gv,
            "glucose_conditional_mean_variance":g_explained,"glucose_expected_conditional_variance":g_residual,
            "glucose_beta_concentration":concentration,"reference_glucose_mean":gm_ref,
            "reference_glucose_expected_conditional_variance":g_residual_ref,
            "normal_shape_derived_reference_hba1c_variance":hrefv,
            "normal_shape_derived_reference_hba1c_sd":math.sqrt(hrefv),
            "reference_hba1c_explained_variance":hex_ref,
            "hba1c_conditional_variance":hrv,"hba1c_conditional_sd":math.sqrt(hrv),
            "whole_design_hba1c_variance_components":components,
            "whole_design_hba1c_variance":hv,"whole_design_hba1c_sd":math.sqrt(hv),
            "whole_design_hba1c_mean":h["reference_mean"]+(ha+c*ga)*(am-arm),
            "law_coefficients":{"Q1_age10":10*ha,"Q2_bmi5":5*hbt,"Q3_bmi5":5*hb,
                                "conditional_glucose_per_mg_dL":c,"conditional_female":hf,
                                "Q2_minus_Q3_bmi5":5*c*gb},
            "law_marginal_glucose_hba1c_correlation":(cov0+cov1*c)/math.sqrt(gv*hv),
            "Kerman_hba1c_sd_context_only":.73,
            "matches_archived_pre_target_algebra_max_abs_difference":error,
            "interpretation":"Residual variance is explicitly reference marginal variance minus explained variance. No marginal/residual mix-up found. The narrow outcome scale follows a normal-shape quantile approximation and cross-source transfer choices; the full beta-mixture quantile is not proved to equal its source anchor."}


def h02_budget():
    p=read(author_dir("H02")/"candidates/initial/model_spec.json")["parameters"]
    am,av=age_moments(p["age_bands"])
    aa,bb=p["bmi_alpha"],p["bmi_beta"]
    width=p["bmi_upper"]-p["bmi_lower"]
    bm=p["bmi_lower"]+width*aa/(aa+bb)
    bv=width**2*aa*bb/((aa+bb)**2*(aa+bb+1))
    ga,gf,gb=[p["glucose_"+k+"_coefficient"] for k in ("age","female","bmi")]
    gm=p["glucose_center"]+ga*(am-p["age_center"])+gf*.5+gb*(bm-p["bmi_center"])
    vmg=ga*ga*av+gf*gf*.25+gb*gb*bv
    vg_res=((gm-p["glucose_lower"])*(p["glucose_upper"]-gm)-vmg)/(p["glucose_precision"]+1)
    ha,hf,hb,hg=[p["hba1c_"+k+"_coefficient"] for k in ("age","female","bmi","glucose")]
    components={"age":(ha+hg*ga)**2*av,"female":(hf+hg*gf)**2*.25,
                "bmi":(hb+hg*gb)**2*bv,"glucose_innovation":hg*hg*vg_res,
                "conditional_hba1c_innovation":p["hba1c_residual_sd"]**2}
    return {"scope":"deterministic authored-law implications", "bmi_mean":bm,"bmi_sd":math.sqrt(bv),
            "glucose_mean":gm,"glucose_sd":math.sqrt(vmg+vg_res),
            "hba1c_variance_components":components,"hba1c_sd":math.sqrt(sum(components.values())),
            "conditional_hba1c_sd":p["hba1c_residual_sd"],
            "law_coefficients":{"Q1_age10":ha*10,"Q2_bmi5":5*(hb+hg*gb),"Q3_bmi5":5*hb}}


def rows(path):
    with Path(path).open(newline="",encoding="utf8") as stream:
        return list(csv.DictReader(stream))


def source_original_check():
    bundle=author_dir("H03"); e=read(bundle/"candidates/initial/evidence.json")
    result=[]
    for sid in ("PMC2551641","PMC3075530"):
        src=next(s for s in e["sources"] if s["id"]==sid)
        artifact=src["artifacts"][0]; path=bundle/artifact["path"]
        assert provenance(path)["sha256"]==artifact["sha256"]
        xml=ET.fromstring(path.read_text(encoding="utf8"))
        extracted=[]
        for tab in xml.iter("table-wrap"):
            label=" ".join("".join(x.itertext()) for x in tab.findall("label"))
            if "1" not in label:continue
            for row in tab.iter("tr"):
                text=" | ".join("".join(x.itertext()).strip() for x in row)
                if sid=="PMC2551641" and "50–54" in text or sid=="PMC3075530" and any(text.startswith(x) for x in ("BMI |","FBS |","A1c |","Self-reported diabetes |")):
                    extracted.append(text)
        result.append({"source_id":sid,"table":"Table 1","rows":extracted,"provenance":provenance(path)})
    return result


def age_profile_analysis():
    bundle=author_dir("H03")
    ep=bundle/"candidates/initial/evidence.json"
    e=read(ep)
    by_id={x["id"]:x for x in e["items"]}
    artifact=next(x for x in e["sources"] if x["id"]=="PMC2551641")["artifacts"][0]
    original=bundle/artifact["path"]
    assert provenance(original)["sha256"]==artifact["sha256"]
    age_labels=["25-39 (source >=25 and <40)","40-44","45-49","50-54","55-59","60-64","65-69",">=70 (not restricted to79)"]
    # Exact moments of H03's declared law restricted to each age bin, with
    # its own equal-sex design and invariant BMI distribution. These are
    # not a replay of source survey weights or source covariate mixtures.
    spec=read(bundle/"candidates/initial/model_spec.json")["parameters"]
    b,g,h=[spec[k] for k in ("bmi","glucose","hba1c")]
    budget=h03_budget()
    c=budget["law_coefficients"]["conditional_glucose_per_mg_dL"]
    age_coefficient=h["age_slope"]+c*g["age_slope"]
    bands=[(25,39),(40,44),(45,49),(50,54),(55,59),(60,64),(65,69),(70,79)]
    xml=ET.fromstring(original.read_text(encoding="utf8"))
    table=next(t for t in xml.iter("table-wrap") if t.attrib.get("id")=="t1")
    original_rows=list(table.find("table/tbody"))
    records=[]
    for i,label in enumerate(age_labels):
        m_id="E_h_ref_mean" if i==3 else f"E_nh_mean_{i}"
        q_id="E_h_ref_q" if i==3 else f"E_nh_q_{i}"
        mean,quantile=by_id[m_id],by_id[q_id]
        am,av=age_moments([bands[i]])
        gm=g["mean"]+g["age_slope"]*(am-budget["age_mean"])
        gmv=g["age_slope"]**2*av+g["bmi_slope"]**2*b["sd"]**2+g["female_slope"]**2*.25
        g_res=(gm*(g["upper"]-gm)-gmv)/(budget["glucose_beta_concentration"]+1)
        hm=h["reference_mean"]+age_coefficient*(am-budget["reference_age_mean"])
        hv=(age_coefficient**2*av+h["bmi_total_slope"]**2*b["sd"]**2+
            h["female_total_slope"]**2*.25+c*c*g_res+budget["hba1c_conditional_variance"])
        source_cells=["".join(cell.itertext()).strip() for cell in original_rows[i]]
        records.append({"age_coverage":label,"mean":mean["estimate"],"q975":quantile["estimate"],
                        "evidence_ids":[m_id,q_id],"source_locator":mean["locator"],
                        "exact_original_locator":{"table_id":"t1","table":"Table 1","tbody_row_one_based":i+1,
                                                   "column_group":"NHANES nondiabetic subjects","mean_column":9,"q975_column":10,
                                                   "original_row_label":source_cells[0],"source_n":int(source_cells[7].replace(",","")),
                                                   "original_mean_plus_minus_SE":source_cells[8],"unit":"HbA1c percentage points"},
                        "normal_shape_implied_sd_not_reported_sd":(quantile["estimate"]-mean["estimate"])/1.959963984540054,
                        "H03_exact_declared_age_bin_moments":{"ages":list(bands[i]),"mean":hm,"variance":hv,"sd":math.sqrt(hv),
                                                              "mean_minus_source_mean":hm-mean["estimate"],
                                                              "normal_approximation_q975_not_exact_beta_mixture_quantile":hm+1.959963984540054*math.sqrt(hv),
                                                              "comparison_scope":"H03 equal-sex uniform-age-bin design with its unchanged BMI distribution; source survey weighting/covariate mix not reproduced"},
                        "current_H03_role":"fitted_reference_pair" if i==3 else "context_or_check_only"})
    return {"id":"GLY-Q5-AVAILABLE-AGE-PROFILE","case":"Q5 H03, existing Pani source",
            "analysis":"Age-stratified HbA1c location and upper-tail scientific use",
            "observed_result":{"approved_packet_has_all_eight_mean_quantile_pairs":True,"source_cells":records,
                               "generated_age_stratum_quantiles_evaluated_in_this_audit":False},
            "evidence_status":{"reported":"Eight source age-bin weighted HbA1c means and97.5th percentiles; original mean+/-SE, never SD",
                               "derived":"Under a normal-shape working assumption, implied marginal SD ranges.25511–.35205 across bins. This is neither directly reported residual SD nor a uniquely identified variance.",
                               "assumed":"Shape, within-bin predictor distribution, matching source survey weights, and transport to Mexican equal-cell design; oldest source bin includes ages above79. Exact H03 law moments below are not strict source replay. Displayed H03 q97.5 uses a normal approximation and is not the exact quantile of its conditional beta mixture."},
            "supported_use":"There is already permitted age-specific location/tail evidence that a new source-driven candidate could use, independent of exposed target values.",
            "unsupported_use":"Does not prove heteroscedastic residuals, improved target utility or that fitting all source quantiles is compatible with the separately transported adjusted age/BMI/glucose effects.",
            "diagnosis":{"category":"available_source_profile_not_fitted_by_current_candidate","confidence":"high for availability/non-use; improvement untested",
                         "reason":"H03 takes only the50–54 pair to set a constant conditional variance; its metadata expressly leaves other pairs as context/check-only. This is a deliberate evidence-selection/model-completion choice, not code failure or missing data access.",
                         "alternatives":["Rounded quantiles and sampling uncertainty may explain age differences","Different predictor mix by age may account for marginal variation without conditional heteroscedasticity","Source tail shape need not be normal"]},
            "smallest_followup":"A bounded deterministic candidate-design check: ask an Agent to jointly honor the existing eight source mean/quantile pairs under an explicit shape and source-population design, retain the original adjusted operators, and show nonnegative within-age residual budgets. If compatible, freeze a new model before any new sampling; first evaluate source-profile fit, not promise to close exposed ENSANUT SD discrepancy. Do not force >=70 source to equal70–79 target without declaring transport.",
            "provenance":[provenance(ep),provenance(original),provenance(bundle/"candidates/initial/model_spec.json"),
                          provenance(bundle/"candidates/initial/generator.py")]}


def main():
    h03=h03_budget(); h02=h02_budget()
    q1rows=rows(Q1/"final_evaluation/ALL_ENDPOINTS.csv")
    q5rows=rows(Q5/"evaluation/ALL_ENDPOINTS.csv")
    def q1(case,endpoint):
        result={}
        for arm in ("E0","E1"):
            rr=[r for r in q1rows if r["case_id"]==case and r["information_condition"]==arm and
                r["constructor_kind"]=="agent" and r["category"]=="analyses" and r["id"]==endpoint]
            authors={r["constructor_id"] for r in rr}
            result[arm]={"sample_reference":float(rr[0]["reference_value"]),"unit":rr[0]["unit"],
                         "n_constructors":len(authors),"n_seeded_outputs":len(rr),
                         "mean_absolute_native_difference":float(np.mean([float(r["absolute_discrepancy"]) for r in rr])),
                         "constructor_means":{a:float(np.mean([float(r["value"]) for r in rr if r["constructor_id"]==a])) for a in sorted(authors)}}
        return result
    def q5(endpoints):
        result={}
        for a in ("H01","H02","H03"):
            result[a]={}
            for endpoint in endpoints:
                rr=[r for r in q5rows if r["author_id"]==a and r["endpoint"]==endpoint]
                if not rr:continue
                values=[float(r["generated_value"]) for r in rr]
                result[a][endpoint]={"values":values,"seeds":[int(r["seed"]) for r in rr],
                                     "mean":float(np.mean(values)),"min":min(values),"max":max(values),
                                     "reference":float(rr[0]["reference_value"]) if rr[0]["reference_value"] else None,
                                     "unit":rr[0]["unit"]}
        return result
    def p1(case):
        return [provenance(Q1/"final_evaluation/ALL_ENDPOINTS.csv"),
                provenance(Q1/"cases"/case/("E1_evidence.json" if case=="CHNS2009" else "E1.json"))]
    def p5(*authors):
        files=[Q5/"evaluation/ALL_ENDPOINTS.csv"]
        for a in authors:
            files += [author_dir(a)/"candidates/initial"/name for name in ("evidence.json","model_spec.json","generator.py","whole_cohort_feedback.json")]
        return [provenance(x) for x in files]
    analyses=[]
    def add(id,case,analysis,observed,evidence,supported,unsupported,category,confidence,reason,alternatives,followup,prov):
        analyses.append({"id":id,"case":case,"analysis":analysis,"observed_result":observed,
                         "evidence_status":evidence,"supported_use":supported,"unsupported_use":unsupported,
                         "diagnosis":{"category":category,"confidence":confidence,"reason":reason,"alternatives":alternatives},
                         "smallest_followup":followup,"provenance":prov})
    add("GLY-Q1-CHNS-BMI","Q1 CHNS2009","HbA1c~BMI+age+sex, BMI coefficient",q1("CHNS2009","E1"),
        {"reported":"Jansen source BMI coefficient0.13 mmol/mol per BMI unit adjusted age/sex", "derived":"NGSP scale0.09148 gives0.0118924 percentage points per BMI unit", "assumed":"Transfer from selected Lifelines to Chinese35–74 sample; joint predictor structure and source-to-target shift"},
        "All frozen outputs permit the requested regression; E1 has positive coefficients but larger mean discrepancy than E0.",
        "Cannot claim quantitative preservation or that more relational evidence always improves the target analysis.",
        "source_population_transport_and_completion","high for declared assumptions; target cause unresolved",
        "E1 mean absolute difference increases0.0203795→0.0315574. Several constructors intentionally use a much smaller source slope. This is not evidence of a coding error; E0 closeness can be assumption-dependent coincidence.",
        ["Source/target selection or measurement differs","Chosen target completion changes the source projection","Finite reference uncertainty"],
        "Audit each adopted source projection against its own declared context; only repair a source/operator inconsistency if found. Do not change slope toward revealed CHNS value.",p1("CHNS2009"))
    add("GLY-Q1-CHNS-GLUCOSE","Q1 CHNS2009","HbA1c~glucose+age+sex, glucose coefficient",q1("CHNS2009","E2"),
        {"reported":"Jansen separately adjusted glucose slope2.29 IFCC/mmolL; Bao Pearson.619; MIND Spearman.529", "derived":"Jansen conversion.2094892 percentage points/mmolL; copula conversions and other source equations are construction-specific", "assumed":"Assay/plasma-serum and population/selection transfer; unreported joint dependence"},
        "E1 yields smaller developmental reference discrepancy for this prespecified analysis:0.1340185→0.0240792.",
        "Does not identify which source/structural choice caused improvement or establish universal transport, clinical interchangeability or all-model superiority.",
        "quantitative_evidence_use_with_unresolved_transport","high for empirical difference; moderate/low for mechanism",
        "All E1 authors use at least one numerical relation, but multiple sources and laws change; no single causal mechanism is isolated.",
        ["Source marginal scale transfer drives apparent fit","Copula/rank-to-linear relationship matters","Reference uncertainty"],
        "Preserve this favorable endpoint with the full constructor range; use source-law operator checks rather than adding new target-fitted calibration.",p1("CHNS2009"))
    a03=WORKSPACE/"evcMS/CHNS2009_E1_A03/bundle/candidates/initial"
    add("GLY-Q1-CHNS-AGE","Q1 CHNS2009","Age coefficient in HbA1c~age+sex+BMI+glucose",q1("CHNS2009","E3"),
        {"reported":"No matched fully adjusted age coefficient in this E1 packet", "derived":"Under A03 demography independent of all biomarkers, the population conditional-age coefficient is exactly0", "assumed":"Other authors assign age relationships; source summaries do not identify the requested partial coefficient"},
        "E1 average discrepancy decreases, but directions depend on construction; A03 has mean−0.00050934 against positive sample reference.00810704.",
        "A03 negative finite-seed estimate is not demonstrated biological reversal; all-author preservation of age association is unsupported.",
        "explicit_unidentified_relationship_completion","high",
        "A03 specification A_DEMOGRAPHY explicitly sets age independent of biomarkers; generator implements it. The missing relationship is a declared zero-association assumption, not an accidental omission proved by target mismatch.",
        ["Finite draws explain A03 small departure from its zero population coefficient","Other authors impose different unverified age models"],
        "Tag age association assumption-dependent before generation. A new nonzero age law needs independent matching source evidence; changing A03 because target age is positive is not justified.",p1("CHNS2009")+[provenance(a03/"model_spec.json"),provenance(a03/"generator.py")])
    add("GLY-Q1-ENSANUT","Q1 ENSANUT2018","Age/BMI regressions before and after glucose adjustment",
        {x:q1("ENSANUT2018",x) for x in ("Q1_age10","Q2_bmi5","Q3_bmi5")},
        {"reported":"E1 adds NHANES fully adjusted age.01pp/year and Lifelines separately adjusted BMI/glucose coefficients", "derived":"Age.1pp/decade; BMI.059462pp/5BMI units; joint coefficients require unreported BMI-glucose covariance and completion", "assumed":"Transfer across countries, assays and selected populations; fixed eight-cell design; latent dependence"},
        "All three prespecified discrepancies fall with E1. Direction and effect magnitude can be displayed analysis by analysis.",
        "No exact target recovery; E1 conditional-BMI means.024997–.042091 are below reference.056638; age means cluster near transferred.1 rather than reference.07513.",
        "source_supported_projection_with_assumed_joint_structure","high for implementation/use; transport not identified",
        "Static laws numerically incorporate reported relationships. The conditional-BMI task is not directly reported in the same source adjustment set; its completion depends on covariances and specification.",
        ["Population/selection changes source slopes","Unreported predictor covariance changes partial slopes","Finite reference uncertainty"],
        "Report a joint-moment/source-operator compatibility diagnostic. The completed artificial necessity test shows ordinary agents can solve complete exact moments; do not assume an extra instruction component repairs clinical transport.",p1("ENSANUT2018"))
    add("GLY-Q5-PARTIAL-SLOPES","Q5 H01/H02/H03","Fully adjusted age and BMI analyses",q5(["Q1_age10","Q2_bmi5","Q3_bmi5","Q2_minus_Q3_bmi5"]),
        {"reported":"Pani age.01/year; Finnish BMI.0125 and glucose-BMI.0240 on inferred outcome units; Kerman marginal r.23 and individual SD(H).73,SD(G)12.4", "derived":"H01/H02 use marginal r*SDH/SDG=.0135403 as conditional G slope by explicit assumption; H03 solves cross-source marginal moments, conditionalG=.00280395", "assumed":"Each marginal-to-conditional/measurement/population bridge; source original weights/adjustment differences"},
        "All nine author-mean requested coefficients have reference direction; their magnitudes and attenuation patterns differ substantially. H03 conditional-BMI mean is.050978 vs reference.056638.",
        "No general valid-data label, no proof one author is best across uses, no causal mediation interpretation of Q2−Q3.",
        "different_declared_marginal_to_conditional_completions","high for algebra; target cause not established",
        "The distinct conditional glucose slopes explain why H03 preserves much more of BMI's total coefficient after glucose adjustment. H01/H02 explicitly treat a marginal source slope as a conditional working slope; this is not an unnoticed extraction identity.",
        ["Actual target conditional glucose association differs","Source selection/units/fasting-duration mismatches","Different BMI-glucose joint distributions"],
        "Expose marginal-vs-conditional status in the use map; require compatible adjustment sets for exact checks. Smallest future test compares authored source-context projections, keeping target values out of construction.",p5("H01","H02","H03"))
    add("GLY-Q5-HBA1C-DISPERSION","Q5 H01/H02/H03; H03 focus","Marginal HbA1c SD and adjusted residual RMS",
        {"outputs":q5(["hba1c.mean","hba1c.sd_population","q1_residual_rms"]),"H03_deterministic_budget":h03,"H02_deterministic_budget":h02,
         "H01_exact_conditional_sd":.35},
        {"reported":"Pani age50–54 NHANES mean5.40±SE.02 and97.5th percentile6.0; Kerman marginal SD.73", "derived":"H03 assumes normal shape to convert(6−5.4)/1.95996 into reference marginalSD.306128, subtracts explained variation and obtains residualSD.300047", "assumed":"Normal-shape quantile inversion; reference-age joint covariates; transfer to equal-cell target; constant conditional variance. H01/H02 residualSD.35/.40 explicitly assumed. Kerman HbA1cSD.73 is H03 context/check-only."},
        "Existing outputs agree with the authored narrow-dispersion laws; this supports implementation consistency and reveals an unresolved distributional-use limit.",
        "Does not support target residual variance, tail risk, sample-size/power or precision calculations as interchangeable with real data. Does not prove true source SD must equal target SD.",
        "declared_dispersion_and_transport_assumption_not_detected_code_error","high for variance accounting; biological cause unresolved",
        "H03 total variance is the sum of explicit age/BMI/sex/glucose/innovation components. Archived pre-target algebra already predictedSD.351616 and residualSD.300047; actualSD.350313–.353734 andRMS.299835–.301468 follow this. Narrowness is not a wrong SD-to-SE conversion or residual subtraction bug. A source quantile plus mean does not identify SD without shape assumptions, and a beta-mixture is not exactly normal.",
        ["Assumed reference shape yields incorrect source dispersion","NHANES-to-ENSANUT transport changes biological/assay variation","Age/sex/BMI and selection mixture differs","Unmodeled HbA1c determinants"],
        "Keep old model. Add a source-derived variance budget to new candidate review and distinguish fitted marginal, residual and check-only scales. No numeric repair is warranted from these data alone; next discriminating step is an applicable independently reported conditional/residual scale or source-context quantile check with declared weighting, not raising noise toward.488478.",p5("H01","H02","H03")+[provenance(author_dir("H03")/"candidates/initial/checks/independent_analytic_recheck.json")])
    add("GLY-Q5-PREDICTOR-DISPERSION","Q5 H01/H02/H03","BMI/glucose marginal means and SDs",q5(["bmi.mean","bmi.sd_population","glucose.mean","glucose.sd_population"]),
        {"reported":"Kerman BMImean24.5 SD3.8, glucosemean91.2 SD12.4; PaniBMImean28.01", "derived":"H03 matches transferred BMI variance14.44 and glucose variance153.76 through exact beta moment allocation", "assumed":"H03 combines NHANES location with Kerman BMI scale; H01BMI SD5 and H02beta shape imply different dispersions; independence from age/sex chosen"},
        "H03 glucose location/scale and BMI scale are implemented as specified; different authors offer explicit hypothetical predictor populations.",
        "H03 BMI distribution is not a faithful ENSANUT dispersion proxy: final SD3.784–3.823 vs reference5.521. No universal distributional adequacy inferred from glucose mean agreement.",
        "cross_source_location_scale_transfer","high for implementation; transport uncertain",
        "H03 intentionally transports only KermanBMI SD while not its mean; the source profile is not reconstructed by this hybrid. This differs from a coding loss of variability.",
        ["True Mexican target composition differs from Kerman","Different obesity-tail/selection structure","Published source marginal estimates have uncertainty"],
        "Label location and scale source identities separately and require source-specific checks before claiming a reproduced population. A broader target BMI scale cannot be inserted merely to improve the exposed reference.",p5("H01","H02","H03"))
    analyses.append(age_profile_analysis())
    assert len(analyses)<=8
    inventory=[]
    for case in ("CHNS2009","ENSANUT2018"):
        for arm in ("E0","E1"):
            for b in sorted((WORKSPACE/"evcMS").glob(case+"_"+arm+"_A*")):
                candidate=b/"bundle/candidates/initial"
                spec=read(candidate/"model_spec.json")
                code=(candidate/"generator.py").read_text(encoding="utf8")
                inventory.append({"constructor":b.name,"parameter_keys":list(spec.get("parameters",{})),
                                  "review_scope":"Static source/spec/program inventory; not a full law-by-law mathematical verification",
                                  "provenance":[provenance(candidate/"model_spec.json"),provenance(candidate/"generator.py")]})
    report={"schema_version":1,"created_utc":datetime.now(timezone.utc).isoformat(),
            "scope":"Analysis-use diagnostic of existing exposed Q1/Q5 glycemia cases; no fresh validation",
            "analyses":analyses,"Q1_constructor_inventory":inventory,
            "H03_original_table_checks":source_original_check(),
            "H03_variance_budget":h03,"H02_variance_budget":h02,
            "hard_coding_assessment":"No scientific parameter change made. Diagnoses distinguish explicit Agent-selected assumptions from code/spec inconsistency. Target discrepancies are not used as replacement parameters.",
            "repair_decision":{"numeric_generator_repair_warranted":False,
                               "reason":"No H03 variance-accounting/code defect found; H01/H02 residual scales and marginal-to-conditional bridge are explicit assumptions. Correctlaw does not mean applicablelaw. An eight-bin Pani mean/quantile profile is already available and could justify a new source-profile completion design, but improved target utility remains untested.",
                               "framework_improvement":"Before any new generation, require a use-specific variance and covariance budget tied to stated source populations, and mark assumed scales/unavailable estimators. This diagnostic is useful regardless of target values; it is not a proven new algorithm or superiority result.",
                               "do_not":"Do not tune old exposed target means/slopes/SDs, relabel unsupported strict source feedback as source fit, or require every reference mismatch to be repaired."},
            "statistical_limits":["No new usability threshold was added; reference estimates are sample quantities, not known population truth.",
                                  "Same frozen data can agree on one association and fail on dispersion; agreement is endpoint-specific.",
                                  "Repeated seeds measure conditional generation variability, not transport/parameter uncertainty.",
                                  "All Q5 strict source comparisons were unavailable for original estimator definitions; the custom deterministic budgets check authored assumptions, not certified source replay."],
            "execution":{"generator_imports":0,"generated_tables":0,"patient_rows_read":0,"reference_refits":0,"frozen_files_modified":0},
            "provenance":[provenance(__file__),provenance(Q1/"RESULTS.md"),provenance(Q5/"RESULTS.md")],
            "next_decision":"Retain analysis-specific favorable results with native magnitudes. A bounded new design may use the already-approved age-specific Pani profile, first checking source/adjustment compatibility. Do not tune noise to the exposed H03 target or add a reconciliation component merely because that target has broader dispersion."}
    destination=ROOT/"GLYCEMIA_AUDIT.json"
    with destination.open("x",encoding="utf8") as stream:
        json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write("\n")
    print(json.dumps({"analyses":len(analyses),"H03":h03,"H02":h02},indent=2))


if __name__=="__main__":main()
