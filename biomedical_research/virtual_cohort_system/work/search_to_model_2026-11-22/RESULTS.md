# Can a scientific agent find the study and build the cohort?

Starting with the question alone, GPT searched Europe PMC, chose a primary article, and passed the selected article text into the cohort authoring workflow. A fresh session of the same model designed the cohort, wrote its sampling and analysis code and reviewed the trial discrepancies. All six final 10,000-eye tables executed. The average instrument difference agreed with the published paired estimate. The proportion exceeding 20 µm depended on the agent's distributional choice, and the virtual absolute thickness levels disagreed with values published in image-only tables. [Research request](REQUEST.txt) · [Run design](PROTOCOL.md) · [Selected study](https://doi.org/10.3349/ymj.2012.53.3.634)

## Where the evidence came from

The retrieval session issued two queries, considered 16 distinct hit records and opened three original papers. It selected Hong et al. after reading the quantitative details of the paired study. No study ID, title, target outcome or handpicked evidence packet was in its request. The chosen study included 50 eyes from 30 healthy volunteers and compared two OCT instruments to contact ultrasound on the same eyes. The agent selected the Visante comparison. The article reports a young mean age; adult-only eligibility was left conditional. The search stage can select a second paper. This run selected one. A fresh modeling context received only the unaltered question and the selected scientific text. It could not initiate a further retrieval after handoff. [Actual retrieval decisions and calls](SEARCH_AUDIT.json) · [Independent reading](SOURCE_READING.md)

The audit reconciled the actual six search-model responses with the dispatched queries, opened papers and final choice. The three modeling requests contained the same byte-verified source block. Among 13 declared evidence/assumption entries, 11 included a locator mapping to the delivered study. Two unmapped entries were explicitly assumed ultrasound parameters. A mapped citation establishes source attribution; factual agreement was assessed separately. In each table the generic replay returned one match to reported precision, one descriptive numerical difference, seven unresolved items and four items without a comparable source target. [Post-run model and table audit](MODEL_AUDIT.json)

## Same analysis on every delivered cohort

| Quantity | Paired Gaussian primary | Heavy-tailed difference model (t, 5 df) | Independent check of the source |
|---|---:|---:|---|
| Mean Visante minus ultrasound, µm | −3.60 | −3.60 | −3.6 in narrative and Table 3 |
| Eyes with absolute difference strictly greater than 20 µm | 22/10,000 (0.22%) | 89/10,000 (0.89%) | Measured count not tabulated; no paired public file identified |
| Mean Visante thickness, µm | 536.4 | 536.4 | 520.5 in Table 1 |
| Mean ultrasound thickness, µm | 540.0 | 540.0 | 524.2 in Table 1 |

The evaluator recomputed the two requested estimands from the raw paired thickness columns for every scenario and seed. The sampler fixes distribution quantiles and permutes them across rows. All three seeds therefore give the same threshold count within each scenario. They measure repeat execution rather than three independent sources or fitted models. The authors reported agreement limits adjusted for repeat measurement error. Turning those limits into an SD for individual paired records requires an assumption about which reading protocol those records represent. The two generated rates differ by 0.67 percentage points; neither has been empirically validated in this population. [All independently recomputed estimates](SCIENCE.json) · [Original agreement table](https://pmc-oa-opendata.s3.us-east-1.amazonaws.com/PMC3343442.1/ymj-53-634-i003.jpg)

Four tables in the public article were supplied as images. The retrieved payload preserved the scientific prose but delivered none of those table cells. The agent marked the ultrasound level 540 µm and spread 30 µm as assumptions and used the source paired bias to generate Visante measurements. Both resulting means exceed Table 1 by about 16 µm. The common offset cancels in the requested signed difference. This is a concrete reason to grade the data by intended use and also check the individual measurement columns. A future retrieval-stage enhancement should inventory image-only tables and expose their verified aggregate cells or signal the precise evidence gap before a source is chosen. This run was not tuned after independent table inspection. [Independent read of both instruments](SOURCE_READING.md) · [Original measurement table](https://pmc-oa-opendata.s3.us-east-1.amazonaws.com/PMC3343442.1/ymj-53-634-i001.jpg)

## Execution and reproducibility

The completed run used gpt-6.1-sol (medium), six search decisions at an estimated $0.139595 and three modeling calls at $0.1595555. The usage-based estimate is $0.2991505. An earlier initial request in r01 was rejected with HTTP 400 before a search occurred because JSON output mode required the word JSON in the input as well as the instructions. It had no returned usage and remains archived separately. The corrected run retained the same scientific request and design. Direct identifiers, full articles, API bodies, virtual rows and gateway caches stay under the ignored private run directory. The aggregate results, code and tests are local project artifacts.

To run a new research request, execute the following from this directory with a fresh root and a UTF-8 request file. An existing run path resumes from verified receipts. A settled provider error stays recorded. The source and model audits run without further paid calls.

~~~text
python -B run.py --root private/new_study --request REQUEST.txt
python -B search_audit.py private/new_study NEW_SEARCH_AUDIT.json
python -B verify_model.py private/new_study REQUEST.txt --output NEW_MODEL_AUDIT.json
~~~

Fourteen local tests passed, covering discovery, table rendering, source identity, frozen handoff, tamper detection and numerical evaluation. The CCT-specific analysis in score_final.py consumes the agent's actual measurement names and checks units. Scientific modeling and the search controller have no case-specific constants for the two instruments. [Pipeline entry](run.py) · [Independent CCT analysis](score_final.py)
