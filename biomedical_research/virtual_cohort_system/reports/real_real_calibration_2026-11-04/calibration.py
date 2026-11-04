"""Frozen descriptive real-real scale comparison; no reads or writes at import.

The pure helpers accept caller-supplied frames. Patient identifiers, community
identifiers and row positions never enter a report. Only run() may decode the
frozen input files, after its hash gate and an exclusive read receipt.
"""
from __future__ import annotations

import hashlib
import csv
import importlib.util
import json
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
SEEDS = tuple(range(8400, 8500))
SAMPLE_SIZE = 3000
REFERENCE_N = 6631
COMMUNITY_COUNT = 218
MAX_ATTEMPTS = 1000
HISTORICAL_HASHES = {
    "selection_definition": "52333d983959caf54c136540c4b31109c634358f078b7360ffa76ca070408d6a",
    "selection_plan": "a2c5f43969c700474a9466416be8503dc0c92b1c78b12a07a6edc6bc88f247b7",
    "selection_engine": "e40f403b13125f5b41f620126a807122bb99796558adda576518fcf50796365a",
    "historical_reference": "f5565a6fb54072462f278b2a6b6f0d7ff343d91bd6e166048e8da65bab1f1c10",
    "historical_generation_report": "2dfe84dca528adcc4edc6035b1f70ffbf13df72697ef82ac273344660824e2c6",
}
CONTINUOUS = ("age", "bmi", "glucose", "hba1c")
VARIABLES = ("age", "female", "bmi", "glucose", "hba1c")
MODELS = {"A": ("bmi", "age", "female"),
          "B": ("bmi", "glucose", "age", "female")}
PAIRS = (("bmi", "hba1c"), ("glucose", "hba1c"), ("bmi", "glucose"))
MARGINALS = ("mean", "sd_ddof1", "q10", "median", "q90")
METRIC_NAMES = tuple(
    [f"model_{model}.{term}" for model, terms in MODELS.items()
     for term in ("intercept", *terms)]
    + [f"{variable}.{stat}" for variable in CONTINUOUS for stat in MARGINALS]
    + ["female.proportion"]
    + [f"{left}_{right}.{method}" for left, right in PAIRS
       for method in ("pearson", "spearman")]
)
if len(METRIC_NAMES) != 36 or len(set(METRIC_NAMES)) != 36:
    raise RuntimeError("The fixed metric inventory must contain exactly 36 items")


def sha256(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path | str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_exclusive(path: Path | str, value: dict) -> None:
    # Serialize first so a nonfinite value cannot leave a partial JSON file.
    payload = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)


def _numeric_frame(frame: pd.DataFrame) -> np.ndarray:
    if not isinstance(frame, pd.DataFrame) or not frame.columns.is_unique:
        raise ValueError("An unambiguously named DataFrame is required")
    if not set(VARIABLES).issubset(frame.columns) or len(frame) < 6:
        raise ValueError("At least six complete rows and the five variables are required")
    for name in VARIABLES:
        if not pd.api.types.is_numeric_dtype(frame[name]) or pd.api.types.is_bool_dtype(frame[name]):
            raise ValueError(f"Numeric values without coercion required: {name}")
    values = frame[list(VARIABLES)].to_numpy(dtype=float, na_value=np.nan)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite values are not filtered or imputed")
    if not np.isin(frame["female"].to_numpy(), [0, 1]).all():
        raise ValueError("female must already be encoded as zero or one")
    return values


def _pearson(left: np.ndarray, right: np.ndarray) -> float:
    a, b = left - left.mean(), right - right.mean()
    divisor = np.sqrt(np.dot(a, a) * np.dot(b, b))
    if not np.isfinite(divisor) or divisor <= 0:
        raise ValueError("Undefined correlation; stop without replacing this split")
    return float(np.clip(np.dot(a, b) / divisor, -1.0, 1.0))


