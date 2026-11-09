# Independent source-operator review

2026-11-09. This review concerns a bounded, source-only whole-cohort replay. It makes no clinical parameter or generator-family choices. The reviewer read `FOLLOW_ON_SPEC.md`, both prior independent reviews, the association inventory, `docs/SOURCE_CHECKS.md`, `docs/SEMANTIC_FEEDBACK_V1.md`, and the evidence-cohort-generation skill/interface. Original Soares 2019 XML Methods, Tables 1–3 and missingness/selection passages were inspected directly; saved extracted supplement text was inspected, including Supplementary Tables 1–3. Original Soares 2020 XML was inspected for the contrasting selection and multiple-imputation procedure. No new searches, downloads, datasets, candidates, target data, target results, or generator executions were accessed. Only this review file is written.

## Verdict and scope of approval

The eight Soares 2019 Table 3 BMI coefficients are authentic source constraints. A bounded **assumption-dependent model-projection replay** is feasible. It does not require discovery of every unpublished estimation convention, exact source participant reconstruction, or a specific generator family. It does require an immutable account of the reported operator, an explicit implemented operator, and a declared source-to-target model connection. This approves that scientific design concept, not an uninspected protocol/engine or a claim of exact finite-sample reproduction.

## Verified Table 3 inputs

All entries below are **mmol/L difference in the raw lipid outcome per one SD higher BMI**, adjusted within the specified sex/location stratum. The printed interval is a 95% CI for the coefficient. BMI and WHR have separate table columns; the selected BMI effects must not be turned into effects jointly adjusted for WHR.

| Stratum | BMI-model n | TC coefficient | TC 95% CI | HDL-C coefficient | HDL-C 95% CI |
|---|---:|---:|---|---:|---|
| Rural women | 4,971 | 0.23 | [0.19, 0.26] | -0.03 | [-0.04, -0.02] |
| Rural men | 3,548 | 0.20 | [0.16, 0.23] | -0.03 | [-0.04, -0.02] |
| Urban women | 7,455 | 0.13 | [0.11, 0.15] | -0.05 | [-0.05, -0.04] |
| Urban men | 3,705 | 0.15 | [0.12, 0.18] | -0.04 | [-0.05, -0.04] |

The primary source is Soares et al. 2019, DOI `10.1136/bmjgh-2019-001542`, XML table `T3`; its footnote states the adjustment set and the outcome/BMI scales. Original XML `s2-4` describes multiple linear regression, household-cluster robust standard errors, the four strata and Stata 15.1. Direct age standardization of descriptive summaries is a separate operation and does not establish regression sampling weights. Regression weighting and an explicit intercept are not stated; an unweighted regression with intercept is a reasonable implemented convention when labelled assumed. Robust standard errors concern inference; they do not change an otherwise identical OLS point coefficient.

## Population, measurements, and incomplete selection reconstruction

The study concerns resident adults aged at least 18 in Southern Karonga and Area 25, Lilongwe, sampled in 2013–2017. Of 33,177 eligible people, 30,575 consented and 24,943 had fasting lipid measurements. Missing lipid and nonfasting measurements were excluded. Lipids were assayed enzymatically with a Beckman Coulter AU480 after at least eight hours fasting; duplicate anthropometric measurements were averaged. The source does not justify changing raw lipid units to logs, lipid SD units, or a different assay representation without a declared conversion.

Table 3 regression denominators are smaller than the fasting-lipid group denominators (rural women 7,096, rural men 5,000, urban women 8,563, urban men 4,284). Supplementary Table 3 reports missing BMI, marital status, parity and HIV/ART, with HIV/ART missing in 18.5% overall. The 2019 article does not explicitly describe multiple imputation or name a complete-case algorithm. Complete-case regression is a reasonable inference from the model denominators and reported missingness, but is not a fully reconstructed procedure.

There is a small unresolved denominator inconsistency: urban men have 4,284 fasting-lipid records, 2 missing BMI and 573 missing HIV/ART, with no other missing values reported in Supplementary Table 3. Deleting the union of these missing records would retain at least 3,709, whereas Table 3 gives 3,705. Preserve the reported n and this four-record discrepancy; do not silently correct either table. A replay may sample directly from an assumed selected analysis law or simulate selection/missingness. It need not reproduce the original rejection process, but must state which law its sample represents and why comparison is assumption-dependent.

