"""Render Figure 5 from frozen aggregates; copy the existing resplit supplement.

Run from any directory with Python and Matplotlib. This script never reads
individual records, imports a generator, refits a model or recalculates analyses.
The numeric binding records every plotted value and the exact source hashes.
Local work/ inputs and public reports/ inputs have separately pinned byte
profiles. Only the published real-real REPORT.json differs (JSON whitespace).
The public source package contains the resplit SVG but not its source PNG.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FuncFormatter

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PINNED_LOCAL = {
    "work/evidence_to_generation_2026-11-04/evaluation/REPORT.json":
        "2dfe84dca528adcc4edc6035b1f70ffbf13df72697ef82ac273344660824e2c6",
    "work/evidence_to_generation_2026-11-04/SENSITIVITY_REVIEW.json":
        "1680b49b947b64be5ccb8413b959845bb9e984982af0452b7c28b3e6081846ee",
    "work/evidence_to_generation_2026-11-04/evaluation/INDEPENDENT_NUMERICAL_REVIEW.md":
        "62e746642d522d178078871f842ecad040c277585e08b40ff206d69961a01909",
    "work/real_real_calibration_2026-11-04/REPORT.json":
        "bc836fd61973ca7ece74855b87c0064d3b07ecb37228316318099239460ca95f",
    "work/real_real_calibration_2026-11-04/REAL_REAL_CONTEXT.svg":
        "de98d52f3680af6167039e58a0eee8c3915d4c4df8deb2ee13b9a11c308a3335",
    "work/real_real_calibration_2026-11-04/REAL_REAL_CONTEXT.png":
        "20b47a2f72107e95b77fd9b50d95560f49a35234359fdba0659912e1889c481b",
}
PINNED_PUBLIC = {
    "reports/evidence_to_generation_2026-11-04/evaluation/REPORT.json":
        "2dfe84dca528adcc4edc6035b1f70ffbf13df72697ef82ac273344660824e2c6",
    "reports/evidence_to_generation_2026-11-04/SENSITIVITY_REVIEW.json":
        "1680b49b947b64be5ccb8413b959845bb9e984982af0452b7c28b3e6081846ee",
    "reports/evidence_to_generation_2026-11-04/evaluation/INDEPENDENT_NUMERICAL_REVIEW.md":
        "62e746642d522d178078871f842ecad040c277585e08b40ff206d69961a01909",
    "reports/real_real_calibration_2026-11-04/REPORT.json":
        "cfb05818b85792d12ad2ab63ae609b06516c6838e3bdfff6b2e380c403c136d0",
    "reports/real_real_calibration_2026-11-04/REAL_REAL_CONTEXT.svg":
        "de98d52f3680af6167039e58a0eee8c3915d4c4df8deb2ee13b9a11c308a3335",
}
BLUE = "#1678A6"
INK = "#243543"
GRAY = "#737D86"
ORANGE = "#B55A16"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def short_number(value, _position):
    if abs(value) < 1e-12:
        return "0"
    return f"{value:.3g}".replace("-", "−")


def main():
    # Do not fall back after a missing/mismatched local input: each profile is
    # closed and byte-pinned. Public rendering is selected only without work/.
    input_profile = "local_work" if (PROJECT / "work").is_dir() else "public_reports"
    input_root = "work" if input_profile == "local_work" else "reports"
    pinned = PINNED_LOCAL if input_profile == "local_work" else PINNED_PUBLIC
    for path, expected in pinned.items():
        actual = sha(PROJECT / path)
        if actual != expected:
            raise RuntimeError(f"Frozen input hash mismatch: {path}: {actual}")
    report = json.loads((PROJECT / f"{input_root}/evidence_to_generation_2026-11-04/evaluation/REPORT.json").read_text(encoding="utf-8"))
    sensitivity = json.loads((PROJECT / f"{input_root}/evidence_to_generation_2026-11-04/SENSITIVITY_REVIEW.json").read_text(encoding="utf-8"))
    slots = sorted((s for s in report["slots"] if s["stage"] == "final"), key=lambda s: s["seed"])
    assert [s["seed"] for s in slots] == [7401, 7402, 7403]
    assert all(s["status"] == "success" and s["aliased_initial"] for s in slots)
    assert len({s["table_sha256"] for s in slots}) == 3
    assert all(s["analysis"]["n"] == 3000 for s in slots)
    assert sensitivity["status"] == "PASS" and len(sensitivity["cases"]) == 2
    assert sensitivity["random_draws"] == 0 and not sensitivity["generator_executed"]

    matplotlib.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8.5,
        "axes.labelsize": 8.2, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.linewidth": .65, "svg.fonttype": "none", "pdf.fonttype": 42,
        "svg.hashsalt": "figure5-scientific-utility-v09-2026-11-04",
    })
    fig = plt.figure(figsize=(7.8, 8.0), facecolor="white")
    fig.text(.075, .973, "Evidence-guided data for requested scientific analyses",
             color=INK, fontsize=12, weight="bold", ha="left", va="top")
    fig.text(.075, .939, "One Agent-authored model · three fixed 3,000-person draws · exposed CHNS reference",
             color=GRAY, fontsize=8.5, ha="left", va="top")
    fig.text(.075, .896, "A", fontsize=12, weight="bold", color=INK)
    fig.text(.112, .897, "Primary: HbA1c (pp) ~ BMI + glucose + age + female", fontsize=9, weight="bold", color=INK)
    fig.text(.075, .601, "B", fontsize=12, weight="bold", color=INK)
    fig.text(.112, .602, "Prespecified secondary: HbA1c (pp) ~ BMI + age + female", fontsize=9, weight="bold", color=INK)
    fig.text(.075, .310, "C", fontsize=12, weight="bold", color=INK)
    fig.text(.112, .311, "Unreported joint dependence can change the conditional BMI effect",
             fontsize=9, weight="bold", color=INK)

    display = {
        "bmi": ("BMI", "per kg/m²"),
        "glucose": ("Glucose", "per mmol/L"),
        "age": ("Age", "per year"),
        "female": ("Female − male", "difference"),
    }
    coefficients = []
    for row, terms in enumerate((["bmi", "glucose", "age", "female"], ["bmi", "age", "female"])):
        source_key = "B" if row == 0 else "A"
        panel = "A" if row == 0 else "B"
        for col, term in enumerate(terms):
            ax = fig.add_axes([.09 + col*.23, .695 - row*.295, .18, .146])
            rc = report["reference"][source_key]["coefficients"][term]
            ax.axvspan(rc["lower"], rc["upper"], color="#DCE0E3", alpha=.88, zorder=0)
            ax.axvline(rc["value"], color=GRAY, lw=1.2, ls=(0, (3, 2)), zorder=1)
            ax.axvline(0, color="#BCC3C8", lw=.65, zorder=0)
            entries = []
            for y, slot in enumerate(slots):
                analysis = slot["analysis"] if row == 0 else slot["analysis"]["descriptive_secondary"]
                c = analysis["coefficients"][term]
                assert c["lower"] <= c["value"] <= c["upper"]
                ax.errorbar(c["value"], y,
                    xerr=[[c["value"]-c["lower"]], [c["upper"]-c["value"]]],
                    fmt="o", color=BLUE, capsize=2.6, ms=4.5, lw=1.1, zorder=3)
                entries.append({"seed": slot["seed"], "table_sha256": slot["table_sha256"],
                    "value": c["value"], "lower": c["lower"], "upper": c["upper"],
                    "standard_error": c["standard_error"], "stored_unit": c["unit"],
                    "source_locator": f"slots[stage=final,seed={slot['seed']}].analysis." +
                    ("" if row == 0 else "descriptive_secondary.") + f"coefficients.{term}"})
            ax.set_yticks(range(3), [str(s["seed"]) if col == 0 else "" for s in slots])
            if col == 0:
                ax.set_ylabel("Seed", labelpad=3)
            ax.set_ylim(2.55, -.55)
            ax.set_title(display[term][0], fontsize=9, loc="left", pad=7, color=INK)
            ax.set_xlabel(display[term][1], labelpad=4)
            ax.xaxis.set_major_locator(MaxNLocator(nbins=3, steps=[1, 2, 2.5, 5, 10]))
            ax.xaxis.set_major_formatter(FuncFormatter(short_number))
            ax.tick_params(axis="y", length=0)
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.spines["bottom"].set_color("#B1BAC1")
            coefficients.append({"panel": panel, "reference_analysis_key": source_key,
                "term": term, "reference": {k: rc[k] for k in ("value", "lower", "upper", "standard_error", "unit")},
                "reference_locator": f"reference.{source_key}.coefficients.{term}", "generated": entries})
    # The eighth small-panel cell explains the distinct interval meanings.
    leg = fig.add_axes([.78, .390, .20, .17])
    leg.axis("off")
    leg.text(0, 1, "REFERENCE", color=GRAY, fontsize=8, weight="bold", va="top")
    leg.text(0, .86, "Dashed line: estimate\nGray band: 95%\ncommunity-cluster interval",
             color=INK, fontsize=7.9, va="top", linespacing=1.35)
    leg.text(0, .46, "GENERATED DATA", color=BLUE, fontsize=8, weight="bold", va="top")
    leg.text(0, .32, "Dots: three fixed draws\nBars: conditional 95%\nHC3-t intervals",
             color=INK, fontsize=7.9, va="top", linespacing=1.35)

    # Plot only the two already reported analytic scenarios, with no interpolation.
    ax = fig.add_axes([.105, .106, .35, .151])
    points = []
    for case in sensitivity["cases"]:
        assert case["status"] == "PASS" and case["secondary_projection_unchanged"]
        rho = case["declared_latent_BMI_glucose"]
        value = case["primary"][case["primary_order"].index("bmi")]
        ax.plot(rho, value, marker="D", color=ORANGE, markersize=6, linestyle="none")
        ax.annotate(f"{value:+.5f}".replace("-", "−"), (rho, value),
            xytext=(0, 10 if value > 0 else -17), textcoords="offset points",
            ha="center", fontsize=9, color=ORANGE, weight="bold")
        points.append({"latent_bmi_glucose_correlation": rho, "primary_bmi_coefficient": value,
            "secondary_bmi_coefficient": case["secondary"][case["secondary_order"].index("bmi")],
            "source_locator": f"cases[declared_latent_BMI_glucose={rho}].primary[primary_order=bmi]"})
    ax.axhline(0, color="#B4BCC3", lw=.8)
    ax.set_xlim(.04, .46)
    ax.set_ylim(-.029, .053)
    ax.set_xticks([.1, .4], ["0.10", "0.40"])
    ax.set_yticks([-.02, 0, .02, .04])
    ax.yaxis.set_major_formatter(FuncFormatter(short_number))
    ax.set_xlabel("Assumed latent BMI–glucose correlation", labelpad=5)
    ax.set_ylabel("Conditional BMI coefficient\n(HbA1c pp per kg/m²)", fontsize=8.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#B1BAC1")
    fig.text(.525, .263,
        "Two prespecified analytical scenarios",
        fontsize=9, weight="bold", color=ORANGE, va="top")
    fig.text(.525, .232,
        "Only BMI–glucose dependence changes.\n"
        "All marginal laws and every other bivariate\n"
        "law remain fixed; the secondary regression\n"
        "is unchanged.\n\n"
        "The delivered model used 0.25, an explicit\n"
        "assumption. These are not new data draws\n"
        "or calibrated uncertainty bounds.",
        fontsize=8.6, color=INK, va="top", linespacing=1.43)
    fig.text(.075, .023,
        "Developmental analysis, not equivalence. Generated intervals condition on the fixed model;\n"
        "they omit source, structural and transport uncertainty. Real-sample resplit context is shown separately.",
        fontsize=8.2, color=GRAY, va="bottom", linespacing=1.35)
    assert len(coefficients) == 7 and sum(len(x["generated"]) for x in coefficients) == 21
    assert [p["latent_bmi_glucose_correlation"] for p in points] == [.1, .4]

    stem = HERE / "figure5_agent_scientific_utility"
    fig.savefig(stem.with_suffix(".svg"), metadata={"Date": None, "Creator": "render_figure5.py; frozen aggregates"})
    fig.savefig(stem.with_suffix(".png"), dpi=300, metadata={"Software": "Matplotlib; frozen aggregate redraw"})
    fig.savefig(stem.with_suffix(".pdf"), metadata={"CreationDate": None, "ModDate": None,
        "Title": "Figure 5. Evidence-guided data for requested scientific analyses", "Creator": "render_figure5.py"})
    plt.close(fig)

    supplements = []
    supplement_extensions = ("svg", "png") if input_profile == "local_work" else ("svg",)
    for ext in supplement_extensions:
        source = PROJECT / f"{input_root}/real_real_calibration_2026-11-04/REAL_REAL_CONTEXT.{ext}"
        target = HERE / f"supplement_real_real_context.{ext}"
        shutil.copyfile(source, target)
        assert sha(source) == sha(target)
        supplements.append({"source": source.relative_to(PROJECT).as_posix(), "copy": target.name,
            "sha256": sha(target), "operation": "byte-identical copy; all seven prespecified nonintercept effects"})

    binding = {
        "schema": "figure5_aggregate_value_binding_v1",
        "production_identity": "New graphic of frozen aggregate coefficients and precomputed analytical sensitivity; existing resplit figure copied unchanged",
        "input_profile": input_profile,
        "input_sha256": pinned,
        "accepted_input_profiles": {"local_work": PINNED_LOCAL, "public_reports": PINNED_PUBLIC},
        "byte_variant_note": "The public real_real_calibration REPORT.json differs only in insignificant JSON whitespace; all parsed values and all other common input bytes are identical. Each profile has its own exact byte pins; arbitrary variants are rejected.",
        "script_sha256": sha(Path(__file__)),
        "matplotlib_version": matplotlib.__version__,
        "individual_records_read": False, "generator_executed": False, "statistical_analysis_rerun": False,
        "selection": {"stage": "final", "seeds": [7401, 7402, 7403], "unique_delivered_tables": 3,
            "model_constructions": 1, "rows_per_table": 3000, "all_nonintercept_effects": 7,
            "reference_n": report["reference"]["B"]["n"], "reference_clusters": report["reference"]["B"]["cluster_count"]},
        "coefficient_bindings": coefficients,
        "sensitivity_bindings": points,
        "delivered_model_latent_correlation": sensitivity["baseline_latent_BMI_glucose"],
        "sensitivity_display": "Two precomputed points only; no connecting curve, new calculations, new draws or intervals",
        "reference_interval_meaning": "95% CHNS community-cluster CR1-t, exposed selected sample",
        "generated_interval_meaning": "95% HC3-t, conditional on fixed generated law and draw; not source/structural/transport uncertainty",
        "supplement": supplements,
        "supplement_png_status": "Copied from pinned local source" if input_profile == "local_work" else
            "Not copied: the public source package distributes only the resplit SVG; no source PNG is attached to that input profile. A pre-existing output PNG, if any, is not regenerated or validated by this public run.",
        "output_sha256": {stem.with_suffix(ext).name: sha(stem.with_suffix(ext)) for ext in (".svg", ".png", ".pdf")},
    }
    (HERE / "figure5_input_and_value_bindings.json").write_text(json.dumps(binding, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"figure": stem.name, "coefficient_panels": len(coefficients), "generated_estimates": 21,
        "analytic_scenarios": len(points), "supplement_copies": len(supplements), "input_profile": input_profile,
        "input_hashes_verified": len(pinned), "supplement_png_status": binding["supplement_png_status"]}, indent=2))


if __name__ == "__main__":
    main()
