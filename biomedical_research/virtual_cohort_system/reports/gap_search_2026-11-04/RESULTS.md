# Autonomous gap-directed search: evidence acquisition result

4 November 2026. A fresh scientific Agent was given the intended analysis, target population/measurement description and a bounded search budget, with **no preset DOI list, desired coefficient, sign or generator family**. It selected queries, original studies and follow-up routes. This unit acquired and reviewed evidence; it did not construct or execute a new generator.

The search recovered a directly relevant published conditional BMI coefficient and several complementary or contrasting results. In particular, it obtained the original LifeLines paper through its publisher, where the preceding live-generation run had used only the abstract. This is a real improvement in the inputs available to an author. It is not yet evidence that a revised generator performs better, nor a controlled comparison isolating the effect of unrestricted search from access-route changes.

## Research request

Future whole-cohort synthesis should support `HbA1c ~ 1 + BMI + glucose + age + female` for community-dwelling Chinese adults aged 35–74 around 2009, without diabetes/treatment exclusions. HbA1c is requested in percent and glucose as central serum mmol/L; individual fasting adherence is not verified. These population descriptors were supplied without target distributions, coefficients or expected signs. The search could consider other populations but had to state their applicability limits. CHNS-derived numerical evidence was excluded.

The main acquisition Agent had a fresh context, was not supplied the old generators or target results, and did not read them; filesystem and tool access were not technically isolated. Search snippets can nevertheless expose excluded material incidentally: a CHNS-derived result appeared in a web search and was logged/excluded, not opened or admitted as construction evidence. Fresh context and search exclusions are procedural boundaries, not proof that every returned snippet is unexposed.

## What the source review found

| Original study | Inspected information relevant to construction | Appropriate use and limit |
|---|---|---|
| **Jansen et al., LifeLines, 2013**, DOI 10.1111/joim.12010 | Table 3 Model III: BMI coefficient **0.05**, reported CI **0.02–0.08**, in HbA1c **mmol/mol per kg/m²**; FPG **2.13 (1.91–2.36)**; age **0.07 (0.06–0.09)**. Model includes age, gender, BMI, FPG, MCH, MCHC, current smoking and alcohol. | A genuine numeric conditional relationship, not a marginal correlation. Western-European nondiabetic/anemia-excluded population, plasma rather than target serum, additional covariates and different HbA1c units prevent direct target-parameter substitution. The original supplies the factor 10.93: dividing a slope by it converts to HbA1c percentage points. This algebraic conversion does not resolve population or adjustment differences. CI level and gender coding remain unresolved. |
| **Pani et al., 2008**, Framingham Offspring / NHANES, DOI 10.2337/dc08-0577 | Main text reports age coefficients **0.012** and **0.010 HbA1c percentage points/year**, respectively, with sex, BMI and fasting glucose adjustment; FOS additionally adjusts two-hour glucose. | Useful age-relationship evidence from two cohorts within one publication. No verified adjusted BMI coefficient or coefficient CI in the inspected passage; no-diabetes selections and population differences remain. |
| **Wisgerhof et al., Hoorn, 2020**, DOI 10.1371/journal.pone.0233769 | Adjusted HbA1c differences across BMI quartiles in two cohorts, with fasting/two-hour glucose and other adjustment. | Retain differing association patterns and full adjustment context. These are quartile contrasts, not per-unit BMI slopes; they cannot be inserted into a continuous linear coefficient field. |
| **Sakane et al., Japan Diabetes Prevention Program, 2017**, DOI 10.14740/jocmr2928w | Sex-stratified Table 3 BMI entries labelled “Beta”: 0.27 in men and 0.22 in women. | The inspected original does not establish whether Beta is standardized or unstandardized. The IGT-selected population and adjustment set also differ. Keep as partial evidence; no verified raw-scale BMI slope is claimed. |
| **Li et al., Hainan, 2021**, DOI 10.1038/s41598-021-85581-z | Joint anthropometric/glycaemic and diagnostic information; models and plot transformations differ from the requested regression. | Table 1 contains logistic effects for diabetes, not an HbA1c outcome slope. Uninspected supplements and scale/orientation details remain leads. No target-adjusted BMI slope was verified from the main text. |

The independently reopened LifeLines original confirms the Model III entries and adjustment set. The publication's model-complete-case count requires qualification: 2,832 is expressly given for the Table 2 alcohol model and is consistent with 2,921 minus 89 missing alcohol responses; it is **inferred/expected**, not explicitly printed for Table 3 Model III in the inspected material. The evidence ledger preserves that distinction.

The useful result is not “five papers all support the same relation.” It is a source packet that distinguishes native numerical conditional evidence, grouped contrasts, undefined-scale coefficients, and diagnostic models that do not answer the requested question. Conflicting or less applicable findings were retained rather than filtered by a desired sign.

## Actual execution and review

The same request-intake and task-bound literature adapter were reused. The host dispatched a scientific acquisition Agent; the library did not independently launch an LLM. The Agent used both the screened gateway and primary-publisher web access. Web-inspected originals remain explicitly separate from gateway-approved artifacts; no gateway approval was fabricated.

The bounded acquisition reviewed five original studies. Four original articles were saved as gateway XML/text. The fifth was inspected through the publisher, with methods and Tables 1–3 retained as a partial web-rendered snapshot, not a complete raw HTML/PDF. The gateway logs and a combined search ledger record successful calls, failed access, version selection and rejections. An independent reviewer checked source definitions and the critical coefficients, using saved originals plus a successful primary-publisher reopening; an earlier `/doi/full/` URL attempt failed and is retained in the accounting.

The generic intake's AUTHOR_TASK.md contains generation-stage delivery instructions. A separate EVIDENCE_ASSIGNMENT.md explicitly makes them inapplicable to this retrieval-only unit while preserving the original intake artifact. The existing gateway's transport ceiling is 16 MiB per response; the narrower 10 MiB saved-file / 50 MiB total allowance is procedurally tracked, not claimed as new enforcement code. Actual byte counts and combined-route usage are recorded in STATE.json.

## What this changes for the method

An Agent should be allowed to formulate searches around the missing conditional/joint evidence, not only look up an imposed bibliography. Suitable original routes beyond PMC matter: an absent PMCID did not make the LifeLines full text inaccessible through every allowed route. Independent source review also matters because a number labelled Beta, a logistic coefficient and a quartile contrast represent different estimands.

The new evidence still does not identify the complete requested target joint distribution. In particular, the extra LifeLines covariates need treatment or explicit marginalization assumptions; the source-supported HbA1c conversion must be applied explicitly, while plasma/serum transport, diabetes/treatment mix and within-population covariance remain construction assumptions. None is resolved by copying a source coefficient or increasing synthetic row count.

**Next bounded use:** supply a reviewed evidence-use packet to a fresh scientific constructor, let it choose which constraints and assumptions to use for the requested analysis, and check its joint-model implications. A new construction would be a separately recorded development version. Do not edit the closed live candidates, mandate source-population replay, or claim a quality gain before generating and evaluating the new version. No such construction was started in this unit.

## Record

See [the acquisition plan](PLAN.json), [protocol review](PROTOCOL_REVIEW.md), [independent evidence review](EVIDENCE_INDEPENDENT_REVIEW.md), [combined accounting/state](STATE.json), and the acquisition reports under the local bundle `evcGap01/reports/`. Public copies of the original authored evidence ledger and search log are accompanied by source URLs and hashes; full third-party articles and any individual data remain outside the public export.
