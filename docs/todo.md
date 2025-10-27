- [x] 不要なファイルやディレクトリを整理
- [x] backupsディレクトリを削除
- [x] 一時的なスクリプトファイルを削除
- [x] 出力ファイルとmemoファイルを削除
- [x] 重複ファイルを削除
- [x] プロジェクトホームのファイル構造を整理
- [x] docsディレクトリにドキュメントを整理
- [x] scriptsディレクトリにスクリプトを整理
- [x] dataディレクトリにデータファイルを整理
- [x] 不要なファイルを削除
- [x] 問題更新フローを仕様に書きたい
- [x] 全問題タイプの統合仕様書を作成
- [x] 仕様書を1つに統合
- [] 残りのuntracked filesをgitに追加するか判断


## 最終的なディレクトリ構造

プロジェクトホーム/
├── docs/                    # ドキュメント
│   └── README.md
├── scripts/                 # スクリプト
│   └── start.sh
├── data/                    # データファイル
│   ├── all_questions_export.json
│   ├── conversation_questions_export.json
│   ├── grammar_questions_export.json
│   ├── word_order_questions_export.json
│   └── questions_data.json
├── accounts/               # Djangoアプリ
├── exams/                 # Djangoアプリ
├── questions/             # Djangoアプリ
├── eiken_project/         # Djangoプロジェクト設定
├── static/               # 静的ファイル
├── templates/            # テンプレート
├── utils/               # ユーティリティ
└── manage.py           # Django管理コマンド
