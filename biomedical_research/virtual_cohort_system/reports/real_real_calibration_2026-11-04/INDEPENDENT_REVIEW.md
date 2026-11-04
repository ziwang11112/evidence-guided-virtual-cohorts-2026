# Independent numerical review

**PASS — numerical assertions completed; a later reviewer scope-scanner false positive was resolved in a metadata-only continuation.**

The one full independent run rebuilt all 100 seeds (8400–8499), selection hashes and attempt logs, all 36 point metrics, every signed/absolute/symmetric discrepancy and all summary quantiles. It also checked the shared historical coefficient, marginal and relationship anchors. The completed 204 frames were 200 real halves, three fixed generated tables and one old full-reference anchor; there was no new generation or repeated frame calculation.

The original program then exited at line 458 when its scope scanner incorrectly treated the fixed `report.design.selection_hash_domains.rows` string (`real_real:rows:v1`) as patient rows. The actual traceback is retained in [INDEPENDENT_REVIEW_FAILURE.json](INDEPENDENT_REVIEW_FAILURE.json). The unchanged original code shows that all numerical and historical comparison calls precede this checkpoint. A numerical assertion failure would have exited earlier.

The follow-up [independent_review_continue.py](independent_review_continue.py) reads metadata, the aggregate REPORT and rendered table, and hashes frozen input bytes. It performs no row decoding, fitting or sampling. Its first scope pass also flagged the integer missing-value count named `commid`; that second field-name false positive is retained in [INDEPENDENT_REVIEW_CONTINUATION_FAILURE.json](INDEPENDENT_REVIEW_CONTINUATION_FAILURE.json). The final scanner permits only the exact hash-domain string and the exact nonnegative missing-count path, retains other identifier/membership prohibitions, and admits the known aggregate PNG/SVG figures produced solely from REPORT.json. There was one full numerical run and two metadata-only continuation attempts.

Every bound input hash remains unchanged after the audit, and the complete 36-metric displayed table matches REPORT.json. Output contains only original code, controls, aggregate statistics, counts, hashes and aggregate figures. The production report, original audit program and original read receipt remain untouched.

Numerical comparison tolerances were rtol=1e-9 and atol=2e-11. The exact comparison counter and maximum absolute difference were still in memory when the later scanner error ended the process; both are therefore null in the review record. They were not reconstructed or invented, and the clinical data were not reprocessed to recover them.

The calculations used independent pool enumeration and hash construction, SciPy QR regression, math.fsum means/sample SD, explicit linear quantile interpolation and SciPy correlations. A different linkage order and independent measurement/eligibility derivation reproduced the entire ordered selected frame. Production statistical functions were not imported or called.

BMI–glucose Pearson/Spearman are newly prespecified developmental diagnostics, not earlier holdout outcomes. Historical intervals remain unchanged. All 100 splits remain same-cohort development analyses; this audit does not revalidate biological utility or establish clinical validity, external transportability, equivalence, a scientific pass threshold or independent-cohort calibration.
