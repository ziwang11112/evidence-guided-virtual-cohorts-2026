# Jansen 2013: contextual adjusted source projections

Authored summary from retained, independently audited source records; no original was reopened for this packet. Jansen et al., Lifelines, [DOI 10.1111/joim.12010](https://onlinelibrary.wiley.com/doi/10.1111/joim.12010). Review-ready contextual use only, not a target parameter assignment.

The source includes unrelated western-European adults, favoring the oldest family members for GWAS. Diabetes by self-report or fasting plasma glucose at least 7.0 mmol/L, specified anemia thresholds, and missing HbA1c/erythrocytes/FPG are excluded. Its marginal cohort n is 2,921; regression-row n is unconfirmed. Exact age limits, fasting hours and gender coefficient coding remain unresolved. HbA1c is an IFCC-standardized immunoassay; fresh fasting plasma glucose uses hexokinase/G6PD. Analytic weighting is not established for this reuse.

Table 2 separately relates each named predictor to HbA1c with age/gender adjustment:

| Source projection | Reported coefficient | Printed interval | Native coefficient unit |
|---|---:|---|---|
| BMI term, adjusted for age/gender | 0.13 | 0.10–0.16 | mmol/mol per kg/m^2 |
| Fasting plasma glucose term, adjusted for age/gender | 2.29 | 2.07–2.51 | mmol/mol per mmol/L |

The printed intervals' confidence level and row-specific n are not established. No SE is reconstructed. Because the strict evidence schema requires a known level for a numeric CI object, its uncertainty field is `not_reported` with this explicit incomplete-interval qualification retained in applicability/admission metadata. This does not mean no interval was printed.

These are two separate adjusted projections, not coefficients from one complete jointly fitted equation. Do not concatenate them, treat either as an intercept or prescribe them as CHNS parameters. Population exclusions, IFCC-versus-percent units, plasma-versus-serum measurement, weighting and exact sample differences prevent strict numerical feedback in this packet. Any algebraic HbA1c scale conversion uses the separately labelled [NGSP relation](NGSP_UNITS.md), remains a dependent representation of the same source coefficient, and does not establish assay/transport equivalence.

Table 3 is quarantined and its numeric coefficients are absent here. No source intercept, coefficient covariance or residual distribution is supplied. No prior target result, fitted candidate or historical tuning choice is imported. Individual-level source/target non-overlap has not been verified.
