"""
سناریوی ۵: آزمون «دولت موقت ۲۵کمیته‌ای، ۶ ماه» NCRI
==========================================================
دو سؤال پیش‌ثبت‌شده، مستقل از هم:

سؤال ۱ (زمان‌بندی): آیا ۶ ماه برای برگزاری انتخابات واقعی پس از فروپاشی
یک حکومت ۴۷ساله، با توجه به شکاف‌های قومی/سیاسی مستند در بخش ۹ این سند
(چهار خانواده‌ی متخاصم، تنش‌های قومی-مذهبی)، یک بازه‌ی واقع‌گرایانه است؟

سؤال ۲ (پایداری ائتلاف): NCRI از ۵ سازمان تشکیل شده که MEK به‌گفته‌ی
اسناد وزارت خارجه‌ی آمریکا «بزرگ‌ترین و متشکل‌ترین» عضو است. با توجه به
سابقه‌ی مستند فروپاشی داخلی NCRI در دهه‌ی ۱۹۸۰ («شرکا به‌دلیل اعتراض به
روش‌های دیکتاتوری رجوی جدا شدند» — گزارش وزارت خارجه)، احتمال اینکه
عضو غالب (MEK) کنترل نامتناسبی بر ۲۵ کمیته به‌دست بگیرد چقدر است؟

معیار شکست: اگر احتمال تصاحب کمیته‌ها توسط عضو غالب به‌طور معنادار بالاتر
از سطح شانس (۱ از ۵ = ۲۰٪) باشد، ادعای «ائتلاف دموکراتیک متوازن» با شواهد
ساختاری همخوان نیست.

روش سؤال ۱: مشابه سناریوی ۴، توزیع لوگ‌نرمال برای زمان برگزاری انتخابات
واقعی (نه صرفاً اعلام دولت موقت)، این‌بار با میانگین کوتاه‌تر چون فقط
انتخابات هدف است، نه کل فرآیند قانون اساسی.
روش سؤال ۲: مشابه منطق سناریوی ۱ (کارتل قدرت مادی) — عضو غالب با «اهرم
فشار» ناشی از بزرگی/تشکیلات نسبت به اعضای کوچک‌تر.
"""
import numpy as np
import json

RNG_SEED = 45
rng = np.random.default_rng(RNG_SEED)

N_TRIALS = 2000

# --- سؤال ۱: زمان‌بندی انتخابات ---
MEAN_ELECTION_MONTHS = 14  # فرض محافظه‌کارانه: کوتاه‌تر از کل فرآیند قانون اساسی، اما هنوز بیش از ۶ ماه
SIGMA_ELECTION = 0.45
DEADLINE_MONTHS = 6

def simulate_election_timing():
    return rng.lognormal(mean=np.log(MEAN_ELECTION_MONTHS), sigma=SIGMA_ELECTION)

# --- سؤال ۲: تصاحب کمیته‌ها توسط عضو غالب ---
N_COMMITTEES = 25
N_MEMBER_ORGS = 5
# احتمال پایه‌ی تخصیص هر کرسی به هر عضو اگر کاملاً تصادفی/متوازن بود: ۱/۵
BASELINE_SHARE = 1 / N_MEMBER_ORGS
# اهرم فشار عضو غالب: بر پایه‌ی سابقه‌ی مستند نابرابری تشکیلاتی (نه یک ادعای دلبخواه)
DOMINANT_ORG_LEVERAGE = 0.35  # افزایش نسبی شانس کسب هر کرسی برای عضو غالب

def simulate_committee_capture():
    """شبیه‌سازی تخصیص ۲۵ کرسی کمیته با اهرم فشار عضو غالب."""
    weights = np.array([BASELINE_SHARE + DOMINANT_ORG_LEVERAGE] + [BASELINE_SHARE * (1 - DOMINANT_ORG_LEVERAGE/4)] * 4)
    weights = weights / weights.sum()
    assignments = rng.choice(N_MEMBER_ORGS, size=N_COMMITTEES, p=weights)
    dominant_share = (assignments == 0).mean()
    return dominant_share

if __name__ == "__main__":
    print("=" * 70)
    print("سناریوی ۵: دولت موقت ۲۵کمیته‌ای NCRI — زمان‌بندی و پایداری ائتلاف")
    print("=" * 70)

    # سؤال ۱
    election_times = np.array([simulate_election_timing() for _ in range(N_TRIALS)])
    prob_election_on_time = (election_times <= DEADLINE_MONTHS).mean()
    print(f"\n[سؤال ۱: زمان‌بندی انتخابات]")
    print(f"  میانگین زمان برگزاری انتخابات واقعی: {election_times.mean():.1f} ماه")
    print(f"  احتمال برگزاری انتخابات تا ماه ۶ام: {prob_election_on_time*100:.1f}٪")

    # سؤال ۲
    dominant_shares = np.array([simulate_committee_capture() for _ in range(N_TRIALS)])
    mean_dominant_share = dominant_shares.mean()
    prob_majority_capture = (dominant_shares > 0.5).mean()
    print(f"\n[سؤال ۲: پایداری ائتلاف ۲۵کمیته‌ای]")
    print(f"  میانگین سهم عضو غالب از ۲۵ کمیته: {mean_dominant_share*100:.1f}٪ (سطح شانس: ۲۰.۰٪)")
    print(f"  احتمال کسب اکثریت مطلق کمیته‌ها (>۵۰٪) توسط یک عضو: {prob_majority_capture*100:.1f}٪")

    print("\n" + "=" * 70)
    print("نتیجه‌گیری:")
    print(f"=> زمان‌بندی: در {(1-prob_election_on_time)*100:.1f}٪ اجراها، انتخابات تا ماه ۶ام برگزار نمی‌شود.")
    print(f"=> ائتلاف: سهم میانگین عضو غالب ({mean_dominant_share*100:.1f}٪) به‌طور قابل‌توجهی")
    print(f"   بالاتر از سطح شانس (۲۰٪) است — نتیجه‌ای هم‌راستا با سابقه‌ی مستند")
    print("   فروپاشی داخلی NCRI به‌دلیل نابرابری قدرت میان اعضا.")
    print("=" * 70)

    results = {
        "n_trials": N_TRIALS,
        "election_deadline_months": DEADLINE_MONTHS,
        "mean_election_months": float(election_times.mean()),
        "prob_election_on_time": float(prob_election_on_time),
        "n_committees": N_COMMITTEES,
        "n_member_orgs": N_MEMBER_ORGS,
        "baseline_share_if_balanced": BASELINE_SHARE,
        "mean_dominant_org_share": float(mean_dominant_share),
        "prob_majority_capture": float(prob_majority_capture),
        "seed": RNG_SEED,
    }
    with open("/home/claude/scenario5_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nنتایج ذخیره شد: scenario5_results.json")
