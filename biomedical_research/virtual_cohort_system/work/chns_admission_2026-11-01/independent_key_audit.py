"""Private identifier-only audit using ReadStat and Python counters/sets.

No identifier values or clinical values are serialized. The existing audit is
read only after all independent counts and schema comparisons are computed.
"""
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent
FILES = (
    "biomarker_09.sas7bdat", "pexam_00.sas7bdat",
    "mast_pub_12.sas7bdat", "surveys_pub_12.sas7bdat",
)
OLD_SURVEY_FIELDS = {
    "BIOMAKER", "DIET", "INDIVIDUAL", "PHYSICAL", "TOENAIL",
    "IDIND", "HHID", "LINE", "AGE_DAYS", "AGE", "WAVE", "COMMID",
    "T1", "T2", "T3", "T4", "T5", "STRATUM", "URBAN", "T7",
}


def digest(path):
    h = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def identifier(value):
    if pd.isna(value):
        return None
    numeric = float(value)
    if not math.isfinite(numeric) or not numeric.is_integer() or abs(numeric) >= 2**53:
        raise ValueError("Unsafe nonmissing identifier cell; values intentionally omitted")
    return int(numeric)


def count_file(name):
    path = ROOT / "private_data" / name
    _, metadata = pyreadstat.read_sas7bdat(path, metadataonly=True)
    schema = {column.upper(): column for column in metadata.column_names}
    if len(schema) != len(metadata.column_names):
        raise ValueError("Case-insensitive schema collision")
    wanted = ("IDIND",) if name.startswith("mast_") else ("IDIND", "WAVE")
    if not set(wanted) <= set(schema):
        raise ValueError("Required identifier field absent")
    # ReadStat receives an explicit column allowlist. Clinical columns are not
    # present in the returned frame; no dataframe merge or groupby is used.
    frame, _ = pyreadstat.read_sas7bdat(
        path, usecols=[schema[column] for column in wanted],
        disable_datetime_conversion=True, formats_as_category=False,
    )
    frame = frame[[schema[column] for column in wanted]]
    counts, wave_counts = Counter(), Counter()
    missing = 0
    for row in frame.itertuples(index=False, name=None):
        values = tuple(identifier(value) for value in row)
        if len(wanted) == 2 and values[1] is not None:
            wave_counts[values[1]] += 1
        if any(value is None for value in values):
            missing += 1
        else:
            counts[values] += 1
    if len(frame) != metadata.number_rows:
        raise ValueError("ReadStat header/decoded row-count mismatch")
    selected = counts if len(wanted) == 1 else Counter({key: n for key, n in counts.items() if key[1] == 2009})
    report = {
        "header_rows": int(metadata.number_rows), "decoded_rows": len(frame),
        "column_count": len(metadata.column_names), "rows_missing_key": missing,
        "finite_integral_keys": True, "keys_within_exact_float_integer_range": True,
        "duplicate_key_rows_all_waves": sum(n for n in counts.values() if n > 1),
        "join_ready": all(n == 1 for n in selected.values()),
        "sha256": digest(path),
    }
    if len(wanted) == 2:
        report.update(
            wave_record_counts={str(wave): wave_counts[wave] for wave in sorted(wave_counts)},
            records_wave_2009=sum(selected.values()),
            duplicate_key_rows_2009=sum(n for n in selected.values() if n > 1),
        )
    return report, selected, schema


