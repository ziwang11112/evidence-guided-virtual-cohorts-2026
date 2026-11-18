"""Render already-computed aggregate results; never read individual-level data.

This presentation layer is outside the scientific freeze. It imports no analysis,
generator, launcher, or API module. Missing results produce an error, not a demo.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parent
TRAITS = ["bmi", "total_cholesterol", "hdl_cholesterol"]
TITLES = {"bmi": "BMI", "total_cholesterol": "Total cholesterol", "hdl_cholesterol": "HDL cholesterol"}
UNITS = {"bmi": "kg/m²", "total_cholesterol": "mg/dL", "hdl_cholesterol": "mg/dL"}
CONTRASTS = ["rural_minus_pastoralist", "urban_minus_pastoralist", "urban_minus_rural"]
CONTRAST_NAMES = {
    "rural_minus_pastoralist": "Rural − pastoralist",
    "urban_minus_pastoralist": "Urban − pastoralist",
    "urban_minus_rural": "Urban − rural",
}
EPISODES = ["LIFESTYLE_A1", "LIFESTYLE_A2"]
COLORS = {"real": "#233C62", "LIFESTYLE_A1": "#7653AA", "LIFESTYLE_A2": "#D68032"}
MARKERS = {"LIFESTYLE_A1": "o", "LIFESTYLE_A2": "s"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def fmt(value, digits=3):
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if finite(value):
        return f"{value:.{digits}f}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def p_fmt(value):
    if not finite(value):
        return "—"
    return f"{value:.3g}" if value else "0 (numeric underflow)"


def esc(value):
    return html.escape(str(value), quote=True)


def table(headers, rows, cls=""):
    head = "".join(f"<th scope='col'>{esc(v)}</th>" for v in headers)
    body = "".join("<tr>" + "".join(f"<td>{esc(v)}</td>" for v in row) + "</tr>" for row in rows)
    if not body:
        body = f"<tr><td colspan='{len(headers)}'>No records available.</td></tr>"
    return f"<div class='table-scroll {cls}'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def contrast_record(dataset, trait, contrast, stratum="pooled"):
    matches = [r for r in dataset.get("analysis", {}).get("contrasts", [])
               if (r.get("trait"), r.get("contrast"), r.get("stratum")) == (trait, contrast, stratum)]
    if len(matches) > 1:
        raise ValueError(f"Duplicate contrast in {dataset['dataset_id']}: {trait}/{stratum}/{contrast}")
    return matches[0] if matches else {"status": "unavailable", "reason": dataset.get("error", dataset.get("status", "missing"))}


def short_id(dataset):
    return "Real reference" if dataset.get("kind") == "real_reference" else dataset["dataset_id"].replace("LIFESTYLE_", "")


def plot_contrasts(results, out_dir, raw=False):
    """Show reference intervals and all available individual synthetic draws."""
    reference = next(r for r in results if r.get("kind") == "real_reference")
    prefix = "raw_" if raw else ""
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.titlesize": 12, "axes.labelsize": 9,
                         "svg.fonttype": "none", "pdf.fonttype": 42,
                         "axes.edgecolor": "#CBD2DF", "axes.labelcolor": "#33425C",
                         "text.color": "#203047", "xtick.color": "#526074", "ytick.color": "#33425C"})
    fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.75), sharey=True)
    all_bounds = []
    for i, (ax, trait) in enumerate(zip(axes, TRAITS)):
        bounds = []
        unavailable = []
        for j, contrast in enumerate(CONTRASTS):
            y = 2-j
            r = contrast_record(reference, trait, contrast)
            value, lo, hi = (r.get(prefix+k) for k in ["estimate", "lower", "upper"])
            if r.get("status") == "computed" and all(finite(v) for v in [value, lo, hi]):
                ax.errorbar(value, y+.20, xerr=[[value-lo], [hi-value]], fmt="D", ms=5,
                            color=COLORS["real"], capsize=3, elinewidth=1.6, zorder=4)
                bounds.extend([lo, hi])
            else:
                unavailable.append(f"Reference/{j+1}")
            for ep, offset in zip(EPISODES, [0, -.20]):
                draws = sorted([d for d in results if d.get("episode_id") == ep], key=lambda d: d.get("seed", 0))
                values = []
                for draw in draws:
                    c = contrast_record(draw, trait, contrast)
                    if c.get("status") == "computed" and finite(c.get(prefix+"estimate")):
                        values.append((draw.get("seed"), c[prefix+"estimate"]))
                if values:
                    xs = [v for _, v in values]
                    ax.hlines(y+offset, min(xs), max(xs), color=COLORS[ep], linewidth=2.5, alpha=.42, zorder=2)
                    for k, (_, x) in enumerate(values):
                        jitter = (k-(len(values)-1)/2)*.040
                        ax.plot(x, y+offset+jitter, MARKERS[ep], ms=5,
                                mec="white", mew=.65, color=COLORS[ep], zorder=5)
                    bounds.extend(xs)
                if len(values) != 3:
                    unavailable.append(f"{ep[-2:]}/{j+1}: {len(values)}/3 draws")
        ax.axvline(0, color="#AEB8C7", lw=.9, linestyle=(0, (3, 3)), zorder=1)
        for y in [.5, 1.5]:
            ax.axhline(y, color="#E9EDF4", lw=.8)
        ax.set_title(f"{'ABC'[i]}  {TITLES[trait]}", loc="left", pad=16, fontweight="bold")
        ax.set_yticks([2, 1, 0], [CONTRAST_NAMES[c] for c in CONTRASTS])
        ax.set_ylim(-.52, 2.57)
        ax.set_xlabel(UNITS[trait] if raw else "Within-dataset biomarker SD")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=9)
        ax.tick_params(axis="x", length=3)
        ax.grid(axis="x", color="#EFF2F7", linewidth=.6)
        if unavailable:
            ax.text(0, -.22, "Missing: " + "; ".join(unavailable), transform=ax.transAxes,
                    ha="left", va="top", fontsize=7, color="#8B4F31", wrap=True)
        bounds.append(0)
        low, high = min(bounds), max(bounds)
        padding = max((high-low)*.14, .12 if not raw else .35)
        ax.set_xlim(low-padding, high+padding)
        all_bounds.extend([low, high])
    if not raw:
        low, high = min(all_bounds), max(all_bounds)
        padding = max((high-low)*.12, .12)
        for ax in axes:
            ax.set_xlim(low-padding, high+padding)
    handles = [Line2D([0], [0], marker="D", ms=6, color=COLORS["real"], label="Real reference: estimate + 95% OLS CI"),
               Line2D([0], [0], marker="o", ms=6, color=COLORS[EPISODES[0]], label="A1: three seeds + draw range"),
               Line2D([0], [0], marker="s", ms=6, color=COLORS[EPISODES[1]], label="A2: three seeds + draw range")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(.54, .055), fontsize=9)
    fig.suptitle("Same age- and sex-adjusted analysis; different input data", x=.055, ha="left", y=.99, fontsize=14, fontweight="bold")
    fig.text(.055, .012, "All nine pooled contrasts are shown. Synthetic ranges are Monte Carlo draw variation, not confidence intervals.", fontsize=8.5, color="#526074")
    fig.subplots_adjust(left=.165, right=.985, top=.80, bottom=.25, wspace=.18)
    name = "lifestyle_contrasts_raw" if raw else "lifestyle_contrasts_standardized"
    paths = []
    for suffix in ["svg", "png", "pdf"]:
        path = out_dir / f"{name}.{suffix}"
        fig.savefig(path, dpi=220, facecolor="white", bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def svg_inline(path):
    text = Path(path).read_text(encoding="utf-8")
    return text[text.index("<svg"):]


def complete_details(dataset):
    analysis = dataset.get("analysis", {})
    rows = []
    for trait in TRAITS:
        for stratum in ["pooled", "F", "M"]:
            for contrast in CONTRASTS:
                c = contrast_record(dataset, trait, contrast, stratum)
                reason = c.get("reason", "")
                rows.append([TITLES[trait], stratum, CONTRAST_NAMES[contrast], c.get("status", "missing"),
                             fmt(c.get("selected_by_paper_rule")), fmt(c.get("n"), 0),
                             fmt(c.get("estimate")), f"{fmt(c.get('lower'))}, {fmt(c.get('upper'))}",
                             fmt(c.get("raw_estimate")), f"{fmt(c.get('raw_lower'))}, {fmt(c.get('raw_upper'))}",
                             UNITS[trait], p_fmt(c.get("p_value")), p_fmt(c.get("q_subset_bh9")), fmt(reason)])
    contrasts = table(["Trait", "Stratum", "Contrast", "Status", "Paper branch selected?", "n",
                       "SD effect", "SD 95% CI", "Raw effect", "Raw 95% CI", "Raw unit", "p", "BH q (9 pooled)", "Reason"], rows)
    by_trait = {i["trait"]: i for i in analysis.get("interactions", [])}
    interactions = table(["Trait", "Status", "LR statistic", "df", "p (nominal)", "Sex-specific branch?", "Reason"],
                         [[TITLES[t], by_trait.get(t, {}).get("status", "unavailable"), fmt(by_trait.get(t, {}).get("lr")),
                           fmt(by_trait.get(t, {}).get("df"), 0), p_fmt(by_trait.get(t, {}).get("p_value")),
                           fmt(by_trait.get(t, {}).get("selects_sex_specific")),
                           fmt(by_trait.get(t, {}).get("reason", dataset.get("error", "")))] for t in TRAITS])
    group_rows = [[TITLES.get(r.get("trait"), r.get("trait")), r.get("lifestyle"), fmt(r.get("n"), 0), fmt(r.get("mean")), fmt(r.get("sd"))]
                  for r in analysis.get("group_summaries", [])]
    diagnostics = table(["Trait", "Lifestyle", "Available n", "Raw mean", "Raw SD"], group_rows)
    error = f"<p class='warning'>{esc(fmt(dataset['error']))}</p>" if dataset.get("error") else ""
    return (f"<details><summary>{esc(short_id(dataset))} · {esc(dataset.get('status', 'unknown'))}"
            f" <span>27 contrast slots + 3 interaction tests</span></summary>{error}"
            f"<p>All predeclared contrasts are retained, including unavailable entries. Female (F) and male (M) models adjust for age and use the pooled trait-specific SD.</p>"
            f"{contrasts}<h3>Interaction branch</h3>{interactions}"
            f"<p>The branch rule uses a Gaussian maximum-likelihood ratio test at nominal p &lt; 0.05. The additive overview remains visible even if this rule selects sex-specific results.</p>"
            f"<h3>Sample and distribution diagnostics</h3>{diagnostics}</details>")


def overview_rows(results):
    rows = []
    for dataset in results:
        a = dataset.get("analysis", {})
        trait_rows = {r["trait"]: r for r in a.get("trait_status", [])}
        for trait in TRAITS:
            r = trait_rows.get(trait, {})
            rows.append([short_id(dataset), TITLES[trait], r.get("status", dataset.get("status", "unavailable")),
                         fmt(a.get("input_rows"), 0), fmt(a.get("eligible_age_rows"), 0), fmt(r.get("n"), 0),
                         fmt(r.get("missing"), 0), fmt(r.get("nonpositive"), 0), fmt(r.get("sample_sd")),
                         r.get("selected_branch", "unresolved")])
    return rows


def run_findings(results):
    """Descriptive comparisons from aggregate estimates, without pass/fail cutoffs."""
    reference = next(r for r in results if r.get("kind") == "real_reference")
    virtual = [r for r in results if r.get("kind") == "virtual"]
    needed = [(t, c) for t in TRAITS for c in CONTRASTS]
    if len(virtual) != 6 or any(contrast_record(d, t, c).get("status") != "computed"
                              for d in [reference] + virtual for t, c in needed):
        return "<section><h2>What happened in this run</h2><p>The planned aggregate set is incomplete. Interpret the available estimates and statuses below; no complete-run summary is inferred.</p></section>"
    urban = "urban_minus_pastoralist"
    rural = "rural_minus_pastoralist"
    def value(d, t, c, raw=False):
        return contrast_record(d, t, c)["raw_estimate" if raw else "estimate"]
    def interval(values, digits=3):
        return f"{min(values):.{digits}f} to {max(values):.{digits}f}"
    bmi_ref = value(reference, "bmi", urban, True)
    bmi_values = [value(d, "bmi", urban, True) for d in virtual]
    tc_ref = value(reference, "total_cholesterol", urban)
    tc_author_means = []
    for ep in EPISODES:
        xs = [value(d, "total_cholesterol", urban) for d in virtual if d.get("episode_id") == ep]
        tc_author_means.append(f"{ep[-2:]} {sum(xs)/len(xs):.4f}")
    tc_raw = [value(d, "total_cholesterol", urban, True) for d in virtual]
    paragraphs = [f"<p><b>Urban–pastoralist BMI has a similar positive scale.</b> The real reference contrast is {bmi_ref:.3f} kg/m²; the six final draws give {interval(bmi_values)} kg/m². This is a descriptive comparison, not an equivalence claim.</p>",
                  f"<p><b>Standardized cholesterol agreement hides a raw-scale difference.</b> The urban–pastoralist total-cholesterol contrast is {tc_ref:.4f} SD in the reference; the means over three seeds are {'; '.join(tc_author_means)} SD. In raw units, the reference is {value(reference, 'total_cholesterol', urban, True):.3f} mg/dL, compared with {interval(tc_raw)} mg/dL across the virtual draws.</p>"]
    rural_bits = []
    sd_bits = []
    real_status = {r["trait"]: r for r in reference.get("analysis", {}).get("trait_status", [])}
    for trait in ["total_cholesterol", "hdl_cholesterol"]:
        vals = [value(d, trait, rural, True) for d in virtual]
        rural_bits.append(f"{TITLES[trait]}: reference {value(reference, trait, rural, True):.3f}, virtual {interval(vals)} mg/dL")
        sds = [next(r["sample_sd"] for r in d["analysis"]["trait_status"] if r["trait"] == trait) for d in virtual]
        sd_bits.append(f"{TITLES[trait]}: reference {real_status[trait]['sample_sd']:.3f}, virtual {interval(sds)} mg/dL")
    paragraphs.append("<p><b>The rural lipid contrasts are not closely reproduced as point estimates.</b> " + "; ".join(rural_bits) + ". Both reference 95% intervals include zero, so this is a mismatch with uncertain sample estimates, not a claim of established positive population effects.</p>")
    paragraphs.append("<p><b>Virtual lipid variability is smaller.</b> Sample SDs are " + "; ".join(sd_bits) + ". The raw-unit view is therefore essential alongside the standardized view.</p>")
    branch_notes = []
    for d in virtual:
        for inter in d.get("analysis", {}).get("interactions", []):
            if inter.get("status") == "computed" and inter.get("selects_sex_specific"):
                real_inter = next((r for r in reference["analysis"]["interactions"] if r["trait"] == inter["trait"]), {})
                branch_notes.append(f"{short_id(d)} {TITLES[inter['trait']]} (p={inter['p_value']:.5f}; reference p={fmt(real_inter.get('p_value'), 5)})")
    if branch_notes:
        paragraphs.append("<p><b>The analysis branch can differ.</b> The sex-interaction rule selects sex-specific analysis for " + "; ".join(branch_notes) + ". The affected stratified estimates are retained below; a branch change in one draw does not establish a stable biological interaction.</p>")
    return "<section><h2>What happened in this run</h2>" + "".join(paragraphs) + "<p class='note'>These results show partial application fidelity under source-rich reconstruction. The positive and discordant patterns are both retained. The published lifestyle findings were allowed inputs, so their reproduction is not independent discovery.</p></section>"


def render_html(payload, results, outcomes, plan, out_dir, standard_svg, raw_svg, input_hashes):
    reference = next(r for r in results if r.get("kind") == "real_reference")
    virtual = [r for r in results if r.get("kind") == "virtual"]
    available = sum(r.get("status") == "computed" for r in virtual)
    real_ns = {r["trait"]: r.get("n") for r in reference.get("analysis", {}).get("trait_status", [])}
    n_text = "; ".join(f"{TITLES[t]} n={fmt(real_ns.get(t), 0)}" for t in TRAITS)
    outcome_rows = []
    for ep in EPISODES:
        o = outcomes.get(ep, {})
        outcome_rows.append([ep.replace("LIFESTYLE_", ""), o.get("status", "No outcome file"),
                             o.get("selected_candidate", "—"), fmt(o.get("calls_receipted"), 0),
                             fmt(o.get("known_tariff_cost_usd"), 4), fmt(o.get("accounted_usd"), 4),
                             fmt(o.get("unknown_usage_calls"), 0)])
    outcome_table = table(["Constructor", "Status", "Selected candidate", "Receipted calls", "Known tariff USD", "Accounted USD", "Unknown-usage calls"], outcome_rows)
    sample_table = table(["Dataset", "Trait", "Status", "Input n", "Age-eligible n", "Analysis n", "Missing outcome", "Nonpositive", "Raw SD", "Selected branch"], overview_rows(results))
    branch_rows = []
    for d in results:
        by_trait = {r["trait"]: r for r in d.get("analysis", {}).get("interactions", [])}
        branch_rows.append([short_id(d)] + [
            ("sex-specific" if by_trait[t].get("selects_sex_specific") else "pooled") + f" (p={p_fmt(by_trait[t].get('p_value'))})"
            if t in by_trait and by_trait[t].get("status") == "computed" else "unavailable" for t in TRAITS])
    branch_table = table(["Dataset"] + [TITLES[t] for t in TRAITS], branch_rows)
    details = "".join(complete_details(r) for r in results)
    hash_table = table(["Aggregate input", "SHA-256"], sorted(input_hashes.items()))
    html_text = """<!doctype html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Lifestyle analysis · real and Agent-generated cohorts</title>
