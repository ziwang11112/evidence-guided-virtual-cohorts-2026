# Evidence-to-generation development comparison

All scheduled initial and final deliveries are retained below. Reference intervals are reused community-cluster CR1-t intervals for an already-exposed selected sample. Synthetic intervals condition on the submitted model and draw. Seed ranges are Monte Carlo variation, not reference uncertainty or independent clinical replication.

Physical attempts: 4; final choice: retain.

## primary

| Term | Reference estimate [95% CI] | Initial seed range | Final seed range |
|---|---:|---:|---:|
| bmi | 0.0224642 [0.0152595, 0.0296689] | 0.00380346 to 0.018107 | 0.00380346 to 0.018107 |
| glucose | 0.392909 [0.361754, 0.424064] | 0.28417 to 0.313682 | 0.28417 to 0.313682 |
| age | 0.00810704 [0.00638704, 0.00982703] | 0.00841987 to 0.0108417 | 0.00841987 to 0.0108417 |
| female | 0.025989 [-0.00776095, 0.059739] | -0.0914339 to -0.0512354 | -0.0914339 to -0.0512354 |

## descriptive secondary

| Term | Reference estimate [95% CI] | Initial seed range | Final seed range |
|---|---:|---:|---:|
| bmi | 0.0549461 [0.0457262, 0.0641659] | 0.0421676 to 0.0517584 | 0.0421676 to 0.0517584 |
| age | 0.0153037 [0.0132208, 0.0173866] | 0.0161254 to 0.0177095 | 0.0161254 to 0.0177095 |
| female | -0.0452957 [-0.0897137, -0.000877619] | -0.0515715 to -0.0310825 | -0.0515715 to -0.0310825 |

## Delivery inventory

| Stage | Seed | Run | Status | Initial alias |
|---|---:|---|---|---|
| initial | 7401 | b_initial_delivery_7401 | success | False |
| initial | 7402 | b_initial_delivery_7402 | success | False |
| initial | 7403 | b_initial_delivery_7403 | success | False |
| final | 7401 | b_initial_delivery_7401 | success | True |
| final | 7402 | b_initial_delivery_7402 | success | True |
| final | 7403 | b_initial_delivery_7403 | success | True |

REPORT.json contains every intercept and nonintercept coefficient, conditional synthetic interval, distribution summary, correlation and raw difference for every delivery slot, including failures. No favorable-result filter or equivalence threshold is applied.

This comparison cannot identify an effect of evidence search, model revision or author choice. Agreement does not establish clinical validity, causal effects, transportability, or publication readiness. Separate reviewer recomputation is required before final delivery.
