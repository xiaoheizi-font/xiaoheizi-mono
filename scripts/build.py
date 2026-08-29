"""把 JetBrains Mono NL 缩到半个汉字宽，覆盖到更纱 Fixed SC 的西文/盒绘上。"""

from __future__ import annotations

import copy
import json
import shutil
import unicodedata
from functools import cache
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple
from fontTools.ttLib.tables.ttProgram import Program

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor"
DIST = ROOT / "dist"
PREVIEW_HTML = ROOT / "preview" / "preview.html"
BLOCK_ZH_PATH = Path(__file__).resolve().parent / "unicode-block-zh.json"

SARASA = VENDOR / "sarasa-fixed-sc" / "SarasaFixedSC-Regular.ttf"
JBM = VENDOR / "jetbrains-mono" / "fonts" / "ttf" / "JetBrainsMonoNL-Regular.ttf"
JBM_OFL = VENDOR / "jetbrains-mono" / "OFL.txt"
SOURCE_HAN = VENDOR / "source-han-sans" / "SourceHanSansSC-Regular.otf"

# 规范 §6：配套表情字体，不并入 Regular；Regular 保留 EP 黑白半宽，由栈覆盖
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
        "family_en": "Xiaoheizi Emoji 3D",
        "family_zh": "小黑字表情立体",
        "ps": "XiaoheiziEmoji3D-Regular",
        "full_en": "Xiaoheizi Emoji 3D Regular",
        "out_name": "XiaoheiziEmoji3D-Regular.ttf",
        "preview_name": "preview-emoji-3d.ttf",
        "flags_from_noto": True,
        "copyright": "Copyright 2026 小黑字. Artwork: Microsoft Fluent Emoji (MIT); flag glyphs from Noto Emoji (Google LLC, SIL OFL 1.1). Font compilation portions: tetunori/fluent-emoji-webfont (MIT).",
        "license_notice": "Font names under SIL OFL 1.1. Fluent Emoji artwork under MIT. Flag portions from Noto Emoji under SIL OFL 1.1. See license files in dist/.",
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

# 规范 §4：图鉴与覆盖率共用 Unicode Blocks.txt。一页 16 列 × 32 行。
CATALOG_COLS = 16
CATALOG_ROWS = 32
CATALOG_PAGE_SIZE = CATALOG_COLS * CATALOG_ROWS
BLOCK_SKIP_NAMES = frozenset(
    {
        "No_Block",
        "High Surrogates",
        "High Private Use Surrogates",
        "Low Surrogates",
        "Private Use Area",
        "Supplementary Private Use Area-A",
        "Supplementary Private Use Area-B",
    }
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

# 规范 §2 例外表：带圈字母数字按 1 em（2 格），来源思源，覆盖更纱 Fixed 的半格稿。
ENCLOSED_ALNUM = (0x2460, 0x24FF)
SOURCE_HAN_PREFIX = "shs."
# 思源有则覆盖。扑克不覆盖、不拉宽。
SOURCE_HAN_OVERLAY_RANGES = (
    (0x2460, 0x24FF),
    (0x2300, 0x23FF),
    (0x25A0, 0x25FF),
    (0x2600, 0x26FF),
    (0x2700, 0x27BF),
)
# 已映射码位直接拉到 1 em（补充带圈全量）。
STRETCH_TO_EM_RANGES = (
    (0x1F100, 0x1F1FF),
)
# 带圈表意文字补充：此前 W/EP 半宽的 13 个。
STRETCH_TO_EM_CPS = frozenset(
    {
        0x1F201,
        0x1F21A,
        0x1F22F,
        0x1F232,
        0x1F233,
        0x1F234,
        0x1F235,
        0x1F236,
        0x1F238,
        0x1F239,
        0x1F23A,
        0x1F250,
        0x1F251,
    }
)
NOTO_PREFIX = "noto."

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

# Unicode Emoji_Presentation。Regular 保留更纱黑白稿并收成半宽；彩色全宽由表情字体覆盖。
# 不含 ⚠★❤☀✓✔ 等默认文本表现字符（那些走 UAX #11）。
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
def unicode_block_defs() -> tuple[tuple[str, int, int], ...]:
    """Unicode Blocks.txt 官方区块，去掉代理区、私用区与空隙。"""
    from fontTools.unicodedata.Blocks import RANGES, VALUES

    out: list[tuple[str, int, int]] = []
    for i, start in enumerate(RANGES):
        name = VALUES[i]
        if name in BLOCK_SKIP_NAMES:
            continue
        end = (RANGES[i + 1] - 1) if i + 1 < len(RANGES) else 0x10FFFF
        out.append((name, start, end))
    return tuple(out)


@cache
def block_zh_map() -> dict[str, str]:
    """规范 §4.3：英文区块名 → 简体中文。缺译名回退英文。"""
    if not BLOCK_ZH_PATH.exists():
        return {}
    data = json.loads(BLOCK_ZH_PATH.read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in data.items()}


def block_zh_name(english: str) -> str:
    return block_zh_map().get(english) or english


def unicode_block_coverage(
    cmap: dict[int, str],
    hmtx=None,
    sources: dict[str, str] | None = None,
    upem: int | None = None,
) -> list[dict]:
    """规范 §4.3：每个官方区块一行。本版本已分配为 0 的块不出现。"""
    rows: list[dict] = []
    for name, lo, hi in unicode_block_defs():
        assigned = 0
        mapped = 0
        cells: set[str] = set()
        origin: set[str] = set()
        for cp in range(lo, hi + 1):
            if not _is_assigned(cp):
                continue
            assigned += 1
            if cp not in cmap:
                continue
            mapped += 1
            if hmtx is None or upem is None:
                continue
            adv = hmtx[cmap[cp]][0]
            cell = expected_cells(cp, adv, upem)
            if cell is None:
                cells.add("?")
            elif cell < 0:
                cells.add("~")
            else:
                cells.add(str(cell))
            if sources is not None:
                origin.add(sources.get(f"U+{cp:04X}", "sarasa"))
        if assigned == 0:
            continue
        row = pack_count_row(name, f"U+{lo:04X}–{hi:04X}", mapped, assigned)
        row["nameZh"] = block_zh_name(name)
        if hmtx is not None:
            if not cells:
                grid = "—"
            elif cells <= {"1"}:
                grid = "1"
            elif cells <= {"2"}:
                grid = "2"
            else:
                grid = "混"
            row["grid"] = grid
            row["source"] = "+".join(sorted(origin)) if origin else "—"
        rows.append(row)
    return rows


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


def pack_coverage_row(
    cmap: dict[int, str],
    name: str,
    note: str,
    universe,
    *,
    empty_ok: bool = False,
) -> dict:
    mapped, total = count_mapped(cmap, universe)
    return pack_count_row(name, note, mapped, total, empty_ok=empty_ok)


def pack_count_row(
    name: str,
    note: str,
    mapped: int,
    total: int,
    *,
    empty_ok: bool = False,
) -> dict:
    value = pct_value(mapped, total)
    if empty_ok:
        accepted = total > 0 and mapped == 0
    else:
        accepted = total > 0 and mapped == total
    return {
        "name": name,
        "note": note,
        "mapped": mapped,
        "total": total,
        "percent": f"{value:.2f}%",
        "percentValue": value,
        "accepted": accepted,
    }


def acceptance_mark(row: dict) -> str:
    return "✅" if row.get("accepted") else ""


def product_coverage(
    cmap: dict[int, str],
    hmtx=None,
    sources: dict[str, str] | None = None,
    upem: int | None = None,
) -> dict:
    """规范 §4.2 产品向分集表 + §4.3 官方区块全表。"""
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
                "accepted": False,
            },
            {
                "name": "增补平面",
                "note": "已映射且码位 ≥ U+10000 / 该版本已分配",
                "mapped": supp_mapped,
                "total": supp_total,
                "percent": f"{supp_value:.2f}%",
                "percentValue": supp_value,
                "accepted": False,
            },
            {
                "name": "全平面已分配",
                "note": "mapped / 该 Unicode 版本已分配标量值",
                "mapped": all_mapped,
                "total": all_assigned,
                "percent": f"{all_value:.2f}%",
                "percentValue": all_value,
                "accepted": False,
            },
        ],
        "cjk": [pack_coverage_row(cmap, n, note, u) for n, note, u in cjk],
        "unicode": [pack_coverage_row(cmap, n, note, u) for n, note, u in unicode_rows],
        "blocks": unicode_block_coverage(cmap, hmtx=hmtx, sources=sources, upem=upem),
    }


