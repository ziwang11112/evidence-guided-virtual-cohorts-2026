# L01 proposed joint construction

Status: concrete proposal for controller review, before candidate implementation. No target numerical summaries are available or used.

## Representation and source roles

Generate 3,000 independent synthetic rows with columns id, age, sex, bmi, total_cholesterol, hdl_cholesterol. Lipids are delivered in mmol/L; intended analysis converts using the requested factor 38.67 mg/dL per mmol/L. This factor is unit conversion only. Sex uses literal F/M with M as the analysis reference; mapping external female/male summaries to those literals is an explicit assumption because the metadata legend was not independently verified.

The model has a 50:50 sex mixture, sex-specific BMI distributions, sex-specific lipid location with common log variance per lipid, and a common four-dimensional Gaussian copula for age/BMI/TC/HDL. It does not posit latent source-study membership or label synthetic people as rural or urban. The source moments, rank associations, and relative contrasts are separate components.

## Exact law and proposed parameters

1. Draw S as Bernoulli(p_F=0.5), independent of a four-dimensional latent vector Z. This is an assumption about a hypothetical adult sample, not an estimated Turkana sex fraction. Each row is independent; no source or target cluster structure is claimed.
2. Draw Z=(Z_A,Z_B,Z_T,Z_H) from a centered multivariate normal with unit marginal variances and correlation matrix R below. Use the same R in both sex strata.
3. Let U=Phi(Z_A). Set age to the piecewise-linear quantile function with probability knots (0,0.25,0.5,0.75,1) and value knots (18,24.5,33.5,47,90) years. No age rounding is required.
4. For X in BMI, TC, HDL, set X=exp(mu_X,S + sigma_X,S * Z_X). Use natural logarithms. The marginal parameters below are sex-specific but not conditional residual parameters.
5. Set unique string identifiers. Do not apply a target eligibility exclusion beyond the task. In particular, do not infer pregnancy, diabetes, HIV, fasting or lifestyle flags. Do not impose TC≥HDL, clip lipids, or redraw rows to improve any analytical result.

The age distribution has bounded support 18–90 and finite mean 39.75 years and SD 19.1322154145 years. The upper endpoint is a modeling assumption, not a claim that the target excludes older adults. The quartile-linear shape is likewise an assumption; no source density between quantiles or age tail is supplied.

### Dependence matrix

Order: age latent score, BMI latent score, TC latent score, HDL latent score.

```text
R =
[ 1.0000000000,  0.1000000000, 0.1500000000,  0.0500000000 ]
[ 0.1000000000,  1.0000000000, 0.2215502484, -0.1046719125 ]
[ 0.1500000000,  0.2215502484, 1.0000000000,  0.1109459600 ]
[ 0.0500000000, -0.1046719125, 0.1109459600,  1.0000000000 ]
```

The last three pair correlations derive from rural Ashanti Spearman values 0.212, −0.100, 0.106 via `2*sin(pi*rho_S/6)`. They define the model's unadjusted within-sex rank dependence. They are not coefficients in either requested OLS model, raw-scale Pearson correlations, or the requested lipid residual correlation. Transferring a community-pooled statistic to each sex stratum remains an unresolved conditioning assumption.

The age latent correlations 0.10 with BMI, 0.15 with TC, and 0.05 with HDL are explicitly assumed modest positive associations. Their magnitudes and directions are not measured target facts or extracted source estimates. They retain possible confounding by age without claiming identification. Common dependence across sexes and age ranges, Gaussian copula form, and absence of further interactions are additional assumptions. These choices can materially change adjusted results even with fixed source marginals.

Deterministic Cholesky calculation produced diagonal values (1, 0.9949874371, 0.9666468101, 0.9840079558), all positive. Thus this proposed R is positive definite; no nearest-correlation repair is needed. Exact values are retained in ANALYTIC_PROPOSAL_CHECK.json.

### BMI scale

Use Agongo sex-specific arithmetic mean/SD directly as transported scale components:

| Literal sex | Arithmetic mean | Arithmetic SD | Natural-log mu | Natural-log sigma |
|---|---:|---:|---:|---:|
| M | 20.87 | 3.15 | 3.027049939347 | 0.150085187424 |
| F | 22.28 | 3.85 | 3.088977936907 | 0.171531210873 |

