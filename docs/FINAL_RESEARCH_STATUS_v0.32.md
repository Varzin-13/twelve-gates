# Twelve Gates v0.32 — Final Research Status

**Status:** reproducible research release candidate
**Scope:** institutional-design research + executable hypothesis model
**Implementation readiness:** not established
**Accepted empirical parameter mappings:** 0
**Political ranking/endorsement:** none

This is the single technical status entry point for v0.32. Historical reports remain in the repository for provenance.

## 1. What v0.32 contains

v0.32 combines:
- a public institutional-design layer;
- an executable twelve-gate ABM used as a hypothesis model;
- regression tests, finite-state checks and a TLA+ research skeleton;
- parameter-provenance, calibration and active/inert-mechanism registries;
- frozen simulation artifacts protected by Git blob hashes.

These layers make assumptions inspectable and reproducible. They do not establish that the proposed institutions would work in practice.

## 2. Main software corrections

The v0.32 audit corrected or hardened:
- stress timing so the documented shock actually begins at tick 52;
- resource-share conservation after implementation;
- explicit emergency-extension votes and threshold logic;
- bilateral coalition scoring so execution order cannot overwrite one direction;
- coalition duration versus consecutive passed-decision streaks;
- dissent logging and deterministic proposal references;
- typed external-timeline events, including multiple events at one tick;
- hidden behavioral constants by moving them into explicit configuration;
- the documented two-thirds budget rule: 7/12 fails, 8/12 passes;
- numerical threshold equality with a small floating-point tolerance;
- coalition lifetime output with right-censoring-aware quantities and RMST;
- explicit refusal of undefined multi-target resource proposals;
- a non-vacuous resource-transfer transition in the TLA+ skeleton.

The repository does not claim a completed TLC verification run.

## 3. Current frozen stress lineage

Latest frozen stress artifact after the numeric-threshold correction:
- 300 runs × 520 ticks;
- modeled capture endpoint: 0.970000;
- emergency-time-share mean: 0.562167;
- weighted proposal-pass fraction: 0.876647;
- coalition RMST mean across valid runs: about 82.712 ticks;
- first coded-cartel coalition in captured runs: [0,2,4] in 291 runs.

These are outputs of the coded model under uncalibrated assumptions, not real-world political probabilities.

The preceding matched-seed lineage after the budget-majority correction had capture 0.976667. The numeric-threshold correction moved 7 runs false-to-true and 9 runs true-to-false, a net change of -0.006667.

## 4. Sensitivity and phase structure

Post-budget Latin-hypercube screening used 64 parameter points × 6 common seeds × 520 ticks.

The coded capture endpoint spans 0–1 across the exploratory space. Strongest exploratory rank associations were approximately:
- theta_pair: -0.707;
- material executive-power multiplier: +0.577;
- trust-learning rate: -0.231;
- vote-support intercept: +0.223.
The material-cluster baseline executive-power sum is 2.30 and the coded cartel power threshold is 1.8. For that triad alone the exact multiplier boundary is:

1.8 / 2.30 = 0.7826086957...

The refined phase map found zero modeled capture at multipliers 0.7750, 0.7800 and 0.7825 across the tested theta range. At 0.7827 and above, capture becomes possible and then decreases as theta rises. This shows that the power discontinuity is largely built into the coded threshold, while theta adds a stochastic coalition-formation transition.

## 5. Structural uncertainty

Three bilateral score aggregations were inspected as model alternatives only:
- minimum;
- mean — the current baseline;
- maximum.

At theta=0.600, post-budget modeled capture frequencies were 0.667, 0.500 and 0.667 respectively. This demonstrates structural-model uncertainty; it does not select a preferred institutional rule.

## 6. Mathematical audit-schedule results

For the documented +6 auditor rule over Z12:
- 12 unique ordered audit pairs are covered in one cycle;
- 132 non-self ordered pairs are possible;
- one cycle therefore covers about 9.09% of pair space;
- the +6 rule contains 6 reciprocal audit dyads per cycle.

The affine family contains 48 permutations; 36 are self-audit-free and 24 of those are also reciprocal-free within one cycle. An exhaustive exact-cover search inside this finite affine family found a minimum total of 6 reciprocal dyads for an 11-cycle exact cover. These are combinatorial facts, not recommendations.

## 7. Calibration status

simulations/calibration_registry.json accepts 0 empirical parameter mappings at this release stage.

Potential evidence sources are screened in docs/CALIBRATION_SOURCE_MATRIX_2026-09-30.md. No external index is copied directly into a behavioral parameter without a construct mapping, uncertainty model and validation plan.
## 8. Remaining gaps

Important mechanisms remain partial or inert:
- most Civil Society variables are not causally active;
- Mirror-13 behavioral effects remain largely outside the main ABM;
- Gate Zero has a bounded interface/state machine but no calibrated behavioral population model;
- external exposure has limited downstream causal use;
- bureaucracy continuity/archive variables are only partially coupled;
- baseline armed-bloc count is zero;
- public-legitimacy output is an internal proxy, not survey evidence;
- budget review-period semantics remain partial;
- no accepted empirical national calibration exists.

Leaving a mechanism visibly incomplete is preferable to inventing unsupported coefficients.

## 9. Frozen provenance

simulations/results/FROZEN_ARTIFACT_MANIFEST.json protects the major result files by Git blob SHA.

Rules:
- frozen artifacts are immutable provenance records;
- corrected outputs use new files rather than overwriting old ones;
- CI validates every frozen blob hash;
- historical and current lineages remain distinguishable.

This protection was added after a workflow race regenerated one historical structural artifact. Git history allowed exact restoration, and the restored artifact is now hash-frozen.

## 10. Reproduce

From the repository root:

    cd simulations
    python3 test_model.py
    python3 test_institutional_interfaces.py
    python3 validate_calibration_registry.py
    python3 validate_parameter_usage_registry.py
    python3 validate_frozen_artifacts.py
    python3 audit_schedule.py
    cd ..
    python3 formal/abstract_model_check.py

## 11. What v0.32 does not claim

v0.32 does not establish founding legitimacy, public acceptance, compliance by powerful actors, predictive accuracy for Iran, empirical superiority over another political arrangement, or implementation readiness.

For new readers: start with README.md, then this document, then the scientific/formal/ODD documents under docs/.
