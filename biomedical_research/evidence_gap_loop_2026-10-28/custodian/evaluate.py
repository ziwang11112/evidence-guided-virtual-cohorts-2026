"""Locked, outcome-neutral evaluation; no reference reading before release gate."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import t

BASE = Path(__file__).resolve().parent
PILOT = BASE.parent
OBSERVED = ["row_id", "bmi", "age", "sex"]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False)+"\n", encoding="utf-8")

def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        header = next(csv.reader(f), [])
    require(header and len(header) == len(set(header)), "Empty or duplicate CSV header")
    return pd.read_csv(path, dtype=str, keep_default_na=False)

def number(frame, column):
    try:
        values = np.array([float(x) for x in frame[column]], float)
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError(f"Invalid numeric column {column}") from exc
    require(np.isfinite(values).all(), f"Nonfinite {column}")
    return values

def valid_observed(frame):
    require(list(frame.columns) == OBSERVED, "Observed columns violate allowlist")
    require(frame.row_id.ne("").all() and frame.row_id.is_unique, "Bad observed row IDs")
    require((number(frame, "bmi") > 0).all(), "Invalid BMI")
    age = number(frame, "age")
    require(((age >= 20) & (age <= 79) & (age == np.floor(age))).all(), "Invalid age")
    require(np.isin(number(frame, "sex"), [1, 2]).all(), "Invalid sex")

def match_generated(observed, generated):
    require(set(generated.columns) == set(OBSERVED+["hdl"]), "Generated columns violate allowlist")
    require(generated.row_id.is_unique and set(generated.row_id) == set(observed.row_id), "Generated ID mismatch")
    aligned = generated.set_index("row_id").loc[observed.row_id].reset_index()
    for name in OBSERVED[1:]:
        require(np.array_equal(number(aligned, name), number(observed, name)), f"Changed observed {name}")
    y = number(aligned, "hdl")
    require((y > 0).all(), "HDL must be positive")
    return y

def matrices(observed):
    b = (number(observed, "bmi")-25)/5
    a = (number(observed, "age")-50)/10
    f = (number(observed, "sex") == 2).astype(float)
    one = np.ones(len(observed))
    return {"A": np.column_stack([one, b]), "B": np.column_stack([one, b, a, f]),
            "C": np.column_stack([one, b, b*b, a, f]), "D": np.column_stack([one, b, a, f, b*f])}

def taylor_fit(X, y, domain, spine):
    """WLS and stratified-PSU Taylor sandwich with zero scores outside domain."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    require(X.ndim == 2 and y.shape == (len(X),), "Bad fit dimensions")
    require(np.isfinite(X).all() and np.isfinite(y).all(), "Nonfinite fit inputs")
    rank = np.linalg.matrix_rank(X)
    require(rank == X.shape[1], "Rank-deficient frozen model")
    w = number(domain, "weight")
    require((w > 0).all(), "Nonpositive domain weight")
    w = w/w.mean()
    pairs = spine[["stratum", "psu"]].drop_duplicates()
    counts = pairs.groupby("stratum").size()
    require((counts >= 2).all(), "Singleton full-spine stratum")
    bread = X.T @ (w[:, None]*X)
    inverse = np.linalg.inv(bread)
    beta = np.linalg.solve(bread, X.T @ (w*y))
    scores = (w*(y-X@beta))[:, None]*X
    names = [f"score_{i}" for i in range(X.shape[1])]
    tagged = domain[["stratum", "psu"]].reset_index(drop=True).copy()
    tagged[names] = scores
    totals = tagged.groupby(["stratum", "psu"])[names].sum().reindex(pd.MultiIndex.from_frame(pairs), fill_value=0)
    meat = np.zeros_like(bread)
    for _, group in totals.groupby(level="stratum"):
        values = group.to_numpy()
        centered = values-values.mean(axis=0)
        meat += len(values)/(len(values)-1)*(centered.T@centered)
    covariance = inverse@meat@inverse
    covariance = (covariance+covariance.T)/2
    domain_pairs = domain[["stratum", "psu"]].drop_duplicates()
    design_df = len(domain_pairs)-domain_pairs.stratum.nunique()
    residual_df = design_df-(rank-1)
    diagnostics = {"full_spine_n": len(spine), "domain_n": len(domain),
                   "full_strata": int(pairs.stratum.nunique()), "full_psus": len(pairs),
                   "domain_strata": int(domain_pairs.stratum.nunique()), "domain_psus": len(domain_pairs),
                   "design_df": int(design_df), "residual_df": int(residual_df), "rank": int(rank)}
    return beta, covariance, diagnostics

