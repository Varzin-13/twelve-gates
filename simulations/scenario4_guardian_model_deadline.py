"""
Scenario 4 — 18-month deadline sensitivity scenario
====================================================
CLAIM BOUNDARY:
This is a synthetic timing scenario, not an empirical estimate of the success
or failure probability of any named political proposal.

Question:
Given an explicitly assumed lognormal completion-time distribution, what
fraction of draws fall before/after an 18-month deadline?

The distribution parameters are scenario assumptions. They are NOT calibrated
from a representative sample of political transitions. A historical example
may motivate a range, but one example cannot identify a population
distribution.

Important statistical note:
For numpy's lognormal distribution, exp(mu) is the MEDIAN, not the arithmetic
mean. The old variable name MEAN_MONTHS was therefore misleading.
"""
import json
from pathlib import Path

import numpy as np

CLAIM_LABEL = "hypothesis"
RNG_SEED = 44
rng = np.random.default_rng(RNG_SEED)

N_TRIALS = 3000
HARD_DEADLINE_MONTHS = 18

# ARBITRARY scenario assumptions — not empirical calibration.
LOGNORMAL_MEDIAN_MONTHS = 30
LOGNORMAL_SIGMA = 0.5


def simulate_trial():
    return rng.lognormal(
        mean=np.log(LOGNORMAL_MEDIAN_MONTHS),
        sigma=LOGNORMAL_SIGMA,
    )


if __name__ == "__main__":
    times = np.array([simulate_trial() for _ in range(N_TRIALS)])
    prob_incomplete = float((times > HARD_DEADLINE_MONTHS).mean())
    prob_complete = 1.0 - prob_incomplete

    print("Scenario 4 — synthetic 18-month deadline sensitivity")
    print(f"claim_label: {CLAIM_LABEL}")
    print(f"assumed lognormal median: {LOGNORMAL_MEDIAN_MONTHS:.1f} months")
    print(f"assumed lognormal sigma: {LOGNORMAL_SIGMA:.3f}")
    print(f"simulated arithmetic mean: {times.mean():.1f} months")
    print(f"simulated median: {np.median(times):.1f} months")
    print(f"fraction <= 18 months: {prob_complete:.3f}")
    print(f"fraction > 18 months: {prob_incomplete:.3f}")
    print(
        "Interpretation: these fractions are consequences of the assumed "
        "distribution, not real-world probabilities."
    )

    results = {
        "schema": "twelve-gates/scenario4-deadline-sensitivity/v2",
        "claim_label": CLAIM_LABEL,
        "not_empirical_validation": True,
        "n_trials": N_TRIALS,
        "hard_deadline_months": HARD_DEADLINE_MONTHS,
        "lognormal_median_months_assumed": LOGNORMAL_MEDIAN_MONTHS,
        "lognormal_sigma_assumed": LOGNORMAL_SIGMA,
        "simulated_mean_completion_months": float(times.mean()),
        "simulated_median_completion_months": float(np.median(times)),
        "fraction_complete_by_deadline": prob_complete,
        "fraction_incomplete_by_deadline": prob_incomplete,
        "seed": RNG_SEED,
        "interpretation_boundary": (
            "Conditional synthetic sensitivity output. The assumed timing "
            "distribution is not calibrated to a representative transition dataset."
        ),
    }
    output_dir = Path(__file__).resolve().parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "scenario4_results_v2.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"saved: {out}")
