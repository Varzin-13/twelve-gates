"""
test_model.py — مجموعه تست خودکار
====================================
اجرا: python3 test_model.py
هدف: گرفتن خودکار باگ‌های این‌چنینی در آینده، نه با شانس یا بازرسی دستی.
"""
import numpy as np
import json, sys
from twelve_gates_model import (
    TwelveGatesModel, PreconditionError, N_GATES, ROTATION_STEP, OBSERVER_OFFSET,
    CoalitionRegistry, Coalition, Proposal, ExternalScenarioDriver
)
from run_baseline import BASELINE_CFG
from run_model import normalize_config, validate_config
from run_stress import StressDriver
from audit_schedule import (
    cycle_with_offset, offset_supercycle, coverage_stats, all_affine_permutations
)

PASS, FAIL = [], []

def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}")

# --- تست ۱: فرمول چرخش دقیقاً طبق بند ۴.۲ ---
def test_rotation_formula():
    for t in range(12):
        P = (ROTATION_STEP * t) % N_GATES
        A = (P + OBSERVER_OFFSET) % N_GATES
        check(f"چرخش t={t}: P≠A", P != A)
    all_P = sorted((ROTATION_STEP * t) % N_GATES for t in range(12))
    check("چرخش: هر گیت دقیقاً یک‌بار P_t می‌شود (دور کامل، بند ۴.۲)", all_P == list(range(12)))

# --- تست ۲: مدل زیر ظرفیت هماهنگی پایین باید امتناع کند (بند ۱۰.۶.۷) ---
def test_precondition_refusal():
    cfg = json.loads(json.dumps(BASELINE_CFG))  # deep copy
    cfg["preconditions"]["coordination_capacity"] = 0.1
    raised = False
    try:
        TwelveGatesModel(cfg, seed=1)
    except PreconditionError:
        raised = True
    check("مدل زیر min_coordination_capacity باید PreconditionError بدهد", raised)

def test_precondition_allows_normal():
    raised = False
    try:
        TwelveGatesModel(BASELINE_CFG, seed=1)
    except PreconditionError:
        raised = True
    check("مدل با coordination_capacity عادی (baseline) نباید امتناع کند", not raised)

# --- تست ۳: رگرسیون باگ کلیدهای JSON (کشف‌شده در همین نشست) ---
def test_json_key_regression():
    cfg = json.loads(json.dumps(BASELINE_CFG))  # شبیه‌سازی رفت‌وبرگشت JSON واقعی
    trust_keys_before_norm = list(cfg["gates"][0]["trust_row"].keys())
    is_str_before = all(isinstance(k, str) for k in trust_keys_before_norm)
    check("قبل از نرمال‌سازی: کلیدهای trust_row باید رشته باشند (تأیید وجود مشکل)", is_str_before)

    cfg = normalize_config(cfg)
    trust_keys_after = list(cfg["gates"][0]["trust_row"].keys())
    is_int_after = all(isinstance(k, int) for k in trust_keys_after)
    check("رگرسیون: بعد از normalize_config، کلیدها باید int باشند (باگ رفع‌شده بماند)", is_int_after)

    # تست عملکردی: آیا واقعاً روی نتیجه اثر می‌گذارد؟
    m1 = TwelveGatesModel(cfg, seed=7)  # کانفیگ نرمال‌شده
    m2 = TwelveGatesModel(BASELINE_CFG, seed=7)  # کانفیگ اصلی پایتون
    same_initial_trust = m1.gates_by_id[0].trust == m2.gates_by_id[0].trust
    check("کانفیگ نرمال‌شده باید همان trust اولیه‌ی کانفیگ پایتون اصلی را بدهد", same_initial_trust)

# --- تست ۴: فیوز اضطراری دقیقاً ۲ تیک (=۱۴ روز، بند ۳.۲) ---
def test_emergency_fuse_length():
    cfg = json.loads(json.dumps(BASELINE_CFG))
    check("emergency_fuse_ticks باید دقیقاً ۲ باشد (بند ۳.۲، تنها عدد سخت سند)",
          cfg["time"]["emergency_fuse_ticks"] == 2)

# --- تست ۵: resource_share اولیه دقیقاً ۱/۱۲ (بند ۱.۴) ---
def test_baseline_resource_share():
    shares = [g["resource_share"] for g in BASELINE_CFG["gates"]]
    check("همه‌ی گیت‌ها باید resource_share=1/12 در baseline داشته باشند (بند ۱.۴)",
          all(abs(s - 1/12) < 1e-9 for s in shares))

# --- تست ۶: validate_config باید config های خراب را رد کند ---
def test_config_validation_catches_errors():
    bad_cfg = {"gates": [{"gate_id": i, "resource_share": 2.0, "exec_power": 0.5,
                            "info_reliability": 0.5} for i in range(12)]}
    errors = validate_config(bad_cfg)
    check("validate_config باید resource_share=2.0 (خارج از [0,1]) را رد کند", len(errors) > 0)

