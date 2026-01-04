# セキュリティログ確認ガイド

## 開発環境でのログ確認方法

### 1. 開発サーバーを起動

```bash
python manage.py runserver
```

### 2. ログインを試行

ブラウザで以下の操作を行います：

#### ログイン成功のログを確認
1. 正しいユーザー名とパスワードでログイン
2. ターミナルに以下のようなログが表示されます：

```
INFO 2025-01-XX XX:XX:XX views [SECURITY] ログイン成功: username=testuser, ip=127.0.0.1, user_agent=Mozilla/5.0...
```

#### ログイン失敗のログを確認
1. 間違ったパスワードでログインを試行
2. ターミナルに以下のようなログが表示されます：

```
WARNING 2025-01-XX XX:XX:XX views [SECURITY] ログイン失敗: username=testuser, ip=127.0.0.1, user_agent=Mozilla/5.0..., errors={...}
```

#### レート制限超過のログを確認
1. 5分間に5回以上ログインを試行（失敗でも成功でも可）
2. ターミナルに以下のようなログが表示されます：

```
WARNING 2025-01-XX XX:XX:XX views [SECURITY] ログイン試行レート制限超過: username=testuser, ip=127.0.0.1, user_agent=Mozilla/5.0...
```

### 3. ログをファイルに保存して確認（オプション）

ターミナルで以下のコマンドを実行すると、ログをファイルに保存できます：

```bash
python manage.py runserver 2>&1 | tee logs/django.log
```

または、`grep`でセキュリティログだけを抽出：

```bash
python manage.py runserver 2>&1 | grep "\[SECURITY\]"
```

## 本番環境（Fly.io）でのログ確認方法

### 1. Fly.ioのログをリアルタイムで確認

```bash
fly logs
```

### 2. 特定のアプリのログを確認

```bash
fly logs -a eiken-app
```

### 3. セキュリティログだけをフィルタリング

```bash
fly logs -a eiken-app | grep "\[SECURITY\]"
```

### 4. ログイン関連のログだけを確認

```bash
fly logs -a eiken-app | grep -E "(ログイン成功|ログイン失敗|レート制限超過)"
```

## ログの形式

### ログイン成功
```
INFO {timestamp} views [SECURITY] ログイン成功: username={username}, ip={ip_address}, user_agent={user_agent}
```

### ログイン失敗
```
WARNING {timestamp} views [SECURITY] ログイン失敗: username={username}, ip={ip_address}, user_agent={user_agent}, errors={errors}
```

### レート制限超過
```
WARNING {timestamp} views [SECURITY] ログイン試行レート制限超過: username={username}, ip={ip_address}, user_agent={user_agent}
```

## トラブルシューティング

### ログが表示されない場合

1. **ログレベルを確認**
   - `settings.py`の`LOGGING`設定で`accounts`ロガーのレベルが`INFO`以上になっているか確認

2. **ログハンドラーを確認**
   - `accounts`ロガーに`console`と`security_console`ハンドラーが設定されているか確認

3. **カスタムログインビューが使用されているか確認**
   - `accounts/urls.py`で`CustomLoginView`が登録されているか確認
   - `eiken_project/urls.py`で`accounts.urls`が先に読み込まれているか確認

## ログをファイルに保存する設定（オプション）

本番環境でログをファイルに保存したい場合は、`settings_production.py`の`LOGGING`設定にファイルハンドラーを追加できます。

