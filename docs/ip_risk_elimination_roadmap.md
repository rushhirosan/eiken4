# 安全な対策サイト化ロードマップ

目的: **子供に役立つ練習サイトを残しつつ**、市販・塾教材と同じ正攻法（オリジナル問題＋商標ルール順守）に寄せ、公式著作物・商標リスクを公開経路からゼロにする。

> 運用計画であり法律意見ではありません。重要な公開判断の前に弁護士確認を推奨します。  
> 参考: [協会・知的財産ガイドライン](https://www.eiken.or.jp/trademark/)、市販過去問集／予想問題／連動アプリの一般的な作り。

進捗ボード（Canvas）: `ip-risk-elimination-roadmap`

---

## いまの位置（2026-08-18 時点）

| 項目 | 状態 |
|------|------|
| Phase 0〜2 | **完了**（公開は `original` のみ。既存は `blocked`） |
| Phase 3・5級 | **本番公開済み**（`https://eigogohan.com/exams/?level=5`） |
| Phase 3・4級 | **本番公開済み**（`https://eigogohan.com/exams/?level=4`） |
| Phase 3・3級 | **本番公開済み**（`https://eigogohan.com/exams/?level=3`。酷似・解説の仕上げも完了） |
| Phase 4 | **継続**（公開前チェックはスキル／ルールに必須化済み。協会確認は任意・後回し） |

**リスクの言い方（社内メモ）**

- 「公式転載を公開している」E型からは脱出済み（設計上）。
- 「著作権リスクがゼロ」とは言わない。酷似の最終目視・商標文言・誤登録防止は続ける。
- 公開クエリは `original` のみでも、リポジトリに公式由来 txt / PDF / `archived_media` は保管として残る。誤登録・誤配信に注意。

```text
[完了] Phase0 停止 → Phase1 ブランド → Phase2 出所 → Phase3 5・4・3級 original 本番公開
[いま] Phase4: 試験運用中。協会確認は任意・後回し
```

---

## 世の中の正攻法（このロードマップの手本）

出回っている対策物は、だいたい次のどれか。**見た目は似ていても、権利の土台が違う。**

| タイプ | 問題の中身 | 商標の扱い | 例 |
|--------|------------|------------|-----|
| A. 協会公式 | 協会の著作物 | 権利者本人 | 公式サイト過去問、公式教材 |
| B. 許諾済み過去問集 | 権利処理した過去問 | ®＋非承認文言 | 大手の「過去○回全問題集」＋連動アプリ |
| C. オリジナル対策 | **自作の予想・練習問題**（形式だけ本番寄り） | ®＋非承認文言 | ゼミ本、塾専用教材、多くの対策アプリ |
| D. 解説・学習法中心 | 例題は自作、過去問は載せない | 記述的言及＋表記 | 勉強法サイト、単語解説 |
| E. グレー／危険 | 公式PDF・音源の無断転載 | 雑なことが多い | 個人の無断掲載サイト等 |

**このサイトが目指すのは C（＋本物が欲しければ A へのリンク）。**  
B は協会・出版社との契約が前提なので、個人開発では狙わない。E はやらない。

### 大手・塾がやっていることで、こちらも取り入れること

1. **問題はオリジナル**（「過去問そのもの」をサイトに載せない）
2. **試験の「形式」に寄せた練習**（4択・会話補充・リスニング部構成など）
3. **本物の過去問は公式サイト／市販過去問集へ誘導**
4. **商標表記**: `英検®` ＋「協会の承認・推奨を受けたものではありません」
5. **サービス名・ドメインに「英検」「Eiken」を入れない**（ブランドは自社名、試験名は説明として小さく）
6. **連動アプリ型**: 自前コンテンツの練習・進捗・音声再生（公式音源の再配布ではない）

### やらないこと（E および協会が禁止している方向）

- 公式PDF・問題文・選択肢・原稿の転載
- 公式音源・イラストの切り出し再利用
- 公式問題をAIに入れて類題生成（機械学習・解析利用の禁止に抵触しうる）
- 「公式そっくり」「過去問そのまま」を売りにする表現
- 協会公式／公認と誤解されるブランド・ロゴ利用

---

## ターゲットプロダクト（完成形のイメージ）

子供向けの **オリジナル英語級練習サイト**。

| 要素 | 完成形 |
|------|--------|
| 問題 | すべて自作（provenance = original） |
| 音声 | TTS または自作のみ |
| 画像 | 自作またはライセンス済みのみ |
| ブランド | えいごごはん（EigoGohan）。TOEIC 等は将来の別枠 |
| 試験名の言及 | 説明として「英検®」「実用英語技能検定」＋®・非承認文言 |
| 本物の過去問 | [協会の級別過去問ページ](https://www.eiken.or.jp/eiken/exam/) 等へのリンクのみ |
| 価値 | 形式練習・進捗・習慣・解説（市販の「予想問題＋学習アプリ」に近い） |

### 価値の置き換え

| これまで（リスクあり） | これからの安全な形（C型） |
|------------------------|---------------------------|
| 公式に近い問題をそのまま解く | 同じ形式の**オリジナル**問題で練習する |
| サイト内に過去問がある | 公式過去問ページ／市販過去問集へリンク |
| 「Eiken Practice」ブランド | **えいごごはん**。試験名は説明用に小さく。TOEIC は別枠 |
| 「過去問形式」コピー | 「試験形式の練習問題」「オリジナル予想問題」 |

---

## フェーズ概要

| Phase | 目的 | 手本との対応 | 状態 |
|-------|------|--------------|------|
| 0 | E型の露出を止める | 危険ゾーンから脱出 | **完了** |
| 1 | 商標・ブランドを市販並みに | 大手の ®・非承認・自社名 | **完了** |
| 2 | 出所管理を仕組み化 | 「すべてオリジナル」を技術で担保 | **完了**（任意の出所メモのみ残） |
| 3 | C型コンテンツを積み上げる | ゼミ本・予想ドリルと同じ作り | **完了**（5・4・3級 original を本番公開） |
| 4 | 運用で再発防止 | 公開前チェックを習慣化 | **必須化済み**（協会確認は任意） |

---

## Phase 0 — E型の露出を止める

市販がやらないこと（公式転載の公開）を、まず止める。

- [x] 本番で公式由来問題の公開を停止（空表示／メンテ／家族だけ閉域のいずれか）
- [x] `data/pdf_import` と公式PDF由来テキストを配信パイプラインから切り離す
- [x] 公式由来の `static/audio` / `static/images` を配信対象外にする
- [x] 「過去問」「公式に近い」と誤解されるコピーを見直し
- [x] （任意）メンテ中も「公式過去問は協会サイトへ」リンクだけ残す（Aへの誘導）

**完了条件:** 外部ユーザーが公式由来の問題・音声・画像に到達できない。 → **達成**

> 実装メモ（シンプル方針）:
> - 既存は公式/AI を**分類しない**（誤ラベル自体がリスク）
> - すべて `blocked` のまま残し、公開クエリは `original` のみ
> - 公開してよいのは、公式・既存文面を見ずに新規作成し `original` を明示したものだけ
> - `data/pdf_import` は保管・形式参考用に残す。再取り込みは既定禁止（`LEGACY_QUESTION_IMPORT_ENABLED` / `ALLOW_LEGACY_PDF_IMPORT`）
> - 公式由来メディアは `data/archived_media/`（`static/` から移設）

---

## Phase 1 — ブランドを市販の表記ルールに寄せる

旺文社などと同様、**自社ブランドで提供し、試験名は説明＋免責**。

- [x] 新サービス名を決定（英検 / Eiken を含まない）  
  → **えいごごはん**（正式表記の補助: EigoGohan）。本線は子供の級練習。TOEIC 等は将来の別枠／別名。
- [x] 表示名・タイトル・OG・ナビ等を **えいごごはん / EigoGohan** に置換  
- [x] ドメイン切替（`eiken-practice.com` → **`eigogohan.com`**。Fly 接続＋旧ドメイン 301）
- [x] フッター常設（市販の定番に合わせる）
  - `英検®は、公益財団法人 日本英語検定協会の登録商標です。`
  - `このコンテンツは、公益財団法人 日本英語検定協会の承認や推奨、その他の検討を受けたものではありません。`
- [x] UI上、試験名よりサービス名を大きく（協会ガイドラインの趣旨）
- [x] 協会ロゴや赤地に白の「英検」風デザインを使わない（目視点検）
  - 公開面ナビ・LP・OG は紫系ブランド。OG を `eigogohan-og-image.png`（えいごごはん）に更新。旧 `Eiken Practice` OG を削除
  - アイコン略号 `EP` → `EG`
- [x] （任意）商標の説明的利用の範囲で迷う場合は `chitekizaisan@eiken.or.jp` に確認  
  → **スキップ**（現状迷っていない。必要になったら送る）

**完了条件:** 公開面のブランドが自社名中心。試験名は説明＋®・非承認のみ。 → **達成（Phase 1 完了）**

---

## Phase 2 — 「すべてオリジナル」を技術で担保

塾教材の「オリジナル問題のみ」宣言を、DBと公開クエリで強制する。

**採用方針（シンプル）:** 既存を公式/AI に振り分けない。全部 `blocked`。  
`original` は「これから明示的に自作したもの」だけ。誤って `original` を付けるのが最大リスクなので、出所の精密ラベリングはしない。

- [x] `Question` に `provenance`（`original` / `blocked` 等）を追加
- [x] 公開クエリは `provenance=original` のみ（`Question.objects.published()` 等）
- [x] 既存問題を一括 `blocked`（または削除）
- [x] 新規作成の既定値を `blocked`（公開は明示的な `original` のみ）
- [x] 公式PDFインポート用コマンド／utils を無効化または削除
- [x] 登録コマンドに `--original` を追加（`questions/register_source.py` + `level_paths.questions_file_abspath(..., original=True)`）
  - 読み先: `data/questions/original/level{N}/`
  - `--original` 時は当該 type/level の **original のみ**削除して差し替え（blocked は残す）
  - `--original` と `--allow-legacy-blocked-import` は同時不可
- [ ] 登録フローに「出所メモ」（誰が・いつ・どう作ったか）を残せるようにする（任意・後回し可）

**完了条件:** コード上、既存・取り込みは公開できない。`original` を付けた新規だけ出る。 → **達成**

### 登録コマンド（original）

```bash
# 例: 5級
python manage.py register_grammar_fill_questions --level 5 --original
python manage.py register_conversation_fill_questions --level 5 --original
python manage.py register_wordorder_fill_questions --level 5 --original
python manage.py register_listening_illustration_questions --level 5 --original
python manage.py create_listening_conversation_questions --level 5 --original
python manage.py register_speaking_questions --level 5 --original
# 4級では読解・文章リスニング等も同様に --level 4 --original
```

---

## Phase 3 — C型コンテンツを子供向けに積み上げる

市販の「予想問題ドリル」「集中ゼミ」と同じ発想: **形式は本番寄り、中身は完全自作。**

優先順: **5級 → 4級 → 3級**（子供にすぐ役立つ順）

### 作成ルール（市販の実務に寄せる）

- 難易度・出題形式・時間感は「級の傾向」として参考にしてよい
- **文言・場面・選択肢・イラスト・音源は新規**（丸写し・並べ替え禁止）
- 公式PDFを開いたまま AI に「同じ問題を」と依頼しない
- 作成後、公式公開過去問と並べて酷似がないか目視（スキル `eiken-originality-review` のあとに人の目）
- 音声は TTS／自作、画像は自作またはライセンス済みのみ
- 級ごとに「最小セットで一通り練習できる」ことを再公開条件にする
- 置き場: `data/questions/original/level{N}/` のみ（`data/questions/level5/` 等の級別 txt は公式由来保管・公開登録しない）

### 作業スキル入口

| 用途 | スキル |
|------|--------|
| 作問 | `eiken-original-authoring`（`references/*.md`） |
| 酷似 | `eiken-originality-review`（公式由来は txt 比較。PDF は開かない） |
| 級フィット・ダミー | `eiken-question-quality-review` |
| 解説 | `eiken-explanation-quality-review` |
| イラスト生成 | `eiken-listening-illustration-images` |
| 登録・パス | `eiken-question-operations` / `eiken-question-pipeline` |
| Cursor rule | `.cursor/rules/original-questions.mdc` |

---

### 5級 — 本番公開済み

テキスト: `data/questions/original/level5/`

| カテゴリ | ファイル | 件数（目安） | 状態 |
|----------|----------|--------------|------|
| 文法・語彙 | `grammar_fill_questions.txt` | 10 | [x] 作問・酷似・解説・登録・ローカル確認 |
| 会話補充 | `conversation_questions.txt` | 10 | [x] 同上 |
| 語順 | `wordorder_questions.txt` | 10 | [x] 同上 |
| リスニング第1部 | `listening_illustration_questions.txt` No.1–10 | 10 | [x] TTS・画像・登録 |
| リスニング第2部 | `listening_conversation_questions.txt` | 5 | [x] TTS・登録 |
| リスニング第3部 | 同 txt No.101–105 | 5 | [x] TTS・本問画像・登録 |
| スピーキング | `speaking_questions.txt` | 5 | [x] 作問・登録・ローカル確認 |

**アセット（5級 original）**

| 種類 | 配置 |
|------|------|
| 音声 Part1 | `static/audio/level5/part1/listening_illustration_question{1–10}.mp3` |
| 音声 Part2 | `static/audio/level5/part2/listening_conversation_question{1–5}.mp3` |
| 音声 Part3 | `static/audio/level5/part3/listening_illustration_question{101–105}.mp3` |
| 本問画像 | `static/images/level5/part1/listening_illustration_image{1–10,101–105}.png` |
| Part3 参考用選択肢画像（任意） | `.../listening_illustration_q{101–105}_choice{1–3}.png`（**UI には出さない**） |

**実装・運用メモ（5級で決めたこと）**

- TTS 話速: 5級は Edge TTS **`-15%`**（`utils/eiken_paths.default_tts_rate`）。他級は `+0%`。
- Part3（イラスト一致）の UI 選択肢は **`1` / `2` / `3` のみ**。放送3文から本問イラストに合うものを選ぶ。`choice_text` に画像パスや英文を入れない（spoil・誤表示防止）。
- 文法 Q1 正解は `food`（`give it some food`）。`fish` から差し替え済み。
- スピーキングは自動採点しない。達成カードは「練習おつかれさま！…」（「ぜんぶ正解」は出さない）。模擬までの % 案内は解放対象カテゴリ向けに残る。
- ローカル DB: 5級公開は original のみ（例: Question original 40 + Listening 15）。blocked は大量に残存してよい。

**5級の残り（本番前）** → **完了（本番公開済み）**

- [x] 人の目視で公式公開過去問と並べて酷似最終確認（スキル通過後の人間チェック）
- [x] 「公式の過去問はこちら」リンク（級ページ／試験一覧）
- [x] 本番（Fly）へ original テキスト・静的アセット・DB 登録の反映
- [x] 本番で `published` のみ見えること・公式メディアが出ないことの確認

---

### 4級 — 本番公開済み

5級と同じパイプライン。置き場は `data/questions/original/level4/`。

**4級で作るもの（最小セット）**

- [x] 文法・語彙（`grammar_fill_questions.txt`）
- [x] 会話補充（`conversation_questions.txt`）
- [x] 語順（`wordorder_questions.txt`）
- [x] 読解（`reading_comprehesion_questions.txt` ※ファイル名は既存コマンドの typo に合わせる）
- [x] リスニングイラスト（`listening_illustration_questions.txt`）＋自作画像＋TTS
- [x] リスニング会話（`listening_conversation_questions.txt`）＋TTS
- [x] リスニング文章（`listening_passage_questions.txt`）＋TTS（4級にある形式）
- [x] スピーキング（`speaking_questions.txt`）
- [ ] （任意）ライティングは3級優先。4級に出すなら original で
- [x] 公式過去問リンク
- [x] `--level 4 --original` で登録・ローカル確認
- [x] 本番公開（`?level=4`）

**4級の注意**

- 4級のレガシー txt は `data/questions/*.txt`（`level4/` サブディレクトリではない）。**original は必ず `original/level4/`**。
- 作問中に公式 PDF / レガシー txt を読んで類題にしない（傾向把握は級の一般知識レベルまで）。
- 酷似チェック時だけ `data/questions/*.txt`（4級保管）と比較する。
- 音声・画像: `static/audio/level4/part1|2|3/` と `static/images/level4/part1/`（他級と同様に `level{N}/` 配下。`questions/level_paths.py` / `utils/eiken_paths.py`）。
- TTS 既定は `+0%`（5級より速め）。必要なら `--rate` で調整。

**当時の進め方（記録）**

1. `eiken-original-authoring` で文法 → 会話 → 語順
2. 酷似・品質・解説スキル
3. 読解ミニセット
4. リスニング3種（テキスト → TTS → イラスト画像 → 登録）
5. スピーキング
6. `python manage.py … --level 4 --original` 一括登録 → ローカル画面確認 → 本番反映

---

### 3級 — 本番公開済み

テキスト: `data/questions/original/level3/`

- [x] 文法・語彙 10 / 会話 10 / 語順 10（語順検算 OK）
- [x] 読解 本文5×2
- [x] リスニング3種（イラスト10・会話5・文章5）テキスト
- [x] スピーキング 5 / ライティング 5
- [x] TTS・イラスト画像などのアセット（目視前）
- [x] `--level 3 --original` ローカル登録
- [x] 酷似再確認・解説/品質レビューの仕上げ
- [x] 人の目視（`VISUAL_CHECK.md`）・画面テスト
- [x] 公式過去問リンク
- [x] 本番公開（`?level=3`）

---

### 学習体験（大手連動アプリから借りる機能価値）

問題を合法にしたうえで、サイトの強みとして残す／伸ばす:

- [x] 進捗・間違えた問題の復習（既存機能）
- [x] デイリー／習慣（既存機能）
- [x] 解説（original 作問時に品質レビュー済みのものを載せる）
- [x] 級別の進め方ガイド（`/guides/`。勉強法は D型として安全）

**完了条件:** 級ごとにオリジナルのみで学習が一通りできる。本物の過去問は外部リンク。

---

## Phase 4 — 運用で再発防止

- [x] Cursor rule / 本ドキュメントを作業の入口にする  
  → `.cursor/rules/original-questions.mdc`。作問 `eiken-original-authoring`、酷似 `eiken-originality-review`、解説 `eiken-explanation-quality-review`
- [x] 公開面の案内を試験運用に変更（`MAINTENANCE_NOTICE_*`。問題ゼロ公開の文言は廃止）
- [x] 公開前チェックを PR・登録前に必須化  
  → `.cursor/rules/original-questions.mdc`。作問 `eiken-original-authoring`、デプロイ `eiken-fly-operations` / `release`。未なら登録・デプロイしない。
- [x] 公式過去問・市販過去問集はリンク誘導のみ（転載しない）
- [ ] （任意）協会知財へ「オリジナル問題の練習サイト」方針を一文で確認
- [ ] （任意）将来、許諾が取れるなら B型（過去問連動）は別プロジェクトとして検討。現サイトの既定にはしない
- [x] 5級→本番デプロイ後、4級・3級も同じ公開前チェックを通す

### 公開前チェックリスト（毎回）

1. 出所は `original` か？（`--original` 登録）
2. 音声・画像は自前または許可済みか？（`archived_media` / 公式切り出しを使っていないか）
3. サービス名・ドメイン・目立つロゴに英検/Eiken がないか？
4. 試験名を出す箇所に ® と非承認文言があるか？
5. 「過去問そのもの」「公式」と誤解される文言がないか？
6. 本物の過去問が必要なら公式／市販へのリンクになっているか？
7. 酷似チェック（スキル）＋人の目視を通したか？
8. 本番で `published()` 以外が出ていないか？

---

## 管理のやり方

1. **このファイル**のチェックボックスを正とする。
2. Canvas `ip-risk-elimination-roadmap` でフェーズ単位の進捗を見る。
3. 実装は「4級の文法だけ」など小さく指示して進める。
4. コミットはユーザー指示があるまで作らない（作業ルール）。

## 決定済み事項

1. Phase 0 の止め方: **問題ゼロ公開（既存は blocked）** ← 採用・完了。案内文言は 2026-08-18 に試験運用へ変更
2. 新サービス名: **えいごごはん**（補助: EigoGohan）。TOEIC は将来の別枠／別名 ← 決定
3. 最初に作り直す級: **5級** ← ローカル最小セット完了 → 5・4・3級とも本番公開済み
4. 新ドメイン: **`eigogohan.com`** ← 取得・Fly 接続・コード切替済み（旧 `eiken-practice.com` は 301）
5. 出所の精密分類（公式 vs AI）は**しない**
6. **次の作業: なし（本線は完了）。任意は協会知財への一文確認**

## 残リスク（忘れない用）

| リスク | 対策 |
|--------|------|
| 公式文面との偶然の酷似 | originality-review ＋人の目視 |
| レガシー誤登録 | `--original` 以外の register は既定禁止。本番でも確認 |
| リポジトリ内の公式保管物の再露出 | `static` / 公開クエリから切り離したまま。archived を戻さない |
| 「リスクゼロ」と誤解 | C型の正攻法に乗った、と説明する。法律意見は別 |
| 公開前チェックの形骸化 | 登録・デプロイ前に `original-questions.mdc` を必須（飛ばしたら止める） |
