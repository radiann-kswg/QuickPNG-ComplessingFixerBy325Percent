#!/usr/bin/env python3
"""QuickPNG-ComplessingFixerBy325Percent 変換本体。

input-PNG/ の各PNGを、input-baseSize/ 内の対応画像の SCALE_PERCENT%（既定 325% = 3.25倍）の
ピクセルサイズへアスペクト比を維持して縮小し、パレット量子化した圧縮PNGとして output-PNG/ へ
入力と同じフォルダ構成で出力する。透過（アルファ）は保持する。

対応付け: 両者のファイル名から INPUT_KEY_RE / BASE_KEY_RE でキー（例: 数字）を抜き出して照合し、
同キーが複数あれば縦横比が最も近いものを採用する。対応が無いファイルは、対応が取れた同一バッチの
倍率の中央値（1件も無ければ FALLBACK_SCALE_PERCENT）で縮小する。

設定はリポジトリ直下の .env（無ければ既定値）から読み込む。依存: Pillow
"""
from __future__ import annotations

import re
import statistics
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input-PNG"
BASE_DIR = ROOT / "input-baseSize"
OUTPUT_DIR = ROOT / "output-PNG"

DEFAULTS = {
    "SCALE_PERCENT": 325.0,          # 基準画像に対する出力倍率(%)
    "FALLBACK_SCALE_PERCENT": 95.5,  # 対応が1件も取れない時の、入力画像に対する倍率(%)
    "PALETTE_COLORS": 256,
    "DITHER": 1,
    "INPUT_KEY_RE": r"_(0x[A-Fa-f]|\d+|[^\W\d_]+)",  # 入力名から抜くキー("_"直後の 0xA / 数字 / 単語)
    "BASE_KEY_RE": r"(0x[A-Fa-f]|\d+)",              # 基準名から抜くキー(最初の 0xA / 数字)
}


def load_env() -> dict:
    cfg = dict(DEFAULTS)
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" not in line:
                continue
            k, v = (s.strip() for s in line.split("=", 1))
            if k in cfg:
                cfg[k] = type(cfg[k])(v) if not isinstance(cfg[k], str) else v
    return cfg


def key_of(name: str, pattern: str) -> str | None:
    m = re.search(pattern, name)
    return m.group(1).upper() if m else None


def plan(inputs: list[Path], bases: dict[str, list[tuple[int, int]]], cfg: dict):
    """[(path, Image, scale)] と対応なし件数、採用したフォールバック倍率を返す。"""
    ratio = cfg["SCALE_PERCENT"] / 100
    matched, unmatched = [], []
    for f in inputs:
        im = Image.open(f)
        w, h = im.size
        cands = bases.get(key_of(f.stem, cfg["INPUT_KEY_RE"]) or "")
        if cands:
            bw, _ = min(cands, key=lambda s: abs(s[0] / s[1] - w / h))  # 縦横比最近傍
            matched.append((f, im, ratio * bw / w))                     # 幅基準で等比
        else:
            unmatched.append((f, im))
    fb = statistics.median(s for _, _, s in matched) if matched else cfg["FALLBACK_SCALE_PERCENT"] / 100
    return matched + [(f, im, fb) for f, im in unmatched], len(unmatched), fb


def run(cfg: dict) -> int:
    inputs = sorted(p for p in INPUT_DIR.rglob("*.png") if p.is_file())
    bases: dict[str, list[tuple[int, int]]] = {}
    for b in BASE_DIR.glob("*.png"):
        k = key_of(b.stem, cfg["BASE_KEY_RE"])
        if k:
            with Image.open(b) as bi:
                bases.setdefault(k, []).append(bi.size)
    if not inputs:
        print(f"入力なし: {INPUT_DIR}")
        return 0
    items, n_fb, fb = plan(inputs, bases, cfg)
    for f, im, s in items:
        src = im.size
        size = (max(1, round(im.width * s)), max(1, round(im.height * s)))
        out = im.convert("RGBA").resize(size, Image.LANCZOS)
        out = out.quantize(cfg["PALETTE_COLORS"], method=Image.Quantize.FASTOCTREE,
                           dither=Image.Dither.FLOYDSTEINBERG if cfg["DITHER"] else Image.Dither.NONE)
        out.info = {}
        dst = OUTPUT_DIR / f.relative_to(INPUT_DIR)
        dst.parent.mkdir(parents=True, exist_ok=True)
        out.save(dst, optimize=True)
        im.close()
        print(f"{src[0]}x{src[1]} -> {size[0]}x{size[1]} (x{s:.3f}) {f.relative_to(INPUT_DIR)}")
    print(f"完了: {len(items)}件 -> {OUTPUT_DIR}  (対応なし {n_fb}件は x{fb:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(run(load_env()))
