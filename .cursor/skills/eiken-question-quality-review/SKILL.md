---
name: eiken-question-quality-review
description: Reviews and revises existing Eiken question quality by level and category, including level appropriateness, near-duplicate detection, and answer-choice bias checks. Use when asked to review a whole file or a question-number range like 10-20.
disable-model-invocation: true
---

# Eiken Question Quality Review

## Goal

指定された級・カテゴリの既存問題をレビューし、品質問題を特定して改訂する。

## Inputs to confirm

- 級（`5` / `4` / `3`）
- カテゴリ
- 対象範囲（全件 or 問題番号レンジ。例: 10〜20）
- 改訂方針（保守的に最小修正 / 積極修正）

## Review focus

1. **級適合性**: 語彙・文法・文長が該当級に合うか
2. **重複性**: 同一または実質同一の問題がないか
3. **選択肢品質**: 明らかに不自然なダミー選択肢がないか
4. **正解偏り**: 正解番号が偏っていないか（範囲内・全体）
5. **形式整合**: 番号、区切り、解説フィールドの欠落がないか

## Workflow

1. 対象ファイルと対象範囲を特定する。
2. 対象範囲を読み、問題ごとの懸念点をリスト化する。
3. 改訂候補を作成する（必要最小限の変更を優先）。
4. 修正をファイルへ反映する。
5. 変更後に再レビューして、同じ問題が残っていないか確認する。

## Revision policy

- 問題の意図を壊す大改造は避ける。
- 重複問題は「設定・文脈・正解根拠」を変えて差別化する。
- 正解偏り是正では、正解番号だけ変更せず選択肢全体の自然さを維持する。
- 変更理由を短く明示する（例: 「5級には難語のため語彙を平易化」）。

## Output format

- 修正した問題番号一覧
- 各問題の修正理由（1行）
- 必要なら未修正で残した理由

## Recommended commands

```bash
python utils/check_answer_distribution.py
```

## Example requests

- 「5級の文法問題のクオリティーをレビューして」
- 「5級の文法問題の10問目から20問目をレビュー・改訂して」
