#!/usr/bin/env bash
# launchd watchdog for the Study 1 multirun.
# Invoked every 60s by a LaunchAgent. Idempotent + non-overlapping.
#
# - If 25/25 cells done: exit 0, no action.
# - If a multirun master is already running: exit 0, no action.
# - Otherwise: relaunch run_study1_multirun.sh detached. Lock-protected
#   so two concurrent watchdog ticks can't race.

set -uo pipefail

REPO_ROOT="/Users/ren/IdeaProjects/Paper/narcissus"
SCRIPT="${REPO_ROOT}/experiments/src/run_study1_multirun.sh"
OUT_DIR="${REPO_ROOT}/experiments/data/raw/study1-replication"
STATE_DIR="${REPO_ROOT}/experiments/state"
LOCK="${STATE_DIR}/watchdog.lock"
MASTER_LOG="${STATE_DIR}/multirun-v2-master.log"
WD_LOG="${STATE_DIR}/watchdog.log"

mkdir -p "$STATE_DIR"

ts() { date -u +%FT%TZ; }
wd_log() { echo "[$(ts)] $*" >> "$WD_LOG"; }

# Non-blocking lock via atomic mkdir (portable on macOS where `flock` is absent).
LOCKDIR="${LOCK}.d"
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  # Stale lock check: if the dir is older than 5 min, assume crashed and steal it.
  if [[ -d "$LOCKDIR" ]]; then
    age_s=$(( $(date +%s) - $(stat -f %m "$LOCKDIR" 2>/dev/null || echo 0) ))
    if (( age_s > 300 )); then
      wd_log "stale lock dir (${age_s}s old); stealing"
      rmdir "$LOCKDIR" 2>/dev/null
      mkdir "$LOCKDIR" 2>/dev/null || { wd_log "lock contention; skipping"; exit 0; }
    else
      wd_log "another watchdog tick holds lock (${age_s}s old); skipping"
      exit 0
    fi
  fi
fi
trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT

# Already done?
done_cnt=$(ls "$OUT_DIR"/*__bare__run-[1-5].json 2>/dev/null | wc -l | tr -d ' ')
if (( done_cnt >= 25 )); then
  wd_log "all 25 cells complete; no action"
  exit 0
fi

# Already running?
if pgrep -f "run_study1_multirun.sh" > /dev/null 2>&1; then
  wd_log "multirun running (${done_cnt}/25); no action"
  exit 0
fi

wd_log "multirun NOT running and only ${done_cnt}/25 done — relaunching"

# Detached relaunch. nohup + disown so watchdog process can exit while
# multirun keeps running. setsid -f gives it its own session so the
# launchd parent doesn't kill it on watchdog exit.
setsid -f /bin/bash "$SCRIPT" 5 8 >> "$MASTER_LOG" 2>&1 < /dev/null \
  || nohup /bin/bash "$SCRIPT" 5 8 >> "$MASTER_LOG" 2>&1 < /dev/null &

new_pid=$(pgrep -f "run_study1_multirun.sh" | head -1)
wd_log "relaunch fired (pid=${new_pid:-unknown})"
