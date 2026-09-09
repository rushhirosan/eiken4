# 4級 original 目視チェックリスト（登録前）

作業順の正本: `eiken-original-authoring` After writing  
**このチェックが終わるまで `--original` 登録しない。**

公式の公開過去問（協会サイト等）と並べて見る。リポジトリの公式由来 txt / PDF をチャットに貼らない。近いものがあれば番号だけメモし、場面を作り直す。

## 対象ファイル

| カテゴリ | パス | 目安件数（inventory 最小セット） |
|----------|------|----------|
| 文法・語彙 | `grammar_fill_questions.txt` | 40（比較・進行・不定詞・must・熟語・語彙） |
| 会話補充 | `conversation_questions.txt` | 30（励まし／礼・祝福／断り／快諾／値段／経験） |
| 語順 | `wordorder_questions.txt` | 28（`validate_wordorder_questions.py` 済） |
| 読解 | `reading_comprehesion_questions.txt` | 本文6 / 設問20（2セット。How many / How long / What color 含む） |
| Lイラスト | `listening_illustration_questions.txt` | 30 |
| L会話 | `listening_conversation_questions.txt` | 30 |
| L文章 | `listening_passage_questions.txt` | 28 |
| スピーキング | `speaking_questions.txt` | 10（How many / What color 含む） |

## アセット

| 種類 | 配置 | 状態メモ |
|------|------|----------|
| 音声 Part1 | `static/audio/level4/part1/listening_illustration_question{1–30}.mp3` | 1–30 TTS 済（18・21–30 は最新テキストで再生成含む） |
| 音声 Part2 | `static/audio/level4/part2/listening_conversation_question{1–30}.mp3` | 21–30 TTS 済 |
| 音声 Part3 | `static/audio/level4/part3/listening_passage_question{1–28}.mp3` | 21–28 TTS 済 |
| 画像 | `static/images/level4/part1/listening_illustration_image{1–30}.png` | 21–30 生成済・要目視（特に **image30** に看板文字が残る可能性） |

画像の注意:

- [ ] 文字・看板・吹き出しが入っていないか（特に **image9** は生成時に看板文字が混入しやすい）
- [ ] 会話の状況と矛盾しないか
- [ ] 白黒教育線画として違和感がないか

## カテゴリ共通（各問）

- [ ] 公式公開過去問と場面・選択肢・原稿が酷似していない
- [ ] 人名差し替えだけになっていない
- [ ] 正解が文脈上一つに決まる
- [ ] 4級の語彙・文長として妥当
- [ ] 解説を子供が一人で読める

## カテゴリ別

### 文法・語彙 / 会話補充

- [ ] 空所・発話の型が自然
- [ ] ダミーが「別の疑問詞への答え」など学習になる誤答になっている

### 語順

- [ ] 解説の全文と枠・①〜⑤が一致（2番目・4番目。スクリプト再実行可）

```bash
python utils/validate_wordorder_questions.py data/questions/original/level4/wordorder_questions.txt
```

### 読解

- [ ] 1セットが掲示2問・メール3問・物語5問（12 / 123 / 12345）
- [ ] 語数が4級目安（掲示約55・メール約130・物語約160）
- [ ] 案内・メール・物語の設定（行事名・日程骨格）が公式と被っていない
- [ ] 設問が本文に根拠がある。ダミーは本文の別情報になっている

### リスニング

- [ ] 音声を通して聞き、読み上げとテキストが一致
- [ ] イラスト問は画像を見ながら正解肢が自然か
- [ ] ひっかけが「会話の別情報」になっていて理不尽でない

### スピーキング

- [ ] パッセージが公式面接台本に近くない
- [ ] 内容2＋イラスト1＋自分1のバランスが取れている

## 完了後

1. 要修正があれば `original/level4/` の該当問だけ直す → 酷似・品質を再確認
2. 問題なければ登録例:

```bash
python manage.py register_grammar_fill_questions --level 4 --original
python manage.py register_conversation_fill_questions --level 4 --original
python manage.py register_wordorder_fill_questions --level 4 --original
python manage.py register_reading_comprehension_questions --level 4 --original
python manage.py register_listening_illustration_questions --level 4 --original
python manage.py create_listening_conversation_questions --level 4 --original
python manage.py create_listening_passage_questions --level 4 --original
python manage.py register_speaking_questions --level 4 --original
```

3. ローカルで公開クエリが original のみ見えることを確認
