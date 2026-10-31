"""Render aggregate C4 results from already-evaluated outputs; no data generation."""
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1]
OUT = R / "results"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(name):
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main():
    table_rows = csv_rows("all_table_endpoints.csv")
    aggregate_rows = csv_rows("aggregate_results.csv")
    aggregate = [row for row in aggregate_rows if row["policy"] == "retain_initial"]
    selected = read(R / "method" / "selection.json")
    pool = read(R / "method" / "pool.json")
    contract = read(R / "custody" / "evaluate_contract.json")
    commitment = read(R / "TASK_COMMITMENT.json")
    receipt = read(OUT / "EVALUATION_RECEIPT.json")
    primary = [row for row in table_rows if row["candidate"] == "c0" and row["endpoint"] == "adjusted_x_coefficient"]
    unique = [row for row in primary if row["world"] != "compatible_world_2"]
    assert len(unique) == 6
    assert all(selected["cases"][case][policy] == 0 for case in ("task_a", "task_b") for policy in ("retain_initial", "minloss", "protected_gate"))
    for case in pool["cases"]:
        assert len({(v["generator_sha256"], v["spec_sha256"]) for v in pool["cases"][case]}) == 1
    source_counts = {}
    for phase, prefix, expected in (("feedback", "f", 6), ("election", "e", 24), ("test", "t", 24)):
        diagnostics = [read(path) for path in (R / "stats").glob(f"{prefix}_*.json")]
        assert len(diagnostics) == expected
        assert all(d["status"] == "success" for d in diagnostics)
        source_counts[phase] = {"scheduled": expected,
                                "numeric_pass": sum(d["numeric_pass"] for d in diagnostics),
                                "protected_pass": sum(d["protected_pass"] for d in diagnostics),
                                "fixed_check_evaluations": sum(d["fixed_denominator"] for d in diagnostics)}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.3), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.75, bottom=0.23, wspace=0.16)
    fig.suptitle("Identical policy choices; unresolved Task B dependence", x=0.09, y=0.97,
                 ha="left", fontsize=17, fontweight="bold")
    fig.text(0.09, 0.905, "All policies select c0. Three distinct untouched tables per case; n = 4,000 per table.",
             fontsize=11, color="#424b57")
    colors = {"identified_world": "#23815c", "compatible_world_1": "#23815c", "compatible_world_2": "#bd4b35"}
    for ax, case, title in zip(axes, ("task_a", "task_b"), ("A  Identified Gaussian law", "B  Two compatible Gaussian laws")):
        rows = sorted([row for row in unique if row["case"] == case], key=lambda row: row["seed"])
        for world_id, world in contract["cases"][case]["worlds"].items():
            truth = world["truth"]["adjusted_x_coefficient"]
            ax.axhline(truth, color=colors[world_id], linewidth=1.8, linestyle=(0, (5, 3)), zorder=1)
            label = "Truth" if case == "task_a" else "World 1 truth" if world_id == "compatible_world_1" else "World 2 truth"
            xz = world["covariance"][0][2]
            ax.text(-0.43, truth + 0.014, f"{label} = {truth:+.4f}  (rXZ = {xz:.2f})",
                    color=colors[world_id], fontsize=10)
        ax.axhline(0, color="#c5c9cf", linewidth=0.8, zorder=0)
        ax.scatter(range(3), [float(row["estimate"]) for row in rows], s=58, color="#1d3850", zorder=3)
        for i, row in enumerate(rows):
            ax.annotate(f"{float(row['estimate']):.4f}", (i, float(row["estimate"])),
                        xytext=(0, -19), textcoords="offset points", ha="center", fontsize=10, color="#1d3850")
        ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=14)
        ax.set_xticks(range(3), [row["seed"] for row in rows])
        ax.set_xlim(-0.5, 2.5)
        ax.set_ylim(-0.29, 0.30)
        ax.set_yticks([-.2, -.1, 0, .1, .2])
        ax.set_xlabel("Untouched seed", labelpad=10)
        ax.grid(axis="y", color="#e9ebef", linewidth=0.6)
    axes[0].set_ylabel("Adjusted X coefficient in Y ~ X + Z", labelpad=10)
    fig.text(0.09, 0.095, "Points are shared by all three policies and all four candidate labels within each case.", fontsize=10, color="#424b57")
    fig.text(0.09, 0.05, "24 scheduled slots contain six distinct tables. No confidence intervals or independent-world replication are implied.", fontsize=10, color="#424b57")
    plot = OUT / "primary_endpoint.png"
    fig.savefig(plot, dpi=200, facecolor="white")
    plt.close(fig)

    short_world = {"identified_world": "A", "compatible_world_1": "B world 1", "compatible_world_2": "B world 2"}
    endpoint_label = {"adjusted_x_coefficient": "Adjusted X (primary)", "adjusted_z_coefficient": "Adjusted Z", "partial_correlation_xy_given_z": "Partial r(X,Y given Z)"}
    summary_lines = ["| Case / world | Endpoint | Truth | Mean estimate | MAE | MSE | Direction matches |",
                     "|---|---|---:|---:|---:|---:|---:|"]
    for row in aggregate:
        summary_lines.append(f"| {short_world[row['world']]} | {endpoint_label[row['endpoint']]} | {float(row['truth']):.6f} | {float(row['mean_estimate']):.6f} | {float(row['mean_absolute_error']):.6f} | {float(row['mean_squared_error']):.6g} | {row['direction_matches_count']}/3 |")
    seed_lines = ["| Case | Seed | Adjusted X | Adjusted Z | Partial r |", "|---|---:|---:|---:|---:|"]
    for row in unique:
        others = {v["endpoint"]: float(v["estimate"]) for v in table_rows if v["case"] == row["case"] and v["candidate"] == "c0" and v["seed"] == row["seed"]}
        seed_lines.append(f"| {row['case'].replace('task_', '').upper()} | {row['seed']} | {others['adjusted_x_coefficient']:.6f} | {others['adjusted_z_coefficient']:.6f} | {others['partial_correlation_xy_given_z']:.6f} |")
    bands = []
    for row in aggregate:
        if row["endpoint"] == "adjusted_x_coefficient":
            counts = Counter(row["engineering_fidelity_bands"].split("|"))
            bands.append(f"- {short_world[row['world']]}: {dict(counts)}; mean numerical utility {float(row['mean_numerical_utility_score']):.6f}.")
    chronology_paths = [("Task/evaluator frozen", "TASK_COMMITMENT.json", "frozen_at_utc"),
                        ("Visible source admission", "SOURCE_ADMISSION.json", "created_utc"),
                        ("Initial feedback released", "FEEDBACK_GATE.json", "created_utc"),
                        ("Frozen pool election released", "ELECTION_GATE.json", "created_utc"),
                        ("Sealed selection bound into test release", "TEST_GATE.json", "created_utc"),
                        ("All 24 outputs committed and reveal authorized", "REVEAL_GATE.json", "created_utc"),
                        ("Unchanged evaluator completed", "results/EVALUATION_RECEIPT.json", "completed_utc")]
    chronology = ["| Phase (31 October 2026, UTC) | Time | Artifact SHA256 |", "|---|---|---|"]
    artifact_hashes = {}
    for title, path, key in chronology_paths:
        value = read(R / path)
        artifact_hashes[path] = sha(R / path)
        chronology.append(f"| {title} | {value[key].split('T')[1].split('.')[0]} | `{artifact_hashes[path]}` |")
    source_lines = ["| Phase | Scheduled tables | Full numeric pass | Protected-use pass | Fixed check evaluations |", "|---|---:|---:|---:|---:|"]
    for phase, value in source_counts.items():
        source_lines.append(f"| {phase} | {value['scheduled']} | {value['numeric_pass']} | {value['protected_pass']} | {value['fixed_check_evaluations']} |")
    b_separation = contract["task_b_identification_separation"]
    report = f"""# C4: identical policy choices and a designed identification counterexample

The policy comparison is nondiscriminating: retain, minimum source loss, and protected-use acceptance all select c0 in both tasks. Each author proposal opportunity retained the initial generator/specification within its task. All four labels produce byte-identical outputs for each seed. Therefore the 24 scheduled test slots contain only six distinct tables (three per task); policies and candidate labels are not additional replicates. No selector benefit or superiority is established. This interpretation was recorded in ELECTION_GATE.json before election and hidden reveal.

All 54 scheduled generation runs succeeded (6 initial feedback, 24 election, 24 untouched test). This evaluation generated no new rows and imported no candidate code. The unchanged frozen evaluator scored every scheduled final table under every precommitted world. Rows remain local.

## Source qualification and selection

{chr(10).join(source_lines)}

Election losses were 0.042433618 for every A label and 0.036015735 for every B label. Every candidate passed all fixed source checks on all three election seeds (27 checks per A candidate; 24 per B candidate) and every admitted correlation. Tie order retains c0; no proposal strictly improves loss, so the protected policy also retains qualified c0. Qualification concerns admitted source statistics only.

## Held-out endpoints

The primary operator is the X coefficient from OLS Y ~ X + Z with intercept. Secondary operators are the Z coefficient and Pearson partial correlation of X,Y given Z. Coefficients use fixed population-standardized measurement units, without sample restandardization. The following results apply identically to all three policies; means and errors summarize only the three distinct seed tables per task. Both B worlds score the same outputs.

{chr(10).join(summary_lines)}

All raw estimates and errors are retained in [all_table_endpoints.csv](all_table_endpoints.csv) (108 rows: 24 tables × applicable worlds × 3 endpoints), [selected_policy_endpoints.csv](selected_policy_endpoints.csv) (81 rows, with policy reuse explicit), and [aggregate_results.csv](aggregate_results.csv) (27 rows). None of these row counts is an independent-sample count.

{chr(10).join(seed_lines)}

The frozen primary error bands are <=0.05, >0.05–0.10, >0.10–0.20 and >0.20. Numerical utility is 1/(1+(absolute error/0.10)^2), averaged over three tables. These are descriptive engineering conventions, not clinical usefulness thresholds. Direction is separate; no bands or utility were prespecified for secondary endpoints.

{chr(10).join(bands)}

![Primary endpoint across the three distinct untouched seeds](primary_endpoint.png)

## Meaning and limits

Task A admits an explicitly artificial Gaussian law with zero means, unit SDs and correlations rXY=0.30, rYZ=0.60, rXZ=0.20. Its adjusted-X truth 0.1875 is mathematically derivable from those moments. Its small error establishes numerical agreement for this construction, not a new biological result or independent validation of unreported evidence. Gaussianity identifies the full joint law when its moments are complete; these linear projection endpoints themselves are determined by the covariance matrix and do not require Gaussianity.

Task B admits the same X,Y and Y,Z Gaussian marginals but leaves rXZ unidentified. Two positive-definite compatible Gaussian laws were deliberately fixed before authorship: rXZ=0.10 and rXZ=0.70. Their adjusted-X truths are +0.242424 and −0.235294. Both preserve every admitted source moment. The same source-qualified outputs are positive on all three seeds, yet disagree in direction with world 2 and have mean absolute primary error 0.427674 there. The partial correlation also has the wrong direction under world 2; the Z coefficient retains its direction but has mean absolute error 0.206078.

The primary truths differ by {b_separation['primary_truth_absolute_difference']:.6f}, so any single estimate must have absolute error at least {b_separation['any_single_estimate_minimum_possible_worst_world_absolute_error']:.6f} under at least one world. This is a designed identification counterexample, not a discovered biomedical phenomenon. The two worlds are ambiguity witnesses with no assigned probabilities; no preferred world was selected after seeing outcomes. Source matching alone cannot resolve the missing dependence. Three simulation seeds do not support confidence intervals, clinical claims, or broad policy comparisons.

## Chronology and integrity

{chr(10).join(chronology)}

The sealed selection SHA256 is `{sha(R/'method'/'selection.json')}`; the test output manifest SHA256 is `{sha(R/'TEST_OUTPUT_MANIFEST.json')}`. The test release binds the selection before test generation; the reveal gate binds all 24 table commitments. Every test table and test diagnostic hash was checked. Frozen evaluator SHA256 `{sha(R/'custody'/'evaluate.py')}` and contract SHA256 `{sha(R/'custody'/'evaluate_contract.json')}` matched before and after evaluation. The [evaluation receipt](EVALUATION_RECEIPT.json) records all 24 result hashes and the adapter hash. Hidden findings are not candidate feedback. Independent root review remains the final audit step.

The requested comparison is complete. Preserve the nondiscriminating result; this unit supplies no basis for adding selector complexity or claiming its benefit. Any new scientific question requires a separately authorized design.
"""
    (OUT / "RESULTS.md").write_text(report, encoding="utf-8")
    artifact_hashes.update({name: sha(OUT / name) for name in ("RESULTS.md", "primary_endpoint.png", "render_results.py")})
    artifact_hashes["method/selection.json"] = sha(R / "method" / "selection.json")
    artifact_hashes["TEST_OUTPUT_MANIFEST.json"] = sha(R / "TEST_OUTPUT_MANIFEST.json")
    (OUT / "REPORT_MANIFEST.json").write_text(json.dumps({"schema": "c4_aggregate_report_manifest_v1", "files": artifact_hashes, "source_qualification_counts": source_counts, "plot_distinct_points": 6, "confidence_intervals": False}, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({"status": "report_and_plot_created", "source_counts": source_counts, "report_sha256": sha(OUT/'RESULTS.md'), "plot_sha256": sha(plot)}))


if __name__ == "__main__":
    main()
