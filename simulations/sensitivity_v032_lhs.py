#!/usr/bin/env python3
"""Exploratory Latin-hypercube behavior-space analysis for Twelve Gates v0.32.

CLAIM BOUNDARY
--------------
This is NOT calibration, validation, forecasting, or an estimate of real-world
political probabilities. All ranges below are deliberately labeled ARBITRARY
exploration ranges. The purpose is to identify which assumptions dominate the
current model's outputs and where model conclusions are unstable.
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
N_POINTS = 64
SEEDS_PER_POINT = 6
MAX_TICKS = 520
DESIGN_SEED = 32032
RUN_SEED_MASTER = 32033

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "sensitivity_v032_lhs_results.json"
DOC = ROOT / "docs" / "SENSITIVITY_V032_LHS_2026-09-30.md"

RANGES = {
    "theta_pair": (0.45, 0.70),
    "material_exec_multiplier": (0.70, 1.10),
    "emergency_support_probability": (0.30, 0.80),
    "audit_detection_prob": (0.10, 0.70),
    "verification_accuracy": (0.60, 0.95),
    "trust_learning_rate": (0.02, 0.20),
    "vote_support_intercept": (0.25, 0.55),
    "bureaucracy_drift_rate": (0.0, 0.002),
}


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lhs(n, names, rng):
    design = np.empty((n, len(names)), dtype=float)
    for j, name in enumerate(names):
        lo, hi = RANGES[name]
        u = (np.arange(n, dtype=float) + rng.random(n)) / n
        rng.shuffle(u)
        design[:, j] = lo + u * (hi - lo)
    return design


def rank_average_ties(values):
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and values[order[j]] == values[order[i]]:
            j += 1
        avg_rank = (i + j - 1) / 2.0
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def rank_corr(x, y):
    rx = rank_average_ties(x)
    ry = rank_average_ties(y)
    sx = float(np.std(rx))
    sy = float(np.std(ry))
    if sx == 0 or sy == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def apply_point(base, point):
    cfg = copy.deepcopy(base)
    cfg["coalitions"]["theta_pair"] = float(point["theta_pair"])
    cfg["emergency_extension"]["support_probability"] = float(
        point["emergency_support_probability"]
    )
    cfg["trust_dynamics"]["audit_detection_prob"] = float(
        point["audit_detection_prob"]
    )
    cfg["trust_dynamics"]["trust_learning_rate"] = float(
        point["trust_learning_rate"]
    )
    cfg["model_assumptions"]["vote_support_intercept"] = float(
        point["vote_support_intercept"]
    )
    cfg["model_assumptions"]["bureaucracy_politicization_drift_rate"] = float(
        point["bureaucracy_drift_rate"]
    )

    verification = float(point["verification_accuracy"])
    for g in cfg["gates"]:
        g["verification_accuracy"] = verification

    multiplier = float(point["material_exec_multiplier"])
    cluster = set(cfg["coalitions"]["cartel"]["material_cluster"])
    for g in cfg["gates"]:
        if g["gate_id"] in cluster:
            g["exec_power"] = float(np.clip(g["exec_power"] * multiplier, 0, 1))
    return cfg


def summarize_runs(runs):
    def vals(key):
        return np.array([float(r[key]) for r in runs], dtype=float)

    cartel = np.array([1.0 if r["cartel_capture_ever"] else 0.0 for r in runs])
    outputs = {
        "cartel_capture_rate": float(cartel.mean()),
        "emergency_time_share_mean": float(vals("emergency_time_share").mean()),
        "coalition_mean_duration_mean": float(vals("coalition_mean_duration").mean()),
        "legitimacy_internal_mean": float(vals("mean_legitimacy_end").mean()),
        "capture_pressure_mean": float(vals("mean_capture_pressure_end").mean()),
        "bureaucracy_politicization_mean": float(
            vals("bureaucracy_politicization_end").mean()
        ),
        "civil_society_legitimacy_proxy_mean": float(
            vals("civil_society_legitimacy_proxy_end").mean()
        ),
    }
    mcse = {
        "cartel_capture_rate_sd_across_seeds": float(cartel.std(ddof=1))
        if len(cartel) > 1 else 0.0,
        "emergency_time_share_sd_across_seeds": float(
            vals("emergency_time_share").std(ddof=1)
        ) if len(runs) > 1 else 0.0,
        "coalition_mean_duration_sd_across_seeds": float(
            vals("coalition_mean_duration").std(ddof=1)
        ) if len(runs) > 1 else 0.0,
    }
    return outputs, mcse


def main():
    t0 = time.time()
    names = list(RANGES)
    design_rng = np.random.default_rng(DESIGN_SEED)
    design = lhs(N_POINTS, names, design_rng)

    seed_rng = np.random.default_rng(RUN_SEED_MASTER)
    common_seeds = [
        int(x) for x in seed_rng.integers(0, 2**31, size=SEEDS_PER_POINT)
    ]

    points = []
    for idx in range(N_POINTS):
        params = {name: float(design[idx, j]) for j, name in enumerate(names)}
        cfg = apply_point(BASELINE_CFG, params)
        runs = []
        for seed in common_seeds:
            model = TwelveGatesModel(cfg, seed=seed)
            model.external = StressDriver([])
            runs.append(model.run(MAX_TICKS))
        outputs, seed_dispersion = summarize_runs(runs)
        points.append({
            "point_id": idx,
            "parameters": params,
            "outputs": outputs,
            "seed_dispersion": seed_dispersion,
        })

    output_names = list(points[0]["outputs"])
    correlations = {}
    for out_name in output_names:
        y = [p["outputs"][out_name] for p in points]
        correlations[out_name] = {
            name: rank_corr([p["parameters"][name] for p in points], y)
            for name in names
        }

    ranges_observed = {
        out_name: {
            "min": float(min(p["outputs"][out_name] for p in points)),
            "max": float(max(p["outputs"][out_name] for p in points)),
            "median": float(np.median([p["outputs"][out_name] for p in points])),
        }
        for out_name in output_names
    }

    payload = {
        "schema": "twelve-gates/sensitivity-v032-lhs/v1",
        "claim_label": CLAIM_LABEL,
        "not_calibration": True,
        "not_empirical_validation": True,
        "git_head": git_head(),
        "script_sha256": sha256_file(__file__),
        "model_sha256": sha256_file(HERE / "twelve_gates_model.py"),
        "baseline_script_sha256": sha256_file(HERE / "run_baseline.py"),
        "n_points": N_POINTS,
        "seeds_per_point": SEEDS_PER_POINT,
        "max_ticks": MAX_TICKS,
        "design_seed": DESIGN_SEED,
        "run_seed_master": RUN_SEED_MASTER,
        "common_run_seeds": common_seeds,
        "parameter_ranges": {
            k: {"min": v[0], "max": v[1], "status": "ARBITRARY_EXPLORATION_RANGE"}
            for k, v in RANGES.items()
        },
        "output_ranges": ranges_observed,
        "spearman_rank_correlations_exploratory": correlations,
        "points": points,
        "elapsed_seconds": round(time.time() - t0, 3),
        "interpretation_boundary": (
            "Rank correlations and output ranges describe this finite exploratory "
            "design only. They are not causal effects, calibrated estimates, or "
            "real-world political probabilities."
        ),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Compact human-readable report.
    lines = [
        "# v0.32 Latin-Hypercube Behavior-Space Exploration",
        "",
        "**Claim label:** exploratory hypothesis  ",
        "**Calibration:** no  ",
        "**Empirical validation:** no  ",
        f"**Design:** {N_POINTS} LHS points × {SEEDS_PER_POINT} common seeds × {MAX_TICKS} ticks",
        "",
        "All parameter ranges are arbitrary exploration ranges.",
        "",
        "## Output ranges",
        "",
        "| Output | Min | Median | Max |",
        "|---|---:|---:|---:|",
    ]
    for name, stats in ranges_observed.items():
        lines.append(
            f"| {name} | {stats['min']:.6f} | {stats['median']:.6f} | {stats['max']:.6f} |"
        )

    lines += [
        "",
        "## Exploratory rank correlations",
        "",
        "These are Spearman rank correlations across the 64 LHS point means. "
        "They are screening statistics, not causal coefficients or significance tests.",
        "",
    ]
    for out_name, corrs in correlations.items():
        ranked = sorted(
            ((k, v) for k, v in corrs.items() if v is not None),
            key=lambda kv: abs(kv[1]),
            reverse=True,
        )
        lines.append(f"### {out_name}")
        for name, value in ranked:
            lines.append(f"- {name}: {value:+.3f}")
        lines.append("")

    lines += [
        "## Interpretation boundary",
        "",
        payload["interpretation_boundary"],
        "",
        "The full JSON preserves every LHS point, parameter vector, common seed set, "
        "point-level output, and provenance hash.",
    ]
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "git_head": payload["git_head"],
        "n_points": N_POINTS,
        "seeds_per_point": SEEDS_PER_POINT,
        "elapsed_seconds": payload["elapsed_seconds"],
        "output_ranges": ranges_observed,
        "output": str(OUT.relative_to(ROOT)),
        "doc": str(DOC.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
