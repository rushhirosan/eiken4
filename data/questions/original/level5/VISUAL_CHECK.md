# 5級 original 目視チェックリスト（登録前）

作業順の正本: `eiken-original-authoring` After writing  
**このチェックが終わるまで `--original` 登録しない。**

公式の公開過去問（協会サイト等）と並べて見る。リポジトリの公式由来 txt / PDF をチャットに貼らない。近いものがあれば番号だけメモし、場面を作り直す。

機械チェック（エージェント済み・再実行可）:

```bash
python utils/validate_original_questions.py --level 5
python utils/validate_wordorder_questions.py data/questions/original/level5/wordorder_questions.txt
```

## 対象ファイル

| カテゴリ | パス | 件数 |
|----------|------|-----:|
| 文法・語彙 | `grammar_fill_questions.txt` | 30 |
| 会話補充 | `conversation_questions.txt` | 30 |
| 語順 | `wordorder_questions.txt` | 30 |
| Lイラスト | `listening_illustration_questions.txt` | 30（Part1: 1–20 / Part3: 101–110） |
| L会話 | `listening_conversation_questions.txt` | 20 |
| スピーキング | `speaking_questions.txt` | 10 |

5級に読解・ライティング・L文章は作らない（仕様どおり）。

## アセット

| 種類 | 配置 | 状態メモ |
|------|------|----------|
| 音声 Part1 | `static/audio/level5/part1/listening_illustration_question{1–20}.mp3` | 16–20 TTS 済（最新テキスト） |
| 音声 Part2 | `static/audio/level5/part2/listening_conversation_question{1–20}.mp3` | 16–20 TTS 済 |
| 音声 Part3 | `static/audio/level5/part3/listening_illustration_question{101–110}.mp3` | 既存 |
| 画像 Part1 | `static/images/level5/part1/listening_illustration_image{1–20}.png` | 16–20 線画生成済・要目視 |
| 画像 Part3 | `static/images/level5/part1/listening_illustration_image{101–110}.png`（＋ choice 任意） | 既存 |

画像の注意:

- [ ] 文字・看板・吹き出しが入っていないか（特に **image20** カレンダー周り）
- [ ] 会話の状況と矛盾しないか（16 お絵かき / 17 かばん / 18 バナナ / 19 くれよん / 20 日付）
- [ ] 白黒教育線画として 1–15 とテイストが大きく違わないか

## カテゴリ共通（各問）

- [ ] 公式公開過去問と場面・選択肢・原稿が酷似していない
- [ ] 人名差し替えだけになっていない
- [ ] 正解が文脈上一つに決まる
- [ ] 5級の語彙・文長として妥当（ひらがな多めの解説で読める）
- [ ] 解説を子供が一人で読める
- [ ] `【ポイント】` が見出しだけで意味を持ち、解説のコピペだけになっていない

## カテゴリ別

### 文法・語彙（特に Q21–30）

- [ ] 前置詞・Whose / mine / many / 進行 / can / because / Have a 〜 / goes が自然
- [ ] Q21 `on the wall` が under と複数正解になっていない
- [ ] ダミーが学習になる誤答（別品詞の羅列だけにしない）

### 会話補充（特に Q21–30）

- [ ] 礼 / You’re welcome / 誘い / 断り / 依頼 / 謝罪 / 感情 / 同意 / 歓迎 / 提案の機能が自然
- [ ] 誤答が別のスピーチアクトになっている

### 語順（特に Q21–30）

- [ ] 解説の全文と枠・①〜④が一致（1番目・3番目）
- [ ] 疑問文パターン（How much / Who / What does / When / Can / Is / What time / What do）が崩れていない
- [ ] チップ語が枠の固定部分と重複していない

```bash
python utils/validate_wordorder_questions.py data/questions/original/level5/wordorder_questions.txt
```

### リスニング

- [ ] 音声を通して聞き、読み上げとテキストが一致（Part1 16–20 / Part2 16–20）
- [ ] Part1 は応答3択・★／☆、Part2 は☆／★＋`☆☆`
- [ ] Part3（101–110）はイラスト一致のまま
- [ ] ひっかけが「会話の別情報」で理不尽でない
- [ ] L会話の焦点（how much / who / color / how many / how）が聞き取れる

### スピーキング

- [ ] 内容2＋自分1（イラストなし）
- [ ] パッセージが公式面接台本に近くない（特に Q6–10: Pool / Skateboard / Saturday Afternoon / Friend / Store）

## inventory カバレッジ（ざっと）

新規で埋めた穴の確認用（詳細は `docs/inventory/level5/`）:

- [ ] 文法: 前置詞・所有・進行・can・because・定型
- [ ] 会話: 礼・誘い・断り・依頼・謝罪・感情
- [ ] 語順: 疑問語順
- [ ] L会話: how much / who / color / how many / how
- [ ] Lイラスト: 提案・礼・同意・Whose・日付

## 完了後

1. 要修正があれば `original/level5/` の該当問だけ直す → 酷似・品質を再確認
2. 音声・画像を直した問は TTS / 画像を再生成
3. 問題なければ登録例:

```bash
python manage.py register_grammar_fill_questions --level 5 --original
python manage.py register_conversation_fill_questions --level 5 --original
# （他カテゴリも同様。リスニングは画像・音声パス確認後）
```

4. 公開前チェック（`.cursor/rules/original-questions.mdc`）を通してから本番反映

## メモ（エージェント作業ログ）

| 日付 | 内容 |
|------|------|
| 2026-09-10 | 公開セットを 30/30/30/30/20/10 に拡充。酷似分を差し替え。Q21 複数正解修正。L 16–20 TTS・線画。新規解説を厚くした。 |
| 2026-09-10 | ユーザー指示で本番登録へ進む（VISUAL_CHECK 台帳作成・preflight-original OK・公開前チェック前提で `--original`）。 |
