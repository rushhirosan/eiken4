---
name: eiken-question-pipeline
description: 英検の問題データ更新フロー（PDF→テキスト→DB→試験画面）を案内する。4級の既定パスと 3級の level3 配下、register/create の --level、問題登録コマンド、docs/question_update_flow_specification.md に沿った作業で使う。
---

# 英検問題パイプライン

## 一次情報

- 統合仕様: リポジトリの `docs/question_update_flow_specification.md` を開き、該当セクション（問題タイプ・コマンド名・パス）を確認する。

## アプリの役割

- `questions/`: マスタ登録・専用モデル・`questions/management/commands/` の登録・作成コマンド。
- `exams/`: ユーザー向け試験・`exams.models.Question` 中心・進捗・回答履歴。
- データファイル: **4級**は `data/questions/*.txt`。**3級**は `data/questions/level3/*.txt`（ファイル名は 4級と同じ）。多くの `register_*` / `create_*` と形式が結合している。
- **4級のパスを `level3` 用に置き換えない**（4級マスタは直下のまま）。

## 級と登録コマンド（`--level`）

- すべての対象コマンドに **`--level`** あり（**既定 `4`**）。**3級**は **`--level 3`** → テキストは `data/questions/level3/`、DB は `level='3'`、音声・画像の保存パスは `questions/level_paths.py` の規約（例: `audio/level3/part2/...`）。
- 実装の単一ソース: Django 側 `questions/level_paths.py`、PDF/TTS 系ユーティリティ `utils/eiken_paths.py`（`--level` / 環境変数 `EIKEN_LEVEL` 等）。

## 登録コマンド（仕様書と一致させる）

| 用途の目安 | コマンド例（`python manage.py <name>`） |
|-----------|----------------------------------------|
| 文法・語彙 | `register_grammar_fill_questions`（例: `--level 3`） |
| 会話補充 | `register_conversation_fill_questions` |
| 語順 | `register_wordorder_fill_questions` |
| 長文読解 | `register_reading_comprehension_questions` |
| リスニング第1部 | `register_listening_illustration_questions` |
| リスニング第2部 | `create_listening_conversation_questions` |
| リスニング第3部 | `create_listening_passage_questions` |

実装・引数の詳細は各 `questions/management/commands/*.py` と仕様書。

## 作業時のチェック

1. 変更するのは **テキスト** か **コマンド** か **モデル/ビュー** かを切り分ける。
2. テキスト形式を変えるなら **パース処理を同じ PR / コミットで**直す。
3. 音声・画像は `static/` と DB に保存するパス表記が両方ずれないか確認する（必要なら `exams` の `update_audio_paths` を確認）。

## 本番・運用

- DB 削減・Fly.io・クリーンアップは `docs/README.md` の「データベースメンテナンス」節を参照。
