"""One authorized independent audit; importing this file reads no study data.

Preparation may compile this file, but run requires --execute, a freeze, and the
completed production REPORT. Production calibration.py is never imported.
Only the previously frozen, selection-only decoder is reused. All statistical
calculations, random splits, hashes and report comparisons are independent.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy import linalg, stats

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
COLS = ("age", "female", "bmi", "glucose", "hba1c")
CONT = ("age", "bmi", "glucose", "hba1c")
REG = {"A": ("bmi", "age", "female"), "B": ("bmi", "glucose", "age", "female")}
PAIRS = (("bmi", "hba1c"), ("glucose", "hba1c"), ("bmi", "glucose"))
STATS = ("mean", "sd_ddof1", "q10", "median", "q90")
METRICS = tuple([f"model_{a}.{t}" for a, p in REG.items() for t in ("intercept", *p)]
                + [f"{v}.{s}" for v in CONT for s in STATS] + ["female.proportion"]
                + [f"{x}_{y}.{s}" for x, y in PAIRS for s in ("pearson", "spearman")])
SEEDS = list(range(8400, 8500))
RTOL, ATOL = 1e-9, 2e-11
ANCHORS = {
    "selection_definition": "52333d983959caf54c136540c4b31109c634358f078b7360ffa76ca070408d6a",
    "selection_plan": "a2c5f43969c700474a9466416be8503dc0c92b1c78b12a07a6edc6bc88f247b7",
    "selection_engine": "e40f403b13125f5b41f620126a807122bb99796558adda576518fcf50796365a",
    "historical_reference": "f5565a6fb54072462f278b2a6b6f0d7ff343d91bd6e166048e8da65bab1f1c10",
    "historical_generation_report": "2dfe84dca528adcc4edc6035b1f70ffbf13df72697ef82ac273344660824e2c6",
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    payload = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)


class Comparator:
    def __init__(self):
        self.numeric_leaves = 0
        self.exact_leaves = 0
        self.maximum_absolute_difference = 0.0
        self.maximum_difference_path = None

    def check(self, actual, expected, path):
        if isinstance(expected, dict):
            need(isinstance(actual, dict) and set(actual) == set(expected), f"Object fields differ: {path}")
            for k, value in expected.items():
                self.check(actual[k], value, f"{path}.{k}")
        elif isinstance(expected, (list, tuple)):
            need(isinstance(actual, list) and len(actual) == len(expected), f"Array size differs: {path}")
            for i, value in enumerate(expected):
                self.check(actual[i], value, f"{path}[{i}]")
        elif expected is None or isinstance(expected, (str, bool)):
            need(type(actual) is type(expected) and actual == expected, f"Exact value differs: {path}")
            self.exact_leaves += 1
        elif isinstance(expected, (int, np.integer)):
            need(type(actual) is int and actual == int(expected), f"Integer differs: {path}")
            self.numeric_leaves += 1
        else:
            need(isinstance(actual, (int, float)) and not isinstance(actual, bool), f"Numeric type differs: {path}")
            need(np.isfinite([actual, expected]).all(), f"Nonfinite value: {path}")
            difference = abs(float(actual) - float(expected))
            need(difference <= ATOL + RTOL * abs(float(expected)), f"Numeric discrepancy: {path}")
            self.numeric_leaves += 1
            if difference > self.maximum_absolute_difference:
                self.maximum_absolute_difference = difference
                self.maximum_difference_path = path

    def result(self):
        return dict(self.__dict__)


def linear_quantiles(values):
    ordered = sorted(float(x) for x in values)
    if not ordered:
        return [None, None, None]
    output = []
    for probability in (.1, .5, .9):
        position = (len(ordered) - 1) * probability
        lower, upper = math.floor(position), math.ceil(position)
        weight = position - lower
        output.append(ordered[lower] + weight * (ordered[upper] - ordered[lower]))
    return output


def valid_frame(frame, n=None):
    need(frame.columns.is_unique and set(COLS) <= set(frame), "Missing/ambiguous analysis fields")
    if n is not None:
        need(len(frame) == n, "Unexpected analysis row count")
    for name in COLS:
        need(pd.api.types.is_numeric_dtype(frame[name]) and not pd.api.types.is_bool_dtype(frame[name]),
             "Nonnumeric field")
    need(np.isfinite(frame[list(COLS)].to_numpy(float)).all(), "Incomplete or nonfinite values")
    need(frame.age.between(35, 74).all() and frame.female.isin([0, 1]).all(), "Invalid age/sex")
    need((frame[["bmi", "glucose", "hba1c"]] > 0).all().all(), "Nonpositive measurements")


def independent_metrics(frame):
    valid_frame(frame)
    output, unavailable = {}, {}
    y = frame.hba1c.to_numpy(float)
    for label, terms in REG.items():
        design = np.column_stack([np.ones(len(frame)), frame[list(terms)].to_numpy(float)])
        # Householder QR and triangular solve do not call production's lstsq.
        q, r = linalg.qr(design, mode="economic", check_finite=True)
        full_rank = np.linalg.matrix_rank(design) == design.shape[1]
        coefficients = linalg.solve_triangular(r, q.T @ y) if full_rank else [None] * design.shape[1]
        for term, value in zip(("intercept", *terms), coefficients):
            key = f"model_{label}.{term}"
            output[key] = None if value is None else float(value)
            if value is None:
                unavailable[key] = "rank_deficient_design"
    for variable in CONT:
        values = frame[variable].to_numpy(float)
        mean = math.fsum(values) / len(values)
        sd = math.sqrt(math.fsum((float(v) - mean) ** 2 for v in values) / (len(values) - 1))
        output.update(zip((f"{variable}.{key}" for key in STATS), [mean, sd, *linear_quantiles(values)]))
    output["female.proportion"] = math.fsum(frame.female.to_numpy(float)) / len(frame)
    for x, z in PAIRS:
        a, b = frame[x].to_numpy(float), frame[z].to_numpy(float)
        for label, fn in (("pearson", stats.pearsonr), ("spearman", stats.spearmanr)):
            key = f"{x}_{z}.{label}"
            if np.ptp(a) == 0 or np.ptp(b) == 0:
                output[key] = None
                unavailable[key] = "zero_variance_or_nonfinite_correlation"
            else:
                output[key] = float(fn(a, b).statistic)
    need(tuple(output) == METRICS and len(output) == 36, "Independent metric inventory")
    return output, unavailable


def position_hash(values, category):
    header = {"rows": b"real_real:rows:v1\x00", "communities": b"real_real:communities:v1\x00"}[category]
    encoded = b"".join(int(value).to_bytes(8, "little", signed=False) for value in sorted(values))
    return hashlib.sha256(header + encoded).hexdigest()


def independent_split(reference, seed):
    communities = sorted(reference.survey_commid.unique().tolist())
    need(len(communities) == 218, "Unexpected number of communities")
    lookup = {label: index for index, label in enumerate(communities)}
    codes = np.array([lookup[label] for label in reference.survey_commid], dtype=np.int64)
    rng = np.random.Generator(np.random.PCG64(seed))
    attempts = []
    for attempt in range(1, 1001):
        allocation = rng.permutation(218)
        left_codes = set(int(v) for v in allocation[:109])
        right_codes = set(int(v) for v in allocation[109:])
        # Reconstruct pools by row enumeration, not production factorize/isin.
        pool1 = np.array([i for i, code in enumerate(codes) if int(code) in left_codes], dtype=np.int64)
        pool2 = np.array([i for i, code in enumerate(codes) if int(code) in right_codes], dtype=np.int64)
        accepted = min(len(pool1), len(pool2)) >= 3000
        attempts.append({"attempt": attempt, "r1_pool_n": len(pool1), "r2_pool_n": len(pool2),
                         "accepted": accepted, "reason": "accepted" if accepted else "pool_size_below_sample_size"})
        if not accepted:
            continue
        r1 = np.array(sorted(rng.choice(pool1, 3000, replace=False)))
        r2 = np.array(sorted(rng.choice(pool2, 3000, replace=False)))
        need(len(set(r1)) == len(set(r2)) == 3000, "Within-side duplicated rows")
        need(not set(r1).intersection(r2) and len(set(r1).union(r2)) == 6000, "Person overlap")
        need(not set(codes[r1]).intersection(codes[r2]), "Community overlap")
        audit = {"seed": seed, "accepted_attempt": attempt, "size_rejection_n": attempt - 1, "attempts": attempts}
        for label, rows, assigned, pool in (("R1", r1, left_codes, pool1), ("R2", r2, right_codes, pool2)):
            audit[label] = {"pool_n": len(pool), "sample_n": len(rows), "assigned_community_n": len(assigned),
                "sampled_community_n": len(set(codes[rows])),
                "selected_row_positions_sha256": position_hash(rows, "rows"),
                "assigned_community_positions_sha256": position_hash(assigned, "communities")}
        audit.update(row_disjoint=True, community_disjoint=True)
        return r1, r2, audit
    raise AssertionError(f"Scheduled seed {seed} exhausted count-only attempts; no replacement")


def alternate_selection(frames):
    # Preserve original biomarker order, but change linkage order to surveys,
    # master, examination. IDs remain in memory and are never serialized.
    bio = frames["biomarker_09.sas7bdat"].rename(columns={"IDind": "id"}).copy()
    bio["source_position"] = np.arange(len(bio))
    exam = frames["pexam_00.sas7bdat"].rename(columns={"IDind": "id", "WAVE": "wave"})
    survey = frames["surveys_pub_12.sas7bdat"].rename(columns={"Idind": "id"})
    master = frames["mast_pub_12.sas7bdat"].rename(columns={"Idind": "id"})
    for table, keys in ((bio, ["id", "wave"]), (exam, ["id", "wave"]),
                        (survey, ["id", "wave"]), (master, ["id"])):
        values = table[keys].to_numpy(float)
        need(np.isfinite(values).all() and (np.abs(values) < 2**53).all()
             and (values == np.floor(values)).all() and not table.duplicated(keys).any(), "Invalid linkage key")
    linked = bio[bio.wave.eq(2009)].merge(survey[survey.wave.eq(2009)], on=["id", "wave"], validate="one_to_one")
    linked = linked.merge(master, on="id", validate="many_to_one")
    linked = linked.merge(exam[exam.wave.eq(2009)], on=["id", "wave"], validate="one_to_one")
    linked = linked.sort_values("source_position").reset_index(drop=True)
    heights = np.where(linked.CLN_HT.eq(9), np.nan, linked.HEIGHT)
    weights = np.where(linked.CLN_WT.eq(9), np.nan, linked.WEIGHT)
    allowed = np.isfinite(heights) & np.isfinite(weights) & (heights > 0) & (weights > 0)
    bmi = np.full(len(linked), np.nan)
    bmi[allowed] = weights[allowed] / np.square(heights[allowed] * .01)
    bmi[(~np.isfinite(bmi)) | (bmi <= 0)] = np.nan
    derived = pd.DataFrame({"age": linked.age, "female": linked.GENDER.map({1: 0, 2: 1}), "bmi": bmi,
        "glucose": linked.GLUCOSE, "hba1c": linked.HbA1c, "survey_commid": linked.commid})
    keep = derived.age.ge(35) & derived.age.le(74) & np.isfinite(derived[list(COLS)]).all(axis=1)
    selected_ids = linked.loc[keep, "id"]
    need(not selected_ids.duplicated().any(), "Selected person IDs are not unique")
    return derived.loc[keep].reset_index(drop=True)


def load_selected(protocol, definition):
    import pyreadstat
    frames = {}
    for item in definition["reference_files"]:
        frames[item["file"]], _ = pyreadstat.read_sas7bdat(
            str(Path(protocol["private_data_directory"]) / item["file"]), usecols=item["columns"], user_missing=False)
    spec = importlib.util.spec_from_file_location("independent_selection_only_decoder", protocol["selection_engine"]["path"])
    engine = importlib.util.module_from_spec(spec)
    original_path = sys.path.copy()
    try:
        sys.path.insert(0, str(PROJECT))
        spec.loader.exec_module(engine)
        reference, quality = engine.prepare_reference_frames(frames, read(protocol["selection_plan"]["path"]))
    finally:
        sys.path[:] = original_path
    alternate = alternate_selection(frames)
    pd.testing.assert_frame_equal(reference, alternate, check_dtype=False, rtol=1e-12, atol=1e-12)
    valid_frame(reference, 6631)
    groups = reference.survey_commid.to_numpy(float)
    need(np.isfinite(groups).all() and (groups > 0).all() and (groups == np.floor(groups)).all(), "Invalid community IDs")
    need(reference.survey_commid.nunique() == 218, "Selected community count changed")
    return reference, quality


def load_generated(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream))
    need(len(header) == len(set(header)) and set(header) == {"person_id", *COLS}, "Generated table schema changed")
    table = pd.read_csv(path, dtype={"person_id": "string"}, float_precision="round_trip")
    need(table.person_id.notna().all() and table.person_id.str.strip().ne("").all()
         and not table.person_id.duplicated().any(), "Generated identifiers missing or duplicated")
    valid_frame(table, 3000)
    return table[list(COLS)]


def difference(a, b):
    return None if a is None or b is None else a - b


def abs_or_none(value):
    return None if value is None else abs(value)


def reasons(values):
    return {key: "operand_metric_unavailable_or_nonfinite_difference" for key, value in values.items() if value is None}


def quantile_summary(values):
    available = [v for v in values if v is not None]
    return {**dict(zip(("q10", "median", "q90"), linear_quantiles(available))),
            "scheduled_n": len(values), "available_n": len(available), "unavailable_n": len(values) - len(available)}


def reconstruct_report(reference, generated):
    g = {}
    for label, frame in generated.items():
        metrics, errors = independent_metrics(frame)
        g[label] = {"n": len(frame), "metrics": metrics, "unavailable": errors}
    splits = []
    for seed in SEEDS:
        i1, i2, selection = independent_split(reference, seed)
        r1, e1 = independent_metrics(reference.iloc[i1])
        r2, e2 = independent_metrics(reference.iloc[i2])
        signed = {m: difference(r1[m], r2[m]) for m in METRICS}
        generated_differences = {}
        for label, item in g.items():
            d1 = {m: difference(item["metrics"][m], r1[m]) for m in METRICS}
            d2 = {m: difference(item["metrics"][m], r2[m]) for m in METRICS}
            symmetric = {m: None if d1[m] is None or d2[m] is None else (abs(d1[m]) + abs(d2[m])) / 2
                         for m in METRICS}
            generated_differences[label] = {"signed": d2, "absolute": {m: abs_or_none(v) for m, v in d2.items()},
                "sym_abs": symmetric, "unavailable": {"signed_and_absolute": reasons(d2), "sym_abs": reasons(symmetric)}}
        splits.append({"seed": seed, "selection": selection, "R1": r1, "R2": r2,
            "R1_unavailable": e1, "R2_unavailable": e2, "real_real_signed": signed,
            "real_real_abs": {m: abs_or_none(v) for m, v in signed.items()}, "real_real_unavailable": reasons(signed),
            "generated_vs_R2": generated_differences})
    summary = {}
    for metric in METRICS:
        summary[metric] = {"real_real": {
            kind: quantile_summary([s[key][metric] for s in splits])
            for kind, key in (("signed", "real_real_signed"), ("absolute", "real_real_abs"))},
            "generated": {label: {kind: quantile_summary([s["generated_vs_R2"][label][kind][metric] for s in splits])
                for kind in ("signed", "absolute", "sym_abs")} for label in g}}
    return g, splits, summary


def historical_check(protocol, reference, generated, comparator):
    old_ref = read(protocol["historical_reference"]["path"])
    old_gen = read(protocol["historical_generation_report"]["path"])
    reference_metrics, _ = independent_metrics(reference)
    records = []
    def one(analysis, metrics, label, model):
        count = 0
        for term, value in analysis["coefficients"].items():
            target = "intercept" if term == "const" else term
            comparator.check(value["value"], metrics[f"model_{model}.{target}"], f"historical.{label}.coefficient.{term}")
            count += 1
        for variable, values in analysis["marginal"].items():
            for stat in ("mean", "sd", "q10", "median", "q90"):
                if variable == "female" and stat != "mean":
                    continue
                metric = "female.proportion" if variable == "female" else f"{variable}.{'sd_ddof1' if stat == 'sd' else stat}"
                comparator.check(values[stat], metrics[metric], f"historical.{label}.marginal.{variable}.{stat}")
                count += 1
        for relation, values in analysis["relationships"].items():
            for method in ("pearson", "spearman"):
                comparator.check(values[method], metrics[f"{relation}.{method}"], f"historical.{label}.relationship.{relation}.{method}")
                count += 1
        records.append({"analysis": label, "point_statistics_compared": count})
    for model in REG:
        one(old_ref["reference"][model], reference_metrics, f"selected_reference_{model}", model)
        comparator.check(old_gen["reference"][model], old_ref["reference"][model], f"historical.reused_reference.{model}")
    slots = [s for s in old_gen["slots"] if s["stage"] == "initial"]
    need([s["seed"] for s in slots] == [7401, 7402, 7403], "Historical physical deliveries differ")
    for slot in slots:
        label = str(slot["seed"])
        need(slot["status"] == "success", "Historical delivery unavailable")
        one(slot["analysis"], generated[label]["metrics"], f"G{label}_B", "B")
        one(slot["analysis"]["descriptive_secondary"], generated[label]["metrics"], f"G{label}_A", "A")
    return {"status": "PASS", "comparisons": records, "unique_shared_metrics_per_frame": 34,
        "bmi_glucose_correlations": "Two new prespecified developmental diagnostics in this unit; not old holdout metrics.",
        "historical_intervals": "Kept unchanged; not recomputed or claimed as new inference."}


def aggregate_scope(report):
    forbidden = {"person_id", "IDind", "Idind", "survey_commid", "commid", "r1_positions", "r2_positions",
                 "selected_row_positions", "assigned_community_positions", "membership", "members", "rows"}
    def visit(value, path):
        if isinstance(value, dict):
            for key, entry in value.items():
                need(key not in forbidden, f"Participant-level field in report: {path}.{key}")
                visit(entry, f"{path}.{key}")
        elif isinstance(value, list):
            need(len(value) < 3000, f"Possible row-level array: {path}")
            for i, entry in enumerate(value):
                visit(entry, f"{path}[{i}]")
    visit(report, "report")
    files = [p for p in HERE.rglob("*") if p.is_file()]
    need(all(p.suffix in {".json", ".md", ".py"} for p in files), "Unexpected file type in evaluation output directory")
    need(all(p.parent == HERE for p in files), "Unexpected nested output files")
    return {"status": "PASS", "report_contains_only_aggregate_statistics_counts_and_hashes": True,
            "participant_or_generated_rows_exported": 0, "files_checked": sorted(p.name for p in files)}


def run(freeze_path):
    sys.dont_write_bytecode = True
    freeze_path = Path(freeze_path).resolve()
    need(freeze_path.parent == HERE and freeze_path.is_file(), "A local production freeze is required")
    need((HERE / "REPORT.json").exists() and (HERE / "READ_RECEIPT.json").exists(), "Production must finish before review")
    need(not (HERE / "INDEPENDENT_READ_RECEIPT.json").exists(), "One full independent audit already reserved")
    protocol, freeze, report = read(HERE / "PROTOCOL.json"), read(freeze_path), read(HERE / "REPORT.json")
    receipt = read(HERE / "READ_RECEIPT.json")
    need(freeze["protocol_sha256"] == sha(HERE / "PROTOCOL.json"), "Protocol freeze mismatch")
    need(receipt["freeze_sha256"] == sha(freeze_path), "Production freeze differs")
    need(protocol["sampling"]["seeds"] == SEEDS and protocol["sampling"]["sample_size_each"] == 3000
         and protocol["sampling"]["expected_reference_n"] == 6631 and protocol["sampling"]["expected_communities"] == 218,
         "Fixed design differs")
    inputs = {}
    def bind(label, path, expected=None):
        value = sha(path)
        need(expected is None or value == expected, f"Frozen input differs: {label}")
        inputs[label] = {"path": str(Path(path).resolve()), "sha256": value}
    for label, digest in ANCHORS.items():
        need(protocol[label]["sha256"] == digest, f"Historical anchor differs: {label}")
    for key in (*ANCHORS, "generation_closure", "generator_freeze"):
        bind(key, protocol[key]["path"], protocol[key]["sha256"])
    definition = read(protocol["selection_definition"]["path"])
    for item in definition["reference_files"]:
        bind("reference:" + item["file"], Path(protocol["private_data_directory"]) / item["file"], item["sha256"])
    need([item["seed"] for item in protocol["generated_tables"]] == [7401, 7402, 7403], "Generated seed inventory changed")
    for item in protocol["generated_tables"]:
        bind("generated:" + str(item["seed"]), item["path"], item["sha256"])
    source_inputs = inputs.copy()
    for name, digest in freeze["code_sha256"].items():
        bind("code:" + name, HERE / name, digest)
    bind("DESIGN_REVIEW.md", HERE / "DESIGN_REVIEW.md", freeze["design_review_sha256"])
    for filename in ("PROTOCOL.json", "PLAN.md", "REPORT.json", "READ_RECEIPT.json", "independent_review.py"):
        bind(filename, HERE / filename)
    bind("freeze", freeze_path)
    for label, item in source_inputs.items():
        need(receipt["input_hashes_before_decode"][label] == item, f"Production input receipt differs: {label}")
    started = datetime.now(timezone.utc).isoformat()
    write(HERE / "INDEPENDENT_READ_RECEIPT.json", {"created_utc": started, "scope": "one independent full numerical audit",
        "authorization": "Explicit coordinator execution after production freeze and completed REPORT",
        "production_report_sha256": sha(HERE / "REPORT.json"), "independent_code_sha256": sha(__file__),
        "frozen_inputs_before_decode": inputs, "clinical_or_generated_values_decoded_before_receipt": False})
    reference, quality = load_selected(protocol, definition)
    generated_frames = {str(i["seed"]): load_generated(i["path"]) for i in protocol["generated_tables"]}
    generated, splits, summary = reconstruct_report(reference, generated_frames)
    compare = Comparator()
    for name, expected in (("generated", generated), ("splits", splits), ("summary", summary)):
        compare.check(report[name], expected, name)
    expected_design = {"reference_n": 6631, "reference_community_n": 218, "sample_n_per_side": 3000,
        "communities_assigned_per_side": 109, "seeds": SEEDS, "split_n": 100,
        "rng": "numpy.random.Generator(numpy.random.PCG64(seed))", "max_partition_attempts_per_seed": 1000,
        "partition_acceptance_rule": "both community-pool row counts >= sample_n_per_side; size only",
        "sampling_order": "sorted community labels; permute; R1 choice then R2 choice; sort chosen row positions",
        "quantile_method": "linear", "sample_sd_ddof": 1, "spearman_ties": "average_ranks",
        "ols_solver": "numpy.linalg.lstsq(rcond=None); intercept; unweighted", "metric_n": 36, "metric_names": list(METRICS),
        "difference_summary_quantiles": ["q10", "median", "q90"],
        "unavailable_policy": "null with metric reason; retain split and all other metrics; no replacement",
        "summary_missing_policy": "available values per metric; always report scheduled/available/unavailable counts",
        "generated_table_n": 3, "generated_values_fixed_across_splits": True,
        "selection_hash_encoding": "domain + NUL + sorted little-endian uint64 positions",
        "selection_hash_domains": {"rows": "real_real:rows:v1", "communities": "real_real:communities:v1"}}
    compare.check(report["design"], expected_design, "design")
    need(set(report) == {"schema_version", "kind", "design", "generated", "splits", "summary", "limitations", "provenance"},
         "Unexpected production report section")
    compare.check(report["schema_version"], 1, "schema_version")
    compare.check(report["kind"], "descriptive_disjoint_community_real_real_scale_comparison", "kind")
    import pyreadstat
    expected_provenance = {"protocol_sha256": sha(HERE / "PROTOCOL.json"), "freeze_sha256": sha(freeze_path),
        "read_receipt_sha256": sha(HERE / "READ_RECEIPT.json"), "code_sha256": freeze["code_sha256"],
        "input_hashes": source_inputs, "input_hashes_unchanged_after_evaluation": True, "new_generator_executions": 0,
        "reference_quality": quality, "versions": {"python": platform.python_version(), "numpy": np.__version__,
            "pandas": pd.__version__, "pyreadstat": pyreadstat.__version__}}
    compare.check(report["provenance"], expected_provenance, "provenance")
    need(set(protocol["limitations"]) <= set(report["limitations"]), "Required interpretation limits missing")
    historical_comparator = Comparator()
    historical = historical_check(protocol, reference, generated, historical_comparator)
    historical["comparison_counts_and_precision"] = historical_comparator.result()
    scope = aggregate_scope(report)
    for label, item in inputs.items():
        need(sha(item["path"]) == item["sha256"], f"Input changed during independent audit: {label}")
    result = {"schema_version": 1, "status": "PASS", "created_utc": datetime.now(timezone.utc).isoformat(),
        "production_report_sha256": sha(HERE / "REPORT.json"), "independent_code_sha256": sha(__file__),
        "independent_read_receipt_sha256": sha(HERE / "INDEPENDENT_READ_RECEIPT.json"),
        "method": "Independent PCG64 pool enumeration and hashes; SciPy Householder QR; math.fsum means/sample SD; explicit linear quantile interpolation; SciPy Pearson/Spearman.",
        "production_statistical_functions_imported_or_called": False,
        "selection_check": "Frozen pure selection decoder plus separate survey-master-exam linkage and derivation; complete ordered frame equality.",
        "reference_n": 6631, "reference_community_n": 218, "seeds_checked": SEEDS, "split_n": 100,
        "sample_n_per_side": 3000, "distinct_selected_people_per_split": 6000, "unselected_people_per_split": 631,
        "metric_n": 36, "production_raw_statistics_checked": 36 * 203,
        "independently_summarized_frames": {"total": 204, "sampled_real_halves": 200,
            "fixed_generated_tables": 3, "previous_full_reference_for_historical_anchor": 1},
        "independent_ols_fits": 408,
        "all_selection_hashes_and_attempt_logs_checked": True, "all_summaries_checked": True,
        "all_production_numeric_fields_checked": True, "numeric_comparison": compare.result(),
        "tolerance": {"relative": RTOL, "absolute": ATOL}, "historical_consistency": historical,
        "input_hashes_unchanged_after_review": True, "frozen_input_count": len(inputs),
        "aggregate_output_scope": scope, "new_generator_executions": 0,
        "scientific_interpretation": "Numerical audit only; developmental same-cohort description, not equivalence, a pass threshold, or external clinical validation.",
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                     "scipy": scipy.__version__, "pyreadstat": pyreadstat.__version__}}
    write(HERE / "INDEPENDENT_REVIEW.json", result)
    lines = ["# Independent numerical review", "", "**PASS — complete independent audit of the new descriptive evaluation.**", "",
        "The review rebuilt all 100 scheduled seeds (8400–8499), all 36 point metrics, all signed/absolute/symmetric discrepancies and every summary quantile. It checked every production numeric field, selection hash, assignment attempt and unavailable-result field.", "",
        "Selection: 6,631 common-complete CHNS participants aged 35–74 in 218 communities. Each seed assigns 109 communities per side, accepts on eligible counts only, then samples R1 followed by R2 from the same PCG64 stream. Every split has 3,000 people per side, 6,000 distinct people, no person/community overlap and 631 unselected people.", "",
        "The selection-only frozen decoder was cross-checked against a different linkage order and independent BMI/eligibility derivation, including original frame order. The statistics use separate QR regression, explicit quantile interpolation, math.fsum means/sample SD and SciPy correlations. No production statistical function was imported or called. The 204 summarized frames comprise 200 sampled real halves, three fixed generated tables and one old full reference for the historical anchor check; there were no new generator executions.", "",
        f"Numeric leaves compared: {compare.numeric_leaves:,}; largest absolute implementation difference: {compare.maximum_absolute_difference:.6g}. Tolerances: rtol={RTOL:g}, atol={ATOL:g}.", "",
        "All 34 shared historical point metrics per frame were checked where supported, covering both regressions, continuous marginals, female proportion and the two previously declared outcome associations. BMI–glucose Pearson/Spearman are two newly prespecified developmental diagnostics in this unit, not older holdout outcomes. Historical intervals remain unchanged.", "",
        f"All {len(inputs)} bound inputs and control files retained their pre-read hashes after the audit. Outputs contain only code, controls, aggregate statistics, counts and hashes; no participant IDs, sampled membership lists or generated rows were exported.", "",
        "This PASS means the arithmetic and accounting agree with the frozen design. All 100 splits remain same-cohort developmental analyses; this does not revalidate the generator's biological utility or establish equivalence, clinical validity, external transportability, an acceptance threshold or an independent-cohort calibration.", ""]
    with (HERE / "INDEPENDENT_REVIEW.md").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines))
    return {"status": result["status"], "split_n": 100, "metric_n": 36,
            "maximum_absolute_difference": compare.maximum_absolute_difference, "numeric_leaves": compare.numeric_leaves}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="Explicit coordinator-authorized postproduction audit")
    args = parser.parse_args()
    parser.error("--execute is required after coordinator authorization") if not args.execute else None
    print(json.dumps(run(args.freeze), indent=2, allow_nan=False))
