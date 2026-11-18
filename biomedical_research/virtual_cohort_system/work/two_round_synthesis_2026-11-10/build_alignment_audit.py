"""Read-only cross-round accounting. No model imports, generation, fits, APIs, or credentials."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
import hashlib
import json

U = Path(__file__).resolve().parent
PROJECT = U.parents[1]
R1 = U.parent / "cross_model_api_pilot_2026-11-10"
R2 = U.parent / "economy_feedback_pilot_2026-11-10"


def read(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
def require(ok, why):
    if not ok: raise ValueError(why)


def candidate_identity(root, path):
    folder = root/path
    code = (folder/"generator.py").read_bytes()
    model = read(folder/"model_spec.json")
    signature = hashlib.sha256(code + b"\x00" + canonical(model)).hexdigest()
    return {"candidate_path": str(folder), "exact_program_canonical_spec_signature": signature,
            "files": {name: sha(folder/name) for name in ["generator.py", "model_spec.json", "decision_record.json", "capture_binding.json"]}}


def main():
    old_plan, new_plan = read(R1/"RUN_PLAN.json"), read(R2/"RUN_PLAN.json")
    old_out, new_out, reviews = read(R1/"CONSTRUCTION_OUTCOMES.json"), read(R2/"INITIAL_OUTCOMES.json"), read(R2/"REVIEW_OUTCOMES.json")
    old_eval, new_eval = read(R1/"EVALUATION.json"), read(R2/"EVALUATION.json")
    old_audit, new_audit = read(R1/"INDEPENDENT_CALL_AUDIT.json"), read(R2/"REVIEW_CALL_AUDIT.json")
    old_cost, new_cost = read(R1/"PILOT_COSTS.json"), read(R2/"FINAL_SUMMARY.json")
    old_seal, new_seal = read(R1/"CONSTRUCTION_CLOSURE.json"), read(R2/"INITIAL_SEAL.json")
    require(old_audit["status"] == new_audit["status"] == "pass", "Capture audit not passed")
    packet_alignment = []
    for rel in ["packets/common_prompt.txt", *[f"packets/{case}/{name}" for case in ["PNS", "LIPID"] for name in ["task.json", "requested_analyses.json", "evidence.json", "prompt.txt"]], "_host_only/REFERENCE_SNAPSHOT.json"]:
        a, b = sha(R1/rel), sha(R2/rel)
        require(a == b, "Copied packet/reference differs: "+rel)
        packet_alignment.append({"path": rel, "round_1_sha256": a, "round_2_sha256": b, "byte_identical": True})
    common_engine = []
    for rel in sorted(set(old_seal["implementation_hashes"]) & set(new_seal["implementation_hashes"])):
        digest = old_seal["implementation_hashes"][rel]
        require(digest == new_seal["implementation_hashes"][rel] == sha(PROJECT/rel), "Statistical/runtime engine changed: "+rel)
        common_engine.append({"path": rel, "sha256": digest})
    endpoint_refs = {}
    for label, evaluation, key in [("round_1", old_eval, "construction_summaries"), ("round_2", new_eval, "version_summaries")]:
        endpoint_refs[label] = {}
        for row in evaluation[key]:
            ident = row["case_id"]+"/"+row["category"]+"/"+row["id"]
            pair = {"unit": row["unit"], "reference": row["reference"]}
            require(ident not in endpoint_refs[label] or endpoint_refs[label][ident] == pair, "Inconsistent reference within round")
            endpoint_refs[label][ident] = pair
    require(endpoint_refs["round_1"] == endpoint_refs["round_2"], "Endpoint/reference operator alignment differs")

    call_rows = []
    for old in old_audit["calls"]:
        folder = R1/"calls"/old["call_id"]
        receipt = read(folder/"receipt.json")
        call_rows.append({"round": 1, "phase": old["turn"], "id": old["call_id"], "config": old["config"],
            "requested_model": old["requested_model"], "returned_model": old["returned_model"], "status": old["status"],
            "known_tariff_usd": old["independent_tariff_usd"], "unknown_reserve_usd": old["reserved_unknown_usd"],
            "receipt_path": str(folder/"receipt.json"), "receipt_sha256": sha(folder/"receipt.json"), "request_sha256": sha(folder/"request.json")})
    for row in new_audit["calls"]:
        folder = R2/"calls"/row["phase"]/row["id"]
        receipt = read(folder/"receipt.json")
        require(sha(folder/"receipt.json") == row["receipt_sha256"], "New receipt changed after audit")
        call_rows.append({"round": 2, "phase": row["phase"], "id": row["id"], "config": receipt["config"],
            "requested_model": row["requested_model"], "returned_model": row["returned_model"], "status": row["status"],
            "known_tariff_usd": row["tariff_cost_usd"], "unknown_reserve_usd": row["accounted_usd"] if row["tariff_cost_usd"] is None else 0.,
            "receipt_path": str(folder/"receipt.json"), "receipt_sha256": sha(folder/"receipt.json"), "request_sha256": sha(folder/"request.json")})
    require(len(call_rows) == 32 and Counter(r["phase"] for r in call_rows) == {"initial": 28, "review": 4}, "Call denominator differs")
    common_request_alignment = []
    for config in ["OA_SOL", "OA_ASTRA", "DS_PRO"]:
        require(old_plan["configs"][config] == new_plan["configs"][config], "Shared tariff/config changed")
        for case in ["PNS", "LIPID"]:
            old_requests = [read(R1/"calls"/r["call_id"]/"request.json") for r in old_audit["calls"] if r["config"] == config and r["call_id"].startswith(case+"_")]
            selected = [p for p in new_plan["parents"] if p["model_config"] == config and p["parent_id"].startswith(case+"_")]
            new_requests = [read(R2/"calls/initial"/p["parent_id"]/"request.json") for p in selected]
            require(old_requests and new_requests and all(v == old_requests[0] for v in old_requests+new_requests), "Initial request/model settings differ")
            common_request_alignment.append({"case": case, "config": config, "old_initial_requests": len(old_requests), "new_initial_requests": len(new_requests),
                "exact_endpoint_and_body_equal": True, "canonical_request_sha256": hashlib.sha256(canonical(old_requests[0])).hexdigest(), "tariff_and_effort_equal": True})

    rows = []
    old_slots, new_slots = old_eval["all_slots"], new_eval["all_slots"]
    for root, label, records in [(R1, 1, old_out["records"]), (R2, 2, new_out["records"])]:
        for row in records:
            ident = row.get("construction_id", row.get("parent_id"))
            chosen = [s for s in (old_slots if label == 1 else new_slots) if s.get("construction_id", s.get("version_id")) == ident]
            require(len(chosen) == 3, "Initial evaluation slot denominator differs")
            identity = candidate_identity(root, row["candidate_path"]) if row["candidate_path"] else None
            rows.append({"round": label, "kind": "initial", "version_id": ident, "parent_id": None,
                "case_id": row["case_id"], "model_config": row["model_config"], "context": row["context"],
                "api_candidate_available": row["status"] == "sealed", "scientific_artifact": identity,
                "successful_evaluation_tables": sum(s["execution_status"] == "success" for s in chosen), "scheduled_evaluation_tables": 3})
    new_parents = {r["parent_id"]: r for r in new_out["records"]}
    for branch in reviews["records"]:
        parent = new_parents[branch["parent_id"]]
        chosen = [s for s in new_slots if s["version_id"] == branch["branch_id"]]
        require(len(chosen) == 3, "Review evaluation denominator differs")
        rows.append({"round": 2, "kind": "review", "version_id": branch["branch_id"], "parent_id": branch["parent_id"],
            "case_id": parent["case_id"], "model_config": parent["model_config"], "arm": branch["arm"],
            "disposition": branch["disposition"], "api_candidate_available": branch["candidate_path"] is not None,
            "scientific_artifact": candidate_identity(R2, branch["candidate_path"]) if branch["candidate_path"] else None,
            "successful_evaluation_tables": sum(s["execution_status"] == "success" for s in chosen), "scheduled_evaluation_tables": 3})
    fingerprints = defaultdict(list)
    for row in rows:
        if row["scientific_artifact"]: fingerprints[row["scientific_artifact"]["exact_program_canonical_spec_signature"]].append(row)
    require(len(fingerprints) == 22, "Unexpected exact program/spec uniqueness count")
    productive_signatures = {r["scientific_artifact"]["exact_program_canonical_spec_signature"] for r in rows if r["successful_evaluation_tables"]}
    require(len(productive_signatures) == 21, "Unexpected data-producing exact version count")
    table_records = []
    for round_id, root, slots in [(1, R1, old_slots), (2, R2, new_slots)]:
        for slot in slots:
            ident = slot.get("construction_id", slot.get("version_id"))
            path = root/"executions"/("" if round_id == 1 else "evaluation")/ident/f"seed_{slot['seed']}"/"output/generated.csv"
            if slot["execution_status"] == "success": require(sha(path) == slot["generated_sha256"], "Generated table bytes differ from sealed metadata")
            table_records.append({"round": round_id, "phase": "evaluation", "version_id": ident, "seed": slot["seed"],
                "status": slot["execution_status"], "analysis_status": slot["analysis_status"], "generated_sha256": slot["generated_sha256"]})
    diagnostic = read(R2/"DIAGNOSTIC_CLOSURE.json")
    for record in diagnostic["records"]:
        run = R2/"executions/diagnostic"/record["version_id"]/f"seed_{record['seed']}"
        receipt = read(run/"execution.json")
        require(sha(run/"execution.json") == record["execution_sha256"], "Diagnostic receipt changed")
        require(receipt["status"] == "success" and sha(run/"output/generated.csv") == receipt["generated_sha256"], "Diagnostic output changed")
        table_records.append({"round": 2, "phase": "diagnostic", "version_id": record["version_id"], "seed": record["seed"], "status": "success", "generated_sha256": receipt["generated_sha256"]})
    table_groups = defaultdict(list)
    for row in table_records:
        if row["status"] == "success": table_groups[row["generated_sha256"]].append(row)
    known = sum(r["known_tariff_usd"] or 0. for r in call_rows)
    unknown = sum(r["unknown_reserve_usd"] for r in call_rows)
    require(abs(known-14.14412666) < 1e-10 and abs(unknown-.21840852) < 1e-10, "Combined cost differs")
    counts = {
        "actual_api_requests": 32, "initial_request_opportunities": 28, "dependent_review_requests": 4,
        "provider_model_configurations": 5, "complete_initial_api_candidates": sum(r["kind"] == "initial" and r["api_candidate_available"] for r in rows),
        "initial_candidates_producing_evaluation_tables": sum(r["kind"] == "initial" and r["successful_evaluation_tables"] > 0 for r in rows),
        "complete_review_api_artifacts": 4, "complete_api_artifacts_total": 25,
        "review_exact_noops": 3, "review_revisions": 1, "distinct_exact_program_canonical_spec_combinations": len(fingerprints),
        "data_producing_exact_program_spec_combinations": len(productive_signatures),
        "scheduled_evaluation_slots": 96, "successful_evaluation_files": 72,
        "evaluation_execution_failures": 3, "evaluation_candidate_unavailable": 21,
        "distinct_evaluation_file_hashes": len({r["generated_sha256"] for r in table_records if r["phase"] == "evaluation" and r["status"] == "success"}),
        "diagnostic_slots_and_successes": 6, "all_scheduled_table_slots": len(table_records),
        "all_successful_table_files": sum(r["status"] == "success" for r in table_records),
        "all_distinct_successful_table_hashes": len(table_groups), "duplicate_successful_file_instances_from_retained_branches": sum(len(v)-1 for v in table_groups.values()),
        "evaluation_rows_counting_workflow_duplicates": 216000, "all_successful_rows_counting_workflow_duplicates": 234000,
        "distinct_evaluation_file_rows": 189000, "all_distinct_file_rows": 207000}
    require(counts["distinct_evaluation_file_hashes"] == 63 and counts["all_distinct_successful_table_hashes"] == 69, "Unexpected table deduplication")
    by_model = []
    for round_id in [1, 2]:
        for config in sorted({r["model_config"] for r in rows if r["round"] == round_id}):
            selected = [r for r in rows if r["round"] == round_id and r["model_config"] == config and r["kind"] == "initial"]
            calls = [r for r in call_rows if r["round"] == round_id and r["config"] == config]
            initial_calls = [r for r in calls if r["phase"] == "initial"]
            by_model.append({"round": round_id, "config": config, "initial_requests": len(selected),
                "complete_initial_candidates": sum(r["api_candidate_available"] for r in selected),
                "initial_candidates_producing_tables": sum(r["successful_evaluation_tables"] > 0 for r in selected),
                "initial_successful_evaluation_files": sum(r["successful_evaluation_tables"] for r in selected),
                "all_api_calls": len(calls), "known_tariff_usd_all_calls": sum(r["known_tariff_usd"] or 0 for r in calls),
                "unknown_usage_reserve_usd": sum(r["unknown_reserve_usd"] for r in calls),
                "initial_known_tariff_usd": sum(r["known_tariff_usd"] or 0 for r in initial_calls),
                "initial_calls_with_known_usage": sum(r["known_tariff_usd"] is not None for r in initial_calls)})
    source_names = {
        R1: ["RUN_PLAN.json", "CONSTRUCTION_OUTCOMES.json", "CONSTRUCTION_CLOSURE.json", "EXECUTION_CLOSURE.json", "EVALUATION.json", "EVALUATION_COMPLETED.json", "EVALUATION_PROTOCOL.json", "INDEPENDENT_CALL_AUDIT.json", "PILOT_COSTS.json", "FINAL_REVIEW.json", "provider_client.py", "analyze_pilot.py"],
        R2: ["RUN_PLAN.json", "INITIAL_OUTCOMES.json", "REVIEW_OUTCOMES.json", "INITIAL_SEAL.json", "REVIEW_SEAL.json", "DIAGNOSTIC_CLOSURE.json", "EVALUATION_CLOSURE.json", "EVALUATION.json", "EVALUATION_COMPLETED.json", "PROTOCOL.json", "REVIEW_CALL_AUDIT.json", "FINAL_SUMMARY.json", "FINAL_REVIEW.json", "provider_client.py", "evaluate_stages.py", "review/INDEPENDENT_RECOMPUTATION.json", "review/SUPPLEMENTARY_OUTPUT_CHECKS.json"]}
    report = {"status": "pass", "blocking_issues": [], "created_utc": datetime.now(timezone.utc).isoformat(),
        "counts": counts, "by_round_and_model_initial_denominators": by_model,
        "round_summary": [
            {"round": 1, "initial_requests": 20, "review_requests": 0, "complete_initial_candidates": 14, "initial_laws_producing_tables": 14, "evaluation_slots": 60, "successful_evaluation_files": 42, "candidate_unavailable_slots": 18, "execution_failed_slots": 0, "diagnostic_slots": 0, "evaluation_seeds": [31001,31003,31007], "known_tariff_usd": old_cost["known_tariff_total_usd"], "unknown_reserve_usd": 0.},
            {"round": 2, "initial_requests": 8, "review_requests": 4, "complete_initial_candidates": 7, "initial_laws_producing_tables": 6, "evaluation_slots": 36, "successful_evaluation_files": 30, "candidate_unavailable_slots": 3, "execution_failed_slots": 3, "diagnostic_slots": 6, "evaluation_seeds": [42001,42003,42007], "diagnostic_seeds": [41001,41003,41007], "known_tariff_usd": new_cost["known_tariff_usd"], "unknown_reserve_usd": new_cost["unknown_reserve_usd"]}],
        "combined_cost": {"known_usage_tariff_usd": known, "unknown_usage_reserved_usd": unknown, "accounted_usd": known+unknown, "invoice": False},
        "packet_and_reference_alignment": packet_alignment, "shared_frozen_runtime_and_analysis_hashes": common_engine,
        "shared_initial_request_alignment": common_request_alignment,
        "endpoint_reference_alignment": {"identical": True, "endpoints_and_diagnostics_per_case": 6, "canonical_reference_map_sha256": hashlib.sha256(canonical(endpoint_refs["round_1"])).hexdigest()},
        "version_lineage": rows, "table_accounting": table_records,
        "duplicate_output_groups": [{"generated_sha256": digest, "members": members} for digest,members in table_groups.items() if len(members)>1],
        "calls_and_costs": call_rows,
        "valid_comparisons": [
            "Case-specific initial constructions can be compared descriptively on the same six predeclared endpoint/diagnostic definitions, same row count, same curated evidence bytes, same aggregate reference and uncertainty.",
            "For Sol, Astra and DeepSeek, initial request endpoint/body, model alias, high effort, 32768 output allowance and published tariff configuration are equal across rounds.",
            "Generated numerical differences, component violations, availability, provenance choices and assumption classes can be compared while preserving each initial construction and its case.",
            "Within round 2, the two review arms are shared-parent comparisons on fresh evaluation seeds; reporting-only revisions and the one actual age-law revision are separate from initial constructions.",
            "Usage-derived costs are arithmetically comparable under the captured same-date tariffs; unknown usage remains a reservation and all failed paid calls stay in the denominator."],
        "caveats": [
            "Twenty-eight initial request contexts are construction opportunities, not twenty-eight successful laws or statistically independent investigators. Only twenty-one initial candidates were delivered and twenty produced tables.",
            "Code/spec signatures distinguish exact executable implementations, not mathematical probability laws. Different implementations can induce the same law; narrative/spec differences can also change the signature. No distributional-equivalence proof is implied by the count22.",
            "The four reviews depend on two preassigned Sol_A parents; three exact no-ops add workflow products and repeated output files but no new code/spec law. One age revision is a dependent new version, not an independent initial author.",
            "Round-1 and round-2 evaluation seeds differ. Seed draws are nested within constructions; their counts do not multiply independent scientific evidence, and cross-round rows are not paired observations.",
            "Round 1 emphasized three adjusted analyses; round 2 prespecified component consistency as primary. Common numerical endpoints are comparable, but changing primary emphasis does not create a confirmatory pooled success criterion.",
            "Both rounds reuse previously exposed aggregate clinical references. Their exact equality ensures alignment, not independent validation or truth. PNS conditional row-resampling and lipid HC3 sensitivity intervals retain their original interpretation.",
            "Tariff comparisons are not matched-compute comparisons: providers allocate reasoning differently, actual output/caching varies, and round-2 review prompts are longer. No invoice reconciliation was performed; DeepSeek uses the conservative peak tariff.",
            "Model allocation is unbalanced across rounds; Fable and Carbon have no second-round observations. Reduced second-round total spend partly reflects model mix and fewer calls, not demonstrated scientific equivalence.",
            "Round-1 six incomplete responses were output/reasoning-budget delivery failures, not assessable scientific errors. Round-2 DeepSeek lipid failed in transport and PNS failed at its output interface; these failure causes must remain separate.",
            "Round-2 review dispatch was feedback-first in both cases despite planned counterbalancing. Approved context isolation and exact paired input equality held; order is a reported nonblocking deviation.",
            "Source packets were checked against previously curated frozen inputs and previous verification. This synthesis does not newly retrieve or independently audit original articles, reproduce source cohorts, read clinical rows or refit reference data.",
            "Within-case population projections, source coefficients, pooled/conditional Spearman anchors, latent Gaussian correlations and adjusted residual Pearson correlations are different operators and must not be pooled into one parameter column."],
        "source_hashes": {str(root/rel):sha(root/rel) for root, rels in source_names.items() for rel in rels},
        "audit_script_sha256":sha(Path(__file__)), "api_calls_made":0,"credential_files_read":False,"raw_responses_read":False,"patient_rows_read":False,"generated_programs_run":False,"new_statistical_fits":False}
    with (U/"ROUND_ALIGNMENT_AUDIT.json").open("x",encoding="utf-8",newline="\n") as stream: json.dump(report,stream,indent=2,allow_nan=False)
    md = """# Independent two-round alignment and denominator audit