def test_config_validation_accepts_valid():
    errors = validate_config(json.loads(json.dumps(BASELINE_CFG)))
    check("validate_config نباید روی baseline_v1 معتبر خطا بدهد", len(errors) == 0)

def test_emergency_extension_validation():
    missing = json.loads(json.dumps(BASELINE_CFG))
    missing.pop("emergency_extension")
    check("validate_config: نبود emergency_extension باید صریحاً رد شود",
          any("emergency_extension" in e for e in validate_config(missing)))

    bad_p = json.loads(json.dumps(BASELINE_CFG))
    bad_p["emergency_extension"]["support_probability"] = 1.2
    check("validate_config: support_probability خارج از [0,1] باید رد شود",
          len(validate_config(bad_p)) > 0)

    bad_f = json.loads(json.dumps(BASELINE_CFG))
    bad_f["emergency_extension"]["required_fraction"] = 0
    check("validate_config: required_fraction باید در (0,1] باشد",
          len(validate_config(bad_f)) > 0)

def test_stress_timing_gate():
    driver = StressDriver([])
    driver.apply(51)
    check("stress: قبل از tick=52 نباید شوک اعمال شود",
          driver.current_shock_for(0) == {})
    driver.apply(52)
    shock = driver.current_shock_for(0)
    check("stress: در tick=52 باید شوک خوشه‌ی مادی فعال شود",
          shock.get("crisis_delta") == 0.02)
    check("stress: گیت خارج از خوشه حتی بعد از tick=52 شوک نگیرد",
          driver.current_shock_for(1) == {})

def test_budget_share_conservation():
    model = TwelveGatesModel(BASELINE_CFG, seed=3)
    model.gates[0].resource_share += 0.10
    model._renormalize_resource_shares()
    total = sum(g.resource_share for g in model.gates)
    check("resource_share: نرمال‌سازی باید مجموع سهم‌ها را دقیقاً به ۱ برگرداند",
          abs(total - 1.0) < 1e-12)

def test_audit_schedule_combinatorics():
    fixed = coverage_stats(cycle_with_offset(6))
    complete = coverage_stats(offset_supercycle())
    check("ممیزی +6: فقط ۱۲ جفت مرتب یکتا در یک چرخه دارد",
          fixed["unique_ordered_pairs"] == 12)
    check("ابرچرخه offsets=1..11: هر ۱۳۲ جفت غیرخودی را دقیقاً پوشش می‌دهد",
          complete["unique_ordered_pairs"] == 12 * 11)
    check("ابرچرخه offsets=1..11: خودممیزی ندارد",
          complete["self_audits"] == 0)
    check("Aff(Z12): دقیقاً ۴۸ جایگشت affine دارد",
          len(all_affine_permutations()) == 48)

def test_coalition_pair_order_invariance():
    cfg = json.loads(json.dumps(BASELINE_CFG["coalitions"]))
    r1 = CoalitionRegistry(cfg)
    r1.propose_pair(0, 1, 0.20)
    r1.propose_pair(1, 0, 0.80)
    score1 = r1.bilateral_pair_score(frozenset((0, 1)))

    r2 = CoalitionRegistry(cfg)
    r2.propose_pair(1, 0, 0.80)
    r2.propose_pair(0, 1, 0.20)
    score2 = r2.bilateral_pair_score(frozenset((0, 1)))

    check("coalition score: ترتیب اجرای دو جهت نباید نتیجه را تغییر دهد",
          abs(score1 - 0.50) < 1e-12 and abs(score2 - 0.50) < 1e-12)
    r3 = CoalitionRegistry(cfg)
    r3.propose_pair(0, 1, 0.90)
    check("coalition score: یک ارزیابی یک‌طرفه برای تشکیل جفت کافی نیست",
          r3.bilateral_pair_score(frozenset((0, 1))) is None)

def test_cartel_requires_decisions_not_age_only():
    model = TwelveGatesModel(BASELINE_CFG, seed=11)
    reg = model.coalition_registry
    members = frozenset((0, 2, 4))
    coal = Coalition(0, members, formed_tick=0)
    reg.active_coalitions[members] = coal
    for member in members:
        model.gates_by_id[member].coalition_id = 0

    for tick in range(20):
        reg.dissolve_check(tick, model.gates_by_id)

    check("cartel: گذشت زمان به‌تنهایی نباید passed_decisions_streak بسازد",
          coal.active_duration_ticks == 20 and coal.passed_decisions_streak == 0)
    check("cartel: ائتلاف قدرتمندِ قدیمی بدون تصمیم‌های تصویب‌شده نباید active شود",
          not reg.cartel_active(model.gates_by_id))

    for i in range(BASELINE_CFG["coalitions"]["cartel"]["M_consecutive_decisions"]):
        p = Proposal(tick=i, proposer_id=0, coalition_id=0,
                     domain_targets=[0], resource_delta={0: 0.0})
        reg.record_proposal_outcome(p, passed=True, tick=i)

    check("cartel: پس از مدت کافی و تعداد تصمیم‌های لازم، شرط تصمیم می‌تواند برقرار شود",
          reg.cartel_active(model.gates_by_id))