def contrast(beta, covariance, c, df):
    c = np.array(c, float)
    estimate = float(c@beta)
    variance = float(c@covariance@c)
    require(variance >= -1e-9, "Negative contrast variance")
    se = float(np.sqrt(max(0, variance)))
    margin = float(t.ppf(.975, df))*se if df > 0 else None
    return {"estimate": estimate, "standard_error": se,
            "ci95_low": estimate-margin if margin is not None else None,
            "ci95_high": estimate+margin if margin is not None else None,
            "df": int(df)}

def analyze(observed, y, domain, spine, spec):
    y = np.asarray(y, float)
    require(y.shape == (len(observed),) and np.isfinite(y).all() and (y > 0).all(), "Bad HDL vector")
    fits, endpoints = {}, []
    for name, X in matrices(observed).items():
        beta, covariance, diag = taylor_fit(X, y, domain, spine)
        fits[name] = {"coefficients": beta.tolist(), "covariance": covariance.tolist(), "diagnostics": diag}
        for endpoint in spec["endpoints"]:
            if endpoint["model"] == name:
                endpoints.append({"endpoint": endpoint["name"], "model": name, "role": endpoint["role"],
                                  **contrast(beta, covariance, endpoint["contrast"], diag["residual_df"])})
    w = number(domain, "weight")
    w = w/w.sum()
    mean = float(w@y)
    sd = float(np.sqrt(w@((y-mean)**2)))
    order = np.argsort(y, kind="stable")
    cumulative = np.cumsum(w[order])
    quantiles = {str(q): float(y[order][min(np.searchsorted(cumulative, q, side="left"), len(y)-1)]) for q in [.1, .5, .9]}
    b = number(observed, "bmi")
    bc, yc = b-w@b, y-mean
    denominator = float(np.sqrt((w@(bc*bc))*(w@(yc*yc))))
    corr = float((w@(bc*yc))/denominator) if denominator > 0 else None
    return {"endpoints": endpoints, "fits": fits,
            "distribution": {"weighted_mean": mean, "weighted_sd_population": sd,
                             "weighted_quantiles_inverse_cdf": quantiles, "weighted_bmi_correlation": corr}}

def safe_path(relative):
    path = (PILOT/relative).resolve()
    require(path.is_relative_to(PILOT.resolve()), "Path escapes pilot")
    return path

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def scoped_path(value):
    path = Path(value).resolve()
    require(path.is_relative_to(PILOT.resolve()), "Provenance path escapes pilot")
    return path

def verify_commitment(commitment, required=(), within=None):
    require(isinstance(commitment, dict) and commitment, "Missing file commitment")
    canonical = {}
    for value, expected in commitment.items():
        path = scoped_path(value)
        require(path not in canonical, "Duplicate canonical commitment path")
        if within is not None:
            require(path.is_relative_to(within.resolve()), "Candidate commitment escapes construction")
        require(path.is_file() and sha(path) == expected, "Committed provenance file changed")
        canonical[path] = expected
    require(set(p.resolve() for p in required) <= set(canonical), "Required file absent from commitment")
    return canonical

