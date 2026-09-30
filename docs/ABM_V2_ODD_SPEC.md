# Twelve Gates ABM v2 — ODD Model Specification

**Version:** draft 0.1  
**Date:** 2026-09-30  
**Claim boundary:** model-description and software-design artifact only.

This document follows the 2020 ODD (Overview, Design concepts, Details) protocol
for agent-based and individual-based models:

https://jasss.soc.surrey.ac.uk/23/2/7.html

ODD is used here to make the model reimplementable and auditable. It does not
make an uncalibrated model empirically valid.

## 1. Purpose and patterns

### Purpose
The Twelve Gates ABM is a **hypothesis model** for inspecting internal
consequences of explicitly stated institutional assumptions. It is intended to:

- expose hidden assumptions;
- test software/logical invariants;
- explore mechanism interactions;
- identify parameter-sensitive conclusions;
- generate falsifiable questions for later calibration or bounded pilots.

It is **not** intended to forecast a political transition or estimate the
probability of real-world outcomes.

### Patterns used for current evaluation
At v0.32, accepted empirical target patterns = **none**.

The current evaluation patterns are internal/model-based:
- rotation coverage and no self-audit;
- resource conservation;
- explicit emergency expiry/extension transitions;
- coalition formation/dissolution behavior;
- distinction between coalition duration and passed-decision streak;
- deterministic replay under frozen seed/config/code;
- stress scenario behavior under stipulated assumptions.

Any future empirical pattern must be registered separately with source,
measurement uncertainty, mapping method, and holdout rule.

## 2. Entities, state variables and scales

### GateAgent — 12 instances
State includes:
- gate id and domain;
- resource share;
- executive-power scenario value;
- coordination role;
- pairwise trust;
- pairwise policy affinity;
- coalition membership id;
- coalition propensity;
- information reliability;
- audit exposure;
- crisis load;
- internal legitimacy;
- capture-pressure proxy;
- external exposure;
- personnel-overlap risk;
- decision backlog;
- memory dependence;
- verification parameters.

### BureaucracyAgent — 1 instance
State includes:
- institutional memory stock;
- politicization-risk proxy;
- service continuity;
- archive integrity;
- geographic redundancy.

### CivilSocietyAgent — 1 instance
State includes:
- mobilization capacity;
- oversight strength;
- media visibility;
- union-density proxy;
- a variable currently named `public_legitimacy_signal`.

**Important:** the current legitimacy signal is updated substantially from
internal gate trust and is therefore not measured public opinion.

### ArmedBlocAgent — 0..N instances
State includes:
- field control;
- negotiation readiness;
- conflict-risk proxy;
- external dependency;
- organizational cohesion;
- path state.

The baseline configuration instantiates **zero** armed-bloc agents.

### Institutional subsystems
- Mirror13Subsystem;
- GateZeroProcess;
- EmergencyCourtProcess;
- TrustLedger;
- CoalitionRegistry;
- ExternalScenarioDriver.

Gate Zero and Mirror-13 additionally have bounded interface contracts in
`simulations/institutional_interfaces.py`; those interfaces enforce allowed
transitions/negative competence without inventing behavioral probabilities.

### Temporal scale
Baseline:
- one tick = 7 days;
- rotation period = 26 ticks;
- emergency fuse = 2 ticks;
- many runs use 520 ticks.

These scales are model inputs. Except where explicitly sourced from the design
document, they are not empirical constants.

## 3. Process overview and scheduling

Each model tick executes the following gate stages in order:

1. rotate roles;
2. apply shocks;
3. local assessment;
4. submit reports;
5. cross-verification;
6. generate proposals;
7. coalition negotiation;
8. voting;
9. implementation;
10. audit and record;
11. trust/legitimacy update.

After staged updates:
- emergency state is processed;
- critical reports receive final modeled status;
- coalitions are formed from bilateral pair scores;
- coalition dissolution is checked;
- tick advances.

The order matters and is therefore part of the model specification.

### v0.32 scheduling corrections
- stress driver is genuinely time-aware;
- external timeline preserves multiple same-tick events;
- coalition pair assessments preserve both directions;
- decision streaks change on decisions, not on passage of time;
- resource shares are conservation-checked/renormalized after implementation.

## 4. Design concepts

### 4.1 Basic principles
The model operationalizes a finite twelve-gate structure, rotating
coordination/audit roles, coalition dynamics, emergency authority, information
verification, and stylized institutional continuity.

### 4.2 Emergence
Outputs such as coalition structure, modeled capture, trust distribution, and
emergency share emerge from coded rules plus stochastic draws. Their emergence
inside the model does not establish real-world emergence.

### 4.3 Adaptation
Implemented adaptation is limited:
- pairwise trust changes after verification outcomes;
- coalition structure can form/dissolve;
- armed-bloc paths can transition if such agents are instantiated.

### 4.4 Objectives
Agents do not currently optimize a general utility function. Voting and
coalition behavior are heuristic/stochastic. This is a major modeling
simplification.

