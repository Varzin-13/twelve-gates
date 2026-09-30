#!/usr/bin/env python3
"""Scenario 3 v2 — analytical redundancy toy model.

For iid exponential recovery times with mean mu, the expected maximum of k
affected components is mu * H_k. Therefore the direction of the legacy
1-city/2-city/3-city comparison is built into the assumed affected-component
counts; simulation is not needed to establish that direction.
"""
from fractions import Fraction
import json
from pathlib import Path


MEAN_RECOVERY_DAYS = 21.0


def harmonic(k):
    return sum(Fraction(1, i) for i in range(1, k + 1))


def expected_max_exponential(k, mean):
    return float(harmonic(k)) * mean


def main():
    expected = {
        3: expected_max_exponential(3, MEAN_RECOVERY_DAYS),
        2: expected_max_exponential(2, MEAN_RECOVERY_DAYS),
        1: expected_max_exponential(1, MEAN_RECOVERY_DAYS),
    }

    result = {
        "schema": "twelve-gates/scenario3-redundancy-analytic/v2",
        "claim_label": "conditional_engineering_toy",
        "not_empirical_validation": True,
        "mean_recovery_days_assumed": MEAN_RECOVERY_DAYS,
        "affected_components_by_legacy_city_case": {
            "1_city": 3,
            "2_cities": 2,
            "3_cities": 1,
        },
        "expected_max_recovery_days": {
            "1_city_case": expected[3],
            "2_city_case": expected[2],
            "3_city_case": expected[1],
        },
        "relative_reduction_2_vs_1_city_case": 1 - expected[2] / expected[3],
        "relative_reduction_3_vs_1_city_case": 1 - expected[1] / expected[3],
        "direction_is_built_into_affected_component_counts": True,
        "common_mode_failures_modeled": False,
        "interpretation_boundary": (
            "These values are exact consequences of iid exponential recovery "
            "and the assumed 3→2→1 affected-component construction. They do not "
            "validate real geographic resilience or common-mode independence."
        ),
    }

    out = Path(__file__).resolve().parent / "results" / "scenario3_v2_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
