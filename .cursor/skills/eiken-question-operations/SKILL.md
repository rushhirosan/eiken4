---
name: eiken-question-operations
description: Guides safe updates for Eiken question data files, registration management commands, and listening asset linkage. Use when editing question text, importing new sets, or fixing registration errors.
---

# Eiken Question Operations

## Goal

問題データ更新を、壊さず・戻せる形で実行する。

## Standard workflow

1. バックアップを作成する。
2. `data/questions/` の対象ファイルを編集する。
3. 対応する `manage.py` コマンドを実行する。
4. 必要なら `update_audio_paths` を実行する。
5. 実画面で最低限の表示と再生を確認する。

## Commands

```bash
python manage.py dumpdata questions > data/questions_backup.json
python manage.py register_grammar_fill_questions
python manage.py register_conversation_fill_questions
python manage.py register_wordorder_fill_questions
python manage.py register_reading_comprehension_questions
python manage.py register_listening_illustration_questions
python manage.py create_listening_conversation_questions
python manage.py create_listening_passage_questions
python manage.py update_audio_paths
```

## Practical checks

- 問題数が想定通りか（極端な増減がないか）
- 解説テキストが空になっていないか
- リスニング問題で `audio_file` / `image_file` が有効か

## Common pitfalls

- テキスト区切り（`---`）の崩れ
- 問題番号重複
- 音声ファイル名とDBパスの不一致
