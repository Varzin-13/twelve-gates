"""
test_model.py — مجموعه تست خودکار
====================================
اجرا: python3 test_model.py
هدف: گرفتن خودکار باگ‌های این‌چنینی در آینده، نه با شانس یا بازرسی دستی.
"""
import numpy as np
import json, sys
from twelve_gates_model import TwelveGatesModel, PreconditionError, N_GATES, ROTATION_STEP, OBSERVER_OFFSET
from run_baseline import BASELINE_CFG
from run_model import normalize_config, validate_config

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

if __name__ == "__main__":
    test_rotation_formula()
    test_precondition_refusal()
    test_precondition_allows_normal()
    test_json_key_regression()
    test_emergency_fuse_length()
    test_baseline_resource_share()
    test_config_validation_catches_errors()
    test_config_validation_accepts_valid()

    print(f"\n{'='*50}\n{len(PASS)} موفق، {len(FAIL)} ناموفق از {len(PASS)+len(FAIL)} تست")
    if FAIL:
        print("تست‌های ناموفق:")
        for f in FAIL:
            print(f"  - {f}")
        sys.exit(1)
    sys.exit(0)
