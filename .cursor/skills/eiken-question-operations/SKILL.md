---
name: eiken-question-operations
description: Guides safe updates for Eiken question data files, registration management commands, and listening asset linkage. Use when editing question text, importing new sets, or fixing registration errors.
---

# Eiken Question Operations

## Goal

問題データ更新を、壊さず・戻せる形で実行する。

## Standard workflow

1. バックアップを作成する。
2. 編集先を間違えない: **4級**は `data/questions/*.txt`、**3級**は `data/questions/level3/*.txt`。**4級ファイルを 3級用に上書きしない。**
3. 対応する `manage.py` コマンドを実行する（3級は **`--level 3`**）。
4. 必要なら `update_audio_paths` を実行する（主に 4級パス向け。3級は登録コマンドが `level_paths` でパスを組み立てる）。
5. 実画面で最低限の表示と再生を確認する。

## Commands

```bash
python manage.py dumpdata questions > data/questions_backup.json

# 4級（既定のまま）
python manage.py register_grammar_fill_questions
python manage.py register_conversation_fill_questions
python manage.py register_wordorder_fill_questions
python manage.py register_reading_comprehension_questions
python manage.py register_listening_illustration_questions
python manage.py create_listening_conversation_questions
python manage.py create_listening_passage_questions

# 3級（同じコマンド名 + --level 3。テキストは data/questions/level3/）
python manage.py register_grammar_fill_questions --level 3
# …他も同様に --level 3 を付与可能

python manage.py update_audio_paths
```

ユーティリティ（PDF 抽出・TTS）の出力先は `utils/pdf_text_extractor.py` 等の引数・環境変数、または `utils/eiken_paths.py` と `--level` で 3級に切り替え可能。既定は 4級レイアウトのまま。

## Practical checks

- 問題数が想定通りか（極端な増減がないか）
- 解説テキストが空になっていないか
- リスニング問題で `audio_file` / `image_file` が有効か
- **3級**: 正解変更後は `python utils/verify_level3_official_answers.py` で F日程公式PDFと一致することを確認する（[grade_3 過去問](https://www.eiken.or.jp/eiken/exam/grade_3/) → 解答PDF `202501F3kyu.pdf` 等）。D日程 `*D3kyu*` は照合に使わない。

## Common pitfalls

- テキスト区切り（`---`）の崩れ
- 問題番号重複
- 音声ファイル名とDBパスの不一致
