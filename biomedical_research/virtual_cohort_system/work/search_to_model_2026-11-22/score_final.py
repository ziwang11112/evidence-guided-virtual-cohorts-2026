"""Read the frozen sampler's raw OCT/ultrasound columns and recompute both analyses."""
import argparse
import json
from pathlib import Path
import pandas as pd
from science import evaluate
from verify_model import audit
from run import persist, transport


def measurement_scale(spec, name):
    cols = [c for c in spec["columns"] if c["name"] == name]
    if len(cols) != 1:
        raise ValueError("Expected a unique declared measurement")
    unit = cols[0]["unit"].strip().casefold().replace("μ","u").replace("µ","u")
    if unit in {"um","micron","microns","micrometer","micrometers","micrometre","micrometres"}:
        return 1.
    if unit in {"mm","millimeters","millimetres","millimeter","millimetre"}:
        return 1000.
    raise ValueError("Unrecognized measurement unit")


def score(root, request_path, oct_col, us_col):
    bindings = audit(root,request_path)
    path = root/"model"
    review = transport.read(path/"review.json")
    candidate = review["candidate"] if review["action"] == "revise" else transport.read(path/"build.json")
    scales = {c:measurement_scale(candidate["model_spec"],c) for c in (oct_col,us_col)}
    runs = []
    for row in transport.read(path/"final_manifest.json")["runs"]:
        brief = {k:row[k] for k in ("scenario","seed","status")}
        runs.append(brief)
        if row["status"] != "success":
            continue
        table = Path(row["table"])
        if transport.sha(table) != row["sha256"]:
            raise ValueError("Final table changed")
        frame = pd.read_csv(table,usecols=[oct_col,us_col],float_precision="round_trip")
        for col,scale in scales.items():
            frame[col] *= scale
        brief["science"] = evaluate(frame,oct_col,us_col)
        if brief["science"]["n_input"] != row["n"]:
            raise ValueError("Analyzed rows differ from manifest")
    return {"sources":bindings["selected_source_ids_in_bundle"],"oct_col":oct_col,"us_col":us_col,
            "scales_to_um":scales,"runs":runs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root",type=Path)
    parser.add_argument("request",type=Path)
    parser.add_argument("oct_col")
    parser.add_argument("us_col")
    parser.add_argument("output",type=Path)
    args = parser.parse_args()
    persist(args.output,score(args.root.resolve(), args.request,args.oct_col,args.us_col))
