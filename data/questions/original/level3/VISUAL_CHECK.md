# 3級 original 目視チェックリスト（登録前）

作業順の正本: `eiken-original-authoring` After writing  
**このチェックが終わるまで `--original` 登録しない。**

公式の公開過去問（協会サイト等）と並べて見る。リポジトリの公式由来 txt / PDF をチャットに貼らない。近いものがあれば番号だけメモし、場面を作り直す。

## 対象ファイル

| カテゴリ | パス | 目安件数 |
|----------|------|----------|
| 文法・語彙 | `grammar_fill_questions.txt` | 10 |
| 会話補充 | `conversation_questions.txt` | 10 |
| 語順 | `wordorder_questions.txt` | 10（`validate_wordorder_questions.py` 済） |
| 読解 | `reading_comprehesion_questions.txt` | 本文6（掲示2問・メール3問・物語5問を2セット） |
| Lイラスト | `listening_illustration_questions.txt` | 10 |
| L会話 | `listening_conversation_questions.txt` | 10 |
| L文章 | `listening_passage_questions.txt` | 10 |
| スピーキング | `speaking_questions.txt` | 5（イラスト説明付き） |
| ライティング | `writing_questions.txt` | 5（メール返信） |

## アセット

| 種類 | 配置 | 状態メモ |
|------|------|----------|
| 音声 Part1 | `static/audio/level3/part1/listening_illustration_question{1–10}.mp3` | image1/2 は場面差し替え済。登録時に該当 TTS を再生成 |
| 音声 Part2 | `static/audio/level3/part2/listening_conversation_question{1–10}.mp3` | テキスト10問。登録時に TTS（既存は1–5） |
| 音声 Part3 | `static/audio/level3/part3/listening_passage_question{1–10}.mp3` | テキスト10問。登録時に TTS（既存は1–5） |
| 画像 | `static/images/level3/part1/listening_illustration_image{1–10}.png` | 生成済・640×426・要目視 |
| スピーキング | テキスト内【Illustration】説明のみ | 別画像ファイル不要 |

画像の注意:

- [ ] 文字・看板・吹き出しが入っていないか（生成時に混入しやすい）
- [ ] 会話の状況と矛盾しないか（**image1** は改札の機械のうえの定期、**image2** は体育館ドア横のリサイクル箱。床にびんが落ちていないか）
- [ ] 白黒教育線画として違和感がないか

## カテゴリ共通（各問）

- [ ] 公式公開過去問と場面・選択肢・原稿が酷似していない
- [ ] 人名差し替えだけになっていない
- [ ] 正解が文脈上一つに決まる
- [ ] 3級の語彙・文長として妥当（理由・経験・予定まで可）
- [ ] 解説を子供が一人で読める

## カテゴリ別

### 文法・語彙 / 会話補充

- [ ] 空所・発話の型が自然（接続詞・比較・不定詞・現在完了・受動態など）
- [ ] ダミーが「別の疑問詞への答え」など学習になる誤答になっている

### 語順

- [ ] 解説の全文と枠・①〜⑤が一致（2番目・4番目）

```bash
python3 utils/validate_wordorder_questions.py data/questions/original/level3/wordorder_questions.txt
```

### 読解

- [ ] 1セットが掲示2問・メール3問・物語5問（12 / 123 / 12345）
- [ ] 語数が3級目安（掲示約100・メール約280–300・物語約250）
- [ ] 案内・メール・物語の設定が公式と被っていない
- [ ] 設問が本文に根拠がある。メールは用件をまたぐ。物語は理由・目的を含む

### リスニング

- [ ] 音声を通して聞き、読み上げとテキストが一致
- [ ] イラスト問は画像を見ながら正解肢が自然か
- [ ] ひっかけが「会話の別情報」になっていて理不尽でない

### スピーキング

- [ ] パッセージが公式面接台本に近くない
- [ ] 内容1＋イラスト2＋自分2のバランス
- [ ] イラスト説明と質問が対応している

### ライティング

- [ ] メールの題材が公式と被っていない
- [ ] 下線部2問に答える形が崩れていない
- [ ] 参考解答が 15〜25 語目安に収まる

## 完了後

1. 要修正があれば `original/level3/` の該当問だけ直す → 酷似・品質を再確認
2. 問題なければ登録例:

```bash
python3 manage.py register_grammar_fill_questions --level 3 --original
python3 manage.py register_conversation_fill_questions --level 3 --original
python3 manage.py register_wordorder_fill_questions --level 3 --original
python3 manage.py register_reading_comprehension_questions --level 3 --original
python3 manage.py register_listening_illustration_questions --level 3 --original
python3 manage.py create_listening_conversation_questions --level 3 --original
python3 manage.py create_listening_passage_questions --level 3 --original
python3 manage.py register_speaking_questions --level 3 --original
python3 manage.py register_writing_questions --level 3 --original
```

（コマンド名は `eiken-question-operations` / 既存4級手順に合わせて最終確認すること）
