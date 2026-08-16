---
name: eiken-original-authoring
description: Creates original (provenance=original) practice questions for えいごごはん by level and category. Use when asked to 作問, add original questions, write 5級/4級/3級 grammar, conversation, word order, listening, speaking, reading, or writing items for data/questions/original/.
---

# Original Question Authoring

子供向けオリジナル練習問題を、公式由来ファイルを見ずに新規作成する。

公開用の置き場は `data/questions/original/level{5|4|3}/` のみ。既存の `data/questions/*.txt`・`level3/`・`level5/` や `data/pdf_import/` には書かない。

## Inputs to confirm

- 級（`5` / `4` / `3`）。未指定なら **5級**
- カテゴリ（下表）
- 追加数（未指定なら 5〜10）
- 追記か新規ファイルか

## Categories by level

| カテゴリ | 5級 | 4級 | 3級 | 参照 |
|----------|-----|-----|-----|------|
| `grammar_fill` 文法・語彙 | ○ | ○ | ○ | [grammar_fill.md](references/grammar_fill.md) |
| `conversation_fill` 会話補充 | ○ | ○ | ○ | [conversation_fill.md](references/conversation_fill.md) |
| `word_order` 語順 | ○ | ○ | ○ | [word_order.md](references/word_order.md) |
| `listening_illustration` リスニングイラスト | ○（Part1＋Part3） | ○ | ○ | [listening_illustration.md](references/listening_illustration.md) |
| `listening_conversation` リスニング会話 | ○ | ○ | ○ | [listening_conversation.md](references/listening_conversation.md) |
| `listening_passage` リスニング文章 | × | ○ | ○ | [listening_passage.md](references/listening_passage.md) |
| `speaking` スピーキング | ○（流れ練習） | △ | ○ | [speaking.md](references/speaking.md) |
| `reading_comprehension` 読解 | × | ○ | ○ | [reading_comprehension.md](references/reading_comprehension.md) |
| `writing` ライティング | × | × | ○ | [writing.md](references/writing.md) |

5級に読解・ライティング・`listening_passage` は作らない。5級リスニング第3部は文章問題ではなく **イラスト一致**（`listening_illustration` の No.101+）。

## Output paths

ファイル名は既存の register コマンドと同じ。

```
data/questions/original/level{N}/grammar_fill_questions.txt
data/questions/original/level{N}/conversation_questions.txt
data/questions/original/level{N}/wordorder_questions.txt
data/questions/original/level{N}/listening_illustration_questions.txt
data/questions/original/level{N}/listening_conversation_questions.txt
data/questions/original/level{N}/listening_passage_questions.txt
data/questions/original/level{N}/speaking_questions.txt
data/questions/original/level{N}/reading_comprehesion_questions.txt
data/questions/original/level{N}/writing_questions.txt
```

`reading_comprehesion` の綴りは既存コマンド依存。変えない。

## Do not

- 公式PDF（`data/pdf_import/`）を開いて「同じ問題を」と作らない
- 既存の `data/questions/level5|level3|直下` を読んで類題にしない
- 公式文面・選択肢・原稿・イラスト・音源をコピー／並べ替えしない
- 人名差し替えだけの問題を作らない
- 完成稿を `provenance=blocked` のレガシーパスへ置かない

形式が不明なときは、公式問題文ではなく **このスキルの参照ファイル** と `questions/management/commands/register_*.py` の正規表現を見る。

## Workflow

1. 級・カテゴリ・件数を確定する。級に無いカテゴリなら止める。
2. 該当の `references/*.md` だけ読む。
3. 既存の **original** ファイルがあれば末尾番号を確認する（公式由来ファイルは見ない）。
4. 級の傾向（4択、会話補充、部構成、語彙の粗さ）だけ頭に入れて、場面・文言・選択肢を新規に書く。
5. 解説も同時に書く（詳細は `eiken-explanation-quality-review`）。
6. `---` 区切り・連番・選択肢数を崩さない。
7. 追加分の正解番号が極端に偏らないようにする。
8. **カテゴリ固有の検算**を全問でやる（参照の Mandatory check）。語順は枠の手検算に加え、必ず次を実行する:

```bash
python utils/validate_wordorder_questions.py data/questions/original/level{N}/wordorder_questions.txt
```

exit 0 以外なら直し、通るまで次に進まない。
9. 書き終わったら **この場では登録しない**。下の **After writing** の順でレビューへ進む（登録は目視のあと）。

## Authoring rules

- 難易度・形式は級の傾向に合わせてよい。中身は完全自作
- 場面は日常（家・学校・買い物・天気・趣味）。固有の組み合わせを公式と共有しない
- 5級: 短文、基本語彙、専門用語なし。解説はひらがな多め可
- 4級: 少し長い会話・簡単な接続詞まで
- 3級: 理由・経験・予定。読解は案内・メール・短い物語
- 音声は TTS／自作のみ。画像は自作またはライセンス済みのみ（公式切り出し禁止）
- イラストが必要なら、テキストを置いたあと `eiken-listening-illustration-images` を使う。参照画像に `data/archived_media/` は使わない

## After writing

カテゴリごと（またはまとめて）この順。飛ばさない。**登録は人の目視のあと**。

1. 作問（このスキル。テキストを `original/level{N}/` に置く）
2. `eiken-originality-review`（同一カテゴリの類似・公式由来との酷似・本当に original か）
3. `eiken-explanation-quality-review`（懇切丁寧）
4. `eiken-question-quality-review`（級適合・ダミーの質・正解偏り）
5. **人の目視**（公式公開過去問と並べて酷似最終確認。スキルの代用ではない）
6. 登録・ローカル確認（`--original` など。目視前に登録しない）

級の最小セットを積み上げるときは、カテゴリごとに 1〜4 を回し、セットが揃ってから 5→6 でもよい。いずれにせよ **6 の前に 5**。

登録コマンドの既定はレガシー取り込みを `blocked` にする。`original` は明示した新規だけ。

## Example requests

- 「5級の文法・語彙を10問、オリジナルで作って」
- 「5級の会話補充を5問追加」
- 「4級の語順をオリジナルで8問」
