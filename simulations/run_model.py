#!/usr/bin/env python3
"""
run_model.py — رابط خط‌فرمان مدل دوازده‌گیت
=================================================
استفاده:
  python3 run_model.py --config baseline.json --n-runs 300 --max-ticks 520 --out results.json
  python3 run_model.py --config baseline.json --shock security,energy,economy --shock-magnitude 0.02
  python3 run_model.py --list-params            # نمایش همه‌ی پارامترها با منبع/وضعیت هرکدام

⚠️ این ابزار مدل را قابل‌اجرا و قابل‌پیکربندی می‌کند — نه قابل‌اتکا برای پیش‌بینی واقعی.
هر خروجی همیشه با claim_label صریح برچسب می‌خورد.
"""
import argparse, json, sys, time
import numpy as np
from twelve_gates_model import TwelveGatesModel, PreconditionError, ExternalScenarioDriver, N_GATES
from param_provenance import PARAM_PROVENANCE, print_provenance_table

GATE_NAME_TO_ID = {"economy":0,"science":1,"security":2,"culture":3,"energy":4,"education":5,
                   "justice":6,"health":7,"environment":8,"infrastructure":9,
                   "foreign_affairs":10,"welfare":11}

class ConfigValidationError(Exception): pass

def normalize_config(cfg: dict) -> dict:
    """
    رفع یک باگ واقعی: JSON کلیدهای عددی دیکشنری را به رشته تبدیل می‌کند
    (trust_row, affinity_row, overlap_row) — این تابع آن‌ها را به int برمی‌گرداند.
    بدون این تابع، هر بار config از فایل JSON خوانده شود، تمام مقادیر trust/affinity
    به‌خاطر شکست خاموش .get() به مقدار پیش‌فرض سقوط می‌کنند — دقیقاً همان چیزی که
    باعث نتیجه‌ی نادرست اولین اجرای این CLI شد.
    """
    for g in cfg.get("gates", []):
        for field in ["trust_row", "affinity_row", "overlap_row"]:
            if field in g and isinstance(g[field], dict):
                g[field] = {int(k): v for k, v in g[field].items()}
    return cfg

