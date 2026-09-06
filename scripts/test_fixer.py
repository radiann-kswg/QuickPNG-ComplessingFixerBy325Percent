"""自己チェック: python3 scripts/test_fixer.py  （合成画像のみ使用・実アセット不要）"""
import sys, tempfile
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import fixer

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    fixer.INPUT_DIR, fixer.BASE_DIR, fixer.OUTPUT_DIR = d / "in", d / "base", d / "out"
    fixer.INPUT_DIR.mkdir(); fixer.BASE_DIR.mkdir()
    Image.new("RGBA", (1500, 1700), (255, 0, 0, 0)).save(fixer.INPUT_DIR / "sample_7(a)-1.png")
    Image.new("RGBA", (1000, 1000)).save(fixer.INPUT_DIR / "sample_zeta-1.png")  # 対応なし → 中央値倍率
    Image.new("P", (400, 453)).save(fixer.BASE_DIR / "base7-1.png")
    Image.new("P", (600, 300)).save(fixer.BASE_DIR / "base7-2.png")              # 縦横比が遠い候補
    fixer.run(fixer.DEFAULTS)
    a = Image.open(fixer.OUTPUT_DIR / "sample_7(a)-1.png")
    b = Image.open(fixer.OUTPUT_DIR / "sample_zeta-1.png")
    assert a.size == (1300, 1473) and a.mode == "P", (a.size, a.mode)  # 400 * 3.25 = 1300
    assert a.convert("RGBA").getpixel((0, 0))[3] == 0                    # 透過保持
    assert b.size == (867, 867), b.size                                  # 1000 * (1300/1500)
    assert "dpi" not in a.info and "exif" not in a.info                  # メタデータなし
print("ok")
