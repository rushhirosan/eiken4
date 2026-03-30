# 問題データの登録・検証

次の文脈で、適切な Django 管理コマンドと確認手順を提案または実行してください。

## 前提の確認

- 変更したのは `data/questions/` のどのファイルか、または `questions/management/commands/` のどれか

## やってほしいこと

1. 問題タイプに対応する `register_*` / `create_*` コマンドを特定する（`docs/question_update_flow_specification.md` の一覧を参照）。
2. プロジェクトルートで実行する想定のコマンドを `python manage.py ...` 形式で示す。
3. コマンドが既存データを削除してから入れ直すタイプかどうかを明記し、本番で実行するときの注意を一行入れる。
4. 可能なら `python manage.py check` を実行して結果を報告する。

ユーザーが「実行しないで」と言っていない限り、venv を有効にしたうえでコマンドを実際に試してよい。
