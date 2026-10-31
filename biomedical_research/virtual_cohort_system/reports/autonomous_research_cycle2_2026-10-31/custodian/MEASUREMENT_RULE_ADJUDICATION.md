# Standing anthropometry rule adjudication

2026-10-31. Metadata-only supplement to `PREFLIGHT_REPORT.md` and review of `../PROTOCOL_DRAFT.md` (reviewed snapshot SHA-256 `4116a97ec85982bb7a66cc423f3013908b5364da8339a88c58e3d22320d334bc`). No participant file, field frequency, measurement value, eligibility count or effect was read or calculated for this follow-up. No acquisition or target preparation occurred. The original preflight/ledger remain unchanged; this is a new supplemental artifact.

**Use the first complete admissible ordinal weight/standing-height pair, otherwise the second complete pair. This explicitly supersedes the preflight's provisional mean-of-two proposal.** It is an investigator-defined secondary-analysis rule. Neither the official questionnaire nor catalogue prescribes this pair-selection algorithm or establishes that equal ordinal weight/height readings were collected at the same instant.

The official documentation resolves routing and explicit nonmeasurement. It does **not** resolve whether an adverse/unknown block result invalidates either stored repeat. The selected prospective investigator policy requires both age-routed weight and standing-height result flags to be **code 1, whose exact official label is "Sin problema" (no problem)**. The source label does not literally say "completed". Other documented codes or missing block flags are excluded because they do not meet the investigator's documented-quality criterion, not because their numeric readings have been proven invalid. This additional restriction changes the target definition and must appear in the protocol and paper.

The selected executable rule distinguishes `ADMIT_PAIR`, `EXCLUDE_EXPLICIT_OR_MISSING`, `EXCLUDE_QUALITY_RESTRICTION`, and `HOLD_FOR_ADJUDICATION`. Undocumented codes and explicit cross-field contradictions remain holds before effects; they are not silently removed or rescued by choosing another repeat. A broader earlier alternative that held every uncertain result status is retained in the final audit section and is **not** the selected rule.

## Authoritative local sources and locators

The PDF pages below use one-based viewer pages, which also have printed page numbers 2-5. Graphical arrows on pages 3-4 were checked; extracted text alone does not preserve their row alignment. An independent agent confirmed the mappings from these same official files without participant-data access.

