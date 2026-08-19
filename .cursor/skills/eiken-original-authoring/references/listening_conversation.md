# listening_conversation（リスニング会話）

ファイル: `listening_conversation_questions.txt`  
コマンド: `create_listening_conversation_questions`  
短い2人会話のあと、内容に関する4択。

## Template

```
No.1:
☆I'm going to the park.  I want to play soccer.
★Can I come, too?  I have a ball.
☆☆

Question No.1:
Where are they going?

1. To school.
2. To the park.
3. To the store.
4. To a zoo.

【正解1】
2. To the park.

【解説1】
放送文
☆I'm going to the park.  I want to play soccer.（公園に行くの。サッカーがしたいな。）
★Can I come, too?  I have a ball.（ぼくも行っていい？ボールを持っているよ。）
Question: Where are they going?（2人はどこへ行きますか？）

女の子が「公園に行く」と言っているので、2「To the park.（公園へ）」が正解です。
1・3・4は会話に出てきません。

---
```

## Rules

- 5級: 会話の終わりに `☆☆` を置く。話者は `☆` / `★`。現行公開セットは **15問**
- 4級・3級: 話者は `M:` / `W:`。`☆☆` は使わない。4ターン前後、本文は4級約28語・3級約30語。現行公開セットは各 **10問**
- `Question No.N:` の次の行が質問文、続けて `1.`〜`4.`
- 5級: 場所・持ち物・好き嫌いなど一問一答で取れる情報
- 3級は理由・条件・現在完了を混ぜ、4級と同じ骨格にしない
- 誤答のうち1つは「もう一方の話者が言ったこと」にすると学習になる（本文に無い語の羅列だけにしない）
- 5級は第2部。4級・3級も会話問題として同じファイル名
- 5級 TTS は既定 **-15%**
