"""Compile independent source supports into an unchanged v1 execution contract.

This compiler validates declared source/target supports against a computational
model domain. It does not reconstruct a source population, transform values,
select rows, execute a generator, or establish scientific transport validity.
The replay adapter owns validation of the complete context envelope, source-file
bindings, evidence/check definitions, and execution receipts.
"""
from __future__ import annotations

import copy

import pandas as pd

from .contracts import exact_keys, require, string_list, text, validate_input, validate_task


_IDENTITY_FIELDS = ("name", "kind", "role", "unit", "nullable")


def _known_assumptions(value, known: set[str], where: str) -> None:
    string_list(value, where)
    require(set(value) <= known, f"Unknown assumption in {where}")


def _same_identity(columns: list[dict], target_columns: list[dict], where: str) -> None:
    require([c["name"] for c in columns] == [c["name"] for c in target_columns],
            f"{where} must preserve ordered column names")
    for column, target in zip(columns, target_columns):
        for field in _IDENTITY_FIELDS:
            require(column[field] == target[field],
                    f"{where} changes {field} for {target['name']}")


def _within_domain(columns: list[dict], domain_columns: list[dict], where: str) -> None:
    """Compare declared supports, including generated variables absent in input."""
    for column, domain in zip(columns, domain_columns):
        name = column["name"]
        if column["kind"] in {"number", "integer"}:
            for bound in ("minimum", "maximum"):
                if bound not in domain:
                    continue
                require(bound in column,
                        f"{where} {name} needs a declared {bound} for the finite model domain")
                within = column[bound] >= domain[bound] if bound == "minimum" else column[bound] <= domain[bound]
                require(within, f"{where} {name} {bound} is outside the model domain")
        elif column["kind"] == "category":
            require(set(column["categories"]) <= set(domain["categories"]),
                    f"{where} {name} categories are outside the model domain")


def compile_source_task(target_task: dict, context: dict, model_domain: dict,
                        source_frame: pd.DataFrame, *, assumption_ids: set[str]) -> dict:
    """Return a validated v1 source task without mutating any supplied object.

    The target must be an enrichment task. Context and model-domain columns use
    full v1 column schemas. Their ordered identities, types, roles, units and
    nullability must match the target; numeric supports and category sets may
    differ. Both source and target declared supports must fit inside the model
    domain. A missing bound is not interpreted as finite merely because the
    supplied rows happen to lie inside a finite computational domain.

    Context ``measurement`` is identity-only. ``assumption_ids`` on the context
    and domain are references to the supplied known assumption set, not a claim
    that those assumptions have been scientifically established. The caller
    validates all remaining replay-context fields and the outer plan version.
    """
    validate_task(target_task)
    require(target_task["mode"] == "enrichment", "Source contexts support enrichment tasks only")
    require(isinstance(context, dict), "Source context must be an object")
    require(isinstance(source_frame, pd.DataFrame), "Source input must be a pandas DataFrame")
    require(isinstance(assumption_ids, set), "Known assumption IDs must be a set")
    for identifier in assumption_ids:
        text(identifier, "Known assumption ID")

    exact_keys(model_domain, {"columns", "assumption_ids", "description"}, where="model domain")
    text(model_domain["description"], "Model domain description")
    _known_assumptions(model_domain["assumption_ids"], assumption_ids, "model domain assumption_ids")
    _known_assumptions(context.get("assumption_ids"), assumption_ids, "source context assumption_ids")
    text(context.get("population"), "Source context population")
    measurement = context.get("measurement")
    exact_keys(measurement, {"mode", "description"}, where="source measurement mapping")
    require(measurement["mode"] == "identity", "Only identity source measurement mapping is supported")
    text(measurement["description"], "Source measurement description")

    # Copy every nested object before compiling. Only these three task fields
    # change; task identity, mode, policy, budget and row-ID contract stay intact.
    source_task = copy.deepcopy(target_task)
    source_task.update(population=context["population"], n_rows=len(source_frame),
                       columns=copy.deepcopy(context.get("columns")))
    domain_task = copy.deepcopy(target_task)
    domain_task.update(population=model_domain["description"], n_rows=len(source_frame),
                       columns=copy.deepcopy(model_domain["columns"]))
    validate_task(source_task)
    validate_task(domain_task)
    _same_identity(source_task["columns"], target_task["columns"], "Source context")
    _same_identity(domain_task["columns"], target_task["columns"], "Model domain")
    _within_domain(target_task["columns"], domain_task["columns"], "Target")
    _within_domain(source_task["columns"], domain_task["columns"], "Source")

    # validate_input enforces exact covariate-only columns/order, row count,
    # identifiers, types, nullability and declared supports. No clipping or
    # filtering can make an otherwise invalid frame pass either contract.
    validate_input(source_frame, source_task)
    validate_input(source_frame, domain_task)
    return source_task
