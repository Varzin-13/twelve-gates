# Twelve Gates — Formal Execution Specification v0.1

**Date:** 2026-09-30  
**Status:** pre-implementation research specification.  
**Scope:** machine-checkable invariants and testable interfaces only.

Let `G = Z_12 = {0,...,11}`.

At period `t`:

`P(t) = 5t mod 12`

is the modeled coordinator. The currently documented auditor rule is:

`A(t) = P(t) + 6 mod 12`.

Alternative schedules remain research candidates.

## Hard invariants

### F1 — Rotation coverage
For `t = 0..11`, `{P(t)} = G`.

### F2 — No self-audit
For every period, `A(t) != P(t)`.

### F3 — Resource conservation
If `resource[g]` is a share:

`sum(resource[g] for g in G) = 1`

within numerical tolerance after each completed implementation stage.

The TLA+ research skeleton now includes an explicit unit `BudgetTransfer`
transition so this invariant is exercised under state change rather than holding
only because resources never move. The repository still does not claim TLC
verification until an actual TLC run is recorded.

### F4 — Nonnegative resources
`resource[g] >= 0` for every gate.

### F5 — Emergency expiry
Emergency authority cannot persist solely because time advances. An extension requires a distinct authorization transition.

### F6 — Extension history
Each extension should record at minimum:
- participating gates;
- yes/no/abstention;
- threshold;
- review result;
- start and expiry;
- extension count.

### F7 — Gate Zero bounded competence
Gate Zero software should act only on enumerated criteria in a frozen eligibility rule set. Out-of-scope cases must have an explicit state rather than silent rejection.

This is a software-scope rule; it does not solve founding legitimacy.

### F8 — Appeal terminality
A rejection should enter an explicit appeal lifecycle with terminal outcomes. No case should disappear without a final state.

### F9 — Mirror-13 negative competence
If the design retains Mirror-13 as a coordinating/review function, its executable interface should not silently gain capabilities outside the frozen specification.

### F10 — Append-only record integrity
A future decision ledger should support inclusion verification, history consistency verification, and independent checkpoint comparison.

This is a log-integrity property, not a truth property.

### F11 — Random-selection replay
For a verifiable draw:
- eligible-pool hash is frozen before randomness is known;
- algorithm/version is frozen;
- randomness reference is recorded;
- replay reproduces the selected indices.

Eligibility itself remains an external legal/normative input.

### F12 — Parameter provenance
Every numeric model input must be tagged:

`DOCUMENT | DESIGN | EMPIRICAL | ARBITRARY`.

An `EMPIRICAL` tag additionally requires source, date/version, mapping method, and uncertainty.

### F13 — Claim monotonicity
Reproducible code must not, by itself, convert an `ARBITRARY` parameter into an `EMPIRICAL` parameter.

## Audit-schedule design space

The fixed `+6` rule has 12 unique ordered coordinator→auditor pairs per 12-period cycle.

The non-self offset benchmark `d ∈ {1,...,11}` has:
- 132 unique ordered pairs over 132 periods;
- no self-audit;
- every gate auditing every other gate exactly once.

This is a coverage benchmark, not a preferred institutional schedule.

The affine family is:

`x -> ax+b mod 12`, where `a ∈ {1,5,7,11}`, `b ∈ Z_12`.

There are 48 affine permutations.

Additional finite-family audit results:
- 36 affine auditor schedules have no self-audit;
- 24 of those 36 also have no reciprocal dyad within a single cycle;
- the documented fixed `+6` rule has six reciprocal dyads in one cycle;
- exhaustive exact-cover search over the collision-free affine family finds
  minimum total reciprocal dyads = 6 for an 11-cycle exact cover of all 132
  non-self ordered pairs.

These are search results over a finite design family, not normative criteria.

Candidate schedules can be compared on explicit software objectives such as:
- self-audit count;
- repeated-pair count;
- minimum repeat distance;
- ordered-pair coverage;
- declared conflict constraints;
- transition burden.

## ABM v2 interfaces

### Gate Zero
`submit -> validate_scope -> evidence_check -> decide -> appeal? -> final`

### Mirror-13
`receive_items -> construct_allowed_agenda -> coordinate -> recommend -> log_response`

### Emergency
`request -> activate -> expire_or_extend -> record`

### Budget
`propose -> vote -> implement -> conservation_check`

### Ledger
`append -> checkpoint -> inclusion_proof -> consistency_proof -> witness_compare`

## Verification ladder

1. unit tests;
2. invariant/property tests;
3. deterministic replay;
4. randomized/property-based testing;
5. abstract model checking;
6. adversarial scenario tests;
7. calibration;
8. empirical validation;
9. bounded human pilot.

Passing levels 1–5 establishes software/logical consistency only.
