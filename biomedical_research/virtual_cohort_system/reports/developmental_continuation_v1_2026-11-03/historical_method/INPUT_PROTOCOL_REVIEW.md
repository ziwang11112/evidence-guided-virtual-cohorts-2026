# Independent prospective input and protocol review

Final decision: the exact prospective developmental release with approval-payload digest `b7ae055e1172e5b1c49cf71feb067cb24660fb9cdda3ae50376814836987a1aa` is approved. No concrete scientific-contract blocker remains. The final independent code reviews and completed bounded composition-test receipt have been verified as detailed in the final addition below. `RELEASE_REVIEW.json` supplies the seven-field approval; all candidate-specific and execution gates remain applicable. This is not a claim of clinical validity or target performance.

Reviewer: support_selection_design. Producer: root. Reviewed UTC: 2026-11-03 05:29:49 UTC.

The reviewer read the prospective protocol, author task/schema, source packet, compiled evidence, unit guidance, registry, support contract, unsigned release, schedule and preparation scripts. Relevant allowlisted interface documentation and code were inspected or screened; all 24 allowlisted file hashes were independently checked. The reviewer did not run either preparation script, import or execute a candidate generator, read patient/reference report contents, inspect prior candidate scientific values in this audit, retrieve literature or sample any cohort. Metadata checks used only JSON, file hashes, integer schedule arithmetic and exact rational unit arithmetic. The four admitted source-input files were compared by hash with their approved source-only predecessors; no prior candidate/output was opened.

## Scientific contract

The primary question concerns evidence-guided whole-cohort generation with no individual input. The within-method numerical-feedback comparison is secondary. The task specifies the selected target population, five generated variables, measurement units and three downstream analyses, while leaving distributions, dependencies, parameter values, scientific sharing and transport assumptions to the author. It supplies no target mean, slope, desired sign, residual scale or participant observation. The target cohort name and eligibility are task definitions, not supplied target answers.

Both constructors must use the same designated initial manifest and exact task, evidence and registry bytes. The packet contains the same three external source studies, 31 compiled marginal items, four source relationships and one unit-guidance item. The registry, compiled evidence, evidence packet and NGSP guidance are byte-identical to the admitted inputs. The copied author protocol is byte-identical to the root protocol. Evaluation/reference files are absent from the 24-file author allowlist. References or links within permitted text do not authorize reading unlisted reports or retrieving papers.

Source distinctions are retained correctly:

- Jansen supplies two separate age/binary-gender-adjusted IFCC HbA1c projections, one for BMI and one for FPG. It does not supply their simultaneous joint structural coefficients. The FPG <7 eligibility condition is specific to this source; unmeasured diabetes/anemia and other exclusions remain assumptions. Its exact adult age limits are unreported and are left for explicit author assumptions.
- Bao supplies marginal Pearson FPG–HbA1c correlation, retains screen-detected diabetes, and has an unresolved age-20 wording boundary. Requiring an age >=20 envelope permits either disclosed integer convention; it does not force inclusion of age 20. No Jansen glucose cutoff is imposed on Bao.
- MIND supplies marginal Spearman serum-glucose–HbA1c correlation for ages 61–80. Its separate plasma assay is not substituted. Prior-year demographics/BMI, later laboratories, imputation and unknown original tie handling remain visible qualifications.
- Original weights, exact model/pair membership, estimator processing and missing precision remain unknown. Individual SDs and quartiles are not treated as estimator SEs or confidence intervals. Unknown-level Jansen intervals are not relabelled 95% intervals. Equal weighting, intercept inclusion, complete generated rows and average Spearman ties define qualified scenarios rather than exact source replay. No automatic pooling, precision weighting or target assignment is introduced.

The exact inverse scale check is correct: `(NGSP - 2.152) / 0.09148` equals an affine map with scale `25000/2287` and shift `-53800/2287`. The release requires this exact native map and nonnegative Jansen IFCC support. It separately requires positive output BMI/glucose/HbA1c, task-compatible integer/category values and reported context eligibility. There is no coordinator-imposed target mean, target association, extra biomarker maximum or invented source upper age bound. The smallest-positive-float BMI schema value is a representation envelope, not a fitted physiological lower bound.

The contract permits a directly specified eligible-population joint law as well as a correctly conditioned assumed parent joint law. It does not demand reconstruction of source individuals or an unknown parent population. Clipping is separately disclosed and cannot masquerade as exclusion. Approximate/initialization algebra can remain approximate; published point agreement is not an admission requirement. Actual code/law correspondence, native support, source-to-target dependency and required design conditions still need candidate-specific independent review. The conservative moment grammar limits the executable model class; the protocol explicitly acknowledges this and forbids replacing an unsupported conditional law with a false surrogate declaration. This is a disclosed pilot implementation limitation, not evidence against such laws in general.

