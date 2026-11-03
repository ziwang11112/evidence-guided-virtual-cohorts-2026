"""Materialize arm-scoped author inputs; no author dispatch or row generation.

Run only after implementation review; creates an unsigned manifest. It cannot
enable execution. Scientific parameters are not supplied by this assembler.
"""
from pathlib import Path
import json
import shutil
import main_session_v1 as session
from cohort_harness.contracts import validate_evidence

UNIT = Path(__file__).resolve().parents[1]
PROJECT = UNIT.parents[1]
WORKSPACE = PROJECT.parents[1]
RUNTIME_ROOT = WORKSPACE / "evcMS"


def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError("Refuse overwrite: " + str(destination))
    shutil.copyfile(source, destination)


def assemble():
    if RUNTIME_ROOT.exists() or (UNIT / "RELEASE_DRAFT.json").exists():
        raise ValueError("Preparation already exists; inspect and resume explicitly, do not reset")
    review = UNIT / "review/IMPLEMENTATION_REVIEW.json"
    if not review.is_file() or session.READ(review).get("status") != "ready_for_materialization":
        raise ValueError("Independent adapter/case materialization review required")
    for inspected in session.READ(review)["inspected_artifacts"]:
        if session.SHA(UNIT / inspected["path"]) != inspected["sha256"]:
            raise ValueError("Materialization review is stale: " + inspected["path"])
    provider_names = {"CHNS2009": "generated_provider.py", "ENSANUT2018": "generated_feedback.py"}
    slots = []
    # Bind only files actually imported by a session/provider here. The common
    # final evaluator/comparator/assembler are bound separately in the release.
    dependencies = [PROJECT / "work/chns_admission_2026-11-01/f2/evaluation/chns_f2_evaluation.py",
                     PROJECT / "work/chns_admission_2026-11-01/f2/analysis_plan.json",
                     PROJECT / "work/autonomous_research_cycle2_2026-10-31/analysis/analytical_engine.py"]
    for case in ("CHNS2009", "ENSANUT2018"):
        source = UNIT / "cases" / case
        for condition in ("E0", "E1"):
            for index in range(6):
                kind = "agent" if index < 5 else "statistical"
                constructor_id = f"{case}_{condition}_{'A'+str(index+1).zfill(2) if kind == 'agent' else 'S01'}"
                root = RUNTIME_ROOT / constructor_id
                bundle = root / "bundle"
                (bundle / "input").mkdir(parents=True)
                task = session.READ(source / "task.json")
                task["task_id"] = constructor_id
                task["budget"] = {"source_queries": 0, "source_downloads": 0, "revisions": 1}
                session.WRITE(bundle / "task.json", task)
                if case == "CHNS2009":
                    copy(source / f"{condition}_evidence.json", bundle / "input/evidence.json")
                    copy(source / f"{condition}.json", bundle / "input/reported_packet.json")
                    copy(source / "evaluation.json", bundle / "input/analysis_definitions.json")
                    copy(source / "AUTHOR_COMMON.md", bundle / "input/CASE_TASK.md")
                    copy(source / "NGSP_UNITS.md", bundle / "input/NGSP_UNITS.md")
                    shutil.copytree(source / f"{condition}_sources", bundle / "sources")
                    if condition == "E1":
                        copy(source / "source_operations.json", bundle / "input/source_operations.json")
                        copy(source / "source_operations.py", bundle / "input/source_operations.py")
                    profile_source = source / f"{condition}_{kind}_profile.json"
                else:
                    copy(source / f"{condition}.json", bundle / "input/evidence.json")
                    copy(source / f"{condition}_normalization.json", bundle / "input/evidence_normalization.json")
                    copy(source / "analysis_definitions.json", bundle / "input/analysis_definitions.json")
                    copy(source / f"{condition}_source_operations.json", bundle / "input/source_operations.json")
                    if condition == "E1":
                        copy(source / "source_operators.py", bundle / "input/source_operators.py")
                    shutil.copytree(source / "sources" / condition, bundle / "sources" / condition)
                    profile_source = source / f"profile_{condition}_{kind}.json"
                copy(source / f"{condition}_registry.json", bundle / "registry.json")
                evidence = session.READ(bundle / "input/evidence.json")
                validate_evidence(evidence, task)
                _, entries, _ = session.lifecycle._registry(bundle)
                for record in evidence["sources"]:
                    for artifact in record["artifacts"]:
                        if (record["id"], artifact["path"], artifact["sha256"]) not in entries:
                            raise ValueError("Prepared evidence missing from scoped registry")
                copy(profile_source, root / "profile.json")
                copy(UNIT / "AUTHOR_CONTRACT_TEMPLATE.md", bundle / "input/AUTHOR_TASK.md")
                session.WRITE(bundle / "input/identity.json", {"author_id": constructor_id,
                      "constructor_kind": kind, "case_id": case, "information_condition": condition,
                      "provided_reference_values": False, "separate_condition_access": False,
                      "scope": "Only this bundle input/, sources/, task.json, registry.json, profile and own candidates/output; no project-wide discovery"})
                session.initialize(root, root / "profile.json", source / provider_names[case],
                                   author_id=constructor_id, dependencies=dependencies)
                slots.append({"id": constructor_id, "session_root": str(root),
                              "contract_sha256": session.SHA(root / "session/contract.json")})
    artifacts = [session.bound(p) for p in sorted(UNIT.rglob("*")) if p.is_file()
                 and p.suffix in {".py", ".json", ".md"} and "__pycache__" not in p.parts
                 and p.name not in {"STATE.json", "PUBLIC_SYNC_RECEIPT.json"}]
    release = {"kind": "main_study_release_v1", "execution_enabled": False,
               "budget": session.BUDGET, "maximum_total_attempts": 120,
               "constructions": slots, "artifacts": artifacts, "independent_review": None,
               "source_numeric_mode": "reviewed_analytic_only", "created_utc": session.now()}
    session.WRITE(UNIT / "RELEASE_DRAFT.json", release)
    return {"status": "materialized_unsigned", "sessions": len(slots), "row_attempts": 0,
            "author_dispatches": 0, "execution_enabled": False}


if __name__ == "__main__":
    print(json.dumps(assemble()))
