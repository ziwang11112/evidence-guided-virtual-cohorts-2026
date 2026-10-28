"""Descriptive Stage 1 reporting from completed aggregate evaluation only.

This script never reads participant rows, candidate programs, or source packets.
It requires the evaluator's final manifest, verifies its aggregate file hashes,
and writes only reporting/ and ../RESULTS.md. No analysis or cohort is selected.
Run: python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/reporting/build_report.py
"""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
EVAL = STAGE / "custodian" / "evaluation_v1"
TABLES = HERE / "tables"
FIGURES = HERE / "figures"
CASE = {"case_a": "Ross: adults, five visits", "case_b": "Travers: 12 paired adults", "case_c": "He: 44 pediatric completers"}
SHORT = {"case_a": "Ross", "case_b": "Travers", "case_c": "He"}
COLORS = {"ordinary": "#253b56", "proposed": "#007c83", "statistical": "#a96924"}
LABELS = {"pfs": "PFS", "gng": "Go/no-go", "dd100": "Discounting $100", "dd1000": "Discounting $1,000", "leptin": "Leptin (ng/mL)", "leptin_log10": "Leptin (log10 pg/mL)", "body_mass": "Body mass (kg)", "glucose": "Glucose (mmol/L)", "triglycerides": "Triglycerides (mmol/L)"}
CORR_LABELS = dict(LABELS, leptin="Leptin", leptin_log10="Log10 leptin", body_mass="Body mass", glucose="Glucose", triglycerides="Triglycerides")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt(x, digits=3):
    return "NA" if pd.isna(x) else f"{float(x):.{digits}f}"


def plain(x):
    return str(x).replace("|", "\\|").replace("\n", " ")


def md_table(headers, rows):
    return "| " + " | ".join(headers) + " |\n| " + " | ".join("---" for _ in headers) + " |\n" + "\n".join("| " + " | ".join(plain(v) for v in row) + " |" for row in rows)


def savefig(fig, name):
    fig.savefig(FIGURES / f"{name}.png", dpi=180, facecolor="white")
    fig.savefig(FIGURES / f"{name}.pdf", facecolor="white", metadata={"Creator": "Frozen Stage 1 aggregate reporting", "CreationDate": None})
    plt.close(fig)


def groups_for(case, records):
    rows = []
    d = records.loc[records.case_id.eq(case)]
    for li, lineage in enumerate(sorted(d.loc[d.branch.ne("statistical"), "lineage_id"].unique()), 1):
        for branch in ["ordinary", "proposed"]:
            # Preserve the frozen draw allocation order: anchor, alternative 1, alternative 2.
            scenarios = d.loc[d.lineage_id.eq(lineage) & d.branch.eq(branch), "scenario"].unique()
            for si, scenario in enumerate(scenarios, 1):
                label = f"L{li} O" if branch == "ordinary" else f"L{li} P{si}"
                rows.append(dict(case_id=case, lineage_id=lineage, branch=branch, scenario=scenario, plot_label=label))
    for scenario in ["rho_0", "rho_04", "rho_08"]:
        sd = d.loc[d.branch.eq("statistical") & d.scenario.eq(scenario)]
        if len(sd):
            rows.append(dict(case_id=case, lineage_id=sd.lineage_id.iloc[0], branch="statistical", scenario=scenario, plot_label={"rho_0": "Stat. ρ=0", "rho_04": "Stat. ρ=.4", "rho_08": "Stat. ρ=.8"}[scenario]))
    return rows


def select(d, group):
    return d.loc[d.lineage_id.eq(group["lineage_id"]) & d.branch.eq(group["branch"]) & d.scenario.eq(group["scenario"])]


def plot_distribution(ax, d, groups, metric, reference, interval=None, log=False, correlation=False):
    if interval is not None and np.isfinite(interval).all():
        ax.axvspan(*interval, color="#c5c9ce", alpha=.38, zorder=0)
    ax.axvline(reference, color="#202020", lw=1.4, linestyle="--", zorder=1)
    if correlation:
        ax.axvline(0, color="#8b8e92", lw=.6, zorder=0)
    for i, g in enumerate(groups):
        sg = select(d, g)
        x = sg.loc[sg.valid_comparison, metric].dropna().to_numpy(dtype=float)
        color = COLORS[g["branch"]]
        if len(x):
            ax.plot([x.min(), x.max()], [i, i], color=color, lw=1, alpha=.65, zorder=2)
            jitter = np.linspace(-.13, .13, len(x))
            ax.scatter(x, i+jitter, color=color, s=10, alpha=.55, edgecolor="none", zorder=3)
            ax.scatter([np.median(x)], [i], color=color, marker="D", s=27, edgecolor="white", linewidth=.4, zorder=4)
        else:
            ax.text(.99, i, "unavailable", transform=ax.get_yaxis_transform(), ha="right", fontsize=7, color="#b44242")
    ax.set_yticks(range(len(groups)), [g["plot_label"] for g in groups], fontsize=8)
    ax.set_ylim(len(groups)-.35, -.65)
    for y in [3.5, 7.5, 11.5]:
        if y < len(groups)-1:
            ax.axhline(y, color="#ced3d7", lw=.7)
    ax.grid(axis="x", color="#e5e7e9", lw=.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    if correlation:
        ax.set_xlim(-1, 1)
        ax.set_xticks([-1, -.5, 0, .5, 1])
    if log:
        ax.set_xscale("log")
        lo, hi = ax.get_xlim()
        ticks = [x for x in [.125, .25, .5, 1, 2, 4, 8, 16, 32, 64] if lo <= x <= hi]
        ax.xaxis.set_major_locator(FixedLocator(ticks))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))
        ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis="x", labelsize=8)


