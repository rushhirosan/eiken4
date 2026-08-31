#!/usr/bin/env bash
# Phase 0: 変更種別に応じた最小自動チェック + 手動確認リストの表示
#
# 使い方:
#   ./scripts/preflight-phase0.sh                 # 作業ツリーの変更から種別を推定
#   ./scripts/preflight-phase0.sh --base main     # main との差分から推定
#   ./scripts/preflight-phase0.sh --kind ui,original
#   ./scripts/preflight-phase0.sh --full          # release.sh と同等（全テスト + 秘密情報）
#   ./scripts/preflight-phase0.sh --deploy        # 本番デプロイ向け手動項目も表示
#   ./scripts/preflight-phase0.sh --list          # 実行予定のみ表示（dry-run）
#
# 詳細: docs/testing_automation_roadmap.md（Phase 0）

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="python3"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
elif [[ -x "venv/bin/python" ]]; then
  PYTHON="venv/bin/python"
fi

BASE=""
FORCE_KINDS=""
DO_FULL=false
DO_DEPLOY=false
DO_LIST=false

KINDS=""
CHANGED_FILES=""
AUTO_STEPS=""
MANUAL_ITEMS=""

usage() {
  cat <<EOF
Usage: $0 [options]

  (no args)       変更ファイルから種別を推定し、最小の自動チェックを実行
  --base REF      差分の基準（例: main, origin/main）
  --kind LIST     種別を明示（カンマ区切り）
                  ui | original | views | listening | explanations | deploy
  --full          ./scripts/release.sh と同等（全テスト + 秘密情報スキャン）
  --deploy        本番デプロイ向けの手動チェック項目も表示
  --list          実行せず、推定種別と予定コマンドのみ表示
  -h, --help      このヘルプ

手動チェックリスト: docs/checklists/phase0-release-checklist.md
EOF
}

has_kind() {
  echo "$KINDS" | grep -qw "$1"
}

add_kind() {
  local k="$1"
  has_kind "$k" || KINDS="${KINDS:+$KINDS }$k"
}

add_step() {
  AUTO_STEPS="${AUTO_STEPS}${AUTO_STEPS:+$'\n'}$1"
}

add_manual() {
  MANUAL_ITEMS="${MANUAL_ITEMS}${MANUAL_ITEMS:+$'\n'}$1"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      BASE="${2:-}"
      [[ -n "$BASE" ]] || { echo "error: --base needs a ref"; exit 1; }
      shift 2
      ;;
    --kind)
      FORCE_KINDS="${2:-}"
      [[ -n "$FORCE_KINDS" ]] || { echo "error: --kind needs a list"; exit 1; }
      shift 2
      ;;
    --full)
      DO_FULL=true
      shift
      ;;
    --deploy)
      DO_DEPLOY=true
      shift
      ;;
    --list)
      DO_LIST=true
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

collect_changed_files() {
  local f buf=""
  if [[ -n "$BASE" ]]; then
    while IFS= read -r f; do
      [[ -n "$f" ]] && buf="${buf}${buf:+$'\n'}$f"
    done < <(git diff --name-only "$BASE" 2>/dev/null || true)
    while IFS= read -r f; do
      [[ -n "$f" ]] && buf="${buf}${buf:+$'\n'}$f"
    done < <(git diff --cached --name-only "$BASE" 2>/dev/null || true)
  else
    while IFS= read -r f; do
      [[ -n "$f" ]] && buf="${buf}${buf:+$'\n'}$f"
    done < <(git diff --name-only 2>/dev/null || true)
    while IFS= read -r f; do
      [[ -n "$f" ]] && buf="${buf}${buf:+$'\n'}$f"
    done < <(git diff --cached --name-only 2>/dev/null || true)
    while IFS= read -r f; do
      [[ -n "$f" ]] && buf="${buf}${buf:+$'\n'}$f"
    done < <(git ls-files --others --exclude-standard 2>/dev/null || true)
  fi
  CHANGED_FILES="$(printf '%s\n' "$buf" | sed '/^$/d' | sort -u)"
}

