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
    cycle_with_offset, offset_supercycle, coverage_stats, all_affine_permutations,
    collision_free_affine_catalog, minimum_reciprocal_exact_cover
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

def test_budget_two_thirds_majority():
    # 7/12 = 58.3% must FAIL under a documented 2/3 rule.
    model7 = TwelveGatesModel(BASELINE_CFG, seed=51)
    p7 = Proposal(
        tick=0, proposer_id=0, coalition_id=None,
        domain_targets=[0], resource_delta={0: 0.0}
    )
    p7.votes = {i: (i < 7) for i in range(N_GATES)}
    model7.active_proposals = [p7]
    model7.gates_by_id[0].implementation_stage()
    check("budget majority: 7 از 12 باید زیر آستانه 2/3 رد شود",
          p7.status.name == "VOTED_FAIL")

    # 8/12 = exactly 2/3 must PASS.
    model8 = TwelveGatesModel(BASELINE_CFG, seed=52)
    p8 = Proposal(
        tick=0, proposer_id=0, coalition_id=None,
        domain_targets=[0], resource_delta={0: 0.0}
    )
    p8.votes = {i: (i < 8) for i in range(N_GATES)}
    model8.active_proposals = [p8]
    model8.gates_by_id[0].implementation_stage()
    check("budget majority: 8 از 12 باید دقیقاً آستانه 2/3 را پاس کند",
          p8.status.name == "IMPLEMENTED")

    bad = json.loads(json.dumps(BASELINE_CFG))
    bad["budget"].pop("reallocation_required_fraction")
    check("budget majority: نبود fraction صریح باید در validation رد شود",
          any("reallocation_required_fraction" in e for e in validate_config(bad)))

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
    check("ممیزی +6: در یک چرخه دقیقاً ۶ dyad متقابل می‌سازد",
          fixed["reciprocal_dyads"] == 6)
    catalog = collision_free_affine_catalog()
    check("Aff(Z12): از ۳۶ schedule بدون self-audit، ۲۴ تا reciprocal-free هستند",
          len(catalog) == 36
          and sum(1 for x in catalog if x["reciprocal_dyads"] == 0) == 24)
    cover = minimum_reciprocal_exact_cover()
    check("Aff(Z12): exact cover یازده‌چرخه‌ای حداقل ۶ reciprocal dyad دارد",
          cover["minimum_total_reciprocal_dyads"] == 6
          and len(cover["solution"]) == 11)

def test_coalition_pair_aggregation_structural_modes():
    base_cfg = json.loads(json.dumps(BASELINE_CFG["coalitions"]))
    expected = {
        "minimum": 0.20,
        "mean": 0.50,
        "maximum": 0.80,
    }
    for mode, target in expected.items():
        cfg = json.loads(json.dumps(base_cfg))
        cfg["pair_aggregation"] = mode
        reg = CoalitionRegistry(cfg)
        reg.propose_pair(0, 1, 0.20)
        reg.propose_pair(1, 0, 0.80)
        score = reg.bilateral_pair_score(frozenset((0, 1)))
        check(f"pair aggregation {mode}: structural rule باید مقدار مشخص خود را بدهد",
              abs(score - target) < 1e-12)

    invalid = json.loads(json.dumps(BASELINE_CFG))
    invalid["coalitions"]["pair_aggregation"] = "invented"
    check("pair aggregation: mode نامعتبر باید در config validation رد شود",
          any("pair_aggregation" in e for e in validate_config(invalid)))

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

def test_proposal_ids_are_deterministic_and_auditable():
    m1 = TwelveGatesModel(BASELINE_CFG, seed=71)
    m2 = TwelveGatesModel(BASELINE_CFG, seed=71)

    ids1 = [m1.next_proposal_id(), m1.next_proposal_id(), m1.next_proposal_id()]
    ids2 = [m2.next_proposal_id(), m2.next_proposal_id(), m2.next_proposal_id()]
    check("proposal id: sequence باید deterministic و rerun-stable باشد",
          ids1 == ids2 == ["p00000000", "p00000001", "p00000002"])

    p = Proposal(
        tick=0, proposer_id=1, coalition_id=None,
        domain_targets=[1], resource_delta={1: 0.0}
    )
    ref = m1.ensure_proposal_id(p)
    m1.trust_ledger.record_dissent(0, 0, ref)
    event = m1.trust_ledger.dissents[-1]
    check("dissent ledger: proposal_ref باید شناسه پایدار را حفظ کند",
          event["proposal_ref"] == p.proposal_id
          and event["proposal_ref"].startswith("p"))

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

def test_claim_boundary_outputs():
    model = TwelveGatesModel(BASELINE_CFG, seed=21)
    out = model.run(1)
    check("claim boundary: civil-society legitimacy باید صریحاً proxy برچسب بخورد",
          out.get("public_legitimacy_signal_is_internal_proxy") is True
          and "civil_society_legitimacy_proxy_end" in out)

    raised = False
    try:
        model.trust_ledger.integrity()
    except NotImplementedError:
        raised = True
    check("claim boundary: ledger integrity نباید عدد ثابتِ ساختگی برگرداند", raised)

