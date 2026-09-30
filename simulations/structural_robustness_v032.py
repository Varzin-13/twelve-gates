#!/usr/bin/env python3
"""Structural robustness experiment for coalition pair aggregation.

CLAIM BOUNDARY
--------------
Exploratory structural-uncertainty analysis only. The three aggregation modes
are mathematical model variants/bounds, not political recommendations and not
empirically calibrated mechanisms.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from run_baseline import BASELINE_CFG
from run_stress import StressDriver
from twelve_gates_model import TwelveGatesModel


CLAIM_LABEL = "exploratory_structural_uncertainty"
PAIR_AGGREGATIONS = ["minimum", "mean", "maximum"]
THETA_VALUES = [0.575, 0.600, 0.625]
SEEDS_PER_CELL = 12
MAX_TICKS = 520
SEED_MASTER = 52032

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "structural_robustness_v032_results.json"
DOC = ROOT / "docs" / "STRUCTURAL_ROBUSTNESS_V032_2026-09-30.md"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def config_for(mode, theta):
    cfg = copy.deepcopy(BASELINE_CFG)
    cfg["coalitions"]["pair_aggregation"] = mode
    cfg["coalitions"]["theta_pair"] = float(theta)
    return cfg


def mean_optional(values):
    valid = [float(x) for x in values if x is not None]
    return None if not valid else float(np.mean(valid))


def run_cell(mode, theta, seeds):
    captures = []
    emergency = []
    rmst = []
    right_censored = 0
    total_coalitions = 0
    active_end = []
    legitimacy = []

    for seed in seeds:
        model = TwelveGatesModel(config_for(mode, theta), seed=seed)
        model.external = StressDriver([])
        out = model.run(MAX_TICKS)
        captures.append(1.0 if out["cartel_capture_ever"] else 0.0)
        emergency.append(float(out["emergency_time_share"]))
        rmst.append(out["coalition_rmst_ticks"])
        right_censored += int(out["coalitions_right_censored_n"])
        total_coalitions += int(out["coalitions_total_observed"])
        active_end.append(float(out["n_active_coalitions_end"]))
        legitimacy.append(float(out["mean_legitimacy_end"]))

    return {
        "pair_aggregation": mode,
        "theta_pair": float(theta),
        "n_runs": len(seeds),
        "cartel_capture_rate": float(np.mean(captures)),
        "cartel_capture_sd_across_seeds": float(np.std(captures, ddof=1)),
        "emergency_time_share_mean": float(np.mean(emergency)),
        "coalition_rmst_ticks_mean_valid_runs": mean_optional(rmst),
        "runs_with_defined_coalition_rmst": int(sum(x is not None for x in rmst)),
        "coalitions_total_observed": int(total_coalitions),
        "coalitions_right_censored_n": int(right_censored),
        "coalition_right_censored_fraction": (
            None if total_coalitions == 0 else float(right_censored / total_coalitions)
        ),
        "active_coalitions_end_mean": float(np.mean(active_end)),
        "internal_legitimacy_mean": float(np.mean(legitimacy)),
    }


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED_MASTER)
    seeds = [int(x) for x in rng.integers(0, 2**31, size=SEEDS_PER_CELL)]

    cells = [
        run_cell(mode, theta, seeds)
        for mode in PAIR_AGGREGATIONS
        for theta in THETA_VALUES
    ]

    matrix = {
        mode: {
            str(theta): next(
                c["cartel_capture_rate"] for c in cells
                if c["pair_aggregation"] == mode and c["theta_pair"] == theta
            )
            for theta in THETA_VALUES
        }
        for mode in PAIR_AGGREGATIONS
    }

    payload = {
        "schema": "twelve-gates/structural-robustness-v032/v1",
        "claim_label": CLAIM_LABEL,
        "not_calibration": True,
        "not_empirical_validation": True,
        "git_head": git_head(),
        "script_sha256": sha256_file(__file__),
        "model_sha256": sha256_file(HERE / "twelve_gates_model.py"),
        "baseline_script_sha256": sha256_file(HERE / "run_baseline.py"),
        "pair_aggregation_modes": PAIR_AGGREGATIONS,
        "theta_values": THETA_VALUES,
        "seeds_per_cell": SEEDS_PER_CELL,
        "common_seeds": seeds,
        "max_ticks": MAX_TICKS,
        "cells": cells,
        "cartel_capture_rate_matrix": matrix,
        "elapsed_seconds": round(time.time() - t0, 3),
        "interpretation_boundary": (
            "Differences across modes quantify structural model uncertainty under "
            "the current uncalibrated assumptions. They do not identify which "
            "institutional rule is correct or preferable."
        ),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# v0.32 Coalition Structural Robustness",
        "",
        "**Claim class:** exploratory structural uncertainty  ",
        "**Calibration:** no  ",
        f"**Design:** {len(PAIR_AGGREGATIONS)} pair aggregations × {len(THETA_VALUES)} theta values × {SEEDS_PER_CELL} common seeds",
        "",
        "The modes are mathematical alternatives/bounds, not institutional recommendations.",
        "",
        "## Mode definitions",
        "",
        "- `minimum`: pair strength equals the weaker directional assessment.",
        "- `mean`: current v0.32 baseline; arithmetic mean of the two directions.",
        "- `maximum`: permissive bound; pair strength equals the stronger direction.",
        "",
        "## Modeled cartel-capture frequencies",
        "",
        "| aggregation | " + " | ".join(f"θ={x:.3f}" for x in THETA_VALUES) + " |",
        "|" + "---|" * (len(THETA_VALUES) + 1),
    ]
    for mode in PAIR_AGGREGATIONS:
        vals = [matrix[mode][str(theta)] for theta in THETA_VALUES]
        lines.append(
            f"| {mode} | " + " | ".join(f"{v:.3f}" for v in vals) + " |"
        )

    lines += [
        "",
        "## Censoring-aware coalition summaries",
        "",
        "| aggregation | theta | RMST ticks (mean valid runs) | right-censored fraction |",
        "|---|---:|---:|---:|",
    ]
    for cell in cells:
        rmst = cell["coalition_rmst_ticks_mean_valid_runs"]
        cens = cell["coalition_right_censored_fraction"]
        lines.append(
            f"| {cell['pair_aggregation']} | {cell['theta_pair']:.3f} | "
            f"{'n/a' if rmst is None else f'{rmst:.3f}'} | "
            f"{'n/a' if cens is None else f'{cens:.3f}'} |"
        )

    lines += [
        "",
        "## Interpretation boundary",
        "",
        payload["interpretation_boundary"],
        "",
        "A strong difference between modes is evidence that the simulation conclusion "
        "depends on structural form. It is not evidence for selecting the mode that "
        "produces any particular outcome.",
    ]
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "git_head": payload["git_head"],
        "elapsed_seconds": payload["elapsed_seconds"],
        "cartel_capture_rate_matrix": matrix,
        "output": str(OUT.relative_to(ROOT)),
        "doc": str(DOC.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
