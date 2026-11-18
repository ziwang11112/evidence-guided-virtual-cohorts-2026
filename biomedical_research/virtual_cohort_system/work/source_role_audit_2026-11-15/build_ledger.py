"""Extend the frozen provenance maps without reading rows or executing authors.

The annotations below are root judgments after reading original programs and
decision entries. They are not keyword classifications or independent human labels.
"""
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / "work/two_round_synthesis_2026-11-10"

# Explicit, reviewable coding. No target estimate or error is used by this script.
# id: group, parameter-map entry, original provenance entries, scientific reading.
ANNOTATIONS = {
    "PNS_OA_ASTRA_C1": ("scenario_completion", "residual_law", [10, 11],
        "Independent DBP and pulse-pressure innovations induce SBP-DBP dependence; no source identifies these loadings."),
    "PNS_DS_PRO_C1": ("marginal_covariance_decomposition", "residual_law", [6, 7],
        "Transport Beijing marginal covariance, subtract the covariance of assumed means, then store fixed residual SD/rho. Arithmetic does not identify target applicability."),
    "PNS_OA_SOL_C1": ("scenario_completion", "residual_law", [10, 11, 12],
        "Residual rho 0.55 is explicitly a scenario informed by context, not equality to a reported raw correlation."),
    "PNS_OA_ASTRA_C2": ("marginal_covariance_decomposition", "residual_law", [8, 9, 10],
        "Source raw covariance minus assumed reference mean covariance sets innovations. The omitted age hinge means innovation rho is not requested OLS residual rho."),
    "PNS_DS_PRO_C2": ("scenario_completion", "residual_law", [5, 6],
        "Residual rho 0.50 and SDs are disclosed choices contextualized by Beijing, not reported conditional estimates."),
    "PNS_OA_SOL_C2": ("scenario_completion", "residual_law", [14, 15, 16],
        "Shared and specific uniform factor loadings imply residual rho 0.48; the loadings are assumed."),
    "PNS_SOL_A": ("scenario_completion", "residual_law", [6, 7],
        "The fixed mixing rows imply rho 0.60; the source does not identify this conditional relationship."),
    "PNS_DS": ("scenario_completion", "residual_law", [8, 9, 10, 11],
        "Fixed bivariate normal error law is an assumption. Output indexing failed historically; this is not a delivered cohort."),
    "PNS_SOL_B": ("marginal_covariance_decomposition", "residual_law", [10, 11],
        "The pulse-pressure identity plus subtraction of modeled mean covariance is valid algebra under an explicit transport and composition assumption."),
    "PNS_ASTRA": ("scenario_completion", "residual_law", [10, 11],
        "Assumed shared factors imply rho 5/13; an additional omitted-score mean shifts BMI projections. Neither is reported target evidence."),
    "LIPID_OA_ASTRA_C1": ("gaussian_copula_rank_within_sex", "core_2", [8, 9, 10],
        "Source pooled Spearman values are Gaussian-copula anchors within each sex. The within-sex transfer is explicitly assumed; raw adjusted rho is a different functional."),
    "LIPID_DS_PRO_C1": ("rank_to_residual_assumption", "core_3", [14],
        "Mean of two source Spearman values, rounded to 0.14, is assumed to be residual Pearson rho. The program implements that choice; the record acknowledges the unsupported bridge."),
    "LIPID_CL_FABLE_C1": ("judgment_residual_or_component", "core_3", [14],
        "A judgment compromise selects raw residual rho 0.35; the latent-normal conversion implements it. Differently defined source statistics do not by themselves establish a source conflict."),
    "LIPID_OA_SOL_C1": ("scenario_completion", "core_2", [9],
        "The source rank-to-residual substitution is explicitly rejected. Assumed loadings 0.5 and 0.3 nevertheless imply rho 0.15."),
    "LIPID_OA_ASTRA_C2": ("gaussian_copula_rank_within_sex", "core_2", [7, 8],
        "The valid rank-to-latent identity is combined with an explicit pooled-to-within-sex transport assumption; adjusted projections remain separate."),
    "LIPID_DS_PRO_C2": ("rank_to_residual_assumption", "core_3", [6],
        "A chosen rho 0.12 informs normal proposals. Outcome-dependent positive-pair rejection changes the final conditional law; the claimed exact final residual rho is not established."),
    "LIPID_CL_FABLE_C2": ("judgment_residual_or_component", "core_3", [9],
        "Judgment selects zero HDL/non-HDL residual correlation. TC=HDL+non-HDL then has nonzero TC/HDL correlation; zero is not the requested analysis value."),
    "LIPID_OA_SOL_C2": ("gaussian_copula_rank_unconditional", "core_2", [0, 6, 7],
        "Reported unadjusted ranks constrain unconditional copula entries; assumed demographic edges determine adjusted projections. No direct rank-to-residual equality is asserted."),
    "LIPID_SOL_A": ("gaussian_copula_rank_within_sex", "lipid_rank_block", [8],
        "The source rural rank triple is transported into within-sex copulas; the extra conditioning assumption is explicit."),
    "LIPID_SOL_B": ("gaussian_copula_rank_unconditional", "lipid_rank_block", [0, 6],
        "Unconditional source ranks become latent Gaussian entries; margins and demographic dependencies complete the target scenario."),
    "LIPID_ASTRA": ("gaussian_copula_rank_unconditional", "lipid_rank_block", [6],
        "Unconditional source ranks are preserved under continuous monotone margins; requested adjusted projections are explicitly different operators."),
}

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def pointer(obj, path):
    for token in path.lstrip("/").split("/") if path else []:
        token = token.replace("~1", "/").replace("~0", "~")
        obj = obj[int(token)] if isinstance(obj, list) else obj[token]
    return obj

