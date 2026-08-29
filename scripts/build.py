"""把 JetBrains Mono NL 缩到半个汉字宽，覆盖到更纱 Fixed SC 的西文/盒绘上。"""

from __future__ import annotations

import copy
import json
import shutil
import unicodedata
from functools import cache
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple
from fontTools.ttLib.tables.ttProgram import Program

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor"
DIST = ROOT / "dist"
PREVIEW_HTML = ROOT / "preview" / "preview.html"

SARASA = VENDOR / "sarasa-fixed-sc" / "SarasaFixedSC-Regular.ttf"
JBM = VENDOR / "jetbrains-mono" / "fonts" / "ttf" / "JetBrainsMonoNL-Regular.ttf"
JBM_OFL = VENDOR / "jetbrains-mono" / "OFL.txt"

# 规范 §6：配套表情字体，不并入 Regular；Regular 剔除 Emoji_Presentation
NOTO_EMOJI = VENDOR / "noto-emoji" / "Noto-COLRv1.ttf"
NOTO_EMOJI_OFL = VENDOR / "noto-emoji" / "LICENSE"
FLUENT_EMOJI = VENDOR / "fluent-emoji" / "FluentEmojiColor.ttf"
FLUENT_MIT_MS = VENDOR / "fluent-emoji" / "LICENSE-Microsoft.txt"
FLUENT_MIT_BUILD = VENDOR / "fluent-emoji" / "LICENSE-tetunori.txt"

EMOJI_VARIANTS = (
    {
        "src": NOTO_EMOJI,
        "family_en": "Xiaoheizi Emoji",
        "family_zh": "小黑字表情",
        "ps": "XiaoheiziEmoji-Regular",
        "full_en": "Xiaoheizi Emoji Regular",
        "out_name": "XiaoheiziEmoji-Regular.ttf",
        "preview_name": "preview-emoji.ttf",
        "copyright": "Copyright 2026 小黑字. Portions: Google LLC / Noto Emoji authors. SIL OFL 1.1.",
        "license_notice": "This Font Software is licensed under the SIL Open Font License, Version 1.1. https://openfontlicense.org",
    },
    {
        "src": FLUENT_EMOJI,
        "family_en": "Xiaoheizi Emoji MS",
        "family_zh": "小黑字表情微软",
        "ps": "XiaoheiziEmojiMS-Regular",
        "full_en": "Xiaoheizi Emoji MS Regular",
        "out_name": "XiaoheiziEmojiMS-Regular.ttf",
        "preview_name": "preview-emoji-ms.ttf",
        "copyright": "Copyright 2026 小黑字. Artwork: Microsoft Fluent Emoji (MIT). Font compilation portions: tetunori/fluent-emoji-webfont (MIT).",
        "license_notice": "Font names under SIL OFL 1.1. Fluent Emoji artwork under MIT. See dist/FluentEmoji-MIT-Microsoft.txt.",
    },
)

# 规范 §3：西文与盒绘走 JetBrains Mono
JBM_RANGES = (
    (0x0000, 0x007F),
    (0x00A0, 0x024F),
    (0x0370, 0x03FF),
    (0x0400, 0x04FF),
    (0x2000, 0x206F),
    (0x2190, 0x21FF),
    (0x2500, 0x259F),
)

REQUIRED_BLOCKS = (
    ("Basic Latin", 0x0000, 0x007F),
    ("Box Drawing", 0x2500, 0x257F),
    ("Block Elements", 0x2580, 0x259F),
    ("CJK Unified Ideographs", 0x4E00, 0x9FFF),
    ("CJK Symbols and Punctuation", 0x3000, 0x303F),
    ("Halfwidth and Fullwidth Forms", 0xFF00, 0xFFEF),
)

# 名称里的 em：按排版长度（1.0 = 一个汉字宽），不压成 UAX #11 的半格
NAMED_EM_RATIO = {
    0x2000: 0.5,       # EN QUAD
    0x2001: 1.0,       # EM QUAD
    0x2002: 0.5,       # EN SPACE
    0x2003: 1.0,       # EM SPACE
    0x2004: 1 / 3,     # THREE-PER-EM SPACE
    0x2005: 1 / 4,     # FOUR-PER-EM SPACE
    0x2006: 1 / 6,     # SIX-PER-EM SPACE
    0x2009: 1 / 5,     # THIN SPACE
    0x200A: 1 / 10,    # HAIR SPACE
    0x2013: 0.5,       # EN DASH
    0x2014: 1.0,       # EM DASH
    0x2E3A: 2.0,       # TWO-EM DASH
    0x2E3B: 3.0,       # THREE-EM DASH
}

SCALE = 500 / 600  # JBM 0.6em → 半个汉字
PREFIX = "jbm."
BMP_DENOM = 65535  # 规范 §4.2：BMP 习惯分母（U+0000–U+FFFF）
FAMILY_EN = "Xiaoheizi Mono"
FAMILY_ZH = "小黑字等宽"
FULL_EN = "Xiaoheizi Mono Regular"
PS_NAME = "XiaoheiziMono-Regular"
TARGET_UPEM = 1000  # Regular 与配套表情同一 em；1 em = 2 格

# 表情序列用到的零宽/组合码位，本身不是「一幅图」，但 cmap 里要留着才能拼 ZWJ / 键帽。
EMOJI_SEQUENCE_CPS = frozenset({0x200D, 0xFE0E, 0xFE0F, 0x20E3})