def emoji_coverage(
    regular_cmap: dict[int, str],
    emoji_stats: list[tuple[str, dict, int]],
) -> list[dict]:
    """配套表情字体覆盖；Regular 对 Emoji_Presentation 保留黑白半宽稿。"""
    ep = emoji_presentation_set()
    rows = [
        pack_coverage_row(
            regular_cmap,
            "Emoji_Presentation · Regular",
            "等宽本体黑白稿，半宽，不剔除",
            ep,
        )
    ]
    for label, cmap, _nliga in emoji_stats:
        rows.append(
            pack_coverage_row(
                cmap,
                f"Emoji_Presentation · {label}",
                "配套表情字体",
                ep,
            )
        )
    ri = frozenset(range(0x1F1E6, 0x1F200))
    flag_total = 0
    for _label, _cmap, nliga in emoji_stats:
        if nliga > flag_total:
            flag_total = nliga
    for label, cmap, nliga in emoji_stats:
        rows.append(
            pack_coverage_row(
                cmap,
                f"区域指示符 · {label}",
                "U+1F1E6–1F1FF 共 26 个字母，不是旗面",
                ri,
            )
        )
        rows.append(
            pack_count_row(
                f"国旗连字 · {label}",
                "GSUB 两枚区域指示符连成一图",
                nliga,
                flag_total or nliga,
            )
        )
    ms_cmap = None
    for label, cmap, _nliga in emoji_stats:
        if "立体" in label:
            ms_cmap = cmap
            break
    if ms_cmap is None and emoji_stats:
        ms_cmap = emoji_stats[-1][1]
    if ms_cmap is not None:
        blocks = [
            ("杂项符号及象形文字 · 立体", "U+1F300–1F5FF", 0x1F300, 0x1F5FF),
            ("表情符号 · 立体", "U+1F600–1F64F Emoticons", 0x1F600, 0x1F64F),
            ("交通和地图符号 · 立体", "U+1F680–1F6FF", 0x1F680, 0x1F6FF),
            ("补充符号和象形文字 · 立体", "U+1F900–1F9FF", 0x1F900, 0x1F9FF),
            ("符号和象形文字扩展 A · 立体", "U+1FA70–1FAFF", 0x1FA70, 0x1FAFF),
        ]
        for name, note, lo, hi in blocks:
            rows.append(pack_coverage_row(ms_cmap, name, note, assigned_set(lo, hi)))
    return rows


