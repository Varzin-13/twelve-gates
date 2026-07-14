"""
سناریوی ۱: آزمون ائتلاف مادی (Coalition Capture Test)
==========================================================
سؤال پیش‌ثبت‌شده:
آیا سه گیت با منافع مکمل (امنیت، انرژی، اقتصاد)، حتی با اعمال دو
مکانیزم کاهش‌دهنده‌ی پیشنهادی در سند (تفکیک بودجه‌ای + ممنوعیت
هم‌پوشانی پرسنلی)، می‌توانند در بلندمدت نتایج تصمیم‌گیری شبکه‌ی
۱۲گیتی را به نفع خود منحرف کنند؟

معیار شکست (پیش‌ثبت‌شده):
"نرخ تصاحب" = درصد تصمیمات کلیدی که علی‌رغم مخالفت اکثریت ۹ گیت
دیگر، به نفع ائتلاف سه‌گانه به تصویب می‌رسد.
اگر نرخ تصاحب در حالت "با مکانیزم کاهش‌دهنده" هنوز به‌طور معنادار
بالاتر از سطح شانس (که با ائتلاف‌های تصادفی سه‌نفره‌ی دیگر مقایسه
می‌شود) بماند، فرضیه‌ی "مکانیزم‌های کاهش‌دهنده کافی‌اند" رد می‌شود.

این یک شبیه‌سازی مونت‌کارلوی سبک است، نه یک مدل جامع سیاسی. هدف
آزمون جهت اثر (آیا کاهش واقعی رخ می‌دهد) است، نه پیش‌بینی دقیق
رفتار سیاسی واقعی ایران.

توجه روش‌شناختی (دو اصلاح انجام‌شده در حین ممیزی این مدل):
۱) در نسخه‌ی اول، احتمال تبانی برای «کارتل واقعی» و «ائتلاف
   تصادفیِ کنترل» به‌اشتباه یکسان تعریف شده بود که نتیجه را به‌طور
   تصنعی تضمین می‌کرد. اصلاح شد: کارتل واقعی دو مزیت ساختاری صریح
   دارد که کنترل تصادفی ندارد - احتمال تبانی ذاتاً بالاتر، و توان
   فشار/نفوذ بر آرای گیت‌های دیگر (LEVERAGE_PRESSURE).
۲) معیار «تصاحب» در نسخه‌ی دوم به‌اشتباه فقط یک نقطه‌ی تکی از توزیع
   احتمال را می‌سنجید (دقیقاً ۴ رأی موافق از ۹ گیت مستقل)، که باعث
   نوسان غیرمنطقی نتیجه با تغییر کوچک پارامترها می‌شد. اصلاح شد:
   «تصاحب» یعنی تصمیم تصویب شد و آرای کارتل *تعیین‌کننده* بودند
   (بازه‌ی ۴ تا ۶ رأی مستقل، نه یک نقطه).
این پارامترها فرض‌های مدل‌سازی برای آزمون جهت اثرند، نه داده‌ی
تجربی درباره‌ی ایران.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from persian_shaping import reshape_persian as _r

# فونت FreeSerif پوشش کامل حروف فارسی دارد (روی اغلب توزیع‌های لینوکس/دبیان
# از قبل نصب است). اگر پیدا نشد، matplotlib با فونت پیش‌فرض ادامه می‌دهد -
# نمودار همچنان تولید می‌شود، فقط شکل‌دهی حروف فارسی ممکن است ناقص باشد.
_FONT_CANDIDATES = [
    '/usr/share/fonts/truetype/freefont/FreeSerif.ttf',       # دبیان/اوبونتو
    '/usr/share/fonts/TTF/FreeSerif.ttf',                       # آرچ
    '/opt/homebrew/share/fonts/FreeSerif.ttf',                  # مک (Homebrew)
    'C:/Windows/Fonts/tahoma.ttf',                               # ویندوز (جایگزین)
]
for _fp in _FONT_CANDIDATES:
    if os.path.exists(_fp):
        fm.fontManager.addfont(_fp)
        plt.rcParams['font.family'] = fm.FontProperties(fname=_fp).get_name()
        break
else:
    print("هشدار: فونت با پوشش کامل فارسی پیدا نشد؛ از فونت پیش‌فرض matplotlib "
          "استفاده می‌شود (حروف فارسی ممکن است درست شکل نگیرند).", file=sys.stderr)

RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)

GATES = [
    "اقتصاد", "علم", "امنیت", "فرهنگ", "انرژی", "آموزش",
    "دادگستری", "سلامت", "محیط‌زیست", "زیرساخت", "روابط خارجی", "رفاه اجتماعی"
]
N_GATES = 12
CARTEL_IDX = [GATES.index("امنیت"), GATES.index("انرژی"), GATES.index("اقتصاد")]

N_PERIODS = 2000         # تعداد دوره‌های تصمیم‌گیری شبیه‌سازی‌شده
N_TRIALS = 300           # تعداد اجراهای مستقل مونت‌کارلو برای هر حالت
MAJORITY_THRESHOLD = 7   # از ۱۲ گیت، برای تصویب یک تصمیم لازم است

# ---------------------------------------------------------------
# پارامترهای مدل
# ---------------------------------------------------------------
# baseline_collusion_prob: احتمال اینکه در یک دوره، سه گیت کارتل
#   بتوانند به‌طور مؤثر هماهنگ شوند (بدون هیچ مکانیزم کاهش‌دهنده‌ای)
# mitigation_effect: میزان کاهش این احتمال توسط تفکیک بودجه‌ای +
#   ممنوعیت هم‌پوشانی پرسنلی (بر اساس ادبیات ضد-تبانی سازمانی؛
#   این عدد یک فرض مدل‌سازی است، نه داده‌ی تجربی مستقیم درباره‌ی
#   ایران - این محدودیت باید در تفسیر نتایج لحاظ شود)
BASELINE_COLLUSION_PROB = 0.55   # احتمال تبانی مؤثر کارتل واقعی (منافع مادی مکمل)
RANDOM_TRIO_COLLUSION_PROB = 0.15  # احتمال تبانی یک ائتلاف تصادفیِ سه‌نفره (کنترل، بدون منافع مکمل)
LEVERAGE_PRESSURE = 0.20         # افزایش احتمال رأی «بله»‌ی هر یک از ۹ گیت دیگر تحت فشار/نفوذ مادی کارتل (بودجه، اطلاعات، ارتقا)
MITIGATION_EFFECT = 0.35         # کاهش نسبی احتمال تبانی توسط تفکیک بودجه‌ای + ممنوعیت هم‌پوشانی پرسنلی
LEVERAGE_MITIGATION_EFFECT = 0.50  # کاهش نسبی توان فشار مادی توسط همان مکانیزم‌ها
SWING_VOTE_PROB = 0.5


def simulate_trial(collusion_prob, leverage_pressure, n_periods=N_PERIODS):
    """یک اجرای کامل شبیه‌سازی برای کارتل واقعی (با اهرم مادی).

    تعریف «تصاحب»: تصمیم تصویب شد (کل آرا >= آستانه) و آرای کارتل
    *تعیین‌کننده* بودند - یعنی بدون آن‌ها تصمیم تصویب نمی‌شد.
    با آستانه‌ی ۷ از ۱۲ و ۳ رأی ثابت کارتل، این یعنی آرای ۹ گیت
    مستقل در بازه‌ی [۴, ۶] باشد (نه دقیقاً یک نقطه).
    """
    captured = 0
    for _ in range(n_periods):
        cartel_coordinates = rng.random() < collusion_prob
        swing_prob = min(SWING_VOTE_PROB + leverage_pressure, 0.95) if cartel_coordinates else SWING_VOTE_PROB
        independent_votes = rng.random(N_GATES - 3) < swing_prob
        independent_yes = independent_votes.sum()
        if cartel_coordinates:
            total_yes = independent_yes + 3
            passed = total_yes >= MAJORITY_THRESHOLD
            decisive = MAJORITY_THRESHOLD - 3 <= independent_yes < MAJORITY_THRESHOLD
            if passed and decisive:
                captured += 1
    return captured / n_periods


def simulate_control_trial(n_periods=N_PERIODS):
    """کنترل: ائتلاف تصادفی سه‌نفره، بدون منافع مادی مکمل و بدون اهرم فشار."""
    captured = 0
    for _ in range(n_periods):
        coordinates = rng.random() < RANDOM_TRIO_COLLUSION_PROB
        independent_votes = rng.random(N_GATES - 3) < SWING_VOTE_PROB
        independent_yes = independent_votes.sum()
        if coordinates:
            total_yes = independent_yes + 3
            passed = total_yes >= MAJORITY_THRESHOLD
            decisive = MAJORITY_THRESHOLD - 3 <= independent_yes < MAJORITY_THRESHOLD
            if passed and decisive:
                captured += 1
    return captured / n_periods


def run_condition(collusion_prob, leverage_pressure, label):
    capture_rates = []
    control_rates = []
    for _ in range(N_TRIALS):
        capture_rates.append(simulate_trial(collusion_prob, leverage_pressure))
        control_rates.append(simulate_control_trial())
    capture_rates = np.array(capture_rates)
    control_rates = np.array(control_rates)
    print(f"\n[{label}]")
    print(f"  احتمال تبانی کارتل={collusion_prob:.2f}  فشار اهرمی=+{leverage_pressure:.2f}")
    print(f"  نرخ تصاحب کارتل امنیت-انرژی-اقتصاد: میانگین={capture_rates.mean():.4f}  "
          f"(انحراف معیار={capture_rates.std():.4f})")
    print(f"  نرخ تصاحب ائتلاف تصادفی (کنترل):     میانگین={control_rates.mean():.4f}  "
          f"(انحراف معیار={control_rates.std():.4f})")
    return capture_rates, control_rates


if __name__ == "__main__":
    print("=" * 70)
    print("سناریوی ۱: آزمون ائتلاف مادی (امنیت-انرژی-اقتصاد)")
    print("=" * 70)

    # حالت ۱: بدون هیچ مکانیزم کاهش‌دهنده
    baseline_capture, baseline_control = run_condition(
        BASELINE_COLLUSION_PROB, LEVERAGE_PRESSURE, "بدون مکانیزم کاهش‌دهنده"
    )

    # حالت ۲: با اعمال تفکیک بودجه‌ای + ممنوعیت هم‌پوشانی پرسنلی
    mitigated_prob = BASELINE_COLLUSION_PROB * (1 - MITIGATION_EFFECT)
    mitigated_leverage = LEVERAGE_PRESSURE * (1 - LEVERAGE_MITIGATION_EFFECT)
    mitigated_capture, mitigated_control = run_condition(
        mitigated_prob, mitigated_leverage, "با مکانیزم‌های کاهش‌دهنده (بند ۳.۶)"
    )

    # ---------------------------------------------------------------
    # نتیجه‌گیری آماری ساده
    # ---------------------------------------------------------------
    reduction_pct = (1 - mitigated_capture.mean() / baseline_capture.mean()) * 100
    still_above_control = mitigated_capture.mean() - mitigated_control.mean()

    print("\n" + "=" * 70)
    print("نتیجه‌گیری:")
    print(f"  کاهش نرخ تصاحب با اعمال مکانیزم‌ها: {reduction_pct:.1f}٪")
    print(f"  فاصله‌ی باقی‌مانده تا سطح شانس (ائتلاف تصادفی) پس از کاهش: "
          f"{still_above_control:.4f}")
    if still_above_control > 0.01:
        print("  => فرضیه رد می‌شود: حتی با مکانیزم‌های کاهش‌دهنده، کارتل ساختاری")
        print("     همچنان به‌طور معنادار بیش از یک ائتلاف تصادفی موفق می‌شود.")
        print("     این با اذعان صریح بند ۳.۶ سند («کاهش‌دهنده، نه مانع») همخوان است.")
    else:
        print("  => در این مدل ساده، مکانیزم‌ها کارتل را به سطح شانس نزدیک کردند.")
    print("=" * 70)

    # ذخیره‌ی نتایج خام برای گزارش
    results = {
        "baseline_collusion_prob": BASELINE_COLLUSION_PROB,
        "mitigated_collusion_prob": mitigated_prob,
        "baseline_capture_mean": float(baseline_capture.mean()),
        "baseline_capture_std": float(baseline_capture.std()),
        "mitigated_capture_mean": float(mitigated_capture.mean()),
        "mitigated_capture_std": float(mitigated_capture.std()),
        "control_capture_mean_baseline": float(baseline_control.mean()),
        "control_capture_mean_mitigated": float(mitigated_control.mean()),
        "reduction_pct": float(reduction_pct),
        "gap_above_chance_after_mitigation": float(still_above_control),
        "n_trials": N_TRIALS,
        "n_periods_per_trial": N_PERIODS,
        "seed": RNG_SEED,
    }
    with open("/home/claude/scenario1_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # ---------------------------------------------------------------
    # نمودار
    # ---------------------------------------------------------------
    plt.rcParams['font.size'] = 11
    fig, ax = plt.subplots(figsize=(8, 5.5))

    conditions = [_r("بدون مکانیزم\nکاهش‌دهنده"), _r("با مکانیزم‌های\nکاهش‌دهنده (۳.۶)")]
    cartel_means = [baseline_capture.mean(), mitigated_capture.mean()]
    cartel_stds = [baseline_capture.std(), mitigated_capture.std()]
    control_means = [baseline_control.mean(), mitigated_control.mean()]
    control_stds = [baseline_control.std(), mitigated_control.std()]

    x = np.arange(len(conditions))
    width = 0.32

    ax.bar(x - width/2, cartel_means, width, yerr=cartel_stds, capsize=5,
           label=_r("کارتل امنیت-انرژی-اقتصاد"), color="#c0392b")
    ax.bar(x + width/2, control_means, width, yerr=control_stds, capsize=5,
           label=_r("ائتلاف تصادفی (کنترل / سطح شانس)"), color="#7f8c8d")

    ax.set_ylabel(_r("نرخ تصاحب تصمیمات کلیدی"))
    ax.set_title(_r("سناریوی ۱ — نرخ تصاحب تصمیمات: کارتل ساختاری در برابر سطح شانس"))
    ax.set_xticks(x)
    ax.set_xticklabels(conditions)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("/home/claude/scenario1_chart.png", dpi=150)
    print("\nنمودار ذخیره شد: scenario1_chart.png")
