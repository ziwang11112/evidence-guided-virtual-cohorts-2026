# Stage 1: bounded development execution

**Completed:** 420/420 cohorts and all 7,700 analysis records. Read [RESULTS.md](RESULTS.md), [DECISION.md](DECISION.md), and the [independent postrun review](../stage1_review/postrun/POSTRUN_REVIEW.md). All outputs are frozen; commands below describe the workflow and must not be rerun into occupied output directories. Fit warnings and model-assumption limitations remain material despite successful execution.

This controller implements the frozen A0 whole-cohort synthesis experiment. Case A is Ross (75 people, five visits), B is Travers (12 paired adults), and C is He (44 paired pediatric completers; 43 glucose/TG pairs). Builders see anonymous case labels and source-only packets. All cases remain exposed development, regardless of fresh builder isolation.

`protocol_freeze.json` hashes the exact protocol, 55-entry analysis registry, source checker, generator/controller implementations, delivered packets, and custodian reference inputs. Original studies and previous experiment files are untouched. Source and reference provenance is retained in `custodian/provenance.json`. Do not upload patient reference files to GitHub.

The nine initial requests are at `runs/{case_a,case_b,case_c}/build_{01,02,03}/initial_v3/REQUEST.md`. Each fresh builder receives only its exact run directory's allowlist. It writes `generator.py` and `decision.json` using the delivered template. Return a DataFrame from `generate(n, seed, evidence, context="target")`; the controller saves labelled CSVs. Ordinary/initial candidates use `target`; proposed candidates can declare one to three named contexts.

Commands, from the workspace root:

```powershell
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/test_stage1.py
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/runner.py checkcandidate RUN
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/runner.py stagebranch INITIAL_RUN ordinary
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/runner.py stagebranch INITIAL_RUN proposed
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/runner.py executefinal BRANCH_RUN
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/runner.py stagestatistical
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/runner.py checkcandidate STATISTICAL_RUN
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/runner.py executefinal STATISTICAL_RUN
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/audit_inventory.py
python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/runner.py evaluate
```

Root independent review must precede production final-cohort execution. Never evaluate until all planned branches/reference runs have completed or their documented failure status is accepted. The evaluator does not call builders. Its output must not return to either branch in this experiment.

One branch revision is scheduled within a maximum of two. Common-parent code, decisions and source feedback are byte-identical across ordinary and proposed siblings. Retain failed checks; never edit executed runs. A repair uses `stagebranch ... --version v2` or, for an initial interface repair, the Python `runner.stage(case_id, build_number, version="v2")` API. Record the repair and any additional source allowance before retrying. Scientific changes after target opening require a separate experiment.

The source envelope is a diagnostic (3 sampling-SE widths around supplied mean and SD), not a validation/equivalence criterion. Schema, support, person/visit keys, observation counts, reproducibility, local RNG and evidence preservation are mandatory. Seed diversity and evidence-use probes are reported. No adversarial isolation guarantee is claimed.

The fixed statistical arm uses one prespecified copula family with rho 0/.4/.8 sensitivities and 7/7/6 of twenty total cohorts. Its shared-person factor yields a positive-semidefinite dependence kernel. Endpoint factors are independent. These contexts remain separate; neither the best rho nor a mixture is selected from target performance.

The evaluator retains every analysis and per-draw failure. Thirty-one Ross replay terms are separated from four proxy terms by family; paired mean reconstruction is separated from reserved paired covariance/uncertainty, and six cross-endpoint change correlations remain reserved per paired case. Whole-cohort samples are never Rubin-pooled or stacked as extra observed patients. No generic clinical equivalence cutoff is invented. Reproducing supplied means is not method success.

Ten contract tests plus a complete artificial-data reporting test and a toy full execution passed before production. `toy_smoke_audit.json` retains the compact smoke result without any target analyses. Model/provider/token metadata are unavailable through the current subagent tool; this limits model-cost comparisons. Controller timings measure local execution, not isolated model latency.
