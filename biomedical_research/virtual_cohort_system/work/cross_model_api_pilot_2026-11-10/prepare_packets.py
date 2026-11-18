"""Deterministically stage source-only author packets. Never execute model code.

Only explicitly admitted files below are read. The study configuration is a
custodian staging input: only its task schema/population and analysis purpose
are selected. No results, previous generators, credentials or .env files enter.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT.parents[1]
UNIT = Path(__file__).resolve().parent
PACKETS = UNIT / "packets"

# These expected hashes are the admitted packet anchors, not new approvals.
INPUTS = {
    "pns_evidence": (
        PROJECT / "work/next_case_validation_2026-11-09/author_packet/input/evidence_packet.json",
        "0d9f2df4baff869efe2d81e83b0058e6809e75af7b98c365bdf694b183ce03db",
    ),
    "pns_moment_algebra": (
        PROJECT / "work/next_case_validation_2026-11-09/author_packet/input/REPORTED_MOMENT_ALGEBRA.json",
        "d62535be9208ad50963540274b9f5f84109b805092e6097ed0c7983cb10d591c",
    ),
    "pns_staging_config": (
        PROJECT / "work/next_case_validation_2026-11-09/runtime/study_config.json",
        "8f9a071ed64818bbc74fa40d866e6beb191274d86ffb3e7239b85363360de088",
    ),
    "agongo": (
        WORKSPACE / "evcUseL03/sources/curated/AGONGO_2018_CURATOR_EXTRACTION.json",
        "e783bdc1a4d05800f5393636aff57dd58e161388a56286087d43888388b15851",
    ),
    "greiner": (
        WORKSPACE / "evcUseL03/sources/curated/GREINER_2021_CURATOR_EXTRACTION.json",
        "dd111f6d64daf9e7fad86f20b6a5a54142c3af1709b95ebab265344b0ee50ba5",
    ),
    "obirikorang": (
        WORKSPACE / "evcUseL03/sources/curated/OBIRIKORANG_2015_CURATOR_EXTRACTION.json",
        "bdbd18b458d1abc7e24d8c760e820dd0954a5bdb58c09c9a8f995c33a0fefc43",
    ),
    "lipid_metadata": (
        WORKSPACE / "evcUseL03/input/population_metadata.json",
        "a589c04d2e6a81a3c45bfcaec122b7da478dab4b69266d236a4061668c372045",
    ),
    "lipid_request": (
        WORKSPACE / "evcUseL03/request.json",
        "10b819ce12681e0c37c253867710e557f24125b3632aff9bf8506554ca2336af",
    ),
}

COMMON = """Construct one joint virtual cohort for the supplied population and requested analyses using only the task metadata and source evidence below. Choose and justify the statistical structure, scientific parameters, covariate composition, dependencies, support, uncertainty treatment and transfer assumptions yourself. No desired answer, direction, common correlation, distribution or exemplar generator is supplied. Missing source relationships remain unidentified by that evidence; they are not automatically zero or independent. You may make explicit assumptions to complete a usable joint model.

The requested analyses are association projections of the generated joint law, not causal intervention effects. Distinguish source statistics from model parameters and from requested population estimands. Preserve the source population, measurement, operator, adjustment set, scale, units and uncertainty. A confidence interval or standard error is not individual dispersion. Repeated summaries from one cohort are dependent evidence. A reported unadjusted, differently adjusted, log-scale or rank statistic is not the requested conditional raw-scale statistic without a justified bridge. State any assumptions used to resolve source ambiguities. Existing curator extraction claims are historical provenance, not a fresh authentication of original articles.

Use no retrieval, browsing, tools, external files, network access, other datasets, previous generators or remembered target outcome statistics. Bibliographic links are citations only. Choose from the supplied evidence and explicit assumptions, not from outside numerical information. Do not claim that a check or execution has occurred. Do not generate a data table in this response.

