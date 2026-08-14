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

# 规范 §6：配套表情字体，不并入 Regular
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

SCALE = 500 / 600  # JBM 0.6em → 半个汉字
PREFIX = "jbm."
BMP_DENOM = 65535  # 规范 §4.2：BMP 习惯分母（U+0000–U+FFFF）


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


def product_coverage(cmap: dict[int, str]) -> dict:
    """规范 §4.2 产品向分集表。"""
    bmp_mapped = sum(1 for cp in cmap if cp <= 0xFFFF)
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
        ("希腊和科普特字母", "U+0370–03FF", assigned_set(0x0370, 0x03FF)),
        ("泰文", "U+0E00–0E7F", assigned_set(0x0E00, 0x0E7F)),
    ]

    def pack(name: str, note: str, universe) -> dict:
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

    bmp_value = pct_value(bmp_mapped, BMP_DENOM)
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
            }
        ],
        "cjk": [pack(n, note, u) for n, note, u in cjk],
        "unicode": [pack(n, note, u) for n, note, u in unicode_rows],
    }


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
    return lines


def empty_program() -> Program:
    prog = Program()
    prog.fromBytecode(b"")
    return prog


def in_jbm_ranges(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in JBM_RANGES)


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
    """把最常见的非零推进宽度收到 1 em，使一枚 emoji 占两格。"""
    from collections import Counter

    upem = font["head"].unitsPerEm
    metrics = font["hmtx"].metrics
    counts = Counter(adv for adv, _lsb in metrics.values() if adv > 0)
    typical, _n = counts.most_common(1)[0]
    scale = upem / typical
    glyf = font["glyf"] if "glyf" in font else None
    for name in font.getGlyphOrder():
        if glyf is not None:
            scale_glyph(glyf[name], glyf, scale, scale)
        adv, lsb = metrics[name]
        if adv == 0:
            metrics[name] = (0, _scale_int(lsb, scale))
        else:
            metrics[name] = (upem, _scale_int(lsb, scale))
    scale_colr_paints(font, scale)
    hhea = font["hhea"]
    hhea.ascent = _scale_int(hhea.ascent, scale)
    hhea.descent = _scale_int(hhea.descent, scale)
    hhea.advanceWidthMax = upem
    if "vmtx" in font:
        for name, (adv, tsb) in list(font["vmtx"].metrics.items()):
            font["vmtx"].metrics[name] = (
                _scale_int(adv, scale) if adv else 0,
                _scale_int(tsb, scale),
            )
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
    set_emoji_names(font, variant)
    sanitize_for_ots(font)
    out = DIST / variant["out_name"]
    print("save", out, "scale", round(scale, 6))
    font.save(out)
    return out


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


def expected_cells(cp: int, advance: int, upem: int) -> int | None:
    cat = unicodedata.category(chr(cp)) if cp < 0x110000 else "Cn"
    if cat in {"Mn", "Me"}:
        return 0
    ratio = advance / upem
    if abs(ratio - 0.5) <= 0.002:
        return 1
    if abs(ratio - 1.0) <= 0.002:
        return 2
    if advance == 0:
        return 0
    return None


def write_coverage(font: TTFont, sources: dict[str, str]) -> list[dict]:
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upem = font["head"].unitsPerEm
    violations: list[dict] = []
    for cp, gname in cmap.items():
        adv = hmtx[gname][0]
        if expected_cells(cp, adv, upem) is None:
            violations.append({"cp": f"U+{cp:04X}", "advance": adv})

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
            cells.add("0" if c == 0 else ("1" if c == 1 else ("2" if c == 2 else "?")))
            origin.add(sources.get(f"U+{cp:04X}", "sarasa"))
        if cells <= {"1"}:
            grid = "1"
        elif cells <= {"2"}:
            grid = "2"
        elif cells <= {"1", "2"}:
            grid = "混"
        else:
            grid = ",".join(sorted(cells))
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
    product = product_coverage(tiny.getBestCmap())
    payload = {
        "unicodeVersion": product["unicodeVersion"],
        "overview": product["overview"],
        "cjk": product["cjk"],
        "unicode": product["unicode"],
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
    sub.populate(text=html + js, unicodes=range(0x20, 0x7F))
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
    set_names(base)
    sanitize_for_ots(base)
    out = DIST / "XiaoheiziMono-Regular.ttf"
    print("save", out)
    base.save(out)
    print("coverage")
    built = TTFont(out)
    violations = write_coverage(built, sources)
    emoji_outs = build_all_emoji()
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
    print("done", out, "bytes", out.stat().st_size)


if __name__ == "__main__":
    main()
