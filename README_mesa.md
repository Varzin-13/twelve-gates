# مدل دوازده‌گیت — راهنمای اجرا

## نصب و اجرای سریع
```bash
pip install numpy --break-system-packages
python3 test_model.py                    # اجرای regression suite فعلی
python3 run_model.py --list-params       # جدول منبع/وضعیت هر پارامتر
python3 run_model.py --config baseline_config.json --n-runs 300 \
    --shock security,energy,economy --shock-magnitude 0.02 --out results.json
```

## فایل‌ها
| فایل | نقش |
|---|---|
| `twelve_gates_model.py` | هسته‌ی مدل — کلاس‌ها، ۱۱ استیج، منطق چرخش/ائتلاف/کارتل |
| `run_model.py` | رابط خط‌فرمان — اعتبارسنجی config، اعمال شوک، اجرای دسته‌ای |
| `param_provenance.py` | جدول شفاف: کدام پارامتر از سند، کدام دلبخواه |
| `test_model.py` | regression suite فعال — تعداد تست‌ها در CI گزارش می‌شود و ثابت فرض نمی‌شود |
| `baseline_config.json` | نمونه کانفیگ قابل‌ویرایش (بدون دستکاری کد پایتون) |
| `sensitivity_analysis.py` | تحلیل حساسیت سه پارامتر کلیدی |

## دو باگ واقعی که در ساخت همین ابزار پیدا و رفع شد
۱. منطق به‌روزرسانی اعتماد اشتباه محاسبه می‌شد (چک خودارجاع نادرست) — اعتماد را مصنوعاً به صفر می‌رساند.
۲. JSON کلیدهای عددی دیکشنری (trust_row) را به رشته تبدیل می‌کند — بدون `normalize_config()`،
   هر بار config از فایل خوانده شود، مقادیر واقعی trust/affinity گم و به پیش‌فرض سقوط می‌کنند.

## مرز صداقت — چیزی که این ابزار *نیست*
این CLI مدل را **قابل‌اجرا و قابل‌پیکربندی** می‌کند، **نه قابل‌اتکا برای پیش‌بینی واقعی**.
طبق `param_provenance.py` و `calibration_registry.json`، اکثریت پارامترهای مؤثر هنوز
غیرکالیبره‌اند و در رجیستری فعلی هیچ mapping تجربی پذیرفته نشده است. هر خروجی باید با
claim boundary خودش خوانده شود — نه به‌عنوان پیش‌بینی، بلکه پیامد یک مجموعه فرض مشخص.

برای وضعیت به‌روز v0.32 به README ریشه، `docs/SCIENTIFIC_EXECUTION_AUDIT_2026-09-30.md`
و `docs/ABM_V2_ODD_SPEC.md` مراجعه شود.
