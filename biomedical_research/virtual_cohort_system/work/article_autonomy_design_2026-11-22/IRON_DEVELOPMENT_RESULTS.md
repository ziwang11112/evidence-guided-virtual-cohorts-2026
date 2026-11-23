# Iron development run: one supported association and one pairing-sensitive analysis

22 November 2026. One scientific authoring session with three GPT calls. This paper had already been used in project development. The experimental unit is one article and one author. The three scenarios and three evaluation seeds yield nine final virtual tables.

## What the agent received and authored

The constructor received the original article in layout text and the [short iron research request](development_requests.json). The first model response chose the study population, measurements, evidence, estimands, model and assumptions. The program-writing response received that design and a generic numerical interface. Each virtual table had 10,000 rows. After one diagnostic seed, the model could keep, replace or withdraw its program. It kept the original. The [audited API captures](IRON_API_AUDIT.json) matched these transmitted inputs, including the model's own earlier responses and generated-only diagnostics. No evaluator output or historical task instructions were transmitted. The project tariff estimate for three calls to gpt-6.1-sol was USD 0.240498.

The agent collapsed the eight deficiency categories in Table IV into the four cells needed for the crude odds ratio. It used the study cutoffs and distinguished the adjusted estimate in Table V. It selected the stratum-specific and overall evidence, chose distributions and their calibration targets, wrote both the generator and its analysis function, and proposed three ways to pair the two measurements within the same hemoglobin-stratum and iron-status cells. The investigator supplied the article, the questions, the general design and review instructions, the row budget and seeds. The first execution was launched in stages. No case-specific scientific corrections were sent to the author and no generator parameters were edited. The [single-command driver](run_development.py) subsequently resumed the entire run from the same saved submissions and receipts.

## Two analyses on the same rows

| Within-cell assignment chosen by the agent | Crude anemia odds ratio, all three seeds | Continuous Hb–ferritin Spearman correlation, min to max across seeds |
|---|---:|---:|
| Random pairing | 6.651662 | 0.211240 to 0.230048 |
| Pair similar ranks | 6.651662 | 0.652888 to 0.662419 |
| Pair opposite ranks | 6.651662 | −0.224629 to −0.213338 |

The original 1,671 participants yielded threshold counts of 173, 85, 331 and 1,082. Their cross-product ratio is 6.653137. The integer allocation across 10,000 synthetic records yielded 1,036, 509, 1,981 and 6,474. This accounts for the small odds-ratio difference. The paper's adjusted odds ratio is 6.448 and answers a separate question. In each of the six alternative-versus-primary comparisons within a seed, the sorted values of both measurements were identical. The independent scorer reproduced both agent estimates on all nine tables to within an absolute tolerance of 1e-9. The source provides no individual-level Spearman estimate. The observed range illustrates attainable sensitivity under the submitted models. It gives neither sharp bounds nor an estimate of the true participant correlation. [Independent results](IRON_INDEPENDENT_RESULTS.json) · [Source article](https://doi.org/10.1024/0300-9831/a000014)

## What the agent missed

Every table reproduced the three printed within-stratum ferritin geometric means, 1.3, 5.9 and 22.3 µg/L, and the overall hemoglobin geometric mean of 129.9 g/L. The overall ferritin geometric mean in the generated rows was 17.3087 µg/L. The article prints 17.4 µg/L. The generated value rounds to 17.3. The review diagnostic checked ferritin's stratum-specific geometric means and omitted its overall geometric mean. The difference is small in magnitude and reveals a specific gap in source coverage. It does not account for the sign reversal between scenarios. Distribution tails and the biological plausibility of the alternative pairings remain assumptions.

## Interpretation and next decision

This run supports the feasibility of article-to-model authorship for a previously known study using a short researcher request. Its strongest evidence is the agent's pre-generation distinction between a reconstructible analysis and an underdetermined one, followed by an executable demonstration of the difference. No independent patient cohort, external clinician adjudication or ordinary-agent comparator was used here. The grader's three test groups checked equivalent derivations, altered units, adjusted-versus-crude substitution and table edge cases. [Evaluator and source definitions](evaluation/README.md)

Before new-article testing, let the next development case use the same interface. Record whether each material source statistic identified in the design was replayed, was left untested with a reason, or disagreed at its reported precision. Preserve the iron candidate and this failure. The four-article pilot remains unopened.
