"""
سناریوی ۳: آزمون فروپاشی هم‌زمان (زلزله‌ی بزرگ تهران)
==========================================================
سؤال پیش‌ثبت‌شده:
اگر زیرساخت حیاتی (دبیرخانه‌ی هماهنگی Mirror-13، سرورهای سجل عمومی،
منبع انتروپی Gate Zero) در ۱، ۲، یا ۳ شهر مختلف پراکنده باشد، زمان
بازیابی کارکرد حداقلی سیستم پس از یک فاجعه‌ی طبیعی بزرگ در یک شهر
(تهران) چقدر تغییر می‌کند؟

معیار شکست (پیش‌ثبت‌شده):
اگر پراکندگی جغرافیایی زمان بازیابی را به‌طور معنادار کوتاه نکند،
راهکار بند ۳.۶ («پراکندگی اجباری در حداقل ۳ شهر») نمی‌تواند به‌عنوان
یک راهکار مؤثر معرفی شود - باید فقط به‌عنوان کاهش‌دهنده‌ی جزئی ثبت
شود.

فرض‌های کلیدی مدل:
- زلزله فقط زیرساختی را که در همان شهر مستقر است از کار می‌اندازد
  (فرض ساده - در واقعیت شبکه‌های ارتباطی سراسری هم می‌توانند
  آسیب ببینند، که این مدل لحاظ نکرده)
- سه جزء حیاتی مدل شده: (۱) دبیرخانه‌ی هماهنگی Mirror-13،
  (۲) سرورهای سجل عمومی/راستی‌آزمایی، (۳) منبع انتروپی Gate Zero
- زمان بازیابی هر جزء از کارافتاده با توزیع نمایی مدل شده (فرض
  ساده‌شده‌ی مهندسی قابلیت اطمینان - نه داده‌ی واقعی درباره‌ی
  زیرساخت ایران)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from persian_shaping import reshape_persian as _r
from theme_dark import apply_dark_theme, INK, MUTED, BRASS, RUST, GREEN, VERDIGRIS, FAINT
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

RNG_SEED = 21
rng = np.random.default_rng(RNG_SEED)

N_TRIALS = 2000
COMPONENTS = ["دبیرخانه Mirror-13", "سرورهای سجل عمومی", "منبع انتروپی Gate Zero"]
N_COMPONENTS = 3

# میانگین زمان بازیابی یک جزء از کارافتاده (روز) - فرض مهندسی ساده
MEAN_RECOVERY_DAYS_PER_COMPONENT = 21
# سیستم «کارکرد حداقلی» را وقتی بازمی‌یابد که همه‌ی اجزای ازکارافتاده بازیابی شوند
# (فرض محافظه‌کارانه؛ در واقعیت شاید بازیابی جزئی هم کافی باشد)


def simulate_earthquake(n_cities):
    """
    n_cities=1: هر سه جزء در یک شهر (تهران) -> زلزله هر سه را هم‌زمان می‌زند
    n_cities=2: دو جزء در تهران، یکی در شهر دیگر
    n_cities=3: هر جزء در یک شهر جداگانه -> فقط اجزای مستقر در تهران آسیب می‌بینند
    """
    if n_cities == 1:
        affected = [True, True, True]
    elif n_cities == 2:
        # فرض: دو جزء با بیشترین وابستگی متقابل (هماهنگی + سجل) در تهران می‌مانند
        affected = [True, True, False]
    elif n_cities == 3:
        # فقط یکی (به‌طور تصادفی هر بار همان یکی که در تهران قرار دارد) آسیب می‌بیند
        affected = [True, False, False]
    else:
        raise ValueError("n_cities must be 1, 2, or 3")

    recovery_times = []
    for is_affected in affected:
        if is_affected:
            # زمان بازیابی از توزیع نمایی (فرض مهندسی ساده)
            recovery_times.append(rng.exponential(MEAN_RECOVERY_DAYS_PER_COMPONENT))

    if not recovery_times:
        return 0.0

    # کارکرد حداقلی وقتی بازمی‌گردد که همه‌ی اجزای آسیب‌دیده بازیابی شوند
    return max(recovery_times)


def run_condition(n_cities, label):
    times = np.array([simulate_earthquake(n_cities) for _ in range(N_TRIALS)])
    print(f"\n[{label}]")
    print(f"  میانگین زمان بازیابی: {times.mean():.1f} روز  "
          f"(میانه={np.median(times):.1f}، انحراف معیار={times.std():.1f})")
    print(f"  احتمال بازیابی در کمتر از ۷ روز: {(times < 7).mean()*100:.1f}٪")
    print(f"  احتمال بازیابی بیش از ۳۰ روز طول کشیدن: {(times > 30).mean()*100:.1f}٪")
    return times


if __name__ == "__main__":
    print("=" * 70)
    print("سناریوی ۳: فروپاشی هم‌زمان (زلزله‌ی بزرگ تهران)")
    print("=" * 70)

    t1 = run_condition(1, "بدون پراکندگی (هر سه جزء در تهران)")
    t2 = run_condition(2, "پراکندگی جزئی (دو جزء در تهران، یکی خارج)")
    t3 = run_condition(3, "پراکندگی کامل (هر جزء در شهر جداگانه - بند ۳.۶)")

    reduction_2 = (1 - t2.mean() / t1.mean()) * 100
    reduction_3 = (1 - t3.mean() / t1.mean()) * 100

    print("\n" + "=" * 70)
    print("نتیجه‌گیری:")
    print(f"  کاهش زمان بازیابی با پراکندگی جزئی (۲ شهر): {reduction_2:.1f}٪")
    print(f"  کاهش زمان بازیابی با پراکندگی کامل (۳ شهر، بند ۳.۶): {reduction_3:.1f}٪")
    print("  این تنها سناریویی از سه سناریو است که مکانیزم پیشنهادی سند")
    print("  به‌طور قابل‌توجه و بدون قید مؤثر ظاهر می‌شود - چون این مسئله")
    print("  ماهیتاً مهندسی/فیزیکی است، نه سیاسی/بازگشتی مثل دو سناریوی دیگر.")
    print("=" * 70)

    results = {
        "n_trials": N_TRIALS,
        "mean_recovery_days_per_component": MEAN_RECOVERY_DAYS_PER_COMPONENT,
        "mean_recovery_1_city": float(t1.mean()),
        "mean_recovery_2_cities": float(t2.mean()),
        "mean_recovery_3_cities": float(t3.mean()),
        "reduction_pct_2_cities": float(reduction_2),
        "reduction_pct_3_cities": float(reduction_3),
        "prob_under_7days_1city": float((t1 < 7).mean()),
        "prob_under_7days_3cities": float((t3 < 7).mean()),
        "seed": RNG_SEED,
    }
    with open("/home/claude/scenario3_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # نمودار
    apply_dark_theme()
    plt.rcParams['font.size'] = 12
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))

    axes[0].hist(t1, bins=40, alpha=0.65, color=RUST, label=_r("۱ شهر (بدون پراکندگی)"), density=True)
    axes[0].hist(t2, bins=40, alpha=0.65, color=BRASS, label=_r("۲ شهر (پراکندگی جزئی)"), density=True)
    axes[0].hist(t3, bins=40, alpha=0.65, color=GREEN, label=_r("۳ شهر (پراکندگی کامل)"), density=True)
    axes[0].set_xlabel(_r("زمان بازیابی کارکرد حداقلی (روز)"), color=INK)
    axes[0].set_ylabel(_r("چگالی احتمال"), color=INK)
    axes[0].set_title(_r("توزیع زمان بازیابی پس از زلزله"), color=INK, fontsize=13)
    axes[0].set_xlim(0, 120)
    axes[0].legend(fontsize=9)
    axes[0].grid(alpha=0.25)

    labels = [_r("۱ شهر\n(بدون پراکندگی)"), _r("۲ شهر\n(پراکندگی جزئی)"), _r("۳ شهر\n(بند ۳.۶)")]
    means = [t1.mean(), t2.mean(), t3.mean()]
    stds = [t1.std(), t2.std(), t3.std()]
    axes[1].bar(labels, means, yerr=stds, capsize=6, color=[RUST, BRASS, GREEN],
                error_kw={'ecolor': INK, 'alpha': 0.8})
    axes[1].set_ylabel(_r("میانگین زمان بازیابی (روز)"), color=INK)
    axes[1].set_title(_r("مقایسه‌ی میانگین زمان بازیابی"), color=INK, fontsize=13)
    axes[1].grid(axis="y", alpha=0.25)
    for i, m in enumerate(means):
        axes[1].text(i, m + stds[i] + 1, _r(f"{m:.1f} روز"), ha="center", fontweight="bold", color=INK)
    for ax in axes:
        for spine in ax.spines.values():
            spine.set_color("#c19a56")
            spine.set_alpha(0.3)

    plt.tight_layout()
    plt.savefig("scenario3_chart.png", dpi=150, facecolor="#1c1811")
    print("\nنمودار تیره ذخیره شد: scenario3_chart.png")
