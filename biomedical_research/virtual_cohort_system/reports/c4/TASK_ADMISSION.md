# C4 task admission and frozen information boundary

This is a new controlled artificial benchmark. It does not contain real patients,
literature evidence, a medical target, or a claim of new biomedical discovery.
All three generated columns are invented neutral standardized measurements.
Each table contains exactly 4,000 local fictional rows in row_id,x,y,z order.

## Visible artifacts proposed for controller admission

- visible/task_a/source_contract.json: all means 0, all population SDs 1; Pearson
  population correlations X,Y = 0.30, Y,Z = 0.60, X,Z = 0.20. The admitted Gaussian
  family and these parameters fully identify its artificial joint law.
- visible/task_b/source_contract.json: the same means, SDs, X,Y and Y,Z marginals.
  The Gaussian X,Z dependence is explicitly unknown and unidentified. No value or
  independence assumption is admitted. There is one byte-identical visible packet
  for every compatible hidden world; candidates do not receive a world assignment.

The fixture custodian proposes these artifacts; the root/controller must inspect
and register their exact hashes using the harness registry before the author starts.
This document is not a fabricated registry approval. The source contract is a
synthetic source fixture, even if a harness compatibility enum says published_evidence.

## Source criteria and comparison

All constructed moments are exact artificial population definitions, not source
standard errors or confidence intervals. The table estimators are arithmetic means,
sample SDs (ddof=1), and Pearson correlations. Absolute tolerances are 0.10 for means,
0.10 for SDs, and 0.05 for correlations. These are engineering tolerances on this
standardized synthetic scale, not clinical acceptance limits.

The fixed denominator is every source check: 9 per Task A table and 8 per Task B
table. Aggregate loss is the arithmetic mean of squared error/tolerance over all
fixed checks and all three election seeds, using precisely the same formula for
every method. Missing, invalid, or failed checks cannot shrink the denominator;
they produce infinite loss and a failed numeric gate.

Protected uses are exactly every admitted correlation: three in A and two in B.
The use gate requires each protected error to be within its own tolerance on every
one of the three election seeds. It must not average away a failed seed or introduce
any unreported relationship. The full numeric source gate separately requires every
fixed source check to pass on all three election seeds. The protected-use method
adopts a proposal only with strict aggregate-loss improvement over the initial and
all protected checks passing; otherwise retain the initial and report its protected-use
qualification flag. The method controller fixes remaining comparison/tie rules
before election outputs are inspected.

The methods are baseline retain, minimum aggregate source error, and a
source-protected-use gate. Every method receives the same initial candidate and
three proposal opportunities. Retention and duplicate/no-op proposals are allowed;
the protocol never requires an intentionally poor baseline or artificial diversity.

## Fixed execution schedule

- Initial feedback seeds: 24101, 24103, 24107; 2 tasks x 1 initial x 3 = 6 runs.
- Election seeds: 24203, 24209, 24223; 2 tasks x 4 pool members x 3 = 24 runs.
- Untouched test seeds: 24301, 24307, 24317; 2 tasks x 4 pool members x 3 = 24 runs.
- Total 54 generation runs, each n=4,000. All 24 untouched-test tables remain in
  the fixed report, even when selectors choose the same candidate.

No rerun, discarded seed, outcome-selected world, extra proposal, web access,
paid API, training, or real patient data is authorized by this task packet.

## Custody and release

Hidden laws, analytical answers, endpoint operators, numerical-fidelity bands, and
scoring rules are fixed inside custody before candidate construction. They must not
be read by the author, selectors, or feedback controller before both task selections
are sealed. Held-out operators, values, errors, signs, scores and world-specific
results are never candidate feedback. The root may inspect this admission document,
visible source contracts and hash-only commitment metadata without opening custody.

The custodian analytically verified positive definiteness and algebra without
generating rows or importing candidate code. TASK_COMMITMENT.json binds the visible
and hidden artifacts. Reveal and export of the hidden truth/evaluator are permitted
only after selector sealing, all untouched-test table commitments, and root audit.
All compatible hidden worlds are reported; no probability weights or preferred
world are inferred. Numeric fidelity and direction are reported separately and
neither establishes clinical usefulness, causality, or population transport.
