"""Prepare prospective author inputs only; no science execution or reference reads."""
from pathlib import Path
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
PRIOR = WORKSPACE / "evcSI"
INPUTS = HERE / "author_inputs"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def domain(lower, upper=None, lower_closed=False, upper_closed=False):
    return dict(lower=lower, upper=upper, lower_closed=lower_closed, upper_closed=upper_closed)


def main():
    if (HERE / "RELEASE.json").exists():
        raise RuntimeError("Preparation cannot modify a released unit")
    INPUTS.mkdir(exist_ok=True)
    for relative in ("registry.json", "input/compiled_evidence.json", "sources/evidence_packet.json", "sources/NGSP_UNITS.md"):
        destination = INPUTS / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PRIOR / relative, destination)
    task = json.loads((PRIOR / "task.json").read_text(encoding="utf-8"))
    task["task_id"] = "developmental-evidence-guided-whole-cohort-pilot-v1"
    # Lifecycle depth: at most one initial validity correction plus one branch child.
    # The pilot controller separately limits scientific opportunities and ancestry.
    task["budget"]["revisions"] = 2
    write_json(INPUTS / "task.json", task)
    checks = {}
    for context in ("J", "B", "M", "T"):
        checks[context] = [dict(id=f"{name}_positive", variable=name, domain=domain("0")) for name in ("bmi", "glucose", "hba1c")]
        checks[context].append(dict(id="female_binary_envelope", variable="female", domain=domain("0", "1", True, True)))
    checks["J"].extend([
        dict(id="age_schema", variable="age", domain=domain("0", lower_closed=True)),
        dict(id="source_fpg_eligible", variable="glucose", domain=domain("0", "7")),
        dict(id="source_native_ifcc_nonnegative", variable="hba1c", native_view="HbA1c_IFCC",
             native_mapping=dict(kind="affine", variable="hba1c", scale="25000/2287", shift="-53800/2287"),
             domain=domain("0", lower_closed=True)),
    ])
    checks["B"].append(dict(id="age_source", variable="age", domain=domain("20", lower_closed=True)))
    checks["M"].append(dict(id="age_source", variable="age", domain=domain("61", "80", True, True)))
    checks["T"].append(dict(id="age_target", variable="age", domain=domain("35", "74", True, True)))
    write_json(HERE / "SUPPORT_CONTRACT.json", dict(required_contexts=["J", "B", "M", "T"], required_checks=checks,
               definition_ids=["D_TASK_SCHEMA", "D_SOURCE_ELIGIBILITY", "D_OUTPUT_POSITIVITY", "D_NATIVE_UNIT_RANGE"]))
    original = (PRIOR / "input/AUTHOR_TASK.md").read_text(encoding="utf-8")
    original = original.replace("# One source integration construction", "# Evidence-guided whole-cohort developmental pilot: author instructions")
    original = original.replace("input/PROTOCOL.md", "input/PROTOCOL.md")
    original = original.replace("Each source has n_rows=1000.", "Each source has n_rows=3000.")
    original = original.replace("The qualified comparison's own check IDs must be distinct, for example Q_J_bmi, and its semantic_check_id refers to the original strict ID.",
                                "The qualified comparison IDs are exactly Q_J_bmi, Q_J_fpg, Q_B_pearson and Q_M_spearman, respectively; each semantic_check_id refers to its original strict ID.")
    original = original.replace("- `context_eligibility.json`:", "- `support_selection_v1.json`: the additive support/selection declaration described in the supplied schema and SUPPORT_CONTRACT.json. Declare every final support and scientific transformation, exact required native maps, conditioning versus direct eligible laws, and which derivations remain exact or approximate after transformations. This file is mandatory; actual code-law correspondence also requires independent review.\n- `context_eligibility.json`:")
    prefix = original.split("## Frozen schedule and limits")[0]
    suffix = """## Fixed schedule, author allowance and branches

Your assignment identifies constructor A01 or A02, candidate destination and version. It does not supply scientific parameter values. In context_bridge_v1.json use nine source trials and three target trials. Source seeds are 41011, 41012 and 41013 for each of J/B/M; target seeds are 41911, 41912 and 41913. Every trial has n_rows=3000. IDs are `{constructor}_{version}_{context}_{seed}`. The exact bridge budget is source_attempts=9, source_rows=27000, target_attempts=3, target_rows=9000. The controller initially opens sources only. Global scientific closure must precede any target dispatch. All versions use the same nominal seed schedule; different algorithms need not map it to identical latent draws. Pairing is by seed ID, not matched virtual participants or independent method replicates.

Execution limits are timeout_seconds=60, memory_mb=1536, output_bytes=4000000 and log_bytes=20000. Entire candidate submissions may contain at most 1048576 bytes, of which generator.py may contain at most 65536 bytes. A scientific initial submission may receive at most one common pre-branch validity correction; any rejected original is frozen/retained. At most two schema-only returns per stage can fix interfaces without changing the scientific law, parameters or generator code. Do not create approval records. Do not run a generator or a simulation during authoring, including internal pilots. You may run metadata/schema/static-law checks and report them honestly.

The two branches separately review the same accepted initial candidate. The self_review branch receives no numerical source results. The source_feedback branch additionally receives authenticated initial source feedback, including failures. Each branch gets one scientific decision: retain, revise or stop. Submit that explicit decision with reasons, addressed findings and remaining limitations. A retain branch copies the same generator.py and model_spec.json into its own immutable child candidate and updates only necessary branch identities/metadata. A revise branch gets one new scientific candidate. Both use the fixed schedule and the same submission caps. Final branch feedback is not available before that decision; neither branch sees target outcomes. Revision is optional. Evidence-supported direct eligible laws are allowed; do not force a new component merely to make a change.

The currently supported moment grammar does not represent arbitrary conditional/truncated laws. Any selected conditional_joint law must have a faithful final-law representation in the admitted grammar and independently reviewable code. An unconditional parent or clipped surrogate cannot stand in for the actual conditional law. You may choose a directly specified eligible-population joint law. Unknown distributional and transport details must be recorded as assumptions. Source point discrepancy is not an admission threshold; truthful unsupported analyses remain visible.

Submit analysis_evidence IDs exactly A_BMI, A_GLUCOSE and A_AGE. An age coefficient can be calculated even if its scientific relation is unassessed; do not convert calculability into evidence support. The unit is developmental on already researcher-exposed CHNS. It cannot establish fresh confirmation. The source and target tables are withheld from authors except the allowed numerical source summaries. Do not inspect sibling output, reference data, prior candidate science, or earlier result reports.
"""
    (INPUTS / "input/AUTHOR_TASK.md").write_text(prefix + suffix, encoding="utf-8")
    receipt = {"kind":"prospective_input_preparation", "generator_executions":0, "reference_reads":0,
               "evidence_reused_unchanged":True,
               "files": {str(p.relative_to(INPUTS)).replace("\\", "/"):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(INPUTS.rglob("*")) if p.is_file()}}
    write_json(HERE / "INPUT_PREPARATION.json", receipt)
    print(json.dumps({"status":"prepared", "files":len(receipt["files"]), "generator_executions":0}))


if __name__ == "__main__":
    main()
