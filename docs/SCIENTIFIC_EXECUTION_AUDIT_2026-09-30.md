# Twelve Gates — Scientific & Execution Audit for v0.32

**Date:** 2026-09-30  
**Status:** research/audit artifact. This document does not establish real-world political effectiveness, legitimacy, or predictive validity.

## 1. Claim classes

This audit separates four claim classes:

1. **Mathematical/software invariants** — may be proved or regression-tested.
2. **Simulation findings** — conditional on code, model structure, and parameter choices.
3. **Empirical institutional claims** — require external evidence, calibration, or bounded human study.
4. **Normative/constitutional choices** — cannot be derived from mathematics alone.

Evidence from one class must not be silently promoted into another.

## 2. Code findings closed on the execution-audit branch

### 2.1 Stress timing mismatch
The stress runner stated that the persistent shock begins at tick 52, while the previous driver returned the material-cluster shock regardless of tick.

**Correction:** the base scenario driver now records `current_tick`; the stress driver applies its shock only at `tick >= 52`.

**Provenance rule:** historical stress result JSON is not overwritten merely because the implementation changed.

### 2.2 Resource-share conservation
`resource_share` is modeled as a share. Previously, an implemented proposal could change one gate independently, allowing the total to drift away from 1.

**Correction:** after the implementation stage, resource shares are normalized so their total remains 1. This is a bookkeeping invariant, not a claim about the appropriate real-world allocation rule.

### 2.3 Emergency-extension representation
The former implementation represented the collective non-involved-gate decision with a single Bernoulli draw.

**Correction:** non-involved gates now receive separate simulated votes and an explicit required fraction is checked.

The per-gate support probability remains tagged **ARBITRARY**. The change makes the institutional rule inspectable; it does not make the probability empirically valid.

### 2.4 Z12 audit-pair coverage
The current rule `A_t = P_t + 6 (mod 12)` has 12 unique ordered coordinator→auditor pairs in one 12-period cycle.

The new `simulations/audit_schedule.py` exposes:
- the 48 affine permutations `x -> ax+b (mod 12)` with `gcd(a,12)=1`;
- collision-free affine auditor schedules;
- pair-coverage statistics;
- a non-self offset benchmark using offsets 1..11.

That benchmark covers all `12 × 11 = 132` non-self ordered pairs exactly once across 132 periods. This is a combinatorial benchmark, not a recommendation about institutional cadence.

### 2.5 Hidden behavioral constants made explicit
A second-pass audit found active behavioral constants embedded directly in code:
audit bonus, coalition-propensity weights, capture-pressure weights, voting
intercept/slope, bureaucracy drift, public-legitimacy smoothing, and armed-bloc
threshold/probability values.

v0.32 moves these values into `model_assumptions` without changing their
numerical values. The bundle is tagged **ARBITRARY**. This is a provenance
improvement, not a calibration result.

### 2.6 Coalition and event-engine corrections
Second-pass execution audit closed four additional software-semantic defects:

- unordered coalition-pair keys no longer overwrite one directional assessment;
- coalition active duration is distinct from consecutive passed decisions;
- a failed coalition-linked decision resets the consecutive-decision streak;
- external timeline events are typed, time-scoped, and preserve multiple events at one tick.

The original stored simulation artifacts remain historical outputs of their
original code. They are not retroactively reinterpreted as outputs of these fixes.

### 2.7 Claim-boundary hardening
The model no longer returns a fixed numeric `TrustLedger.integrity()` value
without a real integrity mechanism. The civil-society legitimacy output is also
explicitly labeled as an internal proxy rather than measured public opinion.

### 2.8 Affine reciprocal-audit result
The fixed `+6` schedule contains six reciprocal audit dyads within each
12-period cycle. Among the 36 collision-free affine auditor schedules over
`Z_12`, 24 are reciprocal-free within one cycle. An exhaustive finite search
within this affine family found that an exact 11-cycle cover of all 132 non-self
ordered audit pairs has a minimum total of six within-cycle reciprocal dyads.

This is a finite computational result **within the affine family**, not a
theorem about every possible institutional schedule.

