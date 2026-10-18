# writing（ライティング）

ファイル: `writing_questions.txt`  
コマンド: `register_writing_questions`  
**3級と準2級。** 5級・4級では作らない。準2級は下の3級テンプレ（下線の質問に答える、15〜25語）を使わない。正本は [pre2.md](pre2.md)。

2024年度以降、一次試験のライティングは **2題**（Eメール＋意見論述）。公開セットでは両形式をそろえる。

## 形式一覧

| 形式 | 語数目安 | 配点目安 | 内容 |
|------|---------|---------|------|
| Eメール返信 | 15〜25語 | 9点 | 友人メールの下線部2問に答える |
| 意見論述 | 25〜35語 | 16点 | 質問に対し意見と理由を2つ述べる |

## Template（Eメール）

```
問題1:
友人 Alex から次のメールをもらいました。読んで英文で返信メールを書きなさい。Alex の 2 つの質問（下線部）に答えること。

●あなたが書く返信メールのうち、Alex に対応する英文の語数の目安は 15～25 語です。
●解答は以下のテキストボックスに書きなさい。
●解答が Alex のメールに対応していないと判断された場合は 0 点と採点されることがあります。Alex のメールの内容をよく読んでから答えてください。
●空行の下の Best wishes, の後にあなたの名前を書く必要はありません。

Hi,
Thank you for your e-mail.
I hear you have a small garden at home.
I have some questions for you. <u>What do you grow in your garden?</u> <u>And when do you water the plants?</u>
Your friend,
Alex

Hi, Alex!
Thank you for your e-mail.



Best wishes,

【参考解答】
■ この問題で求められること
Alex からのメールの下線部2問（何を育てているか／いつ水をやるか）に英文で答えます。

■ 書き方のポイント
・2つの質問に必ず答える
・本文は語数の目安 15～25 語
・What には名詞、When には時間帯や頻度

■ 参考解答の例
I grow tomatoes in my garden. I water them every morning. I like my garden.

■ 表現のメモ
every morning / on weekends / after school など、時期や頻度を具体的に書く。

---
```

## Template（意見論述）

```
問題2:
次の質問に対して、あなたの意見とその理由を2つ英文で書きなさい。

●語数の目安は 25～35 語です。
●解答は以下のテキストボックスに書きなさい。

Do you think students should do homework on weekends?
Why or why not?

【参考解答】
■ この問題で求められること
質問に対して、自分の意見（Yes/No など）と理由を2つ、25〜35語でまとめます。

■ 書き方のポイント
・最初に意見をはっきり書く（I think ... / I don't think ...）
・理由を2つ（First, ... Second, ... や because ... Also, ...）
・語数は 25〜35 語を目安にする

■ 参考解答の例
I think students should do homework on weekends. First, they can review what they learned. Second, they will not forget important words.

■ 表現のメモ
I think ... / First, ... / Second, ... / because ... / Also, ...

---
```

## Rules

- 公式のメール題材（作物・部活などの特定組み合わせ）をなぞらない
- 3級: Eメールは下線の質問2つに答える（15〜25語）。意見論述は意見＋理由2つ（25〜35語）
- 準2級: 友人メールは約65〜70語。下線は1か所の短い名詞句。最後の Do you think に理由を1つつけて答え、その下線の特徴を聞く質問を2つする（本文40〜50語）。文を2本下線にしない。意見は50〜60語。問題文に「2つの質問」と「語数の目安」を残す。返信欄の目印は空行で区切る。詳細は [pre2.md](pre2.md)
- 参考解答は explanation として登録される
- 指示文の箇条書き構造は既存パーサに合わせる
- 3級の現行公開セットは **5問以上** を目安。**Eメールと意見論述を混ぜる**（例: メール3＋意見2、または交互）
- `register_writing_questions` は級の既存ライティングを削除する。3級では実行しない
