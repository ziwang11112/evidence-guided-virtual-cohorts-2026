---
name: analysis-guided-cohort
description: Turn a biomedical virtual-data request into task-specific scientific criteria and use tool-backed findings to choose evidence searches, generation checks and revisions. Applies to whole-cohort generation, variable enrichment and missing-value completion.
---

# Analysis-guided cohort construction

Produce data that support the user's intended scientific analyses. Use the task's information and execution contract, including its allowed literature retrieval and feedback. Keep the requested generation scope and output route; no particular model family, relationship sign, agent count or clinical endpoint is prescribed.

This is a project-local experimental skill. It does not replace an installed skill, implement an agent launcher, authorize new tools, or upgrade the frozen harness. Use its records outside a frozen candidate unless the supplied interface explicitly admits them.

## Define success in terms of the requested data use

Before inspecting candidate results, derive a small task rubric using [references/rubric.md](references/rubric.md). Bind criteria to the requested population, variables, analysis and allowed evidence. Preserve every requested analysis, including uses that cannot yet be justified. A user may disclose the research question and may permit reference statistics for calibration; classify that comparison accordingly.

Separate executable requirements, evidence-supported numerical checks and assumptions that affect interpretation. Do not invent a target sign, desired p-value, clinical tolerance or hidden answer. A reference sample estimate is not a known population constant. When a defensible success margin is unavailable, report the discrepancy and uncertainty without creating a pass threshold.

## Choose the next useful operation

Inspect what is already known before loading a procedure. Use [references/procedures.md](references/procedures.md) only for the needed operation: source replay, conditional variation, joint dependence, longitudinal structure or hypothesis-dependent generation. Each procedure identifies required inputs, an appropriate calculation and actions when inputs are missing. It is a decision aid, not a fixed statistical recipe.

Select a construction yourself. Compute the implications relevant to the requested analyses, using approved tools; mathematical checks of a declared law, empirical checks of a finite table and source-population replay are different assessments. A program's execution receipt does not replace any of them. For direct-row generation, evaluate the resulting table without inventing a population law or claiming certified tail moments.

## Act on findings

For each material finding retain: affected analysis, source or computed artifact, concrete observation, explanation status, next action and the check that could resolve it. Choose among a justified correction, focused retrieval, alternate construction, explicit sensitivity, retain or stop. Distinguish missing tools from missing source information and from a transfer assumption. Do not solve all three by adding arbitrary parameters or extra noise.

If a revision targets one criterion, recheck already supported criteria that its change can affect. Judge the final data and scientific analyses; more complete annotations are a separate process outcome. Keep the earlier artifact and its negative findings. Do not change acceptance criteria after a poor result; version an actual change in the user's scientific question separately.

## Return usable data with an honest use profile

Return the requested data/program and the compact criterion-by-criterion result, not a pooled quality score. Explain which analyses are supported at which evidence level and which are assumption-dependent or unassessed. An unknown relationship may be explored through stated scenarios rather than silently set to independence. Do not make an absent measurement look recovered for a real person.

An independent reviewer may apply the same rubric to raw permitted evidence and computed artifacts. The reviewer need not share the author's explanation, and agreement between agents is not a measurement. Respect the supplied budget; a valid retain or unresolved decision does not require another iteration.

## Stable criteria and evidence-bearing actions

Keep each requested analysis ID stable through the rubric and check record. Link a consequential choice to the criterion, the actual source or calculation, and the next action. After a change, name which dependent checks need repeating; a statement of intent is not a completed calculation. These workflow patterns are attributed in the pilot reuse note.
