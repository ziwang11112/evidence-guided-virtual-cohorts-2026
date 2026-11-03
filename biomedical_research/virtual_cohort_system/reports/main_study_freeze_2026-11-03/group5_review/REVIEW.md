# Group 5 independent implementation review

Reviewer: `/root/main_review_g5`. This review checks committed implementation, source mapping, numerical uptake and mathematical readiness. It does not select models for favorable source or target fit, and it does not certify target-population validity. Only assigned bundles, registered scoped sources, their permitted inputs/profile/decision, and the allowed skill/interface/schema/lifecycle/controller documents were used. No generator was imported or executed, no rows were sampled, and no clinical target results, sibling constructions or old experiments were read.

## ENSANUT2018_E0_A03 — ready

Candidate: `candidates/initial`; decision: `initial_final`.

- Candidate freeze SHA-256: `5c5e43f423589d34e36937ff8061c20984b6bdfe438114710afef214b888c851`.
- Decision SHA-256: `b0d72c1c07bf2617b665b170e6c1de170545b8f5870c188dd9417ebfd6d77fc3`.
- Retained independent script: `review_ensanut_e0_a03.py`; calculations: `ENSANUT2018_E0_A03_calculations.json`.
- Fresh `lifecycle.verify_candidate(bundle, 'candidates/initial')` passed; all 31 independent checks passed. Frozen files and decision were not modified.

The actual code constructs eight nonoverlapping sex-by-age-band cells with 375 rows each, draws integer age inclusively within each band, and then draws independent gamma BMI and scaled-beta glucose/HbA1c. The final permutation preserves the exact 3000-row design and 1500 rows per sex. Unique row identifiers and the six task columns follow directly from the code. Support guards fail explicitly on nonfinite or boundary values; they do not clip or rescale a sample.

All 17 evidence items and normalizations match the admitted registered source extracts. BMI uses the Jansen mean/individual-SD pair 26.5/4.1 kg/m²; glucose uses 5.1/0.5 mmol/L multiplied once by the supplied factor 18; HbA1c uses the directly reported percent pair 5.6/0.3. Alternate IFCC/NGSP representations are retained without double counting. Source age and sex margins are contextual because the task fixes another demographic design. Shared Lifelines evidence and NGSP's measurement-only role are disclosed.

Independent exact arithmetic, linked by static inspection to the actual RNG transformations, gives:

| Variable | Mean | Variance | Second raw moment |
|---|---:|---:|---:|
| Age | 53.875 | 270.359375 | 3172.875 |
| Female | 0.5 | 0.25 | 0.5 |
| BMI | 26.5 | 16.81 | 719.06 |
| Glucose | 91.8 | 81 | 8508.24 |
| HbA1c | 5.6 | 0.09 | 31.45 |

Gamma shape/scale are positive; both beta shape pairs are positive. BMI has finite moments of every nonnegative integer order; the other variables have bounded support. The centered predictor covariance diagonal is `(2.70359375, 0.25, 0.6724, 0.81)` for age10, female, bmi5 and glucose10, so the requested population OLS projections exist uniquely under the declared factorization. Zero slopes are consequences of an explicit independence assumption, not observed target or source associations.

The E0 non-marginal operation inventory and uptake list are both empty, as permitted. All 17 target-as-source feedback checks are unavailable with null operators and matching semantic hashes. The retained analytic record reproduces the law's marginal moments and does not claim source-population reconstruction.

Readiness is limited to implementation and mathematical review. External marginal transport, independence, distribution shapes, stratum invariance and the HbA1c modeling upper bound remain disclosed assumptions. Source-estimator and transport uncertainty are not simulated by changing seeds. Successful isolated final execution still must establish table validity. This review did not close science or run/deliver any seeds.

## CHNS2009_E1_A03 — ready

Candidate: `candidates/initial`; decision: `initial_final`.

- Candidate freeze SHA-256: `21487d0d6d514a4ccce0d0e675129c7407588352ffcf762711810e2fe16f3ac7`.
- Decision SHA-256: `e56acf91b9f3cbb33859d6334e73bb78b63f5e645597a79ebf6d36938b99566c`.
- Retained independent script: `review_chns_e1_a03.py`; calculations: `CHNS2009_E1_A03_calculations.json`.
- Fresh `lifecycle.verify_candidate(bundle, 'candidates/initial')` passed; all 102 independent checks passed. Frozen files and decision were not modified.

The code implements the specified triangular Gaussian factor law with latent BMI-glucose correlation `q=0.20`, glucose-HbA1c correlation `r=2 sin(pi*0.529/6)`, and BMI-HbA1c correlation `q*r`. The factor matrix is nonsingular because `(1-q²)(1-r²)>0`. Pointwise lognormal transformations use the MIND arithmetic means and individual SDs. Independent integer ages 35–74 and Bernoulli(0.5) sex are disclosed completion assumptions. This task does not supply exact demographic quotas. The total row count, unique IDs, six output columns and positivity guards match the contract.

For a finite power vector `k`, the raw biomarker moment is `exp(k'μ + k'Σk/2)`, so all finite-order moments of the actual linear-normal exponentiation exist. The independent calculation reproduces the retained first/second moments, confirms finite fourth moments and positive-definite covariance, and checks the selected-source normal-CDF normalization. Biomarker full support on the positive orthant, plus independent nondegenerate demographics, gives nonsingular population predictor moments for the requested OLS analyses. The zero age coefficient is a declared assumption consequence. The unbounded tails and rare finite-sample rank/roundoff failures remain limitations; final execution must retain failures.

