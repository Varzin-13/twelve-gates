# Formal execution layer

This directory contains an abstract state-machine layer for Twelve Gates.

- `TwelveGates.tla`: TLA+ skeleton for rotation, emergency transitions, a non-vacuous resource-transfer transition, and Gate Zero case states.
- `TwelveGates.cfg`: initial invariant set.
- `abstract_model_check.py`: dependency-free finite-state checks that run in CI.

## Claim boundary

Passing these checks establishes only properties of the encoded state machine. It does not establish political legitimacy, empirical effectiveness, public acceptance, or predictive validity.

The Python checker is intentionally executable in ordinary CI. The TLA+ model is a research target for TLC expansion; the repository must not claim TLC verification unless a TLC run is actually recorded.

## Resource-conservation note

The initial skeleton left `resources` unchanged in every transition, which made
the resource-conservation invariant vacuous in the TLA+ layer. The current
skeleton adds `BudgetTransfer`, moving one unit between distinct gates while
preserving the total.

This strengthens the state-machine specification but is still **not** a claim
that TLC has been run. The dependency-free Python checker separately explores
resource transfers in CI.
