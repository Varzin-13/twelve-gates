#!/usr/bin/env python3
"""Scenario 1 v2 — conditional coalition-capture arithmetic.

This file does not estimate the real behavior of any political institution.
It exposes the exact mathematical consequences of the script's assumed
collusion and leverage probabilities.
"""
from math import comb
import json
from pathlib import Path

N_INDEPENDENT = 9
MAJORITY_THRESHOLD = 7
CARTEL_VOTES = 3

BASELINE_COLLUSION_PROB = 0.55
RANDOM_TRIO_COLLUSION_PROB = 0.15
LEVERAGE_PRESSURE = 0.20
MITIGATION_EFFECT = 0.35
LEVERAGE_MITIGATION_EFFECT = 0.50
SWING_VOTE_PROB = 0.50


def binomial_range_probability(n, p, lo, hi):
    return sum(
        comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
        for k in range(lo, hi + 1)
    )


def exact_capture_rate(collusion_prob, leverage_pressure):
    """Exact expectation under the original script's own assumptions."""
    p = min(SWING_VOTE_PROB + leverage_pressure, 0.95)
    lo = MAJORITY_THRESHOLD - CARTEL_VOTES
    hi = MAJORITY_THRESHOLD - 1
    return collusion_prob * binomial_range_probability(
        N_INDEPENDENT, p, lo, hi
    )


def exact_control_rate():
    lo = MAJORITY_THRESHOLD - CARTEL_VOTES
    hi = MAJORITY_THRESHOLD - 1
    return RANDOM_TRIO_COLLUSION_PROB * binomial_range_probability(
        N_INDEPENDENT, SWING_VOTE_PROB, lo, hi
    )


def main():
    baseline = exact_capture_rate(
        BASELINE_COLLUSION_PROB, LEVERAGE_PRESSURE
    )
    mitigated = exact_capture_rate(
        BASELINE_COLLUSION_PROB * (1 - MITIGATION_EFFECT),
        LEVERAGE_PRESSURE * (1 - LEVERAGE_MITIGATION_EFFECT),
    )
    control = exact_control_rate()

    result = {
        "schema": "twelve-gates/scenario1-conditional-arithmetic/v2",
        "claim_label": "conditional_sensitivity",
        "not_empirical_validation": True,
        "inputs_are_model_assumptions": True,
        "majority_threshold": MAJORITY_THRESHOLD,
        "baseline_expected_capture_rate": baseline,
        "mitigated_expected_capture_rate": mitigated,
        "random_trio_expected_capture_rate": control,
        "mitigation_relative_change_given_assumptions": (
            1 - mitigated / baseline
        ),
        "mitigated_minus_control_given_assumptions": mitigated - control,
        "interpretation_boundary": (
            "The exact rates are mathematical consequences of the assumed "
            "collusion/leverage probabilities. They are not evidence that those "
            "probabilities describe a real political system."
        ),
    }

    out = Path(__file__).resolve().parent / "results" / "scenario1_v2_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
