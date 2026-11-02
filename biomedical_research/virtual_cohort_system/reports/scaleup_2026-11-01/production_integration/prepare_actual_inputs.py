"""One-time permitted metadata assembly; no constructors, candidates or runs."""
from datetime import datetime, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
import bundle_assembly as assembly
from cohort_harness import lifecycle


def main():
    destination = HERE / "prepared_inputs"
    if destination.exists():
        raise ValueError("Input assembly already reserved; no overwrite or reset")
    packages = {case: assembly.load_package(case) for case in ("K01", "K02")}
    # Registration is scoped to the exact already-reviewed selected artifacts.
    # It does not assert case release, exact source replay or transport validity.
    original_reviews = {
        "K01": assembly.SCALE / "case_k01/CONTRACT_INDEPENDENT_REVIEW.md",
        "K02": assembly.SCALE / "case_k02/assembly/INDEPENDENT_REVIEW.md",
    }
    started = datetime.now(timezone.utc).isoformat()
    destination.mkdir()
    results = []
    for case, package in packages.items():
        review = {"curator_id": "/root", "reviewed_utc": started,
                  "reason": "Register the exact selected source artifacts after the retained independent metadata review "
                            + lifecycle.sha256(original_reviews[case])
                            + "; declared context/approximation limits retained; no model or clinical execution released",
                  "package_sha256": assembly.package_digest(package)}
        for constructor in assembly.CONSTRUCTORS:
            folder = destination / case / constructor
            receipt = assembly.prepare_bundle(case, constructor, folder, review)
            assembly.verify_bundle_inputs(folder)
            results.append({"case": case, "constructor": constructor, "bundle": folder.relative_to(HERE).as_posix(),
                            "input_receipt_sha256": lifecycle.sha256(folder / "INPUT_ASSEMBLY.json"),
                            "package_sha256": receipt["package_sha256"], "input_file_count": len(receipt["files"])})
    result = {"schema_version": 1, "kind": "actual_reviewed_metadata_assembly", "created_utc": started,
              "producer": "/root", "assembler_sha256": lifecycle.sha256(assembly.__file__),
              "script_sha256": lifecycle.sha256(__file__), "bundles": results,
              "source_artifacts_registered": "K01 three source IDs, K02 seven source-context IDs; not independent-study counts",
              "clinical_constructions": 0, "parameter_fits": 0, "generated_tables": 0, "target_rows_read": 0,
              "global_release": False, "scope": "Prepared inputs only; source registration does not authorize execution"}
    path = HERE / "INPUT_ASSEMBLY_RESULTS.json"
    with path.open("xb") as handle:
        handle.write(assembly.encoded(result))
    print({"metadata_bundles": len(results), "clinical_constructions": 0, "target_rows_read": 0})


if __name__ == "__main__":
    main()
