"""Write the one-use release only after a recorded independent closure audit.

This script reads commitments and candidate hashes, never reference rows.
The evaluator, not this authorizer, subsequently opens the reference.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
P = R.parents[1]
CHECKS = (
    "all_builders_closed", "preauthorship_verified", "feedback_binding_verified",
    "source_exposure_verified", "preservation_verified", "budgets_verified",
    "independent_code_review_complete",
)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def binding(path: Path) -> dict:
    return {"path": str(path.resolve()), "sha256": digest(path)}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("Explicit execution required; no files read.")
    audit_path = R / "review/RELEASE_CHECKS.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8-sig"))
    if audit.get("status") != "pass" or audit.get("target_outcomes_read") is not False:
        raise SystemExit("Independent closure audit missing or not passed.")
    for name in CHECKS:
        if audit.get("checks", {}).get(name) is not True:
            raise SystemExit(f"Unverified closure check: {name}")
    prelaunch = json.loads((R / "prelaunch.json").read_text(encoding="utf-8-sig"))
    reference_path = Path(prelaunch["reference"]["path"]).resolve()
    private_root = (R / "private").resolve()
    required_report = (R / "review/FINAL_RELEASE_AUDIT.md").resolve()
    covered = {str(Path(x["path"]).resolve()) for x in audit["bindings"]}
    if str(required_report) not in covered:
        raise SystemExit("Independent closure report is not bound.")
    # Reject private/reference bindings before hashing any of their bytes.
    for record in audit["bindings"]:
        path = Path(record["path"]).resolve()
        if path.is_relative_to(private_root) or path == reference_path:
            raise SystemExit("Private cohort data cannot be closure-audit bindings.")
        if path.exists() and reference_path.exists() and path.samefile(reference_path):
            raise SystemExit("Reference alias cannot be a closure-audit binding.")
    # The audit must bind the report and all final freezes to current bytes.
    for record in audit["bindings"]:
        if digest(Path(record["path"])) != record["sha256"]:
            raise SystemExit("Closure audit binding changed.")
    builders = []
    for bid in ("b1", "b2", "b3"):
        bundle = R / "visible" / bid / "bundle"
        item = {
            "id": bid, "bundle_path": str(bundle), "status": "complete",
            "task_sha256": digest(bundle / "task.json"),
            "observed_sha256": digest(bundle / "observed.csv"),
        }
        for stage in ("initial", "final"):
            candidate = bundle / "candidates" / stage
            freeze = candidate / "freeze.json"
            if str(freeze.resolve()) not in covered:
                raise SystemExit(f"Unbound audited freeze: {bid}/{stage}")
            item[stage] = {
                "candidate": f"candidates/{stage}",
                "freeze_sha256": digest(freeze),
                "table_sha256": digest(candidate / "generated.csv"),
                "preauthoring": binding(R / "commitments" / bid / f"{stage}.json"),
            }
        builders.append(item)
    release = {
        "schema_version": 1, "kind": "m16_target_evaluation_release",
        "evaluation_authorized": True,
        "protocol": binding(R / "PROTOCOL.md"),
        "controller": binding(R / "controller.py"),
        "prelaunch": binding(R / "prelaunch.json"),
        "self_checker": binding(P / "cohort_harness/self_consistency.py"),
        "evaluator": binding(R / "evaluation_code/evaluator.py"),
        "estimands": binding(R / "evaluation_code/frozen_m15b_estimands.py"),
        "reference": prelaunch["reference"],
        "reference_weight_column": prelaunch["reference_weight_column"],
        "controller_checks": {name: True for name in CHECKS},
        "builders": builders,
    }
    destination = R / "private/evaluation_release.json"
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(release, indent=2, ensure_ascii=False) + "\n")
    log = {
        "release": binding(destination), "independent_audit": binding(audit_path),
        "reference_rows_read_by_authorizer": False,
        "builder_statuses": {x["id"]: x["status"] for x in builders},
    }
    with (R / "RELEASE_LOG.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(log, indent=2) + "\n")
    print(json.dumps(log))

if __name__ == "__main__":
    main()
