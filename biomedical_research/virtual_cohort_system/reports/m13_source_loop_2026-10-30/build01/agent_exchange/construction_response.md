# build01 candidate submitted

Candidate: `candidates/initial`.

The generator uses Gallagher's published DXA inverse-BMI Equation1 as the baseline, with an explicit Asian-only0.35 blend toward the Thai development age/BMI/sex equation. The same law applies to every input row and never uses row IDs, context IDs or sample size. Shared level/male shifts and one residual multiplier complete a four-scalar bounded calibration proposal. Mean-preserving beta individual variation is anchored to the reported4.31 pp SEE, with an assumed female/male SD ratio1.10. Bounded-mean and variance guards are explicit assumptions. Neither marginal outcome means nor SDs are treated as regression intercepts/residual SDs.

Evidence contains108 items and exactly the registry source IDs, artifact paths and hashes. All10 Thai diagnostics and all8 original Gallagher DXA coefficient diagnostics are represented and constrained once. Gallagher retains its original seven-predictor design, without a standalone Asian intercept. Original units, adjustment sets, locators, within-cohort overlap, unknown coefficient precision, device differences, Thai validation bias conflicts and contextual unreplayed evidence are retained.

Two covariate-only contexts contain8,920 Thai development rows and9,756 Gallagher rows with exact reported group weights and age/BMI means/sample SDs. No generated outcome column is present. Thai rows all have BMI<30; Gallagher BMI<=35. Model-domain v2 covers source and qualification supports without changing target eligibility. Derived columns recompute exactly. Fixed latent age–BMI correlations−0.15 and+0.10 are unidentified scientific scenarios, never optimizer parameters.

A covariate-only consistency check rejected an initial single-beta Thai BMI shape: it implied32.35% BMI>=25 in development, exceeding the full-cohort approximate count budget. The final reconstruction explicitly assumes15% above25 in each development sex, using a bounded two-component shape while preserving moments. This per-sex allocation is not reported evidence. The resulting female lower-component distribution is strongly U-shaped and demonstrates substantial reconstruction uncertainty. Alternative shape/dependence scenarios require scientific sensitivity analysis; this context is not recovered patient data.

The calibration plan follows the exact controller seeds, execution limits, all18 term-specific scales, max9 trials, shrink0.5, min-step fraction0.01 and target loss0. Source populations/devices are not asserted equivalent. Thai/Japanese transport cannot be resolved with the permitted binary indicator. Reproducing source summaries would not establish target validity, calibrated uncertainty or causal effects.

Actual checks passed: covariate reconstruction arithmetic; exact derived columns; source v2 support compilation; typed-empty operator schema preflight; Thai rank4/4 and Gallagher rank8/8 regression designs; all18 constraints once; controller settings; unchanged approved input hashes; generator AST/signature; core candidate contracts. `python -m cohort_harness validate --candidate initial` returned contract valid/program route/generator_executed false/scientific_validity not_assessed. The first CLI attempt used `candidates/initial` and was rejected for requiring a simple name; the corrected invocation passed. Both outputs are retained. Full freeze-dependent replay/calibration validation and all generated outcomes remain unperformed for the controller.

Files:

- `generator.py`, `model_spec.json`, `evidence.json`, `decision.md`, `checks.json`
- `source_replay_v2.json`, `proposed_calibration_plan.json`
- `source_contexts/thai_development.csv`, `source_contexts/gallagher_full.csv`
- `prepare_candidate.py` (seed130117; covariate/artifact construction only)
- `validate_preparation.py` (contract/covariate validation only)
- `covariate_diagnostics.json`, `preparation_validation.json`, `validation_cli.txt`

No generator import/execution, freeze, calibration, target analysis, retrieval or forbidden-data inspection was performed. Ready for controller freezing and isolated execution.
