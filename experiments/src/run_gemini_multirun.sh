#!/usr/bin/env bash
# Minimal cross-vendor batch: 5 papers x N runs of the Gemini Fresh x
# Adversarial cell. Deliberately NOT built on run_study1_multirun.sh, whose
# quota machinery is anchored to Claude's 5h reset boundary — Gemini uses
# Google quota (per-minute RPM), so on a transient failure we use a short
# fixed backoff, not a 5h sleep. Idempotent (skips existing cells). Bails
# fast on deterministic failures (exit 4/5/6/7/8 from the cell runner).
#
# Usage: bash run_gemini_multirun.sh [n_runs] [model]
set -uo pipefail
n_runs="${1:-5}"
model="${2:-gemini-3.1-pro-preview}"
safe_model="${model//\//_}"

REPO_ROOT="/Users/ren/IdeaProjects/Paper/narcissus"
OUT_DIR="${REPO_ROOT}/experiments/data/raw/study1-replication"
LOG_DIR="${REPO_ROOT}/experiments/state/multirun-logs"
CELL="${REPO_ROOT}/experiments/src/run_fresh_review_gemini.sh"
mkdir -p "$OUT_DIR" "$LOG_DIR"

PAPER_PATHS=(
  "narcissus:${REPO_ROOT}/paper/main.tex"
  "analogic-appropriation:/Users/ren/IdeaProjects/Paper/analogic-appropriation/paper/main.tex"
  "z-gap:/Users/ren/IdeaProjects/Paper/z-gap/paper/main.tex"
  "eddy:/Users/ren/IdeaProjects/Paper/eddy/paper/main.tex"
  "ploidy:/Users/ren/IdeaProjects/Paper/ploidy/paper/main.tex"
)
expected=$(( n_runs * ${#PAPER_PATHS[@]} ))
BACKOFF=60          # seconds between zero-progress passes (RPM throttle)
MAX_BACKOFFS=20     # cap -> ~20 min of pure-transient retry before giving up

ts(){ echo "[$(date -u +%FT%TZ)] $*" >&2; }
count_done(){
  local c=0
  for e in "${PAPER_PATHS[@]}"; do local p="${e%%:*}"
    for r in $(seq 1 "$n_runs"); do
      [[ -f "${OUT_DIR}/${p}__${safe_model}__bare__run-${r}.json" ]] && c=$((c+1)); done; done
  echo "$c"
}

ts "gemini multirun: model=$model n_runs=$n_runs expected=$expected initial=$(count_done)"
backoffs=0
while true; do
  before=$(count_done)
  (( before >= expected )) && { ts "all $expected done"; break; }
  det=0; trans=0
  for r in $(seq 1 "$n_runs"); do
    pids=()
    for e in "${PAPER_PATHS[@]}"; do
      p="${e%%:*}"; pp="${e#*:}"
      out="${OUT_DIR}/${p}__${safe_model}__bare__run-${r}.json"
      [[ -f "$out" ]] && continue
      log="${LOG_DIR}/${p}__${safe_model}__bare__run-${r}.log"
      ts "  launch $p run=$r"
      bash "$CELL" "$p" "$pp" "$OUT_DIR" "$r" "$model" > "$log" 2>&1 &
      pids+=( "$!:$p:$r" )
    done
    for entry in "${pids[@]}"; do
      pid="${entry%%:*}"; rc=0; wait "$pid" || rc=$?
      # exit 5/6/7 are model-OUTPUT parse/shape failures — stochastic for an
      # LLM, so a re-run usually fixes them (verified: ploidy run-4 failed
      # exit 5 once, parsed cleanly on retry). Treat them as TRANSIENT
      # (retry, capped by MAX_BACKOFFS), not deterministic-bail. Only exit 4
      # (permanent: model not found / no access) and 8 (model mismatch) bail.
      case "$rc" in 0) :;; 3|5|6|7) trans=$((trans+1));; 4|8) det=$((det+1));; *) det=$((det+1));; esac
    done
  done
  after=$(count_done)
  ts "pass: ${before}->${after}/${expected}  transient=$trans deterministic=$det"
  (( after >= expected )) && { ts "all $expected done"; break; }
  if (( after == before )); then
    if (( det > 0 )); then
      ts "ERROR: zero progress with $det deterministic failures — bailing (fix config, re-run)"; exit 3
    fi
    backoffs=$((backoffs+1))
    (( backoffs > MAX_BACKOFFS )) && { ts "ERROR: $MAX_BACKOFFS transient backoffs, still stuck — bailing"; exit 2; }
    ts "transient-only zero progress; sleeping ${BACKOFF}s (backoff ${backoffs}/${MAX_BACKOFFS})"
    sleep "$BACKOFF"
  else
    backoffs=0
  fi
done
ts "gemini multirun complete: $(count_done)/$expected"
