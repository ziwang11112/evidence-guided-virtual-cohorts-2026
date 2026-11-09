# Reused workflow patterns and provenance

This developmental pilot tests whether task-specific criteria and reusable scientific procedures change the usefulness of generated biomedical data. A reusable procedure is not a fixed clinical relationship, and a rubric is not an answer key.

## AutoSciRub

The inspected repository revision is [2c6c58392ee6399e08f2526e35176f0e2c716e16](https://github.com/zjunlp/AutoSciRub/commit/2c6c58392ee6399e08f2526e35176f0e2c716e16), dated 17 October 2026. The repository LICENSE is MIT. We adapt two prompt-level workflow patterns in original wording:

1. Connect the user instruction to stable goal identifiers, then connect each goal to evidence, a calculation and a checkable artifact. Implementations: [rubric-skeleton-induction](https://github.com/zjunlp/AutoSciRub/blob/2c6c58392ee6399e08f2526e35176f0e2c716e16/plugins/autoscirub/skills/rubric-skeleton-induction/SKILL.md) and [criterion-synthesis](https://github.com/zjunlp/AutoSciRub/blob/2c6c58392ee6399e08f2526e35176f0e2c716e16/plugins/autoscirub/skills/criterion-synthesis/SKILL.md).
2. Map a failed criterion to a concrete action and identify other checks affected by a change. Implementations: [criterion-level-verification](https://github.com/zjunlp/AutoSciRub/blob/2c6c58392ee6399e08f2526e35176f0e2c716e16/plugins/autoscirub/skills/criterion-level-verification/SKILL.md) and [targeted-revision](https://github.com/zjunlp/AutoSciRub/blob/2c6c58392ee6399e08f2526e35176f0e2c716e16/plugins/autoscirub/skills/targeted-revision/SKILL.md).

The first pattern is exercised in construction. The second informs the reusable skill, but this pilot supplies no numerical feedback or revision round and therefore does not test feedback repair. No third-party code is installed, vendored or executed. We do not treat the repository's JSON schema validation as statistical verification. Its portable benchmark adaptation explicitly distinguishes structural validation from benchmark performance. The [paper](https://arxiv.org/html/2608.31076v1) reports scientific-agent benchmark results, not biomedical synthetic-data validation; those results cannot be transferred to our task or assigned to this inspected release.

## SkillCoach

[Appendix D of SkillCoach](https://arxiv.org/html/2607.01874v1#A4) links procedural assessments to observed trajectory events and separates process scoring from outcome verification. We adapt the modest requirement that a claimed calculation has a retained command and result. We did not verify an author code repository or software license; this is a paper-level influence, not an audited software dependency. We do not import training, gold-skill oracles, weights or acceptance thresholds.

## Local contribution being tested

The common installed evidence-cohort-generation skill already requires source use, assumptions and provenance. The experimental addition supplies analysis-specific criteria and reusable procedures for conditional variation, joint dependence and source replay. These are adapted to the scientific use of virtual data, rather than scored as report-writing quality. The outcome is the final data's analysis profile. The number of completed checklist entries is secondary and cannot establish clinical validity.

This is attribution and a small transfer test, not a claim that rubric prompting, skills or verification loops are new.
