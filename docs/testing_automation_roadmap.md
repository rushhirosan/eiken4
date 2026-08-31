# テスト自動化ロードマップ

## 概要

UI/UX・問題・解説・学習ポイントの品質が上がるほど、**手動で全問・全画面を確認する負荷**が指数的に増える。  
このドキュメントは「全部目で見る」をやめ、**段階的に自動化とサンプリングに寄せる**ための計画である。

### 目的

| 目的 | 内容 |
|------|------|
| 回帰防止 | リリース前に「壊れていない」を機械で担保する |
| 手動の削減 | 人間の目は「UX の違和感」「音声・イラスト」「解説の優しさ」に集中する |
| 問題データの早期検出 | 登録・本番反映の前にテキスト・アセットの不整合を弾く |

### 対象外（当面）

- 解説・ポイントの「教育的に優しいか」の完全自動判定（AI レビュー + サンプル目視で対応）
- 全カテゴリ・全級のブラウザ E2E（最小導線のみ）
- 公式過去問 txt の照合（保管用。公開経路とは別）

---

## いまの位置（2026-09-01 時点）

| 項目 | 状態 |
|------|------|
| Django 機能テスト | **あり**（`exams/tests.py` 100件超、provenance・answer_keys 等） |
| リリース前チェック | **あり**（`scripts/release.sh` → 全テスト + シークレット検出） |
| 語順バリデータ | **あり**（`utils/validate_wordorder_questions.py`） |
| 正解分布・リスニング照合 | **あり**（`utils/check_answer_distribution.py`、`verify_listening_*`） |
| original 統合 preflight | **あり**（`scripts/preflight-original.sh`） |
| original 全件スキャン | **未**（Phase 2） |
| 登録→採点→ポイント表示テスト | **一部**（`TrySamplePageTest` のみ。拡張は Phase 3） |
| 管理コマンド dry-run | **未**（Phase 4） |
| Playwright E2E | **未**（Phase 5） |
| CI（GitHub Actions） | **未**（Phase 6） |

```text
[完了] Phase 0: preflight-phase0.sh + チェックリスト
[完了] Phase 1: preflight-original.sh（release.sh に組み込み済み）
[いま] Phase 2: original 全件バリデータ
[次]   Phase 3 …
```

---

## 手動テストが重い理由（3レイヤ）

| レイヤ | 例 | 自動化の向き |
|--------|-----|--------------|
| **A. 壊れていないか** | 採点、404、blocked 非表示、進捗更新 | Django テストでほぼカバー可能 |
| **B. データの正しさ** | 正解・解説・ポイント形式、アセットパス、正解偏り | スクリプト + 登録 dry-run |
| **C. 体験・コンテンツ** | CSS、音声、解説の優しさ、初見 UX | 最小 E2E + サンプル目視 + AI レビュー |

**方針**: A と B を機械に任せ、C は頻度と範囲を絞る。

---

## 変更種別ごとの最小セット（Phase 0）

毎回フル手動しない。**何を触ったか**で実行セットを変える。

```bash
# 変更から種別を推定 → 最小自動チェック → 手動リスト表示
./scripts/preflight-phase0.sh

# 種別を明示 / 本番デプロイ向け / 実行予定のみ
./scripts/preflight-phase0.sh --kind ui,original
./scripts/preflight-phase0.sh --deploy
./scripts/preflight-phase0.sh --list
```

印刷用チェックリスト: [docs/checklists/phase0-release-checklist.md](checklists/phase0-release-checklist.md)

| 変更内容 | 自動（必須） | 手動（これだけ） |
|----------|--------------|------------------|
| CSS / UI | `./scripts/release.sh` | 結果画面・ポイント表示・お試し 1 級 |
| 問題テキスト（original） | `./scripts/preflight-original.sh` | 該当カテゴリから **2〜3 問** ランダム |
| ビュー / 採点ロジック | 該当 `TestCase` + `release.sh` | `/try/{level}/` を 1 回 |
| リスニングアセット | `verify_listening_*` | 音声が鳴るか **1 問** |
| 解説・ポイントの文言だけ | パースチェック（Phase 2 後） | AI レビュー + 10% サンプル目視 |
| 本番デプロイ | `release.sh` + [公開前チェック](../.cursor/rules/original-questions.mdc) | 本番 URL でお試し 1 級 |

