"""Contract validator. Does not inspect hidden truth or fit downstream analyses."""
from __future__ import annotations

import csv
import math
from pathlib import Path

COLS = ["person_id", "month", "weight_kg", "pfs", "gng", "dd100", "dd1000"]


def _read(path: Path):
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def _number(value: str) -> float:
    return float("nan") if value.strip().lower() in {"", "nan"} else float(value)


def _key(row):
    out = []
    for column in ("person_id", "month"):
        value = float(row[column])
        if not math.isfinite(value) or value != int(value):
            raise ValueError("Identifier and month must be finite integers")
        out.append(int(value))
    return tuple(out)


def validate_completion(input_csv: Path, targets_csv: Path, completion_csv: Path) -> dict:
    input_columns, original = _read(input_csv)
    target_columns, targets = _read(targets_csv)
    output_columns, completed = _read(completion_csv)
    if input_columns != COLS or output_columns != COLS or target_columns != ["person_id", "month"]:
        raise ValueError("Columns do not match canonical contract")
    if len(original) != len(completed):
        raise ValueError("Completion row count changed")
    original_keys, output_keys, target_keys = [list(map(_key, rs)) for rs in (original, completed, targets)]
    if len(set(original_keys)) != len(original_keys) or len(set(target_keys)) != len(target_keys):
        raise ValueError("Duplicate input or target keys")
    if output_keys != original_keys:
        raise ValueError("Completion keys or row order changed")
    if not set(target_keys).issubset(set(original_keys)):
        raise ValueError("Target keys absent from input")
    targets_set = set(target_keys)
    for before, after, row_key in zip(original, completed, original_keys):
        for column in COLS:
            a, b = _number(before[column]), _number(after[column])
            if column == "pfs" and row_key in targets_set:
                if not math.isnan(a):
                    raise ValueError("Target was observed in supplied input")
                if not math.isfinite(b) or not 1 <= b <= 5:
                    raise ValueError("Target imputation missing, nonfinite, or outside PFS bounds")
                if abs(15 * b - round(15 * b)) > 1e-3:
                    raise ValueError("Target imputation violates 15-item PFS lattice")
            elif not ((math.isnan(a) and math.isnan(b)) or a == b):
                raise ValueError("Non-target observed value or native missingness changed")
    return {"status": "passed", "n_rows": len(original), "n_targets": len(targets)}
