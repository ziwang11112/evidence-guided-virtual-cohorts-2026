"""Gated M16 three-construction evaluation using unchanged M15-B estimands.

No target read is performed at import. Every public-input, code, preauthoring
and lifecycle binding is verified before reference bytes are opened. This is
a procedural controller gate, not OS isolation or proof of reviewer identity.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RUN = HERE.parent
PROJECT = RUN.parent.parent
FROZEN_PATH = HERE / "frozen_m15b_estimands.py"
FROZEN_SHA256 = "4181cfbd8ae37df58699558196ca241f2bd60e4d895b9a18de40a42cbaffce12"
BUILDERS = ("b1", "b2", "b3")
REQUIRED_CHECKS = (
    "all_builders_closed", "preauthorship_verified", "feedback_binding_verified",
    "source_exposure_verified", "preservation_verified", "budgets_verified",
    "independent_code_review_complete",
)
PREAUTHOR_FILES = (
    "evidence.json", "model_spec.json", "audit/construction.json", "audit/revision_plan.json",
)
LIMITATIONS = (
    "Unweighted descriptions of the identical 200-person equal-stratum quota cohort; "
    "not national estimates or survey inference. Native examination/blood weights are "
    "retained privately and are not used by the estimators. Three Agent constructions "
    "are not independent patient studies or calibrated model uncertainty draws. "
    "Leave-one-joint-PSU-out ranges are descriptive sensitivity ranges, not confidence "
    "intervals. Source agreement and construction consistency are distinct from target "
    "utility. No target-based selection or further repair is authorized by evaluation."
)


class EvaluationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvaluationError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    def pairs(items):
        answer = {}
        for key, value in items:
            require(key not in answer, "Duplicate JSON key")
            answer[key] = value
        return answer
    def bad(value):
        raise EvaluationError("Nonfinite JSON constant: " + value)
    result = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs,
                        parse_constant=bad)
    require(isinstance(result, dict), "Expected JSON object")
    return result


def check_binding(item: dict, label: str) -> Path:
    require(isinstance(item, dict) and set(item) == {"path", "sha256"}, label + " binding schema")
    digest = item["sha256"]
    require(isinstance(digest, str) and len(digest) == 64 and
            all(c in "0123456789abcdef" for c in digest), label + " invalid SHA256")
    path = Path(item["path"]).resolve()
    require(path.is_file() and sha(path) == digest, label + " hash mismatch")
    return path


def safe_child(root: Path, name: str) -> Path:
    require(isinstance(name, str) and name and "\\" not in name and ":" not in name,
            "Expected portable relative path")
    parts = name.split("/")
    require(all(p not in ("", ".", "..") for p in parts), "Path traversal rejected")
    path = root.joinpath(*parts).resolve()
    require(path.is_relative_to(root.resolve()), "Path escaped root")
    return path


def load_estimands():
    require(sha(FROZEN_PATH) == FROZEN_SHA256, "Frozen estimand module changed")
    spec = importlib.util.spec_from_file_location("m16_frozen_estimands", FROZEN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_prelaunch(path: Path, run: Path, forbidden_reference: Path) -> dict:
    record = load_json(path)
    files = record.get("files")
    require(isinstance(files, dict) and bool(files), "Prelaunch file commitments missing")
    for name, digest in files.items():
        target = safe_child(run, name)
        require(target != forbidden_reference, "Reference must not be opened as a prelaunch input")
        check_binding({"path": str(target), "sha256": digest}, "prelaunch " + name)
    engines = record.get("engine_files")
    require(isinstance(engines, dict) and bool(engines), "Prelaunch engine commitments missing")
    for name, digest in engines.items():
        target = Path(name).resolve()
        require(target != forbidden_reference and target.suffix == ".py",
                "Only code files may enter prelaunch engine bindings")
        check_binding({"path": str(target), "sha256": digest}, "prelaunch engine")
    return record


def verify_preauthoring(binding: dict, directory: Path, candidate: str, freeze: dict,
                       *, builder: str, prelaunch_sha256: str) -> dict:
    path = check_binding(binding, "preauthoring")
    record = load_json(path)
    require(record.get("candidate") == candidate, "Preauthoring candidate mismatch")
    require(record.get("builder") == builder and record.get("prelaunch_sha256") == prelaunch_sha256,
            "Preauthoring builder/prelaunch mismatch")
    require(record.get("generated_exists") is False, "Model was not committed before table existence")
    files = record.get("files")
    require(isinstance(files, dict) and set(PREAUTHOR_FILES) <= set(files),
            "Required preauthoring files missing")
    require("generated.csv" not in files, "Preauthoring receipt must not include generated outcomes")
    audit_copy = directory / "audit/preauthoring_commitment.json"
    require(audit_copy.is_file() and sha(audit_copy) == binding["sha256"],
            "Preauthoring canonical receipt/candidate copy differ")
    require(freeze["commitments"].get(candidate + "/audit/preauthoring_commitment.json") == binding["sha256"],
            "Preauthoring audit copy not bound in freeze")
    for name, digest in files.items():
        check_binding({"path": str(safe_child(directory, name)), "sha256": digest},
                      "preauthoring " + name)
        require(freeze["commitments"].get(candidate + "/" + name) == digest,
                "Preauthoring file differs from candidate freeze")
    try:
        committed = datetime.fromisoformat(record["created_utc"].replace("Z", "+00:00"))
        frozen = datetime.fromisoformat(freeze["created_utc"].replace("Z", "+00:00"))
        require(committed.tzinfo is not None and frozen.tzinfo is not None and committed <= frozen,
                "Preauthoring chronology invalid")
    except (KeyError, TypeError, ValueError) as error:
        raise EvaluationError("Preauthoring chronology invalid") from error
    return record


def task_semantics(task: dict) -> dict:
    require(isinstance(task.get("task_id"), str) and bool(task["task_id"]), "Task ID missing")
    return {key: value for key, value in task.items() if key != "task_id"}


def verify_release(manifest: Path, *, run: Path = RUN) -> tuple[dict, bytes]:
    """Return verified release and reference bytes, opened only after all other checks."""
    release = load_json(manifest)
    require(release.get("schema_version") == 1 and
            release.get("kind") == "m16_target_evaluation_release", "Wrong release schema")
    require(release.get("evaluation_authorized") is True, "Evaluation not authorized")
    require(all(release.get("controller_checks", {}).get(k) is True for k in REQUIRED_CHECKS),
            "Controller review incomplete")
    reference_item = release["reference"]
    require(isinstance(reference_item, dict) and set(reference_item) == {"path", "sha256"},
            "Reference binding schema")
    reference_path = Path(reference_item["path"]).resolve()
    require(reference_path.is_relative_to(run.resolve() / "private"), "Reference outside private run")
    expected_paths = {"protocol": run / "PROTOCOL.md", "controller": run / "controller.py",
                      "evaluator": Path(__file__).resolve(), "estimands": FROZEN_PATH,
                      "self_checker": PROJECT / "cohort_harness/self_consistency.py"}
    for role, expected in expected_paths.items():
        require(Path(release[role]["path"]).resolve() == expected.resolve(), role + " path mismatch")
        check_binding(release[role], role)
    require(release["estimands"]["sha256"] == FROZEN_SHA256, "Estimand version changed")
    prelaunch_path = check_binding(release["prelaunch"], "prelaunch")
    prelaunch_record = verify_prelaunch(prelaunch_path, run, reference_path)
    require(release.get("reference_weight_column") in ("WTMEC2YR", "WTPH2YR"),
            "Native reference weight column unspecified")
    require(prelaunch_record.get("reference") == reference_item and
            prelaunch_record.get("reference_weight_column") == release["reference_weight_column"],
            "Reference differs from pre-generation commitment")
    builders = release.get("builders")
    require(isinstance(builders, list) and [x.get("id") for x in builders] == list(BUILDERS),
            "Exactly b1,b2,b3 in fixed order are required")
    require(isinstance(prelaunch_record.get("registry_prefixes"), dict) and
            set(prelaunch_record["registry_prefixes"]) == set(BUILDERS), "Seed registry commitments missing")
    if str(PROJECT) not in sys.path:
        sys.path.insert(0, str(PROJECT))
    from cohort_harness.lifecycle import verify_candidate
    shared_task = shared_observed_hash = None
    for builder in builders:
        bundle = Path(builder["bundle_path"]).resolve()
        require(bundle.is_relative_to(run.resolve()), "Bundle outside run")
        require(builder["status"] in ("complete", "failed"), "Builder not closed")
        for name, field in (("task.json", "task_sha256"), ("observed.csv", "observed_sha256")):
            check_binding({"path": str(bundle / name), "sha256": builder[field]}, builder["id"] + " " + name)
            relative = (bundle / name).relative_to(run.resolve()).as_posix()
            require(prelaunch_record["files"].get(relative) == builder[field],
                    "Task/X not bound in prelaunch")
        registry = load_json(bundle / "registry.json")
        prefix = prelaunch_record["registry_prefixes"][builder["id"]]
        require(isinstance(prefix, list) and registry.get("artifacts", [])[:len(prefix)] == prefix,
                "Seed registry prefix changed")
        if shared_observed_hash is None:
            shared_observed_hash = builder["observed_sha256"]
            shared_task = task_semantics(load_json(bundle / "task.json"))
        require(builder["observed_sha256"] == shared_observed_hash and
                task_semantics(load_json(bundle / "task.json")) == shared_task,
                "Builders do not share task semantics and identical X")
        if builder["status"] == "failed":
            check_binding(builder["failure_record"], "builder failure")
            require("final" not in builder, "Failed builder cannot declare a final output")
        else:
            require("initial" in builder and "final" in builder, "Complete builder lacks outputs")
        receipts = {}
        for stage in ("initial", "final"):
            if stage not in builder:
                continue
            entry = builder[stage]
            candidate = entry["candidate"]
            require(candidate == "candidates/" + stage, "Unexpected scheduled candidate")
            directory = safe_child(bundle, candidate)
            check_binding({"path": str(directory / "freeze.json"), "sha256": entry["freeze_sha256"]},
                          builder["id"] + " " + stage + " freeze")
            receipt = verify_candidate(bundle, candidate)
            require(receipt["route"] == "generated.csv", "Only literal-table route may be evaluated")
            require(receipt["commitments"].get("task.json") == builder["task_sha256"] and
                    receipt["commitments"].get("observed.csv") == builder["observed_sha256"],
                    "Freeze task/X mismatch")
            check_binding({"path": str(directory / "generated.csv"), "sha256": entry["table_sha256"]},
                          builder["id"] + " " + stage + " table")
            require(receipt["commitments"].get(candidate + "/generated.csv") == entry["table_sha256"],
                    "Table freeze mismatch")
            canonical_precommit = run / "commitments" / builder["id"] / (stage + ".json")
            require(Path(entry["preauthoring"]["path"]).resolve() == canonical_precommit.resolve(),
                    "Noncanonical preauthoring receipt path")
            verify_preauthoring(entry["preauthoring"], directory, candidate, receipt,
                               builder=builder["id"], prelaunch_sha256=release["prelaunch"]["sha256"])
            receipts[stage] = receipt
        if "initial" in receipts:
            require(receipts["initial"]["revision_index"] == 0, "Initial revision index incorrect")
        if "final" in receipts:
            current = receipts["final"]
            seen = set()
            while current["candidate"] != "candidates/initial":
                require(current["candidate"] not in seen and current["parent"] is not None,
                        "Final lacks initial ancestor")
                seen.add(current["candidate"])
                current = load_json(safe_child(bundle, current["parent"]["receipt_path"]))
                if current["candidate"] != "candidates/initial":
                    stage = current["candidate"].split("/")[-1]
                    require(stage == "revision1", "Unexpected intermediate candidate")
                    canonical_precommit = run / "commitments" / builder["id"] / (stage + ".json")
                    verify_preauthoring({"path": str(canonical_precommit), "sha256": sha(canonical_precommit)},
                                       safe_child(bundle, current["candidate"]), current["candidate"], current,
                                       builder=builder["id"], prelaunch_sha256=release["prelaunch"]["sha256"])
            require(current == receipts["initial"], "Initial ancestry receipt mismatch")
    # FIRST private reference file access, after every prerequisite has passed.
    require(isinstance(reference_item["sha256"], str) and len(reference_item["sha256"]) == 64 and
            all(c in "0123456789abcdef" for c in reference_item["sha256"]), "Invalid reference SHA256")
    reference_bytes = reference_path.read_bytes()
    require(hashlib.sha256(reference_bytes).hexdigest() == reference_item["sha256"],
            "Reference hash mismatch")
    return release, reference_bytes


def parse_csv_bytes(raw: bytes, *, reference: bool, weight_column: str = "WTMEC2YR") -> pd.DataFrame:
    text = raw.decode("utf-8-sig")
    header = next(csv.reader(io.StringIO(text)), [])
    require(header and len(header) == len(set(header)), "Duplicate or missing CSV header")
    frame = pd.read_csv(io.StringIO(text), dtype={"sample_id": str, "race": str, "sex": str,
                        "SDMVSTRA": str, "SDMVPSU": str}, float_precision="round_trip",
                        keep_default_na=False, na_values=[""])
    module = load_estimands()
    if reference:
        required = set(module.BASE_COLUMNS) | set(module.DESIGN_COLUMNS)
        allowed = required | {"SEQN", weight_column}
        require(required <= set(frame.columns) <= allowed, "Unexpected native reference schema")
        # The old module deliberately accepts only the original cycle's weight name.
        # Drop native metadata before pure estimands; no weighting or numeric change.
        frame = frame.loc[:, list(module.BASE_COLUMNS) + list(module.DESIGN_COLUMNS)]
    return module.validate_table(frame, reference=reference)


def evaluate_verified(release: dict, reference_bytes: bytes) -> dict:
    module = load_estimands()
    reference = parse_csv_bytes(reference_bytes, reference=True,
                                weight_column=release["reference_weight_column"])
    measured = module.evaluate_table(reference, reference=True)
    sensitivity = module.reference_sensitivity(reference)
    sensitivity["limitations"] = LIMITATIONS
    candidates, outcomes, changes, table_hashes = [], [], [], set()
    for builder in release["builders"]:
        records = {}
        tables = {}
        for stage in ("initial", "final"):
            if stage not in builder:
                continue
            entry = builder[stage]
            path = Path(builder["bundle_path"]) / entry["candidate"] / "generated.csv"
            raw = path.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == entry["table_sha256"],
                    "Candidate changed after gate")
            frame = parse_csv_bytes(raw, reference=False)
            module.validate_pair(reference, frame)
            generated = module.evaluate_table(frame)
            # Same arithmetic pairing as the frozen compare_tables, with measured
            # estimands computed once rather than recomputing for all six tables.
            paired = []
            for ref, gen in zip(measured, generated, strict=True):
                require(ref["estimand"] == gen["estimand"], "Estimand order mismatch")
                valid = ref["status"] == gen["status"] == "ok"
                paired.append({
                    **{k: ref[k] for k in ("estimand", "family", "race", "sex", "model", "coefficient", "units")},
                    "measured": ref, "generated": gen,
                    "difference_generated_minus_measured": gen["value"] - ref["value"] if valid else None,
                    "same_sign": ref["sign"] == gen["sign"] if valid and ref["family"] != "group_summary" else None,
                })
            records[stage] = paired
            tables[stage] = frame
            table_hashes.add(entry["table_sha256"])
            candidates.append({"builder": builder["id"], "stage": stage,
                               "table_sha256": entry["table_sha256"], "estimands": paired})
        outcome = {"builder": builder["id"], "status": builder["status"],
                   "scheduled_initial": "initial" in builder, "scheduled_final": "final" in builder,
                   "changed_urate_rows": None, "unique_candidate_tables": len({
                       builder[s]["table_sha256"] for s in ("initial", "final") if s in builder})}
        if set(tables) == {"initial", "final"}:
            outcome["changed_urate_rows"] = int(np.count_nonzero(
                tables["initial"]["urate"].to_numpy() != tables["final"]["urate"].to_numpy()))
            for first, last in zip(records["initial"], records["final"], strict=True):
                di = first["difference_generated_minus_measured"]
                df = last["difference_generated_minus_measured"]
                change = abs(df) - abs(di) if di is not None and df is not None else None
                changes.append({"builder": builder["id"], "estimand": first["estimand"],
                                "units": first["units"], "initial_difference": di, "final_difference": df,
                                "change_in_absolute_difference_final_minus_initial": change,
                                "direction": None if change is None else "lower" if change < 0 else
                                             "higher" if change > 0 else "unchanged"})
        if builder["status"] == "failed":
            outcome["failure_record"] = builder["failure_record"]
        outcomes.append(outcome)
    return {"schema_version": 1, "protocol": "M16", "limitations": LIMITATIONS,
            "cohort_n": len(reference), "stratum_n": 50, "estimand_count": 24,
            "sd_ddof": 1, "quantile_convention": "linear", "scheduled_builders": list(BUILDERS),
            "unique_candidate_table_hashes": len(table_hashes), "builder_outcomes": outcomes,
            "reference_estimands": measured, "candidate_comparisons": candidates,
            "initial_final_changes": changes, "reference_sensitivity": sensitivity}


def write_results(destination: Path, result: dict) -> None:
    require(not destination.exists(), "Output already exists; no overwrite")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "evaluation.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                                                 encoding="utf-8")
    rows = []
    for candidate in result["candidate_comparisons"]:
        for record in candidate["estimands"]:
            row = {"builder": candidate["builder"], "stage": candidate["stage"]}
            row.update({k: v for k, v in record.items() if k not in ("measured", "generated")})
            for role in ("measured", "generated"):
                row.update({role + "_" + k: record[role][k] for k in
                            ("value", "n", "n_complete", "rank", "n_parameters", "status", "reason", "sign")})
            rows.append(row)
    with (destination / "estimands.csv").open("x", encoding="utf-8", newline="") as stream:
        fields = list(rows[0]) if rows else ["builder", "stage", "estimand"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with (destination / "initial_final_changes.csv").open("x", encoding="utf-8", newline="") as stream:
        changes = result["initial_final_changes"]
        fields = list(changes[0]) if changes else ["builder", "estimand"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(changes)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--release-manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    if not args.execute:
        parser.error("Disabled without --execute; no input read")
    try:
        require(not args.output_dir.exists(), "Output exists; no reference read")
        release, reference_bytes = verify_release(args.release_manifest)
        result = evaluate_verified(release, reference_bytes)
        result["release_manifest_sha256"] = sha(args.release_manifest)
        result["evaluator_sha256"] = sha(Path(__file__))
        result["frozen_estimands_sha256"] = FROZEN_SHA256
        write_results(args.output_dir, result)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, "Evaluation stopped: " + str(error) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
