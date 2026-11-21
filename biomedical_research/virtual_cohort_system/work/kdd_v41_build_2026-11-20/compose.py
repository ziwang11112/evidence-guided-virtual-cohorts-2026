"""Prepare v0.41 from versioned v0.40 source and reviewed, aggregate-only figures."""
from pathlib import Path
import re
import shutil

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parents[1]
OLD = ROOT / "manuscript/kdd_draft_v40_2026-11-20"
NEW = ROOT / "manuscript/kdd_draft_v41_2026-11-20"
EVIDENCE = ROOT / "work/kdd_v40_pairing_review_2026-11-20"
OLD_BUILD = BUILD.parent / "kdd_v40_build_2026-11-20"


def save(file, content):
    file.write_text(content, encoding="utf-8", newline="\n")


def replace_once(s, before, after):
    if s.count(before) != 1:
        raise ValueError(f"Expected one occurrence of {before[:85]!r}")
    return s.replace(before, after)


def main():
    (NEW / "figures").mkdir(exist_ok=True, parents=True)
    main_text = (OLD / "main.tex").read_text(encoding="utf-8")
    abstract = r"""Researchers often have published summaries but lack paired measurements for a new analysis. We study agents that read a paper, choose how to pair measurements in a virtual person, and write a reusable sampling program. We evaluate each scientific analysis on virtual and measured records, then isolate the contribution of pairing. In a Kenyan lifestyle study, virtual records recovered the adjusted urban BMI contrast about as closely as two real resamples did. Reassigning age within lifestyle and sex groups changed that virtual contrast by at most 0.0111 kg/m$^2$. In Chinese iron-status data, retaining each of six agents' biomarker pairings improved agreement with a held-out rank correlation over within-band re-pairing. The threshold odds ratio stayed fixed. In lipids, an agent and a statistical generator predicted nearly identical screening rates (25.53\% and 25.52\%); two Ethiopian samples gave 21.18\% and 20.96\%. When asked for alternatives, four fresh agent sessions each produced two pairings that met the same source constraints and changed the screening rate by 16.37--29.35 percentage points. These comparisons locate which conclusions depend on the agent's model and where paired measurements can test those choices."""
    i = main_text.index(r"\begin{abstract}") + len(r"\begin{abstract}")
    j = main_text.index(r"\end{abstract}")
    main_text = main_text[:i] + "\n" + abstract + "\n" + main_text[j:]
    main_text = replace_once(main_text,
        "Holding the supplied values and threshold counts fixed, we change which measurements share a virtual person and recompute the same analysis. The threshold odds stay fixed while a continuous association can move.",
        "We alter which measurements share a person, hold their values fixed, and recompute the same analysis. We also give independent agents a source paper's lipid summaries and ask each for two executable models. Their screening rates quantify the consequences of their own modeling choices.")
    location = "Its size is relative to the measured estimate on this split."
    main_text = replace_once(main_text, location, location + r"""

\begin{figure*}[t]
\centering
\includegraphics[width=.94\textwidth]{figures/pairing-attribution.pdf}
\caption{How much of an analysis comes from the agent's pairing? (A) Each line follows one CHNS law from the expected correlation after randomly re-pairing within Hb bands to its authored value. The dotted line and shading show the measured correlation and its 95\% interval. (B) In the lifestyle case, age was re-paired with the intact biomarker vector within sex and lifestyle groups. The cells show the largest absolute change over all six virtual tables as a percentage of the mean absolute difference between two real resamples for that regression. These are retrospective within-table comparisons.}
\Description{All six authored iron correlations lie closer to the measured sample than their re-paired counterparts. The largest age-pairing shift for the nine lifestyle regressions ranges from 0.3 to 16.2 percent of the corresponding real resampling discrepancy.}
\label{fig:attribution}
\end{figure*}

The lifestyle example provides a comparison where pairing did little (Figure~\ref{fig:attribution}B). In each of its six virtual tables, we kept every outcome vector and randomly reassigned it among participants in the same lifestyle and sex group. The expected age-adjusted urban--pastoralist BMI contrast moved by only 0.0025--0.0110 kg/m$^2$. The real--real mean absolute difference was 0.316. The group structure already supplied most of this particular contrast. Across all nine regressions the largest shift reached 16.2\% of the corresponding real--real difference. Appendix~\ref{app:pairingtest} gives the calculation.""")
    main_text = replace_once(main_text, r"\includegraphics[width=.91\textwidth]{figures/nonhdl-two-cohorts.pdf}",
                              r"\includegraphics[width=.94\textwidth]{figures/nonhdl-selection.pdf}")
    original = next(line for line in main_text.splitlines() if line.startswith(r"\caption{The same virtual lipid"))
    main_text = replace_once(main_text, original, r"""\caption{What can a lipid screening study infer from the source? (A) A frozen agent and a statistical model independently selected similar joint laws. Diamonds and 95\% stratified bootstrap intervals summarize the two measured samples. (B) Four fresh authors received the same source summaries and were explicitly asked for two different, admissible joint models. Each line connects the pooled screening estimates for one author. The dashed segment joins two independently constructed numerical examples. The scenarios measure sensitivity at source.}""")
    main_text = replace_once(main_text,
        r"\Description{For Mekelle and Haramaya the generated mean is 128.77 mg/dL, compared with measured means of 125.12 and 123.58. The virtual threshold percentages are 25.53 and 25.52, compared with 21.18 and 20.96 measured.}",
        r"\Description{The original agent and comparator place about a quarter above the cutoff. In the separate experiment all four agents construct pairs of admissible models whose screening fractions differ by more than 16 percentage points.}")
    main_text = replace_once(main_text, r"3.65 above the Mekelle estimate and 5.19 above Haramaya (Figure~\ref{fig:nonhdl}A)",
                             r"compared with measured means of 125.12 in Mekelle and 123.58 in Haramaya")
    main_text = replace_once(main_text, r"25.52\% for the statistical generator.", r"25.52\% for the statistical generator (Figure~\ref{fig:nonhdl}A).")
    main_text = replace_once(main_text, r"\section{Related work}", r"""\paragraph{Can the agent construct the alternative?}
Four fresh GPT sessions each wrote a program for two pairings using only the same source packet and fixed marginal values. They knew the requested analysis and saw neither the Ethiopian estimates nor the numerical comparator. We sealed all programs before execution, used three fixed seeds per scenario, and independently recomputed the checks. All 24 tables retained the exact marginal arrays, placed HDL at or below TC for every virtual person, and reproduced the reported mean individual ratio to within 0.00020. The non-HDL mean stayed at 128.77. Each author's two screening rates differed by 16.37--29.35 percentage points (Figure~\ref{fig:nonhdl}B). One calibrated opposite rank cycles to the same ratio. The other three used swaps guided by the screening threshold. A numerical assignment procedure found admissible examples at 9.38\% and 41.41\%. Their spread shows why the original agreement at 25.5\% supplies little evidence about which estimate to use. These deliberately different model pairs establish feasibility. Their frequency in a patient population remains unknown (Appendix~\ref{app:pairingtest}).

\section{Related work}""")
    main_text = replace_once(main_text, r"has a long history~\cite{bounds}", r"has a long history, including distributional bounds with fixed margins and additional constraints~\cite{bounds,makarov,zaev}")
    main_text = replace_once(main_text,
        "Generalization across populations or agent models, individual-level prediction and clinical use remain open.",
        "The four new lipid sessions used the same GPT configuration. Each was explicitly asked for alternatives. The next test is whether a pre-disclosure decision about using a virtual analysis predicts external agreement within a researcher-defined tolerance. That test requires a newly held-out sample and a same-information statistical comparator allowed to express uncertainty.")
    appendix = (OLD / "appendix.tex").read_text(encoding="utf-8") + r"""
\section{Auditing pairing decisions on frozen tables}
\label{app:pairingtest}
\paragraph{Lifestyle.} We examined all nine age- and sex-adjusted contrasts on each of the six existing tables. Conditional on the design matrix, an OLS contrast is linear in the outcomes. Under uniform joint permutation of the outcome vectors within each lifestyle-by-sex cell, its expected coefficient equals the coefficient obtained by substituting the cell means. We verified the expectation using centered within-cell covariances and exhaustive permutations on a small fixture. Real--real discrepancies are the archived mean absolute differences at matched sample size. The nine real effects were already known when this ablation was defined. The comparison measures how much this particular age pairing affected the estimate.

\paragraph{Lipids.} The protocol, source-only request, scorer, interface and budget were sealed before the four new calls. Each author received one call and had to supply a program with two scenarios. We then sealed all four programs before executing any. Each scenario used the same three ordered seeds and 16,000 observations per seed. Mean individual TC/HDL had to be within 0.02 of 3.66 on every seed and round to 3.66 in the pool. All clinical ordering constraints had to hold. Material sensitivity required a pooled difference exceeding four percentage points and a difference in the same direction exceeding two points on every seed. All four sessions met this criterion on the first call. Each marginal array had 14.4\% above the source TC cutoff and 15.3\% below the source HDL cutoff. The tariff estimate for four calls was US\$0.231. The observed seed spread measures simulation variability within a particular model pair.

\begin{figure*}[t]
\centering
\includegraphics[width=.91\textwidth]{figures/lipid-rank-maps.pdf}
\caption{Two ways of assigning the same HDL measurements to the same total cholesterol measurements. The panels show all four authors on the first predeclared seed. Bin intensity is relative to independent rank pairing, on a common scale capped at four. Pairs below the orange curve have non-HDL at or above 160 mg/dL. Insets give the proportion from each complete draw. Author 2's rank cycles illustrate how a model can match the source ratio while imposing a distinctive joint structure.}
\Description{Eight rank density maps share the same axes. Orange curves mark the screening threshold. Opposite rank cycles are particularly visible for author two.}
\label{fig:lipidmaps}
\end{figure*}

The constructive control partitions the fixed order statistics into 125 interleaved blocks of 128. Linear assignment within each block supplies admissible permutations. Integer programming selects one per block while constraining the pooled ratio. Direct calculation on the full tables verified the two solutions. The 32.03-point spread is 98.5\% of the width of the unrestricted empirical bounds of 9.02--41.54\%. We establish two feasible points under the added conditions. The source summaries and the numerical test do not assign probabilities to the models in Figure~\ref{fig:lipidmaps}. Neither this separate four-author test nor the constructive control used another measured cohort.
"""
    appendix = appendix.replace("\n \n", "\n\n")
    bib = (OLD / "references.bib").read_text(encoding="utf-8") + r"""
@article{makarov,
  author = {Makarov, G. D.},
  title = {Estimates for the Distribution Function of a Sum of Two Random Variables When the Marginal Distributions Are Fixed},
  journal = {Theory of Probability and Its Applications}, volume = {26}, number = {4},
  pages = {803--806}, year = {1982}, doi = {10.1137/1126086}
}
@article{zaev,
  author = {Zaev, Danila},
  title = {On the {Monge--Kantorovich} Problem with Additional Linear Constraints},
  journal = {Mathematical Notes}, year = {2015}, volume = {98}, pages = {725--741},
  url = {https://arxiv.org/abs/1404.4962}
}
"""
    for name, s in (("main.tex", main_text), ("appendix.tex", appendix), ("references.bib", bib)):
        save(NEW / name, s)
    for name in re.findall(r"\\includegraphics\[[^]]+\]\{figures/([^}]+)\}", main_text + appendix) + ["evidence-and-pairing.drawio"]:
        path = EVIDENCE / "figures" / name
        shutil.copy2(path if path.exists() else OLD / "figures" / name, NEW / "figures" / name)
    wrapper = (OLD / "external_review.tex").read_text(encoding="utf-8").replace("v0.40", "v0.41")
    old_new = [
        ("b69c95b298497e8d5d6c078779a8ca636c4ad5eb", "e6c4ba2e6e737cdf619d76562611061a942a9979"),
        ("8a344e4d342940551003514a3cb190e3f8a4e32e", "f1a852204fb2fe3766f16d1b50313493ed2e1aa9"),
        ("5802057fc703260f965a1d455c7aa87f0a6c3790", "c9d60941af00dcd0a48ab451ac2f5cb550e9a2d8"),
        ("work/nonhdl_external_2026-11-20/", "work/kdd_v40_pairing_review_2026-11-20/"),
        ("MODEL_CLOSURE.json", "AUTHORS.json"), ("RESULTS.md", "REVIEW.md")]
    for old, new in old_new:
        wrapper = wrapper.replace(old, new)
    save(NEW / "external_review.tex", wrapper)
    for script in ("build_release.py", "external_release.py"):
        s = (OLD_BUILD / script).read_text(encoding="utf-8").replace("v40", "v41").replace("0.40", "0.41")
        if script == "build_release.py":
            s = s.replace("== 13", "== 15").replace("len(fig_pages)==10", "len(fig_pages)==12")
            s = s.replace("len(table_pages) in (6,7)", "len(table_pages)==7")
            s = s.replace("refs<=9", "refs<=8").replace("for i in (1,2,3)", "for i in (1,2,3,4)")
            s = s.replace('"nonhdl-two-cohorts"', '"pairing-attribution","nonhdl-selection","lipid-rank-maps"')
            s = s.replace("reproducibility/check_v41.py", "work/kdd_v40_pairing_review_2026-11-20/public_check.py")
        save(BUILD / script, s)

if __name__ == "__main__":
    main()