def test_model_assumptions_validation():
    missing = json.loads(json.dumps(BASELINE_CFG))
    missing.pop("model_assumptions")
    check("model assumptions: نبود bundle باید صریحاً رد شود",
          any("model_assumptions" in e for e in validate_config(missing)))

    bad = json.loads(json.dumps(BASELINE_CFG))
    bad["model_assumptions"]["capture_pressure_overlap_weight"] = 0.9
    check("model assumptions: weightهای compositional با مجموع نادرست باید رد شوند",
          any("capture pressure" in e for e in validate_config(bad)))

    bad_vote = json.loads(json.dumps(BASELINE_CFG))
    bad_vote["model_assumptions"]["vote_support_intercept"] = 0.8
    bad_vote["model_assumptions"]["vote_support_trust_weight"] = 0.5
    check("model assumptions: احتمال رأی نباید از ۱ عبور کند",
          any("vote_support" in e for e in validate_config(bad_vote)))

def test_coalition_survival_summary_right_censoring():
    model = TwelveGatesModel(BASELINE_CFG, seed=31)
    reg = model.coalition_registry

    dissolved = Coalition(10, frozenset((0, 1)), formed_tick=0, dissolved_tick=10)
    reg._history.append(dissolved)

    active = Coalition(
        11, frozenset((2, 3)), formed_tick=5, active_duration_ticks=15
    )
    reg.active_coalitions[active.members] = active

    summary = reg.survival_summary(horizon=20)
    check("coalition survival: تعداد dissolved و right-censored باید جدا باشد",
          summary["n_total"] == 2
          and summary["n_dissolved"] == 1
          and summary["n_right_censored"] == 1)
    check("coalition survival: dissolved mean و active age نباید با هم مخلوط شوند",
          summary["dissolved_duration_mean"] == 10.0
          and summary["active_age_mean"] == 15.0)
    check("coalition survival: observed age/duration mean باید هر دو observation را ببیند",
          summary["observed_age_or_duration_mean"] == 12.5)
    check("coalition survival: RMST باید censoring را نگه دارد، نه active را حذف کند",
          abs(summary["rmst_ticks"] - 15.0) < 1e-12)

def test_budget_vote_counters_and_required_yes_output():
    model = TwelveGatesModel(BASELINE_CFG, seed=61)
    p = Proposal(
        tick=0, proposer_id=0, coalition_id=None,
        domain_targets=[0], resource_delta={0: 0.0}
    )
    p.votes = {i: (i < 8) for i in range(N_GATES)}
    model.active_proposals = [p]
    model.gates_by_id[0].implementation_stage()
    check("proposal counters: pass باید دقیقاً یک بار شمرده شود",
          model.proposals_voted_pass == 1 and model.proposals_voted_fail == 0)

    out = TwelveGatesModel(BASELINE_CFG, seed=62).run(1)
    check("run output: آستانه بودجه باید 8 رأی گزارش شود",
          out["budget_required_yes_votes"] == 8)
    check("run output: proposal pass/fail counters باید schema صریح داشته باشند",
          "proposals_voted_pass" in out and "proposals_voted_fail" in out
          and "proposal_pass_fraction" in out)

def test_run_exposes_censoring_boundary():
    model = TwelveGatesModel(BASELINE_CFG, seed=32)
    out = model.run(3)
    required = {
        "coalition_duration_legacy_dissolved_mean",
        "coalition_duration_dissolved_mean",
        "coalition_active_age_mean",
        "coalition_observed_age_or_duration_mean",
        "coalition_rmst_ticks",
        "coalitions_right_censored_n",
    }
    check("run output: censoring-aware coalition fields باید صریح باشند",
          required.issubset(out))

def test_cartel_snapshot_explains_boolean_endpoint():
    model = TwelveGatesModel(BASELINE_CFG, seed=41)
    reg = model.coalition_registry
    members = frozenset((0, 2, 4))
    coal = Coalition(
        0, members, formed_tick=0,
        active_duration_ticks=12,
        passed_decisions_streak=5,
    )
    reg.active_coalitions[members] = coal
    snaps = reg.cartel_snapshots(model.gates_by_id)
    check("cartel diagnostic: snapshot باید boolean endpoint را توضیح دهد",
          bool(snaps) == reg.cartel_active(model.gates_by_id))
    check("cartel diagnostic: اعضا و power sum باید صریح ثبت شوند",
          snaps and snaps[0]["members"] == [0, 2, 4]
          and abs(snaps[0]["power_sum"] - 2.30) < 1e-12)

def test_run_cartel_snapshot_fields_present():
    model = TwelveGatesModel(BASELINE_CFG, seed=42)
    out = model.run(2)
    check("run output: first-cartel diagnostic fields باید همیشه schema داشته باشند",
          "cartel_first_detected_tick" in out
          and "cartel_first_snapshot" in out)

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
    test_budget_two_thirds_majority()
    test_budget_share_conservation()
    test_budget_vote_counters_and_required_yes_output()
    test_audit_schedule_combinatorics()
    test_coalition_pair_aggregation_structural_modes()
    test_coalition_pair_order_invariance()
    test_cartel_requires_decisions_not_age_only()
    test_failed_coalition_decision_resets_streak()
    test_proposal_ids_are_deterministic_and_auditable()
    test_dissent_uses_single_decision_draw()
    test_external_timeline_preserves_multiple_events()
    test_external_timeline_validation()
    test_claim_boundary_outputs()
    test_model_assumptions_validation()
    test_coalition_survival_summary_right_censoring()
    test_run_exposes_censoring_boundary()
    test_cartel_snapshot_explains_boolean_endpoint()
    test_run_cartel_snapshot_fields_present()

    print(f"\n{'='*50}\n{len(PASS)} موفق، {len(FAIL)} ناموفق از {len(PASS)+len(FAIL)} تست")
    if FAIL:
        print("تست‌های ناموفق:")
        for f in FAIL:
            print(f"  - {f}")
        sys.exit(1)
    sys.exit(0)
