# Independent reading of paired corneal thickness in the selected study

The retrieval agent selected one article, PMC3343442. This reading used the sealed article text and the original study's aggregate tables in the PMC archive. The reader had no access to the model, its generated tables or participant measurements. The retrieval manifest records 40 of 40 prose blocks and zero machine-readable tables. The original JATS has four table wrappers carrying JPEGs, so complete text-block coverage did not deliver their numerical cells to the author. [Selected paper](https://doi.org/10.3349/ymj.2012.53.3.634) · [Archived article and figures](https://pmc.ncbi.nlm.nih.gov/articles/PMC3343442/)

## Population and measurement pair

The study enrolled 30 healthy volunteers and analyzed 50 eyes, since a volunteer could contribute one or both eyes. Mean age was 27.0 years (SD 2.9). The measured cohort had 21 men and nine women. The investigator excluded previous ocular surgery, recent contact lens wear and clinically abnormal corneas, among other criteria. Participants attended three visits in four weeks. For the inter-device agreement analysis, the team averaged three successive measurements from visit two within each eye and instrument. Eye counts describe the denominator; the 50 eyes came from 30 people. [Article, methods and results](https://pmc.ncbi.nlm.nih.gov/articles/PMC3343442/)

There are two legitimate, different OCT definitions. RTVue is Fourier-domain, pupil-centered OCT and Visante is time-domain, centered at the corneal vertex; both return the average central 2 mm thickness. The comparator is contact ultrasound with the probe mounted on a slit lamp after topical anesthesia. Time of day and protocol were controlled, and the order of the OCT examinations was randomized before the ultrasound measurement. Choosing a specific OCT instrument determines which source statistics apply. These are measurements in µm of the same eye by each instrument. [Original methods](https://doi.org/10.3349/ymj.2012.53.3.634)

## Numerical evidence

| Instrument pair | Visit-two Table 1 CCT, mean (SD), µm | Table 3 mean OCT minus ultrasound (95% CI), µm | Lower and upper 95% agreement limits, µm |
|---|---|---:|---:|
| RTVue and SL-US | 524.7 (27.8) and 524.2 (27.4) | +0.5 (−0.7 to +1.7) | −7.8 to +8.8 |
| Visante and SL-US | 520.5 (27.7) and 524.2 (27.4) | −3.6 (−5.3 to −2.0) | −14.9 to +7.6 |

The table cells above were transcribed independently from two of the original table images. Visit-to-visit reproducibility in Table 2 uses a distinct set of observations and its SDs answer a different question. Subtracting the two displayed Table 1 means yields −3.7 µm for Visante minus ultrasound whereas the paired contrast in Table 3 rounds to −3.6 µm. The latter is the direct study estimate. The printed means have limited precision. [Table 1](https://pmc-oa-opendata.s3.us-east-1.amazonaws.com/PMC3343442.1/ymj-53-634-i001.jpg) · [Table 3](https://pmc-oa-opendata.s3.us-east-1.amazonaws.com/PMC3343442.1/ymj-53-634-i003.jpg)

The delivered prose directly states the Visante-minus-SL-US bias and the +4.1 µm RTVue-minus-Visante bias. Adding the two reported central values gives an approximate +0.5 µm RTVue-minus-SL-US bias. The largest absolute endpoint of the agreement interval is described as 8.8 µm for RTVue and 14.9 µm for Visante against SL-US. These endpoints describe expected agreement and do not represent measured sample maxima. The authors explicitly corrected the SD of paired differences to account for repeat-measurement error removed by averaging. Under the usual limits of bias ±1.96 SD, interval widths imply corrected SDs near 4.23 and 5.74 µm, respectively. These are estimates for the corrected agreement calculation; reconstructing the distribution of visit-two averages requires accounting for the correction. A within-instrument repeatability coefficient or intraclass correlation answers a separate question. [Original methods and Table 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC3343442/)

## Evidence for the 20 µm threshold

The text, table summaries and agreement limits supply no exact count of eyes with absolute paired difference strictly greater than 20 µm. The SD and limits alone cannot identify this probability. The article contains plotted individual points, excluded by the study protocol. Its JATS and the archived article files did not identify a downloadable participant-level paired dataset. The audit did not digitize the plots, infer a zero observed count from the 95% limits or open individual data. Consequently a generated threshold percentage can be scored for internal reproducibility and source compatibility. Direct empirical validation of that percentage is unavailable from the reviewed material. [Published article](https://doi.org/10.3349/ymj.2012.53.3.634)

The sealed text bundle SHA-256 is `e324ea672eadcafa191ad13ebe20d2c41a94f8b94e1479567c53b1baa61170d2`. The original Table 1 image hash is `a5461f365098065da5283a48d7e9d26201f340ad8df19f0d4ec8098a3cfe30d3`; the Table 3 image hash is `c13b2153251a012a5055d5edbd0b99f7310d77a789173f2500e05bec8f33afbf`.
