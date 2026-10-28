"""Write the declared initial model and evidence ledger within this run only."""
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
OUT = RUN / 'initial'
OUT.mkdir(exist_ok=True)

def artifact(stem, extension):
    return {'path': f'literature/approved/{stem}.{extension}', 'sha256': stem}

sources = [
    dict(id='G2019', identifier='PMC6627528; DOI:10.3390/genes10060440',
         population='Taiwan Biobank: 14,537 adults (6,184 men; 8,353 women), ages 30-70, recruited in 2012-2016; volunteer/genotyping-selected cohort.',
         measurement='HDL-C in mg/dL; biochemical examination. Maintext does not provide a complete HDL assay method or assay harmonization with target.',
         cohort_overlap='Likely substantial but unquantified participant overlap with H2019; not independent corroboration. No identified overlap with target; both source populations are distinct cohorts.',
         approved_artifacts=[artifact('47555a144a38e836dab7da8c676a10f51089bc8f6f7776df74dbf31c464261ac','txt'), artifact('23728f05bcc689d1e4d9549f25d163243c4dd6b3a174225f34a7758c1514eaa8','xml')]),
    dict(id='H2019', identifier='PMC6566419; DOI:10.3390/nu11051102',
         population='Taiwan Biobank: 9,075 adults (4,262 men; 4,813 women), ages 30-70.',
         measurement='HDL-C in mg/dL, measured during biochemical examination; detailed assay unknown in inspected maintext.',
         cohort_overlap='Likely overlapping Taiwan Biobank participants with G2019; overlap count unknown; not a replication.',
         approved_artifacts=[artifact('cb68a4a8b61bcb589c29ee9a65451d519fbcc65362cd053a05e45d5a5f27d1c8','txt'), artifact('489641ed0c6573ac2206410a614007b94090b2305b585f0cfa755581bbd1321e','xml')]),
    dict(id='D2019', identifier='DOI:10.1016/j.jacl.2018.12.001',
         population='28,090 patients: 14,121 women and 13,969 men; geography, age range, selection, follow-up duration and full adjustment not established by the approved abstract.',
         measurement='Changes in HDL-C; HDL subfraction apo A1 concentrations measured using two-dimensional HDL-mapping. Exact total HDL-C assay unknown.',
         cohort_overlap='No reported link to Taiwan Biobank in abstract; independence cannot be established fully from abstract; no individual data accessed.',
         approved_artifacts=[artifact('a7cadad1cc84d15551e08f90d13dd983524b4d57a4d2dda477354bfcfef08537','json')]),
    dict(id='K2017', identifier='PMC5627541; DOI:10.1161/ATVBAHA.117.309201',
         population='GRAPHIC UK white European nuclear families; 1,932 analyzed individuals, ages 18-61, 49% male.',
         measurement='HDL-C and cholesterol efflux capacity (CEC) are separate measures; serum lipids by ultracentrifugation or NMR; detailed methods in external supplement unavailable here.',
         cohort_overlap='Separate UK cohort, distinct from Taiwan Biobank; no known target overlap.',
         approved_artifacts=[artifact('306bb06a748391a76ddaf275cfec42685c9ed63ce9aa0fdbe498e05f2212e07a','txt'), artifact('5a807059833dd8d6f85e279822c0258c3e0cdb2b487842f0701d782e1068bd6f','xml')]),
]

