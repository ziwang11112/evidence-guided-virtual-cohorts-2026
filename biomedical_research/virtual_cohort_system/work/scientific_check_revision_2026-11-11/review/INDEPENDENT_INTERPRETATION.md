# Independent interpretation of the scientific-check revision experiment

**The checks found real defects; their repair did not produce a broad improvement in scientific analysis quality.**

The independent source/code audit was frozen before opening the numerical comparisons. Independent arithmetic then passed13,419 checks over72 final and36 initial saved tables, with maximum discrepancy9.33e-14. No model calls, generator runs or clinical reference fits were repeated.

| Comparison | Initial | Generic review | Structured review | Historical sample reference |
|---|---:|---:|---:|---:|
| R04 K02-TC-BMI | 14.6148 | 14.1064 | 13.3636 | 5.6831 |
| R04 K02-HDL-BMI | -1.4896 | -1.4896 | -1.5110 | -4.6230 |
| R04 K02-LIPID-RESIDUAL | 0.3590 | 0.3594 | 0.3584 | 0.5121 |
| R04 total_cholesterol.sd_sample | 36.6868 | 36.5033 | 36.4175 | 42.8466 |
| R04 hdl_cholesterol.sd_sample | 13.1331 | 13.1331 | 13.1247 | 20.1756 |

Lipid BMI slopes are mg/dL per5 kg/m²; lipid SDs are mg/dL. These are three-seed means, not independent participants or population ground truth.

Both R04 arms replace an infinite-moment ideal TC law with a finite-moment law. Structured review additionally models TC as positive HDL plus non-HDL. Its TC-BMI estimate is closer to the sample reference, but residual correlation remains about0.36 versus0.51 and both lipid SDs remain low. This supports a genuine validity repair, not a general joint-quality improvement.

Both R07 arms move rounding before pressure-pair acceptance. Every saved output is unchanged, proving that the rare failure branch was not encountered in these seeds. The structured version removes a retry cap, exchanging a capped failure for theoretically unbounded loop time.

Twenty episodes explicitly retained v000. Including R07,66 of72 final tables have exactly the initial table hash. R08 has one HDL>TC row in seed54003 in each arm, unchanged from the original. The two appearances are the same reused output, not independent failures.

Generic review used169 calls ($2.026833); structured review used174 calls ($2.846299). Total343 calls cost $4.873132 in recorded tariffs, with zero unknown usage. This excludes historical construction cost and is not an invoice reconciliation.

Keep the reliability checks and analysis-level provenance, but describe their scope honestly. The unit establishes that Agent-directed review can detect and repair particular code/law problems. It does not establish structured-review superiority or solve missing conditional dependence. No further target-driven edits or regeneration are warranted on this revealed unit.
