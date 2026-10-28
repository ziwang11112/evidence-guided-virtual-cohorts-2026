"""Source-only diagnostics across a declared schedule of generator seeds.

These are simulation ranges, not confidence intervals or automatically
independent replications. No biological threshold or objective
function is selected here. Caller records the schedule before running it.
"""
from __future__ import annotations

import statistics
from pathlib import Path

from .contracts import require
from .lifecycle import _bundle, read_json, sha256
from .source_replay import verify_source_replay


def _signature(context, check):
    return {"context_id": context["id"], "check_id": check["id"],
            "context_input_sha256": context["context_input_sha256"],
            "measurement": context["measurement"],
            "context_assumption_ids": context["context_assumption_ids"],
            **{key: check[key] for key in ("evidence_id", "operator", "assumption_ids",
                                           "reason", "reported_value")}}


def summarize_source_portfolio(bundle, candidate, replay_ids, seeds):
    """Verify every requested replay, reject changed schedules, retain every check.

    The ordered seed list is an explicit input, never inferred by selecting
    available successful runs. A failure blocks the summary. Undefined numerical
    checks remain visible with no aggregate, rather than being silently dropped.
    """
    require(isinstance(replay_ids, list) and isinstance(seeds, list), "Schedule lists required")
    require(len(seeds) >= 2 and len(seeds) == len(replay_ids), "At least two matched scheduled runs required")
    require(all(type(seed) is int for seed in seeds), "Seeds must be integers")
    require(len(set(seeds)) == len(seeds), "Duplicate seeds are repeated runs, not new simulation draws")
    require(all(isinstance(r, str) for r in replay_ids) and len(set(replay_ids)) == len(replay_ids),
            "Distinct replay IDs required")
    bundle = _bundle(bundle)
    groups, expected, binding, receipts = {}, None, None, []
    for replay_id, seed in zip(replay_ids, seeds):
        report = verify_source_replay(bundle, replay_id, candidate=candidate)
        require(report["status"] == "success", "All scheduled source executions must succeed")
        require(report["limits"]["seed"] == seed, "Replay seed differs from ordered schedule")
        if binding is None:
            binding = report["parent"]
        require(report["parent"] == binding, "Portfolio mixes different candidate bindings")
        receipts.append({"replay_id": replay_id, "seed": seed,
                         "sha256": sha256(bundle / "source_replays" / replay_id / "replay.json")})
        found = set()
        for context in report["contexts"]:
            require(context["generation_link_verified"], "Source context lacks verified generation")
            for check in context["checks"]:
                require(check["generation_link_verified"], "Source check lacks verified generation")
                key = (context["id"], check["id"])
                require(key not in found, "Duplicate source diagnostic")
                found.add(key)
                signature = _signature(context, check)
                entry = groups.setdefault(key, {"definition": signature, "runs": []})
                require(entry["definition"] == signature, "Diagnostic definition changed across seeds")
                value = check.get("value")
                entry["runs"].append({"seed": seed, "status": check["status"], "value": value,
                                      "difference": check.get("difference"),
                                      "n_used": check.get("n_used"),
                                      "computation_error": check.get("computation_error")})
        if expected is None:
            expected = found
        require(found == expected, "Diagnostic set changed across scheduled runs")
    require(bool(groups), "No source diagnostics")
    for entry in groups.values():
        runs = entry["runs"]
        if any(r["value"] is None or r["status"] == "not_computable" for r in runs):
            entry["summary"] = None
            entry["interpretation"] = "At least one scheduled check is undefined; inspect all runs."
            continue
        values = [r["value"] for r in runs]
        differences = [r["difference"] for r in runs]
        sign = ("above_in_all_draws" if min(differences) > 0 else
                "below_in_all_draws" if max(differences) < 0 else "straddles_or_touches_reported_value")
        entry["summary"] = {
            "n_draws": len(values), "mean": statistics.mean(values),
            "minimum": min(values), "maximum": max(values),
            "generator_seed_draw_sd": statistics.stdev(values),
            "mean_signed_discrepancy": statistics.mean(differences),
            "mean_absolute_discrepancy": statistics.mean(abs(v) for v in differences),
            "discrepancy_pattern": sign,
        }
    directory = bundle / binding["candidate"]
    assumptions = {a["id"]: a["description"] for a in read_json(directory / "model_spec.json")["assumptions"]}
    used_assumptions = {a for g in groups.values() for a in
                        [*g["definition"]["context_assumption_ids"], *g["definition"]["assumption_ids"]]}
    return {"schema_version": 1, "scope": "verified_source_generator_seed_diagnostics_only",
            "parent": binding, "evidence_sha256": sha256(directory / "evidence.json"),
            "source_assumption_definitions": {a: assumptions[a] for a in sorted(used_assumptions)},
            "schedule": receipts, "checks": list(groups.values()),
            "limitations": [
                "Fixed source covariates and program/specification; the program determines what a seed varies.",
                "Residual-only variation requires generator review; ranges/SD are not calibrated confidence intervals.",
                "Unrepresented source/model/transport uncertainty remains unassessed.",
                "Checks sharing populations, outcomes or seeds are dependent; no aggregate success score.",
                "No target outcomes, target analytical conclusions, or automatic acceptance decision.",
            ]}


def compare_source_portfolios(bundle, initial, revised, initial_ids, revised_ids, seeds):
    """Compare same-evidence/recipe candidates using every predeclared paired seed.

    Both portfolios are rebuilt from verified artifacts, not trusted supplied
    summaries. Trade-offs are retained per statistic in its own units.
    """
    before = summarize_source_portfolio(bundle, initial, initial_ids, seeds)
    after = summarize_source_portfolio(bundle, revised, revised_ids, seeds)
    require(before["evidence_sha256"] == after["evidence_sha256"], "Comparison requires unchanged evidence")
    require(before["source_assumption_definitions"] == after["source_assumption_definitions"],
            "Comparison requires unchanged source interpretation assumptions")
    require(before["parent"]["source_replay.json_sha256"] == after["parent"]["source_replay.json_sha256"],
            "Comparison requires unchanged source recipe")
    def keyed(report):
        return {(c["definition"]["context_id"], c["definition"]["check_id"]): c for c in report["checks"]}
    left, right = keyed(before), keyed(after)
    require(left.keys() == right.keys(), "Comparison diagnostic sets differ")
    comparisons = []
    for key, a in left.items():
        b = right[key]
        require(a["definition"] == b["definition"], "Comparison diagnostic definitions differ")
        changes = []
        for x, y in zip(a["runs"], b["runs"]):
            delta = None if x["difference"] is None or y["difference"] is None else abs(y["difference"]) - abs(x["difference"])
            changes.append({"seed": x["seed"], "change_in_absolute_discrepancy": delta})
        valid = [c["change_in_absolute_discrepancy"] for c in changes]
        comparisons.append({"definition": a["definition"], "initial": a["summary"], "revised": b["summary"],
                            "paired_changes": changes,
                            "paired_summary": None if None in valid else {
                                "n_lower": sum(v < 0 for v in valid), "n_higher": sum(v > 0 for v in valid),
                                "n_equal": sum(v == 0 for v in valid),
                                "mean_change_in_absolute_discrepancy": statistics.mean(valid)}})
    return {"schema_version": 1, "scope": "paired_source_diagnostic_tradeoffs_only",
            "initial": before, "revised": after, "comparisons": comparisons,
            "decision": "No automatic winner; source fit is not target analytical validity."}
