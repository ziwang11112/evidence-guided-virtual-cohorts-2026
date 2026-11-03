# Information provision and additional revision: CHNS development results

This is one previously exposed clinical case, with three fresh scientific constructions per information condition. L used external literature and the visible research questions; R additionally received the complete existing reference summaries. Initial delivery could already use two trials; final delivery follows one additional revision/retention stage. This is not a no-feedback versus feedback experiment.

Actual attempts: **42** (36 delivery, 6 trial); successful tables: **42**; distinct byte hashes: **24**; failures: **0**. Each successful table has 3,000 rows. Rows and seeds are not independent clinical or author replications. No raw patient reads are recorded in the retained execution logs; author general-tool access was procedurally scoped.

All six final stages were closed before common reference evaluation. These comparisons concern consistency with an observed development sample, not recovery of population truth or independent target validation.

## Primary and joint analyses

Numbers below are means across available fixed delivery seeds, with each author shown. Full ranges, individual seeds, missingness and matched changes are retained in COMPLETE_RESULTS.json.

| Constructor | Stage | E1 | E2 | E3 | Pearson | Spearman |
|---|---|---:|---:|---:|---:|---:|
| L01 | initial | 0.0130014 | 0.356064 | 0.00690983 | 0.633764 | 0.530211 |
| L01 | final | 0.0130014 | 0.356064 | 0.00690983 | 0.633764 | 0.530211 |
| L02 | initial | 0.034287 | 0.453562 | 0.00355185 | 0.776664 | 0.501339 |
| L02 | final | 0.034287 | 0.453562 | 0.00355185 | 0.776664 | 0.501339 |
| L03 | initial | 0.0224354 | 0.487815 | 0.00487248 | 0.81317 | 0.566477 |
| L03 | final | 0.0224354 | 0.487815 | 0.00487248 | 0.81317 | 0.566477 |
| R01 | initial | 0.0557886 | 0.398681 | 0.00789617 | 0.666438 | 0.360983 |
| R01 | final | 0.0557886 | 0.398681 | 0.00789617 | 0.666438 | 0.360983 |
| R02 | initial | 0.0528208 | 0.413715 | 0.00756943 | 0.650561 | 0.35907 |
| R02 | final | 0.0528208 | 0.413715 | 0.00756943 | 0.650561 | 0.35907 |
| R03 | initial | 0.0553837 | 0.396941 | 0.00794654 | 0.657194 | 0.357571 |
| R03 | final | 0.0553837 | 0.396941 | 0.00794654 | 0.657194 | 0.357571 |

E1: HbA1c–BMI adjusted for age/sex; E2: HbA1c–glucose adjusted for age/sex; E3: HbA1c–age adjusted for sex/BMI/glucose. Exact operators and units remain in analysis_definitions.json.

## Revision results by construction

