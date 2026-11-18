"""Read-only independent audit of a closed captured API construction batch.

No credential load, provider SDK/client import, network, generated-code import,
or raw-response interpretation. Raw response files are hashed only. Run only
after the root confirms construction closure. Writes a new audit report.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import math
import ast

U = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def normalized(provider, usage):
    if provider == "openai":
        d = usage.get("input_tokens_details") or {}
        return {"input": usage.get("input_tokens"), "output": usage.get("output_tokens"),
                "cached": d.get("cached_tokens", 0), "cache_write": d.get("cache_write_tokens", 0),
                "reasoning": (usage.get("output_tokens_details") or {}).get("reasoning_tokens")}
    if provider == "anthropic":
        return {"input": usage.get("input_tokens"), "output": usage.get("output_tokens"),
                "cached": usage.get("cache_read_input_tokens", 0), "cache_write": usage.get("cache_creation_input_tokens", 0), "reasoning": None}
    if provider == "deepseek":
        return {"input": usage.get("prompt_tokens"), "output": usage.get("completion_tokens"),
                "cached": usage.get("prompt_cache_hit_tokens", (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)),
                "reasoning": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")}
    output, thoughts = usage.get("candidatesTokenCount"), usage.get("thoughtsTokenCount", 0)
    return {"input": usage.get("promptTokenCount"), "output": None if output is None else output + thoughts,
            "cached": usage.get("cachedContentTokenCount", 0), "reasoning": thoughts}

def independent_cost(config, counts):
    incoming, output = counts["input"], counts["output"]
    if incoming is None or output is None:
        return None
    cached = counts.get("cached", 0) or 0
    written = counts.get("cache_write", 0) or 0
    if config["provider"] == "anthropic":
        ordinary = incoming
    else:
        ordinary = incoming - cached - written
    assert min(incoming, output, ordinary, cached, written) >= 0
    return (ordinary * config["input_rate"] + cached * config["cached_rate"] +
            written * config.get("cache_write_rate", 0) + output * config["output_rate"]) / 1_000_000

def submitted_text(provider, body):
    if provider == "openai":
        return body["input"]
    if provider in {"deepseek", "anthropic"}:
        assert len([m for m in body["messages"] if m["role"] == "user"]) == 1
        return next(m["content"] for m in body["messages"] if m["role"] == "user")
    assert len(body["contents"]) == 1 and body["contents"][0]["role"] == "user"
    return body["contents"][0]["parts"][0]["text"]

def main():
    assert (U / "CONSTRUCTION_OUTCOMES.json").exists(), "Root has not closed construction outcomes"
    assert not (U / "RUNNING.lock").exists(), "Construction or execution is still active"
    plan = read(U / "RUN_PLAN.json")
    freeze = read(U / "LAUNCH_FREEZE.json")
    outcomes = read(U / "CONSTRUCTION_OUTCOMES.json")
    source = ast.parse((U / "provider_client.py").read_text(encoding="utf-8"))
    common_system = next(ast.literal_eval(n.value) for n in source.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SYSTEM" for t in n.targets))
    endpoints = {"openai": "https://api.openai.com/v1/responses", "deepseek": "https://api.deepseek.com/chat/completions", "anthropic": "https://api.anthropic.com/v1/messages"}
    issues, observations, calls = [], [], []
    def check(condition, message):
        if not condition:
            issues.append(message)
    check(sha(U / "RUN_PLAN.json") == freeze["run_plan_sha256"], "Run plan differs from launch freeze")
    for path, digest in freeze["implementation_and_packet_hashes"].items():
        check(sha(U / path) == digest, "Launch-frozen file changed: " + path)
    check(sha(U / freeze["review_path"]) == freeze["review_sha256"], "Independent launch review changed")
    slots = {s["construction_id"]: s for s in plan["constructions"]}
    final = {s["construction_id"]: s for s in outcomes["records"]}
    check(len(outcomes["records"]) == 20 and set(slots) == set(final), "Twenty outcome denominator differs from frozen plan")
    for folder in sorted((U / "calls").iterdir()):
        ident, turn = folder.name.rsplit("_", 1)
        check(ident in slots and turn in {"initial", "repair"}, "Unexpected paid call slot: " + folder.name)
        if ident not in slots:
            continue
        slot = slots[ident]
        config = plan["configs"][slot["model_config"]]
        provider = config["provider"]
        reservation = read(folder / "reservation.json")
        check(reservation["config"] == slot["model_config"] and reservation["provider"] == provider, "Reservation identity differs: " + folder.name)
        if not (folder / "receipt.json").exists():
            observations.append({"call_id": folder.name, "kind": "interrupted_reserved_no_resend"})
            calls.append({"call_id": folder.name, "provider": provider, "config": slot["model_config"], "turn": turn, "status": "interrupted", "independent_tariff_usd": None, "reserved_unknown_usd": reservation["reserved_usd"]})
            continue
        receipt = read(folder / "receipt.json")
        request = read(folder / "request.json")
        body = request["body"]
        text = submitted_text(provider, body)
        frozen_packet = (U / slot["prompt_path"]).read_bytes()
        check(receipt["call_id"] == folder.name and receipt["config"] == slot["model_config"] and receipt["provider"] == provider, "Receipt identity differs: " + folder.name)
        check(receipt["requested_model"] == config["model"] and receipt["tariff"] == config, "Frozen model/tariff differs: " + folder.name)
        check(config["model"] in request["endpoint"] if provider == "gemini" else body["model"] == config["model"], "Request model differs: " + folder.name)
        check(request["endpoint"] == ("https://generativelanguage.googleapis.com/v1beta/models/" + config["model"] + ":generateContent" if provider == "gemini" else endpoints[provider]), "Provider endpoint differs: " + folder.name)
        if provider == "openai":
            system, effort, maximum = body["instructions"], body["reasoning"]["effort"], body["max_output_tokens"]
            check(body["store"] is False and body["service_tier"] == "default", "OpenAI retention/tier differs: " + folder.name)
        elif provider == "deepseek":
            system, effort, maximum = body["messages"][0]["content"], body["reasoning_effort"], body["max_tokens"]
            check(body["thinking"] == {"type": "enabled"} and body["stream"] is False, "DeepSeek thinking/stream differs: " + folder.name)
        elif provider == "anthropic":
            system, effort, maximum = body["system"], body["output_config"]["effort"], body["max_tokens"]
            check(body["thinking"] == {"type": "adaptive"} and body["stream"] is False, "Claude thinking/stream differs: " + folder.name)
        else:
            system = body["systemInstruction"]["parts"][0]["text"]
            effort, maximum = body["generationConfig"]["thinkingConfig"]["thinkingLevel"], body["generationConfig"]["maxOutputTokens"]
        check(system == common_system and effort == config["effort"] and maximum == plan["maximum_output_tokens_per_call"], "Common instruction, effort or output budget differs: " + folder.name)
        expected_reserve = ((len(json.dumps(body, ensure_ascii=False).encode("utf-8")) + 4096) * max(config["input_rate"], config.get("cache_write_rate", 0)) + maximum * config["output_rate"]) / 1_000_000
        check(math.isclose(expected_reserve, reservation["reserved_usd"], abs_tol=1e-12), "Independent predispatch reservation differs: " + folder.name)
        check(not body.get("tools") and not body.get("previous_response_id") and not body.get("conversation"), "Unexpected request context/tools: " + folder.name)
        if turn == "initial":
            check(text.encode("utf-8") == frozen_packet, "Actual submitted initial prompt differs: " + folder.name)
        else:
            initial = read(U / "calls" / (ident + "_initial") / "receipt.json")
            check(initial.get("status") == "received" and initial.get("artifact_status") == "invalid", "Repair was not an eligible mechanical repair: " + folder.name)
            prefix = frozen_packet.decode("utf-8") + "\n\nMECHANICAL FORMAT/ABI REPAIR ONLY. Preserve your original scientific structure and numerical choices. Return the complete corrected JSON object. Do not introduce new scientific assumptions.\nDiagnostic: " + initial["mechanical_error"] + "\nYour original response:\n"
            check(text.startswith(prefix), "Mechanical repair instruction or source packet differs: " + folder.name)
            if text.startswith(prefix):
                original_text = text[len(prefix):].strip()
                if original_text.startswith("```") and original_text.endswith("```"):
                    original_text = original_text[original_text.find("\n") + 1:-3].strip()
                try:
                    original_artifact = json.loads(original_text)
                except (ValueError, TypeError):
                    observations.append({"call_id": folder.name, "kind": "initial_json_unparseable_no_exact_scientific_spec_comparison"})
                else:
                    if (folder / "artifact.json").exists() and isinstance(original_artifact, dict) and "model_spec" in original_artifact:
                        check(original_artifact["model_spec"] == read(folder / "artifact.json")["model_spec"], "Mechanical repair changed initial scientific model_spec: " + folder.name)
        for field, filename in [("prompt_sha256", "prompt.txt"), ("request_sha256", "request.json"), ("response_raw.json_sha256", "response_raw.json"), ("response_text.txt_sha256", "response_text.txt"), ("artifact.json_sha256", "artifact.json")]:
            if field in receipt:
                check(sha(folder / filename) == receipt[field], "Captured file hash differs: " + folder.name + "/" + filename)
        saved_prompt = (folder / "prompt.txt").read_bytes()
        check(saved_prompt.decode("utf-8").replace("\r\n", "\n") == text.replace("\r\n", "\n"), "Saved prompt content differs beyond newline encoding: " + folder.name)
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != receipt["prompt_sha256"]:
            observations.append({"call_id": folder.name, "kind": "persisted_prompt_newline_encoding_differs_from_submitted_text", "submitted_utf8_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "persisted_prompt_sha256": receipt["prompt_sha256"]})
        price = None
        counts = None
        public_thinking = None
        if receipt.get("usage_raw") is not None:
            counts = normalized(provider, receipt["usage_raw"])
            public_thinking = ((receipt["usage_raw"].get("output_tokens_details") or {}).get("thinking_tokens")
                               if provider == "anthropic" else counts.get("reasoning"))
            check(counts == receipt["usage"], "Normalized usage differs: " + folder.name)
            price = independent_cost(config, counts)
            details = (receipt["usage_raw"].get("input_tokens_details") or {}).get("cache_write_tokens_details") or {}
            check(not details.get("ttl_12h_tokens", 0), "Unexpected 12h OpenAI writes require tariff audit: " + folder.name)
        check(price is None and receipt.get("tariff_cost_usd") is None or price is not None and math.isclose(price, receipt.get("tariff_cost_usd", -1), rel_tol=1e-10, abs_tol=1e-12), "Independent usage cost differs: " + folder.name)
        returned = receipt.get("returned_model")
        identity = "exact" if returned == config["model"] else "dated_snapshot" if isinstance(returned, str) and returned.startswith(config["model"] + "-") else "different_or_unavailable"
        if identity == "different_or_unavailable":
            observations.append({"call_id": folder.name, "kind": "returned_model_requires_explicit_reporting", "requested": config["model"], "returned": returned})
        delivery = ("output_budget_delivery_failure" if receipt.get("stop_reason") in {"MAX_TOKENS", "max_tokens", "max_output_tokens", "length"}
                    else "artifact_delivered_pending_execution" if receipt.get("artifact_status") == "valid_structure_and_python_ast" and receipt.get("completion_status") == "completed"
                    else "mechanical_format_failure" if receipt.get("artifact_status") == "invalid" and receipt.get("status") == "received"
                    else "other_delivery_failure")
        total_output = counts["output"] if counts else None
        calls.append({"call_id": folder.name, "provider": provider, "config": slot["model_config"], "turn": turn, "status": receipt["status"], "stop_reason": receipt.get("stop_reason"), "delivery_classification": delivery, "scientific_correctness_from_delivery_status": "not_determined", "requested_model": config["model"], "returned_model": returned, "model_identity_relation": identity, "submitted_utf8_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "output_tokens_including_thinking": total_output, "public_thinking_tokens": public_thinking, "nonthinking_output_token_remainder": total_output - public_thinking if total_output is not None and public_thinking is not None else None, "thinking_fraction": public_thinking / total_output if total_output and public_thinking is not None else None, "independent_tariff_usd": price, "reserved_unknown_usd": reservation["reserved_usd"] if price is None else 0.0})
    for ident, outcome in final.items():
        if outcome["status"] == "failed":
            check(outcome["candidate_path"] is None, "Failed construction nominates candidate: " + ident)
            continue
        folder = U / outcome["candidate_path"]
        binding = read(folder / "capture_binding.json")
        check(binding["initial_call_id"] == ident + "_initial" and binding["selected_call_id"] in {ident + "_initial", ident + "_repair"}, "Candidate selected unrelated capture: " + ident)
        selected = U / "calls" / binding["selected_call_id"]
        artifact = read(selected / "artifact.json")
        receipt = read(selected / "receipt.json")
        check(binding["selected_artifact_sha256"] == sha(selected / "artifact.json") and binding["scientific_edits_by_host"] is False, "Candidate capture digest/host-edit status differs: " + ident)
        check(binding["repair_count"] == outcome["repair_count"], "Candidate repair count differs: " + ident)
        check(receipt.get("artifact_status") == "valid_structure_and_python_ast" and receipt.get("completion_status") == "completed", "Candidate selected incomplete artifact: " + ident)
        check((folder / "generator.py").read_bytes() == artifact["generator_py"].encode("utf-8"), "Candidate code differs: " + ident)
        check(read(folder / "model_spec.json") == {"task": read(U / slots[ident]["task_path"]), "model": artifact["model_spec"]}, "Candidate scientific settings differ: " + ident)
        check(read(folder / "decision_record.json") == artifact["decision_record"], "Candidate decision record differs: " + ident)
    totals = {}
    for provider, cap in plan["provider_caps_usd"].items():
        subset = [c for c in calls if c["provider"] == provider]
        known = sum(c["independent_tariff_usd"] or 0 for c in subset)
        unknown = sum(c["reserved_unknown_usd"] for c in subset)
        check(known + unknown <= cap + 1e-10, "Provider accounted ceiling exceeded: " + provider)
        check(math.isclose(known + unknown, outcomes["usage_accounted_usd"][provider], abs_tol=1e-10), "Construction cost ledger differs: " + provider)
        totals[provider] = {"initial_calls": sum(c["turn"] == "initial" for c in subset), "repair_calls": sum(c["turn"] == "repair" for c in subset), "known_tariff_usd": known, "unknown_usage_reserved_usd": unknown, "cap_usd": cap}
    if (U / "CONSTRUCTION_CLOSURE.json").exists():
        closure = read(U / "CONSTRUCTION_CLOSURE.json")
        for path, digest in closure["construction_history_files"].items():
            check(sha(U / path) == digest, "Closed construction history changed: " + path)
    value = {"kind": "independent_closed_api_capture_audit_v1", "created_utc": datetime.now(timezone.utc).isoformat(), "status": "pass" if not issues else "needs_review", "issues": issues, "observations": observations, "constructions": 20, "outcomes": dict(Counter(r["status"] for r in outcomes["records"])), "provider_totals": totals, "calls": calls, "run_plan_sha256": sha(U / "RUN_PLAN.json"), "construction_outcomes_sha256": sha(U / "CONSTRUCTION_OUTCOMES.json"), "auditor_sha256": sha(__file__), "raw_responses_interpreted": False, "hidden_reasoning_expanded": False, "credential_file_read": False, "provider_model_calls": 0, "generated_code_executed": False}
    with (U / "INDEPENDENT_CALL_AUDIT.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps({k: value[k] for k in ["status", "issues", "outcomes", "provider_totals"]}))

if __name__ == "__main__":
    main()
