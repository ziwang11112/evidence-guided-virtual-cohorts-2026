"""Replay curated acceptance fixtures on private, immutable v1 development tables."""
import argparse
import hashlib
import json
import math
from pathlib import Path, PureWindowsPath
import sys

FIXTURES = Path(__file__).resolve().parent
UNIT = FIXTURES.parents[1]
sys.path.insert(0, str(UNIT))
from evidence_replay import core


# Fingerprints of the historical manifests, which themselves bind every table.
MANIFEST_HASHES = {
    "d01": {"trial": "8c8c390e03818d95a37cd51ad51a53654c62ca543ac4ff727623e442027fe9f2",
            "final": "f150dd2aac762f535d6b4488047c73454d5c21bba0ee451f25c40b54f80ad391"},
    "d02": {"trial": "be60b17310a0d0df3be4ede3505c23f69dbe54fabe3fcb277dea2822dcac0169",
            "final": "91832e766fbea51234ae171904e9bffcfe829ea8429f3824ccbeedd9946388c5"},
}
EXPECTED = {
    "d01": {
        "run": "d01", "scenarios": ["primary", "concordant", "discordant"],
        "status_counts": {"outside_precision": 1, "within_precision": 7, "descriptive_only": 22, "unresolved": 1},
        "outside": ["overall_ferritin_gm"], "unresolved": ["adjusted_iron_anemia_or"],
        "values": {"overall_ferritin_gm": 17.3086977022, "overall_hb_gm": 129.9,
                   "severe_ferritin_gm": 1.3, "middle_ferritin_gm": 5.9, "higher_ferritin_gm": 22.3,
                   "crude_iron_anemia_or": 6.6516623047},
    },
    "d02": {
        "run": "d02", "scenarios": ["primary"], "status_counts": {"within_precision": 11, "outside_precision": 3},
        "outside": ["male_ols_slope", "male_ols_intercept", "female_ols_intercept"], "unresolved": [],
        "values": {"male_ols_slope": .80, "male_ols_intercept": -.20, "female_ols_intercept": -.204,
                   "female_ols_slope": .84},
    },
    "d02_independent_r_squared": {
        "run": "d02", "scenarios": ["primary"], "status_counts": {"outside_precision": 2},
        "outside": ["male_r_squared", "female_r_squared"], "unresolved": [],
        "values": {"male_r_squared": 92.16, "female_r_squared": 92.16},
    },
}


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(condition, reason):
    if not condition:
        raise ValueError(reason)


def bound_manifest(root, mode):
    path = root / f"{mode}_manifest.json"
    verify(sha(path) == MANIFEST_HASHES[root.name][mode], f"Historical manifest changed: {path.name}")
    manifest = load(path)
    # Allow an intact archive to be moved. Only translate the prefix after its original
    # manifest bytes have been verified. core.replay then rechecks paths and row hashes.
    stage = "execution_" + mode
    for run in manifest["runs"]:
        parts = PureWindowsPath(run["table"]).parts
        verify(parts.count(stage) == 1, "Expected a single execution directory")
        suffix = parts[parts.index(stage):]
        verify(suffix[-1] == "generated.csv" and ".." not in suffix, "Invalid historical table path")
        run["table"] = str(root.joinpath(*suffix))
    return manifest


def run_fixture(name, private):
    expected = EXPECTED[name]
    root = private / expected["run"]
    path = FIXTURES / (name + ".json")
    evidence = load(path)
    candidate = load(root / "build.json")
    verify(load(root / "review.json").get("action") == "keep", "Historical author decision changed")
    references = {item["id"]: item["reference"] for item in evidence["evidence_checks"]}
    result = {"run": root.name, "fixture_sha256": sha(path),
              "scope": "independent_omissions_only" if name.endswith("_r_squared") else "retrospective_author_selected",
              "candidate_sha256": core.digest(candidate), "source_inventory_count": len(references), "stages": {}}
    for mode in ("trial", "final"):
        manifest = bound_manifest(root, mode)
        report = core.replay(root, mode, evidence, candidate, manifest)
        seeds = [823017] if mode == "trial" else [823031, 823039, 823043]
        runs = report["runs"]
        required = {(s, seed) for s in expected["scenarios"] for seed in seeds}
        actual = {(run["scenario"], run["seed"]) for run in runs}
        verify(actual == required and len(runs) == len(required), "Duplicate, altered or missing scenario/seed")
        values = {key: [] for key in expected["values"]}
        for run in runs:
            verify(run["status"] == "success", "Missing frozen virtual table")
            verify(run["counts"] == expected["status_counts"], f"{name}: historical status counts differ")
            checks = {item["id"]: item for item in run["checks"]}
            verify(set(checks) == set(references), f"{name}: lost evidence entry")
            for status, tag in [("outside_precision", "outside"), ("unresolved", "unresolved")]:
                ids = {k for k, v in checks.items() if v["status"] == status}
                verify(ids == set(expected[tag]), f"{name}: {status} items differ")
            for key, target in expected["values"].items():
                value = checks[key]["value"]
                verify(math.isclose(value, target, rel_tol=0, abs_tol=1e-8), f"{name}/{key}: estimate changed")
                values[key].append(value)
        result["stages"][mode] = {
            "historical_manifest_sha256": MANIFEST_HASHES[root.name][mode],
            "verified_tables": len(runs), "scenarios": expected["scenarios"], "seeds": seeds,
            "status_counts_per_table": expected["status_counts"], "outside_precision_ids": expected["outside"],
            "unresolved_ids": expected["unresolved"],
            "checked_aggregate_ranges": {
                key: {"reference": references[key], "min": min(series), "max": max(series)}
                for key, series in values.items()},
        }
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--private", type=Path, default=UNIT / "private",
                     help="Historical private archive containing the d01 and d02 run directories")
    cli.add_argument("--output", type=Path, help="Write a new aggregate-only report, or verify its existing bytes")
    options = cli.parse_args()
    computed = {name: run_fixture(name, options.private.resolve()) for name in EXPECTED}
    report = {"status": "passed",
              "scope": "Software acceptance on frozen development outputs using retrospective evaluator-authored fixtures. No new authors or model calls.",
              "distinct_trial_tables": 4, "distinct_final_tables": 12,
              "author_selected": [computed["d01"], computed["d02"]],
              "independent_omissions_on_same_lung_tables": computed["d02_independent_r_squared"]}
    data = (json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf8")
    if options.output:
        if options.output.exists():
            verify(options.output.read_bytes() == data, "Existing acceptance report differs")
        else:
            with options.output.open("xb") as stream:
                stream.write(data)
    print("Passed on 4 distinct historical trial tables and 12 final tables. Extra two R-squared checks used the same lung tables.")


if __name__ == "__main__":
    main()
