# QuickPNG-ComplessingFixerBy325Percent — 基準画像比 325% サイズ調整 圧縮PNG クイック出力パッチ

## 目的

`input-PNG/` に置かれたPNGを、`input-baseSize/` にある**対応する基準画像**の `SCALE_PERCENT`%
（既定 325% = 3.25倍）のピクセルサイズへ縮小し、パレット量子化した圧縮PNGとして `output-PNG/` へ
**`input-PNG/` と同じフォルダ構成のまま**出力する。

- **アスペクト比は常に維持**する（基準画像の幅×倍率に合わせ、高さは入力の比率で決める）
- **透過（アルファ）は保持**する
- 入力のサブフォルダは再帰的に走査し、出力も同じ相対パスに再現する

## 返答言語

チャットでの返答は必ず日本語。

## プライバシー方針（重要）

`input-PNG/`・`input-baseSize/`・`output-PNG/` の中身（ファイル名・画像内容）は、CLAUDE.md や README 等の
**設定・ドキュメント類・コミットメッセージに一切含めない**。画像アセットは `.gitignore` によりgit管理外。

## 設定（.env）

作業開始時に必ずリポジトリ直下の `.env` を読み、以下をパイプライン全体へ反映する。無い場合は既定値。

```
SCALE_PERCENT=325             # 出力 = 基準画像 × この倍率(%)
FALLBACK_SCALE_PERCENT=95.5   # 対応が1件も取れないときの、入力に対する倍率(%)
PALETTE_COLORS=256            # パレット色数(2-256)
DITHER=1                      # ディザリング(1/0)
INPUT_KEY_RE=_(0x[A-Fa-f]|\d+|[^\W\d_]+)   # 入力名からキーを抜く正規表現(group(1))
BASE_KEY_RE=(0x[A-Fa-f]|\d+)               # 基準名からキーを抜く正規表現(group(1))
```

## 対応付けルール

1. 入力名から `INPUT_KEY_RE`、基準名から `BASE_KEY_RE` でキーを抜き、大文字化して照合する
2. 同キーの基準画像が複数あれば、**入力と縦横比が最も近い**ものを採用する
3. 倍率 = `SCALE_PERCENT/100 × 基準幅 / 入力幅`（幅基準・等比）
4. 対応が無い入力は、同バッチで対応が取れた倍率の**中央値**で縮小する。
   1件も取れなければ `FALLBACK_SCALE_PERCENT` を使う

## 推奨パイプライン: ローカル（既定・最優先）

```bash
pip install -r requirements.txt   # PEP 668 環境: --break-system-packages
python3 scripts/fixer.py
```

処理内容（1ファイルあたり）: RGBA化 → 上記倍率で `LANCZOS` 縮小 → `quantize(method=FASTOCTREE)` で
透過を保ったままパレット化 → `info` を空にして PNG 保存（`optimize=True`）。

自己チェック: `python3 scripts/test_fixer.py`（合成画像のみ・実アセット不要）

## 任意パイプライン: Adobeハイブリッド

Adobe for creativity コネクタで縮小のみ行う運用も可能だが、公式に **20件超のバッチは非対応**で、
1件あたりアップロード→`image_crop_and_resize`→ダウンロードの往復が要る上、パレット圧縮は行われない。
使う場合も最終段は `scripts/fixer.py` 相当の量子化を通す。通常はローカルを使う。

## 検証チェックリスト（毎回・全件）

- PIL で `Image.open(f); im.load()` が通る
- 出力幅 ≈ 採用した基準画像の幅 × `SCALE_PERCENT/100`（±1px）、縦横比が入力と一致（±1px）
- モードが `P`（パレット）で、元が透過なら出力も透過（角ピクセル alpha=0 等で確認）
- 対応なし件数がログに出る。想定外に多ければ `INPUT_KEY_RE` / `BASE_KEY_RE` を見直す

## 既知の落とし穴

- 基準画像がトリミングされていて入力と縦横比が違う場合、**幅を優先**して合わせる（高さは一致しない）
- キー抽出は「`_` 直後の数字/単語」「基準名の最初の数字」という素朴なもの。命名規則が違う
  アセット群では `.env` の正規表現を差し替える
- Coworkのマウント同期: サンドボックスの出力をPC側で見る際、稀に旧内容が残る。出力名を変えて再取得

## ライセンス

このリポジトリの設定・スクリプト・ドキュメントは MIT（`LICENSE` 参照）。
`input-PNG/`・`input-baseSize/`・`output-PNG/` の画像アセットは**ライセンス対象外かつgit管理外**。
