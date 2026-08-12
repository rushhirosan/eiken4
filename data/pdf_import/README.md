# PDF インポート資料（配信パイプライン外）

このディレクトリの PDF・抽出テキストは **保管・形式参考用** です。

## やってよいこと

- 人が級の出題形式・難易度の傾向を思い出す
- 自作問題のあと、公開過去問と酷似していないか目視する材料にする

## やらないこと（既定）

- PDF → txt → `register_*` → サイト公開
- PDF を AI に渡して類題生成
- ここから再生成したテキストを `provenance=original` にする

ツール実行は既定でブロックされています。ローカルでどうしても動かす場合のみ:

```bash
ALLOW_LEGACY_PDF_IMPORT=1 python utils/build_level5_questions.py
```

公開用問題は `data/questions/original/` に新規自作し、明示的に `original` で登録してください。
