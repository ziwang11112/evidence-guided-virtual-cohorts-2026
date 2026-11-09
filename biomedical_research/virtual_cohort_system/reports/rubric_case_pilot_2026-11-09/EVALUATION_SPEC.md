# Construction-stage pilot: evaluation specified before authors

## Question

Can analysis-specific criteria and a reusable scientific procedure guide change final-data usefulness when the source evidence and requested analyses are fixed? This construction-only pilot narrows one implementation decision; it does not redefine the overall system as a closed-literature generator. Retrieval and feedback remain valid system capabilities, but are held fixed here.

## Design

Two existing cases: glycemia (H) and lipids (L). Each has A: installed skill under a shared minimal construction interface; B: A plus a supplied task rubric; C: B plus a reusable analysis-guided skill. B and C receive byte-identical case rubrics. All receive identical admitted evidence, task population and scientific questions. Authors choose the scientific laws and parameters. No patient rows or target estimates are supplied. No new evidence acquisition occurs. The root has historical exposure to aggregate references, so all results are developmental.

One fresh author per arm and case; six constructions total. Three scheduled draws per construction, seeds 9301, 9302, 9303; 3,000 rows per draw; at most 18 physical attempts, including failures. No trial sampling or source-feedback revision. All six submissions and executable implementations are sealed before sampling. Authors may self-check their interface before final submission, but no post-submission repair or result-dependent retry is allowed. A failed submission or execution is retained as an outcome; a blocking infrastructure defect stops the batch rather than authorizing extra clinical draws.

Response count, source access, available tools, interface and draws are matched. Token telemetry is unavailable, prompt lengths differ, and this is not a strict compute-matched experiment. One author per arm/case confounds instruction condition with author variation. Draws from one program are not independent author replications. These observations can guide the next design, not establish general superiority.

## All scientific analyses

The copied ENDPOINT_CONTRACT.json and case request.json files are authoritative. H includes all three age/BMI coefficients from the specified reduced/full HbA1c models. L includes the age/sex-adjusted BMI coefficients for HDL and total cholesterol and their adjusted residual correlation. Keep the same operators, units, selection and case weighting as the existing trusted evaluators.

For every successful table report the coefficient/correlation, generated-data uncertainty where implemented, the corresponding real-reference estimate and supplied uncertainty, signed discrepancy and direction agreement. Report every scheduled seed and every failure. Display arm-level seed means and ranges as variability of draws from that program, not confidence in the arm's performance. Do not aggregate incompatible clinical coefficients into one quality score or select a winning seed.

Include every diagnostic in ENDPOINT_CONTRACT.json: marginal moments and quantiles, conditional residual scale, and case-specific adjustment diagnostics. These explain scientific-use differences; they are not substitutes for the requested analyses. A real sample statistic is an uncertain reference, not a known population truth. Existing coefficient intervals are not intervals for unrelated means or scales. No equivalence margin, pass threshold or desired target sign is invented.

## Process interpretation

Separately inspect whether each author used admitted quantitative evidence, distinguished pooled from adjusted relations, computed implications, and recorded unsupported assumptions. Use the actual source, specification, program and retained command/results; prose or rubric completion alone is not evidence of good generated data. Matching an input statistic is calibration; matching an external reference here is developmental agreement. Correct arithmetic does not establish population transportability.

## Reading the result

Compare A/B/C within case across all requested analyses. If C improves one analysis but worsens another, report the tradeoff. If B performs as well as C, prefer the simpler intervention provisionally. If results do not improve, do not add more agents or criteria to rescue this batch. A favorable pattern justifies a separately designed replicated construction test; no change is automatically installed in the global skill or frozen method.

References are read by the evaluator only after all author outputs are sealed and all scheduled attempts are closed. The evaluator consumes previously saved aggregate references and newly generated local tables; it does not read or refit patient-level data. Independent review covers the protocol and implementation before execution and the aggregate calculations after execution.
