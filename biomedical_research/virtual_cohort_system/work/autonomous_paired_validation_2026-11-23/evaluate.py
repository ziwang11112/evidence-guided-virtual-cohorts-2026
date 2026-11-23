"""Evaluate the same signed paired endpoints using frozen, independently declared column mappings."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
import numbers
from pathlib import Path

import numpy as np
import pandas as pd


TIE_ATOL = 1e-10
BOOTSTRAP_SEED = 20261123
BOOTSTRAP_REPLICATES = 2000
HEIGHT_TO_M = {"m": 1.0, "cm": 0.01, "mm": 0.001, "in": 0.0254}
WEIGHT_TO_KG = {"kg": 1.0, "g": 0.001, "lb": 0.45359237}


def unit_name(value):
    return str(value).strip().replace("²", "2").replace("^2", "2").casefold()


def validate(mapping):
    if not isinstance(mapping, dict) or not {"unit", "threshold", "id", "reported", "measured"} <= mapping.keys():
        raise ValueError("Require unit, signed threshold, ID policy and both measurement mappings")
    allowed = {"unit", "threshold", "id", "row_identity_basis", "reported", "measured",
               "sheet", "header_row", "missing_values", "encoding", "row_filters"}
    if mapping.keys() - allowed:
        raise ValueError("Unknown mapping options: " + str(sorted(mapping.keys() - allowed)))
    threshold = mapping["threshold"]
    if (not isinstance(threshold, numbers.Real) or isinstance(threshold, bool) or
            not np.isfinite(threshold) or not isinstance(mapping["unit"], str) or not mapping["unit"].strip()):
        raise ValueError("Specify a finite numeric threshold and a nonempty analysis unit")
    ident = mapping["id"]
    if ident is None:
        if not str(mapping.get("row_identity_basis") or "").strip():
            raise ValueError("Document the basis for one independent person per row when ID is absent")
    elif not isinstance(ident, str) or not ident.strip():
        raise ValueError("ID must be a column label or null")
    if type(mapping.get("header_row", 0)) is not int or mapping.get("header_row", 0) < 0:
        raise ValueError("header_row must be a nonnegative zero-based index")
    if not isinstance(mapping.get("missing_values", []), list):
        raise ValueError("missing_values must be a list of source-specific markers")
    filters = mapping.get("row_filters", [])
    if not isinstance(filters, list):
        raise ValueError("row_filters must be a list")
    for item in filters:
        if (not isinstance(item, dict) or item.keys() != {"column", "op", "value"}
                or not isinstance(item["column"], str)
                or item["op"] not in {"eq", "ge", "gt", "le", "lt"}):
            raise ValueError("Invalid source cohort filter")
    source_names = []
    for role in ("reported", "measured"):
        side = mapping[role]
        if isinstance(side, dict) and side.keys() == {"column", "unit"}:
            fields = [side]
            if unit_name(side["unit"]) != unit_name(mapping["unit"]):
                raise ValueError("Direct measures must be expressed in the analysis unit")
        elif isinstance(side, dict) and side.keys() == {"height", "weight"}:
            fields = [side["height"], side["weight"]]
            if (unit_name(mapping["unit"]) != "kg/m2" or
                    any(not isinstance(f, dict) or f.keys() != {"column", "unit"} for f in fields) or
                    unit_name(fields[0]["unit"]) not in HEIGHT_TO_M or unit_name(fields[1]["unit"]) not in WEIGHT_TO_KG):
                raise ValueError("BMI requires declared supported height and weight units")
        else:
            raise ValueError("Define either a direct column or height and weight for each side")
        names = [f["column"] for f in fields]
        if (any(not isinstance(c, str) or not c.strip() or c == ident for c in names)
                or len(set(names)) != len(names)):
            raise ValueError("Invalid or duplicate measurement column")
        source_names.append(names)
    if source_names[0] == source_names[1]:
        raise ValueError("Identical source columns cannot supply two distinct paired measures")


def numeric_column(frame, name, mapping):
    if name not in frame:
        raise ValueError("Missing required column " + name)
    series = frame[name].replace(r"^\s*$", np.nan, regex=True)
    markers = mapping.get("missing_values", [])
    if markers:
        series = series.mask(series.isin(markers) | series.astype(str).str.strip().isin([str(v) for v in markers]))
    value = pd.to_numeric(series, errors="raise").to_numpy(dtype=float, na_value=np.nan)
    if np.isinf(value).any():
        raise ValueError("Nonfinite input measurement in " + name)
    return value


def measurement(frame, spec, mapping):
    if "column" in spec:
        value = numeric_column(frame, spec["column"], mapping)
        return value, value <= 0
    height = numeric_column(frame, spec["height"]["column"], mapping) * HEIGHT_TO_M[unit_name(spec["height"]["unit"])]
    weight = numeric_column(frame, spec["weight"]["column"], mapping) * WEIGHT_TO_KG[unit_name(spec["weight"]["unit"])]
    invalid = (height <= 0) | (weight <= 0)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        value = weight / height**2
    return value, invalid


def paired_intervals(diff, below):
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    estimates = np.empty((BOOTSTRAP_REPLICATES, 2))
    for i in range(BOOTSTRAP_REPLICATES):
        indices = rng.integers(len(diff), size=len(diff))
        estimates[i] = [np.mean(diff[indices]), 100 * np.mean(below[indices])]
    lohi = np.quantile(estimates, [0.025, 0.975], axis=0).T
    return {"replicates": BOOTSTRAP_REPLICATES, "seed": BOOTSTRAP_SEED,
            "method": "paired participant percentile bootstrap, linear quantiles",
            "interval_95": {"mean_difference": lohi[0].tolist(), "strictly_below_pct": lohi[1].tolist()}}


def evaluate(frame, mapping, *, bootstrap=False):
    validate(mapping)
    if not frame.columns.is_unique:
        raise ValueError("Input has duplicate column labels")
    n_source = len(frame)
    for condition in mapping.get("row_filters", []):
        column, op, value = condition["column"], condition["op"], condition["value"]
        if op == "eq" and isinstance(value, str):
            keep = frame[column].astype("string").str.strip().eq(value)
        else:
            values = pd.Series(numeric_column(frame, column, mapping), index=frame.index)
            keep = getattr(values, op)(float(value))
        frame = frame.loc[keep.fillna(False)]
    ident = mapping["id"]
    if ident is not None:
        if ident not in frame:
            raise ValueError("No declared ID column")
        ids = frame[ident].astype("string").str.strip()
        if ids.isna().any() or ids.eq("").any() or ids.duplicated().any():
            raise ValueError("Missing or duplicate participant ID")
    reported, invalid_r = measurement(frame, mapping["reported"], mapping)
    measured, invalid_m = measurement(frame, mapping["measured"], mapping)
    if (invalid_r | invalid_m).any() or np.isinf(reported).any() or np.isinf(measured).any():
        raise ValueError("Nonpositive or nonfinite biomedical measurements; no rows excluded for plausibility")
    complete = ~np.isnan(reported) & ~np.isnan(measured)
    n = int(complete.sum())
    if n < 2:
        raise ValueError("Need at least two complete participant pairs")
    diff = reported[complete] - measured[complete]
    threshold = mapping["threshold"]
    ties = np.isclose(diff, threshold, rtol=0, atol=TIE_ATOL)
    below = (diff < threshold) & ~ties
    result = {"n_source": n_source, "n_removed_by_population_filters": n_source - len(frame),
              "n_input": len(frame), "n_complete": n, "n_incomplete": len(frame) - n,
              "n_missing_reported": int(np.isnan(reported).sum()), "n_missing_measured": int(np.isnan(measured).sum()),
              "id": ident, "row_identity_basis": mapping.get("row_identity_basis"),
              "analysis_unit": mapping["unit"], "difference": "reported minus measured",
              "threshold": threshold, "equality_atol": TIE_ATOL,
              "reported_mean": float(reported[complete].mean()), "measured_mean": float(measured[complete].mean()),
              "mean_difference": float(diff.mean()), "difference_sd": float(diff.std(ddof=1)),
              "strictly_below_n": int(below.sum()), "strictly_below_pct": float(100 * below.mean()),
              "ties_n": int(ties.sum())}
    if bootstrap:
        result["paired_bootstrap"] = paired_intervals(diff, below)
    return result


def parse_table(raw, filename, mapping):
    """Keep exact headers and preserve known missing codes until mapping is applied."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".dta":
        return pd.read_stata(BytesIO(raw), convert_categoricals=False, convert_dates=False, preserve_dtypes=False)
    if suffix == ".sav":
        import pyreadstat
        frame, _ = pyreadstat.read_sav(BytesIO(raw), apply_value_formats=False)
        return frame
    opts = dict(header=None, skiprows=mapping.get("header_row", 0), dtype=object, keep_default_na=False)
    if suffix in {".csv", ".tsv"}:
        data = pd.read_csv(BytesIO(raw), **opts, sep="\t" if suffix == ".tsv" else ",",
                           encoding=mapping.get("encoding", "utf-8-sig"))
    elif suffix in {".xlsx", ".xls"}:
        if not isinstance(mapping.get("sheet"), str) or not mapping["sheet"]:
            raise ValueError("Spreadsheet requires an explicit sheet name")
        data = pd.read_excel(BytesIO(raw), sheet_name=mapping["sheet"], **opts)
    else:
        raise ValueError("Expected CSV, TSV, spreadsheet, SAV or DTA")
    labels = [str(value).strip() for value in data.iloc[0]]
    if len(set(label for label in labels if label)) != sum(bool(label) for label in labels):
        raise ValueError("File has duplicate nonempty source headers")
    frame = data.iloc[1:, [bool(label) for label in labels]].copy().reset_index(drop=True)
    frame.columns = [label for label in labels if label]
    return frame


