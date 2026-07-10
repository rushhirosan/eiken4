# 英検5級 過去問 PDF（インポート用）

## 問題冊子・リスニング原稿

| 回 | 問題冊子 | リスニング原稿 |
|----|---------|---------------|
| 2025年度第2回 | `2025-2-1ji-5kyu.pdf` | `2025-2-1ji-5kyu_script.pdf` |
| 2025年度第3回 | `2025-3-1ji-5kyu.pdf` | `2025-3-1ji-5kyuscript.pdf` |
| 2026年度第1回 | `2026-1-1ji-5kyu.pdf` | `2026-1-1ji_5kyuscript.pdf` |

## 解答（F日程のみ・正解照合の一次情報）

- `202502F5kyu_answers.pdf`（2025年度第2回）
- `202503F5kyu_answers.pdf`（2025年度第3回）
- `202601F5kyu_answers.pdf`（2026年度第1回）

**D日程の解答PDFは使わない**（3級と同様、過去問冊子と正解がずれることがある）。

照合: `python utils/verify_level5_official_answers.py`

## テキスト生成

`python utils/build_level5_questions.py` → `data/questions/level5/*.txt`

## 音声・画像

| 公式 | 配置先 | ファイル名 |
|------|--------|-----------|
| リスニング Part1 | `static/audio/level5/part1/` | `listening_illustration_question{1-30}.mp3` |
| リスニング Part2 | `static/audio/level5/part2/` | `listening_conversation_question{1-15}.mp3` |
| リスニング Part3 | `static/audio/level5/part3/` | `listening_illustration_question{31-60}.mp3` |

**イラスト画像**（本問用）: `static/images/level5/part1/listening_illustration_image{1-60}.png`

過去問 PDF から一括抽出:

```bash
python utils/extract_level5_illustrations.py
python manage.py register_listening_illustration_questions --level 5
```

音声のプレースホルダー生成のみ必要な場合: `python utils/setup_level5_assets.py`
