# Copyright (c) 2026 小黑字
# SPDX-License-Identifier: MIT

"""下载构建所需的上游字体到 vendor/（不入库）。已存在则跳过。"""

from __future__ import annotations

import shutil
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor"

JBM_ZIP = "https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip"
SARASA_7Z = (
    "https://github.com/be5invis/Sarasa-Gothic/releases/download/v1.0.40/"
    "SarasaFixedSC-TTF-Unhinted-1.0.40.7z"
)
# 2026-09 起上游把 COLRv1 挪到 2D/fonts/，旧的 fonts/ 路径会 404。
NOTO_COLR = "https://github.com/googlefonts/noto-emoji/raw/main/2D/fonts/Noto-COLRv1.ttf"
NOTO_OFL = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/2D/fonts/LICENSE"
FLUENT_TTF = (
    "https://github.com/tetunori/fluent-emoji-webfont/raw/main/dist/FluentEmojiColor.ttf"
)
FLUENT_MIT_MS = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/LICENSE"
FLUENT_MIT_BUILD = "https://raw.githubusercontent.com/tetunori/fluent-emoji-webfont/main/LICENSE"
# 规范 §2 例外表 / §3：带圈字母数字 U+2460–24FF 取思源黑体 SC Regular（单一 OTF，非 SuperOTC）
SOURCE_HAN_OTF = (
    "https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/"
    "SourceHanSansSC-Regular.otf"
)
SOURCE_HAN_LIGHT_OTF = (
    "https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/"
    "SourceHanSansSC-Light.otf"
)

JBM_DIR = VENDOR / "jetbrains-mono" / "fonts" / "ttf"
JBM_TTF = JBM_DIR / "JetBrainsMonoNL-Regular.ttf"
JBM_LIGHT = JBM_DIR / "JetBrainsMonoNL-Light.ttf"
SARASA_DIR = VENDOR / "sarasa-fixed-sc"
SARASA_TTF = SARASA_DIR / "SarasaFixedSC-Regular.ttf"
SARASA_LIGHT = SARASA_DIR / "SarasaFixedSC-Light.ttf"
NOTO_TTF = VENDOR / "noto-emoji" / "Noto-COLRv1.ttf"
FLUENT_PATH = VENDOR / "fluent-emoji" / "FluentEmojiColor.ttf"
SOURCE_HAN_DIR = VENDOR / "source-han-sans"
SOURCE_HAN_PATH = SOURCE_HAN_DIR / "SourceHanSansSC-Regular.otf"
SOURCE_HAN_LIGHT = SOURCE_HAN_DIR / "SourceHanSansSC-Light.otf"

UA = {"User-Agent": "xiaoheizi-mono-fetch/0.1"}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print("download", url)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req) as resp, dest.open("wb") as out:
        shutil.copyfileobj(resp, out)
    print(" saved", dest, dest.stat().st_size)


