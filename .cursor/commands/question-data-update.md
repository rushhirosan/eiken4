---
description: Update question datasets and register them into DB safely.
---

# Question data update

## 事前バックアップ

```bash
python manage.py dumpdata questions > data/questions_backup.json
```

## 問題タイプごとの登録コマンド

```bash
python manage.py register_grammar_fill_questions
python manage.py register_conversation_fill_questions
python manage.py register_wordorder_fill_questions
python manage.py register_reading_comprehension_questions
python manage.py register_listening_illustration_questions
python manage.py create_listening_conversation_questions
python manage.py create_listening_passage_questions
```

## リスニング音声パス更新

```bash
python manage.py update_audio_paths
```

## 動作確認

- 管理画面 or 問題ページで表示確認
- 音声問題は再生確認も実施
