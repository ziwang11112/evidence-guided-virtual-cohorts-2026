"""Independent static candidate audit: JSON/bytes/AST only; never import generator."""
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

w = Path(r"D:/AIR-014_ECRC_Paper_Clean_2026-08-16")
d = w / "biomedical_research/virtual_cohort_system/work/source_increment_revision_2026-11-05"
b = w / "evcIncE01"
c = b / "candidates/source_increment"
old = w / "evcRepE01/candidates/initial"

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def leaves(x, prefix=""):
    if isinstance(x, dict):
        return {k2: v2 for k,v in x.items() for k2,v2 in leaves(v, prefix+"."+k if prefix else k).items()}
    if isinstance(x, list):
        return {k2: v2 for i,v in enumerate(x) for k2,v2 in leaves(v, f"{prefix}[{i}]").items()}
    return {prefix:x}

# Only already-admitted baseline static model/evidence are read for comparison.
assert sha(old/"model_spec.json") == "679056f23c563804e53a84326557c8c62c6581f64db830d32ae7b31aa1f088a5"
assert sha(old/"evidence.json") == "9442bfdefd20fc4356832645904d0d77eed95f5d80210d177d70ae94679eb20b"
initial = read(old/"model_spec.json")
initial_evidence = read(old/"evidence.json")
current = read(c/"model_spec.json")
evidence = read(c/"evidence.json")
proposal = read(d/"PROPOSAL.json")
review = read(d/"REVIEW.json")
assert sha(d/"PROPOSAL.json") == review["reviewed_proposal"]["sha256"]
before,after = leaves(initial["parameters"]),leaves(current["parameters"])
assert before.keys() == after.keys()
diff = {key:{"old":before[key],"new":after[key]} for key in before if before[key] != after[key]}
expected = {x["path"].removeprefix("parameters."):{"old":x["old"],"new":x["value"]}
            for x in proposal["proposed_model"]["parameter_patch"]}
assert len(diff) == 7 and diff == expected
assert sha(c/"generator.py") == "eb90182a471cbee5443cb4419e4e9f7c90ea538218d226e2c314c6e5329b1477"
ast.parse((c/"generator.py").read_text(encoding="utf-8"))

by_id = {x["id"]:x for x in evidence["items"]}
assert len(by_id) == len(evidence["items"]) == 22
for item in initial_evidence["items"]:
    new = by_id[item["id"]]
    assert {k:v for k,v in item.items() if k != "applicability"} == {k:v for k,v in new.items() if k != "applicability"}
new_ids = set(by_id)-{x["id"] for x in initial_evidence["items"]}
assert new_ids == {"supp_s1_bmi_glucose","supp_s2_bmi_hba1c"}
assert by_id["supp_s1_bmi_glucose"]["estimate"] == .024
assert by_id["supp_s2_bmi_hba1c"]["estimate"] == .0125
for id_ in new_ids:
    assert by_id[id_]["unit"] == ""
    assert by_id[id_]["uncertainty"] == {"kind":"not_reported"}

recipe = read(c/"whole_cohort_feedback.json")
sem = read(c/"source_semantics_v1.json")
assert sem["evidence_sha256"] == sha(c/"evidence.json")
assert sem["recipe_sha256"] == sha(c/"whole_cohort_feedback.json")
bindings = {x["check_id"]:x for x in sem["bindings"]}
assert len(bindings) == len(recipe["checks"]) == 22
assert {x["evidence_id"] for x in recipe["checks"]} == set(by_id)
for item in recipe["checks"]:
    bind = bindings[item["id"]]
    assert bind["evidence_id"] == item["evidence_id"]
    assert bind["source_operator"] == item["operator"]
    assert item["status"] in ("not_computable","approximate")
    if item["status"] == "approximate":
        assert item["evidence_id"].startswith("s4_")
        assert bind["definition_status"] == "specified" and bind["weights"] == "none"
        assert "never source replay" in item["reason"]
    else:
        assert item["operator"] is None and bind["definition_status"] == "unsupported"
status_counts = Counter(x["status"] for x in recipe["checks"])
assert status_counts == {"approximate":6,"not_computable":16}
for id_ in new_ids:
    item = next(x for x in recipe["checks"] if x["evidence_id"] == id_)
    bind = bindings[item["id"]]
    assert item["status"] == "not_computable" and bind["transform"] == "not_reported"
    assert bind["source_variable_units"] == {} and bind["weights"] == "weighted"

checks = read(c/"checks.json")
for artifact in checks["artifacts"]:
    path = (c/artifact["path"]).resolve()
    assert path.is_relative_to(c.resolve())
    assert sha(path) == artifact["sha256"], str(path)
validation = read(c/"static/STATIC_VALIDATION_01.json")
preflight = read(c/"static/SEMANTIC_PREFLIGHT_01.json")
assert validation["exit_code"] == preflight["exit_code"] == 0
validation_output = json.loads(validation["output"])
assert validation_output["contract"] == "valid" and validation_output["generator_executed"] is False
preflight_output = json.loads(preflight["output"])
semantic_counts = Counter(x["semantic_status"] for x in preflight_output["checks"])
assert semantic_counts == {"matched_declared":6,"unavailable":16}

assert sha(b/"request.json") == "618e6568b6733df5f08e264ff47b39d8ad96dabfabbabd5842c70bcde8f686ea"
admission = read(b/"SOURCE_INCREMENT_ADMISSION.json")
assert admission["task_sha256"] == sha(b/"task.json")
assert admission["registry_sha256"] == sha(b/"registry.json")
assert admission["proposal_sha256"] == sha(d/"PROPOSAL.json")
assert admission["review_sha256"] == sha(d/"REVIEW.json")
assert review["independent_checks"]["finite_fixed_order_moments"] is True

record = {
    "scope":"Static content/hash/AST audit only; no import or execution of generator, RNG, rows or target/evaluation files.",
    "builder_finalized_signal_received":True,
    "exact_scientific_parameter_changes":diff,
    "unreviewed_parameter_additions_deletions_or_changes":False,
    "generator_same_as_admitted_baseline":True,
    "generator_ast_parse_passed":True,
    "original_evidence_items_preserved_except_applicability_prose":20,
    "new_unit_empty_evidence_items":sorted(new_ids),
    "source_recipe_status_counts":dict(status_counts),
    "semantic_preflight_status_counts":dict(semantic_counts),
    "checks_artifact_hashes_verified":True,
    "request_bytes_identical_to_original":True,
    "admission_bindings_verified":True,
    "finite_moment_proof_reused":"Exact parameter patch and identical generator implement the already independently proved law; REVIEW.json bound below.",
    "candidate_sha256":{str(p.relative_to(c)).replace('\\','/'):sha(p) for p in sorted(c.rglob('*')) if p.is_file()},
    "bundle_sha256":{n:sha(b/n) for n in ('task.json','request.json','registry.json','SOURCE_INCREMENT_ADMISSION.json')},
    "proposal_sha256":sha(d/"PROPOSAL.json"),
    "scientific_review_sha256":sha(d/"REVIEW.json"),
    "all_checks_passed":True,
}
(d/"CANDIDATE_REVIEW_AUDIT.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in record.items() if k not in ('candidate_sha256','exact_scientific_parameter_changes')},indent=2))
