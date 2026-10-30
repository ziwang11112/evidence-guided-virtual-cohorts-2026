"""Invented release-boundary tests; no biological data accessed."""
import importlib.util
import json
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location("m11_campaign_test",Path(__file__).resolve().parents[1]/"campaign.py")
campaign=importlib.util.module_from_spec(spec); spec.loader.exec_module(campaign)


def test_evaluate_never_parses_reference_if_gate_fails(monkeypatch):
    calls=[]
    def fail(): raise ValueError("changed generation receipt")
    monkeypatch.setattr(campaign,"verify_release",fail)
    monkeypatch.setattr(campaign,"csv",lambda p: calls.append(p))
    with pytest.raises(ValueError,match="receipt"): campaign.evaluate()
    assert calls==[]


def test_binding_rejects_changed_bytes(tmp_path):
    p=tmp_path/"invented.json"; p.write_text("{}")
    b=campaign.bind(p); campaign.check_bindings([b])
    p.write_text('{"changed":true}')
    with pytest.raises(ValueError,match="Changed binding"):
        campaign.check_bindings([b])


def test_release_cannot_omit_scheduled_output(tmp_path,monkeypatch):
    monkeypatch.setattr(campaign,"HERE",tmp_path)
    launch=tmp_path/"launch.json"; launch.write_text("{}")
    planned={"family":"ha","arm":"initial","seed":1,"run_id":"t_initial_1","bundle":str(tmp_path/"ha"),"candidate":"candidates/initial","freeze_sha256":"irrelevant"}
    monkeypatch.setattr(campaign,"verified_launch",lambda:{"schedule":[planned]})
    campaign.write(tmp_path/"release.json",{"schema_version":"m11-release-1","launch":campaign.bind(launch),"executions":[]})
    with pytest.raises(ValueError,match="Incomplete release"):
        campaign.verify_release()


def test_release_cannot_substitute_another_output_path(tmp_path,monkeypatch):
    monkeypatch.setattr(campaign,"HERE",tmp_path)
    launch=tmp_path/"launch.json"; launch.write_text("{}")
    planned={"family":"ha","arm":"initial","seed":1,"run_id":"t_initial_1","bundle":str(tmp_path/"ha"),"candidate":"candidates/initial","freeze_sha256":"irrelevant"}
    monkeypatch.setattr(campaign,"verified_launch",lambda:{"schedule":[planned]})
    wrong=tmp_path/"wrong.csv"; wrong.write_text("row_id,y\na,1\n")
    entry={**planned,"generated":campaign.bind(wrong),"receipt":campaign.bind(launch)}
    campaign.write(tmp_path/"release.json",{"schema_version":"m11-release-1","launch":campaign.bind(launch),"executions":[entry]})
    with pytest.raises(ValueError,match="Output path mismatch"):
        campaign.verify_release()


def test_launch_cannot_omit_required_binding(tmp_path,monkeypatch):
    monkeypatch.setattr(campaign,"HERE",tmp_path)
    required=tmp_path/"mandatory.txt"; required.write_text("fixed")
    monkeypatch.setattr(campaign,"required_paths",lambda:[required])
    campaign.write(tmp_path/"launch.json",{"schema_version":"m11-launch-1","bindings":[]})
    with pytest.raises(ValueError,match="Mandatory binding"):
        campaign.verified_launch()
