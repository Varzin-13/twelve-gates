# v0.32 Latin-Hypercube Behavior-Space Exploration

**Claim label:** exploratory hypothesis  
**Calibration:** no  
**Empirical validation:** no  
**Design:** 64 LHS points × 6 common seeds × 520 ticks

All parameter ranges are arbitrary exploration ranges.

## Output ranges

| Output | Min | Median | Max |
|---|---:|---:|---:|
| cartel_capture_rate | 0.000000 | 0.250000 | 1.000000 |
| emergency_time_share_mean | 0.552244 | 0.562179 | 0.579808 |
| coalition_mean_duration_mean | 0.000000 | 22.240120 | 157.000000 |
| legitimacy_internal_mean | 0.572105 | 0.615576 | 0.624620 |
| capture_pressure_mean | 0.578942 | 0.580000 | 0.580000 |
| bureaucracy_politicization_mean | 0.207483 | 0.561503 | 0.921333 |
| civil_society_legitimacy_proxy_mean | 0.572322 | 0.615745 | 0.624527 |

## Exploratory rank correlations

These are Spearman rank correlations across the 64 LHS point means. They are screening statistics, not causal coefficients or significance tests.

### cartel_capture_rate
- theta_pair: -0.708
- material_exec_multiplier: +0.540
- vote_support_intercept: +0.211
- trust_learning_rate: -0.207
- audit_detection_prob: +0.109
- verification_accuracy: +0.091
- emergency_support_probability: +0.030
- bureaucracy_drift_rate: -0.011

### emergency_time_share_mean
- emergency_support_probability: +0.982
- verification_accuracy: +0.089
- trust_learning_rate: -0.087
- bureaucracy_drift_rate: -0.085
- theta_pair: +0.064
- vote_support_intercept: -0.057
- audit_detection_prob: +0.053
- material_exec_multiplier: +0.018

### coalition_mean_duration_mean
- theta_pair: -0.483
- audit_detection_prob: -0.446
- material_exec_multiplier: +0.219
- emergency_support_probability: -0.147
- vote_support_intercept: +0.119
- trust_learning_rate: -0.088
- verification_accuracy: +0.046
- bureaucracy_drift_rate: +0.007

### legitimacy_internal_mean
- verification_accuracy: +0.825
- trust_learning_rate: -0.497
- audit_detection_prob: -0.194
- emergency_support_probability: +0.093
- vote_support_intercept: -0.069
- bureaucracy_drift_rate: +0.062
- material_exec_multiplier: +0.040
- theta_pair: -0.003

### capture_pressure_mean
- vote_support_intercept: -0.263
- bureaucracy_drift_rate: +0.237
- emergency_support_probability: -0.181
- theta_pair: -0.076
- verification_accuracy: +0.076
- audit_detection_prob: -0.070
- trust_learning_rate: -0.044
- material_exec_multiplier: -0.001

### bureaucracy_politicization_mean
- bureaucracy_drift_rate: +1.000
- trust_learning_rate: -0.145
- emergency_support_probability: -0.062
- theta_pair: +0.020
- audit_detection_prob: -0.019
- material_exec_multiplier: -0.012
- vote_support_intercept: +0.011
- verification_accuracy: -0.001

### civil_society_legitimacy_proxy_mean
- verification_accuracy: +0.834
- trust_learning_rate: -0.483
- audit_detection_prob: -0.176
- emergency_support_probability: +0.088
- vote_support_intercept: -0.067
- bureaucracy_drift_rate: +0.057
- material_exec_multiplier: +0.048
- theta_pair: -0.012

> **Metric note:** `coalition_mean_duration_mean` is based on the legacy dissolved-coalition duration field. Active coalitions at run end are right-censored; see `SENSITIVITY_V032_INTERPRETATION_AUDIT.md`.

## Interpretation boundary

Rank correlations and output ranges describe this finite exploratory design only. They are not causal effects, calibrated estimates, or real-world political probabilities.

The full JSON preserves every LHS point, parameter vector, common seed set, point-level output, and provenance hash.