Units are kg/m² for means/SDs and log(kg/m² numerical representation) for mu. For each pair (m,s), `v=log(1+(s/m)^2)`, `sigma=sqrt(v)`, `mu=log(m)-v/2`. This is a model moment conversion, not a reported log-scale statistic. The source is ages 40–60; the proposal assumes these sex-specific moments can describe the broader adult synthetic scenario. With p_F=0.5 the pooled BMI moments are consequences, not forced to equal the source's pooled 21.63/3.61.

### Lipid scale and sex contrasts

For each lipid, let m and s be Agongo pooled arithmetic mean/SD, q the Greiner rural female/male geometric-mean ratio, and p=p_F:

```text
m_M = m / ((1-p)+p*q)
m_F = q*m_M
between = p*(1-p)*(m_F-m_M)^2
v = log(1 + (s^2-between)/((1-p)*m_M^2+p*m_F^2))
sigma_M = sigma_F = sqrt(v)
mu_sex = log(m_sex)-v/2
```

The numerator is positive for both proposed lipids. This construction matches the chosen pooled arithmetic moments exactly in the mathematical model while allowing the chosen sex contrast. Common log variance makes the sex ratio identical on geometric and arithmetic mean scales; this is explicit synthesis across distinct source cohorts.

| Parameter | TC | HDL |
|---|---:|---:|
| Source pooled arithmetic m, mmol/L | 3.23 | 1.14 |
| Source pooled arithmetic s, mmol/L | 0.92 | 0.38 |
| Assumed transferred F/M ratio q | 3.9/3.6 = 1.083333333333 | 1.10/1.05 = 1.047619047619 |
| Model arithmetic mean M, mmol/L | 3.100800000000 | 1.113488372093 |
| Model arithmetic mean F, mmol/L | 3.359200000000 | 1.166511627907 |
| Model arithmetic SD M, mmol/L | 0.873748707632 | 0.370158288746 |
| Model arithmetic SD F, mmol/L | 0.946561099935 | 0.387784873924 |
| Natural-log mu M | 1.093457046927 | 0.055087850510 |
| Natural-log mu F | 1.173499754601 | 0.101607866145 |
| Common natural-log sigma | 0.276416699159 | 0.323758905627 |

These individual SDs are model-derived marginal SDs within sex, not source-reported conditional SDs. The requested OLS residual RMS values will be induced by the full law and must not be set to 0.92 or 0.38.

## Intended analysis decisions

All three analyses have assessment “partial,” not “directly_reported.” Their estimands concern the target design, while the available statistics are components. The eventual evidence-use manifest must bind the actual parameter paths, evidence items, assumptions, and reviewed check artifacts.

| Analysis | Evidence-use decision | Actual parameters used | Unresolved link |
|---|---|---|---|
| K02-HDL-BMI | Relationship: rural BMI–HDL Spearman component; dispersion: Agongo BMI and HDL moments; relationship: Greiner HDL sex ratio | R[B,H], BMI sex moments, HDL pooled mean/SD and ratio, age copula terms, sex mixture and age knots | Rank association does not identify adjusted raw-scale slope; cross-population, selection, assay, conditioning and scale bridges |
| K02-TC-BMI | Relationship: rural BMI–TC Spearman component; dispersion: Agongo BMI and TC moments; relationship: Greiner TC sex ratio | R[B,T], BMI sex moments, TC pooled mean/SD and ratio, age copula terms, sex mixture and age knots | Same missing identification and transport links |
| K02-LIPID-RESIDUAL | Relationship: rural TC–HDL Spearman plus both BMI–lipid components; dispersion: lipid/BMI moments | R[T,H], R[B,T], R[B,H], all marginal scales and age links | Unadjusted rank correlation does not identify age/sex/BMI-adjusted Pearson residual correlation |

No requested target coefficient or residual correlation is assigned a source number. After permitted execution, fit the specified unweighted OLS models with intercept, age, F indicator, BMI; report BMI coefficient times 5 and lipid units times 38.67. Residual correlation is Pearson on the two fitted residual vectors from identical eligible rows. Equivalent centered/scaled designs preserve these quantities.

