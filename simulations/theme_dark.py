"""
theme_dark.py — تم تیره‌ی دقیقاً منطبق با توکن‌های CSS خودِ سایت
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

BG_SOFT = "#1c1811"
SURFACE_STRONG = "#241f16"
INK = "#f3ead9"
MUTED = "#ab9c7c"
FAINT = "#756a52"
LINE = "#c19a56"
BRASS = "#c9a35f"
VERDIGRIS = "#7f9b8a"
GREEN = "#83a374"
RUST = "#c06248"

_FONT_CANDIDATES = [
    '/usr/share/fonts/truetype/freefont/FreeSerif.ttf',
    '/usr/share/fonts/TTF/FreeSerif.ttf',
    '/opt/homebrew/share/fonts/FreeSerif.ttf',
]

def apply_dark_theme():
    for fp in _FONT_CANDIDATES:
        if os.path.exists(fp):
            fm.fontManager.addfont(fp)
            plt.rcParams['font.family'] = fm.FontProperties(fname=fp).get_name()
            break
    plt.rcParams.update({
        'figure.facecolor': BG_SOFT,
        'axes.facecolor': BG_SOFT,
        'savefig.facecolor': BG_SOFT,
        'axes.edgecolor': LINE,
        'axes.labelcolor': INK,
        'xtick.color': MUTED,
        'ytick.color': MUTED,
        'text.color': INK,
        'grid.color': LINE,
        'grid.alpha': 0.25,
        'legend.facecolor': SURFACE_STRONG,
        'legend.edgecolor': LINE,
        'legend.labelcolor': INK,
        'axes.grid': True,
        'axes.axisbelow': True,
        'font.size': 12,
    })