def validate_config(cfg: dict) -> list:
    """اعتبارسنجی صریح — خطای مبهم بهتر از کرش خاموش است."""
    errors = []

    def in_unit_interval(path, value):
        if (value is None or isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not (0 <= value <= 1)):
            errors.append(f"{path}={value} باید عددی در [0,1] باشد")

    def positive_int(path, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            errors.append(f"{path}={value} باید integer مثبت باشد")

    required_top = ["preconditions", "time", "emergency_extension", "model_assumptions",
                     "gates", "coalitions", "budget", "mirror13", "gate_zero",
                     "emergency_court", "bureaucracy", "civil_society", "trust_dynamics"]
    for key in required_top:
        if key not in cfg:
            errors.append(f"کلید اجباری غایب: '{key}'")
    if "gates" in cfg:
        if not isinstance(cfg["gates"], list) or len(cfg["gates"]) != 12:
            errors.append(
                f"باید دقیقاً ۱۲ گیت باشد، "
                f"{len(cfg['gates']) if isinstance(cfg['gates'], list) else 'non-list'} داده شد")
        else:
            ids = [g.get("gate_id") for g in cfg["gates"]]
            if any(isinstance(x, bool) or not isinstance(x, int) for x in ids):
                errors.append(f"gate_id ها باید integer باشند، یافت شد: {ids}")
            elif sorted(ids) != list(range(12)):
                errors.append(f"gate_id ها باید دقیقاً ۰..۱۱ باشند، یافت شد: {sorted(ids)}")

            prob_fields = [
                "resource_share", "exec_power", "info_reliability",
                "audit_exposure", "initial_crisis_load", "legitimacy_internal",
                "external_exposure", "memory_dependence",
                "critical_report_threshold", "verification_accuracy",
            ]
            for g in cfg["gates"]:
                gid = g.get("gate_id")
                for field in prob_fields:
                    in_unit_interval(f"gate[{gid}].{field}", g.get(field))

                if isinstance(gid, int) and not isinstance(gid, bool) and 0 <= gid < N_GATES:
                    expected = set(range(N_GATES)) - {gid}
                    for field in ("trust_row", "affinity_row", "overlap_row"):
                        row = g.get(field)
                        if not isinstance(row, dict):
                            errors.append(f"gate[{gid}].{field} باید dict باشد")
                            continue
                        if set(row) != expected:
                            errors.append(
                                f"gate[{gid}].{field} باید دقیقاً کلیدهای سایر گیت‌ها را داشته باشد")
                        for key, value in row.items():
                            in_unit_interval(f"gate[{gid}].{field}[{key}]", value)

            shares = [g.get("resource_share") for g in cfg["gates"]]
            if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in shares):
                if abs(sum(shares) - 1.0) > 1e-9:
                    errors.append(
                        f"مجموع resource_share اولیه باید 1 باشد، یافت شد: {sum(shares)}")
    if "coalitions" in cfg:
        aggregation = cfg["coalitions"].get("pair_aggregation", "mean")
        if aggregation not in {"mean", "minimum", "maximum"}:
            errors.append(
                f"coalitions.pair_aggregation={aggregation!r} باید یکی از mean/minimum/maximum باشد")
        weights = cfg["coalitions"].get("weights", {})
        expected_weights = {
            "w1_affinity", "w2_trust", "w3_complementarity",
            "w4_audit_exposure", "w5_overlap_penalty",
        }
        if set(weights) != expected_weights:
            errors.append("coalitions.weights باید دقیقاً پنج وزن تعریف‌شده را داشته باشد")
        else:
            vals = list(weights.values())
            for name, value in weights.items():
                in_unit_interval(f"coalitions.weights.{name}", value)
            if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
                if abs(sum(vals) - 1.0) > 1e-9:
                    errors.append(f"مجموع قدرمطلق weights مدل فعلی باید 1 باشد، یافت شد: {sum(vals)}")

        for name in ("theta_pair", "theta_audit", "trust_dissolve_floor", "crisis_divergence_max"):
            in_unit_interval(f"coalitions.{name}", cfg["coalitions"].get(name))

        cartel = cfg["coalitions"].get("cartel", {})
        positive_int("coalitions.cartel.K_min_duration_ticks", cartel.get("K_min_duration_ticks"))
        positive_int("coalitions.cartel.M_consecutive_decisions", cartel.get("M_consecutive_decisions"))
        power = cartel.get("theta_power_sum")
        if (power is None or isinstance(power, bool)
                or not isinstance(power, (int, float)) or power <= 0):
            errors.append(f"coalitions.cartel.theta_power_sum={power} باید عدد مثبت باشد")
        cluster = cartel.get("material_cluster")
        if (not isinstance(cluster, list) or not cluster
                or len(cluster) != len(set(cluster))
                or any(isinstance(x, bool) or not isinstance(x, int)
                       or x < 0 or x >= N_GATES for x in cluster)):
            errors.append("coalitions.cartel.material_cluster باید list یکتای gate_idهای 0..11 باشد")
    if "budget" in cfg:
        rule = cfg["budget"].get("reallocation_rule")
        fraction = cfg["budget"].get("reallocation_required_fraction")
        if rule != "qualified_majority":
            errors.append(
                f"budget.reallocation_rule={rule!r} فعلاً فقط qualified_majority پشتیبانی می‌شود")
        if fraction is None or not isinstance(fraction, (int, float)) or not (0 < fraction <= 1):
            errors.append(
                f"budget.reallocation_required_fraction={fraction} باید در (0,1] باشد")
    if "emergency_extension" in cfg:
        support_p = cfg["emergency_extension"].get("support_probability")
        required_fraction = cfg["emergency_extension"].get("required_fraction")
        if support_p is None or not (0 <= support_p <= 1):
            errors.append(
                f"emergency_extension.support_probability={support_p} باید در [0,1] باشد")
        if required_fraction is None or not (0 < required_fraction <= 1):
            errors.append(
                f"emergency_extension.required_fraction={required_fraction} باید در (0,1] باشد")
    if "external_timeline" in cfg:
        timeline = cfg["external_timeline"]
        if not isinstance(timeline, list):
            errors.append("external_timeline باید یک list باشد")
        else:
            for idx, ev in enumerate(timeline):
                if not isinstance(ev, dict):
                    errors.append(f"external_timeline[{idx}] باید object باشد")
                    continue
                tick = ev.get("tick")
                gate_ids = ev.get("gate_ids")
                if not isinstance(tick, int) or tick < 0:
                    errors.append(f"external_timeline[{idx}].tick باید integer نامنفی باشد")
                if not isinstance(gate_ids, list) or not gate_ids:
                    errors.append(f"external_timeline[{idx}].gate_ids باید list غیرخالی باشد")
                elif any((not isinstance(g, int)) or g < -1 or g >= N_GATES for g in gate_ids):
                    errors.append(f"external_timeline[{idx}].gate_ids فقط -1 یا 0..11 مجاز است")
                for field in ("crisis_delta", "exposure_delta"):
                    value = ev.get(field, 0.0)
                    if not isinstance(value, (int, float)):
                        errors.append(f"external_timeline[{idx}].{field} باید عدد باشد")
    if "model_assumptions" in cfg:
        a = cfg["model_assumptions"]
        bounded = [
            "audit_accuracy_bonus",
            "coalition_propensity_resource_weight",
            "coalition_propensity_trust_weight",
            "capture_pressure_resource_weight",
            "capture_pressure_cluster_affinity_weight",
            "capture_pressure_overlap_weight",
            "vote_support_intercept",
            "vote_support_trust_weight",
            "public_legitimacy_memory_weight",
            "public_legitimacy_internal_weight",
            "armed_bloc_split_threshold",
            "armed_bloc_split_probability",
            "armed_bloc_confrontation_threshold",
            "armed_bloc_confrontation_probability",
            "armed_bloc_bargain_threshold",
            "armed_bloc_bargain_probability",
        ]
        for name in bounded:
            value = a.get(name)
            if value is None or not isinstance(value, (int, float)) or not (0 <= value <= 1):
                errors.append(f"model_assumptions.{name}={value} باید عددی در [0,1] باشد")
        drift = a.get("bureaucracy_politicization_drift_rate")
        if drift is None or not isinstance(drift, (int, float)) or drift < 0:
            errors.append(
                f"model_assumptions.bureaucracy_politicization_drift_rate={drift} باید نامنفی باشد")
        weight_groups = [
            ("coalition propensity", [
                "coalition_propensity_resource_weight",
                "coalition_propensity_trust_weight",
            ]),
            ("capture pressure", [
                "capture_pressure_resource_weight",
                "capture_pressure_cluster_affinity_weight",
                "capture_pressure_overlap_weight",
            ]),
            ("public legitimacy proxy", [
                "public_legitimacy_memory_weight",
                "public_legitimacy_internal_weight",
            ]),
        ]
        for label, names in weight_groups:
            vals = [a.get(name) for name in names]
            if all(isinstance(v, (int, float)) for v in vals):
                if abs(sum(vals) - 1.0) > 1e-9:
                    errors.append(f"model_assumptions weights for {label} باید مجموعاً 1 باشند")
        vi = a.get("vote_support_intercept")
        vw = a.get("vote_support_trust_weight")
        if isinstance(vi, (int, float)) and isinstance(vw, (int, float)) and vi + vw > 1:
            errors.append("vote_support_intercept + vote_support_trust_weight نباید از 1 بیشتر شود")
    if "time" in cfg:
        for name in (
            "tick_days", "rotation_period_ticks",
            "budget_review_period_ticks", "emergency_fuse_ticks",
        ):
            positive_int(f"time.{name}", cfg["time"].get(name))
    if "budget" in cfg:
        in_unit_interval("budget.annual_delta_cap", cfg["budget"].get("annual_delta_cap"))

    if "trust_dynamics" in cfg:
        for name in (
            "trust_learning_rate", "audit_detection_prob", "dissent_chilling_beta",
        ):
            in_unit_interval(f"trust_dynamics.{name}", cfg["trust_dynamics"].get(name))

    if "mirror13" in cfg:
        if not isinstance(cfg["mirror13"].get("enabled"), bool):
            errors.append("mirror13.enabled باید boolean باشد")
        in_unit_interval("mirror13.coordination_gain", cfg["mirror13"].get("coordination_gain"))

    if "gate_zero" in cfg:
        for name in (
            "admission_threshold", "measurement_noise_sd", "entropy_manipulability",
        ):
            in_unit_interval(f"gate_zero.{name}", cfg["gate_zero"].get(name))

    if "emergency_court" in cfg:
        mode = cfg["emergency_court"].get("independence_mode")
        if mode not in {"ideal", "erodible"}:
            errors.append(
                f"emergency_court.independence_mode={mode!r} باید ideal یا erodible باشد")
        in_unit_interval(
            "emergency_court.erosion_rate",
            cfg["emergency_court"].get("erosion_rate"),
        )

    if "bureaucracy" in cfg:
        for name in (
            "memory_stock", "politicization_risk", "service_continuity",
            "archive_integrity", "geo_redundancy", "redundancy_floor",
        ):
            in_unit_interval(f"bureaucracy.{name}", cfg["bureaucracy"].get(name))

    if "civil_society" in cfg:
        for name in (
            "mobilization_capacity", "oversight_strength", "media_visibility",
            "union_density_proxy", "public_legitimacy_signal",
        ):
            in_unit_interval(f"civil_society.{name}", cfg["civil_society"].get(name))

    if "armed_blocs" in cfg:
        if not isinstance(cfg["armed_blocs"], list):
            errors.append("armed_blocs باید list باشد")
        else:
            for idx, bloc in enumerate(cfg["armed_blocs"]):
                for name in (
                    "field_control", "negotiation_readiness", "conflict_risk",
                    "external_dependency", "organizational_cohesion",
                ):
                    in_unit_interval(f"armed_blocs[{idx}].{name}", bloc.get(name))

    if "preconditions" in cfg:
        cap = cfg["preconditions"].get("coordination_capacity")
        mn = cfg["preconditions"].get("min_coordination_capacity")
        in_unit_interval("preconditions.coordination_capacity", cap)
        in_unit_interval("preconditions.min_coordination_capacity", mn)
        if (isinstance(cap, (int, float)) and not isinstance(cap, bool)
                and isinstance(mn, (int, float)) and not isinstance(mn, bool)
                and cap < mn):
            errors.append(
                f"coordination_capacity={cap} < min={mn} — طبق بند ۱۰.۶.۷، مدل باید امتناع کند "
                f"(این خطا نیست، این خودِ رفتار صحیح مدل است؛ نه یک باگ config)")
    return errors

