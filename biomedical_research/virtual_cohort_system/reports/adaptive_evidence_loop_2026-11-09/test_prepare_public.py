"""Exporter checks on invented content only; no clinical/session access or network."""
import base64
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("finite_export_test", Path(__file__).with_name("prepare_public.py"))
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(exporter.encoded(value) if not isinstance(value, bytes) else value)


def fixture(tmp_path):
    project, bundle = tmp_path / "project", tmp_path / "bundle"
    unit = project / "work" / exporter.UNIT
    bundle.mkdir(); unit.mkdir(parents=True)
    write(bundle / "registry.json", {"artifacts": []})
    write(bundle / "web_evidence_v1/state.json", {"usage": {"downloads": 0}, "retrievals": {}})
    write(bundle / "gateway/session/state.json", {"usage": {"downloads": 0}})
    protocol = {"bundle": str(bundle), "seeds": [11], "unit": exporter.UNIT}
    write(unit / "PROTOCOL.json", protocol)
    write(unit / "DESIGN_LOCK.json", {"PROTOCOL.json": exporter.sha((unit / "PROTOCOL.json").read_bytes())})
    closure = {"status": "author_finished_no_further_revision", "bundle": str(bundle),
               "candidates": ["candidates/toy"], "final_candidate": "candidates/toy", "runs": ["toy11"],
               "execution_slots": [{"candidate": "candidates/toy", "seed": 11, "run_id": "toy11"}],
               "session": {"status": "completed", "pending": None, "candidates": ["candidates/toy"]},
               "files": {p.relative_to(bundle).as_posix(): exporter.sha(p.read_bytes()) for p in bundle.rglob("*") if p.is_file()}}
    write(unit / "AUTHOR_CLOSED.json", closure)
    closure_hash = exporter.sha((unit / "AUTHOR_CLOSED.json").read_bytes())
    evaluation = {"closure_sha256": closure_hash, "runs": [{"run_id": "toy11", "candidate": "candidates/toy", "seed": 11}],
                  "stages": [{"candidate": "candidates/toy", "selected_final": True}]}
    write(unit / "EVALUATION.json", evaluation)
    write(unit / "RECOMPUTATION.json", {"closure_sha256": closure_hash, "checks": 1, "passed": 1,
          "evaluation_sha256": exporter.sha((unit / "EVALUATION.json").read_bytes())})
    return project, bundle, unit, closure


def test_missing_closure_refuses_without_output(tmp_path):
    project = tmp_path / "project"
    unit = project / "work" / exporter.UNIT
    unit.mkdir(parents=True)
    output = unit / "transport"
    with pytest.raises(ValueError, match="Missing regular file"):
        exporter.prepare(project, tmp_path / "mirror", tmp_path / "bundle", output)
    assert not output.exists()


def test_missing_final_output_refuses_without_transport(tmp_path, monkeypatch):
    project, bundle, unit, _ = fixture(tmp_path)
    monkeypatch.setattr(exporter, "PROJECT_FILES", ())
    monkeypatch.setattr(exporter, "RESEARCH_FILES", ())
    monkeypatch.setattr(exporter, "UNIT_REQUIRED", ("RESULTS.md",))
    monkeypatch.setattr(exporter, "read_tree", lambda *_: pytest.fail("Missing files must refuse before Git"))
    with pytest.raises(ValueError, match="Missing regular file"):
        exporter.prepare(project, tmp_path / "mirror", bundle, unit / "transport")
    assert not (unit / "transport").exists()


