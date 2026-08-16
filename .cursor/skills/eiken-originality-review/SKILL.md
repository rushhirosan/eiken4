---
name: eiken-originality-review
description: Reviews original practice questions for near-duplicates in the same category, similarity to official-derived items, and true originality before human visual check. Use when asked to 酷似チェック, 類似, 公式と並べる前のレビュー, or verify provenance=original candidates in data/questions/original/.
---

# Originality Review

目視の前に、自作候補が本当にオリジナルか見る。教育的な難しさや解説の丁寧さは見ない（それらは `eiken-question-quality-review` / `eiken-explanation-quality-review`）。

## Inputs to confirm

- 級（`5` / `4` / `3`）
- カテゴリ
- 対象（新規追加分 / ファイル全件 / 番号レンジ）

対象ファイルは `data/questions/original/level{N}/` のみ。

## Comparison corpus

公式PDFは開かない。比較に使うのは、すでにリポジトリにある公式由来テキスト:

| 級 | パス |
|----|------|
| 5 | `data/questions/level5/` |
| 4 | `data/questions/*.txt`（`level3` / `level5` / `original` 以外の直下） |
| 3 | `data/questions/level3/` |

同一カテゴリの **他の original ファイル** も見る（自作同士の重複）。

`data/pdf_import/` は使わない。公式文面をチャットに書き出さない。

## What to flag

- 本文が同一、または言い換えだけ
- 場面＋行為＋目的語など、固有の組み合わせが同じ（人名差し替えだけ）
- 選択肢セットが同じ、または3つ同じで1つだけ違う
- リスニング: 会話の流れ・質問の切り口・イラスト状況が同じ
- 読解: 掲示・メールの設定（行事名・日程の骨格）が同じ
- original 同士のほぼ重複

形式（4択・穴埋め・部構成）が同じだけではフラグしない。

## Verdicts

| 判定 | 意味 |
|------|------|
| 通す | 目視へ回してよい |
| 直す | 近い。場面か選択肢を作り直す |
| 差し替え | 公式由来または他の自作と実質同じ。その問は使わない |

迷ったら **直す** または **差し替え**。通すは差が大きいときだけ。

## Workflow

1. 対象の original ブロックを読む。
2. 同カテゴリの original 同士を先に見る。
3. 公式由来ファイルをスキャンする。近い候補の **番号だけ** メモする。
4. 問ごとに判定を付ける。
5. 直す／差し替えは、公式文を示さず「どう変えるか」だけ書く。
6. 差し替えが必要な問を残したまま「公開可」としない。

作問者と同じターンなら、直す分は `eiken-original-authoring` のルールで書き直してから再チェックする。

## Report format

公式の問題文・選択肢・原稿は載せない。

```
対象: 5級 grammar_fill / original Q1–10

Q1  通す
Q2  直す  — 既存5級文法の No.xx 付近と場面が近い（場所＋テレビ）。場所か行為を変える
Q3  差し替え — 選択肢セットが既存 No.yy と実質同一
...

目視へ: Q1, Q4, ...
書き直し後に再チェック: Q2, ...
破棄: Q3, ...
```

最後に一文: 人が公式の公開過去問と並べて目視する。このレビューは目視の代用ではない。

## Example requests

- 「今作った5級文法を酷似チェックして」
- 「original の5級会話補充を、公式由来と類似がないか見て」
