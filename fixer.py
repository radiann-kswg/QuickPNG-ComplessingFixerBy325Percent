"""ComplessingFixerBy325Permill
出力PNG群を、対応する圧縮版PNGの 3.25 倍サイズに等比縮小し、256色パレットPNGとして1フォルダに出力する。

usage: python fixer.py <出力フォルダ> <サイズ調整圧縮版フォルダ> <サイト用圧縮版フォルダ> [--scale 3.25]
"""
import glob, os, re, statistics, sys
from PIL import Image

KEY_OUT = re.compile(r'_(0x[A-Fa-f]|\d+|[^\W\d_]+)')          # "_000(チトセ)-1" → 000 / 0xA / ゼフィア
KEY_CMP = re.compile(r'emstk_corefolder(0x[A-Fa-f]|\d+)')       # "emstk_corefolder10alt-1" → 10
DEFAULT_SCALE = 0.955  # 対応が1枚も取れないとき用: 実測中央値（圧縮版×3.25 ≒ 元×0.955）


def plan(outs, cmps, ratio):
    """[(path, Image, scale)] を返す。同キーの圧縮版から縦横比最近傍を選ぶ。"""
    matched, unmatched = [], []
    for f in outs:
        im = Image.open(f); w, h = im.size
        m = KEY_OUT.search(os.path.basename(f).split('コアフォルダ単体', 1)[-1])
        cands = cmps.get(m.group(1).upper()) if m else None
        if cands:
            cw, _ = min(cands, key=lambda s: abs(s[0] / s[1] - w / h))
            matched.append((f, im, ratio * cw / w))
        else:
            unmatched.append((f, im))
    fb = statistics.median(s for _, _, s in matched) if matched else DEFAULT_SCALE
    return matched + [(f, im, fb) for f, im in unmatched], len(unmatched), fb


def run(src, ref, dst, ratio=3.25):
    outs = sorted(glob.glob(os.path.join(src, '**', '*.png'), recursive=True))
    cmps = {}
    for c in glob.glob(os.path.join(ref, '*.png')):
        m = KEY_CMP.search(os.path.basename(c))
        if m:
            cmps.setdefault(m.group(1).upper(), []).append(Image.open(c).size)
    os.makedirs(dst, exist_ok=True)
    items, n_fb, fb = plan(outs, cmps, ratio)
    for f, im, s in items:
        out = im.convert('RGBA').resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        out.quantize(256).save(os.path.join(dst, os.path.basename(f)), optimize=True)
    print(f'{len(items)} files -> {dst} (fallback {n_fb}, scale {fb:.3f})')


if __name__ == '__main__':
    a = sys.argv[1:]
    ratio = float(a[a.index('--scale') + 1]) if '--scale' in a else 3.25
    a = [x for x in a if x != '--scale' and x != str(ratio)]
    if len(a) != 3:
        sys.exit(__doc__)
    run(*a, ratio=ratio)
