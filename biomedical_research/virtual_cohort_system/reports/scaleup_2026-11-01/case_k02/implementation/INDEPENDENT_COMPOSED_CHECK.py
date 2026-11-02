"""One small invented interface check; writes no row data or clinical candidate.

Run once by the independent reviewer. The only numeric constraints come from
test_statistical_reference.invented, never a source packet or measured target.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SCALEUP = HERE.parents[1]
PROJECT = SCALEUP.parents[1]
for directory in (PROJECT, HERE, SCALEUP / "bridge_units", SCALEUP / "analysis"):
    sys.path.insert(0, str(directory))

import statistical_reference as reference
from test_statistical_reference import invented
from test_generated_validity import sample as validity_fixture
from generated_validity import validate_generated_release
from unit_conversion import convert_frame, frame_digest
from k02_analysis import analyze_frame


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report_path = HERE / "INDEPENDENT_COMPOSED_RESULT.json"
    if report_path.exists():
        raise RuntimeError("Existing independent result; this check must not be silently repeated")
    n_rows, seed = 24, 20261102
    model = reference.fit_reference(invented.__wrapped__())
    _, task = validity_fixture.__wrapped__()
    task["task_id"] = "invented-k02-composed-interface-24"
    task["n_rows"] = n_rows
    frame = reference.sample(model["parameters"], reference.TARGET_CONTEXT_ID, n_rows, seed)
    before = frame.copy(deep=True)
    guard = validate_generated_release(frame, task)
    units = HERE.parent / "unit_mapping"
    manifest = json.loads((units / "APPROVED_MANIFEST.json").read_text(encoding="utf-8"))
    input_contract = json.loads((units / "INPUT_CONTRACT.json").read_text(encoding="utf-8"))
    output_contract = json.loads((units / "OUTPUT_CONTRACT.json").read_text(encoding="utf-8"))
    mapped, receipt = convert_frame(
        frame, manifest, input_contract=input_contract, output_contract=output_contract,
        expected_input_sha256=frame_digest(frame),
        caller_binding={"kind": "invented_interface_check_only", "n_rows": n_rows,
                        "seed": seed, "execution_authenticated": False,
                        "actual_source_values_used": False, "clinical_candidate_created": False},
    )
    pd.testing.assert_frame_equal(frame, before)
    identity = ["id", "age", "sex", "bmi"]
    pd.testing.assert_frame_equal(frame[identity], mapped[identity])
    unit_differences = {}
    for name in ("total_cholesterol", "hdl_cholesterol"):
        independent_values = np.array([float(value) * 38.67 for value in frame[name]])
        unit_differences[name] = float(np.max(np.abs(independent_values - mapped[name].to_numpy())))
        assert unit_differences[name] == 0
    result = analyze_frame(mapped, role="generated")
    assert result["status"] == "complete"
    assert result["selection"]["input_rows"] == result["selection"]["eligible_rows"] == n_rows
    assert result["selection"]["excluded_rows"] == 0
    assert not result["metric_denominators"]
    assert all(value["interval"]["standard_error"] is None for value in result["estimands"].values())
    assert result["release_status"] == "prospective_not_released"
    x = np.column_stack((np.ones(n_rows), (mapped["age"].to_numpy() - 50) / 10,
                         mapped["sex"].eq("F").to_numpy(dtype=float),
                         (mapped["bmi"].to_numpy() - 25) / 5))
    q, r = np.linalg.qr(x, mode="reduced")
    assert np.linalg.matrix_rank(r) == 4
    differences, residuals = {}, {}
    for endpoint, column in (("K02-HDL-BMI", "hdl_cholesterol"),
                             ("K02-TC-BMI", "total_cholesterol")):
        y = mapped[column].to_numpy()
        beta = np.linalg.solve(r, q.T @ y)
        residuals[column] = y - x @ beta
        differences[endpoint] = abs(float(beta[3]) - result["estimands"][endpoint]["estimate"])
    a = residuals["total_cholesterol"]
    b = residuals["hdl_cholesterol"]
    a, b = a - a.mean(), b - b.mean()
    independent_correlation = float(np.sum(a * b) / np.sqrt(np.sum(a * a) * np.sum(b * b)))
    differences["K02-LIPID-RESIDUAL"] = abs(independent_correlation - result["estimands"]["K02-LIPID-RESIDUAL"]["estimate"])
    assert all(value < 1e-10 for value in differences.values())
    commitments = {
        str(path.relative_to(SCALEUP)).replace("\\", "/"): file_hash(path)
        for path in (HERE / "statistical_reference.py", HERE / "test_statistical_reference.py",
                     HERE / "generated_validity.py", HERE / "test_generated_validity.py",
                     HERE / "INDEPENDENT_COMPOSED_CHECK.py", SCALEUP / "bridge_units/unit_conversion.py",
                     SCALEUP / "analysis/k02_analysis.py", units / "APPROVED_MANIFEST.json",
                     units / "INPUT_CONTRACT.json", units / "OUTPUT_CONTRACT.json")
    }
    report = {
        "reviewer_id": "/root/context_bridge_review", "status": "passed",
        "scope": "one invented in-memory interface check; no scientific performance inference",
        "invented_constraints_only": True, "actual_source_or_target_read": False,
        "clinical_candidate_created": False, "isolated_execution_performed": False,
        "retained_row_data": False, "sample_calls": 1, "n_rows": n_rows, "seed": seed,
        "context_id": reference.TARGET_CONTEXT_ID, "guard": guard,
        "fit_normalized_constraints_sha256": model["provenance"]["normalized_constraints_sha256"],
        "fit_parameters_sha256": model["provenance"]["parameters_sha256"],
        "conversion_receipt": receipt, "unit_maximum_absolute_differences": unit_differences,
        "analysis_status": result["status"], "analysis_rows": result["selection"],
        "analysis_design_rank": result["design"]["rank"],
        "analysis_generated_standard_errors_emitted": False,
        "independent_QR_estimate_absolute_differences": differences,
        "estimate_comparison_tolerance": 1e-10, "case_or_global_release_authorized": False,
        "file_sha256": commitments,
    }
    with report_path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status": report["status"], "n_rows": n_rows, "seed": seed,
                      "unit_discrepancies": unit_differences, "QR_discrepancies": differences,
                      "result_sha256": file_hash(report_path)}, sort_keys=True))


if __name__ == "__main__":
    main()
