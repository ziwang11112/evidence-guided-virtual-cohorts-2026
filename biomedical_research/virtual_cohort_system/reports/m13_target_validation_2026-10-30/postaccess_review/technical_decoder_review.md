# Post-acquisition technical decoder review

30 October 2026. Reviewer: `/root/m13b_audit`. This review occurred after acquisition and before generator execution or outcome analysis. The original pre-access commitment and acquisition are preserved. Nothing in the original 19 frozen files, scientific candidates, protocol or evaluator was changed.

**Confirmed defect:** pandas 3.0.3 decodes an all-zero IBM double in these XPORT fields as `2^-260 = 5.397605346934028e-79`. Applying the already frozen rule `WTMEC2YR > 0` then incorrectly retained zero-weight DEMO records. This is a parser error, not a reason to select a small-weight threshold.

`weight_decode_review.py` reads header metadata and seeks directly to the eight WTMEC2YR bytes for each DEMO observation. Its independent conversion implements `sign × integer_mantissa × 2^(4(exponent−64)−56)`, following the IBM format in the [SAS XPORT specification](https://support.sas.com/techsup/technote/ts140.pdf). It compares those results against pyreadstat 1.3.7 restricted to WTMEC2YR and the installed pandas conversion function. It does not read DXA files or participant outcome values.

All 13 checks pass. Of 9,254 weight fields, exactly 550 consist of eight zero bytes. The independent formula and ReadStat decode all 550 as zero; pandas maps them to `2^-260`. Every remaining weight agrees exactly across all three calculations. The source DEMO SHA256 is `c0b46e0345ea19404928656277c8b0d10b0cca348a9b2fe4fc3c67e8b7ee73ec`.

The separately versioned, root-authorized repair uses pyreadstat 1.3.7 for the required columns, then calls the unchanged frozen `build_frames`. It verifies original input/output hashes and allows only the demonstrated exact-zero decoding discrepancies. It adds no threshold, eligibility rule, model parameter, missingness rule or scientific analysis. The repair's aggregate comparison also records 357 corrected zero ages; those age-zero observations are outside the frozen adult domain. Required BMI and DXA fields have no reader discrepancies according to the custody comparison; the reviewer did not inspect their outcome values.

`correction_binding_review.py` independently passed 30 checks. Its main full-frame read uses an explicit whitelist excluding DXDTOPF; a separately root-authorized endpoint-only read computes presence, finiteness and physical-support masks. It verifies:

- all 19 pre-access hashes and all original raw/output hashes remain unchanged;
- corrected outputs match the technical amendment and unchanged transformation hashes;
- the corrected 8,704-record frame matches the independently read positive-weight/design rows exactly, with 15 strata and 30 nested PSUs;
- the original and corrected generator inputs contain exactly the same 842 participants and identical permitted numeric covariates, after comparison through custody SEQN mappings;
- every selected row satisfies the frozen age, sex, race, BMI and scan conditions, with 612 primary and 230 extension rows;
- all four deployment freezes preserve the original generator/specification identities and bind the corrected permitted inputs.

The independent Boolean endpoint check confirms physical integrity of every available endpoint and exact ordered equality between the complete frozen-domain mask and generator-input IDs, including the disjoint 612/230 partition. No endpoint magnitudes, association or distribution statistic were exposed or analyzed. The unchanged frozen transformation and the exact original/corrected participant-set comparison provide the other domain-preservation checks.

The accepted repair script SHA256 is `60748debd229f5ff4b444837b44c5f69b403ca1cc1749f75b53341b48c62e4bd`; corrected observed-input SHA256 is `62e137f9f1b9daa6af33ec3a79919fee8dfa735c4b750ce64e77b8eeec3e59c5`. Machine-readable evidence is in `weight_decode_review.json` and `correction_binding_review.json`. An initial review-script header assertion was adjusted for SAS's padded `OBS` header, and NumPy Boolean serialization was corrected; neither preparation error altered any acquired or frozen artifact.

This correction restores the already declared positive-MEC-weight frame. It is a transparent technical amendment made before generation and outcome analysis, not a candidate revision or target-informed scientific adjustment. The 12 Agent and four reference outputs remain the complete fixed schedule. The pre-access audit's statistical and scientific limitations remain unchanged.
