"""Render the completed continuation using aggregate reports only.

PREPARED ONLY: do not run until authorized primary and independent evaluation finish.

Usage (from any directory):
    python -B <this file's absolute path>

Inputs are an exact local allowlist: the two COMPLETION.json files, their two
REPORT.json files and INTENT.json files under evcDC/ledger, plus this unit's
CLOSED_INVENTORY.json. No report-embedded reference binding, execution path,
individual table, generator, evaluator or controller is opened/imported.

The frozen primary completion schema has report/intent bindings, not a status
field. Successful primary completion is checked by those bindings and absence
of FAILURE.json. Independent completion and report must both say "matched".

Outputs:
  COMPLETE_AGGREGATE_SUMMARY.json
  figures/target_analysis_complete.png and .svg
  figures/target_analysis_complete_caption.md

Caption specification: all three frozen endpoints; both reused constructions
and all three versions on separate rows, even when identical; three seed points
and min-max range, never an inference interval; reference point and existing
community-clustered nominal 95% interval; unavailable estimates and unsupported
age use remain visible. No adequacy threshold, new endpoint or test is added.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
LEDGER = WORKSPACE / "evcDC/ledger"
PRIMARY = LEDGER / "evaluation"
INDEPENDENT = LEDGER / "independent_evaluation"
CONSTRUCTORS = ("A01", "A02")
VERSIONS = ("initial", "self_review", "source_feedback")
SEEDS = (41911, 41912, 41913)
SOURCE_SEEDS = (41011, 41012, 41013)
ENDPOINTS = ("E1", "E2", "E3")
VARIABLES = ("age", "female", "bmi", "glucose", "hba1c")
MARGINAL_STATS = ("mean", "sd", "q10", "median", "q90")
INPUTS = {
    "primary_completion": PRIMARY / "COMPLETION.json",
    "independent_completion": INDEPENDENT / "COMPLETION.json",
    "primary_report": PRIMARY / "REPORT.json",
    "independent_report": INDEPENDENT / "REPORT.json",
    "primary_intent": PRIMARY / "INTENT.json",
    "independent_intent": INDEPENDENT / "INTENT.json",
    "closed_inventory": HERE / "CLOSED_INVENTORY.json",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def reject_constant(value):
    raise ValueError("Nonfinite JSON constant: " + value)


def load_inputs():
    """Authenticate aggregate snapshots; never follow arbitrary stored paths."""
    blobs = {}

    def snapshot(name):
        path = INPUTS[name]
        require(path.is_file() and not path.is_symlink(), "Missing regular input: " + str(path))
        blobs[name] = path.read_bytes()
        return json.loads(blobs[name].decode("utf-8-sig"), parse_constant=reject_constant)

    done = snapshot("primary_completion")
    independently_done = snapshot("independent_completion")
    require(not (PRIMARY / "FAILURE.json").exists() and
            not (INDEPENDENT / "FAILURE.json").exists(), "Evaluation failure artifact present")
    require(done.get("status", "complete") in {"complete", "matched"},
            "Primary completion is not successful")
    require(independently_done.get("status") == "matched", "Independent completion is not matched")

    # Read only the four known aggregate paths, never binding['path'] itself.
    primary = snapshot("primary_report")
    independent = snapshot("independent_report")
    primary_intent = snapshot("primary_intent")
    independent_intent = snapshot("independent_intent")
    for field, name in (("report", "primary_report"), ("intent", "primary_intent")):
        binding = done[field]
        require(Path(binding["path"]).resolve() == INPUTS[name].resolve(),
                "Primary completion names an unexpected " + field + " path")
        require(binding["sha256"] == sha_bytes(blobs[name]), "Primary " + field + " hash mismatch")
    require(independently_done["report_sha256"] == sha_bytes(blobs["independent_report"]),
            "Independent report hash mismatch")
    require(independent.get("status") == "matched" and independent.get("disagreements") == [],
            "Independent report has not matched without disagreements")
    require(independent["primary_report_sha256"] == sha_bytes(blobs["primary_report"]),
            "Independent report checked different primary bytes")
    require(independent_intent["primary_report_sha256"] == sha_bytes(blobs["primary_report"]),
            "Independent intent checked different primary bytes")
    require(independent_intent["independent_code_sha256"] == independent["independent_code_sha256"],
            "Independent code commitment differs")

    inventory = snapshot("closed_inventory")
    require(inventory.get("kind") == "developmental_pilot_closed_inventory" and
            inventory.get("status") == "closed" and inventory.get("scientific_closed") is True,
            "Scientifically closed inventory required")
    require(primary.get("kind") == "developmental_pilot_paired_branch_evaluation",
            "Unexpected primary report kind")
    require(sha_bytes(canonical(inventory["slots"])) == inventory["inventory_sha256"],
            "Closed slot inventory digest mismatch")
    for field in ("release_sha256", "scientific_freeze_sha256", "inventory_sha256"):
        require(primary[field] == inventory[field], "Report/inventory mismatch: " + field)
    for intent in (primary_intent, independent_intent):
        for field in ("release_sha256", "inventory_sha256"):
            require(intent[field] == inventory[field], "Intent/inventory mismatch: " + field)
    require(set(primary["endpoints"]) == set(independent["summary"]["endpoints"]) == set(ENDPOINTS),
            "All three frozen endpoints are required")
    require(set(primary["reference"]["estimands"]) == set(ENDPOINTS), "Missing reference endpoint")

    slots = inventory["slots"]
    require(len(slots) == 72 and all(s["status"] != "pending" for s in slots),
            "All 72 allocation dispositions must be closed")
    sources = [s for s in slots if s["role"] == "source"]
    targets = [s for s in slots if s["role"] == "target"]
    require(len(sources) == 54 and len(targets) == 18, "Wrong source/target allocation counts")
    require({(s["constructor"], s["version"], s["context_id"], s["seed"]) for s in sources}
            == set(itertools.product(CONSTRUCTORS, VERSIONS, ("J", "B", "M"), SOURCE_SEEDS)),
            "Source schedule differs")
    expected = set(itertools.product(CONSTRUCTORS, VERSIONS, SEEDS))
    require({key(s) for s in targets} == expected and all(s["context_id"] == "T" for s in targets),
            "Target schedule differs")
    require(all(s["n_rows"] == 3000 for s in slots), "Wrong row-count contract")
    inventory_targets = {key(s): s for s in targets}
    for report_slots in (primary["slots"], independent["recomputed_slots"]):
        require(len(report_slots) == 18 and {key(s) for s in report_slots} == expected,
                "Aggregate report omits a target disposition")
        for row in report_slots:
            require(all(row.get(field) == value for field, value in inventory_targets[key(row)].items()),
                    "Aggregate target identity/disposition differs from inventory")
    require(primary["independent_constructions"] == independent["summary"]["independent_constructions"] == 2,
            "Unexpected scientific-construction count")
    bindings = {name: {"path": str(INPUTS[name]), "sha256": sha_bytes(data)}
                for name, data in blobs.items()}
    return primary, independent, inventory, bindings


def key(slot):
    return slot["constructor"], slot["version"], slot["seed"]


def identity(slot):
    return {k: slot.get(k) for k in
            ("constructor", "version", "role", "context_id", "run_id", "seed", "status")}


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def diagnostic_value(diagnostics, variable, statistic):
    if not isinstance(diagnostics, dict):
        return None
    if variable == "glucose__hba1c":
        return diagnostics.get("joint", {}).get(statistic)
    return diagnostics.get("marginal", {}).get(variable, {}).get(statistic)


def diagnostic_ranges(primary):
    """Extrema across existing seed-level diagnostics, not row-level estimates."""
    definitions = [(v, s) for v in VARIABLES for s in MARGINAL_STATS]
    definitions += [("glucose__hba1c", "pearson"), ("glucose__hba1c", "spearman")]
    require(len(definitions) == 27, "Frozen diagnostic count changed")
    result = {}
    reference_diagnostics = primary["reference"].get("diagnostics")
    for constructor, version in itertools.product(CONSTRUCTORS, VERSIONS):
        subset = sorted((s for s in primary["slots"] if key(s)[:2] == (constructor, version)),
                        key=lambda s: s["seed"])
        require(len(subset) == 3, "Diagnostic summaries require all planned seed records")
        records = []
        for variable, statistic in definitions:
            observations = []
            for slot in subset:
                analysis = slot.get("analysis") or {}
                value = diagnostic_value(analysis.get("diagnostics"), variable, statistic)
                observations.append({"seed": slot["seed"], "value": value,
                                     "execution_status": slot["status"],
                                     "analysis_status": analysis.get("status"),
                                     "analysis_error": slot.get("analysis_error"),
                                     "available": finite(value)})
            values = [x["value"] for x in observations if x["available"]]
            complete = len(values) == 3 and all(s["status"] == "success" for s in subset)
            reference = diagnostic_value(reference_diagnostics, variable, statistic)
            records.append({"id": variable + "." + statistic, "variable": variable,
                            "statistic": statistic, "reference_value": reference,
                            "reference_status": "available" if finite(reference) else "unavailable",
                            "planned_seed_count": 3, "available_seed_count": len(values),
                            "complete": complete, "seed_values": observations,
                            "generated_range": [min(values), max(values)] if values else None,
                            "range_scope": "three_fixed_seeds_not_CI" if complete else
                                           "available_subset_only_incomplete_not_CI"})
        result[constructor + "/" + version] = records
    return result


def hash_accounting(inventory):
    result = {}
    for role in ("source", "target"):
        slots = [s for s in inventory["slots"] if s["role"] == role]
        groups = defaultdict(list)
        for slot in slots:
            if slot.get("output_sha256") is not None:
                groups[slot["output_sha256"]].append(identity(slot))
        successful = [s for s in slots if s["status"] == "success"]
        result[role] = {
            "planned_allocation_count": len(slots),
            "execution_status_counts": dict(Counter(s["status"] for s in slots)),
            "successful_execution_count": len(successful),
            "allocations_with_retained_output_hash": sum(len(g) for g in groups.values()),
            "unique_retained_output_hash_count": len(groups),
            "unique_successful_output_hash_count": len({s["output_sha256"] for s in successful
                                                         if s.get("output_sha256") is not None}),
            "unique_execution_receipt_hash_count": len({s["execution_sha256"] for s in slots
                                                         if s.get("execution_sha256") is not None}),
            "output_hash_groups": [{"sha256": h, "allocation_count": len(g), "allocations": g}
                                   for h, g in sorted(groups.items())],
            "interpretation": "Output-byte identities from the authenticated inventory; not independent laws or evidence.",
        }
    return result


def make_summary(primary, independent, inventory, bindings):
    endpoint_rows = []
    failures = [{"scope": "execution", **s} for s in inventory["slots"] if s["status"] != "success"]
    generated = []
    for slot in primary["slots"]:
        analysis = slot.get("analysis") or {}
        if slot.get("analysis_error") is not None or (slot["status"] == "success" and not analysis):
            failures.append({"scope": "analysis", **identity(slot), "analysis_error": slot.get("analysis_error")})
        for endpoint in ENDPOINTS:
            estimate = analysis.get("estimands", {}).get(endpoint)
            comparison = (slot.get("comparison") or {}).get(endpoint)
            endpoint_rows.append({**identity(slot), "endpoint": endpoint,
                                  "estimate": estimate, "comparison": comparison,
                                  "analysis_support": slot["analysis_support"][endpoint],
                                  "analysis_error": slot.get("analysis_error")})
            if not estimate or estimate.get("status") != "computed":
                failures.append({"scope": "endpoint", **identity(slot), "endpoint": endpoint,
                                 "estimate": estimate, "analysis_error": slot.get("analysis_error")})
        generated.append({**identity(slot),
                          "generated_only_diagnostics": slot.get("generated_only_diagnostics"),
                          "analysis_quality": analysis.get("quality"),
                          "analysis_gate_reason": analysis.get("gate_reason"),
                          "estimand_records_including_design_diagnostics": analysis.get("estimands"),
                          "analysis_error": slot.get("analysis_error")})
    require(len(endpoint_rows) == 54, "All endpoint/version/seed records are required")
    return {
        "schema_version": 1, "kind": "completed_continuation_aggregate_rendering",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_bindings": bindings,
        "script_sha256": sha_bytes(Path(__file__).read_bytes()),
        "release_sha256": inventory["release_sha256"],
        "scientific_freeze_sha256": inventory["scientific_freeze_sha256"],
        "inventory_sha256": inventory["inventory_sha256"],
        "scientific_constructions": {"reused_initial_scientific_constructions": 2,
                                     "new_initial_scientific_constructors": 0,
                                     "fresh_branch_authors": 4,
                                     "committed_branch_decisions": "all_four_retain",
                                     "basis": "Frozen continuation method and decisions; execution slots are not independent laws."},
        "allocation_hash_accounting": hash_accounting(inventory),
        "all_closed_allocation_dispositions": inventory["slots"],
        "endpoint_version_seed_results": endpoint_rows,
        "endpoint_summaries_and_changes": primary["endpoints"],
        "reference_aggregate_as_reported": primary["reference"],
        "reference_comparable_diagnostics_27": diagnostic_ranges(primary),
        "generated_only_and_design_diagnostics_unchanged": generated,
        "target_slot_records_unchanged": primary["slots"],
        "all_failure_statuses": failures,
        "independent_numeric_verification": {
            "status": independent["status"], "disagreements": independent["disagreements"],
            "primary_report_sha256": independent["primary_report_sha256"],
            "independent_code_sha256": independent["independent_code_sha256"],
            "numerical_tolerance": independent["numerical_tolerance"],
            "method": independent["method"],
            "reference_uncertainty": independent["reference_uncertainty"],
            "recomputed_target_slot_count": len(independent["recomputed_slots"]),
            "summary_unchanged": independent["summary"],
        },
        "primary_historical_independent_recomputation_field": primary.get("independent_recomputation"),
        "verification_status_note": "The primary report's historical pending field is retained, not rewritten; current matched status comes from the bound independent completion/report.",
        "scientific_annotations_unchanged": primary["scientific_annotations"],
        "overall_success_rule": primary["overall_success_rule"],
        "equivalence_margin": primary["equivalence_margin"],
        "limitations": primary["limitations"] + [
            "Postprocessing reads aggregate reports and inventory only; it does not revalidate individual tables.",
            "Diagnostic extrema are descriptive across available fixed seeds; incomplete records remain visible.",
            "Repeated or byte-identical outputs do not add independent constructions or clinical evidence.",
        ],
    }


CAPTION = """**Figure. Frozen target analyses for both reused constructions and all versions.** Each row retains one constructor/version, including retained versions whose estimates coincide. Symbols show the three prespecified target-seed point estimates; horizontal lines span available seed minima and maxima. These ranges describe conditional simulation variation and are **not confidence intervals**. Incomplete rows are labelled by their available-seed count; unavailable estimates are shown explicitly. The dashed vertical line marks the existing reference point and the grey band its available nominal 95% community-clustered interval. The interval describes reference-sample uncertainty and is not an adequacy or equivalence region. All three prespecified analyses are shown, including the age analysis with its declared unassessed evidence support. Separate rows and repeated outputs do not add independent scientific laws. CHNS remains a researcher-exposed developmental reference. Rendering uses only completed aggregate reports and the closed inventory, after matched independent numerical recomputation; no new endpoint, statistical test or row-level analysis is introduced.
"""


def draw_figure(primary):
    # Deferred until after the completion/hash gates; imports no scientific engine.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import MaxNLocator

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titlesize": 11.5, "axes.labelsize": 10,
                         "axes.edgecolor": "#A9B0B7", "text.color": "#202B33",
                         "axes.labelcolor": "#2B343B", "xtick.color": "#4B565E",
                         "ytick.color": "#2B343B", "svg.fonttype": "none"})
    colors = {"A01": "#187D83", "A02": "#B45F26"}
    titles = {"E1": "BMI coefficient", "E2": "Glucose coefficient", "E3": "Age coefficient"}
    units = {"E1": "HbA1c (%) per kg/m²", "E2": "HbA1c (%) per mmol/L glucose",
             "E3": "HbA1c (%) per year"}
    names = {"initial": "Initial", "self_review": "Self-review", "source_feedback": "Source feedback"}
    rows = [(c, v) for c in CONSTRUCTORS for v in VERSIONS]
    y_positions = [6.0, 5.0, 4.0, 2.5, 1.5, 0.5]
    markers = ("o", "s", "D")
    offsets = (-0.10, 0.0, 0.10)
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 6.5), sharey=True)
    fig.subplots_adjust(left=0.145, right=0.985, bottom=0.24, top=0.77, wspace=0.25)
    fig.text(0.145, 0.955, "Frozen target analyses: all versions retained", fontsize=16, weight="bold")
    fig.text(0.145, 0.907, "Two reused scientific constructions · three fixed target seeds · 3,000 rows per draw",
             fontsize=10.5, color="#4B565E")
    for ax, endpoint in zip(axes, ENDPOINTS):
        reference = primary["endpoints"][endpoint]["reference"]
        ci = reference.get("interval") or {}
        if ci.get("status") == "available" and finite(ci.get("lower")) and finite(ci.get("upper")):
            ax.axvspan(ci["lower"], ci["upper"], color="#CBD2D8", alpha=0.48, zorder=0)
        if reference.get("status") == "computed" and finite(reference.get("coefficient")):
            ax.axvline(reference["coefficient"], color="#66727B", linestyle=(0, (4, 3)), lw=1.3, zorder=1)
        else:
            ax.text(0.02, 0.03, "Reference unavailable", transform=ax.transAxes, fontsize=8.5)
        for (constructor, version), y in zip(rows, y_positions):
            record = primary["endpoints"][endpoint]["constructors"][constructor]["versions"][version]
            estimates = {x["seed"]: x["coefficient"] for x in record["seed_estimates"]}
            require(set(estimates) == set(SEEDS), "Figure must retain the planned seeds")
            values = [estimates[s] for s in SEEDS if finite(estimates[s])]
            if values:
                ax.plot([min(values), max(values)], [y, y], color=colors[constructor], lw=1.8,
                        linestyle="-" if len(values) == 3 else "--", zorder=2)
                for seed, marker, offset in zip(SEEDS, markers, offsets):
                    if finite(estimates[seed]):
                        ax.scatter([estimates[seed]], [y + offset], s=27, marker=marker,
                                   color=colors[constructor], linewidths=0.5,
                                   edgecolors="white", zorder=3)
            if len(values) < 3:
                ax.text(0.98, y, "unavailable" if not values else f"{len(values)}/3 seeds",
                        transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=8,
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85})
        support_lines = []
        for constructor in CONSTRUCTORS:
            assessments = {primary["endpoints"][endpoint]["constructors"][constructor]["versions"][v]
                           ["analysis_support"].get("assessment") or "unavailable" for v in VERSIONS}
            support_lines.append(constructor + ": " + "/".join(sorted(assessments)))
        ax.set_title(titles[endpoint], loc="left", weight="semibold", pad=44)
        ax.text(0, 1.04, "Declared support\n" + "; ".join(support_lines),
                transform=ax.transAxes, fontsize=8.5, color="#4B565E", va="bottom")
        ax.set_xlabel(units[endpoint], labelpad=10)
        ax.set_yticks(y_positions, [c + " · " + names[v] for c, v in rows])
        ax.set_ylim(-0.2, 6.6)
        ax.tick_params(axis="y", length=0, pad=8)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.ticklabel_format(axis="x", style="plain", useOffset=False)
        ax.margins(x=0.15)
        ax.set_axisbelow(True)
        ax.grid(axis="x", color="#E8ECEF", lw=0.7)
        ax.axhline(3.25, color="#E3E7EB", lw=0.8)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
    handles = [Line2D([], [], marker=m, color="#33434D", linestyle="none", markersize=5,
                      label="Seed " + str(s)) for m, s in zip(markers, SEEDS)]
    handles += [Line2D([], [], color="#33434D", lw=1.8, label="Seed min–max (not CI)"),
                Line2D([], [], color="#66727B", linestyle=(0, (4, 3)), lw=1.3, label="Reference point"),
                Patch(facecolor="#CBD2D8", alpha=0.48, label="Reference clustered 95% CI")]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.138, 0.075),
               frameon=False, ncol=3, fontsize=9, columnspacing=2)
    fig.text(0.145, 0.035, "Separate version rows preserve coincident estimates; paired repeats add no distinct laws. Age use remains unassessed.",
             fontsize=9, color="#4B565E")
    destination = HERE / "figures"
    destination.mkdir(exist_ok=True)
    png = destination / "target_analysis_complete.png"
    svg = destination / "target_analysis_complete.svg"
    fig.savefig(png, dpi=240, facecolor="white",
                metadata={"Description": "Completed aggregate target figure; seed ranges are not CIs."})
    fig.savefig(svg, facecolor="white",
                metadata={"Description": "Completed aggregate target figure; seed ranges are not CIs.",
                          "Creator": "matplotlib"})
    plt.close(fig)
    caption = destination / "target_analysis_complete_caption.md"
    caption.write_text(CAPTION, encoding="utf-8")
    return {name: {"path": str(path), "sha256": sha_bytes(path.read_bytes())}
            for name, path in (("png", png), ("svg", svg), ("caption", caption))}


def main():
    primary, independent, inventory, bindings = load_inputs()
    summary = make_summary(primary, independent, inventory, bindings)
    summary["figure_artifacts"] = draw_figure(primary)
    destination = HERE / "COMPLETE_AGGREGATE_SUMMARY.json"
    destination.write_text(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({"summary": str(destination), "independent_status": independent["status"],
                      "target_slots": len(primary["slots"]),
                      "endpoint_version_seed_results": len(summary["endpoint_version_seed_results"]),
                      "diagnostics_per_constructor_version": 27,
                      "figure_artifacts": summary["figure_artifacts"],
                      "individual_tables_read": 0, "new_scientific_tests": 0}))


if __name__ == "__main__":
    main()
