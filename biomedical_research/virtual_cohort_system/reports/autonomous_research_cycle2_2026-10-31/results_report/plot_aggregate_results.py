"""Rebuild the report tables and figures from frozen aggregate artifacts only.

Run: python results_report/plot_aggregate_results.py
No participant/generated-row tables, model code, fitting, or resampling are read/run.
The manifest binds the exact inputs, script, report and produced files.
"""
from pathlib import Path
import csv
import hashlib
import json
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
INPUTS = [
    "analysis/results/aggregate.json", "analysis/results/all_endpoints.csv",
    "analysis/results/EVALUATION_COMPLETED.json", "s1i/report.json", "s2i/report.json",
    "PROTOCOL_v2.md", "CASE_ADMISSION.md", "review/INITIAL_SCIENTIFIC_REVIEW.md",
    "review/CASE_INTERPRETATION.md",
    "independent_analysis/postrun_results/comparison.json",
    "independent_analysis/postrun_results/COMPLETED.json",
    "independent_analysis/POSTRUN_REVIEW.md",
    *[f"{b}/candidates/{s}/{f}" for b in ["b1", "b2"] for s in ["initial", "final"]
      for f in ["freeze.json", "generator.py", "model_spec.json"]],
    "b1/candidates/final/decision.md", "b1/candidates/final/feedback_review.md",
    "b1/candidates/final/transfer_linkage.md", "b2/candidates/final/decision.md",
    "b2/candidates/final/source_feedback_review.md", "b2/candidates/final/transfer_linkage.md",
    *[f"b1/sources/{s}/source_summary.md" for s in ["PANI2008", "JANSEN2013", "LIU2015"]],
]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

agg = json.loads((ROOT / INPUTS[0]).read_text(encoding="utf-8"))
with (ROOT / INPUTS[1]).open(encoding="utf-8", newline="") as f:
    csv_rows = list(csv.DictReader(f))
sources = [json.loads((ROOT / name / "report.json").read_text(encoding="utf-8"))
           for name in ["s1i", "s2i"]]
completion = json.loads((ROOT / "independent_analysis/postrun_results/COMPLETED.json").read_text())
assert completion["status"] == "match"
assert completion["outputs"]["comparison.json"] == sha(ROOT / "independent_analysis/postrun_results/comparison.json")
assert agg["reference"]["n"] == 6931
assert agg["failed_slots"] == 0
assert len(agg["scheduled_results"]) == 12
assert len(csv_rows) == 403
assert agg["reference_stability"]["attempted"] == agg["reference_stability"]["valid"] == 399
for builder in ["b1", "b2"]:
    for scientific_file in ["generator.py", "model_spec.json"]:
        assert sha(ROOT / builder / "candidates/initial" / scientific_file) == sha(ROOT / builder / "candidates/final" / scientific_file)

def flat(a):
    result = {**a["questions"], **a["secondary"], "q1_residual_rms": a["q1_residual_rms"]}
    result.update({f"{var}.{stat}": val for var, vals in a["diagnostics"].items() for stat, val in vals.items()})
    return result

reference = flat(agg["reference"])
bands = agg["reference_stability"]["bands"]
slots = agg["scheduled_results"]
unique = [s for s in slots if s["stage"] == "initial"]
assert len(unique) == len({s["output_sha256"] for s in slots}) == 6
for initial in unique:
    final = next(s for s in slots if (s["builder"], s["seed"], s["stage"]) ==
                 (initial["builder"], initial["seed"], "final"))
    assert initial["output_sha256"] == final["output_sha256"]
    assert initial["analysis"] == final["analysis"]

ENDPOINTS = ["Q1_age10", "Q2_bmi5", "Q3_bmi5", "Q2_minus_Q3_bmi5", "glucose10_age_sex", "q1_residual_rms"]
ENDPOINTS += [f"{v}.{s}" for v in ["age", "female", "bmi", "glucose", "hba1c"]
              for s in ["mean", "sd_population", "q10", "q50", "q90"]]
assert len(ENDPOINTS) == len(reference) == 31
for row in csv_rows:
    obj = reference if row["kind"] == "reference" else flat(next(s["analysis"] for s in slots
          if s["builder"] == row["builder"] and s["stage"] == row["stage"] and s["seed"] == int(row["seed"])))
    assert float(row["value"]) == obj[row["endpoint"]]

