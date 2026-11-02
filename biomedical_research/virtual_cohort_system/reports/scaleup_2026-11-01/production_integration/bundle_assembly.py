"""Curated input assembly and mechanical plans, never scientific parameters.

No generator import, fitting, execution, target read, or release approval occurs.
The scientific submission and its independent reviews remain separate inputs.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from cohort_harness import contracts, lifecycle

HERE = Path(__file__).resolve().parent
SCALE = HERE.parent
PROJECT = SCALE.parents[1]
CONSTRUCTORS = ("A01", "A02", "A03", "A04", "A05", "S01")
LIMITS = dict(timeout_seconds=60, memory_mb=1024, output_bytes=2_000_000, log_bytes=10_000)
DESIGN_SHA256 = {"K01": "2e0fa250052ef0a71042041e00851caa17869185a4eeaa04675423aa1d7427bc",
                 "K02": "bb2d10a9237ed2733fccd02dd64789d95e487212f03890f2e9b35d0e18cf03ff"}
K02_COMPILATION_COMMITMENTS = {
    "compiled/COMPILATION_REPORT.json": "0cda12eaae358351c1c82d8c3f85cdd5d161cc036360f7aa86f43f9934662ccb",
    "COMPILER_VERIFICATION.json": "bf8397fca94b4108bc029dd21fe3cd6c4125c9ddd43a9ffaade7fe67b380cb11",
    "INDEPENDENT_REVIEW.md": "f5422fa9ad9e9540ec5abca2345004a5e0f5db9340ced79d548308ac56ed5d32",
}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _json(path):
    return lifecycle.read_json(path)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _case(case_id):
    contracts.require(case_id in {"K01", "K02"}, "Only the two fixed Wave A cases")
    return SCALE / ("case_" + case_id.lower())


def verify_design(case_id):
    case = _case(case_id)
    name = "REVIEWED_DESIGN_COMMITMENT.json" if case_id == "K01" else "REVIEWED_DESIGN_SNAPSHOT.json"
    contracts.require(lifecycle.sha256(case / name) == DESIGN_SHA256[case_id], "Scientific commitment changed")
    commitment = _json(case / name)
    for relative, expected in commitment["files"].items():
        contracts.require(lifecycle.sha256(lifecycle._path(case, relative)) == expected,
                          "Committed scientific artifact changed: " + relative)
    for relative, expected in commitment.get("read_only_dependencies", {}).items():
        contracts.require(lifecycle.sha256(lifecycle._path(PROJECT, relative)) == expected,
                          "Committed dependency changed: " + relative)
    return lifecycle.sha256(case / name)


def load_package(case_id):
    """Read only reviewed request/source metadata. No target data or fitted law."""
    case = _case(case_id)
    design_hash = verify_design(case_id)
    if case_id == "K01":
        compiler = _load("production_k01_sources", HERE / "k01_sources/k01_sources.py")
        compiled = compiler.compile_committed()
        manifest = _json(case / "request/packet_manifest.json")
        request_files = {n: (case / "request" / n).read_bytes() for n in manifest["builder_files"]}
        source_files = {compiler.ARTIFACT: (case / "request/selected_source_evidence.json").read_bytes()}
        evidence, templates = compiled["evidence"], compiled["source_context_templates"]
        registrations = compiled["registration_requirements"]
    else:
        manifest = _json(case / "request/manifest.json")
        # The builder does not receive the packaging script, S01, or admission/evaluation notes.
        request_files = {n: (case / "request" / n).read_bytes() for n in manifest["files"] if n != "build_request.py"}
        compiled_root = case / "assembly/compiled"
        for name, expected in K02_COMPILATION_COMMITMENTS.items():
            contracts.require(lifecycle.sha256(case / "assembly" / name) == expected,
                              "Reviewed K02 compiler commitment changed: " + name)
        report = _json(compiled_root / "COMPILATION_REPORT.json")
        for name, expected in report["compiled_files"].items():
            contracts.require(lifecycle.sha256(compiled_root / name) == expected,
                              "Reviewed K02 compiled artifact changed: " + name)
        evidence = _json(compiled_root / "evidence.json")
        templates = json.loads((compiled_root / "source_context_templates.json").read_text(encoding="utf-8"))
        registrations = json.loads((compiled_root / "registration_requirements.json").read_text(encoding="utf-8"))
        source_files = {"sources/greiner_source_packet.json": (case / "request/sources/greiner_source_packet.json").read_bytes()}
    expected_files = manifest["files"]
    for name, data in request_files.items():
        entry = expected_files[name]
        expected = entry["sha256"] if isinstance(entry, dict) else entry
        contracts.require(hashlib.sha256(data).hexdigest() == expected, "Request byte mismatch: " + name)
    task = json.loads(request_files["task_template.json"])
    contracts.validate_task(task)
    contracts.validate_evidence(evidence, task)
    for registration in registrations:
        contracts.require(registration["path"] in source_files, "Unknown source artifact")
        contracts.require(hashlib.sha256(source_files[registration["path"]]).hexdigest() == registration["sha256"],
                          "Source artifact mismatch")
    ids = {s["id"] for s in evidence["sources"]}
    contracts.require(ids == {r["source_id"] for r in registrations}, "Source registry coverage mismatch")
    target_metadata = json.loads(request_files["target_protocol_metadata.json"])
    target_id = "target_haalsi_pooled_poc" if case_id == "K01" else "target_turkana_adults"
    # The target measurement description is metadata, not an assumed assay conversion.
    measurement = ("Pooled released-cleaned capillary point-of-care glucose in mmol/L; feeding status not universally fasting"
                   if case_id == "K01" else
                   "Recorded study-protocol total and HDL cholesterol represented in canonical mmol/L; no assay or fasting equivalence asserted")
    descriptor = dict(population=task["population"], n_rows=5000, measurement=measurement)
    return dict(case_id=case_id, design_sha256=design_hash, request_files=request_files,
                source_files=source_files, evidence=evidence, templates=templates,
                registrations=registrations, task=task, target_id=target_id,
                target_descriptor=descriptor, target_metadata=target_metadata)


def package_digest(package):
    """Digest the permitted bytes and deterministic metadata, excluding private paths."""
    return digest({"case_id": package["case_id"], "design_sha256": package["design_sha256"],
                   "requests": {n: hashlib.sha256(b).hexdigest() for n, b in package["request_files"].items()},
                   "sources": {n: hashlib.sha256(b).hexdigest() for n, b in package["source_files"].items()},
                   "evidence": package["evidence"], "templates": package["templates"],
                   "target_id": package["target_id"], "target_descriptor": package["target_descriptor"]})


def _bundle_files(package):
    files = {"task.json": package["request_files"]["task_template.json"],
             "compiled_evidence.json": encoded(package["evidence"]),
             "source_context_templates.json": encoded(package["templates"]),
             "target_descriptor.json": encoded({"id": package["target_id"], **package["target_descriptor"]}),
             **package["source_files"],
             **{"request/" + n: b for n, b in package["request_files"].items()}}
    registry = {"artifacts": [{**r, "origin": "curator", "screening": "approved"} for r in package["registrations"]]}
    files["registry.json"] = encoded(registry)
    return files


def prepare_bundle(case_id, constructor, destination, curator_record):
    """Exclusively assemble an input bundle; does not release a construction.

    Curator registration is the coordinator's scoped provenance decision, not an
    independent scientific approval or an assertion of exact source transport.
    """
    contracts.require(constructor in CONSTRUCTORS, "Unknown reserved constructor")
    package = load_package(case_id)
    contracts.exact_keys(curator_record, {"curator_id", "reviewed_utc", "reason", "package_sha256"}, where="curator record")
    for key in ("curator_id", "reviewed_utc", "reason"):
        contracts.text(curator_record[key], "curator " + key)
    contracts.require(curator_record["package_sha256"] == package_digest(package), "Curator inspected another package")
    folder = Path(destination).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    files = _bundle_files(package)
    for name, data in files.items():
        path = folder.joinpath(*lifecycle.safe_relative(name))
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(data)
    receipt = {"schema_version": 1, "kind": "wave_a_builder_input_assembly", "case_id": case_id,
               "constructor": constructor, "package_sha256": package_digest(package),
               "design_sha256": package["design_sha256"], "curator": copy.deepcopy(curator_record),
               "files": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()},
               "source_screening_scope": "Reviewed selected artifact bytes and declared provenance; not extraction, transport or model validity certification",
               "clinical_construction_released": False, "generator_executed": False, "target_data_read": False}
    (folder / "INPUT_ASSEMBLY.json").write_bytes(encoded(receipt))
    lifecycle._registry(folder)
    return receipt


def verify_bundle_inputs(bundle):
    folder = Path(bundle).resolve()
    receipt = _json(folder / "INPUT_ASSEMBLY.json")
    package = load_package(receipt["case_id"])
    contracts.require(receipt["constructor"] in CONSTRUCTORS, "Unknown reserved constructor")
    contracts.require(receipt["package_sha256"] == package_digest(package), "Permitted source package changed")
    expected_files = {n: hashlib.sha256(b).hexdigest() for n, b in _bundle_files(package).items()}
    contracts.require(receipt["files"] == expected_files, "Input receipt does not cover the exact permitted packet")
    for name, expected in receipt["files"].items():
        contracts.require(lifecycle.sha256(lifecycle._path(folder, name)) == expected, "Builder input changed: " + name)
    lifecycle._registry(folder)
    return receipt


def build_bridge_plan(package, constructor, stage, model_spec, authoring):
    """Bind Agent-authored assumptions/contexts to fixed source and seed schemas.

    The caller retains model_spec bytes unchanged. No scientific parameter is
    supplied, replaced, inferred, fit, sampled, or selected by this function.
    """
    contracts.require(constructor in CONSTRUCTORS and stage in {"initial", "final"}, "Unknown construction/stage")
    case = package["case_id"]
    contracts.validate_spec(model_spec, {x["id"] for x in package["evidence"]["items"]})
    contracts.exact_keys(authoring, {"context_assumption_ids", "context_varying_parameters", "descriptive_proxies"}, where="context authoring")
    ids = [x["id"] for x in package["templates"]] + [package["target_id"]]
    assumptions = {x["id"] for x in model_spec["assumptions"]}
    mapping = authoring["context_assumption_ids"]
    contracts.require(set(mapping) == set(ids), "All and only scheduled context assumptions required")
    for context_id, values in mapping.items():
        contracts.string_list(values, "context assumptions")
        contracts.require(bool(values) and set(values) <= assumptions, "Unknown/missing Agent assumptions")
    params = model_spec["parameters"]
    contracts.require(params.get("active_context") == package["target_id"], "Parent must be target context")
    contracts.require(set(params.get("contexts", {})) == set(ids), "Scientific contexts differ from fixed schedule")
    contexts = copy.deepcopy(package["templates"])
    for context in contexts:
        cid = context["id"]
        descriptor = params["contexts"][cid]
        expected = dict(population=context["recipe"]["population"], n_rows=5000,
                        measurement=context["recipe"]["measurement"]["description"])
        contracts.require({k: descriptor.get(k) for k in expected} == expected, "Source descriptor differs: " + cid)
        context["assumption_ids"] = copy.deepcopy(mapping[cid])
        context["recipe"]["assumption_ids"] = copy.deepcopy(mapping[cid])
        if context["supplement"] is not None:
            context["supplement"]["assumption_ids"] = copy.deepcopy(mapping[cid])
            proxy = authoring["descriptive_proxies"].get(cid)
            if proxy is not None:
                contracts.exact_keys(proxy, {"assumption_ids", "reason"}, where="Agent descriptive proxy")
                contracts.string_list(proxy["assumption_ids"], "proxy assumptions")
                contracts.require(bool(proxy["assumption_ids"]) and set(proxy["assumption_ids"]) <= assumptions,
                                  "Unknown/missing proxy assumptions")
                contracts.text(proxy["reason"], "proxy reason")
            for check in context["supplement"]["checks"]:
                check["proxy"] = None if proxy is None else {**copy.deepcopy(proxy), "review": None}
    allowed_proxies = {c["id"] for c in contexts if c["supplement"] is not None}
    contracts.require(set(authoring["descriptive_proxies"]) <= allowed_proxies, "Unexpected proxy context")
    target = params["contexts"][package["target_id"]]
    contracts.require({k: target.get(k) for k in package["target_descriptor"]} == package["target_descriptor"],
                      "Target descriptor differs")
    contexts.append(dict(id=package["target_id"], role="target", source_ids=[],
                         assumption_ids=copy.deepcopy(mapping[package["target_id"]]), feedback_policy="none",
                         recipe=None, semantics=None, supplement=None))
    trials = [dict(id=f"{case}_{constructor}_{stage}_{cid}", context_id=cid, seed=3101+i, n_rows=5000)
              for i, cid in enumerate(ids[:-1])]
    trials.extend(dict(id=f"{case}_{constructor}_{stage}_target_{seed}", context_id=ids[-1], seed=seed, n_rows=5000)
                  for seed in (2101, 2102, 2103))
    return dict(schema_version=1, shared_parameters=[k for k in params if k not in {"contexts", "active_context"}],
                context_varying_parameters=copy.deepcopy(authoring["context_varying_parameters"]), contexts=contexts,
                trials=trials, execution_limits=copy.deepcopy(LIMITS),
                budget=dict(source_attempts=len(ids)-1, source_rows=5000*(len(ids)-1), target_attempts=3, target_rows=15000))
