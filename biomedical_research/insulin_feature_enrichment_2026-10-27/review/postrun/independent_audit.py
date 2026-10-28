"""Read-only, independently implemented post-release numerical audit.

Never imports or executes the generator, evaluator, or presentation code.
Writes aggregate audit artifacts only beside this file. No row data are emitted.
"""
from __future__ import annotations

import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import t

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
checks = []
hash_checks = []
numeric_errors = {}


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(name, passed, detail=None):
    checks.append({"check": name, "passed": bool(passed), "detail": detail})
    if not passed:
        save("FAILED; no comparison authorization", error=name)
        raise AssertionError(name)


def save(status, **extra):
    result = {"utc": datetime.now(timezone.utc).isoformat(), "status": status,
              "scope": "Independent read-only postrun audit; no generator execution; aggregate outputs only",
              "checks": checks, "hash_checks": hash_checks,
              "maximum_absolute_errors": numeric_errors, **extra}
    (OUT / "audit_results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def hash_check(path, expected, origin, expected_bytes=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    passed = path.is_file() and sha(path) == expected
    if expected_bytes is not None:
        passed = passed and path.stat().st_size == expected_bytes
    hash_checks.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"),
                        "origin": origin, "sha256": expected, "passed": bool(passed)})
    require("file commitment " + str(path.relative_to(ROOT)) + " in " + origin, passed)


def close(name, actual, expected, atol=1e-10, rtol=1e-10, category="other"):
    a, b = np.asarray(actual, float), np.asarray(expected, float)
    error = float(np.max(np.abs(a-b))) if a.size else 0.
    numeric_errors[category] = max(numeric_errors.get(category, 0.), error)
    require(name, a.shape == b.shape and np.allclose(a, b, atol=atol, rtol=rtol),
            {"max_absolute_error": error, "absolute_tolerance": atol, "relative_tolerance": rtol})


