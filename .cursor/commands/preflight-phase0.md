---
description: >-
  Phase 0 preflight: run minimal automated checks from changed files and print
  a manual checklist. Use before merge/deploy, or when the user says Phase 0 /
  preflight / 変更種別チェック / 手動テスト削減.
---

# Phase 0 preflight（eiken4）

[docs/testing_automation_roadmap.md](../docs/testing_automation_roadmap.md) Phase 0。  
変更種別に応じた**最小自動チェック** + **手動確認リスト**を出す。

## 基本

```bash
./scripts/preflight-phase0.sh
```

- 作業ツリーの変更から `ui` / `original` / `views` / `listening` 等を推定
- 該当する自動チェックだけ実行
- 終わりに手動確認項目を表示

## よく使うオプション

```bash
./scripts/preflight-phase0.sh --base main      # main との差分
./scripts/preflight-phase0.sh --kind ui,original
./scripts/preflight-phase0.sh --deploy         # 本番向け手動項目も
./scripts/preflight-phase0.sh --list           # 実行せず予定のみ
./scripts/release.sh                           # リリース直前（全テスト）
```

## 手動チェックリスト（印刷用）

[docs/checklists/phase0-release-checklist.md](../docs/checklists/phase0-release-checklist.md)

## エージェント向けメモ

- UI/CSS 変更 → `--kind ui` または自動推定 + 手動 3 項目
- original 問題 → 語順バリデータ + 2〜3 問サンプル目視
- デプロイ → `--deploy` + 必ず `./scripts/release.sh` を別途通す
- Phase 1 以降は `preflight-original.sh` に統合予定