def validate_provenance(release, entries):
    """Bind all slots to four run, review, candidate and execution receipts."""
    artifacts = release.get("artifacts", {})
    require(isinstance(artifacts, dict) and artifacts, "Release must bind provenance artifacts")
    registered = {}
    for value, digest in artifacts.items():
        path = safe_path(value)
        require(path not in registered, "Duplicate canonical artifact path")
        require(path.is_file() and sha(path) == digest, "Release artifact hash mismatch")
        registered[path] = digest
    def bound(path):
        path = path.resolve()
        require(path in registered and registered[path] == sha(path), "Unbound provenance artifact")
        return read_json(path)
    controller = PILOT/"loop_control.py"
    protocol_path = PILOT/"protocol.json"
    require(controller.resolve() in registered, "Controller not release-bound")
    protocol = bound(protocol_path)
    seeds = protocol.get("generation_seeds")
    require(seeds == [281001, 281002, 281003, 281004, 281005], "Protocol seed schedule changed")
    expected_runs = {"ordinary_1": "ordinary", "ordinary_2": "ordinary", "gap_1": "gap_policy", "gap_2": "gap_policy"}
    require({e["construction"] for e in entries} == set(expected_runs), "Unexpected construction directories")
    n_rows = read_json(PILOT/"shared/schema.json")["row_count"]
    paths = [safe_path(e["file"]) for e in entries]
    require(len(set(paths)) == 40, "Each output slot requires a distinct canonical path")
    by_slot = {(e["construction"], e["stage"], e["draw"]): e for e in entries}
    run_paths = [(PILOT/"runs"/name).resolve() for name in expected_runs]
    require(len(set(run_paths)) == 4, "Construction directories are not distinct")
    for construction, arm in expected_runs.items():
        run = (PILOT/"runs"/construction).resolve()
        require(run.is_relative_to((PILOT/"runs").resolve()), "Run path escapes construction root")
        cfg = bound(run/"run.json")
        require(cfg["policy"] == arm, "Run policy disagrees with assigned arm")
        observed = scoped_path(cfg["observed"])
        contract = scoped_path(cfg["contract"])
        require(observed == (PILOT/"shared/observed.csv").resolve(), "Run used different observed packet")
        require(scoped_path(cfg["protocol"]) == protocol_path.resolve(), "Run used different protocol")
        require(scoped_path(cfg["literature_session"]) == (run/"literature").resolve(), "Run used another literature session")
        gateway_config = PILOT/"tools/gateway_config.json"
        require(scoped_path(cfg["gateway_config"]) == gateway_config.resolve(), "Run used different gateway configuration")
        cfg_commitment = verify_commitment(cfg["commitment"], [observed, contract, protocol_path, controller, PILOT/"tools/literature_gateway.py", gateway_config])
        for p in cfg_commitment:
            require(p in registered, "Run input absent from release artifact map")
        receipt = bound(run/"review_receipt.json")
        require(receipt.get("execution_allowed") is True and receipt.get("no_reference_feedback") is True, "Initial review blocks or lacks blinding assertion")
        review_commitment = verify_commitment(receipt["commitment"], [run/"initial/freeze.json"])
        review_paths = set(review_commitment)-{(run/"initial/freeze.json").resolve()}
        require(len(review_paths) == 1, "Initial receipt must bind exactly one review document")
        initial_review = bound(next(iter(review_paths)))
        final_review = bound(run/"final_code_review.json")
        for stage, review in [("initial", initial_review), ("final", final_review)]:
            folder = run/stage
            require(review.get("execution_allowed") is True, "Candidate review blocks execution")
            for key, name in [("generator_sha256", "generator.py"), ("model_spec_sha256", "model_spec.json"),
                              ("evidence_sha256", "evidence.json"), ("candidate_freeze_sha256", "freeze.json")]:
                require(review.get(key) == sha(folder/name), "Review does not bind current candidate")
            frozen = bound(folder/"freeze.json")
            require(frozen.get("version") == stage and frozen.get("policy") == arm, "Candidate stage/policy mismatch")
            require(frozen.get("run_sha256") == sha(run/"run.json"), "Candidate bound to different run")
            require(frozen.get("run_commitment") == cfg["commitment"], "Candidate run commitment changed")
            required = [folder/name for name in ["generator.py", "model_spec.json", "evidence.json", "decision.md", "gateway_snapshot.json"]]
            if arm == "gap_policy":
                required += [folder/"gaps.json", folder/"actions.json"]
            if stage == "final":
                required += [folder/"revision.json"]
            verify_commitment(frozen["commitment"], required, within=run)
            snapshot = bound(folder/"gateway_snapshot.json")
            require(scoped_path(snapshot["session"]) == (run/"literature").resolve(), "Gateway snapshot uses different session")
            require(snapshot["config_sha256"] == sha(gateway_config), "Gateway configuration differs from snapshot")
            audit = (run/"literature/audit.jsonl").read_bytes()
            length = snapshot["audit_bytes"]
            require(isinstance(length, int) and length > 0 and len(audit) >= length, "Bad gateway snapshot extent")
            require(hashlib.sha256(audit[:length]).hexdigest() == snapshot["audit_prefix_sha256"], "Gateway audit prefix changed")
            execution = bound(folder/"outputs/execution.json")
            require(execution.get("version") == stage, "Execution stage mismatch")
            require(execution.get("controller_sha256") == sha(controller), "Execution controller mismatch")
            require(execution.get("run_sha256") == sha(run/"run.json"), "Execution run mismatch")
            require(execution.get("candidate_freeze_sha256") == sha(folder/"freeze.json"), "Execution candidate mismatch")
            require(execution.get("review_receipt_sha256") == sha(run/"review_receipt.json"), "Execution initial review mismatch")
            final_review_hash = sha(run/"final_code_review.json") if stage == "final" else None
            require(execution.get("final_code_review_sha256") == final_review_hash, "Execution final review mismatch")
            require(execution.get("observed_cells_preserved") is True and execution.get("same_seed_reproducible") is True, "Execution output contract failed")
            require(isinstance(execution.get("unique_generated_vectors"), int) and execution["unique_generated_vectors"] > 1, "Execution draw variability check failed")
            draws = execution.get("draws", [])
            require(len(draws) == 5 and [d["seed"] for d in draws] == seeds, "Execution seed schedule mismatch")
            for number, draw in enumerate(draws, 1):
                entry = by_slot[(construction, stage, number)]
                path = (folder/"outputs"/f"draw_{number:02d}.csv").resolve()
                require(scoped_path(draw["path"]) == path and safe_path(entry["file"]) == path, "Output slot bound to wrong execution path")
                require(entry["arm"] == arm and entry.get("seed") == draw["seed"], "Output slot policy/seed mismatch")
                require(draw["n_rows"] == n_rows, "Execution row count mismatch")
                require(entry["sha256"] == draw["sha256"] == sha(path), "Output slot hash disagrees with execution")

