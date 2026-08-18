# reading_comprehension（読解）

ファイル: `reading_comprehesion_questions.txt`（綴り注意）  
コマンド: `register_reading_comprehension_questions`  
**4級・3級のみ。** 5級では作らない。

公式の長文大問に合わせ、**1セット = 掲示2問 + メール3問 + 物語5問**（12 / 123 / 12345）。  
公開用 original はこれを **2セット**（本文6、設問20）置く。

ラベルは本文番号＋a〜e（登録コマンドが `問題Na:` を読むため）。画面では本文ごとに 問題 1, 2, 3… と表示される。

## 級別の分量

| | 掲示（2問） | メール（3問） | 物語（5問） |
|--|------------|--------------|------------|
| 4級 | 約 55 語 | 約 130 語 | 約 160 語 |
| 3級 | 約 100 語 | 約 280–300 語 | 約 250 語 |

- 4級: 具体語彙。`and` / `but` / `so` / `because` / `if`。現在完了は使わない
- 3級: 理由・目的・条件。メールは用件を2つ以上。物語は段落をまたぐ設問を混ぜる
- 本文を公式の掲示・メールの改変にしない

## Template（4級・掲示の骨格）

```
本文1
Park Day
There will be a park day for families in May.

When: May 10
Where: Green Park

Children can play games and eat lunch under the trees.

We will meet at the school gate and walk to the park.

If you want to come, talk to Mr. Sato before April 20.

問題1a:
What can children do at the park?

選択肢1a:
1. Swim in a pool.
2. Play games.
3. Ride a train.
4. Visit a museum.

【正解1a】
2. Play games.

【解説1a】
本文に「Children can play games and eat lunch under the trees」とあります。プール・電車・博物館の記述はありません。

問題1b:
Where will they meet?

選択肢1b:
1. At the school gate.
2. In Mr. Sato's room.
3. At the bus stop.
4. Under the trees.

【正解1b】
1. At the school gate.

【解説1b】
集合場所は「We will meet at the school gate」と書いてあります。木の下は昼食の場所、Sato先生は申し込み先です。

---
```

メールは `From:` / `To:` / `Subject:` で始め、設問は `問題2a`〜`2c`。  
物語は地の文で、設問は `問題3a`〜`3e`（事実・理由・別段落の情報を混ぜる）。

次のセットは本文4=掲示、本文5=メール、本文6=物語。

## Rules

- ブロックは `本文N` で始め、設問は `問題Na:` / `選択肢Na:` / `【正解Na】` / `【解説Na】`
- ダミーは本文の別情報（別の日付・場所・用件）を優先する。無関係な語だけにしない
- 1セット（10問）で正解番号 1〜4 が極端に偏らないようにする
