# Independent scientific candidate and derivation review

Reviewed UTC: 2026-11-03T04:31:48.011748+00:00
Reviewer: source_integration_contract_review
Producer: source_integration_author
Candidate: D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcSI/candidates/initial

Decision: approved for the frozen source-only point-functional integration gates, subject to separately bound qualified-comparison reviews and actual runtime checks. No target execution or release is approved. No remaining scientific admission blocker was identified under this limited contract. The technical qualified-plan binding placeholders were corrected to exactly empty objects before freeze.

## Scientific basis

The actual code matches all four context-law declarations: finite age mixtures, nondegenerate Bernoulli female membership, independent normal source drivers, the stated latent loadings and log scales, and J glucose clipping. The residual latent variances are positive in every context (approximately J 0.84636, B 0.60792, M 0.69352, T 0.66272). Biomarkers are exponentials of finite normal linear combinations, so every finite polynomial moment exists; the native IFCC affine view preserves finite second moments. Age and female are bounded. This is not the invalid exponential-of-lognormal composition.

For the planned intercept-including population projections, age and female supply independent nondegenerate nuisance directions. BMI and glucose have nondegenerate continuous joint variation, including J's positive-probability interior below its clipping cap. Thus no nonzero affine combination of the predictors is constant and their population moment matrices are nonsingular. Realized rank, categories, finite values and eligibility must still be checked after the authorized draw; finite sampling can fail.

All four published relationships enter actual numerical code paths through declared algebra:
- Jansen BMI and FPG coefficients are converted separately to pairwise latent correlations under the assumed margins and age/sex independence. They are not pasted into one joint structural regression.
- Their combination with assumed q=0.25 determines shared residual BMI loading k.
- Bao Pearson uses the lognormal covariance identity; MIND Spearman uses the continuous Gaussian-copula rank identity.
- Bao and MIND anchors define the common dependence rule used in dormant T at its assumed glucose dispersion.

The static shared-parameter substitution is substantive: with rho held fixed, k -> k+delta changes Corr(BMI_latent,Hb_latent)=q*rho+sqrt(1-q^2)*k by sqrt(1-q^2)*delta, while the remaining Hb latent residual is adjusted according to the same code for sufficiently small delta. Both J projections inform k. The target rho is a combination of Bao and MIND anchors with its declared interpolation coordinate strictly between zero and one. No perturbation simulation or target-result check was performed.

The shared age envelope does not replace context conditions. Reviewed code uses assumed J ages 18-81, Bao 20-80 with its disclosed boundary convention, MIND 61-80, and dormant target 35-74. J observed glucose is capped at 6.999 before return; Bao/MIND/target do not inherit that cutoff. Source aliases and native units preserve J/B plasma, M serum, and target central serum distinctions.

## Limits retained

This is an engineering/point-functional admission, not full physiological or transport validity. The positive lognormal HbA1c percent law has nonzero probability below 2.152%, mapping to negative IFCC values; the author now discloses that support defect. Positive lognormal tails more generally are assumed rather than established physiological bounds. J clipping creates an atom and changes the FPG projection from the pre-clipping derivation. These do not invalidate the reviewed finite-moment point functionals, but prevent a general physiological-support claim.

Age/sex independence, q=0.25, biomarker distributions, source age supports/coarsening, hypothetical target margins and dispersion-based sharing are assumptions. The population age coefficient is zero by the declared independence assumption, not evidence. Source fit would not validate those choices.

Original weights, exact regression/pair membership, processing, MIND imputation/ties, some fasting/timing details, assay comparability and exclusions on unobserved variables remain unresolved or conditioning assumptions. Source margins and relationships share source parents; no independent-replication, precision-weighting or pooled-loss claim is justified. Source SDs are not estimator SEs. Four qualified checks are still pending execution and do not become strict replay.

## Frozen derivation verification

All 15 parent freeze commitments were checked against actual bytes. Registry commitment was checked using the lifecycle's canonical artifact-prefix convention, rather than raw JSON bytes. Actual J/B/M/T child tasks equal the parent task with only descriptor population/count changes. Actual child model specifications equal the final parent specification except active_context. Copied candidate/source/evidence bytes, source recipes, mechanically filled semantic hashes and schedules match the parent and binding requests. Target has neither a source recipe nor semantic feedback. Science request sidecars, engine hashes and canonical request digest match the inspected files.

The science request is 73a06e3f7fbac99f9a652bcb948530e3a50d6df46d5519666ccac9ee9a9f5f94. The target binding approval covers only dormant derivation; the governing execution quota remains three source attempts of 1000 rows including failures and zero target dispatch.

## Reviewed artifact hashes

| Artifact | SHA-256 |
|---|---|
| generator.py | b7ac834f5533d909b1d41d0b276c508e2bfd1ab0f85275d56d1a5c55d640dad8 |
| model_spec.json | 3ffcb200a50adbe47943052e9c724f846454b0e95e73eae25a2f309cfa4cd1d6 |
| scientific_validity_v1.json | 7d7f7ce548b49c10c1861b51b0cbb8ee5b928f56384f532e4ccc3939534a780a |
| context_bridge_v1.json | 1fe7425582fabaff3c6d9fd11eb6f9d1e661437d2b754e74466e0eda2a7d4c2e |
| qualified_plan_v1.json | b8e2b5a855a9074ec322ee25c64f402f8f8c7e684086264049ea24df5181b25b |
| context_eligibility.json | ee15e103178cbb970d7f229aff5b3fb6e60d26d2c117ff1cfca29405aa0e6499 |
| evidence_use_v1.json | ece44fa54ad424e18ebff0353440699061c7bb4d84c255d986fb42afc80c0ac4 |
| analysis_evidence.json | 2bd0e983d5a7baf2502368803103afb9821bd04cdb70b306d01a2899d51040ff |
| decision.md | 8bc002d7054ddaa05c1a4aee1adb812f9d57780e26d2547badffee4888789b1c |

Read-only scientific review and metadata arithmetic preceded these review records. No generator was imported or executed, no rows were sampled or inspected, and no network or target data were accessed. Only the reviewer-owned binding, science and candidate-review files were written.
