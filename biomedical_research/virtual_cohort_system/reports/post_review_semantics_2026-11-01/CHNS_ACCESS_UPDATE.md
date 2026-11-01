# CHNS access update: Chrome metadata verification

1 November 2026. This updates, rather than replaces, the 31 October access checkpoint. The user-requested wang Chrome extension profile successfully opened the official UNC Dataverse collection. The earlier web-reader denial is not a current browser-access blocker.

## Verified observations

| Item | Observed metadata |
|---|---|
| Collection | [China Health and Nutrition Survey Dataverse](https://dataverse.unc.edu/dataverse/chns), six datasets in the displayed collection. This is the existing CHNS candidate family, not six new candidates. |
| Biomarker release | [DOI 10.15139/S3/GQ9GPP](https://dataverse.unc.edu/dataset.xhtml?persistentId=doi:10.15139/S3/GQ9GPP), Version 1.0, published 10 May 2019. |
| Biomarker file | [biomarker_09.sas7bdat, file ID 7505013, version 1.0](https://dataverse.unc.edu/file.xhtml?fileId=7505013&version=1.0). SAS System file; displayed size 3.7 MB. Exact byte size and local SHA256 are not yet known. |
| Publisher checksum | Displayed MD5 `60945adcb840138a559836c0b33e2be0`. This is publisher metadata, not a hash independently computed from acquired bytes. |
| Biomarker terms | Dataset Terms tab displays CC0 1.0, with a request for proper data citation. File Access menu explicitly says Public and offers SAS System download. No download or agreement acceptance was performed. |
| Companion individual release | [DOI 10.15139/S3/9PQ5KV](https://dataverse.unc.edu/dataset.xhtml?persistentId=doi:10.15139/S3/9PQ5KV), Version 1.0. Directory displays 54 files, comprising data and documentation. This is not an eligible sample count. |
| Companion terms | Custom terms, not CC0. The page permits analysis use subject to safeguards, prohibits identifying/contacting participants, communities or providers, and specifies citation/acknowledgment requirements. Full terms must be retained locally when acquisition is performed; do not assume the biomarker license covers companion files. |

No login, contact message, controlled-data application, patient-file download, source-paper audit or target effect calculation occurred. No fourth family was introduced. The prior relationship-exposure log still applies. No claim of global blinding or untouched CHNS literature is made.

## Remaining work

1. Identify the necessary covariate/measurement files and their versioned IDs, sizes and access conditions from the visible directory. The first directory page alone does not establish the correct anthropometry/age/sex inputs.
2. Review official schema and assay documents without extracting participant distributions or target analysis answers. Preserve central/field glucose distinctions and serum/plasma terminology from the prior checkpoint.
3. Before any bounded acquisition, check existing local copies, record an allowlist and transfer ledger, and preserve the 200 MiB per-file / 500 MiB incremental cap. Only processed data needed for the admitted analysis are in scope. Row-level files remain local and unavailable to the generation context.
4. Use the remaining six-original-study audit quota to assess independent external evidence. Define scientific uses, source conditions, measurement mappings, uncertainty and exposure before freezing F2. Public accessibility is necessary but does not establish a scientifically admissible case.

One attempted detail navigation was aborted before dispatch; a later verified navigation succeeded. Numeric accessibility IDs also became stale during directory interactions. These were interface issues, not evidence that the dataset is unavailable; resume via fresh visible state or the documented Chrome DOM locator API. Do not silently switch to Windows desktop input.
