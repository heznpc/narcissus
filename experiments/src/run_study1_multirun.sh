#!/usr/bin/env bash
# Study 1 multi-run reliability launcher — quota-resilient v3 (model-aware).
#
# Loops 5 papers × N runs at the requested MODEL. After each batch checks
# whether new output files actually landed; if not (= quota wall), sleeps
# until the next 5h reset boundary (anchored at 2026-05-21 03:10 KST) and
# retries. All cell runs are idempotent (skip on file existence), so
# re-attempts only spend quota on cells that haven't completed.
#
# Usage:
#   bash experiments/src/run_study1_multirun.sh [n_runs] [max_resets] [model]
# Defaults: n_runs=5, max_resets=8, model=claude-opus-4-7
#
# Output files live in experiments/data/raw/study1-replication/ with the
# model name embedded in the filename — so 4.6 and 4.7 multirun batches
# coexist in the same dir without overwriting each other.

set -uo pipefail

n_runs="${1:-5}"
max_resets="${2:-8}"
model="${3:-claude-opus-4-7}"
prompt_style="${4:-adversarial}"   # adversarial | neutral
safe_model="${model//\//_}"
style_suffix=""
[[ "$prompt_style" != "adversarial" ]] && style_suffix="__${prompt_style}"

PAPER_PATHS=(
  "narcissus:/Users/ren/IdeaProjects/Paper/narcissus/paper/main.tex"
  "analogic-appropriation:/Users/ren/IdeaProjects/Paper/analogic-appropriation/paper/main.tex"
  "z-gap:/Users/ren/IdeaProjects/Paper/z-gap/paper/main.tex"
  "eddy:/Users/ren/IdeaProjects/Paper/eddy/paper/main.tex"
  "ploidy:/Users/ren/IdeaProjects/Paper/ploidy/paper/main.tex"
)

REPO_ROOT="/Users/ren/IdeaProjects/Paper/narcissus"
OUT_DIR="${REPO_ROOT}/experiments/data/raw/study1-replication"
LOG_DIR="${REPO_ROOT}/experiments/state/multirun-logs"
CELL_RUNNER="${REPO_ROOT}/experiments/src/run_fresh_review_cli.sh"
RESET_WINDOW_PY="${REPO_ROOT}/experiments/src/reset_window.py"

mkdir -p "$OUT_DIR" "$LOG_DIR"

n_papers="${#PAPER_PATHS[@]}"
expected=$(( n_runs * n_papers ))

log_ts() { echo "[$(date -u +%FT%TZ)] $*"; }

count_done() {
  local cnt=0
  for entry in "${PAPER_PATHS[@]}"; do
    local pid="${entry%%:*}"
    for r in $(seq 1 "$n_runs"); do
      [[ -f "${OUT_DIR}/${pid}__${safe_model}__bare${style_suffix}__run-${r}.json" ]] && cnt=$(( cnt + 1 ))
    done
  done
  echo "$cnt"
}

# Run all incomplete cells once. Returns the number of NEW cells produced.
run_one_pass() {
  local before=$(count_done)
  for r in $(seq 1 "$n_runs"); do
    local pids=()
    local needed=0
    for entry in "${PAPER_PATHS[@]}"; do
      local pid="${entry%%:*}"
      local ppath="${entry#*:}"
      local out="${OUT_DIR}/${pid}__${safe_model}__bare${style_suffix}__run-${r}.json"
      [[ -f "$out" ]] && continue
      needed=$(( needed + 1 ))
      local log="${LOG_DIR}/${pid}__${safe_model}__bare${style_suffix}__run-${r}.log"
      log_ts "  launch ${pid} run=${r} model=${model} style=${prompt_style}"
      bash "$CELL_RUNNER" "$pid" "$ppath" "$OUT_DIR" "$r" "$model" "$prompt_style" > "$log" 2>&1 &
      pids+=( $! )
    done
    if (( ${#pids[@]} == 0 )); then
      continue
    fi
    for p in "${pids[@]}"; do
      wait "$p" || true
    done
    log_ts "  batch run=$r: needed=$needed completed_files=$(count_done)"
  done
  local after=$(count_done)
  echo "$(( after - before ))"
}

# Sleep until the next 5h reset boundary (UTC, anchored 2026-05-20 18:10 UTC
# = 2026-05-21 03:10 KST). +30s jitter to avoid the exact-boundary collision.
sleep_until_next_reset() {
  local secs
  secs=$(python3 -c "
import sys
sys.path.insert(0, '${REPO_ROOT}/experiments/src')
from reset_window import seconds_until_next_reset
print(int(seconds_until_next_reset(jitter_seconds=30)))
")
  if [[ -z "$secs" || "$secs" -lt 30 ]]; then
    secs=300  # safety floor
  fi
  log_ts "quota wall — sleeping ${secs}s ($(date -u -r $(( $(date +%s) + secs )) +%FT%TZ)) until next 5h reset"
  sleep "$secs"
  log_ts "wake — retrying"
}

log_ts "multirun v3 starting: model=$model n_runs=$n_runs n_papers=$n_papers expected=$expected max_resets=$max_resets"
log_ts "out_dir=$OUT_DIR"
log_ts "initial completed (for model=$model): $(count_done)/$expected"

reset_count=0
while true; do
  done_before=$(count_done)
  if (( done_before >= expected )); then
    log_ts "all $expected cells complete — exiting"
    break
  fi

  log_ts "pass starting: ${done_before}/${expected} done"
  produced=$(run_one_pass)
  done_after=$(count_done)
  log_ts "pass done: produced=${produced} new cells, total=${done_after}/${expected}"

  if (( done_after >= expected )); then
    log_ts "all $expected cells complete — exiting"
    break
  fi

  if (( produced == 0 )); then
    reset_count=$(( reset_count + 1 ))
    if (( reset_count > max_resets )); then
      log_ts "ERROR: zero progress for ${max_resets} consecutive reset cycles; bailing"
      log_ts "final state: ${done_after}/${expected}"
      exit 2
    fi
    log_ts "no progress this pass (reset cycle ${reset_count}/${max_resets})"
    sleep_until_next_reset
  else
    # Made progress but not done — keep going immediately without sleeping.
    reset_count=0
  fi
done

log_ts "multirun v3 complete (model=$model): final $(count_done)/$expected cells on disk"
