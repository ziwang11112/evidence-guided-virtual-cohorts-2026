"""Exact input-only copies to a short workspace path supported by Windows/WSL."""
from datetime import datetime, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
import bundle_assembly as assembly
from cohort_harness import lifecycle


def main():
    workspace = assembly.PROJECT.parents[1]
    destination = workspace / "evcA"
    if destination.exists():
        raise ValueError("Execution input root exists; no overwrite or budget reset")
    source_result = lifecycle.read_json(HERE / "INPUT_ASSEMBLY_RESULTS.json")
    for entry in source_result["bundles"]:
        source = HERE / entry["bundle"]
        assembly.verify_bundle_inputs(source)
        if lifecycle.sha256(source / "INPUT_ASSEMBLY.json") != entry["input_receipt_sha256"]:
            raise ValueError("Original input assembly receipt changed")
    destination.mkdir()
    outputs = []
    longest = 0
    for entry in source_result["bundles"]:
        source = HERE / entry["bundle"]
        target = destination / entry["case"] / entry["constructor"]
        receipt = lifecycle.read_json(source / "INPUT_ASSEMBLY.json")
        for relative in [*receipt["files"], "INPUT_ASSEMBLY.json"]:
            src = lifecycle._path(source, relative)
            dst = target.joinpath(*lifecycle.safe_relative(relative))
            dst.parent.mkdir(parents=True, exist_ok=True)
            with dst.open("xb") as handle:
                handle.write(src.read_bytes())
            if lifecycle.sha256(dst) != lifecycle.sha256(src):
                raise ValueError("Input copy mismatch")
        assembly.verify_bundle_inputs(target)
        suffix = "context_bridge_v1/initial/contexts/source_ayele_dire_dawa_2017/bundle/executions/K01_A01_initial_source_ayele_dire_dawa_2017/input/model_spec.json"
        length = len(str(target / suffix))
        if length >= 240:
            raise ValueError("Insufficient ordinary Windows path headroom")
        longest = max(longest, length)
        outputs.append({"case": entry["case"], "constructor": entry["constructor"],
                        "workspace_relative_bundle": target.relative_to(workspace).as_posix(),
                        "input_receipt_sha256": entry["input_receipt_sha256"]})
    result = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
              "script_sha256": lifecycle.sha256(__file__), "input_assembly_sha256": lifecycle.sha256(HERE / "INPUT_ASSEMBLY_RESULTS.json"),
              "bundles": outputs, "representative_deep_path_characters": longest,
              "exact_input_bytes_preserved": True, "source_inputs_only": True,
              "clinical_execution_released": False, "generated_tables": 0, "target_data_reads": 0,
              "reason": "Prepared metadata tree would produce a 298-character child path; ordinary short paths avoid unsupported extended-path runtime conversion"}
    with (HERE / "EXECUTION_INPUT_LOCATIONS.json").open("xb") as handle:
        handle.write(assembly.encoded(result))
    print({"metadata_bundle_copies": len(outputs), "representative_deep_path_characters": longest, "generated_tables": 0})


if __name__ == "__main__":
    main()
