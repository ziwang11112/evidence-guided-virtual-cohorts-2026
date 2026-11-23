"""Evaluator-only comparison of frozen virtual-eye tables using the selected source study."""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "search_to_model_2026-11-22"))
from science import evaluate
sys.path.insert(0, str(HERE.parent / "article_autonomy_design_2026-11-22"))
from evidence_replay.core import digest


# The evaluator read the original aggregate images independently in the earlier
# study. Never include these values, article-specific roles or grading outputs
# in prompts for querying, reading the table, or model authorship.
REFERENCES = {
    "Visante": {"oct_mean_um":520.5, "oct_sd_um":27.7, "us_mean_um":524.2,
                "us_sd_um":27.4, "mean_difference_um":-3.6},
    "RTVue": {"oct_mean_um":524.7, "oct_sd_um":27.8, "us_mean_um":524.2,
              "us_sd_um":27.4, "mean_difference_um":0.5},
}


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def scale_to_um(spec, column):
    declarations = [c for c in spec["columns"] if c["name"] == column]
    if len(declarations) != 1:
        raise ValueError("Expected one declared raw measurement column: " + column)
    unit = declarations[0]["unit"].strip().casefold().replace("μ","u").replace("µ","u")
    if unit in ("um","micron","microns","micrometer","micrometers","micrometre","micrometres"):
        return 1.
    if unit in ("mm","millimeter","millimeters","millimetre","millimetres"):
        return 1000.
    raise ValueError("Unsupported thickness unit: " + unit)


def errors(stats, ref):
    return {key: (stats[key] - value if stats[key] is not None else None)
            for key,value in ref.items()}


def analyze_run(model_root, oct_col, us_col, *, instrument="Visante"):
    root = Path(model_root).resolve()
    manifest = read(root/"final_manifest.json")
    review = read(root/"review.json")
    if manifest["action"] != review["action"] or manifest["review_sha256"] != digest(review):
        raise ValueError("Review differs from the frozen manifest")
    result = {"instrument":instrument, "doi":"10.3349/ymj.2012.53.3.634",
              "reference":REFERENCES[instrument], "registered_seeds":manifest["seeds"],
              "selected_review_action":review["action"], "runs":[]}
    if review["action"] == "abstain":
        if manifest["runs"]:
            raise ValueError("An abstention should have no delivered rows")
        return result
    if review["action"] not in ("revise","keep"):
        raise ValueError("Unknown final review action")
    chosen = review["candidate"] if review["action"] == "revise" else read(root/"build.json")
    if manifest["candidate_sha256"] != digest(chosen):
        raise ValueError("Selected candidate differs from the frozen manifest")
    spec = chosen["model_spec"]
    scales = {col:scale_to_um(spec,col) for col in (oct_col,us_col)}
    if len(scales) != 2:
        raise ValueError("The two raw measurement fields must differ")
    result.update(columns={"oct":oct_col,"us":us_col}, scales_to_um=scales,
                  candidate_sha256=manifest["candidate_sha256"],
                  generator_sha256=sha256(chosen["generator_py"].encode("utf8")).hexdigest(),
                  declared_parameter_provenance=chosen["decision_record"].get("parameter_provenance",[]))
    evidence = read(root/"source_inventory.json")["evidence_checks"]
    result["source_entries"] = [
        {k:item[k] for k in ("id","source","reference","provenance","applicability") if k in item}
        for item in evidence]
    scenarios = ["primary", *spec.get("alternatives",[])]
    expected = set(product(scenarios,manifest["seeds"]))
    seen = set()
    for row in manifest["runs"]:
        pair = (row["scenario"],row["seed"])
        if pair in seen or pair not in expected:
            raise ValueError("Unexpected scenario or repeated seed")
        seen.add(pair)
        entry = {k:row[k] for k in ("scenario","seed","status")}
        result["runs"].append(entry)
        if row["status"] != "success":
            continue
        table = Path(row["table"]).resolve()
        if not table.is_relative_to(root/"execution_final") or table.name != "generated.csv":
            raise ValueError("Final table outside the declared execution directory")
        actual_sha = sha256(table.read_bytes()).hexdigest()
        if actual_sha != row["sha256"]:
            raise ValueError("Generated table differs from its receipt")
        frame = pd.read_csv(table, usecols=["row_id",oct_col,us_col], float_precision="round_trip")
        if len(frame) != row["n"] or len(frame) != manifest["n"] or not frame["row_id"].is_unique or frame["row_id"].isna().any():
            raise ValueError("Generated row count or unique identifiers conflict with manifest")
        for col, scale in scales.items():
            frame[col] = frame[col] * scale
        stats = evaluate(frame,oct_col,us_col)
        entry.update(table_sha256=actual_sha, science=stats, signed_error_um=errors(stats,REFERENCES[instrument]))
    result["missing_scenario_seeds"] = [list(x) for x in sorted(expected-seen)]
    if manifest["status"] == "success" and (result["missing_scenario_seeds"] or
                                            any(r["status"]!="success" for r in result["runs"])):
        raise ValueError("Successful manifest lacks a successful result for every registered seed")
    return result


