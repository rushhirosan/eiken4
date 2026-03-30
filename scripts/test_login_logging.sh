#!/bin/bash
# ログインログのテストスクリプト

echo "=== ログインログテスト ==="
echo ""
echo "このスクリプトは、ログイン成功/失敗のログが正しく記録されるかテストします。"
echo ""
echo "手順:"
echo "1. 開発サーバーを起動しているターミナルでログを監視してください"
echo "2. 以下のコマンドでログインを試行します"
echo ""

# テストユーザーの作成（存在しない場合）
echo "テストユーザーを作成しますか？ (y/n)"
read -r answer
if [ "$answer" = "y" ]; then
    python manage.py shell << EOF
from accounts.models import CustomUser
try:
    user = CustomUser.objects.get(username='testuser')
    print("テストユーザーは既に存在します")
except CustomUser.DoesNotExist:
    user = CustomUser.objects.create_user(username='testuser', password='testpass123')
    print("テストユーザーを作成しました: testuser / testpass123")
EOF
fi

echo ""
echo "=== テスト1: ログイン成功 ==="
echo "正しい認証情報でログインを試行します..."
curl -X POST http://127.0.0.1:8000/accounts/login/ \
  -d "username=testuser&password=testpass123" \
  -c cookies.txt \
  -b cookies.txt \
  -L \
  -s -o /dev/null

echo "ターミナルに 'ログイン成功' のログが表示されているか確認してください"
echo ""
read -p "Enterキーを押して次に進む..."

echo ""
echo "=== テスト2: ログイン失敗 ==="
echo "間違ったパスワードでログインを試行します..."
curl -X POST http://127.0.0.1:8000/accounts/login/ \
  -d "username=testuser&password=wrongpassword" \
  -c cookies.txt \
  -b cookies.txt \
  -L \
  -s -o /dev/null

echo "ターミナルに 'ログイン失敗' のログが表示されているか確認してください"
echo ""
read -p "Enterキーを押して次に進む..."

echo ""
echo "=== テスト3: レート制限 ==="
echo "5回連続でログインを試行します（レート制限のテスト）..."
for i in {1..6}; do
    echo "試行 $i/6..."
    curl -X POST http://127.0.0.1:8000/accounts/login/ \
      -d "username=testuser&password=wrongpassword" \
      -c cookies.txt \
      -b cookies.txt \
      -L \
      -s -o /dev/null
    sleep 1
done

echo "ターミナルに 'レート制限超過' のログが表示されているか確認してください"
echo ""

# クリーンアップ
rm -f cookies.txt

echo "=== テスト完了 ==="
echo ""
echo "確認ポイント:"
echo "1. ログイン成功時に 'ログイン成功' のログが表示される"
echo "2. ログイン失敗時に 'ログイン失敗' のログが表示される"
echo "3. レート制限超過時に 'ログイン試行レート制限超過' のログが表示される"
echo "4. すべてのログに [SECURITY] タグが付いている"
echo "5. ログにIPアドレス、ユーザー名、User-Agentが含まれている"

