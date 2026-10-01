#!/usr/bin/env python3
"""Paired 300×520 stress rerun after fixing the documented 2/3 budget rule.

CLAIM BOUNDARY
--------------
This is a paired software-effect audit under the same uncalibrated model and
the same 300 seeds used by the preceding v0.32 stress artifact. It estimates
the effect of a code/rule correction inside the model, not a real-world
political probability.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from run_baseline import BASELINE_CFG
from run_stress import StressDriver
from twelve_gates_model import TwelveGatesModel


N_RUNS = 300
MAX_TICKS = 520
MASTER_SEED = 43

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "stress_v032_post_budget_majority_results.json"
DOC = ROOT / "docs" / "STRESS_V032_POST_BUDGET_MAJORITY_2026-10-01.md"
PRE = RESULTS / "stress_v032_execution_audit_results.json"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_config_sha256(cfg):
    raw = json.dumps(
        cfg, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def mean(values):
    return float(np.mean(values))


def mean_optional(values):
    xs = [float(x) for x in values if x is not None]
    return None if not xs else float(np.mean(xs))


def summarize(runs):
    decided = sum(r["proposals_voted_pass"] + r["proposals_voted_fail"] for r in runs)
    passed = sum(r["proposals_voted_pass"] for r in runs)
    first_members = Counter(
        tuple(r["cartel_first_snapshot"]["members"])
        for r in runs
        if r["cartel_first_snapshot"] is not None
    )
    return {
        "cartel_capture_rate": mean([bool(r["cartel_capture_ever"]) for r in runs]),
        "emergency_time_share_mean": mean([r["emergency_time_share"] for r in runs]),
        "legacy_dissolved_coalition_duration_mean": mean([
            r["coalition_duration_legacy_dissolved_mean"] for r in runs
        ]),
        "coalition_rmst_ticks_mean_valid_runs": mean_optional([
            r["coalition_rmst_ticks"] for r in runs
        ]),
        "mean_internal_legitimacy": mean([r["mean_legitimacy_end"] for r in runs]),
        "mean_capture_pressure": mean([r["mean_capture_pressure_end"] for r in runs]),
        "proposal_decisions_total": int(decided),
        "proposal_passed_total": int(passed),
        "proposal_failed_total": int(decided - passed),
        "proposal_pass_fraction_weighted": None if decided == 0 else float(passed / decided),
        "budget_required_yes_votes_unique": sorted({
            int(r["budget_required_yes_votes"]) for r in runs
        }),
        "first_cartel_members_counts": {
            ",".join(map(str, k)): int(v)
            for k, v in sorted(first_members.items(), key=lambda kv: (-kv[1], kv[0]))
        },
    }


def paired_compare(pre, post, seeds):
    if pre.get("run_seeds") != seeds:
        raise RuntimeError("pre-budget artifact seeds do not match paired rerun seeds")
    old = pre["run_results"]
    if len(old) != len(post):
        raise RuntimeError("paired run count mismatch")

    old_capture = [bool(r["cartel_capture_ever"]) for r in old]
    new_capture = [bool(r["cartel_capture_ever"]) for r in post]

    old_to_new = Counter(zip(old_capture, new_capture))
    return {
        "capture_transition_counts": {
            "false_to_false": int(old_to_new[(False, False)]),
            "false_to_true": int(old_to_new[(False, True)]),
            "true_to_false": int(old_to_new[(True, False)]),
            "true_to_true": int(old_to_new[(True, True)]),
        },
        "cartel_capture_rate_pre": mean(old_capture),
        "cartel_capture_rate_post": mean(new_capture),
        "cartel_capture_rate_difference": mean(new_capture) - mean(old_capture),
        "emergency_time_share_paired_mean_difference": mean([
            float(n["emergency_time_share"]) - float(o["emergency_time_share"])
            for o, n in zip(old, post)
        ]),
        "legacy_coalition_duration_paired_mean_difference": mean([
            float(n["coalition_duration_legacy_dissolved_mean"])
            - float(o["coalition_mean_duration"])
            for o, n in zip(old, post)
        ]),
        "internal_legitimacy_paired_mean_difference": mean([
            float(n["mean_legitimacy_end"]) - float(o["mean_legitimacy_end"])
            for o, n in zip(old, post)
        ]),
    }


def render(payload):
    s = payload["summary"]
    p = payload["paired_comparison"]
    t = p["capture_transition_counts"]
    return f"""# v0.32 Post-Budget-Majority Stress Audit

