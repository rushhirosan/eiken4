# 英検学習アプリ

Django製の英検学習Webアプリケーションです。文法、リーディング、リスニング問題を提供します。

## 🚀 セットアップ

### 必要要件

- Python 3.9+
- PostgreSQL (本番環境)
- SQLite (開発環境)

### インストール

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# マイグレーション
python manage.py migrate

# 静的ファイルの収集
python manage.py collectstatic --noinput

# 開発サーバーの起動
python manage.py runserver
```

## 📊 データベースメンテナンス

### 💰 課金削減：2段階アプローチ

#### Phase 1: データクリーンアップ ✅

古いデータを削除してDB使用量を削減

**クイックスタート:**

```bash
fly ssh console -a eiken-app
python manage_production.py cleanup_database --dry-run  # 確認
python manage_production.py cleanup_database --vacuum   # 実行
```

詳細なガイド:

- 📘 [クイックガイド](QUICK_CLEANUP_GUIDE.md) - 今すぐ実行する方法
- 📗 [詳細ガイド](DATABASE_CLEANUP.md) - 完全なドキュメント

#### Phase 2: ボリューム縮小（10GB→1GB）💡

ボリュームサイズを縮小して**月額約$1.35削減**

**クイックスタート:**

```bash
./migrate_db_volume.sh  # 自動実行（10分で完了）
```

詳細なガイド:

- 🚀 [クイックスタート](VOLUME_MIGRATION_QUICK_START.md) - 10分で完了
- 📙 [詳細ガイド](VOLUME_MIGRATION_GUIDE.md) - 完全な手順

**削減効果:**

- ボリュームサイズ: 10GB → 1GB（90%削減）
- 月額コスト: 約$1.35削減

### 自動クリーンアップ

GitHub Actionsで毎月自動的にクリーンアップを実行します:

1. GitHubのSettings > Secretsに`FLY_API_TOKEN`を追加
2. ワークフローが毎月1日に自動実行されます

手動実行: GitHub Actions > "Database Cleanup" > "Run workflow"

### データベース分析

```bash
fly postgres connect -a eiken-app-db < analyze_db_size.sql
```

## 🏗️ プロジェクト構造

```
eiken/
├── accounts/           # ユーザー認証
├── exams/             # 試験・問題管理
├── questions/         # 問題データ
├── eiken_project/     # プロジェクト設定
├── static/            # 静的ファイル（音声、画像）
├── templates/         # テンプレート
└── utils/             # ユーティリティスクリプト
```

## 📱 機能

- ✅ ユーザー登録・ログイン
- ✅ 文法・語彙問題
- ✅ 長文読解問題
- ✅ リスニング問題（3部構成）
- ✅ 学習進捗の記録
- ✅ 正答率の表示
- ✅ レベル別問題（Grade 4〜Pre-Grade 1）

## 🔧 管理コマンド

### データベースクリーンアップ

```bash
# Dry run（削除せず確認のみ）
python manage.py cleanup_database --dry-run

# 実際に削除（90日前より古い回答履歴、180日前より古い進捗データ）
python manage.py cleanup_database

# カスタム期間で削除
python manage.py cleanup_database --answers-days 60 --progress-days 120

# VACUUM処理も実行
python manage.py cleanup_database --vacuum
```

### 問題データのインポート

```bash
python manage.py import_questions
```

## 🌐 デプロイ（Fly.io）

### 初回デプロイ

```bash
fly launch
fly postgres create
fly postgres attach eiken-app-db
fly deploy
```

### 更新デプロイ

```bash
fly deploy
```

### データベース接続

```bash
fly ssh console -a eiken-app
fly postgres connect -a eiken-app-db
```

## 📈 モニタリング

### ログの確認

```bash
fly logs -a eiken-app
fly logs -a eiken-app-db
```

### データベースサイズの確認

```bash
fly postgres connect -a eiken-app-db
SELECT pg_size_pretty(pg_database_size(current_database()));
```

## 🔒 セキュリティ

- SECRET_KEYは環境変数で管理
- 本番環境ではDEBUG=False
- CSRF対策を実装
- セッションはデータベースに保存

## 📝 ライセンス

プライベートプロジェクト

## 👥 貢献

このプロジェクトはクローズドソースです。

## 📞 サポート

問題が発生した場合は、以下を確認してください:

- [データベースクリーンアップガイド](DATABASE_CLEANUP.md)
- [クイックガイド](QUICK_CLEANUP_GUIDE.md)
- アプリケーションログ: `fly logs -a eiken-app`

