---
description: Run this Django project locally (setup, migrate, runserver).
---

# Local development

## 初回セットアップ

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## 開発サーバー起動

```bash
python manage.py runserver
```

ブラウザ: `http://127.0.0.1:8000/`

## よく使う確認

```bash
python manage.py check
python manage.py test
```
