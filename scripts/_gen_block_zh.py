"""一次性生成 unicode-block-zh.json。运行时不依赖本脚本。"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from zhconv import convert

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "unicode-block-zh.json"
UA = {"User-Agent": "xiaoheizi-mono-block-zh/0.1"}

# 图鉴里已经用过的通行译法，覆盖字嗨「CJK统合…」一类写法。
OVERRIDE = {
    "CJK Unified Ideographs": "中日韩统一表意文字",
    "CJK Unified Ideographs Extension A": "中日韩统一表意文字扩展区A",
    "CJK Unified Ideographs Extension B": "中日韩统一表意文字扩展区B",
    "CJK Unified Ideographs Extension C": "中日韩统一表意文字扩展区C",
    "CJK Unified Ideographs Extension D": "中日韩统一表意文字扩展区D",
    "CJK Unified Ideographs Extension E": "中日韩统一表意文字扩展区E",
    "CJK Unified Ideographs Extension F": "中日韩统一表意文字扩展区F",
    "CJK Unified Ideographs Extension G": "中日韩统一表意文字扩展区G",
    "CJK Unified Ideographs Extension H": "中日韩统一表意文字扩展区H",
    "CJK Unified Ideographs Extension I": "中日韩统一表意文字扩展区I",
    "CJK Unified Ideographs Extension J": "中日韩统一表意文字扩展区J",
    "CJK Symbols and Punctuation": "中日韩符号和标点",
    "CJK Compatibility": "中日韩兼容字符",
    "CJK Compatibility Ideographs": "中日韩兼容表意文字",
    "CJK Compatibility Ideographs Supplement": "中日韩兼容表意文字补充",
    "CJK Compatibility Forms": "中日韩兼容形式",
    "CJK Radicals Supplement": "中日韩部首补充",
    "CJK Strokes": "中日韩笔画",
    "Enclosed CJK Letters and Months": "带圈中日韩字母和月份",
    "Halfwidth and Fullwidth Forms": "半角及全角形式",
    "Enclosed Alphanumerics": "带圈字母数字",
    "Enclosed Alphanumeric Supplement": "带圈字母数字补充",
    "Enclosed Ideographic Supplement": "带圈表意文字补充",
    "NKo": "西非书面文字",
    "Todhri": "托特里",
    "Sidetic": "西代",
    "Garay": "加莱",
    "Tulu-Tigalari": "图卢-蒂加拉里",
    "Myanmar Extended-C": "缅文扩充丙",
    "Sharada Supplement": "沙勒德补充",
    "Sunuwar": "苏努瓦尔",
    "Tolong Siki": "托隆希基",
    "Egyptian Hieroglyphs Extended-A": "埃及圣书体扩充甲",
    "Gurung Khema": "古隆凯马",
    "Kirat Rai": "基拉特拉伊",
    "Beria Erfe": "贝里亚埃尔菲",
    "Tangut Components Supplement": "西夏偏旁补充",
    "Symbols for Legacy Computing Supplement": "遗留电脑符号补充",
    "Miscellaneous Symbols Supplement": "杂项符号补充",
    "Ol Onal": "奥纳尔",
    "Tai Yo": "傣攸",
    "Box Drawing": "制表符",
    "Block Elements": "方块元素",
    "Geometric Shapes": "几何图形",
    "Miscellaneous Symbols": "杂项符号",
    "Miscellaneous Technical": "杂项技术用字符",
    "Miscellaneous Symbols and Arrows": "杂项符号和箭头",
    "Dingbats": "印刷符号",
    "General Punctuation": "通用标点",
    "Letterlike Symbols": "类字符号",
    "Number Forms": "数字形式",
    "Arrows": "箭头",
    "Mathematical Operators": "数学运算符",
    "Currency Symbols": "货币符号",
    "Basic Latin": "基本拉丁字母",
    "Latin-1 Supplement": "拉丁字母补充-1",
    "Hangul Syllables": "谚文音节",
    "Hiragana": "平假名",
    "Katakana": "片假名",
    "Bopomofo": "注音符号",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def parse_zihi(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    pat = re.compile(
        r"\|\[(?:U\+)?[0-9A-F]+ – [0-9A-F]+\][^|]*\|([^|]+)\|([^|]+)\|"
    )
    for zh, en in pat.findall(text):
        zh = re.sub(r"\[PDF表格\].*", "", zh).strip()
        en = en.strip().replace("N'Ko", "NKo").replace("Nüshu", "Nushu")
        if zh and en:
            out[en] = convert(zh, "zh-cn")
    return out


def parse_my1l(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if ".." not in line or ";" not in line or line.startswith("#"):
            continue
        _, rest = line.split(";", 1)
        parts = rest.split("|")
        if len(parts) < 2:
            continue
        en = parts[-1].strip()
        zh = parts[0].strip()
        zh = re.sub(r"^[0-9A-Fa-fg]+", "", zh)
        zh = zh.strip()
        if en and zh:
            out[en] = zh
    return out


def polish(en: str, zh: str) -> str:
    if en in OVERRIDE:
        return OVERRIDE[en]
    zh = zh.replace("CJK统合表意文字", "中日韩统一表意文字")
    zh = zh.replace("CJK兼容", "中日韩兼容")
    return zh


def main() -> None:
    zihi = parse_zihi(fetch("https://zi-hi.com/sp/uni/Blocks"))
    my1l = parse_my1l(
        fetch("https://raw.githubusercontent.com/MY1L/Unicode/master/Blocks/Blocks.txt")
    )
    from fontTools.unicodedata.Blocks import VALUES

    merged: dict[str, str] = {}
    missing: list[str] = []
    for en in VALUES:
        if en == "No_Block":
            continue
        zh = (
            zihi.get(en)
            or my1l.get(en)
            or my1l.get(en.replace("Nushu", "Nüshu"))
            or zihi.get(en.replace("NKo", "N'Ko"))
        )
        if not zh:
            zh = en
        merged[en] = polish(en, zh)
        if merged[en] == en:
            missing.append(en)
    OUT.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote", OUT, "entries", len(merged), "missing", len(missing))
    for name in missing[:30]:
        print("  ", name)


if __name__ == "__main__":
    main()