In contrast, Soares 2020 explicitly selects complete anthropometry and fasting lipids, then imputes missing covariates by chained equations separately by age group and sex. Its relevant Malawi adults have 9.2% missing HIV status. This is not an all-covariate complete-case estimator, and it is not the 2019 estimation procedure. An ordinary complete-source-law projection can inform comparison with 2020 only under explicit missingness/imputation assumptions. The overlapping MEIRU cohorts cannot supply independent precision or replication.

## Covariates and design matrix

The Table 3 adjustment set is age, ethnicity, education, household assets score, marital status, parity for women, lipid-lowering medication, smoking, alcohol, physical activity, and HIV/ART status. Source Methods `s2-3` supplies these encodings:

| Covariate | Source-supported definition | Remaining implementation issue |
|---|---|---|
| Age | Age adjustment | Continuous/other functional form is not explicitly specified. |
| Ethnicity | Chewa, Tumbuka, Ngoni, Yao, Lomwe, Nkhonde, other | Reference category/contrasts not printed. Table spelling `Nkonde` is a naming variant. |
| Education | No formal, standard 1–5, standard 6–8, secondary, tertiary | Do not silently use a linear 1–5 score. |
| Household assets | Cumulative local value of 15 assets, categorized into quintiles **within each area** | Exact cutpoints, tie conventions, and regression contrasts not printed; do not silently substitute continuous asset value. |
| Marital status | Never married, married, widowed, divorced/separated | Categorical contrasts not printed. |
| Parity | Number of pregnancies irrespective of outcome, categories 0, 1, 2, 3, ≥4; women only | Not live-birth count or a mandatory continuous 0–4 score. |
| Smoking | Never, former (stopped >6 months ago), current (smoked in last 6 months) | Categorical contrasts not printed. |
| Alcohol | Previous 12-month frequency: never, <once/month, 1–3 days/month, 1–4 days/week, ≥5 days/week | Not an established equally spaced numeric dose. |
| Physical activity | IPAQ/MET-derived low, moderate, high | Do not silently use one linear ordinal term. |
| Lipid-lowering medication | No raised-cholesterol diagnosis; diagnosis without medication; diagnosis with medication | A simple medication yes/no discards a reported distinction. |
| HIV/ART | HIV status and ART use among people reporting HIV positive | Exact joint model encoding is unresolved; a joint three-state coding is possible but assumed. |

A saturated categorical design with an intercept can choose any reference levels without changing the BMI slope, provided its column space is unchanged. Exact reference-category recovery is therefore unnecessary for the point comparison. An ordinal score, collapsed levels, altered age basis, or different HIV/ART representation changes the adjustment space and must be disclosed as an implemented convention/approximation. Sparse or absent categories may create redundant columns: an engine may remove mathematically redundant columns deterministically while recording rank and retained span; it must not drop scientific covariates because their fitted coefficients are inconvenient.

## Standardization is a declared operation

The paper reports BMI in SD units but does not uniquely specify whether the SD was pooled or stratum-specific, which retained population supplied it, or its finite-sample divisor. The phrase about fifths and SD units “by sex and area” supports stratum-aware analysis but does not settle all these choices. Descriptive BMI SDs in the supplement describe broader denominators, so they cannot be treated as exact Table 3 conversion constants.

For any chosen source reference SD `s_ref`, fitting raw BMI and reporting `beta_raw * s_ref` is algebraically equivalent to fitting `(BMI - c_ref)/s_ref` with an intercept. This is a mathematical scale identity, not evidence that `s_ref` is the paper's SD. The contract must name the reference population, stratum scope, pre/post-selection stage, population versus sample SD, any `ddof`, and how the SD is obtained. No target BMI SD or target outcome SD may fill this gap. Centering does not change the coefficient when an intercept is included, but the implemented convention should still be recorded.