Return exactly one valid JSON object, without markdown fences or surrounding prose, with exactly these three top-level keys:
1. "model_spec": an object containing the scientific structure and every numerical scientific setting used by the program. You choose its internal schema. Keep settings in this object and read them in the program; do not hide scientific constants in executable code.
2. "generator_py": a JSON string containing the complete minimal Python module. Define a top-level synchronous generate(observed, spec, seed) with exactly three positional parameters and no variadic or keyword-only parameters. It will be called as generate(None, {"task": task_json, "model": model_spec}, seed). Return a pandas.DataFrame with exactly task_json["n_rows"] rows and exactly the task columns in the listed order. Identifiers must be unique and nonmissing; all required values must be finite, within stated bounds and correctly coded. Use the seed reproducibly. You may import numpy, pandas, scipy and Python's math module. Do not read/write files, access the network, launch processes, load external resources, or include a runner/main block. Runtime inputs are only observed=None, spec and seed.
3. "decision_record": an object containing "structure" (a concise account of the chosen joint law), "parameter_provenance" (an array of records for every scientific parameter or parameter vector), "requested_estimands" (an array with one record per requested analysis), "limitations" (an array), and "checks_actually_performed" (an array, empty if none). Each parameter record must identify its actual JSON path within model_spec, meaning/statistical operator, conditioning set, scale, unit, classification as reported/derived/assumed/mixed, source pointers with original locators when applicable, derivation when applicable, and unverified assumptions. Source pointers must resolve to evidence supplied below. Explicitly identify covariate composition, dependence, distribution/tail, selection and measurement-transfer assumptions, including any deliberate omission. A compact record may cover a named vector if each component's meaning and provenance are unambiguous. Each requested-estimand record must give the analysis ID, exact model-implied population value only if derived, otherwise null, its unit, and the derivation or reason unavailable. A literal coefficient or source statistic is not a substitute for the requested estimand. Do not fabricate an exact value from a finite simulated sample.

