"""Synthetic phase-gate tests; authored generators and APIs never execute."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import execute_stages as host
import evaluate_stages as evaluation


def setup_workspace(tmp_path,monkeypatch,*,failed=False):
    monkeypatch.setattr(host,"ROOT",tmp_path)
    monkeypatch.setattr(host,"implementation_hashes",lambda:{"fixture_implementation":"stable"})
    def forbidden(*args,**kwargs):raise AssertionError("Scientific generator execution forbidden in fixtures")
    monkeypatch.setattr(host.execution,"_capture",forbidden)
    host.write(tmp_path/"PROTOCOL.json",{"fixture":True})
    host.write(tmp_path/"RUN_PLAN.json",{"fixture":True})
    host.write(tmp_path/"calls/initial/fixture/receipt.json",{"fixture":True})
    host.write(tmp_path/"calls/review/fixture/receipt.json",{"fixture":True})
    host.write(tmp_path/"_host_only/REFERENCE_COPY.json",{"fixture":True})
    refs={}
    for case in host.CASES:
        refs[case]={key:evaluation.trusted().endpoint(key,unit,0.,uncertainty={"status":"unavailable","reason":"synthetic fixture"})
                    for category in ["analyses","diagnostics"] for key,unit in evaluation.trusted().ENDPOINTS[case][category]}
    host.write(tmp_path/"_host_only/REFERENCE_SNAPSHOT.json",{"author_visible":False,"patient_rows_read":False,"new_reference_fits":False,
                                                           "sources":{},"references":refs})
    records=[];branches=[]
    for case,packet_case in [("PNS","PNS"),("lipids","LIPID")]:
        task=host.read(host.PREVIOUS/f"packets/{packet_case}/task.json")
        taskpath=f"packets/{packet_case}/task.json";host.write(tmp_path/taskpath,task)
        for suffix,model,role in [("SOL_A","OA_SOL","paired_parent"),("SOL_B","OA_SOL","benchmark"),
                                  ("ASTRA","OA_ASTRA","benchmark"),("DS","DS_PRO","benchmark")]:
            ident=f"{case}_{suffix}";candidate=f"candidates/{ident}"
            folder=tmp_path/candidate;folder.mkdir(parents=True)
            (folder/"generator.py").write_text("raise RuntimeError('must never be executed in fixtures')\ndef generate(observed,spec,seed):\n    return None\n")
            host.write(folder/"model_spec.json",{"task":task,"model":{"fixture":True}})
            host.write(folder/"decision_record.json",{"fixture":True})
            records.append({"parent_id":ident,"case_id":case,"model_config":model,"role":role,"task_path":taskpath,
                            "candidate_path":None if failed else candidate,"status":"failed" if failed else "sealed"})
            if role=="paired_parent":
                branches += [{"branch_id":ident+"_FB","parent_id":ident,"arm":"feedback"},
                             {"branch_id":ident+"_SL","parent_id":ident,"arm":"second_look"}]
    return records,branches


def dummy_diagnostic_gate(tmp_path,monkeypatch,initial):
    host.write(tmp_path/"DIAGNOSTIC_CLOSURE.json",{"fixture":True})
    reports={}
    for row in initial["records"]:
        if row["role"]!="paired_parent":continue
        path=f"_host_only/diagnostic_reports/{row['parent_id']}.json"
        host.write(tmp_path/path,{"parent_id":row["parent_id"],"fixture":"own generated summary"})
        reports[row["parent_id"]]={"path":path,"sha256":host.sha(tmp_path/path)}
    host.write(tmp_path/"DIAGNOSTIC_REPORTS.json",{"kind":"economy_generated_only_diagnostic_reports_v1","target_reference_read":False,
        "diagnostic_closure_sha256":host.sha(tmp_path/"DIAGNOSTIC_CLOSURE.json"),"reports":reports})
    monkeypatch.setattr(host,"verify_stage_closure",lambda phase:{"stage":phase,"fixture":True})


def test_exact_same_parent_branch_schedule(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch)
    value=host.seal_initial(rows,branches)
    assert len(host.versions("diagnostic"))==2
    assert host.SEEDS["diagnostic"]==[41001,41003,41007]
    assert host.SEEDS["evaluation"]==[42001,42003,42007]
    assert sum(host.SLOTS.values())==42
    assert all(len([b for b in value["branches"] if b["parent_id"]==r["parent_id"]])==2
               for r in value["records"] if r["role"]=="paired_parent")


def test_preapproval_and_early_evaluation_rejected(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch);host.seal_initial(rows,branches)
    with pytest.raises(ValueError):host.run_stage("diagnostic")
    with pytest.raises(ValueError):host.approve_stage("evaluation","too soon")
    assert not (tmp_path/"executions").exists()


def test_initial_history_mutation_rejected(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch);host.seal_initial(rows,branches)
    (tmp_path/"calls/initial/fixture/receipt.json").write_text('{"changed":true}')
    with pytest.raises(ValueError,match="history changed"):host.verify_initial()


def test_branch_parent_replacement_rejected(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch)
    branches[0]["parent_id"]="PNS_SOL_B"
    with pytest.raises(ValueError,match="share each paired parent"):host.seal_initial(rows,branches)


def test_feedback_only_own_assigned_arm(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch);initial=host.seal_initial(rows,branches)
    dummy_diagnostic_gate(tmp_path,monkeypatch,initial)
    assert evaluation.feedback_for("PNS_SOL_A_FB")["parent_id"]=="PNS_SOL_A"
    with pytest.raises(ValueError,match="second-look"):evaluation.feedback_for("PNS_SOL_A_SL")


def test_retained_final_exact_initial_bytes_and_review_disposition(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch);initial=host.seal_initial(rows,branches)
    dummy_diagnostic_gate(tmp_path,monkeypatch,initial)
    parents={r["parent_id"]:r for r in initial["records"]}
    finals=[dict(b,disposition="retained_noop" if b["arm"]=="feedback" else "retained_review_failed",
                 candidate_path=parents[b["parent_id"]]["candidate_path"],reason="Fixture retention, no scientific host edits") for b in branches]
    seal=host.seal_reviews(finals)
    assert len(host.versions("evaluation"))==12
    assert all(r["files"]==parents[r["parent_id"]]["files"] for r in seal["records"])


def test_failed_parent_cannot_be_rescued(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch,failed=True);initial=host.seal_initial(rows,branches)
    dummy_diagnostic_gate(tmp_path,monkeypatch,initial)
    finals=[dict(b,disposition="parent_failed",candidate_path=None,reason="Failed parent retained in denominator") for b in branches]
    finals[0].update(disposition="revised",candidate_path="candidates/PNS_SOL_B")
    with pytest.raises(ValueError,match="cannot be rescued"):host.seal_reviews(finals)


def test_empty_review_history_only_when_all_parents_failed(tmp_path,monkeypatch):
    monkeypatch.setattr(host,"ROOT",tmp_path)
    records=[{"disposition":"parent_failed"} for _ in range(4)]
    host.write(tmp_path/"REVIEW_OUTCOMES.json",{"records":records})
    assert set(host.review_history(records))=={"REVIEW_OUTCOMES.json"}
    records[0]["disposition"]="retained_noop"
    with pytest.raises(ValueError,match="Missing review history"):host.review_history(records)


def test_reference_reader_never_opens_snapshot_before_evaluation_closure(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch);host.seal_initial(rows,branches)
    original=host.read;opened=[]
    def track(path):
        opened.append(Path(path).name)
        return original(path)
    monkeypatch.setattr(host,"read",track)
    with pytest.raises(ValueError):evaluation.references_after_evaluation()
    assert "REFERENCE_SNAPSHOT.json" not in opened


def test_unchanged_isolation_command():
    command=host.execution._command(host.execution.DEFAULT_RUNTIME,host.ROOT/"fixture_run",60)
    assert "--unshare-all" in command and "--clearenv" in command and command.count("--bind")==2
    assert "/runtime/bin/python" in command and "/input/worker.py" in command
    assert not any("REFERENCE" in v or "calls/" in v for v in command)


def test_all_failed_stage_accounting_has_no_worker_or_reference_feedback(tmp_path,monkeypatch):
    rows,branches=setup_workspace(tmp_path,monkeypatch,failed=True);host.seal_initial(rows,branches)
    host.approve_stage("diagnostic","Synthetic failures only; capture forbidden")
    diagnostic=host.run_stage("diagnostic")
    assert len(diagnostic["records"])==6 and diagnostic["physical_generator_attempts"]==0
    original=host.read
    def forbid_reference(path):
        if Path(path).name=="REFERENCE_SNAPSHOT.json":raise AssertionError("Reference values opened during diagnostic feedback")
        return original(path)
    monkeypatch.setattr(host,"read",forbid_reference)
    report=evaluation.prepare_diagnostics()
    assert report["target_reference_read"] is False
    assert evaluation.feedback_for("PNS_SOL_A_FB")["parent_id"]=="PNS_SOL_A"
    with pytest.raises(ValueError):evaluation.feedback_for("PNS_SOL_A_SL")
    monkeypatch.setattr(host,"read",original)
    finals=[dict(b,disposition="parent_failed",candidate_path=None,reason="Failed parent; no branch rescue") for b in branches]
    host.seal_reviews(finals);host.approve_stage("evaluation","Synthetic failures only; capture forbidden")
    final=host.run_stage("evaluation")
    assert len(final["records"])==36 and final["physical_generator_attempts"]==0
    result=evaluation.evaluate()
    assert result=={"evaluation_slots":36,"successful_evaluation_tables":0,"complete_evaluation_tables":0}
    stored=host.read(tmp_path/"EVALUATION.json")
    assert len(stored["version_summaries"])==72 and len(stored["paired_seed_contrasts"])==36
    with pytest.raises(ValueError):host.run_stage("evaluation")
