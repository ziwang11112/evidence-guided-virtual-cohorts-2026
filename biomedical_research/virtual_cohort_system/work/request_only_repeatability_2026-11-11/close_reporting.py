"""Close completed reporting; never executes models or rewrites frozen experiments."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    frozen = {
        ROOT / "PLAN.json": "ec1115c2df2ee6a4be3c320bf690893325870561474418661f4c813faec20152",
        ROOT / "LAUNCH_FREEZE.json": "6605f3c22c186bd352c707009371784c20c99e796fb2669e7cbb8a252d16776f",
        PROJECT / "manuscript/DRAFT_v0_29.md": "ba5e5704a5537c5c9483fd3b6b85266f849cf7f41781d21255b3716626963506",
    }
    for path, expected in frozen.items():
        if sha(path) != expected:
            raise RuntimeError(f"Frozen artifact changed: {path.name}")
    reviews = {
        "review/INDEPENDENT_RECOMPUTATION.json": "pass",
        "review/CLOSED_EXECUTION_AUDIT.json": "pass",
        "review/INDEPENDENT_CLOSURE_REVIEW.json": "pass",
        "review/SCIENTIFIC_PROVENANCE_AUDIT.json": "COMPLETE_12_OF_12_BOUNDED_SOURCE_CODE_AUDIT",
        "review/FIGURE_VISUAL_REVIEW.json": "PASS",
        "review/FINAL_REPORT_REVIEW.json": "PASS",
    }
    for rel, expected in reviews.items():
        if read(ROOT / rel)["status"] != expected:
            raise RuntimeError(f"Review not complete: {rel}")
    now = datetime.now(timezone.utc).isoformat()
    state = read(ROOT / "STATE.json")
    if (state["finalized_sessions"], state["successful_final_tables"], state["api_calls"]) != (12, 36, 331):
        raise RuntimeError("Unexpected completion counts")
    state.update({
        "status": "completed_independently_reviewed_with_scientific_findings",
        "updated_utc": now,
        "completed_utc": now,
        "known_closed_episode_tariff_usd": state["known_tariff_usd"],
        "unknown_usage_calls": 0,
        "independent_recomputation": "pass",
        "independent_execution_and_closure": "pass",
        "scientific_source_code_audit": "complete_with_tail_and_transfer_findings",
        "final_figures": "independent_actual_pdf_visual_and_numeric_review_pass",
        "report_review": "pass",
        "manuscript_delivery": "MANUSCRIPT_INSERT.md; old v0.29 unchanged; erratum recorded",
        "public_github_synced_this_unit": False,
        "next_paid_run_scheduled": False,
        "next_action": "Integrate complete results; define bounded generic scientific-law review before any separately approved expansion.",
        "review_artifacts": list(reviews),
    })
    figure_manifest = read(ROOT / "figures/FIGURE_MANIFEST.json")
    figure_manifest["visual_review"] = "pass_independent_actual_pdf_and_png_review"
    figure_manifest["review_artifact"] = "../review/FIGURE_VISUAL_REVIEW.json"
    figure_manifest["review_sha256"] = sha(ROOT / "review/FIGURE_VISUAL_REVIEW.json")
    write(ROOT / "figures/FIGURE_MANIFEST.json", figure_manifest)
    write(ROOT / "STATE.json", state)
    paths = ["RESULTS.md", "MANUSCRIPT_INSERT.md", "AGGREGATE_TABLES.md", "SUMMARY_STATS.json",
             "FIGURE_CAPTIONS.md", "SEED_INTERPRETATION_ADDENDUM.md", "STATE.json",
             "figures/primary_analyses.pdf", "figures/delivery_resources.pdf",
             "figures/FIGURE_MANIFEST.json", "review/REFERENCE_VALUE_RECONCILIATION.json", *reviews]
    write(ROOT / "REPORTING_CLOSURE.json", {
        "completed_utc": now,
        "scope": "Reporting closure only; no API calls, data generation or frozen-artifact changes",
        "frozen_artifacts_verified": {str(p.relative_to(PROJECT)): h for p, h in frozen.items()},
        "artifacts": {rel: {"bytes": (ROOT / rel).stat().st_size, "sha256": sha(ROOT / rel)} for rel in paths},
        "scientific_findings_preserved": ["one ideal-law divergent TC mean", "separate capped-law concern",
            "one HDL above TC row", "mixed scientific quality", "incidental PNS preview exposure",
            "no submitted scientific revisions", "no new independent target"],
    })
    print(json.dumps({"status": state["status"], "sessions": 12, "tables": 36, "known_usd": state["known_tariff_usd"]}))


if __name__ == "__main__":
    main()