def apply_shock(cfg: dict, gate_names: list, magnitude: float):
    """تزریق شوک روی گیت‌های نام‌برده‌شده — معادل StressDriver ولی پیکربندی‌پذیر از CLI."""
    ids = [GATE_NAME_TO_ID[n] for n in gate_names if n in GATE_NAME_TO_ID]
    class CLIShockDriver(ExternalScenarioDriver):
        def current_shock_for(self, gate_id):
            if gate_id in ids:
                return {"crisis_delta": magnitude, "exposure_delta": magnitude / 2}
            return {}
    return CLIShockDriver([]), ids

def run(cfg, n_runs, max_ticks, shock_ids, shock_magnitude, master_seed):
    rng = np.random.default_rng(master_seed)
    seeds = rng.integers(0, 2**31, size=n_runs)
    results, n_refused = [], 0
    for s in seeds:
        try:
            m = TwelveGatesModel(cfg, seed=int(s))
        except PreconditionError as e:
            n_refused += 1
            continue
        if shock_ids:
            driver, _ = apply_shock(cfg, [], 0)  # placeholder ساخت کلاس؛ زیر بازنویسی می‌شود
            class D(ExternalScenarioDriver):
                def current_shock_for(self, gate_id):
                    if gate_id in shock_ids:
                        return {"crisis_delta": shock_magnitude, "exposure_delta": shock_magnitude/2}
                    return {}
            m.external = D([])
        results.append(m.run(max_ticks))
    return results, n_refused