def summarize_metrics(frame: pd.DataFrame, *, errors: dict | None = None) -> dict[str, float | None]:
    """All nine OLS point coefficients and 27 descriptive measures; no CIs."""
    _numeric_frame(frame)
    metrics: dict[str, float | None] = {}
    unavailable = errors if errors is not None else {}
    def put(name: str, value: float | None, reason: str = "nonfinite_statistic") -> None:
        if value is None or not np.isfinite(value):
            metrics[name] = None
            unavailable[name] = reason
        else:
            metrics[name] = float(value)
    outcome = frame["hba1c"].to_numpy(dtype=float)
    for label, predictors in MODELS.items():
        design = np.column_stack((np.ones(len(frame)), frame[list(predictors)].to_numpy(dtype=float)))
        try:
            coefficients, _, rank, _ = np.linalg.lstsq(design, outcome, rcond=None)
            reason = "rank_deficient_design" if rank != design.shape[1] else "nonfinite_coefficient"
            for name, value in zip(("intercept", *predictors), coefficients):
                put(f"model_{label}.{name}", value if rank == design.shape[1] else None, reason)
        except np.linalg.LinAlgError:
            for name in ("intercept", *predictors):
                put(f"model_{label}.{name}", None, "lstsq_numerical_failure")
    for name in CONTINUOUS:
        values = frame[name].to_numpy(dtype=float)
        with np.errstate(all="ignore"):
            quantiles = np.quantile(values, [0.1, 0.5, 0.9], method="linear")
            statistics = (values.mean(), values.std(ddof=1), *quantiles)
        for statistic, value in zip(MARGINALS, statistics):
            put(f"{name}.{statistic}", value)
    put("female.proportion", frame["female"].mean())
    for left, right in PAIRS:
        a, b = frame[left].to_numpy(dtype=float), frame[right].to_numpy(dtype=float)
        # Average ranks, including ties, define Spearman's rho.
        ra = pd.Series(a).rank(method="average").to_numpy(dtype=float)
        rb = pd.Series(b).rank(method="average").to_numpy(dtype=float)
        for method, x, y in (("pearson", a, b), ("spearman", ra, rb)):
            try:
                with np.errstate(all="ignore"):
                    value = _pearson(x, y)
                put(f"{left}_{right}.{method}", value)
            except ValueError:
                put(f"{left}_{right}.{method}", None, "zero_variance_or_nonfinite_correlation")
    if tuple(metrics) != METRIC_NAMES:
        raise RuntimeError("The fixed 36-metric inventory is incomplete")
    return metrics


def _position_hash(positions: np.ndarray, domain: str) -> str:
    """SHA-256 of a domain tag and sorted little-endian uint64 positions."""
    encoded = np.sort(np.asarray(positions, dtype=np.uint64)).astype("<u8", copy=False)
    return hashlib.sha256((domain + "\0").encode("ascii") + encoded.tobytes()).hexdigest()


@dataclass(frozen=True)
class SampleSplit:
    # Ephemeral positional indices stay in memory; never serialize this object.
    r1_positions: np.ndarray
    r2_positions: np.ndarray
    audit: dict


class SamplingExhaustedError(RuntimeError):
    """Retain aggregate-only rejection history when a scheduled seed fails."""
    def __init__(self, seed: int, attempts: list[dict], sample_size: int):
        self.audit = {"failed_seed": int(seed), "attempts": attempts,
                      "attempt_n": len(attempts), "sample_n_per_side": sample_size,
                      "reason": "no_size_valid_partition_within_fixed_attempt_budget",
                      "replacement_seed_used": False, "eligibility_relaxed": False}
        super().__init__(f"Seed {seed}: no size-valid partition within {len(attempts)} attempts; no replacement seed")


