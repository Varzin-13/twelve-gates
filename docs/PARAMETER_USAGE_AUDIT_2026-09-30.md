# Twelve Gates — Parameter Usage Audit

**Date:** 2026-09-30  
**Scope:** software reachability/usage, not empirical validity.

The machine-readable source is:

`simulations/parameter_usage_registry.json`

## Why this exists

A configuration can look detailed while some of its variables never affect the
model. That creates false confidence: a reader may assume a mechanism is
simulated merely because its parameter appears in a config file.

v0.32 therefore distinguishes:

- **ACTIVE** — directly changes current ABM state transitions or reported outputs;
- **PARTIAL** — used in a limited path but does not implement the broader construct;
- **DIAGNOSTIC_ONLY** — computed/stored but does not drive main transitions;
- **INERT_MAIN_ABM** — present but currently has no effect on main ABM dynamics;
- **INTERFACE_ONLY** — enforced in a separate formal/interface layer, not coupled
  to behavioral dynamics.

These labels describe code usage only. ACTIVE does not mean calibrated or valid.

## Important findings

### Inert in the main ABM
Examples currently include:

- `time.budget_review_period_ticks`;
- `budget.reallocation_rule`;
- `coalitions.theta_audit`;
- `coalitions.crisis_divergence_max`;
- `gate.memory_dependence`;
- core behavioral effects of `mirror13.*`;
- `gate_zero.admission_threshold`;
- `gate_zero.measurement_noise_sd`;
- `gate_zero.appeal_board`;
- `civil_society.mobilization_capacity`;
- `civil_society.oversight_strength`;
- `civil_society.media_visibility`;
- `civil_society.union_density_proxy`.

These must not be described as if the current ABM tests their effects.

### Partial
Important partial mechanisms include:

- `gate.external_exposure`: shocks update it, but it currently has no downstream
  causal use;
- `gate.decision_backlog`: can trigger proposals and is decremented, but there
  is no endogenous increment path in the main model;
- bureaucracy service continuity/archive integrity: can be damaged by a system
  disaster, but are not yet fully coupled to service/decision outcomes;
- civil-society legitimacy signal: active only as an internal smoothing proxy,
  not survey-based public legitimacy;
- armed-bloc behavior: implemented conditionally, but baseline contains zero
  armed-bloc agents.

### Diagnostic only
`gate.coalition_propensity` is computed but coalition formation uses the
bilateral pair-score mechanism instead.

`gate_zero.entropy_manipulability` is exposed as a helper metric but does not
drive the main ABM.

## Rule for future development

An inert or partial parameter must not be made ACTIVE merely by inventing a
probability or coefficient.

Activation requires:
1. a defined causal mechanism;
2. a testable state transition;
3. provenance for all new numbers;
4. targeted and negative-control tests;
5. an explicit claim boundary.

If those conditions are not met, keeping the mechanism visibly inert is more
scientifically honest than adding unsupported behavior.
