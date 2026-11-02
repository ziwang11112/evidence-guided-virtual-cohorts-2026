# HAALSI official access checkpoint

2 November 2026. HAALSI is the fourth screened target family of the current
six-family campaign, following the [history-first check](HISTORY_PREFLIGHT.md).
It is a candidate, not an admitted cohort or a new scientific validation.

The [official baseline release](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/F5YHML)
is version 3.0. Its public description identifies a November 2014-November 2015
survey of 5,059 adults aged at least 40, sampled within the Agincourt surveillance
population in rural South Africa. The listed participant release has 1,933
variables. Anthropometry and point-of-care hemoglobin, glucose and lipids are
described. HbA1c and CRP appear as future-release plans in that description;
their availability in this actual version must not be assumed.

The official description also names an H3Africa/AWIGEN collaboration for a
laboratory subsample. Future evidence screening must check Agincourt/HAALSI and
AWI-Gen recruitment/site overlap explicitly. A differently titled AWI-Gen paper
is not automatically independent external generation evidence; the collaboration
description alone does not establish exactly which participants overlap.

## Actual access and downloads

The official site requires a custom data usage agreement and a guestbook with
real contact, affiliation, position and research-use information. The user
explicitly accepted this agreement and subsequently supplied the information
and authorized its entry. The official workflow was completed in wang Chrome;
no account, restricted-data application or alternate acquisition route was
used. Personal guestbook fields are excluded from this report and public export.

The agreement restricts use to research/statistical purposes, disallows
commercial use, identification and unauthorized redistribution, and includes
deletion, attribution, research-product reporting and error-reporting duties.
Any later reporting/contact action must follow the user's authorization; this
unit did not contact researchers. The original source files remain local.

| Official file | File DOI suffix | Saved bytes | Official MD5 matched |
|---|---|---:|---|
| HAALSI Baseline Codebook.pdf | 5WBCG6 | 1,740,530 | 57893c50d15dd0653e38ee126acdfa57 |
| HAALSI Baseline Survey and Variables.docx | IA1N9T | 194,943 | 898d6239a9e6a01dbd1c9c45f9d628cc |
| HAALSI_baseline_dataverse_14Apr2017.dta | MMQO8Q | 19,039,887 | e11a69121c7cee6726835d6106820104 |

All three belong to DOI `10.7910/DVN/F5YHML`, version 3.0. SHA256 hashes, paths,
browser route and budget accounting are in [HAALSI_ACCESS.json](HAALSI_ACCESS.json)
and the [acquisition ledger](../ACQUISITION_LEDGER.json). Local copies are not
double-counted as downloads. Saved bytes in this unit total 20,975,360; cumulative
metered acquisition is 253,785,516 bytes, leaving 270,502,484 bytes under the
unchanged 500 MiB cap. Browser traffic remains unmetered.

The first Accept action enabled the codebook preview rather than saving the
file; a download-event wait timed out. The subsequent Access File workflow
displayed the same populated guestbook, and its Accept action produced a
confirmed download event. The companion documentation and original Stata file
likewise completed through their official guestbooks. No failed response file or
duplicate download was saved.

## Exposure and remaining decision

The access-only search and official pages exposed sampling, release counts,
measurement descriptions and generic memory/cognition titles in search results.
They did not expose metabolic effect estimates. No clinical value, mean,
correlation or target analysis was read in this access unit. The
history audit found no positive recorded HAALSI use; it does not prove global
or model-pretraining non-exposure.

Definition-only content in the older 2016 PDF and the updated 14 April 2017
survey/variable document was subsequently reconciled. In the latter, orange denotes
confidentiality restrictions, grey denotes unavailability due to coding/cleaning,
and green directs readers to other variables. These distinctions must survive
extraction. Two document reviewers confirmed that the cleaned BMI/glucose fields
are present without unavailable/replacement colors; this justified obtaining one
original Stata file for schema, code, identifier and availability checks. Its
official metadata explicitly identify the checksum as **Original File MD5**;
the original format was selected rather than comparing that checksum to an
ingested tab-delimited conversion. Exact
measurements, analysis population, source applicability and independent-case
eligibility remain unapproved. This metadata review consumes no new original
empirical-study slot; the campaign remains at three of twelve such reviews.

The subsequent [schema audit](HAALSI_DATA_SCHEMA_AUDIT.json) and
[independent recomputation](HAALSI_INDEPENDENT_SCHEMA_REVIEW.md) are complete:
all 13 selected fields exist, 5,059 primary keys are unique/nonmissing, and
4,394 records have age/sex/BMI/glucose physically present. These counts do not
define final eligibility. Sex/flag code labels and tagged missingness were
verified without emitting continuous measurements, moments or clinical effects.
Next is independent external-evidence and scientific-use review, not another
download or an outcome-based choice of analyses.
