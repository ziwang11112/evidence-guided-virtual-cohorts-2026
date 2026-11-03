# Methods factual review

Status: **needs_edit**. Reviewer: `/root/main_review_g7`.

Reviewed `MAIN_STUDY_METHODS_2026-11-03.md` against the frozen procedure, `RELEASE.json`, and the two cases' task/profile/analysis-definition metadata. No clinical references, generated tables/results, experiments or tests were used. Manuscript edits are left to the coordinator.

1. **Line 25 — distinguish scheduled attempts from successful deliveries.** Replace the first sentence with: “Each construction was assigned three prespecified final attempts (seeds 5101, 5102 and 5103), each scheduled to produce 3,000 rows, giving 72 final slots.” The release fixes 24 × 3 final attempts and permits failures; it does not itself establish 72 successful tables.

2. **Lines 33, 37 and 41 — reconcile completed versus pending evaluation/audit language.** Use procedural wording without asserting unreviewed completion:
   - Line 33: replace “Evaluation reported each prescribed regression coefficient” with “The prespecified evaluation reports each prescribed regression coefficient”.
   - Line 37: replace the first two sentences with: “The prespecified independent audit recomputes the generated-table statistics using a separately written implementation with independent regression and weighted-summary arithmetic, checks frozen reference-aggregate mappings and rechecks the constructor-first contrasts. It does not regenerate rows or reopen model selection.”
   - Line 41: replace “Final results, failures and independent recomputation remain pending until the global closure requirement is satisfied.” with “The protocol requires global closure before common reference evaluation and independent recomputation.”

These are wording corrections to the frozen design and internal status claims. They require no method expansion or additional experiments.

Manuscript SHA-256: `008d823e9cbe9dfd0096b95d265db1a14a96061d0561fcbf323b449ca6e5c6d1`.
Release SHA-256: `796fb50db7fc49c0b0195e596182a3550816938f5d8e1d28e859bf267ee78aad`.
