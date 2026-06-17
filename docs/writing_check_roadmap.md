# ライティング自己チェック ロードマップ

英検3級ライティングは **自動採点（正解/不正解）を行わない**。提出後に参考解答と見比べる自己学習が基本。
本ドキュメントは、機械的に判定できる項目を段階的に足していく方針を管理する。

## 現状（Phase 0）

- 提出条件: テキストが空でないこと（フロント + サーバー）
- 結果画面: 提出文 + `explanation`（参考解答・ヒント）
- 進捗: 提出ごとに `update_user_progress(..., is_correct=True)`（内容は見ない）

## Phase 1 — ルールベースの軽いチェック ✅ 実装済み

**目的**: 語数・文数など、ルールで判定できる項目を「目安」として表示する。

### データ

| 項目 | 場所 | 内容 |
|------|------|------|
| `Question.writing_rubric` | JSON | 登録時に問題文から抽出 |
| `WritingUserAnswer.feedback_json` | JSON | 提出時のチェック結果 |

`writing_rubric` の例:

```json
{"kind": "email_reply", "word_min": 15, "word_max": 25, "count_body_only": true}
{"kind": "opinion", "word_min": 25, "word_max": 35, "sentence_min": 2, "sentence_max": 2}
```

### チェック項目

| 項目 | 判定 |
|------|------|
| 英文の有無 | 英単語がほぼない → warn |
| 語数 | 目安範囲内 → ok / やや外れ → warn |
| 文数（意見問題） | 2文前後 → ok / 外れ → warn |

メール返信の語数は `Hi, James!`・`Thank you for your e-mail.`・`Best wishes,` 以降を除いた **本文部分** のみカウント（本番に近い）。

### UI

回答結果にチェックリスト（✅ / ⚠️ / ℹ️）。採点ではなくヒント。提出はブロックしない。

### 実装ファイル

- `exams/writing_feedback.py` — ルーブリック抽出・解析
- `questions/management/commands/register_writing_questions.py` — rubric 保存
- `exams/views.py` — 提出時に `feedback_json` 保存
- `exams/templates/exams/_writing_feedback.html` — 結果表示

### やらないこと（Phase 1）

- 正解/不正解の判定
- 提出の拒否（語数オーバーでも提出可）
- 設問内容への回答充足（Phase 2）
- 文法指摘（Phase 3）

---

## Phase 2 — 設問対応ヒューリスティック（未着手）

- メール返信: James の下線2問に答えている可能性（キーワード・疑問詞）
- 意見問題: 意見文 + 理由2つ（`First,` / `Second,` など）の型
- すべて **warn/info** 表現（「答えられていない可能性」）

## Phase 3 — 文法チェック（未着手・任意）

- LanguageTool 等の外部サービス
- 「〜かもしれません」トーン。本番減点の代替にはしない

## Phase 4 — AI フィードバック（未着手・任意）

- 参考解答 + 提出文を LLM に渡し日本語コメント
- コスト・プライバシー・キャッシュ設計が必要

---

## 問題データとの関係

- マスタ: `data/questions/level3/writing_questions.txt`
- 登録: `python manage.py register_writing_questions --level 3`
- rubric は問題文の「語数の目安」「2つの質問/英文」から自動抽出。テキスト形式変更時は `writing_feedback.parse_writing_rubric` も更新する。

## 検証

```bash
python manage.py test exams.tests.WritingFeedbackTests
python manage.py check
```
