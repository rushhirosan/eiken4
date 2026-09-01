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
| `speaking` スピーキング | ○（流れ練習） | ○ | ○ | [speaking.md](references/speaking.md) |
| `reading_comprehension` 読解 | × | ○ | ○ | [reading_comprehension.md](references/reading_comprehension.md) |
| `writing` ライティング | × | × | ○ | [writing.md](references/writing.md) |

5級に読解・ライティング・`listening_passage` は作らない。5級リスニング第3部は文章問題ではなく **イラスト一致**（`listening_illustration` の No.101+）。

## 公式形式（必須）

新規も追記も、級の公式1回分に近い型を崩さない。件数は依頼に従うが、**枠・話者・セット構成は変えない。** 詳細とテンプレは各 `references/*.md`。

| カテゴリ | 5級 | 4級 | 3級 |
|----------|-----|-----|-----|
| 文法・語彙 | 短文／短い2人会話。身近な名詞・be/一般動詞 | 前置詞・時制の基本・簡単な助動詞 | 接続詞・比較・不定詞・現在完了・受動態のやさしい用法 |
| 会話補充 | 短いやりとり。誤答は別の疑問詞への答え | 4級らしい長さ。誤答は聞き違い | 理由・経験・予定まで。4級の焼き直しにしない |
| 語順 | ①〜④、空所は **1番目と3番目**（日本文つき） | ①〜⑤、空所は **2番目と4番目**（日本文つき） | 4級と同じ5語枠。不定詞・現在完了など |
| 読解 | 作らない | **1セット＝掲示2＋メール3＋物語5**。公開は2セット（本文6・設問20）。掲示約55／メール約130／物語約160語 | 同じセット構成。掲示約100／メール約280–300／物語約250語。メールは用件をまたぐ |
| Lイラスト | Part1（No.1–）会話応答3択（★／☆）。Part3（No.101+）イラスト一致3英文 | 会話＋イラスト、応答3択。話者 **M: / W:**。画像は会話と矛盾させない | 4級と同じ型。3級らしい理由・条件。画像と会話を一致 |
| L会話 | ☆／★、末尾 `☆☆`。一問一答で取れる情報。現行セット15問 | **M: / W:**、`☆☆` なし。4ターン前後。現行セット10問 | 同じ話者。理由・条件・現在完了を混ぜる。現行セット10問 |
| L文章 | 作らない | 1人モノローグ（M: または W:）。現行セット10問 | 同じ型。やや長め。現行セット10問 |
| スピーキング | 内容2＋自分1。**イラストなし** | **内容2＋イラスト1＋自分1** | **内容1＋イラスト2＋自分2** |
| ライティング | 作らない | 作らない | **Eメール**（下線部2問・15〜25語）＋**意見論述**（25〜35語）。2024年度〜2題 |

## 本番出題数と公開セット

本番の1回分の配分（形式の正本）。公開セットは練習用に増量してよいが、**枠・話者・セット構成は崩さない**。

### 5級（一次のみ・面接なし）

| 技能 | 大問 | 本番問題数 | 時間 |
|------|------|----------:|------|
| R | 大問1 短文空所 | 15 | 25分 |
| R | 大問2 会話空所 | 5 | |
| R | 大問3 語句整序（日本文つき） | 5 | |
| L | 第1部 会話応答（3択） | 10 | 約20分 |
| L | 第2部 会話内容一致 | **5** | |
| L | 第3部 イラスト内容一致 | 10 | |

語彙目安 約600〜630語。合格基準 419/850（目安6割）。勉強時間の目安 約5〜10時間。

学習の伸びやすい順（参考）: 単語 → 穴埋め → 語順 → リスニング。

### 4級（一次のみ・面接なし・ライティングなし）

| 技能 | 大問 | 本番問題数 | 時間 |
|------|------|----------:|------|
| R | 大問1 短文空所 | 15 | 35分 |
| R | 大問2 会話空所 | 5 | |
| R | 大問3 語句整序（日本文つき） | 5 | |
| R | 大問4 長文内容一致（掲示・メール・説明文） | 10 | |
| L | 大問1 会話応答（**3択・選択肢読み上げ**） | 10 | 約30分 |
| L | 大問2 会話内容一致 | 10 | |
| L | 大問3 文内容一致 | 10 | |

語彙目安 約900〜1,300語（中学1〜2年）。合格基準 622/1000（目安6〜7割）。勉強時間の目安 約30時間。