A source-law sample SD is an estimate of a declared source-law scale. A fixed/model-population SD is a different convention. Either can be chosen by the scientific Agent, with provenance and uncertainty labels; neither should be silently substituted for the other. Expose at least one relevant alternative if materially consequential, within the fixed source-evaluation budget. This is not a demand for all possible conventions or a source-paper-specific unpublished exact answer.

## Full nuisances versus a justified reduced projection

There are three distinct legitimate paths; the engine must not conflate their labels:

1. **Explicit full design.** The source-law table includes every variable needed by the declared regression and filters, with declared categorical expansions and female-only parity. Unreported nuisance distributions or correlations are model assumptions. They need not appear in final target-output columns.
2. **Equivalent computational representation.** A residualization, sufficient-moment calculation, or orthogonal basis may replace explicit raw nuisance columns if the Agent supplies the mapping and shows that it represents the same declared adjustment span/operator. Frisch–Waugh–Lovell equivalence is computational; arbitrary latent scores with familiar labels do not prove it. An analytic route is not verified row-based replay unless its own calculation and provenance are separately supported.
3. **Reduced projection under an orthogonality/model assumption.** The Agent may explicitly assume omitted nuisance terms are orthogonal to residual BMI conditional on retained covariates in the declared source law. Then the corresponding population linear-projection BMI coefficient is unchanged. This is a substantive assumption and must identify every covered source covariate, the conditioning set and the mathematical condition. It is not the paper's empirically verified full regression. Independence in a generating law gives population orthogonality, not exact orthogonality in each finite random sample. A finite reduced-model coefficient must therefore be labelled an approximation to that assumed projection, not an exact full-design finite-sample result.

For the third path, if `B` is the retained design and `C` the omitted nuisance design, a sufficient population condition is `E[(BMI - P_B BMI) (C - P_B C)] = 0`, with finite second moments and identifiable residual BMI variation. Alternatively the Agent can supply another correct equivalence argument. Missing evidence about nuisance relationships does not establish this condition. Do not require a particular condition, covariance, distribution, or zero nuisance effect in the controller.

The reported operator remains the full source regression for all paths. A reduced path receives a separately named implemented operator and assumption IDs. If the implemented engine cannot support such a path, the Agent may use the full-design path or mark a check unavailable. It must never call an age-only fit the full Table 3 regression merely because a prose caveat exists elsewhere.

## Minimal operator contract and reporting

Before execution, freeze all of the following for every admitted check (shared definitions may be referenced rather than duplicated):

- Source ID, exact locator, immutable printed estimate/CI/n, unit and dependent-family ID; all eight checks remain represented.
- The reported operator: raw outcome, BMI-per-SD scale, sex/site/adult/fasting population, full adjustment set and known categorical definitions, unknown weighting/encoding/SD/selection details, and household-robust inference.
- The replay operator: source-law/context identity; sampling or analytic projection route; selection/missingness law; explicit design or mathematically justified alternative; intercept/weights; standardization order/reference/divisor; inference output or an explicit statement that source CIs are only displayed descriptively.
- Assumption IDs that distinguish source-law reconstruction, operator implementation, measurement and transport. Each assumption must be substantive and linked to the part it resolves. Unknowns cannot be relabelled supported simply because code needs a value.
- Source-to-target linkage: which parameter/function/distribution components are shared, which are population-specific, how each requested target analysis is affected through the link, and which links are supported versus assumed. A disconnected source fit is `context_only` for target use. Parameter equality across populations is allowed only as an explicit Agent choice/assumption, never imposed by the host.
- Output labels distinguishing `source_model_projection`, `assumption_dependent_replay`, `exact_finite_sample_reproduction` (not established here), and unavailable calculations. Preserve source n separately from generated n and retain selection/used-row counts.

The printed CIs quantify coefficient-estimation uncertainty with source dependence and rounding. They do not identify individual residual SDs, a joint multivariate likelihood, covariance between all eight estimates, or transport uncertainty. Do not infer dispersion from the CIs, use eight independent inverse-variance weights by default, impose a CI-overlap acceptance gate, or treat a closer point discrepancy as target validation. Numerical/Monte Carlo variability is separate from source uncertainty.

