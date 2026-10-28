"""Artificial-input and approved-source integrity checks only; no observed.csv read."""

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
spec = json.loads((HERE / "initial/model_spec.json").read_text(encoding="utf-8"))
ledger = json.loads((HERE / "EVIDENCE_LEDGER.json").read_text(encoding="utf-8"))
module_spec = importlib.util.spec_from_file_location("initial_insulin", HERE / "initial/generator.py")
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)

checks = {}
artificial = pd.DataFrame({
    "row_id": [f"artificial_{i}" for i in range(40)],
    "bmi": np.tile([16.0, 20.0, 23.01, 27.0, 31.0, 40.0, 50.0, 60.0], 5),
    "age": np.resize([20, 24, 35, 44, 55, 60, 70, 79], 40),
    "sex": np.resize([1, 2], 40).astype(np.int64),
}, index=np.arange(101, 141))
before = artificial.copy(deep=True)
before_spec = json.dumps(spec, sort_keys=True)
state_before = np.random.get_state()
first = module.generate(artificial, spec, 1901)
second = module.generate(artificial, spec, 1901)
other = module.generate(artificial, spec, 1902)
state_after = np.random.get_state()
pd.testing.assert_frame_equal(artificial, before)
pd.testing.assert_frame_equal(first.iloc[:, :4], before)
pd.testing.assert_frame_equal(first, second)
assert list(first.columns) == ["row_id", "bmi", "age", "sex", "insulin"]
assert json.dumps(spec, sort_keys=True) == before_spec
assert not np.array_equal(first.insulin, other.insulin)
assert state_before[0] == state_after[0]
assert np.array_equal(state_before[1], state_after[1])
assert state_before[2:] == state_after[2:]
checks.update({"exact_schema": True, "input_and_spec_unchanged": True,
               "values_dtypes_index_and_order_preserved": True,
               "same_seed_reproducible": True, "different_seed_varies": True,
               "global_numpy_rng_unchanged": True})

for seed in range(1901, 1921):
    draw = module.generate(artificial, spec, seed)
    assert np.isfinite(draw.insulin).all() and (draw.insulin > 0).all()
checks["twenty_artificial_draws_finite_and_positive"] = True

p = spec["parameters"]
beta = math.log(6.05 / 4.29) / (28.96 - 21.07)
v1 = math.log1p((0.16 * math.sqrt(307) / 4.29) ** 2)
v2 = math.log1p((0.37 * math.sqrt(168) / 6.05) ** 2)
sigma = math.sqrt((306 * v1 + 167 * v2) / 473)
assert math.isclose(beta, p["bmi_log_slope"], rel_tol=1e-13)
assert math.isclose(sigma, p["residual_log_sd"], rel_tol=1e-13)
assert math.isclose(6.37 * 47.0 / 42.1, p["age_anchor_median_insulin"][-1], rel_tol=1e-13)
checks["source_quantity_transformations_reproduced"] = True

replicated = pd.DataFrame({"row_id": [f"repeat_{i}" for i in range(6000)],
                           "bmi": 23.01, "age": 44.5, "sex": 1})
logs = np.log(module.generate(replicated, spec, 2901).insulin.to_numpy())
assert abs(logs.mean() - math.log(6.03)) < 0.04
assert abs(logs.std(ddof=1) - sigma) < 0.04
assert np.unique(logs).size == len(logs)
checks["constant_covariates_retain_stochastic_variation"] = True
checks["artificial_log_moments_match_implemented_distribution"] = True

source_hashes = {}
for source in ledger["sources"]:
    path = HERE.parent / source["approved_path"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == source["sha256"]
    source_hashes[source["id"]] = digest
checks["all_six_approved_fulltext_hashes_match"] = True

report = {
    "status": "PASS", "scope": "Artificial inputs and source-quantity/hash checks only; no observed.csv or target outcomes read",
    "checks": checks,
    "artificial_constant_covariate_log_mean": float(logs.mean()),
    "artificial_constant_covariate_log_sd": float(logs.std(ddof=1)),
    "source_hashes": source_hashes,
    "limitations": "These checks verify implementation and provenance, not biological validity, assay transport, or prediction performance."
}
(HERE / "ARTIFICIAL_CHECKS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "checks": checks}, indent=2))
