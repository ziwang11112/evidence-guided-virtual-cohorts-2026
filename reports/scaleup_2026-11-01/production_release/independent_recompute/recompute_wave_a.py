"""Independent Wave A arithmetic from frozen prose/JSON contracts.

This module deliberately imports no project implementation. The prepare command
reads metadata only. The run command requires explicit coordinator authorization
and independently validates all twelve closures and the matching target reveal.
It never reads the production evaluator or production numerical results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_complex_dtype, is_numeric_dtype
from pandas.io.stata import StataMissingValue

HERE = Path(__file__).resolve().parent
RELEASE = HERE.parent
SCALEUP = RELEASE.parent
WORKSPACE = SCALEUP.parents[3]
LEDGER = WORKSPACE / "evcA" / "ledger"
CASES = ("K01", "K02")
CONSTRUCTORS = ("A01", "A02", "A03", "A04", "A05", "S01")
SEEDS = (2101, 2102, 2103)
STAGES = ("initial", "final")
GRID = (0.05, 0.10, 0.20, 0.30)
EPS = np.finfo(np.float64).eps
TINY = np.finfo(np.float64).tiny
Z95 = 1.959963984540054
ENDPOINTS = {
    "K01": ("K01-GLUCOSE-BMI", "K01-GLUCOSE-AGE", "K01-SEX-BMI"),
    "K02": ("K02-HDL-BMI", "K02-TC-BMI", "K02-LIPID-RESIDUAL"),
}
OUTCOMES = {"K01": ("glucose",), "K02": ("hdl_cholesterol", "total_cholesterol")}
SPEC_PATHS = {
    "K01": SCALEUP / "case_k01/analysis/K01_ANALYSIS_SPEC_v1.json",
    "K02": SCALEUP / "analysis/K02_ANALYSIS_SPEC_v0.json",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as handle:
        result = hashlib.file_digest(handle, "sha256").hexdigest()
    return result


def write_new_json(path, obj):
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def metadata():
    manifest_path = RELEASE / "evaluation/EVALUATION_MANIFEST.json"
    manifest = read_json(manifest_path)
    release = read_json(RELEASE / "GLOBAL_RELEASE.json")
    require(read_json(LEDGER / "release.json") == release, "Ledger/global release mismatch")
    require(manifest["policy"]["cases"] == list(CASES), "Case contract changed")
    require(manifest["policy"]["constructors"] == list(CONSTRUCTORS), "Constructor contract changed")
    require(manifest["policy"]["target_seeds"] == list(SEEDS), "Seeds changed")
    require(manifest["policy"]["complete_sensitivity_grid"] == list(GRID), "Grid changed")
    require(manifest["policy"]["fixed_target_report_slots"] == 72, "Slot count changed")
    require(manifest["policy"]["working_resolution"] == 0.1, "Working resolution changed")
    # Read and hash the allowed metadata, never the listed Python dependencies.
    commitments = {}
    for item in manifest["dependencies"]:
        path = Path(item["path"])
        if path.suffix.lower() in (".json", ".md"):
            require(file_hash(path) == item["sha256"], f"Metadata hash mismatch: {path}")
            commitments[str(path)] = item["sha256"]
    specs = {case: read_json(path) for case, path in SPEC_PATHS.items()}
    for case, spec in specs.items():
        require(tuple(x["id"] for x in spec["estimands"]) == ENDPOINTS[case], "Endpoints changed")
    mapping = read_json(SCALEUP / "case_k02/unit_mapping/APPROVED_MANIFEST.json")
    factors = {x["column"]: x["factor"] for x in mapping["columns"]}
    require(factors["hdl_cholesterol"] == factors["total_cholesterol"] == 38.67,
            "Approved lipid factor differs")
    return manifest, release, commitments, factors


def ledger_state(release, require_reveal=False):
    release_digest = digest(release)
    previous = release_digest
    events = []
    records = {f"{case}:{who}": {"stages": {}, "closed": None}
               for case in CASES for who in CONSTRUCTORS}
    wave = None
    reveal = None
    for index, path in enumerate(sorted((LEDGER / "events").glob("*.json"))):
        event = read_json(path)
        require(event["sequence"] == index and event["previous_sha256"] == previous,
                "Ledger sequence/hash chain differs")
        require(event["event_sha256"] == digest({k: v for k, v in event.items()
                                                if k != "event_sha256"}), "Event hash differs")
        previous = event["event_sha256"]
        events.append(event)
        kind, payload = event["kind"], event["payload"]
        if kind == "wave_closed":
            require(wave is None, "Repeated wave closure")
            wave = event
        elif kind == "target_reveal":
            require(reveal is None and wave is not None, "Repeated or premature reveal")
            reveal = event
        else:
            require(payload["key"] in records, "Unexpected constructor key")
            record = records[payload["key"]]
            if kind == "stage_bound":
                record["stages"].setdefault(payload["stage"], {})["binding"] = payload
            elif kind == "stage_finished":
                record["stages"].setdefault(payload["stage"], {})["result"] = payload
            elif kind == "constructor_closed":
                require(record["closed"] is None, "Repeated constructor closure")
                require(digest(payload["final_inventory"]) == payload["final_inventory_sha256"],
                        "Closed final inventory digest differs")
                record["closed"] = payload
                record["closed_sequence"] = index
    if require_reveal:
        require(all(x["closed"] is not None for x in records.values()), "All twelve closures required")
        require(wave is not None and reveal is not None, "Wave closure and target reveal required")
        require(all(x["closed_sequence"] < wave["sequence"] for x in records.values()),
                "Wave closure predates a constructor closure")
        closed = {key: record["closed"] for key, record in records.items()}
        require(wave["payload"]["closed_inventory"] == closed, "Wave inventory differs")
        require(wave["payload"]["closed_inventory_sha256"] == digest(closed), "Wave digest differs")
        require(wave["payload"]["final_target_slots"] == 36, "Final slots differ")
        require(wave["payload"]["reserved_initial_and_final_target_slots"] == 72, "All slots differ")
        require(reveal["payload"]["release_sha256"] == release_digest, "Reveal release differs")
        require(reveal["payload"]["closed_inventory_sha256"] == digest(closed), "Reveal inventory differs")
        require(reveal["payload"]["evaluator_code_sha256"] == release["designated_evaluator"]["sha256"],
                "Reveal evaluator commitment differs")
        require(reveal["payload"]["cases"] == list(CASES), "Reveal cases differ")
    return records, {"events": len(events), "ledger_head_sha256": previous,
                     "closed_count": sum(x["closed"] is not None for x in records.values()),
                     "wave_closed": wave is not None,
                     "reveal_receipt_sha256": None if reveal is None else reveal["event_sha256"],
                     "release_sha256": release_digest}


def unavailable(reason):
    return {"value": None, "available": False, "reason": reason,
            "hc3_se": None, "hc3_interval": None, "interval_reason": reason}


def eligibility(frame, case, role):
    numeric = ["age", "bmi", *OUTCOMES[case]]
    needed = set(numeric + ["sex"])
    require(needed <= set(frame.columns), "Missing analytical columns")
    require(not frame.columns.duplicated().any(), "Duplicate columns")
    for name in numeric:
        dtype = frame[name].dtype
        require(is_numeric_dtype(dtype) and not is_bool_dtype(dtype) and not is_complex_dtype(dtype),
                f"Malformed numeric schema: {name}")
    sex = frame["sex"]
    require((sex.isna() | sex.isin(["F", "M"])).all(), "Unknown nonmissing sex")
    arrays = {name: frame[name].to_numpy(dtype=np.float64, na_value=np.nan) for name in numeric}
    reasons = {f"nonfinite_{name}": ~np.isfinite(values) for name, values in arrays.items()}
    reasons["sex_missing"] = sex.isna().to_numpy()
    minimum = 40 if case == "K01" else 18
    reasons["age_below_minimum"] = np.isfinite(arrays["age"]) & (arrays["age"] < minimum)
    for name in ["bmi", *OUTCOMES[case]]:
        reasons[f"nonpositive_{name}"] = np.isfinite(arrays[name]) & (arrays[name] <= 0)
    excluded = np.logical_or.reduce(list(reasons.values()))
    counts = {name: int(mask.sum()) for name, mask in reasons.items()}
    info = {"input_n": len(frame), "eligible_n": int((~excluded).sum()),
            "excluded_n": int(excluded.sum()), "overlapping_exclusion_counts": counts,
            "age_minimum_inclusive": minimum, "common_rows": True,
            "filtering": "reference fixed eligibility" if role == "reference" else "whole-table guard"}
    if role == "generated":
        require(len(frame) == 5000, "Generated row count differs from 5000")
        require(set(frame.columns) == needed | {"id"}, "Generated column set differs")
        require(frame["id"].notna().all() and frame["id"].is_unique, "Invalid generated IDs")
        require(frame["id"].map(lambda x: isinstance(x, str) and bool(x.strip())).all(),
                "Generated IDs must be nonempty strings")
        require(not excluded.any(), "Generated ineligible rows: reject whole table")
    return frame.loc[~excluded].copy(), info


def design_matrix(frame, interaction=False):
    age = (frame["age"].to_numpy(dtype=float) - 50.0) / 10.0
    bmi = (frame["bmi"].to_numpy(dtype=float) - 25.0) / 5.0
    female = (frame["sex"] == "F").to_numpy(dtype=float)
    columns = [np.ones(len(frame)), age, female, bmi]
    if interaction:
        columns.append(female * bmi)
    return np.column_stack(columns)


def factor_design(x):
    u, singular, vt = np.linalg.svd(x, full_matrices=False)
    tolerance = max(x.shape) * EPS * singular[0]
    rank = int(np.sum(singular > tolerance))
    require(rank == x.shape[1], "Rank deficient design")
    inverse = (vt.T / singular) @ u.T
    leverage = np.sum(u * u, axis=1)
    require(np.isfinite(inverse).all() and np.isfinite(leverage).all(), "Nonfinite design arithmetic")
    return inverse, leverage, {"rank": rank, "columns": x.shape[1],
                               "rank_tolerance": float(tolerance)}


def fit_response(x, factor, y, reference):
    inverse, leverage, _ = factor
    if np.all(y == y[0]):
        return None, None, None, "Constant response"
    beta = inverse @ y
    residual = y - x @ beta
    require(np.isfinite(beta).all() and np.isfinite(residual).all(), "Nonfinite OLS arithmetic")
    residual_tolerance = 16 * EPS * max(x.shape) * max(float(np.linalg.norm(y)), TINY)
    variable_residual = float(np.linalg.norm(residual)) > residual_tolerance
    se = None
    reason = "Generated interval unavailable by contract"
    if reference:
        if not variable_residual:
            reason = "Numerically degenerate residuals"
        elif np.any(1 - leverage <= 64 * EPS):
            reason = "Near-unit leverage"
        else:
            influence = inverse * (residual / (1 - leverage))[None, :]
            covariance = influence @ influence.T
            variances = np.diag(covariance)
            if np.isfinite(covariance).all() and (variances >= 0).all():
                se = np.sqrt(variances)
                reason = None
            else:
                reason = "Nonfinite HC3 arithmetic"
    return beta, residual if variable_residual else None, se, reason


def endpoint_from_fit(fit, term):
    beta, _, se, reason = fit
    if beta is None:
        return unavailable(reason)
    estimate = float(beta[term])
    stderr = None if se is None else float(se[term])
    interval = None if stderr is None else [estimate - Z95 * stderr, estimate + Z95 * stderr]
    return {"value": estimate, "available": True, "reason": None,
            "hc3_se": stderr, "hc3_interval": interval, "interval_reason": reason}


def analyze(frame, case, role):
    result = {"case": case, "role": role, "endpoints": {e: unavailable("Not computed") for e in ENDPOINTS[case]},
              "eligibility": None, "reference_sample_sd": {}, "design": {}, "status": "unavailable"}
    try:
        eligible, info = eligibility(frame, case, role)
        result["eligibility"] = info
        if role == "reference":
            for name in OUTCOMES[case]:
                sd = float(eligible[name].std(ddof=1)) if len(eligible) > 1 else math.nan
                result["reference_sample_sd"][name] = sd if np.isfinite(sd) and sd > 0 else None
        require(len(eligible) > (5 if case == "K01" else 4), "Too few eligible rows")
        if case == "K01":
            require(set(eligible["sex"]) == {"F", "M"}, "Both sexes required")
        x = design_matrix(eligible)
        base = factor_design(x)
        result["design"]["base"] = base[2]
        if case == "K01":
            xi = design_matrix(eligible, True)
            interaction = factor_design(xi)
            result["design"]["interaction"] = interaction[2]
            y = eligible["glucose"].to_numpy(dtype=float)
            fit = fit_response(x, base, y, role == "reference")
            fit_i = fit_response(xi, interaction, y, role == "reference")
            result["endpoints"] = {
                ENDPOINTS[case][0]: endpoint_from_fit(fit, 3),
                ENDPOINTS[case][1]: endpoint_from_fit(fit, 1),
                ENDPOINTS[case][2]: endpoint_from_fit(fit_i, 4),
            }
        else:
            fits = {}
            for name in OUTCOMES[case]:
                try:
                    fits[name] = fit_response(x, base, eligible[name].to_numpy(dtype=float), role == "reference")
                except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
                    fits[name] = (None, None, None, str(error))
            result["endpoints"][ENDPOINTS[case][0]] = endpoint_from_fit(fits["hdl_cholesterol"], 3)
            result["endpoints"][ENDPOINTS[case][1]] = endpoint_from_fit(fits["total_cholesterol"], 3)
            residuals = [fits[name][1] for name in OUTCOMES[case]]
            if all(r is not None for r in residuals):
                centered = [r - r.mean() for r in residuals]
                norms = [float(np.linalg.norm(r)) for r in centered]
                rho = float(np.dot(centered[0] / norms[0], centered[1] / norms[1]))
                if np.isfinite(rho) and abs(rho) <= 1 + 64 * EPS:
                    result["endpoints"][ENDPOINTS[case][2]] = {
                        "value": float(np.clip(rho, -1, 1)), "available": True, "reason": None,
                        "hc3_se": None, "hc3_interval": None,
                        "interval_reason": "Residual-correlation interval unavailable by contract"}
                else:
                    result["endpoints"][ENDPOINTS[case][2]] = unavailable("Nonfinite residual correlation")
            else:
                result["endpoints"][ENDPOINTS[case][2]] = unavailable("Constant or degenerate residuals")
        result["status"] = "available" if all(e["available"] for e in result["endpoints"].values()) else "partly_unavailable"
    except (ValueError, TypeError, FloatingPointError, np.linalg.LinAlgError) as error:
        result["endpoints"] = {e: unavailable(str(error)) for e in ENDPOINTS[case]}
        result["error"] = str(error)
    return result


def load_reference(case, info):
    path = Path(info["path"])
    require(file_hash(path) == info["sha256"], "Measured-reference hash differs")
    mapping = info["raw_mapping"]
    if case == "K01":
        raw = pd.read_stata(path, columns=list(mapping), convert_categoricals=False, convert_missing=True)
        raw = raw.rename(columns=mapping)
        for name in ["age", "bmi", "glucose", "sex"]:
            raw[name] = raw[name].map(lambda x: np.nan if isinstance(x, StataMissingValue) else x)
            raw[name] = pd.to_numeric(raw[name], errors="raise")
        require((raw["sex"].isna() | raw["sex"].isin([1, 2])).all(), "Unexpected raw K01 sex code")
        raw["sex"] = raw["sex"].map({1: "M", 2: "F"})
    else:
        raw = pd.read_csv(path, sep="\t", encoding="utf-8-sig", dtype=str, keep_default_na=False,
                          usecols=list(mapping)).rename(columns=mapping)
        for name in raw.columns:
            raw[name] = raw[name].str.strip().replace({"": np.nan, "NA": np.nan})
        for name in ["age", "bmi", *OUTCOMES[case]]:
            raw[name] = pd.to_numeric(raw[name], errors="raise")
    require(len(raw) == info["rows_in_schema_audit"], "Reference row count differs")
    return raw


def stage_pass(entry):
    result = entry.get("result") or {}
    verified = result.get("verified") or {}
    bridge, guards = verified.get("bridge") or {}, verified.get("guards") or {}
    return bool(result.get("status") == "success" and not result.get("error_type")
                and bridge.get("all_planned_generation_links_verified") is True
                and bridge.get("all_planned_trials_successful") is True
                and guards.get("all_guards_valid") is True and guards.get("all_slots_successful") is True)


def resolve_slots(records):
    slots = []
    for case in CASES:
        for who in CONSTRUCTORS:
            record = records[f"{case}:{who}"]
            for stage in STAGES:
                closed = record["closed"]
                actual_stage = "initial" if stage == "final" and closed["decision"] == "retain" else stage
                entry = record["stages"].get(actual_stage, {})
                binding = entry.get("binding") or {}
                result = entry.get("result") or {}
                bridge = (result.get("verified") or {}).get("bridge") or {}
                observed = {x["trial_id"]: x for x in bridge.get("trials", []) if x["role"] == "target"}
                plan = {x["id"]: x for x in (binding.get("plan") or {}).get("trials", [])}
                inventory = {x["trial"]["seed"]: x for x in closed["final_inventory"] if x["role"] == "target"}
                require(set(inventory) == set(SEEDS), "Final seed inventory differs")
                for seed in SEEDS:
                    report_id = f"{case}_{who}_{stage}_target_{seed}"
                    actual_id = f"{case}_{who}_{actual_stage}_target_{seed}"
                    trial = observed.get(actual_id)
                    if stage == "final":
                        inv = inventory[seed]
                        require(inv["trial"]["id"] == report_id, "Final trial identity differs")
                        require(inv.get("verified_trial") == trial, "Final verified trial differs")
                        require(inv.get("alias_of") == (actual_id if actual_stage != stage else None), "Alias differs")
                    table_path = None
                    if trial is not None and trial.get("generated_table_sha256"):
                        require(actual_id in plan, "Generated target missing from plan")
                        context = trial["context_id"]
                        require(context.startswith("target_"), "Source context cannot be evaluated as target")
                        table_path = str(Path(binding["bundle"]) / "context_bridge_v1" / actual_stage /
                                         "contexts" / context / "bundle" / "executions" / actual_id /
                                         "output/generated.csv")
                    slots.append({"case": case, "constructor": who, "stage": stage, "seed": seed,
                                  "report_slot_id": report_id, "actual_trial_id": actual_id,
                                  "alias_of": actual_id if actual_stage != stage else None,
                                  "actual_stage": actual_stage, "whole_stage_pass": stage_pass(entry),
                                  "stage_status": result.get("status", "not_run"),
                                  "trial_status": None if trial is None else trial.get("status"),
                                  "table_path": table_path,
                                  "table_sha256": None if trial is None else trial.get("generated_table_sha256"),
                                  "generation_link_verified": bool(trial and trial.get("generation_link_verified"))})
    require(len(slots) == 72 and len({s["report_slot_id"] for s in slots}) == 72, "Slot inventory differs")
    return slots


def discrepancy(case, endpoint, virtual, reference):
    truth = reference["endpoints"][endpoint]["value"]
    estimate = virtual["endpoints"][endpoint]["value"]
    denominator = 1.0
    if case == "K01":
        denominator = reference["reference_sample_sd"].get("glucose")
    elif endpoint != "K02-LIPID-RESIDUAL":
        outcome = "hdl_cholesterol" if endpoint == "K02-HDL-BMI" else "total_cholesterol"
        denominator = reference["reference_sample_sd"].get(outcome)
    valid = truth is not None and estimate is not None and denominator is not None and denominator > 0
    raw = None if truth is None or estimate is None else estimate - truth
    scaled = abs(raw) / denominator if valid else None
    return {"reference": truth, "generated": estimate, "signed_difference": raw,
            "absolute_difference": None if raw is None else abs(raw), "denominator": denominator,
            "scaled_discrepancy": scaled,
            "reference_direction": None if truth is None else int(np.sign(truth)),
            "generated_direction": None if estimate is None else int(np.sign(estimate)),
            "pass_grid": {str(m): bool(scaled is not None and scaled <= m) for m in GRID}}


def run(reveal_receipt, output):
    manifest, release, commitments, factors = metadata()
    preparation = read_json(HERE / "PREPARATION_RECEIPT.json")
    require(preparation["script_sha256"] == file_hash(__file__), "Prepared independent script changed")
    require(preparation["metadata_commitments"] == commitments, "Prepared metadata changed")
    records, audit = ledger_state(release, require_reveal=True)
    require(reveal_receipt == audit["reveal_receipt_sha256"], "Explicit authorization receipt differs")
    require(not output.exists(), "Refusing to overwrite an independent numerical report")
    slots = resolve_slots(records)
    references = {case: analyze(load_reference(case, manifest["target_files"][case]), case, "reference") for case in CASES}
    unique = {}
    for slot in slots:
        cache_key = slot["actual_trial_id"]
        if cache_key not in unique:
            if slot["table_path"] is None:
                computation = {"status": "missing", "endpoints": {e: unavailable("No generated target table") for e in ENDPOINTS[slot["case"]]}, "eligibility": None}
            else:
                path = Path(slot["table_path"])
                try:
                    require(file_hash(path) == slot["table_sha256"], "Generated table hash differs")
                    frame = pd.read_csv(path, dtype={"id": str, "sex": str}, keep_default_na=True)
                    if slot["case"] == "K02":
                        for name in OUTCOMES["K02"]:
                            frame[name] = frame[name] * factors[name]
                    computation = analyze(frame, slot["case"], "generated")
                except (OSError, ValueError, TypeError) as error:
                    computation = {"status": "unavailable", "endpoints": {e: unavailable(str(error)) for e in ENDPOINTS[slot["case"]]}, "eligibility": None, "error": str(error)}
            unique[cache_key] = {"path": slot["table_path"], "sha256": slot["table_sha256"], "analysis": computation}
        analysis = unique[cache_key]["analysis"]
        slot["analysis_key"] = cache_key
        slot["comparisons"] = {e: discrepancy(slot["case"], e, analysis, references[slot["case"]]) for e in ENDPOINTS[slot["case"]]}
        slot["pass_grid"] = {str(m): bool(slot["whole_stage_pass"] and slot["generation_link_verified"]
                                          and slot["trial_status"] == "success"
                                          and analysis["status"] == "available"
                                          and all(c["pass_grid"][str(m)] for c in slot["comparisons"].values())) for m in GRID}
    bundles = []
    for case in CASES:
        for stage in STAGES:
            for who in CONSTRUCTORS:
                group = [s for s in slots if (s["case"], s["stage"], s["constructor"]) == (case, stage, who)]
                require(len(group) == 3, "Bundle missing seed")
                bundles.append({"case": case, "stage": stage, "constructor": who,
                                "retained_alias": all(s["alias_of"] is not None for s in group),
                                "pass_grid": {str(m): all(s["pass_grid"][str(m)] for s in group) for m in GRID}})
    case_results = {}
    for case in CASES:
        anchors = {}
        for endpoint in ENDPOINTS[case]:
            virtual_zero = {"endpoints": {endpoint: {"value": 0.0}}}
            anchors[endpoint] = discrepancy(case, endpoint, virtual_zero, references[case])
        reliability = {}
        for stage in STAGES:
            agents = [b for b in bundles if b["case"] == case and b["stage"] == stage and b["constructor"] != "S01"]
            reliability[stage] = {str(m): {"passing_agents": sum(b["pass_grid"][str(m)] for b in agents),
                                          "denominator": 5, "reliability_pass": sum(b["pass_grid"][str(m)] for b in agents) >= 4} for m in GRID}
        reference_available = all(x["available"] for x in references[case]["endpoints"].values())
        anchor_all_close = all(x["pass_grid"]["0.1"] for x in anchors.values())
        case_results[case] = {"zero_anchors": anchors, "zero_all_within_working_resolution": anchor_all_close,
                              "discriminating": reference_available and not anchor_all_close,
                              "reliability": reliability}
    gate = bool(case_results["K01"]["reliability"]["final"]["0.1"]["reliability_pass"] and case_results["K01"]["discriminating"])
    report = {"kind": "independent_wave_a_recomputation", "created_utc": datetime.now(timezone.utc).isoformat(),
              "independence": "Prepared from frozen specifications before raw/generated table access; no production mathematics or numerical results imported or read.",
              "script_sha256": file_hash(__file__), "metadata_commitments": commitments,
              "evaluation_manifest_sha256": file_hash(RELEASE / "evaluation/EVALUATION_MANIFEST.json"),
              "ledger_audit": audit, "runtime": {"numpy": np.__version__, "pandas": pd.__version__},
              "references": references, "unique_target_analyses": unique, "report_slots": slots,
              "constructor_bundles": bundles, "case_results": case_results,
              "positive_wave_a_gate": gate, "wave_b_automatic_execution": False,
              "working_resolution": 0.1, "sensitivity_grid": list(GRID),
              "unique_target_output_count": sum(x["path"] is not None for x in unique.values()),
              "report_slot_count": len(slots), "alias_slot_count": sum(s["alias_of"] is not None for s in slots)}
    write_new_json(output, report)
    receipt = {"report_path": str(output), "report_sha256": file_hash(output),
               "created_utc": datetime.now(timezone.utc).isoformat(), "production_results_read": False}
    write_new_json(output.with_name(output.stem + "_COMMITMENT.json"), receipt)
    print(json.dumps(receipt))


def prepare():
    _, release, commitments, _ = metadata()
    _, audit = ledger_state(release)
    receipt = {"kind": "independent_specification_only_preparation", "created_utc": datetime.now(timezone.utc).isoformat(),
               "script_sha256": file_hash(__file__), "metadata_commitments": commitments,
               "ledger_metadata_status": audit, "raw_data_read": False, "generated_tables_read": False,
               "production_mathematics_read": False, "production_results_read": False,
               "readiness": "Ready for coordinator-authorized execution after all twelve closures and matching target reveal",
               "ambiguities": ["Overlapping exclusion-count labels are not individually named in the JSON specifications; this verifier uses explicit nonfinite-variable, missing-sex, below-age, and nonpositive-variable counts."]}
    write_new_json(HERE / "PREPARATION_RECEIPT.json", receipt)
    print(json.dumps({k: v for k, v in receipt.items() if k != "metadata_commitments"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare", help="Metadata only: pin independent script and approved contracts")
    execute = sub.add_parser("run", help="Only after explicit coordinator authorization")
    execute.add_argument("--authorized-reveal-receipt", required=True)
    execute.add_argument("--output", type=Path, default=HERE / "INDEPENDENT_WAVE_A_RESULTS.json")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    else:
        run(args.authorized_reveal_receipt, args.output)