@pytest.mark.parametrize("corruption", ["duplicate_slot", "extra_evaluation_run", "changed_bundle", "failed_recomputation"])
def test_closure_gate_rejects_inconsistent_inputs(tmp_path, corruption):
    project, bundle, unit, closure = fixture(tmp_path)
    if corruption == "duplicate_slot":
        closure["execution_slots"].append(deepcopy(closure["execution_slots"][0]))
        write(unit / "AUTHOR_CLOSED.json", closure)
    elif corruption == "extra_evaluation_run":
        evaluation = exporter.read_json(unit / "EVALUATION.json")
        evaluation["runs"].append({"run_id": "extra", "candidate": "candidates/toy", "seed": 11})
        write(unit / "EVALUATION.json", evaluation)
    elif corruption == "changed_bundle":
        write(bundle / "registry.json", {"artifacts": ["changed"]})
    else:
        value = exporter.read_json(unit / "RECOMPUTATION.json"); value["passed"] = 0
        write(unit / "RECOMPUTATION.json", value)
    with pytest.raises(ValueError):
        exporter.closure_gate(project, bundle)


def test_links_map_work_to_reports_and_existing_public_files(tmp_path):
    project = (tmp_path / "project").resolve()
    source = project / "work" / exporter.UNIT / "RESULTS.md"
    existing = exporter.PREFIX + "docs/ADAPTIVE_SESSION_V1.md"
    selected = {exporter.REPORT + "RESULTS.md": source}
    available = {existing, exporter.REPORT + "PROTOCOL_PUBLIC.json"}
    text = b"[old](../../docs/ADAPTIVE_SESSION_V1.md)\n[p]: PROTOCOL.json\n"
    # From work/UNIT, docs is two levels above the source directory.
    result = exporter.rewrite_markdown(text, source, exporter.REPORT + "RESULTS.md", selected,
                                      available, project, [], []).decode()
    assert "../../docs/ADAPTIVE_SESSION_V1.md" in result
    assert "[p]: PROTOCOL_PUBLIC.json" in result


def test_absolute_line_link_and_private_link(tmp_path):
    project = (tmp_path / "project").resolve()
    source = project / "work" / exporter.UNIT / "RESULTS.md"
    code = project / "cohort_harness/adaptive_session_v2.py"
    selected = {exporter.PREFIX + "cohort_harness/adaptive_session_v2.py": code}
    raw = ("[code](<" + str(code) + ":17>)").encode()
    result = exporter.rewrite_markdown(raw, source, exporter.REPORT + "RESULTS.md", selected,
                                      set(selected), project, [], []).decode()
    assert result.endswith("adaptive_session_v2.py#L17)")
    with pytest.raises(ValueError, match="Unpublished/private"):
        exporter.rewrite_markdown(b"[private](../../../private.csv)", source, exporter.REPORT + "RESULTS.md",
                                  selected, set(selected), project, [], [])


def test_old_private_accounting_link_is_visibly_a_public_projection(tmp_path):
    project = (tmp_path / "workspace/biomedical_research/project").resolve()
    source = project / "work/retrieval_validation_analysis_2026-11-09/LOCAL_CHECK_AUDIT.md"
    old_state = project.parents[1] / "evcAdaptiveL01/gateway/session/state.json"
    target = exporter.PREFIX + "reports/adaptive_case_loop_2026-11-09/ACTION_SUMMARY.json"
    raw = ("[gateway accounting](" + str(old_state) + ")").encode()
    rewrites = []
    result = exporter.rewrite_markdown(raw, source, exporter.REPORT + "audit.md", {}, {target},
                                      project, rewrites, []).decode()
    assert "public acquisition summary (local state not redistributed)" in result
    assert "ACTION_SUMMARY.json" in result and rewrites[0]["projection"]
    with pytest.raises(ValueError, match="Unpublished/private"):
        exporter.rewrite_markdown(raw, source, exporter.REPORT + "audit.md", {}, set(), project, [], [])


@pytest.mark.parametrize("value", [{"patients": [{"id": 1}]}, {"full_text": "invented source body"}, {"token": "sk-" + "x" * 30}])
def test_forbidden_data_or_credentials_rejected(value):
    with pytest.raises(ValueError):
        exporter.inspect_public(exporter.REPORT + "toy.json", exporter.encoded(value))