## Budget, branches and analyses

Independent schedule arithmetic confirms 72 unique planned slots: 54 source and 18 target tables of 3,000 rows, totaling at most 216,000 virtual rows. There are two constructors and exactly initial, self_review and source_feedback versions. All slot records are presently pending, without candidate, execution or output bindings. Failed, stopped, aborted and unavailable slots stay in the denominator.

The task's lifecycle revision depth of two is consistent with one optional initial common correction followed by one branch child. It does not grant each branch two scientific revisions. The controller separately requires each branch to parent its accepted initial version, counts one branch scientific opportunity and prevents reuse of a version slot. Two schema-only returns concern interfaces, not additional model search. Both branches receive the same output-byte allowance; unavailable model-call/token counts remain null, so the protocol makes no false token-matching claim.

The self-review branch excludes numerical source output/feedback; the numerical branch adds only authenticated initial source feedback. Final branch diagnostics remain unavailable to that author until its decision is irrevocable. All scientific versions and source dispositions freeze before any target generation; evaluation/reference reveal follows complete target disposition. These are procedural boundaries, not OS isolation or proof against pretrained/prior exposure.

The required qualified IDs are exactly `Q_J_bmi`, `Q_J_fpg`, `Q_B_pearson`, and `Q_M_spearman`, with the correct J/J/B/M contexts. Target eligibility requires all nine source executions, all retained support checks and all four qualified relationships on their three seeds. This is a computability/support gate, not a source point-fit tolerance. An author may disclose incompatibility and stop; unsupported checks are not silently converted to exact evidence.

All three intercept-including target projections remain: BMI with age/female adjustment; glucose with age/female adjustment; and age with female/BMI/glucose adjustment. The age analysis can remain assumption-dependent even when mathematically calculable. The comparison reports each version/seed, complete discrepancy vectors and paired changes, without requiring every endpoint to improve. Three-seed means require complete availability; seeds and virtual rows are not independent scientific replications. Reference-comparable diagnostics stay separate from newly generated-only tails, dependence and duplicates. No post-result adequacy/equivalence threshold or binary overall success rule is supplied.

The existing locked aggregate references are explicitly developmental because coordinating researchers have prior exposure. Their paths/hashes appear only in evaluator metadata; neither their values nor patient data were opened in this review. Their validity/extraction is inherited rather than independently re-established here. The separate host analytical environment is frozen as Python 3.12.10, NumPy 2.4.5, pandas 3.0.3 and SciPy 1.17.1; it is not conflated with the WSL generator runtime. The preparation script explicitly copies reference metadata instead of opening or hashing either reference report.

## Initial reviewed commitments

The initial unsigned release digest, independently recomputed while excluding only its `review` field, was `b507d78f1832315d043d23ead843cf02cd5eb0cb5b42b214d6d67a1a1229a53c`. This was an observed **draft digest**, not an approved final release digest. All 24 non-reference release file bindings checked at that checkpoint matched their retained bytes. The entire 24-file author allowlist was committed by `INITIAL_PACKET.json`; no duplicate allowlist path was found. The following table preserves that initial checkpoint; the bounded delta below supersedes changed hashes.