evidence = [
    dict(id='G01', source_id='G2019', locator='Table 2, Sex rows; BMI category column headings; Methods 2.2',
         estimand='Unadjusted arithmetic mean HDL-C within each sex-by-BMI category', variables=['hdl','bmi','sex'],
         adjustment='None; stratified by sex and BMI category; age and other covariates remain mixed within cells.',
         reported={'bmi_categories':['<18.5','18.5 to <24','24 to <27','>=27'], 'male_means_mg_dl':[61.83,51.92,46.75,43.25], 'female_means_mg_dl':[66.55,60.72,54.66,51.06]},
         uncertainty='Rounded group means; SEMs and n are in G02. Not conditional means at an exact BMI or age.',
         applicability='Reasonably broad adult cohort but Asian volunteer sample, different BMI distribution and incomplete assay comparability; ages outside 30-70 require extrapolation.',
         model_use='Anchor sex-specific conditional means after age centering; do not use a fully adjusted BMI coefficient as a marginal coefficient.',
         bridge_assumptions=['A01','A02','A03']),
    dict(id='G02', source_id='G2019', locator='Table 2, Sex rows; Methods 2.4 explicitly defines continuous results as mean +/- standard error',
         estimand='Standard errors of cell arithmetic means and cell sample counts, not individual standard deviations', variables=['hdl','bmi','sex'], adjustment='Same unadjusted cells as G01.',
         reported={'male_se_mg_dl':[1.52,0.25,0.21,0.21], 'female_se_mg_dl':[0.79,0.19,0.27,0.30], 'male_n':[75,2192,2308,1609], 'female_n':[333,4766,1963,1291]},
         uncertainty='SEs are rounded to two decimals. SE*sqrt(n) presumes conventional unweighted mean SE and independent observations; the paper does not give a residual SD for a model using only BMI, sex and age.',
         applicability='Supports heteroskedastic individual variability within broad sex-BMI categories; conditional-on-exact-predictor and target variances are uncertain.',
         model_use='Convert each SEM to aggregate individual SD using SE*sqrt(n); use the resulting CV as conditional variability proxy.', bridge_assumptions=['A01','A04','A05']),
    dict(id='G03', source_id='G2019', locator='Table 3, Age rows; model covariates listed in table',
         estimand='Adjusted additive HDL-C contrasts by age category relative to ages 30-40', variables=['hdl','age'],
         adjustment='Table includes exercise, WHR category, BMI category, body fat category, sex, smoking, alcohol, coffee and vegetarian diet. It is not a model adjusted only for the observed target fields.',
         reported={'age_categories':['30-40','40-50','51-60','61-70'], 'contrasts_mg_dl':[0,0.75841,1.18484,0.87361], 'p_values':['reference',0.003,'<0.0001',0.0068]},
         uncertainty='SE/CI not reported in table; overlapping 40-year boundary in printed category labels is preserved as a source ambiguity. Common-sex contrasts do not establish a sex-by-age interaction.',
         applicability='Age association may change when omitted covariates are marginalized; cross-sectional contrasts are not aging effects.',
         model_use='Smooth interpolation of the reported contrasts with no numerical sex-age interaction; category centers and extrapolation are declared assumptions.', bridge_assumptions=['A01','A03','A06']),
    dict(id='G04', source_id='G2019', locator='Table 2, Age rows, counts within each BMI column',
         estimand='Empirical counts of age groups conditional on BMI category, pooled across sex', variables=['age','bmi'], adjustment='None.',
         reported={'age_order':['30-40','40-50','51-60','61-70'], 'counts_by_bmi':[[183,99,81,45],[2156,1966,1846,990],[941,1209,1355,766],[832,813,859,396]]},
         uncertainty='Counts are exact as printed but joint sex-by-age-by-BMI counts unavailable.',
         applicability='Source centering only; not imposed on target predictor distributions.',
         model_use='Within each source BMI category subtract the count-weighted mean age contrast from each sex-specific HDL anchor.', bridge_assumptions=['A03']),
    dict(id='H01', source_id='H2019', locator='Table 3 BMI and age rows; Table 1 and Results paragraph 1',
         estimand='Adjusted sex-specific BMI category contrasts and reported descriptive means', variables=['hdl','bmi','age','sex'],
         adjustment='Includes genotype, age, diet, exercise, smoking, second-hand smoke, alcohol, tea, WHR, LDL-C, triglycerides, diabetes and hypertension.',
         reported={'male_bmi_contrasts_mg_dl':[7.72243,0,-3.68345,-5.04663], 'female_bmi_contrasts_mg_dl':[4.66897,0,-3.06323,-5.23881], 'age_ge_49_1_contrast_male':0.54472, 'age_ge_49_1_contrast_female':2.47290, 'table1_hdl_mean_male':48.5852, 'table1_hdl_mean_female':58.4673},
         uncertainty='Table 1 prints male/female SEMs 0.171/0.191 whereas prose prints 0.191/0.171. Underweight/normal count rows appear swapped, but no correction is asserted. Some regression row labels also have unexplained extra numbers.',
         applicability='Same parent cohort as G2019; heavier adjustment (including TG and WHR) changes the estimand.',
         model_use='Qualitative compatibility and extraction warning only; no parameters or residual scales obtained from the inconsistent fields.', bridge_assumptions=[]),
    dict(id='D01', source_id='D2019', locator='Approved Europe PMC abstract, Results and Conclusions',
         estimand='Longitudinal percent change in HDL-C per change in BMI, expressed relative to baseline HDL-C', variables=['change_hdl','change_bmi','sex'],
         adjustment='Abstract says age- and sex-adjusted subfraction measurements; exact adjustment for each total HDL-C relation is not established.',
         reported={'male_percent_hdl_change_per_bmi_change':-0.77, 'female_percent_hdl_change_per_bmi_change':-0.42, 'direction_across_obesity_classes':'HDL-C decreased with weight-category gain and increased with weight-category loss across multiple classes'},
         uncertainty='Abstract only, no total HDL-C slope SE/CI, no baseline mean by sex, no fulltext or numerical tail cross-sectional estimate available.',
         applicability='Within-person weight-change associations are not between-person BMI effects; clinical selection and population comparability uncertain.',
         model_use='Weak mechanistic continuation choice above largest BMI anchor; approximate small percentages as log slopes, explicitly an assumption bridge.', bridge_assumptions=['A01','A07']),
    dict(id='K01', source_id='K2017', locator='Results: relationships, stability and heritability; Materials and Methods',
         estimand='Distinction between HDL-C concentration and cholesterol efflux capacity plus evidence of stable non-predictor variation', variables=['hdl','cec'],
         adjustment='Varies by analysis; not extracted as an HDL-on-BMI model.',
         reported={'hdl_cec_correlation':0.62,'hdl_repeat_correlation_n82':0.82,'hdl_heritability_age_sex_batch_plate_adjusted':0.51},
         uncertainty='Not a conditional residual variance estimate. Tabular HDL summaries are rendered as images and unavailable in approved text; linked external supplement not retrieved.',
         applicability='Independent cohort supports avoiding the substitution of HDL-function effects for HDL-C effects; does not establish target calibration.',
         model_use='Context only. Do not import CEC regression coefficients, repeatability or heritability as residual SD.', bridge_assumptions=[]),
]