def aggregate_review_fixture():
    return {"additional_independent_row_checks": {
        "method": "Invented aggregate arithmetic check", "checks": 1, "maximum_absolute_difference": 0.0,
        "records": [{"run_id": "toy11", "endpoint": "K02-TC-BMI", "recomputed": 1.0,
                     "reported": 1.0, "absolute_difference": 0.0}]}}


def test_aggregate_review_records_allowed_only_in_exact_document_and_path():
    value = aggregate_review_fixture()
    exporter.inspect_public(exporter.REPORT + "INDEPENDENT_RESULT_REVIEW.json", exporter.encoded(value))
    with pytest.raises(ValueError, match="individual-record"):
        exporter.inspect_public(exporter.REPORT + "other.json", exporter.encoded(value))
    with pytest.raises(ValueError, match="individual-record"):
        exporter.inspect_public(exporter.REPORT + "INDEPENDENT_RESULT_REVIEW.json",
                                exporter.encoded({"other": value["additional_independent_row_checks"]}))


@pytest.mark.parametrize("corruption", ["patient_rows", "extra_patient_field", "boolean_value", "unknown_endpoint", "duplicate", "wrong_count"])
def test_patient_rows_and_nonaggregate_shapes_rejected_at_review_path(corruption):
    value = aggregate_review_fixture()
    check = value["additional_independent_row_checks"]
    if corruption == "patient_rows":
        check["records"] = [{"patient_id": "p1", "age": 42, "bmi": 23}]
    elif corruption == "extra_patient_field":
        check["records"][0]["patient_id"] = "p1"
    elif corruption == "boolean_value":
        check["records"][0]["recomputed"] = True
    elif corruption == "unknown_endpoint":
        check["records"][0]["endpoint"] = "patient_bmi"
    elif corruption == "duplicate":
        check["records"].append(deepcopy(check["records"][0])); check["checks"] = 2
    else:
        check["checks"] = 99
    with pytest.raises(ValueError, match="individual-record"):
        exporter.inspect_public(exporter.REPORT + "INDEPENDENT_RESULT_REVIEW.json", exporter.encoded(value))


def test_public_projections_and_transport_chunks(tmp_path, monkeypatch):
    project, bundle, unit, _ = fixture(tmp_path)
    original = b"# Invented aggregate\n" + b"text " * 8000
    write(unit / "RESULTS.md", original)
    monkeypatch.setattr(exporter, "PROJECT_FILES", ())
    monkeypatch.setattr(exporter, "RESEARCH_FILES", ())
    monkeypatch.setattr(exporter, "UNIT_REQUIRED", ("RESULTS.md",))
    monkeypatch.setattr(exporter, "read_tree", lambda *_: {})
    output = unit / "transport"
    result = exporter.prepare(project, tmp_path / "mirror", bundle, output)
    assert result["status"] == "prepared_not_uploaded"
    transport = exporter.read_json(output / "TRANSPORT.json")
    items = {item["path"]: item for item in transport["files"]}
    protocol = json.loads(base64.b64decode(items[exporter.REPORT + "PROTOCOL_PUBLIC.json"]["content"]))
    assert "bundle" not in protocol
    closed = json.loads(base64.b64decode(items[exporter.REPORT + "AUTHOR_CLOSED_PUBLIC.json"]["content"]))
    assert "files" not in closed and "bundle" not in closed
    index = items[exporter.REPORT + "RESULTS.md"]["index"]
    with pytest.raises(ValueError, match="Large blob"):
        exporter.read_blob(output, index)
    first = exporter.read_blob(output, index, 0)
    fragments = [exporter.read_blob(output, index, n)["content"] for n in range(first["chunk_count"])]
    assert all(len(fragment) <= 32000 for fragment in fragments)
    assert base64.b64decode("".join(fragments)) == original
    with pytest.raises(ValueError, match="size must"):
        exporter.read_blob(output, index, 0, 48000)
    assert exporter.sha((unit / "RESULTS.md").read_bytes()) == exporter.sha(original)