def immutable_json(path, value):
    path = Path(path)
    buf = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    if path.exists():
        if path.read_bytes() != buf:
            raise ValueError("Existing artifact differs: " + path.name)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as f:
            f.write(buf)


def freeze(table, mapping_path, lock_path):
    table, mapping_path = Path(table), Path(mapping_path)
    raw = mapping_path.read_bytes()
    mapping = json.loads(raw)
    validate(mapping)
    lock = {"table_name": table.name, "table_sha256": sha256(table.read_bytes()).hexdigest(),
            "mapping_filename": mapping_path.name, "mapping_file_sha256": sha256(raw).hexdigest(),
            "mapping": mapping, "original_mapping_text": raw.decode("utf-8-sig"),
            "mapping_had_bom": raw.startswith(b"\xef\xbb\xbf"),
            "scorer_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}
    immutable_json(lock_path, lock)
    return lock


def score(table, lock_path, *, bootstrap=False):
    table = Path(table)
    lock = json.loads(Path(lock_path).read_bytes())
    raw = table.read_bytes()
    if (lock["table_name"] != table.name or lock["table_sha256"] != sha256(raw).hexdigest() or
            lock["scorer_sha256"] != sha256(Path(__file__).read_bytes()).hexdigest()):
        raise ValueError("Source filename, data or scorer differs from the freeze")
    mapping = lock["mapping"]
    encoding = "utf-8-sig" if lock["mapping_had_bom"] else "utf-8"
    mapping_raw = lock["original_mapping_text"].encode(encoding)
    if sha256(mapping_raw).hexdigest() != lock["mapping_file_sha256"] or json.loads(mapping_raw) != mapping:
        raise ValueError("Frozen column mapping differs from its recorded source")
    validate(mapping)
    result = evaluate(parse_table(raw, table.name, mapping), mapping, bootstrap=bootstrap)
    result.update(lock_sha256=sha256(Path(lock_path).read_bytes()).hexdigest(),
                  input_sha256=lock["table_sha256"], mapping_file_sha256=lock["mapping_file_sha256"])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    lock_cmd = commands.add_parser("freeze")
    lock_cmd.add_argument("table", type=Path)
    lock_cmd.add_argument("mapping", type=Path)
    lock_cmd.add_argument("lock", type=Path)
    score_cmd = commands.add_parser("score")
    score_cmd.add_argument("table", type=Path)
    score_cmd.add_argument("lock", type=Path)
    score_cmd.add_argument("--bootstrap", action="store_true")
    score_cmd.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.command == "freeze":
        freeze(args.table, args.mapping, args.lock)
    else:
        payload = score(args.table, args.lock, bootstrap=args.bootstrap)
        if args.out:
            immutable_json(args.out, payload)
        else:
            print(json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=2))
