---
name: eiken-django-dev
description: eiken4 リポジトリでの Django 開発・検証手順をまとめる。runserver、migrate、静的ファイル、本番設定ファイルの場所、セキュリティログの確認を依頼されたときに使う。
---

# eiken4 Django 開発メモ

## 環境

- 依存: ルートの `requirements.txt`（本番用の複製が `config/requirements.txt`）。
- ローカル DB: 通常 SQLite（`docs/README.md` のセットアップ手順）。
- 本番設定: `eiken_project/settings_production.py`、`config/fly.toml` など。

## よく使うコマンド

```bash
python manage.py migrate
python manage.py runserver
python manage.py collectstatic --noinput   # 本番前・静的変更時
python manage.py check
```

## テスト・品質

- アプリごとに `tests.py` がある。変更範囲に合わせて `python manage.py test <app>` を実行する。

## セキュリティログ（認証まわり）

- 開発時: `runserver` 出力の `[SECURITY]`。手順の詳細は `docs/security_logging_guide.md`。

## デプロイ

- Fly.io 手順は `docs/README.md` のデプロイ節。ログは `fly logs` など。
