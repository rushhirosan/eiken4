# 英検3級 過去問 PDF（インポート用・配信外）

> 配信パイプラインからは切り離し済み。詳細は [`../README.md`](../README.md)。
> ツール実行は `ALLOW_LEGACY_PDF_IMPORT=1` が必要。

## 2026年度第1回

| 種別 | ファイル |
|------|---------|
| 問題冊子 | `2026-1-1ji-3kyu.pdf` |
| リスニング原稿 | `2026-1-1ji_3kyuscript.pdf` |
| 解答（F日程） | `202601F3kyu_answers.pdf` |
| 音源 Part1/2/3 | `3Q-part1.mp3` 等 |

テキスト生成・追記: `python utils/build_level3_202601.py`  
追加登録（既存削除なし）: `python manage.py append_new_questions --level 3`

アプリ通し番号（2026①）:

- 文法 101–115 / 会話 51–55
- 読解 本文16–18
- ライティング 21–22（メール＋英作文の2題）
- リスニング各部 No.41–50

正解照合の一次情報は **F日程** のみ（`202601F3kyu.pdf`）。D日程は使わない。
