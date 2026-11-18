# Controller runbook

Run from the virtual_cohort_system project root. Builder sees only work/m15a_direct_rows_2026-10-30/visible; never give it the whole work directory or controller history. Spawn a fresh context using visible/INITIAL_PROMPT.txt and the exact visible directory path. Initial evidence/checks are already supplied. No generated.csv exists during preparation.

After initial builder completion:

    python -m cohort_harness validate --bundle work/m15a_direct_rows_2026-10-30/visible/bundle --candidate initial
    python -m cohort_harness freeze --bundle work/m15a_direct_rows_2026-10-30/visible/bundle --candidate initial
    python -m cohort_harness verify --bundle work/m15a_direct_rows_2026-10-30/visible/bundle --candidate initial
    python work/m15a_direct_rows_2026-10-30/controller.py feedback

Capture CLI failures in private/controller_events.jsonl or a separate append-only run log. Do not give additional numerical diagnostics. The feedback command runs the existing direct_rows_validation adapter; no code execution or runtime backend is needed. The seed value in its receipt is inert for a literal table.

Send the same builder visible/FOLLOWUP_PROMPT.txt plus the actual feedback path. It may author one revision or choose retain. For retain, copy initial CSV/model bytes exactly into final; for revise, do not modify the builder's table. Controller copies approved evidence.json into final, exact initial_feedback.json into final/check_artifacts/initial_feedback.json, and writes checks.json with source_only scope, one factual feedback record and artifact SHA256. A failure record may have status fail even though the feedback was successfully calculated. Bind truthful revision.json outside candidates using the exact schema in the template. The builder's actual decision.md goes in final. Record all copied files and their byte-identical source hashes. The revised candidate may differ in model and data only as explicitly authored.

Then:

    python -m cohort_harness validate --bundle work/m15a_direct_rows_2026-10-30/visible/bundle --candidate final
    python -m cohort_harness freeze --bundle work/m15a_direct_rows_2026-10-30/visible/bundle --candidate final --parent initial --revision work/m15a_direct_rows_2026-10-30/visible/revision.json
    python -m cohort_harness verify --bundle work/m15a_direct_rows_2026-10-30/visible/bundle --candidate final
    python work/m15a_direct_rows_2026-10-30/controller.py evaluate

The final report is private/evaluation/final_report.json. Evaluate it only after both versions freeze. It must never be fed back to the builder. If initial/final is invalid, log the failure and stop without hidden scoring. Do not run prepare_metadata.py again, alter precommitted files, delete budget receipts, or repeat an evaluation to choose a favorable table. verify-precommit is read-only. Preparation ran no candidate evaluation and did not generate rows.
