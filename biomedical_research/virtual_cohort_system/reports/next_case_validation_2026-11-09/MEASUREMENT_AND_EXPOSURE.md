# Measurement verification and exposure boundary

Host audit, 2026-11-09. This note contains no candidate clinical measurements or fitted target results.

The retained official PNS dictionary (SHA256 5aa4a3685fa2b1a9b8aa3739e3da2b83cf72fdb0affe988f2b6cc4442a6833c0) defines final SBP W00407 and DBP W00408 in mmHg, with documented admissibility ranges and error/missing codes. The actual header inventory uses lowercase z004/z005 for anthropometry. Dictionary mapping uses aligned A:D entries, not the unrelated column-E list. Independent task audit supplies the precise field/row locations.

The official manual was obtained from the PNS Fiocruz domain; its actual bytes/hash are in METADATA_DOWNLOAD_RECEIPT.json. Pages16/19–23 were inspected. It specifies G-TECH MA100; seated rest at least5minutes; three measurements at two-minute intervals; generally the leftarm, supported at heart height. The manual describes each measurement and communicating the last reading to the participant. That is **not evidence that W00407/W00408 equal the last reading** or the mean of the last two. Final release aggregation remains undocumented in inspected sources. No conversion or averaging is invented.

The official 2013 IBGE launch search description places BP and anthropometry in the baseline selected-adult interview; the retained laboratory-page documentation places laboratory collection in2014–15. The target uses baseline C008 age; it does not invent later BP dates. The later laboratory-substudy release/weight restricts interpretation. The laboratory-substudy completeness and weighting target is stated in the protocol; no national-design inference is claimed without the necessary design information.

## Incidental exposure record

During metadata searches for the measurement manual and device, the search service returned a snippet from the official national-results PDF `https://biblioteca.ibge.gov.br/visualizacao/livros/liv94522.pdf`. The snippet included broad age/sex BP prevalence information. The host did **not** open that PDF. Those values are not copied into this note or author inputs and are excluded from generation evidence. This exposure concerns published national prevalence, not the candidate lab-subset BMI-adjusted slopes or residual dependence. It prevents a globally blind/new-cohort claim; HISTORY_AUDIT gives the qualified new-task conclusion.

Search queries were `site.pns.icict.fiocruz.br "pressão" "manual" 2013` and `site.ibge.gov.br PNS 2013 manual antropometria pressão arterial Omron HEM 7200`. The second query's guessed device was only a search lead; verified manual specifies G-TECH MA100. No quantitative source constraint is taken from a search snippet.

## Retrieval environment

wang Chrome inventory returned browsers=[] and “Local browser use is disabled in Work settings.” No desktop fallback was used. Local retained documentation, public web search and public static metadata retrieval were used and are labelled accordingly. New measurement-manual download:4,810,356bytes; no new patient data downloaded. Browser/search traffic is not byte-metered and is not represented as zero.

## Separation

Authors may receive the neutral target description and verified measurement protocol. They must not read this host exposure discussion, historical reports, clinical source files or candidate target results. Source agents admit independent original studies, with study conditions and unresolved transfer assumptions. Shared paper/statistic families are not independent confirmations. All clinical/generated row tables and third-party fulltexts remain local.