COLORS = ["#0072B2", "#D55E00"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12,
                     "axes.labelsize": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.facecolor": "white"})

def save(fig, stem):
    fig.savefig(OUT / (stem + ".png"), dpi=240, bbox_inches="tight", metadata={"Software": "Matplotlib; aggregate-only report"})
    fig.savefig(OUT / (stem + ".pdf"), bbox_inches="tight", metadata={"Title": stem, "Creator": "Aggregate-only report",
                "CreationDate": None, "ModDate": None})
    plt.close(fig)

# Figure 1: every unique estimate is visible; retained stage labels do not add dots.
fig, axes = plt.subplots(1, 5, figsize=(15.3, 5.1), sharey=True)
panels = [
    ("Q1_age10", "A  Q1: age", "Per 10 years\nAdjusted for sex, BMI, glucose"),
    ("Q2_bmi5", "B  Q2: BMI", "Per 5 kg/m²\nAdjusted for age and sex"),
    ("Q3_bmi5", "C  Q3: BMI", "Per 5 kg/m²\nAdjusted for age, sex, glucose"),
    ("Q2_minus_Q3_bmi5", "D  Q2 − Q3", "Per 5 kg/m²\nDescriptive coefficient change"),
    ("glucose10_age_sex", "E  Secondary: glucose", "Per 10 mg/dL\nAdjusted for age and sex"),
]
for ax, (key, title, subtitle) in zip(axes, panels):
    band = bands[key]
    ax.axvspan(band["lower"], band["upper"], color="#d9d9d9", zorder=0)
    ax.plot(reference[key], 6, "D", color="#222222", markersize=6, zorder=4)
    for j, slot in enumerate(unique):
        b = 0 if slot["builder"] == "construction_1" else 1
        ax.plot(flat(slot["analysis"])[key], 5-j, "o" if b == 0 else "^", color=COLORS[b], markersize=6.5, zorder=4)
    ax.axvline(0, color="#444444", linewidth=0.7)
    ax.set_xlim(0, max(band["upper"], *[flat(s["analysis"])[key] for s in unique]) * 1.16)
    ax.set_ylim(-0.65, 6.8)
    ax.set_title(title, loc="left", weight="bold", pad=47)
    ax.text(0, 1.025, subtitle, transform=ax.transAxes, va="bottom", fontsize=8.8)
    ax.set_xlabel("HbA1c percentage points")
    ax.grid(axis="x", alpha=0.18)
    ax.xaxis.set_major_locator(plt.MaxNLocator(4))
    ax.set_yticks(range(7))
axes[0].set_yticklabels(["B · 18223", "B · 18211", "B · 18203", "A · 18223", "A · 18211", "A · 18203", "Reference"])
fig.suptitle("Prespecified target projections: direction agrees; magnitude differs", fontsize=16, weight="bold", y=1.10)
fig.legend(handles=[Line2D([], [], marker="D", color="#222222", ls="", label="Finite reference (n = 6,931)"),
                    Patch(facecolor="#d9d9d9", label="Reference empirical stability band"),
                    Line2D([], [], marker="o", color=COLORS[0], ls="", label="Construction A"),
                    Line2D([], [], marker="^", color=COLORS[1], ls="", label="Construction B")],
           loc="lower center", bbox_to_anchor=(0.5, -0.09), ncol=4, frameon=False)
fig.text(0.5, -0.13, "Bands: 2.5th–97.5th percentiles of 399 valid cluster resamples; not confidence or equivalence intervals.\nSix unique generated tables, n = 2,000 each. Finals retain initials; no synthetic error bars. Horizontal scales vary by panel.",
         ha="center", va="top", fontsize=9)
fig.subplots_adjust(wspace=0.25, top=0.88, bottom=0.15)
save(fig, "figure_1_target_coefficients")

checks = [{c["id"]: c for ctx in source["contexts"] for c in ctx["feedback"]["checks"]} for source in sources]
assert all(len(c) == 20 for c in checks)
pani_ids = [c["id"] for c in sources[0]["contexts"][1]["feedback"]["checks"] if c["operator"]["kind"] == "mean"]
assert len(pani_ids) == 8
x = np.arange(8)
fig, ax = plt.subplots(figsize=(10.3, 5.7))
ax.errorbar(x, [checks[0][k]["reported_value"] for k in pani_ids],
            yerr=[checks[0][k]["reported_uncertainty"]["value"] for k in pani_ids],
            color="#222222", marker="D", capsize=4, lw=1.7, label="Published mean ± reported SE (not CI)")
for b, marker in enumerate(["o", "^"]):
    ax.plot(x, [checks[b][k]["calculation"]["value"] for k in pani_ids], color=COLORS[b],
            marker=marker, lw=1.6, label=f"Construction {'AB'[b]} · source seed 18101")
ax.set_xticks(x, ["25–39", "40–44", "45–49", "50–54", "55–59", "60–64", "65–69", "≥70"])
ax.set_xlabel("Pani NHANES age band (years; source reconstruction extends to age 95)")
ax.set_ylabel("HbA1c mean (%)")
ax.set_ylim(5.09, 5.72)
ax.set_title("Pani source reconstruction: all eight age-band means", loc="left", weight="bold", fontsize=15, pad=18)
ax.grid(axis="y", alpha=0.2)
ax.legend(loc="upper left", frameon=False)
fig.text(0.5, -0.015, "Published points use the original survey estimator; reconstructions use unweighted fictional rows (6,000 per construction).\nSE bars describe the published source means. No simulation uncertainty or model uncertainty intervals are shown.",
         ha="center", fontsize=9)
fig.tight_layout()
save(fig, "figure_2_pani_age_profile")

fig, axes = plt.subplots(3, 2, figsize=(10.6, 7.8))
for r, (var, label, unit) in enumerate([("bmi", "BMI", "kg/m²"), ("glucose", "Glucose", "mg/dL"), ("hba1c", "HbA1c", "%")] ):
    for c, (stat, statlabel) in enumerate([("mean", "Mean"), ("sd_population", "Finite-reference SD")] ):
        ax = axes[r, c]
        key = f"{var}.{stat}"
        lo, hi = bands[key]["lower"], bands[key]["upper"]
        ax.axvspan(lo, hi, color="#d9d9d9", zorder=0)
        ax.plot(reference[key], 2, "D", color="#222222", ms=6)
        for j, slot in enumerate(unique):
            b, s = divmod(j, 3)
            ax.plot(flat(slot["analysis"])[key], 1-b+[-0.16, 0, 0.16][s], "o" if b == 0 else "^", color=COLORS[b], ms=6)
        vals = [lo, hi, *[flat(s["analysis"])[key] for s in unique]]
        pad = (max(vals)-min(vals))*0.15
        ax.set_xlim(min(vals)-pad, max(vals)+pad)
        ax.set_ylim(-0.5, 2.5)
        ax.set_yticks([0, 1, 2], ["B · 3 seeds", "A · 3 seeds", "Reference"])
        ax.set_xlabel(f"{label} ({unit})")
        ax.set_title(f"{'ABCDEF'[r*2+c]}  {label}: {statlabel}", loc="left", weight="bold")
        ax.grid(axis="x", alpha=0.2)
fig.suptitle("Target marginal diagnostics: means and spread", fontsize=16, weight="bold", y=1.02)
fig.text(0.5, -0.025, "Grey: reference empirical stability bands, not confidence intervals. Coloured points: six unique generated estimates.\nWithin each construction, seeds 18203 / 18211 / 18223 appear from lower to upper offset; no error bars are assigned to them.",
         ha="center", fontsize=9)
fig.tight_layout(h_pad=1.7, w_pad=2.7)
save(fig, "figure_3_target_marginals")

def fmt(x):
    return f"{x:.6f}".rstrip("0").rstrip(".")

def unit(k):
    if k == "Q1_age10": return "HbA1c pp / 10 years"
    if k.startswith("Q2") or k == "Q3_bmi5": return "HbA1c pp / 5 kg/m²"
    if k == "glucose10_age_sex": return "HbA1c pp / 10 mg/dL"
    if k == "q1_residual_rms": return "HbA1c pp"
    return {"age": "years", "female": "0/1", "bmi": "kg/m²", "glucose": "mg/dL", "hba1c": "%"}[k.split(".")[0]]

labels = [f"{'A' if s['builder']=='construction_1' else 'B'}_{s['seed']}" for s in unique]
endpoint_rows=[]
for k in ENDPOINTS:
    endpoint_rows.append({"endpoint":k, "unit":unit(k), "reference":reference[k],
       "reference_band_lower":bands[k]["lower"], "reference_band_upper":bands[k]["upper"],
       **{label:flat(s["analysis"])[k] for label,s in zip(labels,unique)}})
with (OUT / "all_31_endpoints.csv").open("w", encoding="utf-8", newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(endpoint_rows[0]));w.writeheader();w.writerows(endpoint_rows)

md=["# Complete aggregate endpoint appendix", "", "All 31 prespecified endpoints are shown. A/B denote constructions 1/2; each seed column represents a unique 2,000-row fictional table. Initial and final labels have identical values because both constructions retained their generators. This appendix does not treat 12 labels as 12 independent cohorts.", "", "Reference n = 6,931. Reference bands are empirical cluster-resampling stability bands (399/399 valid), not confidence intervals or equivalence bounds. SD uses normalized weights and no degrees-of-freedom correction; source-feedback SD uses the separate sample-SD convention. Quantiles use the inverted empirical CDF. Values are rounded only for display; CSV preserves numeric precision.", ""]
for title, ids in [("Associational projections and residual spread", ENDPOINTS[:6]), *[(f"{v}: marginal diagnostics",[k for k in ENDPOINTS if k.startswith(v+'.')]) for v in ["age","female","bmi","glucose","hba1c"]]]:
    md += [f"## {title}", "", "| Endpoint (unit) | Reference | Empirical band | " + " | ".join(labels) + " |", "|---|---:|---|" + "---:|"*6]
    for k in ids:
        md.append("| " + f"{k} ({unit(k)}) | {fmt(reference[k])} | {fmt(bands[k]['lower'])}–{fmt(bands[k]['upper'])} | " + " | ".join(fmt(flat(s['analysis'])[k]) for s in unique) + " |")
    md.append("")
md += ["## All scheduled labels and output identities", "", "Every retained final label reuses the corresponding initial table and is not a new draw.", "", "| Construction | Stage | Seed | Status | Output SHA-256 |", "|---|---|---:|---|---|"]
for s in slots:
    md.append(f"| {s['builder']} | {s['stage']} | {s['seed']} | {s['status']} | `{s['output_sha256']}` |")
(OUT / "APPENDIX_ALL_ENDPOINTS.md").write_text("\n".join(md)+"\n", encoding="utf-8")

source_rows=[]
for b, source in enumerate(sources):
    for ctx in source["contexts"]:
        for chk in ctx["feedback"]["checks"]:
            source_rows.append({"construction":"AB"[b],"context":ctx["id"],"seed":18101,"check_id":chk["id"],
                "unit":chk["operator"]["unit"],"status":chk["status"],"reported":chk["reported_value"],
                "reported_uncertainty":json.dumps(chk["reported_uncertainty"],sort_keys=True),
                "computed":chk["calculation"]["value"],"difference":chk["difference"],"n_used":chk["calculation"]["n_used"],
                "operator":json.dumps(chk["operator"],sort_keys=True),"assumption_ids":";".join(chk["assumption_ids"])})
with (OUT / "all_40_source_checks.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(source_rows[0]));w.writeheader();w.writerows(source_rows)
md=["# Complete source-feedback appendix", "", "All 20 fixed checks per construction are computable with status approximate. Differences are computed minus reported. A/B share the same reported quantities and operator definitions. Each source table contains 6,000 fictional rows at seed 18101; age-band checks use the selected counts shown below. Finals reuse the initial source outputs. No source threshold or pooled pass score was specified.", "", "Lifelines source projections each adjust for age and female, separately; Pani's age projection adjusts for female, BMI and glucose. Source slopes use raw units (years, kg/m², mg/dL, HbA1c %), unlike scaled target slopes. Source SD is sample SD. Pani means are originally survey-weighted; reconstructions are unweighted approximate projections. Source mean uncertainty is reported SE, not individual SD or CI. Unknown Jansen interval levels are not assigned a confidence level here; the feedback report's not_reported tag is retained.", ""]
for ctx in sources[0]["contexts"]:
    md += [f"## {ctx['id']}", "", "| Check (unit) | Reported | Reported SE | A | A − source | A n | B | B − source | B n |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for ch in ctx["feedback"]["checks"]:
        k=ch["id"]; a,b=checks[0][k],checks[1][k]
        se=fmt(ch["reported_uncertainty"]["value"]) if ch["reported_uncertainty"]["kind"]=="se" else "Not reported"
        md.append(f"| {k} ({ch['operator']['unit']}) | {fmt(ch['reported_value'])} | {se} | {fmt(a['calculation']['value'])} | {fmt(a['difference'])} | {a['calculation']['n_used']} | {fmt(b['calculation']['value'])} | {fmt(b['difference'])} | {b['calculation']['n_used']} |")
    md.append("")
(OUT / "APPENDIX_ALL_SOURCE_CHECKS.md").write_text("\n".join(md)+"\n",encoding="utf-8")

manifest={"scope":"Aggregate-only reporting; no model execution, new fitting/resampling, or participant/generated-row access",
          "checks":{"csv_json_endpoint_rows_equal":403,"fixed_endpoints":31,"unique_target_outputs":6,
                    "scheduled_stage_labels":12,"source_checks":40,"valid_reference_resamples":399,
                    "independent_completion_status":completion["status"],"retained_scientific_files_byte_identical":4},
          "runtime":{"python":platform.python_version(),"numpy":np.__version__,"matplotlib":matplotlib.__version__},
          "inputs":{name:sha(ROOT/name) for name in INPUTS},
          "outputs":{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!="REPORT_MANIFEST.json"}}
(OUT / "REPORT_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"output_directory":str(OUT),"checks":manifest["checks"],"files":list(manifest["outputs"])},indent=2))