detect_kinds_from_files() {
  local f
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in
      static/css/*|templates/*|static/js/*|exams/templates/*)
        add_kind ui
        ;;
      data/questions/original/*)
        add_kind original
        ;;
      exams/views.py|exams/answer_keys.py|exams/models.py|exams/forms.py)
        add_kind views
        ;;
      static/audio/*|static/images/*)
        add_kind listening
        ;;
      exams/tests*.py|eiken_project/tests*.py|questions/tests*.py|accounts/tests.py)
        add_kind views
        ;;
    esac
  done <<< "$CHANGED_FILES"
}

apply_force_kinds() {
  local part
  if [[ -n "$FORCE_KINDS" ]]; then
    KINDS=""
    IFS=',' read -ra parts <<< "$FORCE_KINDS"
    for part in "${parts[@]}"; do
      part="${part// /}"
      case "$part" in
        ui|original|views|listening|explanations|deploy)
          add_kind "$part"
          ;;
        *)
          echo "error: unknown kind '$part' (ui|original|views|listening|explanations|deploy)"
          exit 1
          ;;
      esac
    done
  fi
}

affected_original_levels() {
  local f out=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in
      data/questions/original/level5/*) out="${out}${out:+ }5" ;;
      data/questions/original/level4/*) out="${out}${out:+ }4" ;;
      data/questions/original/level3/*) out="${out}${out:+ }3" ;;
    esac
  done <<< "$CHANGED_FILES"
  if [[ -z "$out" ]]; then
    echo "5 4 3"
  else
    echo "$out" | tr ' ' '\n' | sort -u | tr '\n' ' ' | sed 's/ $//'
  fi
}

affected_listening_levels() {
  local f out=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in
      static/audio/level5/*|static/images/level5/*) out="${out}${out:+ }5" ;;
      static/audio/level4/*|static/images/level4/*) out="${out}${out:+ }4" ;;
      static/audio/level3/*|static/images/level3/*) out="${out}${out:+ }3" ;;
    esac
  done <<< "$CHANGED_FILES"
  echo "$out" | tr ' ' '\n' | sed '/^$/d' | sort -u | tr '\n' ' ' | sed 's/ $//'
}

plan_steps() {
  local lv args

  if [[ "$DO_FULL" == true ]]; then
    add_step "./scripts/release.sh"
    add_manual "（--full 時は release.sh 内で自動チェック完了。下記はデプロイ時のみ）"
    return
  fi

  add_step "$PYTHON manage.py check"

  if has_kind original || has_kind explanations; then
    add_step "$PYTHON utils/validate_original_questions.py"
    for lv in $(affected_original_levels); do
      add_step "$PYTHON utils/validate_wordorder_questions.py --original --level $lv"
    done
  fi

  if has_kind views; then
    add_step "$PYTHON manage.py test exams.tests_provenance eiken_project.tests.TrySamplePageTest -v 1"
  fi

  if has_kind ui; then
    add_step "$PYTHON manage.py test eiken_project.tests.TrySamplePageTest -v 1"
  fi

  if has_kind listening; then
    args=""
    for lv in $(affected_listening_levels); do
      args="$args --level $lv"
    done
    if [[ -n "$args" ]]; then
      add_step "$PYTHON utils/verify_listening_alignment.py$args"
    fi
  fi

  if [[ -z "$KINDS" && -n "$CHANGED_FILES" ]]; then
    add_step "$PYTHON manage.py test -v 1"
    add_manual "変更種別を自動判定できませんでした。必要なら ./scripts/preflight-phase0.sh --full"
  fi

  if [[ -z "$CHANGED_FILES" && -z "$FORCE_KINDS" && "$DO_FULL" == false ]]; then
    add_manual "変更ファイルがありません。--kind ui などで種別を指定するか、作業後に再実行してください。"
  fi
}

plan_manual_items() {
  if has_kind ui; then
    add_manual "結果画面（answer_results）を開き、レイアウト・ポイント表示を確認"
    add_manual "study_point.css 変更時: 解説下の【ポイント】ブロックと「今回のまとめ」表"
    add_manual "お試し 1 級: http://127.0.0.1:8000/try/4/ （級は変更に合わせて）"
  fi

  if has_kind original; then
    add_manual "変更したカテゴリから 2〜3 問をランダムに選び、登録後に画面で正解・解説を確認"
    add_manual "語順を触った場合: validate_wordorder は自動実行済み。表示も 1 問目視"
  fi

  if has_kind explanations; then
    add_manual "解説・ポイント文言: AI レビュー（eiken-explanation-quality-review / eiken-study-point-review）"
    add_manual "10% 程度をサンプル目視（全問不要）"
  fi

  if has_kind views; then
    add_manual "/try/{level}/ を 1 回: 回答 POST → 採点結果"
  fi

  if has_kind listening; then
    add_manual "リスニング 1 問: 音声が再生されるか、画像が表示されるか"
  fi

  if [[ "$DO_DEPLOY" == true ]] || has_kind deploy; then
    add_manual "本番デプロイ前: ./scripts/release.sh を必ず通す"
    add_manual ".cursor/rules/original-questions.mdc の公開前チェック 8 項目"
    add_manual "デプロイ後: 本番 URL でお試し 1 級（例: https://eigogohan.com/try/4/）"
  fi

  if [[ "$DO_FULL" == false ]] && { has_kind ui || has_kind views || [[ "$DO_DEPLOY" == true ]]; }; then
    add_manual "リリース前の最終確認: ./scripts/release.sh（全テスト + 秘密情報スキャン）"
  fi
}

count_lines() {
  if [[ -z "${1:-}" ]]; then
    echo 0
  else
    printf '%s\n' "$1" | sed '/^$/d' | wc -l | tr -d ' '
  fi
}

print_header() {
  local n
  n="$(count_lines "$CHANGED_FILES")"
  echo "==> Phase 0 preflight"
  if [[ "$n" -gt 0 ]]; then
    echo "    変更ファイル: ${n} 件"
    if [[ "$n" -le 8 ]]; then
      printf '      - %s\n' $(printf '%s\n' "$CHANGED_FILES")
    else
      printf '      - %s\n' $(printf '%s\n' "$CHANGED_FILES" | head -5)
      echo "      - ... 他 $((n - 5)) 件"
    fi
  fi
  if [[ -n "$KINDS" ]]; then
    echo "    推定種別: $KINDS"
  else
    echo "    推定種別: （なし）"
  fi
  echo ""
}

run_auto_steps() {
  local step n=1 total
  total="$(count_lines "$AUTO_STEPS")"
  while IFS= read -r step; do
    [[ -z "$step" ]] && continue
    echo "==> 自動 [$n/$total] $step"
    if [[ "$DO_LIST" != true ]]; then
      # shellcheck disable=SC2086
      eval "$step"
    fi
    n=$((n + 1))
  done <<< "$AUTO_STEPS"
}

print_manual_checklist() {
  local i=1 item
  [[ -z "$MANUAL_ITEMS" ]] && return
  echo ""
  echo "==> 手動確認（人の目）"
  echo "    詳細: docs/checklists/phase0-release-checklist.md"
  echo ""
  while IFS= read -r item; do
    [[ -z "$item" ]] && continue
    echo "  [ ] $i. $item"
    i=$((i + 1))
  done <<< "$MANUAL_ITEMS"
  echo ""
  echo "自動チェックが通っても、上記を必要に応じて確認してから merge / deploy してください。"
}

collect_changed_files
detect_kinds_from_files
apply_force_kinds
[[ "$DO_DEPLOY" == true ]] && add_kind deploy
plan_steps
plan_manual_items
print_header
run_auto_steps
print_manual_checklist

if [[ "$DO_LIST" == true ]]; then
  echo "（--list のため自動チェックは実行していません）"
  exit 0
fi

echo "OK: Phase 0 自動チェック完了"
