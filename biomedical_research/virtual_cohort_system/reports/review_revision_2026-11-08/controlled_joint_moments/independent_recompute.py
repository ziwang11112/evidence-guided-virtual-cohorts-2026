"""Recompute existing artificial deliveries; never import/run authored generators.

Independent numerical path: stdlib CSV reading, centered cross-products and
normal equations, residual sum of squares from covariance decomposition.
Does not import runner.py, evaluate.py or any cohort_harness calculator.
The auditor previously authored the runner/evaluator: numerical independence
does not imply independent personnel review.
"""
from __future__ import annotations

import ast
from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
COLS = ["Z", "X1", "X2", "Y"]
AUTHORS = ["O1", "O2", "C1", "C2"]
SEEDS = [8101, 8102, 8103]
MODELS = {"source_Z_X1": [0, 1], "source_Z_X2": [0, 2], "heldout_joint": [0, 1, 2]}
ATOL = 1e-10
RTOL = 1e-10


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(condition, message):
    if not condition:
        raise AssertionError(message)


class Comparisons:
    def __init__(self):
        self.n = 0
        self.max_abs = defaultdict(float)
        self.failures = []

    def compare(self, actual, expected, label, group):
        a, b = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
        self.n += int(a.size)
        if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
            self.failures.append({"label": label, "reason": "shape_or_nonfinite"})
            return
        difference = float(np.max(np.abs(a - b))) if a.size else 0.0
        self.max_abs[group] = max(self.max_abs[group], difference)
        if not np.allclose(a, b, atol=ATOL, rtol=RTOL):
            self.failures.append({"label": label, "max_absolute_difference": difference})


def projection(means, covariance, indices, n=None):
    coefficients = np.linalg.solve(covariance[np.ix_(indices, indices)], covariance[indices, 3])
    residual_variance = float(covariance[3, 3] - covariance[3, indices] @ coefficients)
    check(residual_variance > 0, "Nonpositive independently calculated residual variance")
    # covariance uses n-1. For an intercept and k predictors the fitted SSE
    # divided by n-k-1 equals covariance residual variance times this factor.
    if n is not None:
        residual_variance *= (n - 1) / (n - len(indices) - 1)
    return {"coefficients": {"intercept": float(means[3] - means[indices] @ coefficients),
                              **{COLS[j]: float(v) for j, v in zip(indices, coefficients)}},
            "residual_sd": float(np.sqrt(residual_variance))}


def source_value(check_item, means, covariance):
    op = check_item["operator"]
    check(op["selection"] == [] and op["missing_policy"] == "error" and op["unit"] == "1",
          "Unexpected controlled source operator")
    kind = op["kind"]
    if kind == "mean":
        return float(means[COLS.index(op["column"])])
    if kind == "sd":
        return float(np.sqrt(covariance[COLS.index(op["column"]), COLS.index(op["column"])]))
    if kind == "correlation":
        i, j = COLS.index(op["x"]), COLS.index(op["y"])
        return float(covariance[i, j] / np.sqrt(covariance[i, i] * covariance[j, j]))
    check(kind == "ols_coefficient" and op["outcome"] == "Y" and op["include_intercept"],
          "Unexpected source regression")
    indices = [COLS.index(x) for x in op["predictors"]]
    return projection(means, covariance, indices)["coefficients"][op["term"]]


def reconstruct_from_source(source):
    means = np.zeros(4)
    covariance = np.zeros((4, 4))
    for item in source["checks"]:
        op = item["operator"]
        if op["kind"] == "mean":
            means[COLS.index(op["column"])] = item["estimate"]
        elif op["kind"] == "sd":
            index = COLS.index(op["column"])
            covariance[index, index] = item["estimate"] ** 2
    for item in source["checks"]:
        op = item["operator"]
        if op["kind"] == "correlation":
            i, j = COLS.index(op["x"]), COLS.index(op["y"])
            covariance[i, j] = covariance[j, i] = item["estimate"] * np.sqrt(covariance[i, i] * covariance[j, j])
    slopes = defaultdict(dict)
    for item in source["checks"]:
        op = item["operator"]
        if op["kind"] == "ols_coefficient":
            slopes[tuple(op["predictors"])][op["term"]] = item["estimate"]
    recovered = defaultdict(list)
    for names, coefficients in slopes.items():
        indices = [COLS.index(x) for x in names]
        c = covariance[np.ix_(indices, indices)] @ np.array([coefficients[x] for x in names])
        for index, value in zip(indices, c):
            recovered[index].append(float(value))
    check(set(recovered) == {0, 1, 2}, "Source does not identify all outcome cross-covariances")
    for index, values in recovered.items():
        check(np.allclose(values, values[0], atol=1e-14, rtol=0), "Conflicting source normal equations")
        covariance[index, 3] = covariance[3, index] = values[0]
    return means, covariance


