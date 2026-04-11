---
description: Pre-release checklist for this Django/Fly project.
---

# Release check

## ローカル検証

```bash
python manage.py check
python manage.py test
```

## 変更確認

```bash
git status
git diff
```

## セキュリティ/秘密情報チェック

- `.env` や鍵情報を含むファイルをコミット対象に入れない
- `eiken_project/settings.py` の本番設定影響を再確認

## デプロイ

```bash
fly deploy
```
