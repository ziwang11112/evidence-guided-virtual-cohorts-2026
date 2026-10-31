# Source-only scientific decision: linear

The candidate tests a common centered HbA1c response law in two explicitly approximated source populations, with fixed reported source reference locations. Lifelines5.6 is a whole-source mean; Pani5.44 is specifically the55–59 mean. Analytic centering preserves this distinction. The difference is not attributed to an assay effect or freely fitted away. Any future target location is unidentified.

Age feature is age itself. This transparent shared linear response is the reference structure.

Age, sex, BMI, glucose and HbA1c are all generated without IPD. Each source has6000rows. The development parent is never executed. Pani age-bin n values construct unweighted probabilities; the upper age group includes70–90, not a borrowed target age limit. Lifelines support18–90 is an assumption. Pani BMI/glucose/sex marginals are unavailable and fixed to Lifelines marginals. Independence and no direct sex term are declared simplifications shared across structures and never calibrated.

Jansen BMI/FPG coefficients are separate age/sex-adjusted projections. They equal the model's conditional terms only under the fixed independence assumption. Pani's age estimate is a survey-adjusted projection; the supplied unweighted regression approximates it. In the nonlinear alternative the feature coefficient is not itself the age projection. All exact20source operators are retained, including age-stratum means. Pani SEs are not individual SDs; Jansen interval coverage is unknown; duplicate unit representations are not additional constraints. Liu and Table3 remain contextual/quarantined.

Five common scalar parameters are fit within predeclared bounds. All population distributions, covariance, reference anchors, domain limits and curve shape choices are fixed before execution. The residual SD is initialized by a linear independent-variance subtraction, not by interpreting the marginal SD as residual SD. The Gaussian noise law and its transport are assumptions.

calibration_plan.json and scientific_criteria.json are written before freeze. All20weights are1; scales are nondimensionalization choices and are not clinical tolerances or probabilities. Prospective requirements include exact execution linkage, finite checks, age-profile/association compatibility and unchanged covariate marginals. Selection uses only seed19101 with at most40evaluations inclusive baseline; unused19111/19123 compare both initial and selected candidates. Strict improvement on both unused seeds is required for robust numerical improvement. No target is generated or evaluated.

This authored candidate is a testable source-only submission, not a claim that the unknown source distributions are correct. Successful source fit cannot establish target validity, causal effects, measurement replacement or individual realism. Current stopping point is complete static artifacts; actual isolated execution and calibration belong to the controller.
