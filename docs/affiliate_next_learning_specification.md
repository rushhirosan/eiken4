# アフィリエイト「このあとの学習」仕様

無料のブラウザ英検練習というコンセプトを維持しつつ、**学習の次の一手**として教材・過去問への外部リンク（アフィリエイト候補）を出す仕組みの仕様。  
後からコピー・しきい値・商材・表示場所をブラッシュアップする前提で記録する。

**方針（採用理由）**

- フリーミアム課金はコンセプト（小学生・モバイルなしでも無料で試せる）とずれやすい → 採用しない
- 表示広告より、級・弱点に沿った教材紹介の方が学習導線として自然
- 押し売りバナーやダイアログは使わない。任意・小さく・学習の言葉で提示する

---

## 公開ゲート

| 設定 | 場所 | 意味 |
|------|------|------|
| `SHOW_NEXT_LEARNING` | `eiken_project/settings.py` | ローカルは `DEBUG` 連動（開発時 ON） |
| 同上 | `eiken_project/settings_production.py` | **本番は `True`（公開）** |
| `AMAZON_ASSOCIATE_TAG` | 環境変数 / settings | あれば Amazon URL に `tag=` を付与。未設定でも検索へは遷移する |

OFF のとき:

- guides の級末尾ブロック・フッター表記・リソースへのリンクが出ない
- `/resources/` は **404**
- プライバシーのアフィリエイト節が出ない
- 回答結果の tip が出ない
- sitemap に `/resources/` が入らない

本番では `SHOW_NEXT_LEARNING = True`。紹介料を付けるには:

```bash
fly secrets set AMAZON_ASSOCIATE_TAG=your-tracking-id-22 -a eiken-app
```

Amazon URL は検索ベース。`affiliate_url()` が `tag=` を付与する。商品固定 ASIN URL への差し替えは今後の作業。

---

## フェーズ概要

| Phase | 内容 | 状態 |
|-------|------|------|
| A | guides 級別末尾＋フッター表記＋プライバシー表記 | 実装済み（ゲート付き） |
| B | 専用 `/resources/` ページ | 実装済み（ゲート付き） |
| C | 回答結果最下部の条件付き tip（週1） | 実装済み（ゲート付き） |
| 以降 | タグ付き URL・ランダム弱点出し分け・計測強化など | 未着手 |

---

## Phase A — guides 埋め込み

### UI

- 見出し: 「このあとの学習」
- 主CTA: サイト内（未ログイン「練習を始める」/ ログイン済「練習を続ける」）
- 副リンク: 外部教材（`target="_blank"` `rel="noopener noreferrer sponsored"`）
- 注記: アフィリエイトを含む旨
- フッター: 「当ページの一部リンクにはアフィリエイトを含みます。」

### 級別コピー（guides 用・1リンク）

| 級 | 趣旨 | リンク先（現状） |
|----|------|------------------|
| 5 | 基礎演習のあと紙で時間配分・マーク感 | Amazon 検索「英検5級 過去問」（タグなし） |
| 4 | 長文・リスニング後に通しペース確認 | 同上 4級 |
| 3 | 選択とライティング分離練習後に全体通し | 同上 3級 |

データ: `NEXT_LEARNING_BY_LEVEL`（`eiken_project/next_learning.py`）

### 共通部品

`templates/partials/_next_learning.html`

---

## Phase B — 学習リソースページ

| 項目 | 内容 |
|------|------|
| URL | `/resources/`（slashless → `/resources/` 301） |
| 目的 | 透明・集約・SEO。演習画面を汚さず教材ヒントを一覧化 |
| 誘導元 | guides 目次・下部ボタン・フッター（ゲート ON 時） |

### 級別コンテンツ（`resources_page_sections()`）

| 級 | 主 | 任意 |
|----|----|------|
| 5 | 過去問・問題集 | 単語帳 |
| 4 | 過去問・問題集 | 長文対策、単語帳 |
| 3 | 過去問・問題集 | 長文対策、単語帳、ライティング対策 |

ページ下部にアフィリエイト表記と「公式サイトではない」旨。  
リンクはすべて Amazon 検索の **プレースホルダ（タグなし）**。商品固定 URL への差し替えは今後の作業。

---

## Phase C — 回答結果の条件付き tip

結果画面（`exams/templates/exams/answer_results.html`）の最下部。ダイアログではない。

