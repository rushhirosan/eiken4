---
name: eiken-question-authoring
description: Creates new Eiken questions for a specified level and category by scanning existing question files first, then appending similar-but-not-duplicate items in the same format. Use when asked to add N questions such as "5級の文法問題を10問作って追加".
disable-model-invocation: true
---

# Eiken Question Authoring

## Goal

指定された級・カテゴリの既存問題を踏まえて、形式互換を保った新規問題を追記する。

## Inputs to confirm

- 級（`5` / `4` / `3`）
- カテゴリ（`grammar_fill` / `conversation_fill` / `word_order` / `reading_comprehension` / `writing` / `listening_illustration` / `listening_conversation` / `listening_passage` / `listening_illustration_part3`）
- 追加問題数（例: 10）
- 必要なら対象範囲（例: 既存の末尾に追記のみ）

## File mapping

- 5級: `data/questions/level5/*.txt`
- 3級: `data/questions/level3/*.txt`
- 4級: `data/questions/*.txt`

カテゴリごとの実ファイル名は既存ファイルを優先して特定する（例: `grammar_fill_questions.txt`）。

## Workflow

1. 対象ファイルを読み、構造（区切り、番号、選択肢、解説）を把握する。
2. 直近20〜40問を中心に、出題パターンと難易度をスキャンする。
3. 類題を作るが、語句・状況・正解位置・言い換えを変えて重複を避ける。
4. 既存フォーマットを崩さずに末尾へ追記する。
5. 連番と区切り（`---`）を検証する。
6. 必要に応じて関連チェックを実行する。

## Authoring rules

- 既存問題の「型」は合わせるが、同一文面・同一選択肢セットは作らない。
- 同一ファイル内でのほぼ重複問題を避ける（主語差し替えだけは禁止）。
- 正解番号の偏りを減らす（追加分の中で偏らせない）。
- 級相応の語彙・文法だけを使う。
- 解説は簡潔かつ学習者に通じる表現にする。

## Validation checklist

- [ ] 追加件数が要求通り
- [ ] 問題番号が連番
- [ ] `---` 区切りが崩れていない
- [ ] 露骨な重複がない
- [ ] 正解位置の偏りが過度でない

## Recommended commands

```bash
# 級別の正解照合（必要時）
python utils/verify_level5_official_answers.py
python utils/verify_level3_official_answers.py

# 分布チェック
python utils/check_answer_distribution.py
```

## Example requests

- 「5級の文法問題を10問作って追加して」
- 「3級の会話補充を5問増やして」
