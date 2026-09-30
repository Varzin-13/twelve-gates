# ABM v2 — Odd-Trace Preregistration Skeleton

**Date:** 2026-09-30  
**Status:** preregistration scaffold; no confirmatory results are claimed here.

## Purpose

ABM v2 exists to test whether adding currently inert or placeholder mechanisms changes conclusions that are artifacts of the simpler implementation.

## Frozen separation

- **Exploratory:** mechanism search, debugging, parameter-range discovery.
- **Confirmatory:** hypotheses and failure thresholds frozen before rerun.
- **Calibration:** separate process; no value becomes empirical merely because it improves fit.

## Primary implementation targets

1. Gate Zero case/appeal lifecycle.
2. Mirror-13 causal effects and negative-competence constraints.
3. Civil-society/media oversight path.
4. Explicit public-legitimacy input distinct from internal gate trust.
5. Typed external shocks.
6. Emergency vote history.
7. Resource conservation.
8. Coalition-pair symmetry/asymmetry rule made explicit.

## Odd-trace tests

Each mechanism must have at least one targeted test where its effect is expected to be observable and one null/negative-control test where it should remain inactive.

Examples:
- stress driver: no effect before configured start tick;
- Mirror-13: zero effect when disabled;
- Gate Zero appeal: no appeal transition for approved cases;
- ledger: consistency check fails after deliberate history mutation;
- resource system: total share remains conserved after arbitrary valid reallocations.

## Confirmatory rule

A mechanism graduates from placeholder to implemented hypothesis only if:
- its state transitions are explicit;
- targeted tests pass;
- negative controls pass;
- parameter provenance is complete;
- outputs are reproducible from frozen seed/config/code hash.

No such graduation implies empirical validity.
