"""Offline v0.7 aggregate verification, numeric tables and scientific plot rendering.

This entry point never imports a generator, evaluator or cohort_harness. Inputs
are an explicit hash-pinned public allowlist. Legacy plotting code runs only in
temporary staging; neither the public checkout nor frozen inputs are rewritten.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import platform
import runpy
import shutil
import statistics
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PROJECT_REL = Path("biomedical_research/virtual_cohort_system")
UTILITY = Path("manuscript/utility_package_2026-11-03")
STORY = Path("manuscript/story_package_2026-11-03")
HRS = Path("reports/hrs_public_example_2026-11-03")
MAIN = Path("reports/main_study_freeze_2026-11-03")
HISTORY = Path("reports/information_revision_ablation_2026-11-03")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pointer(document, expression):
    value = document
    for segment in expression.strip("/").split("/"):
        key = segment.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def equal_number(actual, expected, label):
    require(math.isfinite(float(actual)) and math.isclose(float(actual), float(expected),
            rel_tol=1e-10, abs_tol=1e-12), f"Numeric mismatch: {label}: {actual} != {expected}")


def locate_source(repo_root):
    root = repo_root.resolve()
    project = root / PROJECT_REL if (root / PROJECT_REL).is_dir() else root
    require((project / "reports").is_dir() and (project / "manuscript").is_dir(),
            "--repo-root must name the public repository or its virtual_cohort_system project")
    protected = root
    for parent in (project, *project.parents):
        if (parent / ".git").exists():
            protected = parent
            break
    return project, protected


def validate_output(output, protected):
    require(not output.is_relative_to(protected) and not protected.is_relative_to(output),
            "Output must be separate from the source checkout, not inside it or an ancestor")
    require(not output.exists() or (output.is_dir() and not any(output.iterdir())),
            "Output must be absent or an empty directory; existing results are never overwritten")


def verify_inputs(project, lock):
    records = []
    for item in lock["files"]:
        relative = Path(item["path"])
        require(not relative.is_absolute() and ".." not in relative.parts, "Invalid allowlist path")
        path = project / relative
        require(path.resolve().is_relative_to(project), f"Input escapes public project: {relative}")
        require(path.is_file(), f"Missing public input: {relative.as_posix()}")
        actual = sha(path)
        require(actual == item["sha256"] and path.stat().st_size == item["bytes"],
                f"Public input hash mismatch: {relative.as_posix()} (observed {actual})")
        records.append(dict(item))
    return records


def original_bytes(project, lock):
    """Validate the exact two historical export transformations without writes."""
    restored = {}
    public_manifest = load(project / HISTORY / "PUBLIC_PACKAGE_MANIFEST.json")
    for item in lock["crlf_exports"]:
        exported = (project / item["path"]).read_bytes()
        require(b"\r" not in exported, "Pinned historical export must have LF-only bytes")
        original = exported.replace(b"\n", b"\r\n")
        require(hashlib.sha256(original).hexdigest() == item["original_sha256"],
                f"Original-byte reconstruction failed: {item['path']}")
        require(json.loads(exported) == json.loads(original), "Line-ending conversion changed JSON")
        matching = [r for r in public_manifest["files"] if r["export"] == Path(item["path"]).name]
        require(len(matching) == 1 and matching[0]["original_sha256"] == item["original_sha256"]
                and matching[0]["original_bytes"] == len(original), "Original-byte manifest mismatch")
        restored[item["path"]] = original
    return restored


def verify_aggregates(project, lock):
    payload = load(project / UTILITY / "AGGREGATE_SOURCE.json")
    utility_manifest = load(project / UTILITY / "NUMERIC_MANIFEST.json")
    main = load(project / MAIN / "final_evaluation/RESULTS.json")
    audit = load(project / MAIN / "independent_audit/RESULTS.json")
    historical = load(project / HISTORY / "COMPLETE_RESULTS.json")
    historical_audit = load(project / HISTORY / "INDEPENDENT_RECOMPUTE.json")
    hrs = load(project / HRS / "summary/AGGREGATE_RESULTS.json")
    hrs_audit = load(project / HRS / "FINAL_RESULT_REVIEW.json")
    hrs_manifest = load(project / HRS / "figures/FIGURE_MANIFEST.json")
    story_manifest = load(project / STORY / "DISPLAY_PROVENANCE.json")
    for extension in ("drawio", "drawio.svg", "drawio.png"):
        relative = f"figures/figure1-evidence-to-analysis.{extension}"
        require(sha(project / STORY / relative) == story_manifest["outputs"][relative], "Method schematic provenance binding failed")
    restored = original_bytes(project, lock)
    expected_original = {key: hashlib.sha256(value).hexdigest() for key, value in restored.items()}
    require(audit["status"] == "matched" and audit["result_sha256"] == sha(project / MAIN / "final_evaluation/RESULTS.json"), "Main audit binding failed")
    require(historical_audit["status"] == "pass" and historical_audit["report_sha256"] == expected_original[(HISTORY / "COMPLETE_RESULTS.json").as_posix()], "Historical audit binding failed")
    for item in utility_manifest["sources"].values():
        relative = item["path"].replace("work/", "reports/", 1)
        require(item["sha256"] == expected_original.get(relative, sha(project / relative)), f"Utility source binding failed: {relative}")
    require(sha(project / UTILITY / "AGGREGATE_SOURCE.json") == utility_manifest["outputs"]["AGGREGATE_SOURCE.json"]["sha256"], "Retained plotting payload binding failed")
    counts = {}
    for key, document, seeds, expected in [
        ("main_experiment", main, [5101, 5102, 5103], (6, 216, 72)),
        ("historical_information_experiment", historical, [4101, 4102, 4103], (5, 90, 30)),
    ]:
        panels = payload[key]["panels"]
        seed_count = summary_count = 0
        for panel in panels:
            source_ref = pointer(document, panel["reference_pointer"])
            if key == "main_experiment":
                require(panel["reference"] == source_ref, "Main reference and interval mismatch")
            else:
                require(panel["reference"]["value"] == source_ref, "Historical reference mismatch")
                if "interval_pointer" in panel:
                    require(panel["reference"]["interval"] == pointer(document, panel["interval_pointer"]), "Historical interval mismatch")
                else:
                    require(panel["reference"]["interval"] is None, "Unavailable reference interval introduced")
            for series in panel["series"]:
                require([r["seed"] for r in series["seeds"]] == seeds, "Unexpected seed identities")
                values = [r["value"] for r in series["seeds"]]
                for point in series["seeds"]:
                    require(point["value"] == pointer(document, point["pointer"]), "Seed pointer mismatch")
                equal_number(series["mean"], statistics.mean(values), "constructor mean")
                require(series["range"] == [min(values), max(values)], "Seed range mismatch")
                summary = pointer(document, series["summary_pointer"])
                require(series["mean"] == summary["mean_effect" if key == "main_experiment" else "mean"], "Summary mean pointer mismatch")
                require(series["range"] == summary["seed_effect_range" if key == "main_experiment" else "range"], "Summary range pointer mismatch")
                seed_count += len(values)
                summary_count += 1
        require((len(panels), seed_count, summary_count) == expected, f"Unexpected display counts: {key}")
        counts[key] = {"panels": len(panels), "seed_values": seed_count, "constructor_means": summary_count}
    require(main["planned_constructions"] == 24 and main["scheduled_final_slots"] == main["unique_successful_table_contents"] == main["complete_analysis_slots"] == 72, "Main experiment counts changed")
    require(historical["attempts"] == 42 and historical["distinct_table_hashes"] == 24, "Historical attempt counts changed")
    require(hrs["counts"]["valid_comparison_tables"] == 6 and hrs["counts"]["total_physical_generations"] == 9 and hrs["counts"]["invalid_initial_comparator_tables"] == 3, "HRS comparison counts changed")
    require(hrs_audit["status"] == "pass", "HRS audit did not pass")
    bindings = {item["path"].replace("\\", "/"): item["sha256"] for item in hrs_audit["bindings"]}
    for name in ("AGGREGATE_RESULTS.json", "fixed_effects_all_seeds.csv", "fixed_effects_summary.csv", "distributions_summary.csv"):
        relative = "summary/" + name
        require(bindings[relative] == sha(project / HRS / relative), f"HRS audit binding failed: {name}")
    require(hrs_manifest["input"]["sha256"] == sha(project / HRS / hrs_manifest["input"]["path"]), "HRS plotting-input binding failed")
    rows = read_csv(project / HRS / "summary/fixed_effects_all_seeds.csv")
    summaries = read_csv(project / HRS / "summary/fixed_effects_summary.csv")
    distributions = read_csv(project / HRS / "summary/distributions_summary.csv")
    require(len(rows) == 96 and len({r["term"] for r in rows}) == 16 and len(summaries) == 32 and len(distributions) == 54, "HRS aggregate row counts changed")
    require({r["arm"] for r in rows} == {"native", "agent"} and {r["seed"] for r in rows} == {"6101", "6102", "6103"}, "HRS identities changed")
    require(len({(r["arm"], r["term"], r["seed"]) for r in rows}) == 96, "Duplicate HRS coefficient records")
    for summary in summaries:
        group = [r for r in rows if r["arm"] == summary["arm"] and r["term"] == summary["term"]]
        values = [float(r["estimate"]) for r in group]
        require(len(values) == 3 and summary["available_seeds"] == "3", "Incomplete HRS summary")
        for name, value in [("mean_estimate", statistics.mean(values)), ("min_estimate", min(values)), ("max_estimate", max(values))]:
            equal_number(summary[name], value, name)
    for row in rows:
        estimate, se = float(row["estimate"]), float(row["se"])
        require(se > 0, "Invalid exported standard error")
        equal_number(row["wald_lower"], estimate - 1.959963984540054 * se, "HRS Wald lower")
        equal_number(row["wald_upper"], estimate + 1.959963984540054 * se, "HRS Wald upper")
    counts["hrs"] = {"all_fixed_effect_seed_values": 96, "fixed_effect_means": 32, "focal_seed_values": 12, "distribution_summary_rows": 54}
    return payload, main, historical, hrs, counts, restored


def manuscript_tables(text):
    tables = {}
    for number in range(1, 5):
        section = text.split(f"**Table {number}.", 1)[1]
        lines = section.splitlines()
        first = next(i for i, line in enumerate(lines) if line.startswith("|"))
        block = []
        for line in lines[first:]:
            if not line.startswith("|"):
                break
            block.append([cell.strip() for cell in line.strip("|").split("|")])
        tables[number] = block
    return tables


def make_tables(project, result, payload, main, historical, hrs):
    folder = result / "tables"
    folder.mkdir()
    published = manuscript_tables((project / "manuscript/DRAFT_v0_7.md").read_text(encoding="utf-8"))
    output_tables = {1: published[1]}
    table2, table3, table4, points = [], [], [], []
    for panel in payload["main_experiment"]["panels"]:
        reference = panel["reference"]
        table2.append({"case": panel["case"], "endpoint": panel["endpoint"], "predictor": panel["predictor"], "adjustment": panel["adjustment"], "predictor_increment": panel["display_unit"], "reference": reference["value"], "lower": reference["interval"]["lower"], "upper": reference["interval"]["upper"], "source_pointer": panel["reference_pointer"]})
    for contrast in main["agent_information_contrasts"]:
        case, endpoint = contrast["case_id"], contrast["endpoint"]
        panel = next(p for p in payload["main_experiment"]["panels"] if p["case"] == case and p["endpoint"] == endpoint)
        calculated = {}
        for arm in ("E0", "E1"):
            authors = [s for s in panel["series"] if s["kind"] == "agent" and s["condition"] == arm]
            require(len(authors) == 5, "Table 3 requires five Agent authors per condition")
            calculated[arm] = statistics.mean(statistics.mean(abs(p["value"] - panel["reference"]["value"]) for p in s["seeds"]) for s in authors)
            equal_number(calculated[arm], contrast["arms"][arm]["mean_constructor_mean_absolute_discrepancy"], "Table 3 discrepancy")
        equal_number(calculated["E1"] - calculated["E0"], contrast["E1_minus_E0_mean_absolute_discrepancy"], "Table 3 contrast")
        table3.append({"case": case, "endpoint": endpoint, "unit": contrast["unit"], "E0_MAD": contrast["arms"]["E0"]["mean_constructor_mean_absolute_discrepancy"], "E1_MAD": contrast["arms"]["E1"]["mean_constructor_mean_absolute_discrepancy"], "E1_minus_E0": contrast["E1_minus_E0_mean_absolute_discrepancy"]})
    for panel in payload["historical_information_experiment"]["panels"]:
        row = {"endpoint": panel["endpoint"], "reference": panel["reference"]["value"]}
        for arm in ("L", "R"):
            means = [s["mean"] for s in panel["series"] if s["condition"] == arm]
            require(len(means) == 3, "Table 4 requires three authors per condition")
            row[arm + "_min_constructor_mean"] = min(means)
            row[arm + "_max_constructor_mean"] = max(means)
        table4.append(row)
    for key in ("main_experiment", "historical_information_experiment"):
        for panel in payload[key]["panels"]:
            for series in panel["series"]:
                for point in series["seeds"]:
                    points.append({"experiment": key, "panel": panel["panel"], "case": panel.get("case", "CHNS2009"), "endpoint": panel["endpoint"], "constructor": series["constructor"], "condition": series["condition"], "seed": point["seed"], "value": point["value"], "source_pointer": point["pointer"]})
    for number, data, name in [(2, table2, "table2_sample_references"), (3, table3, "table3_information_contrasts"), (4, table4, "table4_summary_assisted")]:
        write_csv(folder / (name + ".csv"), data)
        require(len(data) == len(published[number]) - 2, f"Table {number} row count mismatch")
        rebuilt = published[number][:2]
        for original, row in zip(published[number][2:], data):
            if number == 2:
                values = [f"{row['reference']:.6f}", f"{row['lower']:.6f}–{row['upper']:.6f}"]
                rebuilt_row = original[:4] + values
            elif number == 3:
                values = [f"{row['E0_MAD']:.6f}", f"{row['E1_MAD']:.6f}", f"{row['E1_minus_E0']:+.6f}".replace("-", "−")]
                rebuilt_row = original[:1] + values
            else:
                values = [f"{row['reference']:.6f}", *[f"{row[arm + '_min_constructor_mean']:.6f}–{row[arm + '_max_constructor_mean']:.6f}" for arm in ("L", "R")]]
                rebuilt_row = original[:1] + values
            require(rebuilt_row == original, f"Reconstructed Table {number} differs from published rounded cells")
            rebuilt.append(rebuilt_row)
        output_tables[number] = rebuilt
    write_csv(folder / "cross_sectional_plotted_values.csv", points)
    scope = [
        {"experiment": "external_evidence", "constructions": main["planned_constructions"], "valid_final_tables": main["scheduled_final_slots"], "rows_or_subjects_per_table": 3000, "visits_per_subject": 1},
        {"experiment": "summary_assisted", "constructions": payload["historical_information_experiment"]["constructors"], "valid_final_tables": payload["historical_information_experiment"]["final_tables"], "rows_or_subjects_per_table": 3000, "visits_per_subject": 1},
        {"experiment": "hrs_public_model", "constructions": 2, "valid_final_tables": hrs["counts"]["valid_comparison_tables"], "rows_or_subjects_per_table": hrs["counts"]["subjects_per_table"], "visits_per_subject": 4},
    ]
    write_csv(folder / "table1_numeric_scope.csv", scope)
    for source, target in [("fixed_effects_all_seeds.csv", "hrs_all_fixed_effects.csv"), ("fixed_effects_summary.csv", "hrs_fixed_effect_summary.csv"), ("distributions_summary.csv", "hrs_distribution_summary.csv")]:
        shutil.copyfile(project / HRS / "summary" / source, folder / target)
    focal = [r for r in read_csv(project / HRS / "summary/fixed_effects_all_seeds.csv") if r["term"] in ("age60:hba1c_U65", "age60:hba1c_O65")]
    require(len(focal) == 12, "Unexpected focal HRS selection")
    write_csv(folder / "hrs_focal_plotted_values.csv", focal)
    lines = ["# Manuscript v0.7 tables", "", "Tables 2–4: numeric cells rebuilt and checked against the frozen manuscript. Editorial labels and Table 1 prose are retained verbatim. Full-precision numeric CSVs accompany this file.", ""]
    for number, table in output_tables.items():
        lines += [f"## Table {number}", ""]
        lines += ["| " + " | ".join(row) + " |" for row in table]
        lines.append("")
    (folder / "MANUSCRIPT_TABLES.md").write_text("\n".join(lines), encoding="utf-8")
    return {"manuscript_numeric_rows": {"Table 2": 6, "Table 3": 6, "Table 4": 5}, "rounded_numeric_cells_matched": 45, "cross_sectional_plotted_values": len(points)}


def render(stage, result, payload):
    os.environ["MPLCONFIGDIR"] = str(stage / "matplotlib_config")
    os.environ["SOURCE_DATE_EPOCH"] = "1793664000"
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ft2font
    import numpy
    import PIL
    require(not sys.flags.optimize, "Rendering requires Python without -O: legacy plotting assertions must execute")
    utility = runpy.run_path(str(stage / UTILITY / "build_utility_figures.py"), run_name="v07_utility_renderer")
    rebuilt = utility["build_payload"]()
    require({k: v for k, v in rebuilt.items() if k != "sources"} == {k: v for k, v in payload.items() if k != "sources"}, "Rebuilt plotting payload differs from frozen aggregate payload")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.titlesize": 8,
                         "axes.labelsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7,
                         "svg.fonttype": "none", "svg.hashsalt": "evidence-guided-utility-2026-11-03"})
    utility["plot_main"](rebuilt)
    utility["plot_history"](rebuilt)
    plt.rcdefaults()
    plt.rcParams["svg.hashsalt"] = "manuscript-v07-hrs-reproduction"
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(str(stage / HRS / "plot_results.py"), run_name="__main__")
    mappings = [(UTILITY, "figure1_main_scientific_utility", "fig2_external_evidence"),
                (UTILITY, "figure2_chns_information_conditions", "fig3_summary_assisted"),
                (HRS, "focal_longitudinal_relationships", "fig4_longitudinal"),
                (HRS, "all_16_fixed_effects", "figS1_longitudinal_all_effects")]
    for directory, origin, target in mappings:
        for extension in ("png", "svg"):
            shutil.copyfile(stage / directory / "figures" / f"{origin}.{extension}", result / "figures" / f"{target}.{extension}")
    return {"matplotlib": matplotlib.__version__, "numpy": numpy.__version__, "Pillow": PIL.__version__, "FreeType": matplotlib.ft2font.__freetype_version__, "backend": matplotlib.get_backend(), "svg_timestamp_epoch": os.environ["SOURCE_DATE_EPOCH"], "freshly_rendered_files": 8, "reconstructed_plot_payload_matches_frozen_values": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=HERE.parent, help="Public repository root or virtual_cohort_system project")
    parser.add_argument("--output", required=True, type=Path, help="New/empty output directory outside the source checkout")
    parser.add_argument("--verify-only", action="store_true", help="Standard-library verification and numeric tables; do not render or package figures")
    args = parser.parse_args(argv)
    require(not sys.flags.optimize, "Run without -O/PYTHONOPTIMIZE so legacy renderer assertions remain active")
    project, protected = locate_source(args.repo_root)
    output = args.output.resolve()
    validate_output(output, protected)
    lock = load(HERE / "public_inputs_v07.json")
    records = verify_inputs(project, lock)
    payload, main_data, historical, hrs, counts, restored = verify_aggregates(project, lock)
    if not args.verify_only:
        require(importlib.util.find_spec("matplotlib") is not None,
                "Matplotlib is required for rendering (tested: 3.10.9); --verify-only needs only Python's standard library. Nothing was installed.")
    with tempfile.TemporaryDirectory(prefix="v07_public_reproduction_") as temporary:
        base = Path(temporary)
        stage, result = base / "project", base / "result"
        result.mkdir()
        for record in records:
            destination = stage / record["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(restored.get(record["path"], (project / record["path"]).read_bytes()))
        tables = make_tables(stage, result, payload, main_data, historical, hrs)
        environment = {"python": platform.python_version(), "platform": platform.platform()}
        if not args.verify_only:
            (result / "figures").mkdir()
            for extension in ("drawio", "drawio.svg", "drawio.png"):
                shutil.copyfile(stage / STORY / "figures" / f"figure1-evidence-to-analysis.{extension}", result / "figures" / f"fig1_method.{extension.split('.')[-1]}")
            shutil.copyfile(stage / "manuscript/integrated_figures_v07_2026-11-03/CAPTIONS.md", result / "CAPTIONS.md")
            environment.update(render(stage, result, payload))
        write_json(result / "cross_sectional_aggregate_source.json", payload)
        verify_inputs(project, lock)
        receipt = {"schema": "manuscript_v07_public_reproduction_v1", "status": "pass",
                   "mode": "aggregate_verification_and_tables" if args.verify_only else "aggregate_tables_and_plot_rendering",
                   "scope": "Retained public aggregate statistics only; display reproduction, not clinical or generator reproduction.",
                   "reference_export_commit": lock["reference_export_commit"],
                   "entrypoint_sha256": sha(Path(__file__)), "input_lock_sha256": sha(HERE / "public_inputs_v07.json"),
                   "inputs": records, "public_input_hashes_unchanged_after_run": True,
                   "temporary_only_byte_restorations": lock["crlf_exports"], "display_counts": counts,
                   "table_verification": tables, "environment": environment,
                   "operations": {"new_generations": 0, "new_scientific_fits": 0, "new_generator_or_target_evaluations": 0,
                                  "patient_rows_read": 0, "generated_rows_read": 0, "network_calls": 0,
                                  "figure1": "not packaged" if args.verify_only else "Verified unchanged schematic asset copy; not redrawn",
                                  "figures2_3_4_S1": "not rendered" if args.verify_only else "Freshly rendered from aggregate statistics with existing plotting algorithms",
                                  "table1_prose": "Copied from frozen manuscript; numeric scope exported separately",
                                  "tables2_3_4": "Rebuilt numeric cells; full-precision CSV and manuscript-rounded cell checks",
                                  "hrs_summary_csvs": "Verified unchanged aggregate copies, plus exact 12-row focal selection"},
                   "limitations": ["No clinical validation, original-data analysis, generator execution or independent replication is performed.",
                                   "Historical analyses and HRS source-model reconstruction remain distinct from the external-evidence study; no pooled ranking is computed.",
                                   "Original image bytes may differ across rendering libraries, fonts and platforms. Numeric fidelity is checked separately from image hashes.",
                                   "This command does not compile the Word/PDF manuscript or establish journal-layout readability."],
                   "outputs": {p.relative_to(result).as_posix(): {"sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(result.rglob("*")) if p.is_file()}}
        write_json(result / "REPRODUCTION_RECEIPT.json", receipt)
        validate_output(output, protected)
        shutil.copytree(result, output, dirs_exist_ok=True)
    print(json.dumps({"status": "pass", "mode": receipt["mode"], "output": str(output), "public_inputs_verified": len(records), "cross_sectional_seed_values": 306, "hrs_seed_values": 96, "manuscript_numeric_cells_matched": tables["rounded_numeric_cells_matched"], "rendered_figures": 0 if args.verify_only else 4}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, KeyError, AssertionError) as error:
        print(f"Reproduction failed: {error}", file=sys.stderr)
        sys.exit(1)
