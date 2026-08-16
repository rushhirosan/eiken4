# conversation_fill（会話補充）

ファイル: `conversation_questions.txt`  
コマンド: `register_conversation_fill_questions`  
空所に入る発話を4択で選ぶ。

## Template

```
問題1:
Girl : What time is the bus? Boy : ( )

選択肢1:
1. At eight.
2. It’s a book.
3. I’m hungry.
4. By bike.

【正解1】
1. At eight.

【解説1】
「バスは何時？」と時刻を聞いているので、「At eight.（8時です）」が自然です。
「It's a book.」はもの、「I'm hungry.」は気持ち、「By bike.」は行き方で、時刻の答えになりません。

---
```

## Rules

- 話者ラベルは `A :` / `B :` または `Girl :` / `Boy :` など。既存パーサは文面全体を取る
- 空所は発話の一部または発話全体の `( )`
- 誤答は「別の疑問詞に対する答え」など、よくある聞き違いにする（意味不明な英語は避ける）
- 選択肢は必ず4つ。重複テキスト禁止
