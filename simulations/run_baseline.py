"""
run_baseline.py
================
اجرای دسته‌ای baseline_v1 — دقیقاً کانفیگ hypothesis-برچسب‌خورده‌ای که AI طراح داد.
seed=42 طبق spec؛ n_runs کاهش‌یافته از ۳۰۰۰ به ۳۰۰ برای زمان اجرای معقول در این محیط
(⚠️ این کاهش، نه تغییر روش‌شناسی — فقط محدودیت محاسباتی این نشست؛ صریح گزارش می‌شود).
"""
import numpy as np
import json
import time
from twelve_gates_model import TwelveGatesModel, PreconditionError

def make_gate_cfg(gate_id, domain, exec_power, is_material_cluster=False):
    others = [i for i in range(12) if i != gate_id]
    cluster = {2, 4, 0}  # امنیت=2، انرژی=4، اقتصاد=0 (طبق material_cluster spec)
    return {
        "gate_id": gate_id, "domain": domain,
        "resource_share": 1/12,
        "exec_power": exec_power,
        "trust_row": {j: 0.5 for j in others},
        "affinity_row": {j: (0.6 if (gate_id in cluster and j in cluster) else 0.3) for j in others},
        "info_reliability": 0.95,
        "audit_exposure": 0.4,
        "initial_crisis_load": 0.0,
        "legitimacy_internal": 0.7,
        "external_exposure": 0.3,
        "overlap_row": {j: 0.15 for j in others},
        "memory_dependence": 0.5,
        "critical_report_threshold": 0.6,
        "verification_accuracy": 0.8,
    }

DOMAINS = ["economy","science","security","culture","energy","education",
           "justice","health","environment","infrastructure","foreign_affairs","welfare"]
# exec_power سناریویی: خوشه‌ی امنیت-انرژی-اقتصاد کمی بالاتر (فرض آزمون‌شونده، نه واقعیت)
EXEC_POWER = {0:0.75, 2:0.85, 4:0.70}  # اقتصاد، امنیت، انرژی
GATES_CFG = [make_gate_cfg(i, DOMAINS[i], EXEC_POWER.get(i, 0.55)) for i in range(12)]

BASELINE_CFG = {
    "meta": {"scenario_name": "baseline_v1", "claim_label": "hypothesis", "seed": 42},
    "preconditions": {"coordination_capacity": 0.6, "min_coordination_capacity": 0.3},
    "time": {"tick_days": 7, "rotation_period_ticks": 26, "budget_review_period_ticks": 52,
              "emergency_fuse_ticks": 2},
    "gates": GATES_CFG,
    "coalitions": {
        "weights": {"w1_affinity": 0.30, "w2_trust": 0.25, "w3_complementarity": 0.25,
                     "w4_audit_exposure": 0.10, "w5_overlap_penalty": 0.10},
        "theta_pair": 0.55, "theta_audit": 0.60,
        "trust_dissolve_floor": 0.25, "crisis_divergence_max": 0.5,
        "cartel": {"K_min_duration_ticks": 12, "theta_power_sum": 1.8,
                    "M_consecutive_decisions": 5, "material_cluster": [2, 4, 0]},
    },
    "budget": {"annual_delta_cap": 0.15, "reallocation_rule": "qualified_majority"},
    "mirror13": {"enabled": True, "coordination_gain": 0.3},
    "gate_zero": {"admission_threshold": 0.6, "measurement_noise_sd": 0.1,
                   "entropy_manipulability": 0.3, "appeal_board": "random_placeholder"},
    "emergency_court": {"independence_mode": "erodible", "erosion_rate": 0.05},
    "bureaucracy": {"memory_stock": 0.7, "politicization_risk": 0.2, "service_continuity": 0.8,
                      "archive_integrity": 0.9, "geo_redundancy": 0.66, "redundancy_floor": 0.5},
    "armed_blocs": [],
    "civil_society": {"mobilization_capacity": 0.5, "oversight_strength": 0.4,
                        "media_visibility": 0.6, "union_density_proxy": 0.3,
                        "public_legitimacy_signal": 0.6},
    "external_timeline": [],
    "trust_dynamics": {"trust_learning_rate": 0.1, "audit_detection_prob": 0.35,
                         "dissent_chilling_beta": 0.5},
}

if __name__ == "__main__":
    N_RUNS = 300          # کاهش‌یافته از 3000 (spec اصلی) — دلیل بالا
    MAX_TICKS = 520       # ۱۰ سال، طبق spec
    MASTER_SEED = 42

    t0 = time.time()
    results = []
    errors = 0
    master_rng = np.random.default_rng(MASTER_SEED)
    run_seeds = master_rng.integers(0, 2**31, size=N_RUNS)

    for i, s in enumerate(run_seeds):
        try:
            model = TwelveGatesModel(BASELINE_CFG, seed=int(s))
            res = model.run(MAX_TICKS)
            results.append(res)
        except PreconditionError as e:
            errors += 1

    elapsed = time.time() - t0
    print(f"=== baseline_v1 (claim_label=hypothesis) — {len(results)}/{N_RUNS} اجرای موفق در {elapsed:.1f}s ===\n")

    if results:
        cartel_rate = np.mean([r["cartel_capture_ever"] for r in results])
        emerg_share = np.mean([r["emergency_time_share"] for r in results])
        mean_leg = np.mean([r["mean_legitimacy_end"] for r in results])
        mean_capture_pressure = np.mean([r["mean_capture_pressure_end"] for r in results])
        mean_coal_dur = np.mean([r["coalition_mean_duration"] for r in results])
        mean_politicization = np.mean([r["bureaucracy_politicization_end"] for r in results])
        mean_pub_leg = np.mean([r["public_legitimacy_signal_end"] for r in results])

        print(f"cartel_capture_rate         : {cartel_rate*100:.1f}%")
        print(f"emergency_time_share (میانگین): {emerg_share*100:.1f}%")
        print(f"legitimacy_internal (پایانی) : {mean_leg:.3f}")
        print(f"capture_pressure (پایانی)    : {mean_capture_pressure:.3f}")
        print(f"coalition_mean_duration      : {mean_coal_dur:.1f} tick")
        print(f"bureaucracy_politicization    : {mean_politicization:.3f}")
        print(f"public_legitimacy_signal      : {mean_pub_leg:.3f}")

        out = {
            "claim_label": "hypothesis",
            "n_runs_requested": N_RUNS, "n_runs_completed": len(results),
            "max_ticks": MAX_TICKS, "master_seed": MASTER_SEED,
            "cartel_capture_rate": float(cartel_rate),
            "emergency_time_share_mean": float(emerg_share),
            "legitimacy_internal_mean": float(mean_leg),
            "capture_pressure_mean": float(mean_capture_pressure),
            "coalition_mean_duration": float(mean_coal_dur),
            "bureaucracy_politicization_mean": float(mean_politicization),
            "public_legitimacy_signal_mean": float(mean_pub_leg),
            "elapsed_seconds": elapsed,
        }
        with open("/home/claude/mesa_baseline_results.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print("\nذخیره شد: mesa_baseline_results.json")
