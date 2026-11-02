# C2 initial independent candidate review

Disposition: **PASS for the released controller schedule**, with the two fixed conditional interpretations approved only as task-population proxies. No blocking provenance, scientific-description, implementation or interface defect was found in the reviewed bytes. This is not a finding of biomedical validity or source reproduction.

Reviewer: `/root/public_repository_audit`. Builder: `/root/chns_c2_initial`. The reviewer did not author this candidate or select its scientific parameters. The reviewer previously curated the fixed source templates; those received separate packet review. Independence here is from the candidate builder, not a cryptographically authenticated identity, an external clinical review or an independent source-study replication.

## Bound artifacts

| Artifact | SHA256 |
|---|---|
| F2_RELEASE.json | `730a1cbab4e3dddaa33f3fa24d43ba1bc260ed57de8a8beb48075a37df02d8a9` |
| model_spec.json | `b6b4de1aec6d85c88104c906e1cf9023f4cf0b2ae676f8d01de5475aaae74972` |
| generator.py | `6b26e312a38e8d6de17be6791a760179a08e42d2d070685b9ba5b6e28613a3bf` |
| interpretation_approval.json | `2c82acb1a25731cdd93a6342e5d1b8b8fb9521af33bd83f26640777e32b50f02` |
| conditional_interpretations_v1.json | `8b11d64ebda6ca4d7e7cfb49a1c9ca8e852be25e106f799e8c88674395bbf8d1` |
| candidate_review.json | `82fbb655609bf7f372c4616929e26bace025028ec93d6ac4145ac886371a5a51` |

The candidate review binds all **11** other current candidate artifacts, including the complete interpretation approval and plan, and has no declined interpretations. The frozen-stage binding and lifecycle freeze receipt are appropriately excluded by the controller contract; neither existed at completion of this review. The original nine builder artifacts were not edited.

## Scientific and provenance assessment

The 36 model settings have complete evidence/assumption provenance and 19 declared assumptions. Exact evidence, recipe and semantic-sidecar bytes match the released inputs; all six required interpretation assumptions are unchanged. Five source artifacts match their approved registry hashes. Constructor metadata and auxiliary-check hashes also match.

Age composition, age/sex independence, BMI shape, mixture probabilities, within-component covariate shifts, residual scales and residual correlations are explicitly assumed. The external evidence does not identify this joint law, and uniqueness is not required for this bounded construction experiment. Source medians are not relabelled means; marginal individual SDs are not claimed to be estimator SEs or fitted residual SDs. The conditional HbA1c shifts are not copied from Pani or assembled from Jansen's separate adjusted regressions. The two source correlations are not substituted for the model's conditional log-scale residual correlation.

The glucose specimen, assay, source selection, age composition, calendar and missingness gaps remain explicit. Positive lognormal support and a latent elevated component are modelling choices, not recovered diabetes categories or prevalence. No target moment, desired target coefficient, clinical threshold calibration, participant row or another candidate was used in this review. Parameters remain fixed; seed variation would represent conditional Monte Carlo variation among fictional people, not source-estimation, structural or transport uncertainty.

## Code and runtime interface

Static review of [generator.py](../candidates/C2_initial/generator.py) finds the required synchronous three-argument entry point and an explicit rejection of non-null observations (lines 11–17). Age discretization and endpoint protection implement the declared support (19–24). Conditional BMI, stable logistic mixing and paired Gaussian log residuals implement the specification (28–67). The final DataFrame has the declared six-column order and deterministic unique row labels (69–80).

Only NumPy and Pandas are imported. The used Generator, array, elementary-function and DataFrame APIs present no apparent incompatibility with the supplied NumPy 2.4.5/Pandas 3.0.3 runtime. SciPy is unnecessary. There is no file/network access, external input read, generator-time source lookup, or import-time generation. This is a static compatibility assessment, not an execution result. Unbounded tails, finite-sample output validity, resource use and exact runtime behavior remain untested.

## Interpretation and metadata gates

Both unchanged proposal entries are accepted: Bao Pearson and MIND serum-glucose/HbA1c Spearman. Equal weights, complete generated-input handling and average Spearman ties are explicit interpretations. Original weighting, original missingness processing and the original tie implementation do not thereby become known. The reported source-wide sample sizes are not promoted to pair-specific precision. Approval permits descriptive, assumption-defined task proxies; neither is an original-source replay.

All **16** evidence items have dispositions: **2 interpretation_approved**, **14 not_approved** for numerical interpretation. The latter remain usable as contextual evidence with explicit assumptions. Pani's known weighting and Jansen's unit/adjustment/uncertainty gaps do not receive an equal-weight override. Quarantined MIND agreement statistics remain outside the admitted packet.

Actual metadata-only checks passed: lifecycle program/contract/registry/check-artifact validation, fixed-policy equality, parameter domains, and the real strict and conditional preflight APIs. Each strict row remains **unavailable**, reason “Weighted or unknown source estimator is not implemented.” Conditional preflight returns **approved_declarations**, original weights **not_reported**, strict status **unavailable**, and source reproduction **not_established**. The initial inline review utility had a syntax error before execution; after correction, the described checks passed. No old or new software test suite was run.

Final rehash confirms 12 candidate files, with the 11 non-review artifacts bound by candidate_review.json, and unchanged model, generator and release hashes. A first final-inventory call supplied a relative root to the internal absolute-path helper and was rejected; the corrected absolute-root call passed without changing candidate contents.

Only the three authorized approval/plan files and this report were written. No generator was imported or called, no clinical table or numerical feedback was produced, no new source was opened, and no candidate was frozen. Controller execution, output validation and later independent target evaluation remain separate gates.

