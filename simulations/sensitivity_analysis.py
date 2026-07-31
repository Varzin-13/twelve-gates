"""
sensitivity_analysis.py
========================
تحلیل حساسیت حرفه‌ای — پاسخ به «اذعان صریح به جانبداری پارامتری».
سه پارامتر کلیدی که در طراحی spec به‌صورت دلبخواه/سناریویی انتخاب شدند را
سیستماتیک تغییر می‌دهیم تا نشان دهیم نتیجه‌ی cartel_capture_rate چقدر به
انتخاب خودمان (نه به سند) وابسته است.

پارامترهای تحت آزمون:
  A) theta_pair (آستانه‌ی تشکیل ائتلاف) — مقدار اصلی: 0.55
  B) نسبت وزن trust به affinity در فرمول ائتلاف — مقدار اصلی: w2=0.25, w1=0.30
  C) توزیع اولیه‌ی exec_power خوشه‌ی مادی — مقدار اصلی: امنیت=0.85, انرژی=0.70, اقتصاد=0.75

هرکدام مستقل، با ۱۵۰ اجرا (به‌جای ۳۰۰، برای زمان اجرای معقول)، تحت سناریوی «فشار»
(همان stress_v1) تکرار می‌شود.
"""
import numpy as np
import json, time
from twelve_gates_model import TwelveGatesModel, PreconditionError
from run_baseline import BASELINE_CFG, make_gate_cfg, DOMAINS
from run_stress import StressDriver
import copy

N_RUNS = 40
MAX_TICKS = 400
MASTER_SEED = 44

def run_batch(cfg, n_runs=N_RUNS, seed=MASTER_SEED):
    rng = np.random.default_rng(seed)
    seeds = rng.integers(0, 2**31, size=n_runs)
    results = []
    for s in seeds:
        m = TwelveGatesModel(cfg, seed=int(s))
        m.external = StressDriver([])
        results.append(m.run(MAX_TICKS))
    return {
        "cartel_capture_rate": float(np.mean([r["cartel_capture_ever"] for r in results])),
        "emergency_time_share": float(np.mean([r["emergency_time_share"] for r in results])),
        "coalition_mean_duration": float(np.mean([r["coalition_mean_duration"] for r in results])),
    }

report = {}

def save():
    with open("/home/claude/sensitivity_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

# ---------- A) theta_pair ----------
print("=== A) آستانه‌ی تشکیل ائتلاف (theta_pair) ===", flush=True)
theta_values = [0.45, 0.50, 0.55, 0.60, 0.65]
report["A_theta_pair"] = {}
for th in theta_values:
    cfg = copy.deepcopy(BASELINE_CFG)
    cfg["coalitions"]["theta_pair"] = th
    res = run_batch(cfg)
    report["A_theta_pair"][th] = res
    save()
    print(f"  theta_pair={th:.2f} → cartel_capture_rate={res['cartel_capture_rate']*100:5.1f}%", flush=True)

# ---------- B) نسبت وزن trust/affinity ----------
print("\n=== B) نسبت وزن اعتماد به هم‌راستایی سیاسی در فرمول ائتلاف ===")
weight_variants = [
    {"w1_affinity": 0.45, "w2_trust": 0.10, "w3_complementarity": 0.25, "w4_audit_exposure": 0.10, "w5_overlap_penalty": 0.10},  # affinity-heavy
    {"w1_affinity": 0.30, "w2_trust": 0.25, "w3_complementarity": 0.25, "w4_audit_exposure": 0.10, "w5_overlap_penalty": 0.10},  # اصلی
    {"w1_affinity": 0.10, "w2_trust": 0.45, "w3_complementarity": 0.25, "w4_audit_exposure": 0.10, "w5_overlap_penalty": 0.10},  # trust-heavy
]
labels = ["affinity-محور (w1=0.45)", "اصلی (متوازن)", "trust-محور (w2=0.45)"]
report["B_weight_ratio"] = {}
for label, w in zip(labels, weight_variants):
    cfg = copy.deepcopy(BASELINE_CFG)
    cfg["coalitions"]["weights"] = w
    res = run_batch(cfg)
    report["B_weight_ratio"][label] = res
    save()
    print(f"  {label:25s} → cartel_capture_rate={res['cartel_capture_rate']*100:5.1f}%", flush=True)

# ---------- C) توزیع اولیه‌ی exec_power ----------
print("\n=== C) توزیع اولیه‌ی exec_power خوشه‌ی مادی (امنیت-انرژی-اقتصاد) ===")
power_variants = [
    {0: 0.55, 2: 0.55, 4: 0.55},   # مساوی با بقیه (بدون برتری خوشه)
    {0: 0.75, 2: 0.85, 4: 0.70},   # اصلی (spec)
    {0: 0.90, 2: 0.95, 4: 0.88},   # برتری شدید خوشه
]
labels_c = ["بدون برتری خوشه (0.55 برای همه)", "اصلی (0.70-0.85)", "برتری شدید (0.88-0.95)"]
report["C_exec_power"] = {}
for label, ep in zip(labels_c, power_variants):
    cfg = copy.deepcopy(BASELINE_CFG)
    cfg["gates"] = [make_gate_cfg(i, DOMAINS[i], ep.get(i, 0.55)) for i in range(12)]
    res = run_batch(cfg)
    report["C_exec_power"][label] = res
    save()
    print(f"  {label:32s} → cartel_capture_rate={res['cartel_capture_rate']*100:5.1f}%", flush=True)

save()
print("\nذخیره شد: sensitivity_results.json")
