# 英検準2級 二次（バーチャル二次）サンプル

> 配信パイプライン外・形式参考用。詳細は [`../README.md`](../README.md)。
> **公式台本・イラストの転用、公開登録はしない。**

一次の過去3回と違い、二次の過去問冊子は [準2級の過去問ページ](https://www.eiken.or.jp/eiken/exam/grade_p2/) に無い。公開されているのはバーチャル二次のサンプル1種。

## 出所

- 問題カード PDF: https://www.eiken.or.jp/eiken/exam/virtual/grade_p2/pdf/grade_p2.pdf
- アニメーション: https://www.eiken.or.jp/eiken/exam/virtual/grade_p2/eiken_pre2.swf
- 案内: https://www.eiken.or.jp/eiken/exam/virtual/grade_p2/
- 試験内容（形式の正本）: https://www.eiken.or.jp/eiken/exam/grade_p2/solutions.html
- 取得日: 2026-10-05

## ファイル

| ファイル | 内容 |
|----------|------|
| `grade_p2.pdf` | サンプル問題カード（2ページ。パッセージ、Picture A/B、質問） |
| `eiken_pre2.swf` | 入室から退室までの Flash アニメーション（約116KB） |
| `images/page1_img{0-3}.jpeg` | PDF 内イラスト（ローカル参照用。`static/` には置かない） |

## 面接の型（公式の試験内容ページ）

英語での面接、約6分。面接委員1人。問題カードはパッセージとイラスト2枚。

1. パッセージ黙読20秒 → 音読（50語程度、1）
2. No.1 パッセージについての質問（1）
3. No.2 イラストの人物の行動を描写（1）
4. No.3 イラストの人物の状況を説明（1）。このあとカードを裏返す
5. No.4 カードのトピックに関連した自分の意見（1）
6. No.5 日常生活の身近な事柄（カードに直接関係しない内容も含む）（1）

## やらないこと

- パッセージ・設問・イラストを `data/questions/original/` にコピーしない
- サイト静的配信に載せない
