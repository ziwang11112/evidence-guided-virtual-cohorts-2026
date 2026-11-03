"""Write the complete descriptive report from independently checked aggregates."""
from pathlib import Path
import hashlib
import json

N = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def number(value):
    return "unavailable" if value is None else f"{value:.6g}"


def span(values):
    return "unavailable" if not values else "–".join(number(v) for v in values)


def main():
    s = read(N / "COMPLETE_AGGREGATE_SUMMARY.json")
    assert s["independent_numeric_verification"]["status"] == "matched"
    assert not s["independent_numeric_verification"]["disagreements"]
    for binding in s["input_bindings"].values():
        assert hashlib.sha256(Path(binding["path"]).read_bytes()).hexdigest() == binding["sha256"]
    assert not s["all_failure_statuses"]
    slots = s["target_slot_records_unchanged"]
    assert all(x["generated_only_diagnostics"]["invalid_rows"] == 0 and
               x["generated_only_diagnostics"]["duplicate_rows_after_first"] == 0 for x in slots)
    assert all(change["complete"] and change["mean_absolute_discrepancy_change"] == 0
               for endpoint in s["endpoint_summaries_and_changes"].values()
               for constructor in endpoint["constructors"].values()
               for change in constructor["changes"].values())
    for a in ("A01", "A02"):
        for seed in (41911, 41912, 41913):
            selected = [x for x in slots if x["constructor"] == a and x["seed"] == seed]
            assert len(selected) == 3 and len({x["output_sha256"] for x in selected}) == 1
    source = read(N / "INITIAL_SOURCE_AGGREGATES.json")
    source_audit = read(N / "source_audit/SOURCE_AUDIT.json")
    cost = read(N / "TARGET_EXECUTION_COST.json")
    lines = [
        "# Complete developmental continuation results — 3 November 2026",
        "",
        "The two Agent-authored laws generated whole biomedical cohorts without participant input. The clearest target result is analysis-specific: A02 preserved the adjusted glucose–HbA1c slope near the existing CHNS sample estimate across all three fixed seeds. Both laws retained positive BMI and glucose associations, but BMI effects were too small relative to that sample reference, age associations were not recovered, and marginal/joint discrepancies remained. All four revision authors retained their initial laws; all paired revision contrasts are zero. This unit establishes a limited use profile, not general population recovery, equivalence, or a revision advantage.",
        "",
        "Primary and independent numerical evaluation are complete. CHNS is a researcher-exposed developmental reference, not a new independent confirmation. All generation and scientific decisions closed before the frozen evaluator accessed its existing reference aggregates. No reference participant records were redecoded, no new patient data were downloaded, and no target result was returned for revision.",
        "",
        "## What was implemented and executed",
        "",
        "This is a separately approved technical continuation of the prior pilot, which remains closed with all 72 allocations aborted unrun. It reuses two previously Agent-authored laws, with zero fresh initial scientific constructors. Root repaired only the Jansen native HbA1c alias/conversion metadata; initial generator bytes, scientific specification, evidence, support and analysis declarations stayed unchanged. The exact lineage and allowed deltas were reviewed before execution. Four fresh-context branch authors then made one self-review or source-feedback decision each; all four retained, with no schema return or scientific change in those branches.",
        "",
        "The Agent chose the scientific law and parameters. Deterministic tools executed its sampler, translated measurements, calculated source statistics and checked declarations. A01 is an additive glucose-mediated construction; A02 is a shared-factor construction using different Pearson/lognormal and Spearman/copula identities. These are assumed associative joint laws, not identified causal models. Both explicitly assume age/female independence. Source contexts J/B/M and target T use the same respective generator and shared specification with declared context inputs. See [method implementation](METHOD_IMPLEMENTATION.md), [frozen protocol](PROTOCOL.md), and [lineage](LINEAGE.json).",
        "",
        "| Role | Successful / planned executions | Rows per table | Virtual row-slots | Distinct output hashes |",
        "|---|---:|---:|---:|---:|",
    ]
    for role in ("source", "target"):
        r = s["allocation_hash_accounting"][role]
        lines.append(f"| {role} | {r['successful_execution_count']} / {r['planned_allocation_count']} | 3,000 | {r['successful_execution_count'] * 3000:,} | {r['unique_successful_output_hash_count']} |")
    lines += [
        "",
        "All 72 executions succeeded, with no replacement draws. These comprise 24 distinct table hashes, not 72 independent constructions or 216,000 clinical observations. Retained versions repeat the same seed-specific outputs. The statistical construction count remains two. Target reference: 6,631 eligible CHNS participants, with regression uncertainty based on 218 communities. Synthetic rows do not increase that real sample size.",
        "",
        "## Source relationships",
        "",
        "The table shows initial versions once because all branches retained them. Every source allocation and all 72 comparison records remain in [the independent source audit](source_audit/SOURCE_AUDIT.json). Jansen slopes are on native IFCC HbA1c units; target slopes below are on HbA1c percentage-point units. Source comparisons are qualified equal-weight source-context point comparisons. Unknown original weighting, processing and selection prevent strict source replay; point proximity is not source equivalence.",
        "",
        "| Source statistic | Published point | A01 mean [three-seed range] | A02 mean [three-seed range] |",
        "|---|---:|---:|---:|",
    ]
    labels = {"Q_J_bmi": "J: adjusted BMI slope, IFCC per kg/m²", "Q_J_fpg": "J: adjusted glucose slope, IFCC per mmol/L", "Q_B_pearson": "B: glucose–HbA1c Pearson r", "Q_M_spearman": "M: glucose–HbA1c Spearman rho"}
    for check, label in labels.items():
        records = {r["constructor"]: r for r in source["groups"] if r["check"] == check}
        cells = [f"{number(records[a]['generated_mean'])} [{span([records[a]['generated_min'], records[a]['generated_max']])}]" for a in ("A01", "A02")]
        lines.append(f"| {label} | {number(records['A01']['published_point'])} | {cells[0]} | {cells[1]} |")
    lines += [
        "",
        "A02's source point estimates are closer on the MIND rank relationship. A01's MIND Spearman range remains materially below its published point; the feedback author saw this and retained the model because it did not consider a unique structural/transport revision justified. A02's feedback author also retained. These decisions do not establish that revision is impossible or that authoring restrictions caused retention. No optimizer, author-side simulation or source-fitting pilot was run.",
        "",
        "![Source relationships](figures/source_fidelity_initial.png)",
        "",
        "## All three frozen target analyses",
        "",
        "All models include an intercept. E1: HbA1c on age/female/BMI, focal BMI. E2: HbA1c on age/female/glucose, focal glucose. E3: HbA1c on female/BMI/glucose/age, focal age. The reported generated ranges are fixed-seed variation, not confidence intervals. Reference intervals describe sample-estimation uncertainty; they are not equivalence margins or known population truth. No new overall success threshold was introduced.",
        "",
        "| Analysis | Reference coefficient [clustered 95% CI] | A01 three-seed range | A02 three-seed range | Declared support, both laws |",
        "|---|---:|---:|---:|---|",
    ]
    for endpoint, label in (("E1", "BMI, percentage points per kg/m²"), ("E2", "Glucose, percentage points per mmol/L"), ("E3", "Age, percentage points per year")):
        r = s["endpoint_summaries_and_changes"][endpoint]
        ref = r["reference"]
        versions = {a: r["constructors"][a]["versions"]["initial"] for a in ("A01", "A02")}
        lines.append(f"| {label} | {number(ref['coefficient'])} [{span([ref['interval']['lower'], ref['interval']['upper']])}] | {span(versions['A01']['seed_range'])} | {span(versions['A02']['seed_range'])} | {versions['A01']['analysis_support']['assessment']} / {versions['A02']['analysis_support']['assessment']} |")
    lines += [
        "",
        "A02's three glucose coefficients lie within the existing reference regression interval. This is a useful descriptive agreement for that analysis, not a formal equivalence result. Both BMI profiles remain below the reference coefficient and its interval despite retaining the positive direction. Age is unresolved in A01 and weakly negative in all three A02 draws, while the reference association is positive. Neither law had evidence support for the age analysis; both assumed independence. These observed failures remain main results, not a discarded subset.",
        "",
        "All 18 branch/endpoint discrepancy changes (two laws × three endpoints × three paired contrasts) are exactly zero. Initial, self-review and source-feedback versions yield identical seed-specific analyses. This unit provides no revision benefit and does not compare against new statistical or Agent baselines. Per-seed estimates, paired changes and support declarations are retained in [the complete aggregate summary](COMPLETE_AGGREGATE_SUMMARY.json).",
        "",
        "![All target analyses and versions](figures/target_analysis_complete.png)",
        "",
        "## Complete reference-comparable diagnostic profile",
        "",
        "All 27 predeclared diagnostics are shown. Since retained versions have byte-identical seed-specific outputs, the table displays one profile per law; the JSON retains every version. Marginal reference values are sample summaries without newly estimated uncertainty. Differences are descriptive sample discrepancies, not estimates of bias against a known population distribution.",
        "",
        "| Diagnostic | Reference value | A01 three-seed range | A02 three-seed range |",
        "|---|---:|---:|---:|",
    ]
    a1 = s["reference_comparable_diagnostics_27"]["A01/initial"]
    a2 = {r["id"]: r for r in s["reference_comparable_diagnostics_27"]["A02/initial"]}
    for r in a1:
        lines.append(f"| {r['id']} | {number(r['reference_value'])} | {span(r['generated_range'])} | {span(a2[r['id']]['generated_range'])} |")
    lines += [
        "",
        "A02's glucose-slope agreement coexists with substantially narrower glucose and HbA1c variation than this reference and a different Pearson/Spearman profile. Thus reproducing an association coefficient is not sufficient evidence that the same dataset supports every distributional or joint analysis. A01 also retains important marginal/joint discrepancies. This is an observed use-profile contrast; the present two-law experiment does not identify which modeling assumption caused each discrepancy.",
        "",
        "The generated-only profile is also retained in full: BMI/glucose/HbA1c q01 and q99, all ten Pearson pairs, exact duplicate-row counts, nonfinite/domain/fractional-age counts, and all fit ranks and condition numbers. These additions have no newly opened reference comparator. All 18 target tables have zero detected invalid rows and exact duplicate rows, and all 54 focal analyses are computable. These are execution/design checks; they do not certify physiological realism, population diversity or inference calibration.",
        "",
        "## Verification, limitations and cost",
        "",
        f"The independent source script recomputed {source_audit['compared_available_count']} available comparisons with no mismatches; maximum absolute arithmetic difference was {source_audit['maximum_absolute_statistic_error']:.4g}. The separate frozen target evaluator independently recomputed all 18 target profiles, including 54 focal coefficients, 486 reference-comparable diagnostic values, generated-only diagnostics and paired summaries. Its status is matched with zero disagreements. Reference uncertainty was reused from the frozen aggregate, not reestimated. The primary report's original pending field is intentionally unchanged; current verification status comes from the independent completion and report.",
        "",
        "All source/target support checks and the reviewed finite-moment laws are retained. Passing a metadata interface cannot certify correct paper extraction, valid transport, or a realistic biomedical population. The construction laws remain assumption-dependent. The independent source report's release_sha256 is the raw release-file byte hash; the controller uses a canonical full-release digest and the approval record uses a review-excluding digest. These are different defined hash scopes, not different scientific releases.",
        "",
        f"Measured target dispatch wall time across six versions was {cost['version_dispatch_wall_seconds_sum']:.3f} seconds ({cost['version_dispatch_wall_seconds_sum']/60:.2f} minutes), while their 18 execution-adapter receipts sum to {cost['target_adapter_elapsed_seconds_sum']:.3f} seconds. The difference includes repeated verification/orchestration and is not an instrumented CPU breakdown. Global closure, evaluation, earlier sources and author/reviewer time are excluded. Model-token totals were not available. See [cost records](TARGET_EXECUTION_COST.json). This prototype has substantial orchestration overhead; potential reductions were not measured. No time/cost-saving superiority is claimed.",
        "",
        "No new original evidence, dataset, initial scientific law, trained model, paid API or HPC job was introduced. The four fresh scientific branch decisions must not be confused with the number of orchestration/review Agent calls. The earlier unrun pilot and all failures remain in the lineage. Public records contain code, original prose, metadata and aggregate results; no individual real/generated tables, full third-party papers or credentials are included.",
        "",
        "## Decision for the research direction",
        "",
        "Retain evidence-to-whole-cohort generation and numerical study-conditioned evidence translation as the core method under investigation. This unit supports one particularly useful target analysis and directional feasibility for BMI/glucose, with explicit limits. It does not support a general high-quality-data guarantee, a feedback-revision contribution, an overall method ranking, individual measurement recovery, causal conclusions or replacing clinical collection. There is no matched old-versus-new causal comparison of the overall method in this unit.",
        "",
        "Close this bounded unit. Preserve both laws and all predeclared outcomes; do not choose a winner by the revealed target, retune CHNS, add seeds, acquire new datasets or expand components here. The method description and complete developmental results are ready for the working draft; broad method superiority and confirmatory claims remain unsupported. A future scientific revision would need a separately specified evidence/assumption gap and evaluation design. Computational overhead can be addressed separately from scientific model choices, after this frozen unit.",
        "",
        "Reproduction/inspection: unchanged controller and evaluator modules are bound in RELEASE.json; exact seeds, context operators, support rules, branch packets and review hashes are retained. The public package is an inspection archive, not a self-contained runtime: private row tables and some absolute local bindings are deliberately omitted. Aggregate rendering scripts do not execute generators or create additional scientific analyses.",
        "",
    ]
    (N / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"report": str(N / "RESULTS.md"), "all_target_profiles": len(slots), "all_reference_diagnostics": 27}))


if __name__ == "__main__":
    main()
