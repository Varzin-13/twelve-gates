"""
param_provenance.py
====================
جدول منبع/وضعیت هر پارامتر مدل — پاسخ دائمی و قابل‌پرس‌وجو به «این عدد از کجا اومده؟»
هر پارامتر یکی از این برچسب‌ها را دارد:
  DOCUMENT   = مستقیماً از متن سند می‌آید (عدد سخت، نه تفسیر)
  DESIGN     = تصمیم طراحی مهندسی‌شده، مستند در spec، ولی نه از سند اصلی
  ARBITRARY  = انتخاب سناریویی بدون هیچ داده‌ی پشتیبان — نیازمند کالیبراسیون واقعی
"""

PARAM_PROVENANCE = {
    "resource_share (baseline 1/12)": {
        "label": "DOCUMENT", "source": "بند ۱.۴ — تنها پیشنهاد صریح سند برای تخصیص اولیه"},
    "emergency_fuse_ticks = 2 (=۱۴ روز)": {
        "label": "DOCUMENT", "source": "بند ۳.۲ — تنها عدد زمانی سخت کل سند"},
    "rotation formula P_t=(5t)mod12, A_t=(P_t+6)mod12": {
        "label": "DOCUMENT", "source": "بند ۴.۲ — فرمول دقیق و اثبات‌شده"},
    "annual_delta_cap = 0.15": {
        "label": "DOCUMENT", "source": "بند ۱.۴ — سقف صریح تغییر بودجه"},
    "budget_reallocation = qualified_majority (۲/۳)": {
        "label": "DESIGN", "source": "بند ۳.۱.۱ — 'مهندسی‌شده، نه اثبات‌شده' به تصریح خودِ سند"},
    "cross_verification threshold (≥۲ گیت مستقل)": {
        "label": "DOCUMENT", "source": "بند ۶.۱ — قاعده‌ی صریح لایه‌ی بیزانسی"},
    "geo_redundancy مرجع (۳ شهر)": {
        "label": "DOCUMENT", "source": "بند ۳.۶/۶.۴ — الزام صریح پراکندگی جغرافیایی"},
    "theta_pair (آستانه‌ی تشکیل ائتلاف) = 0.55": {
        "label": "ARBITRARY", "source": "بدون داده؛ تحلیل حساسیت نشان داد نتیجه در ۰.۶۰-۰.۶۵ کاملاً معکوس می‌شود"},
    "coalition weights (w1..w5)": {
        "label": "ARBITRARY", "source": "بدون داده؛ فقط نسبتاً کم‌حساس در تحلیل حساسیت"},
    "exec_power اولیه‌ی هر گیت": {
        "label": "ARBITRARY", "source": "بدون داده؛ تحلیل حساسیت نشان داد این مهم‌ترین محرک نتیجه‌ی کارتل است"},
    "trust_row / affinity_row / overlap_row اولیه": {
        "label": "ARBITRARY", "source": "بند ۹.۳/۱۰.۳ — ماتریس واقعی هرگز کالیبره نشده"},
    "info_reliability = 0.95": {
        "label": "ARBITRARY", "source": "فرض دلبخواه صداقت گزارش‌دهی"},
    "verification_accuracy = 0.8": {
        "label": "ARBITRARY", "source": "فرض دلبخواه دقت راستی‌آزمایی"},
    "cartel: K_min/theta_power/M_consecutive": {
        "label": "DESIGN", "source": "عملیاتی‌سازی مستقیم بند ۳.۵/۳.۶، ولی آستانه‌های عددی‌اش دلبخواه"},
    "emergency_court.independence_mode": {
        "label": "ARBITRARY", "source": "بند ۳.۶ فقط 'مرجع مستقل' می‌گوید؛ ترکیب/رفتار حل‌نشده — PLACEHOLDER صریح"},
    "gate_zero.appeal_board = random_placeholder": {
        "label": "ARBITRARY", "source": "بند ۱.۴/۳.۱ — بازگشتی حل‌نشده، PLACEHOLDER صریح در کد"},
    "rotation_period_ticks = 26": {
        "label": "ARBITRARY", "source": "سند مدت واقعی دوره‌ی چرخش را مشخص نکرده — dependency حل‌نشده"},
    "coordination_capacity precondition threshold": {
        "label": "DESIGN", "source": "بند ۱۰.۶.۷ — اصل مفهومی مستند، آستانه‌ی عددی‌اش دلبخواه"},
}

def print_provenance_table():
    labels_order = {"DOCUMENT": "🟢 از سند", "DESIGN": "🟡 طراحی مهندسی‌شده", "ARBITRARY": "🔴 دلبخواه/غیرکالیبره"}
    print(f"{'پارامتر':50s} {'برچسب':22s} منبع")
    print("-" * 110)
    for lbl_key, lbl_name in labels_order.items():
        for name, info in PARAM_PROVENANCE.items():
            if info["label"] == lbl_key:
                print(f"{name:50s} {lbl_name:22s} {info['source']}")
    n_doc = sum(1 for v in PARAM_PROVENANCE.values() if v["label"] == "DOCUMENT")
    n_des = sum(1 for v in PARAM_PROVENANCE.values() if v["label"] == "DESIGN")
    n_arb = sum(1 for v in PARAM_PROVENANCE.values() if v["label"] == "ARBITRARY")
    print("-" * 110)
    print(f"جمع: {n_doc} از سند · {n_des} طراحی مهندسی‌شده · {n_arb} دلبخواه/غیرکالیبره "
          f"(از مجموع {len(PARAM_PROVENANCE)})")
    print(f"\n⚠ نتیجه: اکثریت پارامترهای مؤثر بر نتیجه هنوز ARBITRARY هستند — این خودِ دلیل ماندن")
    print(f"  برچسب مدل در 🟡 فرضیه (نه 🟢) است، مستقل از اینکه کد چقدر درست اجرا شود.")

if __name__ == "__main__":
    print_provenance_table()