### 4.5 Learning
There is no general learning algorithm. Trust updating is the main adaptive
memory mechanism.

### 4.6 Prediction
The model is not currently licensed for real-world prediction. No empirical
calibration mapping is accepted in the calibration registry.

### 4.7 Sensing
Gate agents sense modeled reports, trust, affinity, crisis and audit variables.
Sensing is synthetic and does not yet model realistic information access,
latency, censorship, strategic deception, or measurement error in full.

### 4.8 Interaction
Implemented interactions include:
- cross-verification;
- voting;
- coalition pair scoring;
- coalition formation/dissolution;
- audit exposure;
- resource proposals.

### 4.9 Stochasticity
Randomness enters:
- report truth generation;
- verification calls;
- proposals;
- voting/dissent;
- emergency-extension support;
- emergency-court behavior;
- armed-bloc transitions.

Every confirmatory run must record seeds.

### 4.10 Collectives
Coalitions are modeled as collectives. v0.32 prevents silent overlapping
coalitions while each gate has a singular `coalition_id`.

### 4.11 Observation
Current reported outputs include:
- any modeled cartel capture;
- emergency time share;
- active coalition count;
- coalition duration;
- internal legitimacy;
- capture-pressure proxy;
- bureaucracy-politicization proxy;
- civil-society legitimacy signal.

Output names must not be interpreted as directly observed real-world
quantities unless a mapping is separately validated.

## 5. Initialization

The baseline initializes:
- exactly 12 gates;
- equal resource shares of 1/12;
- scenario-specific executive-power values;
- trust/affinity/overlap matrices;
- bureaucracy and civil-society proxy values;
- zero armed-bloc agents.

Most behavioral initial values are uncalibrated. The authoritative status of
each tracked parameter group is recorded in:
- `simulations/param_provenance.py`;
- `simulations/calibration_registry.json`.

## 6. Input data

### Current input classes
- JSON/Python configuration;
- optional typed external timeline;
- random seed.

### External timeline schema
Each event has:
- `tick`;
- `gate_ids`;
- optional `crisis_delta`;
- optional `exposure_delta`;
- optional `disaster`.

Multiple events at one tick are preserved and aggregated.

### Empirical input status
No external political dataset is currently accepted as a direct calibration
mapping.

For example, V-Dem expert-coded indicators are estimates of latent concepts
with uncertainty from a measurement model; a point estimate must not be copied
directly into a behavioral parameter without a mapping model and uncertainty
propagation.

V-Dem methodology:
https://www.v-dem.net/about/v-dem-project/methodology/

## 7. Submodels

### 7.1 Rotation
`P(t) = 5t mod 12`

Current documented auditor:
`A(t) = P(t)+6 mod 12`.

The affine schedule tool is an audit/design-space utility, not an adopted rule.

### 7.2 Coalition pair scoring
Each direction computes its own score. v0.32 stores both directions and uses
their mean only after both assessments exist. This removes execution-order
overwrite.

### 7.3 Coalition formation
Strong bilateral pairs are connected through a union-find component model.
While GateAgent exposes only one coalition id, silent overlapping active
coalitions are prevented.

### 7.4 Cartel/capture criterion
The current coded criterion requires, jointly:
- minimum active duration;
- minimum consecutive passed coalition-linked decisions;
- executive-power threshold;
- material-cluster participation;
- no exposure flag.

These thresholds remain design/arbitrary assumptions unless separately
calibrated.

### 7.5 Voting and dissent
Voting support is a stochastic function of a configurable intercept and trust
weight. Dissent logging uses a separate stochastic draw conditional on a
negative vote.

### 7.6 Emergency
Activation depends on modeled crisis load. Extension requires:
- continued crisis;
- individual simulated votes by non-involved gates;
- configured threshold;
- modeled court approval.

Support probability and court behavior are uncalibrated.

### 7.7 Resource accounting
Proposals may change gate shares. v0.32 enforces compositional conservation
after implementation.

### 7.8 Information verification
Reports are generated with modeled reliability and cross-verified with modeled
accuracy. Audit role can add a configurable accuracy bonus.

### 7.9 Bureaucracy
Continuity/archive state exists. Politicization currently follows an explicit
but arbitrary configured drift rule. This is a placeholder mechanism, not an
empirical law.

### 7.10 Civil society / public legitimacy
Civil-society state exists, but most variables are not causally active.
The legitimacy signal is a smoothed model proxy, not survey evidence.

### 7.11 Gate Zero and Mirror-13
The main ABM still lacks empirically defensible behavioral dynamics for these
institutions. v0.32 therefore separates:
- formal/interface constraints that can be tested now;
- behavioral effects that remain unimplemented rather than filled with invented
  probabilities.

## Reimplementation checklist

A reimplementation should reproduce:
- stage order;
- config schema;
- seed handling;
- bilateral coalition scoring;
- coalition duration vs decision streak separation;
- emergency transition rules;
- resource conservation;
- typed external timeline;
- output definitions.

A reimplementation that changes any of these is a different model version.
