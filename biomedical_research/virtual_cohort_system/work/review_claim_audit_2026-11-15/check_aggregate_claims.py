"""Read saved aggregates only; no generation, model calls or patient refits."""
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REPEAT = ROOT / "work/request_only_repeatability_2026-11-11"

files = [
    REPEAT / "ANALYSIS_RESULTS.csv",
    REPEAT / "SUMMARY_STATS.json",
    REPEAT / "AGGREGATE_TABLES.md",
    ROOT / "work/evidence_indirectness_review_2026-11-11/local_claim_audit.json",
    ROOT / "work/scientific_check_revision_2026-11-11/RESULTS.md",
]
rows = list(csv.DictReader(files[0].open(encoding="utf-8-sig", newline="")))
summary = json.loads(files[1].read_text(encoding="utf-8-sig"))
primary = {
    "bmi_sbp", "bmi_dbp", "residual_correlation",
    "K02-TC-BMI", "K02-HDL-BMI", "K02-LIPID-RESIDUAL",
}
grouped = defaultdict(list)
for row in rows:
    if row["analysis_id"] in primary:
        grouped[(row["case_id"], row["analysis_id"], row["arm"])].append(row)
comparisons = []
for case, analysis in sorted({(c, a) for c, a, _ in grouped}):
    arms = {}
    for arm in ("ordinary", "workflow"):
        selected = grouped[(case, analysis, arm)]
        arms[arm] = {
            "n_constructors": len(selected),
            "mean_estimate": mean(float(r["mean"]) for r in selected),
            "mean_absolute_difference_of_constructor_means": mean(
                abs(float(r["mean"]) - float(r["reference_value"]))
                for r in selected
            ),
        }
    comparisons.append({
        "case": case, "analysis": analysis, "arms": arms,
        "workflow_closer_descriptively":
            arms["workflow"]["mean_absolute_difference_of_constructor_means"]
            < arms["ordinary"]["mean_absolute_difference_of_constructor_means"],
    })

resources = []
section = files[2].read_text(encoding="utf-8-sig").split("## Construction and resources", 1)[1]
for line in section.splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) == 10 and cells[0].startswith(("PNS_", "LIPID_")):
        resources.append({
            "constructor": cells[0],
            "arm": "workflow" if "WORKFLOW" in cells[0] else "ordinary",
            "calls": int(cells[3]), "tariff_usd": float(cells[8]),
        })
costs = {arm: sum(r["tariff_usd"] for r in resources if r["arm"] == arm)
         for arm in ("ordinary", "workflow")}
result = {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Root arithmetic check of existing aggregate artifacts, not a new independent clinical review",
    "new_api_calls": 0, "generator_runs": 0, "patient_refits": 0,
    "patient_or_generated_rows_read": False,
    "input_bindings": [
        {"path": str(p.relative_to(ROOT)).replace("\\", "/"),
         "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in files
    ],
    "primary_profiles": comparisons,
    "workflow_closer_count": sum(x["workflow_closer_descriptively"] for x in comparisons),
    "primary_profile_count": len(comparisons),
    "costs": {
        "basis": "Saved usage-derived token-tariff estimates, not invoices or full researcher/tool costs",
        "per_arm_usd": costs,
        "workflow_to_ordinary_ratio": costs["workflow"] / costs["ordinary"],
        "mean_per_constructor_usd": sum(costs.values()) / len(resources),
        "range_per_constructor_usd": [min(r["tariff_usd"] for r in resources), max(r["tariff_usd"] for r in resources)],
        "model_calls": sum(r["calls"] for r in resources),
        "constructors": len(resources),
        "mean_model_calls_per_constructor": sum(r["calls"] for r in resources) / len(resources),
        "384_constructor_arithmetic_extrapolation_usd_not_forecast": sum(costs.values()) / len(resources) * 384,
        "cost_total_matches_saved_summary": abs(sum(costs.values()) - summary["costs"]["known_tariff_usd"]) < 1e-9,
        "call_total_matches_saved_summary": sum(r["calls"] for r in resources) == summary["counts"]["model_calls"],
    },
    "limits": [
        "Two contexts and three authors per policy/context; six endpoints are not six independent biomedical tasks.",
        "Previously exposed sample references are uncertain, not known population truth.",
        "This calculation neither tests evidence indirectness causally nor certifies workflow superiority/inferiority.",
        "17/18 adoption count and r=0.98 were not independently established here; no missing roster was invented.",
    ],
}
(HERE / "CHECKED_FACTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "primary_profiles": len(comparisons),
    "workflow_closer": result["workflow_closer_count"],
    "costs": result["costs"],
}, ensure_ascii=False, indent=2))
