# 仮想環境（venv）のセットアップ

## 仮想環境の作成と有効化

仮想環境は既に作成済みです。以下のコマンドで有効化できます：

```bash
source venv/bin/activate
```

## パッケージのインストール

必要なパッケージは既にインストール済みです。新しく追加する場合は：

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 開発サーバーの起動

```bash
source venv/bin/activate
python manage.py runserver
```

## 仮想環境の無効化

```bash
deactivate
```

## 注意事項

- Python 3.14を使用しているため、一部のパッケージは最新版がインストールされています：
  - Pillow: 12.1.0 (requirements.txtでは10.1.0を指定していますが、互換性のため最新版を使用)
  - psycopg2-binary: 2.9.11 (requirements.txtでは2.9.9を指定していますが、互換性のため最新版を使用)

## トラブルシューティング

### 仮想環境が認識されない場合

```bash
# 仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### パッケージのインストールエラーが発生した場合

```bash
# 最新版を試す
source venv/bin/activate
pip install --upgrade <パッケージ名>
```

