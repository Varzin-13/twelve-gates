# v0.32 Sensitivity Interpretation Audit

**Date:** 2026-09-30  
**Evidence class:** exploratory simulation only  
**Calibration:** none  
**Political prediction:** none

Source artifact:
`simulations/results/sensitivity_v032_lhs_results.json`

Design:
- 64 Latin-hypercube parameter points;
- 8 varied assumptions;
- 6 common seeds per point;
- 520 ticks per run;
- all parameter ranges explicitly marked `ARBITRARY_EXPLORATION_RANGE`.

## Main technical findings

### 1. Cartel/capture endpoint is parameter-sensitive
Across this finite exploration, modeled cartel-capture rate ranges from:

`0.000 -> 1.000`

with median point mean:

`0.250`.

Largest exploratory rank associations:
- `theta_pair`: **−0.708**
- material-cluster executive-power multiplier: **+0.540**
- vote-support intercept: **+0.211**
- trust-learning rate: **−0.207**

Therefore the single corrected-stress value `0.973333` must be interpreted as
the output of one uncalibrated parameter point. It is not robust across the
explored assumption space and is not a real-world probability.

### 2. Emergency time share is structurally dominated by its support assumption
The exploratory rank association between
`emergency_support_probability` and modeled emergency-time share is:

`rho = +0.982`.

The output range is relatively narrow:
`0.552244 -> 0.579808`.

This means the current emergency-time result is largely controlled by a
parameter that remains ARBITRARY. More Monte Carlo runs at one support
probability cannot solve that calibration problem.

### 3. Bureaucracy-politicization output is mechanically determined
The rank association between the configured bureaucracy drift rate and the
reported politicization proxy is effectively:

`rho = +1.000`.

Observed output range:
`0.207483 -> 0.921333`.

This is not an emergent empirical finding. It reveals that the present output
is mostly a deterministic transformation of the configured drift mechanism.
Until that mechanism has external evidence or competing structural models, the
output should be treated as a scenario proxy.

### 4. Internal legitimacy is driven by verification assumptions
Largest rank associations for modeled internal legitimacy:
- verification accuracy: **+0.825**
- trust-learning rate: **−0.497**

The civil-society legitimacy proxy shows almost the same pattern:
- verification accuracy: **+0.834**
- trust-learning rate: **−0.483**

This is expected because the current civil-society signal is smoothed from
internal gate legitimacy. The two outputs are therefore not independent
evidence.

### 5. Capture-pressure proxy has little discrimination in this design
Across the LHS:
`0.578942 -> 0.580000`.

A nearly constant output is not useful for distinguishing most mechanisms in
this explored region. Its formula or target role should be reconsidered before
giving it interpretive weight.

### 6. Coalition-duration field needs a censoring warning
The current legacy field `coalition_mean_duration` summarizes durations of
coalitions that have dissolved. Coalitions still active at the end of a run are
not included as completed durations.

The LHS range (`0 -> 157` ticks) therefore combines parameter sensitivity with
right-censoring/empty-history behavior. It must not be read as an unbiased
estimate of the lifetime of all coalitions.

A future output schema should distinguish:
- dissolved-coalition duration;
- active-coalition age at censoring;
- survival/censoring-aware summaries.

This observation does not require changing the already-frozen v0.32 LHS
artifact.

## Consequence for the research program

The LHS accomplishes its intended falsification role: it shows that several
headline simulation outputs are dominated by uncalibrated model assumptions.

The next scientifically defensible step is **not** to increase Monte Carlo
replicates at the baseline point. It is to:
1. reduce or empirically map influential arbitrary parameters where possible;
2. compare plausible alternative submodels;
3. separate calibration targets from holdout validation patterns;
4. retain the full uncertainty/instability record.

No result in this document ranks or predicts real political actors or
institutional proposals.
