# Technical decoder amendment, after the M13-B freeze

Root authorized this separate repair after the first acquisition's quality checks exposed a decoder defect. The original 19-file freeze and original `custodian/acquisition/` files stay unchanged. This script makes no network requests and changes no scientific rules, models, parameters or estimands.

Pandas 3.0.3 `read_sas(format="xport")` decoded 550 true zero examination weights as the exact positive number `2**-260`. Installed pyreadstat 1.3.7 decoded them as zero; every nonzero weight and SEQN agreed. This defect caused the first full design frame to include 550 interview-only records despite the frozen positive-weight rule. The repair uses the independent reader, not a chosen small-weight cutoff.

`repair.py` verifies the original freeze/authorization, original raw-file and output hashes, reads only the required columns from the preserved CDC XPT files with pyreadstat, and asserts that every difference from pandas in those columns is exactly its zero-decoding defect. Missingness, row keys, schemas and all nonzero numeric values must match. It then calls the unchanged frozen `prep.build_frames` and writes `custodian/acquisition_corrected/` with new opaque IDs, corrected private frame, covariate-only input, quality report and a technical amendment binding the script, package versions, original/raw/derived hashes and decoder comparison.

Only aggregate technical checks are logged. No participant outcome values or associations are printed. Corrected outputs remain local. Independent audit must approve the correction before any generator execution.

Execution requires the original root manifest hash and authorization plus an explicit technical-repair flag:

```powershell
python work/m13b/custodian_repair_v1/repair.py --freeze-manifest work/m13b/preaccess_freeze.json --freeze-sha256 bdf2503726d4f7f5c2ab2093e7e9bcdbb4da0e11cc74d847fb215c9205bd5c60 --authorization work/m13b/target_access_authorization.json --authorize-technical-decoder-repair
```
