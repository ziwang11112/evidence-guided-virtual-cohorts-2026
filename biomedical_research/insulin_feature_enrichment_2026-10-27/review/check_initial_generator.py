"""Source-only and toy-only audit. Never loads target reference or scores."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CANDIDATE = ROOT / "agent_clean" / "initial"
APPROVED = ROOT / "literature" / "approved"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_path, spec_path = CANDIDATE/"generator.py", CANDIDATE/"model_spec.json"
    source = source_path.read_text(encoding="utf-8")
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    parameters = spec["parameters"]
    tree = ast.parse(source)
    checks = []

    def check(name, condition, detail):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(name)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    check("imports_allowlist", set(imports) <= {"__future__", "numpy", "pandas"}, imports)
    forbidden = {"open", "eval", "exec", "compile", "__import__", "read_csv", "read_json",
                 "read_bytes", "read_text", "to_csv", "to_json", "write_bytes", "write_text",
                 "load", "save", "loadtxt", "savetxt", "urlopen", "request", "system", "popen"}
    called = [node.func.id if isinstance(node.func, ast.Name) else node.func.attr
              for node in ast.walk(tree) if isinstance(node, ast.Call)
              and isinstance(node.func, (ast.Name, ast.Attribute))]
    check("no_direct_io_or_dynamic_execution_calls", not set(called)&forbidden,
          "AST screen plus manual full-source review; procedural review, not a security sandbox")

    # These manually verified paper-table values are audit fixtures, not new
    # generator parameters and not target outcomes.
    ns = np.array([307, 168], dtype=float)
    bmi = np.array([21.07, 28.96])
    means = np.array([4.29, 6.05])
    sem = np.array([0.16, 0.37])
    sd = sem*np.sqrt(ns)
    log_variances = np.log1p((sd/means)**2)
    pooled_log_sd = float(np.sqrt(np.sum((ns-1)*log_variances)/np.sum(ns-1)))
    slope = float(np.log(means[1]/means[0])/(bmi[1]-bmi[0]))
    old_anchor = 6.37*47.0/42.1
    check("S1_age_insulin_medians", parameters["age_anchor_median_insulin"][:4] == [7.25,6.28,6.03,6.37],
          "S1 Table 2, approved text lines 269-310: marginal medians in microU/mL")
    check("S1_age_BMI_medians", parameters["age_anchor_bmi"][:4] == [22.58,22.83,23.01,23.07],
          "S1 Table 2: marginal BMI medians in kg/m^2")
    check("S2_older_ratio_arithmetic", np.isclose(parameters["age_anchor_median_insulin"][4], old_anchor, rtol=0, atol=1e-14),
          {"computed_anchor": old_anchor, "ratio":47/42.1, "interpretation":"Dimensionless median ratio; conditional transport remains assumption A2"})
    check("S3_source_sample_sizes_and_SE", spec["source_values_for_reproduction"]["S3_n"] == ns.tolist()
          and spec["source_values_for_reproduction"]["S3_insulin_sem"] == sem.tolist()
          and spec["source_values_for_reproduction"]["S3_insulin_mean"] == means.tolist()
          and spec["source_values_for_reproduction"]["S3_bmi_mean"] == bmi.tolist(),
          "S3 Table 1 is unadjusted mean +/- SE; Table 2 is explicitly age/sex adjusted")
    check("S3_between_group_slope_arithmetic", np.isclose(parameters["bmi_log_slope"], slope, rtol=0, atol=1e-14),
          {"computed_slope":slope, "interpretation":"Group arithmetic-mean contrast, not an individual regression coefficient"})
    check("S3_SE_to_SD_then_lognormal_pool_arithmetic", np.isclose(parameters["residual_log_sd"], pooled_log_sd, rtol=0, atol=1e-14)
          and np.allclose(spec["source_values_for_reproduction"]["S3_derived_log_sd"], np.sqrt(log_variances), rtol=0, atol=1e-14),
          {"raw_group_sd":sd.tolist(), "group_log_sd":np.sqrt(log_variances).tolist(), "pooled_log_sd":pooled_log_sd,
           "interpretation":"Correct moment-matching arithmetic; conditional residual interpretation remains assumption A5"})
    check("zero_sex_effect_labeled_assumption", parameters["female_log_effect"] == 0
          and any(a["id"] == "A4" and "does not establish" in a["description"] for a in spec["assumptions"]),
          "Reference-interval pooling does not establish a zero conditional association")
    check("fixed_parameter_uncertainty_disclosed", any(a["id"] == "A9" and "not proper multiple imputations" in a["description"] for a in spec["assumptions"]),
          "Repeated draws represent conditional simulation noise, not parameter or transport uncertainty")

    before = np.random.get_state()
    module_spec = importlib.util.spec_from_file_location("audit_initial_insulin_generator", source_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    toy = pd.DataFrame({"row_id":["toy_a","toy_b","toy_c","toy_d","toy_e","toy_f"],
                        "bmi":[18.5,23.,27.,31.,35.,45.], "age":[20,24.5,40,55,70,79], "sex":[1,2,1,2,1,2]})
    toy_before, evidence_before = toy.copy(deep=True), copy.deepcopy(spec)
    result = module.generate(toy, spec, 99821)
    repeated = module.generate(toy, spec, 99821)
    alternate = module.generate(toy, spec, 99822)
    pd.testing.assert_frame_equal(toy, toy_before, check_exact=True)
    check("input_dataframe_and_spec_unmutated", spec == evidence_before, "Toy frame checked with pandas exact equality; evidence deep-compared")
    check("output_schema_and_observed_cells", result.columns.tolist() == list(toy.columns)+["insulin"], "Exact columns and input order")
    pd.testing.assert_frame_equal(result[list(toy.columns)], toy, check_exact=True)
    check("positive_finite_toy_output", np.isfinite(result.insulin).all() and (result.insulin>0).all(), "Six arbitrary toy rows only")
    check("same_seed_reproducible", np.array_equal(result.insulin, repeated.insulin), "Independent local RNG")
    check("different_seed_changes_draw", not np.array_equal(result.insulin, alternate.insulin), "No model reconstruction implied")
    after = np.random.get_state()
    check("global_numpy_rng_unchanged", before[0] == after[0] and np.array_equal(before[1], after[1]) and before[2:] == after[2:], "Includes module import and three toy calls")
    nodes = np.asarray(parameters["age_nodes_years"])
    expected_log_median = np.interp(toy.age, nodes, np.log(parameters["age_anchor_median_insulin"]))
    expected_log_median += parameters["bmi_log_slope"]*(toy.bmi-np.interp(toy.age, nodes, parameters["age_anchor_bmi"]))
    expected_log_median += parameters["female_log_effect"]*(toy.sex == 2)
    expected = np.exp(expected_log_median+parameters["residual_log_sd"]*np.random.default_rng(99821).normal(size=len(toy)))
    check("documented_equation_matches_code", np.array_equal(result.insulin, expected), "No added unit conversion, scale offset, or alternate residual rule")
    for name, column, value in [("nonfinite_BMI","bmi",np.nan), ("nonpositive_BMI","bmi",-1),
                                ("out_of_range_age","age",80), ("invalid_sex","sex",3), ("duplicate_id","row_id","toy_b")]:
        invalid = toy.copy()
        invalid.loc[0,column] = value
        rejected = False
        try:
            module.generate(invalid, spec, 99821)
        except ValueError:
            rejected = True
        check("reject_"+name, rejected, "Contract guard on toy input")
    source_records = []
    for pmcid in ["PMC11554367","PMC10350850","PMC6887811","PMC8862500","PMC9165426","PMC8169863"]:
        matches = list(APPROVED.glob(pmcid+"_*.txt"))
        check("approved_source_present_"+pmcid, len(matches) == 1, "Read approved primary fulltext only")
        source_records.append({"pmcid":pmcid, "path":str(matches[0]), "sha256":sha(matches[0])})
    ledger_path = ROOT/"agent_clean"/"EVIDENCE_LEDGER.json"
    decision_path = ROOT/"agent_clean"/"INITIAL_DECISION.md"
    search_log_path = ROOT/"agent_clean"/"SEARCH_LOG.md"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8-sig"))
    records_by_pmcid = {entry["pmcid"]:entry for entry in source_records}
    check("ledger_source_ids_and_count", len(ledger["sources"]) == 6
          and {entry["pmcid"] for entry in ledger["sources"]} == set(records_by_pmcid),
          "Exactly the six approved primary studies reviewed")
    for entry in ledger["sources"]:
        check("ledger_file_commitment_"+entry["id"], sha(ROOT/entry["approved_path"]) == entry["sha256"]
              == records_by_pmcid[entry["pmcid"]]["sha256"], "Ledger path and hash bind the inspected approved fulltext")
    check("decision_and_search_record_present", decision_path.is_file() and search_log_path.is_file(),
          "Final decision and search records read manually; no target data read")
    report = {"scope":"Approved external source extraction and toy implementation only; no target outcomes, spine, or scores accessed",
              "model_version":spec["version"], "generator_sha256":sha(source_path), "model_spec_sha256":sha(spec_path),
              "all_checks_pass":all(c["passed"] for c in checks), "checks":checks, "sources":source_records,
              "scientific_status":"Explicit weak transport assumptions; not a fitted conditional prediction model",
              "ledger_status":"Reviewed; source values and roles consistent; two documentation clarifications identified",
              "evidence_ledger_sha256":sha(ledger_path), "initial_decision_sha256":sha(decision_path),
              "search_log_sha256":sha(search_log_path),
              "recommendation":"No numerical or structural model revision required before the pilot",
              "documentation_findings":[
                  {"id":"D1", "severity":"minor", "item":"S2 age60-80 source locator",
                   "finding":"Ledger locator606-672 excludes the age60-80 FI rows at674-684; numbers themselves are correct.",
                   "action":"Correct source locator; no model change."},
                  {"id":"D2", "severity":"interpretation", "item":"Latent concentration wording",
                   "finding":"Sources report measured assay distributions; no measurement-error model separates true concentrations from assay noise.",
                   "action":"Describe simulated positive concentrations on borrowed source assay scales, without an explicit target measurement/censoring model; no numerical correction is identified."}
              ]}
    (HERE/"initial_source_code_checks.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"checks":len(checks), "all_pass":report["all_checks_pass"], "generator_sha256":report["generator_sha256"], "model_spec_sha256":report["model_spec_sha256"]}))


if __name__ == "__main__":
    main()
