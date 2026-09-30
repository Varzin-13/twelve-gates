#!/usr/bin/env python3
"""Paired stress rerun after numerical strict-threshold hygiene.

This isolates the software effect of treating floating values numerically equal
to crisis thresholds as equality, rather than accidental strict crossings.
It is not calibration or a real-world political probability.
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
from twelve_gates_model import TwelveGatesModel, NUMERIC_ATOL


N_RUNS = 300
MAX_TICKS = 520
MASTER_SEED = 43

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "stress_v032_post_numeric_threshold_results.json"
DOC = ROOT / "docs" / "STRESS_V032_POST_NUMERIC_THRESHOLD_2026-10-01.md"
PRE = RESULTS / "stress_v032_post_budget_majority_results.json"


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


def mean_optional(xs):
    vals=[float(x) for x in xs if x is not None]
    return None if not vals else float(np.mean(vals))


def summarize(runs):
    decisions=sum(r["proposals_voted_pass"]+r["proposals_voted_fail"] for r in runs)
    passed=sum(r["proposals_voted_pass"] for r in runs)
    critical=sum(r["critical_reports_total"] for r in runs)
    dissents=sum(r["dissent_events_total"] for r in runs)
    members=Counter(
        tuple(r["cartel_first_snapshot"]["members"])
        for r in runs if r["cartel_first_snapshot"] is not None
    )
    return {
        "cartel_capture_rate":float(np.mean([r["cartel_capture_ever"] for r in runs])),
        "emergency_time_share_mean":float(np.mean([r["emergency_time_share"] for r in runs])),
        "legacy_dissolved_coalition_duration_mean":float(np.mean([
            r["coalition_duration_legacy_dissolved_mean"] for r in runs
        ])),
        "coalition_rmst_ticks_mean_valid_runs":mean_optional([
            r["coalition_rmst_ticks"] for r in runs
        ]),
        "mean_internal_legitimacy":float(np.mean([r["mean_legitimacy_end"] for r in runs])),
        "proposal_decisions_total":int(decisions),
        "proposal_decisions_per_run":float(decisions/len(runs)),
        "proposal_passed_total":int(passed),
        "proposal_failed_total":int(decisions-passed),
        "proposal_pass_fraction_weighted":None if decisions==0 else float(passed/decisions),
        "critical_reports_total":int(critical),
        "critical_reports_per_run":float(critical/len(runs)),
        "dissent_events_total":int(dissents),
        "first_cartel_members_counts":{
            ",".join(map(str,k)):int(v)
            for k,v in sorted(members.items(),key=lambda kv:(-kv[1],kv[0]))
        },
    }


def paired_compare(pre, post, seeds):
    if pre["run_seeds"] != seeds:
        raise RuntimeError("pre-numeric artifact seeds mismatch")
    old=pre["run_results"]
    if len(old)!=len(post):
        raise RuntimeError("paired run count mismatch")

    old_cap=[bool(x["cartel_capture_ever"]) for x in old]
    new_cap=[bool(x["cartel_capture_ever"]) for x in post]
    trans=Counter(zip(old_cap,new_cap))

    old_decisions=[
        int(x["proposals_voted_pass"])+int(x["proposals_voted_fail"])
        for x in old
    ]
    new_decisions=[
        int(x["proposals_voted_pass"])+int(x["proposals_voted_fail"])
        for x in post
    ]

    return {
        "capture_transition_counts":{
            "false_to_false":int(trans[(False,False)]),
            "false_to_true":int(trans[(False,True)]),
            "true_to_false":int(trans[(True,False)]),
            "true_to_true":int(trans[(True,True)]),
        },
        "cartel_capture_rate_pre":float(np.mean(old_cap)),
        "cartel_capture_rate_post":float(np.mean(new_cap)),
        "cartel_capture_rate_difference":float(np.mean(new_cap)-np.mean(old_cap)),
        "proposal_decisions_total_pre":int(sum(old_decisions)),
        "proposal_decisions_total_post":int(sum(new_decisions)),
        "proposal_decisions_total_difference":int(sum(new_decisions)-sum(old_decisions)),
        "proposal_decisions_per_run_difference":float(np.mean(
            np.array(new_decisions)-np.array(old_decisions)
        )),
        "emergency_time_share_paired_mean_difference":float(np.mean([
            n["emergency_time_share"]-o["emergency_time_share"]
            for o,n in zip(old,post)
        ])),
        "legacy_coalition_duration_paired_mean_difference":float(np.mean([
            n["coalition_duration_legacy_dissolved_mean"]-o["coalition_duration_legacy_dissolved_mean"]
            for o,n in zip(old,post)
        ])),
        "internal_legitimacy_paired_mean_difference":float(np.mean([
            n["mean_legitimacy_end"]-o["mean_legitimacy_end"]
            for o,n in zip(old,post)
        ])),
    }


def render(p):
    s=p["summary"]; d=p["paired_comparison"]; t=d["capture_transition_counts"]
    return f"""# v0.32 Post-Numeric-Threshold Stress Audit

