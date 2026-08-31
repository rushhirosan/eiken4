---
name: eiken-study-point-review
description: Reviews and improves the 【ポイント】 study-point blocks attached to original Eiken-style questions so learners can copy them into notes. Use when asked to review ポイント, add 学習ポイント, check study_points quality, or improve the まとめ shown on the answer results screen.
---

# Study Point Review

`【ポイントN】` は「この問題で何を覚えて帰るか」を1枚にしたもの。解答結果画面で解説の手前と、下部の「今回のまとめ」表に出る。**学習者がそのままノートに写せる**ことがゴール。

解説（`【解説N】`）とは役割が違う。解説は「この問題の答えの理由」、ポイントは「次に似た問題が出たときに使う知識」。両方を直したいときは `eiken-explanation-quality-review` を先に通す。

## Inputs to confirm

- 級（`5` / `4` / `3`）とカテゴリ
- 対象範囲（全件 or 番号レンジ）
- 新規付与か、既存ポイントのレビューか

対象は `data/questions/original/level{N}/` のみ。パースは `questions/study_points.py`、格納先は `exams.Question.study_points`。

## Format

```
【ポイント1】
種別: 文法
見出し: Why の答えは Because（理由を表すつなぎ言葉）
・Because のあとは「主語 + 動詞」の文が続く
・Although は逆接、Before / Until は時を表す
・理由が名詞ひとつなら because of を使う
```

- 置き場所: `【解説N】` の直後、`---` の前
- `種別:` は 単語 / 熟語 / 文法 / 会話 / 読解 / リスニング のいずれか（`Question.STUDY_POINT_BADGE_CLASSES` のキー。増やすならモデルも直す）
- `見出し:` は1行。`・` 行は2〜4本
- 読解など識別子つき（`【ポイント1a】`）は登録コマンドの suffix 対応が要る

## Review criteria

1. **一般化されているか**: その問題限定の説明でなく、次の問題で使える形か
2. **見出しが単体で意味を持つか**: まとめ表では見出しだけ拾い読みされる
3. **解説の要約になっていないか**: 解説を短くしただけならポイントの価値がない
4. **種別が正しいか**: 語のかたまりで覚えるものは熟語、規則は文法
5. **級の範囲か**: 上の級の用語・例を持ち込んでいないか
6. **粒度がそろっているか**: 同じ級・カテゴリ内で情報量に差がないか
7. **箇条書きが独立しているか**: 前の行を読まないと分からない行を作らない

## Level bar

### 5級

- 文法用語を出さない。「〜のとき使う」「形はこう」で書く
- 例は必ず英語の実物（`on the desk = 机の上`）
- `・` は2本まで

### 4級

- 用語は基本的なものだけ（比較級、過去形 など）。使うなら例とセット
- 対比を1本入れる（`under = 下、in = 中`）

### 3級

- 変化形・活用をまとめて置く（`see - saw - seen`）
- 紛らわしい相手との違いを1本入れる（`made of` と `made from`）
- 例文の型を書く（`If it rains tomorrow, we will 〜`）

## Good / Bad

**Bad**（解説の縮小コピー・その問題限定）

```
【ポイント5】
種別: 文法
見出し: 正解は was broken
・窓は壊されたので受動態になる
```

**Good**（次に使える形）

```
【ポイント5】
種別: 文法
見出し: 受動態「be動詞 + 過去分詞」（〜される／された）
・時制は be動詞で表す（was broken = 壊された）
・動作をした人は by 〜 で表す
・break - broke - broken の変化を覚える
```

## Workflow

1. 対象 txt を読み、問題文・正解・解説とポイントを突き合わせる。
2. 上の criteria で問題のあるポイントを挙げる。新規付与なら「その問題の核」を1つに絞る。
3. `【ポイント】` ブロックだけ直す。問題文・選択肢・正解・解説は触らない。
4. パースを確認する。

```bash
source venv/bin/activate && python -c "
from questions.study_points import extract_study_points
c=open('data/questions/original/level3/grammar_fill_questions.txt',encoding='utf-8').read()
blocks=[b for b in c.split('---') if b.strip()]
for i,b in enumerate(blocks,1):
    sp=extract_study_points(b)
    if not sp or not sp['category'] or not sp['title'] or not sp['keys']:
        print('要確認:',i,sp)
print('total',len(blocks))
"
```

5. 種別の偏りを見る（全部「文法」になっていないか）。
6. 登録して画面で確認する。

```bash
python manage.py register_grammar_fill_questions --level 3 --original
```

## Do not

- 公式の解説・参考書の要約をそのまま写さない（`original-questions.mdc` の公開前チェックはポイント文にも効く）
- 正解そのものを見出しに書かない（`見出し: 答えは on` は不可）
- 1つのポイントに複数の文法事項を詰め込まない。分けられないなら問題側を見直す
- 未登録のまま本番へ出さない。登録は目視と公開前チェックのあと

## Output format

- 対象の級・カテゴリ・問題番号
- 直した理由（criteria の番号で短く）
- 種別の内訳（例: 文法15 / 熟語5）
- パース確認の結果

## Example requests

- 「3級文法のポイントをレビューして」
- 「3級の会話補充にポイントを付けて」
- 「まとめ表の見出しが弱いので直して」
