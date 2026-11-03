"""Prepare a separate unsigned reuse release; never execute or read references."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
PRIOR = HERE.parent / "developmental_revision_pilot_v1_2026-11-02"
PREFLIGHT = HERE.parent / "qualified_author_preflight_v1_2026-11-03"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PRIOR / "implementation"))
import pilot_controller_v1 as controller


def binding(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def main():
    if (HERE / "RELEASE.json").exists():
        raise RuntimeError("This unit is released; preparation is closed")
    closure = json.loads((PRIOR / "ADMISSION_CLOSURE.json").read_text())
    assert closure["status"] == "closed_admission_failure"
    assert closure["source_draws"] == closure["target_draws"] == 0
    inputs = HERE / "author_inputs"
    for path in (PRIOR / "author_inputs").rglob("*"):
        if path.is_file():
            destination = inputs / path.relative_to(PRIOR / "author_inputs")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
    shutil.copyfile(HERE / "PROTOCOL.md", inputs / "input/PROTOCOL.md")
    task_text = (inputs / "input/AUTHOR_TASK.md").read_text(encoding="utf-8")
    task_text = ("# Continuation note\n\nThe initial scientific laws are inherited, not newly authored. "
                 "Only your assigned branch may make one scientific decision. The new PROTOCOL.md controls reuse and admission. "
                 "Run the supplied read-only qualified author preflight before submission. Authored qualified bindings are exactly {}; "
                 "measurement mappings must use the native variable names in their unit evidence, linked through declared aliases. "
                 "Never manufacture approval or execute/simulate a candidate while authoring.\n\n" + task_text)
    (inputs / "input/AUTHOR_TASK.md").write_text(task_text, encoding="utf-8")
    prior_packet = json.loads((PRIOR / "INITIAL_PACKET.json").read_text())
    files = []
    for item in prior_packet["files"]:
        path = Path(item["path"])
        if path.is_relative_to(PRIOR / "author_inputs"):
            path = inputs / path.relative_to(PRIOR / "author_inputs")
        files.append(binding(path))
    for path in (PROJECT / "cohort_harness/lifecycle.py", PREFLIGHT / "qualified_author_preflight.py", PREFLIGHT / "README.md"):
        if str(path.resolve()) not in {item["path"] for item in files}:
            files.append(binding(path))
    packet = {"schema_version": 1, "kind": "pilot_initial_author_packet",
              "task": binding(inputs / "task.json"), "evidence": binding(inputs / "input/compiled_evidence.json"),
              "registry": binding(inputs / "registry.json"), "files": files}
    write(HERE / "INITIAL_PACKET.json", packet)
    release = copy.deepcopy(json.loads((PRIOR / "RELEASE.json").read_text()))
    release.update(ledger_directory=str((WORKSPACE / "evcDC/ledger").resolve()),
                   protocol=binding(HERE / "PROTOCOL.md"), initial_packet=binding(HERE / "INITIAL_PACKET.json"), review=None)
    additional = [HERE / "prepare_release.py", HERE / "review/DESIGN_REVIEW.md", PRIOR / "PROTOCOL.md",
                  PRIOR / "ADMISSION_CLOSURE.json", PRIOR / "INDEPENDENT_CLOSURE_REVIEW.json",
                  PRIOR / "NEXT_EXECUTION_REQUIREMENTS.md", PREFLIGHT / "qualified_author_preflight.py",
                  PREFLIGHT / "README.md", PREFLIGHT / "ROOT_REVIEW.json", PREFLIGHT / "test_result.json"]
    for path in additional:
        if str(path.resolve()) not in {item["path"] for item in release["artifacts"]}:
            release["artifacts"].append(binding(path))
    write(HERE / "RELEASE_DRAFT.json", release)
    write(HERE / "PLANNED_SLOTS.json", controller.planned_slots(release))
    write(HERE / "PREPARATION.json", {"kind": "technical_continuation_preparation", "fresh_initial_authors": 0,
          "reused_original_constructions": 2, "new_source_draw_budget": 54, "new_target_draw_budget": 18,
          "old_unrun_allocations_preserved": 72, "source_draws": 0, "target_draws": 0,
          "reference_contents_read": False, "new_packet_is_not_original_author_delivery": True,
          "original_packet": binding(PRIOR / "INITIAL_PACKET.json"), "new_admission_packet": binding(HERE / "INITIAL_PACKET.json"),
          "release_digest": controller.release_digest(release), "unchanged_engine_hashes": controller.engine_hashes() == release["engine_sha256"]})
    print(json.dumps({"release_digest": controller.release_digest(release), "status": "unsigned_only", "author_input_files": len(files)}))


if __name__ == "__main__":
    main()