def validate_release(release):
    require(release.get("all_four_constructions_frozen") is True, "Missing all-four freeze assertion")
    require(release.get("root_authorized_evaluation") is True, "Root has not authorized evaluation")
    require(release.get("no_builder_access_to_target") is True, "Missing blinding assertion")
    require(release.get("analysis_spec_sha256") == sha(BASE/"analysis_spec.json"), "Analysis spec mismatch")
    require(release.get("evaluator_sha256") == sha(__file__), "Evaluator mismatch")
    entries = release.get("outputs", [])
    require(len(entries) == 40, "Expected 4 constructions x 2 stages x 5 draws")
    keys = [(e["construction"], e["stage"], e["draw"]) for e in entries]
    require(len(set(keys)) == 40, "Duplicate output slot")
    constructions = sorted(set(e["construction"] for e in entries))
    require(len(constructions) == 4, "Expected four constructions")
    arms = {}
    for construction in constructions:
        group = [e for e in entries if e["construction"] == construction]
        require({e["stage"] for e in group} == {"initial", "final"}, "Missing stage")
        require(len({e["arm"] for e in group}) == 1, "Conflicting arm")
        arms[construction] = group[0]["arm"]
        for stage in ["initial", "final"]:
            require({e["draw"] for e in group if e["stage"] == stage} == {1, 2, 3, 4, 5}, "Missing draw")
    require(list(arms.values()).count("ordinary") == 2 and list(arms.values()).count("gap_policy") == 2, "Require two constructions per arm")
    for entry in entries:
        require(sha(safe_path(entry["file"])) == entry["sha256"], "Generated output hash mismatch")
    validate_provenance(release, entries)
    return entries

