"""Prepare an invented cross-study fixture, without writing any generator."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

def write(path, value):
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")

def prepare(destination):
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=False)
    (root / "sources").mkdir()
    (root / "candidates").mkdir()
    task = {
        "schema_version": 1, "task_id": "m2-invented-study-context-execution",
        "mode": "enrichment", "population": "128 invented records for execution and interface testing only. No patients or hidden biological answers.",
        "row_id": "record_id", "n_rows": 128,
        "columns": [
            {"name": "record_id", "kind": "string", "unit": "identifier", "role": "identifier", "nullable": False},
            {"name": "x", "kind": "number", "unit": "x_unit", "role": "observed", "nullable": False, "minimum": 0, "maximum": 2},
            {"name": "group", "kind": "integer", "unit": "0_or_1", "role": "observed", "nullable": False, "minimum": 0, "maximum": 1},
            {"name": "y", "kind": "number", "unit": "u", "role": "generated", "nullable": False, "minimum": 0}
        ],
        "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["NHANES"],
                               "allowed_tools": ["local_fixture_only", "literature.search", "literature.fetch",
                                                 "literature.list-supplements", "literature.fetch-supplement"]},
        "budget": {"source_queries": 2, "source_downloads": 1, "revisions": 1}
    }
    write(root / "task.json", task)
    observed = pd.DataFrame({"record_id": [f"fixture_{i:03d}" for i in range(128)],
                             "x": np.tile(np.linspace(0, 2, 64), 2),
                             "group": np.repeat([0, 1], 64)})
    observed.to_csv(root / "observed.csv", index=False)
    sources = [
        ("T1", "fictional-study-a.txt", """ARTIFICIAL SOURCE A — invented execution fixture, not a published paper.
Population: group=0 only. x measured exactly in x_unit.
Outcome y is nonnegative, measured in unit u.
Three distinct x strata report arithmetic outcome mean and within-stratum individual SD, not SE:
x=0: mean 2 u, SD 1 u.
x=1: mean 3 u, SD 1.5 u.
x=2: mean 4 u, SD 2 u.
No distributional family, interpolation law, tail shape or target individual outcome is supplied.
Values are fixture constraints, not clinical evidence. A synthetic generator may require additional assumptions.
"""),
        ("T2", "fictional-study-b.txt", """ARTIFICIAL SOURCE B — invented execution fixture, not a published paper.
Population: group=1 only. x measured exactly in x_unit.
Outcome instrument reports z in unit du. Measurement calibration defines z=10*y, with y in u.
Three x strata report arithmetic mean and within-stratum individual SD of z, not SE:
x=0: mean 25 du, SD 12.5 du.
x=1: mean 37.5 du, SD 18.75 du.
x=2: mean 50 du, SD 25 du.
These are distinct fictional records, with no overlap with source A.
No outcome distribution or target individual y is supplied. Cross-study transfer to the invented target is an assumption.
""")
    ]
    registry = {"artifacts": []}
    for source_id, name, content in sources:
        p = root / "sources" / name
        p.write_text(content, encoding="utf-8")
        registry["artifacts"].append({"source_id":source_id, "path":"sources/"+name,
                                     "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                                     "origin":"fixture", "screening":"approved"})
    write(root / "registry.json", registry)
    (root / "TASK_BRIEF.md").write_text("""# Controlled Agent execution task
This is an invented mechanical fixture, not a biomedical result or a method-superiority test.
Use the supplied evidence-cohort-generation skill and current harness interface.
Choose the generator family, structure, parameters and scientific assumptions yourself from the approved fictional sources.
Submit a PROGRAM candidate named agent_initial. Do not execute the generator locally; the controller will run its frozen code in the isolated execution adapter.
Preserve every observed value. Provide a positive stochastic outcome if justified; seed handling must be reproducible if used.
No hidden reference outcomes exist in this fixture. Do not inspect prior cases, other candidates, custodian directories or framework tests.
You may use syntax/interface validation and record exactly what checks ran. Before actual execution, do not claim data generation passed.
Treat source A/B values as artificial fixture evidence, not as real publications. Use origin=fixture registration and fixture_only checks.
Retain all relevant study conditions and distinguish units of z versus y; do not silently convert SD to SE or pretend missing distributions are known.
Do not create source_tables or a source-check report unless the table was actually obtained by a permitted procedure; this task tests execution first.
The declared literature tools are available for a separate tool-transport smoke check, not to establish real-world meaning of the invented variables. No literature retrieval is required for the candidate.
""", encoding="utf-8")
    return root

if __name__ == "__main__":
    import sys
    print(prepare(sys.argv[1]))

