# M11 point-estimate adapter

Prospective descriptive estimators, prepared before new target outcome release. Primary: equally sex-averaged absolute discrepancy in weighted sex-specific medians, in HbA1c percentage points. Reuse: six fixed age–sex cell means (20–39, 40–59, 60–79 by sex) and overall weighted Q90. Preservation: adjusted age and BMI slopes from the same WLS model in real and generated data.

Primary target weights are official NHANES 2021–2023 phlebotomy weights WTPH2YR, not MEC weights. Estimates describe the eligible measured-outcome domain under those weights. Missingness/transport assumptions limit national generalization. No survey standard errors, clinical equivalence tests or inferential p-values are supplied by this narrow adapter. Design fields are preserved for future design-based uncertainty work.

Quantiles use the left inverse of the weighted empirical CDF, aggregating ties. This differs from linearly interpolated source-paper check quantiles; it is a prespecified target estimator applied identically to real and generated data. Empty cells remain unassessed and are not silently dropped from composite errors.

Pure additive sex-specific location shifts preserve adjusted linear age/BMI slopes by construction when output clipping does not intervene. Preservation is an implementation/control check, not new evidence that calibration learned these relationships. Residual seeds do not represent source/model/transport uncertainty. Source scenarios are sensitivity alternatives, not posterior draws.

This module does not read reference outcomes. A separate release-gated controller must verify protocol, all freezes, inputs and execution artifacts before reference parsing.