def run(release_path):
    release = json.loads(Path(release_path).read_text(encoding="utf-8"))
    entries = validate_release(release)
    frozen = json.loads((BASE/"locked/freeze_manifest.json").read_text())
    for item in frozen["files"]:
        require(sha(safe_path(item["path"])) == item["sha256"], "Frozen custodian packet changed")
    observed = read_csv(PILOT/"shared/observed.csv")
    valid_observed(observed)
    generated = [(entry, match_generated(observed, read_csv(safe_path(entry["file"])))) for entry in entries]
    # Reference and design are read only after the release and every output pass.
    reference = read_csv(BASE/"locked/reference.csv")
    truth = match_generated(observed, reference)
    spine = read_csv(BASE/"locked/design_spine.csv")
    require(spine.design_id.is_unique, "Duplicate design ID")
    require((number(spine, "weight") > 0).all(), "Nonpositive full-spine weight")
    target_spine = spine[spine.in_target_domain == "1"].copy()
    require(target_spine.row_id.is_unique and set(target_spine.row_id) == set(observed.row_id), "Domain/spine mismatch")
    require((spine.loc[spine.in_target_domain == "0", "row_id"] == "").all(), "Unexpected out-of-domain row key")
    require(spine[["stratum", "psu"]].ne("").all().all(), "Missing design code")
    domain = target_spine.set_index("row_id").loc[observed.row_id].reset_index()
    spec = json.loads((BASE/"analysis_spec.json").read_text())
    reference_results = analyze(observed, truth, domain, spine, spec)
    by_endpoint = {x["endpoint"]: x for x in reference_results["endpoints"]}
    draw_results, differences = [], []
    for entry, values in generated:
        result = analyze(observed, values, domain, spine, spec)
        metadata = {key: entry[key] for key in ["construction", "arm", "stage", "draw"]}
        draw_results.append({**metadata, **result})
        for endpoint in result["endpoints"]:
            ref = by_endpoint[endpoint["endpoint"]]
            difference = endpoint["estimate"]-ref["estimate"]
            differences.append({**metadata, **endpoint, "true_estimate": ref["estimate"],
                                "true_ci95_low": ref["ci95_low"], "true_ci95_high": ref["ci95_high"],
                                "difference": difference, "absolute_difference": abs(difference)})
    table = pd.DataFrame(differences)
    summary = table.groupby(["construction", "arm", "stage", "endpoint"], sort=True).agg(
        generated_median=("estimate", "median"), generated_min=("estimate", "min"), generated_max=("estimate", "max"),
        median_difference=("difference", "median"), median_absolute_difference=("absolute_difference", "median"),
        true_estimate=("true_estimate", "first")).reset_index()
    initial = summary[summary.stage == "initial"].drop(columns="stage")
    final = summary[summary.stage == "final"].drop(columns="stage")
    paired = initial.merge(final, on=["construction", "arm", "endpoint"], suffixes=("_initial", "_final"), validate="one_to_one")
    paired["final_minus_initial_median_absolute_difference"] = paired.median_absolute_difference_final-paired.median_absolute_difference_initial
    results = BASE/"results"
    require(not results.exists(), "Evaluation results already exist; never silently overwrite")
    results.mkdir()
    table.to_csv(results/"all_endpoint_draws.csv", index=False)
    summary.to_csv(results/"endpoint_summary.csv", index=False)
    paired.to_csv(results/"initial_final_changes.csv", index=False)
    save(results/"analysis_results.json", {"reference": reference_results, "generated": draw_results,
        "release_manifest_sha256": sha(release_path), "spec_sha256": sha(BASE/"analysis_spec.json"),
        "limitations": [spec["claims"], spec["uncertainty"], "No inferential arm-superiority test or overall pass/fail is calculated.",
                        "All eight endpoints are reported, including disagreement and unsupported endpoints."]})
    print(json.dumps({"outputs_evaluated": len(entries), "endpoint_rows": len(table), "results_directory": str(results)}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    args = parser.parse_args()
    run(args.release)
