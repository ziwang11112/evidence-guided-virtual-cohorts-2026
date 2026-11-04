"""Small analytical fixtures for added secondary routing and unavailable intervals."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from generated_diagnostics import analyze_generated
from comparison_core import independently_check

HERE = Path(__file__).resolve().parent
index = np.arange(160, dtype=float)
frame = pd.DataFrame({"age": 35 + index % 40, "female": (index % 3 == 0).astype(float),
                      "bmi": 20 + (index % 13) * .4 + np.sin(index),
                      "glucose": 4 + (index % 17) * .1 + np.cos(index) * .1})
frame["hba1c"] = 3 + .04 * frame.bmi + .3 * frame.glucose + .006 * frame.age + .12 * frame.female + .1 * np.sin(index * .7)
analysis = analyze_generated(frame, "B")
assert set(analysis["coefficients"]) == {"const", "bmi", "glucose", "age", "female"}
secondary = analysis["descriptive_secondary"]
assert set(secondary["coefficients"]) == {"const", "bmi", "age", "female"}
assert secondary["analysis_role"] == "prespecified_descriptive_secondary"
checks = [{"check": "B exposes primary and separately labeled descriptive-secondary adjustment sets", "status": "PASS"}]
for key, item in (("B", analysis), ("A", secondary)):
    checks.append({"check": "generated-only QR consistency " + key, **independently_check(frame, item, key)})
try:
    analyze_generated(frame, "A")
except ValueError:
    checks.append({"check": "public diagnostic request A is rejected", "status": "PASS"})
else:
    raise AssertionError("Unauthorized request accepted")
# A unique indicator can give one row leverage=1 while leaving a full-rank design.
frame["female"] = 0.0
frame.loc[0, "female"] = 1.0
edge = analyze_generated(frame, "B")
assert edge["status"] == "complete"
assert any(item["interval_status"] == "unavailable" for item in edge["coefficients"].values())
result = independently_check(frame, edge, "B")
assert result["status"] == "PASS" and result["unavailable_interval_checks"]
checks.append({"check": "full-rank high-leverage unavailable intervals retain coefficient verification", **result})
report = {"checks": checks, "analytical_fixture_rows": 160, "clinical_rows": 0,
          "scientific_candidate_executions": 0, "reference_read": False,
          "code_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                          for name in ("generated_diagnostics.py", "comparison_core.py")}}
with (HERE / "ANALYSIS_ROUTING_CHECKS.json").open("x", encoding="utf-8") as stream:
    json.dump(report, stream, indent=2, allow_nan=False)
    stream.write("\n")
print(json.dumps(report, indent=2, allow_nan=False))