### Phase 0 の完了条件

- [x] 上表をリリース前チェックリストとして使える（`docs/checklists/phase0-release-checklist.md`）
- [x] `./scripts/preflight-phase0.sh` で変更種別に応じた自動チェック + 手動項目表示
- [x] original を触ったとき語順バリデータを preflight が実行（`--kind original` または自動推定）
- [ ] 運用習慣: デプロイ前に `./scripts/release.sh` を必ず通す

---

## Phase 1: preflight スクリプト統合

**目的**: 散在するチェックを 1 コマンドにまとめ、「実行し忘れ」をなくす。

### やること

`scripts/preflight-original.sh`（仮称）を追加し、以下を順に実行して **どれか 1 つでも FAIL なら exit 1**。

```bash
# 想定コマンド（Phase 1 完了時）
./scripts/preflight-original.sh          # original 向け全チェック
./scripts/preflight-original.sh --quick  # 語順 + manage.py test のみ（日常用）
```

| 順 | コマンド | 備考 |
|----|----------|------|
| 1 | `python manage.py check` | Django 設定 |
| 2 | `python utils/validate_wordorder_questions.py --original --level 5` | 5級語順 |
| 3 | 同上 `--level 4` / `--level 3` | 4・3級語順 |
| 4 | `python manage.py test exams.tests_provenance questions.tests_legacy_import_guard` | 公開面の安全 |
| 5 | Phase 2 完成後: `python utils/validate_original_questions.py` | original 全件 |

`scripts/release.sh` の**前**、または original 登録の**前**に `./scripts/preflight-original.sh` を挟む。

### Phase 1 の完了条件

- [x] `scripts/preflight-original.sh` がリポジトリに存在する
- [x] `--quick` とフル版の使い分けが本 doc に書いてある
- [x] `scripts/release.sh` の先頭で preflight-original を実行
- [x] 問題更新フロー仕様から本スクリプトへリンク（`docs/question_update_flow_specification.md`）

---

## Phase 2: original 問題バリデータ

**目的**: 「登録して画面を開いて初めて気づく」系を、テキスト段階で潰す。

### 新規: `utils/validate_original_questions.py`

`data/questions/original/level{5|4|3}/` を走査し、カテゴリごとに以下を検証する。

| チェック | 内容 |
|----------|------|
| ブロック区切り | `---` で分割できる、空ブロックなし |
| 必須マーカー | `【正解】` `【解説】` が存在 |
| 選択肢 | 4択（語順・スピーキング等はカテゴリ別ルール） |
| 正解 | 1 問 1 正解、ラベルと選択肢が一致 |
| 正解偏り | ファイル内で 1〜4 が極端に偏っていない（警告 or FAIL） |
| 学習ポイント | `【ポイント】` がある場合、`questions/study_points.py` でパース可能 |
| 種別 | `種別:` が `Question.STUDY_POINT_BADGE_CLASSES` のキーに含まれる |
| 静的アセット | `audio/` `images/` パスが `static/` 下に実在（リスニング・スピーキング） |
| 形式 | 級・カテゴリ固有（会話の M:/W:、読解セット数など）— 段階的に追加 |

既存の `validate_wordorder_questions.py` は語順専用として残し、本スクリプトから呼び出すか、preflight で並列実行する。

### 実行例

```bash
python utils/validate_original_questions.py
python utils/validate_original_questions.py --level 4 --category grammar_fill
python utils/validate_original_questions.py --level 3 --fail-on-warn
```

### Phase 2 の完了条件

- [ ] 5・4・3 級の original 全ファイルが ERROR 0 で通る（既存データを直してからマージ）
- [ ] Phase 1 の preflight から呼ばれる
- [ ] `eiken-question-quality-review` スキルに「必ず本スクリプトを実行」と追記済み

