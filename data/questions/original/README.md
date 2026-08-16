# オリジナル問題テキスト（公開用）

ここに置いた問題だけを、`provenance=original` で登録・公開する想定です。

```
data/questions/original/level5/
data/questions/original/level4/
data/questions/original/level3/
```

ファイル名は既存の register コマンドと同じ（`grammar_fill_questions.txt` など）。

- 公式 PDF（`data/pdf_import`）や既存の級別 txt をコピーしない
- 公式文面を AI に渡して類題を作らない
- 形式（穴埋め・会話補充など）だけ級の傾向に合わせる

作業スキル: `eiken-original-authoring` → `eiken-originality-review` → 人の目視 → `eiken-explanation-quality-review`

登録例:

```bash
python manage.py register_grammar_fill_questions --level 5 --original
```

進捗・次作業: `docs/ip_risk_elimination_roadmap.md`（いまは5級ローカル完了 → 次は4級）。
