---
name: eiken-fly-operations
description: Covers practical Fly.io operations for this Eiken Django app, including deploy, log checks, and production DB maintenance flow. Use when handling release or production troubleshooting.
---

# Eiken Fly Operations

## Scope

- Fly.io へのデプロイ
- ログ確認
- DBメンテナンス系の運用作業

## Core commands

```bash
fly deploy
fly logs -a eiken-app
fly ssh console -a eiken-app
fly postgres connect -a eiken-app-db
```

## Production maintenance references

- DBクリーンアップ: `python manage_production.py cleanup_database --dry-run`
- 実行例: `python manage_production.py cleanup_database --vacuum`

## Safety checklist

1. 先に `python manage.py check` / `python manage.py test` を通す。
2. 変更に秘密情報が含まれないことを確認する。
3. デプロイ後にログを確認し、500系エラー有無をチェックする。

## Troubleshooting focus

- 起動失敗時は `scripts/start.sh` の `collectstatic` / `migrate` 失敗を優先確認
- 認証系不具合は `accounts` ロガーと `docs/security_logging_guide.md` を参照
