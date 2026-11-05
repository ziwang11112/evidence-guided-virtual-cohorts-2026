# H01 initial candidate decisions

Implements the independently reviewed proposal without numerical redesign: exact375-per-cell design, uniform integer ages, bounded-beta BMI mean28.01/SD5, conditionally truncated-normal glucose, and linear HbA1c conditional mean plus centered gamma residual SD.35/shape9. The generator consumes all specification settings and performs no file/network access or import-time sampling.

Q1 age .010/year transfers Pani NHANES. Q2/Q3 use the explicit cross-source decomposition: Kerman marginal covariance slope .23*.73/12.4 is ASSUMED conditional; Finnish reduced BMI .0125 minus gamma*.432 yields .006650580645161291. This is an assumed model, not identified causal/target biology. Glucose truncation makes Q2 .06200508 rather than nominal .0625 per5. Deterministic expectations are not target observations. Implied glucose-HbA1c marginal correlation .437 differs from Kerman .23, openly retained.

Required review annotation: Finnish S1/S2 response units are inferred from main Table1/intercept scale, not directly printed; unlabelled coefficients remain in evidence and A_FIN_UNIT carries their mapping. Hoorn quartile contrasts retain expanded, multiply-imputed/pooled, backward-selected model meaning; their direction is not imposed on Q3.

All source-feedback recipes remain not_computable where weighting/missingness/units/operator definitions are unavailable. Review and deterministic calculations are retained with provenance. Unknown residual structure, interactions, anemia/medication and source-to-target selection remain assumptions. Bounded predictors plus shifted gamma have all integer moments finite and positive HbA1c support infimum2.7291; upper HbA1c tail remains unbounded.

Four query credits used (one HTTP503), one original download; no further acquisition. No generator execution, freeze, random simulation or participant/target data inspected by the author. Root separately reviews code and runs the prescribed isolated schedule. Candidate supports transparent hypothetical-law inspection; no national prevalence, causal, clinical-validity, measurement-savings or publication-readiness claim.
