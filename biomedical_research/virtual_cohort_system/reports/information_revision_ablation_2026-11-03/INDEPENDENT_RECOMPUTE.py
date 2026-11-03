"""Bounded independent audit; no generation and no original patient reads.

Refuses to read report, generated rows, or reference summaries before all six
session ledgers have final feedback/handback/decision records. Statistical
calculations do not call analysis_feedback or the common evaluator.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
import numpy as np
from scipy import linalg, stats

U = Path(__file__).resolve().parent
ROOT = U.parents[3] / "evcIA"
KEYS = ("L01", "R01", "R02", "L02", "L03", "R03")
VARIABLES = ("age", "female", "bmi", "glucose", "hba1c")


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def quantile(values, probability):
    xs = sorted(values)
    index = (len(xs)-1)*probability
    lo = math.floor(index)
    return xs[lo] + (index-lo)*(xs[min(lo+1, len(xs)-1)]-xs[lo])


def recompute(p, definitions):
    with p.open(encoding="utf-8-sig", newline="") as stream:
        raw = list(csv.DictReader(stream))
    columns = {v: [float(row[v]) for row in raw] for v in VARIABLES}
    assert all(math.isfinite(x) for xs in columns.values() for x in xs)
    values = {}
    for v, xs in columns.items():
        for key, value in (("mean", statistics.mean(xs)), ("sd", statistics.stdev(xs)),
                           ("q10", quantile(xs, .1)), ("median", statistics.median(xs)), ("q90", quantile(xs, .9))):
            values[v+"_"+key] = value
    for method, func in (("pearson", stats.pearsonr), ("spearman", stats.spearmanr)):
        value = float(func(columns["glucose"], columns["hba1c"]).statistic)
        values["glucose_hba1c_"+method] = value if math.isfinite(value) else None
    nonpositive = {v: sum(x <= 0 for x in columns[v]) for v in ("glucose", "hba1c")}
    ranks = {}
    for d in definitions["analyses"]:
        # Centered QR-pivoted least squares, not the provider's uncentered numpy SVD.
        x = np.array([columns[v] for v in d["predictors"]], dtype=float).T
        y = np.array(columns[d["outcome"]], dtype=float)
        slopes, _, rank, _ = linalg.lstsq(x-x.mean(axis=0), y-y.mean(), lapack_driver="gelsy")
        ranks[d["id"]] = int(rank)+1
        values[d["id"]] = (float(slopes[d["predictors"].index(d["term"])])
                           if rank == len(d["predictors"]) and not any(nonpositive.values()) else None)
    measurements = [tuple(float(r[v]) for v in VARIABLES) for r in raw]
    quality = {"nonpositive_glycemia": nonpositive, "duplicate_measurement_rows": len(measurements)-len(set(measurements))}
    support = {"nonunique_identifiers": len(raw)-len({r["row_id"] for r in raw}),
               "age_outside_support": sum(x < 35 or x > 74 or int(x) != x for x in columns["age"]),
               "nonbinary_female": sum(x not in (0, 1) for x in columns["female"]),
               "nonpositive_bmi": sum(x <= 0 for x in columns["bmi"])}
    return values, quality, support, ranks, len(raw)


def reference_values(reference):
    vals = {key: item["coefficient"] for key, item in reference["estimands"].items()}
    for variable, record in reference["diagnostics"]["marginal"].items():
        vals.update({variable+"_"+stat: value for stat, value in record.items()})
    vals.update({"glucose_hba1c_"+stat: value for stat, value in reference["diagnostics"]["joint"].items()})
    return vals


def main():
    events = {key: [load(p) for p in sorted((ROOT/key/"session/events").glob("*.json"))] for key in KEYS}
    # Metadata-only closure checks must precede any target or generated values.
    for key, es in events.items():
        for kind in ("feedback", "handback"):
            assert sum(e["kind"] == kind and e.get("stage") == "final" for e in es) == 1, (key, kind, "not closed")
        assert sum(e["kind"] == "decision" for e in es) == 1, (key, "decision not closed")
    report = load(U/"COMPLETE_RESULTS.json")
    reference = load(ROOT/"R01/b/input/reference_summary.json")
    refs = reference_values(reference)
    mismatches = []
    comparisons = 0
    max_error = 0.0

    def check(actual, expected, label):
        nonlocal comparisons, max_error
        comparisons += 1
        if actual is None or expected is None:
            ok = actual is None and expected is None
        elif isinstance(actual, (float, int)) and not isinstance(actual, bool) and isinstance(expected, (float, int)):
            err = abs(actual-expected); max_error = max(max_error, err)
            ok = math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-8)
        else:
            ok = actual == expected
        if not ok:
            mismatches.append({"label": label, "reported": actual, "independent": expected})

    recomputed = {}; ledgers = []; all_attempts = []
    for key, es in events.items():
        root = ROOT/key; contract = load(root/"session/contract.json")
        previous = sha(root/"session/contract.json")
        for index, event in enumerate(es, 1):
            check(event["index"], index, key+":event-index")
            check(event["previous_sha256"], previous, key+":event-chain")
            previous = sha(root/"session/events"/f"{index:04d}.json")
        for path, binding in contract["bindings"].items():
            check(sha(path), binding["sha256"], key+":bound-source:"+Path(path).name)
            check(sha(root/binding["snapshot"]), binding["sha256"], key+":snapshot:"+Path(path).name)
        attempts = [e for e in es if e["kind"] == "attempt"]
        dispatches = [e for e in es if e["kind"] == "author_dispatch"]
        check(len(dispatches), 2, key+":author-phases")
        check({e["author_id"] for e in dispatches}, {contract["author_id"]}, key+":author-identity")
        for stage in ("initial", "final"):
            seeds = sorted(e["seed"] for e in attempts if e["purpose"] == "delivery" and e["stage"] == stage)
            check(seeds, [4101, 4102, 4103], key+":"+stage+":seeds")
        for phase, allowed in (("initial", {4201, 4202}), ("revision", {4301, 4302})):
            trials = [e for e in attempts if e["purpose"] == "trial" and e["phase"] == phase]
            check(len(trials) <= 2 and len({t["seed"] for t in trials}) == len(trials) and all(t["seed"] in allowed for t in trials), True, key+":"+phase+":trial-budget")
        check(len(attempts) <= 10, True, key+":attempt-budget")
        retrievals = [e for e in es if e["kind"] == "retrieval"]
        counts = Counter(e["retrieval_kind"] for e in retrievals)
        check(counts["query"] <= 2 and counts["document"] <= 1, True, key+":retrieval-budget")
        ledgers.append({"constructor": key, "author_id": contract["author_id"], "dispatches": dispatches,
                        "attempts": len(attempts), "trials": sum(e["purpose"] == "trial" for e in attempts),
                        "retrievals": retrievals, "numeric_semantic_evidence_ids": contract["numeric_semantic_evidence_ids"]})
        definitions = load(root/"b/input/analysis_definitions.json")
        for attempt in attempts:
            all_attempts.append((key, attempt))
            matching = [r for r in report["runs"] if r["constructor"] == key and r["run_id"] == attempt["run_id"]]
            check(len(matching), 1, key+":report-run-coverage")
            row = matching[0]
            results = [e for e in es if e["kind"] == "result" and e["attempt_index"] == attempt["index"]]
            status = results[-1]["status"] if results else "interrupted_or_unresolved"
            check(row["status"], status, key+":run-status")
            if status != "success":
                for group in ("analyses", "diagnostics"):
                    check(all(x["value"] is None and x["status"] == "unavailable" for x in row["statistics"][group]), True, key+":failure-retention")
                continue
            output = root/"b/executions"/attempt["run_id"]/"output/generated.csv"
            vals, quality, support, ranks, n = recompute(output, definitions)
            check(n, 3000, key+":rows")
            check(row["output_sha256"], sha(output), key+":output-hash")
            check(row["statistics"]["quality"], quality, key+":quality")
            check(all(x == 0 for x in support.values()), True, key+":support")
            check(len(vals), 30, key+":thirty-statistics")
            for group in ("analyses", "diagnostics"):
                for item in row["statistics"][group]:
                    ident = item["id"]; label = f"{key}:{attempt['run_id']}:{ident}"
                    check(item["value"], vals[ident], label+":value")
                    check(item["reference"], refs[ident], label+":reference")
                    check(item["difference"], vals[ident]-refs[ident] if vals[ident] is not None else None, label+":difference")
                    if group == "analyses":
                        check(item["rank"], ranks[ident], label+":rank")
                        check(item["reference_interval"], reference["estimands"][ident]["interval"], label+":interval")
            recomputed[(key, attempt["run_id"])] = {"values": vals, "quality": quality, "support": support,
                                                      "n": n, "sha256": sha(output), "attempt": attempt}
    summaries = {}
    for key in KEYS:
        for stage in ("initial", "final"):
            runs = [r for (k, _), r in recomputed.items() if k == key and r["attempt"]["stage"] == stage and r["attempt"]["purpose"] == "delivery"]
            for ident in refs:
                seed_vals = {str(seed): next((r["values"][ident] for r in runs if r["attempt"]["seed"] == seed), None) for seed in (4101, 4102, 4103)}
                xs = [v for v in seed_vals.values() if v is not None]
                expected = {"seed_values": seed_vals, "n_successful_seeds": len(xs), "mean": statistics.mean(xs) if xs else None,
                            "range": [min(xs), max(xs)] if xs else None,
                            "mean_absolute_difference": statistics.mean(abs(v-refs[ident]) for v in xs) if xs else None}
                row = next(c for c in report["constructor_stage_statistics"] if c["constructor"] == key and c["stage"] == stage and c["id"] == ident)
                for field, value in expected.items():
                    if field == "seed_values":
                        for seed, v in value.items(): check(row[field][seed], v, f"{key}:{stage}:{ident}:{seed}")
                    elif field == "range" and value is not None:
                        for i, v in enumerate(value): check(row[field][i], v, f"{key}:{stage}:{ident}:range{i}")
                    else: check(row[field], value, f"{key}:{stage}:{ident}:{field}")
                summaries[(key, stage, ident)] = expected
        for ident in refs:
            initial, final = [summaries[(key, stage, ident)] for stage in ("initial", "final")]
            row = next(c for c in report["paired_revision_changes"] if c["constructor"] == key and c["id"] == ident)
            matches = [s for s, v in initial["seed_values"].items() if v is not None and final["seed_values"][s] is not None]
            check(row["matched_seed_ids"], matches, key+":"+ident+":matched-seeds")
            check(row["matched_seed_count"], len(matches), key+":"+ident+":matched-count")
            for s in matches:
                delta = abs(final["seed_values"][s]-refs[ident])-abs(initial["seed_values"][s]-refs[ident])
                check(row["matched_seed_changes"][s], delta, key+":"+ident+":"+s+":paired-change")
            a, b = initial["mean_absolute_difference"], final["mean_absolute_difference"]
            check(row["change"], b-a if a is not None and b is not None else None, key+":"+ident+":mean-change")
    count_expected = {"attempts": len(all_attempts), "delivery_attempts": sum(a["purpose"] == "delivery" for _, a in all_attempts),
                      "trial_attempts": sum(a["purpose"] == "trial" for _, a in all_attempts), "successful_tables": len(recomputed),
                      "failed_attempts": len(all_attempts)-len(recomputed), "distinct_table_hashes": len({r["sha256"] for r in recomputed.values()})}
    for field, value in count_expected.items(): check(report[field], value, field)
    check(len({r["author_id"] for r in ledgers}), 6, "distinct-author-contexts")
    decisions = []
    for key in KEYS:
        es = events[key]
        selected = {stage: next(e for e in es if e["kind"] == "freeze" and e["stage"] == stage)["candidate"] for stage in ("initial", "final")}
        hashes = {stage: {name: sha(ROOT/key/"b"/candidate/name) for name in ("generator.py", "model_spec.json")} for stage, candidate in selected.items()}
        paired_output_identity = {str(seed): next((r["sha256"] for (k, _), r in recomputed.items() if k == key and r["attempt"]["stage"] == "initial" and r["attempt"]["seed"] == seed), None) == next((r["sha256"] for (k, _), r in recomputed.items() if k == key and r["attempt"]["stage"] == "final" and r["attempt"]["seed"] == seed), None) for seed in (4101,4102,4103)}
        decision = next(e for e in es if e["kind"] == "decision")["decision"]
        decisions.append({"constructor": key, "decision": decision, "candidates": selected, "science_hashes": hashes,
                          "generator_bytes_identical": hashes["initial"]["generator.py"] == hashes["final"]["generator.py"],
                          "spec_bytes_identical": hashes["initial"]["model_spec.json"] == hashes["final"]["model_spec.json"],
                          "paired_output_hashes_identical": paired_output_identity})
    outcome = {"kind": "independent_actual_output_recomputation", "created_utc": datetime.now(timezone.utc).isoformat(),
               "status": "pass" if not mismatches else "mismatch", "raw_patient_reads": 0, "new_scientific_tables": 0,
               "method": "stdlib CSV/mean/sample-SD/linear-quantile; scipy Pearson/Spearman; centered scipy QR-pivoted OLS; no provider calls",
               "report_sha256": sha(U/"COMPLETE_RESULTS.json"), "reference_sha256": sha(ROOT/"R01/b/input/reference_summary.json"),
               "script_sha256": sha(Path(__file__)), "comparisons": comparisons, "max_absolute_numeric_difference": max_error,
               "statistic_values_recomputed": len(recomputed)*30, "counts": count_expected, "mismatches": mismatches,
               "session_audit": ledgers, "decisions_and_identity": decisions,
               "scope_limits": ["Reference is an exposed development sample, not known population truth", "Ledger context declarations are not adversarial filesystem isolation", "Actual local-row and raw-file nonaccess claims require retained tool logs; ledgers alone are insufficient"]}
    with (U/"INDEPENDENT_RECOMPUTE.json").open("x", encoding="utf-8") as f:
        json.dump(outcome, f, indent=2, ensure_ascii=False, allow_nan=False); f.write("\n")
    print(json.dumps({k: outcome[k] for k in ("status", "comparisons", "max_absolute_numeric_difference", "statistic_values_recomputed", "counts")}))
    if mismatches: raise SystemExit(1)


if __name__ == "__main__":
    main()
