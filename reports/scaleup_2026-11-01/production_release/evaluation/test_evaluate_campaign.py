"""Invented rows and mocked custody/runtime boundaries; no clinical data read."""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from pandas.io.stata import StataMissingValue

import evaluate_campaign as ev


def frame(case,n=24):
    i = np.arange(n,dtype=float)
    age = 40+(i*7 % 37)
    bmi = 19+(i*3 % 13)
    female = (i % 2 == 0).astype(float)
    data = dict(id=[f"invented-{j}" for j in range(n)],age=age,sex=np.where(female,"F","M"),bmi=bmi)
    if case == "K01":
        data["glucose"] = 8+.1*age+.8*bmi+.6*female*bmi+.2*np.sin(i)
    else:
        data["total_cholesterol"] = 3+.03*bmi+.01*age+.04*np.cos(i)
        data["hdl_cholesterol"] = 1.2+.01*bmi+.003*age+.02*np.sin(i)
    return pd.DataFrame(data)


def test_manifest_preparation_never_reads_raw_reference_bytes(monkeypatch,tmp_path):
    original = Path.read_bytes
    forbidden = {ev.SCALE/"private_data/22Jul20_for_Dryad_noIDs.txt",
                 ev.SCALE/"admission_next/private_data/HAALSI_baseline_dataverse_14Apr2017.dta"}
    def read(path):
        assert path not in forbidden
        return original(path)
    monkeypatch.setattr(Path,"read_bytes",read)
    manifest = ev.prepare_evaluation_manifest(tmp_path/"results")
    assert manifest["target_files"]["K01"]["sha256"] == "27c968d5c9e53948bc8ee21e0a5bdc2262ed3c17f1dbafb5bb303050b6715b9f"
    assert manifest["target_files"]["K02"]["sha256"] == "7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9"
    assert manifest["policy"]["fixed_target_report_slots"] == 72


def stata_fixture():
    raw = pd.DataFrame({"prim_key":["a","b","c","d"],"rage":[45,51,63,71],"rsex":[1,2,1,2],
        "c_bs_bmi":[21.0,StataMissingValue(102),26.0,88.0],
        "c_bs_glucose":[5.0,6.0,StataMissingValue(101),99.0]})
    return raw,{"file_dimensions":{"rows":4}}


def test_stata_native_tagged_missing_and_empty_finite_sentinel_list():
    raw,audit = stata_fixture()
    clean,receipt = ev._canonical_stata(raw,audit)
    assert clean["sex"].tolist() == ["M","F","M","F"]
    assert np.isnan(clean.loc[1,"bmi"]) and np.isnan(clean.loc[2,"glucose"])
    assert clean.loc[3,"bmi"] == 88 and clean.loc[3,"glucose"] == 99
    assert receipt["native_tagged_missing_counts"]["bmi"] == {".a":1}
    assert receipt["native_tagged_missing_counts"]["glucose"] == {".":1}


@pytest.mark.parametrize("code",[0,3,"1",True])
def test_unknown_stata_sex_fails_without_label_as_measurement(code):
    raw,audit = stata_fixture(); raw["rsex"] = raw["rsex"].astype(object); raw.loc[0,"rsex"] = code
    with pytest.raises(ev.EvaluationError,match="sex code"): ev._canonical_stata(raw,audit)


def tsv_fixture(token="NA"):
    columns = ["Individual ID","Age","Sex","BMI","Total cholesterol","HDL cholesterol"]
    # TC<HDL is deliberately retained, not used as an exclusion.
    rows = [["toy-a","47","F","88","35","90"],["toy-b","61","M",token,"110","40"]]
    payload = ("\ufeff"+"\t".join(columns)+"\n"+"\n".join("\t".join(row) for row in rows)).encode("utf-8")
    return payload,{"columns":columns,"rows_in_deposit":2}


