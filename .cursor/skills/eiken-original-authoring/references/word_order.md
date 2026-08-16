# word_order（語順）

ファイル: `wordorder_questions.txt`  
コマンド: `register_wordorder_fill_questions`  
日本語の意味に合うよう、①〜④から **1番目と3番目** の語を4択で選ぶ。

## Template

固定部分と①〜④は **重複させない**。下例では主語 `I` と末尾 `night` が固定、①〜④がちょうど4マス。

```
問題1:
私は夜，本を読みます。
① books ② at ③ read ④ I
[1番目] ( ) [3番目] ( ) night.

選択肢1:
1. ④ ─ ③
2. ③ ─ ①
3. ④ ─ ①
4. ② ─ ③

【正解1】
3. ④ ─ ①

【解説1】
I read books at night.
1番目は I、3番目は books です。全文は「私は夜、本を読みます」という意味になります。
「I + read + books + at + night」のじゅんばんを思い出しましょう。

---
```

別パターン（主語を枠の外に固定する例）:

```
① to ② school ③ walk ④ in
I [1番目] ( ) [3番目] ( ) the morning.
```

→ 全文 `I walk to school in the morning.`（①〜④は walk / to / school / in。`I` と `the morning` は枠固定で①〜④に入れない）

## Rules

- 日本語文 → ①〜④ → 英語の枠（`[1番目] ( ) [3番目] ( )`）→ 選択肢は `① ─ ③` 形式
- 正解の全文を解説に書く
- 5級: S+V / S+V+O / 簡単な前置詞句
- 3級: 疑問文・助動詞・不定詞を含む短い文まで

## Mandatory check（書くたびに・1問ずつ）

全文を `固定前置 + ①〜④の正しい順 + 固定後置` に分解する。

1. ①〜④は **ちょうど4語**（句を1番号にまとめるなら公式由来と同じ粒度）
2. 枠の `[1番目] ( ) [3番目] ( )` は **4マス**。ここに入るのが①〜④の順列
3. **①〜④のどの語も、枠の固定部分に再度書かない**（例: ③が `friends` なのに枠末尾にも `friends` と書くのは不可）
4. 【正解】の「1番目─3番目」が、分解した4語の **1語目と3語目** と一致する
5. 解説の全文が、その分解結果と文字どおり一致する

検算に落ちた問は書き直す。酷似レビューの前にこのチェックを終える。

```bash
python utils/validate_wordorder_questions.py data/questions/original/level{N}/wordorder_questions.txt
```

exit 0 以外ならファイルを直す。通るまで次（酷似・品質）に進まない。
