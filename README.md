# ComplessingFixerBy325Permill

`出力/` の PNG を、`サイズ調整圧縮版/` の対応画像の **3.25倍** のピクセルサイズに等比縮小し、256色パレットPNGとして `サイト用圧縮版/` に平置きで出力する。

```
pip install pillow
python fixer.py "<出力>" "<サイズ調整圧縮版>" "<サイト用圧縮版>" [--scale 3.25]
```

対応付け: 出力ファイル名の `_000(…)` / `_0xA(…)` / `_ゼフィア` と、圧縮版 `emstk_corefolder000-1.png` のキーを照合し、縦横比が最も近いものの幅×3.25 に合わせる。対応なしはフォルダ内の中央値倍率（無ければ 0.955）で代用。

check: `python test_fixer.py`
