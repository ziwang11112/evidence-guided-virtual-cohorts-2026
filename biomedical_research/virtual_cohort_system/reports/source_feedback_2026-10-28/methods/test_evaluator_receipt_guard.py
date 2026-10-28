"""Invented-artifact tests only; no target table is read or evaluated."""
import json
import pathlib
from evaluate_committed_v2 import digest,verify_preparation_anchors

HERE=pathlib.Path(__file__).resolve().parent

def write(path,obj):
    path.write_text(json.dumps(obj,sort_keys=True)+"\n",encoding="utf-8")

def fixture(root):
    root.mkdir(exist_ok=False)
    visible=root/"visible"
    visible.mkdir()
    (root/"analysis_protocol.json").write_text('{"invented":true}\n',encoding="utf-8")
    (root/"evaluate_committed.py").write_text("# original invented evaluator\n",encoding="utf-8")
    (root/"evaluate_committed_v2.py").write_text("# amended invented evaluator\n",encoding="utf-8")
    (root/"design_with_hidden_outcome.csv").write_text("invented-placeholder-only\n",encoding="utf-8")
    (root/"data_provenance.json").write_text("{}\n",encoding="utf-8")
    (visible/"observed.csv").write_text("id,x\na,1\n",encoding="utf-8")
    write(root/"protocol_freeze.json",{"files":{name:digest(root/name) for name in ["analysis_protocol.json","evaluate_committed.py"]}})
    write(visible/"input_hashes.json",{"files":{"observed.csv":digest(visible/"observed.csv")}})
    write(root/"preparation_receipt.json",{
        "protocol_freeze_sha256":digest(root/"protocol_freeze.json"),
        "protocol_sha256":digest(root/"analysis_protocol.json"),
        "visible_input_hashes_sha256":digest(visible/"input_hashes.json"),
        "hidden_table_sha256":digest(root/"design_with_hidden_outcome.csv"),
        "provenance_sha256":digest(root/"data_provenance.json"),
    })
    write(root/"evaluator_guard_amendment.json",{"files":{name:digest(root/name) for name in ["preparation_receipt.json","evaluate_committed.py","evaluate_committed_v2.py"]}})
    return visible,digest(root/"evaluator_guard_amendment.json")

def run():
    destination=HERE/"guard_test_fixtures"
    destination.mkdir(exist_ok=False)
    checks=[]
    for case in ["unchanged","protocol_freeze_rewritten","protocol_rewritten","visible_manifest_rewritten","receipt_rewritten","amendment_rewritten"]:
        root=destination/case
        visible,anchor=fixture(root)
        expected_message=None
        if case=="protocol_freeze_rewritten":
            value=json.loads((root/"protocol_freeze.json").read_text())
            value["extra_self_consistent_metadata"]="changed"
            write(root/"protocol_freeze.json",value)
            expected_message="protocol_freeze_sha256"
        elif case=="protocol_rewritten":
            (root/"analysis_protocol.json").write_text('{"invented":false}\n',encoding="utf-8")
            expected_message="protocol_sha256"
        elif case=="visible_manifest_rewritten":
            (visible/"observed.csv").write_text("id,x\na,2\n",encoding="utf-8")
            write(visible/"input_hashes.json",{"files":{"observed.csv":digest(visible/"observed.csv")}})
            expected_message="visible_input_hashes_sha256"
        elif case=="receipt_rewritten":
            value=json.loads((root/"preparation_receipt.json").read_text())
            value["extra"]="changed"
            write(root/"preparation_receipt.json",value)
            expected_message="preparation_receipt.json"
        elif case=="amendment_rewritten":
            value=json.loads((root/"evaluator_guard_amendment.json").read_text())
            value["extra"]="changed"
            write(root/"evaluator_guard_amendment.json",value)
            expected_message="Custodian amendment commitment mismatch"
        try:
            verify_preparation_anchors(root,visible,anchor)
        except AssertionError as error:
            assert expected_message and expected_message in str(error),(case,str(error))
            checks.append({"case":case,"status":"correctly_rejected","reason":str(error)})
        else:
            assert expected_message is None,case
            checks.append({"case":case,"status":"accepted_unchanged"})
    # The main evaluator must call the guard before any pandas CSV read.
    source=(HERE/"evaluate_committed_v2.py").read_text(encoding="utf-8")
    main=source[source.index("def main():"):]
    assert main.index("verify_preparation_anchors(")<main.index("pd.read_csv(")
    checks.append({"case":"guard_precedes_all_table_loading","status":"passed_static_order_check"})
    return {"status":"passed","scope":"invented artifacts only; no target outcomes read","checks":checks}

if __name__=="__main__":
    result=run()
    write(HERE/"guard_validation.json",result)
    print(json.dumps(result))
