#!/usr/bin/env python3
"""Scenario 2 v2 — conditional emergency-persistence sensitivity.

The extension variable is explicitly modeled as an aggregate Bernoulli approval
assumption. It is NOT described as an implemented 2/3 vote, because the legacy
script did not simulate individual votes.
"""
import json
from pathlib import Path

import numpy as np


N_CYCLES = 60
CYCLE_DAYS = 14
N_TRIALS = 500
SEED = 7

WAR_CONTINUATION_PROB = 0.93
AGGREGATE_EXTENSION_APPROVAL = 0.55
PRESSURE_GROWTH_PER_CYCLE = 0.025
JUDICIAL_REJECT_PROB = 0.30


def simulate_trial(rng, with_review):
    active = False
    consecutive = 0
    emergency_count = 0
    war_count = 0
    war = True

    for _ in range(N_CYCLES):
        if not war:
            active = False
            consecutive = 0
            continue

        war_count += 1
        if not active:
            active = True
            consecutive = 1
        else:
            bonus = min(consecutive * PRESSURE_GROWTH_PER_CYCLE, 0.40)
            approval_p = min(
                AGGREGATE_EXTENSION_APPROVAL + bonus, 0.98
            )
            extended = rng.random() < approval_p
            if with_review and extended:
                extended = not (rng.random() < JUDICIAL_REJECT_PROB)
            if extended:
                consecutive += 1
            else:
                active = False
                consecutive = 0

        if active:
            emergency_count += 1

        war = rng.random() < WAR_CONTINUATION_PROB

    return 0.0 if war_count == 0 else emergency_count / war_count


def run_condition(seed, with_review):
    rng = np.random.default_rng(seed)
    return np.array([
        simulate_trial(rng, with_review)
        for _ in range(N_TRIALS)
    ])


def main():
    no_review = run_condition(SEED, False)
    review = run_condition(SEED + 1, True)

    expected_untruncated_war_cycles = 1 / (1 - WAR_CONTINUATION_PROB)

    result = {
        "schema": "twelve-gates/scenario2-emergency-persistence/v2",
        "claim_label": "conditional_sensitivity",
        "not_empirical_validation": True,
        "inputs_are_model_assumptions": True,
        "max_cycles": N_CYCLES,
        "cycle_days": CYCLE_DAYS,
        "war_continuation_probability_assumed": WAR_CONTINUATION_PROB,
        "untruncated_expected_war_cycles_from_assumption": expected_untruncated_war_cycles,
        "untruncated_expected_war_days_from_assumption": expected_untruncated_war_cycles * CYCLE_DAYS,
        "aggregate_extension_approval_probability_assumed": AGGREGATE_EXTENSION_APPROVAL,
        "aggregate_approval_is_not_an_explicit_two_thirds_vote": True,
        "judicial_reject_probability_assumed": JUDICIAL_REJECT_PROB,
        "pressure_growth_per_cycle_assumed": PRESSURE_GROWTH_PER_CYCLE,
        "emergency_share_mean_without_review": float(no_review.mean()),
        "emergency_share_mean_with_review": float(review.mean()),
        "interpretation_boundary": (
            "Differences are consequences of an assumed stochastic process. "
            "The aggregate approval and review probabilities are not calibrated "
            "institutional probabilities."
        ),
    }

    out = Path(__file__).resolve().parent / "results" / "scenario2_v2_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
