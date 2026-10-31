# Cross study virtual cohort minimum experiment

Status: protocol and source preparation, 25 October 2026. This is a methods
feasibility experiment. No new biological discovery is required. Two real-study
families are selected; different queries or generator seeds are not new cases.

## Question and contribution

Does an Agent's joint virtual-cohort representation improve predictions of
relationships in an entire withheld study over the same Agent doing numerical
inference without participant records and over conventional statistical transfer?
The potential contribution is evidence integration and transport with uncertainty.
Generating more records, reproducing disclosed moments, and recovering a familiar
obesity association are not by themselves innovations.

This first screen provides complete small source-summary panels, rather than
messy paper extraction. It tests cross-study transfer under a favorable input
condition. It does not yet test sparse evidence completion, autonomous literature
review, privacy, causal inference or replacement of patient recruitment.

## Selected cases

| Case | Source studies | Reserved target | Variables and primary query |
|---|---|---|---|
| Population transport | Rich Healthcare, China; NHANES 2011–12, USA | NAGALA, Japan | BMI and natural-log fasting TG, conditional on age and recorded sex |
| Intervention transport | WLM and STRRIDE-PD, six months | DIETFITS, six months | Log weight ratio and log HOMA-IR ratio, conditional on sex and log baseline TG |

The population case is selected health-screening populations, not exclusively
obesity. The second case is concurrent change, not a baseline forecast or a causal
effect of achieved weight loss. Detailed access, units and source papers are in
CASE_POPULATION_AUDIT.md and CASE_INTERVENTION_AUDIT.md.

Population analysis: age 20–75 inclusive, fasting plasma glucose >0 and <6.1
mmol/L, positive BMI/TG, sex coding present, complete four-variable rows.
For NHANES additionally require DIQ010=2, not recorded pregnant, fasting >=8.5
and <24 hours, and positive fasting-subsample weight. Use fasting weights for
the source moments and a stratified delete-PSU jackknife for Fisher-z standard
errors. These weighted US source moments do not turn the Japanese target into
a US-population estimand. Rich and NAGALA retain their study-sample estimands.
Residual medication/alcohol/selection differences remain explicit.

Intervention analysis: complete paired positive weight, fasting insulin and
glucose at baseline/six months; positive baseline TG; known sex. Source signed
percent changes convert to log ratios as log1p(change/100); target log HOMA ratio
is log(I6*G6/(I0*G0)). No outcome-based trimming. Source conventional percent
definition is supported by the paper's signed-percent examples and tables but
cannot be independently reconstructed without the unreleased absolute pairs.
Report that limitation. Age is excluded from the common first-pass adjustment.
WLM selected successful weight losers, STRRIDE mixes four intervention arms,
and DIETFITS is a younger dietary cohort. Neither sources nor target are assumed
exchangeable without uncertainty.

Each case has four ordered variables [X, Y, Z, female]. Population: [BMI, logTG,
age, female]; intervention: [logWeightRatio, logHOMARatio, logBaselineTG, female].
Three queries, fixed before target statistics, are:

1. Q1: partial correlation X,Y conditional on Z and female (primary).
2. Q2: partial correlation X,Z conditional on female (secondary).
3. Q3: partial correlation Y,Z conditional on female (secondary).

All three use the same complete-case participants in each study. The frozen
queries are disclosed in this minimum experiment; a later reusable-analysis claim
requires hidden queries revealed only after the joint representation is frozen.

## Shared information

Each method receives the same masked-source packet: recruitment/measurement
descriptors, study-specific means/covariances and sample sizes, sex composition,
the three source partial correlations and Fisher-z standard errors. Means and
covariances use one common analysis set, not incompatible pairwise deletion.
Target input contains recruitment/measurement eligibility only; no target
participant values, means, covariance, subgroup effects or results.

All measured relationships in the source studies are admissible; the unseen
relationships are in the target study. Do not describe source-summary construction
as automatic extraction from published tables. Keep studies separate so large N
does not erase between-study heterogeneity.

Fresh experimental Agent contexts get only the packet and task instructions, no
parent history, no web/retrieval and no target paths. This is procedural isolation
on a shared host, not an enforced filesystem security boundary. Public-study
pretraining contamination cannot be excluded. Keep study names out of experimental
packets, while keeping original provenance in custodian files.

