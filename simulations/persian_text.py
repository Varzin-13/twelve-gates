"""
persian_text.py
================
matplotlib هیچ موتور شکل‌دهی متن (text shaping) و الگوریتم دوجهته
(bidi) ندارد -- فقط هر کاراکتر را به‌ترتیبِ رشته، چپ‌به‌راست می‌چیند.
برای همین متن فارسی خام در نمودارهای matplotlib به‌شکل جدا از‌هم و
در جهت اشتباه نمایش داده می‌شود.

این ماژول دو کار می‌کند:
۱) Shaping: هر حرف فارسی را بر اساس همسایه‌های منطقی‌اش به فرم درست
   (ایزوله/آغازین/میانی/پایانی) از یونیکد Presentation Forms تبدیل
   می‌کند - این جدول با پارس کردن نام رسمی کاراکترهای یونیکد ساخته
   شده، نه از حافظه، تا خطای انسانی نداشته باشد.
۲) Bidi ساده‌شده: ترتیب واحدهای متن (اجزای فارسی، اجزای عددی، و
   کاراکترهای منفرد) را برای نمایش صحیح راست‌به‌چپ معکوس می‌کند - با
   حفظ ترتیب داخلی اعداد (که نباید معکوس شوند) و آینه‌کردن پرانتزها.

استفاده: reshape(text) -> رشته‌ی آماده برای پاس‌دادن به matplotlib
"""

import unicodedata

# ---------------------------------------------------------------
# ساخت خودکار جدول presentation forms با پارس نام یونیکد کاراکترها
# ---------------------------------------------------------------
_FORM_TABLE = {}
for _cp in list(range(0xFB50, 0xFE00)) + list(range(0xFE70, 0xFF00)):
    try:
        _name = unicodedata.name(chr(_cp))
    except ValueError:
        continue
    if not _name.startswith("ARABIC LETTER"):
        continue
    for _form in ("ISOLATED FORM", "INITIAL FORM", "MEDIAL FORM", "FINAL FORM"):
        if _name.endswith(_form):
            _base = _name[len("ARABIC LETTER "):-len(" " + _form)]
            _key = _form.split()[0].lower()
            _FORM_TABLE.setdefault(_base, {})[_key] = _cp
            break

_PERSIAN_LETTER_NAMES = {
    'ا': 'ALEF', 'ب': 'BEH', 'پ': 'PEH', 'ت': 'TEH', 'ث': 'THEH', 'ج': 'JEEM',
    'چ': 'TCHEH', 'ح': 'HAH', 'خ': 'KHAH', 'د': 'DAL', 'ذ': 'THAL', 'ر': 'REH',
    'ز': 'ZAIN', 'ژ': 'JEH', 'س': 'SEEN', 'ش': 'SHEEN', 'ص': 'SAD', 'ض': 'DAD',
    'ط': 'TAH', 'ظ': 'ZAH', 'ع': 'AIN', 'غ': 'GHAIN', 'ف': 'FEH', 'ق': 'QAF',
    'ک': 'KEHEH', 'گ': 'GAF', 'ل': 'LAM', 'م': 'MEEM', 'ن': 'NOON', 'ه': 'HEH',
    'و': 'WAW', 'ی': 'FARSI YEH',
    # چند حرف عربی رایج که ممکن است به‌جای معادل فارسی‌شان تایپ شوند
    'ي': 'FARSI YEH', 'ك': 'KEHEH',
}

LETTER_FORMS = {}      # ch -> {'isolated':cp, 'initial':cp, 'medial':cp, 'final':cp}
DUAL_JOINERS = set()   # حروفی که هم به قبل هم به بعد متصل می‌شوند
RIGHT_JOINERS = set()  # حروفی که فقط از قبل متصل می‌شوند (ا د ذ ر ز ژ و)

for ch, name in _PERSIAN_LETTER_NAMES.items():
    forms = _FORM_TABLE.get(name)
    if not forms:
        continue
    LETTER_FORMS[ch] = forms
    if 'initial' in forms:
        DUAL_JOINERS.add(ch)
    else:
        RIGHT_JOINERS.add(ch)

ARABIC_LETTERS = set(LETTER_FORMS.keys())
ZWNJ = '\u200c'

DIGIT_CHARS = set('0123456789') | set('۰۱۲۳۴۵۶۷۸۹') | set('٠١٢٣٤٥٦٧٨٩') | set('.,٪%')
MIRROR_MAP = {'(': ')', ')': '(', '[': ']', ']': '[', '{': '}', '}': '{'}


