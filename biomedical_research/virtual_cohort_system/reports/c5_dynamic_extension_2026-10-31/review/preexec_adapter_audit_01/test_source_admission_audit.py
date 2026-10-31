"""Source commitment tests use invented metadata only; no C5 source data."""
import json

import pytest

from cohort_harness.contracts import ContractError
from cohort_harness.lifecycle import sha256
from work.c5 import setup_tasks as s


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def setup_fixture(tmp_path, monkeypatch):
    root = tmp_path / "admission_fixture"
    root.mkdir()
    for phase, names in [("initial", ["x1", "x2"]), ("final", ["x1", "x2", "x3"])]:
        packet = {"population_id": "invented-interface-only", "population": "Invented metadata only",
                  "packet_id": phase, "variables": [{"name": x, "unit": "arbitrary"} for x in names]}
        write(root / f"visible/{phase}_source_packet.json", packet)
    commitment = {"committed_files": [
        {"path": f"visible/{phase}_source_packet.json", "access_before_final_outputs": "visible",
         "sha256": sha256(root / f"visible/{phase}_source_packet.json")}
        for phase in ["initial", "final"]]}
    write(root / "source_commitment.json", commitment)
    monkeypatch.setattr(s, "SOURCE_COMMITMENT_PIN", sha256(root / "source_commitment.json"))
    return root


def test_visible_source_mutation_rejected_before_admission(tmp_path, monkeypatch):
    root = setup_fixture(tmp_path, monkeypatch)
    assert s.verify_source_commitment(root)["committed_files"]
    with (root / "visible/initial_source_packet.json").open("a") as f:
        f.write(" ")
    with pytest.raises(ContractError, match="Visible source changed"):
        s.setup(root, "initial")
    assert not (root / "b/p").exists()


def test_replaced_custodian_commitment_is_not_accepted(tmp_path, monkeypatch):
    root = setup_fixture(tmp_path, monkeypatch)
    write(root / "source_commitment.json", {"committed_files": []})
    with pytest.raises(ContractError, match="independently delivered pin"):
        s.verify_source_commitment(root)


def test_changed_initial_author_artifact_blocks_final_source_setup(tmp_path, monkeypatch):
    root = setup_fixture(tmp_path, monkeypatch)
    artifact = root / "b/p/freeze_token.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("original commitment fixture", encoding="utf-8")
    write(root / "INITIAL_AUTHOR_COMMITMENT.json", {
        "source_commitment_sha256": s.SOURCE_COMMITMENT_PIN,
        "bindings": {"b/p/freeze_token.txt": sha256(artifact)}})
    # Native candidate verification has separate coverage; this isolates the
    # pre-authoring commitment comparison and never authors/executes a model.
    monkeypatch.setattr(s, "verify_candidate", lambda *args: None)
    artifact.write_text("changed fixture", encoding="utf-8")
    with pytest.raises(ContractError, match="Initial author artifact changed"):
        s.setup(root, "final")
    assert not (root / "b/j").exists()