assumptions = [
    dict(id='A01', description='Transport the selected external aggregate patterns to the target without a target-outcome calibration offset. Geography, ancestry, cohort selection, treatment, fasting and assay differences remain unresolved; this is a scenario assumption, not validated transportability.'),
    dict(id='A02', description='Treat source BMI-category HDL means as values at representative BMI anchors 17, 21.25, 25.5 and 30.5 kg/m^2. The two closed-bin anchors are midpoints; the open-bin anchors are assumed. Piecewise linear interpolation between anchors supplies a continuous model. For BMI below 17 use the underweight anchor.'),
    dict(id='A03', description='Use a common additive age pattern across sex and BMI. Within each source BMI category assume the pooled age distribution also applies to each sex, so count-weighted category age contrasts can center sex-BMI means. This does not establish actual sex-specific source age distributions.'),
    dict(id='A04', description='Convert reported SEM to SD as SEM*sqrt(n) under the conventional independent unweighted mean formula; use that broad-cell marginal SD as an approximate conditional variability scale rather than claiming it is a measured regression residual SD. This retains some variation due to unmodeled within-cell predictor variation.'),
    dict(id='A05', description='Use a lognormal conditional distribution with exact arithmetic mean correction and source-derived coefficient of variation. Interpolate log variance across BMI anchors; hold CV constant with age and beyond extreme BMI anchors. This positive, right-skewed family and its tail behavior are not estimated from source quantiles.'),
    dict(id='A06', description='Interpolate age contrasts at representative ages 35, 45, 55.5 and 65.5, hold the nearest value outside this knot range, and do not impose a menopausal discontinuity. Treat an adjusted source age contrast as a provisional age association in a model omitting other source covariates.'),
    dict(id='A07', description='Beyond BMI 30.5, use longitudinal percent-change associations as provisional cross-sectional log-mean slopes: -0.0077 for men and -0.0042 for women per kg/m^2. This assumes local-percent-to-log approximation, extension across persons and transport across populations; it is a weak extrapolation choice, not an identified tail relationship.'),
    dict(id='A08', description='Draw participants independently conditional on the three observed predictors using a local seed-controlled RNG; no unobserved family, household, race, lifestyle or clinical covariates are reconstructed. Draw-to-draw Monte Carlo variation does not represent epistemic parameter uncertainty.'),
]
parameters = {
    'bmi_knots':[17.0,21.25,25.5,30.5],
    'age_knots':[35.0,45.0,55.5,65.5],
    'source_hdl_means':{'male':[61.83,51.92,46.75,43.25], 'female':[66.55,60.72,54.66,51.06]},
    'source_cell_counts':{'male':[75,2192,2308,1609], 'female':[333,4766,1963,1291]},
    'source_mean_standard_errors':{'male':[1.52,0.25,0.21,0.21], 'female':[0.79,0.19,0.27,0.30]},
    'source_age_counts_by_bmi':[[183,99,81,45],[2156,1966,1846,990],[941,1209,1355,766],[832,813,859,396]],
    'age_contrasts':[0.0,0.75841,1.18484,0.87361],
    'tail_log_slopes':{'male':-0.0077,'female':-0.0042},
}
provenance = {
    'bmi_knots':dict(evidence_ids=['G01'],assumption_ids=['A02'],derivation='Midpoints of [18.5,24) and [24,27) are 21.25 and 25.5; 17 and 30.5 are assumed representatives of open-ended bins, not reported source means.'),
    'age_knots':dict(evidence_ids=['G03'],assumption_ids=['A06'],derivation='Representative centers of printed age categories; boundary overlap is unresolved and no individual age distribution is inferred.'),
    'source_hdl_means':dict(evidence_ids=['G01'],assumption_ids=['A01','A02','A03'],derivation='Exact printed Table 2 sex-BMI arithmetic means; age centering and interpolation described in equations.'),
    'source_cell_counts':dict(evidence_ids=['G02'],assumption_ids=['A04'],derivation='Exact Table 2 counts; used only in SEM-to-SD conversion.'),
    'source_mean_standard_errors':dict(evidence_ids=['G02'],assumption_ids=['A04','A05'],derivation='Exact printed Table 2 SEMs, transformed to source SD=SEM*sqrt(n) then log variance=log(1+(SD/source_mean)^2).'),
    'source_age_counts_by_bmi':dict(evidence_ids=['G04'],assumption_ids=['A03'],derivation='Exact Table 2 age counts; each row weights the corresponding age contrasts to center the sex-BMI mean anchor.'),
    'age_contrasts':dict(evidence_ids=['G03'],assumption_ids=['A01','A03','A06'],derivation='Exact adjusted Table 3 contrasts, reference fixed to zero, used as additive mg/dL age function.'),
    'tail_log_slopes':dict(evidence_ids=['D01'],assumption_ids=['A01','A07'],derivation='Abstract percent changes -0.77 and -0.42 divided by 100, then used as approximate log-mean slopes above BMI 30.5.'),
}
spec = dict(
    model_id='ordinary_1_initial_source_anchored_lognormal', outcome='hdl', unit='mg/dL',
    family='Conditional heteroskedastic lognormal with interpolated arithmetic means',
    parameters=parameters, assumptions=assumptions, parameter_provenance=provenance,
    equations=[
        'Let j index four BMI categories and s sex. c_j=sum_k(n_jk*a_k)/sum_k(n_jk).',
        'm0(b,age,s)=linear_interpolate_BMI(m_js-c_j)+linear_interpolate_age(a_k). Interpolation clamps outside knots.',
        'm=m0*exp(tail_log_slope_s*max(b-30.5,0)).',
        'v_js=log(1+(SEM_js*sqrt(n_js)/m_js)^2); v(b,s)=linear_interpolate_BMI(v_js).',
        'HDL=exp(log(m)-v/2+sqrt(v)*Z), Z~N(0,1) independently, so E[HDL|x]=m and Var[HDL|x]=m^2*(exp(v)-1).',
    ],
    uncertainty='Fixed scenario parameters; stochastic residual draws only. Source uncertainty and transport uncertainty are not resolved by repeated draws.',
    alternatives_considered=[
        'Fully adjusted BMI contrasts: rejected as the sole BMI relationship because conditioning on TG, WHR and lifestyle changes the estimand.',
        'Categorical step function: avoids midpoint assumptions but introduces discontinuities and zero within-category continuous BMI association.',
        'Unbounded linear HDL mean: rejected for extreme BMI extrapolation because it can create nonpositive means.',
        'Gaussian residuals with clipping: rejected because it introduces an arbitrary positive point mass; lognormal distribution is explicitly assumed.',
        'Flat obesity tail: plausible sensitivity alternative, retained for checks because the selected longitudinal tail bridge is weak.',
    ],
    target_outcome_access=False,
)
(OUT/'model_spec.json').write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
(OUT/'evidence.json').write_text(json.dumps({'sources':sources,'evidence':evidence},indent=2)+'\n',encoding='utf-8')