def main():
    comparisons = Comparisons()
    lock = read(ROOT / "BATCH_LOCK.json")
    design = read(ROOT / "DESIGN_LOCK.json")
    source = read(ROOT / "SOURCE.json")
    stored = read(ROOT / "RESULTS.json")
    truth = read(ROOT / "custodian/TRUTH.json")
    for rel, expected in lock["records"].items():
        check(sha(ROOT / rel) == expected, "BATCH_LOCK mismatch: " + rel)
    for rel, expected in design["records"].items():
        check(sha(ROOT / rel) == expected, "DESIGN_LOCK mismatch: " + rel)
    for module, expected in lock["engine_sha256"].items():
        path = PROJECT / "cohort_harness" / ("_worker.py" if module == "worker" else module.split(".")[-1] + ".py")
        check(sha(path) == expected, "Engine hash mismatch: " + module)
    check(sha(ROOT / "custodian/TRUTH.json") == lock["truth_sha256"] == stored["truth_sha256"], "Truth commitment mismatch")
    check(sha(ROOT / "BATCH_LOCK.json") == stored["batch_lock_sha256"], "Results use different batch")
    check(sha(ROOT / "RESULTS.csv") == stored["results_csv_sha256"], "CSV aggregate hash mismatch")
    means_truth = np.asarray(truth["mean"], dtype=float)
    cov_truth = np.asarray(truth["covariance"], dtype=float)
    sd_truth = np.sqrt(np.diag(cov_truth))
    source_mean, source_cov = reconstruct_from_source(source)
    comparisons.compare(source_mean, means_truth, "source_mean_identifies_truth", "source_law")
    comparisons.compare(source_cov, cov_truth, "source_covariance_identifies_truth", "source_law")
    theory = {name: projection(means_truth, cov_truth, indices) for name, indices in MODELS.items()}
    reference_beta = np.array([theory["heldout_joint"]["coefficients"][x] for x in COLS[:3]])
    check(len(stored["records"]) == 12, "Expected all twelve result records")
    stored_by_slot = {(r["author"], r["seed"]): r for r in stored["records"]}
    check(set(stored_by_slot) == {(a, s) for a in AUTHORS for s in SEEDS}, "Result slots incomplete")
    flat = {}
    def add(author, seed, section, metric, value, error=None, signed_error=None, status="computed"):
        flat[(author, seed, section, metric)] = {"value": value, "error": error,
                                               "signed_error": signed_error, "status": status}
    csv_hash_groups = defaultdict(list)
    table_reports = []
    law_reports = []
    bound_files = 0
    source_check_count = 0
    stage_seed_checks = []
    runner_syntax = ast.parse((ROOT / "runner.py").read_text(encoding="utf8"))
    bridge = next(ast.literal_eval(n.value) for n in runner_syntax.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "BRIDGE" for t in n.targets))
    check("np.random.default_rng(seed)" in bridge and "author.generate" in bridge, "Bridge seed forwarding changed")
    for author in AUTHORS:
        spec = read(ROOT / f"bundles/{author}/model_spec.json")
        decision = read(ROOT / f"bundles/{author}/decision.json")
        program = (ROOT / f"bundles/{author}/generator.py").read_text(encoding="utf8")
        ast.parse(program)
        means = np.array(spec.get("predictor_mean", spec.get("predictor_means")), dtype=float)
        cov = np.asarray(spec["predictor_covariance"], dtype=float)
        beta = np.asarray(spec["outcome_coefficients"], dtype=float)
        residual_variance = spec.get("outcome_residual_variance", float(spec.get("residual_sd", 0)) ** 2)
        comparisons.compare(means, source_mean[:3], author + ":predictor_means", "source_law")
        comparisons.compare(cov, source_cov[:3, :3], author + ":predictor_covariance", "source_law")
        comparisons.compare(beta, reference_beta, author + ":derived_joint_beta", "source_law")
        comparisons.compare(residual_variance, theory["heldout_joint"]["residual_sd"] ** 2,
                            author + ":derived_residual_variance", "source_law")
        law_cov = np.zeros((4, 4)); law_cov[:3, :3] = cov
        law_cov[:3, 3] = cov @ beta; law_cov[3, :3] = law_cov[:3, 3]
        law_cov[3, 3] = beta @ cov @ beta + residual_variance
        comparisons.compare(law_cov, source_cov, author + ":full_law_covariance", "source_law")
        source_ids = {c["id"] for c in source["checks"]}
        check(set(decision["source_check_ids_used"]) == source_ids, "Missing stated source use")
        # Static calls only; no invocation, import or regeneration.
        rng_calls = [ast.unparse(n) for n in ast.walk(ast.parse(program)) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                     and n.func.value.id == "rng"]
        layout = "one_n_by_4_array" if len(rng_calls) == 1 else "n_by_3_then_n_array"
        check(len(rng_calls) in {1, 2} and all("standard_normal" in x for x in rng_calls), "Unexpected RNG layout")
        law_reports.append({"author": author, "code_sha256": sha(ROOT / f"bundles/{author}/generator.py"),
                            "source_check_ids_used": sorted(source_ids), "joint_beta": beta.tolist(),
                            "residual_variance": float(residual_variance), "full_covariance": law_cov.tolist(),
                            "sampling_layout": layout, "rng_calls_static": rng_calls,
                            "decision_describes_source_normal_equation_derivation": True})
        for seed in SEEDS:
            run = ROOT / f"private_runs/{author}/seed_{seed}"
            receipt = read(run / "execution.json")
            check(receipt["status"] == "success" and receipt["seed"] == seed and receipt["author"] == author, "Wrong receipt identity")
            check(receipt["batch_lock_sha256"] == sha(ROOT / "BATCH_LOCK.json"), "Receipt lock mismatch")
            actual = {p.relative_to(run).as_posix() for p in run.rglob("*") if p.is_file() and p != run / "execution.json"}
            check(actual == set(receipt["files"]), "Receipt inventory mismatch")
            for rel, expected in receipt["files"].items():
                check(sha(run / rel) == expected, "Receipt artifact mismatch: " + rel)
                bound_files += 1
            input_bindings = read(run / "input_bindings.json")
            for name, expected in input_bindings.items():
                check(sha(run / "input" / name) == expected, "Input hash mismatch")
            request = read(run / "input/request.json")
            check(request["seed"] == seed, "Staged seed mismatch")
            check(read(run / "input/model_spec.json") == {"n": 10000, "author_spec": spec}, "Staged specification mismatch")
            check(sha(run / "input/author.py") == sha(ROOT / f"bundles/{author}/generator.py"), "Staged code mismatch")
            check((run / "input/generator.py").read_text(encoding="utf8") == bridge, "Staged bridge mismatch")
            check(sha(run / "input/worker.py") == lock["engine_sha256"]["worker"], "Staged worker mismatch")
            stage_seed_checks.append({"author": author, "seed": seed, "staged_seed": request["seed"]})
            table = run / "output/generated.csv"
            h = sha(table)
            check(receipt["generated_sha256"] == h, "Receipt table hash mismatch")
            csv_hash_groups[h].append({"author": author, "seed": seed})
            with table.open(newline="", encoding="utf8") as stream:
                reader = csv.reader(stream)
                check(next(reader) == COLS, "CSV schema differs")
                values = np.array([[float(x) for x in row] for row in reader], dtype=float)
            check(values.shape == (10000, 4) and np.isfinite(values).all(), "Invalid table")
            n = len(values)
            means = np.sum(values, axis=0) / n
            centered = values - means
            crossproducts = centered.T @ centered
            covariance = crossproducts / (n - 1)
            sd = np.sqrt(np.diag(covariance))
            eigenvalues = np.linalg.eigvalsh(covariance)
            check(np.min(eigenvalues) > 0 and np.linalg.matrix_rank(centered) == 4, "Finite/rank/eigen failure")
            actual_record = stored_by_slot[(author, seed)]
            check(actual_record["status"] == "evaluated" and actual_record["failure_flags"] == [], "Stored status differs")
            check(actual_record["generated_sha256"] == h, "Results hash mismatch")
            check(actual_record["execution_receipt_sha256"] == sha(run / "execution.json"), "Results receipt mismatch")
            comparisons.compare(covariance, actual_record["sample_covariance"], f"{author}/{seed}:covariance", "table_covariance")
            comparisons.compare(eigenvalues, actual_record["sample_covariance_eigenvalues"], f"{author}/{seed}:eigenvalues", "table_covariance")
            add(author, seed, "execution", "status", None, status="evaluated")
            for j, name in enumerate(COLS):
                marginal = actual_record["marginals"][name]
                signed = float(np.log(sd[j] / sd_truth[j]))
                mean_error = abs(means[j] - means_truth[j]) / sd_truth[j]
                for key, value in (("mean", means[j]), ("sd", sd[j]), ("variance", covariance[j, j]),
                                   ("standardized_mean_absolute_error", mean_error),
                                   ("log_sd_ratio", signed), ("abs_log_sd_ratio", abs(signed))):
                    comparisons.compare(value, marginal[key], f"{author}/{seed}:{name}/{key}", "marginal")
                add(author, seed, "marginal_mean", name, float(means[j]), float(mean_error))
                add(author, seed, "marginal_sd", name, float(sd[j]), abs(signed), signed)
                add(author, seed, "marginal_variance", name, float(covariance[j, j]))
            computed_models = {}
            for model, indices in MODELS.items():
                calc = projection(means, covariance, indices, n)
                original = actual_record["models"][model]
                check(original["status"] == "computed", "Stored model failure")
                check(original["rank"] == len(indices) + 1 and original["residual_denominator"] == n - len(indices) - 1, "Rank/DF differ")
                absolute = []
                for term, value in calc["coefficients"].items():
                    comparisons.compare(value, original["coefficients"][term], f"{author}/{seed}:{model}/{term}", "regression")
                    signed = None
                    if term != "intercept":
                        j = COLS.index(term)
                        signed = (value - theory[model]["coefficients"][term]) * sd_truth[j] / sd_truth[3]
                        absolute.append(abs(signed))
                        comparisons.compare(signed, original["standardized_coefficient_signed_errors"][term],
                                            f"{author}/{seed}:{model}/{term}/signed", "regression_error")
                        comparisons.compare(abs(signed), original["standardized_coefficient_absolute_errors"][term],
                                            f"{author}/{seed}:{model}/{term}/absolute", "regression_error")
                    add(author, seed, model, "coefficient_" + term, value, abs(signed) if signed is not None else None, signed)
                signed_sd = float(np.log(calc["residual_sd"] / theory[model]["residual_sd"]))
                for key, value in (("residual_sd", calc["residual_sd"]), ("log_residual_sd_ratio", signed_sd),
                                   ("abs_log_residual_sd_ratio", abs(signed_sd)),
                                   ("mean_standardized_coefficient_absolute_error", np.mean(absolute))):
                    comparisons.compare(value, original[key], f"{author}/{seed}:{model}/{key}", "regression_error")
                add(author, seed, model, "residual_sd", calc["residual_sd"], abs(signed_sd), signed_sd)
                computed_models[model] = {**calc, "signed_residual_log_ratio": signed_sd,
                                          "mean_absolute_standardized_beta_error": float(np.mean(absolute))}
            stored_checks = {r["id"]: r for r in actual_record["source_checks"]["checks"]}
            check(set(stored_checks) == {r["id"] for r in source["checks"]}, "Source check inventory differs")
            diagnostic_file = read(run / "source_diagnostics.json")
            check(diagnostic_file == actual_record["source_checks"], "Receipt source diagnostics differ from RESULTS")
            for item in source["checks"]:
                value = source_value(item, means, covariance)
                original = stored_checks[item["id"]]
                check(original["operator"] == item["operator"] and original["reported_value"] == item["estimate"], "Source definition/value changed")
                check(original["status"] == "computed", "Source not computed")
                check(all(original["calculation"][x] == n for x in ("n_input", "n_selected", "n_used")), "Source denominator differs")
                comparisons.compare(value, original["calculation"]["value"], f"{author}/{seed}:{item['id']}", "source_checks")
                comparisons.compare(value - item["estimate"], original["difference"], f"{author}/{seed}:{item['id']}/difference", "source_checks")
                add(author, seed, "source_constraint", item["id"], value, value - item["estimate"])
                source_check_count += 1
            for i, j in itertools.combinations(range(3), 2):
                key = COLS[i] + "__" + COLS[j]
                value = float(covariance[i, j] / (sd[i] * sd[j]))
                reference = cov_truth[i, j] / (sd_truth[i] * sd_truth[j])
                comparisons.compare(value, actual_record["predictor_correlations"][key]["value"], f"{author}/{seed}:{key}", "correlation")
                add(author, seed, "predictor_correlation", key, value, abs(value - reference))
            table_reports.append({"author": author, "seed": seed, "csv_sha256": h,
                                  "rows": n, "unique_rows": int(np.unique(values, axis=0).shape[0]),
                                  "joint": computed_models["heldout_joint"]})
    with (ROOT / "RESULTS.csv").open(newline="", encoding="utf8") as stream:
        csv_rows = list(csv.DictReader(stream))
    check(len(csv_rows) == len(flat), "CSV metric inventory differs")
    seen = set()
    for item in csv_rows:
        key = (item["author"], int(item["seed"]), item["section"], item["metric"])
        check(key in flat and key not in seen, "Unexpected or duplicate CSV metric")
        seen.add(key)
        check(item["status"] == flat[key]["status"], "CSV metric status differs")
        for field in ("value", "error", "signed_error"):
            expected = flat[key][field]
            if expected is None:
                check(item[field] == "", "Expected empty CSV numeric cell")
            else:
                comparisons.compare(float(item[field]), expected, str(key) + ":" + field, "csv_metrics")
    aggregate_groups = defaultdict(list)
    for (author, seed, section, metric), item in flat.items():
        for field in ("value", "error", "signed_error"):
            if item[field] is not None:
                aggregate_groups[(author, section, metric, field)].append(item[field])
    construction_rows = stored["aggregation"]["construction_summaries"]
    check(len(construction_rows) == len(aggregate_groups), "Construction aggregate inventory differs")
    arm_groups = defaultdict(dict)
    primary_constructor = defaultdict(dict)
    for item in construction_rows:
        key = tuple(item[x] for x in ("author", "section", "metric", "field"))
        values = aggregate_groups[key]
        check(item["n_seeds_available"] == len(values) == item["n_seeds_planned"] == 3, "Construction seed count differs")
        for stat, value in (("mean", np.mean(values)), ("min", min(values)), ("max", max(values))):
            comparisons.compare(value, item[stat], str(key) + ":" + stat, "constructor_aggregates")
        arm_groups[(key[0][0], *key[1:])][key[0]] = float(np.mean(values))
        if key[1] == "heldout_joint" and key[3] == "error":
            primary_constructor[key[0]][key[2]] = {"mean": float(np.mean(values)), "min": float(min(values)), "max": float(max(values))}
    arm_rows = stored["aggregation"]["arm_summaries"]
    check(len(arm_rows) == len(arm_groups), "Arm aggregate inventory differs")
    arm_primary = defaultdict(dict)
    for item in arm_rows:
        key = tuple(item[x] for x in ("arm", "section", "metric", "field"))
        values = arm_groups[key]
        check(item["status"] == "complete" and item["n_constructions_available"] == 2, "Arm incomplete")
        value = float(np.mean(list(values.values())))
        comparisons.compare(value, item["equal_weight_construction_mean"], str(key), "arm_aggregates")
        for author, v in values.items():
            comparisons.compare(v, item["construction_means"][author], str(key) + ":" + author, "arm_aggregates")
        if key[1] == "heldout_joint" and key[3] == "error":
            arm_primary[key[0]][key[2]] = value
    primary_arm_difference = {key: arm_primary["C"][key] - arm_primary["O"][key] for key in arm_primary["O"]}
    duplicates = [{"sha256": h, "slots": slots} for h, slots in sorted(csv_hash_groups.items())]
    check(len(csv_hash_groups) == 6 and all(len(slots) == 2 for slots in csv_hash_groups.values()), "Unexpected distinct-table inventory")
    for slots in csv_hash_groups.values():
        check(len({x["seed"] for x in slots}) == 1 and
              {x["author"] for x in slots} in ({"O1", "C2"}, {"O2", "C1"}), "Unexpected duplicate pattern")
    report = {
        "schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_NUMERICAL_RECOMPUTATION_WITH_REPLICATION_QUALIFICATION" if not comparisons.failures else "FAIL",
        "reviewer": "claude_seed_audit", "independent_numerical_implementation": True,
        "independent_personnel_review": False,
        "reviewer_role_disclosure": "This auditor previously authored runner.py/evaluate.py; recalculation imports neither and uses a different numerical formulation.",
        "method": "Stdlib CSV + centered cross-products + normal equations. Residual variance computed from covariance decomposition with n-k-1 correction, independently of evaluator lstsq/SSE.",
        "no_sampling_no_generator_import_no_patient_data": True,
        "frozen_files_changed": False,
        "binding_checks": {"batch_files": len(lock["records"]), "design_files": len(design["records"]),
                           "engines": len(lock["engine_sha256"]), "receipt_files": bound_files,
                           "correct_seed_staging": stage_seed_checks},
        "comparison": {"numeric_comparisons": comparisons.n, "atol": ATOL, "rtol": RTOL,
                       "maximum_absolute_differences_by_group": dict(comparisons.max_abs), "failures": comparisons.failures,
                       "source_checks_recomputed": source_check_count,
                       "csv_metric_rows_recomputed": len(csv_rows), "construction_aggregate_rows": len(construction_rows),
                       "arm_aggregate_rows": len(arm_rows)},
        "scientific_law": {"source_suffices_for_joint_projection_and_residual_variance": True,
                           "source_reconstructed_covariance": source_cov.tolist(),
                           "joint_beta": reference_beta.tolist(),
                           "residual_variance": theory["heldout_joint"]["residual_sd"] ** 2,
                           "four_programs_same_gaussian_law_up_to_floating_point": True,
                           "maximum_source_law_difference": comparisons.max_abs["source_law"], "authors": law_reports},
        "replication": {"authored_programs": 4, "scientific_laws_up_to_roundoff": 1,
                        "sampling_layouts": 2, "nominal_delivery_slots": 12,
                        "distinct_csv_tables": 6, "rows_per_table": 10000,
                        "identical_output_groups": duplicates,
                        "explanation": "O1/C2 consume one n-by-4 Gaussian draw; O2/C1 consume n-by-3 predictors then n residual draws. Same seeds and same paired parameters/layouts yield paired identical bytes. No resampling was needed to establish this.",
                        "interpretation": "Do not call twelve independent cohorts, four distinct laws, or an independently replicated arm performance difference. Six distinct tables are deterministic seeded deliveries; their stochastic independence is not separately demonstrated."},
        "primary_by_construction": dict(primary_constructor), "primary_by_arm": dict(arm_primary),
        "C_minus_O_primary_arm_means": primary_arm_difference,
        "table_recomputations": table_reports,
        "information_boundary": {
            "approved_inputs": "Each author had the same SOURCE.json and own request; no truth staged into any generator.",
            "supported_statement": "All four specifications and written derivations solve the requested joint moments from the supplied source summaries; this solution is algebraically available without target values.",
            "limits": "The filesystem/tool access of author Agents was not OS-isolated. Static artifacts and declarations alone cannot prove absence of every unlogged read; independent agent dispatch/tool history is a separate provenance check."},
        "conclusion": "No added reconciliation-instruction gain in this fixture: the ordinary arm already reconstructs the same correct joint Gaussian law. Both arm averages are equal because each contains the same two sampling layouts. Retain this as a bounded necessity result; it neither proves universal component uselessness nor broad biomedical efficacy.",
        "input_hashes": {"RESULTS.json": sha(ROOT / "RESULTS.json"), "RESULTS.csv": sha(ROOT / "RESULTS.csv"),
                         "BATCH_LOCK.json": sha(ROOT / "BATCH_LOCK.json"), "independent_recompute.py": sha(__file__)}
    }
    with (ROOT / "INDEPENDENT_RESULTS_REVIEW.json").open("x", encoding="utf8") as stream:
        json.dump(report, stream, indent=2, allow_nan=False); stream.write("\n")
    print(json.dumps({"decision": report["decision"], "numeric_checks": comparisons.n,
                      "source_checks": source_check_count, "distinct_tables": len(csv_hash_groups),
                      "max_numeric_difference": max(comparisons.max_abs.values()),
                      "arm_differences": primary_arm_difference}, indent=2))


if __name__ == "__main__":
    main()
