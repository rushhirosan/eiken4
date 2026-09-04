# 公式保管問題の出題内容インベントリ

`data/questions/`（級別 txt）で**実際に聞かれていること**を級・カテゴリごとに整理した台帳。
オリジナル作問の網羅チェック用。公式文面の転載・公開登録用ではない。

## 構成

```
docs/inventory/
  level3/   # 手厚め分類（既存）
  level4/
  level5/
```

| 級 | 状態 | 備考 |
|----|------|------|
| 3級 | [`level3/`](level3/) | 公式保管カテゴリ一式（語順ファイルなし） |
| 4級 | [`level4/`](level4/) | 語順・読解あり。ライティングなし |
| 5級 | [`level5/`](level5/) | 語順あり。読解・ライティング・L文章なし |

## ファイル一覧

### 3級

- [`level3/conversation.md`](level3/conversation.md)
- [`level3/grammar_vocabulary.md`](level3/grammar_vocabulary.md)
- [`level3/listening_conversation.md`](level3/listening_conversation.md)
- [`level3/listening_illustration.md`](level3/listening_illustration.md)
- [`level3/listening_passage.md`](level3/listening_passage.md)
- [`level3/reading_comprehension.md`](level3/reading_comprehension.md)
- [`level3/speaking.md`](level3/speaking.md)
- [`level3/writing.md`](level3/writing.md)

### 4級

- [`level4/conversation.md`](level4/conversation.md)
- [`level4/grammar_vocabulary.md`](level4/grammar_vocabulary.md)
- [`level4/listening_conversation.md`](level4/listening_conversation.md)
- [`level4/listening_illustration.md`](level4/listening_illustration.md)
- [`level4/listening_passage.md`](level4/listening_passage.md)
- [`level4/reading_comprehension.md`](level4/reading_comprehension.md)
- [`level4/speaking.md`](level4/speaking.md)
- [`level4/wordorder.md`](level4/wordorder.md)

### 5級

- [`level5/conversation.md`](level5/conversation.md)
- [`level5/grammar_vocabulary.md`](level5/grammar_vocabulary.md)
- [`level5/listening_conversation.md`](level5/listening_conversation.md)
- [`level5/listening_illustration.md`](level5/listening_illustration.md)
- [`level5/speaking.md`](level5/speaking.md)
- [`level5/wordorder.md`](level5/wordorder.md)

## 再生成

```bash
python scripts/gen_official_inventory.py          # 4級・5級
python scripts/gen_level3_inventory.py            # 3級の一部カテゴリ
```

4・5級の文法／会話／L応答の種別は解説ベースの自動分類（目安）。
3級の文法・会話は手作業タグを含む既存台帳を優先。