# Unicode Emoji_Presentation。Regular 从 cmap 剔除，避免挡住配套彩色表情。
# 不含 ⚠★❤☀✓✔ 等默认文本表现字符。
EMOJI_PRESENTATION_RANGES = (
    (0x231A, 0x231B),
    (0x23E9, 0x23EC),
    (0x23F0, 0x23F0),
    (0x23F3, 0x23F3),
    (0x25FD, 0x25FE),
    (0x2614, 0x2615),
    (0x2648, 0x2653),
    (0x267F, 0x267F),
    (0x2693, 0x2693),
    (0x26A1, 0x26A1),
    (0x26AA, 0x26AB),
    (0x26BD, 0x26BE),
    (0x26C4, 0x26C5),
    (0x26CE, 0x26CE),
    (0x26D4, 0x26D4),
    (0x26EA, 0x26EA),
    (0x26F2, 0x26F3),
    (0x26F5, 0x26F5),
    (0x26FA, 0x26FA),
    (0x26FD, 0x26FD),
    (0x2705, 0x2705),
    (0x270A, 0x270B),
    (0x2728, 0x2728),
    (0x274C, 0x274C),
    (0x274E, 0x274E),
    (0x2753, 0x2755),
    (0x2757, 0x2757),
    (0x2795, 0x2797),
    (0x27B0, 0x27B0),
    (0x27BF, 0x27BF),
    (0x2B1B, 0x2B1C),
    (0x2B50, 0x2B50),
    (0x2B55, 0x2B55),
    (0x1F004, 0x1F004),
    (0x1F0CF, 0x1F0CF),
    (0x1F18E, 0x1F18E),
    (0x1F191, 0x1F19A),
    (0x1F1E6, 0x1F1FF),
    (0x1F201, 0x1F201),
    (0x1F21A, 0x1F21A),
    (0x1F22F, 0x1F22F),
    (0x1F232, 0x1F236),
    (0x1F238, 0x1F23A),
    (0x1F250, 0x1F251),
    (0x1F300, 0x1F320),
    (0x1F32D, 0x1F335),
    (0x1F337, 0x1F37C),
    (0x1F37E, 0x1F393),
    (0x1F3A0, 0x1F3CA),
    (0x1F3CF, 0x1F3D3),
    (0x1F3E0, 0x1F3F0),
    (0x1F3F4, 0x1F3F4),
    (0x1F3F8, 0x1F43E),
    (0x1F440, 0x1F440),
    (0x1F442, 0x1F4FC),
    (0x1F4FF, 0x1F53D),
    (0x1F54B, 0x1F54E),
    (0x1F550, 0x1F567),
    (0x1F57A, 0x1F57A),
    (0x1F595, 0x1F596),
    (0x1F5A4, 0x1F5A4),
    (0x1F5FB, 0x1F64F),
    (0x1F680, 0x1F6C5),
    (0x1F6CC, 0x1F6CC),
    (0x1F6D0, 0x1F6D2),
    (0x1F6D5, 0x1F6D8),
    (0x1F6DC, 0x1F6DF),
    (0x1F6EB, 0x1F6EC),
    (0x1F6F4, 0x1F6FC),
    (0x1F7E0, 0x1F7EB),
    (0x1F7F0, 0x1F7F0),
    (0x1F90C, 0x1F93A),
    (0x1F93C, 0x1F945),
    (0x1F947, 0x1F9FF),
    (0x1FA70, 0x1FA7C),
    (0x1FA80, 0x1FA8A),
    (0x1FA8E, 0x1FAC6),
    (0x1FAC8, 0x1FAC8),
    (0x1FACD, 0x1FADC),
    (0x1FADF, 0x1FAEA),
    (0x1FAEF, 0x1FAF8),
)


def _is_assigned(cp: int) -> bool:
    return unicodedata.category(chr(cp)) != "Cn"


def assigned_set(lo: int, hi: int) -> set[int]:
    return {cp for cp in range(lo, hi + 1) if _is_assigned(cp)}


@cache
def gb2312_hanzi() -> frozenset[int]:
    """GB/T 2312 汉字：EUC-CN 区 16–87，共 6763 字。"""
    out: set[int] = set()
    for row in range(16, 88):
        for col in range(1, 95):
            try:
                s = bytes((0xA0 + row, 0xA0 + col)).decode("gb2312")
            except UnicodeDecodeError:
                continue
            if len(s) == 1:
                out.add(ord(s))
    return frozenset(out)


@cache
def big5_level1() -> frozenset[int]:
    """Big5 常用汉字（L1，0xA440–0xC67E），共 5401 字。"""
    out: set[int] = set()
    for hi in range(0xA4, 0xC7):
        for lo in list(range(0x40, 0x7F)) + list(range(0xA1, 0xFF)):
            if hi == 0xC6 and lo > 0x7E:
                continue
            try:
                s = bytes((hi, lo)).decode("big5")
            except UnicodeDecodeError:
                continue
            if len(s) == 1:
                out.add(ord(s))
    return frozenset(out)


def kana_letters() -> frozenset[int]:
    """平假名与片假名字母 182 个（不含浊点、中点、双连字号）。"""
    out = set(range(0x3041, 0x3097))
    out.update(range(0x309D, 0x30A0))
    out.update(range(0x30A1, 0x30FB))
    out.update(range(0x30FC, 0x30FF))
    return frozenset(out)


def hangul_syllables() -> frozenset[int]:
    return frozenset(range(0xAC00, 0xD7A4))


def count_mapped(cmap: dict[int, str], universe: set[int] | frozenset[int]) -> tuple[int, int]:
    total = len(universe)
    mapped = sum(1 for cp in universe if cp in cmap)
    return mapped, total