def relationship_figures(records, refs, group_map):
    for case in CASE:
        analysis = "baseline_pearson" if case == "case_a" else "change_pearson"
        d = records.loc[records.case_id.eq(case) & records.analysis.eq(analysis)]
        r = refs.loc[refs.case_id.eq(case) & refs.analysis.eq(analysis)]
        fig, axes = plt.subplots(2, 3, figsize=(14.6, 10.3))
        for ax, rr in zip(axes.flat, r.itertuples()):
            term = d.loc[d.term.eq(rr.term)]
            plot_distribution(ax, term, group_map[case], "estimate", rr.estimate, [rr.ci_low, rr.ci_high], correlation=True)
            left, right = rr.term.split("__")
            ax.set_title(f"{CORR_LABELS.get(left, left)} × {CORR_LABELS.get(right, right)}\nReal r={rr.estimate:.3f} [{rr.ci_low:.3f}, {rr.ci_high:.3f}]", fontsize=10, loc="left", pad=10)
            ax.set_xlabel("Pearson correlation", fontsize=9)
        kind = "Baseline relationships" if case == "case_a" else "Relationships between changes"
        fig.suptitle(f"{CASE[case]} | {kind}", x=.06, y=.985, ha="left", fontsize=16, weight="bold")
        fig.text(.06, .947, "All six reserved correlations; each generated cohort stays separate. L1–L3 are common-parent lineages.", fontsize=10)
        fig.legend(handles=[Patch(facecolor="#c5c9ce", alpha=.5, label="Real unadjusted 95% interval"), Line2D([], [], color="#202020", linestyle="--", label="Real estimate"), Line2D([], [], color="#007c83", marker="D", lw=1, label="Generated median and min–max"), Line2D([], [], color="#007c83", marker="o", lw=0, markersize=4, label="Individual generated estimate")], loc="lower center", ncol=2, frameon=False, fontsize=9, bbox_to_anchor=(.5, .01))
        fig.text(.06, .075, "O: ordinary (20 cohorts). P1–P3: separate proposed scenarios (6 or 7 each); mapping in scenario_key.csv.\nStatistical ρ contexts are separate reference sensitivities. Synthetic ranges are Monte Carlo ranges, not confidence intervals.", fontsize=9)
        fig.subplots_adjust(left=.075, right=.98, top=.89, bottom=.16, wspace=.35, hspace=.37)
        savefig(fig, f"{case}_reserved_correlations")

    case = "case_a"
    d = records.loc[records.case_id.eq(case) & records.analysis.eq("pooled_standardized_reml")]
    r = refs.loc[refs.case_id.eq(case) & refs.analysis.eq("pooled_standardized_reml")]
    fig, axes = plt.subplots(2, 2, figsize=(11, 10.8))
    for ax, rr in zip(axes.flat, r.itertuples()):
        plot_distribution(ax, d.loc[d.term.eq(rr.term)], group_map[case], "estimate", rr.estimate, [rr.ci_low, rr.ci_high])
        ax.set_title(f"{LABELS.get(rr.term, rr.term)}\nReal β={rr.estimate:.3f} [{rr.ci_low:.3f}, {rr.ci_high:.3f}]", loc="left", fontsize=10)
        ax.set_xlabel("Standardized coefficient (weight outcome)", fontsize=9)
    fig.suptitle("Ross | Four reserved exploratory proxy associations", x=.07, y=.98, ha="left", fontsize=15, weight="bold")
    fig.text(.07, .94, "Identical standardized random-intercept analysis; not an exact replay of published coefficients.", fontsize=10)
    fig.text(.07, .045, "Dashed line: real estimate; gray band: real unadjusted 95% interval. Dots: generated estimates; diamond/line: median/min–max.\nO and P1–P3 are common-parent comparisons; statistical contexts remain separate. No scenario is selected or pooled.", fontsize=9)
    fig.subplots_adjust(left=.09, right=.97, top=.88, bottom=.12, hspace=.38, wspace=.27)
    savefig(fig, "case_a_reserved_proxy_associations")


def uncertainty_figures(records, refs, group_map):
    for case in ["case_b", "case_c"]:
        d = records.loc[records.case_id.eq(case) & records.analysis.eq("paired_change")]
        r = refs.loc[refs.case_id.eq(case) & refs.analysis.eq("paired_change")]
        fig, axes = plt.subplots(2, 2, figsize=(11.4, 10.6))
        for ax, rr in zip(axes.flat, r.itertuples()):
            td = d.loc[d.term.eq(rr.term)]
            plot_distribution(ax, td, group_map[case], "change_sd_ratio", 1, log=True)
            ax.set_title(f"{LABELS.get(rr.term, rr.term)} | n={rr.n_persons}\nReal SD(change)={rr.change_sd:.3f}; paired r={rr.paired_r:.3f}", loc="left", fontsize=10)
            ax.set_xlabel("Synthetic / real SD(change) = SE ratio", fontsize=9)
        fig.suptitle(f"{SHORT[case]} | Reserved paired uncertainty", x=.07, y=.98, ha="left", fontsize=16, weight="bold")
        fig.text(.07, .94, "Mean changes use supplied margins; change variability depends on reserved within-person covariance.", fontsize=10)
        fig.text(.07, .045, "Dashed line: ratio 1. Dots: generated cohorts; diamond/line: median/min–max. Logarithmic horizontal axes.\nFixed endpoint sample sizes make the SD(change) ratio equal the paired-mean SE ratio. Ratios do not establish interval coverage.", fontsize=9)
        fig.subplots_adjust(left=.09, right=.97, top=.88, bottom=.12, hspace=.38, wspace=.28)
        savefig(fig, f"{case}_paired_uncertainty")