def _shape_run(run):
    """یک رشته‌ی پشت‌سرهم از حروف فارسی/عربی (+ZWNJ) را بر اساس
    همسایگی منطقی به فرم درست تبدیل می‌کند و ZWNJ را حذف می‌کند."""
    letters = [c for c in run if c != ZWNJ]
    # موقعیت هر حرف در رشته‌ی اصلی (شامل ZWNJ) لازم است تا بفهمیم
    # مسدودکننده‌ی اتصال بین دو حرف وجود دارد یا نه
    out = []
    n = len(run)
    # ایندکس حروف واقعی (غیر ZWNJ) در رشته‌ی اصلی
    real_positions = [i for i, c in enumerate(run) if c != ZWNJ]
    for idx, pos in enumerate(real_positions):
        ch = run[pos]
        # آیا حرف قبلی (در رشته‌ی اصلی) بدون فاصله متصل می‌شود؟
        prev_connects = False
        if idx > 0:
            prev_pos = real_positions[idx - 1]
            prev_ch = run[prev_pos]
            # اگر بین این دو حرف واقعی چیزی جز خودشان نیست (یعنی
            # مستقیماً پشت‌سرهم‌اند، بدون ZWNJ فاصل) و حرف قبلی dual است
            directly_adjacent = (prev_pos == pos - 1)
            if directly_adjacent and prev_ch in DUAL_JOINERS:
                prev_connects = True
        next_connects = False
        if ch in DUAL_JOINERS and idx < len(real_positions) - 1:
            next_pos = real_positions[idx + 1]
            if next_pos == pos + 1:
                next_connects = True

        forms = LETTER_FORMS[ch]
        if prev_connects and next_connects and 'medial' in forms:
            out.append(chr(forms['medial']))
        elif prev_connects and 'final' in forms:
            out.append(chr(forms['final']))
        elif next_connects and 'initial' in forms:
            out.append(chr(forms['initial']))
        else:
            out.append(chr(forms['isolated']))
    return out  # لیست گلیف‌های شکل‌گرفته، هنوز به ترتیب منطقی (معکوس نشده)


def _classify(ch):
    if ch in ARABIC_LETTERS or ch == ZWNJ:
        return 'arabic'
    if ch in DIGIT_CHARS:
        return 'digit'
    if ch.isascii() and ch.isalpha():
        return 'latin'   # کلمات لاتین هم مثل اعداد نباید داخلشان معکوس شود
    return 'other'


def reshape_line(line):
    """یک خط (بدون \\n) را برای نمایش صحیح در matplotlib آماده می‌کند."""
    if not line:
        return line
    # اگر خط هیچ حرف فارسی/عربی ندارد، دست‌نخورده برگردان
    if not any(_classify(c) == 'arabic' for c in line):
        return line

    # ۱) شکستن خط به run های همگن (arabic / digit / other-تک‌کاراکتری)
    runs = []  # هر عنصر: (نوع, رشته‌ی خام)
    cur_type = None
    cur_chars = []
    for ch in line:
        t = _classify(ch)
        if t == 'other':
            if cur_chars:
                runs.append((cur_type, ''.join(cur_chars)))
                cur_chars = []
                cur_type = None
            runs.append(('other', ch))
            continue
        if t == cur_type:
            cur_chars.append(ch)
        else:
            if cur_chars:
                runs.append((cur_type, ''.join(cur_chars)))
            cur_chars = [ch]
            cur_type = t
    if cur_chars:
        runs.append((cur_type, ''.join(cur_chars)))

    # ۲) shape کردن run های عربی (هنوز به ترتیب منطقی)
    processed = []
    for t, s in runs:
        if t == 'arabic':
            processed.append((t, _shape_run(s)))  # لیست گلیف
        else:
            processed.append((t, s))

    # ۳) معکوس‌کردن ترتیب run ها + رفتار مخصوص هر نوع هنگام خروجی
    out_parts = []
    for t, s in reversed(processed):
        if t == 'arabic':
            out_parts.append(''.join(reversed(s)))  # خود گلیف‌ها هم معکوس
        elif t in ('digit', 'latin'):
            out_parts.append(s)  # عدد یا کلمه‌ی لاتین دست‌نخورده
        else:  # other: تک‌کاراکتر، اگر آینه‌ای دارد جایگزین کن
            out_parts.append(MIRROR_MAP.get(s, s))
    return ''.join(out_parts)


def reshape(text):
    """ورودی چندخطی (با \\n) را خط‌به‌خط پردازش می‌کند."""
    return '\n'.join(reshape_line(ln) for ln in text.split('\n'))


if __name__ == "__main__":
    tests = [
        "کارتل امنیت-انرژی-اقتصاد",
        "نرخ تصاحب تصمیمات کلیدی",
        "بدون مکانیزم\nکاهش‌دهنده",
        "با مرجع قضایی مستقل",
        "زلزله‌ی بزرگ تهران",
        "آستانه‌ی هشدار (۸۰٪)",
        "76.0٪",
        "39.4 روز",
        "۱ شهر\n(بدون پراکندگی)",
        "سناریوی ۱ — نرخ تصاحب تصمیمات: کارتل ساختاری در برابر سطح شانس",
    ]
    for t in tests:
        print(repr(t), "->", repr(reshape(t)))