The law-specific Spearman proof is correct. Strictly increasing lognormal transforms preserve population ranks. For correlated standard normals `(Z_G,Z_H)`, introducing independent normals `(A,B)` gives `E[Phi(Z_G)Phi(Z_H)] = P(Z_G-A ≥ 0, Z_H-B ≥ 0)`. The difference-pair correlation is `r/2`; its positive-quadrant probability is `1/4 + asin(r/2)/(2*pi)`. Thus Spearman is `(6/pi)asin(r/2)`, exactly the inverse used by the generator. The resulting equality is imposed under a continuous no-tie scenario and does not reconstruct MIND's unknown mean-imputation/tie effects.

The four non-marginal operations are completely mapped, with preserved source meanings and uncertainty metadata:

| Operation | Independent calculation | Reported source point | Use |
|---|---:|---:|---|
| Jansen BMI, native IFCC per kg/m² | 0.07898479964086959 | 0.13 | Analytic check |
| Jansen FPG, native IFCC per mmol/L | 3.2779684166059226 | 2.29 | Analytic check |
| Bao Pearson | 0.5456200148959719 | 0.619 | Analytic check |
| MIND Spearman | 0.5289999999999999 | 0.529 | Imposed model constraint |

Jansen calculations use the separately declared source law after FPG<7, with native IFCC response and the two correct, separate age/gender-adjusted projections. Their covariance/variance ratios agree with the frozen supplied-operation results. The approximation that uses printed selected moments as parent moments, followed by selection, is explicitly disclosed; other eligibility effects remain unresolved. Bao uses its own conditional source pair, median/log-IQR margins and raw Pearson functional; independently reproduced quantile discrepancies remain in the record. None of these discrepancies was optimized or assessed by a favorable-fit threshold.

All 36 evidence items match the admitted input, including 35 quantitative records and contextual NGSP guidance. Source packet, operation-record, locator and analytic-input hashes agree. All four uptake records have reachable artifact pointers and explicit selection, measurement, source-overlap and uncertainty statements. No SD-to-SE conversion, unconfirmed confidence-level inference, precision pooling, plasma/serum substitution or duplicate-unit evidence counting occurs. All 35 target-as-source comparisons remain unavailable with bound semantic records.

Readiness accepts an explicit, reviewable scenario. Source-to-target marginal/copula transfer, assumed dependence completion and null age effects remain unvalidated. Source discrepancies remain substantive scientific limitations, and unknown estimator/transport uncertainty is not sampled by changing seeds. No generator or author script was imported/executed during this review, no cohort rows were produced, and no final-stage action was taken.

## CHNS2009_E0_A05 — ready

Candidate: `candidates/initial`; decision: `initial_final`.

- Candidate freeze SHA-256: `06921f0323b22e3663cba634c7f90770987ae8dac57a47749115b4e234109966`.
- Decision SHA-256: `650d3ab4831f72b3fcc0968b04259667de7c8342d0b5d4218902c0972d9ef385`.
- Retained independent script: `review_chns_e0_a05.py`; calculations: `CHNS2009_E0_A05_calculations.json`.
- Fresh `lifecycle.verify_candidate(bundle, 'candidates/initial')` passed; all 72 independent checks passed. Frozen files and decision were not modified.

The generator implements the declared 80-component age/sex mixture, with uniformly distributed integer ages 35–74 and independent Bernoulli sex probability `2049/3547`. It samples three conditional lognormal biomarkers with the stated age/sex log effects and shared/individual Gaussian residuals. The task supplies no exact demographic quotas. Its 3000-row construction, identifier convention and six output columns agree with the task.

Independent arithmetic enumerated all 40×2 demographic support states, rather than producing participants or quadrature nodes. Their probabilities sum to one. The joint enumeration agrees with the generator's product of age and sex MGFs. The normalization leaves residual log variances approximately `(0.020366340000528643, 0.06942134387923761, 0.026213875183481485)`, each positive. With absolute loadings below one, the residual covariance is a positive rank-one term plus a strictly positive diagonal matrix, hence positive definite.

The review integrates conditional first and second moments over every state. This reproduces all retained unconditional means, SDs, demographic cross-products, raw second moments and covariance entries. In particular, the actual mixture recovers BMI `25.0/3.6`, serum glucose `5.2/1.4` and HbA1c `6.1/1.0` as mean/total-SD pairs. The derivation does not confuse those total SDs with conditional log-residual SDs. For every finite power vector, the conditional Gaussian exponential moment is finite, and summing 80 finite terms preserves finiteness. Bounded age/sex multipliers also remain integrable. The actual conditional density has support over the positive biomarker orthant, establishing population rank together with nondegenerate demographics.

Independent Cholesky solutions of the full mixture covariance reproduce the correct population OLS adjustment sets and all retained slopes/intercepts. The focal coefficients are:

| Requested use | Independent law consequence |
|---|---:|
| E1 BMI, adjusted for age/female | 0.07697625734099729 |
| E2 glucose, adjusted for age/female | 0.365964760039985 |
| E3 age, adjusted for female/BMI/glucose | 0.00443886748134946 |

These values are model implications, not source coefficients or observed target results; their signs or magnitude did not determine readiness. Age/sex effects and factor loadings have assumption-only provenance, as required for this E0 packet.

All 32 source items equal admitted inputs and map to the registered source packet or contextual NGSP guidance. MIND marginal scales and the female count ratio are explicitly transported assumptions. Jansen/Bao are contextual, and no hidden non-marginal relationship is inserted. Empty numerical uptake agrees with the empty E0 relationship inventory. All 32 target-as-source comparisons remain unavailable with correct semantic hashes.

The unbounded biomarker tails, demographic and assay/population transfer, chosen effect strengths and unquantified structural/source uncertainty remain limitations. Finite theoretical moments do not establish finite-precision table validity or guarantee finite-sample rank; the controller must validate final outputs. The review imported no generator or author script, sampled no rows, used no target clinical references and performed no close/deliver action.