bindings = {}
def bind(path):
    path = Path(path)
    key = path.relative_to(ROOT).as_posix()
    bindings[key] = {"path": key, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

records = []
for filename in ("PNS_PARAMETER_MAP.json", "LIPID_PARAMETER_MAP.json"):
    path = OLD / filename
    bind(path)
    records.extend(load_json(path)["records"])
attempt_path = OLD / "ATTEMPTS.csv"
bind(attempt_path)
attempts = list(csv.DictReader(attempt_path.open(encoding="utf-8-sig", newline="")))
by_attempt = {(x["round"], x["version_id"]): x for x in attempts}
complete = [r for r in records if r["kind"] == "initial" and r["parameters"]]
assert {r["version_id"] for r in complete} == set(ANNOTATIONS), "Explicit roster mismatch"

# The existing map's 80 parameter entries are checked for resolvable locators;
# they are not all reclassified as dependence decisions.
checks = []
for r in records:
    for param in r["parameters"]:
        for locator in param["locators"]:
            check = {"version_id": r["version_id"], "parameter_id": param["parameter_id"], "locator": locator}
            try:
                path_part, sep, fragment = locator.partition("#")
                line = None
                match = re.fullmatch(r"(.+):(\d+)", path_part)
                if match:
                    path_part, line = match.group(1), int(match.group(2))
                path = ROOT / path_part
                bind(path)
                if sep:
                    pointer(load_json(path), fragment)
                if line is not None:
                    assert 1 <= line <= len(path.read_text(encoding="utf-8-sig").splitlines())
                check["resolves"] = True
            except (OSError, KeyError, ValueError, IndexError, AssertionError) as error:
                check["resolves"] = False
                check["error"] = str(error)
            checks.append(check)

ledger = []
for r in complete:
    cid = r["version_id"]
    group, pid, entry_indices, judgment = ANNOTATIONS[cid]
    param = next(p for p in r["parameters"] if p["parameter_id"] == pid)
    selected_paths = {Path(p).name: ROOT / p for p in r["artifact_paths"]
                      if p.endswith(("generator.py", "model_spec.json", "decision_record.json"))}
    for path in selected_paths.values():
        bind(path)
    decision_path = selected_paths["decision_record.json"]
    decision = load_json(decision_path)
    excerpts = [{"pointer": f"/parameter_provenance/{i}", "entry": decision["parameter_provenance"][i]}
                for i in entry_indices]
    attempt = by_attempt[(r["round"], cid)]
    row = {
        "round": r["round"], "version_id": cid, "case_id": r["case_id"],
        "law_delivery": attempt["law_delivery"],
        "unit": "one primary residual-dependence construction decision per complete initial artifact",
        "method_group": group,
        "original_parameter_map_entry": pid,
        "source_operator": param["source_operator"],
        "source_ids": param["source_ids"],
        "source_reported_value": param["source_reported_value"],
        "implemented_input": param["value"],
        "source_to_model_operation": param["transformation"],
        "transport_assumptions": param["transport_assumptions"],
        "requested_analysis": "residual_correlation" if r["case_id"] == "PNS" else "K02-LIPID-RESIDUAL",
        "directly_identified_by_admitted_evidence": False,
        "assumption_or_gap_disclosed": True,
        "disclosure_is_failure": False,
        "source_and_transport_uncertainty_sampled_across_laws": False,
        "fixed_scenario_allowed_by_original_task": True,
        "target_agreement_judged_in_this_unit": False,
        "root_reading": judgment,
        "mathematical_claim_issue": "postselection_endpoint_identity_not_established" if cid == "LIPID_DS_PRO_C2" else None,
        "comparability_wording_issue": "Different source operators are described as conflicting without an established common estimand." if cid in ("LIPID_CL_FABLE_C1", "LIPID_CL_FABLE_C2") else None,
        "decision_path": decision_path.relative_to(ROOT).as_posix(),
        "decision_evidence": excerpts,
        "code_path": selected_paths["generator.py"].relative_to(ROOT).as_posix(),
        "locators": param["locators"],
        "review_status": "root_code_and_record_audit_not_independent_human_adjudication",
    }
    if cid == "LIPID_DS_PRO_C2":
        row["unsupported_endpoint_claims"] = decision["requested_estimands"]
    ledger.append(row)

delivered = [x for x in ledger if x["law_delivery"] == "delivered"]
summary = {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Closed two-round roster; focus on primary dependence decisions. No clinical outcomes imported into this coding table.",
    "coder_exposure": "Root has previously seen clinical results. This is outcome-excluded coding, not a blinded independent study.",
    "original_papers_reauthenticated": False,
    "independent_human_reviewers": 0,
    "new_api_calls": 0, "generator_runs": 0, "patient_refits": 0,
    "counts": {
        "initial_attempts": sum(a["kind"] == "initial" for a in attempts),
        "complete_initial_artifacts": len(ledger),
        "delivering_initial_laws": len(delivered),
        "complete_but_execution_failed": sum(x["law_delivery"] != "delivered" for x in ledger),
        "incomplete_initial_attempts": sum(a["kind"] == "initial" for a in attempts)-len(ledger),
        "dependent_review_versions": sum(a["kind"] == "review" for a in attempts),
        "existing_parameter_map_entries": sum(len(r["parameters"]) for r in records),
        "delivered_primary_dependence_decisions_with_disclosed_assumptions": sum(x["assumption_or_gap_disclosed"] for x in delivered),
        "delivered_primary_dependence_decisions_directly_identified_by_packet": sum(x["directly_identified_by_admitted_evidence"] for x in delivered),
        "delivered_fixed_scenarios": len(delivered),
        "delivered_method_groups": dict(Counter(x["method_group"] for x in delivered)),
        "locator_checks": len(checks),
        "unresolved_locators": sum(not x["resolves"] for x in checks),
    },
    "interpretation": [
        "Twenty disclosures are not twenty errors: the task permits explicitly assumed scenarios.",
        "Rank-to-latent, marginal-to-conditional, component-to-total and proposal-to-output relationships require different judgments.",
        "No calibrated target-confidence ranking or causal source-error mechanism was established.",
        "The prior 17/18 direct-adoption claim remains unverified; this ledger uses a different, explicitly defined unit and complete roster.",
    ],
}
HERE.mkdir(parents=True, exist_ok=True)
def write_json(name, obj):
    (HERE/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
write_json("DEPENDENCE_DECISION_LEDGER.json", ledger)
write_json("SUMMARY.json", summary)
write_json("INPUT_BINDINGS.json", list(bindings.values()))
write_json("LOCATOR_CHECKS.json", checks)
with (HERE/"DEPENDENCE_DECISION_LEDGER.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    cols = ["round", "version_id", "case_id", "law_delivery", "method_group", "source_operator", "source_to_model_operation", "root_reading", "mathematical_claim_issue", "comparability_wording_issue", "decision_path", "code_path"]
    writer = csv.DictWriter(handle, fieldnames=cols, extrasaction="ignore")
    writer.writeheader(); writer.writerows(ledger)
with (HERE/"ATTEMPT_COVERAGE.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    cols = ["round", "version_id", "case_id", "kind", "parent_version_id", "api_artifact_status", "law_delivery"]
    writer = csv.DictWriter(handle, fieldnames=cols, extrasaction="ignore")
    writer.writeheader(); writer.writerows(attempts)
print(json.dumps(summary["counts"], ensure_ascii=False, indent=2))
for failure in (x for x in checks if not x["resolves"]):
    print("UNRESOLVED", json.dumps(failure, ensure_ascii=False))
