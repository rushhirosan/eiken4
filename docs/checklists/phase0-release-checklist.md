# Phase 0 リリース前チェックリスト

[テスト自動化ロードマップ](../testing_automation_roadmap.md) Phase 0 用。  
**何を触ったか**に応じて、下の該当行だけ確認すればよい（毎回フル手動しない）。

## 自動チェック（先に実行）

```bash
# 変更から種別を推定して最小セットを実行
./scripts/preflight-phase0.sh

# main との差分で判定（PR 前など）
./scripts/preflight-phase0.sh --base main

# 本番デプロイ前（手動項目も表示）
./scripts/preflight-phase0.sh --deploy

# リリース直前（全テスト + 秘密情報）
./scripts/release.sh
```

---

## 変更種別ごとの手動確認

### CSS / UI（`static/css/`、`templates/`）

- [ ] 結果画面（`answer_results`）のレイアウト
- [ ] 【ポイント】ブロックと「今回のまとめ」表（`study_point.css` 変更時）
- [ ] お試し 1 級（例: `/try/4/`）

### 問題テキスト original（`data/questions/original/`）

- [ ] 変更カテゴリから **2〜3 問** をランダムに画面確認（正解・解説）
- [ ] 語順を触った場合: `validate_wordorder` は preflight が実行（表示も 1 問）

### ビュー / 採点ロジック（`exams/views.py` 等）

- [ ] `/try/{level}/` を 1 回（回答 → 採点）

### リスニングアセット（`static/audio/`、`static/images/`）

- [ ] 音声が鳴るか **1 問**
- [ ] 画像が表示されるか **1 問**

### 解説・ポイントの文言だけ

- [ ] AI レビュー（`eiken-explanation-quality-review` / `eiken-study-point-review`）
- [ ] **10%** サンプル目視（全問不要）

### 本番デプロイ

- [ ] `./scripts/release.sh` 通過
- [ ] [公開前チェック](../../.cursor/rules/original-questions.mdc) 8 項目
- [ ] 本番 URL でお試し 1 級（例: `https://eigogohan.com/try/4/`）

---

## 種別を明示して実行

```bash
./scripts/preflight-phase0.sh --kind ui
./scripts/preflight-phase0.sh --kind original,explanations
./scripts/preflight-phase0.sh --kind listening --deploy
./scripts/preflight-phase0.sh --list    # 実行予定のみ表示
```

| `--kind` | 自動で走る主なチェック |
|----------|------------------------|
| `ui` | `manage.py check` + `TrySamplePageTest` |
| `original` | `check` + 語順バリデータ（触った級） |
| `views` | `check` + provenance + TrySamplePageTest |
| `listening` | `check` + `verify_listening_alignment` |
| `explanations` | `original` と同様（語順バリデータ含む） |
| `deploy` | 手動項目にデプロイチェックを追加 |

---

## Phase 0 完了の目安

- [ ] リリース前に `./scripts/preflight-phase0.sh` または `./scripts/release.sh` を実行している
- [ ] original を触ったとき語順バリデータが通っている
- [ ] 上表の「手動」は該当種別だけ実施している（全問・全画面ではない）

次の段階: [Phase 1](../testing_automation_roadmap.md#phase-1-preflight-スクリプト統合)（`preflight-original.sh` 統合）
