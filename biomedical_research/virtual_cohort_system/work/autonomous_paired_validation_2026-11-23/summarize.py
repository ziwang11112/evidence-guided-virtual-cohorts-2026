"""After the reveal seal, score all assigned authors on the same two paired endpoints."""
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np

import experiment
import evaluate as paired


HERE = Path(__file__).resolve().parent
SEEDS = (823031, 823039, 823043)
TOLERANCES = {"mean_difference": 0.30, "strictly_below_pct": 3.0}


def ensure(value, description):
    if not value:
        raise ValueError(description)


def expect_sealed(path, digests, root):
    key = path.resolve().relative_to(root.resolve()).as_posix()
    ensure(key in digests and experiment.sha(path) == digests[key], "File outside verified freeze: " + path.name)
    return digests[key]


def input_report(path, mapping, *, real=False):
    raw = path.read_bytes()
    frame = paired.parse_table(raw, path.name, mapping)
    paired.validate(mapping)
    ensure(paired.unit_name(mapping["unit"]) == "kg/m2" and mapping["threshold"] == -2, "Unexpected primary estimand")
    report = paired.evaluate(frame, mapping, bootstrap=real)
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    if real:
        # Apply the frozen inclusion and missing code policies in the identical
        # scorer, then apply rounding to the two BMI values before differencing.
        extras = frame.copy()
        before = {"reported":"_calculated_reported_bmi", "measured":"_calculated_measured_bmi"}
        ensure(set(before.values()).isdisjoint(extras.columns), "Sensitivity columns overlap workbook columns")
        for role, col in before.items():
            bmi, _ = paired.measurement(frame, mapping[role], mapping)
            extras[col] = np.round(bmi, 1)
        remap = {**mapping, **{key:{"column":col, "unit":mapping["unit"]} for key,col in before.items()}}
        shifted = paired.evaluate(extras, remap)
        ensure(shifted["n_complete"] == report["n_complete"], "Rounding sensitivity changed complete-pair sample")
        report["rounding_sensitivity"] = {"operation":"round each BMI to 1 decimal, ties to even, then subtract",
            **{key:shifted[key] for key in ("n_complete", "mean_difference", "strictly_below_n", "strictly_below_pct", "ties_n")}}
    return report


def receipts():
    rows = []
    total = 0.0
    counts = Counter()
    roots = [("search", HERE/"private"/"search")] + [(s, HERE/"private"/"authors"/s) for s in experiment.SLOTS]
    for who, root in roots:
        for folder in sorted((root/"episodes").glob("*/calls/*")):
            if not folder.is_dir():
                continue
            p = folder/"receipt.json"
            if not p.exists():
                entry = {"owner":who, "episode":folder.parents[1].name, "call":folder.name,
                         "status":"reservation_without_receipt", "tariff_cost_usd":None}
            else:
                r = experiment.load(p)
                for filename, field in (("request.json","request_sha256"), ("reservation.json","reservation_sha256"),
                                        ("response_raw.json","response_raw_sha256")):
                    if r.get(field):
                        ensure(experiment.sha(folder/filename) == r[field], "Model receipt digest mismatch")
                entry = {"owner":who, "episode":r["episode_id"], "call":r["call_number"], "status":r["status"],
                         "model":r.get("returned_model"), "receipt_sha256":experiment.sha(p),
                         "tariff_cost_usd":r.get("tariff_cost_usd"), "usage":r.get("usage")}
                counts[who] += 1
                if entry["tariff_cost_usd"] is not None:
                    total += entry["tariff_cost_usd"]
            rows.append(entry)
    return {"calls_with_receipts": sum(counts.values()), "receipts_by_owner": dict(counts),
            "known_tariff_cost_usd":round(total,9),"unknown_cost_records":sum(e["tariff_cost_usd"] is None for e in rows),
            "trace":rows}


