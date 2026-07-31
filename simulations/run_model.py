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
from twelve_gates_model import TwelveGatesModel, PreconditionError, ExternalScenarioDriver
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
    required_top = ["preconditions", "time", "gates", "coalitions", "budget",
                     "mirror13", "gate_zero", "emergency_court", "bureaucracy",
                     "civil_society", "trust_dynamics"]
    for key in required_top:
        if key not in cfg:
            errors.append(f"کلید اجباری غایب: '{key}'")
    if "gates" in cfg:
        if len(cfg["gates"]) != 12:
            errors.append(f"باید دقیقاً ۱۲ گیت باشد، {len(cfg['gates'])} داده شد")
        ids = [g.get("gate_id") for g in cfg["gates"]]
        if sorted(ids) != list(range(12)):
            errors.append(f"gate_id ها باید دقیقاً ۰..۱۱ باشند، یافت شد: {sorted(ids)}")
        for g in cfg["gates"]:
            for field in ["resource_share", "exec_power", "info_reliability"]:
                v = g.get(field)
                if v is None or not (0 <= v <= 1):
                    errors.append(f"گیت {g.get('gate_id')}: '{field}'={v} باید در [0,1] باشد")
    if "preconditions" in cfg:
        cap = cfg["preconditions"].get("coordination_capacity")
        mn = cfg["preconditions"].get("min_coordination_capacity")
        if cap is not None and mn is not None and cap < mn:
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
