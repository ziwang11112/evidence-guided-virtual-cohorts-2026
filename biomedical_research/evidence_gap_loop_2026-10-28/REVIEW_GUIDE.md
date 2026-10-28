# Common independent review rubric

Apply the same rubric and scope to each construction. Reviewers receive no reference HDL values, target analysis results, other constructions, or feedback from another review. Each initial review uses a fresh context. Its final code/source check may reuse that same context after the builder's one revision turn.

Allowed reads: the assigned run's candidate files, registered approved artifacts in its literature session, its request, the common builder guide/runner interface, and shared descriptive metadata. Do not read observed participant CSVs, custodian files, results or another run. Do not search for additional papers yourself: any scientific retrieval recommendation uses the builder's remaining budget through its own gateway. You may execute reviewed code on invented inputs only.

## Review priorities

1. Verify that source estimates, units, sample definitions, adjustment, SEM/SD and transformations agree with the cited location. Distinguish reported quantities, assumptions and source-context mismatches.
2. Verify parameter provenance and code/spec agreement. Check numerical expressions, distribution parameterization and conditional variation. Read code before executing; use the controller's static check and synthetic inputs. Report that static review is not a sandbox.
3. Identify at most a few consequential scientific limitations: whether the evidence supports the intended individual conditional relationship, whether source/measurement differences have been silently treated as individual residual noise, and whether absent information is being portrayed as an established effect or absence.
4. Give actionable feedback grounded in this candidate's own evidence. A useful challenge names an alternative compatible interpretation and obtainable distinguishing information. Do not require splines, sex interactions, a particular slope, or any expected target result. Do not insist on unsupported additional complexity.
5. Separate implementation/extraction errors from openly assumed, currently unvalidated scientific relationships. An honest limited model may be executable for the pilot even when its analytical utility is uncertain.

The purpose is to permit meaningful source-supported revision, not to hand the builder a superior biological model from another construction or to optimize unseen target answers.

## Required initial review artifact

Write the assigned review JSON outside `initial/`; do not modify the candidate. Fields:

```
{
  "summary": "Concise source/code/scientific assessment",
  "execution_allowed": true,
  "generator_sha256": "actual current generator hash",
  "model_spec_sha256": "actual current specification hash",
  "evidence_sha256": "actual current ledger hash",
  "candidate_freeze_sha256": "actual initial freeze receipt hash",
  "findings": [
    {
      "id": "F1",
      "type": "implementation | extraction | evidence_gap | applicability | uncertainty",
      "severity": "blocking | material | limitation",
      "evidence_location": "Exact candidate/source reference",
      "issue": "What is wrong or unsupported",
      "suggested_action": "Feasible action without target answers"
    }
  ],
  "tests": ["Artificial checks actually performed"],
  "review_scope": "Own approved evidence and artificial inputs only; no real outcomes, observed rows, other runs or new retrieval"
}
```

`execution_allowed` concerns safe/valid execution of this submitted implementation, not a claim of target analytical validity. Do not approve execution when there is an unresolved blocking error. Report blockers to the coordinator promptly.

## Final source/code check

After the final candidate is frozen, inspect what actually changed, new source evidence, provenance, and response to initial findings. Recheck numerical changes on invented inputs. Write `final_code_review.json` in the assigned run with the same four binding hashes for the final version, `execution_allowed`, findings and summary. No further scientific optimization turn is planned. Any blocking implementation defect must be reported as a protocol issue rather than silently repaired or hidden.

Record whether the change was scientific, numerical, measurement-related, qualification-only, or a justified exact no-op. A rewrite or additional explanation does not by itself imply better generated data.
