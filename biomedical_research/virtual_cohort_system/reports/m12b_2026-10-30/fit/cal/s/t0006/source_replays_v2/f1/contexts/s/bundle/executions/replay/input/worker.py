"""Trusted entry point inside a curated Linux namespace; never run on the host."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import traceback


def main() -> int:
    root = Path("/input")
    request = json.loads((root / "request.json").read_text())
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (request["timeout_seconds"], request["timeout_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (request["memory_mb"] * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (request["output_bytes"],) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    report = {"schema_version": 1, "status": "started", "generator_started": False,
              "scope": "generator_execution_only", "scientific_validity": "not_assessed"}
    try:
        import numpy as np
        import pandas as pd
        report["runtime"] = {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__}
        report["pre_import_probe"] = {
            "mnt_visible": Path("/mnt").exists(), "home_visible": Path("/home").exists(),
            "network_interfaces": sorted(p.name for p in Path("/sys/class/net").iterdir())
            if Path("/sys/class/net").exists() else "sys_not_mounted",
            "route_table": Path("/proc/net/route").read_text().splitlines()[1:],
        }
        task = json.loads((root / "task.json").read_text())
        specification = json.loads((root / "model_spec.json").read_text())
        dtype = {c["name"]: "string" for c in task["columns"]
                 if c["kind"] == "string" or
                 (c["kind"] == "category" and all(isinstance(v, str) for v in c["categories"]))}
        observed = None if task["mode"] == "whole_cohort" else pd.read_csv(
            root / "observed.csv", dtype=dtype, float_precision="round_trip",
            keep_default_na=False, na_values=[""])
        module_spec = importlib.util.spec_from_file_location("candidate_generator", root / "generator.py")
        module = importlib.util.module_from_spec(module_spec)
        report.update(status="executing", generator_started=True)
        Path("/output/worker_report.json").write_text(json.dumps(report, indent=2) + "\n")
        module_spec.loader.exec_module(module)
        output = module.generate(observed, specification, request["seed"])
        if not isinstance(output, pd.DataFrame):
            raise TypeError("generate must return a pandas DataFrame")
        output.to_csv("/output/generated.csv", index=False)
        report.update(status="completed", rows=len(output), columns=list(output.columns))
        code = 0
    except BaseException as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error)[:2000])
        traceback.print_exc()
        code = 2
    Path("/output/worker_report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

