# Method decision from source and interface review

31 October 2026. Design finding, not a new generation result.

## A concrete context mismatch

Oya et al. ([original methods, p.942](https://www.jstage.jst.go.jp/article/internalmedicine/53/9/53_53.1580/_pdf), DOI 10.2169/internalmedicine.53.1580) supplies age/sex/center BMI and fasting-glucose summaries for Japanese checkup attendees aged 30–79, excluding diabetes (known history or FPG at least 126 mg/dL) and other specified conditions. The potential NAGALA reference has different selection rules that still require original-method confirmation. Applying another population's marginal mean directly to a selected target is an approximation, not a same-context replay.

The current [whole-cohort feedback adapter](../../../docs/WHOLE_COHORT_FEEDBACK.md) explicitly evaluates an already generated **target task population** with identity measurement. It verifies execution/statistic linkage, but does not reconstruct each source population, implement another source's selection process, or transform measurements. Its approximate-check label is therefore essential. This is a documented scope limitation, not a discovered implementation defect.

## Implication for the next experiment

Do not turn target-versus-source marginal discrepancies into an automatic calibration loss. First decide whether the prospective case needs source-context replay or merely transparent approximate diagnostics. If claiming source-conditioned evidence handling, implement and independently test that operation: reuse the Agent-authored scientific construction under frozen, explicitly declared source contexts; calculate each paper's actual estimand; bind resulting output to that context. A comparator should change this operation while holding evidence, structure and budget fixed when possible. Do not claim such a capability from the existing adapter alone.

The Agent, not the root, must choose any parent-distribution and transport assumptions. The protocol may specify known eligibility and units. Clipping or changing a fitted slope to reproduce a revealed target is not a valid repair. Conditional generation and a declared selection model are distinct admissible approaches whose assumptions and consequences must be visible.

## Source checks still needing caution

Oya Table2's printed male BMI-on-age B, SE and standardized coefficient raise a scale-consistency concern. The scout checked the original visual table; it is not merely an OCR artifact. Do not silently correct a decimal or invert a regression. The male center-adjusted FPG-on-age coefficient is more interpretable, but transporting it to a more selected target remains an assumption. Female menopausal subgroups are not equivalent to an age cutoff without supporting evidence.

No HbA1c, insulin-column or diabetes-survival model is admitted from these four newly scouted papers merely because the candidate workbook may contain such fields. Select a modest, source-supported analysis use before expanding variables. Missing joint evidence can motivate an explicitly assumption-sensitive pilot; it does not justify claiming full joint identification.

## Current decision

Proceed with metadata and source-semantic admission, then freeze a limited protocol. Do not yet launch builders, calibration, a target-effect analysis or the optional controlled experiment. All previous target results remain closed. There is no new empirical performance claim in this note.