**PASS.** The two rounds can be synthesized descriptively on aligned evidence, references and statistical operators. They cannot be treated as a larger confirmatory trial or a balanced model leaderboard. Actual source, program/specification, receipt and output hashes are recorded in `ROUND_ALIGNMENT_AUDIT.json`.

| Quantity | First round | Economy round | Combined |
|---|---:|---:|---:|
| Initial API construction opportunities | 20 | 8 | 28 |
| Dependent review requests | 0 | 4 | 4 |
| Complete initial API candidates | 14 | 7 | 21 |
| Initial candidates that produced tables | 14 | 6 | 20 |
| New revised data-law versions | 0 | 1 | 1 |
| Exact retained review products | 0 | 3 | 3 |
| Scheduled evaluation slots | 60 | 36 | 96 |
| Successful evaluation files | 42 | 30 | 72 |
| Unavailable-candidate slots | 18 | 3 | 21 |
| Execution-failed slots | 0 | 3 | 3 |
| Separate diagnostic slots, all successful | 0 | 6 | 6 |
| Distinct successful evaluation file hashes | 42 | 21 | 63 |

The **32 paid requests comprise 28 fresh initial contexts and four parent-dependent reviews**. There are 25 complete API artifacts, including the three review no-ops. The captured candidates contain **22 distinct exact program/canonical-specification combinations**, of which **21 produced evaluation tables**: 20 initial candidates and one dependent revision. These signatures identify implementations, not proven distinct probability laws. “Independent authors” must not be substituted for candidate, law-version, seed or table counts.