def pct_value(mapped: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(100.0 * mapped / total, 2)


@cache
def emoji_presentation_set() -> frozenset[int]:
    out: set[int] = set()
    for lo, hi in EMOJI_PRESENTATION_RANGES:
        out.update(cp for cp in range(lo, hi + 1) if _is_assigned(cp))
    return frozenset(out)


@cache
def assigned_count(lo: int, hi: int) -> int:
    return sum(1 for cp in range(lo, hi + 1) if _is_assigned(cp))


def pack_coverage_row(cmap: dict[int, str], name: str, note: str, universe) -> dict:
    mapped, total = count_mapped(cmap, universe)
    value = pct_value(mapped, total)
    return {
        "name": name,
        "note": note,
        "mapped": mapped,
        "total": total,
        "percent": f"{value:.2f}%",
        "percentValue": value,
    }


def product_coverage(cmap: dict[int, str]) -> dict:
    """规范 §4.2 产品向分集表。"""
    bmp_mapped = sum(1 for cp in cmap if cp <= 0xFFFF)
    supp_mapped = sum(1 for cp in cmap if cp >= 0x10000)
    supp_total = assigned_count(0x10000, 0x10FFFD)
    all_mapped = len(cmap)
    all_assigned = assigned_count(0x20, 0x10FFFD)
    cjk = [
        ("GB/T 2312", "简体中文基本集", gb2312_hanzi()),
        ("Big5 L1", "繁体中文高频用字基本集", big5_level1()),
        ("日文假名", "平假名与片假名", kana_letters()),
        ("谚文音节", "朝鲜文 / 韩文", hangul_syllables()),
    ]
    unicode_rows = [
        ("中日韩统一表意文字", "U+4E00–9FFF", assigned_set(0x4E00, 0x9FFF)),
        ("中日韩符号和标点", "U+3000–303F", assigned_set(0x3000, 0x303F)),
        ("基本拉丁字母", "U+0020–007E 可视 ASCII", frozenset(range(0x20, 0x7F))),
        ("标准阿拉伯数字", "U+0030–0039", frozenset(range(0x30, 0x3A))),
        ("通用可视标点", "U+2010–2027", frozenset(range(0x2010, 0x2028))),
        ("货币符号", "U+20A0–20CF", assigned_set(0x20A0, 0x20CF)),
        ("类字符号", "U+2100–214F", assigned_set(0x2100, 0x214F)),
        ("西里尔字母", "U+0400–04FF", assigned_set(0x0400, 0x04FF)),
        ("中日韩统一表意文字扩展 A 区", "U+3400–4DBF", assigned_set(0x3400, 0x4DBF)),
        ("中日韩统一表意文字扩展 B 区", "U+20000–2A6DF", assigned_set(0x20000, 0x2A6DF)),
        ("中日韩统一表意文字扩展 C 区", "U+2A700–2B73F", assigned_set(0x2A700, 0x2B73F)),
        ("中日韩统一表意文字扩展 D 区", "U+2B740–2B81F", assigned_set(0x2B740, 0x2B81F)),
        ("中日韩统一表意文字扩展 E 区", "U+2B820–2CEAF", assigned_set(0x2B820, 0x2CEAF)),
        ("中日韩统一表意文字扩展 F 区", "U+2CEB0–2EBEF", assigned_set(0x2CEB0, 0x2EBEF)),
        ("中日韩统一表意文字扩展 G 区", "U+30000–3134F", assigned_set(0x30000, 0x3134F)),
        ("中日韩统一表意文字扩展 H 区", "U+31350–323AF Unicode 15.0", assigned_set(0x31350, 0x323AF)),
        ("希腊和科普特字母", "U+0370–03FF", assigned_set(0x0370, 0x03FF)),
        ("泰文", "U+0E00–0E7F", assigned_set(0x0E00, 0x0E7F)),
        ("拉丁文补充-1", "U+0080–00FF", assigned_set(0x0080, 0x00FF)),
        ("通用标点", "U+2000–206F", assigned_set(0x2000, 0x206F)),
        ("箭头", "U+2190–21FF", assigned_set(0x2190, 0x21FF)),
        ("杂项技术用字符", "U+2300–23FF", assigned_set(0x2300, 0x23FF)),
        ("带圈字母数字", "U+2460–24FF", assigned_set(0x2460, 0x24FF)),
        ("制表符", "U+2500–257F", assigned_set(0x2500, 0x257F)),
        ("方块元素", "U+2580–259F", assigned_set(0x2580, 0x259F)),
        ("几何图形", "U+25A0–25FF", assigned_set(0x25A0, 0x25FF)),
        ("杂项符号", "U+2600–26FF", assigned_set(0x2600, 0x26FF)),
        ("印刷符号", "U+2700–27BF", assigned_set(0x2700, 0x27BF)),
        ("杂项符号和箭头", "U+2B00–2BFF", assigned_set(0x2B00, 0x2BFF)),
        ("注音符号", "U+3100–312F", assigned_set(0x3100, 0x312F)),
        ("带圈 CJK 字母和月份", "U+3200–32FF", assigned_set(0x3200, 0x32FF)),
        ("CJK 兼容字符", "U+3300–33FF", assigned_set(0x3300, 0x33FF)),
        ("CJK 兼容表意文字", "U+F900–FAFF", assigned_set(0xF900, 0xFAFF)),
        ("半角及全角形式", "U+FF00–FFEF", assigned_set(0xFF00, 0xFFEF)),
    ]

    bmp_value = pct_value(bmp_mapped, BMP_DENOM)
    supp_value = pct_value(supp_mapped, supp_total)
    all_value = pct_value(all_mapped, all_assigned)
    return {
        "unicodeVersion": unicodedata.unidata_version,
        "overview": [
            {
                "name": "总字符数（BMP）",
                "note": "已映射且码位 ≤ U+FFFF / 65535",
                "mapped": bmp_mapped,
                "total": BMP_DENOM,
                "percent": f"{bmp_value:.2f}%",
                "percentValue": bmp_value,
            },
            {
                "name": "增补平面",
                "note": "已映射且码位 ≥ U+10000 / 该版本已分配",
                "mapped": supp_mapped,
                "total": supp_total,
                "percent": f"{supp_value:.2f}%",
                "percentValue": supp_value,
            },
            {
                "name": "全平面已分配",
                "note": "mapped / 该 Unicode 版本已分配标量值",
                "mapped": all_mapped,
                "total": all_assigned,
                "percent": f"{all_value:.2f}%",
                "percentValue": all_value,
            },
        ],
        "cjk": [pack_coverage_row(cmap, n, note, u) for n, note, u in cjk],
        "unicode": [pack_coverage_row(cmap, n, note, u) for n, note, u in unicode_rows],
    }


def emoji_coverage(regular_cmap: dict[int, str], emoji_cmaps: list[tuple[str, dict]]) -> list[dict]:
    """配套表情字体覆盖；Regular 的 Emoji_Presentation 故意为 0。"""
    ep = emoji_presentation_set()
    rows = [
        pack_coverage_row(
            regular_cmap,
            "Emoji_Presentation · Regular",
            "等宽本体故意不收录默认 emoji 表现",
            ep,
        )
    ]
    for label, cmap in emoji_cmaps:
        rows.append(
            pack_coverage_row(
                cmap,
                f"Emoji_Presentation · {label}",
                "配套表情字体",
                ep,
            )
        )
    ri = frozenset(range(0x1F1E6, 0x1F200))
    for label, cmap in emoji_cmaps:
        rows.append(
            pack_coverage_row(
                cmap,
                f"区域指示符 · {label}",
                "U+1F1E6–1F1FF 国旗字母",
                ri,
            )
        )
    ms_cmap = None
    for label, cmap in emoji_cmaps:
        if "微软" in label:
            ms_cmap = cmap
            break
    if ms_cmap is None and emoji_cmaps:
        ms_cmap = emoji_cmaps[-1][1]
    if ms_cmap is not None:
        blocks = [
            ("杂项符号及象形文字 · 微软", "U+1F300–1F5FF", 0x1F300, 0x1F5FF),
            ("表情符号 · 微软", "U+1F600–1F64F Emoticons", 0x1F600, 0x1F64F),
            ("交通和地图符号 · 微软", "U+1F680–1F6FF", 0x1F680, 0x1F6FF),
            ("补充符号和象形文字 · 微软", "U+1F900–1F9FF", 0x1F900, 0x1F9FF),
            ("符号和象形文字扩展 A · 微软", "U+1FA70–1FAFF", 0x1FA70, 0x1FAFF),
        ]
        for name, note, lo, hi in blocks:
            rows.append(pack_coverage_row(ms_cmap, name, note, assigned_set(lo, hi)))
    return rows


def coverage_markdown_tables(product: dict) -> list[str]:
    lines = [
        "## 总览",
        "",
        "| 项目 | 已覆盖 | 集合大小 | 覆盖率 | 说明 |",
        "|------|--------|----------|--------|------|",
    ]
    for row in product["overview"]:
        lines.append(
            f"| {row['name']} | {row['mapped']} | {row['total']} | {row['percent']} | {row['note']} |"
        )
    lines += [
        "",
        "## CJK",
        "",
        "| 集合 | 已覆盖 | 集合大小 | 覆盖率 | 说明 |",
        "|------|--------|----------|--------|------|",
    ]
    for row in product["cjk"]:
        lines.append(
            f"| {row['name']} | {row['mapped']} | {row['total']} | {row['percent']} | {row['note']} |"
        )
    lines += [
        "",
        "## Unicode 区段",
        "",
        "| 区段 | 已覆盖 | 集合大小 | 覆盖率 | 口径 |",
        "|------|--------|----------|--------|------|",
    ]
    for row in product["unicode"]:
        lines.append(
            f"| {row['name']} | {row['mapped']} | {row['total']} | {row['percent']} | {row['note']} |"
        )
    if product.get("emoji"):
        lines += [
            "",
            "## 表情",
            "",
            "| 集合 | 已覆盖 | 集合大小 | 覆盖率 | 说明 |",
            "|------|--------|----------|--------|------|",
        ]
        for row in product["emoji"]:
            lines.append(
                f"| {row['name']} | {row['mapped']} | {row['total']} | {row['percent']} | {row['note']} |"
            )
    return lines


def empty_program() -> Program:
    prog = Program()
    prog.fromBytecode(b"")
    return prog


def in_jbm_ranges(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in JBM_RANGES)


def is_emoji_presentation(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in EMOJI_PRESENTATION_RANGES)


def strip_emoji_presentation(font: TTFont) -> int:
    """从 cmap 去掉默认 emoji 表现字符，让配套彩色字体能够露出来。"""
    dropped: set[int] = set()
    for table in font["cmap"].tables:
        if table.format == 14 or not table.isUnicode():
            continue
        for cp in [c for c in table.cmap if is_emoji_presentation(c)]:
            del table.cmap[cp]
            dropped.add(cp)
        table.data = None
    print("stripped emoji presentation", len(dropped))
    return len(dropped)


def keep_in_emoji_font(cp: int) -> bool:
    """去掉 ASCII（数字、#*、空格），保留 EP 以及可用栈覆盖的特殊符号。"""
    return cp >= 0x80


def strip_non_emoji_from_emoji_font(font: TTFont) -> int:
    """去掉 ASCII，避免覆盖等宽数字；⚠❤☀ 等特殊符号保留。"""
    dropped: set[int] = set()
    for table in font["cmap"].tables:
        if table.format == 14 or not table.isUnicode():
            continue
        for cp in [c for c in table.cmap if not keep_in_emoji_font(c)]:
            del table.cmap[cp]
            dropped.add(cp)
        table.data = None
    print("emoji dropped ASCII cmap", len(dropped))
    return len(dropped)


def collect_names(font: TTFont, unicodes: set[int]) -> set[str]:
    cmap = font.getBestCmap()
    glyf = font["glyf"]
    names: set[str] = set()

    def add(name: str) -> None:
        if name in names:
            return
        names.add(name)
        glyph = glyf[name]
        if glyph.isComposite():
            for comp in glyph.components:
                add(comp.glyphName)

    for cp in unicodes:
        gname = cmap.get(cp)
        if gname:
            add(gname)
    return names


def scale_glyph(glyph, glyf, sx: float, sy: float) -> None:
    if glyph.numberOfContours > 0:
        coords, _end, flags = glyph.getCoordinates(glyf)
        coords.transform(((sx, 0), (0, sy)))
        for i, fl in enumerate(flags):
            flags[i] = int(fl) & ~flagOverlapSimple
        glyph.coordinates = coords
        glyph.flags = flags
        glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax = coords.calcIntBounds()
        glyph.program = empty_program()
        return
    if glyph.isComposite():
        for comp in glyph.components:
            comp.x = round(comp.x * sx)
            comp.y = round(comp.y * sy)
            if hasattr(comp, "transform") and comp.transform:
                xx, xy, yx, yy = comp.transform
                comp.transform = (xx * sx, xy * sy, yx * sx, yy * sy)


def sanitize_for_ots(font: TTFont) -> None:
    """Chrome OTS：maxZones 须为 1 或 2；glyf 简单轮廓 flag bit6 须为 0。"""
    maxp = font["maxp"]
    if getattr(maxp, "maxZones", 0) < 1:
        maxp.maxZones = 1
    if getattr(maxp, "maxTwilightPoints", 0) and maxp.maxZones < 2:
        maxp.maxZones = 2
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        if glyph.numberOfContours <= 0:
            continue
        coords, _end, flags = glyph.getCoordinates(glyf)
        for i, fl in enumerate(flags):
            flags[i] = int(fl) & ~flagOverlapSimple
        glyph.coordinates = coords
        glyph.flags = flags
    for tag in ("fpgm", "prep", "cvt "):
        if tag in font:
            del font[tag]


def _scale_int(value: float, s: float) -> int:
    return round(value * s)


def scale_colr_paints(font: TTFont, s: float) -> None:
    """把 COLRv1 里的位移、半径、裁剪框缩到与 glyf 同一比例。矩阵的 xx/yy 不乘。"""
    if "COLR" not in font:
        return
    colr = font["COLR"].table
    if getattr(colr, "Version", 0) < 1 or getattr(colr, "BaseGlyphList", None) is None:
        return
    seen: set[int] = set()

    def walk(paint) -> None:
        pid = id(paint)
        if pid in seen:
            return
        seen.add(pid)
        for attr in (
            "x0", "y0", "x1", "y1", "x2", "y2", "r0", "r1",
            "dx", "dy", "centerX", "centerY",
        ):
            if hasattr(paint, attr):
                setattr(paint, attr, _scale_int(getattr(paint, attr), s))
        if hasattr(paint, "Transform") and paint.Transform is not None:
            tr = paint.Transform
            if hasattr(tr, "dx"):
                tr.dx *= s
            if hasattr(tr, "dy"):
                tr.dy *= s
        if getattr(paint, "Format", None) == 1:
            return
        nested = getattr(paint, "Paint", None)
        if nested is not None:
            walk(nested)
        src = getattr(paint, "SourcePaint", None)
        if src is not None:
            walk(src)
            walk(paint.BackdropPaint)

    for rec in colr.BaseGlyphList.BaseGlyphPaintRecord:
        walk(rec.Paint)
    if colr.LayerList is not None:
        for paint in colr.LayerList.Paint:
            walk(paint)
    if colr.ClipList is not None:
        for box in colr.ClipList.clips.values():
            box.xMin = _scale_int(box.xMin, s)
            box.yMin = _scale_int(box.yMin, s)
            box.xMax = _scale_int(box.xMax, s)
            box.yMax = _scale_int(box.yMax, s)


def fit_emoji_to_em(font: TTFont) -> float:
    """把最常见的非零推进收到 1 em，并把 unitsPerEm 改成与 Regular 相同的 1000。"""
    from collections import Counter

    metrics = font["hmtx"].metrics
    counts = Counter(adv for adv, _lsb in metrics.values() if adv > 0)
    typical, _n = counts.most_common(1)[0]
    scale = TARGET_UPEM / typical
    glyf = font["glyf"] if "glyf" in font else None
    for name in font.getGlyphOrder():
        if glyf is not None:
            scale_glyph(glyf[name], glyf, scale, scale)
        adv, lsb = metrics[name]
        if adv == 0:
            metrics[name] = (0, _scale_int(lsb, scale))
        else:
            metrics[name] = (TARGET_UPEM, _scale_int(lsb, scale))
    scale_colr_paints(font, scale)
    font["head"].unitsPerEm = TARGET_UPEM
    hhea = font["hhea"]
    hhea.ascent = _scale_int(hhea.ascent, scale)
    hhea.descent = _scale_int(hhea.descent, scale)
    hhea.advanceWidthMax = TARGET_UPEM
    if "vmtx" in font:
        for name, (adv, tsb) in list(font["vmtx"].metrics.items()):
            font["vmtx"].metrics[name] = (
                _scale_int(adv, scale) if adv else 0,
                _scale_int(tsb, scale),
            )
    if "vhea" in font:
        vhea = font["vhea"]
        for attr in (
            "ascent", "descent", "lineGap", "advanceHeightMax",
            "minTopSideBearing", "minBottomSideBearing", "yMaxExtent",
        ):
            if hasattr(vhea, attr):
                setattr(vhea, attr, _scale_int(getattr(vhea, attr), scale))
    if "OS/2" in font:
        os2 = font["OS/2"]
        for attr in (
            "sTypoAscender", "sTypoDescender", "usWinAscent", "usWinDescent",
            "sxHeight", "sCapHeight", "xAvgCharWidth",
        ):
            if hasattr(os2, attr):
                setattr(os2, attr, abs(_scale_int(getattr(os2, attr), scale)))
        os2.sTypoDescender = -abs(os2.sTypoDescender)
    return scale


def set_emoji_names(font: TTFont, variant: dict) -> None:
    name = font["name"]
    name.names = []
    family_en = variant["family_en"]
    family_zh = variant["family_zh"]
    records = [
        (0, variant["copyright"]),
        (1, family_en),
        (2, "Regular"),
        (3, f"{family_en}:Regular"),
        (4, variant["full_en"]),
        (5, "Version 0.1.0-preview"),
        (6, variant["ps"]),
        (13, variant["license_notice"]),
        (14, "https://openfontlicense.org"),
        (16, family_en),
        (17, "Regular"),
    ]
    for nid, value in records:
        name.setName(value, nid, 3, 1, 0x409)
    name.setName(family_zh, 1, 3, 1, 0x804)
    name.setName(family_zh + " Regular", 4, 3, 1, 0x804)
    name.setName(family_zh, 16, 3, 1, 0x804)
    font["post"].isFixedPitch = 1


def build_emoji_variant(variant: dict) -> Path:
    src = Path(variant["src"])
    if not src.exists():
        raise SystemExit(f"缺少上游表情字体：{src}")
    print("load emoji", src.name)
    font = TTFont(src, recalcBBoxes=True, recalcTimestamp=False)
    # 预览与 Electron 走 COLRv1；位图/SVG 表不随 glyf 缩放，留下会把格子撑乱。
    for tag in ("CBDT", "CBLC", "SVG "):
        if tag in font:
            del font[tag]
    print("fit emoji to 1em", variant["family_en"])
    scale = fit_emoji_to_em(font)
    strip_non_emoji_from_emoji_font(font)
    set_emoji_names(font, variant)
    sanitize_for_ots(font)
    out = DIST / variant["out_name"]
    print("save", out, "scale", round(scale, 6))
    font.save(out)
    return out


def emoji_needs_rebuild(paths: list[Path]) -> bool:
    if not all(p.exists() for p in paths):
        return True
    for path in paths:
        font = TTFont(path)
        upem = font["head"].unitsPerEm
        cmap = font.getBestCmap()
        font.close()
        if upem != TARGET_UPEM:
            return True
        # 数字不应出现在表情 cmap；⚠ 这类可覆盖符号必须保留
        if 0x30 in cmap or 0x26A0 not in cmap:
            return True
    return False


def build_all_emoji() -> list[Path]:
    return [build_emoji_variant(v) for v in EMOJI_VARIANTS]


def overlay_jbm(base: TTFont, jbm: TTFont) -> dict[str, str]:
    """返回码位来源：U+XXXX -> jetbrains-mono。"""
    src_cmap = jbm.getBestCmap()
    src_glyf = jbm["glyf"]
    src_hmtx = jbm["hmtx"]
    unicodes = {cp for cp in src_cmap if in_jbm_ranges(cp)}
    names = collect_names(jbm, unicodes)
    rename = {n: PREFIX + n.replace(".", "_") for n in names}

    dst_glyf = base["glyf"]
    dst_hmtx = base["hmtx"]
    order = list(base.getGlyphOrder())

    for old in names:
        new = rename[old]
        raw = copy.deepcopy(src_glyf[old])
        if raw.isComposite():
            for comp in raw.components:
                comp.glyphName = rename[comp.glyphName]
        scale_glyph(raw, src_glyf, SCALE, SCALE)
        dst_glyf[new] = raw
        adv, lsb = src_hmtx[old]
        dst_hmtx[new] = (round(adv * SCALE), round(lsb * SCALE))
        order.append(new)

    base.setGlyphOrder(order)
    base["maxp"].numGlyphs = len(order)
    source: dict[str, str] = {}
    for table in base["cmap"].tables:
        # format 14 是异体选择器；且 subtable 若仍持有 data，compile 会丢掉 cmap 修改
        if table.format == 14 or not table.isUnicode():
            continue
        for cp in unicodes:
            table.cmap[cp] = rename[src_cmap[cp]]
            source[f"U+{cp:04X}"] = "jetbrains-mono"
        table.data = None
    return source


def strip_ligatures(font: TTFont) -> None:
    if "GSUB" not in font:
        return
    gsub = font["GSUB"].table
    drop = {"liga", "dlig", "hlig", "calt", "rlig"}
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag in drop:
            fr.Feature.LookupListIndex = []


def set_names(font: TTFont) -> None:
    name = font["name"]
    name.names = []
    records = [
        (0, "Copyright 2026 小黑字. Portions: JetBrains Mono Project Authors; Sarasa Gothic / Source Han Sans / Iosevka authors. SIL OFL 1.1."),
        (1, FAMILY_EN),
        (2, "Regular"),
        (3, "Xiaoheizi Mono:Regular"),
        (4, FULL_EN),
        (5, "Version 0.1.0-preview"),
        (6, PS_NAME),
        (13, "This Font Software is licensed under the SIL Open Font License, Version 1.1. https://openfontlicense.org"),
        (14, "https://openfontlicense.org"),
        (16, FAMILY_EN),
        (17, "Regular"),
    ]
    for nid, value in records:
        name.setName(value, nid, 3, 1, 0x409)
    name.setName(FAMILY_ZH, 1, 3, 1, 0x804)
    name.setName(FAMILY_ZH + " Regular", 4, 3, 1, 0x804)
    name.setName(FAMILY_ZH, 16, 3, 1, 0x804)
    font["post"].isFixedPitch = 1


def expected_advance(cp: int, upem: int) -> int:
    """名称里的 em 按排版长度；其余走 UAX #11。Mn/Me 见 §6.2；Cf/Cc 按 POSIX wcwidth 不计列。"""
    if cp in NAMED_EM_RATIO:
        return round(NAMED_EM_RATIO[cp] * upem)
    if cp >= 0x110000:
        return upem // 2
    cat = unicodedata.category(chr(cp))
    if cat in {"Mn", "Me", "Cf", "Cc", "Zl", "Zp"}:
        return 0
    eaw = unicodedata.east_asian_width(chr(cp))
    if eaw in {"W", "F"}:
        return upem
    return upem // 2


def expected_cells(cp: int, advance: int, upem: int) -> int | None:
    """对照应得推进；合则返回格子（可大于 2），不合则 None。分数 em 返回 None 以外的 0 并在覆盖表用 ~。"""
    exp = expected_advance(cp, upem)
    if abs(advance - exp) > 1:
        return None
    if exp == 0:
        return 0
    cells = exp / (upem / 2)
    rounded = round(cells)
    if abs(cells - rounded) <= 0.02:
        return int(rounded)
    return -1  # 不足 1 格的分数 em，覆盖表记为 ~


def apply_uax11_metrics(font: TTFont) -> int:
    """按应得宽度改 hmtx；有轮廓的字横向拉伸到新推进，空格只改推进。"""
    cmap_tables = [
        t for t in font["cmap"].tables if t.isUnicode() and t.format != 14
    ]
    hmtx = font["hmtx"]
    glyf = font["glyf"]
    upem = font["head"].unitsPerEm
    by_glyph: dict[str, dict[int, list[int]]] = {}
    seen: set[int] = set()
    for table in cmap_tables:
        for cp, gname in table.cmap.items():
            if cp in seen:
                continue
            seen.add(cp)
            exp = expected_advance(cp, upem)
            by_glyph.setdefault(gname, {}).setdefault(exp, []).append(cp)

    changed = 0
    order = list(font.getGlyphOrder())
    for gname, widths in by_glyph.items():
        items = list(widths.items())
        items.sort(key=lambda pair: -len(pair[1]))
        for i, (exp, cps) in enumerate(items):
            name = gname
            if i > 0:
                name = f"uax11.{gname}.{exp}"
                glyf[name] = copy.deepcopy(glyf[gname])
                hmtx[name] = hmtx[gname]
                order.append(name)
                for table in cmap_tables:
                    for cp in cps:
                        if cp in table.cmap:
                            table.cmap[cp] = name
                            table.data = None
            adv, lsb = hmtx[name]
            if abs(adv - exp) <= 1:
                continue
            glyph = glyf[name]
            has_outline = glyph.numberOfContours > 0 or glyph.isComposite()
            if has_outline and adv > 0 and exp > 0:
                scale_glyph(glyph, glyf, exp / adv, 1.0)
                lsb = round(lsb * exp / adv)
            elif exp > adv > 0:
                lsb = lsb + (exp - adv) // 2
            hmtx[name] = (exp, lsb)
            changed += 1
    font.setGlyphOrder(order)
    font["maxp"].numGlyphs = len(order)
    print("uax11 metrics changed", changed)
    return changed


def ensure_multi_em_dashes(font: TTFont) -> None:
    """补 TWO-EM / THREE-EM DASH：从已拉到 1 em 的 EM DASH 横向复制。"""
    cmap = font.getBestCmap()
    src_cp = 0x2014
    if src_cp not in cmap:
        return
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    upem = font["head"].unitsPerEm
    src = cmap[src_cp]
    order = list(font.getGlyphOrder())
    added = 0
    for cp, em, suffix in ((0x2E3A, 2, "two"), (0x2E3B, 3, "three")):
        if cp in cmap:
            continue
        name = f"named.{suffix}emdash"
        glyf[name] = copy.deepcopy(glyf[src])
        old_adv, old_lsb = hmtx[src]
        new_adv = em * upem
        ratio = new_adv / old_adv if old_adv else float(em)
        scale_glyph(glyf[name], glyf, ratio, 1.0)
        hmtx[name] = (new_adv, round(old_lsb * ratio))
        order.append(name)
        for table in font["cmap"].tables:
            if table.isUnicode() and table.format != 14:
                table.cmap[cp] = name
                table.data = None
        added += 1
    if added:
        font.setGlyphOrder(order)
        font["maxp"].numGlyphs = len(order)
        print("added multi-em dashes", added)


def load_emoji_cmaps(emoji_ttfs: list[Path] | None) -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []
    if not emoji_ttfs:
        return out
    for variant, path in zip(EMOJI_VARIANTS, emoji_ttfs):
        if path.exists():
            out.append((variant["family_zh"], TTFont(path).getBestCmap()))
    return out


def write_coverage(
    font: TTFont,
    sources: dict[str, str],
    emoji_ttfs: list[Path] | None = None,
) -> list[dict]:
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upem = font["head"].unitsPerEm
    violations: list[dict] = []
    for cp, gname in cmap.items():
        adv = hmtx[gname][0]
        if expected_cells(cp, adv, upem) is None:
            violations.append({
                "cp": f"U+{cp:04X}",
                "advance": adv,
                "expected": expected_advance(cp, upem),
            })

    mapped = len(cmap)
    assigned = 0
    for cp in range(0x20, 0x110000):
        if unicodedata.category(chr(cp)) != "Cn":
            assigned += 1

    block_rows = []
    for title, lo, hi in REQUIRED_BLOCKS:
        in_font = [cp for cp in range(lo, hi + 1) if cp in cmap]
        assigned_blk = [
            cp
            for cp in range(lo, hi + 1)
            if unicodedata.category(chr(cp)) != "Cn"
        ]
        cells = set()
        origin = set()
        for cp in in_font:
            adv = hmtx[cmap[cp]][0]
            c = expected_cells(cp, adv, upem)
            if c is None:
                cells.add("?")
            elif c < 0:
                cells.add("~")
            else:
                cells.add(str(c))
            origin.add(sources.get(f"U+{cp:04X}", "sarasa"))
        if cells <= {"1"}:
            grid = "1"
        elif cells <= {"2"}:
            grid = "2"
        elif cells <= {"1", "2"}:
            grid = "混"
        else:
            grid = "混"
        cov = 100.0 * len(in_font) / len(assigned_blk) if assigned_blk else 0.0
        block_rows.append(
            {
                "block": title,
                "range": f"U+{lo:04X}–U+{hi:04X}",
                "assigned": len(assigned_blk),
                "mapped": len(in_font),
                "percent": round(cov, 2),
                "grid": grid,
                "source": "+".join(sorted(origin)) if origin else "—",
            }
        )

    summary = {
        "unicodeVersion": unicodedata.unidata_version,
        "fontPostScriptName": PS_NAME,
        "mapped": mapped,
        "assignedInVersion": assigned,
        "mappedPercentOfAssigned": round(100.0 * mapped / assigned, 4) if assigned else 0,
        "widthViolations": violations[:200],
        "widthViolationCount": len(violations),
        "sources": {
            "jetbrainsMono": "2.304 NL Regular",
            "sarasaGothic": "Sarasa Fixed SC Regular 1.0.40 unhinted",
        },
    }
    DIST.mkdir(parents=True, exist_ok=True)
    product = product_coverage(cmap)
    product["emoji"] = emoji_coverage(cmap, load_emoji_cmaps(emoji_ttfs))
    summary["productCoverage"] = product
    (DIST / "coverage-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# 小黑字等宽 · 字符覆盖（预览构建）",
        "",
        f"- Unicode {summary['unicodeVersion']}（Python unicodedata）",
        f"- 全平面已映射 {mapped} / 已分配 {assigned} = {summary['mappedPercentOfAssigned']}%",
        f"- 宽度违规 {len(violations)}（发布时必须为 0）",
        "",
        *coverage_markdown_tables(product),
        "",
        "## Unicode 分块（必测）",
        "",
        "| 区块 | 范围 | 该版本已分配 | 已覆盖 | 覆盖率 | 格子 | 来源 |",
        "|------|------|--------------|--------|--------|------|------|",
    ]
    for row in block_rows:
        lines.append(
            f"| {row['block']} | {row['range']} | {row['assigned']} | {row['mapped']} | "
            f"{row['percent']}% | {row['grid']} | {row['source']} |"
        )
    (DIST / "coverage-blocks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return violations


def write_preview(full_ttf: Path, emoji_ttfs: list[Path] | None = None) -> None:
    if not PREVIEW_HTML.exists():
        raise SystemExit(f"缺少预览模板：{PREVIEW_HTML}")
    from fontTools.subset import Options, Subsetter

    DIST.mkdir(parents=True, exist_ok=True)
    html = PREVIEW_HTML.read_text(encoding="utf-8")
    (DIST / "preview.html").write_text(html, encoding="utf-8")

    tiny = TTFont(full_ttf)
    cmap = tiny.getBestCmap()
    product = product_coverage(cmap)
    product["emoji"] = emoji_coverage(cmap, load_emoji_cmaps(emoji_ttfs))
    payload = {
        "unicodeVersion": product["unicodeVersion"],
        "overview": product["overview"],
        "cjk": product["cjk"],
        "unicode": product["unicode"],
        "emoji": product["emoji"],
    }
    js = (
        "/* 由 scripts/build.py 生成，请勿手改 */\n"
        "window.XIAOHEIZI_COVERAGE = "
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + ";\n"
    )
    js_path = DIST / "coverage.js"
    js_path.write_text(js, encoding="utf-8")

    opt = Options()
    opt.ignore_missing_unicodes = True
    opt.layout_features = "*"
    sub = Subsetter(options=opt)
    sub.populate(
        text=html + js,
        unicodes=list(range(0x20, 0x7F))
        + [0xA0]
        + list(range(0x2000, 0x2070))
        + list(range(0x2190, 0x2200))
        + list(range(0x2300, 0x2400))
        + list(range(0x2500, 0x2600))
        + list(range(0x2600, 0x27C0))
        + list(range(0x2900, 0x2980))
        + list(range(0x2B00, 0x2C00))
        + [0x2E3A, 0x2E3B, 0x3000, 0x3030, 0x303D, 0x3297, 0x3299]
        + list(range(0x2460, 0x2500))
        + list(range(0x3200, 0x3300))
        + list(range(0xFF00, 0xFFEF))
        + list(range(0x1F170, 0x1F240)),
    )
    sub.subset(tiny)
    sanitize_for_ots(tiny)
    tiny.save(DIST / "preview.ttf")

    if emoji_ttfs:
        for variant, emoji_ttf in zip(EMOJI_VARIANTS, emoji_ttfs):
            if not emoji_ttf.exists():
                continue
            eopt = Options()
            eopt.ignore_missing_unicodes = True
            eopt.layout_features = "*"
            esub = Subsetter(options=eopt)
            etiny = TTFont(emoji_ttf)
            esub.populate(text=html)
            esub.subset(etiny)
            etiny.save(DIST / variant["preview_name"])


def main() -> None:
    if not SARASA.exists() or not JBM.exists():
        raise SystemExit(f"缺少上游字体：{SARASA} 或 {JBM}")
    DIST.mkdir(parents=True, exist_ok=True)
    print("load sarasa")
    base = TTFont(SARASA, recalcBBoxes=True, recalcTimestamp=False)
    print("load jetbrains")
    jbm = TTFont(JBM, recalcBBoxes=True, recalcTimestamp=False)
    print("overlay")
    sources = overlay_jbm(base, jbm)
    for tag in ("vmtx", "vhea", "VORG"):
        if tag in base:
            del base[tag]
    strip_ligatures(base)
    apply_uax11_metrics(base)
    ensure_multi_em_dashes(base)
    strip_emoji_presentation(base)
    set_names(base)
    sanitize_for_ots(base)
    out = DIST / "XiaoheiziMono-Regular.ttf"
    print("save", out)
    base.save(out)
    emoji_outs = [DIST / v["out_name"] for v in EMOJI_VARIANTS]
    if emoji_needs_rebuild(emoji_outs):
        emoji_outs = build_all_emoji()
    else:
        print("reuse emoji", [p.name for p in emoji_outs])
    print("coverage")
    built = TTFont(out)
    violations = write_coverage(built, sources, emoji_outs)
    write_preview(out, emoji_outs)
    shutil.copyfile(ROOT / "OFL.txt", DIST / "OFL.txt")
    if JBM_OFL.exists():
        shutil.copyfile(JBM_OFL, DIST / "JetBrainsMono-OFL.txt")
    if NOTO_EMOJI_OFL.exists():
        shutil.copyfile(NOTO_EMOJI_OFL, DIST / "NotoEmoji-OFL.txt")
    if FLUENT_MIT_MS.exists():
        shutil.copyfile(FLUENT_MIT_MS, DIST / "FluentEmoji-MIT-Microsoft.txt")
    if FLUENT_MIT_BUILD.exists():
        shutil.copyfile(FLUENT_MIT_BUILD, DIST / "FluentEmoji-MIT-tetunori.txt")
    print("width violations", len(violations))
    a = built.getBestCmap()
    h = built["hmtx"]
    print("A", h[a[ord("A")]][0], "zhong", h[a[0x4E2D]][0], "box", h[a[0x2500]][0])
    print("circled21", h[a[0x3251]][0], "hw-kiyeok", h[a[0xFFA1]][0], "corp", h[a[0x337F]][0])
    print("emdash", h[a[0x2014]][0], "emspace", h[a[0x2003]][0], "twoem", h[a[0x2E3A]][0], "threeem", h[a[0x2E3B]][0])
    print("check-ep", 0x2705 in a, "voltage-ep", 0x26A1 in a, "warn-keep", 0x26A0 in a)
    print("done", out, "bytes", out.stat().st_size)


if __name__ == "__main__":
    main()