学習の伸びやすい順（参考）: 単語 → 穴埋め → 語順 → リスニング。

### 3級（一次＋二次面接）

| 技能 | 大問 | 本番問題数 | 時間 |
|------|------|----------:|------|
| R | 大問1 短文空所 | 15 | R+W 65分 |
| R | 大問2 会話空所 | 5 | |
| R | 大問3 長文内容一致 | 10 | |
| W | Eメール返信 | 1（15〜25語） | |
| W | 意見論述 | 1（25〜35語） | |
| L | 第1〜3部 各 | 10 | 約25分 |

語彙目安 約1,210語。一次合格 1103/1650、二次 353/550。勉強時間の目安 約30時間。

学習の伸びやすい順（参考）: 単語 → 穴埋め → ライティング（Eメール→意見） → 長文 → リスニング → 面接。

### 現行の公開セット件数

本番より多いカテゴリは **練習用増量**。品質レビューで難易度の偏りがないか確認する。

- 5級: 文法20・会話20・語順20・L第1部15・L会話15・L第3部10・スピーキング5
- 4級: 文法20・会話20・語順20・読解本文6/設問20・L各部10・スピーキング10
- 3級: 4級と同型（文法20・会話20・語順20・読解本文6/設問20・L各部10・スピーキング10）＋ ライティング10（**Eメールと意見論述の両形式を目指す**。現行はメールのみの場合あり）

5級リスニング TTS は既定 **-15%**（`utils/text_to_speech.py`）。画像はプレースホルダー禁止。白黒線画で会話／正解シーンと一致させる。

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
4. 級の **公式形式表** と該当 `references/*.md` を守って書く。枠・話者・セット構成を独自に変えない。
5. 解説も同時に書く（詳細は `eiken-explanation-quality-review`）。
6. `---` 区切り・連番・選択肢数を崩さない。
7. 追加分の正解番号が極端に偏らないようにする。
8. **カテゴリ固有の検算**を全問でやる（参照の Mandatory check）。語順は枠の手検算に加え、必ず次を実行する:

```bash
python utils/validate_wordorder_questions.py data/questions/original/level{N}/wordorder_questions.txt
```

exit 0 以外なら直し、通るまで次に進まない。
9. 書き終わったら **この場では登録しない**。下の **After writing** の順でレビューへ進む（登録は目視と公開前チェックのあと）。

## Authoring rules

- 難易度・形式は級の傾向に合わせてよい。中身は完全自作
- 場面は日常（家・学校・買い物・天気・趣味）。固有の組み合わせを公式と共有しない
- 5級: 短文、基本語彙（色・動物・食べ物・曜日・基本動詞・定型表現・前置詞など）、専門用語なし。解説はひらがな多め可
- 4級: 少し長い会話・簡単な接続詞まで。頻出パターン例: `need to do`, `look for`, `have a good time`, `wait for`, `get up`
- 3級: 理由・経験・予定。読解は案内・メール・短い物語。4級の焼き直しにしない
- 音声は TTS／自作のみ。画像は自作またはライセンス済みのみ（公式切り出し禁止）
- イラストが必要なら、テキストを置いたあと `eiken-listening-illustration-images` を使う。参照画像に `data/archived_media/` は使わない

## After writing

カテゴリごと（またはまとめて）この順。飛ばさない。**登録は人の目視と公開前チェックのあと**。

1. 作問（このスキル。テキストを `original/level{N}/` に置く）
2. `eiken-originality-review`（同一カテゴリの類似・公式由来との酷似・本当に original か）
3. `eiken-explanation-quality-review`（懇切丁寧）
4. `eiken-question-quality-review`（級適合・ダミーの質・正解偏り）
5. **人の目視**（公式公開過去問と並べて酷似最終確認。スキルの代用ではない）
6. **公開前チェック**（`.cursor/rules/original-questions.mdc`。1つでも未なら登録しない）
7. 登録・ローカル確認（`--original` など。目視・公開前チェックの前に登録しない）

級の最小セットを積み上げるときは、カテゴリごとに 1〜4 を回し、セットが揃ってから 5→6→7 でもよい。いずれにせよ **7 の前に 5 と 6**。

登録コマンドの既定はレガシー取り込みを `blocked` にする。`original` は明示した新規だけ。

## Example requests

- 「5級の文法・語彙を10問、オリジナルで作って」
- 「5級の会話補充を5問追加」
- 「4級の語順をオリジナルで8問」
