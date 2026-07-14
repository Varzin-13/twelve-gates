"""
سناریوی ۲: آزمون نهادینه‌شدن اضطرار در جنگ فرسایشی
==========================================================
سؤال پیش‌ثبت‌شده:
در یک جنگ فرسایشی طولانی‌مدت (نه یک بحران کوتاه)، آیا فیوز ۱۴روزه +
تأیید مرجع قضایی مستقل (پیشنهاد بند ۳.۶) از تبدیل‌شدن اضطرار به
یک «وضعیت استثنایی دائمی با ظاهر قانونی» جلوگیری می‌کند؟

معیار شکست (پیش‌ثبت‌شده):
درصد کل زمان شبیه‌سازی که سیستم در حالت اضطراری فعال است.
اگر این عدد در طول جنگ طولانی به بالای ۸۰٪ برسد و عملاً هرگز به
حالت عادی بازنگردد، فرضیه‌ی «فیوز مؤثر است» رد می‌شود.

فرض‌های کلیدی مدل (باید همیشه در کنار نتایج خوانده شوند):
- جنگ با احتمال ثابت هر دوره ادامه می‌یابد یا پایان می‌یابد (فرض
  ساده‌شده - جنگ‌های واقعی رفتار پیچیده‌تری دارند)
- «فشار جوی روانی بحران» به‌صورت یک متغیر افزایشی مدل شده که
  احتمال تصویب تمدید را در هر چرخه بالا می‌برد (پایه‌ی این فرض:
  ادبیات روان‌شناسی سیاسی درباره‌ی افزایش تحمل جامعه برای تمرکز
  قدرت در بحران‌های طولانی - نه داده‌ی مستقیم درباره‌ی ایران)
- مرجع قضایی مستقل یک احتمال رد ثابت دارد که مستقل از فشار جوی
  بحران فرض شده (خوش‌بینانه‌ترین فرض ممکن برای این مکانیزم)
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

RNG_SEED = 7
rng = np.random.default_rng(RNG_SEED)

CYCLE_DAYS = 14
N_CYCLES = 60            # حدود ۲.۳ سال جنگ فرسایشی
N_TRIALS = 500

WAR_CONTINUATION_PROB = 0.93   # احتمال ادامه‌ی جنگ در هر چرخه (میانگین طول جنگ ~14 چرخه = ~6 ماه تا چند سال، با پراکندگی)
BASE_EXTENSION_APPROVAL = 0.55  # احتمال پایه‌ی تصویب تمدید توسط ۲/۳ گیت‌های غیردرگیر
PRESSURE_GROWTH_PER_CYCLE = 0.025  # افزایش فشار روانی بحران در هر چرخه‌ی متوالی اضطرار
JUDICIAL_REJECT_PROB = 0.30    # احتمال ثابت رد تمدید توسط مرجع قضایی مستقل (مکانیزم بند ۳.۶)


def simulate_trial(with_judicial_check, n_cycles=N_CYCLES):
    """یک اجرای کامل: دنباله‌ای از چرخه‌های ۱۴روزه در طول یک جنگ فرضی.

    معیار خروجی: نسبت «چرخه‌های اضطراری» به «چرخه‌هایی که جنگ واقعاً
    فعال بود» - نه به کل طول شبیه‌سازی. نسخه‌ی اول این مدل مخرج را
    اشتباه با کل دوره (شامل صلح پس از پایان جنگ) محاسبه می‌کرد که
    نتیجه را به‌طور مصنوعی خوش‌بینانه نشان می‌داد.
    """
    emergency_active = False
    consecutive_emergency_cycles = 0
    emergency_cycle_count = 0
    war_active_cycle_count = 0
    war_active = True

    for cycle in range(n_cycles):
        if not war_active:
            emergency_active = False
            consecutive_emergency_cycles = 0
            continue

        war_active_cycle_count += 1

        if not emergency_active:
            emergency_active = True
            consecutive_emergency_cycles = 1
        else:
            pressure_bonus = min(consecutive_emergency_cycles * PRESSURE_GROWTH_PER_CYCLE, 0.40)
            approval_prob = min(BASE_EXTENSION_APPROVAL + pressure_bonus, 0.98)
            extension_voted = rng.random() < approval_prob

            if with_judicial_check and extension_voted:
                judicial_rejects = rng.random() < JUDICIAL_REJECT_PROB
                extension_voted = extension_voted and not judicial_rejects

            if extension_voted:
                consecutive_emergency_cycles += 1
            else:
                emergency_active = False
                consecutive_emergency_cycles = 0

        if emergency_active:
            emergency_cycle_count += 1

        war_active = rng.random() < WAR_CONTINUATION_PROB

    if war_active_cycle_count == 0:
        return 0.0
    return emergency_cycle_count / war_active_cycle_count


def run_condition(with_judicial_check, label):
    rates = np.array([simulate_trial(with_judicial_check) for _ in range(N_TRIALS)])
    print(f"\n[{label}]")
    print(f"  درصد زمان در حالت اضطراری: میانگین={rates.mean()*100:.1f}٪  "
          f"(میانه={np.median(rates)*100:.1f}٪, انحراف معیار={rates.std()*100:.1f}٪)")
    print(f"  درصد اجراهایی که >۸۰٪ زمان در اضطرار ماندند: "
          f"{(rates > 0.8).mean()*100:.1f}٪")
    return rates


if __name__ == "__main__":
    print("=" * 70)
    print("سناریوی ۲: نهادینه‌شدن اضطرار در جنگ فرسایشی")
    print("=" * 70)

    without_judicial = run_condition(False, "فقط فیوز ۱۴روزه + رأی ۲/۳ (بدون مرجع قضایی مستقل)")
    with_judicial = run_condition(True, "فیوز ۱۴روزه + رأی ۲/۳ + مرجع قضایی مستقل (بند ۳.۶)")

    reduction_pct = (1 - with_judicial.mean() / without_judicial.mean()) * 100

    print("\n" + "=" * 70)
    print("نتیجه‌گیری:")
    print(f"  کاهش زمان اضطراری با افزودن مرجع قضایی مستقل: {reduction_pct:.1f}٪")
    if with_judicial.mean() > 0.5:
        print("  => حتی با بهترین حالت مکانیزم (احتمال رد ثابت و مستقل از فشار")
        print("     روانی بحران)، سیستم در بیش از نیمی از طول جنگ فرسایشی")
        print("     در حالت اضطراری باقی می‌ماند. این نگرانی بند ۳.۶ سند را")
        print("     ('نهادینه‌شدن اضطرار') با عدد تأیید می‌کند.")
    else:
        print("  => مرجع قضایی مستقل زمان اضطراری را به زیر ۵۰٪ کاهش داد.")
    print("=" * 70)

    results = {
        "n_cycles": N_CYCLES,
        "n_trials": N_TRIALS,
        "war_continuation_prob": WAR_CONTINUATION_PROB,
        "base_extension_approval": BASE_EXTENSION_APPROVAL,
        "pressure_growth_per_cycle": PRESSURE_GROWTH_PER_CYCLE,
        "judicial_reject_prob": JUDICIAL_REJECT_PROB,
        "without_judicial_mean": float(without_judicial.mean()),
        "with_judicial_mean": float(with_judicial.mean()),
        "reduction_pct": float(reduction_pct),
        "pct_trials_over_80pct_without_judicial": float((without_judicial > 0.8).mean()),
        "pct_trials_over_80pct_with_judicial": float((with_judicial > 0.8).mean()),
        "seed": RNG_SEED,
    }
    with open("/home/claude/scenario2_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # نمودار
    apply_dark_theme()
    plt.rcParams['font.size'] = 12
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))

    axes[0].hist(without_judicial * 100, bins=25, alpha=0.75, color=RUST,
                 label=_r("بدون مرجع قضایی مستقل"))
    axes[0].hist(with_judicial * 100, bins=25, alpha=0.75, color=GREEN,
                 label=_r("با مرجع قضایی مستقل"))
    axes[0].axvline(80, color=INK, linestyle="--", linewidth=1, alpha=0.7, label=_r("آستانه‌ی هشدار (۸۰٪)"))
    axes[0].set_xlabel(_r("درصد کل زمان جنگ در حالت اضطراری"), color=INK)
    axes[0].set_ylabel(_r("تعداد اجراهای شبیه‌سازی"), color=INK)
    axes[0].set_title(_r("توزیع درصد زمان اضطراری در ۵۰۰ اجرا"), color=INK, fontsize=13)
    axes[0].legend(fontsize=9)
    axes[0].grid(alpha=0.25)

    labels = [_r("بدون مرجع\nقضایی مستقل"), _r("با مرجع\nقضایی مستقل")]
    means = [without_judicial.mean() * 100, with_judicial.mean() * 100]
    axes[1].bar(labels, means, color=[RUST, GREEN])
    axes[1].axhline(80, color=INK, linestyle="--", linewidth=1, alpha=0.7)
    axes[1].axhline(50, color=MUTED, linestyle=":", linewidth=1, alpha=0.7)
    axes[1].set_ylabel(_r("میانگین درصد زمان در حالت اضطراری"), color=INK)
    axes[1].set_title(_r("مقایسه‌ی میانگین"), color=INK, fontsize=13)
    axes[1].set_ylim(0, 100)
    axes[1].grid(axis="y", alpha=0.25)
    for i, m in enumerate(means):
        axes[1].text(i, m + 2, f"{m:.1f}٪", ha="center", fontweight="bold", color=INK)
    for ax in axes:
        for spine in ax.spines.values():
            spine.set_color("#c19a56")
            spine.set_alpha(0.3)

    plt.tight_layout()
    plt.savefig("scenario2_chart.png", dpi=150, facecolor="#1c1811")
    print("\nنمودار تیره ذخیره شد: scenario2_chart.png")