## Comparators

A. Direct Agent: infer a reusable covariance/conditional model and forecast all
three relationships with uncertainty. Numerical tools and parameter sampling are
allowed. Participant-level synthetic records are not allowed.

B. Cohort Agent: infer a joint generator from the same evidence; use a numerical
sampler to make explicitly synthetic analysis records; apply the fixed analyses.
Record assumptions and distinguish parameter/transport uncertainty from Monte
Carlo error. Do not hand-type hundreds of patient rows. Continuous transformed
variables and recorded binary sex must have valid support.

C. Conventional statistics: per-query normal-normal random-effects prediction on
Fisher z, flat location prior, half-normal heterogeneity SD=0.1 (sensitivities .05,
.2). A new study's variance includes heterogeneity, not just pooled-mean error.
Also retain each single-source forecast with 0.1 transport SD so a poor pooling
assumption cannot create a spurious Agent win. A joint Gaussian/covariance sampler
under an identical fitted model is a numerical equivalence control, not a new
independent inferential method. Before a publication-level claim, add a fully
joint hierarchical copula/transport comparator using the identical constraints.

Agent arms use the same inherited model settings and maximum task/tool budget.
Backend model identifier/token usage are recorded only if exposed; never invent
an API version. Initial launch may use one run per arm as an execution check;
three fresh runs per arm/case must be frozen together before opening targets for
the comparative screen. No selection of the best seed. Maximum one source-only
repair per run for invalid numeric/schema output. No target feedback or retuning.

## Evaluation

Primary: squared prediction error for Q1, separately by case and equal-case mean.
Secondary: mean squared error across the three fixed queries, sign, interval
score, computational cost and structural failures. All runs and sensitivities
are shown. Method selection cannot switch from Q1 to a favorable secondary.

The observed target correlation has sampling uncertainty. After forecast lock,
bootstrap target participants (paired visits stay together) to assess uncertainty
in paired method loss differences. Add centered target-estimation errors on the
Fisher scale to each method's frozen latent-relationship draws for predictive
80%/95% intervals and standard WIS. Do not count a large generated N as clinical
evidence or call three correlated queries a calibration study.

Targets are opened only after forecast artifacts, protocol, packet, analysis
code and hashes are frozen. Record all sources/outputs and exact access times.
Any target used to debug an analysis becomes development data thereafter.

## Minimal execution and stopping rules

1. Save public data, verify hashes, harmonize units, audit eligibility and pairing.
2. Produce source packets; run known-truth numerical checks; freeze protocol.
3. Run A/B fresh contexts and C on identical packets. Validate outputs using only
   source evidence and numerical constraints. Freeze all predictions.
4. Evaluate the two reserved studies once, retain every outcome, then decide.

Advance only if B's benefit over A and capable C is interpretable and not merely
one fortunate run or a smaller unjustified interval. With two cases, a useful
signal justifies a larger untouched benchmark; it does not establish superiority.
If A matches B, investigate whether the useful component is evidence integration
rather than cohort generation. If C matches or beats both with lower cost, stop
system expansion unless a specific new information-use hypothesis justifies a
separate pilot. Imprecise comparisons remain inconclusive.

No arbitrary clinical-benefit margin is asserted here: this screen ranks forecast
losses and uncertainty rather than claiming a clinically meaningful gain. No model
training, HPC, wet experiment or patient recruitment is needed for this screen.

## Immediate status

Raw population files and intervention metadata are accessible. The source packet
and numerical controls can be prepared without target effects. Any results file
must distinguish preparation, source-only computations, synthetic checks and real
target evaluation. The original audits are recommendations; this protocol fixes
the operative estimands when their wording differs.

Variance implementation fixed before forecasts: NHANES uses the complete
demographic stratum/PSU roster before domain filtering. PSUs with no eligible
records remain implicit zero-domain-weight units. Within stratum h with m_h
PSUs, deleting one PSU multiplies the other domain weights in that stratum by
m_h/(m_h-1); variance is the sum of (m_h-1)/m_h times squared Fisher-z deviations
of each replicate from the full-sample estimate (MSE centering). Rich uses the
15 observed analysis sites for a delete-site jackknife, centered on the mean
of site-delete replicate estimates. These source standard errors do not include
transport uncertainty; the conventional new-study forecasts add that separately.
