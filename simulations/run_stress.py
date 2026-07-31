"""
run_stress.py
==============
سناریوی «تحت فشار» — نه یه ادعای جدید، صرفاً آزمون صحت عملکرد کد:
آیا با تزریق یک بحران واقعی، منطق کارتل/اضطرار/اعتماد فعال می‌شود؟
شوک: از tick=52 (سال دوم) بحران پیوسته روی گیت امنیت (id=2) تزریق می‌شود.
claim_label همچنان: hypothesis — این فقط تست عملکردی کد است.
"""
import numpy as np
import json, time
from twelve_gates_model import TwelveGatesModel, PreconditionError, ExternalScenarioDriver
from run_baseline import BASELINE_CFG

class StressDriver(ExternalScenarioDriver):
    """تزریق بحران پیوسته روی گیت‌های خوشه‌ی مادی (امنیت=2، انرژی=4، اقتصاد=0) از tick=52."""
    def current_shock_for(self, gate_id):
        if gate_id in (0, 2, 4):
            return {"crisis_delta": 0.02, "exposure_delta": 0.01}
        return {}

def run_one(seed, max_ticks=520):
    model = TwelveGatesModel(BASELINE_CFG, seed=seed)
    model.external = StressDriver([])
    return model.run(max_ticks)

if __name__ == "__main__":
    N_RUNS = 300
    t0 = time.time()
    master_rng = np.random.default_rng(43)
    seeds = master_rng.integers(0, 2**31, size=N_RUNS)
    results = [run_one(int(s)) for s in seeds]
    elapsed = time.time() - t0

    cartel_rate = np.mean([r["cartel_capture_ever"] for r in results])
    emerg_share = np.mean([r["emergency_time_share"] for r in results])
    mean_leg = np.mean([r["mean_legitimacy_end"] for r in results])
    mean_capture_pressure = np.mean([r["mean_capture_pressure_end"] for r in results])
    mean_coal_dur = np.mean([r["coalition_mean_duration"] for r in results])

    print(f"=== stress_v1 (claim_label=hypothesis, آزمون عملکردی کد) — {len(results)} اجرا در {elapsed:.1f}s ===\n")
    print(f"cartel_capture_rate         : {cartel_rate*100:.1f}%")
    print(f"emergency_time_share        : {emerg_share*100:.1f}%")
    print(f"legitimacy_internal (پایانی): {mean_leg:.3f}")
    print(f"capture_pressure (پایانی)   : {mean_capture_pressure:.3f}")
    print(f"coalition_mean_duration     : {mean_coal_dur:.1f} tick")

    out = {"claim_label": "hypothesis", "purpose": "functional_sanity_check",
           "n_runs": N_RUNS, "cartel_capture_rate": float(cartel_rate),
           "emergency_time_share_mean": float(emerg_share),
           "legitimacy_internal_mean": float(mean_leg),
           "capture_pressure_mean": float(mean_capture_pressure),
           "coalition_mean_duration": float(mean_coal_dur)}
    with open("/home/claude/mesa_stress_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nذخیره شد: mesa_stress_results.json")
