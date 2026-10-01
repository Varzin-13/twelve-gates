# v0.32 LHS Sensitivity — Post Budget-Majority Fix

**Claim class:** exploratory hypothesis  
**Calibration:** no  
**Design:** 64 paired LHS points × 6 common seeds × 520 ticks

Same design and run seeds as the pre-budget LHS; only the code/config lineage is updated.

## Paired impact on modeled cartel-capture point means

- changed LHS points: 10 / 64
- mean difference: +0.018229
- mean absolute difference: 0.033854
- max absolute difference: 0.500000

## Post-fix exploratory rank correlations for cartel-capture rate

- theta_pair: -0.707
- material_exec_multiplier: +0.577
- trust_learning_rate: -0.231
- vote_support_intercept: +0.223
- audit_detection_prob: +0.123
- emergency_support_probability: +0.057
- bureaucracy_drift_rate: -0.052
- verification_accuracy: +0.005

## Post-fix output ranges

| output | min | median | max |
|---|---:|---:|---:|
| cartel_capture_rate | 0.000000 | 0.333333 | 1.000000 |
| emergency_time_share_mean | 0.552244 | 0.561538 | 0.579808 |
| coalition_rmst_ticks_mean_valid_runs | 19.758891 | 67.463240 | 208.708333 |
| legitimacy_internal_mean | 0.572105 | 0.615321 | 0.624620 |
| capture_pressure_mean | 0.579580 | 0.580000 | 0.580000 |
| bureaucracy_politicization_mean | 0.207483 | 0.561503 | 0.921333 |
| civil_society_legitimacy_proxy_mean | 0.572322 | 0.615511 | 0.624527 |
| proposal_pass_fraction_mean_valid_runs | 0.440190 | 0.863614 | 0.996872 |

## Interpretation boundary

Paired exploratory behavior-space comparison after a software-rule correction. Rank correlations are screening statistics, not causal effects or real-world political probabilities.
