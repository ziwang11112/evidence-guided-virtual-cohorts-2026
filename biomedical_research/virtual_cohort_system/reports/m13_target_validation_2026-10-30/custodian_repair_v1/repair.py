"""Authorized technical XPORT decoder repair, preserving the original M13-B freeze.

No downloads, scientific changes, generator execution, or endpoint analysis.
Re-read already acquired bytes with pyreadstat; use unchanged frozen build_frames.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent
M13B = HERE.parent
sys.path.insert(0, str(M13B / "custodian"))
import prep


def compare_readers(pandas_table, trusted_table, columns, name):
    """Record decode counts only; never print participant values."""
    prep.require(list(trusted_table) == columns, name + ": trusted-reader schema/order mismatch")
    p = pandas_table.loc[:, columns]
    t = trusted_table
    prep.require(len(p) == len(t), name + ": reader row-count mismatch")
    prep.require(np.array_equal(p.SEQN.to_numpy(), t.SEQN.to_numpy()), name + ": reader key mismatch")
    audit = {}
    for col in columns:
        a = p[col].to_numpy(dtype=float)
        b = t[col].to_numpy(dtype=float)
        prep.require(np.array_equal(np.isnan(a), np.isnan(b)), name + ": missingness mismatch: " + col)
        unequal = (a != b) & ~(np.isnan(a) & np.isnan(b))
        # Diagnostic assertion only: no threshold-based data correction occurs.
        # The independent reader supplies every value used in the corrected frame.
        exact_zero_defect = (b == 0.0) & (a == float.fromhex("0x1.0000000000000p-260"))
        prep.require(np.all(~unequal | exact_zero_defect), name + ": nonzero reader discrepancy: " + col)
        audit[col] = {"zero_decode_discrepancy_count": int(unequal.sum()),
                      "all_nonzero_values_identical": True, "missingness_identical": True}
    return {"rows": len(t), "keys_identical": True, "selected_schema_identical": True, "variables": audit}


def run(args):
    prep.require(args.authorize_technical_decoder_repair, "Explicit technical-repair flag required")
    gate = prep.verify_gate(args.freeze_manifest.resolve(), args.freeze_sha256, args.authorization.resolve())
    prep.require(pyreadstat.__version__ == "1.3.7", "This repair was authorized for installed pyreadstat 1.3.7")
    original = (M13B / "custodian" / "acquisition").resolve()
    output = (M13B / "custodian" / "acquisition_corrected").resolve()
    prep.require(not output.exists(), "Corrected output already exists; original and repair attempts are immutable")
    receipt_path = original / "private" / "acquisition_receipt.json"
    original_receipt = prep.load_json(receipt_path)
    prep.require(original_receipt["status"] == "complete", "Original acquisition is not complete")
    prep.require(original_receipt["gate"]["freeze_manifest_sha256"] == args.freeze_sha256,
                 "Original acquisition belongs to another freeze")
    for item in original_receipt["outputs"].values():
        prep.require(prep.sha256(Path(item["path"])) == item["sha256"], "Original output changed")
    sources = {}
    for item in original_receipt["downloads"]:
        path = original / "private" / "raw" / (item["component"] + ".xpt")
        prep.require(prep.sha256(path) == item["sha256"], "Original raw file changed")
        sources[item["component"]] = {**item, "local_path": str(path)}
    prep.require(set(sources) == {"DEMO_J", "BMX_J", "DXX_J"}, "Original component roster mismatch")
    output.mkdir()
    (output / ".gitignore").write_text("*\n", encoding="utf-8")
    private = output / "private"
    private.mkdir()
    generator_input = output / "generator_input"
    generator_input.mkdir()
    amendment = {"schema_version": "m13b_technical_decoder_amendment_v1", "status": "started",
                 "started_at_utc": prep.now(), "gate": gate,
                 "root_authorization": "Root explicitly authorized pyreadstat 1.3.7 repair in this chat after acquisition; preserve frozen science and original artifacts.",
                 "repair_script": {"path": str(Path(__file__).resolve()), "sha256": prep.sha256(Path(__file__))},
                 "unchanged_frozen_transform": {"path": str(Path(prep.__file__).resolve()), "sha256": prep.sha256(Path(prep.__file__))},
                 "versions": {"pandas": pd.__version__, "pyreadstat": pyreadstat.__version__, "numpy": np.__version__},
                 "original_receipt": {"path": str(receipt_path), "sha256": prep.sha256(receipt_path)},
                 "raw_sources": sources, "reader_comparison": {},
                 "scientific_changes": [],
                 "method": "Re-read all required columns with pyreadstat; accept only exact pandas zero-decoding differences. No small-weight threshold or new eligibility rule."}
    amendment_path = private / "technical_amendment.json"
    prep.write_json(amendment_path, amendment)
    try:
        metadata = prep.load_json(prep.METADATA)
        corrected = []
        for name in ["DEMO_J", "BMX_J", "DXX_J"]:
            raw = Path(sources[name]["local_path"])
            columns = metadata["components"][name]["variables"]
            pandas_table = pd.read_sas(raw, format="xport", encoding="utf-8")
            trusted_table, _ = pyreadstat.read_xport(str(raw), usecols=columns)
            # XPORT retains source column order; the selected ABI is explicit.
            prep.require(set(trusted_table.columns) == set(columns), name + ": selected columns missing")
            trusted_table = trusted_table.loc[:, columns]
            amendment["reader_comparison"][name] = compare_readers(pandas_table, trusted_table, columns, name)
            corrected.append(trusted_table)
        demo = corrected[0]
        amendment["MEC_weight_check"] = {
            "DEMO_rows": len(demo), "zero_weights": int(demo.WTMEC2YR.eq(0).sum()),
            "positive_finite_weights": int((np.isfinite(demo.WTMEC2YR) & demo.WTMEC2YR.gt(0)).sum()),
            "no_arbitrary_small_weight_threshold": True,
        }
        frame, observed, quality = prep.build_frames(*corrected)
        outputs = {"full_frame": private / "full_frame.csv", "generator_input": generator_input / "observed.csv",
                   "id_mapping": private / "id_mapping.csv", "quality_report": private / "quality_report.json"}
        frame.to_csv(outputs["full_frame"], index=False)
        observed.to_csv(outputs["generator_input"], index=False)
        frame[["id", "SEQN"]].to_csv(outputs["id_mapping"], index=False)
        prep.write_json(outputs["quality_report"], quality)
        amendment["outputs"] = {name: {"path": str(path), "sha256": prep.sha256(path)} for name, path in outputs.items()}
        amendment["status"] = "complete"
        amendment["completed_at_utc"] = prep.now()
        amendment["postrepair_frozen_gate"] = prep.verify_gate(args.freeze_manifest.resolve(), args.freeze_sha256,
                                                               args.authorization.resolve())
        prep.write_json(amendment_path, amendment)
    except Exception as exc:
        amendment["status"] = "failed"
        amendment["failure_at_utc"] = prep.now()
        amendment["error"] = str(exc)
        prep.write_json(amendment_path, amendment)
        raise
    return {"status": "complete", "technical_amendment": str(amendment_path),
            "requirement": "Independent audit before generator execution"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--freeze-manifest", type=Path, required=True)
    p.add_argument("--freeze-sha256", required=True)
    p.add_argument("--authorization", type=Path, required=True)
    p.add_argument("--authorize-technical-decoder-repair", action="store_true")
    print(json.dumps(run(p.parse_args()), indent=2))
