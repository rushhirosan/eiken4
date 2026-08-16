---
name: eiken-listening-illustration-images
description: Generates listening illustration images for Eiken by level, matching existing style and layout from reference images in the same level, then saves to the correct static/images paths. Use when new listening_illustration questions need images, e.g. "4級のリスニングイラスト問題を追加したので画像を作って".
disable-model-invocation: true
---

# Eiken Listening Illustration Images

## Goal

追加・更新したリスニングイラスト問題に対し、読み上げテキスト（会話文）に合ったイラストを生成し、級別の正しいフォルダへ配置する。

## Inputs to confirm

- 級（`5` / `4` / `3`）
- 対象問題番号（例: `41`、または `38-40`）
- 新規追加分のみか、既存画像の差し替えか
- 5級 Part3（No.101+）の場合は選択肢イラスト（3枚/問）も作るか（任意・参考用。UI には出さない）
- オリジナル問題か（テキストは `data/questions/original/level{N}/`）

## File mapping

公開用オリジナルのテキストは `data/questions/original/level{N}/listening_illustration_questions.txt`。画像の保存先は級の `static/images/`（配信パス）のまま。

| 級 | レガシーテキスト（非公開） | 画像ディレクトリ（実体） | DB 相対パス |
|----|---------|------------------------|------------|
| 4 | `data/questions/listening_illustration_questions.txt` | `static/images/level4/part1/` | `images/level4/part1/` |
| 3 | `data/questions/level3/listening_illustration_questions.txt` | `static/images/level3/part1/` | `images/level3/part1/` |
| 5 | `data/questions/level5/listening_illustration_questions.txt` | `static/images/level5/part1/` | `images/level5/part1/` |

規約の一次情報: `questions/level_paths.py`（`db_image_path_part1`, `static_images_part1_dir`）。

## Image naming

- **本問イラスト（全級・全問）**: `listening_illustration_image{N}.png`
- **5級 Part3 参考用選択肢（No.101+・任意）**: `listening_illustration_q{N}_choice{1-3}.png`
  - UI の選択肢は番号 1/2/3 のみ。`ListeningChoice.choice_text` に画像パスは入れない。

5級の音声 part 対応: Part1 → `audio/.../part1/`、Part3（No.101+）→ `audio/.../part3/`（画像はいずれも `images/.../part1/` 配下）。`questions/level_paths.py` の `LISTENING_ILLUSTRATION_PART3_MIN` に合わせる。

## Workflow

1. 対象の `listening_illustration_questions.txt` から問題ブロック（`No.{N}:` 〜 `---`）を読む。
2. 会話文・状況・選択肢英文を把握する（Part3 は3つの英文が選択肢イラストの内容）。
3. テイストは白黒の教育向け線画で揃える。**参照に `data/archived_media/` や公式由来画像は使わない**（オリジナル問題のとき）。自作済みの original 用画像があればそれを参照する。
4. 画像を生成する（下記 Style rules）。
5. 正しいファイル名で `static/images/.../part1/` に保存する。
6. 配置後チェックリストを実行する。
7. 必要なら `python manage.py register_listening_illustration_questions --level {N}` で DB 再登録。

## Style rules（級別）

### 4級・3級（会話応答型）

- **白黒のマンガ風線画**（英検公式過去問に近い教育イラスト）。
- 太めの黒線、シンプルな背景、登場人物2名程度の会話シーンが多い。
- 会話の状況が一目で分かる構図（公園、店、教室、家の前など）。
- テキスト・吹き出しは入れない（音声で聞かせるため）。
- 目安サイズ: 横長、おおよそ **320×240** 前後（UI は max 220×160 で `object-fit: contain`）。

### 5級 Part1（No.1–30）

- 4級より簡素な線画・少ない背景要素。
- 日常動作・身近な場面（食事、学校、買い物、天気など）。
- 本問1枚 + 選択肢はテキスト（画像不要）。

### 5級 Part3（No.101+）

- **選択肢3枚**が主。各英文の動作・位置関係を正確に描く。
  - 例: `opening the window` / `washing the window` / `making a window` を視覚的に区別。
- 本問 `listening_illustration_image{N}.png` も登録上必要（シーン全体または中立な状況図）。
- 選択肢画像はやや小さめ（目安 **200×160** 前後）。

## Image generation procedure

1. 参照は自作済みの original 用画像だけ。無ければ参照なしで白黒教育線画のプロンプトのみ。
2. `GenerateImage` を使うときは、参照がある場合だけ `reference_image_paths` を渡し、プロンプトで次を明示:
   - 白黒線画、教育向け、シンプル（公式画像の模写ではない）
   - 会話/英文の状況の具体的描写
   - 文字・吹き出しなし、余白あり
3. 生成結果を所定ファイル名で保存（既存ファイル上書き前にユーザー確認）。
4. PNG 形式。プレースホルダー（単色+ラベル）を本番画像で置き換える。

## Parsing question text

`listening_illustration_questions.txt` の典型構造:

```
No.{N}:
M: ...
W: ...
M: ...

Question No.{N}:
1. ...
2. ...
3. ...

【正解{N}】
...

【解説{N}】
...

---
```

- 本問イラスト: `M:` / `W:` の会話から**最後の質問と状況**を視覚化する。
- Part3: `Question No.` 直下の `1.` `2.` `3.` 英文をそれぞれ選択肢画像に反映。

## Validation checklist

- [ ] ファイル名が `listening_illustration_image{N}.png` と一致
- [ ] 保存先が級の `static/images/.../part1/` である
- [ ] 5級 No.101+ なら `choice1-3` の3枚も揃っている
- [ ] 会話・英文の内容と矛盾しない（正解肢が他肢と混同しない）
- [ ] 同級既存画像とテイストが大きく乖離していない
- [ ] 必要なら登録コマンド実行後、試験画面で表示確認

## Recommended commands

```bash
# DB 再登録（画像パスを ListeningQuestion に反映）
python manage.py register_listening_illustration_questions --level 4
python manage.py register_listening_illustration_questions --level 3
python manage.py register_listening_illustration_questions --level 5

```

## Safety

- **4級の `static/images/level4/part1/` を 3級/5級用に上書きしない**（級別パスを厳守）。
- 公式由来・アーカイブ画像をオリジナル問題の参照や配信に使わない。
- プレースホルダー（`setup_level5_assets.py` 生成物）と本番イラストを混同しない。
- オリジナル用の再登録は `original` 登録コマンドができるまでユーザー確認。レガシー `register_*` は `blocked` になる。

## Example requests

- 「4級のリスニングイラスト問題を追加した。追加した問題に応じた画像を作って」
- 「5級オリジナルのリスニング第3部 No.101 の選択肢イラスト3枚を作って」
- 「3級 No.12 のイラストを会話内容に合わせて差し替えて」
