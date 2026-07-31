"""
debug_coalitions.py
====================
ردیابی دقیق دلیل نرخ صفر تصاحب کارتل — نه فقط نتیجه‌ی نهایی، بلکه مسیر تیک‌به‌تیک.
"""
import numpy as np
from twelve_gates_model import TwelveGatesModel, ExternalScenarioDriver
from run_baseline import BASELINE_CFG

class StressDriver(ExternalScenarioDriver):
    def current_shock_for(self, gate_id):
        if gate_id in (0, 2, 4):
            return {"crisis_delta": 0.02, "exposure_delta": 0.01}
        return {}

model = TwelveGatesModel(BASELINE_CFG, seed=43)
model.external = StressDriver([])

cluster_pairs = [(0,2), (0,4), (2,4)]
log = []

for tick in range(200):
    model.step()
    scores = model.coalition_registry.pair_scores
    cluster_scores = {p: scores.get(frozenset(p), None) for p in cluster_pairs}
    all_scores = list(scores.values())
    trust_02 = model.gates_by_id[0].trust.get(2, None)
    trust_24 = model.gates_by_id[2].trust.get(4, None)
    n_above_theta = sum(1 for v in all_scores if v > 0.55)
    log.append({
        "tick": tick,
        "n_active_coalitions": len(model.coalition_registry.active_coalitions),
        "n_pairs_above_theta": n_above_theta,
        "max_score": max(all_scores) if all_scores else None,
        "cluster_scores": cluster_scores,
        "trust_0_2": trust_02, "trust_2_4": trust_24,
        "crisis_load_gate2": model.gates_by_id[2].crisis_load,
        "exec_power_sum_cluster": sum(model.gates_by_id[i].exec_power for i in (0,2,4)),
        "emergency_state": model.emergency_state.name,
    })

# چاپ هر ۲۰ تیک برای خوانایی
print(f"{'tick':>5} {'n_coal':>6} {'n>θ':>5} {'max_sc':>7} {'sc(0,2)':>8} {'trust02':>8} {'crisis2':>8} {'emerg':>10}")
for row in log[::20]:
    cs = row["cluster_scores"].get((0,2))
    print(f"{row['tick']:>5} {row['n_active_coalitions']:>6} {row['n_pairs_above_theta']:>5} "
          f"{row['max_score']:>7.3f} {cs if cs else 0:>8.3f} "
          f"{row['trust_0_2'] if row['trust_0_2'] is not None else 0:>8.3f} "
          f"{row['crisis_load_gate2']:>8.3f} {row['emergency_state']:>10}")

print(f"\nآستانه‌ی لازم (theta_pair): 0.55")
print(f"وزن‌ها: affinity=0.30 trust=0.25 complementarity=0.25 audit_exposure=-0.10 overlap=-0.10")
print(f"مقدار affinity برای خوشه‌ی مادی: 0.6 (ثابت، از config)")
print(f"حداکثر امتیاز ممکن فقط از affinity+complementarity (اگر trust=1، audit/overlap=0):")
print(f"  0.30*0.6 + 0.25*1.0 + 0.25*1.0 - 0 - 0 = {0.30*0.6+0.25*1.0+0.25*1.0:.3f}")
print(f"یعنی حتی با اعتماد کامل (۱.۰)، سقف نظری امتیاز = {0.30*0.6+0.25*1.0+0.25*1.0:.3f}")
