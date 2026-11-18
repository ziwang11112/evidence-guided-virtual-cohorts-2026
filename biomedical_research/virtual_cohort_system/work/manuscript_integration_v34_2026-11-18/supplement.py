"""Retain the earlier full results and append new aggregate-only tables."""
from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "manuscript"
OLD = M / "DRAFT_v0_33.md"
DRAFT = M / "DRAFT_v0_34.md"
P0 = ROOT / "work/matched_size_utility_2026-11-17"
P1 = ROOT / "work/original_paper_capability_2026-11-17"
def span(series):
    return f"{series.min():.3f} to {series.max():.3f}"

def matched():
    out = ["### S7. Equal-size analysis of all lifestyle contrasts",
           "Table S7 retains the sign and size of every discrepancy from the same regression. For each trait, resampling preserved the six observed lifestyle-by-sex counts. The empirical difference is the adjusted contrast in the first resample minus the contrast in real B. A range across tables spans six saved tables from two Agent sessions.",
           "**Table S7. Matched lifestyle comparisons. Signed and absolute differences are means across 500 repetitions per table. BMI is in kg/m² and both lipid outcomes are in mg/dL.**"]
    rows = ["| Trait and contrast | Real–real mean absolute | Virtual–real mean absolute | Virtual–real mean signed |",
            "|---|---|---|---|"]
    df = pd.read_csv(P0 / "CONTRAST_SUMMARIES.csv")
    labels = {"rural_minus_pastoralist": "rural − pastoralist", "urban_minus_pastoralist": "urban − pastoralist",
              "urban_minus_rural": "urban − rural"}
    for t,name in [("bmi","BMI"), ("total_cholesterol","TC"), ("hdl_cholesterol","HDL")]:
        for c,label in labels.items():
            d = df[(df.trait == t) & (df.contrast == c)]
            v = d[d.comparison != "real_real"]
            r = d[d.comparison == "real_real"].iloc[0]
            assert len(v) == 6 and d.signed_n.eq(500).all()
            rows.append(f"| {name}, {label} | {r.absolute_mean:.3f} | {span(v.absolute_mean)} | {span(v.signed_mean)} |")
    out += ["\n".join(rows), "Measured urban lipid subsamples were small. Matching their sizes and composition helps interpret discrepancies for those contrasts, while the rural lipid effects are systematically smaller. Household structure, measurement selection and source-to-target variation are outside this conditional bootstrap.",
            "![Matched resample standard deviations for BMI, total cholesterol and HDL cholesterol.](../work/matched_size_utility_2026-11-17/figures/matched_dispersion.svg)",
            "**Figure S2. Dispersion of all six saved lifestyle tables under the same matched resampling.** Each panel compares real B resamples with all six virtual tables. The annotated original sample SD is the measured-sample reference. The thin and thick lines span the middle 95% and 50% of 500 resamples and the dot is the median. Both lipid SDs remain too small for variance-dependent applications.",
            "All 12,000 planned trait fits completed. A separately implemented centered-age QR regression reproduced 372 checked numerical fields to within 4.05 × 10⁻¹³. The [matched-size study record](../work/matched_size_utility_2026-11-17/RESULTS.md) binds the complete data summaries, protocol and numerical review."]
    return "\n\n".join(out)

def authors():
    out = ["### S8. Original-paper construction and generated analyses",
           "Fresh constructors read the original Jaspert or Zhu article and could search for additional sources. They ran one trial on virtual data, kept the submitted law, and used the same three final seeds (17121, 17123 and 17127). The six models produced 3,000 rows per draw for blood pressure and 5,000 for iron status. Model calls by constructor were 28, 25 and 23 for pressure and 21, 22 and 23 for iron. The tariff estimate was USD 1.5113403 and includes all 142 model calls.",
           "**Table S8. Complete original-paper results. Each Agent entry is the mean of three seeded analyses. Percentages use a 0–100 scale. Pressure slopes are mmHg per five kg/m² BMI and SDs are mmHg.**"]
    rows = ["| Scientific analysis | Agent 1 | Agent 2 | Agent 3 | Measured sample |","|---|---|---|---|---|"]
    spec = [("bmi_sbp","BMI–systolic slope",1), ("bmi_dbp","BMI–diastolic slope",1),
            ("residual_correlation","SBP–DBP residual r",1), ("sbp.sd_population","Systolic SD",1),
            ("dbp.sd_population","Diastolic SD",1), ("sbp_below_dbp_fraction","SBP below DBP (%)",100),
            ("odds_ratio","Anemia–iron depletion OR",1), ("joint_prevalence","Both markers low (%)",100),
            ("spearman","Hb–ferritin Spearman r",1), ("low_hb_fraction","Low hemoglobin (%)",100),
            ("low_ferritin_fraction","Low ferritin (%)",100)]
    df = pd.read_csv(P1 / "analysis/author_results.csv")
    for key,name,scale in spec:
        d = df[df.estimand == key].sort_values("episode_id")
        assert len(d) == 3 and d.available_seeds.eq(3).all() and d.reference.nunique() == 1
        vals = [*d.seed_mean, d.reference.iloc[0]]
        rows.append("| " + name + " | " + " | ".join(f"{x*scale:.3f}" for x in vals) + " |")
    out += ["\n".join(rows), "For pressure the reference uses weighted PNS measurements in adults aged 20–79. We fit both outcomes on an intercept, age, sex and BMI and take the Pearson correlation of the two residuals. Generated draws have equal weights. The age/BMI source projection lacks the sex adjustment of the target estimand. For iron we use the phlebotomy weights in the measured NHANES sample of nonpregnant women aged 20–44 and the same threshold and rank operators for synthetic draws. The published Chinese sample includes selected rural women after childbirth. Applying its deficiency association to this target is a transport assumption.",
            "The PNS A2 source preview identified the target-family survey and reported demographics and a qualitative topic. The constructor excluded the preview and did not open the paper. It had not been shown the requested reference estimates. We retained all sessions. A [source-to-program audit](../work/original_paper_capability_2026-11-17/SOURCE_MODEL_AUDIT.md) documents the adopted and excluded evidence. The [experiment record](../work/original_paper_capability_2026-11-17/RESULTS.md) links all 99 seed-level estimates. The separate numerical reimplementation checks execution and analysis within this project."]
    return "\n\n".join(out)

if __name__ == "__main__":
    assert hashlib.sha256(OLD.read_bytes()).hexdigest() == "20ae7f87682a422db3e7c7af6b66962956634be861eb75789b340722130eeb3c"
    main = DRAFT.read_text(encoding="utf-8").split("\n## References",1)[0].rstrip()
    historic = OLD.read_text(encoding="utf-8").split("\n## References",1)[1].strip()
    historic = historic.replace("Figure 4 plots all five scientific metrics rather than only the primary gain.", "Table S3 gives both pressure slopes, their residual correlation and both SDs.")
    historic = historic.replace("Points, draw ranges and reference lines have the same interpretation as Figure 4.", "Points are construction means, ranges span three seeded draws and dashed lines are measured-sample estimates.")
    historic = historic.replace("Complete pns profile", "Complete PNS profile")
    historic = historic.replace(" Publication beyond this preprint was not established in the positioning audit.", "")
    historic = historic.replace(" Original Tables I and IV provide the admitted iron evidence.", "")
    historic = historic.replace(" Published September 2024; documentation checked 17 November 2026.", "")

    DRAFT.write_text(main + "\n\n## References\n\n" + historic + "\n\n" + matched() + "\n\n" + authors() + "\n", encoding="utf-8")
