"""Prepare a new controlled source-feedback task, without a scientific model.

Reuses the explicitly fictional sources, not a prior Agent candidate. The builder
chooses the model and source-covariate recipes. No hidden outcomes exist here.
"""
from pathlib import Path
import json

from prepare_execution_fixture import prepare


def prepare_loop(destination):
    root = prepare(destination)
    task_path = root / "task.json"
    task = json.loads(task_path.read_text(encoding="utf-8"))
    task["task_id"] = "controlled-source-feedback-loop-2026-10-28"
    task["information_policy"]["allowed_tools"] = ["local_fixture_only", "source_replay"]
    task["budget"] = {"source_queries": 0, "source_downloads": 0, "revisions": 1}
    task_path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")
    protocol = {
        "scope": "invented execution and feedback integration only",
        "agent_constructions": 1,
        "feedback_rounds": 1,
        "source_seed": 73001,
        "target_seeds": [73101, 73102, 73103],
        "selection": "Report initial and final; no best-seed or target-based selection",
        "feedback": "Only executed source-replay diagnostics; no target reference exists",
        "revision": "Agent may revise or retain; no forced change and no controller parameter edits",
        "interpretation": "Software integration, not biomedical efficacy or arm superiority",
        "builder_boundary": "Fresh-context subagent with instructed allowlist, not OS tool isolation"
    }
    (root / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    (root / "TASK_BRIEF.md").write_text(
        "# Controlled source-feedback loop\n\n"
        "All source records are fictional. Build an initial program candidate named initial.\n"
        "Read the supplied generation skill, authoritative contracts and source replay interface.\n"
        "Choose scientific structure/parameters yourself; do not reuse an old candidate.\n"
        "Submit source_replay.json and source_contexts/*.csv inside the candidate before freezing.\n"
        "Source tables contain covariates only, never fabricated observed outcomes.\n"
        "Use the same task column names/units; record any source unit conversion as a derived\n"
        "evidence item with original value and calculation retained. Describe any assumptions\n"
        "needed to represent a source population or measurement. No exact recovery is claimed.\n"
        "The controller executes the frozen generator and returns source diagnostics once.\n"
        "After feedback choose either a justified revision or retention, in a new final candidate.\n"
        "Do not execute your program outside the supplied isolated adapter. Static checks are allowed.\n"
        "Do not inspect prior candidates, framework tests, custodian data or unrelated experiments.\n",
        encoding="utf-8",
    )
    return root


if __name__ == "__main__":
    import sys
    print(prepare_loop(Path(sys.argv[1])))