def summaries(records):
    keys = ["case_id", "lineage_id", "branch", "scenario", "validation_role", "multiplicity_family", "analysis", "term"]
    out = []
    for key, g in records.groupby(keys, sort=False, dropna=False):
        v = g.loc[g.valid_comparison]
        row = dict(zip(keys, key))
        row.update(draws=len(g), usable=len(v), usable_fraction=len(v)/len(g), reference_estimate=g.reference_estimate.iloc[0], reference_ci_low=g.reference_ci_low.iloc[0], reference_ci_high=g.reference_ci_high.iloc[0], reference_evidence_state=g.reference_evidence_state.iloc[0])
        for metric in ["estimate", "absolute_estimate_error", "se_ratio", "change_sd_ratio", "paired_r", "paired_r_absolute_error"]:
            a = pd.to_numeric(v[metric], errors="coerce").dropna() if metric in v else pd.Series(dtype=float)
            row.update({f"{metric}_{k}": f(a) if len(a) else np.nan for k, f in [("median", np.median), ("min", np.min), ("max", np.max)]})
        for state in ["positive", "negative", "overlaps_null", "unavailable"]:
            row[f"state_{state}_count"] = int(g.evidence_state.eq(state).sum())
        row["evidence_state_agreement_count"] = int(v.evidence_state_agreement.sum())
        row["evidence_state_agreement_rate"] = v.evidence_state_agreement.mean() if len(v) else np.nan
        row["unsupported_evidence_discrepancy_count"] = int(v.unsupported_evidence_discrepancy.sum())
        row["unsupported_evidence_discrepancy_rate_all_usable"] = v.unsupported_evidence_discrepancy.mean() if len(v) else np.nan
        unresolved = v.loc[v.reference_evidence_state.eq("overlaps_null")]
        row["reference_unresolved_draw_count"] = len(unresolved)
        row["unsupported_evidence_discrepancy_rate_unresolved"] = unresolved.unsupported_evidence_discrepancy.mean() if len(unresolved) else np.nan
        established = v.loc[v.reference_direction_established.eq(True)]
        row["direction_applicable_count"] = len(established)
        row["direction_agreement_count"] = int(established.direction_agreement.sum())
        row["direction_agreement_rate"] = established.direction_agreement.mean() if len(established) else np.nan
        row["n_persons_min"] = g.n_persons.min()
        row["n_persons_max"] = g.n_persons.max()
        out.append(row)
    return pd.DataFrame(out)


def paired_table(summary):
    keys = ["case_id", "lineage_id", "validation_role", "multiplicity_family", "analysis", "term"]
    o = summary.loc[summary.branch.eq("ordinary")].drop(columns="branch")
    p = summary.loc[summary.branch.eq("proposed")].drop(columns="branch")
    return p.merge(o, on=keys, how="outer", suffixes=("_proposed", "_ordinary"), validate="many_to_one")