**Claim class:** paired software-effect audit  
**Calibration:** no  
**Empirical validation:** no  
**Runs:** {payload['n_runs']} × {payload['max_ticks']} ticks  
**Master seed:** {payload['master_seed']}  
**Required budget yes votes:** {s['budget_required_yes_votes_unique']}

## Why this rerun exists

The documented/configured budget reallocation rule was two thirds, but the old
implementation passed proposals at 7/12 votes. The corrected implementation
requires 8/12.

This rerun uses the same 300 seeds as the immediately preceding v0.32 stress
artifact so the before/after comparison is paired.

## Paired capture transition

| pre-budget code | corrected code | runs |
|---|---|---:|
| false | false | {t['false_to_false']} |
| false | true | {t['false_to_true']} |
| true | false | {t['true_to_false']} |
| true | true | {t['true_to_true']} |

- pre-budget modeled capture rate: {p['cartel_capture_rate_pre']:.6f}
- post-fix modeled capture rate: {p['cartel_capture_rate_post']:.6f}
- difference: {p['cartel_capture_rate_difference']:+.6f}

## Current corrected-code summaries

- emergency time share mean: {s['emergency_time_share_mean']:.6f}
- legacy dissolved-only coalition duration mean: {s['legacy_dissolved_coalition_duration_mean']:.6f}
- censoring-aware coalition RMST mean across valid runs: {s['coalition_rmst_ticks_mean_valid_runs'] if s['coalition_rmst_ticks_mean_valid_runs'] is not None else 'n/a'}
- proposal decisions: {s['proposal_decisions_total']}
- proposal passes: {s['proposal_passed_total']}
- proposal failures: {s['proposal_failed_total']}
- weighted proposal pass fraction: {s['proposal_pass_fraction_weighted'] if s['proposal_pass_fraction_weighted'] is not None else 'n/a'}

## Other paired mean differences

- emergency time share: {p['emergency_time_share_paired_mean_difference']:+.6f}
- legacy coalition duration: {p['legacy_coalition_duration_paired_mean_difference']:+.6f}
- internal legitimacy: {p['internal_legitimacy_paired_mean_difference']:+.6f}

## Provenance

- Git HEAD: `{payload['git_head']}`
- runner SHA256: `{payload['runner_sha256']}`
- model SHA256: `{payload['model_sha256']}`
- canonical config SHA256: `{payload['baseline_config_canonical_sha256']}`
- pre-budget artifact SHA256: `{payload['pre_budget_artifact_sha256']}`

## Interpretation boundary

This document measures how a specific implementation correction changes the
output of the coded, uncalibrated model under matched seeds. It is not evidence
for the real-world probability of any political outcome.
"""


def main():
    if not PRE.exists():
        raise FileNotFoundError(PRE)
    pre = json.loads(PRE.read_text(encoding="utf-8"))

    rng = np.random.default_rng(MASTER_SEED)
    seeds = [int(x) for x in rng.integers(0, 2**31, size=N_RUNS)]

    t0 = time.time()
    runs = []
    for seed in seeds:
        model = TwelveGatesModel(BASELINE_CFG, seed=seed)
        model.external = StressDriver([])
        runs.append(model.run(MAX_TICKS))

    summary = summarize(runs)
    paired = paired_compare(pre, runs, seeds)

    payload = {
        "schema": "twelve-gates/stress-v032-post-budget-majority/v1",
        "claim_label": "software_effect_hypothesis",
        "not_calibration": True,
        "not_empirical_validation": True,
        "git_head": git_head(),
        "runner_sha256": sha256_file(__file__),
        "model_sha256": sha256_file(HERE / "twelve_gates_model.py"),
        "baseline_config_canonical_sha256": canonical_config_sha256(BASELINE_CFG),
        "pre_budget_artifact_sha256": sha256_file(PRE),
        "n_runs": N_RUNS,
        "max_ticks": MAX_TICKS,
        "master_seed": MASTER_SEED,
        "run_seeds": seeds,
        "summary": summary,
        "paired_comparison": paired,
        "elapsed_seconds": round(time.time() - t0, 3),
        "run_results": runs,
        "interpretation_boundary": (
            "Paired software-effect audit under uncalibrated assumptions; "
            "not a real-world political probability."
        ),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    DOC.write_text(render(payload), encoding="utf-8")

    print(json.dumps({
        "git_head": payload["git_head"],
        "elapsed_seconds": payload["elapsed_seconds"],
        "summary": summary,
        "paired_comparison": paired,
        "output": str(OUT.relative_to(ROOT)),
        "doc": str(DOC.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