def extract_7z(archive: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    try:
        import py7zr
    except ImportError as exc:
        raise SystemExit("解压 7z 需要 py7zr：pip install py7zr") from exc
    with py7zr.SevenZipFile(archive, mode="r") as zf:
        zf.extractall(path=dest)


def fetch_jetbrains() -> None:
    if JBM_TTF.exists() and JBM_LIGHT.exists():
        print("skip", JBM_TTF)
        return
    archive = VENDOR / "JetBrainsMono-2.304.zip"
    if not archive.exists():
        download(JBM_ZIP, archive)
    dest = VENDOR / "jetbrains-mono"
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(dest)
    for name in ("JetBrainsMonoNL-Regular.ttf", "JetBrainsMonoNL-Light.ttf"):
        target = JBM_DIR / name
        if target.exists():
            continue
        found = list(dest.rglob(name))
        if not found:
            raise SystemExit(f"JetBrains zip 中没有 {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(found[0], target)
    ofl = dest / "OFL.txt"
    if not ofl.exists():
        found_ofl = list(dest.rglob("OFL.txt"))
        if found_ofl:
            shutil.copyfile(found_ofl[0], dest / "OFL.txt")


def fetch_sarasa() -> None:
    if SARASA_TTF.exists() and SARASA_LIGHT.exists():
        print("skip", SARASA_TTF)
        return
    archive = VENDOR / "SarasaFixedSC-TTF-Unhinted-1.0.40.7z"
    if not archive.exists():
        download(SARASA_7Z, archive)
    tmp = VENDOR / "_sarasa_unpack"
    if tmp.exists():
        shutil.rmtree(tmp)
    extract_7z(archive, tmp)
    SARASA_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("SarasaFixedSC-Regular.ttf", "SarasaFixedSC-Light.ttf"):
        found = list(tmp.rglob(name))
        if not found:
            raise SystemExit(f"Sarasa 7z 中没有 {name}")
        shutil.copyfile(found[0], SARASA_DIR / name)
    shutil.rmtree(tmp, ignore_errors=True)


def fetch_noto() -> None:
    if not NOTO_TTF.exists():
        download(NOTO_COLR, NOTO_TTF)
    ofl = VENDOR / "noto-emoji" / "LICENSE"
    if not ofl.exists():
        download(NOTO_OFL, ofl)


def fetch_fluent() -> None:
    if not FLUENT_PATH.exists():
        download(FLUENT_TTF, FLUENT_PATH)
    ms = VENDOR / "fluent-emoji" / "LICENSE-Microsoft.txt"
    build = VENDOR / "fluent-emoji" / "LICENSE-tetunori.txt"
    if not ms.exists():
        download(FLUENT_MIT_MS, ms)
    if not build.exists():
        download(FLUENT_MIT_BUILD, build)


def assert_source_han(path: Path) -> None:
    """带圈字母数字按 1 em 画（规范 §2）。不合格即退出，禁止拿半格稿充数。"""
    from fontTools.ttLib import TTFont
    from fontTools.pens.boundsPen import BoundsPen

    font = TTFont(path)
    cmap = font.getBestCmap()
    if 0x2460 not in cmap:
        raise SystemExit(f"{path.name} 缺少 U+2460，上游不合格")
    upem = font["head"].unitsPerEm
    gname = cmap[0x2460]
    adv, _lsb = font["hmtx"][gname]
    if abs(adv - upem) > upem * 0.01:
        raise SystemExit(f"{path.name} U+2460 推进 {adv} 不是 1 em（upem {upem}），上游不合格")
    pen = BoundsPen(font.getGlyphSet())
    font.getGlyphSet()[gname].draw(pen)
    width = pen.bounds[2] - pen.bounds[0] if pen.bounds else 0
    if width < upem * 0.8:
        raise SystemExit(f"{path.name} U+2460 轮廓宽度 {width} 小于 0.8 em，疑似半格稿，上游不合格")
    weight = font["OS/2"].usWeightClass
    print(f"source han ok: {path.name} U+2460 adv={adv} upem={upem} width={width:.0f} weight={weight}")
    font.close()


def fetch_source_han() -> None:
    """思源黑体 SC Regular 与 Light：带圈字母数字按 1 em 画，覆盖半格稿。"""
    pairs = (
        (SOURCE_HAN_PATH, SOURCE_HAN_OTF),
        (SOURCE_HAN_LIGHT, SOURCE_HAN_LIGHT_OTF),
    )
    for path, url in pairs:
        if not path.exists():
            download(url, path)
        assert_source_han(path)


def main() -> None:
    VENDOR.mkdir(parents=True, exist_ok=True)
    fetch_jetbrains()
    fetch_sarasa()
    fetch_noto()
    fetch_fluent()
    fetch_source_han()
    missing = [
        p
        for p in (
            JBM_TTF,
            JBM_LIGHT,
            SARASA_TTF,
            SARASA_LIGHT,
            NOTO_TTF,
            FLUENT_PATH,
            SOURCE_HAN_PATH,
            SOURCE_HAN_LIGHT,
        )
        if not p.exists()
    ]
    if missing:
        raise SystemExit("上游仍缺失：" + ", ".join(str(p) for p in missing))
    print("vendor ready")


if __name__ == "__main__":
    main()