- `metadata_local/CN_ANTROPOMETRIA.Cuestionarios.pdf`, SHA-256 `54a651dc5765920ea110b0966e30e57fc4d59a388625f728c810c7df053cbf29`: p2 Q1-Q5 and under-60 age/sex routes; p3 Q6-Q10; p4 Q11-Q18 and exact mobility arrows; p5 Q19-Q26 and alternative-measurement blocks.
- `metadata_local/CN_ANTROPOMETRIA.Catálogo.xlsx`, SHA-256 `f6b949c2b93a2ba383079d5392c1dc45b8e06d4f1fb2763e6c8b99d02f227d62`: `Variables` worksheet rows 22-42 and `Valores` rows 18-67, detailed below. Spreadsheet row numbers include the 16 leading blank rows and header row 17.
- Source acquisition URL: [official ENSANUT downloads](https://ensanut.insp.mx/encuestas/ensanut2018/descargas.php). Exact previously observed POST field IDs, empty values, bytes and hashes remain in `DOWNLOAD_LEDGER.json`; no new request was made.

## Measurement-block and result-flag lookup

All four result fields contain **one status for a measurement block with two recorded readings**. There is no status for repeat 1 separately from repeat 2, and no combined BMI-pair result flag. A weight-block status cannot identify which height reading is acceptable, or vice versa.

| Adult age / measurement | Reading fields | Result flag | Scope | Exact source locators |
|---|---|---|---|---|
| 25-59 weight | `PESO1_1`, `PESO1_2` | `P3` | Entire Q1 weight block | PDF p2 Q1-Q3; Variables rows 22-25; Valores 24-27 |
| 25-59 standing height | `TALLA4_1`, `TALLA4_2` | `P5` | Entire Q4 height block | PDF p2 Q4-Q5; Variables 26-28; Valores 29-32 |
| 60-79 measured weight | `PESO12_1`, `PESO12_2` | `P14` | Entire Q12 weight block, subject to Q11 routing | PDF p4 Q12-Q14; Variables 36-39; Valores 59-62 |
| 60-79 standing height | `TALLA15_1`, `TALLA15_2` | `P16` | Entire Q15 standing-height block, subject to Q11 routing | PDF p4 Q15-Q16; Variables 40-42; Valores 64-67 |

The questionnaire's under-60 block covers all selected ages below 60; height is standing height from ages 2-59, with infant length in the same field family below age 2. The reviewed protocol's age 25-79 restriction avoids that pediatric distinction.

| Code | `P3`, `P5`, `P14` meaning | `P16` meaning | Adjudication consequence |
|---|---|---|---|
| 1 | No problem | No problem | Uncomplicated block result; still require an admissible numeric reading. Status 1 never rescues a missing or nonmeasurement value. |
| 2 | Physical problem | Physical problem | Exclude under the selected investigator quality restriction. The sources do not identify which repeat failed or prove both numbers invalid; second-reading fallback cannot bypass this block criterion. |
| 3 | Did not cooperate | Did not cooperate | Exclude under the selected quality restriction. Failure after one successful attempt is possible but not established; do not recode stored numbers as officially invalid. |
| 9 | Does not know | Unspecified | Catalogue-only unknown status, absent from the printed question's response list. Exclude for failure to document a code-1 block result, without claiming numeric invalidity. |
| Blank | No documented result | No documented result | Exclude under the same prospective documentation/quality restriction; missing status is not proof the measurement failed. |
| Other nonblank code | Undocumented | Undocumented | Coding error: hold before effects. Do not infer a meaning from participant patterns. |

If neither ordinal pair is numerically available, ordinary missing/nonmeasurement exclusion already applies. If a pair is available, the relevant **weight and height** block statuses must both equal 1 under the selected restriction. Switching to repeat 2 cannot escape a criterion that covers the same whole block. Raw result codes and measurements stay preserved; exclusion is an analysis-mask decision, not destructive editing of the source.

## Q11 mobility/amputation routing at age 60 or older

Source: PDF p4 Q11 graphical arrows; `Variables` row 35; `Valores` rows 49-53. The printed questionnaire, not the incomplete value catalogue, resolves code 2.

| `P11` | Meaning | Official destination | Standing-pair treatment |
|---|---|---|---|
| 1 | Upper-limb amputation; walks | Continue to Q12 weight, then Q15 standing height | Standing route is permitted. Do not blanket-exclude all amputations, invent a weight correction, or claim amputation has no effect on BMI comparability. Preserve this quality/context flag. |
| 2 | Upper-limb amputation; does not walk | Q17 heel-to-knee measurement | **Not a standing route.** Code 2 is omitted from XLSX Valores but explicit in the PDF. |
| 3 | Lower-limb amputation | Q23 hemi-span | Alternative measurement route; not measured standing height. |
| 4 | No amputation; can remain standing | Continue to Q12 and Q15 | Standing route is permitted. |
| 5 | No amputation; can only sit | Q17 heel-to-knee measurement | Alternative seated route. |
| 6 | No amputation; confined to bed | Q27 blood pressure | Skips these anthropometric blocks. |
| Blank | Unknown route | Not specified | Exclude under the selected requirement for a documented standing route at age 60+; missing route is not proof of inability to stand. |
| Other nonblank code | Undocumented | Not specified | Hold as coding error. |

Known alternative routes with no admissible standing values are excluded from this standing-pair analysis. If admissible positive, nonsentinel values appear in fields that a **known alternative route** skips, flag a routing contradiction and hold; do not silently decide that either the route or the numbers are correct. A missing route is uncertainty, not this same contradiction; it is excluded under the prospective documented-route criterion. `TALLAPIE17_1` is heel-to-knee distance; `HEMIENVERGADURA23_1` is chest-to-fingertip distance. Neither is a substitute standing-height observation. No reconstruction equation is admitted.

## Clothing and other flags

| Field(s) | Codes / meaning | Measurement consequence and source |
|---|---|---|
| `P2` (under 60), `P13` (60+) | 1 light clothing; 2 heavy clothing; 3 no clothing; 4 not weighed | One flag for the whole weight block, not a repeat. Codes 1/2/3 do not invalidate weight; do not subtract an invented clothing allowance. Code 4 explicitly records no weighing. PDF p2 Q2 / p4 Q13; Variables 24/38; Valores 19-23 / 55-58. |
| `P2=9` | Unknown clothing | Catalogue-defined unknown, not invalid weight. Retain an otherwise admissible pair with the clothing status unknown. |
| `P13=9` | **Not defined** in the available catalogue/questionnaire | Do not transfer P2's codebook automatically. Treat this nonblank undocumented code as a hold. |
| Blank `P2`/`P13` | Clothing unknown | Missing clothing is not proof no weighing occurred; it does not alone exclude an otherwise admissible pair. |
| `P10` | 1 no recent weight loss; 2 loss of 1-3 kg; 3 loss greater than 3 kg; 8 no answer; 9 unknown | Recent weight-loss history, not a result flag for the present measured weight. No filter or correction for this five-variable protocol. PDF p3 Q10; Variables 34; Valores 44-48. |
| `P6`, `P7_1` | Physiological status and conditional pregnancy duration | Separate protocol eligibility, not proof that earlier weight/height is invalid. See the next section. |
| `P9`, `P18`, `P20`, `P22`, `P24`, `P26` | Results of waist, heel-knee, calf, older-adult waist, hemi-span and arm measurements | They do not validate or invalidate Q1/Q4/Q12/Q15 readings. Do not require all questionnaire flags to be 1. PDF pp3-5; Variables 33,44,46,49,51,53. |
| `P29`, `P30` | Blood-pressure arm and measurement result | Unrelated to the standing weight/height pair; no gate for this protocol. PDF p6 Q29-Q30. |

An explicit clothing code 4 with no admissible weight is ordinary no-measurement exclusion. Code 4 alongside an admissible numeric weight is a **contradiction requiring a hold**; the new rule does not silently overwrite either source field.

Weight nonmeasurement code `222.222` and height nonmeasurement code `222.2` are documented at PDF p2 Q1/Q4 and p4 Q12/Q15; the XLSX attaches them to the first-reading fields at Valores rows 18,28,54,63. Applying the identical numeric codes to the same-unit second readings is an explicitly declared conservative cleaning convention. Compare numeric equality, not only string formatting. No empirical range, quantile or BMI plausibility rule is introduced.

## Pregnancy/lactation rule: P6 code 4 is correct

The reviewed protocol's women-aged-25-through-49 rule is consistent with the official questionnaire. Anthropometry `P6=4` means **neither pregnancy nor breastfeeding**. It is not a missing code. `P6=1` is pregnant, 2 breastfeeding, 3 both, 9 unknown. Source: PDF p3 Q6, `Variables` row 29, `Valores` rows 33-37.

Q6 is asked of selected women ages 12-49. The proposed target's 25-49 female subset lies within that route. Require the exact female code 2 and inclusive age bounds 25 and 49; for those participants, require `anthropometry.P6 == 4`. Codes 1/2/3 are excluded by the **investigator's physiological-status restriction**, not as failed anthropometry; code 9 or blank lacks the required status. Other undocumented nonblank codes require a hold. For men and women aged 50 or older, do not require or invent a P6=4 response.

Graphical routing: pregnant codes 1/3 proceed through pregnancy months Q7, then Q27; breastfeeding-only code 2 goes directly to Q27. Codes 4/9 send women age 20+ to waist Q8 and end the questionnaire for ages 12-19. The weight/height block occurs **before** these routes. Q7 months are conditional; 99 is unknown/unspecified (PDF p3 Q7; Variables row 30; Valores row 38). Do not use blank Q7 to manufacture a nonpregnant status or require Q7 for P6=4. This adjudicates the rule written in the draft; no notebook implementation was inspected or certified.

## Missing third measurements and ordinal pairing

The official adult weight third-reading trigger is a discrepancy of at least 0.400 kg. Height triggers differ: greater than 1 cm under 60, at least 1 cm from age 60. Sources: PDF p2 Q1/Q4 and p4 Q12/Q15. Only two repeat fields are documented. No source establishes whether a stored reading replaced an earlier reading, whether the third was kept elsewhere, or which averaging/adjudication rule produced a final measurement.

The draft already declares an investigator-defined first-complete-ordinal-pair measurement, rather than reconstruction of that unobserved final algorithm. Under that explicit policy, a discrepancy trigger is recorded as an audit diagnostic **without changing pair choice, filtering the record, forcing an average, or selecting a more convenient result**. Its absence would not prove a third measurement was unnecessary or obtained. If the protocol instead claims to reproduce the official final/adjudicated measurement, these files cannot support that claim and preparation must stop. Do not add a post-inspection discrepancy cutoff to eligibility.

## Proposed executable logic, not executed on target data

The following defines measurement selection for a row already known to have integer age 25-79. `a` is the anthropometry record with original module-specific field names; it must never use laboratory `P3` or laboratory `P6`. All identifiers and participant values stay private. The function below is specification text only: it was not called, no target file was opened, and no BMI was computed during this follow-up.

```python
from decimal import Decimal, InvalidOperation

class MeasurementHold(Exception):
    pass  # Raise field/reason only; never log the participant or raw value.

def code(a, field, allowed):
    raw = a.get(field)
    if raw is None or str(raw).strip() == "":
        return None
    try:
        value = Decimal(str(raw).strip())
    except InvalidOperation:
        raise MeasurementHold(field + ": malformed code")
    if not value.is_finite() or value != value.to_integral_value():
        raise MeasurementHold(field + ": nonintegral/nonfinite code")
    value = int(value)
    if value not in allowed:
        raise MeasurementHold(field + ": undocumented code")
    return value

def reading(a, field, sentinel):
    raw = a.get(field)
    if raw is None or str(raw).strip() == "":
        return None
    try:
        value = Decimal(str(raw).strip())
    except InvalidOperation:
        raise MeasurementHold(field + ": malformed measurement")
    if not value.is_finite() or value <= 0 or value == sentinel:
        return None  # Unusable; reason must be preserved in the private audit.
    return value

def first_complete_standing_pair(a, age):
    assert isinstance(age, int) and 25 <= age <= 79
    older = age >= 60
    wfields = ("PESO12_1", "PESO12_2") if older else ("PESO1_1", "PESO1_2")
    hfields = ("TALLA15_1", "TALLA15_2") if older else ("TALLA4_1", "TALLA4_2")
    required = set(wfields + hfields)
    required.update({"P14", "P16", "P13", "P11"} if older else {"P3", "P5", "P2"})
    if not required.issubset(a):
        raise MeasurementHold("schema: required anthropometry field absent")
    wstatus = code(a, "P14" if older else "P3", {1, 2, 3, 9})
    hstatus = code(a, "P16" if older else "P5", {1, 2, 3, 9})
    clothing = code(a, "P13" if older else "P2",
                    {1, 2, 3, 4} if older else {1, 2, 3, 4, 9})
    route = code(a, "P11", {1, 2, 3, 4, 5, 6}) if older else None
    weights = [reading(a, name, Decimal("222.222")) for name in wfields]
    heights = [reading(a, name, Decimal("222.2")) for name in hfields]

    if older and route in {2, 3, 5, 6}:
        if any(x is not None for x in weights + heights):
            raise MeasurementHold("P11: alternative route with standing-field values")
        return {"decision": "EXCLUDE_EXPLICIT_OR_MISSING", "reason": "alternative_route"}
    if clothing == 4:
        if any(x is not None for x in weights):
            raise MeasurementHold("clothing: not-weighed code with numeric weight")
        return {"decision": "EXCLUDE_EXPLICIT_OR_MISSING", "reason": "not_weighed"}

    complete = [i for i in (0, 1)
                if weights[i] is not None and heights[i] is not None]
    if not complete:
        return {"decision": "EXCLUDE_EXPLICIT_OR_MISSING", "reason": "no_complete_ordinal_pair"}
    if older and route not in {1, 4}:
        return {"decision": "EXCLUDE_QUALITY_RESTRICTION", "reason": "standing_route_not_documented"}
    if wstatus != 1 or hstatus != 1:
        return {"decision": "EXCLUDE_QUALITY_RESTRICTION", "reason": "both_block_results_not_code1"}

    i = complete[0]  # Pair 1 always has priority; no cross-repeat mixing.
    return {"decision": "ADMIT_PAIR", "repeat": i + 1,
            "weight_kg": weights[i], "height_cm": heights[i],
            "clothing_code": clothing, "older_route": route}
```

Precedence is deliberate: validate the active field codes; recognize explicit routing/nonmeasurement contradictions; determine whether an ordinal pair exists; require a documented standing route and both code-1 block results under the selected investigator quality restriction; then choose the first complete pair. Result flag 1 cannot rehabilitate an unusable reading. The second pair is considered only for absent/nonmeasurement/nonpositive/nonfinite first-pair readings and cannot override route, no-weighing or result-status criteria. No other age block or alternative stature field is considered.

After a separately authorized preparation freeze, BMI would use the admitted pair exactly as `weight_kg / (height_cm / 100) ** 2`. Repeat availability, discrepancy triggers, clothing unknown/heavy, and permitted P11=1 context may be preserved in a private audit, but not used to select an outcome-favorable rule. This document supplies no target count, BMI, distribution or effect.

## Selected policy and paper wording

The first/second ordinal selection, code-1 quality restriction, pregnancy code 4, documented standing routes, clothing interpretation, explicit sentinels and hold conditions above are the selected prospective proposal. They remain subject to the independent protocol/code review and freeze; this document does not release target preparation.

Suggested methods wording:

> We required the age-appropriate weight and standing-height blocks to be recorded as having no problem (result code 1). At age 60 or older, we additionally required a documented standing-measurement route. Other documented or missing block results were excluded under this prespecified quality/documentation criterion; they were not treated as proof that all stored readings were numerically invalid. We used the first complete positive, nonsentinel ordinal weight-height pair, falling back to the second complete ordinal pair without mixing readings. This investigator-defined secondary-analysis measure does not reconstruct an undocumented final or third-reading adjudication algorithm. Undocumented codes or explicit routing/no-measurement contradictions stopped preparation for adjudication before effects were calculated.

Suggested limitation: this is a target subset with documented uncomplicated measurement blocks and other protocol exclusions; it need not represent participants with physical measurement difficulties, unknown result documentation, or alternative mobility routes. Retained P11=1 upper-limb amputation may also affect BMI comparability even though it follows the documented standing route. No correction was invented.

## Earlier broader alternative retained for audit, not selected

Before the investigator selected the quality restriction, the metadata-conservative alternative was: admit an uncomplicated numeric pair; exclude explicit nonmeasurement/missing pairs; **hold every complete pair with result code 2/3/9/blank or unknown standing route**, because the official sources do not identify repeat-specific validity. That approach avoided a new quality-defined target restriction but could not automatically settle ambiguous records from the available documents. The selected rule instead excludes those documented/missing-status records prospectively as an eligibility choice. It retains holds for undocumented codes and explicit cross-field contradictions. Neither approach may claim that status 2/3/9 proves both stored readings invalid, and neither permits an outcome-driven choice between them.