| Constructor | Analysis | Initial mean absolute difference | Final mean absolute difference | Matched seeds |
|---|---|---:|---:|---:|
| L01 | E1 | 0.0419447 | 0.0419447 | 3 |
| L01 | E2 | 0.0460298 | 0.0460298 | 3 |
| L01 | E3 | 0.00119721 | 0.00119721 | 3 |
| L01 | glucose_hba1c_pearson | 0.0272043 | 0.0272043 | 3 |
| L01 | glucose_hba1c_spearman | 0.168753 | 0.168753 | 3 |
| L02 | E1 | 0.0206591 | 0.0206591 | 3 |
| L02 | E2 | 0.0514689 | 0.0514689 | 3 |
| L02 | E3 | 0.00455519 | 0.00455519 | 3 |
| L02 | glucose_hba1c_pearson | 0.115695 | 0.115695 | 3 |
| L02 | glucose_hba1c_spearman | 0.139881 | 0.139881 | 3 |
| L03 | E1 | 0.0325107 | 0.0325107 | 3 |
| L03 | E2 | 0.0857216 | 0.0857216 | 3 |
| L03 | E3 | 0.00323456 | 0.00323456 | 3 |
| L03 | glucose_hba1c_pearson | 0.152202 | 0.152202 | 3 |
| L03 | glucose_hba1c_spearman | 0.20502 | 0.20502 | 3 |
| R01 | E1 | 0.00144102 | 0.00144102 | 3 |
| R01 | E2 | 0.0179576 | 0.0179576 | 3 |
| R01 | E3 | 0.000632671 | 0.000632671 | 3 |
| R01 | glucose_hba1c_pearson | 0.0417151 | 0.0417151 | 3 |
| R01 | glucose_hba1c_spearman | 0.0272824 | 0.0272824 | 3 |
| R02 | E1 | 0.00254251 | 0.00254251 | 3 |
| R02 | E2 | 0.0236525 | 0.0236525 | 3 |
| R02 | E3 | 0.00092635 | 0.00092635 | 3 |
| R02 | glucose_hba1c_pearson | 0.0268697 | 0.0268697 | 3 |
| R02 | glucose_hba1c_spearman | 0.0124767 | 0.0124767 | 3 |
| R03 | E1 | 0.00252278 | 0.00252278 | 3 |
| R03 | E2 | 0.0237858 | 0.0237858 | 3 |
| R03 | E3 | 0.000462294 | 0.000462294 | 3 |
| R03 | glucose_hba1c_pearson | 0.0151144 | 0.0151144 | 3 |
| R03 | glucose_hba1c_spearman | 0.00388626 | 0.00388626 | 3 |

These discrepancies retain each statistic’s own units. They are not a global accuracy score, an acceptance threshold, or proof that a reference sample estimate equals its population parameter.

## Complete distribution diagnostics

Every diagnostic is included; each cell shows initial → final mean. No favorable subset is selected.

