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
NOTO_COLR = "https://github.com/googlefonts/noto-emoji/raw/main/fonts/Noto-COLRv1.ttf"
NOTO_OFL = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/fonts/LICENSE"
FLUENT_TTF = (
    "https://github.com/tetunori/fluent-emoji-webfont/raw/main/dist/FluentEmojiColor.ttf"
)
FLUENT_MIT_MS = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/LICENSE"
FLUENT_MIT_BUILD = "https://raw.githubusercontent.com/tetunori/fluent-emoji-webfont/main/LICENSE"

JBM_TTF = VENDOR / "jetbrains-mono" / "fonts" / "ttf" / "JetBrainsMonoNL-Regular.ttf"
SARASA_TTF = VENDOR / "sarasa-fixed-sc" / "SarasaFixedSC-Regular.ttf"
NOTO_TTF = VENDOR / "noto-emoji" / "Noto-COLRv1.ttf"
FLUENT_PATH = VENDOR / "fluent-emoji" / "FluentEmojiColor.ttf"

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
    if JBM_TTF.exists():
        print("skip", JBM_TTF)
        return
    archive = VENDOR / "JetBrainsMono-2.304.zip"
    if not archive.exists():
        download(JBM_ZIP, archive)
    dest = VENDOR / "jetbrains-mono"
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(dest)
    if not JBM_TTF.exists():
        found = list(dest.rglob("JetBrainsMonoNL-Regular.ttf"))
        if not found:
            raise SystemExit("JetBrains zip 中没有 JetBrainsMonoNL-Regular.ttf")
        JBM_TTF.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(found[0], JBM_TTF)
    ofl = dest / "OFL.txt"
    if not ofl.exists():
        found_ofl = list(dest.rglob("OFL.txt"))
        if found_ofl:
            shutil.copyfile(found_ofl[0], dest / "OFL.txt")


def fetch_sarasa() -> None:
    if SARASA_TTF.exists():
        print("skip", SARASA_TTF)
        return
    archive = VENDOR / "SarasaFixedSC-TTF-Unhinted-1.0.40.7z"
    if not archive.exists():
        download(SARASA_7Z, archive)
    tmp = VENDOR / "_sarasa_unpack"
    if tmp.exists():
        shutil.rmtree(tmp)
    extract_7z(archive, tmp)
    found = list(tmp.rglob("SarasaFixedSC-Regular.ttf"))
    if not found:
        raise SystemExit("Sarasa 7z 中没有 SarasaFixedSC-Regular.ttf")
    SARASA_TTF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(found[0], SARASA_TTF)
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


def main() -> None:
    VENDOR.mkdir(parents=True, exist_ok=True)
    fetch_jetbrains()
    fetch_sarasa()
    fetch_noto()
    fetch_fluent()
    missing = [p for p in (JBM_TTF, SARASA_TTF, NOTO_TTF, FLUENT_PATH) if not p.exists()]
    if missing:
        raise SystemExit("上游仍缺失：" + ", ".join(str(p) for p in missing))
    print("vendor ready")


if __name__ == "__main__":
    main()
