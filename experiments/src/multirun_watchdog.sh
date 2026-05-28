#!/usr/bin/env bash
# launchd watchdog for the Study 1 multirun.
# Invoked every 60s by a LaunchAgent. Idempotent + non-overlapping.
#
# REWRITTEN (code review #1, #2, #10): the previous watchdog hardcoded
# `bash $SCRIPT 5 8` for relaunch and counted `*__bare__run-[1-5].json`
# for completion. This caused:
#   - non-default batches (neutral, collaborator, run-6..10, claude-opus-4-6)
#     to be replaced with the default 4.7-adversarial-fresh-runs-1..5 job
#     on every relaunch
#   - mixed-cohort directories to falsely satisfy the 25-cell completion
#     gate, suppressing all future relaunches
#   - pgrep -f false positives on editors/tail/grep blocking valid
#     relaunches
#
# New design: the watchdog refuses to act unless an explicit intent file
# (multirun-intent.env) exists in STATE_DIR. The intent file is written by
# the launcher at the START of each multirun (export form, source-able by
# this watchdog) and contains the exact args the launcher was invoked
# with, plus a PID. The watchdog:
#   1) sources the intent file
#   2) checks if the recorded PID is alive (kill -0); if so, no action
#   3) counts cells matching the EXACT cohort the intent describes; if
#      complete, removes the intent file and exits
#   4) otherwise relaunches the master with the SAME args
# The intent file is the single source of truth — the watchdog never
# guesses defaults.

set -uo pipefail

REPO_ROOT="/Users/ren/IdeaProjects/Paper/narcissus"
SCRIPT="${REPO_ROOT}/experiments/src/run_study1_multirun.sh"
OUT_DIR="${REPO_ROOT}/experiments/data/raw/study1-replication"
STATE_DIR="${REPO_ROOT}/experiments/state"
INTENT_FILE="${STATE_DIR}/multirun-intent.env"
LOCK="${STATE_DIR}/watchdog.lock"
WD_LOG="${STATE_DIR}/watchdog.log"

mkdir -p "$STATE_DIR"

ts() { date -u +%FT%TZ; }
wd_log() { echo "[$(ts)] $*" >> "$WD_LOG"; }

# Non-blocking lock via atomic mkdir.
# FIX (code review #15): trap installed BEFORE mkdir so a SIGKILL between
# acquisition and trap-installation cannot leak the lock.
LOCKDIR="${LOCK}.d"
trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  if [[ -d "$LOCKDIR" ]]; then
    age_s=$(( $(date +%s) - $(stat -f %m "$LOCKDIR" 2>/dev/null || echo 0) ))
    if (( age_s > 300 )); then
      wd_log "stale lock (${age_s}s); stealing"
      rmdir "$LOCKDIR" 2>/dev/null || true
      mkdir "$LOCKDIR" 2>/dev/null || { wd_log "lock contention; skipping"; exit 0; }
    else
      wd_log "another tick holds lock (${age_s}s); skipping"
      trap - EXIT
      exit 0
    fi
  fi
fi

# No intent file → no action. The launcher must write one to opt in.
if [[ ! -f "$INTENT_FILE" ]]; then
  wd_log "no intent file at ${INTENT_FILE}; no action"
  exit 0
fi

# Source the intent. Expected variables:
#   INTENT_MODEL, INTENT_STYLE, INTENT_CONTEXT, INTENT_START_RUN,
#   INTENT_N_RUNS, INTENT_MAX_RESETS, INTENT_PID, INTENT_TAG
# shellcheck disable=SC1090
source "$INTENT_FILE"

: "${INTENT_MODEL:?intent file missing INTENT_MODEL}"
: "${INTENT_STYLE:?intent file missing INTENT_STYLE}"
: "${INTENT_CONTEXT:?intent file missing INTENT_CONTEXT}"
: "${INTENT_START_RUN:=1}"
: "${INTENT_N_RUNS:=5}"
: "${INTENT_MAX_RESETS:=8}"
: "${INTENT_PID:=0}"
: "${INTENT_TAG:?intent file missing INTENT_TAG}"

END_RUN=$(( INTENT_START_RUN + INTENT_N_RUNS - 1 ))
EXPECTED=$(( INTENT_N_RUNS * 5 ))   # 5 papers

# Count cells for the EXACT cohort, EXACT run range.
PAPERS=( narcissus analogic-appropriation z-gap eddy ploidy )
done_cnt=0
for p in "${PAPERS[@]}"; do
  for r in $(seq "$INTENT_START_RUN" "$END_RUN"); do
    f="${OUT_DIR}/${p}__${INTENT_MODEL}__${INTENT_TAG}__run-${r}.json"
    [[ -f "$f" ]] && done_cnt=$(( done_cnt + 1 ))
  done
done

if (( done_cnt >= EXPECTED )); then
  wd_log "cohort complete (${done_cnt}/${EXPECTED}) — removing intent file"
  rm -f "$INTENT_FILE"
  exit 0
fi

# Check if the recorded PID is alive. kill -0 returns 0 if the process
# exists and we have permission to signal it.
if (( INTENT_PID > 0 )) && kill -0 "$INTENT_PID" 2>/dev/null; then
  wd_log "master alive (pid=$INTENT_PID, ${done_cnt}/${EXPECTED}); no action"
  exit 0
fi

wd_log "master not alive (pid=${INTENT_PID}, ${done_cnt}/${EXPECTED}) — relaunching with intent args"

# Relaunch with the EXACT args from the intent. nohup + disown so the
# child survives the watchdog exit and SIGHUP from launchd.
nohup /bin/bash "$SCRIPT" \
  "$INTENT_N_RUNS" "$INTENT_MAX_RESETS" \
  "$INTENT_MODEL" "$INTENT_STYLE" \
  "$INTENT_START_RUN" "$INTENT_CONTEXT" \
  >> "${STATE_DIR}/multirun-v2-master.log" 2>&1 < /dev/null &
new_pid=$!
disown "$new_pid" 2>/dev/null || true

# Update the intent file with the new PID so subsequent ticks recognize it.
sed -i.bak "s/^INTENT_PID=.*/INTENT_PID=${new_pid}/" "$INTENT_FILE" && rm -f "${INTENT_FILE}.bak"

wd_log "relaunch fired (new_pid=${new_pid}; args=${INTENT_N_RUNS} ${INTENT_MAX_RESETS} ${INTENT_MODEL} ${INTENT_STYLE} ${INTENT_START_RUN} ${INTENT_CONTEXT})"
