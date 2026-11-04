# Independent recovery v1 review

**PASS: corrected source parameters, unchanged native law and bounded recovery controller.** No recovery generator, model fit or generated-row read was performed by this review.

Direct reading of the exact SHA256-pinned original export verified all **36 coefficient/SE pairs**, the 28 demographic cells and count normalization, Gamma dispersion, CSES residual SD, memory variance/SD/correlation inputs, and their use in the active corrected candidate. This reviewer did not import the new section parser or its independent-audit module. The retained LF/CRLF equivalence and six malformed-input rejection records were inspected, not rerun.

## Source-only correction

| Gamma term | Invalid old estimate | Correct source estimate | Correct SE | Original line |
|---|---:|---:|---:|---:|
| (Intercept) | 0.674696 | 1.741085 | 0.005083 | 42 |
| base.age60 | -0.180141 | 0.002538 | 0.001564 | 43 |
| sexMale | -0.351786 | 0.008013 | 0.003072 | 44 |
| raceBlack | -0.478198 | 0.055273 | 0.004517 | 45 |
| educHS | -0.389693 | 0.011442 | 0.004932 | 46 |
| educLessThanHS | -0.837970 | 0.039171 | 0.006009 | 47 |
| cses | 0.051445 | -0.008943 | 0.001582 | 48 |

The corrected generator has exactly the original bytes (`68a901ff3cbec008d4a5d18fa4322852fe4c883bf87ac742fbc6ce5bcc558765`). Non-HbA1c parameter groups, dispersion and assumptions are identical; only seven coefficient/SE/source-locator objects and their corresponding evidence records change, together with the explanatory provenance text. No effect size was selected using generated outcomes.

All **58 original release file commitments** still match, including the old invalid native candidate, original Agent candidate and evaluator. The old preflight PASS is explicitly overturned in the repair documentation; it is not silently rewritten.

## Controller and budget

The revised recovery controller requires an explicitly released record, its original-release binding and committed files. It allows exactly three additional native slots at 6101/6102/6103, with no Agent redo. Exclusive reservations and exact closure/attempt/seed/release checks prevent silent slot reuse. All three generation attempts close before any native fit. Each successful draw receives at most one unchanged native evaluation (300-second subprocess cap, 325-second host cap), followed by conditional GLS checking. Exceptions and nonzero/partial outputs are retained without optimizer or generation retries. The protocol explicitly reports six original plus three additional physical attempts and prohibits further recovery.

The remaining coordinator step is to copy/freeze these reviewed candidate bytes and bind the new release. The JSON provides all file hashes. This review does not predict scientific success, reopen the old six slots, or certify the original patient distribution. A failed correction must close this comparison rather than start another allocation.
