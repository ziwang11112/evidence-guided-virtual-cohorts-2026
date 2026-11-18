"""Engineering fixtures only; never execute an authored scientific generator."""
import itertools
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import execute_pilot as host
import analyze_pilot as analysis


@pytest.fixture
def factorial():
    a,b,c,d = np.array(list(itertools.product([-1.,1.], repeat=4))).T
    female=(b+1)/2
    residual1=3*d
    residual2=4*(.4*d+np.sqrt(1-.4**2)*a*d)
    pns=pd.DataFrame({"row_id":range(16),"age":50+10*a,"female":female,"bmi":25+5*c,
                      "sbp":120+2*a-3*female+7*c+residual1,
                      "dbp":80+a-2*female+4*c+residual2})
    lipid=pd.DataFrame({"id":[f"s{i}" for i in range(16)],"age":50+10*a,"sex":np.where(female,"F","M"),"bmi":25+5*c,
                        "total_cholesterol":(200+2*a-3*female+7*c+residual1)/38.67,
                        "hdl_cholesterol":(60+a-2*female-4*c+residual2)/38.67})
    return pns,lipid


def lookup(value,category="analyses"): return {e["id"]:e for e in value[category]}


def test_pns_known_adjusted_slopes_and_residual_correlation(factorial):
    value=analysis.analyze_frame(factorial[0],"PNS",expected_rows=None)
    rows=lookup(value)
    assert rows["bmi_sbp"]["value"] == pytest.approx(7,abs=1e-11)
    assert rows["bmi_dbp"]["value"] == pytest.approx(4,abs=1e-11)
    assert rows["residual_correlation"]["value"] == pytest.approx(.4,abs=1e-11)
    # Analytic variance: orthogonal age, female, BMI and residual components.
    assert lookup(value,"diagnostics")["sbp.sd_population"]["value"] == pytest.approx(np.sqrt(4+9/4+49+9))


def test_lipid_known_slopes_conversion_and_sample_sd(factorial):
    value=analysis.analyze_frame(factorial[1],"lipids",expected_rows=None)
    rows=lookup(value)
    assert rows["K02-TC-BMI"]["value"] == pytest.approx(7,abs=1e-11)
    assert rows["K02-HDL-BMI"]["value"] == pytest.approx(-4,abs=1e-11)
    assert rows["K02-LIPID-RESIDUAL"]["value"] == pytest.approx(.4,abs=1e-11)
    assert lookup(value,"diagnostics")["total_cholesterol.sd_sample"]["value"] == pytest.approx(np.sqrt((4+9/4+49+9)*16/15))


@pytest.mark.parametrize("case,index,column",[("PNS",0,"sbp"),("lipids",1,"total_cholesterol")])
def test_mixed_numeric_strings_refused_without_coercion(factorial,case,index,column):
    frame=factorial[index].copy();frame[column]=frame[column].astype(object);frame.loc[0,column]="123"
    with pytest.raises(ValueError,match="Canonical real numeric"): analysis.analyze_frame(frame,case,expected_rows=None)
    assert frame.loc[0,column] == "123"


@pytest.mark.parametrize("bad",[np.nan,np.inf,-np.inf])
def test_nonfinite_rows_not_silently_filtered(factorial,bad):
    frame=factorial[0].copy();frame.loc[0,"dbp"]=bad
    with pytest.raises(ValueError,match="finite"): analysis.analyze_frame(frame,"PNS",expected_rows=None)


def test_lipid_zero_eligibility_not_silently_filtered(factorial):
    frame=factorial[1].copy();frame.loc[0,"bmi"]=0
    with pytest.raises(ValueError,match="eligibility"): analysis.analyze_frame(frame,"lipids",expected_rows=None)
    assert len(frame)==16


def test_executor_strict_positive_eligibility(factorial):
    task=host.read(host.ROOT/"packets/LIPID/task.json")
    task["n_rows"]=16
    frame=factorial[1].copy()
    host.validate_generated_output(frame,task,"lipids")
    frame.loc[0,"total_cholesterol"]=0
    with pytest.raises(ValueError,match="strictly positive"): host.validate_generated_output(frame,task,"lipids")


def test_component_violations_preserved(factorial):
    pns,lipid=[x.copy() for x in factorial]
    pns.loc[0,"sbp"]=pns.loc[0,"dbp"]-1
    lipid.loc[0,"hdl_cholesterol"]=lipid.loc[0,"total_cholesterol"]+1
    before=[pns.copy(deep=True),lipid.copy(deep=True)]
    for frame,case,component in [(pns,"PNS","sbp_below_dbp_fraction"),(lipid,"lipids","hdl_above_total_fraction")]:
        value=analysis.analyze_frame(frame,case,expected_rows=None)
        assert lookup(value,"diagnostics")[component]["value"]==pytest.approx(1/16)
        assert value["quality"]["component_violation_count"]==1
    pd.testing.assert_frame_equal(before[0],pns);pd.testing.assert_frame_equal(before[1],lipid)


def test_rank_deficiency_and_exact_residual_degeneracy(factorial):
    frame=factorial[0].copy();frame["bmi"]=25
    value=analysis.analyze_frame(frame,"PNS",expected_rows=None)
    assert all(e["status"]=="unavailable" for e in value["analyses"])
    frame=factorial[0].copy();frame["sbp"]=100+frame.age
    value=analysis.analyze_frame(frame,"PNS",expected_rows=None)
    assert lookup(value)["residual_correlation"]["status"]=="unavailable"


