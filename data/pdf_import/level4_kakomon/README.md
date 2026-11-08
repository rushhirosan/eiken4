# 英検4級 過去問 PDF（インポート用・配信外）

> 配信パイプラインからは切り離し済み。詳細は [`../README.md`](../README.md)。
> ツール実行は `ALLOW_LEGACY_PDF_IMPORT=1` が必要。

## 一次試験

| 回 | 問題冊子 | リスニング原稿 | 解答（F日程） | 音源（ローカル・gitignore） |
|----|---------|---------------|--------------|---------------------------|
| 2025年度第3回 | `2025-3-1ji-4kyu.pdf` | `2025-3-1ji-4kyuscript.pdf` | `202503F4kyu_answers.pdf` | `2025-3-4Q-part{1,2,3}.mp3` |
| 2026年度第1回 | `2026-1-1ji-4kyu.pdf` | `2026-1-1ji_4kyuscript.pdf` | `202601F4kyu_answers.pdf` | `4Q-part{1,2,3}.mp3` |
| 2026年度第2回 | `2026-2-1ji-4kyu.pdf` | `2026-2-1ji_4kyuscript.pdf` | `202602F4kyu_answers.pdf` | `2026-2-4Q-part{1,2,3}.mp3` |

テキスト生成・追記（2026①）: `python utils/build_level4_202601.py`  
追加登録（既存削除なし）: `python manage.py append_new_questions --level 4`

アプリ通し番号（2026①）:

- 文法 166–180 / 会話 56–60 / 語順 26–30
- 読解 本文13–15
- リスニング各部 No.41–50

正解照合の一次情報は **F日程** のみ。D日程は使わない。
