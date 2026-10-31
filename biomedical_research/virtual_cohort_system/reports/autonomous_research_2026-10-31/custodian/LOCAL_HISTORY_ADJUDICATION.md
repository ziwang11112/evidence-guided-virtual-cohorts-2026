# Append-only local-history adjudication

Date: 2026-10-31. This addendum preserves the original failed-download artifacts and corrects the scope of their interpretation. The failed attempts establish that this pass acquired no new workbook; they do not establish that the candidate was absent from the wider project.

## File identity

An existing project file was found at:

`D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/cross_study_virtual_cohort_pilot_2026-10-25/data/target_reserved/nagala/Data_set_Int_J_Obesity.xlsx`

Only filesystem length and cryptographic hashes were read. The workbook was not opened with an Excel reader, its archive/schema was not inspected, and no participant data or derived quantities were accessed.

| Identity check | Local observation | Official deposit reference | Adjudication |
|---|---|---|---|
| File size | 3,255,571 bytes | 3,255,571 bytes | Exact match |
| MD5 | `47edfb147078657a0eecfff7f9364532` | `47edfb147078657a0eecfff7f9364532` | Exact match |
| SHA-256 | `671359aea2019c848f969395f88e57f888eaba8463ea0351bcda8f1c947f5523` | Not supplied by the frozen official metadata | Local content fingerprint only |

The local file matches the official Dryad file 76808, version 22266, DOI `10.5061/dryad.8q0p192`, on both published size and MD5. This supports identity with the same deposited workbook despite its underscore-normalized local filename. No new download or copy into the current case was made.

## Prior target role

Only restricted narrative/protocol excerpts were inspected, with field-detail columns excluded and numerical content suppressed during extraction:

- The earlier `PROTOCOL.md`, line 23, names its third table column **Reserved target**; line 25 assigns **NAGALA, Japan** to that column for the population-transport case. Source-study and reserved-target roles are distinct in that table.
- The earlier `CASE_POPULATION_AUDIT.md`, line 8, records the exact reserved workbook path.
- Its line 15 explicitly assigns NAGALA a held-out target role; line 58 is headed **NAGALA Japanese cohort: verified held-out target**.

These inspected records establish prior project selection and reservation of this same NAGALA workbook as a held-out target. The controller additionally reports an associated prior evaluated target. No evaluation artifacts were opened here, so the fact or extent of executed evaluation is not independently adjudicated by this metadata-only addendum. Prior target reservation and file identity are sufficient to reject any claim that this is a newly discovered, project-fresh candidate.

## Interpretation and boundary

The initial absence of a project-wide freshness audit was an implementation/workflow gap. This is a local-history correction, not confirmation of fresh-target admissibility, a new schema admission, or a semantic-readiness finding. Original access failures remain valid as recorded; their artifacts are unchanged. This addendum does not authorize opening or reusing the existing workbook. No schema, patient rows, target results, numerical target summaries, analysis, generation, uncertainty calculation, or `STATE.json` mutation occurred in this follow-up.