def detailed_markdown(summary, refs, group_map):
    lines = ["# Complete registered results: common-parent comparisons", "", "Post hoc descriptive presentation of the frozen metrics. Every registered term is retained. Cells show median estimate [minimum, maximum], median synthetic/real SE ratio, usable/total draws and evidence-state agreement count. The min–max limits describe generated-cohort estimates, not confidence intervals. Real intervals are unadjusted 95% intervals. Supplied mean reconstruction is not independent validation; its uncertainty remains reserved. No proposed scenario is selected, combined, or weighted.", ""]
    for case in CASE:
        lines += [f"## {CASE[case]}", ""]
        for lineage in sorted(summary.loc[summary.case_id.eq(case) & summary.branch.eq("ordinary"), "lineage_id"].unique()):
            groups = [g for g in group_map[case] if g["lineage_id"] == lineage]
            lines += [f"### {lineage}", "", "Scenario key: " + "; ".join(f"**{g['plot_label']}** = `{g['scenario']}`" for g in groups), ""]
            cs = summary.loc[summary.case_id.eq(case) & summary.lineage_id.eq(lineage)]
            for analysis in refs.loc[refs.case_id.eq(case), "analysis"].unique():
                rr = refs.loc[refs.case_id.eq(case) & refs.analysis.eq(analysis)]
                role = cs.loc[cs.analysis.eq(analysis), "validation_role"].iloc[0]
                lines += [f"#### `{analysis}` — {role}", ""]
                rows = []
                for r in rr.itertuples():
                    row = [r.term, f"{fmt(r.estimate)} [{fmt(r.ci_low)}, {fmt(r.ci_high)}]"]
                    for g in groups:
                        s = select(cs.loc[cs.analysis.eq(analysis) & cs.term.eq(r.term)], g).iloc[0]
                        row.append(f"{fmt(s.estimate_median)} [{fmt(s.estimate_min)}, {fmt(s.estimate_max)}]; SE×{fmt(s.se_ratio_median,2)}; {s.usable}/{s.draws} usable; state {s.evidence_state_agreement_count}/{s.usable}")
                    rows.append(row)
                lines += [md_table(["Term", "Real estimate [95% CI]"]+[g["plot_label"] for g in groups], rows), ""]
    (HERE / "ALL_TERM_COMPARISONS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    lines = ["# Fixed statistical reference contexts", "", "All three prespecified contexts remain separate. The 7/7/6 allocation is a computational budget. Cells show median [min, max]; median SE ratio; evidence-state agreement count/usable draws. No context is selected using target results. This plug-in family is not matched to the finite-cohort moment-conditioning choices of every Agent lineage.", ""]
    for case in CASE:
        lines += [f"## {CASE[case]}", ""]
        ss = summary.loc[summary.case_id.eq(case) & summary.branch.eq("statistical")]
        for analysis in refs.loc[refs.case_id.eq(case), "analysis"].unique():
            rows = []
            for r in refs.loc[refs.case_id.eq(case) & refs.analysis.eq(analysis)].itertuples():
                row = [r.term, f"{fmt(r.estimate)} [{fmt(r.ci_low)}, {fmt(r.ci_high)}]"]
                for scenario in ["rho_0", "rho_04", "rho_08"]:
                    s = ss.loc[ss.analysis.eq(analysis) & ss.term.eq(r.term) & ss.scenario.eq(scenario)].iloc[0]
                    row.append(f"{fmt(s.estimate_median)} [{fmt(s.estimate_min)}, {fmt(s.estimate_max)}]; SE×{fmt(s.se_ratio_median,2)}; state {s.evidence_state_agreement_count}/{s.usable}")
                rows.append(row)
            lines += [f"### `{analysis}`", "", md_table(["Term", "Real estimate [95% CI]", "ρ=0 (7)", "ρ=.4 (7)", "ρ=.8 (6)"], rows), ""]
    (HERE / "STATISTICAL_REFERENCE_RESULTS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def render_results(records, refs, summary, group_map, disagreement, manifest):
    correlation_rows = []
    discrepancy_rows = []
    body_rows = []
    baseline_rows = []
    disagreement_rows = []
    scenario_rows = []
    for case in CASE:
        analysis = "baseline_pearson" if case == "case_a" else "change_pearson"
        for lineage in sorted(records.loc[records.case_id.eq(case) & records.branch.eq("ordinary"), "lineage_id"].unique()):
            groups = [g for g in group_map[case] if g["lineage_id"] == lineage]
            cor = [SHORT[case], lineage[-2:]]
            dis = [SHORT[case], lineage[-2:]]
            body = [SHORT[case], lineage[-2:]]
            for g in groups:
                s = select(summary.loc[summary.case_id.eq(case) & summary.analysis.eq(analysis)], g)
                cor.append(f"{s.evidence_state_agreement_count.sum()}/{s.usable.sum()}")
                dis.append(f"{s.unsupported_evidence_discrepancy_count.sum()}/{s.reference_unresolved_draw_count.sum()}")
                b = select(summary.loc[summary.case_id.eq(case) & summary.analysis.eq("paired_change") & summary.term.eq("body_mass")], g)
                if len(b):
                    body.append(fmt(b.se_ratio_median.iloc[0], 2))
                if g["branch"] == "proposed":
                    scenario_rows.append([SHORT[case], lineage[-2:], g["plot_label"].split()[-1], g["scenario"], int(s.draws.iloc[0])])
            correlation_rows.append(cor)
            discrepancy_rows.append(dis)
            if case != "case_a":
                body_rows.append(body)
            sd = disagreement.loc[disagreement.case_id.eq(case) & disagreement.lineage_id.eq(lineage) & disagreement.branch.eq("proposed")]
            for family, g in sd.groupby("multiplicity_family", sort=False):
                disagreement_rows.append([SHORT[case], lineage[-2:], family, f"{int(g.between_scenario_modal_evidence_state_disagreement.sum())}/{len(g)}"])
        for scenario in ["rho_0", "rho_04", "rho_08"]:
            s = summary.loc[summary.case_id.eq(case) & summary.branch.eq("statistical") & summary.scenario.eq(scenario) & summary.analysis.eq(analysis)]
            b = summary.loc[summary.case_id.eq(case) & summary.branch.eq("statistical") & summary.scenario.eq(scenario) & summary.analysis.eq("paired_change") & summary.term.eq("body_mass")]
            baseline_rows.append([SHORT[case], scenario, f"{s.evidence_state_agreement_count.sum()}/{s.usable.sum()}", f"{s.unsupported_evidence_discrepancy_count.sum()}/{s.reference_unresolved_draw_count.sum()}", fmt(b.se_ratio_median.iloc[0],2) if len(b) else "—"])
    for name, headers, rows in [
        ("main_correlation_evidence_state_counts", ["case", "lineage", "ordinary", "proposed_target", "proposed_alternative_1", "proposed_alternative_2"], correlation_rows),
        ("main_correlation_unsupported_counts", ["case", "lineage", "ordinary", "proposed_target", "proposed_alternative_1", "proposed_alternative_2"], discrepancy_rows),
        ("body_mass_se_ratio_medians", ["case", "lineage", "ordinary", "proposed_target", "proposed_alternative_1", "proposed_alternative_2"], body_rows),
        ("proposed_scenario_key", ["case", "lineage", "plot_label", "scenario", "cohorts"], scenario_rows),
        ("scenario_disagreement_by_family", ["case", "lineage", "family", "terms_disagree_over_total"], disagreement_rows),
        ("statistical_reference_context_counts", ["case", "scenario", "correlation_evidence_state_agreement", "correlation_unsupported_confident", "body_mass_se_ratio_median"], baseline_rows),
    ]:
        pd.DataFrame(rows, columns=headers).to_csv(TABLES / f"{name}.csv", index=False)
    case_rows = []
    for case in CASE:
        d = records.loc[records.case_id.eq(case)]
        r = refs.loc[refs.case_id.eq(case)]
        case_rows.append([SHORT[case], {"case_a":"75; five visits", "case_b":"12 endpoint pairs", "case_c":"44; glucose/TG 43 pairs"}[case], len(r), f"{int(r.validation_role.eq('given/reconstruction').sum())} given means; {int(r.validation_role.eq('reserved').sum())} reserved relations", d[["run_id","draw"]].drop_duplicates().shape[0], f"{int(d.valid_comparison.sum()):,}/{len(d):,}"])
    # Fit warnings are taken directly from aggregate analysis outputs.
    warnings = {}
    for row in records.itertuples():
        for warning in row.fit_warnings if isinstance(row.fit_warnings, list) else []:
            warnings.setdefault(warning, []).append((row.run_id, row.draw, row.analysis, row.term if row.analysis == "pooled_standardized_reml" else "trajectory"))
    warning_rows = [[msg, len(keys), len(set(keys))] for msg, keys in warnings.items()]
    pd.DataFrame(warning_rows, columns=["warning", "term_records", "unique_fits"]).to_csv(TABLES / "retained_fit_warnings.csv", index=False)
    headers = ["Case", "Lineage", "Ordinary (20)", "P1 target (7)", "P2 (7)", "P3 (6)"]
    lines = [
        "# Frozen Stage 1 results: evidence-compatible virtual cohorts",
        "",
        "**The bounded experiment completed successfully, but it does not establish a recurring accuracy advantage for the proposed scenario policy.** Its demonstrated value is an auditable sensitivity report: plausible source-compatible assumptions can change reserved relationships and uncertainty substantially. Several expanded shared-response scenarios introduce confident synthetic findings where the real-data interval is unresolved. The present policy should not advance to a broad superiority or calibrated-inference claim.",
        "",
        f"Evaluation committed at {manifest['created_utc']}. This is whole-cohort synthesis in three previously exposed development studies, with no independent confirmation, clinical validation, or journal-acceptance claim. The narrative, displays and descriptive summaries below were prepared after evaluation; they use only the metrics fixed in `protocol.json` and the 55-entry analysis registry.",
        "",
        "## Complete execution and interpretation boundary",
        "",
        "Nine initial lineages produced eighteen paired Agent revisions and three fixed statistical arms. All 420 scheduled cohorts were saved: 360 Agent and 60 statistical. Each ordinary branch has 20 cohorts; each proposed branch retains all three named scenarios with 7/7/6 cohorts, a total budget of 20. Eight ordinary revisions were legitimate no-ops. All 7,700 synthetic term records and all 55 real-reference terms were available, with no dataset-level generation or analysis failures. Counts of draws or analytic terms do not increase the number of studies.",
        "",
        md_table(["Case", "Design / denominator", "Registered terms", "Validation role", "Cohorts", "Usable term records"], case_rows),
        "",
        "The main comparison is ordinary revision beside each proposed scenario from the identical initial lineage. No proposed probabilities, effects, rows or confidence intervals are pooled; no best scenario is selected. The `target` anchor itself has seven proposed draws versus twenty ordinary draws, so its different summary may reflect finite sampling. Proposed P1/P2/P3 labels follow frozen allocation order, not ranking. All exact scenario names appear below and in [scenario_key.csv](reporting/tables/scenario_key.csv).",
        "",
        "The 25 Ross time contrasts and eight paired mean changes are given/reconstruction quantities. Their covariance, SE and evidence states remain reserved. The other 22 terms are reserved relationships: six baseline Ross correlations, four exploratory Ross proxy associations, and six change correlations in each paired study. Supplied means cannot count as independent method success. Errors are retained by endpoint and term in original units; no mixed-unit overall error score is constructed.",
        "",
        "## Reserved correlations: all cases and lineages",
        "",
        "Evidence states are positive, negative, or interval-overlaps-zero under the same registered analysis in real and synthetic data. Direction agreement is applicable only when the real interval excludes zero. These are unadjusted descriptive intervals; agreement with an unresolved interval is not proof that a relationship is absent.",
        "",
        "The table counts state agreements across the six correlations and the allocated cohorts in each separate scenario. Terms and draws are correlated diagnostic outcomes, not independent trials; these counts have no superiority test or inferential confidence interval. The detailed per-term values remain in [complete comparisons](reporting/ALL_TERM_COMPARISONS.md).",
        "",
        md_table(headers, correlation_rows),
        "",
        "**Ross.** Two reference baseline correlations have positive intervals: PFS–DD100, r=0.229 [0.002, 0.433], and DD100–DD1000, r=0.644 [0.489, 0.760]. The other four are unresolved. Ordinary state agreement is 87/120, 97/120 and 80/120 in lineages 1–3. The proposed alternatives do not give a consistent improvement; for example the shared-trait variants of lineages 1 and 3 give only 15/42 and 13/42 agreements. Lineage 2 shows less state sensitivity among its six correlations, but this does not establish calibrated magnitudes or uncertainty. All six relationships are shown in [Figure 1](reporting/figures/case_a_reserved_correlations.png) ([PDF](reporting/figures/case_a_reserved_correlations.pdf)).",
        "",
        "**Travers.** All six reference change-correlation intervals overlap zero at n=12, despite point estimates from −0.090 to 0.493. Ordinary state agreement is 116/120, 114/120 and 112/120. The separate shared-response alternatives give 25/36, 14/36 and 14/36; other proposed alternatives are closer to the unresolved state. These findings identify sensitivity to imposed shared response, not population false-positive rates or evidence that true correlations are zero. See [Figure 2](reporting/figures/case_b_reserved_correlations.png) ([PDF](reporting/figures/case_b_reserved_correlations.pdf)).",
        "",
        "**He.** All six reference change-correlation intervals also overlap zero. Ordinary state agreement declines across the three independently constructed parents (93/120, 78/120, 67/120). The persistent-endpoint/stable-trait alternatives give 41/42, 40/42 and 41/42; the shared-visit, discordant-response and mixed-visit alternatives give 0/36, 0/36 and 7/36. Keeping both sets visible shows why selecting the apparently better scenario after seeing the target would be misleading. See [Figure 3](reporting/figures/case_c_reserved_correlations.png) ([PDF](reporting/figures/case_c_reserved_correlations.pdf)).",
        "",
        "The corresponding unsupported-confident counts below use only term-by-draw comparisons whose real interval overlaps zero as denominator (four Ross correlations, all six in Travers/He). A confident synthetic interval in this subset is an unsupported-evidence discrepancy, not an observed population false positive.",
        "",
        md_table(headers, discrepancy_rows),
        "",
        "Each correlation figure includes every generated estimate, a median and min–max line for each separate context, and the real estimate/95% interval. Generated min–max ranges are Monte Carlo ranges, not confidence intervals or calibrated scenario coverage. The smaller six/seven-draw scenario samples provide coarse frequency and range estimates.",
        "",
        "## Mean reconstruction and reserved paired uncertainty",
        "",
        "Near-matching means do not recover paired change variability. Travers lineages 1 and 2 condition every finite cohort on exact supplied sample means and SDs; their constant rounded mean changes therefore largely reflect construction. Other lineages use plug-in distributions or stratified quantiles. That distinction changes sampling variation and the meaning of nominal intervals, and prevents a fixed-statistical comparison from isolating an Agent-prior effect.",
        "",
        "Body mass illustrates the unresolved covariance directly. The real pre/post correlation is 0.9986 in Travers and 0.9875 in He. The table gives each context's median synthetic/real SE ratio; with the fixed endpoint sample size this is exactly the SD(change) ratio. Every context remains separate. Other endpoints, including pediatric log10 leptin where ordinary median SE ratios are only 0.45–0.58, are retained in the full tables and figures.",
        "",
        md_table(headers, body_rows),
        "",
        "For Travers, ordinary body-mass medians range from 1.91 to 7.57 times the real SE; the nine proposed context medians range from 1.66 to 16.97. For He the respective ranges are 4.07–5.13 and 2.65–7.70. These ranges describe the set of listed context medians, not a pooled distribution or interval. All four paired endpoints appear in [Figure 4: Travers](reporting/figures/case_b_paired_uncertainty.png) ([PDF](reporting/figures/case_b_paired_uncertainty.pdf)) and [Figure 5: He](reporting/figures/case_c_paired_uncertainty.png) ([PDF](reporting/figures/case_c_paired_uncertainty.pdf)). SE agreement, even when close, would not establish confidence-interval coverage without a separate known-truth or resampling experiment.",
        "",
        "All 25 Ross reconstruction contrasts remain visible in the complete comparisons, including the five contrasts per endpoint. Their SE ratios vary by endpoint and scenario: ordinary median ratios span 0.65–1.00 for weight and 1.20–1.59 across the four behavioral endpoint families; proposed median ratios span 0.65–1.41 for weight and 1.16–1.68 for the behavioral families. These dimensionless ranges describe uncertainty diagnostics only; raw effect errors from kg, PFS, go/no-go and discounting are never combined. With unequal observation patterns even mixed-model point estimates can depend on joint structure, so the role label is not a claim of exact mathematical mean recovery.",
        "",
        "## Reserved Ross proxy associations and scenario disagreement",
        "",
        "The four standardized random-intercept proxy associations are exploratory and are not asserted to reproduce the published coefficient specification exactly. The real PFS coefficient is 0.166 [0.069, 0.262]; the other three real proxy intervals overlap zero. Proposed occasion/shared-state variants can strengthen the PFS association, but also create confident go/no-go and discounting associations unsupported by the reference interval. For the third six-draw scenario, these three unresolved proxies yield 18/18 unsupported-confident outcomes in lineages 1 and 3 and 17/18 in lineage 2. Ordinary branches already show some such discrepancies. [Figure 6](reporting/figures/case_a_reserved_proxy_associations.png) ([PDF](reporting/figures/case_a_reserved_proxy_associations.pdf)) and complete term tables retain all four proxies and every scenario.",
        "",
        "The prespecified modal-state sensitivity diagnostic gives the counts below. It compares the empirical modal state sets across the three proposed scenarios. Finite Monte Carlo variation and ties can contribute; this is neither proof of a structural effect nor a newly calibrated uncertainty measure. For given/reconstruction means, modal-state variation reflects uncertainty and any construction/missingness effect rather than independent mean validation.",
        "",
        md_table(["Case", "Lineage", "Analysis family", "Terms with modal-state disagreement / all terms"], disagreement_rows),
        "",
        "## Fixed statistical contexts",
        "",
        "The fixed Gaussian-copula family retains ρ=0, .4 and .8 separately with 7/7/6 draws. It uses independent endpoint factors and plug-in margins. These are transparent sensitivities, not a posterior mixture or target-selected comparator. The correlation state agreement, unsupported-confident count among unresolved reference terms, and body-mass SE ratio below have the same definitions as above. [The full statistical appendix](reporting/STATISTICAL_REFERENCE_RESULTS.md) retains all 55 terms and all contexts.",
        "",
        md_table(["Case", "Context", "Correlation state agreement", "Unsupported / unresolved", "Body-mass median SE ratio"], baseline_rows),
        "",
        "The fixed family's high unresolved-state agreement in Travers and He does not validate zero cross-endpoint relationships, and its wide body-mass uncertainty misses the near-perfect observed pairing. In Ross, independent endpoint factors do not reproduce the strong DD100–DD1000 correlation. No universal winner is supported by these checks.",
        "",
        "## Execution audit, warnings and limits",
        "",
        "The independent source audit passed 3,030 checks over 30 committed candidates, 21 final arms and 420 saved cohorts. The independent evaluation audit passed 127,271 checks: all 3,640 synthetic and 26 real simple-analysis rows were recomputed, and eight representative mixed-model terms received explicit-design checks plus independent scalar-REML estimate checks. Maximum simple-analysis differences were about 7.4×10⁻¹⁵ and the independent mixed estimate differences were at most 2.7×10⁻⁸. These audits verify accounting and calculations, not clinical validity or inferential coverage. See [source execution review](../stage1_review/postrun/SOURCE_EXECUTION_REVIEW.md) and [numeric audit](../stage1_review/postrun/evaluation_audit.json).",
        "",
        "All fit warnings remain included; no result was excluded after target evaluation. There were boundary warnings in 184 unique Ross fits, affecting 828 term records. One statistical ρ=0 draw (draw 7), in the DD100 trajectory, reported a non-positive-definite Hessian for its five contrast records while the evaluator retained `status=ok`. The distinction between successful execution and diagnostic model adequacy matters.",
        "",
        "Several limitations prevent a stronger claim. All three cases were previously exposed development data; fresh restricted builder contexts cannot turn them into independent confirmation. Isolation is procedural rather than an adversarial operating-system sandbox. Ordinary and proposed branches share the same maximum numerical allowance, but their retained actual diagnostic-cohort totals are 30 versus 81; equal allowance is not matched actual search. Provider/model IDs, settings, token counts, isolated inference latency and costs are unavailable, so there is no cost, model-efficiency or time-saving claim.",
        "",
        "The first Ross ordinary branch changes PFS to a 1/15-lattice beta-binomial aggregate, while its proposed sibling retains the continuous parent mapping. The validator required bounded PFS, not that score lattice. Thus even common-parent comparisons are not uniformly a pure dependence-only ablation. The finite scenario sets also bundle some assumptions (for example attendance and dependence), omit source-parameter uncertainty, and cannot exhaust all evidence-compatible joint distributions. The six/seven-cohort scenario allocation limits Monte Carlo precision. Seeds, terms and lineages cannot substitute for independent studies or support a superiority p value.",
        "",
        "## Stop/go recommendation",
        "",
        "**Go for a reproducible feasibility benchmark and an analysis-sensitivity reporting tool. Stop expansion of the current unconstrained scenario policy as an accuracy or calibrated-inference method.** Execution and complete reporting work; the recurrent finding is that marginal compatibility leaves consequential joint structure unresolved. Extra scenarios alone have not shown a recurring advantage across the development cases and builders, and some introduce substantial unsupported confidence.",
        "",
        "A justified next experiment would first predefine a bounded request for discriminating joint evidence (such as paired covariance/change SD or cross-endpoint change covariance), source applicability, and an independent analysis or research-design decision. Freeze the revision rule, comparator, scenario inclusion rules and evaluation on eligible unexposed cases before opening their results. Existing results must not be used to select the best present scenario and relabel it confirmation. Known-truth/resampling diagnostics are still needed for coverage and decision performance, and a measured user task is needed for any preparation-time claim. If no independent analytical or decision benefit recurs, retain the benchmark/resource contribution or park the policy claim.",
        "",
        "## Reproduction and complete deliverables",
        "",
        "Run from the workspace root:",
        "",
        "```powershell",
        "python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/reporting/build_report.py",
        "```",
        "",
        "The script requires and verifies the final aggregate evaluation manifest before reading any results. It reads aggregate estimates only; it never opens participant rows, generators or source packets. It rewrites only `reporting/` and this `RESULTS.md`. [reporting_manifest.json](reporting/reporting_manifest.json) records input/output hashes and the Python, pandas, NumPy and Matplotlib versions. The independent audits above are separate evidence, not rerun by this script.",
        "",
        "The complete audit trail includes [825 term-by-scenario summaries](reporting/tables/all_term_scenario_summaries.csv), [495 ordinary-vs-each-proposed term comparisons](reporting/tables/paired_policy_term_comparisons.csv), [all reference estimates](reporting/tables/real_reference_analyses.csv), [all scenario state frequencies](reporting/tables/all_scenario_state_distributions.csv), [paired means and reserved uncertainty](reporting/tables/paired_mean_and_reserved_uncertainty.csv), [given mean reconstruction with reserved SEs](reporting/tables/given_mean_reconstruction_with_reserved_se.csv), [all reserved relationships](reporting/tables/reserved_relationships.csv), and [retained fit warnings](reporting/tables/retained_fit_warnings.csv). Each scientific figure has PNG and vector PDF versions. Every case, registered term, lineage and retained scenario is present; explanatory examples above are not selection rules.",
        "",
        "### Proposed scenario names used in figures and tables",
        "",
        md_table(["Case", "Lineage", "Label", "Frozen scenario", "Cohorts"], scenario_rows),
        "",
    ]
    (STAGE / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    manifest_path = EVAL / "evaluation_manifest.json"
    if not manifest_path.exists():
        raise SystemExit("Evaluation is incomplete: final evaluation_manifest.json is required before reading aggregate results.")
    manifest = load(manifest_path)
    if (manifest["requested_cohorts"], manifest["n_final_manifests"], manifest["reference_analysis_records"]) != (420, 21, 55):
        raise ValueError("Unexpected frozen experiment inventory")
    for path, expected in manifest["files"].items():
        if sha(EVAL / path) != expected:
            raise ValueError(f"Aggregate evaluation hash mismatch: {path}")
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    records = pd.DataFrame(load(EVAL / "analysis_records.json"))
    registry = pd.DataFrame(load(STAGE / "analysis_registry.json"))
    refs = pd.concat([pd.DataFrame(load(EVAL / f"{case}_reference_analyses.json")).assign(case_id=case) for case in CASE], ignore_index=True)
    refs = refs.merge(registry[["case_id", "analysis", "term", "validation_role", "multiplicity_family"]], on=["case_id", "analysis", "term"], validate="one_to_one")
    if len(records) != manifest["analysis_records"] or len(refs) != 55:
        raise ValueError("Aggregate analysis inventory differs")
    actual = set(map(tuple, records[["case_id", "analysis", "term"]].drop_duplicates().to_numpy()))
    expected = set(map(tuple, registry[["case_id", "analysis", "term"]].to_numpy()))
    if actual != expected:
        raise ValueError("Registered term inventory differs")
    group_map = {case: groups_for(case, records) for case in CASE}
    group_rows = []
    for case, groups in group_map.items():
        for g in groups:
            r = select(records.loc[records.case_id.eq(case)], g)
            group_rows.append(dict(g, cohorts=r.draw.nunique(), seeds=",".join(map(str, sorted(r.seed.unique())))))
    scenario_key = pd.DataFrame(group_rows)
    scenario_key.to_csv(TABLES / "scenario_key.csv", index=False)
    summary = summaries(records)
    summary.to_csv(TABLES / "all_term_scenario_summaries.csv", index=False)
    pairs = paired_table(summary)
    pairs.to_csv(TABLES / "paired_policy_term_comparisons.csv", index=False)
    # Verify every recomputed display summary against the frozen evaluator.
    evaluator_summary = pd.DataFrame(load(EVAL / "scenario_summaries.json"))
    keys = ["case_id", "lineage_id", "branch", "scenario", "validation_role", "multiplicity_family", "analysis", "term"]
    check = summary.merge(evaluator_summary, on=keys, validate="one_to_one")
    validation = {"verified_summary_rows":len(check), "paired_policy_rows":len(pairs), "max_absolute_differences":{}}
    if len(check) != 825 or len(summary) != 825 or len(pairs) != 495:
        raise ValueError("Incomplete reporting inventory")
    for ours, theirs in [("draws", "analyses_total"), ("usable", "analyses_usable"), ("evidence_state_agreement_rate", "evidence_state_agreement"), ("absolute_estimate_error_median", "median_absolute_estimate_error"), ("se_ratio_median", "median_se_ratio"), ("unsupported_evidence_discrepancy_count", "unsupported_evidence_discrepancies")]:
        if not np.allclose(check[ours], check[theirs], equal_nan=True, atol=1e-12, rtol=1e-12):
            raise ValueError(f"Display summary mismatch: {ours}")
        validation["max_absolute_differences"][ours] = float(np.nanmax(np.abs(check[ours]-check[theirs])))
    if not (scenario_key.loc[scenario_key.plot_label.str.endswith("P1"), "scenario"].eq("target").all() and scenario_key.loc[scenario_key.plot_label.str.endswith(("P1", "P2")), "cohorts"].eq(7).all() and scenario_key.loc[scenario_key.plot_label.str.endswith("P3"), "cohorts"].eq(6).all()):
        raise ValueError("Figure labels differ from frozen allocation order")
    validation["frozen_plot_order_verified"] = True
    (HERE / "aggregate_reporting_validation.json").write_text(json.dumps(validation, indent=2)+"\n", encoding="utf-8")
    refs.drop(columns=["fit_warnings"], errors="ignore").to_csv(TABLES / "real_reference_analyses.csv", index=False)
    summary.loc[summary.analysis.eq("paired_change")].to_csv(TABLES / "paired_mean_and_reserved_uncertainty.csv", index=False)
    summary.loc[summary.validation_role.eq("given/reconstruction")].to_csv(TABLES / "given_mean_reconstruction_with_reserved_se.csv", index=False)
    summary.loc[summary.validation_role.eq("reserved")].to_csv(TABLES / "reserved_relationships.csv", index=False)
    # Rates are only descriptive counts of correlated term-by-draw outcomes.
    family = records.groupby(["case_id", "lineage_id", "branch", "scenario", "validation_role", "multiplicity_family"], sort=False).agg(analysis_records=("valid_comparison", "size"), usable=("valid_comparison", "sum"), state_agreement=("evidence_state_agreement", "sum"), unsupported_confident=("unsupported_evidence_discrepancy", "sum")).reset_index()
    family["agreement_rate_descriptive"] = family.state_agreement / family.usable
    family.to_csv(TABLES / "family_state_counts_descriptive.csv", index=False)
    sensitivity = load(EVAL / "scenario_sensitivity.json")
    sensitivity_flat = []
    for s in sensitivity:
        base = {k: v for k, v in s.items() if k != "scenarios"}
        for scenario, detail in s["scenarios"].items():
            sensitivity_flat.append(dict(base, scenario=scenario, **{k:json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k,v in detail.items()}))
    pd.DataFrame(sensitivity_flat).to_csv(TABLES / "all_scenario_state_distributions.csv", index=False)
    disagreement = pd.DataFrame([{k:v for k,v in s.items() if k not in ["scenarios", "interpretation"]} for s in sensitivity]).merge(registry[["case_id", "analysis", "term", "validation_role", "multiplicity_family"]], on=["case_id", "analysis", "term"], validate="many_to_one")
    disagreement.to_csv(TABLES / "scenario_disagreement_all_terms.csv", index=False)
    detailed_markdown(summary, refs, group_map)
    plt.rcParams.update({"font.family":"DejaVu Sans", "axes.titleweight":"medium", "pdf.fonttype":42, "ps.fonttype":42, "text.parse_math":False})
    relationship_figures(records, refs, group_map)
    uncertainty_figures(records, refs, group_map)
    render_results(records, refs, summary, group_map, disagreement, manifest)
    metadata = dict(evaluation_manifest_sha256=sha(manifest_path), protocol_sha256=manifest["protocol_sha256"], inputs={"analysis_records":sha(EVAL/"analysis_records.json"), "analysis_registry":sha(STAGE/"analysis_registry.json")}, environment={"python":platform.python_version(), "pandas":pd.__version__, "numpy":np.__version__, "matplotlib":matplotlib.__version__}, records=len(records), real_registered_terms=len(refs), term_scenario_summary_rows=len(summary), cohorts=records[["run_id", "draw"]].drop_duplicates().shape[0], generated_files={str(p.relative_to(HERE)).replace("\\", "/"):sha(p) for p in sorted(HERE.rglob("*")) if p.is_file() and p.name != "reporting_manifest.json" and "__pycache__" not in str(p)}, interpretation="Post hoc descriptive presentation of frozen metrics. No inferential superiority test, scenario pooling or cohort-row access.")
    metadata["results_md_sha256"] = sha(STAGE / "RESULTS.md")
    (HERE / "reporting_manifest.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:metadata[k] for k in ["records", "real_registered_terms", "term_scenario_summary_rows", "cohorts"]}, indent=2))


if __name__ == "__main__":
    main()
