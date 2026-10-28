"""Independent metadata-only release verification before any target analysis."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import json
import evaluate as ev

BASE = Path(__file__).resolve().parent

def main():
    release_path = BASE/"evaluation_release.json"
    expected_release = "ff6f5dfedbca6565b694d3ea4929db7e392dbaa889f5e95808e16ca6e03ad046"
    expected_evaluator = "b8416f30282329b9e55b3a814187eb5d65ad239bac7b6f5ba610d37344b1c29c"
    assert ev.sha(release_path) == expected_release
    assert ev.sha(BASE/"evaluate.py") == expected_evaluator
    release = ev.read_json(release_path)
    assert release["evaluator_sha256"] == expected_evaluator
    assert release["analysis_spec_sha256"] == ev.sha(BASE/"analysis_spec.json")
    before = ev.read_json(BASE/"locked/pre_read_freeze.json")
    assert before["files"]["analysis_spec.json"] == ev.sha(BASE/"analysis_spec.json")
    def nodes(path):
        return {node.name: ast.dump(node, include_attributes=False) for node in ast.parse(path.read_text()).body if isinstance(node, ast.FunctionDef)}
    original = nodes(BASE/"locked/evaluate_before_provenance_amendment.py")
    current = nodes(BASE/"evaluate.py")
    names = ["matrices", "taylor_fit", "contrast", "analyze"]
    assert all(original[name] == current[name] for name in names)
    entries = ev.validate_release(release)
    frozen = ev.read_json(BASE/"locked/freeze_manifest.json")
    for item in frozen["files"]:
        assert ev.sha(ev.safe_path(item["path"])) == item["sha256"]
    audit = {"verified_utc": datetime.now(timezone.utc).isoformat(), "release_sha256": expected_release,
             "evaluator_sha256": expected_evaluator, "analysis_spec_sha256": ev.sha(BASE/"analysis_spec.json"),
             "all_gate_checks_passed": True, "output_slots": len(entries), "bound_artifacts": len(release["artifacts"]),
             "prespecified_statistical_functions_unchanged": names,
             "validation_read_target_values": False, "validation_computed_target_statistics": False,
             "authorized_by": "Parent explicit release-and-evaluate instruction after all four constructions and 40 scheduled outputs frozen"}
    ev.save(BASE/"evaluation_preflight_audit.json", audit)
    print(json.dumps(audit))

if __name__ == "__main__":
    main()
