# v0.7 follow-up: reproducibility and focused next step

3 November 2026 (America/Chicago). This follow-up implements public aggregate display reproduction and checks the feasibility of one optional extension. It does not alter the frozen v0.7 draft, original study scripts, outputs or historical receipts.

## Completed work

- Added the [public reproduction entry point](../docs/REPRODUCING_MANUSCRIPT_v07.md) with 21 pinned inputs, a standard-library verification mode and a full plot-rendering mode.
- Reconstructed all 45 rounded numeric cells in Tables 2-4 and checked 306 cross-sectional seed values plus 96 HRS coefficient estimates. Table 1 prose remains editorial content copied from the draft; numerical scope is exported separately.
- Redrew Figures 2-4 and S1 using the retained aggregate plotting algorithms. Figure 1 is explicitly a copied schematic, including its editable source.
- [Independent review](../reproducibility/INDEPENDENT_REVIEW_v07_2026-11-03.md) verified two full runs, repeat-output identity, original PNG identity in the tested environment, numerical reconstruction and refusal of invalid inputs/output paths. No claim of cross-platform image identity or clinical rerun is made.
- Reviewed exactly three already available alternate-outcome leads in the [feasibility audit](EXISTING_REFERENCE_FEASIBILITY_v07_2026-11-03.md). Zero cases were admitted. No participant records, target effects, new original studies or downloads were used by that audit.
- Updated the repository/project/manuscript navigation and appended the latest completed-study and metadata-only disclosures to the exposure registry.

## Decision

**Continue the paper under its current evidence-to-model and analysis-use contribution. Defer the optional prospective extension.** There is no basis to present a reused cohort family as a new independent cohort, and no need to launch another collection campaign for the current bounded claim.

The empirical narrative remains: external study fragments can numerically guide a joint model; richer information can improve several requested analyses while leaving important failures; a detailed published model permits a more complex longitudinal data product. The procedure is reusable across these requests. The evidence does not show universal data equivalence or a benefit from every revision stage.

The three principal settings retain separate meanings: CHNS/ENSANUT are developmental external-evidence comparisons; the separate CHNS summary-access experiment tests reconstruction; the HRS example reconstructs a supplied public model. Historical enrichment/direct output and failed studies remain supporting evidence with their original qualifications.

## What to do next

1. Review the completed manuscript around the Agent's scientific decisions, the analysis-use results and the worked source-to-model example. Keep all six main-study endpoints and the HRS weak-effect/upper-tail exceptions visible.
2. Complete authorship, funding, dataset access/ethics, AI-use and software/data-availability declarations from actual author/project information.
3. Choose the intended article type and prepare its formatted manuscript and publication-size figures. This requires a current venue/instructions check when the target is chosen.
4. Add an experiment only when choosing a specific stronger claim. A fixed-corpus extraction audit addresses assisted evidence processing; a separately admitted prospective reference addresses new-target usefulness. Neither is automatically required or started.

## Cost and boundaries

This unit adds documentation, metadata inspection and aggregate numerical/plot reproduction. It performs zero new Agent constructions, clinical fits, reference-effect analyses, participant/generated-table reads, downloads, model training, paid API calls or HPC jobs. Counts of independent review checks are implementation evidence, not extra scientific sample size.

The reviewed draft SHA-256 remains `63a3f705f86a93e0b07a3b8da08687bb0652822300e1169c29ce84b16721baf6`. Historical presentation checks are not relabelled as actual redraws; the new reproduction review separately records that capability. Public publication is limited to original code, documentation, metadata and aggregate records.