| File | SHA-256 |
|---|---|
| `PROTOCOL.md` and `author_inputs/input/PROTOCOL.md` | `91fc5b521376b3e940a72c42ab4afe8d27775107d4d8fb0b75974c35e1c5f897` |
| `INITIAL_PACKET.json` | `3bbe87317cda0f21f579433a3a10cc4045f03cd8186165744cf020fde92d812f` |
| `SUPPORT_CONTRACT.json` | `9a36904df634ba3f8dea59d82150199281f02f6ecd91a77e2f23e173a3e84d70` |
| `author_inputs/input/AUTHOR_TASK.md` | `c1499775ffe5c1abc3c73b6133e87771766b6cab4c16b0388f536018cf50690c` |
| `author_inputs/task.json` | `efb52e72944ec2e50f2ed70bd934e94341f9d659a0699a831350f8e43703cb4d` |
| `author_inputs/registry.json` | `dcb2f039e3ee81798ec69abf2df05b5567787078e0e1a8f01cd97e858b584007` |
| `author_inputs/input/compiled_evidence.json` | `a10a223af16f040d34fa82a5d183128c8e40396cc009ffb92395b715b386a648` |
| `author_inputs/sources/evidence_packet.json` | `254a9bca0c612e4e03a22c9e4457b4b34eb4d5cd4672df8c2a4cd15131f7ab84` |
| `author_inputs/sources/NGSP_UNITS.md` | `724a8b7965ab7bcb1d27a089204473b505d9e83b3042dea05c52cca3d8cf89d4` |
| `RELEASE_DRAFT.json` | `6d5dd0a6039e7114fed6677ee9451d430e6bb29b7e31fc492208c60ccaba890a` |
| `PLANNED_SLOTS.json` | `e0985cf53ac3db471b49da1ae4047aa7f61f7d9ea5630adc10976651aa6f234e` |
| `prepare_inputs.py` | `f4c4815e8a505386e7bd99db9d6cdff228877950bd93240e80c860902985f880` |
| `prepare_release.py` | `c2acf1e0d351c0b05c4ab9d257865bcc98f3c5973399fb34ce02616b4e8e29a3` |
| `EVALUATION_POLICY.json` | `28595f94cad350ca1b8f67e82ac8bd0694a577fb971b15e07c27e313578ea935` |
| `ANALYSIS_ENVIRONMENT.json` | `3f912f285e249f931e26518774f685c8a96c3e57aa16b87f6ffa9e6406f1c60c` |

## Bounded final delta, reviewed 2026-11-03 05:39:31 UTC

The revised unsigned digest independently recomputes to `b7ae055e1172e5b1c49cf71feb067cb24660fb9cdda3ae50376814836987a1aa`. Its `review` remains null. All 24 current author-file bindings and all 25 current non-reference release-file bindings match. Reference-report contents were not opened or hashed. No source/target execution or test rerun occurred in this delta review.

The protocol and author-task changes clarify that a shared nominal seed schedule does not guarantee identical latent draws or matched virtual individuals across algorithms. Pairing is by the planned seed ID. This correction strengthens the interpretation without changing the scientific question, seed values, row counts, branches or analysis. Replacing only those exact new sentences with their former sentences recovers the previously reviewed protocol, author-task and `prepare_inputs.py` hashes. `prepare_release.py` itself is unchanged; its regenerated bindings reflect the changed files. The planned slots, support contract, task/evidence/registry, source evidence/units, evaluation policy, host environment and controller remain unchanged.

The independent final `EVALUATION_CODE_REVIEW.md` approves both final wrappers, the evaluator fixture/schema and their actual-controller interface at the hashes below. The narrow repair makes both wrappers independently compute the canonical **complete-release** identity including its review; the approval-payload digest still excludes review. This aligns the wrappers with the controller without weakening its gate. The reviewer read that independent disposition, verified its exact file hashes and inspected the narrow canonical-identity contract. The review's controller hash matches the separate complete controller approval. The root's separate support-code review and binding also match the unchanged support module/contract; no self-approval of that module is supplied here.

The newly bound composition fixture uses the actual controller and default evaluator gates with invented inputs, one admitted version, five explicit aborts and the complete 72-slot inventory. Only the process boundary is mocked. Its assertions require 12 qualified results, nine source support reports, 18 retained target dispositions, preauthorization reference-read rejection, scientific-use labels, complete source annotations and independent recomputation agreement. Reading these assertions is not evidence that they have passed. The final test outcome is still awaited at this checkpoint.

| Final-delta artifact | SHA-256 |
|---|---|
| `PROTOCOL.md` and copied author protocol | `97bf30eb7ac4befde023d92cc2af6c2fb952e7bd0675c47d4d384ac459d0651e` |
| `author_inputs/input/AUTHOR_TASK.md` | `96a593fa2c6a5122866105c5bb39b13b1e5862cdc66ee59c057b24725eccb771` |
| `prepare_inputs.py` | `5359d40acec302bf194e344a3b37af75132adb51214f680a931d23197ccead33` |
| `INITIAL_PACKET.json` | `8d34e077ac3d086317441952bb6e161f4521a27881784f2905b9c24dc08f74f5` |
| `RELEASE_DRAFT.json` | `70a889c6ddf2dbcd2fc938de5237741ebdf876ceab3ca2a73cd5813a86f08dc4` |
| `implementation/pilot_evaluation_v1.py` | `ab9a6bfddbc74c7ef31a72ff2ebb34c618f6d145332c000f5e15e70aa88f4a0f` |
| `implementation/independent_pilot_recompute.py` | `a309c8bdad728a7a9e32ee073d5ea64d9b6e302e8ffb89dbe8b82c2cc1cde539` |
| `implementation/PILOT_EVALUATION_SCHEMA.md` | `01b75a98943ed04bcaf2d4e12b8a8742ef29d7191996665c9b6d28a844bcf7c6` |
| `implementation/test_pilot_evaluation_v1.py` | `80831ddc5e9ca41ddfb41668a948d5af34da9b34a59d0eeb32cc72c636e94c27` |
| `implementation/test_pilot_composition_v1.py` | `bff7716ac37902bb1d42befee0dd9b66384d8619f4a520927ed6869a518eb83a` |
| `EVALUATION_CODE_REVIEW.md` | `37212370bdbd568f4d291683390f9e6d1de705f06b5584bb89e8aecd79c4666f` |
| `CONTROLLER_CODE_REVIEW.md` | `736334f9e1596e2114a4ef1c0f673b77628ea8a817a6e3ecd7f2aa5b473c88c7` |

