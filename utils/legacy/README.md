# Legacy PDF / 公式保管ツール（再実行非推奨）

公式 PDF → 級別 txt / 画像切り出し用の**一度きり・保管向け**スクリプトです。

- **公開パイプラインには使わない**（サイトに載せるのは `data/questions/original/` のみ）
- 既定ではガードで停止する。どうしても動かすときだけ:

```bash
ALLOW_LEGACY_PDF_IMPORT=1 python utils/legacy/build_level5_questions.py
```

- 級・回ごとにファイルが分かれているのは、取り込み作業の履歴のため（全級共通ツールではない）
- 傾向・網羅チェックは `scripts/gen_*_inventory.py` → `docs/inventory/` を使う
- 現行の作問・検証は親の `utils/`（`validate_*` / `text_to_speech*` など）

| スクリプト | 用途 |
|------------|------|
| `build_level5_questions.py` | 5級 PDF → `data/questions/level5/` |
| `build_level3_202601.py` / `build_level4_202601.py` | 各級 2026① の追記 |
| `verify_level3_official_answers.py` / `verify_level5_official_answers.py` | 保管 txt と公式解答 PDF の突合 |
| `extract_level5_illustrations.py` | 5級 PDF からイラスト切り出し |
| `setup_level5_assets.py` | 5級プレースホルダー（本番 original では使わない） |
| `pdf_text_extractor.py` / `pdf_image_extractor.py` | 汎用 PDF 抽出 |
| `legacy_pdf_guard.py` | 上記の実行ガード |
