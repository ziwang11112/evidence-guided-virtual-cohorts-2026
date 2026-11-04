# New conference figures 4–5: captions and placement

These captions describe newly drawn figures, not the superseded v0.7/v0.9 graphics. All displayed estimates and intervals are copied from existing frozen aggregates. No rows, generator execution, regression fitting or new synthetic experiment was used.

## Figure 4 — A published longitudinal specification supports a complete virtual cohort

The two prespecified HRS interactions describe memory-score change per decade against the HbA1c spline below 6.5% (a) and at or above 6.5% (b). An Agent-authored recursive generator and the corrected published-law reconstruction each supplied three fixed-seed tables of 11,509 synthetic subjects at four visits (46,036 rows per table). Both constructions used the supplied aggregate model exports and method code. The same native R/lme4 analysis was applied to all six valid tables. Blue circles and purple squares show the 12 stored seed estimates and their model-conditional 95% Wald intervals; gray dashed lines show the two supplied source coefficients. Gray solid lines mark zero. Source uncertainty is recorded in the numeric binding but is not plotted here. The lower-branch negative relationship is retained; the weaker upper-branch estimates and significance decisions differ across constructions and draws. This is source-rich reconstruction and analysis preservation, not independent clinical validation or a method ranking. The full 16-effect supplement and the documented three invalid initial comparator draws remain part of the experiment record; no Agent table was regenerated.

Suggested Results lead: “The system also represented repeated measurements and executed the requested longitudinal analysis from published aggregate model exports.”

Placement: longitudinal use-case subsection. Use `fig4-longitudinal.pdf` in a full-width 7-inch figure; preserve the existing all-effect supplement. The compact figure does not replace the distribution and parser-incident record.

## Figure 5 — Generated data support scientific analyses while exposing a missing joint constraint

One Agent-authored model supplied three fixed 3,000-person tables. Panels (a–d) show all four nonintercept effects in the requested primary analysis, HbA1c ~ BMI + glucose + age + female; panels (e–g) show all three effects in the prespecified secondary analysis omitting glucose. Blue points are the three stored seed estimates, with conditional 95% HC3-t intervals. Dashed gray lines and shaded bands are estimates and 95% community-cluster CR1-t intervals from the exposed CHNS reference sample (6,631 participants; 218 communities). HbA1c effects are in percentage points, with predictor units shown on each axis. These interval types have different scopes: generated-data intervals condition on the fixed law and omit source, structural and transport uncertainty. Panel (h) displays exactly two previously computed analytical scenarios. Changing the unreported latent BMI–glucose correlation to 0.10 or 0.40 changes the primary BMI coefficient to +0.03422 or −0.01095 while retaining the marginal laws, all other bivariate laws and the secondary projection. The delivered model used 0.25. No connecting curve, new simulation or uncertainty bound is implied. This exposed-reference developmental analysis demonstrates partial scientific utility and a specific unresolved dependence assumption; it is not a new independent confirmation or an equivalence test. Initial and final stages alias the same three delivered tables and do not count as six experiments.

Suggested Results lead: “The final acquisition-to-generation case produced data for both requested analyses, but a conditional BMI effect remained sensitive to a joint relationship absent from the evidence.”

Placement: end-to-end scientific-use subsection. Use `fig5-scientific-use.pdf` at full width, followed by the targeted dependence limitation. Retain the existing real–real resplit context as a separate supplement; do not treat real-sample variation as permission to ignore mismatches.

## Numeric and implementation binding

- `FIG45_NUMERIC_BINDINGS.json` contains every plotted value, interval, source locator, input hash, output hash and construction/seed count.
- `render_use_cases.py` accepts only the three exact pinned aggregate inputs. It supports both local `work/` and public `reports/` layouts.
- Figure 4 preserves 12 fitted seed estimates and two supplied source coefficients; Figure 5 preserves 21 fitted seed estimates, seven reference estimates/intervals and two analytical sensitivity points.
- Generated blue: `#1678A6`; reference gray: `#737D86`; analytical scenario orange: `#B55A16`; published-law reconstruction purple: `#7E6AA2`.
- The bundled Python runtime lacked Matplotlib. Rendering used the already installed Python 3.12 runtime and Matplotlib; no packages or system settings were changed.