## Historical non-authorizing review skeleton

The following preserves the pending checkpoint and is not a valid approval. It must not be installed as an approved release. It is superseded by the final addition and separate `RELEASE_REVIEW.json` after receipt of the completed composition result and the root's final digest confirmation.

```json
{
  "decision": "pending",
  "independent": true,
  "reviewer_id": "support_selection_design",
  "producer_id": "root",
  "reviewed_utc": "2026-11-03T05:39:31Z",
  "reason": "Scientific input/protocol contract and bounded final delta independently reviewed at the commitments in INPUT_PROTOCOL_REVIEW.md; exact final controller/evaluator/support code reviews verified. Final digest confirmation and completed bounded composition-test result remain pending.",
  "approved_sha256": null
}
```

The support-selection implementation was authored by this reviewer and is covered by the root's separate independent support-code review, not self-approved here. This review covers its release-owned scientific constraints and the broader input/protocol contract. No broader framework, additional evidence, additional scientific parameter setting or extra clinical execution is needed to resolve an input-contract issue identified here, because none remains open.

## Final release approval, 2026-11-03 05:42:30 UTC

The root confirmed that the final unsigned approval-payload digest remains `b7ae055e1172e5b1c49cf71feb067cb24660fb9cdda3ae50376814836987a1aa`. This reviewer independently recomputed that digest from the complete release object excluding only `review`. The unsigned file still has raw SHA-256 `70a889c6ddf2dbcd2fc938de5237741ebdf876ceab3ca2a73cd5813a86f08dc4` and a null review. All 25 non-reference release-file bindings, all 24 author-file bindings and all 19 engine bindings match their current bytes. The four separate controller/evaluator/support review artifacts remain byte-identical to the reviewed approvals. Neither private reference report was opened or hashed.

The retained `implementation/COMPOSITION_TEST_RECEIPT.json`, SHA-256 `e66a9dcf0eb2837058a5d01fae4061ec01d655f4f3ca362ad7cd0e8d5e0f45b9`, reports 32 passing tests: one actual-controller composition fixture and 31 affected evaluator tests. The full reported pytest time is 219.95 seconds; the single composition fixture time is 216.256 seconds. The prior ten controller tests were not rerun. This reviewer read the retained receipt and its underlying fixture metadata at `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/.pc02/test_real_closed_controller_in0/COMPOSITION_RECEIPT.json`, SHA-256 `c1d9923858078095e6681cc8adcf10d814c07db4bad9d791eab18503cc6d3685`. Their shared fields agree. All six receipt code/schema/test hashes match the exact release-bound files. The reviewer did not rerun the tests or inspect fixture rows or scientific reports.

The completed fixture reports both evaluators using their default controller gates, 72 closed planned slots, the full 18-target denominator, one admitted version and five explicit aborts, nine mocked source executions, three mocked target executions, 12 available required qualified results, nine retained source support reports, six preserved scientific annotation versions, zero preauthorization reference accesses and independent status `matched`. Its process boundary was mocked; actual generator processes, patient reads and old-reference-report reads are all recorded as zero. This is bounded integration evidence for the reviewed release interfaces, not a simulation result or scientific adequacy claim.

No pending release-contract issue remains within this review's scope. The approval is recorded in `RELEASE_REVIEW.json` with reviewer `support_selection_design`, producer `root`, `independent: true` and the exact approval-payload digest above. The root may validate/embed that record and create the release ledger. This approval does not waive candidate-specific scientific/support review, immutable author lineage, source computability/support checks, complete budget accounting, scientific freeze or later authorized evaluation barriers. No release, protocol, implementation or scientific input was modified by this final review.