If deterministic implied OLS moments are computed later, they will be labeled model-derived, with method and numerical approximation retained. They will not be new evidence or a tuning target.

## Assumptions to preserve in the implementation

- A_population: Agongo Ghana marginal scales, Ashanti Ghana rank structure, and Greiner Malawi relative sex contrasts can be combined as an illustrative adult Turkana-context synthetic scenario; no target composition or validity is established.
- A_measurement: Numeric same-analyte/unit transfer is used despite source fasting serum/central laboratory protocols and target venous EDTA CardioChek Plus with unknown fasting. No assay-error bridge is identified.
- A_selection: Source pregnancy/health/residence/complete-case selection is not target eligibility. Source-conditioned summaries are applied without claiming the target meets those exclusions.
- A_weighting: Model and target requested analyses use equal row weights. Source weighting remains unknown; generation weights do not establish original-study weighting.
- A_sex_mapping: External female/male source labels are mapped to target F/M literals despite the unverified metadata legend.
- A_demography: p_F=0.5, common age distribution across sex, iid rows, age endpoints/within-quartile shape, and absent site/lifestyle clusters are assumptions.
- A_age_dependence: Latent age correlations (0.10,0.15,0.05) and their invariance across sex are assumed, not estimated.
- A_copula: Continuous Gaussian copula and conversion from Spearman; shared dependence across sexes; source community-pooled rank statistics applied within sex.
- A_marginal_family: Positive lognormal BMI/lipid distributions with all finite moments; no clipping; source marginal moments transfer across the age span.
- A_sex_ratio: Greiner geometric-mean sex ratios transfer across populations; common within-sex log variance permits the derived arithmetic ratio; synthesis with Agongo pooled moments is assumed.
- A_uncertainty: Parameters are fixed scenario values. No posterior or calibrated transport distribution is supplied; reported CIs are not residual SDs or source-study weights.
- A_operator: Source SD denominator and quantile convention are unknown; ddof=1 SD and linear sample quantile diagnostics are operational approximations. Source correlation tie/missingness rules remain unknown.

Unreported relations are not inferred to be zero: numerical relations above are explicit choices. The age/sex independence of the latent draw and lack of additional covariates also remain choices, not facts.

## Finite moments, checks, and limits

BMI and both lipids are strictly positive lognormal variables. Every power moment exists: `E[X^k|S]=exp(k*mu + k^2*sigma^2/2)` for finite k. Age is bounded, sex is binary, and the finite mixture preserves finite moments; therefore the moments needed for OLS and Pearson correlation exist. Positive-definite latent dependence and nondegenerate distributions supply model variation; finite generated samples still require design/range checks.

The mathematical law permits rare TC<HDL measurements because no joint physical partition constraint is specified. This is a modeling limitation to report, not an eligibility rule to silently impose. No non-HDL output or clinical interpretation is proposed.

Performed checks: source extraction review, quantity/operator distinctions, deterministic lognormal-moment conversion, lipid mixture-variance arithmetic, and Cholesky positivity. No model implementation, schema validation, generator execution, generated-only diagnostic, or source-feedback result is claimed.

After review and authorized implementation, proposed source feedback is approximate: Agongo sex-specific BMI means/SDs and pooled BMI/lipid moments; all six rural/urban Ashanti Spearman values as separate source comparisons, retaining rural as the calibration component and urban as context-only; Greiner age quantiles if the explicit convention assumption is retained. Comparing a synthetic target-context output with these populations is not source-population reconstruction. Geometric means/ratios and unresolved log regressions remain explicitly not computable under a core operator that lacks those definitions; do not substitute arithmetic means or raw coefficients.

The initial verified output may expose source discrepancies due to finite sampling, the source-to-sex conditioning bridge, deliberate sex composition, or cross-study synthesis. Any proposed revision must diagnose those possibilities first. No change is justified by hidden target performance or a favorable seed. Residual variation is individual variation under this fixed law; repeated seeds do not propagate evidence or transport uncertainty.

Acquisition stop: existing admitted sources suffice to make this scoped construction reviewable. Additional heterogeneous published associations would not identify the missing target age/site/selection joint distribution. No optional retrieval is needed solely to consume budget. The exact model is ready for review; implementation remains unreleased.

