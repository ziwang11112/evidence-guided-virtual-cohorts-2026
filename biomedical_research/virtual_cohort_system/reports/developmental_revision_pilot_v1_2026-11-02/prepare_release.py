"""Build an unsigned prospective release; never approve, execute, or reveal data."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
IMPLEMENTATION = HERE / "implementation"
sys.path.insert(0, str(IMPLEMENTATION))
import pilot_controller_v1 as controller
import pilot_evaluation_v1 as evaluator


def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    if (HERE / "RELEASE.json").exists():
        raise RuntimeError("Cannot rebuild a released unit")
    inputs = HERE / "author_inputs"
    protocol = (HERE / "PROTOCOL_DRAFT.md").read_text(encoding="utf-8")
    protocol = protocol.replace("Status: prospective preparation, not execution release.",
                                "Status: prospective protocol; execution requires the separately approved, hash-bound release.", 1)
    (HERE / "PROTOCOL.md").write_text(protocol, encoding="utf-8")
    shutil.copyfile(HERE / "PROTOCOL.md", inputs / "input/PROTOCOL.md")
    schema_paths = [
        PROJECT / "cohort_harness/contracts.py",
        PROJECT / "cohort_harness/analysis_evidence.py",
        PROJECT / "cohort_harness/whole_cohort_feedback.py",
        PROJECT / "cohort_harness/semantic_feedback_v1.py",
        PROJECT / "work/scaleup_2026-11-01/bridge/README.md",
        PROJECT / "work/scaleup_2026-11-01/bridge/context_bridge.py",
        Path("D:/Codex/home/skills/evidence-cohort-generation/SKILL.md"),
        Path("D:/Codex/home/skills/evidence-cohort-generation/references/harness-interface.md"),
        HERE / "SUPPORT_CONTRACT.json",
        IMPLEMENTATION / "SUPPORT_SELECTION_SCHEMA.md",
        IMPLEMENTATION / "support_selection_v1.py",
    ]
    prior_impl = PROJECT / "work/evidence_revision_v1_2026-11-02/implementation"
    schema_paths += [prior_impl / name for name in (
        "evidence_use_SCHEMA.md", "evidence_use_v1.py",
        "scientific_validity_SCHEMA.md", "scientific_validity_v1.py",
        "qualified_relationships_SCHEMA.md", "qualified_relationships_v1.py")]
    author_files = [binding(p) for p in sorted(inputs.rglob("*")) if p.is_file()] + [binding(p) for p in schema_paths]
    initial = dict(schema_version=1, kind="pilot_initial_author_packet", task=binding(inputs/"task.json"),
                   evidence=binding(inputs/"input/compiled_evidence.json"), registry=binding(inputs/"registry.json"), files=author_files)
    write(HERE / "INITIAL_PACKET.json", initial)
    write(HERE / "EVALUATION_POLICY.json", evaluator.POLICY)
    write(HERE / "ANALYSIS_ENVIRONMENT.json", evaluator.analysis_environment())
    # Previously frozen metadata only: do not open/hash either reference report here.
    refs = {
        "reference_report": dict(path=str((PROJECT/"work/chns_admission_2026-11-01/f2/evaluation_results/REPORT.json").resolve()),
                                 sha256="55c307e230d1d59eded5d5af0dd15b0ca376d8a2b045cb00621c5b0e5409794f"),
        "independent_reference_report": dict(path=str((PROJECT/"work/chns_admission_2026-11-01/f2/independent_results/REPORT.json").resolve()),
                                             sha256="be246b4f33b36d54b981d8b2a5d92ce90e48843861f948522a01ac34948e9d58"),
    }
    evaluation = {**refs,
        "analysis_module":binding(PROJECT/"work/chns_admission_2026-11-01/f2/evaluation/chns_f2_evaluation.py"),
        "analysis_plan":binding(PROJECT/"work/chns_admission_2026-11-01/f2/analysis_plan.json"),
        "independent_recompute":binding(IMPLEMENTATION/"independent_pilot_recompute.py"),
        "policy":binding(HERE/"EVALUATION_POLICY.json"),
        "analysis_environment":binding(HERE/"ANALYSIS_ENVIRONMENT.json")}
    expected = {"analysis_module":"e40f403b13125f5b41f620126a807122bb99796558adda576518fcf50796365a",
                "analysis_plan":"a2c5f43969c700474a9466416be8503dc0c92b1c78b12a07a6edc6bc88f247b7"}
    for key, digest in expected.items():
        if evaluation[key]["sha256"] != digest:
            raise RuntimeError("Historical analysis binding changed: " + key)
    artifacts = [HERE/"prepare_inputs.py", HERE/"prepare_release.py", HERE/"SUPPORT_CODE_REVIEW.md", HERE/"SUPPORT_REVIEW_BINDING.json"]
    artifacts += [p for p in sorted(IMPLEMENTATION.iterdir()) if p.suffix in {".py", ".md"}]
    release = dict(schema_version=1, kind="developmental_revision_pilot_release",
        ledger_directory=str((WORKSPACE/"evcDP/ledger").resolve()), protocol=binding(HERE/"PROTOCOL.md"),
        artifacts=[binding(p) for p in artifacts], engine_sha256=controller.engine_hashes(),
        runtime_identity=binding(PROJECT/"work/scaleup_2026-11-01/production_release/runtime/RUNTIME_IDENTITY.json"),
        source_contexts=["J","B","M"], target_context="T", source_seeds=[41011,41012,41013],
        target_seeds=[41911,41912,41913], n_rows=3000,
        execution_limits=dict(timeout_seconds=60,memory_mb=1536,output_bytes=4000000,log_bytes=20000),
        author_allowance=dict(candidate_bytes=1048576,generator_bytes=65536,schema_returns=2),
        support_contract=binding(HERE/"SUPPORT_CONTRACT.json"), initial_packet=binding(HERE/"INITIAL_PACKET.json"),
        required_qualified_checks=[dict(context_id=c,check_id=q) for c,q in (
            ("J","Q_J_bmi"),("J","Q_J_fpg"),("B","Q_B_pearson"),("M","Q_M_spearman"))],
        evaluator=binding(IMPLEMENTATION/"pilot_evaluation_v1.py"), evaluation=evaluation, review=None)
    write(HERE/"RELEASE_DRAFT.json", release)
    write(HERE/"PLANNED_SLOTS.json", controller.planned_slots(release))
    print(json.dumps(dict(status="unsigned_draft_only", release_digest=controller.release_digest(release),
                         author_files=len(author_files),planned_slots=72,generator_executions=0,reference_reads=0)))


if __name__ == "__main__":
    main()
