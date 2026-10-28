# Reusable evidence to population framework

**Latest: the [two-case policy comparison](strategy_comparison_2026-10-27/RESULTS.md)
is complete.** Four fresh builders produced eight initial/revised programs under
the same evidence and submission budgets. Structured policy final joint TV was
worse than capable ordinary iteration in both tasks (0.0775 vs 0.0646; 0.2382 vs
0.1499). All programs passed their source/baseline checks. The policy has not
demonstrated improved generation; preserve this negative development result.
The shared execution/evaluation infrastructure remains reusable. The comparison
used four explicitly permitted development marginal summaries at revision and
historically exposed check splits, not new external confirmation.

The optimization target is the shared Agent build/check/revise procedure.
Individual papers supply evidence and test tasks; they do not each get a new
runner or a hand-designed target repair. This implements the user's scope
correction on 27 October 2026. It does not impose one statistical model on all
populations or claim that engineering reuse establishes scientific advantage.

The [completed integration demonstration](RESULTS.md) ran both stages for a
historical compatibility fixture and one fresh Agent task, with identical core
and request hashes. The fresh update was a verified no-op. No new target accuracy
evaluation was performed.

## Responsibilities

| Layer | Shared behavior | What varies |
|---|---|---|
| Evidence delivery | Project the active stage into a fixed input interface; preserve versions and evidence differences | Published observations, populations, units and allowed target information |
| Agent construction | One common request; receive an executable generator and evidence-linked decisions | Model family, conditional structure, transport assumptions and numerical fitting |
| Numerical execution | One sampler interface, schema validation, reproducibility and generated artifact retention | Contexts and output fields declared by each task |
| Source and baseline observation | Generic moments, quantiles, regressions, correlations and conditional probabilities | Reported study-native estimands and supplied baseline summaries |
| Revision | Deliver the new evidence and previous diagnostics; retain every candidate | Agent may revise, qualify, request information or keep its model |
| Revision verification | Check claimed invariant outputs with common seeds; probe whether selected inputs reach target sampling | Claimed invariant columns and explicitly proposed evidence perturbations |
| Later evaluation | Separate committed target-outcome analysis | Task-specific endpoints, real cohorts and comparative experiments |

`runner.py` contains no study names, clinical variable names, source mixtures or
fixed correlation values. `observers.py` contains reusable numerical operators.
`adapt_cases.py` currently translates two audited existing formats into the common
contract; extraction is still curator-assisted, not autonomous paper reading.
Adapters define observations and domains, not the generator's model family.

## Mechanism being developed

A revision connects an evidence item or diagnostic to a named model component,
an explicit target-transport assumption, predicted consequences and any claimed
unchanged outputs. The framework then executes the program. It checks selected
invariants and numerical input use rather than accepting the Agent's narrative
alone. A source-only branch can reproduce a table without validating a target
path; source checks and target input-use probes answer different questions.

Individual variation, study differences, measurement and population conditioning
are represented separately when warranted by the model. These are modeling
responsibilities, not mandatory Gaussian layers. The Agent may use a different
distribution, conditional program, simulation or other executable construction.
Unidentified parts remain assumptions or sensitivity scenarios.

Perturbation probes are software checks, not biological interventions or proof
of correct transport. Invariants cover declared columns and executed seeds.
For an action declared `no_op`, all shared output columns are compared
automatically under identical sampling budgets. Equality on these runs is not
a proof of equality for all possible inputs.

## Run a task

Use the installed Python 3.12 with numpy, pandas and scipy. From this directory:

```powershell
python runner.py stage --case cases/exercise/case.json --stage initial --run runs/example/initial
# Deliver runs/example/initial/request.md and its allowed files to the Agent.
# The Agent writes generator.py and decision.json in that run.
python runner.py execute --run runs/example/initial
python runner.py stage --case cases/exercise/case.json --stage updated --run runs/example/updated --parent runs/example/initial
# Deliver the identical shared request plus newly staged evidence/diagnostics.
python runner.py execute --run runs/example/updated
python runner.py verify --run runs/example/updated
```

Executed candidates are immutable; failed candidates retain diagnostics and
snapshots. Use a new run directory for a repair. Active-stage projection omits
future checks and unscoped notes. A first staging attempt exposed a future
coefficient through free-form notes; it was aborted before engine execution,
retained in `runs/exercise/initial/ABORTED.md`, and replaced with a fresh builder
context under `initial_v2`. Regression tests cover that failure mode.

Agent calls currently use the collaboration tool, with explicit request/artifact
handoff by the coordinator. This is not an unattended API service. Exact backend
model identifiers and token costs are unavailable. Import checks and input
instructions aid review but are not an adversarial filesystem/network sandbox.
The core does not load real target outcomes or optimize a target score.

## What the current demonstration can establish

The FIT/Han route imports historical Agent programs as compatibility fixtures.
The exercise route uses a fresh Agent build followed by the shared evidence
update procedure. The same core, prompt and generic observers serve both routes.
Legacy replay is not a second independent Agent-construction experiment.

Source fidelity, baseline fidelity, declared invariants and input-use checks
establish implementation behavior only. Generative accuracy, later-query utility,
novelty and comparative advantage remain unestablished. The current study
observers cover selected quantities, not complete joint-distribution validity.

The next optimization experiment should compare versions of this shared process
across tasks under the same information and revision budget: ordinary iterative
generation versus evidence-linked component revision with numerical checks.
Freeze the common procedure before running tasks, retain failures, and evaluate
unprovided real relationships separately. Improvements confined to supplied
moments, one hand-tuned case or a self-declared no-op do not demonstrate the
intended benefit. Equal-information ordinary statistics and a capable no-record
Agent remain eventual scientific comparators; no large fixed suite is required
to develop the framework.