def sample_disjoint_communities(
    reference: pd.DataFrame,
    seed: int,
    *,
    sample_size: int = SAMPLE_SIZE,
    expected_communities: int = COMMUNITY_COUNT,
    max_attempts: int = MAX_ATTEMPTS,
) -> SampleSplit:
    """One PCG64 stream; reject partitions for pool size only, then sample rows."""
    if sample_size < 1 or max_attempts < 1 or expected_communities < 2 or expected_communities % 2:
        raise ValueError("Positive sizes and an even number of communities are required")
    if "survey_commid" not in reference or reference["survey_commid"].isna().any():
        raise ValueError("A complete community assignment is required")
    if len(reference) < 2 * sample_size:
        raise ValueError("The reference has too few rows for two disjoint samples")
    codes, communities = pd.factorize(reference["survey_commid"], sort=True)
    if len(communities) != expected_communities:
        raise ValueError("Community count differs from the fixed design")
    if pd.api.types.is_numeric_dtype(communities.dtype) and not np.isfinite(communities).all():
        raise ValueError("Community labels must be finite")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    half = expected_communities // 2
    attempts = []
    for attempt in range(1, max_attempts + 1):
        order = rng.permutation(expected_communities)
        c1, c2 = order[:half], order[half:]
        pool1 = np.flatnonzero(np.isin(codes, c1))
        pool2 = np.flatnonzero(np.isin(codes, c2))
        accepted = len(pool1) >= sample_size and len(pool2) >= sample_size
        attempts.append({"attempt": attempt, "r1_pool_n": len(pool1), "r2_pool_n": len(pool2),
                         "accepted": bool(accepted),
                         "reason": "accepted" if accepted else "pool_size_below_sample_size"})
        if not accepted:
            continue
        row1 = np.sort(rng.choice(pool1, size=sample_size, replace=False))
        row2 = np.sort(rng.choice(pool2, size=sample_size, replace=False))
        if np.intersect1d(row1, row2).size or np.intersect1d(codes[row1], codes[row2]).size:
            raise RuntimeError("Internal failure: overlapping community or row selection")
        sides = {}
        for label, rows, cluster_positions, pool in (("R1", row1, c1, pool1), ("R2", row2, c2, pool2)):
            sides[label] = {
                "pool_n": len(pool), "sample_n": len(rows),
                "assigned_community_n": len(cluster_positions),
                "sampled_community_n": int(np.unique(codes[rows]).size),
                "selected_row_positions_sha256": _position_hash(rows, "real_real:rows:v1"),
                "assigned_community_positions_sha256": _position_hash(cluster_positions, "real_real:communities:v1"),
            }
        return SampleSplit(row1, row2, {
            "seed": int(seed), "accepted_attempt": attempt, "size_rejection_n": attempt - 1,
            "attempts": attempts, "R1": sides["R1"], "R2": sides["R2"],
            "row_disjoint": True, "community_disjoint": True,
        })
    raise SamplingExhaustedError(seed, attempts, sample_size)


def _quantiles(values: Sequence[float | None]) -> dict:
    available = [value for value in values if value is not None]
    if available and not np.isfinite(available).all():
        raise ValueError("Non-null discrepancy values must be finite")
    q = np.quantile(available, [0.1, 0.5, 0.9], method="linear") if available else [None] * 3
    return {**{name: None if value is None else float(value)
               for name, value in zip(("q10", "median", "q90"), q)},
            "scheduled_n": len(values), "available_n": len(available),
            "unavailable_n": len(values) - len(available)}


