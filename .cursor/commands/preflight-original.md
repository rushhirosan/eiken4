---
description: >-
  Run preflight-original (wordorder + public-surface tests) before registering
  original questions. Use with --quick for daily checks.
---

# preflight-original（Phase 1）

`data/questions/original/` の登録前・リリース前チェック。

```bash
./scripts/preflight-original.sh          # フル
./scripts/preflight-original.sh --quick  # check 省略
```

`./scripts/release.sh` / `--ship` も内部で同 preflight を先に実行する。

詳細: [docs/testing_automation_roadmap.md](../docs/testing_automation_roadmap.md#phase-1-preflight-スクリプト統合)
