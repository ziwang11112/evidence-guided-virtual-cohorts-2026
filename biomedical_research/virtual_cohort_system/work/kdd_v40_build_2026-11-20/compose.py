"""Prepare the manuscript from the preceding edition and the recorded experiment results."""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/"manuscript/kdd_draft_v39_2026-11-20";NEW=ROOT/"manuscript/kdd_draft_v40_2026-11-20"
work=ROOT/"work/nonhdl_external_2026-11-20"
def read(p):return json.loads(p.read_text(encoding="utf8"))
def movefig(text,label):
    pattern=r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}"
    fig,=[m for m in re.findall(pattern,text,re.S) if "\\label{"+label+"}" in m]
    return text.replace(fig,""),fig
def seg(text,left,right,replace):
    a=text.index(left);b=text.index(right,a+len(left))
    return text[:a]+replace+"\n\n"+text[b:]
def write(p,s):p.write_text(s,encoding="utf8",newline="\n")
def main():
    main=(OLD/"main.tex").read_text(encoding="utf8")
    app=(OLD/"appendix.tex").read_text(encoding="utf8")
    main,support=movefig(main,"fig:support")
    main,revision=movefig(main,"fig:revision")
    app=app.replace(r"\label{app:profiles}",r"\label{app:profiles}"+"\n"+support,1)
    app=app.replace(r"\label{app:chns}",r"\label{app:chns}"+"\n"+revision,1)
    app=app.replace(r"width=.96\textwidth]{figures/original-paper",r"width=.85\textwidth]{figures/original-paper")
    app=app.replace(r"width=.94\textwidth]{figures/freetown",r"width=.84\textwidth]{figures/freetown")
    main=seg(main,r"\caption{Where a generated association comes from.",r"\label{fig:method}",r"""\caption{From a published summary to paired virtual records. (A) Collapsing the iron-status groups in Zhu et al.~\cite{zhu} yields four counts and a crude anemia odds ratio (OR) of 6.65 for low versus higher ferritin. (B) The lines illustrate two ways of assigning the same five ferritin values to the same five hemoglobin values in one threshold cell. Either assignment preserves the cell count. (C) Seven programs that passed the source checks produced similar threshold ORs and a wide range of continuous Spearman correlations. Each dot is one program. The orange mark gives the source OR. The models see the reported band summaries as well as the counts.}
\Description{A two-by-two table implies an odds ratio of 6.65. Two illustrative matchings preserve the values assigned to the cell. Seven real program outputs give odds ratios from 6.55 to 6.86 and continuous correlations from minus 0.272 to 0.446.}""")
    main=seg(main,"A study in rural northern China",r"\section{From a research request",r"""A researcher wants to compare urban and pastoralist adults after adjusting for age and sex. She has a paper describing both groups, but she cannot obtain its individual records. A scientific agent can read the reported summaries and generate a table with one row per person. Can she use that table for the same BMI and cholesterol regressions she would have run on measured records? An error of one unit has a different meaning across the two outcomes. Even two samples of real participants can return different estimates.

The scientific choice is clearest when a study reports two measurements in groups. A paper on anemia in northern China tabulates iron, folate and vitamin B$_{12}$ status~\cite{zhu}. Four collapsed counts already determine the source odds ratio for low hemoglobin and low ferritin. They leave open which continuous ferritin value belongs with each hemoglobin value inside a cell. That choice can change a rank correlation while preserving every count (Figure~\ref{fig:method}). A further question arises when a researcher applies that choice to another population.

Previous work generates synthetic cohorts from shared fitted models, aggregate statistics, trial curves and published covariates~\cite{filshtein,llmsynthor,synthipd,kmgen}. We evaluate one requested analysis in one population at a time. Its unit of evaluation is a scientific estimate, such as an adjusted group contrast or the proportion crossing a laboratory threshold. Our three contributions follow that estimate from the paper into the data.
\begin{enumerate}
\item \textbf{Trace what the source determines.} We link each reported number and its arithmetic implications to the measurement, population and role it has in the executable generator.
\item \textbf{Isolate the agent's pairing decision.} Holding the supplied values and threshold counts fixed, we change which measurements share a virtual person and recompute the same analysis. The threshold odds stay fixed while a continuous association can move.
\item \textbf{Test a stated scientific use.} We run the same estimator on virtual and measured records, compare discrepancies with variation between real resamples, and prospectively test the same frozen lipid tables in two independently recruited samples.
\end{enumerate}""")
    start=main.index(r"\section{How large is the gap")
    end=main.index(r"\section{Related work}",start)
    main=main[:start]+main[end:]
    life=r"""\section{Re-running the published lifestyle analysis}
\label{sec:lifestyle}
Lea et al. compared lifestyle groups among Turkana adults in Kenya~\cite{lea,leadata}. Two agents independently wrote generators from the study evidence, each yielding three tables with age, sex, lifestyle, BMI and blood lipids. We reimplemented the age- and sex-adjusted contrasts once and changed only the input table. This is same-study reconstruction: the publication and measured reference describe the same study. Published group information is available to the agent.

\begin{figure*}[t]
\centering
\includegraphics[width=.91\textwidth]{figures/lifestyle-main.pdf}
\caption{How large is a discrepancy between two analyses? Each curve gives the fraction of 500 matched resamples with an effect difference at or below the horizontal value. The dashed line compares two real resamples. Blue compares virtual with real; the solid curve is the pointwise median and the band spans six fixed virtual tables from two constructors. In (A) urban BMI discrepancies are on the scale seen between real resamples. In (B) the virtual rural cholesterol contrasts tend to be smaller. Appendix Figure~\ref{fig:lifestyle} and Table~\ref{tab:lifestyle} retain all nine comparisons.}
\Description{Cumulative curves overlap for the urban versus pastoralist BMI contrast. The virtual-versus-real curves shift left for rural versus pastoralist total cholesterol.}
\label{fig:lifestyle-main}
\end{figure*}

In each of 500 repetitions we drew two real samples and one sample from each virtual table, with the same size and sex-by-lifestyle composition for each trait. For urban versus pastoralist BMI, real resamples differed by 0.316 kg/m$^2$ on average in absolute value. Virtual--real discrepancies ranged from 0.314 to 0.428 kg/m$^2$ (Figure~\ref{fig:lifestyle-main}A). For rural versus pastoralist total cholesterol, generated data understated the adjusted effect by 7.80--9.54 mg/dL on average (B). The corresponding HDL effects were low by 4.07--6.21 mg/dL. Total and HDL cholesterol SDs in the measured sample were 42.81 and 20.23 mg/dL; virtual resampling gave 31.49--32.67 and 14.50--14.89. The urban BMI analysis is supported as a rehearsal at this scale. The same tables would understate lipid variability in a study-planning calculation. These resamples describe one study and do not establish equivalence in a new population.
"""
    main=main.replace(r"\section{Can the agent model what the paper reports?}",life+"\n"+r"\section{Can the agent model what the paper reports?}",1)
    main=main.replace(r"(Figure~\ref{fig:method}D)",r"(Appendix Figure~\ref{fig:akwa-heat})")
    app+=r"""
\begin{figure*}[t]
\centering
\includegraphics[width=.82\textwidth]{figures/akwa-heat.pdf}
\caption{Continuous ranks in Akwa Ibom, shown after outcome disclosure. Each cell gives the percentage in the specified ferritin quartile within a hemoglobin quartile. Quartiles are formed separately in the measured sample and each virtual law. The first prespecified agent is shown; all six have identical counts at this resolution. The odds ratios use absolute clinical cutoffs.}
\Description{Among mothers in the lowest hemoglobin quartile, the measured fraction also in the lowest ferritin quartile is 27.2 percent, compared with 48.0 and 48.1 percent in the virtual cohorts.}
\label{fig:akwa-heat}
\end{figure*}

\section{Audit of the two lipid comparisons}
\label{app:nonhdl}
The source sample was nonfasting. Mekelle used a Bio-system A25 and Haramaya a Mindray BS-200 on fasting samples. Neither cohort supplied measurements to either constructor. No reference rows were shared between the independently recruited study frames to our knowledge. The project used only the packet and no individual source records. The source mean ratio is the mean of individual ratios. For common lognormal margins, fitting the TC upper-cutoff probability allows two positive log SDs; we fixed the smaller one before generation. Each method used three seeds with 16,000 pairs per seed. Across the 48,000 records per method, HDL exceeded TC in 56 agent and 47 statistical pairs. The measured counts were zero in Mekelle and seven in Haramaya. All were retained as specified. These scientific outputs were computed after explicitly repairing the metadata interface; the raw automation had zero successful agent draws.

We resampled individuals 2,000 times within age groups 20--39 and 40 or older in each study. The 95\% intervals for the sample means were 120.19--130.00 and 120.96--126.27 mg/dL. The corresponding intervals for the fractions above or at the cutoff were 16.82--25.55\% and 18.64--23.20\%. Intervals condition on the observed age composition and frozen generators. They omit uncertainty in the original Tanzanian estimates and do not generalize the samples to the country. Among all possible permutations of the supplied empirical marginal arrays, 9.02--41.54\% can cross the threshold if no source ratio or physiological constraint is imposed. This is an outer diagnostic range for the source-constrained problem. It does not identify which assumption caused the external discrepancies.
"""
    main=main.replace("Both approaches substantially overestimated the measured associations there.","Both approaches substantially overestimated the measured associations there. The Nigerian comparison also introduced an extra source contrast, fresh constructors and a different statistical comparator. The two experiments cannot isolate a country effect.")
    main=main.replace("It evaluates a single GPT configuration, one pair of biomarkers and unweighted measurements in one additional population.","That iron comparison evaluates one GPT configuration and unweighted measurements in one additional population.")
    main=main.replace("Three uses have different levels of support.","The lifestyle example shows that a useful adjusted BMI contrast can coexist with insufficient lipid variation on the same tables. In the Ethiopian comparisons, the mean non-HDL value was available directly from source arithmetic. The threshold fraction required a joint law, yet two independently chosen implementations agreed and both overestimated the measured fraction. Agreement between constructors gives little information about transport when they share the same modeling assumptions.")
    if (work/"VERIFICATION.json").exists():
        middle=(Path(__file__).parent/"lipid-section.tex").read_text(encoding="utf8")
        main=main.replace(r"\section{Related work}",middle+"\n"+r"\section{Related work}",1)
        abstract=(Path(__file__).parent/"abstract.tex").read_text(encoding="utf8").strip()
        main=seg(main,r"\begin{abstract}",r"\end{abstract}",r"\begin{abstract}"+"\n"+abstract)
    write(NEW/"main.tex",main);write(NEW/"appendix.tex",app)
if __name__=="__main__":main()