def test_missing_reference_remains_unavailable(factorial):
    value=analysis.analyze_frame(factorial[1],"lipids",expected_rows=None)
    refs={"lipids":{e["id"]:analysis.endpoint(e["id"],e["unit"],None,"not supplied")
                     for k in ["analyses","diagnostics"] for e in value[k]}}
    value=analysis.compare(value,"lipids",refs)
    assert all(e["comparison_status"]=="unavailable" and e["absolute_difference"] is None
               for k in ["analyses","diagnostics"] for e in value[k])


def test_backend_command_has_no_unrestricted_fallback():
    # Windows drive path is required by the unchanged adapter.
    command=host.execution._command(host.execution.DEFAULT_RUNTIME,host.ROOT/"fixture_run",60)
    assert "--unshare-all" in command and "--clearenv" in command
    assert "/runtime/bin/python" in command and "/input/worker.py" in command
    assert all("REFERENCE" not in v and "credential" not in v.lower() for v in command)
    assert command.count("--bind")==2


def test_preapproval_gate_never_calls_capture(tmp_path,monkeypatch):
    monkeypatch.setattr(host,"ROOT",tmp_path)
    def forbidden(*args,**kwargs): raise AssertionError("generator execution reached")
    monkeypatch.setattr(host.execution,"_capture",forbidden)
    with pytest.raises(ValueError): host.run_all()
    assert not (tmp_path/"executions").exists()


def test_reference_loader_requires_closed_all_slots(tmp_path,monkeypatch):
    monkeypatch.setattr(host,"ROOT",tmp_path)
    with pytest.raises(ValueError): analysis.load_references()


def test_static_program_validation_never_executes_top_level(tmp_path):
    program=tmp_path/"generator.py"
    program.write_text("raise RuntimeError('not executed')\ndef generate(observed,spec,seed):\n    return None\n")
    host.lifecycle.validate_program(program)


def test_protocol_schedule_and_endpoint_contract():
    protocol=json.loads((host.ROOT/"EVALUATION_PROTOCOL.json").read_text())
    assert protocol["seeds"]==[31001,31003,31007] and protocol["max_tables"]==60
    for case in host.CASES:
        assert protocol["cases"][case]["primary"]==[key for key,_ in analysis.ENDPOINTS[case]["analyses"]]
        assert len(analysis.ENDPOINTS[case]["analyses"])==3


def test_closure_rejects_changed_final_file(tmp_path,monkeypatch):
    original=host.ROOT
    monkeypatch.setattr(host,"ROOT",tmp_path)
    monkeypatch.setattr(host,"implementation_hashes",lambda:{"fixture":"same"})
    host.write(tmp_path/"EVALUATION_PROTOCOL.json",{"seeds":host.SEEDS,"n_rows":3000,"max_tables":60})
    host.write(tmp_path/"_host_only/REFERENCE_SNAPSHOT.json",{"fixture":True})
    host.write(tmp_path/"calls/synthetic_fixture/receipt.json",{"fixture":True,"generator_executed":False})
    records=[]
    for case,source in [("PNS","PNS"),("lipids","LIPID")]:
        task=host.read(original/f"packets/{source}/task.json")
        host.write(tmp_path/f"tasks/{case}.json",task)
        for i in range(10):
            ident=f"{case}_{i}";directory=tmp_path/"candidates"/ident;directory.mkdir(parents=True)
            (directory/"generator.py").write_text("def generate(observed,spec,seed):\n    return None\n")
            host.write(directory/"model_spec.json",{"task":task,"model":{}})
            host.write(directory/"decision_record.json",{})
            records.append({"construction_id":ident,"case_id":case,"task_path":f"tasks/{case}.json",
                            "candidate_path":f"candidates/{ident}","status":"sealed","model_config":f"model{i//2}","context":i%2+1})
    host.create_construction_closure(records)
    assert host.verify_construction_closure()["max_tables"]==60
    target=tmp_path/"candidates/PNS_0/generator.py"
    target.write_text(target.read_text()+"# mutation\n")
    with pytest.raises(ValueError,match="changed"): host.verify_construction_closure()


def test_all_failed_constructions_keep_sixty_slots_without_worker(tmp_path,monkeypatch):
    original=host.ROOT
    monkeypatch.setattr(host,"ROOT",tmp_path)
    monkeypatch.setattr(host,"implementation_hashes",lambda:{"fixture":"same"})
    def forbidden(*args,**kwargs): raise AssertionError("Worker must never launch for failed constructions")
    monkeypatch.setattr(host.execution,"_capture",forbidden)
    host.write(tmp_path/"EVALUATION_PROTOCOL.json",{"seeds":host.SEEDS,"n_rows":3000,"max_tables":60})
    host.write(tmp_path/"_host_only/REFERENCE_SNAPSHOT.json",{"fixture":True})
    host.write(tmp_path/"calls/synthetic_fixture/receipt.json",{"fixture":True})
    records=[]
    for case,source in [("PNS","PNS"),("lipids","LIPID")]:
        host.write(tmp_path/f"tasks/{case}.json",host.read(original/f"packets/{source}/task.json"))
        for model in range(5):
            for context in [1,2]:
                records.append({"construction_id":f"{case}_{model}_{context}","case_id":case,"task_path":f"tasks/{case}.json",
                                "candidate_path":None,"status":"failed","model_config":f"model{model}","context":context})
    host.create_construction_closure(records)
    host.approve_frozen_execution("Synthetic fixture accounting only; no generator exists or runs")
    closed=host.run_all()
    assert len(closed["records"])==60 and closed["physical_generator_attempts"]==0
    assert all(r["status"]=="construction_failed" for r in closed["records"])
    assert host.evaluation_gate()[1]==closed
    with pytest.raises(ValueError): host.run_all()