def test_tsv_missing_tokens_and_reference_lipids_not_converted():
    payload,audit = tsv_fixture(" NA ")
    payload = payload.replace(b"\tF\t",b"\t F \t")
    clean,receipt = ev._canonical_tsv(payload,audit)
    assert clean.loc[0,"sex"] == "F"
    assert np.isnan(clean.loc[1,"bmi"]) and clean.loc[0,"bmi"] == 88
    assert clean.loc[0,"total_cholesterol"] == 35 and clean.loc[0,"hdl_cholesterol"] == 90
    assert receipt["conversion_applied"] is False


@pytest.mark.parametrize("token",["na","N/A","nan","inf","bad"])
def test_unrecognized_tsv_tokens_fail_whole_preparation(token):
    payload,audit = tsv_fixture(token)
    with pytest.raises(ev.EvaluationError,match="numerical token"): ev._canonical_tsv(payload,audit)


def test_canonical_id_duplicates_fail():
    raw,audit = stata_fixture(); raw.loc[1,"prim_key"] = "a"
    with pytest.raises(ev.EvaluationError,match="ID integrity"): ev._canonical_stata(raw,audit)


def test_real_stata_reader_on_invented_file_and_hash_failure_before_parse(tmp_path,monkeypatch):
    canonical = frame("K01")
    raw = canonical.rename(columns={v:k for k,v in ev.MAPPINGS["K01"].items()})
    raw["rsex"] = raw["rsex"].map({"M":1,"F":2}).astype("int8")
    raw.loc[0,"c_bs_bmi"] = np.nan
    labels = {name:"INVENTED "+name for name in raw.columns}
    path = tmp_path/"invented-only.dta"
    raw.to_stata(path,write_index=False,version=118,variable_labels=labels,value_labels={"rsex":{1:"Male",2:"Female"}})
    payload = path.read_bytes()
    audit = {"file_dimensions":{"rows":24,"columns":5},"selected_field_metadata":{name:{"variable_label":label} for name,label in labels.items()}}
    # The production reader expects the official SEX value-label set name.
    # pandas names this invented set rsex; change only the reader metadata seam.
    real_labels = ev.StataReader.value_labels
    def invented_labels(reader):
        value = real_labels(reader)
        return {"SEX":value["rsex"]}
    monkeypatch.setattr(ev.StataReader,"value_labels",invented_labels)
    monkeypatch.setattr(ev,"read_json",lambda p:audit)
    binding = {"path":str(path),"bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest()}
    clean,receipt = ev._load_reference("K01",binding)
    assert len(clean)==24 and np.isnan(clean.loc[0,"bmi"])
    np.testing.assert_allclose(clean.glucose,canonical.glucose)
    assert receipt["input_sha256"]==binding["sha256"]
    binding["sha256"]="0"*64
    with pytest.raises(ev.EvaluationError,match="Reference bytes"):
        ev._load_reference("K01",binding)


def test_approved_k02_units_and_original_analysis_compose_with_independent_qr():
    original = frame("K02")
    task = ev.read_json(ev.SCALE/"case_k02/request/task_template.json")
    mapped,receipt = ev._map_generated_units(original,"K02",task,{"invented_fixture":"not_actual_execution"})
    np.testing.assert_array_equal(mapped[["id","age","sex","bmi"]],original[["id","age","sex","bmi"]])
    np.testing.assert_allclose(mapped["total_cholesterol"],original["total_cholesterol"]*38.67,rtol=0,atol=0)
    np.testing.assert_allclose(mapped["hdl_cholesterol"],original["hdl_cholesterol"]*38.67,rtol=0,atol=0)
    result = ev._analyze(mapped,"K02","generated")
    x = np.column_stack([np.ones(len(mapped)),mapped.age,(mapped.sex=="F").astype(float),mapped.bmi])
    q,r = np.linalg.qr(x)
    residuals = []
    for key,column in [(ev.IDS["K02"][0],"hdl_cholesterol"),(ev.IDS["K02"][1],"total_cholesterol")]:
        y = mapped[column].to_numpy(); beta = np.linalg.solve(r,q.T@y)
        assert result["estimands"][key]["estimate"] == pytest.approx(5*beta[3],abs=1e-11)
        residuals.append(y-x@beta)
    assert result["estimands"][ev.IDS["K02"][2]]["estimate"] == pytest.approx(np.corrcoef(residuals)[0,1],abs=1e-10)
    assert receipt["execution_binding_status"] == "caller_asserted_not_verified_by_unit_adapter"
    wrong = copy.deepcopy(task); wrong["columns"][-1]["unit"] = "mg/dL"
    with pytest.raises(ev.EvaluationError,match="actual target task"):
        ev._map_generated_units(original,"K02",wrong,{"invented":True})


def test_original_k01_analysis_composes_with_independent_raw_qr():
    data = frame("K01")
    result = ev._analyze(data,"K01","reference")
    x = np.column_stack([np.ones(len(data)),data.age,(data.sex=="F").astype(float),data.bmi])
    q,r = np.linalg.qr(x); beta = np.linalg.solve(r,q.T@data.glucose)
    assert result["estimands"][ev.IDS["K01"][0]]["estimate"] == pytest.approx(5*beta[3],abs=1e-10)
    assert result["estimands"][ev.IDS["K01"][1]]["estimate"] == pytest.approx(10*beta[1],abs=1e-10)
    xi = np.column_stack([x,x[:,2]*x[:,3]]); q,r = np.linalg.qr(xi)
    beta = np.linalg.solve(r,q.T@data.glucose)
    assert result["estimands"][ev.IDS["K01"][2]]["estimate"] == pytest.approx(5*beta[4],abs=1e-10)
    assert result["metric_denominators"]["glucose"]["sample_sd"] == pytest.approx(data.glucose.std(ddof=1))


def empty_state():
    cc = ev._controller()
    state = {"constructors":{},"wave_closed":None,"reveal":None}
    ledger = SimpleNamespace()
    for case in ev.CASES:
        for constructor in ev.CONSTRUCTORS:
            record = {"stages":{},"decision":{"decision":"stop"},"closed":None}
            inventory = cc.CampaignLedger._final_inventory(ledger,case,constructor,record)
            record["closed"] = {"key":f"{case}:{constructor}","final_inventory":inventory}
            state["constructors"][f"{case}:{constructor}"] = record
    closed = {k:v["closed"] for k,v in state["constructors"].items()}
    state["wave_closed"] = {"closed_inventory":closed,"closed_inventory_sha256":ev.digest(closed)}
    return state


@pytest.fixture
def gate_fixture(tmp_path,monkeypatch):
    state = empty_state()
    manifest = {"output_directory":str(tmp_path/"results"),"dependencies":[]}
    path = tmp_path/"evaluation.json"; path.write_bytes(ev.canonical(manifest))
    evaluator = {"path":str(Path(ev.__file__).resolve()),"sha256":ev.file_hash(ev.__file__)}
    artifact = {"path":str(path.resolve()),"sha256":ev.file_hash(path)}
    release = {"designated_evaluator":evaluator,"artifacts":[artifact]}
    reveal = {"release_sha256":"invented-release","evaluator_code_sha256":evaluator["sha256"],
              "cases":list(ev.CASES),"closed_inventory_sha256":state["wave_closed"]["closed_inventory_sha256"]}
    state["reveal"] = reveal
    events = [{"kind":"target_reveal","event_sha256":"invented-reveal","payload":reveal}]
    ledger = SimpleNamespace(manifest=release,release_sha256="invented-release",_read=lambda:(state,events))
    monkeypatch.setattr(ev._controller().CampaignLedger,"open",lambda p:ledger)
    monkeypatch.setattr(ev,"prepare_evaluation_manifest",lambda p:copy.deepcopy(manifest))
    return ledger,state,manifest,path,events


@pytest.mark.parametrize("defect",["wrong_evaluator","missing_reveal","wrong_receipt","missing_manifest","missing_dependency","open_k02","changed_inventory"])
def test_reveal_gate_rejects_before_any_target_load(gate_fixture,monkeypatch,defect):
    ledger,state,manifest,path,events = gate_fixture
    receipt = "invented-reveal"
    if defect == "wrong_evaluator": ledger.manifest["designated_evaluator"]["sha256"] = "wrong"
    elif defect == "missing_reveal": state["reveal"] = None
    elif defect == "wrong_receipt": receipt = "another-reveal"
    elif defect == "missing_manifest": ledger.manifest["artifacts"] = []
    elif defect == "missing_dependency":
        manifest["dependencies"] = [{"path":"invented.py","sha256":"not-bound"}]
        path.write_bytes(ev.canonical(manifest)); ledger.manifest["artifacts"][0]["sha256"] = ev.file_hash(path)
    elif defect == "open_k02": state["constructors"]["K02:A05"]["closed"] = None
    elif defect == "changed_inventory": events[0]["payload"]["closed_inventory_sha256"] = "changed"
    monkeypatch.setattr(ev,"_load_reference",lambda *a:pytest.fail("Reference loader must not be reached"))
    with pytest.raises(ev.EvaluationError): ev.evaluate_revealed_campaign("invented-ledger",path,receipt)
    assert not Path(manifest["output_directory"]).exists()


def test_actual_gate_success_then_inventory_failure_still_precedes_target_loading(gate_fixture,monkeypatch):
    _,_,manifest,path,_ = gate_fixture
    def invalid(*args): raise ev.EvaluationError("invented changed candidate")
    monkeypatch.setattr(ev,"_verify_inventory",invalid)
    monkeypatch.setattr(ev,"_load_reference",lambda *a:pytest.fail("Reference loader must not be reached"))
    with pytest.raises(ev.EvaluationError,match="changed candidate"):
        ev.evaluate_revealed_campaign("invented-ledger",path,"invented-reveal")
    assert not Path(manifest["output_directory"]).exists()


def invented_plans():
    result = []
    for case in ev.CASES:
        for constructor in ev.CONSTRUCTORS:
            for stage in ("initial","final"):
                for seed in ev.SEEDS:
                    origin = f"{case}_{constructor}_initial_target_{seed}"
                    result.append(dict(case=case,constructor=constructor,stage=stage,seed=seed,
                        report_id=f"{case}_{constructor}_{stage}_target_{seed}",alias_of=origin if stage=="final" else None,
                        origin_trial={"id":origin},entry={},verified_trial={"invented":True},
                        usable=not(case=="K01" and constructor=="A05"),
                        stage_verified_success=not(case=="K01" and constructor=="A05"),
                        execution_disposition="retained_alias" if stage=="final" else "invented_output"))
    return result


def test_complete_invented_evaluation_preserves_72_slots_aliases_failures_and_rejects_rerun(tmp_path,monkeypatch):
    state = empty_state(); output = tmp_path/"evaluation"
    manifest = {"output_directory":str(output),"target_files":{"K01":{},"K02":{}}}
    ledger = SimpleNamespace(release_sha256="invented-release")
    monkeypatch.setattr(ev,"_gate",lambda *args:(ledger,state,manifest,{"invented_manifest":True}))
    monkeypatch.setattr(ev,"_verify_inventory",lambda *args:{"invented_verified_boundary":True})
    monkeypatch.setattr(ev,"_slot_plan",lambda *args:invented_plans())
    calls = {"reference":0,"generated":0}
    def reference(case,binding): calls["reference"]+=1; return frame(case),{"invented":True}
    def generated(case,*args): calls["generated"]+=1; return frame(case),None
    monkeypatch.setattr(ev,"_load_reference",reference); monkeypatch.setattr(ev,"_load_generated",generated)
    completion = ev.evaluate_revealed_campaign("invented","invented","invented")
    assert completion["status"] == "complete" and calls == {"reference":2,"generated":33}
    full = ev.read_json(output/"FULL_EVALUATION.json"); public = ev.read_json(output/"PUBLISHABLE_AGGREGATES.json")
    assert len(full["target_slots"]) == len(public["target_slots"]) == 72
    assert full["aggregate"]["cases"]["K01:final"]["agent_pass_counts"]["0.1"] == 4
    assert full["aggregate"]["cases"]["K01:final"]["agent_denominator"] == 5
    assert full["aggregate"]["positive_wave_a_scientific_gate"] is True
    assert full["aggregate"]["wave_b_execution_authorized"] is False
    assert all("verified_trial" not in row and "unit_conversion_receipt" not in row for row in public["target_slots"])
    for pair in full["aggregate"]["initial_final_paired"]:
        for endpoint in pair["endpoints"].values():
            if endpoint["status"] == "computed":
                assert endpoint["effect_change"] == endpoint["normalized_error_reduction"] == 0
    with pytest.raises(FileExistsError): ev.evaluate_revealed_campaign("invented","invented","invented")
    assert calls == {"reference":2,"generated":33}


def test_undefined_denominator_fails_and_k02_alone_never_opens_gate():
    references = {case:ev._analyze(frame(case),case,"reference") for case in ev.CASES}
    generated = ev._analyze(frame("K01"),"K01","generated")
    bad = copy.deepcopy(references["K01"]); bad["metric_denominators"]["glucose"]["sample_sd"] = None
    assert all(not row["passes"]["0.1"] for row in ev.compare("K01",generated,bad).values())
    assert all(row["signed_raw_discrepancy"] == 0 for row in ev.compare("K01",generated,bad).values())
    slots = []
    for plan in invented_plans():
        case = plan["case"]
        analysis = ev._unavailable(case,"invented_failure") if case == "K01" else ev._analyze(frame(case),case,"generated")
        slots.append({**plan,"analysis":analysis,"comparison":ev.compare(case,analysis,references[case])})
    aggregate = ev.summarize(slots,references)
    assert aggregate["cases"]["K02:final"]["agent_pass_counts"]["0.1"] == 5
    assert aggregate["positive_wave_a_scientific_gate"] is False


def test_source_stage_failure_preserves_target_diagnostics_but_fails_bundle():
    references = {case:ev._analyze(frame(case),case,"reference") for case in ev.CASES}
    slots = []
    for plan in invented_plans():
        case = plan["case"]
        analysis = ev._analyze(frame(case),case,"generated")
        slots.append({**plan,"stage_verified_success":False if case=="K01" else True,
                      "analysis":analysis,"comparison":ev.compare(case,analysis,references[case])})
    assert all(all(endpoint["passes"]["0.1"] for endpoint in slot["comparison"].values()) for slot in slots)
    aggregate = ev.summarize(slots,references)
    assert aggregate["cases"]["K01:final"]["agent_pass_counts"]["0.1"] == 0
    assert aggregate["cases"]["K02:final"]["agent_pass_counts"]["0.1"] == 5
    assert aggregate["positive_wave_a_scientific_gate"] is False


def test_slot_plan_keeps_all_failed_unrun_slots_and_exact_final_alias_identity():
    state = empty_state()
    plans = ev._slot_plan(state)
    assert len(plans) == 72 and sum(p["stage"]=="final" for p in plans)==36
    assert not any(p["usable"] for p in plans)
    state["constructors"]["K01:A01"]["decision"]["decision"] = "retain"
    plans = ev._slot_plan(state)
    aliases = [p for p in plans if p["case"]=="K01" and p["constructor"]=="A01" and p["stage"]=="final"]
    assert len(aliases)==3 and all(p["alias_of"]==p["origin_trial"]["id"] for p in aliases)