**Claim class:** paired software-effect audit  
**Calibration:** no  
**Empirical validation:** no  
**Runs:** {p['n_runs']} × {p['max_ticks']} ticks  
**Master seed:** {p['master_seed']}  
**Numerical equality tolerance:** {p['numeric_atol']}

## Why this rerun exists

Repeated binary floating-point additions made 25 × 0.02 appear as a value
slightly above 0.5 and 30 × 0.02 slightly above 0.6. The old strict comparisons
therefore crossed crisis thresholds one tick earlier than the mathematical
decimal model implied.

The corrected helper treats values within a tiny numerical tolerance as equal
to the threshold. Probability draws and coalition theta/power comparisons were
not changed in this correction.

## Paired capture transition

| before numeric fix | after numeric fix | runs |
|---|---|---:|
| false | false | {t['false_to_false']} |
| false | true | {t['false_to_true']} |
| true | false | {t['true_to_false']} |
| true | true | {t['true_to_true']} |

- modeled capture rate before: {d['cartel_capture_rate_pre']:.6f}
- modeled capture rate after: {d['cartel_capture_rate_post']:.6f}
- difference: {d['cartel_capture_rate_difference']:+.6f}

## Proposal-count diagnostic

- proposal decisions before: {d['proposal_decisions_total_pre']}
- proposal decisions after: {d['proposal_decisions_total_post']}
- total difference: {d['proposal_decisions_total_difference']:+d}
- mean difference per run: {d['proposal_decisions_per_run_difference']:+.3f}
- post-fix decisions per run: {s['proposal_decisions_per_run']:.3f}

Under the stress construction, only gates 0/2/4 have sustained crisis-driven
proposal generation. The mathematical expectation after moving the first
proposal from the 25th to 26th shock is one fewer proposal tick × three gates
per run.

## Current post-fix diagnostics

- critical reports per run: {s['critical_reports_per_run']:.3f}
- weighted proposal pass fraction: {s['proposal_pass_fraction_weighted']:.6f}
- coalition RMST mean across valid runs: {s['coalition_rmst_ticks_mean_valid_runs']}
- emergency time share mean: {s['emergency_time_share_mean']:.6f}
- first-cartel member counts: {json.dumps(s['first_cartel_members_counts'], ensure_ascii=False)}

## Other paired mean differences

- emergency time share: {d['emergency_time_share_paired_mean_difference']:+.6f}
- legacy dissolved coalition duration: {d['legacy_coalition_duration_paired_mean_difference']:+.6f}
- internal legitimacy: {d['internal_legitimacy_paired_mean_difference']:+.6f}

## Provenance

- Git HEAD: `{p['git_head']}`
- runner SHA256: `{p['runner_sha256']}`
- model SHA256: `{p['model_sha256']}`
- config SHA256: `{p['baseline_config_canonical_sha256']}`
- pre-numeric artifact SHA256: `{p['pre_numeric_artifact_sha256']}`

## Interpretation boundary

This is a paired audit of a numerical implementation correction inside an
uncalibrated model. It is not evidence for a real-world political outcome.
"""


def main():
    pre=json.loads(PRE.read_text(encoding="utf-8"))
    rng=np.random.default_rng(MASTER_SEED)
    seeds=[int(x) for x in rng.integers(0,2**31,size=N_RUNS)]
    t0=time.time()
    runs=[]
    for seed in seeds:
        m=TwelveGatesModel(BASELINE_CFG,seed=seed)
        m.external=StressDriver([])
        runs.append(m.run(MAX_TICKS))

    payload={
        "schema":"twelve-gates/stress-v032-post-numeric-threshold/v1",
        "claim_label":"software_effect_hypothesis",
        "not_calibration":True,
        "not_empirical_validation":True,
        "git_head":git_head(),
        "runner_sha256":sha256_file(__file__),
        "model_sha256":sha256_file(HERE/"twelve_gates_model.py"),
        "baseline_config_canonical_sha256":canonical_config_sha256(BASELINE_CFG),
        "pre_numeric_artifact_sha256":sha256_file(PRE),
        "numeric_atol":NUMERIC_ATOL,
        "n_runs":N_RUNS,
        "max_ticks":MAX_TICKS,
        "master_seed":MASTER_SEED,
        "run_seeds":seeds,
        "summary":summarize(runs),
        "paired_comparison":paired_compare(pre,runs,seeds),
        "elapsed_seconds":round(time.time()-t0,3),
        "run_results":runs,
        "interpretation_boundary":(
            "Paired numerical software-effect audit under uncalibrated assumptions; "
            "not a real-world political probability."
        ),
    }
    RESULTS.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    DOC.write_text(render(payload),encoding="utf-8")
    print(json.dumps({
        "git_head":payload["git_head"],
        "elapsed_seconds":payload["elapsed_seconds"],
        "summary":payload["summary"],
        "paired_comparison":payload["paired_comparison"],
        "output":str(OUT.relative_to(ROOT)),
        "doc":str(DOC.relative_to(ROOT)),
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