def _difference(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    difference = left - right
    return float(difference) if np.isfinite(difference) else None


def _abs(value: float | None) -> float | None:
    return None if value is None else abs(value)


def _symmetric_abs(left: float | None, right: float | None) -> float | None:
    return None if left is None or right is None else abs(left) / 2 + abs(right) / 2


def _difference_reasons(values: Mapping[str, float | None]) -> dict:
    return {name: "operand_metric_unavailable_or_nonfinite_difference"
            for name, value in values.items() if value is None}


def build_report(
    reference: pd.DataFrame,
    generated_frames: Mapping[str, pd.DataFrame],
    *,
    seeds: Sequence[int] = SEEDS,
    sample_size: int = SAMPLE_SIZE,
    expected_communities: int = COMMUNITY_COUNT,
    expected_reference_n: int = REFERENCE_N,
    max_attempts: int = MAX_ATTEMPTS,
) -> dict:
    """Pure evaluation: fixed G tables are summarized once, never regenerated.

    Nondefault counts are supported solely for small invented test fixtures;
    the file-backed run() accepts only the constants declared above.
    """
    _numeric_frame(reference)
    if len(reference) != expected_reference_n:
        raise ValueError("Reference row count differs from the fixed design")
    if len(generated_frames) != 3 or not all(isinstance(k, str) and k for k in generated_frames):
        raise ValueError("Exactly three named frozen generated tables are required")
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("A nonempty sequence of unique seeds is required")
    generated = {}
    for label, frame in generated_frames.items():
        if len(frame) != sample_size:
            raise ValueError("Every generated table must have the fixed sample size")
        errors: dict = {}
        generated[label] = {"n": len(frame), "metrics": summarize_metrics(frame, errors=errors), "unavailable": errors}
    splits = []
    for seed in seeds:
        selection = sample_disjoint_communities(
            reference, seed, sample_size=sample_size,
            expected_communities=expected_communities, max_attempts=max_attempts,
        )
        r1_errors, r2_errors = {}, {}
        r1 = summarize_metrics(reference.iloc[selection.r1_positions], errors=r1_errors)
        r2 = summarize_metrics(reference.iloc[selection.r2_positions], errors=r2_errors)
        rr_signed = {metric: _difference(r1[metric], r2[metric]) for metric in METRIC_NAMES}
        real_real = {metric: _abs(rr_signed[metric]) for metric in METRIC_NAMES}
        differences = {}
        for label, value in generated.items():
            signed = {metric: _difference(value["metrics"][metric], r2[metric]) for metric in METRIC_NAMES}
            sym_abs = {metric: _symmetric_abs(_difference(value["metrics"][metric], r1[metric]), signed[metric])
                       for metric in METRIC_NAMES}
            differences[label] = {"signed": signed, "absolute": {key: _abs(x) for key, x in signed.items()},
                                  "sym_abs": sym_abs,
                                  "unavailable": {"signed_and_absolute": _difference_reasons(signed),
                                                  "sym_abs": _difference_reasons(sym_abs)}}
        splits.append({"seed": int(seed), "selection": selection.audit,
                       "R1": r1, "R2": r2, "R1_unavailable": r1_errors, "R2_unavailable": r2_errors,
                       "real_real_signed": rr_signed, "real_real_abs": real_real,
                       "real_real_unavailable": _difference_reasons(rr_signed),
                       "generated_vs_R2": differences})
    summary = {}
    for metric in METRIC_NAMES:
        per_generated = {
            label: {kind: _quantiles([split["generated_vs_R2"][label][kind][metric] for split in splits])
                    for kind in ("signed", "absolute", "sym_abs")}
            for label in generated
        }
        summary[metric] = {"real_real": {kind: _quantiles([split[key][metric] for split in splits])
                                         for kind, key in (("signed", "real_real_signed"), ("absolute", "real_real_abs"))},
                           "generated": per_generated}
    return {
        "schema_version": 1,
        "kind": "descriptive_disjoint_community_real_real_scale_comparison",
        "design": {
            "reference_n": len(reference), "reference_community_n": expected_communities,
            "sample_n_per_side": sample_size, "communities_assigned_per_side": expected_communities // 2,
            "seeds": [int(x) for x in seeds], "split_n": len(splits),
            "rng": "numpy.random.Generator(numpy.random.PCG64(seed))",
            "max_partition_attempts_per_seed": max_attempts,
            "partition_acceptance_rule": "both community-pool row counts >= sample_n_per_side; size only",
            "sampling_order": "sorted community labels; permute; R1 choice then R2 choice; sort chosen row positions",
            "quantile_method": "linear", "sample_sd_ddof": 1, "spearman_ties": "average_ranks",
            "ols_solver": "numpy.linalg.lstsq(rcond=None); intercept; unweighted",
            "metric_n": len(METRIC_NAMES), "metric_names": list(METRIC_NAMES),
            "difference_summary_quantiles": ["q10", "median", "q90"],
            "unavailable_policy": "null with metric reason; retain split and all other metrics; no replacement",
            "summary_missing_policy": "available values per metric; always report scheduled/available/unavailable counts",
            "generated_table_n": len(generated), "generated_values_fixed_across_splits": True,
            "selection_hash_encoding": "domain + NUL + sorted little-endian uint64 positions",
            "selection_hash_domains": {"rows": "real_real:rows:v1", "communities": "real_real:communities:v1"},
        },
        "generated": generated, "splits": splits, "summary": summary,
        "limitations": [
            "Descriptive point differences only; no confidence intervals, equivalence margins or pass/fail decision.",
            "The selected CHNS reference was previously exposed; this is not independent confirmation or population truth.",
            "Repeated splits reuse one selected cohort and overlap across seeds; they are not independent clinical cohorts.",
            "R1 and R2 are complementary and dependent, while fixed G does not share that partition dependence.",
            "Matching row counts does not make discrepancy distributions exchangeable or match intracommunity dependence.",
            "Community partitioning and row subsampling are not the original survey sampling design.",
            "Symmetric absolute G discrepancy removes reference-role arbitrariness without correcting finite-sample dependence.",
            "The three frozen generated tables remain fixed across splits; this does not quantify generation-model uncertainty.",
            "The real-real distribution is conditional on equally partitioning communities and accepting only size-feasible pools.",
            "Unavailable statistics remain null with reasons and explicit counts; no metric-driven split replacement occurs.",
        ],
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_inputs(protocol_path: Path | str, freeze_path: Path | str) -> tuple[dict, dict, dict, dict]:
    """Read metadata and hash bytes only; never decode a clinical/generated row."""
    protocol_path, freeze_path = Path(protocol_path).resolve(), Path(freeze_path).resolve()
    _require(protocol_path.parent == HERE and freeze_path.parent == HERE, "Protocol and freeze must belong to this evaluation unit")
    protocol, freeze = read_json(protocol_path), read_json(freeze_path)
    _require(freeze["protocol_sha256"] == sha256(protocol_path), "Protocol hash mismatch")
    _require(set(freeze["code_sha256"]) == {"calibration.py", "test_calibration.py"}, "Freeze must bind both code files")
    for name, expected in freeze["code_sha256"].items():
        _require(sha256(HERE / name) == expected, f"Frozen code hash mismatch: {name}")
    _require(sha256(HERE / "DESIGN_REVIEW.md") == freeze["design_review_sha256"], "Design review hash mismatch")
    _require(Path(protocol["project_root"]).resolve() == PROJECT, "Unexpected project root")
    sampling = protocol["sampling"]
    _require((sampling["expected_reference_n"], sampling["expected_communities"], sampling["sample_size_each"],
              sampling["max_partition_attempts_per_seed"], sampling["seeds"])
             == (REFERENCE_N, COMMUNITY_COUNT, SAMPLE_SIZE, MAX_ATTEMPTS, list(SEEDS)), "Sampling differs from implemented frozen design")
    metrics, comparisons = protocol["metrics"], protocol["comparisons"]
    _require(metrics["regressions"] == {key: list(value) for key, value in MODELS.items()}
             and metrics["outcome"] == "hba1c" and metrics["intercept"] is True
             and metrics["all_coefficients"] is True and metrics["count"] == len(METRIC_NAMES)
             and metrics["continuous_variables"] == list(CONTINUOUS)
             and metrics["marginal_statistics"] == ["mean", "sd", "q10", "median", "q90"]
             and metrics["female"] == "proportion"
             and metrics["relationship_pairs"] == [list(pair) for pair in PAIRS]
             and metrics["correlations"] == ["pearson", "spearman"], "Metric inventory differs from implementation")
    _require(comparisons["summaries"] == ["q10", "median", "q90"]
             and comparisons["acceptance_threshold"] is None
             and all(comparisons[key] is False for key in ("ratios", "percentile_rank", "win_rate", "p_values"))
             and comparisons["all_metrics_and_seeds"] is True, "Comparison policy differs from implementation")
    inputs = {}
    def check_item(label: str, item: dict) -> None:
        path = Path(item["path"]).resolve()
        _require(path.is_file(), f"Required input is missing: {label}")
        actual = sha256(path)
        _require(actual == item["sha256"], f"Input hash mismatch: {label}")
        inputs[label] = {"path": str(path), "sha256": actual}
    for label, expected in HISTORICAL_HASHES.items():
        _require(protocol[label]["sha256"] == expected, f"Historical anchor changed: {label}")
        check_item(label, protocol[label])
    for label in ("generation_closure", "generator_freeze"):
        check_item(label, protocol[label])
    definition = read_json(protocol["selection_definition"]["path"])
    for old, current in (("metadata_only_original_plan", "selection_plan"), ("original_pure_linkage_engine", "selection_engine")):
        _require(definition[old]["sha256"] == protocol[current]["sha256"]
                 and Path(definition[old]["path"]).resolve() == Path(protocol[current]["path"]).resolve(),
                 "Original selection metadata is inconsistent")
    _require(len(definition["reference_files"]) == 4, "Exactly four reference files are required")
    private = Path(protocol["private_data_directory"]).resolve()
    _require(private == (PROJECT / "work/chns_admission_2026-11-01/private_data").resolve(), "Unexpected reference directory")
    for item in definition["reference_files"]:
        check_item("reference:" + item["file"], {"path": private / item["file"], "sha256": item["sha256"]})
    tables = protocol["generated_tables"]
    _require(len(tables) == 3 and [item["seed"] for item in tables] == [7401, 7402, 7403], "Unexpected generated table inventory")
    _require(len({str(Path(item["path"]).resolve()) for item in tables}) == 3, "Generated table paths must be distinct")
    for item in tables:
        check_item("generated:" + str(item["seed"]), item)
    return protocol, freeze, definition, inputs


def load_reference(protocol: dict, definition: dict) -> tuple[pd.DataFrame, dict]:
    """Use only the frozen historical pure decoder; caller must pass the gate."""
    import pyreadstat
    frames = {}
    private = Path(protocol["private_data_directory"])
    for item in definition["reference_files"]:
        frames[item["file"]], _ = pyreadstat.read_sas7bdat(
            str(private / item["file"]), usecols=item["columns"], user_missing=False)
    engine_path = Path(protocol["selection_engine"]["path"])
    spec = importlib.util.spec_from_file_location("frozen_real_real_reference_decoder", engine_path)
    _require(spec is not None and spec.loader is not None, "Historical decoder cannot be imported")
    engine = importlib.util.module_from_spec(spec)
    original_path, original_bytecode = sys.path.copy(), sys.dont_write_bytecode
    try:
        sys.path.insert(0, str(PROJECT))
        sys.dont_write_bytecode = True
        spec.loader.exec_module(engine)
        reference, quality = engine.prepare_reference_frames(frames, read_json(protocol["selection_plan"]["path"]))
    finally:
        sys.path[:] = original_path
        sys.dont_write_bytecode = original_bytecode
    _numeric_frame(reference)
    _require(len(reference) == REFERENCE_N and reference["survey_commid"].nunique() == COMMUNITY_COUNT,
             "Historical selected reference size/community count changed")
    return reference, quality


def load_generated(path: Path | str) -> pd.DataFrame:
    """Decode the frozen CSV once, rejecting schema or identifier violations."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream))
    _require(len(header) == len(set(header)) and set(header) == {"person_id", *VARIABLES}, "Generated schema mismatch or duplicate header")
    frame = pd.read_csv(path, dtype={"person_id": "string"}, float_precision="round_trip")
    _require(len(frame) == SAMPLE_SIZE, "Generated row count differs from 3000")
    identifiers = frame["person_id"]
    _require(not identifiers.isna().any() and not identifiers.str.strip().eq("").any()
             and not identifiers.duplicated().any(), "Generated IDs must be complete and unique")
    _numeric_frame(frame)
    _require(frame["age"].between(35, 74).all() and (frame[["bmi", "glucose", "hba1c"]] > 0).all().all(),
             "Generated values violate the original age/positive-measurement scope")
    return frame[list(VARIABLES)]


def run(protocol_path: Path | str, freeze_path: Path | str) -> Path:
    """Hash gate -> exclusive receipt -> decode -> evaluate -> exclusive report."""
    _require(not (HERE / "REPORT.json").exists(), "REPORT.json already exists; no overwrite or rerun")
    protocol, freeze, definition, inputs = verify_inputs(protocol_path, freeze_path)
    receipt = {
        "schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "descriptive comparison of previously exposed development inputs",
        "protocol_sha256": sha256(protocol_path), "freeze_sha256": sha256(freeze_path),
        "code_sha256": freeze["code_sha256"], "design_review_sha256": freeze["design_review_sha256"],
        "input_hashes_before_decode": inputs,
        "clinical_or_generated_values_decoded_before_receipt": False,
    }
    write_exclusive(HERE / "READ_RECEIPT.json", receipt)
    reference, quality = load_reference(protocol, definition)
    generated = {str(item["seed"]): load_generated(item["path"]) for item in protocol["generated_tables"]}
    try:
        report = build_report(reference, generated)
    except SamplingExhaustedError as error:
        write_exclusive(HERE / "FAILURE.json", {
            "schema_version": 1, "status": "stopped_without_replacement_seed",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "protocol_sha256": receipt["protocol_sha256"], "freeze_sha256": receipt["freeze_sha256"],
            "read_receipt_sha256": sha256(HERE / "READ_RECEIPT.json"),
            **error.audit,
        })
        raise
    # A mutation during decoding/evaluation must not publish a successful report.
    for label, item in inputs.items():
        _require(sha256(item["path"]) == item["sha256"], f"Input changed during evaluation: {label}")
    _require(sha256(protocol_path) == receipt["protocol_sha256"] and sha256(freeze_path) == receipt["freeze_sha256"],
             "Protocol/freeze changed during evaluation")
    for name, digest in freeze["code_sha256"].items():
        _require(sha256(HERE / name) == digest, f"Code changed during evaluation: {name}")
    import pyreadstat
    report["provenance"] = {
        "protocol_sha256": receipt["protocol_sha256"], "freeze_sha256": receipt["freeze_sha256"],
        "read_receipt_sha256": sha256(HERE / "READ_RECEIPT.json"),
        "code_sha256": freeze["code_sha256"], "input_hashes": inputs,
        "input_hashes_unchanged_after_evaluation": True,
        "new_generator_executions": 0, "reference_quality": quality,
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "pandas": pd.__version__, "pyreadstat": pyreadstat.__version__},
    }
    report["limitations"] = list(dict.fromkeys(report["limitations"] + protocol["limitations"]))
    output = HERE / "REPORT.json"
    write_exclusive(output, report)
    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    arguments = parser.parse_args()
    output_path = run(arguments.protocol, arguments.freeze)
    print(json.dumps({"report": str(output_path), "sha256": sha256(output_path), "split_n": len(SEEDS), "metric_n": len(METRIC_NAMES)}))
