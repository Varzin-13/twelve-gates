#!/usr/bin/env python3
"""Refined post-budget phase map around the coded theta/power boundary.

Exploratory simulation only. The grid is intentionally concentrated around:
- theta_pair transition seen in earlier screening;
- the exact material-triad power threshold 1.8 / 2.3.

Cell frequencies are model Monte Carlo frequencies, not real-world political
probabilities.
"""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
import subprocess
import time
from pathlib import Path

RUN_LABEL = "refined-post-budget-phase-map"

import numpy as np

from run_baseline import BASELINE_CFG
from run_stress import StressDriver
from twelve_gates_model import TwelveGatesModel


CLAIM_LABEL = "exploratory_refined_phase_map"
THETA_VALUES = [0.56, 0.57, 0.58, 0.59, 0.60, 0.61, 0.62, 0.63]
POWER_MULTIPLIERS = [0.775, 0.780, 0.7825, 0.7827, 0.785, 0.790, 0.800]
SEEDS_PER_CELL = 12
MAX_TICKS = 520
SEED_MASTER = 62032

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "phase_map_v032_post_budget_refined_results.json"
DOC = ROOT / "docs" / "PHASE_MAP_V032_POST_BUDGET_REFINED_2026-10-01.md"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


CLUSTER = set(BASELINE_CFG["coalitions"]["cartel"]["material_cluster"])
BASE_TRIAD_POWER = float(sum(
    g["exec_power"] for g in BASELINE_CFG["gates"]
    if g["gate_id"] in CLUSTER
))
THETA_POWER = float(BASELINE_CFG["coalitions"]["cartel"]["theta_power_sum"])
MECHANICAL_MULTIPLIER_THRESHOLD = THETA_POWER / BASE_TRIAD_POWER


def config_for(theta, multiplier):
    cfg = copy.deepcopy(BASELINE_CFG)
    cfg["coalitions"]["theta_pair"] = float(theta)
    cfg["coalitions"]["pair_aggregation"] = "mean"
    for gate in cfg["gates"]:
        if gate["gate_id"] in CLUSTER:
            gate["exec_power"] = float(np.clip(
                gate["exec_power"] * multiplier, 0.0, 1.0
            ))
    return cfg


def mean_optional(values):
    xs = [float(x) for x in values if x is not None]
    return None if not xs else float(np.mean(xs))


def run_cell(theta, multiplier, seeds):
    runs=[]
    for seed in seeds:
        model=TwelveGatesModel(config_for(theta,multiplier),seed=seed)
        model.external=StressDriver([])
        runs.append(model.run(MAX_TICKS))

    captures=[r for r in runs if r["cartel_capture_ever"]]
    member_counts=Counter(
        tuple(r["cartel_first_snapshot"]["members"])
        for r in captures
        if r["cartel_first_snapshot"] is not None
    )
    first_ticks=[
        int(r["cartel_first_detected_tick"]) for r in captures
        if r["cartel_first_detected_tick"] is not None
    ]
    triad_hits=member_counts.get((0,2,4),0)

    return {
        "theta_pair":float(theta),
        "material_exec_multiplier":float(multiplier),
        "mechanical_material_triad_power_condition": bool(
            BASE_TRIAD_POWER * multiplier > THETA_POWER
        ),
        "cartel_capture_rate":float(len(captures)/len(runs)),
        "captured_runs":len(captures),
        "first_trigger_triad_0_2_4_fraction_among_captures": (
            None if not captures else float(triad_hits/len(captures))
        ),
        "first_trigger_member_counts":{
            ",".join(map(str,k)):int(v)
            for k,v in sorted(member_counts.items(),key=lambda kv:(-kv[1],kv[0]))
        },
        "first_trigger_tick_median": (
            None if not first_ticks else float(np.median(first_ticks))
        ),
        "proposal_pass_fraction_mean_valid_runs":mean_optional([
            r["proposal_pass_fraction"] for r in runs
        ]),
        "coalition_rmst_ticks_mean_valid_runs":mean_optional([
            r["coalition_rmst_ticks"] for r in runs
        ]),
        "emergency_time_share_mean":float(np.mean([
            r["emergency_time_share"] for r in runs
        ])),
    }