- tip あり: `_next_learning`（外部リンク＋注記のみ。主CTAは含めない）
- 「問題一覧に戻る」は tip の有無に関係なく、その下に独立ボタンとして常に表示

### 共通ルール

| ルール | 内容 |
|--------|------|
| ゲート | `SHOW_NEXT_LEARNING` |
| 頻度 | **ユーザー（セッション）あたり週1回**（カテゴリ横断） |
| キー | `request.session['next_learning_tip_week_id']` = `YYYY-Www` |
| 会話・語順 | **出さない** |
| ランダム | **出さない**（Phase 2 候補） |

表示したタイミングで週キャップを消費する（クリック不要）。

### カテゴリ別出し分け（`select_answer_result_tip`）

| カテゴリ | `question_type` | 出す条件 | 出すもの |
|----------|-----------------|----------|----------|
| 模擬試験 | `mock_exam` | 完了（`total_count` ≥ 1） | 級の過去問 |
| 長文 | `reading_comprehension` | 正答率 ≤ 60% | 級の長文対策 |
| 文法 | `grammar_fill` | 正答率 50〜70%（両端含む） | 級の単語帳 |
| リスニング | `listening_illustration` / `_part3` / `listening_conversation` / `listening_passage` | 正答率 ≤ 60% | 級の過去問 |
| ライティング | `writing` | 提出完了（3級のみ） | ライティング本 |
| 会話・語順・ランダム | `conversation_fill` / `word_order` / `random` | — | 出さない |

正答率 = `correct_count / total_count * 100`。`total_count == 0` は出さない。

配線: `exams/views.py` の `_finalize_and_render_answer_results`

---

## 実装ファイル一覧

| パス | 役割 |
|------|------|
| `eiken_project/next_learning.py` | コピー・URL・resources 構成・結果 tip 選定・週キャップ |
| `templates/partials/_next_learning.html` | 共通 UI 部品 |
| `templates/guides.html` | Phase A 埋め込み・リソースへの導線 |
| `templates/resources.html` | Phase B ページ |
| `templates/privacy_policy.html` | アフィリエイト節（ゲート ON 時） |
| `exams/templates/exams/answer_results.html` | Phase C 表示 |
| `eiken_project/views.py` | `guides` / `resources` / `privacy_policy` |
| `eiken_project/urls.py` | `/resources/` |
| `exams/views.py` | 結果 tip 付与・sitemap 条件付き |
| `eiken_project/settings.py` | `SHOW_NEXT_LEARNING = DEBUG` |
| `eiken_project/settings_production.py` | `SHOW_NEXT_LEARNING = False` |
| `eiken_project/tests.py` | guides / resources / privacy / sitemap |
| `eiken_project/tests_next_learning_tips.py` | tip 選定・週キャップ単体テスト |

---

## ローカル確認

```bash
./.venv/bin/python manage.py runserver 127.0.0.1:8000
```

- http://127.0.0.1:8000/guides/
- http://127.0.0.1:8000/resources/
- http://127.0.0.1:8000/privacy-policy/
- ログイン後、条件に合う演習 → 回答結果の最下部

URL は `/privacy-policy/`（テンプレート名 `privacy_policy.html` ではない）。

---

## 今後のブラッシュアップ候補

- [x] 本番で `SHOW_NEXT_LEARNING = True`
- [ ] `AMAZON_ASSOCIATE_TAG` を Fly secrets に設定（紹介料の有効化）
- [ ] Amazon 商品固定 URL（ASIN）への差し替え
- [ ] 週キャップをセッション → ユーザー永続（DB）へ
- [ ] ランダム10問: 弱点カテゴリ偏り時のみ tip（Phase 2）
- [ ] 結果 tip のしきい値・コピーの A/B や調整
- [ ] outbound click の GA 計測（級・カテゴリ別）
- [ ] 英会話など単価の高い商材（コンセプト・対象端末を踏まえて慎重に）
- [ ] guides 級末尾と結果 tip の文言統一・短縮

---

## 関連ドキュメント・コンセプトメモ

- サイトの約束: 無料・ウェブ完結・級別練習が主。アフィリは **出口の任意提案**
- 課金（Plus）は現時点では採用しない方針
- 問題データ更新フローは `docs/question_update_flow_specification.md`（本仕様とは独立）