---

## Phase 3: Django 統合テスト拡充

**目的**: ブラウザを開かずに「回答 → 結果 → ポイント・まとめ」まで確認する。

### 既存の手本

- `eiken_project/tests.py` の `TrySamplePageTest` — お試し画面で文法・リスニング・読解を POST 採点
- `questions/tests_update_explanations.py` — 解説更新コマンドと進捗の整合

### 追加するテスト（優先順）

| 優先 | テスト内容 | 参照 |
|------|------------|------|
| 1 | 結果画面に `study_points` が含まれる（`_study_point.html`） | `exams/templates/exams/_study_point.html` |
| 2 | `answer_results.html` の「今回のまとめ」にポイントが並ぶ | `exams/views.py` `_build_study_point_summary` |
| 3 | カテゴリ別 1 本: 登録フィクスチャ → 1 問回答 → 200 + 正解表示 | 各 `register_*` と対応 |
| 4 | 5 級 exam list / 3 級 mock 等、触った画面の `TestCase` | `exams/tests.py` 既存クラスを拡張 |

### 実行

```bash
python manage.py test eiken_project.tests.TrySamplePageTest
python manage.py test exams.tests.ReadingComprehensionBehaviorTest
# Phase 3 追加後
python manage.py test exams.tests.StudyPointDisplayTests  # 仮称
```

### Phase 3 の完了条件

- [ ] study_point 表示とまとめ表のテストが最低 1 クラス存在する
- [ ] 主要カテゴリ（文法・会話・語順・L イラスト・読解）それぞれに「回答→結果」の smoke が 1 本ずつある
- [ ] CSS 変更時は該当テスト + Phase 0 の手動 2 画面で足りる運用になっている

---

## Phase 4: 管理コマンド dry-run

**目的**: DB を汚さず、登録パースエラーを先に検出する。

### 対象

`questions/management/commands/register_*.py` および `create_*.py` に `--dry-run` を追加する。

| dry-run で見ること | 内容 |
|--------------------|------|
| パース | ブロック数、必須フィールド |
| study_points | `extract_study_points` の結果 |
| 正解 | Choice / correct_answer の整合 |
| スキップ | 既存 ID との衝突（更新 vs 新規） |

```bash
python manage.py register_grammar_fill_questions --level 4 --original --dry-run
```

### Phase 4 の完了条件

- [ ] original 登録に使う全 `register_*` / `create_*` が `--dry-run` 対応
- [ ] Phase 1 preflight または登録手順で dry-run → 本登録の順が明文化されている

---

## Phase 5: Playwright E2E（最小本数）

**目的**: テンプレ・静的ファイル・JS の組み合わせだけ Django テストでは拾えない箇所を、**少数の導線**でカバーする。

### 最初の 5 本（これ以上増やさない）

| # | シナリオ | 確認 |
|---|----------|------|
| 1 | `GET /try/4/` → 回答 POST → 結果 | 採点・CTA 表示 |
| 2 | ログイン → 文法 1 問 → 結果 | ポイント CSS・解説 |
| 3 | リスニング 1 問 | `audio` / `img` の src が 200 |
| 4 | 進捗画面 | ログイン後の主要ナビ |
| 5 | viewport 375px でお試し 1 画面 | モバイル崩れの smoke |

### 配置案

```
tests/e2e/
  conftest.py
  test_try_sample.py
  test_study_points.py
  ...
```

CI では headless。ローカルは `./scripts/e2e.sh` で一括実行。

### Phase 5 の完了条件

- [ ] 上記 5 本がグリーン
- [ ] `release.sh --ship` の前に E2E を回すか、CI で main push 時に回すか決定済み
- [ ] フレーク対策（固定フィクスチャユーザー、待ち条件）が doc 化されている

---

## Phase 6: CI（GitHub Actions）

**目的**: ローカルで `./scripts/release.sh` を忘れても、push 時に落ちる。

### ワークフロー案

`.github/workflows/test.yml`:

