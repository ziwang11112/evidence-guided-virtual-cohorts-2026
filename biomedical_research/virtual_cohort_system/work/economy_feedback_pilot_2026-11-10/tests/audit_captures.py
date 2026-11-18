"""Independent read-only closed-call audit. Never reads keys, raw text, or executes author code."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
TARIFF = {
    "OA_SOL": ("openai", "gpt-6.1-sol", 2., 10., .1, 2.5),
    "OA_ASTRA": ("openai", "gpt-6-astra", 10., 50., 1., 12.5),
    "DS_PRO": ("deepseek", "deepseek-v4-pro", 1.32, 3.96, .044, 0.),
}
CAPS = {"openai": 8., "deepseek": 2.}


def read(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok, message):
    if not ok: raise ValueError(message)
def close(a, b, label): require(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-10), label)


def expected_request(config, prompt):
    provider, model, *_ = TARIFF[config]
    system = "You are a scientific model author. Follow the supplied biomedical task and evidence boundary. Return the requested executable artifacts and concise scientific decision record, not a private reasoning transcript."
    if provider == "openai":
        return "https://api.openai.com/v1/responses", {"model": model, "instructions": system, "input": prompt,
            "store": False, "reasoning": {"effort": "high"}, "max_output_tokens": 32768, "service_tier": "default"}
    return "https://api.deepseek.com/chat/completions", {"model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "thinking": {"type": "enabled"}, "reasoning_effort": "high", "max_tokens": 32768, "stream": False}


def normalized(provider, raw):
    if provider == "openai":
        return {"input": raw.get("input_tokens"), "output": raw.get("output_tokens"),
                "cached": (raw.get("input_tokens_details") or {}).get("cached_tokens", 0),
                "cache_write": (raw.get("input_tokens_details") or {}).get("cache_write_tokens", 0),
                "reasoning": (raw.get("output_tokens_details") or {}).get("reasoning_tokens")}
    return {"input": raw.get("prompt_tokens"), "output": raw.get("completion_tokens"),
            "cached": raw.get("prompt_cache_hit_tokens", (raw.get("prompt_tokens_details") or {}).get("cached_tokens", 0)),
            "reasoning": (raw.get("completion_tokens_details") or {}).get("reasoning_tokens")}


def cost(config, usage):
    _, _, rate_i, rate_o, rate_c, rate_w = TARIFF[config]
    i, o = usage.get("input"), usage.get("output")
    if i is None or o is None: return None
    c, w = usage.get("cached", 0) or 0, usage.get("cache_write", 0) or 0
    require(all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in [i, o, c, w]), "Invalid usage")
    require(c + w <= i, "Cache tokens exceed input")
    return ((i-c-w)*rate_i + o*rate_o + c*rate_c + w*rate_w)/1e6


def candidate_matches(path, artifact, task, call_path):
    folder = ROOT/path
    require((folder/"generator.py").read_bytes() == artifact["generator_py"].encode("utf-8"), "Candidate generator differs: "+path)
    require(read(folder/"model_spec.json") == {"task": read(ROOT/task), "model": artifact["model_spec"]}, "Candidate model/task differs")
    require(read(folder/"decision_record.json") == artifact["decision_record"], "Candidate decision differs")
    require(read(folder/"capture_binding.json") == {"call_path": call_path,
        "artifact_sha256": sha(ROOT/call_path/"artifact.json"), "host_scientific_edits": False}, "Candidate capture binding differs")


def audit_review_inputs():
    sys.path.insert(0, str(ROOT))
    import execute_stages as host
    require(not (ROOT/"RUNNING.lock").exists(), "Active operation")
    host.verify_stage_closure("diagnostic")
    reports = host.verify_diagnostic_reports()
    sealed = host.verify_initial()
    parents = {r["parent_id"]: r for r in sealed["records"]}
    plan = read(ROOT/"RUN_PLAN.json")
    plan_parents = {p["parent_id"]: p for p in plan["parents"]}
    inputs = read(ROOT/"REVIEW_INPUTS.json")
    require(len(inputs["rows"]) == 4 and {r["branch_id"] for r in inputs["rows"]} == {b["branch_id"] for b in plan["branches"]}, "Review-input denominator differs")
    require(inputs["diagnostic_closure_sha256"] == sha(ROOT/"DIAGNOSTIC_CLOSURE.json"), "Diagnostic closure changed")
    initial_audit = read(ROOT/"INITIAL_CALL_AUDIT.json")
    require(initial_audit["status"] == "pass" and not initial_audit["blocking_issues"], "Initial captures not approved")
    for call in initial_audit["calls"]:
        require(call["receipt_sha256"] == sha(ROOT/"calls"/call["phase"]/call["id"]/"receipt.json"), "Initial audited receipt changed")
    selected = {r["branch_id"]: r for r in inputs["rows"]}
    observed = []
    def reject_reference_fields(value):
        if isinstance(value, dict):
            require(not ({"reference", "references", "signed_difference", "absolute_difference", "same_sign", "target_value", "desired_value", "recommended_parameter"} & set(value)), "Feedback contains target/comparison fields")
            for item in value.values(): reject_reference_fields(item)
        elif isinstance(value, list):
            for item in value: reject_reference_fields(item)
    for branch in plan["branches"]:
        row = selected[branch["branch_id"]]; parent = parents[branch["parent_id"]]
        require(all(row[k] == branch[k] for k in branch), "Branch identity changed")
        if parent["status"] == "failed":
            require(row["eligible"] is False and row["reason"] == "parent_failed" and row["prompt_path"] is None, "Unavailable parent substituted")
            observed.append(dict(branch, eligible=False)); continue
        require(row["eligible"] is True, "Delivered paired parent unexpectedly skipped")
        artifact_path = ROOT/"calls/initial"/parent["parent_id"]/"artifact.json"
        artifact = read(artifact_path)
        text = (ROOT/plan_parents[parent["parent_id"]]["prompt_path"]).read_text(encoding="utf-8")
        text += "\n\nREVIEW_TASK\n" + (ROOT/"REVIEW_INSTRUCTION.txt").read_text(encoding="utf-8")
        text += "\n\nYOUR_FROZEN_EARLIER_SUBMISSION\n" + json.dumps(artifact, ensure_ascii=False, separators=(",", ":"))
        require(row["initial_artifact_sha256"] == sha(artifact_path), "Initial artifact identity changed")
        if branch["arm"] == "feedback":
            entry = reports["reports"][parent["parent_id"]]
            require(row["diagnostic_path"] == entry["path"] and row["diagnostic_sha256"] == entry["sha256"], "Wrong own diagnostic report")
            payload = read(ROOT/entry["path"])
            require(payload["parent_id"] == parent["parent_id"] and payload["case_id"] == parent["case_id"], "Feedback parent/case changed")
            require(payload["scheduled_seeds"] == [41001, 41003, 41007] and payload["scheduled_rows_per_seed"] == 3000, "Diagnostic seeds/count changed")
            require(len(payload["diagnostics_by_seed"]) == 3 and {r["seed"] for r in payload["diagnostics_by_seed"]} == {41001, 41003, 41007}, "Feedback draw coverage differs")
            reject_reference_fields(payload)
            text += "\n\nRECORDED_OBSERVATIONS_OF_YOUR_OWN_GENERATOR\n" + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        else:
            require(branch["arm"] == "second_look" and row["diagnostic_path"] is None and row["diagnostic_sha256"] is None, "Ordinary arm received feedback")
        prompt_path = ROOT/row["prompt_path"]
        require(prompt_path.read_bytes() == text.encode("utf-8") and row["prompt_sha256"] == sha(prompt_path), "Review prompt is not exact authorized assembly")
        observed.append(dict(branch, eligible=True, prompt_sha256=sha(prompt_path), initial_artifact_sha256=sha(artifact_path)))
    result = {"status": "pass", "blocking_issues": [], "created_utc": datetime.now(timezone.utc).isoformat(),
              "review_inputs_sha256": sha(ROOT/"REVIEW_INPUTS.json"), "diagnostic_reports_sha256": sha(ROOT/"DIAGNOSTIC_REPORTS.json"),
              "initial_call_audit_sha256": sha(ROOT/"INITIAL_CALL_AUDIT.json"), "run_plan_sha256": sha(ROOT/"RUN_PLAN.json"),
              "rows": observed, "only_arm_difference": "Own generated diagnostic suffix; exact shared parent/source/review prefix",
              "api_requests_made": 0, "credential_files_read": False, "raw_responses_read": False, "generated_programs_executed": False,
              "audit_script_sha256": sha(Path(__file__))}
    with (ROOT/"REVIEW_INPUT_AUDIT.json").open("x", encoding="utf-8", newline="\n") as stream: json.dump(result, stream, indent=2, allow_nan=False)
    return {"status": "pass", "phase": "review-inputs", "eligible": sum(r["eligible"] for r in observed)}


def audit(phase):
    require(phase in {"initial", "review"}, "Unknown phase")
    require(not (ROOT/"RUNNING.lock").exists(), "Active operation")
    plan = read(ROOT/"RUN_PLAN.json")
    freeze = read(ROOT/"LAUNCH_FREEZE.json")
    require(freeze["run_plan_sha256"] == sha(ROOT/"RUN_PLAN.json"), "Run plan changed")
    for rel, digest in freeze["implementation_and_packet_hashes"].items():
        require(sha(ROOT/rel) == digest, "Frozen implementation/input changed: "+rel)
    parents = {p["parent_id"]: p for p in plan["parents"]}
    branches = {b["branch_id"]: b for b in plan["branches"]}
    specs = {("initial", k): p["model_config"] for k, p in parents.items()} | {("review", k): "OA_SOL" for k in branches}
    require(len(specs) == 12 and len(parents) == 8 and len(branches) == 4, "Changed opportunity count")
    if phase == "initial": require(not (ROOT/"calls/review").exists(), "Review started before initial audit")
    inputs = read(ROOT/"REVIEW_INPUTS.json") if phase == "review" else None
    input_rows = {r["branch_id"]: r for r in inputs["rows"]} if inputs else {}
    if phase == "review":
        approved_inputs = read(ROOT/"REVIEW_INPUT_AUDIT.json")
        require(approved_inputs["status"] == "pass" and not approved_inputs["blocking_issues"] and
                approved_inputs["review_inputs_sha256"] == sha(ROOT/"REVIEW_INPUTS.json"), "Review inputs changed since audit")
        approved_initial = read(ROOT/"INITIAL_CALL_AUDIT.json")
        require(approved_initial["status"] == "pass" and not approved_initial["blocking_issues"], "Initial capture audit unavailable")
        for call in approved_initial["calls"]:
            require(call["receipt_sha256"] == sha(ROOT/"calls"/call["phase"]/call["id"]/"receipt.json"), "Initial receipt changed after audit")
    rows, captures = [], {}
    totals = {p: 0. for p in CAPS}; known = {p: 0. for p in CAPS}
    for stage_dir in sorted((ROOT/"calls").iterdir()):
        require(stage_dir.is_dir() and stage_dir.name in {"initial", "review"}, "Unexpected call phase")
        for folder in sorted(stage_dir.iterdir()):
            identity = (stage_dir.name, folder.name)
            require(identity in specs and folder.is_dir(), "Unscheduled extra call")
            config = specs[identity]; provider, model, ri, ro, rc, rw = TARIFF[config]
            request, reservation = read(folder/"request.json"), read(folder/"reservation.json")
            receipt = read(folder/"receipt.json")
            rel = folder.relative_to(ROOT).as_posix()
            require(receipt["call_id"] == stage_dir.name+"/"+folder.name and receipt["config"] == config and receipt["provider"] == provider, "Wrong call identity")
            require(receipt["requested_model"] == model, "Requested model mismatch")
            require(receipt["tariff"] == plan["configs"][config], "Recorded tariff/config differs")
            require(set(p.name for p in folder.iterdir()) <= {"request.json", "reservation.json", "receipt.json", "prompt.txt", "response_raw.json", "response_text.txt", "artifact.json"}, "Unexpected persisted call file")
            if receipt.get("http_status") is not None and 200 <= receipt["http_status"] < 300:
                require(receipt.get("returned_model") == model, "Returned model mismatch: "+rel)
            prompt_path = ROOT/parents[folder.name]["prompt_path"] if stage_dir.name == "initial" else ROOT/input_rows[folder.name]["prompt_path"]
            prompt = prompt_path.read_text(encoding="utf-8")
            endpoint, body = expected_request(config, prompt)
            require(request == {"endpoint": endpoint, "body": body}, "Exact request/settings/prompt mismatch: "+rel)
            require((folder/"prompt.txt").read_bytes() == prompt.encode("utf-8"), "Persisted prompt not exact LF input")
            for key, name in [("request_sha256", "request.json"), ("prompt_sha256", "prompt.txt")]:
                require(receipt[key] == sha(folder/name), "Receipt hash differs")
            for name in ["response_raw.json", "response_text.txt", "artifact.json"]:
                if (folder/name).exists(): require(receipt.get(name+"_sha256") == sha(folder/name), "Capture hash differs: "+name)
            require(receipt["no_automatic_retry"] is True, "Retry flag differs")
            encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
            reserve = ((len(encoded)+4096)*max(ri, rw) + 32768*ro)/1e6
            require(len(encoded) <= 190000, "Input ceiling exceeded")
            require(reservation["provider"] == provider and reservation["config"] == config and reservation["provider_cap_usd"] == CAPS[provider], "Reservation identity/cap differs")
            close(reservation["reserved_usd"], reserve, "Reservation math differs")
            close(receipt["reserved_usd"], reserve, "Receipt reservation differs")
            require(reservation["previous_accounted_usd"] + reserve <= CAPS[provider]+1e-10, "Predispatch budget breach")
            estimate = None
            if receipt.get("usage_raw") is not None:
                usage = normalized(provider, receipt["usage_raw"])
                require(usage == receipt["usage"], "Usage normalization differs")
                estimate = cost(config, usage)
                require((estimate is None) == (receipt["tariff_cost_usd"] is None), "Cost availability differs")
                if estimate is not None: close(estimate, receipt["tariff_cost_usd"], "Tariff arithmetic differs")
            else: require(receipt.get("tariff_cost_usd") is None, "Charge without usage")
            require(not receipt.get("reservation_exceeded"), "Reservation exceeded; audit required")
            if estimate is not None:
                require(estimate <= reserve+1e-10, "Cost exceeds allowance")
                known[provider] += estimate
            totals[provider] += estimate if estimate is not None else reserve
            complete = receipt.get("status") == "received" and receipt.get("completion_status") == "completed" and receipt.get("artifact_status") == "valid_structure_and_python_ast"
            captures[identity] = {"receipt": receipt, "complete": complete, "path": rel}
            rows.append({"phase": stage_dir.name, "id": folder.name, "status": receipt["status"], "complete": complete,
                         "requested_model": model, "returned_model": receipt.get("returned_model"),
                         "started_utc": receipt.get("started_utc"), "ended_utc": receipt.get("ended_utc"),
                         "prompt_sha256": sha(folder/"prompt.txt"), "receipt_sha256": sha(folder/"receipt.json"),
                         "tariff_cost_usd": estimate, "accounted_usd": estimate if estimate is not None else reserve})
    require(len(rows) <= (8 if phase == "initial" else 12), "More calls than allowed")
    for provider in CAPS: require(totals[provider] <= CAPS[provider]+1e-10, "Provider cap exceeded")
    require(sum(totals.values()) <= 10+1e-10, "Total budget exceeded")
    initial = read(ROOT/"INITIAL_OUTCOMES.json")
    require(len(initial["records"]) == 8 and {r["parent_id"] for r in initial["records"]} == set(parents), "Initial denominator differs")
    initial_by_id = {r["parent_id"]: r for r in initial["records"]}
    for ident, outcome in initial_by_id.items():
        capture = captures.get(("initial", ident)); successful = capture is not None and capture["complete"]
        require((outcome["status"] == "sealed") == successful, "Initial availability mismatch")
        require(all(outcome[k] == parents[ident][k] for k in ["case_id", "model_config", "role", "task_path"]), "Initial identity changed")
        if successful:
            candidate_matches(outcome["candidate_path"], read(ROOT/capture["path"]/"artifact.json"), outcome["task_path"], capture["path"])
        else: require(outcome["candidate_path"] is None and bool(outcome["failure_reason"]), "Failed initial replaced or unexplained")
    if phase == "review":
        outcomes = read(ROOT/"REVIEW_OUTCOMES.json")["records"]
        require(len(outcomes) == 4 and {r["branch_id"] for r in outcomes} == set(branches), "Review denominator differs")
        for outcome in outcomes:
            ident = outcome["branch_id"]; assigned = branches[ident]; parent = initial_by_id[assigned["parent_id"]]
            require(all(outcome[k] == assigned[k] for k in assigned), "Review assignment changed")
            capture = captures.get(("review", ident))
            if parent["status"] == "failed":
                require(capture is None and outcome["disposition"] == "parent_failed" and outcome["candidate_path"] is None, "Failed parent substituted/called")
                continue
            artifact = read(ROOT/capture["path"]/"artifact.json") if capture and capture["complete"] else None
            declaration = artifact["decision_record"].get("review") if artifact else None
            valid = isinstance(declaration, dict) and declaration.get("action") in {"retain", "revise"} and all(k in declaration for k in ["changes_summary", "evidence_basis", "remaining_limits"])
            if not valid:
                require(outcome["disposition"] == "retained_review_failed" and outcome["candidate_path"] == parent["candidate_path"], "Failed review not explicitly retained")
                continue
            original = read(ROOT/"calls/initial"/assigned["parent_id"]/"artifact.json")
            same = artifact["generator_py"] == original["generator_py"] and artifact["model_spec"] == original["model_spec"]
            expected = "retained_noop" if same else "revised"
            require(outcome["disposition"] == expected, "Review disposition does not match scientific bytes")
            captured_path = "candidates/review/"+ident
            candidate_matches(captured_path, artifact, parent["task_path"], capture["path"])
            require(outcome["candidate_path"] == (parent["candidate_path"] if same else captured_path), "Final product lineage differs")
    actual_review_order = [r["id"] for r in sorted([r for r in rows if r["phase"] == "review"], key=lambda r: r["started_utc"] or "")]
    planned_review_order = [b["branch_id"] for b in plan["branches"]]
    dispatch_deviations = []
    if phase == "review" and actual_review_order != [i for i in planned_review_order if any(r["id"] == i and r["phase"] == "review" for r in rows)]:
        dispatch_deviations.append({"kind": "review_dispatch_order_differs_from_submission_order", "blocking": False,
            "planned_submission_order": planned_review_order, "recorded_call_start_order": actual_review_order,
            "cause": "Two review worker threads can reach pacing/reservation in a different order from submission.",
            "interpretation": "The frozen protocol's counterbalanced dispatch claim is not assumed from submission order. Each arm still used an independent fresh request and its audited exact shared-parent input. No rerun or replacement was made.",
            "timestamp_scope": "Receipt started_utc precedes the HTTP request; this is recorded client start order, not provider-side arrival or compute scheduling."})
    result = {"status": "pass", "blocking_issues": [], "phase": phase, "created_utc": datetime.now(timezone.utc).isoformat(),
        "scheduled_initial_opportunities": 8, "scheduled_review_opportunities": 4, "actual_calls_so_far": len(rows),
        "calls": rows, "usage_tariff_usd": known, "accounted_including_unknown_reserves_usd": totals,
        "total_accounted_usd": sum(totals.values()), "run_plan_sha256": sha(ROOT/"RUN_PLAN.json"),
        "freeze_sha256": sha(ROOT/"LAUNCH_FREEZE.json"), "audit_script_sha256": sha(Path(__file__)),
        "planned_review_submission_order": planned_review_order, "recorded_review_call_start_order": actual_review_order,
        "known_nonblocking_protocol_deviations": dispatch_deviations,
        "secret_review_scope": "Exact allowed request bodies contain no headers/credentials; credentials not read. Client redaction retained; raw response bytes hashed only, hidden reasoning not inspected. No claim of direct secret-value scanning.",
        "raw_response_content_inspected": False, "generated_programs_executed": False, "api_requests_made": 0}
    destination = ROOT/(phase.upper()+"_CALL_AUDIT.json")
    with destination.open("x", encoding="utf-8", newline="\n") as stream: json.dump(result, stream, indent=2, allow_nan=False)
    return {"status": "pass", "phase": phase, "actual_calls": len(rows), "total_accounted_usd": sum(totals.values()), "report": str(destination)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("phase", choices=["initial", "review", "review-inputs"])
    phase = parser.parse_args().phase
    print(json.dumps(audit_review_inputs() if phase == "review-inputs" else audit(phase), indent=2))
