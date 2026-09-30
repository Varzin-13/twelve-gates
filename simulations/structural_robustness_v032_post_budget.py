#!/usr/bin/env python3
"""Paired structural-uncertainty rerun after the 2/3 budget-rule correction."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

RUN_LABEL = "post-budget-rerun-after-provenance-restore"

from structural_robustness_v032 import (
    PAIR_AGGREGATIONS,
    THETA_VALUES,
    SEEDS_PER_CELL,
    MAX_TICKS,
    SEED_MASTER,
    run_cell,
)

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "structural_robustness_v032_post_budget_results.json"
DOC = ROOT / "docs" / "STRUCTURAL_ROBUSTNESS_V032_POST_BUDGET_2026-10-01.md"
PRE = RESULTS / "structural_robustness_v032_results.json"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def matrix(cells):
    return {
        mode: {
            str(theta): next(
                c["cartel_capture_rate"] for c in cells
                if c["pair_aggregation"] == mode and c["theta_pair"] == theta
            )
            for theta in THETA_VALUES
        }
        for mode in PAIR_AGGREGATIONS
    }


def main():
    if not PRE.exists():
        raise FileNotFoundError(PRE)
    pre = json.loads(PRE.read_text(encoding="utf-8"))

    rng = np.random.default_rng(SEED_MASTER)
    seeds = [int(x) for x in rng.integers(0, 2**31, size=SEEDS_PER_CELL)]
    if pre["common_seeds"] != seeds:
        raise RuntimeError("pre-budget structural seeds mismatch")

    t0 = time.time()
    cells = [
        run_cell(mode, theta, seeds)
        for mode in PAIR_AGGREGATIONS
        for theta in THETA_VALUES
    ]
    post_matrix = matrix(cells)
    pre_matrix = pre["cartel_capture_rate_matrix"]

    diffs = {
        mode: {
            str(theta): (
                float(post_matrix[mode][str(theta)])
                - float(pre_matrix[mode][str(theta)])
            )
            for theta in THETA_VALUES
        }
        for mode in PAIR_AGGREGATIONS
    }

    payload = {
        "schema": "twelve-gates/structural-robustness-v032-post-budget/v1",
        "claim_label": "exploratory_structural_uncertainty",
        "not_calibration": True,
        "not_empirical_validation": True,
        "git_head": git_head(),
        "script_sha256": sha256_file(__file__),
        "pre_budget_artifact_sha256": sha256_file(PRE),
        "pair_aggregation_modes": PAIR_AGGREGATIONS,
        "theta_values": THETA_VALUES,
        "seeds_per_cell": SEEDS_PER_CELL,
        "common_seeds": seeds,
        "max_ticks": MAX_TICKS,
        "cells": cells,
        "cartel_capture_rate_matrix": post_matrix,
        "pre_budget_cartel_capture_rate_matrix": pre_matrix,
        "paired_rate_differences": diffs,
        "elapsed_seconds": round(time.time() - t0, 3),
        "interpretation_boundary": (
            "Paired structural uncertainty comparison inside an uncalibrated "
            "simulation. No mode is selected or ranked as a political design."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    lines = [
        "# v0.32 Structural Robustness — Post Budget-Majority Fix",
        "",
        "**Claim class:** exploratory structural uncertainty  ",
        "**Calibration:** no  ",
        f"**Design:** 3 aggregation modes × 3 theta values × {SEEDS_PER_CELL} common seeds",
        "",
        "This is a paired rerun of the previous structural experiment after correcting the budget vote threshold from 7/12 to 8/12.",
        "",
        "## Post-fix modeled capture frequencies",
        "",
        "| aggregation | " + " | ".join(f"θ={x:.3f}" for x in THETA_VALUES) + " |",
        "|" + "---|" * (len(THETA_VALUES)+1),
    ]
    for mode in PAIR_AGGREGATIONS:
        vals=[post_matrix[mode][str(t)] for t in THETA_VALUES]
        lines.append("| "+mode+" | "+" | ".join(f"{v:.3f}" for v in vals)+" |")
    lines += [
        "",
        "## Paired difference vs pre-budget implementation",
        "",
        "| aggregation | " + " | ".join(f"θ={x:.3f}" for x in THETA_VALUES) + " |",
        "|" + "---|" * (len(THETA_VALUES)+1),
    ]
    for mode in PAIR_AGGREGATIONS:
        vals=[diffs[mode][str(t)] for t in THETA_VALUES]
        lines.append("| "+mode+" | "+" | ".join(f"{v:+.3f}" for v in vals)+" |")
    lines += [
        "",
        "## Interpretation boundary",
        "",
        payload["interpretation_boundary"],
    ]
    DOC.write_text("\n".join(lines)+"\n", encoding="utf-8")

    print(json.dumps({
        "git_head": payload["git_head"],
        "elapsed_seconds": payload["elapsed_seconds"],
        "post_matrix": post_matrix,
        "differences": diffs,
        "output": str(OUT.relative_to(ROOT)),
        "doc": str(DOC.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