The deliverable is one executable scientific construction with a traceable specification. Source compatibility and software checks alone do not establish validity for the requested population. Keep the program compact and put scientific explanation in decision_record.
"""


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_inputs() -> tuple[dict, list]:
    objects, records = {}, []
    for key, (path, expected) in INPUTS.items():
        raw = path.read_bytes()
        actual = digest(raw)
        if actual != expected:
            raise RuntimeError(f"Admitted input hash mismatch for {key}: {actual}")
        objects[key] = json.loads(raw.decode("utf-8-sig"))
        records.append({"id": key, "path": str(path), "sha256": actual,
                        "bytes": len(raw), "verified_against_admitted_anchor": True})
    return objects, records


def source_provenance(key: str) -> dict:
    path, sha = INPUTS[key]
    return {"extraction_artifact": path.name, "extraction_sha256": sha,
            "original_source_reauthentication_performed": False}


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8", newline="\n")


def pns_packet(inputs: dict) -> tuple[dict, dict, dict]:
    config = inputs["pns_staging_config"]
    old_task = config["task"]
    # Whitelist only author-visible schema/population; replace historical tools/budgets.
    task = {key: copy.deepcopy(old_task[key]) for key in
            ("schema_version", "mode", "population", "row_id", "n_rows", "columns")}
    task["task_id"] = "api_pilot_pns_whole_cohort_v1"
    task["n_rows"] = 3000
    task["information_policy"] = {"mode": "published_evidence",
                                  "excluded_cohorts": ["PNS", "Pesquisa Nacional de Saude",
                                                       "National Health Survey Brazil"],
                                  "allowed_tools": []}
    task["budget"] = {"source_queries": 0, "source_downloads": 0, "revisions": 0}
    purpose = config["purpose"].replace(" Return all prespecified diagnostics.", "")
    analyses = {
        "purpose": purpose,
        "row_weighting": "equal weight, representing the declared weighted analytical population",
        "design_columns": ["1", "(age-50)/10", "female", "(bmi-25)/5"],
        "outcome_unit_conversion": {"sbp": 1, "dbp": 1},
        "analyses": [
            {"id": "bmi_sbp", "outcome": "sbp", "estimator": "unweighted OLS with intercept",
             "quantity": "coefficient of (bmi-25)/5", "unit": "mmHg per 5 kg/m^2"},
            {"id": "bmi_dbp", "outcome": "dbp", "estimator": "unweighted OLS with intercept",
             "quantity": "coefficient of (bmi-25)/5", "unit": "mmHg per 5 kg/m^2"},
            {"id": "residual_correlation", "outcomes": ["sbp", "dbp"],
             "estimator": "Pearson correlation of paired centered residuals from the two above regressions on the same rows",
             "quantity": "residual Pearson correlation", "unit": "1"},
        ],
    }
    if config["analyses"] != [a["id"] for a in analyses["analyses"]]:
        raise RuntimeError("PNS analysis-ID mapping differs from admitted contract")
    source = copy.deepcopy(inputs["pns_evidence"])
    # Unavailable local resources are provenance only; do not provide historical paths.
    removed = ("local_original_pattern", "original_fulltext", "local_reading_receipt", "derivation_script")
    for item in source["sources"]:
        for key in removed:
            item.pop(key, None)
    evidence = {
        "provenance": [source_provenance("pns_evidence"), source_provenance("pns_moment_algebra")],
        "source_evidence": source,
        "reported_moment_algebra": copy.deepcopy(inputs["pns_moment_algebra"]),
    }
    return task, analyses, evidence


def compact_table(records: list[dict]) -> dict:
    """Lossless factoring of repeated JSON keys; row order and values are preserved."""
    columns = list(dict.fromkeys(k for row in records for k in row))
    if any(set(row) != set(columns) for row in records):
        # Retain heterogeneously shaped source rows instead of inventing missing fields.
        return {"format": "records", "records": records}
    table = {"format": "column_order_then_rows", "columns": columns,
             "rows": [[row[key] for key in columns] for row in records]}
    assert [dict(zip(columns, row)) for row in table["rows"]] == records
    return table


def lipid_packet(inputs: dict) -> tuple[dict, dict, dict]:
    metadata = inputs["lipid_metadata"]
    request = inputs["lipid_request"]
    if request["n_rows"] != 3000 or request["mode"] != "whole_cohort":
        raise RuntimeError("Unexpected admitted lipid schema")
    units = metadata["output_schema"]["units"]
    columns = []
    for name in metadata["output_schema"]["ordered_columns"]:
        col = {"name": name, "kind": "number", "unit": units.get(name, ""),
               "role": "generated", "nullable": False}
        if name == "id":
            col.update(kind="string", role="identifier")
        elif name == "sex":
            col.update(kind="category", categories=["F", "M"])
        elif name == "age":
            col.update(minimum=metadata["eligibility"]["minimum_age_inclusive"])
        elif name in metadata["eligibility"]["strictly_positive"]:
            col.update(minimum=0)  # Exact strict positivity is retained in eligibility below.
        columns.append(col)
    task = {"schema_version": 1, "task_id": "api_pilot_lipid_whole_cohort_v1",
            "mode": request["mode"], "population": request["population"], "row_id": "id",
            "n_rows": 3000, "columns": columns,
            "information_policy": {"mode": "published_evidence",
                                   "excluded_cohorts": ["Turkana 2018-2019 target outcomes"],
                                   "allowed_tools": []},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    analyses = {"purpose": "Construct one joint adult cohort supporting the three supplied lipid associations. These are descriptive projections, not intervention effects.",
                "row_weighting": "equal weight", "design_columns": ["1", "(age-50)/10", "I(sex=='F')", "(bmi-25)/5"],
                "outcome_unit_conversion": {"total_cholesterol": 38.67, "hdl_cholesterol": 38.67},
                "conversion_scope": "Delivered mmol/L converted to mg/dL for slopes; numerical units only, not assay equivalence.",
                "eligibility": copy.deepcopy(metadata["eligibility"]),
                "analyses": copy.deepcopy(request["intended_analyses"])}
    if analyses["analyses"] != metadata["analyses"]:
        raise RuntimeError("Admitted lipid request and metadata analyses differ")
    safe_metadata_keys = ("context_id", "country", "named_context", "population", "geographic_metadata",
                          "eligibility", "measurements", "composition", "inference_scope", "unit_mapping")
    agongo = copy.deepcopy(inputs["agongo"])
    obiri = copy.deepcopy(inputs["obirikorang"])
    greiner = copy.deepcopy(inputs["greiner"])
    greiner.pop("reused_harness_source_ids", None)
    greiner.pop("implementation_disposition", None)
    if "origin" in greiner:
        greiner["origin"].pop("curated_artifact", None)
    # Historical workflow vetoes are not scientific parameters or task restrictions.
    # Preserve factual scale/adjustment warnings, reported numbers and uncertainty.
    for row in greiner["reported_regressions_context_only"]:
        row.pop("numerical_calibration_allowed", None)
    for issue in greiner["unresolved_issues"]:
        if issue["id"] == "regression_scale_unresolved":
            issue["resolution"] = "Response/predictor transformation is unresolved in the supplied extraction. Any numerical use requires an explicit additional scale assumption; no conversion is supplied."
        elif issue["id"] == "source_quantile_convention_unreported":
            issue["resolution"] = "Age median/Q1/Q3 are retained as reported. Their quantile convention is unreported; numerical reconstruction requires an explicit convention assumption."
    greiner["reported_statistics"] = compact_table(greiner["reported_statistics"])
    greiner["reported_regressions_context_only"] = compact_table(greiner["reported_regressions_context_only"])
    evidence = {
        "provenance": [source_provenance(k) for k in ("agongo", "greiner", "obirikorang", "lipid_metadata")],
        "population_metadata": {k: copy.deepcopy(metadata[k]) for k in safe_metadata_keys},
        "sources": [agongo, greiner, obiri],
        "table_encoding": "Where format=column_order_then_rows, each row is the values for columns in order; all reported rows and values are preserved. Else format=records retains the original row objects.",
    }
    return task, analyses, evidence


def main() -> None:
    if (PACKETS / "FREEZE.json").exists():
        raise RuntimeError("Packets are frozen; create a separately versioned assembly instead")
    inputs, records = load_inputs()
    PACKETS.mkdir(parents=True, exist_ok=True)
    (PACKETS / "common_prompt.txt").write_text(COMMON, encoding="utf-8", newline="\n")
    case_records = {}
    for case, builder in (("PNS", pns_packet), ("LIPID", lipid_packet)):
        folder = PACKETS / case
        folder.mkdir(exist_ok=True)
        task, analyses, evidence = builder(inputs)
        for name, obj in (("task.json", task), ("requested_analyses.json", analyses), ("evidence.json", evidence)):
            dump(folder / name, obj)
        # The sole author payload is assembled only from these approved visible objects.
        sections = [COMMON.rstrip(), "TASK_JSON", json.dumps(task, ensure_ascii=False, separators=(",", ":")),
                    "REQUESTED_ANALYSES_JSON", json.dumps(analyses, ensure_ascii=False, separators=(",", ":")),
                    "SOURCE_EVIDENCE_JSON", json.dumps(evidence, ensure_ascii=False, separators=(",", ":"))]
        prompt = "\n\n".join(sections) + "\n"
        (folder / "prompt.txt").write_text(prompt, encoding="utf-8", newline="\n")
        case_records[case] = {"author_payload": f"{case}/prompt.txt", "source_input_policy": "identical bytes for every construction of this case",
                              "files": [{"path": f"{case}/{name}", "sha256": digest((folder / name).read_bytes()),
                                         "bytes": (folder / name).stat().st_size}
                                        for name in ("task.json", "requested_analyses.json", "evidence.json", "prompt.txt")]}
    manifest = {"schema_version": 1, "status": "staged_pending_independent_audit_not_frozen",
                "host_only_do_not_send_to_author": True, "original_input_anchors": records,
                "assembly_script_sha256": digest(Path(__file__).read_bytes()),
                "common_prompt_sha256": digest((PACKETS / "common_prompt.txt").read_bytes()),
                "response_keys": ["model_spec", "generator_py", "decision_record"],
                "abi": "generate(None, {'task':task_json,'model':model_spec}, seed) -> pandas.DataFrame",
                "cases": case_records}
    dump(PACKETS / "ASSEMBLY_MANIFEST.json", manifest)
    print(json.dumps({"status": manifest["status"], "cases": case_records}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