def author_tables(slot, status, vmap, reference, seal):
    root = HERE/"private"/"authors"/slot
    out = {"slot":slot, "construction_status":status["status"],"tables":[],
           "within_all_primary_seeds":dict.fromkeys(TOLERANCES,False),"meets_both":False}
    manifest_path = root/"final_manifest.json"
    if not manifest_path.exists():
        out["status"] = "no_final_manifest"
        return out
    expect_sealed(manifest_path, seal, experiment.PROJECT)
    manifest = experiment.load(manifest_path)
    ensure(manifest["seeds"] == list(SEEDS) and manifest["n"]==10000, "Unregistered number of seeds or virtual rows")
    seen = set()
    for run in manifest["runs"]:
        key = run["scenario"],run["seed"]
        ensure(key not in seen and key[1] in SEEDS,"Duplicate or unexpected virtual run")
        seen.add(key)
        row = {"scenario":key[0],"seed":key[1],"run_status":run["status"]}
        out["tables"].append(row)
        if run["status"] != "success":
            row["score_status"] = "generation_failed"
            continue
        path = Path(run["table"]).resolve()
        ensure(path.name=="generated.csv" and path.is_relative_to(root/"execution_final"),"Unbound generated table")
        ensure(expect_sealed(path, seal, experiment.PROJECT) == run["sha256"], "Row digest differs from manifest")
        if not vmap:
            row["score_status"] = "unavailable_frozen_mapping"
            continue
        try:
            values = input_report(path, vmap)
        except (ValueError,KeyError,TypeError,OverflowError) as error:
            # Pandas errors can quote the offending cell; retain only the exception
            # class in the export. Local raw inputs remain available for diagnosis.
            row.update(score_status="unscorable", exception=type(error).__name__)
            continue
        row["science"] = values
        if (values["n_source"] != manifest["n"] or values["n_input"] != manifest["n"]
                or values["n_complete"] != manifest["n"] or values["n_complete"] != run["n"]):
            row["score_status"] = "incomplete_virtual_sample"
            continue
        row["score_status"] = "scored"
        if reference:
            row["signed_error"] = {k:values[k]-reference[k] for k in TOLERANCES}
            row["within_tolerance"] = {k:abs(row["signed_error"][k]) <= v + 1e-12 for k,v in TOLERANCES.items()}
    primary = [item for item in out["tables"] if item["scenario"]=="primary" and item.get("score_status")=="scored"]
    if {r["seed"] for r in primary} != set(SEEDS):
        out["status"] = "missing_or_ineligible_primary_seed"
        return out
    out["status"] = "three_primary_seeds_scored"
    if reference:
        out["within_all_primary_seeds"] = {k:all(row["within_tolerance"][k] for row in primary) for k in TOLERANCES}
        out["meets_both"] = all(out["within_all_primary_seeds"].values())
    out["primary_seed_median"] = {k:float(np.median([r["science"][k] for r in primary])) for k in TOLERANCES}
    return out


def make_report():
    for stage in ("PRESEARCH","PREBUILD","PREREVEAL"):
        experiment.verify(stage)
    seal = experiment.load(HERE/"PREREVEAL.json")["sha256"]
    pref = experiment.load(HERE/"PREBUILD.json")["sha256"]
    mapsfile = HERE/"MEASUREMENT_MAPS.json"
    accessfile = HERE/"REFERENCE_ACCESS.json"
    expect_sealed(mapsfile, seal, experiment.PROJECT)
    expect_sealed(accessfile, pref, experiment.PROJECT)
    maps = experiment.load(mapsfile)
    name = experiment.load(accessfile)["local_file"]
    reference_path = (HERE/"private"/"reference"/name).resolve()
    ensure(reference_path.is_relative_to(HERE/"private"/"reference"),"Unexpected reference path")
    expect_sealed(reference_path, pref, experiment.PROJECT)
    declared = experiment.load(HERE/"CONSTRUCTORS.json")
    ensure([r["slot"] for r in declared] == experiment.SLOTS, "The assignment register must retain all six slots")
    ensure(isinstance(maps["authors"],dict) and not set(maps["authors"])-set(experiment.SLOTS), "Unknown mapped slot")
    output = {"experiment":"autonomous study choice, six frozen constructors, paired BMI analyses",
              "scorer_sha256":experiment.sha(Path(__file__)), "prereveal_sha256":experiment.sha(HERE/"PREREVEAL.json"),
              "source_evaluable":maps.get("source_evaluable"),"threshold_blinded":maps.get("threshold_blinded"),
              "threshold":-2, "tolerances":TOLERANCES, "primary_scenario":"primary", "assigned":6,
              "costs":receipts(), "reference_input_sha256":experiment.sha(reference_path)}
    try:
        reference = input_report(reference_path, maps["reference"], real=True)
    except (ValueError,KeyError,TypeError,OverflowError) as err:
        output.update(reference_status="unscorable", reference_exception=type(err).__name__,
                      conclusion="No measured endpoint comparison; reconstruction or quality issue requires a recorded explanation")
        reference = None
    else:
        output.update(reference_status="scored", measured=reference)
    slots = [author_tables(row["slot"],row,maps["authors"].get(row["slot"]),reference,seal) for row in declared]
    output["authors"] = slots
    if reference is None:
        for slot in slots:
            slot.update(within_all_primary_seeds=None, meets_both=None)
        output.update(constructors_meeting_tolerance=None, constructors_meeting_both=None,
                      registered_single_case_success=None)
        return output
    output["constructors_meeting_tolerance"] = {k:sum(s["within_all_primary_seeds"][k] for s in slots) for k in TOLERANCES}
    both = sum(s["meets_both"] for s in slots)
    ens = [s["primary_seed_median"] for s in slots if s.get("primary_seed_median")]
    output["constructors_meeting_both"] = both
    output["between_constructor_primary_seed_medians"] = {k:{
        "constructors":len(ens),
        "range":[min(s[k] for s in ens),max(s[k] for s in ens)] if ens else None,
        "median":float(np.median([s[k] for s in ens])) if ens else None} for k in TOLERANCES}
    eligible = output["source_evaluable"] is True and output["threshold_blinded"] is True
    output["registered_single_case_success"] = both>=4 if eligible else None
    output["comparison_scope"] = "same-study withheld reference" if eligible else "blinding or source validity unverified or failed"
    return output


if __name__ == "__main__":
    report = make_report()
    paired.immutable_json(HERE/"AGGREGATES.json",report)
    print(json.dumps({k:report.get(k) for k in ("reference_status","assigned","constructors_meeting_both","registered_single_case_success")}))
