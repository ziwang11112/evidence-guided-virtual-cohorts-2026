# One paper fixes the threshold odds ratio and leaves continuous ranks open

Zhu and colleagues reported hemoglobin (Hb) and ferritin summaries for 1,671 women. A researcher might use virtual records to estimate the odds of anemia in iron-depleted versus iron-replete women and to estimate the association across the continuous measurements. The source contains the four counts needed for the first calculation. It does not report the within-band ordering of the continuous values. Both the ordinary follow-up and the explicit request for an alternative changed this second analysis in **12 of 12 matched author blocks**. [Original study](https://doi.org/10.1024/0300-9831/a000014) · [Registration before the first call](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/commit/5df6277ef63cdcb6dd6367dceda2b4a5242d55e5)

## What the agent and investigator each supplied

Each initial model and its two follow-ups received the full scientific text with its tables. The author had to extract the study population counts, thresholds, units, geometric means and the adjusted odds ratio, then return a model specification, executable Python and an account of its assumptions. Table IV gives crude counts of 173, 85, 331 and 1,082. The resulting crude odds ratio is 6.65314. Table V's adjusted odds ratio of 6.448 answers a different question. Hemoglobin is in g/L and ferritin in µg/L under the methods and Table III. Table I's ferritin label is inconsistent with these. [Checked quantities](SOURCE.json) · [Actual request](REQUEST.txt)

The investigator specified positive marginal grids from the extracted summaries. A common rounding convention reconciled the ferritin band and overall geometric means at their printed precision. Each draw contained 16,710 positions, ten times the published category counts. The agent could permute the ferritin values within each of the three Hb bands. The researcher specified the use and change threshold. No preferred sign, residual dependence, desired correlation or participant measurements entered the prompt. Both branches saw the same initial model. [Frozen design](PROTOCOL.md) · [Common authoring procedure](../DESIGN.md)

## Registered results

All 36 submitted programs passed evidence extraction and all scientific and numerical checks on the three seeds. The crude odds ratio stayed at 6.65314. Each of the 24 follow-ups changed the pooled continuous Spearman correlation by more than 0.10, with a shift greater than 0.05 in the same direction at every seed. The median absolute change was 0.67656 in each branch. There were zero discordant blocks, and the prespecified exact paired comparison gives *p* = 1. The ordinary prompt already found alternatives in every block, so this article reached the ceiling on the binary outcome. Seven matched blocks returned byte-identical assignments across both follow-ups at all three seeds. [All values, failures and source checks](RESULTS.json) · [Independent verification](VERIFICATION.json)

| Block | Initial ρ | Ordinary ρ | Targeted ρ | Both follow-ups returned identical rows at all seeds |
|---|---:|---:|---:|:---:|
| B01 | 0.2512 | 0.9277 | 0.9277 | yes |
| B02 | 0.2512 | 0.5773 | 0.9277 | no |
| B03 | 0.2512 | 0.9277 | 0.9277 | yes |
| B04 | 0.2512 | 0.6434 | 0.9277 | no |
| B05 | 0.2512 | −0.4266 | 0.8182 | no |
| B06 | 0.2512 | 0.9277 | 0.9277 | yes |
| B07 | 0.2512 | 0.9277 | 0.9277 | yes |
| B08 | 0.2512 | 0.5773 | 0.9277 | no |
| B09 | 0.2512 | 0.9277 | 0.9277 | yes |
| B10 | 0.2512 | 0.9277 | 0.9277 | yes |
| B11 | 0.2512 | 0.9277 | 0.9277 | yes |
| B12 | 0.2512 | 0.6461 | 0.9277 | no |

## How far could the reported association move?

After scoring, a separate calculation located these estimates among all allowed permutations. Center each observation's rank using the pooled mean rank. Spearman correlation is a sum of products of centered Hb and ferritin ranks divided by their fixed norms. Within each Hb band, assigning the two rank lists in the same order maximizes that band's contribution, and reversing one minimizes it. The assignments may be chosen independently across bands. The resulting global endpoints are therefore sharp **conditional on these finite marginal values and the registered Hb bands**. The paper itself does not specify these exact individual values. [Derivation and numerical checks](rank_audit.py) · [All audit counts](RANK_AUDIT.json)

The two achievable endpoints were **−0.42660 and 0.92772**. Random assignment within each band has expected correlation 0.25056, since the band means already vary together. Twelve initial programs returned exactly the same three seeded assignment files, yielding 0.25117. Seven ordinary programs and eleven targeted programs reached the upper endpoint at all seeds. One ordinary program reached the lower endpoint. This separates three facts. The original cross-tabulation establishes a positive threshold association. The continuous rank association depends on the unreported within-band pairing. Independent author sessions can repeatedly choose the same assignments. Neither endpoint supplies an estimate of the association in actual women.

## Reproducibility and decision

A second implementation independently extracted all numbers from the original tables, checked the parent artifact and matched prompts for all 36 calls, reconstructed their usage-based tariff of USD 2.4118712, and recalculated the outcome and constraints from the saved inputs and assignments for **108 tables**. A separate run of B01's targeted program at seed 523301 reproduced the original assignment hash. These three-seed assignments support executable counterexamples. Recovering a population's continuous rank association requires comparable paired information. [Provider receipts and model metadata](PUBLIC_AUTHORS.json) · [Model decisions and executable code](PROGRAMS.json) · [Offline replay](../replay.py)

The registration required at least eight complete blocks, independent verification and more material pairs under targeted search to progress to another publication. Twelve complete blocks and a tie close the paid expansion here. The fourth candidate, Australian handgrip, received no authoring calls under this protocol. Earlier independent handgrip measurements remain a separate transfer experiment. [Three-article comparison](../RESULTS.md)
