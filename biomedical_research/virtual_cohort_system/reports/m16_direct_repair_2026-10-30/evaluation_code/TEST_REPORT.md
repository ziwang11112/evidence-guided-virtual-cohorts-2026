# M16 evaluator test report

30 October 2026. Invented engineering fixtures only; no real or Agent-generated participant rows were read.

`18 passed in 7.94s` using Python 3.12 and pytest. The final run used a fresh local temporary directory `work/m16_eval_test_b`. The prior 17-test run also passed; one additional reference-precommit gate test and matching release verification were added afterward.

Validated:

- byte-identical frozen M15-B numerical module, SHA `4181cfbd8ae37df58699558196ca241f2bd60e4d895b9a18de40a42cbaffce12`;
- known invented linear BMI and age coefficients;
- three different task IDs with otherwise identical semantics;
- real lifecycle initial/final freezes and preauthoring receipts for all three fixtures;
- 144 comparison rows and 72 initial/final changes when all constructions complete;
- all improvements, degradations and unchanged cases retained;
- the actual number of invented joint PSUs used, without a historical fixed count;
- incomplete review, modified protocol/engine/freeze/model receipt, missing builder, and changed reference commitment all fail before private reference bytes are opened;
- reference bytes are opened once after the gate, then parsed from memory;
- a failed construction keeps its initial table and failure record, without a replacement run;
- native weight metadata removal leaves the unchanged unweighted estimands identical;
- duplicate/unexpected columns rejected; nonfinite estimands retained as failures;
- wrapper pairing exactly equals the frozen `compare_tables` outputs;
- output destinations cannot be overwritten; the CLI reads no inputs without `--execute`.

This is implementation verification, not evidence of biomedical utility. The wrapper was implemented by the protocol-review agent and separately inspected by the root controller before launch. Real-data independent recomputation remains a later post-release step.

Final tested wrapper SHA: `a63c3aecf9718ee9be1bd462bd0df3d40765d1228efd158fae69d18deda15483`.