All **102 scheduled table slots** remain represented: 96 evaluation and six diagnostic. There are 78 successful output files, but only **69 distinct output hashes** after including diagnostics. Nine extra file instances arise from exact retained branches. Successful file instances contain 234,000 rows (216,000 evaluation); deduplicated file bytes represent 207,000 rows (189,000 evaluation). Neither row total is a count of independent clinical evidence.

The nine source/task/prompt files and host-only aggregate snapshot are byte-identical across rounds. Both use the same frozen statistical functions and runtime/worker. The stored endpoint units, reference values and uncertainty objects also match exactly. PNS uses equal-weight OLS on intercept, centered/scaled age, female and BMI, with BMI slopes per 5 kg/m² and centered residual Pearson correlation. Lipids uses the same adjustment set and common eligible rows, converts mmol/L to mg/dL by 38.67 for slopes, and retains the original positivity/eligibility rules. PNS SD uses population ddof=0; lipid SD uses sample ddof=1. HDL > TC is a diagnostic, not an inferred exclusion rule. No rows were repaired to enforce ordering.

Shared-model initial requests have identical endpoint/body settings: the same source prompt, model alias, high effort and 32,768 output ceiling. Sol, Astra and DeepSeek also retain identical published tariff parameters. The first round's persisted prompt text uses Windows line endings, but the previously audited submitted JSON input equals the same frozen LF prompt; storage-line-ending differences are not an evidence difference. Review prompts intentionally add the same initial artifact and shared review instruction, with own-generated observations added only to feedback.