| Diagnostic | L01 | L02 | L03 | R01 | R02 | R03 |
|---|---:|---:|---:|---:|---:|---:|
| age_mean | 54.1408 → 54.1408 | 53.0376 → 53.0376 | 53.7966 → 53.7966 | 52.7709 → 52.7709 | 52.7426 → 52.7426 | 52.7426 → 52.7426 |
| age_sd | 9.62882 → 9.62882 | 9.85909 → 9.85909 | 9.46134 → 9.46134 | 10.5113 → 10.5113 | 10.5103 → 10.5103 | 10.5103 → 10.5103 |
| age_q10 | 41 → 41 | 40 → 40 | 41 → 41 | 39 → 39 | 39 → 39 | 39 → 39 |
| age_median | 54 → 54 | 53 → 53 | 54 → 54 | 53 → 53 | 53 → 53 | 53 → 53 |
| age_q90 | 67.3333 → 67.3333 | 66.6667 → 66.6667 | 66.6667 → 66.6667 | 68 → 68 | 68 → 68 | 68 → 68 |
| female_mean | 0.548222 → 0.548222 | 0.535889 → 0.535889 | 0.548444 → 0.548444 | 0.537 → 0.537 | 0.543333 → 0.543333 | 0.543333 → 0.543333 |
| female_sd | 0.497738 → 0.497738 | 0.498783 → 0.498783 | 0.497709 → 0.497709 | 0.498631 → 0.498631 | 0.49817 → 0.49817 | 0.49817 → 0.49817 |
| female_q10 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| female_median | 1 → 1 | 1 → 1 | 1 → 1 | 1 → 1 | 1 → 1 | 1 → 1 |
| female_q90 | 1 → 1 | 1 → 1 | 1 → 1 | 1 → 1 | 1 → 1 | 1 → 1 |
| bmi_mean | 23.9135 → 23.9135 | 23.9193 → 23.9193 | 23.7031 → 23.7031 | 23.6897 → 23.6897 | 23.6906 → 23.6906 | 23.6906 → 23.6906 |
| bmi_sd | 3.4843 → 3.4843 | 3.35201 → 3.35201 | 3.3664 → 3.3664 | 3.38965 → 3.38965 | 3.40243 → 3.40243 | 3.40243 → 3.40243 |
| bmi_q10 | 19.6259 → 19.6259 | 19.7527 → 19.7527 | 19.5475 → 19.5475 | 19.5269 → 19.5269 | 19.5541 → 19.5541 | 19.5541 → 19.5541 |
| bmi_median | 23.6729 → 23.6729 | 23.7141 → 23.7141 | 23.4586 → 23.4586 | 23.4732 → 23.4732 | 23.4337 → 23.4337 | 23.4337 → 23.4337 |
| bmi_q90 | 28.4866 → 28.4866 | 28.2872 → 28.2872 | 28.0865 → 28.0865 | 28.1195 → 28.1195 | 28.2291 → 28.2291 | 28.2291 → 28.2291 |
| glucose_mean | 5.28443 → 5.28443 | 5.39662 → 5.39662 | 5.45036 → 5.45036 | 5.49479 → 5.49479 | 5.49339 → 5.49339 | 5.48472 → 5.48472 |
| glucose_sd | 1.24223 → 1.24223 | 1.48082 → 1.48082 | 1.40422 → 1.40422 | 1.58968 → 1.58968 | 1.48817 → 1.48817 | 1.55759 → 1.55759 |
| glucose_q10 | 4.34002 → 4.34002 | 4.31324 → 4.31324 | 4.41434 → 4.41434 | 4.42564 → 4.42564 | 4.4128 → 4.4128 | 4.42149 → 4.42149 |
| glucose_median | 5.05657 → 5.05657 | 5.10816 → 5.10816 | 5.15615 → 5.15615 | 5.16982 → 5.16982 | 5.16579 → 5.16579 | 5.17186 → 5.17186 |
| glucose_q90 | 6.12841 → 6.12841 | 6.32704 → 6.32704 | 6.32756 → 6.32756 | 6.58752 → 6.58752 | 6.48241 → 6.48241 | 6.51792 → 6.51792 |
| hba1c_mean | 5.63342 → 5.63342 | 5.68066 → 5.68066 | 5.75723 → 5.75723 | 5.67592 → 5.67592 | 5.68483 → 5.68483 | 5.67178 → 5.67178 |
| hba1c_sd | 0.706159 → 0.706159 | 0.869475 → 0.869475 | 0.848088 → 0.848088 | 0.965542 → 0.965542 | 0.95751 → 0.95751 | 0.95208 → 0.95208 |
| hba1c_q10 | 5.005 → 5.005 | 4.99609 → 4.99609 | 5.12385 → 5.12385 | 4.99698 → 4.99698 | 4.98757 → 4.98757 | 4.98707 → 4.98707 |
| hba1c_median | 5.52116 → 5.52116 | 5.51128 → 5.51128 | 5.58446 → 5.58446 | 5.49775 → 5.49775 | 5.4972 → 5.4972 | 5.49572 → 5.49572 |
| hba1c_q90 | 6.24018 → 6.24018 | 6.24442 → 6.24442 | 6.24828 → 6.24828 | 6.28654 → 6.28654 | 6.28172 → 6.28172 | 6.30825 → 6.30825 |
| glucose_hba1c_pearson | 0.633764 → 0.633764 | 0.776664 → 0.776664 | 0.81317 → 0.81317 | 0.666438 → 0.666438 | 0.650561 → 0.650561 | 0.657194 → 0.657194 |
| glucose_hba1c_spearman | 0.530211 → 0.530211 | 0.501339 → 0.501339 | 0.566477 → 0.566477 | 0.360983 → 0.360983 | 0.35907 → 0.35907 | 0.357571 → 0.357571 |

## Interpretation limits

Reference-assisted agreement demonstrates the ability to construct data consistent with supplied summaries; it is not independent discovery. Literature-only agreement is developmental evidence for transfer on this case, with unmeasured transport and joint assumptions. External source-population numerical replay was unavailable in both arms. Three fixed seeds assess conditional sampling variation, not evidence, model or transport uncertainty. All 30 summaries were supplied to R; there is no hidden-outcome generalization claim within this unit. Revisions include extra reasoning/computation, and no causal effect of feedback alone is isolated.

A final scientific interpretation and independent numerical audit must be read alongside this automatically generated complete inventory. No post-hoc equivalence margin or clinical validity label has been applied.
