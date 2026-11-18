# Related work and comparison wording for the next KDD draft

## Related work

LLMSynthor synthesizes micro-records by inferring relevant variable subsets and using discrepancies in marginal and joint frequency tables to plan successive batches. Its mobility study also combines aggregate information from multiple sources. In our original-paper setting, the inputs include measurement definitions, coefficients and covariance information reported for different populations and adjustment sets. The scientific Agent determines how those quantities enter a reusable generative program and records the assumptions needed to apply that program to the requested cohort. We evaluate the resulting data by rerunning prespecified scientific analyses on the synthetic and measured samples. [Tang et al., KDD 2026](https://doi.org/10.1145/3770855.3818965).

## How to read the method comparisons

We evaluate three distinct questions. The HRS reconstruction matches the published recipient-side law and the Agent on fitted source exports and a common longitudinal mixed model. A request-only experiment matches the model, tools and resource ceilings between the organized workflow and an ordinary Agent. The blood-pressure and iron experiments vary the availability of joint evidence while retaining the downstream analyses and reference. The HRS test addresses source-rich reconstruction, the ordinary-Agent experiment addresses workflow choice, and the evidence controls address the value of information for particular analyses. All three comparisons retain mixed results and use their originally defined reported scope.

## Supplementary note on aggregate control

An original two-way threshold-frequency table in the iron case supplies an exact aggregate control of the type used by LLMSynthor. Recovering the source threshold frequencies also recovers the source odds ratio algebraically. Two mathematical constructions matching those frequencies and both continuous marginals nevertheless have Spearman correlations of 0.171 and 0.985. The difference illustrates the additional assumptions required for a continuous downstream analysis. In the blood-pressure case, conversion of a source moment block into joint frequency tables similarly requires information or assumptions about distributional shape. The [feasibility audit](FEASIBILITY.md) records these scope restrictions and provides the reproducible calculations.

The published LLMSynthor results remain related-work evidence. The inspected author repository had no executable implementation. A source-frequency adaptation would address a narrower task than the reported end-to-end biomedical study. No relative performance estimate is claimed against LLMSynthor.