## 3. Components that remain model gaps

The following are not yet adequate empirical behavioral models:

- **Gate Zero:** no calibrated population-level admission/rejection/appeal process.
- **Mirror-13:** helper metrics exist, but coordination benefit and informal-power risk are not causally integrated into the main dynamics.
- **Civil society:** oversight/media/union variables are largely inert.
- **Public legitimacy:** the current signal is substantially derived from internal modeled trust and must not be described as measured public opinion.
- **Bureaucracy:** politicization dynamics remain stylized rather than calibrated.
- **Armed blocs:** the baseline instantiates none.
- **External timeline:** typed event semantics remain incomplete.
- **Emergency court:** independence and erosion are scenario assumptions, not measured constants.

These gaps block predictive interpretation even if the software is reproducible.

## 4. External methodological anchors

### Representative deliberation / sortition
OECD good-practice guidance describes representativeness using random sampling followed by demographic stratification and emphasizes transparency, inclusion, information quality, and evaluation.

Source:  
https://www.oecd.org/en/publications/evaluation-guidelines-for-representative-deliberative-processes_10ccbfcb-en/full-report/component-9.html

This supports testing stratified sortition as a mechanism. It does not establish that a particular national design is legitimate or effective.

### Constitution-building participation
International IDEA describes public participation as a central concern in modern constitution-building while also noting that whether and how participation produces claimed benefits is not fully understood and depends on context.

Source:  
https://www.idea.int/publications/catalogue/practical-considerations-public-participation-constitution-building

Therefore founding legitimacy cannot be replaced by an internal mathematical rule.

### Public randomness
drand documents publicly verifiable distributed randomness based on threshold cryptography.

Source:  
https://docs.drand.love/docs/cryptography/

A beacon can reduce manipulation of a draw after the eligible pool and algorithm are frozen. It cannot decide who ought to be eligible.

### Append-only transparency
RFC 9162 specifies Merkle inclusion and consistency proofs, including consistency proofs for append-only log history.

Source:  
https://www.rfc-editor.org/rfc/rfc9162.html

Such techniques can support record integrity. They do not prove the truth or justice of recorded decisions.

## 5. Legitimate VARZIN transfer

The strongest transferable contribution from the broader VARZIN research program is methodological:

- freeze definitions before confirmatory testing;
- separate exploratory from confirmatory work;
- preserve negative/corrective results;
- track parameter provenance;
- do not treat derived observations as independent samples;
- test generalization rather than only in-sample fit;
- keep claim boundaries explicit.

The mathematical contribution here is narrower:
- finite cyclic scheduling over `Z_12`;
- affine permutation analysis;
- coverage/collision measures;
- future constraint-search over schedules.

None of these results establishes that a mathematically symmetric institution will be socially accepted, stable, or effective.

## 6. Gate to ABM v2

ABM v2 should not be described as calibrated or policy-predictive until at least:

1. typed event/state schema;
2. executable Gate Zero case/appeal lifecycle;
3. Mirror-13 causal coupling;
4. conserved resource accounting;
5. explicit emergency voting and extension history;
6. civil-society/media causal paths;
7. empirical target patterns with uncertainty;
8. global sensitivity analysis;
9. out-of-sample or cross-case validation targets;
10. deterministic independent replay from frozen config and code hash.

## 7. Human-pilot boundary

A bounded research pilot can test process mechanics without claiming national authority. Candidate outcomes include:

- decision latency;
- backlog accumulation;
- audit-pair coverage;
- appeal resolution time;
- missing-participant handling;
- workload concentration;
- rule-bypass attempts;
- ledger consistency;
- recovery after simulated participant/server loss;
- participant understanding and perceived representation.

Any pilot result is evidence about that pilot population and context. Generalization requires a defensible sampling and inference design.

## 8. Hard boundary

The following cannot be proved by Z12, affine algebra, ABM, or cryptography alone:

- founding legitimacy;
- compliance by coercive or materially powerful actors;
- public acceptance;
- normative superiority of one value trade-off;
- success of a political transition.

They can be operationalized, measured, stress-tested, and made more transparent; they cannot be mathematically manufactured.