def test_failed_coalition_decision_resets_streak():
    model = TwelveGatesModel(BASELINE_CFG, seed=12)
    reg = model.coalition_registry
    members = frozenset((0, 2, 4))
    coal = Coalition(0, members, formed_tick=0, active_duration_ticks=20,
                     passed_decisions_streak=4)
    reg.active_coalitions[members] = coal
    p = Proposal(tick=20, proposer_id=0, coalition_id=0,
                 domain_targets=[0], resource_delta={0: 0.0})
    reg.record_proposal_outcome(p, passed=False, tick=20)
    check("coalition streak: شکست یک تصمیم باید streak متوالی را صفر کند",
          coal.passed_decisions_streak == 0 and coal.last_decision_tick == 20)

def test_dissent_uses_single_decision_draw():
    class FixedRng:
        def __init__(self, values):
            self.values = iter(values)
            self.calls = 0
        def random(self):
            self.calls += 1
            return next(self.values)

    model = TwelveGatesModel(BASELINE_CFG, seed=13)
    gate = model.gates_by_id[0]
    prop = Proposal(tick=0, proposer_id=1, coalition_id=None,
                    domain_targets=[1], resource_delta={1: 0.0})
    model.active_proposals = [prop]
    fake = FixedRng([0.99, 0.0])  # vote no; then record dissent
    gate.rng = fake
    before = len(model.trust_ledger.dissents)
    gate.voting_stage()
    after = len(model.trust_ledger.dissents)
    check("dissent: رأی منفی باید فقط یک draw جدا برای ثبت dissent مصرف کند",
          fake.calls == 2 and after == before + 1)

def test_external_timeline_preserves_multiple_events():
    driver = ExternalScenarioDriver([
        {"tick": 5, "gate_ids": [2], "crisis_delta": 0.10, "exposure_delta": 0.02},
        {"tick": 5, "gate_ids": [2], "crisis_delta": 0.05, "exposure_delta": 0.03},
        {"tick": 5, "gate_ids": [-1], "disaster": True},
        {"tick": 6, "gate_ids": [2], "crisis_delta": 0.90},
    ])
    driver.apply(5)
    shock = driver.current_shock_for(2)
    check("timeline: چند رویداد هم‌زمان باید جمع شوند، نه overwrite",
          abs(shock["crisis_delta"] - 0.15) < 1e-12
          and abs(shock["exposure_delta"] - 0.05) < 1e-12)
    check("timeline: رویداد tick آینده نباید زودتر اعمال شود",
          shock["crisis_delta"] < 0.90)
    system_shock = driver.current_shock_for(-1)
    check("timeline: target=-1 باید رویداد سیستمی/بوروکراسی را دریافت کند",
          system_shock.get("disaster") is True)
    driver.apply(4)
    check("timeline: tick بدون رویداد باید inert باشد",
          driver.current_shock_for(2) == {})

def test_external_timeline_validation():
    cfg = json.loads(json.dumps(BASELINE_CFG))
    cfg["external_timeline"] = [
        {"tick": -1, "gate_ids": [12], "crisis_delta": "bad"}
    ]
    errs = validate_config(cfg)
    check("timeline validation: tick منفی/gate نامعتبر/delta غیرعددی باید رد شود",
          len([e for e in errs if "external_timeline" in e]) >= 3)

if __name__ == "__main__":
    test_rotation_formula()
    test_precondition_refusal()
    test_precondition_allows_normal()
    test_json_key_regression()
    test_emergency_fuse_length()
    test_baseline_resource_share()
    test_config_validation_catches_errors()
    test_config_validation_accepts_valid()
    test_emergency_extension_validation()
    test_stress_timing_gate()
    test_budget_share_conservation()
    test_audit_schedule_combinatorics()
    test_coalition_pair_order_invariance()
    test_cartel_requires_decisions_not_age_only()
    test_failed_coalition_decision_resets_streak()
    test_dissent_uses_single_decision_draw()
    test_external_timeline_preserves_multiple_events()
    test_external_timeline_validation()

    print(f"\n{'='*50}\n{len(PASS)} موفق، {len(FAIL)} ناموفق از {len(PASS)+len(FAIL)} تست")
    if FAIL:
        print("تست‌های ناموفق:")
        for f in FAIL:
            print(f"  - {f}")
        sys.exit(1)
    sys.exit(0)
