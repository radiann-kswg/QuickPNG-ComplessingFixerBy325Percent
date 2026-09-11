# QuickPNG-ComplessingFixerBy325Percent

`input-PNG/` のPNGを、`input-baseSize/` の対応画像の **325%（3.25倍・`.env` で変更可）** のピクセルサイズへ
アスペクト維持で縮小し、パレット量子化した圧縮PNGとして `output-PNG/` へ出力する、
Claude（Cowork / Claude Code）向けパイプライン設定。

姉妹リポジトリ:

- [QuickPNG-To256Permill](https://github.com/radiann-kswg/QuickPNG-To256Permill) — PSDカンバスの256‰縮小PNG出力
- [QuickPNG-SmartObjectExport](https://github.com/radiann-kswg/QuickPNG-SmartObjectExport) — PSD埋め込みスマートオブジェクトの抽出
- [QuickPNG-Tinize4Web](https://github.com/radiann-kswg/QuickPNG-Tinize4Web) — Web公開用の高圧縮PNG変換

## 使い方

1. `input-PNG/` に対象PNG、`input-baseSize/` にサイズ基準となる圧縮済みPNGを置く
2. `.env.example` を `.env` にリネームコピーする（必要に応じてパラメータを変更）
3. Claude Desktop（Cowork）または Claude Code でこのフォルダを開き、「input-PNGをinput-baseSize基準でoutput-PNGへ変換して」と依頼する — Claudeが `CLAUDE.md` の手順に従って処理する
4. 手動実行も可能:

   ```bash
   pip install -r requirements.txt
   # Cowork のサンドボックスなど PEP 668 管理環境では:
   #   pip install -r requirements.txt --break-system-packages
   python3 scripts/fixer.py
   ```

   macOS では venv を使う（姉妹リポジトリと並べた親フォルダに共有 `.venv` を作ると使い回せる）:

   ```bash
   python3 -m venv ../.venv
   ../.venv/bin/pip install -r requirements.txt
   ../.venv/bin/python scripts/fixer.py
   ```

5. 結果は `output-PNG/<入力と同じ相対パス>.png` に、入力のフォルダ構成のまま出力される

## 仕様

- 入力名・基準名からキー（`_` 直後の数字/単語、基準名の最初の数字）を抜いて照合し、同キーが複数なら縦横比が最も近いものを採用
- 出力倍率 = `SCALE_PERCENT/100 × 基準幅 / 入力幅`（幅基準・等比・透過保持）
- 対応が無い入力は同バッチの倍率中央値、1件も無ければ `FALLBACK_SCALE_PERCENT` で縮小
- 256色パレット（FASTOCTREE・ディザ有）・メタデータなしのPNG

## 構成

```
CLAUDE.md               # Claude向けパイプライン定義（本体）
README.md               # 本ファイル
.env.example            # 変換パラメータのテンプレート
.env                    # 実際の変換パラメータ（git管理外・要作成）
requirements.txt        # Python依存（Pillow）
scripts/fixer.py        # 変換スクリプト
scripts/test_fixer.py   # 自己チェック（合成画像のみ）
input-PNG/              # 入力（git管理外）
input-baseSize/         # サイズ基準画像（git管理外）
output-PNG/             # 出力（git管理外）
```

## 設定（.env）

| 変数                     | 既定値                        | 意味                                         |
| ------------------------ | ----------------------------- | -------------------------------------------- |
| `SCALE_PERCENT`          | `325`                         | 出力 = 基準画像 × 倍率(%)                    |
| `FALLBACK_SCALE_PERCENT` | `95.5`                        | 対応が1件も取れないときの入力に対する倍率(%) |
| `PALETTE_COLORS`         | `256`                         | パレット色数                                 |
| `DITHER`                 | `1`                           | ディザリング                                 |
| `INPUT_KEY_RE`           | `_(0x[A-Fa-f]\|\d+\|[^\W\d_]+)` | 入力名のキー抽出正規表現                     |
| `BASE_KEY_RE`            | `(0x[A-Fa-f]\|\d+)`            | 基準名のキー抽出正規表現                     |

## 出力の検証

全件について、PILで開けること・幅が基準×倍率（±1px）・縦横比一致・パレットモード・透過保持を確認する（詳細は `CLAUDE.md`）。

## ライセンス

MIT（`LICENSE`）。入出力ディレクトリの画像アセットはライセンス対象外かつgit管理外。