def table(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames


def array(rows, column):
    return np.array([float(r[column]) for r in rows])


def verify_hashes():
    freeze = read_json("freeze_v1/outputs_freeze.json")
    hash_check("freeze_v1/outputs_freeze.json", "aee9d3b44df52b59a754cdcfd88629eddf414f4e8b2c7e23c4ce102ba271f4c4", "audit task external commitment")
    for filename in ("freeze_v1/outputs_freeze.json", "runs/initial_v1/pre_execution.json"):
        for path, digest in read_json(filename)["files"].items():
            hash_check(path, digest, filename)
    execution = read_json("runs/initial_v1/execution.json")
    for path, digest in execution["input_files"].items():
        hash_check(path, digest, "execution input_files")
    for filename in ("custodian/locked/freeze_manifest.json", "custodian/locked/evaluator_adapter_manifest.json"):
        for record in read_json(filename)["files"]:
            hash_check(record["path_relative_to_pilot"], record["sha256"], filename, record["bytes"])
    source = read_json("custodian/source_manifest.json")
    for record in source["sources"]:
        hash_check(Path("custodian") / record["file"], record["sha256"], "custodian/source_manifest.json", record["bytes"])
    for line in (ROOT / "literature/audit.jsonl").read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        if "approved_artifact" in entry:
            record = entry["approved_artifact"]
            hash_check(record["path"], record["sha256"], "literature approved artifact", record["bytes"])
    for record in read_json("agent_clean/EVIDENCE_LEDGER.json")["sources"]:
        hash_check(record["approved_path"], record["sha256"], "evidence ledger")
    pre = read_json("custodian/locked/pre_read_freeze.json")
    hash_check("custodian/eligibility_frozen.json", pre["eligibility_sha256"], "pre_read_freeze")
    hash_check("custodian/build_packet_initial_parser_failure.py", pre["build_script_sha256"], "preserved pre-repair code commitment")
    adapter = read_json("custodian/locked/evaluator_adapter_manifest.json")
    hash_check("custodian/locked/freeze_manifest.json", adapter["original_freeze_manifest_sha256"], "adapter")
    spec = read_json("review/frozen_analysis.json")
    for field, path in (("base_spec_sha256", "review/analysis_spec.json"), ("evaluator_sha256", "review/evaluate.py"), ("observed_sha256", "shared/observed.csv")):
        hash_check(path, spec[field], "frozen_analysis")
    manifest = read_json("freeze_v1/evaluation_manifest.json")
    for field, path in (("observed_sha256", "shared/observed.csv"), ("reference_sha256", "custodian/locked/evaluator_reference.csv"), ("spine_sha256", "custodian/locked/evaluator_design_spine.csv")):
        hash_check(path, manifest[field], "evaluation_manifest")
    for field in ("analysis_spec", "outputs_freeze"):
        record = manifest[field]
        hash_check(record["path"], record["sha256"], "evaluation_manifest " + field)
    for origin, records in (("execution", execution["draws"]), ("evaluation_manifest", manifest["draws"])):
        for record in records:
            hash_check(record["path"], record["sha256"], origin)
    return freeze, manifest, execution, spec


def rcs(x, knots):
    # Equivalent divided-difference basis, evaluated separately from evaluator.
    x = np.asarray(x)
    a, b, c = knots
    h = lambda k: np.clip(x-k, 0, None)**3
    return ((h(a)-h(c))/(c-a) - (h(b)-h(c))/(c-b))/(c-a)


def independent_fit(X, y, w, domain_rows, spine_rows):
    # QR on sqrt-weighted X avoids the evaluator's normal-equation solve.
    Q, R = np.linalg.qr(X * np.sqrt(w)[:, None], mode="reduced")
    beta = np.linalg.solve(R, Q.T @ (np.sqrt(w)*y))
    scores = X * (w * (y-X@beta))[:, None]
    influences = np.linalg.solve(R, np.linalg.solve(R.T, scores.T)).T
    # Explicit zero influence for every out-of-domain full-spine record.
    positions = {row["row_id"]: n for n, row in enumerate(spine_rows)}
    full = np.zeros((len(spine_rows), X.shape[1]))
    for i, row in enumerate(domain_rows):
        full[positions[row["row_id"]]] = influences[i]
    totals = {}
    for row, influence in zip(spine_rows, full):
        key = (row["stratum"], row["psu"])
        totals.setdefault(key, np.zeros(X.shape[1]))
        totals[key] += influence
    strata = sorted(set(k[0] for k in totals))
    covariance = np.zeros((X.shape[1], X.shape[1]))
    for h in strata:
        members = [v for key, v in totals.items() if key[0] == h]
        if len(members) < 2:
            raise ValueError("singleton stratum")
        # Pairwise identity for m/(m-1) times centered PSU outer products.
        for j in range(len(members)):
            for k in range(j+1, len(members)):
                delta = members[j]-members[k]
                covariance += np.outer(delta, delta)/(len(members)-1)
    df = len(totals)-len(strata)-(X.shape[1]-1)
    return beta, covariance, df, int(np.count_nonzero(np.any(full != 0, axis=1)))


def corr(x, y, w):
    # np.cov frequency-style analytic weights; normalization cancels in ratio.
    cov = np.cov(np.stack((x, y)), aweights=w, ddof=0)
    return float(cov[0, 1]/np.sqrt(cov[0, 0]*cov[1, 1]))


def main():
    freeze, manifest, execution, spec = verify_hashes()
    observed, columns = table("shared/observed.csv")
    require("exact observed schema", columns == ["row_id", "bmi", "age", "sex"])
    require("observed 1700 unique rows", len(observed) == 1700 and len({r["row_id"] for r in observed}) == 1700)
    expected_seeds = list(range(270101, 270121))
    pre = read_json("runs/initial_v1/pre_execution.json")
    require("20 prescheduled seeds bound throughout", pre["seeds"] == expected_seeds == [r["seed"] for r in execution["draws"]] == [r["seed"] for r in manifest["draws"]])
    require("20 files only in run", len(list((ROOT / "runs/initial_v1").glob("enriched_*.csv"))) == 20)
    require("one evaluated construction", freeze["model_labels"] == ["initial_v1"] and freeze["draw_count"] == 20)
    require("exact draw indices", [str(r["draw_id"]) for r in manifest["draws"]] == [str(i) for i in range(1,21)])
    ev = read_json("results/evaluation_v1/evaluation.json")
    hash_check("freeze_v1/evaluation_manifest.json", ev["manifest_sha256"], "evaluated manifest")
    hash_check("custodian/locked/evaluator_reference.csv", ev["reference_sha256"], "evaluation")
    hash_check("custodian/locked/evaluator_design_spine.csv", ev["spine_sha256"], "evaluation")
    require("evaluation uses exact frozen specification", ev["frozen_analysis"] == spec)
    require("single saved evaluation", len(list((ROOT / "results").glob("evaluation_*/evaluation.json"))) == 1)
    records = sorted(observed, key=lambda r: r["row_id"])
    fingerprint = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    require("independent predictor fingerprint", fingerprint == spec["predictor_fingerprint"])
    bmi, age = array(observed, "bmi"), array(observed, "age")
    sex = np.array([r["sex"] == spec["sex_comparison"] for r in observed], float)
    close("predictor-only knots", np.quantile(bmi, [.1, .5, .9]), spec["bmi_knots"])
    close("predictor-only contrast locations", np.quantile(bmi, [.25, .5, .75]), spec["bmi_contrast_locations"])
    close("predictor centers", [np.median(bmi), np.mean(age)], [spec["bmi_center"], spec["age_center"]])
    reference, _ = table("custodian/locked/evaluator_reference.csv")
    spine, _ = table("custodian/locked/evaluator_design_spine.csv")
    original, _ = table("custodian/locked/reference.csv")
    reference_by_id = {r["row_id"]: r for r in reference}
    require("reference unique exact observed ID set", len(reference) == len(reference_by_id) == 1700 and set(reference_by_id) == {r["row_id"] for r in observed})
    domain = [reference_by_id[r["row_id"]] for r in observed]
    source_by_id = {r["row_id"]: r for r in original}
    require("adapter target values exact original unit", all(float(r["insulin"]) == float(source_by_id[r["row_id"]]["insulin_uU_mL"]) for r in domain))
    require("original reference predictors preserved", all(all(float(r[c]) == float(source_by_id[r["row_id"]][c]) for c in ("bmi", "age", "sex")) for r in observed))
    spine_by_id = {r["row_id"]: r for r in spine}
    require("full spine 2711 unique rows", len(spine) == len(spine_by_id) == 2711)
    require("domain design is exact spine subset", all(all(r[c] == spine_by_id[r["row_id"]][c] for c in ("weight", "stratum", "psu")) for r in domain))
    w = array(domain, "weight")
    require("all full design weights positive finite", np.isfinite(array(spine, "weight")).all() and (array(spine, "weight") > 0).all())
    B, A = (bmi-spec["bmi_center"])/5, (age-spec["age_center"])/10
    ones = np.ones(len(observed))
    matrices = {"A": np.column_stack((ones, B)), "B": np.column_stack((ones, B, A, sex)),
                "C": np.column_stack((ones, B, rcs(bmi, spec["bmi_knots"]), A, sex)),
                "D": np.column_stack((ones, B, A, sex, B*sex))}
    q1, q2, q3 = spec["bmi_contrast_locations"]
    r1, r2, r3 = rcs(np.array([q1,q2,q3]), spec["bmi_knots"])
    curvature = 5*(r1/(q2-q1) - r2*(1/(q3-q2)+1/(q2-q1)) + r3/(q3-q2))
    contrast_specs = {"A": [("overall_bmi_per_5", [0,1])],
                      "B": [("adjusted_bmi_per_5", [0,1,0,0]), ("adjusted_age_per_10", [0,0,1,0]), ("adjusted_sex_comparison", [0,0,0,1])],
                      "C": [("upper_minus_lower_bmi_slope_per_5", [0,0,curvature,0,0])],
                      "D": [("sex_difference_bmi_slope_per_5", [0,0,0,0,1]), ("sex_reference_bmi_slope_per_5", [0,1,0,0,0]), ("sex_comparison_bmi_slope_per_5", [0,1,0,0,1])]}
    # Unit test with two observed and two zero-domain PSUs in one full stratum.
    artificial_domain = [{"row_id":"fixture_a", "stratum":"h", "psu":"1"}, {"row_id":"fixture_b", "stratum":"h", "psu":"2"}]
    artificial_spine = artificial_domain + [{"row_id":"fixture_c", "stratum":"h", "psu":"3"}, {"row_id":"fixture_d", "stratum":"h", "psu":"4"}]
    fb, fv, fdf, fnonzero = independent_fit(np.ones((2,1)), np.array([1.,3.]), np.ones(2), artificial_domain, artificial_spine)
    close("independent zero-domain PSU fixture covariance", fv, [[2/3]])
    require("zero-domain fixture full df and zero rows", fdf == 3 and fnonzero == 2)
    datasets = [("reference", array(domain,"insulin"), ev["reference"])]
    vectors = []
    aggregate_rows = []
    for i, draw in enumerate(manifest["draws"]):
        rows, header = table(draw["path"])
        require(f"draw {i+1}: exact output schema and count", header == columns+["insulin"] and len(rows) == 1700)
        require(f"draw {i+1}: row order preserved", [r["row_id"] for r in rows] == [r["row_id"] for r in observed])
        require(f"draw {i+1}: exact observed numeric values", all(all(float(r[c]) == float(o[c]) for c in ("bmi", "age", "sex")) for r,o in zip(rows,observed)))
        y = array(rows,"insulin")
        require(f"draw {i+1}: positive finite uU/mL outputs", np.isfinite(y).all() and (y > 0).all())
        vectors.append(hashlib.sha256(y.tobytes()).hexdigest())
        saved = ev["generated"][i]
        require(f"draw {i+1}: saved draw accounting", saved["draw_id"] == str(i+1) and saved["model_revision"] == "initial_v1")
        datasets.append((str(i+1), y, saved))
    require("all 20 generated vectors distinct", len(set(vectors)) == 20)
    require("positive finite real outcomes", np.isfinite(datasets[0][1]).all() and (datasets[0][1] > 0).all())
    all_correlations = {}
    reference_estimates = {}
    pairs = {(r["stratum"], r["psu"]) for r in spine}
    strata = {r["stratum"] for r in spine}
    for name, insulin, saved in datasets:
        endpoints = {r["endpoint"]:r for r in saved["endpoints"]}
        require(f"dataset {name}: eight unique endpoints", len(endpoints) == len(saved["endpoints"]) == 8)
        all_correlations[name] = {"bmi_raw_insulin": corr(bmi,insulin,w), "bmi_log_insulin":corr(bmi,np.log(insulin),w)}
        for key,value in all_correlations[name].items():
            close(f"dataset {name}: {key}", value, saved["descriptive_correlations"][key], category="weighted_correlations")
        for model, X in matrices.items():
            beta, variance, df, nonzero = independent_fit(X, np.log(insulin), w, domain, spine)
            saved_fit = saved["fits"][model]
            close(f"dataset {name}, model {model}: QR coefficients", beta, saved_fit["coefficients"], category="coefficients")
            close(f"dataset {name}, model {model}: influence/PSU covariance", variance, saved_fit["covariance"], category="covariances")
            d = saved_fit["diagnostics"]
            require(f"dataset {name}, model {model}: design/df accounting", d["domain_n"] == 1700 and d["full_spine_n"] == 2711 and d["full_psus"] == len(pairs) and d["full_strata"] == len(strata) and d["design_df"] == len(pairs)-len(strata) and d["residual_df"] == df and d["rank"] == X.shape[1] and nonzero <= 1700)
            close(f"dataset {name}, model {model}: weighted total", w.sum(), d["weighted_domain_total"], category="survey_diagnostics")
            close(f"dataset {name}, model {model}: descriptive Kish n", w.sum()**2/(w@w), d["kish_weight_effective_n_descriptive"], category="survey_diagnostics")
            for endpoint,c in contrast_specs[model]:
                c = np.array(c)
                estimate = float(c@beta)
                se = float(np.sqrt(c@variance@c))
                bounds = estimate + np.array([-1,1])*t.ppf(.975,df)*se
                independent = {"estimate_log_scale":estimate, "standard_error":se, "ci95_low_log_scale":bounds[0], "ci95_high_log_scale":bounds[1],
                               "exp_estimate":float(np.exp(estimate)), "exp_ci95_low":float(np.exp(bounds[0])), "exp_ci95_high":float(np.exp(bounds[1]))}
                for key,value in independent.items():
                    close(f"dataset {name}, endpoint {endpoint}: {key}", value, endpoints[endpoint][key], category="endpoint_statistics")
                if name == "reference":
                    reference_estimates[endpoint] = estimate
                else:
                    for key,value in (("signed_difference_from_reference",estimate-reference_estimates[endpoint]), ("absolute_difference_from_reference",abs(estimate-reference_estimates[endpoint]))):
                        close(f"dataset {name}, endpoint {endpoint}: {key}", value,endpoints[endpoint][key],category="endpoint_differences")
                        independent[key] = value
                aggregate_rows.append({"draw_id":name,"analysis":model,"endpoint":endpoint,**independent})
    endpoint_rows,_ = table("results/evaluation_v1/endpoints.csv")
    require("all 168 endpoints accounted for", len(endpoint_rows) == len(aggregate_rows) == 168 and sum(r["source"] == "reference" for r in endpoint_rows) == 8 and sum(r["source"] == "generated" for r in endpoint_rows) == 160)
    for actual,saved in zip(aggregate_rows,endpoint_rows):
        require("endpoint CSV identity/order", all(str(actual[k]) == saved[k] for k in ("draw_id","analysis","endpoint")))
        for key,value in actual.items():
            if key not in ("draw_id","analysis","endpoint"):
                close("endpoint CSV numeric "+key,value,float(saved[key]),category="endpoint_csv")
    summary_csv,_ = table("results/evaluation_v1/draw_summaries.csv")
    require("eight summary endpoints", len(summary_csv) == len(ev["draw_summaries"]) == 8)
    report,_ = table("results/report_v2/scientific_interpretation.csv")
    require("all eight presentation endpoints", len(report) == 8)
    markdown = (ROOT / "results/report_v2/ALL_ANALYSES.md").read_text(encoding="utf-8")
    def state(lo,hi):
        return "positive" if lo > 0 else ("negative" if hi < 0 else "interval includes zero")
    for endpoint in reference_estimates:
        rows = [r for r in aggregate_rows if r["endpoint"] == endpoint and r["draw_id"] != "reference"]
        values = np.array([r["estimate_log_scale"] for r in rows])
        target = reference_estimates[endpoint]
        summary = {"mean_estimate":values.mean(),"between_draw_sd":values.std(ddof=1),"min_estimate":values.min(),"max_estimate":values.max(),"signed_mean_difference":values.mean()-target,"mean_absolute_difference":abs(values-target).mean()}
        for container in (ev["draw_summaries"],summary_csv):
            s = next(r for r in container if r["endpoint"] == endpoint)
            require("summary draw count", int(s["draw_count"]) == 20)
            for key,value in summary.items():
                close("summary "+endpoint+" "+key,value,float(s[key]),category="draw_summaries")
        p = next(r for r in report if r["endpoint"] == endpoint)
        ref = next(r for r in aggregate_rows if r["endpoint"] == endpoint and r["draw_id"] == "reference")
        expected = {"reference_log_estimate":target,"reference_ci_low":ref["ci95_low_log_scale"],"reference_ci_high":ref["ci95_high_log_scale"],"reference_ratio":ref["exp_estimate"],"reference_ratio_low":ref["exp_ci95_low"],"reference_ratio_high":ref["exp_ci95_high"],"generated_median_log_estimate":np.median(values),"generated_min_log_estimate":values.min(),"generated_max_log_estimate":values.max(),"generated_median_ratio":np.exp(np.median(values)),"generated_min_ratio":np.exp(values.min()),"generated_max_ratio":np.exp(values.max()),"draw_count":20}
        counts = {key:sum(state(r["ci95_low_log_scale"],r["ci95_high_log_scale"]) == key for r in rows) for key in ("positive","negative","interval includes zero")}
        expected.update({"draws_"+k.replace(" ","_"):v for k,v in counts.items()})
        expected["draws_unavailable"] = 0
        for key,value in expected.items():
            close("presentation "+endpoint+" "+key,value,float(p[key]),category="presentation_table")
        require("presentation reference interval state",p["reference_state"] == state(ref["ci95_low_log_scale"],ref["ci95_high_log_scale"]))
        line = f"| {p['question']} | {target:.3f} [{ref['ci95_low_log_scale']:.3f}, {ref['ci95_high_log_scale']:.3f}] | {np.median(values):.3f} [{values.min():.3f}, {values.max():.3f}] | {p['reference_state']} | {counts['positive']} / {counts['interval includes zero']} / {counts['negative']} |"
        require("presentation Markdown exact rounded row "+endpoint,line in markdown)
    ctable = read_json("results/report_v2/correlations.json")
    for key in all_correlations["reference"]:
        close("presentation reference correlation "+key,all_correlations["reference"][key],ctable["reference_correlations"][key],category="correlation_summaries")
        vals = np.array([all_correlations[str(i)][key] for i in range(1,21)])
        for stat, value in (("median",np.median(vals)),("min",vals.min()),("max",vals.max())):
            close("presentation generated correlation "+key+" "+stat,value,ctable["models"]["initial_v1"][key][stat],category="correlation_summaries")
    for filename in ("scientific_interpretation.csv","correlations.json","ALL_ANALYSES.md"):
        require("report v2 preserves v1 numerical/text file "+filename,(ROOT/"results/report_v1"/filename).read_bytes() == (ROOT/"results/report_v2"/filename).read_bytes())
    tree = ast.parse((ROOT/"agent_clean/initial/generator.py").read_text(encoding="utf-8"))
    imports = sorted(n.name for node in ast.walk(tree) if isinstance(node,ast.Import) for n in node.names)
    require("generator imports only numpy/pandas",imports == ["numpy","pandas"])
    read_calls = []
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            name = ast.unparse(node.func)
            if any(x in name for x in ("read_","open","load","exec","eval","request","socket","fetch")):
                read_calls.append(name)
    require("generator AST has no file/network/target reads",not read_calls)
    with (OUT/"independently_recomputed_endpoints.csv").open("w",encoding="utf-8",newline="") as handle:
        fields = list(aggregate_rows[-1])
        writer = csv.DictWriter(handle,fieldnames=fields)
        writer.writeheader()
        writer.writerows(aggregate_rows)
    preserved = {str(path.relative_to(ROOT)).replace("\\","/"): sha(path) for path in (ROOT/"results").glob("evaluation_v1/*") if path.is_file()}
    preserved.update({str(path.relative_to(ROOT)).replace("\\","/"):sha(path) for path in (ROOT/"results/report_v2").iterdir() if path.is_file()})
    save("PASS: numerical integrity and independent reproduction",unique_committed_files=len({r["path"] for r in hash_checks}),checked_file_commitments=len(hash_checks),datasets=21,weighted_fits=84,endpoints=168,generated_draws=20,full_spine_rows=2711,domain_rows=1700,outside_domain_rows=1011,full_psus=len(pairs),full_strata=len(strata),residual_df={m:len(pairs)-len(strata)-(X.shape[1]-1) for m,X in matrices.items()},audit_snapshot_result_hashes=preserved,
         limitations=["Static/source and recorded-workflow audit cannot prove absence of unlogged access in a shared filesystem or pretrained knowledge.","Historical retrieval-response/content digests without retained raw response bytes cannot be rehashed; every retained local artifact commitment was checked.","Audit reproduces the frozen design/estimand and conditional intervals; it does not calibrate source/transport uncertainty or repair missing-outcome selection.","No generation was rerun. Single saved evaluation directory supports accounting but is not a tamper-proof execution counter."])
    print(json.dumps({"status":"PASS","checks":len(checks),"hash_commitments":len(hash_checks),"unique_files":len({r["path"] for r in hash_checks}),"weighted_fits":84,"endpoints":168,"maximum_absolute_errors":numeric_errors}))


if __name__ == "__main__":
    main()
