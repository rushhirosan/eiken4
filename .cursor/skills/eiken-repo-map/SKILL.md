---
name: eiken-repo-map
description: Maps this Eiken Django repository structure, main app responsibilities, and operational entry points. Use when navigating files, adding features, or understanding where to implement changes.
---

# Eiken Repository Map

このスキルは「どこに何があるか」を素早く把握するためのガイドです。

## Main apps

| Path | Role |
|------|------|
| `accounts/` | 認証、ログイン、ユーザーモデル |
| `exams/` | 出題、解答、進捗、結果表示 |
| `questions/` | 問題データモデルと登録コマンド |
| `eiken_project/` | URL・settings・全体設定 |

## Data and assets

| Path | Role |
|------|------|
| `data/questions/` | 問題データのテキストソース |
| `static/audio/` | リスニング音声 |
| `static/images/` | リスニング画像 |
| `templates/`, `exams/templates/` | 画面テンプレート |

## Operational entry points

- ローカル起動: `python manage.py runserver`
- 管理コマンド: `python manage.py <command>`
- 本番起動スクリプト: `scripts/start.sh`
- デプロイ設定: `config/` および `fly.toml` 系ファイル

## Change guidance

1. 画面表示変更はまず `views.py` と対応テンプレートをセットで確認。
2. 問題更新ロジックは `questions/management/commands/` を優先して拡張。
3. 音声/画像を扱う変更は `update_audio_paths` と静的パス整合を必ず確認。
