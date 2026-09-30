#!/usr/bin/env python3
"""Provenance-complete stress rerun for the v0.32 execution-audit branch.

This runner records behavior of the current uncalibrated hypothesis model only.
It is not a real-world forecast or empirical validation.
"""
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


N_RUNS = 300
MAX_TICKS = 520
MASTER_SEED = 43
RUN_LABEL = "v0.32-final-execution-audit"


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT = RESULTS / "stress_v032_execution_audit_results.json"
AUDIT_MD = HERE.parent / "docs" / "STRESS_V032_EXECUTION_AUDIT_2026-09-30.md"
HISTORICAL = RESULTS / "mesa_stress_results.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_config_sha256(cfg: dict) -> str:
    raw = json.dumps(
        cfg, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(raw)


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=HERE.parent,
        text=True,
    ).strip()


def summarize(results: list[dict]) -> dict:
    return {
        "cartel_capture_rate": float(np.mean([r["cartel_capture_ever"] for r in results])),
        "emergency_time_share_mean": float(np.mean([r["emergency_time_share"] for r in results])),
        "coalition_mean_duration_mean": float(np.mean([r["coalition_mean_duration"] for r in results])),
        "legitimacy_internal_mean": float(np.mean([r["mean_legitimacy_end"] for r in results])),
        "capture_pressure_mean": float(np.mean([r["mean_capture_pressure_end"] for r in results])),
        "bureaucracy_politicization_mean": float(np.mean([r["bureaucracy_politicization_end"] for r in results])),
        "civil_society_legitimacy_proxy_mean": float(np.mean([r["civil_society_legitimacy_proxy_end"] for r in results])),
        "public_legitimacy_signal_mean_legacy_alias": float(np.mean([r["public_legitimacy_signal_end"] for r in results])),
    }


def historical_summary() -> dict | None:
    if not HISTORICAL.exists():
        return None
    data = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    keys = {
        "cartel_capture_rate": "cartel_capture_rate",
        "emergency_time_share_mean": "emergency_time_share_mean",
        "coalition_mean_duration_mean": "coalition_mean_duration",
        "legitimacy_internal_mean": "legitimacy_internal_mean",
        "capture_pressure_mean": "capture_pressure_mean",
    }
    out = {}
    for new_key, old_key in keys.items():
        if old_key in data:
            out[new_key] = data[old_key]
    return out


def render_audit(payload: dict) -> str:
    new = payload["summary"]
    old = payload.get("historical_summary") or {}

    rows = []
    for key, label in [
        ("cartel_capture_rate", "Cartel capture rate"),
        ("emergency_time_share_mean", "Emergency time share"),
        ("coalition_mean_duration_mean", "Mean coalition duration"),
        ("legitimacy_internal_mean", "Internal legitimacy"),
        ("capture_pressure_mean", "Mean capture pressure"),
    ]:
        nv = new.get(key)
        ov = old.get(key)
        if ov is None:
            rows.append(f"| {label} | n/a | {nv:.6f} | n/a |")
        else:
            rows.append(f"| {label} | {float(ov):.6f} | {nv:.6f} | {nv-float(ov):+.6f} |")

    table = "\n".join(rows)
    return f"""# Stress v0.32 Execution-Audit Rerun

**Claim label:** hypothesis  
**Not empirical validation:** yes  
**Runs:** {payload['n_runs']}  
**Ticks per run:** {payload['max_ticks']}  
**Master seed:** {payload['master_seed']}  
**Git HEAD:** `{payload['git_head']}`

## Provenance

- runner SHA256: `{payload['runner_sha256']}`
- model SHA256: `{payload['model_sha256']}`
- canonical baseline-config SHA256: `{payload['baseline_config_canonical_sha256']}`
- stress start tick: `{payload['stress_start_tick']}`
- stressed gates: `{payload['stress_gate_ids']}`

## Historical artifact vs current implementation

| Metric | Historical stored stress | v0.32 current rerun | Difference |
|---|---:|---:|---:|
{table}

## Interpretation boundary

This rerun measures behavior of the current code under the current uncalibrated
scenario assumptions. It does not estimate the probability of a real political
outcome.

The current implementation differs from the historical artifact in several
software-logical respects, including:
- stress timing is actually gated at tick 52;
- resource shares are conserved;
- emergency extension uses explicit individual simulated votes plus a threshold;
- coalition pair scores preserve both directions rather than execution-order overwrite;
- cartel duration and consecutive passed decisions are distinct criteria;
- failed coalition decisions reset the consecutive-decision streak;
- dissent recording no longer consumes an unused extra random draw.

Because the implementation changed, historical output must not be relabeled as
if it came from this version. The old artifact remains preserved separately.
"""


def main():
    t0 = time.time()
    master_rng = np.random.default_rng(MASTER_SEED)
    seeds = [int(x) for x in master_rng.integers(0, 2**31, size=N_RUNS)]

    results = []
    for seed in seeds:
        model = TwelveGatesModel(BASELINE_CFG, seed=seed)
        model.external = StressDriver([])
        results.append(model.run(MAX_TICKS))

    elapsed = time.time() - t0
    summary = summarize(results)

    payload = {
        "schema": "twelve-gates/stress-v032-execution-audit/v3",
        "claim_label": "hypothesis",
        "purpose": "execution_audit_rerun_after_timing_resource_emergency_coalition_fixes",
        "not_empirical_validation": True,
        "git_head": git_head(),
        "runner_sha256": file_sha256(Path(__file__).resolve()),
        "model_sha256": file_sha256(HERE / "twelve_gates_model.py"),
        "baseline_config_canonical_sha256": canonical_config_sha256(BASELINE_CFG),
        "stress_start_tick": StressDriver.START_TICK,
        "stress_gate_ids": [0, 2, 4],
        "stress_crisis_delta_per_tick": 0.02,
        "stress_exposure_delta_per_tick": 0.01,
        "n_runs": N_RUNS,
        "max_ticks": MAX_TICKS,
        "master_seed": MASTER_SEED,
        "run_seeds": seeds,
        "summary": summary,
        "historical_summary": historical_summary(),
        "elapsed_seconds": round(elapsed, 3),
        "run_results": results,
        "interpretation_boundary": (
            "Conditional on an uncalibrated hypothesis model; not a probability "
            "of real-world political outcomes."
        ),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    AUDIT_MD.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_MD.write_text(render_audit(payload), encoding="utf-8")

    print(json.dumps({
        "claim_label": payload["claim_label"],
        "git_head": payload["git_head"],
        "n_runs": N_RUNS,
        "max_ticks": MAX_TICKS,
        "elapsed_seconds": payload["elapsed_seconds"],
        "summary": summary,
        "output": str(OUT.relative_to(HERE.parent)),
        "audit_doc": str(AUDIT_MD.relative_to(HERE.parent)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
