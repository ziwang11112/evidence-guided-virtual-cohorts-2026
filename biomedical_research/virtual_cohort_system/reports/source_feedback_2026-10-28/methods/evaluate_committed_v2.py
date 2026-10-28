"""Custodian-only gated evaluator. Do not invoke before all outputs are frozen.

Manifest schema: {all_initial_final_committed:true, authorize_target_evaluation:true,
custodian_amendment_sha256: HASH,
candidate_commitments:[{label, stage, path, sha256}, ...],
outputs:[{label, stage, seed, path, sha256}, ...]}.

Version 2 adds pre-table-load receipt anchoring and candidate commitment checks;
statistical functions, endpoints, data and original protocol remain unchanged.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from survey_analysis import evaluate,validate_invented

HERE=pathlib.Path(__file__).resolve().parent
VISIBLE=HERE.parent.parent/"visible"/"nhanes_tg_j_v2"
def digest(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def write_json(path,obj): pathlib.Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n",encoding="utf-8")

def verify_preparation_anchors(here, visible, expected_amendment_sha256):
    """Verify the original receipt chain before loading any participant table."""
    amendment_path=here/"evaluator_guard_amendment.json"
    assert digest(amendment_path)==expected_amendment_sha256, "Custodian amendment commitment mismatch"
    amendment=json.loads(amendment_path.read_text(encoding="utf-8"))
    for name,expected in amendment["files"].items():
        assert digest(here/name)==expected, f"Amendment-anchored file mismatch: {name}"
    receipt=json.loads((here/"preparation_receipt.json").read_text(encoding="utf-8"))
    anchors={
        here/"protocol_freeze.json":"protocol_freeze_sha256",
        here/"analysis_protocol.json":"protocol_sha256",
        visible/"input_hashes.json":"visible_input_hashes_sha256",
        here/"design_with_hidden_outcome.csv":"hidden_table_sha256",
        here/"data_provenance.json":"provenance_sha256",
    }
    for path,key in anchors.items():
        assert digest(path)==receipt[key], f"Preparation receipt anchor mismatch: {key}"
    freeze=json.loads((here/"protocol_freeze.json").read_text(encoding="utf-8"))
    for filename,expected in freeze["files"].items():
        assert digest(here/filename)==expected, f"Original frozen file mismatch: {filename}"
    visible_hashes=json.loads((visible/"input_hashes.json").read_text(encoding="utf-8"))
    for filename,expected in visible_hashes["files"].items():
        assert digest(visible/filename)==expected, f"Visible input mismatch: {filename}"
    return receipt

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--commitment",type=pathlib.Path,required=True)
    args=parser.parse_args()
    commitment=json.loads(args.commitment.read_text(encoding="utf-8-sig"))
    assert commitment.get("all_initial_final_committed") is True
    assert commitment.get("authorize_target_evaluation") is True
    outputs=commitment["outputs"]
    assert outputs and {o["stage"] for o in outputs}=={"initial","final"}
    assert len({(o["label"],o["stage"],o["seed"]) for o in outputs})==len(outputs)
    assert {(o["label"],o["seed"]) for o in outputs if o["stage"]=="initial"}=={(o["label"],o["seed"]) for o in outputs if o["stage"]=="final"}
    verify_preparation_anchors(HERE,VISIBLE,commitment["custodian_amendment_sha256"])
    candidates=commitment["candidate_commitments"]
    candidate_keys={(c["label"],c["stage"]) for c in candidates}
    output_keys={(o["label"],o["stage"]) for o in outputs}
    assert len(candidate_keys)==len(candidates), "Duplicate candidate commitments"
    assert candidate_keys==output_keys, "Candidate commitments do not cover all initial/final output stages"
    for candidate in candidates:
        assert digest(pathlib.Path(candidate["path"]).resolve())==candidate["sha256"], "Candidate freeze commitment changed"
    # Hash every output before loading even the first generated table.
    for entry in outputs:
        assert digest(pathlib.Path(entry["path"]).resolve())==entry["sha256"], "Generated output commitment changed"
    observed=pd.read_csv(VISIBLE/"observed.csv")
    prepared=[]
    for entry in outputs:
        path=pathlib.Path(entry["path"]).resolve()
        assert digest(path)==entry["sha256"]
        table=pd.read_csv(path)
        assert list(table.columns)==list(observed.columns)+["tg_mg_dl"]
        pd.testing.assert_frame_equal(table[observed.columns],observed,check_dtype=False,check_exact=True)
        assert np.isfinite(table.tg_mg_dl).all() and table.tg_mg_dl.gt(0).all()
        prepared.append((entry,table.set_index("record_id").tg_mg_dl))
    validation=validate_invented()
    results=HERE/"evaluation"
    results.mkdir(exist_ok=False)
    write_json(results/"release_receipt.json",{"release_utc":datetime.now(timezone.utc).isoformat(),"commitment_path":str(args.commitment.resolve()),"commitment_sha256":digest(args.commitment),"protocol_sha256":digest(HERE/"analysis_protocol.json"),"validation":validation,"custodian_amendment_sha256":commitment["custodian_amendment_sha256"],"candidate_commitments":candidates,"outputs":outputs})
    full=pd.read_csv(HERE/"design_with_hidden_outcome.csv",keep_default_na=True)
    reference=evaluate(full,full.loc[full.eligible.eq(1)].set_index("record_id").LBXTR)
    write_json(results/"reference_analyses.json",reference)
    rows=[]
    for entry,values in prepared:
        measured=evaluate(full,values)
        for endpoint,stats in measured.items():
            ref=reference[endpoint]
            rows.append({"label":entry["label"],"stage":entry["stage"],"seed":entry["seed"],"endpoint":endpoint,**stats,"reference_log_estimate":ref["log_estimate"],"reference_log_ci_low":ref["log_ci_low"],"reference_log_ci_high":ref["log_ci_high"],"reference_direction":ref["direction"],"signed_log_error":stats["log_estimate"]-ref["log_estimate"],"absolute_log_error":abs(stats["log_estimate"]-ref["log_estimate"]),"conditional_synthetic_interval_only":True})
    comparison=pd.DataFrame(rows)
    comparison.to_csv(results/"endpoint_comparison.csv",index=False)
    initial=comparison.loc[comparison.stage.eq("initial"),["label","seed","endpoint","absolute_log_error"]].rename(columns={"absolute_log_error":"initial_absolute_log_error"})
    final=comparison.loc[comparison.stage.eq("final"),["label","seed","endpoint","absolute_log_error"]].rename(columns={"absolute_log_error":"final_absolute_log_error"})
    changes=initial.merge(final,on=["label","seed","endpoint"],validate="one_to_one")
    changes["final_minus_initial_absolute_log_error"]=changes.final_absolute_log_error-changes.initial_absolute_log_error
    changes.to_csv(results/"initial_final_changes.csv",index=False)
    write_json(results/"report_notes.json",{"protocol_unchanged":True,"outputs_evaluated":len(outputs),"endpoints":len(reference),"ci_interpretation":"Reference intervals are survey sampling uncertainty. Generated intervals condition on the generated draw and do not include evidence, model, residual-model, or transport uncertainty. Draw variation is simulation sensitivity.","claims_not_supported":["individual recovery","causal effects","equivalence based on nonsignificance","calibrated imputation uncertainty","general method superiority","measurement replacement"],"no_post_evaluation_builder_revision":True})
    write_json(results/"result_hashes.json",{p.name:digest(p) for p in sorted(results.iterdir()) if p.is_file()})
    print(json.dumps({"status":"complete","outputs":len(outputs),"endpoints":len(reference),"results":str(results)}))

if __name__=="__main__": main()
