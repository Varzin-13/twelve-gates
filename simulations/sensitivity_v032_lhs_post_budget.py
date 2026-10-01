#!/usr/bin/env python3
"""Paired LHS behavior-space rerun after correcting the 2/3 budget rule."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from run_baseline import BASELINE_CFG
from run_stress import StressDriver
from twelve_gates_model import TwelveGatesModel
from sensitivity_v032_lhs import (
    RANGES,
    N_POINTS,
    SEEDS_PER_POINT,
    MAX_TICKS,
    DESIGN_SEED,
    RUN_SEED_MASTER,
    lhs,
    rank_corr,
    apply_point,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "sensitivity_v032_lhs_post_budget_results.json"
DOC = ROOT / "docs" / "SENSITIVITY_V032_LHS_POST_BUDGET_2026-10-01.md"
PRE = RESULTS / "sensitivity_v032_lhs_results.json"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def mean_optional(values):
    xs=[float(x) for x in values if x is not None]
    return None if not xs else float(np.mean(xs))


def summarize_runs(runs):
    cartel=np.array([1.0 if r["cartel_capture_ever"] else 0.0 for r in runs])
    return {
        "cartel_capture_rate": float(cartel.mean()),
        "emergency_time_share_mean": float(np.mean([r["emergency_time_share"] for r in runs])),
        "coalition_rmst_ticks_mean_valid_runs": mean_optional([r["coalition_rmst_ticks"] for r in runs]),
        "legitimacy_internal_mean": float(np.mean([r["mean_legitimacy_end"] for r in runs])),
        "capture_pressure_mean": float(np.mean([r["mean_capture_pressure_end"] for r in runs])),
        "bureaucracy_politicization_mean": float(np.mean([r["bureaucracy_politicization_end"] for r in runs])),
        "civil_society_legitimacy_proxy_mean": float(np.mean([r["civil_society_legitimacy_proxy_end"] for r in runs])),
        "proposal_pass_fraction_mean_valid_runs": mean_optional([r["proposal_pass_fraction"] for r in runs]),
    }


def main():
    if not PRE.exists():
        raise FileNotFoundError(PRE)
    pre=json.loads(PRE.read_text(encoding="utf-8"))

    names=list(RANGES)
    design_rng=np.random.default_rng(DESIGN_SEED)
    design=lhs(N_POINTS,names,design_rng)
    seed_rng=np.random.default_rng(RUN_SEED_MASTER)
    common_seeds=[int(x) for x in seed_rng.integers(0,2**31,size=SEEDS_PER_POINT)]

    if pre["common_run_seeds"] != common_seeds:
        raise RuntimeError("pre-budget LHS run seeds mismatch")

    t0=time.time()
    points=[]
    for idx in range(N_POINTS):
        params={name:float(design[idx,j]) for j,name in enumerate(names)}
        cfg=apply_point(BASELINE_CFG,params)
        runs=[]
        for seed in common_seeds:
            m=TwelveGatesModel(cfg,seed=seed)
            m.external=StressDriver([])
            runs.append(m.run(MAX_TICKS))
        points.append({
            "point_id":idx,
            "parameters":params,
            "outputs":summarize_runs(runs),
        })

    output_names=list(points[0]["outputs"])
    correlations={}
    for out_name in output_names:
        y=[p["outputs"][out_name] for p in points]
        if any(v is None for v in y):
            correlations[out_name]={name:None for name in names}
        else:
            correlations[out_name]={
                name:rank_corr([p["parameters"][name] for p in points],y)
                for name in names
            }

    capture_diffs=[]
    changed_points=[]
    for old,new in zip(pre["points"],points):
        if old["point_id"] != new["point_id"]:
            raise RuntimeError("point ordering mismatch")
        d=float(new["outputs"]["cartel_capture_rate"])-float(old["outputs"]["cartel_capture_rate"])
        capture_diffs.append(d)
        if abs(d)>1e-12:
            changed_points.append({
                "point_id":new["point_id"],
                "difference":d,
                "pre":old["outputs"]["cartel_capture_rate"],
                "post":new["outputs"]["cartel_capture_rate"],
            })

    ranges={
        name:{
            "min":float(min(p["outputs"][name] for p in points if p["outputs"][name] is not None)),
            "max":float(max(p["outputs"][name] for p in points if p["outputs"][name] is not None)),
            "median":float(np.median([p["outputs"][name] for p in points if p["outputs"][name] is not None])),
        }
        for name in output_names
        if any(p["outputs"][name] is not None for p in points)
    }

    payload={
        "schema":"twelve-gates/sensitivity-v032-lhs-post-budget/v1",
        "claim_label":"exploratory_hypothesis",
        "not_calibration":True,
        "not_empirical_validation":True,
        "git_head":git_head(),
        "script_sha256":sha256_file(__file__),
        "pre_budget_artifact_sha256":sha256_file(PRE),
        "n_points":N_POINTS,
        "seeds_per_point":SEEDS_PER_POINT,
        "max_ticks":MAX_TICKS,
        "design_seed":DESIGN_SEED,
        "run_seed_master":RUN_SEED_MASTER,
        "common_run_seeds":common_seeds,
        "parameter_ranges":pre["parameter_ranges"],
        "output_ranges":ranges,
        "spearman_rank_correlations_exploratory":correlations,
        "paired_cartel_capture_point_differences":{
            "n_changed_points":len(changed_points),
            "mean_difference":float(np.mean(capture_diffs)),
            "mean_absolute_difference":float(np.mean(np.abs(capture_diffs))),
            "max_absolute_difference":float(np.max(np.abs(capture_diffs))),
            "changed_points":changed_points,
        },
        "points":points,
        "elapsed_seconds":round(time.time()-t0,3),
        "interpretation_boundary":(
            "Paired exploratory behavior-space comparison after a software-rule "
            "correction. Rank correlations are screening statistics, not causal "
            "effects or real-world political probabilities."
        ),
    }
    RESULTS.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    cartel_corr=correlations["cartel_capture_rate"]
    ranked=sorted(
        [(k,v) for k,v in cartel_corr.items() if v is not None],
        key=lambda kv:abs(kv[1]), reverse=True
    )
    lines=[
        "# v0.32 LHS Sensitivity — Post Budget-Majority Fix",
        "",
        "**Claim class:** exploratory hypothesis  ",
        "**Calibration:** no  ",
        f"**Design:** {N_POINTS} paired LHS points × {SEEDS_PER_POINT} common seeds × {MAX_TICKS} ticks",
        "",
        "Same design and run seeds as the pre-budget LHS; only the code/config lineage is updated.",
        "",
        "## Paired impact on modeled cartel-capture point means",
        "",
        f"- changed LHS points: {len(changed_points)} / {N_POINTS}",
        f"- mean difference: {float(np.mean(capture_diffs)):+.6f}",
        f"- mean absolute difference: {float(np.mean(np.abs(capture_diffs))):.6f}",
        f"- max absolute difference: {float(np.max(np.abs(capture_diffs))):.6f}",
        "",
        "## Post-fix exploratory rank correlations for cartel-capture rate",
        "",
    ]
    for name,val in ranked:
        lines.append(f"- {name}: {val:+.3f}")
    lines += [
        "",
        "## Post-fix output ranges",
        "",
        "| output | min | median | max |",
        "|---|---:|---:|---:|",
    ]
    for name,st in ranges.items():
        lines.append(f"| {name} | {st['min']:.6f} | {st['median']:.6f} | {st['max']:.6f} |")
    lines += [
        "",
        "## Interpretation boundary",
        "",
        payload["interpretation_boundary"],
    ]
    DOC.write_text("\n".join(lines)+"\n",encoding="utf-8")

    print(json.dumps({
        "git_head":payload["git_head"],
        "elapsed_seconds":payload["elapsed_seconds"],
        "changed_capture_points":len(changed_points),
        "mean_abs_capture_difference":float(np.mean(np.abs(capture_diffs))),
        "cartel_rank_correlations":cartel_corr,
        "output":str(OUT.relative_to(ROOT)),
        "doc":str(DOC.relative_to(ROOT)),
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
