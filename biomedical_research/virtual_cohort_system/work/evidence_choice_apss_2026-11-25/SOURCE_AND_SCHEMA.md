# Norton et al. agreement study: case admission and evaluator specification

## Eligibility and exposure

The 2018 Australian APSS study recruited adult volunteers aged 18–75 from a fitness centre and a sports club. Its 94 participants first reported measurements online. On the following visit they reported some variables again and investigators measured height and weight. The selected comparison uses the first online report and objective anthropometry. The paper and public XLSX come from the same study, so this case evaluates a downstream analysis in the source study. It is a convenience sample. [Original paper](https://doi.org/10.1371/journal.pone.0199836) · [Public data](https://doi.org/10.1371/journal.pone.0199836.s001)

The November 23 search agent opened this article and chose the Malaysian paper for construction. The exposure ledger documents header-only inspection of the Australian workbook. The Malaysian outcomes have already been revealed. This trial uses the same scientific question and a different study with a previously unscored participant file. The publicly available article and previous exposure preclude guarantees about pretraining. [Exposure record](../../docs/DATASET_EXPOSURE_REGISTRY.md) · [Prior selection scope](../autonomous_paired_validation_2026-11-23/eligible.json)

The reuse locations under the previous trial are `private/search/retrieval/PMC6019396.txt` for the frozen aggregate paper text and `private/reference/PMC6019396.xlsx` for the 45,292-byte workbook, SHA-256 `91bd4f5b2e48fec969397c8be68577ea5419ec3190c929f0a956c6525d7c0f45`. Intake examined the source text, bytes/hash and workbook headers through row 4. Measured BMI pairs and their downstream results remained unavailable at intake.

## Published joint evidence (evaluator only)

1. Table 1 gives online and measured BMI marginal means and SDs. On identical complete pairs, the difference of means fixes the mean difference to reported precision. The corresponding table denominators and printed rounding can differ from our complete-case reconstruction.
2. The Stage 3 row of Table 2 compares online BMI with the objectively measured value. The reported obesity margins at BMI ≥30 are 8 online positives and 12 measured positives in 91 pairs. Unweighted Cohen's kappa is printed as 0.776. If the number positive by both methods is `a`, the ordered cells are `[a, 8−a, 12−a, 71+a]`, where `a` can be any integer from zero through eight. With chance agreement `(8×12+83×79)/91²`, only `a=8` puts kappa in the rounding bin [0.7755, 0.7765). The unique table is [8, 0, 4, 79], with kappa 0.776413 and agreement 87/91. Use these four proportions for the source replay. The replay does not establish whether the author intentionally used these counts; code and source provenance are audited separately.
3. That row also reports ICC 0.962 and a parenthesized RMS of 1.3. Methods say intraclass correlations were analyzed but do not specify ICC variant or the exact RMS denominator/formula. Neither equating ICC with Pearson correlation nor using 1.3 as the population standard deviation of the difference is exact without a declared assumption. Stage 2 instead compares two self-report modalities. Treating its ICC or dichotomous kappa as an objective-measurement constraint is a semantic mismatch.
4. The Stage 3 joint classification constrains crossings of a level of 30. The requested event crosses a *difference* of −2. Continuous values can move within these cells or change by small amounts across a cell boundary. Neither the printed marginals, the rounded kappa, the ICC/RMS entry nor the algebraic table fixes the event frequency. The article projection contains no participant-level results or direct count for this event. Individual pixel values and supplemental participant records may not enter the constructor context.

The target is the reported-minus-measured adult BMI difference, with two uses. One asks for the mean signed difference in kg/m². The other asks for the percentage with difference strictly below −2 kg/m². Report all pair-based estimated values in native units. Source agreement and measured use utility are separate. Each seed's source TV is 50 times the L1 distance between the four probability vectors. Report mean and maximum across seeds. The descriptive 3-percentage-point criterion requires all three draws to pass and does not certify clinical equivalence.

## Workbook schema and eligibility

Read `Online_versus_F2F`, row 4 headers. The first row is a title, row 3 labels questionnaire stages. The 77 columns include no participant ID. Under the publisher's one-volunteer-per-row description, preserve repeated phenotype values. Record the number of exact full-record duplicates; their presence calls for examination before interpretation.

| Role | Header | Workbook column |
|---|---|---|
| Age (years) | Age | B |
| Online height and weight | OL_SR_height, OL_SR_weight | AD, AE |
| Online calculated BMI | OL_BMI | AF |
| Objective visit height and weight | F2F_measured_height, F2F_measured_weight | BP, BQ |
| Objective visit calculated BMI | F2F_calculated_bmi(measured) | BR |
| Face-to-face self-reported height and weight | F2F_SR_height, F2F_SR_weight | BN, BO (excluded) |

Use eligible adults with all four raw anthropometric components and a known age. The paper states 18–75; an age above 75 triggers documented eligibility reconciliation. Missing ages and incomplete raw pairs are counted separately. Derive BMI from mass in kg and measured height using the printed units (cm). If the storage header lacks units and ≥90% of comparable observations jointly confirm a metre encoding through the cached BMI under the predeclared factor of 10,000 check, use metres on that storage field. Preserve the scale decision and counts within 0.10 kg/m² of the cached value. Failing both scales, nonpositive inputs or undocumented encodings trigger reconciliation without examining outcome discrepancies. Cached BMI checks units; it does not fill missing inputs. Preserve ties within 1e−10 of −2 at the boundary.

The measured reference is the sample estimate and its paired-participant percentile bootstrap interval (2,000 resamples, seed 20261125); the same participant index supplies both readings to each resample. Three common generated seeds are within-program draws. A generated construction meets a scientific use when **every** primary seed is within the prespecified 3 percentage points for the event or 0.30 kg/m² for the mean. Persistent model failures remain in the assigned denominator. Small-sample uncertainty around the target may exceed the tolerance. Descriptive conditional matches do not establish population equivalence or out-of-sample transport.

Only after the program and draw seals and successful independent blind source-review seal may the evaluator read the measured workbook. The offline grader emits aggregate estimates and eligibility counts; participant-level and synthetic records remain in the private workspace. [Evaluator](evaluate_trial.py) · [Artificial-fixture tests](test_evaluate_trial.py)

