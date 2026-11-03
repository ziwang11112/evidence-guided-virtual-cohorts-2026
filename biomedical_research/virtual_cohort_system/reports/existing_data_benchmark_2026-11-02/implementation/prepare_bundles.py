"""Prepare metadata-only constructor bundles; never import or run a generator.

Approved arm packets are copied byte-for-byte. Existing harness contracts and
lifecycle are used unchanged. This script refuses an existing evcB destination.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys


SEEDS = [1701, 1702, 1703]
ARMS = ["E0", "E1"]
STAGE = "initial"
FIVE_FILES = ["evidence.json", "model_spec.json", "generator.py", "decision.md", "checks.json"]


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def verify_approved_packets(evidence_dir):
    evidence_dir = Path(evidence_dir)
    approval = read(evidence_dir / "PACKET_REVIEW.json")
    if approval["decision"] != "approved_sanitized_evidence_packet_content_only":
        raise ValueError("Packet content approval is not present")
    approved = {r["path"]: r["sha256"] for r in approval["arm_bindings"]}
    packets = {}
    for arm in ARMS:
        data = (evidence_dir / f"{arm}.json").read_bytes()
        if digest(data) != approved[f"{arm}.json"]:
            raise ValueError(f"Approved {arm} packet bytes changed")
        packets[arm] = (json.loads(data.decode("utf-8")), data)
    if packets["E0"][0]["shared_base"] != packets["E1"][0]["shared_base"]:
        raise ValueError("Common source information differs between arms")
    if packets["E0"][0]["relationship_records"]:
        raise ValueError("E0 contains added relationships")
    if [x["id"] for x in packets["E1"][0]["relationship_records"]] != approval["relationship_review"]["approved_ids"]:
        raise ValueError("E1 relationship set differs from approval")
    return packets, approval


def common_task(original):
    task = copy.deepcopy(original)
    task["task_id"] = "existing-CHNS-2009-evidence-information-benchmark-v1"
    task["n_rows"] = 3000
    task["information_policy"]["allowed_tools"] = [
        "admitted_source_read", "request_evidence_clarification", "contract_validation"
    ]
    task["budget"] = {"source_queries": 0, "source_downloads": 0, "revisions": 0}
    return task


def _item(identifier, source_id, locator, variables, kind, estimate, unit,
          selection, applicability, adjustment=None, **extra):
    item = {
        "id": identifier, "source_id": source_id, "locator": locator,
        "variables": variables, "kind": kind, "estimate": estimate,
        "unit": unit, "uncertainty": {"kind": "not_reported"},
        "adjustment": adjustment or [], "selection": selection,
        "applicability": applicability,
    }
    item.update(extra)
    return item


def compile_evidence(packet, packet_bytes, ngsp_bytes):
    """Expand reported grouped facts without converting units or fitting laws."""
    metadata = {s["id"]: s for s in packet["shared_base"]["source_metadata"]}
    sources, items, groups = [], [], {}
    for source in metadata.values():
        sources.append({
            "id": source["id"], "identifier": "doi:" + source["doi"],
            "population": source["population"] + " Source context: " + source["source_context_id"] +
                ". Reported marginal sample count is source-specific, not target size or a guaranteed regression/pair count.",
            "measurement": json.dumps(source["measurement"], ensure_ascii=False, sort_keys=True) +
                " Original weights: " + source["source_weights"] + ". " + source["source_preprocessing"],
            "cohort_ids": [source["family"]],
            "artifacts": [{"path": "sources/evidence_packet.json", "sha256": digest(packet_bytes)}],
        })
    for marginal in packet["shared_base"]["grouped_marginal_records"]:
        identifier = marginal["id"]
        source = metadata[marginal["source_id"]]
        selection = source["population"] + " Source context: " + marginal["source_context_id"] + "."
        context = ("Source marginal only; not target calibration. " + marginal["role"] +
            ". Original analytic weighting unreported. Field-specific sample size and estimator uncertainty not supplied.")
        native = marginal.get("variable", "gender_membership")
        created = []
        if marginal["kind"] == "reported_mean_and_individual_sd":
            for component, kind in [("mean", "mean"), ("individual_sd", "sd")]:
                suffix = "MEAN" if kind == "mean" else "SD"
                created.append(_item(identifier + "_" + suffix, source["id"], marginal["locator"],
                    [native], kind, marginal[component], marginal["unit"], selection,
                    context + " Group " + identifier + ": mean and individual SD are related summaries, not independent evidence. " +
                    "Individual SD is not an estimator SE; its divisor is unreported. No residual law or tail model follows."))
        elif marginal["kind"] == "reported_median_and_quartile_endpoints":
            for component, suffix, kind, q in [("median", "MEDIAN", "median", None), ("q1", "Q1", "quantile", .25), ("q3", "Q3", "quantile", .75)]:
                extra = {"method": "not_reported"}
                if q is not None:
                    extra["q"] = q
                created.append(_item(identifier + "_" + suffix, source["id"], marginal["locator"],
                    [native], kind, marginal[component], marginal["unit"], selection,
                    context + " Group " + identifier + ": quartile endpoints are not an SD or confidence interval. " +
                    "Quantile convention is unreported; no Gaussian conversion is performed.", **extra))
        elif marginal["kind"] == "reported_count_with_derived_fraction":
            if marginal["derived_fraction"] != marginal["numerator"] / marginal["denominator"]:
                raise ValueError("Count fraction does not match retained integers")
            created.append(_item(identifier + "_FRACTION", source["id"], marginal["locator"],
                [native], "proportion", marginal["derived_fraction"], "1", selection,
                context + f" Derived {marginal['category']} count ratio {marginal['numerator']}/{marginal['denominator']}. " +
                marginal["derivation"] + ". Preserve category identity; no target composition is supplied."))
        else:
            raise ValueError("Unapproved marginal record kind")
        items.extend(created)
        groups[identifier] = [x["id"] for x in created]
    for relationship in packet["relationship_records"]:
        source = metadata[relationship["source_id"]]
        definition = relationship["executable_definition_candidate"]
        reported = relationship["reported"]
        if definition["kind"] == "ols_coefficient":
            kind = "ols_coefficient"
            variables = [definition["outcome"], definition["term"]]
            adjustment = [x for x in definition["regressors"] if x != definition["term"]]
        else:
            kind = "correlation" if definition["kind"] == "pearson_correlation" else "spearman_correlation"
            variables = definition["columns"]
            adjustment = []
        # The strict schema cannot represent an interval with unknown level.
        # Preserve it in qualified factual metadata, never invent a CI level/SE.
        qualifications = {key: value for key, value in relationship.items()
                          if key not in {"id", "source_id", "source_locator", "evidence_regime"}}
        items.append(_item(relationship["id"], source["id"], relationship["source_locator"],
            variables, kind, reported["estimate"], reported["unit"],
            source["population"] + " Source context: " + relationship["source_context_id"] + ".",
            "Qualified source point-comparison definition; strict replay remains not_computable. " +
            "This is not a target parameter or target desired result. " +
            json.dumps(qualifications, ensure_ascii=False, sort_keys=True), adjustment=adjustment))
    sources.append({
        "id": "S_NGSP_UNITS", "identifier": "https://ngsp.org/ifccngsp.asp",
        "population": "Official measurement-scale guidance, not a participant cohort or independent empirical constraint.",
        "measurement": "NGSP HbA1c percent = 0.09148 * IFCC HbA1c mmol/mol + 2.152. A scale relation does not certify assay equivalence.",
        "cohort_ids": [], "artifacts": [{"path": "sources/NGSP_UNITS.md", "sha256": digest(ngsp_bytes)}],
    })
    items.append(_item("U_NGSP_SCALE", "S_NGSP_UNITS", "The IFCC and NGSP, Table 2",
        ["HbA1c_IFCC", "HbA1c_percent"], "contextual", None, "", "Unit guidance, not a selected participant sample.",
        "NGSP%=0.09148*IFCC(mmol/mol)+2.152. Multiply slopes, SDs, SEs and slope-interval endpoints by 0.09148 only; " +
        "levels/intercepts also use the offset; variances use its square. These are dependent algebraic representations, " +
        "not additional empirical constraints. No assay, selection, plasma/serum or fasting-glucose equivalence follows. " +
        "No converted empirical coefficient is installed."))
    evidence = {"schema_version": 1, "sources": sources, "items": items}
    registry = {"artifacts": [dict(source_id=s["id"], path=a["path"], sha256=a["sha256"],
                                  origin="curator", screening="approved")
                              for s in sources for a in s["artifacts"]]}
    return evidence, registry, groups


def build(project, workspace, *, check_only=False):
    project, workspace = Path(project).resolve(), Path(workspace).resolve()
    implementation = Path(__file__).resolve().parent
    evidence_dir = implementation.parent / "evidence"
    if project not in implementation.parents:
        raise ValueError("Implementation is not in the declared project")
    sys.path.insert(0, str(project))
    from cohort_harness.contracts import validate_task, validate_evidence
    from cohort_harness.lifecycle import _registry
    packets, approval = verify_approved_packets(evidence_dir)
    old_task_path = project / "work/chns_admission_2026-11-01/f2/task.json"
    ngsp_path = project / "work/chns_admission_2026-11-01/f2/evidence/sources/NGSP_UNITS.md"
    task = common_task(read(old_task_path))
    validate_task(task)
    task_bytes, ngsp_bytes = encoded(task), ngsp_path.read_bytes()
    docs = {name: (implementation / name).read_bytes()
            for name in ["INTERFACE.md", "AGENT_PROMPT.md", "contracts_guidance.md"]}
    compiled = {}
    for arm, (packet, packet_bytes) in packets.items():
        evidence, registry, groups = compile_evidence(packet, packet_bytes, ngsp_bytes)
        ids = validate_evidence(evidence, task)
        expected = 32 if arm == "E0" else 36
        if len(ids) != expected or len(groups) != 15:
            raise ValueError("Compiled evidence coverage differs from fixed scope")
        compiled[arm] = (encoded(evidence), encoded(registry), groups)
    # Registered packet hashes differ by arm; the empirical base items do not.
    e0_items = json.loads(compiled["E0"][0])["items"]
    e1_items = [x for x in json.loads(compiled["E1"][0])["items"] if not x["id"].startswith("R_")]
    if e0_items != e1_items:
        raise ValueError("Compiled common source facts differ between arms")
    summary = {"source_packet_bytes_verified": True, "common_task_sha256": digest(task_bytes),
        "common_compiled_items_exactly_equal": True, "item_counts": {"E0": 32, "E1": 36},
        "grouped_marginal_count": 15, "n_rows": 3000, "seeds": SEEDS,
        "stage": STAGE, "generator_created_or_executed": False}
    if check_only:
        return summary
    destination = workspace / "evcB"
    if destination.exists():
        raise FileExistsError("evcB already exists; no overwrite, deletion or budget reset permitted")
    if destination.resolve().parent != workspace or destination.is_symlink():
        raise ValueError("Short-path destination is not the intended workspace child")
    # All metadata validation happens before the first materialization.
    destination.mkdir()
    entries = []
    for arm in ARMS:
        evidence_bytes, registry_bytes, groups = compiled[arm]
        write_new(implementation / "compiled" / arm / "evidence.json", evidence_bytes)
        for number in range(1, 6):
            identifier = f"{arm}_A{number:02d}"
            bundle = destination / identifier
            files = {"task.json": task_bytes, "registry.json": registry_bytes,
                "sources/evidence_packet.json": packets[arm][1], "sources/NGSP_UNITS.md": ngsp_bytes,
                "input/compiled_evidence.json": evidence_bytes, "candidates/initial/evidence.json": evidence_bytes}
            files.update({"input/" + name: data for name, data in docs.items()})
            for name, data in files.items():
                write_new(bundle / name, data)
            _registry(bundle)  # Metadata/hash verification only; no candidate execution.
            allowlist = ["task.json", "sources/evidence_packet.json", "sources/NGSP_UNITS.md",
                "input/compiled_evidence.json", "input/INTERFACE.md", "input/AGENT_PROMPT.md",
                "input/contracts_guidance.md", "candidates/initial/evidence.json"]
            entries.append({"constructor_id": identifier, "arm": arm,
                "workspace_relative_bundle": bundle.relative_to(workspace).as_posix(),
                "candidate_relative": "candidates/initial", "candidate_cli_name": "initial",
                "stage": STAGE, "seeds": SEEDS,
                "run_ids": [f"initial_{seed}" for seed in SEEDS],
                "constructor_read_allowlist": allowlist,
                "constructor_write_allowlist": ["candidates/initial/" + x for x in FIVE_FILES if x != "evidence.json"],
                "fixed_candidate_file": "candidates/initial/evidence.json",
                "prepared_file_sha256": {name: digest(data) for name, data in files.items()}})
    write_new(implementation / "task.json", task_bytes)
    manifest = {"schema_version": 1, "status": "metadata_prepared_not_constructor_or_runtime_release",
        "scope": "coordinator_only_not_constructor_input", **summary,
        "workspace_root": str(workspace), "project_root": str(project),
        "required_submission_files": FIVE_FILES, "constructors": entries,
        "source_packet_review_sha256": digest((evidence_dir / "PACKET_REVIEW.json").read_bytes()),
        "source_task_sha256": digest(old_task_path.read_bytes()), "ngsp_guidance_sha256": digest(ngsp_bytes),
        "compiler_sha256": digest(Path(__file__).read_bytes()),
        "unchanged_harness_sha256": {name: digest((project / "cohort_harness" / name).read_bytes())
                                     for name in ["contracts.py", "lifecycle.py"]},
        "compiled_group_item_map": {arm: compiled[arm][2] for arm in ARMS},
        "counts": {"constructors": 10, "stages_per_constructor": 1, "scheduled_target_attempts": 30,
            "source_generations": 0, "actual_generated_tables": 0, "actual_target_evaluations": 0},
        "gates_pending": ["independent_compiler_interface_review", "constructor_release", "candidate_review_and_freeze", "runtime_release"]}
    write_new(destination / "PREPARATION_MANIFEST.json", encoded(manifest))
    write_new(implementation / "PREPARATION_MANIFEST.json", encoded(manifest))
    return {**summary, "prepared_constructor_bundles": len(entries), "destination": str(destination),
            "manifest": str(implementation / "PREPARATION_MANIFEST.json")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(args.project, args.workspace, check_only=args.check_only), indent=2))


if __name__ == "__main__":
    main()