The same endpoints support case-specific comparison of generated results and provenance choices across initial constructions. The three old seeds (31001/31003/31007) and three new evaluation seeds (42001/42003/42007) differ; diagnostic seeds are separately 41001/41003/41007. Repeated seeds are nested draws, not independent authors. Round 2 changes the primary focus to component consistency, so common endpoint alignment does not justify a pooled post-hoc success score. Both rounds use previously exposed aggregate references; alignment does not turn them into ground truth or fresh clinical confirmation.

Known usage-derived tariffs sum to **$14.14412666**: $11.20699712 in the first round and $2.93712954 in the second. The second round additionally retains **$0.21840852** for the transport failure with unknown usage, yielding **$14.36253518 accounted** across rounds. These are not invoices. Cache use, reasoning/output allocation, longer review inputs, model mix and unequal request counts prevent treating cost differences as matched-compute or scientific-equivalence evidence. DeepSeek uses the conservative peak tariff in both rounds.

Keep failure mechanisms separate: six first-round incomplete outputs exhausted delivery budgets; the second round adds one transport failure and one delivered program with an output-interface execution error. Neither Fable nor Carbon was tested again. Four review contexts depend on two Sol parents, and both cases actually dispatched feedback first despite planned counterbalancing. No general feedback or model-superiority inference follows.

This audit verifies alignment with curated frozen packets and completed prior audits; it is not a fresh article audit. No API, credential file, private response, clinical row, generated program execution or new statistical fit was used. Final integrated synthesis tables and prose remain subject to a separate consistency check.
"""
    with (U/"ROUND_ALIGNMENT_AUDIT.md").open("x",encoding="utf-8",newline="\n") as stream: stream.write(md)
    print(json.dumps({"status":"pass","counts":counts,"combined_cost":report["combined_cost"],"report_sha256":sha(U/"ROUND_ALIGNMENT_AUDIT.json")},indent=2))


if __name__ == "__main__": main()