<style>
:root{--navy:#233c62;--purple:#7653aa;--orange:#d68032;--ink:#203047;--muted:#607086;--line:#dbe1ec;--paper:#f4f6fa}
*{box-sizing:border-box}body{font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:var(--paper);color:var(--ink)}
main{max-width:1450px;margin:auto;padding:40px 32px 75px}a{color:var(--navy);text-underline-offset:3px}h1{font-size:clamp(28px,4vw,46px);line-height:1.14;max-width:1000px;margin:12px 0 18px;letter-spacing:-.025em}h2{font-size:24px;line-height:1.25;margin:0 0 16px}h3{font-size:17px;margin:22px 0 10px}p{margin:12px 0}.eyebrow{letter-spacing:.12em;text-transform:uppercase;font-size:12px;font-weight:750;color:var(--purple)}.lead{max-width:1050px;font-size:18px;color:var(--muted)}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0}.pill{padding:6px 12px;border:1px solid var(--line);background:white;border-radius:30px;font-size:13px}.pipeline{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:24px 0}.pipeline div{background:white;border:1px solid var(--line);border-top:4px solid var(--navy);padding:18px 20px;border-radius:10px}.pipeline div:nth-child(2){border-top-color:var(--purple)}.pipeline div:nth-child(3){border-top-color:var(--orange)}.pipeline b{display:block;margin-bottom:5px}.pipeline p{font-size:14px;margin:4px 0;color:var(--muted)}
section{background:white;border:1px solid var(--line);border-radius:13px;padding:25px 28px;margin-top:20px}.note{background:#f2f4fa;border-left:4px solid var(--purple);padding:12px 17px;font-size:14px}.warning{border-left:4px solid var(--orange);padding:12px 17px;background:#fff7ef;font-size:14px}.controls{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}button{border:1px solid #bfc8d8;border-radius:7px;padding:9px 16px;font:inherit;font-size:14px;background:white;color:var(--navy);cursor:pointer}button[aria-pressed=true]{background:var(--navy);border-color:var(--navy);color:white}.chart{overflow:auto}.chart svg{width:100%;min-width:850px;height:auto;display:block}.chart[hidden]{display:none}.caption{font-size:14px;color:var(--muted);max-width:1150px}.downloads{font-size:13px;display:flex;gap:14px;flex-wrap:wrap;margin:8px 0 18px}.reading{display:grid;grid-template-columns:1fr 1fr;gap:25px}.reading p{font-size:15px}.table-scroll{overflow:auto;border:1px solid var(--line);border-radius:7px;margin:12px 0 18px}table{border-collapse:collapse;width:100%;font-size:12px;line-height:1.4}th,td{text-align:left;padding:10px 12px;vertical-align:top;border-bottom:1px solid #e6eaf1;white-space:nowrap}th{background:#f1f3f8;color:var(--navy);font-weight:650}tbody tr:last-child td{border-bottom:0}tbody tr:nth-child(even){background:#fafbfe}details{border-top:1px solid var(--line);padding:17px 0}summary{cursor:pointer;font-size:16px;font-weight:650;color:var(--navy)}summary span{font-size:12px;font-weight:400;color:var(--muted);margin-left:10px}details p{font-size:13px;color:var(--muted)}.small{font-size:13px;color:var(--muted)}.provenance td:last-child{font-family:ui-monospace,Consolas,monospace;font-size:11px}.badge-a1{color:var(--purple)}.badge-a2{color:var(--orange)}footer{font-size:12px;color:var(--muted);margin-top:22px}
@media(max-width:760px){main{padding:24px 14px}.pipeline,.reading{grid-template-columns:1fr}section{padding:20px 16px}h1{font-size:31px}.chart svg{min-width:850px}}
@media print{body{background:white}main{max-width:none;padding:0}section{break-inside:avoid}button{display:none}.chart svg{min-width:0}details{break-inside:avoid}.downloads{display:none}}
</style></head><body><main>
<div class='eyebrow'>Published-analysis application · Turkana lifestyle</div>
<h1>Keep the scientific analysis.<br>Replace the input data.</h1>
<p class='lead'>Can a cohort generated by a scientific Agent support the lifestyle comparisons in Lea et al.? These panels apply the same age- and sex-adjusted regression to public reference data and to newly generated cohorts.</p>
<div class='pills'><span class='pill'>3 biomarkers</span><span class='pill'>3 lifestyle contrasts</span><span class='pill'>2 independent constructions</span><span class='pill'>3 final draws per construction</span><span class='pill'>Source-rich reconstruction</span></div>
<div class='pipeline'><div><b>1 · Published evidence → Agent</b><p>Original paper, allowed published summaries, and the analysis request. The Agent chooses the generating law and its assumptions.</p></div><div><b>2 · Freeze → Generate</b><p>The selected construction is closed before final evaluation. Draws vary by seed; they do not add new participants or source evidence.</p></div><div><b>3 · One shared analysis</b><p>BMI, total cholesterol and HDL: standardized outcome ~ lifestyle + age + sex, with three planned lifestyle contrasts.</p></div></div>
"""
    html_text += run_findings(results)
    html_text += f"<section><h2>All nine lifestyle contrasts</h2><p class='small'>{available} of {len(virtual)} virtual tables have computed aggregate analyses. Reference status: {esc(reference.get('status', 'unknown'))}. Evaluation timestamp: {esc(payload.get('created_utc', 'not recorded'))}.</p>"
    html_text += "<div class='controls' role='group' aria-label='Effect scale'><button id='std-button' aria-pressed='true' onclick=\"showScale('std')\">Standardized effects</button><button id='raw-button' aria-pressed='false' onclick=\"showScale('raw')\">Raw-unit effects</button></div>"
    html_text += f"<div id='std-chart' class='chart'>{svg_inline(standard_svg)}</div><div id='raw-chart' class='chart' hidden>{svg_inline(raw_svg)}</div>"
    html_text += "<div class='downloads'>"
    for stem, label in [("lifestyle_contrasts_standardized", "Standardized"), ("lifestyle_contrasts_raw", "Raw units")]:
        for suffix in ["svg", "png", "pdf"]:
            html_text += f"<a href='{stem}.{suffix}'>{label} {suffix.upper()}</a>"
    html_text += "</div><p class='caption'>Navy diamonds and bars: the real reference estimate and its classical OLS 95% t interval. Purple circles (A1) and orange squares (A2): each available final seed; colored lines show their minimum–maximum range. Colored ranges describe draw variation, not confidence in the biological relationship. Points can overlap.</p>"
    html_text += "<div class='reading'><div><h3>How to read this</h3><p>Each row is the first named lifestyle minus the second, adjusted for age and sex. Right of zero means a higher biomarker; left means a lower biomarker. Compare direction, effect size, and variation across the two constructions. The raw-unit view prevents standardization from concealing differences in biomarker variability.</p></div><div><h3>What this comparison supports</h3><p>Agreement indicates that generated data can reproduce this specified analysis under this evidence setting. It does not show exact participant recovery, universal validity, or superiority over another generation method. CI overlap alone is not an equivalence test, and disagreement need not imply that the reference sample is the population truth.</p></div></div>"
    html_text += "<p class='note'>The original paper is allowed construction evidence. Results already described there are reconstruction checks, not unseen discoveries. This application covers three biomarkers and does not reproduce the paper’s full trait family, U.S. comparisons, mediation analyses, or early-life analyses.</p></section>"
    html_text += f"<section><h2>Sample sizes and analysis branches</h2><p>Each virtual table is requested to contain 1,226 rows. Outcome missingness, age eligibility, and analysis exclusions can change the usable n. Actual reference analysis counts: <b>{esc(n_text)}</b>. Neither generated row count nor a smaller synthetic p value creates additional clinical evidence.</p>"
    html_text += "<p class='caption'>The overview always shows the nine additive contrasts for a common visual comparison. The original interaction rule is also evaluated: a nominal likelihood-ratio p &lt; 0.05 selects sex-specific analyses. These branches and all stratified estimates remain visible below.</p>" + branch_table + sample_table
    html_text += "<p class='small'>Each dataset is standardized using its own trait-specific eligible mean and sample SD. That pooled SD is retained in female and male fits. The implementation uses one three-category lifestyle model and linear contrasts; it is a methods-guided reimplementation, not a rerun of recovered author code. No collection-site clustering correction is implied.</p></section>"
    html_text += "<section><h2>Complete analysis record</h2><p class='caption'>Open a dataset to inspect every contrast, interaction test, sample count and status. No unfavorable or unavailable result is filtered out. Synthetic OLS intervals are conditional simulation-model intervals; they do not include uncertainty about literature extraction, source transport or the generating law.</p>"
    html_text += "<p class='small'>The optional BH q values adjust exactly the nine pooled contrasts in this application, if all nine are available. They are not the original paper’s 11-outcome multiplicity correction. Interaction selection uses nominal p, not these q values.</p>" + details + "</section>"
    html_text += f"<section><h2>Agent execution and traceability</h2><p class='small'>Registered model: {esc(plan.get('model', {}).get('id', 'not recorded'))}; reasoning effort: {esc(plan.get('model', {}).get('reasoning_effort', 'not recorded'))}. The report reads finalized metadata and aggregate statistics only.</p>{outcome_table}"
    if len(outcomes) == 2 and all(finite(o.get("known_tariff_cost_usd")) for o in outcomes.values()):
        total_cost = sum(o["known_tariff_cost_usd"] for o in outcomes.values())
        calls = sum(o.get("calls_receipted", 0) for o in outcomes.values())
        html_text += f"<p>Total recorded tariff estimate: <b>${total_cost:.7f}</b> across {calls} receipted API calls.</p>"
    html_text += "<p class='small'>Known tariff cost is the recorded usage-based estimate, not a billing statement. Accounted cost may include budget reservations for unknown usage; the two columns are intentionally separate.</p>"
    html_text += f"<details class='provenance'><summary>Input hashes and audit boundary</summary><p>This report imports no generator, analysis operator, API launcher, or patient-level table. It displays existing aggregate evaluation output. Presentation files are outside the scientific freeze.</p>{hash_table}</details></section>"
    html_text += "<section><h2>Source and interpretation</h2><p><a href='https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/'>Lea et al., Science Advances (2020), doi:10.1126/sciadv.abb1430</a>. Lifestyle groups are pastoralist, rural nonpastoralist and urban nonpastoralist. This comparison is observational and is not a causal estimate of changing lifestyle.</p><p class='small'>Published recruitment and Table 1 counts have a documented discrepancy. The requested virtual n follows the article text (1,226); demographic generation assumptions belong to the Agent’s recorded specification. The reference comparison uses the public-data adapter and frozen analysis rules, not inferred replacements for unavailable author exclusions.</p></section>"
    html_text += "<footer>Generated from frozen-run aggregate artifacts. All data-dependent content is taken from the completed analysis records; no demo results are supplied.</footer></main><script>function showScale(scale){for(const s of ['std','raw']){document.getElementById(s+'-chart').hidden=s!==scale;document.getElementById(s+'-button').setAttribute('aria-pressed',s===scale?'true':'false');}}</script></body></html>"
    (out_dir / "index.html").write_text(html_text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "ANALYSIS_RESULTS.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "report")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error("Completed aggregate ANALYSIS_RESULTS.json is required; no placeholder report will be created.")
    payload = read_json(args.input)
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        raise ValueError("Nonempty aggregate results list required")
    ids = [r["dataset_id"] for r in results]
    if len(ids) != len(set(ids)):
        raise ValueError("Dataset IDs must be unique")
    if sum(r.get("kind") == "real_reference" for r in results) != 1:
        raise ValueError("Exactly one reference record required, even if unavailable")
    if any(r.get("kind") == "virtual" and r.get("episode_id") not in EPISODES for r in results):
        raise ValueError("Unexpected construction: colors and labels are registered for A1/A2 only")
    inputs = {str(args.input.resolve()): digest(args.input)}
    plan_path = ROOT / "PLAN.json"
    plan = read_json(plan_path) if plan_path.is_file() else {}
    if plan_path.is_file():
        inputs[str(plan_path)] = digest(plan_path)
    outcomes = {}
    for ep in EPISODES:
        path = ROOT / "episodes" / ep / "OUTCOME.json"
        if path.is_file():
            outcomes[ep] = read_json(path)
            inputs[str(path)] = digest(path)
    # All files above are aggregate statistics or execution metadata. No row data.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    standard = plot_contrasts(results, args.output_dir, raw=False)
    raw = plot_contrasts(results, args.output_dir, raw=True)
    render_html(payload, results, outcomes, plan, args.output_dir, standard[0], raw[0], inputs)
    output_paths = standard + raw + [args.output_dir / "index.html"]
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                   script_sha256=digest(__file__), patient_or_generated_rows_read=False,
                   data_sources="existing aggregate results and execution metadata only",
                   input_sha256=inputs, output_sha256={p.name: digest(p) for p in output_paths},
                   scientific_analysis_recomputed=False,
                   report_claim_scope="source-rich methods-guided replay of three biomarkers")
    (args.output_dir / "REPORT_RECEIPT.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(args.output_dir / 'index.html'), "datasets": len(results), "patient_rows_read": False}))


if __name__ == "__main__":
    main()
