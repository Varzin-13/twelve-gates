# Scenario 4–5 Claim-Boundary Audit

**Date:** 2026-09-30  
**Scope:** simulation methodology only. This document does not rank, endorse, or
oppose any political actor, organization, or transition proposal.

## Why this audit was necessary

The previous Scenario 4 and Scenario 5 scripts produced precise percentages
from distributions whose key parameters were not empirically identified.

That creates a risk of reading **conditional simulation output** as an
estimated real-world probability.

## Scenario 4 findings

The old script used:

`rng.lognormal(mean=np.log(30), sigma=0.5)`

but described 30 months as the distribution's "mean." For NumPy's lognormal
parameterization, `exp(mu)` is the median. The arithmetic mean is larger.

More importantly, the 30-month location and sigma=0.5 values were modeling
assumptions, not parameters estimated from a representative transition dataset.

Therefore the fraction of draws above 18 months is a sensitivity result
conditional on that assumed distribution. It cannot by itself reject or validate
a real political proposal.

## Scenario 5 findings

The timing submodel had the same mean/median labeling problem.

The allocation submodel explicitly inserts:

`DOMINANT_ORG_LEVERAGE = 0.35`

into the allocation probabilities. A resulting modeled share above the equal
20% reference is therefore a consequence of the inserted leverage assumption,
not independent evidence that a real organization will receive that share.

The leverage value has no accepted empirical calibration mapping in this
repository.

## Corrections

Both scripts now:

- carry `claim_label = hypothesis`;
- state that outputs are not empirical validation;
- name lognormal location parameters as medians;
- label leverage/timing parameters as arbitrary scenario assumptions;
- avoid political verdict language;
- write to portable repository-relative result paths;
- use v2 result schemas so historical artifacts are not overwritten.

## Interpretation rule

These scenarios can answer:

> "If these timing/allocation assumptions are imposed, what output distribution
> does the code generate?"

They cannot currently answer:

> "What is the real probability that this named political proposal or
> organization succeeds, fails, dominates, or completes a transition by a
> deadline?"

That second class of claim requires defensible empirical mapping, uncertainty,
and validation beyond the present scripts.