def coverage_markdown_tables(product: dict) -> list[str]:
    lines = [
        "## 总览",
        "",
        "| 项目 | 已覆盖 | 集合大小 | 覆盖率 | 验收 | 说明 |",
        "|------|--------|----------|--------|------|------|",
    ]
    for row in product["overview"]:
        lines.append(
            f"| {row['name']} | {row['mapped']} | {row['total']} | {row['percent']} | {acceptance_mark(row)} | {row['note']} |"
        )
    lines += [
        "",
        "## CJK",
        "",
        "| 集合 | 已覆盖 | 集合大小 | 覆盖率 | 验收 | 说明 |",
        "|------|--------|----------|--------|------|------|",
    ]
    for row in product["cjk"]:
        lines.append(
            f"| {row['name']} | {row['mapped']} | {row['total']} | {row['percent']} | {acceptance_mark(row)} | {row['note']} |"
        )
    lines += [
        "",
        "## Unicode 区段",
        "",
        "| 区段 | 已覆盖 | 集合大小 | 覆盖率 | 验收 | 口径 |",
        "|------|--------|----------|--------|------|------|",
    ]
    for row in product["unicode"]:
        lines.append(
            f"| {row['name']} | {row['mapped']} | {row['total']} | {row['percent']} | {acceptance_mark(row)} | {row['note']} |"
        )
    lines += [
        "",
        "## Unicode 区块",
        "",
        "| 中文名称 | 区块 | 范围 | 该版本已分配 | 已覆盖 | 覆盖率 | 验收 | 格子 | 来源 |",
        "|----------|------|------|--------------|--------|--------|------|------|------|",
    ]
    for row in product.get("blocks") or []:
        lines.append(
            f"| {row.get('nameZh', row['name'])} | {row['name']} | {row['note']} | {row['total']} | {row['mapped']} | "
            f"{row['percent']} | {acceptance_mark(row)} | {row.get('grid', '—')} | {row.get('source', '—')} |"
        )
    if product.get("emoji"):
        lines += [
            "",
            "## 表情",
            "",
            "| 集合 | 已覆盖 | 集合大小 | 覆盖率 | 验收 | 说明 |",
            "|------|--------|----------|--------|------|------|",
        ]
        for row in product["emoji"]:
            lines.append(
                f"| {row['name']} | {row['mapped']} | {row['total']} | {row['percent']} | {acceptance_mark(row)} | {row['note']} |"
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
    glyf = font["glyf"] if "glyf" in font else None
    names: set[str] = set()

    def add(name: str) -> None:
        if name in names:
            return
        names.add(name)
        # CFF 字体没有 glyf 组件；组件引用在画出时自然展开
        if glyf is None:
            return
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


# COLR 前景色：不指向 CPAL 条目，合并调色板时不得加偏移
FOREGROUND_PALETTE_INDEX = 0xFFFF
_NESTED_PAINT_ATTRS = ("Paint", "SourcePaint", "BackdropPaint")


def _iter_nested_paints(paint):
    """遍历画笔节点上嵌套的 Paint / SourcePaint / BackdropPaint。"""
    for attr in _NESTED_PAINT_ATTRS:
        child = getattr(paint, attr, None)
        if child is not None:
            yield child


def _walk_paint(paint, callback, seen: set[int]) -> None:
    """深度遍历 COLRv1 画笔树，对每个画笔节点调用 callback。

    不走进 PaintColrLayers 的全局 LayerList；那部分须由调用方按 FirstLayerIndex 另走。
    """
    pid = id(paint)
    if pid in seen:
        return
    seen.add(pid)
    callback(paint)
    for child in _iter_nested_paints(paint):
        _walk_paint(child, callback, seen)


def _remap_paint_palettes(paint, offset: int) -> None:
    """把画笔里的调色板索引整体平移（合并两家 CPAL 时用）。"""
    if hasattr(paint, "PaletteIndex"):
        pal = paint.PaletteIndex
        if pal != FOREGROUND_PALETTE_INDEX:
            paint.PaletteIndex = pal + offset
    line = getattr(paint, "ColorLine", None)
    if line is not None:
        for stop in line.ColorStop:
            if stop.PaletteIndex != FOREGROUND_PALETTE_INDEX:
                stop.PaletteIndex += offset


def _collect_paint_glyph_refs(
    paint,
    layer_list,
    glyphs_10: set[str],
    glyphs_11: set[str],
    seen_layers: set[int],
) -> None:
    """收集画笔树及 PaintColrLayers 所指 LayerList 切片里的字形名。

    Format 10（PaintGlyph）只取轮廓；Format 11（PaintColrGlyph）才是另一枚彩色基字。
    """

    def on_paint(p) -> None:
        fmt = getattr(p, "Format", None)
        if fmt == 10:
            name = getattr(p, "Glyph", None)
            if name:
                glyphs_10.add(name)
        elif fmt == 11:
            name = getattr(p, "Glyph", None)
            if name:
                glyphs_11.add(name)
        if fmt == 1 and layer_list is not None:
            first = int(p.FirstLayerIndex)
            num = int(p.NumLayers)
            for i in range(first, first + num):
                if i in seen_layers:
                    continue
                seen_layers.add(i)
                _collect_paint_glyph_refs(
                    layer_list.Paint[i], layer_list, glyphs_10, glyphs_11, seen_layers
                )

    _walk_paint(paint, on_paint, set())


def _glyf_closure(src_glyf, names: set[str]) -> set[str]:
    """把复合字形的构件一并纳入闭包。"""
    out = set(names)
    stack = list(names)
    while stack:
        n = stack.pop()
        glyph = src_glyf[n]
        if not glyph.isComposite():
            continue
        for comp in glyph.components:
            if comp.glyphName not in out:
                out.add(comp.glyphName)
                stack.append(comp.glyphName)
    return out


def _remap_paint_tree(
    paint,
    rename: dict[str, str],
    pal_offset: int,
    src_layers,
    dest_layers,
    slice_cache: dict[tuple[int, int], int],
) -> None:
    """就地重映射一份已 deepcopy 的画笔：调色板、字形名、PaintColrLayers 索引。

    Format 1 引用的 Noto LayerList 切片必须先在 dest 里占住连续槽位，再递归重映射
    切片内的嵌套 Format 1。若先递归拷内层再 extend 本层，FirstLayerIndex 会指到内层
    条目（美国旗只剩 2 条底，星星丢失）。同一 (FirstLayerIndex, NumLayers) 只拷一次。
    """

    def remap_one(p) -> None:
        _remap_paint_palettes(p, pal_offset)
        fmt = getattr(p, "Format", None)
        if fmt in (10, 11):
            old = getattr(p, "Glyph", None)
            if old is None or old not in rename:
                raise SystemExit(f"COLR 引用了未拷贝的字形：{old}")
            p.Glyph = rename[old]
        for child in _iter_nested_paints(p):
            remap_one(child)
        if fmt != 1:
            return
        key = (int(p.FirstLayerIndex), int(p.NumLayers))
        cached = slice_cache.get(key)
        if cached is not None:
            p.FirstLayerIndex = cached
            return
        first, num = key
        copied = [copy.deepcopy(src_layers.Paint[i]) for i in range(first, first + num)]
        new_first = len(dest_layers.Paint)
        dest_layers.Paint.extend(copied)
        slice_cache[key] = new_first
        p.FirstLayerIndex = new_first
        for i in range(new_first, new_first + num):
            remap_one(dest_layers.Paint[i])

    remap_one(paint)


RI_LO, RI_HI = 0x1F1E6, 0x1F1FF


def _find_ri_ligatures(noto: TTFont, ri_glyphs: set[str]) -> dict[str, list]:
    """在 Noto GSUB 里找「首字为区域指示符」的连字子表，返回 {首字形: [连字]}。"""
    gsub = noto["GSUB"].table
    for lk in gsub.LookupList.Lookup:
        if lk.LookupType != 4:
            continue
        for st in lk.SubTable:
            ligs = getattr(st, "ligatures", None) or {}
            if any(k in ri_glyphs for k in ligs):
                return {k: v for k, v in ligs.items() if k in ri_glyphs}
    raise SystemExit("Noto 中未找到区域指示符连字（LookupType 4）")


def _find_ri_liga_glyph(font: TTFont, first: str, component: str) -> str | None:
    """在 GSUB LookupType 4 里找 first+component 的连字字形名。"""
    for lu in font["GSUB"].table.LookupList.Lookup:
        if lu.LookupType != 4:
            continue
        for st in lu.SubTable:
            ligs = getattr(st, "ligatures", None) or {}
            if first not in ligs:
                continue
            for lig in ligs[first]:
                if list(lig.Component) == [component]:
                    return lig.LigGlyph
    return None


def _flag_colr_layers_are_paint_glyph(font: TTFont, first: str, component: str) -> bool:
    """🇨🇳 的 PaintColrLayers 必须指向全是 PaintGlyph 的层（Noto 旗面）。

    旧产物只拷了 BaseGlyph 画笔、没搬 LayerList，FirstLayerIndex 仍指向 Fluent 原层（夹杂 Format 12），
    浏览器会把旗画成区域指示符字母砖。
    """
    liga = _find_ri_liga_glyph(font, first, component)
    if not liga or "COLR" not in font:
        return False
    recs = {r.BaseGlyph: r.Paint for r in font["COLR"].table.BaseGlyphList.BaseGlyphPaintRecord}
    paint = recs.get(liga)
    ll = font["COLR"].table.LayerList
    if paint is None or ll is None:
        return False
    found = False
    ok = True

    def check(p) -> None:
        nonlocal found, ok
        if getattr(p, "Format", None) != 1:
            return
        found = True
        start, num = int(p.FirstLayerIndex), int(p.NumLayers)
        if start < 0 or start + num > len(ll.Paint):
            ok = False
            return
        for i in range(start, start + num):
            if getattr(ll.Paint[i], "Format", None) != 10:
                ok = False

    _walk_paint(paint, check, set())
    return found and ok


def _count_reachable_colr_layers(font: TTFont, first_cp: int, second_cp: int) -> int:
    """统计某面旗 PaintColrLayers 能走到的 LayerList 条目数（含嵌套）。"""
    cmap = font.getBestCmap()
    g_a, g_b = cmap.get(first_cp), cmap.get(second_cp)
    if not g_a or not g_b:
        return 0
    liga = _find_ri_liga_glyph(font, g_a, g_b)
    if not liga or "COLR" not in font:
        return 0
    recs = {r.BaseGlyph: r.Paint for r in font["COLR"].table.BaseGlyphList.BaseGlyphPaintRecord}
    paint = recs.get(liga)
    ll = font["COLR"].table.LayerList
    if paint is None or ll is None:
        return 0
    seen: set[int] = set()

    def walk(p) -> None:
        if getattr(p, "Format", None) == 1:
            start, num = int(p.FirstLayerIndex), int(p.NumLayers)
            for i in range(start, start + num):
                if i in seen or i < 0 or i >= len(ll.Paint):
                    continue
                seen.add(i)
                walk(ll.Paint[i])
        for child in _iter_nested_paints(p):
            walk(child)

    walk(paint)
    return len(seen)


def _count_ri_flag_ligatures(font: TTFont) -> int:
    """GSUB 中「两枚区域指示符 → 一面旗」的连字个数。"""
    cmap = font.getBestCmap()
    ri = {cmap[cp] for cp in range(RI_LO, RI_HI + 1) if cp in cmap}
    if not ri or "GSUB" not in font:
        return 0
    n = 0
    for lu in font["GSUB"].table.LookupList.Lookup:
        if lu.LookupType != 4:
            continue
        for st in lu.SubTable:
            ligs = getattr(st, "ligatures", None) or {}
            for first, lst in ligs.items():
                if first not in ri:
                    continue
                for lig in lst:
                    if lig.Component and all(c in ri for c in lig.Component):
                        n += 1
    return n


def merge_noto_flags(dest: TTFont) -> None:
    """规范 §6：Fluent 不收录国旗，用已缩到 upem 1000 的 Noto 补字。

    拷入 U+1F1E6–1F1FF 的 glyf / hmtx（1000）/ COLR 画笔（含 LayerList 切片）与 RI 连字；
    Noto 调色板条目追加到 CPAL，拷入画笔的 palette index 重映射（0xFFFF 除外）；
    国旗 lookup 挂到 ccmp 最前；不拷 Noto 的 ASCII，不覆盖 Fluent 已有码位。
    """
    product = DIST / "XiaoheiziEmoji-Regular.ttf"
    if product.exists():
        # 与谷歌档同一份已缩到 1000 的 Noto，避免再 fit 一遍
        print("flag source", product.name)
        noto = TTFont(product, recalcBBoxes=True, recalcTimestamp=False)
    else:
        noto = TTFont(NOTO_EMOJI, recalcBBoxes=True, recalcTimestamp=False)
        for tag in ("CBDT", "CBLC", "SVG "):
            if tag in noto:
                del noto[tag]
        fit_emoji_to_em(noto)

    ncmap = noto.getBestCmap()
    missing = [cp for cp in range(RI_LO, RI_HI + 1) if cp not in ncmap]
    if missing:
        raise SystemExit(f"Noto 缺少区域指示符：{[f'U+{c:04X}' for c in missing]}")
    ri_glyphs = {ncmap[cp] for cp in range(RI_LO, RI_HI + 1)}
    ri_ligs = _find_ri_ligatures(noto, ri_glyphs)

    lig_entries: dict[str, list[tuple[str, tuple[str, ...]]]] = {}
    lig_glyphs: set[str] = set()
    for first, ligs in ri_ligs.items():
        for lig in ligs:
            if all(c in ri_glyphs for c in lig.Component):
                lig_entries.setdefault(first, []).append(
                    (lig.LigGlyph, tuple(lig.Component))
                )
                lig_glyphs.add(lig.LigGlyph)

    need = ri_glyphs | lig_glyphs
    ncolr = noto["COLR"].table
    nrecs = {r.BaseGlyph: r for r in ncolr.BaseGlyphList.BaseGlyphPaintRecord}
    if len(need) != len(need & nrecs.keys()):
        raise SystemExit("Noto COLR 缺少旗字形记录")

    colr_need = set(ri_glyphs | lig_glyphs)
    pending = set(colr_need)
    outline_refs: set[str] = set()
    seen_layers: set[int] = set()
    while pending:
        g = pending.pop()
        if g not in nrecs:
            continue
        acc10: set[str] = set()
        acc11: set[str] = set()
        _collect_paint_glyph_refs(nrecs[g].Paint, ncolr.LayerList, acc10, acc11, seen_layers)
        outline_refs |= acc10
        extra11 = acc11 - colr_need
        if extra11:
            colr_need |= extra11
            pending |= extra11
    need = _glyf_closure(noto["glyf"], colr_need | outline_refs)

    rename = {n: NOTO_PREFIX + n.replace(".", "_") for n in need}

    dst_glyf = dest["glyf"]
    dst_hmtx = dest["hmtx"]
    src_glyf = noto["glyf"]
    order = list(dest.getGlyphOrder())
    for old in sorted(need):
        new = rename[old]
        glyph = copy.deepcopy(src_glyf[old])
        if glyph.isComposite():
            for comp in glyph.components:
                comp.glyphName = rename[comp.glyphName]
        dst_glyf[new] = glyph
        dst_hmtx[new] = noto["hmtx"][old]
        order.append(new)
    dest.setGlyphOrder(order)
    dest["maxp"].numGlyphs = len(order)

    # cmap：区域指示符在增补平面，只进 format 12/13 子表；不碰 Fluent 已有码位
    for table in dest["cmap"].tables:
        if not table.isUnicode() or table.format not in (12, 13):
            continue
        for cp in range(RI_LO, RI_HI + 1):
            if cp not in table.cmap:
                table.cmap[cp] = rename[ncmap[cp]]
        table.data = None

    # CPAL：追加 Noto 调色板条目，拷入画笔的 palette index 平移
    dcpal = dest["CPAL"]
    ncpal = noto["CPAL"]
    offset = dcpal.numPaletteEntries
    noto_entries = list(ncpal.palettes[0])
    dcpal.palettes = [list(pal) + noto_entries for pal in dcpal.palettes]
    dcpal.numPaletteEntries = len(dcpal.palettes[0])

    # COLR：拷入旗字形的画笔记录；PaintColrLayers 的切片追加到 LayerList 并重映射索引
    dcolr = dest["COLR"].table
    if dcolr.LayerList is None:
        dcolr.LayerList = ot.LayerList()
        dcolr.LayerList.Paint = []
    slice_cache: dict[tuple[int, int], int] = {}
    layers_before = len(dcolr.LayerList.Paint)

    for old in colr_need:
        if old not in nrecs:
            continue  # PaintGlyph 引用的辅助字形没有自己的画笔记录，只带轮廓
        rec = copy.deepcopy(nrecs[old])
        rec.BaseGlyph = rename[old]
        _remap_paint_tree(
            rec.Paint,
            rename,
            offset,
            ncolr.LayerList,
            dcolr.LayerList,
            slice_cache,
        )
        dcolr.BaseGlyphList.BaseGlyphPaintRecord.append(rec)
    if ncolr.ClipList is not None:
        if dcolr.ClipList is None:
            dcolr.ClipList = ot.ClipList()
            dcolr.ClipList.format = 1
            dcolr.ClipList.clips = {}
        for key, box in ncolr.ClipList.clips.items():
            if isinstance(key, str) and key in rename:
                dcolr.ClipList.clips[rename[key]] = copy.deepcopy(box)
            elif isinstance(key, tuple):
                mapped = tuple(rename[k] for k in key if k in rename)
                if len(mapped) == len(key):
                    dcolr.ClipList.clips[mapped] = copy.deepcopy(box)

    # GSUB：新建 LookupType 4 连字，插到现有 ccmp 最前（与 Noto 一致）
    subtable = ot.LigatureSubst()
    subtable.ligatures = {}
    for first, entries in lig_entries.items():
        ligs = []
        for lig_name, comps in entries:
            lig = ot.Ligature()
            lig.LigGlyph = rename[lig_name]
            lig.Component = [rename[c] for c in comps]
            ligs.append(lig)
        subtable.ligatures[rename[first]] = ligs
    lookup = ot.Lookup()
    lookup.LookupType = 4
    lookup.LookupFlag = 0
    lookup.SubTableCount = 1
    lookup.SubTable = [subtable]
    gsub = dest["GSUB"].table
    new_idx = len(gsub.LookupList.Lookup)
    gsub.LookupList.Lookup.append(lookup)
    gsub.LookupList.LookupCount = new_idx + 1
    ccmp_found = False
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != "ccmp":
            continue
        fr.Feature.LookupListIndex.insert(0, new_idx)
        if hasattr(fr.Feature, "LookupCount"):
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
        ccmp_found = True
    if not ccmp_found:
        raise SystemExit("Fluent GSUB 无 ccmp，无法挂国旗连字")

    if not _flag_colr_layers_are_paint_glyph(dest, rename[ncmap[0x1F1E8]], rename[ncmap[0x1F1F3]]):
        raise SystemExit("国旗 COLR LayerList 重映射失败：🇨🇳 仍未指向 PaintGlyph 层")
    us_layers = _count_reachable_colr_layers(dest, 0x1F1FA, 0x1F1F8)
    if us_layers < 40:
        raise SystemExit(f"国旗嵌套 LayerList 重映射失败：🇺🇸 只有 {us_layers} 层（应含星条）")

    noto.close()
    print(
        "merged noto flags:",
        len(need),
        "glyphs;",
        len(colr_need),
        "colr bases;",
        len(lig_glyphs),
        "ligatures;",
        len(dcolr.LayerList.Paint) - layers_before,
        "colr layers",
    )


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
    if variant.get("flags_from_noto"):
        merge_noto_flags(font)
    set_emoji_names(font, variant)
    sanitize_for_ots(font)
    out = DIST / variant["out_name"]
    print("save", out, "scale", round(scale, 6))
    font.save(out)
    if variant.get("flags_from_noto"):
        check = TTFont(out)
        cmap = check.getBestCmap()
        ok = _flag_colr_layers_are_paint_glyph(check, cmap[0x1F1E8], cmap[0x1F1F3])
        us_layers = _count_reachable_colr_layers(check, 0x1F1FA, 0x1F1F8)
        check.close()
        if not ok or us_layers < 40:
            raise SystemExit(f"写出后国旗 COLR 仍不合格（🇺🇸 {us_layers} 层）")
    return out


def emoji_variant_needs_rebuild(variant: dict, path: Path) -> bool:
    if not path.exists():
        return True
    font = TTFont(path)
    try:
        upem = font["head"].unitsPerEm
        cmap = font.getBestCmap()
        if upem != TARGET_UPEM:
            return True
        # 数字不应出现在表情 cmap；⚠ 这类可覆盖符号必须保留
        if 0x30 in cmap or 0x26A0 not in cmap:
            return True
        # 两套配套字体都必须有区域指示符（立体套由 Noto 补）
        if 0x1F1E8 not in cmap:
            return True
        if variant.get("flags_from_noto"):
            g_c = cmap.get(0x1F1E8)
            g_n = cmap.get(0x1F1F3)
            if not g_c or not g_n:
                return True
            if not _flag_colr_layers_are_paint_glyph(font, g_c, g_n):
                return True
            if _count_reachable_colr_layers(font, 0x1F1FA, 0x1F1F8) < 40:
                return True
        return False
    finally:
        font.close()


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


def overlay_source_han(base: TTFont, shs: TTFont) -> dict[str, str]:
    """规范 §2：思源有的例外表码位覆盖更纱/JBM 半格稿。思源是 CFF，转 TrueType 后保持 1 em。"""
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    src_cmap = shs.getBestCmap()
    unicodes: set[int] = set()
    for lo, hi in SOURCE_HAN_OVERLAY_RANGES:
        for cp in range(lo, hi + 1):
            if _is_assigned(cp) and cp in src_cmap:
                unicodes.add(cp)
    missing = assigned_enclosed_set() - unicodes
    if missing:
        raise SystemExit(f"思源缺少带圈字母数字码位：{sorted(f'U+{c:04X}' for c in missing)}")
    names = collect_names(shs, unicodes)
    rename = {n: SOURCE_HAN_PREFIX + n.replace(".", "_") for n in names}

    src_glyphset = shs.getGlyphSet()
    dst_glyf = base["glyf"]
    dst_hmtx = base["hmtx"]
    src_hmtx = shs["hmtx"]
    shs_glyf = shs["glyf"] if "glyf" in shs else None
    scale = TARGET_UPEM / shs["head"].unitsPerEm
    order = list(base.getGlyphOrder())

    for old in names:
        new = rename[old]
        src_glyph = shs_glyf[old] if shs_glyf is not None else None
        if src_glyph is not None and src_glyph.isComposite():
            raw = copy.deepcopy(src_glyph)
            for comp in raw.components:
                comp.glyphName = rename[comp.glyphName]
                comp.x = round(comp.x * scale)
                comp.y = round(comp.y * scale)
            dst_glyf[new] = raw
        else:
            pen = TTGlyphPen(dst_glyf)
            cu2qu = Cu2QuPen(pen, max_err=1.0, reverse_direction=True)
            src_glyphset[old].draw(cu2qu)
            dst_glyf[new] = pen.glyph()
            if abs(scale - 1.0) > 1e-6:
                scale_glyph(dst_glyf[new], dst_glyf, scale, scale)
        adv, lsb = src_hmtx[old]
        dst_hmtx[new] = (round(adv * scale), round(lsb * scale))
        order.append(new)

    base.setGlyphOrder(order)
    base["maxp"].numGlyphs = len(order)
    source: dict[str, str] = {}
    for table in base["cmap"].tables:
        if table.format == 14 or not table.isUnicode():
            continue
        for cp in unicodes:
            table.cmap[cp] = rename[src_cmap[cp]]
            source[f"U+{cp:04X}"] = "source-han-sans"
        table.data = None
    print("overlay source han", len(unicodes))
    return source


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


@cache
def assigned_enclosed_set() -> frozenset[int]:
    """规范 §2 例外表：U+2460–24FF 已分配码位。"""
    return frozenset(
        cp for cp in range(ENCLOSED_ALNUM[0], ENCLOSED_ALNUM[1] + 1) if _is_assigned(cp)
    )


@cache
def source_han_overlay_set() -> frozenset[int]:
    """思源实际有、且落在 §2 覆盖区的码位。"""
    font = TTFont(SOURCE_HAN)
    try:
        cmap = font.getBestCmap() or {}
    finally:
        font.close()
    out: set[int] = set()
    for lo, hi in SOURCE_HAN_OVERLAY_RANGES:
        for cp in range(lo, hi + 1):
            if _is_assigned(cp) and cp in cmap:
                out.add(cp)
    return frozenset(out)


def is_fullwidth_exception(cp: int) -> bool:
    """规范 §2 例外表：1 em。"""
    if ENCLOSED_ALNUM[0] <= cp <= ENCLOSED_ALNUM[1] and _is_assigned(cp):
        return True
    if any(lo <= cp <= hi for lo, hi in STRETCH_TO_EM_RANGES):
        return True
    if cp in STRETCH_TO_EM_CPS:
        return True
    if cp in source_han_overlay_set():
        return True
    return False


def expected_advance(cp: int, upem: int) -> int:
    """名称里的 em 按排版长度；§2 例外表 1 em；
    未列入例外的 Emoji_Presentation 按半宽；其余走 UAX #11。

    表情字体全宽 1 em，不走本函数。禁止从 Regular 剔除 EP。
    Mn/Me 见 UAX #11 §6.2；Cf/Cc 按 POSIX wcwidth 不计列。
    """
    if cp in NAMED_EM_RATIO:
        return round(NAMED_EM_RATIO[cp] * upem)
    if is_fullwidth_exception(cp):
        return upem
    if is_emoji_presentation(cp):
        return upem // 2
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


def _simple_contours_where(src, glyf, keep) -> tuple[list, list, list]:
    """从简单字形里挑轮廓。keep(ymin, ymax) 为真则保留。"""
    coords, ends, flags = src.getCoordinates(glyf)
    out_c: list = []
    out_f: list = []
    out_e: list = []
    prev = 0
    for end in ends:
        pts = list(coords[prev : end + 1])
        ys = [p[1] for p in pts]
        if keep(min(ys), max(ys)):
            out_c.extend(pts)
            out_f.extend(list(flags[prev : end + 1]))
            out_e.append(len(out_c) - 1)
        prev = end + 1
    return out_c, out_f, out_e


def compose_square_paatu(font: TTFont, sources: dict[str, str]) -> None:
    """规范 §3：U+332C ㌬。从 ㌫ 拆 パ 与 ー，从 ㌪ 拆 ツ，不缩全角假名。"""
    from array import array

    from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates

    cp = 0x332C
    haitz = 0x332A  # ㌪ ハイツ，左下是平方词 ツ
    paasento = 0x332B  # ㌫ パーセント，上半是平方词 パ 与 ー
    cmap = font.getBestCmap()
    if haitz not in cmap or paasento not in cmap:
        raise SystemExit("合成 ㌬ 需要 cmap 含 ㌪ / ㌫")
    glyf = font["glyf"]
    pa_bar_c, pa_bar_f, pa_bar_e = _simple_contours_where(
        glyf[cmap[paasento]], glyf, lambda ymin, ymax: ymin >= 400
    )
    tsu_c, tsu_f, tsu_e = _simple_contours_where(
        glyf[cmap[haitz]], glyf, lambda ymin, ymax: ymax < 400
    )
    if len(pa_bar_e) != 5:
        raise SystemExit(f"㌫ 上半应是 パ(4)+ー(1)，实际 {len(pa_bar_e)} 条轮廓")
    if len(tsu_e) != 3:
        raise SystemExit(f"㌪ 下半应是 ツ 的 3 条轮廓，实际 {len(tsu_e)}")
    coords = pa_bar_c + tsu_c
    flags = pa_bar_f + tsu_f
    ends = list(pa_bar_e) + [e + len(pa_bar_c) for e in tsu_e]
    glyph = Glyph()
    glyph.numberOfContours = len(ends)
    glyph.coordinates = GlyphCoordinates(coords)
    glyph.endPtsOfContours = ends
    glyph.flags = array("B", [int(f) & 0x07 for f in flags])
    glyph.program = empty_program()
    glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax = glyph.coordinates.calcIntBounds()
    name = "composed.uni332C"
    hmtx = font["hmtx"]
    order = list(font.getGlyphOrder())
    glyf[name] = glyph
    lsb = min(p[0] for p in coords)
    hmtx[name] = (TARGET_UPEM, round(lsb))
    if name not in order:
        order.append(name)
    font.setGlyphOrder(order)
    font["maxp"].numGlyphs = len(order)
    for table in font["cmap"].tables:
        if table.isUnicode() and table.format != 14:
            table.cmap[cp] = name
            table.data = None
    sources[f"U+{cp:04X}"] = "composed-square"
    print("composed square paatu U+332C from ㌪/㌫")


def load_emoji_stats(emoji_ttfs: list[Path] | None) -> list[tuple[str, dict, int]]:
    out: list[tuple[str, dict, int]] = []
    if not emoji_ttfs:
        return out
    for variant, path in zip(EMOJI_VARIANTS, emoji_ttfs):
        if not path.exists():
            continue
        font = TTFont(path)
        try:
            out.append(
                (variant["family_zh"], font.getBestCmap(), _count_ri_flag_ligatures(font))
            )
        finally:
            font.close()
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
            "sourceHanSans": "Source Han Sans SC Regular（带圈字母数字 §2 例外表）",
        },
    }
    DIST.mkdir(parents=True, exist_ok=True)
    product = product_coverage(cmap, hmtx=hmtx, sources=sources, upem=upem)
    product["emoji"] = emoji_coverage(cmap, load_emoji_stats(emoji_ttfs))
    have = {row["name"] for row in product["blocks"]}
    missing_req = [name for name, _lo, _hi in REQUIRED_BLOCKS if name not in have]
    if missing_req:
        raise SystemExit("必测区块未出现在覆盖表：" + ", ".join(missing_req))
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
    ]
    (DIST / "coverage-blocks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return violations


def build_glyph_catalog(cmap: dict[int, str]) -> tuple[dict, list[int]]:
    """规范 §4：图鉴数据。覆盖率低且超过一页的区块只列已收录。"""
    blocks: list[dict] = []
    subset: list[int] = []
    for name, lo, hi in unicode_block_defs():
        assigned = [cp for cp in range(lo, hi + 1) if _is_assigned(cp)]
        if not assigned:
            continue
        mapped = [cp for cp in assigned if cp in cmap]
        total = len(assigned)
        got = len(mapped)
        sparse = total > CATALOG_PAGE_SIZE and total > 0 and got / total < 0.05
        shown = mapped if sparse else assigned
        missing = [] if sparse else [cp for cp in shown if cp not in cmap]
        blocks.append(
            {
                "name": name,
                "nameZh": block_zh_name(name),
                "range": f"U+{lo:04X}–{hi:04X}",
                "assigned": total,
                "mapped": got,
                "sparse": sparse,
                "chars": "".join(chr(cp) for cp in shown),
                "missing": missing,
            }
        )
        subset.extend(mapped)
    return {
        "pageSize": CATALOG_PAGE_SIZE,
        "cols": CATALOG_COLS,
        "rows": CATALOG_ROWS,
        "blocks": blocks,
    }, subset


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
    product["emoji"] = emoji_coverage(cmap, load_emoji_stats(emoji_ttfs))
    catalog, catalog_cps = build_glyph_catalog(cmap)
    product["catalog"] = catalog
    payload = {
        "unicodeVersion": product["unicodeVersion"],
        "overview": product["overview"],
        "cjk": product["cjk"],
        "unicode": product["unicode"],
        "blocks": product["blocks"],
        "emoji": product["emoji"],
        "catalog": product["catalog"],
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
        unicodes=list(range(0x20, 0x7F)) + [0xA0] + catalog_cps,
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
            esub.populate(text=html, unicodes=catalog_cps)
            esub.subset(etiny)
            etiny.save(DIST / variant["preview_name"])


def main() -> None:
    if not SARASA.exists() or not JBM.exists():
        raise SystemExit(f"缺少上游字体：{SARASA} 或 {JBM}")
    if not SOURCE_HAN.exists():
        raise SystemExit(f"缺少思源黑体：{SOURCE_HAN}；请先运行 python scripts/fetch-vendor.py")
    DIST.mkdir(parents=True, exist_ok=True)
    print("load sarasa")
    base = TTFont(SARASA, recalcBBoxes=True, recalcTimestamp=False)
    print("load jetbrains")
    jbm = TTFont(JBM, recalcBBoxes=True, recalcTimestamp=False)
    print("overlay")
    sources = overlay_jbm(base, jbm)
    print("load source han")
    shs = TTFont(SOURCE_HAN, recalcTimestamp=False)
    sources.update(overlay_source_han(base, shs))
    shs.close()
    for tag in ("vmtx", "vhea", "VORG"):
        if tag in base:
            del base[tag]
    strip_ligatures(base)
    apply_uax11_metrics(base)
    ensure_multi_em_dashes(base)
    compose_square_paatu(base, sources)
    set_names(base)
    sanitize_for_ots(base)
    regular_out = DIST / "XiaoheiziMono-Regular.ttf"
    print("save", regular_out)
    base.save(regular_out)
    emoji_outs: list[Path] = []
    for variant in EMOJI_VARIANTS:
        emoji_out = DIST / variant["out_name"]
        if emoji_variant_needs_rebuild(variant, emoji_out):
            emoji_outs.append(build_emoji_variant(variant))
        else:
            print("reuse emoji", emoji_out.name)
            emoji_outs.append(emoji_out)
    print("coverage")
    built = TTFont(regular_out)
    violations = write_coverage(built, sources, emoji_outs)
    write_preview(regular_out, emoji_outs)
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
    # §2 例外表抽查：① 推进 1 em 且轮廓来自思源（宽 ≥ 0.8 em，不是半格稿的 436）。
    # 注意：post 3.0 不存字形名，重读后名字会按 cmap 重建，不能用名字前缀判断。
    from fontTools.pens.boundsPen import BoundsPen

    pen = BoundsPen(built.getGlyphSet())
    built.getGlyphSet()[a[0x2460]].draw(pen)
    circled_w = pen.bounds[2] - pen.bounds[0] if pen.bounds else 0
    print("circled1", h[a[0x2460]][0], f"width={circled_w:.0f}", "warn", h[a[0x26A0]][0])
    if h[a[0x2460]][0] != TARGET_UPEM or circled_w < TARGET_UPEM * 0.8:
        raise SystemExit("U+2460 例外表未生效：推进或轮廓宽度不合格")
    if h[a[0x26A0]][0] != TARGET_UPEM:
        raise SystemExit("U+26A0 思源覆盖后须为 1 em")
    print("corp", h[a[0x337F]][0], "paatu", h[a[0x332C]][0])
    if 0x332C not in a:
        raise SystemExit("U+332C ㌬ 须由 ㌪ / ㌫ 拆件合成")
    if h[a[0x332C]][0] != TARGET_UPEM:
        raise SystemExit("U+332C 须为 1 em")

    def _right_bar_height(cp: int) -> float | None:
        g = built["glyf"][a[cp]]
        coords, ends, _ = g.getCoordinates(built["glyf"])
        prev = 0
        best = None
        for end in ends:
            pts = coords[prev : end + 1]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            prev = end + 1
            if min(xs) >= 500 and max(xs) - min(xs) > 300:
                height = max(ys) - min(ys)
                if best is None or height < best:
                    best = height
        return best

    bar_src = _right_bar_height(0x332B)
    bar_dst = _right_bar_height(0x332C)
    if bar_src is None or bar_dst is None or abs(bar_dst - bar_src) > 2:
        raise SystemExit(f"㌬ 横杠高度 {bar_dst} 应与 ㌫ {bar_src} 一致")
    print("emdash", h[a[0x2014]][0], "emspace", h[a[0x2003]][0], "twoem", h[a[0x2E3A]][0], "threeem", h[a[0x2E3B]][0])
    if 0x2705 not in a or 0x1F0CF not in a:
        raise SystemExit("Regular 须保留 U+2705 与 U+1F0CF，不得剔除 EP")
    if h[a[0x2705]][0] != TARGET_UPEM // 2:
        raise SystemExit("U+2705 思源无此字，Regular 仍须 0.5 em")
    if h[a[0x1F0CF]][0] != TARGET_UPEM // 2:
        raise SystemExit("U+1F0CF 扑克不拉宽，Regular 须 0.5 em")
    if 0x1F201 in a and h[a[0x1F201]][0] != TARGET_UPEM:
        raise SystemExit("U+1F201 表意例外须为 1 em")
    if 0x1F100 in a and h[a[0x1F100]][0] != TARGET_UPEM:
        raise SystemExit("带圈字母数字补充须拉到 1 em")
    print(
        "check-ep",
        h[a[0x2705]][0],
        "joker",
        h[a[0x1F0CF]][0],
        "koko",
        h[a[0x1F201]][0] if 0x1F201 in a else None,
        "alnum-sup",
        h[a[0x1F100]][0] if 0x1F100 in a else None,
    )
    print("done", regular_out, "bytes", regular_out.stat().st_size)


if __name__ == "__main__":
    main()