```yaml
# 概要のみ — 実装時に具体化
on: [push, pull_request]
jobs:
  django:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: python manage.py check
      - run: python manage.py test
  original-preflight:  # Phase 1–2 完了後
    steps:
      - run: ./scripts/preflight-original.sh --quick
  e2e:  # Phase 5 完了後、任意
    steps:
      - run: ./scripts/e2e.sh
```

### Phase 6 の完了条件

- [ ] `main` への push で Django テストが自動実行される
- [ ] Phase 2 完了後、preflight が CI に載る
- [ ] 失敗時にどこを直せばよいか本 doc の Phase が分かる

---

## Phase 7: コンテンツ品質のバッチ運用

**目的**: 解説・ポイント・酷似の「人間が全部読む」をやめる。

### 既存スキル（Cursor）

| スキル | 用途 |
|--------|------|
| `eiken-originality-review` | 酷似・original 性 |
| `eiken-explanation-quality-review` | 解説の丁寧さ |
| `eiken-question-quality-review` | 級適合・ダミー・形式 |
| `eiken-study-point-review` | 【ポイント】のノート向き品質 |

### 運用フロー

1. Phase 2 バリデータで **形式 ERROR 0**
2. Agent モードで **カテゴリ単位** に上記スキルを実行（例: level4 文法 1–20）
3. FAIL だけ人間が修正
4. リリース前は **10% サンプル目視**（全問不要）

### Phase 7 の完了条件

- [ ] 新規 original 追加時の標準フローが「バリデータ → AI 4 種 → サンプル目視」になっている
- [ ] `.cursor/rules/original-questions.mdc` の公開前チェックと矛盾しない

---

## 手動テストを残すもの（割り切り）

| 項目 | 頻度の目安 |
|------|------------|
| 解説・ポイントの「優しさ」 | カテゴリ追加時 + AI レビュー後のサンプル |
| 音声の自然さ | 新規音声追加時 1 問 |
| イラストの違和感 | 新規画像追加時 1 問 |
| 初見 UX（使いやすさ） | 月 1 回、1 級だけ通し |
| 本番デプロイ後 | 本番 URL でお試し 1 級 |

---

## 既存ツール早見表

| 用途 | コマンド / ファイル |
|------|---------------------|
| リリース前フル | `./scripts/release.sh` |
| 語順検算 | `python utils/validate_wordorder_questions.py --original --level {5\|4\|3}` |
| 正解分布（5級 legacy txt） | `python utils/check_answer_distribution.py` |
| リスニング照合 | `utils/verify_listening_alignment.py`、`verify_listening_audio_content.py` |
| 公開面テスト | `python manage.py test exams.tests_provenance` |
| お試しフロー | `python manage.py test eiken_project.tests.TrySamplePageTest` |
| 公開前ルール | `.cursor/rules/original-questions.mdc` |
| 問題更新フロー | `docs/question_update_flow_specification.md` |

---

## おすすめの着手順

```text
Phase 0（今日から）→ Phase 1 → Phase 2 → Phase 3
  → Phase 4（登録が多い時期に）
  → Phase 6（Phase 1–2 とセットでも可）
  → Phase 5（UI 変更が続くなら Phase 3 より前でも可）
  → Phase 7（並行して運用開始）
```

**最小の次の一歩**: Phase 2 の `utils/validate_original_questions.py` で original 全件スキャンを追加する。

Phase 0: `./scripts/preflight-phase0.sh` / Phase 1: `./scripts/preflight-original.sh`（`release.sh` 組み込み済み）

---

## 関連ドキュメント

- [問題更新フロー仕様](question_update_flow_specification.md)
- [IP リスク排除ロードマップ](ip_risk_elimination_roadmap.md) — Phase 4 公開前チェック
- [ゲーミフィケーション ロードマップ](gamification_roadmap.md) — 機能テストの参照例
- `.cursor/skills/eiken-question-quality-review/SKILL.md` — 語順スクリプト必須の記載

**最終更新**: 2026-09-01
