# Artificial whole-cohort construction
This is an invented, dimensionless mechanism fixture, not a biomedical population,
paper, patient dataset or empirical study. Construct one joint table of g, x, y
for the population in task.json, with no individual observations supplied.
The intended use is descriptive associations and threshold questions.

You choose the scientific structure, parameters, distribution families and
implementation. Use only task.json, evidence.json, registry.json, evidence_note.md,
this instruction file, and the registered sources/ artifacts in this bundle,
plus the supplied harness contract/interface. Declare every unsupported choice
as an assumption. A source functional is not a full distribution. Do not infer
an error distribution merely from a residual SD or a linear conditional mean.

Deliver candidates/initial/{generator.py,model_spec.json,evidence.json,decision.md,checks.json}.
Copy evidence.json exactly. Use the existing strict schemas and the top-level
generate(observed, spec, seed) ABI returning a pandas DataFrame. observed is None.
The generator may use NumPy/Pandas and the supplied seed only; no file/network
access, hidden truth, other bundles, clinical data, or extra literature.
Metadata/schema/AST checks are allowed. Do not import/run the generator, create
trial rows, optimize against a hidden answer, or manufacture a freeze/approval.
The coordinator will freeze all four constructions before any scheduled output.
There is one construction and no source-feedback revision. No numeric feedback
is provided to you. Different scientific choices consistent with the packet
must be acknowledged; do not promise a uniquely identified joint law.