def compare(oldroot,newroot,old_pair,new_pair,*,old_instrument="Visante",new_instrument="Visante"):
    before = analyze_run(oldroot,*old_pair,instrument=old_instrument)
    after = analyze_run(newroot,*new_pair,instrument=new_instrument)
    output = {"old":before, "new":after, "same_instrument":old_instrument==new_instrument,
              "matched_scenario_seeds":[], "old_only_scenario_seeds":[], "new_only_scenario_seeds":[],
              "measured_abs_gt20_reference_pct":None,
              "interpretation":"Signed errors compare reanalyzed virtual rows with the printed means, SDs and paired contrast in Tables 1 and 3. These values use rounded source cells. Printed agreement limits correct for measurement error and provide no empirical strict exceedance count. Scenario and seed differences are descriptive within this rerun."}
    old = {(r["scenario"],r["seed"]):r for r in before["runs"]}
    new = {(r["scenario"],r["seed"]):r for r in after["runs"]}
    output["old_only_scenario_seeds"] = [list(x) for x in sorted(old.keys()-new.keys())]
    output["new_only_scenario_seeds"] = [list(x) for x in sorted(new.keys()-old.keys())]
    if old_instrument != new_instrument:
        return output
    for key in sorted(old.keys() & new.keys()):
        a,b = old[key],new[key]
        pair = {"scenario":key[0], "seed":key[1], "old_status":a["status"],"new_status":b["status"]}
        if a["status"] == b["status"] == "success":
            ar,br = a["signed_error_um"],b["signed_error_um"]
            pair["absolute_error_reduction_um"] = {
                k:(abs(ar[k])-abs(br[k]) if ar[k] is not None and br[k] is not None else None) for k in ar}
            old_pct,new_pct=a["science"]["abs_gt20_pct"],b["science"]["abs_gt20_pct"]
            pair["threshold_change_pp"] = (new_pct-old_pct if old_pct is not None and new_pct is not None else None)
        output["matched_scenario_seeds"].append(pair)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old",type=Path)
    parser.add_argument("new",type=Path)
    parser.add_argument("--old-pair",nargs=2,required=True,metavar=("OCT","US"))
    parser.add_argument("--new-pair",nargs=2,required=True,metavar=("OCT","US"))
    parser.add_argument("--old-instrument",choices=REFERENCES,default="Visante")
    parser.add_argument("--new-instrument",choices=REFERENCES,default="Visante")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    report = compare(args.old,args.new,args.old_pair,args.new_pair,
                     old_instrument=args.old_instrument,new_instrument=args.new_instrument)
    value=json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    if args.out.exists():
        if args.out.read_text(encoding="utf8") != value:
            raise ValueError("Previous comparison differs")
    else:
        with args.out.open("x",encoding="utf8") as f:
            f.write(value)
