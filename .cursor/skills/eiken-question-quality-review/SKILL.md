---
name: eiken-question-quality-review
description: Reviews original practice questions for level fit, dummy-choice quality, answer-position bias, and format integrity. Use when asked to review question quality or 級に合っているか, not for official-similarity (use eiken-originality-review).
---

# Question Quality Review

オリジナル問題の **学習品質** を見る。公式との酷似は扱わない → `eiken-originality-review`。解説の丁寧さは扱わない → `eiken-explanation-quality-review`。

## Inputs to confirm

- 級（`5` / `4` / `3`）
- カテゴリ
- 対象範囲（全件 or 番号レンジ）
- 改訂方針（最小修正 / 積極修正）

対象は `data/questions/original/level{N}/`。公式由来ファイルを直して「オリジナルにする」作業はしない。

## Review focus

1. **級適合**: 語彙・文法・文長がその級か（5級に難語、3級に幼稚すぎ、など）
2. **選択肢**: ダミーが不自然な英語／明らかにハズレすぎ／正解が文脈上複数、がないか
3. **正解偏り**: 対象範囲で 1〜4 が極端に偏っていないか
4. **形式**: 番号、`---`、【正解】【解説】、選択肢数
5. **自作内の重複**: 人名だけ違う同型。IP 用の公式比較は originality 側
6. **構造の正しさ（カテゴリ別）**: 見た目の丁寧さより先に、枠と正解が機械的に成り立つか。**公式形式は `eiken-original-authoring` の「公式形式」表と一致させる**（独自の語順枠・読解セット・スピーキング配分にしない）

### 級別形式チェック（品質レビューでも見る）

- 語順: 5級は①〜④の1・3番目、4/3級は①〜⑤の2・4番目
- 読解（4/3のみ）: 1セットが掲示2＋メール3＋物語5。公開は2セット
- スピーキング: 5級は内容2＋自分1（イラストなし）。4級は内容2＋イラスト1＋自分1。3級は内容1＋イラスト2＋自分2
- L会話: 5級は☆／★＋`☆☆`。4/3級は M: / W:（`☆☆` なし）
- Lイラスト: 5級 Part1 は応答3択、Part3（101+）はイラスト一致。4/3級は会話と画像が矛盾しない
- 5級に読解・ライティング・L文章を足していないか

### word_order 必須検算

各問について解説の全文を、枠の `固定前置 + チップ順 + 固定後置` に分解する。

- チップ数＝枠のマス数（5級は①〜④の4マス、4級・3級は①〜⑤の5マス）
- 【正解】のラベルが指定位置と一致すること（5級は1番目・3番目、4/3級は2番目・4番目）
- **チップの語が枠の固定部分に再度出ていないこと**（`friends` が③と枠末尾の両方、など）
- 1問でも落ちたら「通す」にしない。直すか差し替える

酷似チェック（`eiken-originality-review`）は文面の近さだけ見る。**この構造バグは originality では拾えない**ので、品質レビュー側の担当。

語順は手検算に加え、必ずスクリプトを実行する:

```bash
python utils/validate_wordorder_questions.py data/questions/original/level{N}/wordorder_questions.txt
```

**original 全カテゴリ**（語順以外も含む）は Phase 2 バリデータを必ず通す:

```bash
python utils/validate_original_questions.py --level {N}
# または全級
python utils/validate_original_questions.py
```

`./scripts/preflight-original.sh` も内部で実行する。ERROR 0 でない限り「品質 OK」にしない。WARN（正解偏り）は内容を確認する。

## Workflow

1. 対象ファイルと範囲を特定する。
2. カテゴリ固有の構造検算を先にやる（語順は上記スクリプト）。
3. 問ごとにその他の懸念をリストする。
4. 最小修正を優先して直す。意図を壊す大改造はしない。
5. 正解番号だけ動かして偏りを消さない。選択肢全体が自然なままにする。
6. 変更理由を1行で残す。

## Revision policy

- 5級の難語は身近な語に置き換える
- 複数正解になる空所は、文脈を足して1つにする
- 意味不明なダミーは「別の疑問詞への答え」など、ありそうな誤りにする
- 酷似の疑いは直さず、`eiken-originality-review` に回す

## Output format

- 修正した問題番号と理由（1行）
- 未修正で残したものと理由
- 酷似の疑いは番号だけ列挙し、originality-review へ

```bash
python utils/check_answer_distribution.py
```

（分布スクリプトが original パス未対応なら、対象ブロックの正解番号を数える。）

## Example requests

- 「5級文法オリジナルの品質をレビューして」
- 「10〜20問目の選択肢が不自然なので見て」
