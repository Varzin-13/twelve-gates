# شبیه‌سازی‌ها — راهنمای بازتولید و مرز ادعا

## وضعیت سناریوهای تاریخی ۱–۳

سه اسکریپت اولیه در مخزن حفظ شده‌اند:

| فایل تاریخی | وضعیت v0.32 |
|---|---|
| `scenario1_coalition_capture.py` | LEGACY — پارامترهای collusion/leverage فرضی و جهت مقایسه تا حد زیادی در ورودی‌ها تعبیه شده است |
| `scenario2_emergency_institutionalization.py` | LEGACY — approval=0.55 یک Bernoulli جمعی است، نه رأی صریح ۲/۳ |
| `scenario3_simultaneous_failure.py` | LEGACY — جهت کاهش recovery از ساختار 3→2→1 جزء آسیب‌دیده ناشی می‌شود |

عبارت‌های قدیمی داخل این فایل‌ها provenance تاریخی‌اند و نباید به‌عنوان
اعتبارسنجی تجربی یا پیش‌بینی سیاسی خوانده شوند.

ممیزی کامل:
[`docs/SCENARIO1_3_CLAIM_BOUNDARY_AUDIT_2026-10-01.md`](../docs/SCENARIO1_3_CLAIM_BOUNDARY_AUDIT_2026-10-01.md)

## نسخه‌های v2 روش‌شناختی

| فایل | نقش |
|---|---|
| `scenario1_coalition_capture_v2.py` | محاسبه‌ی تحلیلی پیامد همان فرض‌های collusion/leverage |
| `scenario2_emergency_persistence_v2.py` | sensitivity شرطی با برچسب صریح aggregate approval |
| `scenario3_redundancy_analytic_v2.py` | راه‌حل تحلیلی expected max برای recovery نمایی |

این فایل‌ها هم **کالیبراسیون یا اعتبارسنجی تجربی نیستند**.

## ABM اصلی v0.32

مدل اصلی و ممیزی‌های جدید در فایل‌های زیرند:

- `twelve_gates_model.py`
- `test_model.py`
- `calibration_registry.json`
- `parameter_usage_registry.json`
- `audit_schedule.py`
- runnerهای v0.32 و artifactهای `results/`

برای وضعیت علمی فعلی، README ریشه و اسناد `docs/` مرجع‌اند.

## اجرا

برای smoke test سناریوهای v2:

```bash
python scenario1_coalition_capture_v2.py
python scenario2_emergency_persistence_v2.py
python scenario3_redundancy_analytic_v2.py
```

برای مدل اصلی:

```bash
python test_model.py
python run_model.py --list-params
```

هیچ خروجی این پوشه نباید بدون mapping تجربی و validation به‌عنوان احتمال
واقعی یک نتیجه‌ی سیاسی تفسیر شود.
