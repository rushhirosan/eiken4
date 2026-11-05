# 準2級 original 目視チェックリスト（登録・ベータ外し前）

作業順の正本: `eiken-original-authoring` After writing / `references/pre2.md`  
**このチェックが終わるまで「通常公開（ベータ外し）」としない。新規 `--original` 登録も目視の前にしない。**

公式の公開過去問（協会サイト等）と並べて見る。リポジトリの公式由来 txt / PDF をチャットに貼らない。近いものがあれば番号だけメモし、場面を作り直す。

## 対象ファイル

| カテゴリ | パス | 目安件数 |
|----------|------|----------|
| 文法・語彙 | `grammar_fill_questions.txt` | 50 |
| 会話補充 | `conversation_questions.txt` | 40（語順なし） |
| 読解 | `reading_comprehesion_questions.txt` | 本文9 / 設問27（長文空所＋内容一致） |
| L第1部（会話応答） | `listening_illustration_questions.txt` | 35（画像なし。内部 type は illustration） |
| L第2部（会話） | `listening_conversation_questions.txt` | 35 |
| L第3部（文章） | `listening_passage_questions.txt` | 35 |
| スピーキング | `speaking_questions.txt` | 10カード（内容1＋絵2＋自分2） |
| ライティング | `writing_questions.txt` | 12（メール6＋意見6） |

## アセット

| 種類 | 配置 | 状態メモ |
|------|------|----------|
| 音声 Part1 | `static/audio/levelpre2/part1/listening_illustration_question{1–35}.mp3` | 第1部は会話応答。画像不要 |
| 音声 Part2 | `static/audio/levelpre2/part2/listening_conversation_question{1–35}.mp3` | |
| 音声 Part3 | `static/audio/levelpre2/part3/listening_passage_question{1–35}.mp3` | |
| 画像 | なし | 第1部にイラストは出さない |
| スピーキング | テキスト内【Illustration】説明のみ | 別画像ファイル不要 |

音声の注意:

- [ ] 台本と読み上げが一致するか（変えた問は TTS し直す）
- [ ] Part1 が応答3択として自然か（イラスト一致になっていないか）

## カテゴリ共通（各問）

- [ ] 公式公開過去問と場面・選択肢・原稿が酷似していない
- [ ] 人名差し替えだけになっていない
- [ ] 正解が空所より前の本文だけで一つに決まる
- [ ] 準2級の語彙・文長として妥当（専門用具・級外句なし。`pre2.md` 語彙）
- [ ] 論外肢・否定エコーだけで正解が残っていない
- [ ] 解説の選択肢番号が、画面の並びに追従する書き方になっている
- [ ] 【ポイント】が語の意味と手がかりを混同していない

## カテゴリ別

### 文法・語彙

- [ ] 2文目・because・that が手がかり（3級の時制・関係代名詞・受動態だけの焼き直しにしない）
- [ ] 正解だけが本文の語を再利用して当たる形になっていない
- [ ] 学校場面がおおよそ6割以下。時刻比較型に偏っていない

### 会話補充

- [ ] 1会話おおよそ65語。A の説明一辺倒・前提の詰め込みすぎになっていない
- [ ] B の空所なのに `your` など視点がずれていない
- [ ] 誤答は会話中の別事実。隣同士で正解骨格が続いていない

### 読解

- [ ] 長文空所は設問が日本語。`Which choice best completes` がない
- [ ] メール約200語・説明文約250語以上。内容一致は本文ごとに質問が分かれている
- [ ] 誤答は本文の別事実（論外の中止・鍵閉めなどだけで落とさない）

### リスニング

- [ ] 第1部: 3往復・3肢・イラストなし。誤答は別発話への返事
- [ ] 第2部: 4往復・質問は言い換え
- [ ] 第3部: 約60語。時刻や because の写しだけで決まらない。`not A` の積み重ねに寄りすぎていない

### スピーキング

- [ ] パッセージ約50語。内容1＋Picture A/B＋自分2
- [ ] No.2 が1動作質問になっていない
- [ ] 絵の描写語が級内

### ライティング

- [ ] メール: 下線1か所・Do you think・返信40〜50語・質問2つは下線について
- [ ] 意見: 50〜60語・意見＋理由2つ
- [ ] 3級の「下線2問に答える」型になっていない

## 模擬試験（プロダクト）

- [ ] `_get_mock_exam_structure('pre2')` が文法15・会話5・読解本文3・L各10
- [ ] 制限時間が筆記80分／リスニング25分
- [ ] 本番画面で通しが動く（ライティング・面接は別メニューのまま）

## 完了後

1. 要修正があれば `original/levelpre2/` の該当問だけ直す → 酷似・品質を再確認
2. 進捗を残す更新なら行削除なしの反映手順（`eiken-question-operations` / `eiken-fly-operations`）
3. about / guides / try の「ベータ・改善中」文言を外すのは、この目視が終わってから

```bash
# 例: 進捗を消さない反映は運用スキルに従う。一括 --original 再登録は回答が消えるので使わない。
python3 manage.py check
python3 manage.py test exams.tests.ExamViewTests.test_mock_exam_structure_pre2_matches_full_practice_set
```
