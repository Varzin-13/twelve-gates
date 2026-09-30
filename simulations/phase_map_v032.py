#!/usr/bin/env python3
"""Focused theta_pair × material-power phase map for Twelve Gates v0.32.

Exploratory only. No calibration, validation, causal estimate, or political
forecast is claimed. The grid is chosen because the preceding LHS screening
identified these two assumptions as the strongest associations with the
model's cartel-capture endpoint.
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


CLAIM_LABEL = "exploratory_hypothesis"
THETA_VALUES = [0.50, 0.525, 0.55, 0.575, 0.60, 0.625, 0.65, 0.675, 0.70]
POWER_MULTIPLIERS = [0.70, 0.7666666667, 0.8333333333, 0.90, 0.9666666667, 1.0333333333, 1.10]
SEEDS_PER_CELL = 8
MAX_TICKS = 520
SEED_MASTER = 42032

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "phase_map_v032_results.json"
DOC = ROOT / "docs" / "PHASE_MAP_V032_2026-09-30.md"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def config_for(theta, multiplier):
    cfg = copy.deepcopy(BASELINE_CFG)
    cfg["coalitions"]["theta_pair"] = float(theta)
    cluster = set(cfg["coalitions"]["cartel"]["material_cluster"])
    for gate in cfg["gates"]:
        if gate["gate_id"] in cluster:
            gate["exec_power"] = float(np.clip(
                gate["exec_power"] * multiplier, 0.0, 1.0
            ))
    return cfg


def run_cell(theta, multiplier, seeds):
    captures = []
    emergencies = []
    coalition_durations = []
    for seed in seeds:
        m = TwelveGatesModel(config_for(theta, multiplier), seed=seed)
        m.external = StressDriver([])
        out = m.run(MAX_TICKS)
        captures.append(1.0 if out["cartel_capture_ever"] else 0.0)
        emergencies.append(float(out["emergency_time_share"]))
        coalition_durations.append(float(out["coalition_mean_duration"]))
    return {
        "theta_pair": float(theta),
        "material_exec_multiplier": float(multiplier),
        "cartel_capture_rate": float(np.mean(captures)),
        "cartel_capture_sd_across_seeds": float(np.std(captures, ddof=1)),
        "emergency_time_share_mean": float(np.mean(emergencies)),
        "legacy_dissolved_coalition_duration_mean": float(
            np.mean(coalition_durations)
        ),
    }


def boundary_for_multiplier(cells, multiplier):
    row = sorted(
        [c for c in cells if c["material_exec_multiplier"] == multiplier],
        key=lambda c: c["theta_pair"],
    )
    candidates = [
        c["theta_pair"] for c in row if c["cartel_capture_rate"] <= 0.5
    ]
    return None if not candidates else min(candidates)


def monotonic_violations(cells, multiplier):
    row = sorted(
        [c for c in cells if c["material_exec_multiplier"] == multiplier],
        key=lambda c: c["theta_pair"],
    )
    vals = [c["cartel_capture_rate"] for c in row]
    # Expected screening direction from LHS: non-increasing with theta.
    return sum(1 for a, b in zip(vals, vals[1:]) if b > a)


def main():
    t0 = time.time()
    seed_rng = np.random.default_rng(SEED_MASTER)
    seeds = [int(x) for x in seed_rng.integers(0, 2**31, size=SEEDS_PER_CELL)]

    cells = []
    for multiplier in POWER_MULTIPLIERS:
        for theta in THETA_VALUES:
            cells.append(run_cell(theta, multiplier, seeds))

    boundaries = {
        str(mult): boundary_for_multiplier(cells, mult)
        for mult in POWER_MULTIPLIERS
    }
    violations = {
        str(mult): monotonic_violations(cells, mult)
        for mult in POWER_MULTIPLIERS
    }

    matrix = []
    for mult in POWER_MULTIPLIERS:
        row = {"material_exec_multiplier": mult}
        for theta in THETA_VALUES:
            cell = next(
                c for c in cells
                if c["material_exec_multiplier"] == mult
                and c["theta_pair"] == theta
            )
            row[f"theta_{theta:.3f}"] = cell["cartel_capture_rate"]
        matrix.append(row)

    payload = {
        "schema": "twelve-gates/phase-map-v032/v1",
        "claim_label": CLAIM_LABEL,
        "not_calibration": True,
        "not_empirical_validation": True,
        "git_head": git_head(),
        "script_sha256": sha256_file(__file__),
        "model_sha256": sha256_file(HERE / "twelve_gates_model.py"),
        "baseline_script_sha256": sha256_file(HERE / "run_baseline.py"),
        "theta_values": THETA_VALUES,
        "material_exec_multipliers": POWER_MULTIPLIERS,
        "seeds_per_cell": SEEDS_PER_CELL,
        "common_seeds": seeds,
        "max_ticks": MAX_TICKS,
        "cells": cells,
        "cartel_rate_matrix": matrix,
        "first_theta_with_rate_at_or_below_0_5_by_multiplier": boundaries,
        "nonincreasing_theta_monotonicity_violations_by_multiplier": violations,
        "elapsed_seconds": round(time.time() - t0, 3),
        "interpretation_boundary": (
            "Finite two-parameter behavior map under arbitrary scenario assumptions. "
            "Cell rates are Monte Carlo frequencies inside the model, not real-world "
            "political probabilities."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    lines = [
        "# v0.32 Theta × Material-Power Phase Map",
        "",
        "**Claim class:** exploratory simulation  ",
        "**Calibration:** no  ",
        f"**Grid:** {len(THETA_VALUES)} theta values × {len(POWER_MULTIPLIERS)} power multipliers × {SEEDS_PER_CELL} common seeds",
        "",
        "Each cell is the fraction of the eight seeded model runs in which the current coded cartel criterion was ever reached.",
        "These cell rates are not real-world probabilities.",
        "",
        "## Cartel-capture-rate matrix",
        "",
        "| power multiplier | " + " | ".join(f"θ={x:.3f}" for x in THETA_VALUES) + " |",
        "|" + "---|" * (len(THETA_VALUES)+1),
    ]
    for row in matrix:
        vals = [
            row[f"theta_{theta:.3f}"]
            for theta in THETA_VALUES
        ]
        lines.append(
            f"| {row['material_exec_multiplier']:.3f} | "
            + " | ".join(f"{v:.3f}" for v in vals) + " |"
        )

    lines += [
        "",
        "## First sampled theta where modeled rate <= 0.5",
        "",
    ]
    for mult in POWER_MULTIPLIERS:
        b = boundaries[str(mult)]
        lines.append(f"- power multiplier {mult:.3f}: {b if b is not None else 'not reached on grid'}")

    lines += [
        "",
        "## Monotonicity diagnostic",
        "",
        "Count of adjacent increases in capture rate as theta rises (0 means the sampled row is non-increasing):",
    ]
    for mult in POWER_MULTIPLIERS:
        lines.append(f"- power multiplier {mult:.3f}: {violations[str(mult)]}")

    lines += [
        "",
        "## Interpretation boundary",
        "",
        payload["interpretation_boundary"],
        "",
        "This focused map follows the LHS screening result. It does not promote either parameter to an empirical estimate.",
    ]
    DOC.write_text("\n".join(lines)+"\n", encoding="utf-8")

    print(json.dumps({
        "git_head": payload["git_head"],
        "elapsed_seconds": payload["elapsed_seconds"],
        "boundaries": boundaries,
        "monotonicity_violations": violations,
        "output": str(OUT.relative_to(ROOT)),
        "doc": str(DOC.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