The existing semantic v1 guard explicitly does not support standardized coefficients and requires operator operands to be task columns. A new source-context extension must review standardization and context-column schemas explicitly; labelling transformed BMI `identity` merely to pass the old gate would defeat it. Preserve existing semantic protections against reversed outcomes, altered adjustment sets, unit mismatch, hidden filters, and unsupported transformations. An assumed reduced operator needs its own accepted mode and derivation, not an `approximate` flag that bypasses mismatch checks.

## Compact recommended declaration shape

This is a field-level recommendation for a new implementation, not an executable existing-schema file or a prescribed scientific construction. `*_ref` values refer to frozen, substantive declarations. Choose one supported replay route; values shown as alternatives describe allowed types, not multiple simultaneous operations.

```json
{
  "schema_version": 1,
  "evidence_id": "soares2019_rural_women_TC",
  "dependent_family_id": "MEIRU_2013_2017",
  "reported_operator": {
    "source_id": "Soares2019",
    "locator": "XML T3, BMI column, rural women, TC",
    "kind": "adjusted_linear_coefficient",
    "outcome": {"variable": "TC", "unit": "mmol/L", "transform": "identity"},
    "exposure": {"variable": "BMI", "raw_unit": "kg/m2", "scale": "per_source_SD"},
    "stratum": {"site": "rural", "sex": "women"},
    "population_ref": "reported_source_population",
    "adjustment_ref": "reported_full_design_women",
    "standardization_reference_status": "not_reported",
    "missingness_procedure_status": "not_fully_reported",
    "weighting_status": "not_reported",
    "inference": "household_cluster_robust",
    "estimate": 0.23,
    "ci95": [0.19, 0.26],
    "source_n": 4971
  },
  "replay_contract": {
    "context_ref": "declared_source_law",
    "estimand": "source_model_projection",
    "route": "explicit_design_or_equivalent_basis_or_assumed_reduced_projection",
    "selection_ref": "implemented_selection_and_missingness",
    "design_ref": "implemented_design_and_encoding",
    "standardization_ref": "implemented_reference_SD_rule",
    "estimator_ref": "implemented_point_estimator",
    "equivalence_argument_ref": null,
    "assumption_ids": ["source_law", "SD_rule", "estimation_conventions"],
    "status": "assumption_dependent",
    "exact_finite_sample_reproduction": false
  },
  "target_use_mapping": {
    "analysis_ids": ["requested_TC_BMI_analysis"],
    "status": "assumption_dependent",
    "shared_components_ref": "shared_model_components",
    "population_specific_components_ref": "population_specific_components",
    "measurement_mapping_ref": "declared_measurement_mapping",
    "support_and_transport_ref": "per_link_supported_or_assumed_declarations"
  }
}
```

The implementation can use fewer nested fields if it retains the same distinctions. It must fail closed on a malformed or mismatched declared operator, while unknown source conventions may proceed under an explicit supported assumption-dependent route. Missing precision alone need not block a point comparison. An unavailable operator remains unavailable, with a reason, and is never zero discrepancy.

## Original-artifact binding

Paths below are relative to `work/conditional_evidence_2026-11-09/`; originals remain local. XML and supplement text were read; the supplement PDF hash was checked, but its pages were not visually re-rendered in this review.

| Artifact | SHA-256 |
|---|---|
| `source_bodies_associations/Soares2019.xml` | `0ae152fdf556f868af152f3b1afb49602b357d71325c41dae493b382ec38b08f` |
| `source_bodies_associations/Soares2019_supp.pdf` | `748c87d0930ebc67eb5d2bb79eb4b8e7d9b4b3c21a42ded246f2311cafdd2194` |
| `source_bodies_associations/Soares2019_supp.txt` | `7a816e02587b08ee29c0734755be8d4224edd533ff3be4ee0b8b82126ad27c72` |

No new clinical evidence or exact unpublished implementation was inferred from these commitments. Subsequent independent protocol/engine review must check that these distinctions survive execution, budget accounting, freezing, feedback separation, and final reporting.
