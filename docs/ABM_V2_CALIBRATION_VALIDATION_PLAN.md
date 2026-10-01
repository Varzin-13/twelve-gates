# ABM v2 — Calibration, Sensitivity and Validation Plan

**Date:** 2026-09-30  
**Status:** methodological plan; no empirical calibration is claimed.

Primary methodological references:

- ODD protocol (Grimm et al., 2020):  
  https://jasss.soc.surrey.ac.uk/23/2/7.html
- Parameter estimation and sensitivity for ABMs (Thiele, Kurth & Grimm, 2014):  
  https://www.jasss.org/17/3/11.html
- Validation methods overview (Collins, Koehler & Lynch, 2024):  
  https://www.jasss.org/27/1/11.html
- V-Dem measurement methodology:  
  https://www.v-dem.net/about/v-dem-project/methodology/

## 1. Purpose-specific validation

Validation asks whether a model is adequate **for its intended purpose**.

Current purpose:
- mechanism inspection;
- falsification of internal assumptions;
- sensitivity discovery;
- generation of empirical questions.

Current purpose does **not** include national political forecasting.

## 2. Verification before calibration

Required software gates:
- regression tests pass;
- invariants pass;
- deterministic seeded replay passes;
- config provenance complete;
- historical outputs are never silently overwritten after code changes;
- code/config/result hashes recorded for confirmatory artifacts.

## 3. Parameter inventory

Every numeric input must be classified:
- DOCUMENT;
- DESIGN;
- EMPIRICAL;
- ARBITRARY.

An EMPIRICAL classification additionally requires:
- exact source/version/date;
- source population/context;
- transformation/mapping rule;
- measurement uncertainty;
- temporal validity window;
- justification for transfer into this model.

## 4. Behavior-space exploration

Before fitting, explore the model globally.

Candidate methods:
- Latin hypercube sampling for broad coverage;
- Morris screening for influential inputs;
- variance-based methods such as Sobol only after computational feasibility and
  output regularity are assessed;
- phase diagrams for threshold-driven outputs.

Outputs should include distributions, not only means.

## 5. Identifiability and equifinality

A parameter is not "estimated" merely because one value reproduces an output.

For every proposed calibration target:
- search for multiple parameter sets that reproduce the same pattern;
- quantify whether parameters are identifiable;
- report equifinal regions if they exist;
- do not convert a weakly identified parameter into a point claim.

## 6. Calibration targets should be patterns, not convenient numbers

Candidate target classes may include:
- distribution of institutional decision latency;
- emergency-duration patterns;
- coalition persistence/turnover patterns;
- verification error patterns;
- workload concentration;
- recovery time under infrastructure failure;
- bounded-pilot appeal/queue metrics.

A target is admitted only when its operational definition and source population
match the modeled construct closely enough to justify a mapping.

## 7. V-Dem mapping rule

V-Dem expert-coded variables estimate latent concepts and publish uncertainty.

Therefore:
- do not directly set a model parameter equal to a V-Dem point estimate;
- specify a mapping function;
- propagate credible-region uncertainty;
- test alternate mappings;
- retain the original indicator version and year;
- document whether the mapping is within-country, cross-country, or temporal.

If no defensible mapping exists, use V-Dem only as contextual evidence, not
calibration.

## 8. Calibration / validation separation

When data permit:
- calibration set and validation set must be separated by time, case, or outcome
  pattern;
- validation targets must not be used to tune parameters;
- model-selection decisions must be frozen before final validation;
- failed validation remains part of the record.

## 9. Global sensitivity

At minimum, include:
- coalition threshold;
- executive-power initialization;
- trust/affinity/overlap initialization;
- emergency support probability;
- verification reliability;
- behavioral constants bundle;
- bureaucracy drift;
- civil-society smoothing;
- shock timing/magnitude.

Report:
- main effects;
- interactions;
- discontinuities/phase transitions;
- output instability;
- parameter regions where conclusions change sign/category.

## 10. Stochastic uncertainty

For each parameter point:
- use enough independent seeds to estimate Monte Carlo uncertainty;
- report intervals for stochastic summaries;
- distinguish Monte Carlo error from parameter uncertainty;
- never treat many seeds at one arbitrary parameter point as empirical
  validation.

## 11. Structural uncertainty

Run competing plausible submodels where the mechanism itself is uncertain, for
example:
- alternate coalition aggregation rules;
- alternate emergency-vote dependence structures;
- alternate trust-update rules;
- alternate public-legitimacy dynamics.

If conclusions depend on one arbitrary structural choice, report that
dependence rather than selecting the favorable version.

## 12. Holdout human pilot

Before national-level interpretation, a bounded non-governmental pilot can test
process mechanics.

Possible measures:
- queue and decision latency;
- audit workload;
- appeal completion;
- rule-bypass attempts;
- missing-member handling;
- ledger consistency;
- comprehension;
- perceived representation.

Pilot results are local evidence. Generalization requires a sampling/inference
design.

## 13. Failure criteria

ABM v2 must remain non-predictive if any of the following holds:
- key outputs are dominated by arbitrary parameters;
- empirical mappings are weak or non-identifiable;
- validation patterns fail;
- structural alternatives reverse conclusions;
- uncertainty intervals are too broad for the intended inference;
- the target construct cannot be operationalized with available data.

## 14. Promotion rule

A claim may be promoted only when the evidence required for its class exists:

`implemented -> verified software behavior -> calibrated mechanism -> validated bounded claim`

There is no automatic promotion from reproducible simulation to real-world
political claim.
