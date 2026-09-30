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
| minimum | 0.833 | 0.667 | 0.000 |
| mean | 0.833 | 0.500 | 0.000 |
| maximum | 1.000 | 0.667 | 0.000 |

## Censoring-aware coalition summaries

| aggregation | theta | RMST ticks (mean valid runs) | right-censored fraction |
|---|---:|---:|---:|
| minimum | 0.575 | 95.844 | 0.115 |
| minimum | 0.600 | 127.886 | 0.148 |
| minimum | 0.625 | n/a | n/a |
| mean | 0.575 | 94.612 | 0.112 |
| mean | 0.600 | 122.122 | 0.145 |
| mean | 0.625 | n/a | n/a |
| maximum | 0.575 | 77.055 | 0.094 |
| maximum | 0.600 | 106.875 | 0.128 |
| maximum | 0.625 | n/a | n/a |

## Interpretation boundary

Differences across modes quantify structural model uncertainty under the current uncalibrated assumptions. They do not identify which institutional rule is correct or preferable.

A strong difference between modes is evidence that the simulation conclusion depends on structural form. It is not evidence for selecting the mode that produces any particular outcome.