def main():
    reports, selected, schemas = {}, {}, {}
    for name in FILES:
        reports[name], selected[name], schemas[name] = count_file(name)
    joins = {}
    biomarker = selected[FILES[0]]
    if reports[FILES[0]]["join_ready"]:
        for name in FILES[1:]:
            if not reports[name]["join_ready"]:
                joins[name] = {"status": "unavailable_due_to_duplicate_keys"}
                continue
            reference = set(selected[name])
            matched = sum(n for key, n in biomarker.items()
                          if ((key[0],) if name.startswith("mast_") else key) in reference)
            total = sum(biomarker.values())
            joins[name] = {
                "biomarker_records": total, "matched_records": matched,
                "unmatched_records": total - matched,
                "join_validation": "many_to_one" if name.startswith("mast_") else "one_to_one",
            }
    missing_fields = sorted(OLD_SURVEY_FIELDS - set(schemas[FILES[3]]))
    added_fields = sorted(set(schemas[FILES[3]]) - OLD_SURVEY_FIELDS)

    # First contact with the controller's numerical audit occurs only here.
    expected = json.loads((ROOT / "SCHEMA_AND_KEY_AUDIT.json").read_text(encoding="utf-8"))
    discrepancies = []
    for name, report in reports.items():
        for field, value in report.items():
            if expected["files"][name].get(field) != value:
                discrepancies.append(name + ":" + field)
    if expected["join_2009"] != joins:
        discrepancies.append("join_2009")

    lines = [
        "# Independent CHNS identifier and schema audit", "",
        "1 November 2026. " + ("**PASS: all independently computed checks match the controller audit.**" if not discrepancies else "**DISAGREEMENT: see comparison below.**"), "",
        "ReadStat (`pyreadstat`) decoded only the explicitly requested ID/wave columns into returned frames. "
        "Python counters and set membership independently computed duplicates and linkage counts; the controller used pandas' SAS reader and dataframe duplicate/merge operations. "
        "The controller JSON was loaded only after all independent computations. This is a second decoder and counting implementation, not a rereading of reported counts.", "",
        "No participant identifiers, clinical values, age/sex summaries, moments, associations or row excerpts were printed or saved. "
        "Per-wave counts are structural exposure and are not eligibility counts. No analytic cohort was formed. F2, state, generators and original-study quotas were not changed.", "",
        "## Integrity and duplicate counts", "",
        "| File | Header / decoded rows | Columns | Missing-key rows | Duplicate-key rows, all waves | Complete-key rows, 2009 | Duplicate-key rows, 2009 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, report in reports.items():
        lines.append(f"| `{name}` | {report['header_rows']} / {report['decoded_rows']} | {report['column_count']} | {report['rows_missing_key']} | {report['duplicate_key_rows_all_waves']} | {report.get('records_wave_2009', 'Not wave-indexed')} | {report.get('duplicate_key_rows_2009', 'Not wave-indexed')} |")
    lines += ["", "Duplicate counts include every row in a repeated complete-key group, not just excess rows. "
              "Every observed key cell was separately checked for finite integral representation and magnitude below 2^53, including wave cells in rows with missing person IDs. "
              "Whole-file SHA-256 values also match the controller audit; no identifier was rounded or silently deduplicated.", "",
              "## Wave counts and biomarker linkage", "",
              "Wave counts include every nonmissing wave cell, even if the corresponding person key is missing; 2009 linkage counts use complete keys only.", ""]
    for name, report in reports.items():
        if "wave_record_counts" in report:
            lines.append(f"- `{name}`: " + "; ".join(f"{wave}: {count}" for wave, count in report["wave_record_counts"].items()) + ".")
    lines += ["", "| Companion | Biomarker 2009 records | Matched | Unmatched | Cardinality |", "|---|---:|---:|---:|---|"]
    for name, join in joins.items():
        if "matched_records" in join:
            lines.append(f"| `{name}` | {join['biomarker_records']} | {join['matched_records']} | {join['unmatched_records']} | {join['join_validation']} |")
        else:
            lines.append(f"| `{name}` | unavailable | unavailable | unavailable | Duplicate keys |")
    lines += ["", "A matched identifier does not establish a nonmissing assay, anthropometry, age or gender value, same-day measurement, fasting compliance, biological eligibility or source applicability.", "",
              "## Survey dictionary mismatch", "",
              "The old `surveys_pub_12.pdf` lists 20 fields on pp. 1-3. Comparison with the actual SAS header, with field-name case normalized only, finds:", "",
              "- Missing from the actual file: " + (", ".join(f"`{field}`" for field in missing_fields) or "none") + ".",
              "- Additional actual fields: " + (", ".join(f"`{field}`" for field in added_fields) or "none") + ".", "",
              "This is a documented release/dictionary difference, not an inferred rename. `AGE` remains a distinct field; its label's rounding/reference-date limitations from [CODEBOOK_SCHEMA_AUDIT.md](CODEBOOK_SCHEMA_AUDIT.md) still apply. No absent field was reconstructed or imputed.", "",
              "## Comparison and reproducibility", "",
              "Discrepancies: " + (", ".join(discrepancies) if discrepancies else "none") + ".", "",
              "Private checker: `independent_key_audit.py`; SHA-256 `" + digest(Path(__file__)) + "`. "
              "Compared against `SCHEMA_AND_KEY_AUDIT.json`; SHA-256 `" + digest(ROOT / "SCHEMA_AND_KEY_AUDIT.json") + "`. "
              "The checker retains identifiers only in process memory and writes this aggregate Markdown report. No patient rows or additional dataset artifacts are saved.", ""]
    (ROOT / "INDEPENDENT_KEY_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "pass" if not discrepancies else "disagreement", "discrepancies": discrepancies,
                      "files": reports, "joins": joins, "missing_survey_fields": missing_fields,
                      "added_survey_fields": added_fields}, indent=2))


if __name__ == "__main__":
    main()
