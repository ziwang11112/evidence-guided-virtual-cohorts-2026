# KDD nearest-method comparison design

**5 November 2026 — design only; no new biomedical experiment has run.**

The selected comparison is the current evidence-qualified Agent law-construction workflow versus an independently reimplemented LLMSynthor with a declared biomedical evidence-to-macro adapter. Both receive the same curated evidence and the same complete-cohort analysis requests. The main endpoint is the scientific use of the final data.

- [Protocol and decisions](PROTOCOL.md)
- [Chinese explanation](DECISION_ZH.md)
- [Independent design review](PROTOCOL_REVIEW.md) and [hash-bound review record](PROTOCOL_REVIEW.json)
- [Machine-readable design and 20 scheduled native episodes](DESIGN_CONTRACT.json)
- [LLMSynthor paper/release audit](LLMSYNTHOR_IMPLEMENTATION_AUDIT.md) and [metadata](LLMSYNTHOR_SOURCE_METADATA.json)
- [G-Sim paper/release audit](GSIM_IMPLEMENTATION_AUDIT.md) and [metadata](GSIM_AUDIT_METADATA.json)
- [Existing-case readiness and earlier recommendations](LOCAL_READINESS_AND_PROTOCOL_REVIEW.md)

**Main planned scale:** two existing requests (ENSANUT glycemia and Turkana lipids), two workflows, five fresh complete episodes each: 20 scheduled final tables of 3,000 rows, 60 primary estimates. A complete LLMSynthor adaptive episode counts once; resampling its final proposal mixture does not create independent runs.

First complete the original LLMSynthor sampler/controller and input adapter, check fidelity on invented native frequency-table fixtures, and establish the actual model-dispatch route and costs. The official repository currently contains no algorithm implementation. The proposed 100-round schedule implies about 2,000 dependency/proposal calls across its ten main episodes before adaptation or repairs. That cost must be checked before execution release; no paid endpoint or HPC is enabled here.

G-Sim remains a relevant secondary summary-based structural-search control, not a scheduled extra arm. The completed CHNS summary/statistical comparison is retained and will not be repeated. Both primary target families remain exposed development references. Old frozen code/results are preserved; the new design does not turn them into fresh clinical confirmation.

The standalone protocol supersedes conflicting preliminary budget ideas in the local readiness note. Final independent design review is recorded separately. A reviewed design is not an implemented or numerically validated comparator.