def main():
    t0=time.time()
    rng=np.random.default_rng(SEED_MASTER)
    seeds=[int(x) for x in rng.integers(0,2**31,size=SEEDS_PER_CELL)]

    cells=[
        run_cell(theta,mult,seeds)
        for mult in POWER_MULTIPLIERS
        for theta in THETA_VALUES
    ]

    matrix=[]
    for mult in POWER_MULTIPLIERS:
        row={"material_exec_multiplier":mult}
        for theta in THETA_VALUES:
            c=next(x for x in cells
                   if x["material_exec_multiplier"]==mult
                   and x["theta_pair"]==theta)
            row[f"theta_{theta:.3f}"]=c["cartel_capture_rate"]
        matrix.append(row)

    violations={}
    for mult in POWER_MULTIPLIERS:
        vals=[
            next(x for x in cells
                 if x["material_exec_multiplier"]==mult
                 and x["theta_pair"]==theta)["cartel_capture_rate"]
            for theta in THETA_VALUES
        ]
        violations[str(mult)]=sum(
            1 for a,b in zip(vals,vals[1:]) if b>a
        )

    payload={
        "schema":"twelve-gates/phase-map-v032-post-budget-refined/v1",
        "claim_label":CLAIM_LABEL,
        "not_calibration":True,
        "not_empirical_validation":True,
        "git_head":git_head(),
        "script_sha256":sha256_file(__file__),
        "model_sha256":sha256_file(HERE/"twelve_gates_model.py"),
        "baseline_script_sha256":sha256_file(HERE/"run_baseline.py"),
        "theta_values":THETA_VALUES,
        "material_exec_multipliers":POWER_MULTIPLIERS,
        "seeds_per_cell":SEEDS_PER_CELL,
        "common_seeds":seeds,
        "max_ticks":MAX_TICKS,
        "mechanical_material_triad":{
            "baseline_power_sum":BASE_TRIAD_POWER,
            "cartel_power_threshold":THETA_POWER,
            "strict_multiplier_threshold":MECHANICAL_MULTIPLIER_THRESHOLD,
        },
        "cells":cells,
        "cartel_capture_rate_matrix":matrix,
        "nonincreasing_theta_monotonicity_violations_by_multiplier":violations,
        "elapsed_seconds":round(time.time()-t0,3),
        "interpretation_boundary":(
            "Refined finite behavior map around coded thresholds under arbitrary "
            "assumptions. Cell frequencies are not real-world probabilities."
        ),
    }
    RESULTS.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    lines=[
        "# v0.32 Refined Post-Budget Theta × Power Phase Map",
        "",
        "**Claim class:** exploratory simulation  ",
        "**Calibration:** no  ",
        f"**Grid:** {len(THETA_VALUES)} theta values × {len(POWER_MULTIPLIERS)} power multipliers × {SEEDS_PER_CELL} common seeds",
        "",
        f"Exact material-triad multiplier threshold from the coded power criterion: **> {MECHANICAL_MULTIPLIER_THRESHOLD:.9f}**.",
        "",
        "## Modeled capture-frequency matrix",
        "",
        "| power multiplier | "+" | ".join(f"θ={t:.3f}" for t in THETA_VALUES)+" |",
        "|"+"---|"*(len(THETA_VALUES)+1),
    ]
    for row in matrix:
        vals=[row[f"theta_{t:.3f}"] for t in THETA_VALUES]
        lines.append(
            f"| {row['material_exec_multiplier']:.4f} | "
            +" | ".join(f"{v:.3f}" for v in vals)+" |"
        )

    lines += [
        "",
        "## Trigger diagnostics",
        "",
        "| power | theta | captures | triad fraction among captures | median first tick | proposal pass fraction |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for c in cells:
        tri=c["first_trigger_triad_0_2_4_fraction_among_captures"]
        tick=c["first_trigger_tick_median"]
        pp=c["proposal_pass_fraction_mean_valid_runs"]
        lines.append(
            f"| {c['material_exec_multiplier']:.4f} | {c['theta_pair']:.3f} | "
            f"{c['captured_runs']}/{SEEDS_PER_CELL} | "
            f"{'n/a' if tri is None else f'{tri:.3f}'} | "
            f"{'n/a' if tick is None else f'{tick:.1f}'} | "
            f"{'n/a' if pp is None else f'{pp:.3f}'} |"
        )

    lines += [
        "",
        "## Interpretation boundary",
        "",
        payload["interpretation_boundary"],
        "",
        "The exact power threshold is a property of the coded operational definition. "
        "The simulation is used to study interaction with coalition formation and theta, "
        "not to present that threshold as an empirical discovery.",
    ]
    DOC.write_text("\n".join(lines)+"\n",encoding="utf-8")

    print(json.dumps({
        "git_head":payload["git_head"],
        "elapsed_seconds":payload["elapsed_seconds"],
        "mechanical_threshold":MECHANICAL_MULTIPLIER_THRESHOLD,
        "output":str(OUT.relative_to(ROOT)),
        "doc":str(DOC.relative_to(ROOT)),
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
