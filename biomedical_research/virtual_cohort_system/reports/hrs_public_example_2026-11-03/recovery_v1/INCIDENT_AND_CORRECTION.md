# Native extraction incident and source-only correction

**The initial native preparation/preflight PASS is overturned.** The native package used incorrect HbA1c model parameters and is not a valid implementation of the intended published HRS law. The native-adapter author introduced the parser defect and failed to detect it during preparation; the coordinator's preflight review also did not detect it. Correct math helpers, valid contracts and intact source hashes did not establish model-specific parameter fidelity.

The original export uses CRLF line endings. The original parser attempted to end the Gamma section with the LF-only string `Call:\nmultinom`. That delimiter was not found, and `split(...)[0]` silently retained later model sections. Repeated term names from the CSES and memory tables then overwrote the Gamma entries in a dictionary. The final key-set check passed because every expected Gamma term still existed. Both the numeric values and their apparent source locators were wrong for the Gamma model.

The coordinator reported that the three initial native runs had an HbA1c mean near 0.94, no observations at or above 6.5, and two dropped mixed-model columns. This report records those findings as coordinator-provided incident context; this recovery author did not inspect generated rows or independently reproduce those outcome diagnostics. The three Agent runs reportedly passed their native fits and independent GLS checks. None of these postrun results determines the correction: all corrected values come directly from the original public Gamma table.

| HbA1c term | Incorrect initial value | Correct source value | Correct source SE | Source line |
| --- | ---: | ---: | ---: | ---: |
| Intercept | 0.674696 | 1.741085 | 0.005083 | 42 |
| Baseline age60 | -0.180141 | 0.002538 | 0.001564 | 43 |
| Male | -0.351786 | 0.008013 | 0.003072 | 44 |
| Black | -0.478198 | 0.055273 | 0.004517 | 45 |
| HS | -0.389693 | 0.011442 | 0.004932 | 46 |
| LessThanHS | -0.837970 | 0.039171 | 0.006009 | 47 |
| CSES | 0.051445 | -0.008943 | 0.001582 | 48 |

The correction lives only in `recovery_v1/`. The original parser, source packet, candidate, freeze/release records, generated attempts and results remain unchanged. `parse_source_corrected.py` uses line-based sections with required unique boundaries and table headers, terminators and exact term order; duplicate or unexpected rows are errors. Scalar and covariance extraction is restricted to the corresponding model. LF/CRLF equality and six malformed-input regression checks pass.

`independent_source_audit.py` does not import that parser. It reads fixed source lines directly after verifying the exact original export SHA256, checking all 36 coefficient/SE pairs, source-model locators, all 28 demographic cells and remaining active scale/covariance/design parameters. It verifies both the corrected packet and candidate evidence/specification. The direct-line method is deliberately separate from section-boundary parsing. `REPAIR_AUDIT.json` records the results, changes and input/output hashes.

The native generator remains byte-identical, SHA256 `68a901ff3cbec008d4a5d18fa4322852fe4c883bf87ac742fbc6ce5bcc558765`. The seven HbA1c coefficients, SEs and their provenance are corrected; dispersion, every other model parameter, assumptions and sampling mechanics remain unchanged. There is no new statistical family, outcome calibration, seed selection or scientific revision.

All six initial attempts remain spent. The coordinator plans a separately released, bounded three-attempt native recovery, which would increase the orchestration budget to nine attempts in total. No recovery generator call or clinical fit occurred during this preparation. Recovery success is not presumed. If a valid comparison is later reported, the invalid initial native runs and technical deviation must remain disclosed rather than counted as predecessor performance or silently replaced.

The independent Agent implementation review is not rescinded by this native-only defect: it compared the Agent's coefficients directly against the first Gamma rows, and the corrected native Gamma values now agree with those same source values. That review still establishes code/source fidelity only, not clinical validity or a performance conclusion.
