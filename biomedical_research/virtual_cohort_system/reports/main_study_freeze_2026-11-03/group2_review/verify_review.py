"""Independent read-only candidate checks and deterministic arithmetic.

No candidate code import/execution, random draws, table/clinical-record reads,
or target-reference access. Writes only this review's aggregate receipt.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
WORKSPACE = PROJECT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness import lifecycle


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, expected):
    assert math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-11), (actual, expected)


def bounds_beta(shapes):
    a, b = shapes
    assert a > 0 and b > 0
    mean = a / (a+b)
    variance = a*b / ((a+b)**2 * (a+b+1))
    return [-mean/math.sqrt(variance), (1-mean)/math.sqrt(variance)]


results = {}
for name in ("CHNS2009_E0_A02", "ENSANUT2018_E0_A01", "ENSANUT2018_E1_A01"):
    root = WORKSPACE / "evcMS" / name
    bundle = root / "bundle"
    candidate = bundle / "candidates/initial"
    frozen = lifecycle.verify_candidate(bundle, "candidates/initial")
    assert frozen["revision_index"] == 0 and frozen["parent"] is None
    task = read(bundle / "task.json")
    assert task["mode"] == "whole_cohort"
    decision = read(root / "decision.json")
    assert decision["candidate"] == "candidates/initial" and decision["action"] == "retain"
    links = decision.get("feedback_artifacts", [decision.get("feedback")])
    assert len(links) == 1 and links[0] is not None
    link = links[0]
    feedback_path = root / link["path"]
    assert sha(feedback_path) == link["sha256"]
    feedback = read(feedback_path)
    assert feedback["kind"] == "generated_only_main_feedback"
    assert feedback["run_id"] == link["run_id"] == "a01_trial_5201"
    semantic = feedback["semantic_feedback_v1"]
    assert semantic["candidate"] == "candidates/initial"
    assert semantic["output_link_verified"] is True
    assert semantic["n_computable"] == 0
    assert semantic["n_not_computable"] == len(semantic["checks"])
    for item in semantic["checks"]:
        assert item["semantic_status"] == "unavailable"
        assert item["calculation"] is None and item["difference"] is None
    generated = feedback["generated"]
    assert generated["n"] == 3000
    for item in generated["analyses"] + generated["diagnostics"]:
        assert item["status"] == "computed" and math.isfinite(item["value"])
    evidence = read(candidate / "evidence.json")
    source_evidence = read(bundle / "input/evidence.json")
    assert evidence["items"] == source_evidence["items"]
    items = {x["id"]: x for x in evidence["items"]}
    p = read(candidate / "model_spec.json")["parameters"]
    uptake = read(candidate / "numerical_uptake.json")["records"]
    result = {
        "lifecycle_verify_candidate": "passed",
        "candidate_freeze_sha256": sha(candidate / "freeze.json"),
        "decision_sha256": sha(root / "decision.json"),
        "feedback_sha256": sha(feedback_path),
        "feedback_hash_matches_decision": True,
        "evidence_items_equal_admitted_input": True,
        "target_source_comparisons_computable": 0,
        "target_source_comparisons_unavailable": len(semantic["checks"]),
        "own_trial_analyses_computed": len(generated["analyses"]),
        "own_trial_diagnostics_computed": len(generated["diagnostics"]),
        "own_trial_output_link_verified_as_recorded": True,
    }
    if name == "CHNS2009_E0_A02":
        assert uptake == []
        close(p["female_probability"], 2049/3547)
        v, first, second = {}, {}, {}
        for variable, prefix in (("bmi", "M_M_BMI"), ("glucose", "M_M_FSG"), ("hba1c", "M_M_HBA1C_PERCENT")):
            m, s = p["marginal_moments"][variable]["mean"], p["marginal_moments"][variable]["individual_sd"]
            close(m, items[prefix+"_MEAN"]["estimate"])
            close(s, items[prefix+"_SD"]["estimate"])
            v[variable] = math.log1p(s*s/(m*m))
            mu = math.log(m)-v[variable]/2
            first[variable] = math.exp(mu+v[variable]/2)
            second[variable] = math.exp(2*mu+2*v[variable])
            close(first[variable], m)
            close(second[variable], m*m+s*s)
        author = read(candidate / "analytic/moments.json")
        covariances = {}
        names = ["bmi", "glucose", "hba1c"]
        for i, left in enumerate(names):
            assert abs(p["factor_loadings"][left]) < 1
            for right in names[i+1:]:
                r = p["factor_loadings"][left]*p["factor_loadings"][right]
                value = first[left]*first[right]*math.expm1(r*math.sqrt(v[left]*v[right]))
                key = left+":"+right
                covariances[key] = value
                close(value, author["continuous_covariances"][key])
        result["arithmetic"] = {"first_moments": first, "second_raw_moments": second, "continuous_covariances": covariances, "female_probability": p["female_probability"], "finite_moment_argument": "Affine Gaussian log-exponents have E[X^k]=exp(k*mu+k^2*v/2); demographic support is finite. Strictly positive independent residual variances ensure nondegenerate continuous covariance."}
    elif name == "ENSANUT2018_E0_A01":
        assert uptake == []
        assert read(bundle / "input/source_operations.json")["non_marginal_operations"] == []
        b, g, h, ref = [p[x] for x in ("bmi", "glucose", "hba1c", "source_reference")]
        for value, evidence_id in ((b["mean"], "J_T1_bmi_mean_task"), (b["sd"], "J_T1_bmi_sd_task"), (g["reference_mean"], "J_T1_glucose_mean_mg_dL_derived"), (g["source_sd"], "J_T1_glucose_sd_mg_dL_derived"), (h["reference_mean"], "J_T1_hba1c_mean_pct"), (h["source_sd"], "J_T1_hba1c_sd_pct")):
            close(value, items[evidence_id]["estimate"])
        close(g["reference_mean"], 18*items["J_T1_glucose_mean_mmol_L"]["estimate"])
        close(g["source_sd"], 18*items["J_T1_glucose_sd_mmol_L"]["estimate"])
        width = b["upper"]-b["lower"]
        q = (b["mean"]-b["lower"])/width
        concentration = q*(1-q)/(b["sd"]/width)**2 - 1
        alpha, beta = q*concentration, (1-q)*concentration
        assert alpha > 0 and beta > 0 and p["residual_law"]["variance"] == 1
        rg2 = g["source_sd"]**2 - (g["age_per_year"]*ref["age_sd"])**2 - g["bmi_standardized_loading"]**2
        rh2 = h["source_sd"]**2 - (h["age_per_year"]*ref["age_sd"])**2 - h["bmi_standardized_loading"]**2 - h["shared_glucose_factor_loading"]**2
        assert rg2 > 0 and rh2 > 0
        z = [(b[x]-b["mean"])/b["sd"] for x in ("lower", "upper")]
        ages, signs = [25,79], [-1,1]
        radius = math.sqrt(6)
        gb = [g["reference_mean"] + g["age_per_year"]*(ages[i]-ref["age_mean"]) + g["bmi_standardized_loading"]*z[i] + signs[i]*math.sqrt(rg2)*radius for i in range(2)]
        hb = [h["reference_mean"] + h["age_per_year"]*(ages[i]-ref["age_mean"]) + h["bmi_standardized_loading"]*z[i] + signs[i]*(h["shared_glucose_factor_loading"]+math.sqrt(rh2))*radius for i in range(2)]
        assert gb[0] > 0 and gb[1] < 126 and hb[0] > 0
        author = read(candidate / "analytic_moments.json")
        for i in range(2):
            close(gb[i], author["target_law_support_bounds"]["glucose"][i])
            close(hb[i], author["target_law_support_bounds"]["hba1c"][i])
        close(alpha, author["beta_shapes"]["alpha"])
        close(beta, author["beta_shapes"]["beta"])
        result["arithmetic"] = {"beta_shapes": [alpha,beta], "residual_variances": [rg2,rh2], "glucose_support": gb, "hba1c_support": hb, "source_glucose_variance": rg2+(g["age_per_year"]*ref["age_sd"])**2+g["bmi_standardized_loading"]**2, "source_hba1c_variance": rh2+(h["age_per_year"]*ref["age_sd"])**2+h["bmi_standardized_loading"]**2+h["shared_glucose_factor_loading"]**2, "finite_moment_argument": "Finite demographic, scaled-beta and triangular supports; affine outcomes have bounded absolute moments of every finite order."}
    else:
        operations = read(bundle / "input/source_operations.json")["non_marginal_operations"]
        assert {x["operation_id"] for x in operations} == {x["operation_id"] for x in uptake}
        assert len(uptake) == 11
        assert sum(x["use"] == "model_constraint" for x in uptake) == 3
        assert sum(x["use"] == "context_only" for x in uptake) == 8
        m, c, lat = p["margins"], p["coefficients"], p["latent"]
        sb, sg, rho = m["bmi_sd"], m["glucose_sd"], lat["bmi_glucose_correlation"]
        kb = items["J_T2_bmi_slope_original"]["estimate"]*0.09148
        kg = items["J_T2_glucose_slope_original"]["estimate"]*0.09148/18
        a = items["P_NHANES_age_slope"]["estimate"]
        close(kb, items["J_T2_bmi_slope_task_derived"]["estimate"])
        close(kg, items["J_T2_glucose_slope_task_derived"]["estimate"])
        close(c["age"], a)
        b = (kb-kg*rho*sg/sb)/(1-rho*rho)
        g = (kg-kb*rho*sb/sg)/(1-rho*rho)
        close(b,c["bmi"])
        close(g,c["glucose"])
        va = p["source_contexts"]["lifelines"]["age_sd"]**2
        r2 = m["hba1c_source_sd"]**2-a*a*va-b*b*sb*sb-g*g*sg*sg-2*b*g*rho*sb*sg
        assert r2 > 0
        close(r2, c["residual_sd"]**2)
        cov = rho*sb*sg
        close(b+g*cov/(sb*sb), kb)
        close(g+b*cov/(sg*sg), kg)
        u,v,w = [bounds_beta(lat[x]) for x in ("bmi_beta", "glucose_beta", "hba1c_beta")]
        bb = [m["bmi_mean"]+sb*x for x in u]
        gb = [m["glucose_mean"]+sg*(rho*u[i]+math.sqrt(1-rho*rho)*v[i]) for i in range(2)]
        hb = [m["hba1c_mean"]+a*([25,79][i]-m["age_center"])+b*(bb[i]-m["bmi_mean"])+g*(gb[i]-m["glucose_mean"])+math.sqrt(r2)*w[i] for i in range(2)]
        assert bb[0] > 0 and gb[0] > 0 and gb[1] < 126 and hb[0] > 0
        author = read(candidate / "analytic_results.json")
        for key,path in (("generator_sha256",candidate/"generator.py"),("model_spec_sha256",candidate/"model_spec.json"),("source_operators_sha256",bundle/"input/source_operators.py"),("mathematical_properties_sha256",candidate/"mathematical_properties.md")):
            assert author["bindings"][key] == sha(path)
        context_checks = {}
        for context_name, context in p["source_contexts"].items():
            if context_name == "lifelines":
                age_mean, age_var = context["age_mean"], context["age_sd"]**2
            else:
                age_mean = context["age_shift"]+context["age_shape"]*context["age_scale"]
                age_var = context["age_shape"]*context["age_scale"]**2
            pf = context["female_probability"]
            # Direct latent transformation from independent A,F,U,V,W.
            transform = np.array([[1,0,0,0,0],[0,1,0,0,0],[0,0,sb,0,0],[0,0,sg*rho,sg*math.sqrt(1-rho*rho),0],[a,0,b*sb+g*sg*rho,g*sg*math.sqrt(1-rho*rho),math.sqrt(r2)]])
            sigma = transform @ np.diag([age_var,pf*(1-pf),1,1,1]) @ transform.T
            assert np.allclose(sigma, author["source_contexts"][context_name]["covariance"],rtol=1e-11,atol=1e-11)
            assert np.linalg.eigvalsh(sigma).min() > 0
            if context_name == "lifelines":
                projections = [float(np.linalg.solve(sigma[np.ix_(ids,ids)],sigma[ids,4])[0]) for ids in ([2,0,1],[3,0,1])]
                close(projections[0],kb)
                close(projections[1],kg)
            else:
                ids = [0,1,2,3]
                projections = [float(np.linalg.solve(sigma[np.ix_(ids,ids)],sigma[ids,4])[0])]
                close(projections[0],a)
            context_checks[context_name] = {"age_mean":age_mean,"age_variance":age_var,"hba1c_variance":float(sigma[4,4]),"minimum_covariance_eigenvalue":float(np.linalg.eigvalsh(sigma).min()),"separate_projection_values":projections}
        for i in range(2):
            close(gb[i],author["support"]["glucose"][i])
            close(hb[i],author["support"]["target_hba1c"][i])
        result["arithmetic"] = {"source_contexts":context_checks,"coefficients":{"age":a,"bmi":b,"glucose":g},"residual_variance":r2,"glucose_support":gb,"hba1c_target_support":hb,"operation_coverage":{"model_constraint":3,"context_only":8},"finite_moment_argument":"Target/Lifelines are affine transformations of bounded variables. Pani age is shifted Gamma(4,7.5), with finite first/second moments, entering HbA1c linearly; other variables are bounded."}
    result["finite_moments_checked"] = True
    result["numerical_uptake_checked"] = True
    results[name] = result

receipt = {"reviewer_id":"/root/main_review_g2","method":"Independent static inspection plus closed-form floating-point arithmetic; no random draws or quadrature", "generator_imported":False,"generator_executed":False,"row_tables_read":False,"target_results_used":False,"results":results}
(HERE / "verification.json").write_text(json.dumps(receipt, indent=2, allow_nan=False)+"\n",encoding="utf-8")
print(json.dumps({name:{"verify":"passed","freeze":r["candidate_freeze_sha256"],"decision":r["decision_sha256"],"source_unavailable":r["target_source_comparisons_unavailable"]} for name,r in results.items()},indent=2))
