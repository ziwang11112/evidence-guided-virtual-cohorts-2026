"""Metadata-only scale-up readiness checks. No execution or reference-data API."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re

CAMPAIGN = "biomedical_scaleup_2026-11-01"
SEEDS = (2101, 2102, 2103)
CASES = ("K01", "K02", "K03", "K04")
ARMS = {"agent_evidence_guided": tuple(f"A{i:02d}" for i in range(1, 6)),
        "statistical_reference": ("S01",)}
GATES = {"all_case_ids_resolved", "exposure_and_overlap_review", "applicable_evidence_admitted",
         "scientific_use_criteria_frozen", "reference_arm_specified", "case_adapters_reviewed",
         "campaign_orchestrator_reviewed", "global_contracts_frozen", "separate_target_access_gate"}
LIMIT = 1_048_576  # Metadata/code only; no participant-table reads.
HASH = re.compile(r"[0-9a-f]{64}")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{2,95}")


class NotReady(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise NotReady(message)


def exact(value, keys, label):
    require(isinstance(value, dict) and set(value) == set(keys), f"Invalid {label} fields")


def nonempty(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"Missing {label}")


def integer(value, expected, label):
    require(type(value) is int and value == expected, f"Wrong {label}")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def hash_value(value):
    require(isinstance(value, str) and HASH.fullmatch(value), "Invalid SHA256")


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "Duplicate JSON key")
        out[key] = value
    return out


def _constant(_):
    raise NotReady("Nonfinite JSON constant")


def _float(value):
    result = float(value)
    require(math.isfinite(result), "Nonfinite JSON number")
    return result


def decode(data):
    try:
        value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_pairs, parse_constant=_constant,
                           parse_float=_float)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise NotReady("Invalid metadata JSON") from error
    require(isinstance(value, dict), "Metadata JSON must be an object")
    return value


def linked(path):
    return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)())


class Reader:
    """Explicit bounded paths only; deliberately no glob or recursive discovery."""
    def __init__(self, root):
        raw = Path(root)
        require(".." not in raw.parts, "Project root traversal")
        self.root = Path(os.path.abspath(raw))
        require(all(not linked(p) for p in (self.root, *self.root.parents)), "Linked project root")
        require(self.root.is_dir(), "Missing project root")
        self.reads = []

    def path(self, relative, suffixes):
        nonempty(relative, "relative artifact path")
        require(not any(c in relative for c in '\\:\x00<>"|?*') and
                all(ord(c) >= 32 for c in relative), "Unsafe artifact path")
        parts = relative.split("/")
        devices = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
                   *(f"lpt{i}" for i in range(1, 10))}
        require(all(p not in {"", ".", ".."} and not p.endswith((".", " ")) and
                    p.split(".")[0].casefold() not in devices for p in parts), "Unsafe artifact path")
        require(Path(parts[-1]).suffix in suffixes, "Only declared metadata/code file types are accepted")
        path = self.root
        for part in parts:
            path /= part
            require(not linked(path), "Linked artifact path")
        require(path.resolve().is_relative_to(self.root), "Artifact escapes project")
        require(path.is_file(), "Missing declared artifact")
        require(path.stat().st_nlink == 1, "Hard-linked artifact rejected")
        return path

    def read(self, relative, suffixes=(".json",)):
        path = self.path(relative, suffixes)
        require(path.stat().st_size <= LIMIT, "Metadata/code size limit exceeded")
        with path.open("rb") as stream:
            data = stream.read(LIMIT + 1)
        require(len(data) <= LIMIT, "Metadata/code size limit exceeded")
        self.reads.append(relative)
        return data

    def ref(self, reference, *, suffixes=(".json",), parse=True):
        exact(reference, {"path", "sha256"}, "artifact reference")
        hash_value(reference["sha256"])
        data = self.read(reference["path"], suffixes)
        require(digest(data) == reference["sha256"], "Declared artifact hash mismatch")
        return decode(data) if parse else data


def inventory(plan):
    require(plan["campaign_id"] == CAMPAIGN, "Wrong campaign")
    require(plan["entry_regime"] == "whole_cohort_no_individual_input", "Wrong information regime")
    budget = plan["budget"]
    fixed = {"cohorts": 4, "agent_constructions_per_cohort": 5, "statistical_constructions_per_cohort": 1,
             "source_feedback_rounds_per_construction": 1, "rows_per_table": 5000,
             "target_table_slots": 144, "extra_simulation_calibration_calls": 0,
             "primary_analyses_per_cohort": 3, "maximum_secondary_analyses_per_cohort": 2,
             "max_agent_design_feedback_turns": 40, "minimum_intended_distinct_study_families": 3,
             "new_candidate_family_ceiling": 6, "new_primary_study_deep_read_ceiling": 12}
    for key, expected in fixed.items():
        integer(budget[key], expected, key)
    require(budget["seeds"] == list(SEEDS) and all(type(x) is int for x in budget["seeds"]), "Wrong seed schedule")
    require(all(budget[key] is False for key in ("paid_api", "training", "hpc", "new_scheduler")),
            "Unreleased resource capability")
    require(budget["hard_start_cutoff"] == "2026-11-14 America/Chicago", "Start cutoff changed")
    require(set(plan["required_release"]) == GATES and len(plan["required_release"]) == len(GATES),
            "Release requirements changed")
    cohorts = plan["cohorts"]
    require(isinstance(cohorts, list) and len(cohorts) == 4 and
            {c["cohort_slot"] for c in cohorts} == set(CASES), "Wrong cohort slots")
    for c in cohorts:
        require(c["wave"] == ("A" if c["cohort_slot"] in CASES[:2] else "B"), "Wrong cohort wave")
    expected = {(c, arm, a, stage, seed) for c in CASES for arm, ids in ARMS.items()
                for a in ids for stage in ("initial", "final") for seed in SEEDS}
    slots = plan["slots"]
    require(isinstance(slots, list) and len(slots) == 144, "Wrong slot count")
    observed, by_id = set(), {}
    for slot in slots:
        key = tuple(slot[k] for k in ("cohort_slot", "method_arm", "construction_id", "stage", "seed"))
        require(type(slot["seed"]) is int and key in expected and key not in observed, "Invalid/duplicate scientific slot")
        observed.add(key)
        canonical = f"{key[0]}_{key[2]}_{key[3]}_{key[4]}"
        require(slot["slot_id"] == canonical and canonical not in by_id, "Invalid/duplicate slot ID")
        by_id[canonical] = slot
        integer(slot["rows"], 5000, "slot rows")
        require(slot["wave"] == ("A" if key[0] in CASES[:2] else "B"), "Wrong slot wave")
        require(slot["evidence_access"] == "case_admitted_external_packet_only", "Invalid evidence access")
        status = slot["status"]
        require(status in {"planned_not_released", "ready", "not_run", "success", "failed", "retained"}, "Invalid slot status")
        if status in {"success", "failed"}:
            hash_value(slot["candidate_hash"])
            nonempty(slot["execution_id"], "execution ID")
            require(slot["retained_from"] is None, "Executed slot cannot be an alias")
            if status == "success":
                hash_value(slot["output_hash"])
            else:
                require(slot["output_hash"] is None, "Failed slot cannot nominate scientific output")
        elif status == "retained":
            require(slot["stage"] == "final" and slot["execution_id"] is None, "Alias must be an unexecuted final slot")
            hash_value(slot["candidate_hash"])
            hash_value(slot["output_hash"])
        else:
            require(all(slot[k] is None for k in ("candidate_hash", "execution_id", "output_hash", "retained_from")),
                    "Unexecuted slot has execution material")
    require(observed == expected, "Incomplete scientific schedule")
    run_ids = [s["execution_id"] for s in slots if s["execution_id"] is not None]
    require(len(run_ids) == len(set(run_ids)), "Duplicate execution ID")
    for slot in slots:
        if slot["status"] == "retained":
            origin_id = f"{slot['cohort_slot']}_{slot['construction_id']}_initial_{slot['seed']}"
            require(slot["retained_from"] == origin_id, "Alias crosses construction/stage/seed")
            origin = by_id[origin_id]
            require(origin["status"] == "success" and origin["method_arm"] == slot["method_arm"] and
                    all(slot[k] == origin[k] for k in ("candidate_hash", "output_hash")), "Alias does not bind successful initial output")
    groups = {}
    for slot in slots:
        key = tuple(slot[k] for k in ("cohort_slot", "method_arm", "construction_id", "stage"))
        groups.setdefault(key, []).append(slot)
    for group in groups.values():
        hashes = {s["candidate_hash"] for s in group if s["candidate_hash"] is not None}
        require(len(hashes) <= 1, "Multiple candidates within one construction stage")
        statuses = {s["status"] for s in group}
        require(not ("retained" in statuses and statuses & {"success", "failed"}),
                "A final stage mixes retention and new execution")
    statuses = Counter(s["status"] for s in slots)
    computed = {"planned_cohorts": 4, "admitted_cohorts": sum(c["admission_status"] == "admitted" for c in cohorts),
                "planned_agent_constructions": 20, "planned_statistical_constructions": 4,
                "maximum_statistical_fit_instances": 8, "planned_candidate_stages": 48, "planned_slots": 144,
                "attempted_slots": statuses["success"] + statuses["failed"], "successful_slots": statuses["success"],
                "failed_slots": statuses["failed"], "not_run_slots": sum(statuses[s] for s in ("planned_not_released", "ready", "not_run")),
                "retained_aliases": statuses["retained"],
                "unique_outputs": len({s["output_hash"] for s in slots if s["output_hash"] is not None})}
    exact(plan["counts"], computed, "counts")
    for key, count in computed.items():
        integer(plan["counts"][key], count, "count " + key)
    return computed


def admissions(plan):
    require(plan["execution_enabled"] is True and plan["campaign_status"] == "released", "Campaign execution release disabled")
    identities, families = set(), set()
    for case in plan["cohorts"]:
        identity = case["actual_case_id"]
        require(isinstance(identity, str) and IDENTIFIER.fullmatch(identity), "Unresolved actual case ID")
        normalized = identity.casefold()
        require(normalized not in {x.casefold() for x in CASES} and
                not any(t in normalized for t in ("placeholder", "unassigned", "tbd", "chns-2009", "chns_2009")),
                "Placeholder or closed CHNS 2009 case")
        require(normalized not in identities, "Duplicate actual case ID")
        identities.add(normalized)
        require(case["admission_status"] == "admitted" and case["reference_exposure_status"] in
                {"unexposed", "qualified_after_prospective_exclusions"}, "Case lacks reviewed exposure qualification")
        nonempty(case["study_family"], "study family")
        families.add(case["study_family"].strip().casefold())
        nonempty(case["authorized_release"], "case release ID")
        for key in ("task_contract", "evidence_packet", "analysis_plan"):
            exact(case[key], {"path", "sha256"}, key)
    require(len(families) >= 3, "Fewer than three study families")


def analysis_ids(value, label):
    require(isinstance(value, list), f"Invalid {label}")
    for item in value:
        require(isinstance(item, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", item),
                f"Invalid {label} ID")
    require(len(value) == len({x.casefold() for x in value}), f"Duplicate {label} ID")
    return set(value)


def exposure_scopes(value):
    require(isinstance(value, list), "Exposure/exclusion scope must be a list")
    scopes = {}
    for item in value:
        exact(item, {"scope_id", "description", "analysis_ids"}, "exposure/exclusion scope")
        nonempty(item["scope_id"], "scope ID")
        nonempty(item["description"], "scope description")
        identifier = item["scope_id"].strip().casefold()
        require(identifier not in scopes, "Duplicate exposure/exclusion scope")
        scopes[identifier] = {x.casefold() for x in analysis_ids(item["analysis_ids"], "scope analysis")}
    return scopes


def exposure_review(review, case, analysis):
    """Check a reviewed scope declaration, not the scientific truth of independence."""
    exact(review, {"schema_version", "case_id", "classification", "decision", "independent", "reviewer_id",
                   "coordinator_id", "reviewed_utc", "reason", "prospective_exclusions_applied",
                   "approved_primary_analysis_ids", "exposed_scope", "excluded_scope"}, "exposure review")
    integer(review["schema_version"], 1, "exposure review version")
    require(review["case_id"] == case["actual_case_id"] and
            review["classification"] == case["reference_exposure_status"], "Exposure qualification identity mismatch")
    require(review["decision"] == "approved" and review["independent"] is True, "Exposure qualification lacks independent approval")
    for key in ("reviewer_id", "coordinator_id", "reviewed_utc", "reason"):
        nonempty(review[key], "exposure review " + key)
    require(review["reviewer_id"].strip().casefold() != review["coordinator_id"].strip().casefold(),
            "Exposure reviewer is coordinator")
    planned = analysis_ids(analysis["primary_analysis_ids"], "planned primary analysis")
    approved = analysis_ids(review["approved_primary_analysis_ids"], "approved primary analysis")
    require(len(planned) == 3 and approved == planned, "Exposure approval does not match all planned primary analyses")
    exposed = exposure_scopes(review["exposed_scope"])
    excluded = exposure_scopes(review["excluded_scope"])
    protected = {x.casefold() for x in approved}
    require(all(not protected & ids for ids in (*exposed.values(), *excluded.values())),
            "Approved primary analyses intersect exposed/excluded analyses")
    if review["classification"] == "unexposed":
        require(not exposed and not excluded and review["prospective_exclusions_applied"] is False,
                "Unexposed classification hides exposure/exclusions")
    else:
        require(bool(exposed) and bool(excluded) and review["prospective_exclusions_applied"] is True,
                "Qualified case lacks explicit prospective exclusions")
        require(set(exposed) <= set(excluded) and all(ids <= excluded[key] for key, ids in exposed.items()),
                "Exposed/overlapping scope is not fully mapped to declared exclusions")


def released_metadata(reader, plan, plan_bytes, release):
    exact(release, {"schema_version", "campaign_id", "status", "plan_sha256", "design", "feedback_engine",
                    "required_gates", "cases", "independent_review"}, "readiness release")
    integer(release["schema_version"], 1, "release version")
    require(release["campaign_id"] == CAMPAIGN and release["status"] == "released", "Readiness release disabled")
    require(release["plan_sha256"] == digest(plan_bytes), "Readiness release binds a different plan")
    review = reader.ref(release["independent_review"])
    exact(review, {"schema_version", "decision", "independent", "reviewer_id", "coordinator_id", "reviewed_utc",
                   "reason", "approved_release"}, "independent review")
    integer(review["schema_version"], 1, "review version")
    require(review["decision"] == "approved" and review["independent"] is True, "Release lacks independent approval")
    for key in ("reviewer_id", "coordinator_id", "reviewed_utc", "reason"):
        nonempty(review[key], key)
    require(review["reviewer_id"].strip().casefold() != review["coordinator_id"].strip().casefold(), "Reviewer is coordinator")
    require(review["approved_release"] == {k: v for k, v in release.items() if k != "independent_review"}, "Review does not bind release")
    require(release["design"]["sha256"] == plan["design_sha256"], "Wrong design commitment")
    reader.ref(release["design"], suffixes=(".md",), parse=False)
    exact(release["feedback_engine"], {"name", "artifact", "legacy_fallback"}, "feedback engine")
    engine = release["feedback_engine"]
    require(engine["name"] == "semantic_feedback_v1" and engine["legacy_fallback"] is False and
            engine["artifact"]["path"] == "cohort_harness/semantic_feedback_v1.py", "Strict semantic_feedback_v1 required")
    reader.ref(engine["artifact"], suffixes=(".py",), parse=False)
    exact(release["required_gates"], GATES, "release gates")
    require(all(v is True for v in release["required_gates"].values()), "Unresolved campaign gate")
    cases = release["cases"]
    require(isinstance(cases, list) and len(cases) == 4 and {c["cohort_slot"] for c in cases} == set(CASES), "Wrong released cases")
    by_slot = {c["cohort_slot"]: c for c in cases}
    for case in plan["cohorts"]:
        released = by_slot[case["cohort_slot"]]
        exact(released, {"cohort_slot", "actual_case_id", "release_id", "reference_arm", "case_gate"}, "case release")
        require(released["actual_case_id"] == case["actual_case_id"] and
                released["release_id"] == case["authorized_release"], "Case identity/release mismatch")
        task = reader.ref(case["task_contract"])
        # Full harness contract validation stays in the future construction runner.
        require(task["task_id"] == case["actual_case_id"] and task["mode"] == "whole_cohort", "Wrong task identity/mode")
        integer(task["n_rows"], 5000, "task rows")
        integer(task["budget"]["revisions"], 1, "task revision budget")
        require(task["information_policy"]["mode"] == "published_evidence" and
                isinstance(task["columns"], list) and bool(task["columns"]) and
                all(c["role"] in {"identifier", "generated"} for c in task["columns"]) and
                any(c["role"] == "generated" for c in task["columns"]), "Task allows individual input or has no generated schema")
        reader.ref(case["evidence_packet"])  # Approved aggregate evidence; no links are followed.
        analysis = reader.ref(case["analysis_plan"])  # No input_files are followed.
        baseline = reader.ref(released["reference_arm"])
        exact(baseline, {"schema_version", "case_id", "evidence_packet", "task_contract", "target_row_fitting",
                         "source_feedback_rounds", "extra_simulation_calls", "family", "fitting_rule", "unhandled_constraints"}, "reference arm")
        integer(baseline["schema_version"], 1, "reference arm version")
        require(baseline["case_id"] == case["actual_case_id"] and
                all(baseline[k] == case[k] for k in ("evidence_packet", "task_contract")), "Reference arm information differs")
        require(baseline["target_row_fitting"] is False, "Reference arm fits target rows")
        integer(baseline["source_feedback_rounds"], 1, "reference feedback rounds")
        integer(baseline["extra_simulation_calls"], 0, "reference extra simulation")
        for key in ("family", "fitting_rule", "unhandled_constraints"):
            nonempty(baseline[key], "reference " + key)
        gate = reader.ref(released["case_gate"])
        exact(gate, {"schema_version", "case_id", "independent_validation_eligible", "exposure_review",
                     "source_overlap_reviewed", "adapters_reviewed", "target_access", "quantitative_use_bundle",
                     "all_five_constructor_rule", "primary_analysis_count", "secondary_analysis_count"}, "case gate")
        integer(gate["schema_version"], 1, "case gate version")
        require(gate["case_id"] == case["actual_case_id"] and
                all(gate[k] is True for k in ("independent_validation_eligible", "source_overlap_reviewed", "adapters_reviewed")),
                "Case gate not ready for independent validation")
        exposure_review(reader.ref(gate["exposure_review"]), case, analysis)
        require(gate["target_access"] == "closed_pending_separate_evaluation_release", "Target access must remain closed")
        for key in ("quantitative_use_bundle", "all_five_constructor_rule"):
            nonempty(gate[key], key)
        integer(gate["primary_analysis_count"], 3, "primary analysis count")
        require(type(gate["secondary_analysis_count"]) is int and 0 <= gate["secondary_analysis_count"] <= 2, "Secondary analysis budget")


def preflight(project_root, plan_path, readiness_path=None):
    result = {"schema_version": 1, "kind": "campaign_readiness_preflight", "status": "blocked",
              "inventory_valid": False, "execution_authorized": False, "generator_executed": False,
              "target_data_accessed": False, "blockers": [], "counts": None, "metadata_files_read": []}
    reader = None
    try:
        reader = Reader(project_root)
        plan_bytes = reader.read(plan_path)
        plan = decode(plan_bytes)
        result["counts"] = inventory(plan)
        result["inventory_valid"] = True
        admissions(plan)  # Crucially precedes ALL readiness/artifact reads.
        require(readiness_path is not None, "Explicit readiness release path required")
        release = decode(reader.read(readiness_path))
        released_metadata(reader, plan, plan_bytes, release)
        result["status"] = "ready_metadata_only"
    except (NotReady, KeyError, TypeError, ValueError, OSError, RecursionError, OverflowError) as error:
        message = str(error) if isinstance(error, NotReady) else "Malformed or unavailable metadata: " + type(error).__name__
        result["blockers"].append(message)
    if reader is not None:
        result["metadata_files_read"] = reader.reads
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--plan", required=True, help="Project-relative JSON metadata path")
    parser.add_argument("--readiness", help="Project-relative readiness-release JSON; no default discovery")
    args = parser.parse_args(argv)
    result = preflight(args.project_root, args.plan, args.readiness)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["status"] == "ready_metadata_only" else 2


if __name__ == "__main__":
    raise SystemExit(main())
