# listening_illustration（リスニングイラスト）

ファイル: `listening_illustration_questions.txt`  
コマンド: `register_listening_illustration_questions`

級で型が違う。5級 Part3 は `listening_passage` ではない。

## 5級 Part1（会話応答・No.1〜）

短い1文（または2文）に対する応答 3択。話者は `★` / `☆`。

```
No.1:
★Where is my hat?

Question No.1:
1. On the sofa.
2. It’s sunny.
3. I’m ten.

【正解1】
1. On the sofa.

【解説1】
放送文：Where is my hat?（ぼうしはどこ？）

「どこ？」と場所をたずねているので、1「On the sofa.（ソファのうえだよ）」が自然です。
2は天気、3は年齢で、場所の答えではありません。

---
```

## 5級 Part3（イラスト一致・No.101〜）

`questions/level_paths.py` の `LISTENING_ILLUSTRATION_PART3_MIN`（101）以上。放送3文からイラストに合うものを選ぶ。txt 上の選択肢は英文のまま書くが、**DB / UI の選択肢は 1・2・3 のみ**（英文は見せない）。

```
No.101:
(イラスト一致問題)

Question No.101:
1. The boy is opening the window.
2. The boy is washing the window.
3. The boy is making a window.

【正解101】
1. The boy is opening the window.

【解説101】
放送された3つの英文から、イラストの内容に合うものを選びます。
1「The boy is opening the window.（男の子はまどを開けている）」が正解です。
2はそうじ、3は「まどを作る」で、イラストと合いません。
動詞（opening / washing / making）の違いがポイントです。

---
```

Part3 は本問画像1枚（正解シーン）。選択肢用の参考画像を生成してもよいが、登録時の `choice_text` には入れない。生成は `eiken-listening-illustration-images`。`data/archived_media/` は使わない。

## 4級・3級（会話＋イラスト、応答3択）

短い会話のあとに、イラスト上の 1/2/3 に対応する応答。

```
No.1:
M: Let's go to the library after lunch.
W: OK.
M: What time do you want to go?

Question No.1:
1. At two.
2. It's twenty yen.
3. For three weeks.

【正解1】
1. At two.

【解説1】
放送文
M: Let's go to the library after lunch.（ひるごはんのあと、図書館に行こう。）
W: OK.（いいよ。）
M: What time do you want to go?（何時に行きたい？）

最後に時刻を聞いているので、1「At two.（2時に）」が自然です。
2は値段、3は期間です。

---
```

話者は `M:` / `W:`。選択肢は3つ。

## Rules

- ブロックは `No.N:` で始め、`Question No.N:`、`【正解N】`、`【解説N】`、`---`
- 5級 Part1 と 4/3級は選択肢テキストではなく番号が DB に入る（登録コマンドの分岐）
- 音声・画像は自作／TTS／新規生成のみ