def summarize(results):
    if not results:
        return {}
    return {
        "n_completed": len(results),
        "cartel_capture_rate": float(np.mean([r["cartel_capture_ever"] for r in results])),
        "emergency_time_share_mean": float(np.mean([r["emergency_time_share"] for r in results])),
        "coalition_mean_duration": float(np.mean([r["coalition_mean_duration"] for r in results])),
        "legitimacy_internal_mean": float(np.mean([r["mean_legitimacy_end"] for r in results])),
        "capture_pressure_mean": float(np.mean([r["mean_capture_pressure_end"] for r in results])),
        "bureaucracy_politicization_mean": float(np.mean([r["bureaucracy_politicization_end"] for r in results])),
        "public_legitimacy_signal_mean": float(np.mean([r["public_legitimacy_signal_end"] for r in results])),
    }

def main():
    p = argparse.ArgumentParser(description="اجرای مدل دوازده‌گیت — همیشه با برچسب صریح ادعا")
    p.add_argument("--config", type=str, help="مسیر فایل JSON کانفیگ")
    p.add_argument("--n-runs", type=int, default=100)
    p.add_argument("--max-ticks", type=int, default=520)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--shock", type=str, default="", help="لیست گیت‌ها با کاما: security,energy,economy")
    p.add_argument("--shock-magnitude", type=float, default=0.02)
    p.add_argument("--out", type=str, default="cli_results.json")
    p.add_argument("--list-params", action="store_true", help="نمایش جدول منبع/وضعیت پارامترها و خروج")
    args = p.parse_args()

    if args.list_params:
        print_provenance_table()
        sys.exit(0)

    if not args.config:
        print("خطا: --config الزامی است (یا --list-params برای دیدن پارامترها)", file=sys.stderr)
        sys.exit(1)

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg = normalize_config(cfg)

    errors = validate_config(cfg)
    if errors:
        print("خطاهای اعتبارسنجی config:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    claim_label = cfg.get("meta", {}).get("claim_label", "نامشخص")
    if claim_label != "hypothesis":
        print(f"⚠ هشدار: claim_label این کانفیگ '{claim_label}' است، نه 'hypothesis'.\n"
              f"  طبق اصل صفر، هر کانفیگی که کالیبراسیون واقعی ندارد باید صریح hypothesis برچسب بخورد.",
              file=sys.stderr)

    shock_ids = [GATE_NAME_TO_ID[n.strip()] for n in args.shock.split(",") if n.strip() in GATE_NAME_TO_ID]

    t0 = time.time()
    results, n_refused = run(cfg, args.n_runs, args.max_ticks, shock_ids, args.shock_magnitude, args.seed)
    elapsed = time.time() - t0

    summary = summarize(results)
    summary["claim_label"] = claim_label
    summary["n_requested"] = args.n_runs
    summary["n_refused_precondition"] = n_refused
    summary["elapsed_seconds"] = round(elapsed, 1)
    summary["shock_applied_to"] = args.shock or "(هیچ)"

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nذخیره شد: {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