decision = '''# Initial model decision: ordinary_1

The selected generator is a conditional lognormal model. Its arithmetic mean varies continuously with BMI and age, separately by sex; its coefficient of variation varies with sex and BMI. Every observed value and input order is preserved. Values are virtual measurements, not patient-level recoveries.

## Evidence and transformations

G2019 (PMC6627528) Table 2 supplies HDL means, standard errors and sample sizes for eight sex-by-BMI cells. These are unadjusted cell summaries. They are preferable here to a heavily adjusted BMI coefficient because the target supplies only BMI, sex and age. Individual SD is approximated as SEM times sqrt(n), not confused with SEM itself. These are broad-cell SDs, not directly reported conditional residual SDs.

G2019 Table 3 supplies a modest, adjusted age pattern; Table 2 age counts center it within each BMI category. Because sex-by-age-by-BMI cells are unavailable, the common age distribution within each BMI category is an assumption. The sex difference and BMI relation are therefore grounded in joint cell means while the added age pattern is more assumption-dependent. Printed overlapping age labels are not silently repaired.

BMI anchors 17, 21.25, 25.5 and 30.5 are declared representative values, not source-reported within-bin mean BMIs. Between them, means and log variances are linearly interpolated. Below BMI 17 the nearest anchor is used. Above 30.5, a gentle sex-specific exponential decline uses the D2019 abstract's longitudinal HDL percentage changes as a weak cross-sectional continuation. That change-of-estimand bridge is uncertain and is tested against a flat-tail alternative. Age effects clamp outside ages 35 to 65.5; source age coverage is 30-70 and target extremes require extrapolation.

The lognormal transformation exactly preserves the chosen arithmetic conditional mean. It assumes positive skew and a coefficient of variation inherited from source cells, with no upper clipping or empirical correlation forcing. Source broad-cell variability may overstate residual variability after exact BMI and age are fixed. Conversely, an ethnically and clinically more diverse target may be more variable. The current evidence does not identify a correction in either direction.

## Source quality and access limitations

H2019 (PMC6566419) is likely overlapping Taiwan Biobank evidence, not an independent confirmation. Its Table 1 and prose interchange male/female SEMs, and its underweight/normal count labels appear inconsistent. No correction is invented, and no parameter uses those inconsistent entries. It supports only qualitative comparison with differently adjusted associations. G2019 also has clear typographic errors in discussion/prose; the model uses the consistent numeric Table 2 cells and Table 3 age rows, not the erroneous discussion beta or p-value.

K2017 (PMC5627541) is an independent UK cohort but mostly concerns cholesterol efflux capacity. It reinforces the distinction between HDL concentration and function and does not supply a usable HDL-on-BMI regression here. Its table values are images outside the approved text. CEC coefficients, heritability and repeat correlations are not substituted for residual HDL variance.

D2019 (DOI 10.1016/j.jacl.2018.12.001) is available through approved abstract metadata only. Its total HDL slope SE, detailed eligibility, age range, geography and exact adjustment are unknown. The tail use is labeled accordingly. Searches/fetches rejected by the gateway (two fulltexts) were not bypassed or used. No excluded study-derived estimate is used. No supplements were needed for the chosen core table; unavailable tables were not treated as zero effects.

## Applicability and uses

This generator supports transparent scenario analyses of a continuous HDL feature with BMI, age and sex, including exploration of interactions generated by the chosen structure. It does not validate a US population distribution, recover an individual's HDL, identify causal effects of weight change or aging, generate associations with unobserved lifestyle variables, or establish treatment/cardiovascular risk conclusions. Any relation not supplied directly by evidence is a consequence of this assumed model. Strongest gaps are target transport, exact BMI shape within and above source bins, sex-specific age effects, residual distribution and tails, and assay comparability.

The only target inspection was the observed BMI/age/sex support: 4,885 rows, BMI ranges 14.1-74.1 in men and 15.2-77.5 in women, ages 20-79. These checks motivated positive, bounded-below functional choices but supplied no outcome information. No target HDL summaries or target validation were obtained. No generated target cohort was used to choose parameters.

## Stopping and reproducibility

Initial retrieval stops with 6 of 12 queries and 5 of 12 download attempts consumed. Six queries and seven downloads remain for an independent review and a targeted revision. The selected evidence identifies cell means/variability sufficiently to build an auditable initial scenario; further wide searches would leave less budget for review-directed questions. The approved artifacts and gateway audit history are retained.

Actual invented-input, source-arithmetic and structural checks are in artificial_checks.json, reproducible with run_initial_checks.py. They test implementation and assumptions, not target accuracy. Parameters were fixed before these checks; no coefficients were tuned to random realizations or significance thresholds. The model specification is passed as the generator's evidence argument. No final directory is created in this turn.
'''
(OUT/'decision.md').write_text(decision,encoding='utf-8')
print('Wrote initial model_spec.json, evidence.json, decision.md')
