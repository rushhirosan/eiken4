---
name: eiken-explanation-quality-review
description: Reviews and improves explanation quality for existing Eiken questions by level and category, with optional question-number range targeting. Use when explanations are unclear, too short, or not learner-friendly.
disable-model-invocation: true
---

# Eiken Explanation Quality Review

## Goal

既存問題の解説を、学習者にとって分かりやすく丁寧な内容へ改訂する。

## Inputs to confirm

- 級（`5` / `4` / `3`）
- カテゴリ
- 対象範囲（全件 or 問題番号レンジ。例: 10〜20）
- 文体（簡潔重視 / 丁寧重視）

## Review criteria

1. **わかりやすさ**: 初見の学習者が読んで理解できるか
2. **根拠の明確さ**: なぜ正解か、なぜ他が不正解かが説明されているか
3. **級適合性**: 使う日本語・英語用語が級に対して難しすぎないか
4. **一貫性**: 同カテゴリ内で解説の粒度が揃っているか
5. **有用性**: 再発防止の学習ポイントがあるか

## Workflow

1. 対象範囲の問題と解説を読む。
2. 解説不足の問題を抽出する（短すぎる、根拠不足、曖昧など）。
3. 同カテゴリの良い既存解説（必要なら他級も参照）をベースに改訂する。
4. 問題フォーマットを崩さず解説のみ更新する。
5. 改訂後にトーンと粒度をそろえる。

## Explanation writing rules

- 1〜3文で「正解理由」をまず示す。
- 必要なら1文で「誤答しやすいポイント」を補足する。
- 5級では専門用語を避け、短く具体的に書く。
- 内容が重複する定型文の連発を避ける。

## Output format

- 改訂した問題番号一覧
- 変更前の課題（短く）
- 改訂方針（短く）

## Example requests

- 「5級の文法問題の解説のクオリティーをレビューして」
- 「5級の文法問題の10問目から20問目の解説をレビュー・改訂して」
