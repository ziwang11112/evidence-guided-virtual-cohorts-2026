# Prospective isolated runtime repair

The first production-release software smoke dispatched five invented trials through the actual guarded WSL/bubblewrap path. All five stopped at import: SciPy was absent. No cohort table was produced. Those consumed software attempts and receipts remain in their original fixture ledger; they are not clinical attempts.

The task-specific Ubuntu-24.04 virtual environment received the binary `scipy==1.16.3` wheel with `--no-deps`; NumPy 2.4.5 and pandas 3.0.3 were preserved. The exact 35,676,692-byte cached wheel matched the SHA256 reported by pip. The acquisition ledger conservatively includes this payload within the existing total cap. Package-index/metadata traffic was not metered. `SCIPY_INSTALL_REPORT.json` and `DOWNLOAD_RECEIPT.json` preserve installation provenance. [Official pinned package](https://pypi.org/project/scipy/1.16.3/).

One separately versioned pure software check then invoked actual bubblewrap, imported the repaired dependencies, and obtained betainc(2,3,0.5)=0.6875 and inverse=0.5. It generated no cohort rows and did not rerun the five failed trials. Component testing on the host used SciPy 1.17.1; the isolated execution version is explicitly 1.16.3, not an identical environment claim.

`runtime_check.py` fingerprints the interpreter, virtual-environment configuration, bubblewrap, SciPy special extension, and every existing regular file listed in the NumPy/pandas/SciPy distribution inventories, including versioned native libraries. `RUNTIME_IDENTITY.json` is the prospective identity. An earlier partial inventory is retained as `RUNTIME_IDENTITY_INITIAL_PARTIAL.json`, but is not the release identity. `run_stage.py` verifies the full identity before consuming each clinical stage intent. This supplements the existing frozen executor's narrower runtime receipt without changing old code or old results.

These are procedural checks against the recorded environment. They do not authenticate a hostile host or certify scientific transport.
