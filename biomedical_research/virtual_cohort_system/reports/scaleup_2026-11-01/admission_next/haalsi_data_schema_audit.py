"""One hash-pinned HAALSI schema/ID/missingness audit; no measurement output.

No network, conversion, clinical filter, model, summary moment or file export.
Pandas is pinned because Stata header fields use its inspected private API.
Run --self-test for invented in-memory missing/ID arithmetic only.
The actual-file run requires --run-authorized-audit and refuses an existing result.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
import warnings

import pandas as pd
from pandas.io.stata import StataMissingValue, StataReader


BASE = Path(__file__).resolve().parent
INPUT = BASE / "private_data" / "HAALSI_baseline_dataverse_14Apr2017.dta"
OUTPUT = BASE / "HAALSI_DATA_SCHEMA_AUDIT.json"
EXPECTED_BYTES = 19039887
EXPECTED_MD5 = "e11a69121c7cee6726835d6106820104"
EXPECTED_SHA256 = "27c968d5c9e53948bc8ee21e0a5bdc2262ed3c17f1dbafb5bb303050b6715b9f"
PANDAS_VERSION = "3.0.3"
CORE = ("rage", "rsex", "c_bs_bmi", "c_bs_glucose")
SELECTED = (
    "prim_key", *CORE, "c_bs_height", "c_bs_weight", "c_bs_hrslastate",
    "c_bs_fasting8hr", "fl_c_bs_glucose", "fl_c_bs_height", "fl_c_bs_weight",
    "fl_c_bs_bmi",
)
TOKEN_FIELDS = (
    "rsex", "c_bs_fasting8hr", "fl_c_bs_glucose", "fl_c_bs_height",
    "fl_c_bs_weight", "fl_c_bs_bmi",
)


def missing_kind(value: object) -> str | None:
    """Physical Stata missing only; labeled numeric sentinels stay nonmissing."""
    if isinstance(value, StataMissingValue):
        return value.string
    if isinstance(value, str):
        return "empty_or_whitespace_string" if not value.strip() else None
    if pd.isna(value):
        return "other_native_na"
    return None


def missing_audit(series: pd.Series) -> tuple[pd.Series, dict]:
    kinds = series.map(missing_kind)
    mask = kinds.notna()
    return mask, {
        "physical_missing_count": int(mask.sum()),
        "physical_nonmissing_count": int((~mask).sum()),
        "missing_kind_counts": dict(sorted(Counter(kinds[mask]).items())),
    }


def id_audit(series: pd.Series, missing: pd.Series) -> dict:
    ids = series[~missing]
    unique = int(ids.nunique(dropna=False))
    return {
        "missing_count": int(missing.sum()),
        "nonmissing_count": int(len(ids)),
        "unique_nonmissing_count": unique,
        "duplicate_excess_count": int(len(ids) - unique),
        "rows_in_duplicate_groups": int(ids.duplicated(keep=False).sum()),
        "comparison_rule": "Exact stored nonmissing ID; no trimming, recoding or token output.",
    }


def numeric_code(value: object) -> str:
    """Only finite integer coding tokens can be emitted from allowed fields."""
    # A string or nonintegral/huge number cannot become an accidental measurement
    # or identifier display. Stata missing objects are excluded before this call.
    if isinstance(value, (str, bytes, bool)):
        raise ValueError("Unexpected categorical token type")
    number = float(value)
    if not (-1_000_000 <= number <= 1_000_000) or not number.is_integer():
        raise ValueError("Unexpected categorical token")
    return str(int(number))


def code_tokens(series: pd.Series, missing: pd.Series) -> list[str]:
    codes = {numeric_code(value) for value in series[~missing].unique()}
    if len(codes) > 32:
        raise ValueError("Unexpected categorical cardinality")
    return sorted(codes, key=int)


def audit_actual_file() -> None:
    if pd.__version__ != PANDAS_VERSION:
        raise RuntimeError("Unreviewed pandas version")
    if OUTPUT.exists():
        raise FileExistsError("Audit result already exists")
    payload = INPUT.read_bytes()
    source_sha = hashlib.sha256(payload).hexdigest()
    source_md5 = hashlib.md5(payload).hexdigest()
    if (len(payload), source_md5, source_sha) != (
        EXPECTED_BYTES, EXPECTED_MD5, EXPECTED_SHA256
    ):
        raise ValueError("Input identity mismatch")

    # Header and label dictionaries first. No row is materialized by these calls.
    with StataReader(
        BytesIO(payload), convert_dates=False, convert_categoricals=False,
        convert_missing=True, preserve_dtypes=True,
    ) as reader:
        variable_labels = reader.variable_labels()
        all_value_labels = reader.value_labels()
        names = list(reader._varlist)
        label_set_names = dict(zip(names, reader._lbllist, strict=True))
        row_count = int(reader._nobs)
        column_count = int(reader._nvar)
        if len(names) != column_count or len(set(names)) != column_count:
            raise ValueError("Unexpected header schema")
        present = [name for name in SELECTED if name in variable_labels]
        absent = [name for name in SELECTED if name not in variable_labels]
        if any(name not in present for name in ("prim_key", *CORE)):
            raise ValueError("Required schema field absent")
        field_metadata = {}
        for name in present:
            label_set = label_set_names[name]
            field_metadata[name] = {
                "variable_label": variable_labels[name],
                "value_label_set": label_set or None,
                "value_label_dictionary": [
                    {"code": str(code), "label": label}
                    for code, label in sorted(all_value_labels.get(label_set, {}).items())
                ],
            }
        # The only table materialized has the fixed whitelist; no categoricals
        # are expanded, no dates transformed, and tagged missing is preserved.
        frame = reader.read(columns=present)
    if len(frame) != row_count or list(frame.columns) != present:
        raise ValueError("Read/header disagreement")

    masks, counts = {}, {}
    for name in present:
        masks[name], counts[name] = missing_audit(frame[name])
        field_metadata[name]["loaded_dtype"] = str(frame[name].dtype)
    core_available = ~masks[CORE[0]]
    for name in CORE[1:]:
        core_available = core_available & ~masks[name]
    tokens = {
        name: code_tokens(frame[name], masks[name])
        for name in TOKEN_FIELDS if name in present
    }
    result = {
        "audit_kind": "schema_id_physical_missingness_only",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "filename": INPUT.name, "bytes": EXPECTED_BYTES,
            "md5": source_md5, "sha256": source_sha,
        },
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "pandas_version": pd.__version__,
        "scope": {
            "selected_columns": list(SELECTED), "absent_selected_columns": absent,
            "categorical_token_columns": list(TOKEN_FIELDS),
            "measurement_values_or_moments_emitted": False,
            "clinical_filters_applied": False,
            "labelled_sentinels_automatically_reclassified": False,
            "counts_are_final_analysis_sample_size": False,
        },
        "file_dimensions": {"rows": row_count, "columns": column_count},
        "selected_field_metadata": field_metadata,
        "selected_field_missingness": counts,
        "id_integrity": id_audit(frame["prim_key"], masks["prim_key"]),
        "joint_core_physical_availability": {
            "columns": list(CORE),
            "all_four_physically_nonmissing": int(core_available.sum()),
            "at_least_one_physically_missing": int((~core_available).sum()),
            "rule": "Physical missing only; no eligibility, range, diagnosis, fasting, or code-label filter.",
        },
        "observed_categorical_codes_without_frequencies": tokens,
        "limitations": [
            "Native '.', '.a' through '.z' are counted separately when present.",
            "Empty/whitespace strings and other native NA are separate missing kinds.",
            "Numeric values with missing-like labels remain physically nonmissing; code meanings need a frozen later protocol.",
            "Metadata value-label codes are definitions, not continuous measurements.",
            "Availability is not final analysis eligibility or case admission.",
        ],
    }
    # Refuse overwrite. No participant row, ID token or continuous value is saved.
    with OUTPUT.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print("Schema/ID/physical-missingness audit saved; no measurement values emitted.")


def self_test() -> None:
    # Invented in-memory tokens only; no file access.
    ordinary = StataMissingValue(101)
    tagged = StataMissingValue(102)
    values = pd.Series([1, ordinary, tagged, "", " ", float("nan"), -9], dtype=object)
    mask, counts = missing_audit(values)
    assert mask.tolist() == [False, True, True, True, True, True, False]
    assert counts["missing_kind_counts"] == {
        ".": 1, ".a": 1, "empty_or_whitespace_string": 2, "other_native_na": 1,
    }
    ids = pd.Series(["toy-a", "toy-a", "toy-b", "", " toy-b"], dtype=object)
    idmask, _ = missing_audit(ids)
    result = id_audit(ids, idmask)
    assert (result["unique_nonmissing_count"], result["duplicate_excess_count"],
            result["rows_in_duplicate_groups"], result["missing_count"]) == (3, 1, 2, 1)
    codes = pd.Series([1, 0, 1, tagged], dtype=object)
    codemask, _ = missing_audit(codes)
    assert code_tokens(codes, codemask) == ["0", "1"]
    for value in ("secret", 1.5, float("inf")):
        try:
            numeric_code(value)
        except ValueError:
            pass
        else:
            raise AssertionError("Unexpected token accepted")
    print("Invented in-memory schema audit checks passed; no source file opened.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--run-authorized-audit", action="store_true")
    args = parser.parse_args()
    try:
        # Suppress library diagnostics that could echo payload values; unexpected
        # warnings fail safely and only the exception class is reported.
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self_test() if args.self_test else audit_actual_file()
    except Exception as error:
        print(f"Audit stopped safely ({type(error).__name__}); no exception payload emitted.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
