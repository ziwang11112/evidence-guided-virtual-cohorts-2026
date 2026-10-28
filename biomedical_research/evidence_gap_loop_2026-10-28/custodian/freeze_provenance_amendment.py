"""Record validation-only amendment; never reads any outcomes or data tables."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import json
import os
import stat
from build_packet import sha, save

BASE = Path(__file__).resolve().parent
LOCKED = BASE/"locked"

def main():
    previous_path = LOCKED/"freeze_manifest_v1.json"
    previous = json.loads(previous_path.read_text())
    old_code = LOCKED/"evaluate_before_provenance_amendment.py"
    code = BASE/"evaluate.py"
    evaluator_relative = code.relative_to(BASE.parent).as_posix()
    prior_evaluator_hash = next(x["sha256"] for x in previous["files"] if x["path"] == evaluator_relative)
    assert sha(old_code) == prior_evaluator_hash
    for item in previous["files"]:
        if item["path"] != evaluator_relative:
            assert sha(BASE.parent/item["path"]) == item["sha256"]
    def functions(path):
        return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef)}
    old, new = functions(old_code), functions(code)
    statistical_functions = ["matrices", "taylor_fit", "contrast", "analyze"]
    assert all(old[name] == new[name] for name in statistical_functions)
    amendment = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "kind": "Validation-only evaluator provenance amendment",
        "reason": "Independent synthetic audit showed 40 labeled hash-matching files were not bound to actual frozen constructions/execution receipts",
        "authorized_by": "Parent agent 2026-10-28 message confirming artifacts mapping, output seed and controller receipt gate",
        "original_freeze_manifest_sha256": sha(previous_path), "original_evaluator_sha256": prior_evaluator_hash,
        "revised_evaluator_sha256": sha(code), "analysis_spec_sha256": sha(BASE/"analysis_spec.json"),
        "statistical_functions_ast_unchanged": statistical_functions,
        "outcome_data_already_parsed_for_preparation": True, "outcome_distribution_summaries_computed": False,
        "outcome_associations_evaluated": False, "changes": [
            "Bind four exact construction directories and assigned policies to run commitments",
            "Require 40 distinct canonical output paths; identical bytes remain valid for justified version no-op",
            "Check all candidate, review, execution, controller and gateway snapshot hashes",
            "Bind each output slot to its protocol seed, path, hash and row count in execution receipt"],
        "scope": "No target rows, values, weights, source files, eligibility, model matrices, analysis endpoints, effect units or comparison definitions changed"
    }
    amendment_path = BASE/"provenance_amendment.json"
    assert not amendment_path.exists(), "Amendment already written"
    save(amendment_path, amendment)
    revised = dict(previous)
    revised["frozen_utc"] = datetime.now(timezone.utc).isoformat()
    revised["freeze_version"] = 2
    revised["previous_freeze_manifest_sha256"] = sha(previous_path)
    revised["amendment"] = "custodian/provenance_amendment.json"
    revised["files"] = [dict(item) for item in previous["files"]]
    for item in revised["files"]:
        if item["path"] == evaluator_relative:
            item["sha256"], item["bytes"] = sha(code), code.stat().st_size
    for path in [old_code, previous_path, amendment_path, Path(__file__), BASE/"runtime_metadata.json"]:
        revised["files"].append({"path": path.relative_to(BASE.parent).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size})
        os.chmod(path, stat.S_IREAD)
    manifest_path = LOCKED/"freeze_manifest.json"
    os.chmod(manifest_path, stat.S_IWRITE | stat.S_IREAD)
    save(manifest_path, revised)
    os.chmod(manifest_path, stat.S_IREAD)
    os.chmod(code, stat.S_IREAD)
    print(json.dumps({"validation_only_amendment": True, "statistical_functions_unchanged": True,
                      "freeze_manifest_sha256": sha(manifest_path), "evaluator_sha256": sha(code)}))

if __name__ == "__main__":
    main()
