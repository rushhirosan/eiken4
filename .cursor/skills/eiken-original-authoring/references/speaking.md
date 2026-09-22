# speaking（スピーキング流れ練習）

ファイル: `speaking_questions.txt`  
コマンド: `register_speaking_questions`  
二次試験の「流れ」を練習するオリジナル。録音・面接の公式台本は使わない。

## 5級

短いパッセージの黙読・音読 → 内容2問 → 自分のこと1問。

```
問題1:
【Title】
My Cat

【Passage】
Mika is 9 years old. She has a cat. The cat's name is Mochi. Mochi is white. Mika likes Mochi.

【Questions】
1. How old is Mika?
2. What color is Mochi?
3. What animal do you like?

【参考解答】
■ この問題で求められること
約20語のパッセージを黙読→音読したあと、内容についての質問2問と、自分自身についての質問1問に答えます。

■ 音読のポイント
・一文ずつ区切ってはっきり読む
・Mika / Mochi などの名前も丁寧に

■ 参考解答の例
1. She is 9 years old.
2. She is white. / Mochi is white.
3. I like dogs. / I like cats. / I like birds.

■ 表現のメモ
内容質問は He / She / It に置き換えて答えると自然です。No.3 は自分の答えを短く言えばOKです。

---
```

## 4級

パッセージ＋イラスト。内容2・イラスト1・自分のこと1。

```
問題1:
【Title】
Park Picnic

【Passage】
Hana is 10 years old. She rides to the park every Saturday. She takes a small lunch and meets her friend Aya there.

【Illustration】
公園。女の子が木の下でおにぎりを食べている。もう一人の女の子が水筒の水を飲んでいる。

【Questions】
1. [passage] When does Hana go to the park?
2. [passage] Who does she meet there?
3. [illustration] What is the girl under the tree eating?
4. [personal] Do you like going to the park?
```

## 3級

パッセージ＋イラスト説明。内容1・イラスト2・自分のこと2。

```
問題1:
【Title】
Saturday Morning

【Passage】
Many families stay home on Saturday morning. Some people cook breakfast. Others read books or watch TV. It is a quiet time of the week.

【Illustration】
台所。お母さんがパンを焼いている。お父さんが新聞を持ってソファへ向かう吹き出しがある。テーブルにカップが2つある。

【Questions】
1. [passage] Please look at the passage. When do many families stay home?
2. [illustration] Please look at the picture. What is the woman doing?
3. [illustration] Please look at the picture. What is the man going to do?
4. [personal] Do you stay home on Saturday morning?
5. [personal] What do you like to do at home?

【参考解答】
■ この問題で求められること
約30語を黙読・音読し、内容1問・イラスト2問のあと、自分のこと2問に答えます。

■ 参考解答の例
1. They stay home on Saturday morning. / On Saturday morning.
2. She is baking bread. / Cooking.
3. He is going to read a newspaper. / He's going to sit on the sofa.
4. Yes, I do. / No, I don't.
5. I watch TV. / I play games.

■ 表現のメモ
No.4 が Yes なら Please tell me more.、No なら What do you usually do on Saturday morning?

---
```

### 3級イラスト問のバラし（必須）

各カードの No.2 / No.3 は、**少なくとも1問を「What is X doing?」以外**にする。

| 型 | 質問例 | Illustration に必要な手がかり |
|----|--------|-------------------------------|
| 進行形 | What is the girl doing? | いまの動作 |
| going to | What is the man going to do? | 思考吹き出し・これから |
| holding / looking at | What is she holding? / What is she looking at? | 持ち物・視線先 |
| 数え・位置 | How many cups …? / Where is the radio? | 数えられる小物・位置 |

パッセージの中心物（radio / market / library など）を Illustration の小物としても出し、可能ならイラスト問の一方で触れる。

### 3級の面接官フレーズ

No.1 は `Please look at the passage.`、No.2・3 は `Please look at the picture.` を設問先頭に付ける。No.4・5（カード裏返し後）には付けない。

### 3級パーソナル No.4・5

Do you / Have you ever / Can you のあとに、参考解答・ポイントへ分岐を書く。

- Yes → Please tell me more. の例
- No → 関連の別質問の例

設問本文に分岐文を無理に入れなくてよい（まず参考解答側で十分）。

## Rules

- 公式面接の設問文・パッセージを転用しない（型・フレーズの一般形は可）
- 5級パッセージはおおよそ 15〜25 語、4級はおおよそ 20〜30 語、3級はおおよそ 25〜40 語
- **5級は内容2＋自分1。イラスト欄は作らない**
- **4級は内容2＋イラスト1＋自分1**（質問に `[passage]` / `[illustration]` / `[personal]`）
- **3級は内容1＋イラスト2＋自分2**（イラスト型バラし・passage/picture フレーズ・Yes/No分岐は上記）
- 現行公開セットは各級 **5問**。追記しても配分は変えない
- 既存問題の文言差し替えで進捗を残すときは `register_speaking_questions --in-place`
