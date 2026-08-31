#!/usr/bin/env bash
# Phase 1: original 問題・公開面向け preflight（散在チェックを 1 本化）
#
# 使い方:
#   ./scripts/preflight-original.sh          # フル（check + 語順 5/4/3 + 公開面テスト）
#   ./scripts/preflight-original.sh --quick  # 日常用（語順 5/4/3 + 公開面テストのみ）
#
# original 登録前・release.sh --ship の前に実行する。
# 詳細: docs/testing_automation_roadmap.md（Phase 1）

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="python3"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
elif [[ -x "venv/bin/python" ]]; then
  PYTHON="venv/bin/python"
fi

DO_QUICK=false

usage() {
  cat <<EOF
Usage: $0 [options]

  (no args)   manage.py check + 語順(5/4/3) + 公開面テスト
  --quick     check を省略し、語順 + 公開面テストのみ
  -h, --help  このヘルプ

Phase 2 完成後: validate_original_questions.py をここに追加予定。
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)
      DO_QUICK=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1 (use --help)"
      exit 1
      ;;
  esac
done

step=0
run_step() {
  step=$((step + 1))
  echo "==> [$step] $*"
  # shellcheck disable=SC2086
  eval "$@"
}

echo "==> preflight-original (quick=$DO_QUICK)"
echo ""

if [[ "$DO_QUICK" == false ]]; then
  run_step "$PYTHON manage.py check"
fi

for lv in 5 4 3; do
  run_step "$PYTHON utils/validate_wordorder_questions.py --original --level $lv"
done

run_step "$PYTHON manage.py test exams.tests_provenance questions.tests_legacy_import_guard -v 1"

# Phase 2: validate_original_questions.py をここに追加

echo ""
echo "OK: preflight-original 完了"
