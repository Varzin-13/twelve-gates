# v0.32 Coalition Structural Robustness

**Claim class:** exploratory structural uncertainty  
**Calibration:** no  
**Design:** 3 pair aggregations × 3 theta values × 12 common seeds

The modes are mathematical alternatives/bounds, not institutional recommendations.

## Mode definitions

- `minimum`: pair strength equals the weaker directional assessment.
- `mean`: current v0.32 baseline; arithmetic mean of the two directions.
- `maximum`: permissive bound; pair strength equals the stronger direction.

## Modeled cartel-capture frequencies

| aggregation | θ=0.575 | θ=0.600 | θ=0.625 |
|---|---|---|---|
| minimum | 0.833 | 0.583 | 0.000 |
| mean | 0.833 | 0.417 | 0.000 |
| maximum | 0.917 | 0.583 | 0.000 |

## Censoring-aware coalition summaries

| aggregation | theta | RMST ticks (mean valid runs) | right-censored fraction |
|---|---:|---:|---:|
| minimum | 0.575 | 92.965 | 0.119 |
| minimum | 0.600 | 128.271 | 0.150 |
| minimum | 0.625 | n/a | n/a |
| mean | 0.575 | 96.649 | 0.119 |
| mean | 0.600 | 114.107 | 0.148 |
| mean | 0.625 | n/a | n/a |
| maximum | 0.575 | 87.634 | 0.110 |
| maximum | 0.600 | 101.280 | 0.135 |
| maximum | 0.625 | n/a | n/a |

## Interpretation boundary

Differences across modes quantify structural model uncertainty under the current uncalibrated assumptions. They do not identify which institutional rule is correct or preferable.

A strong difference between modes is evidence that the simulation conclusion depends on structural form. It is not evidence for selecting the mode that produces any particular outcome.
