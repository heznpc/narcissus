#!/usr/bin/env bash
# Real-time status of the Study 1 multirun. Run anytime; no side effects.
# Usage:
#   bash experiments/src/status.sh        # one-shot
#   watch -n 5 bash experiments/src/status.sh  # live

set -uo pipefail

REPO_ROOT="/Users/ren/IdeaProjects/Paper/narcissus"
OUT_DIR="${REPO_ROOT}/experiments/data/raw/study1-replication"
LOG_DIR="${REPO_ROOT}/experiments/state/multirun-logs"
MASTER_LOG="${REPO_ROOT}/experiments/state/multirun-v2-master.log"

PAPERS=( narcissus analogic-appropriation z-gap eddy ploidy )

now_utc="$(date -u +%FT%TZ)"
now_kst="$(TZ=Asia/Seoul date +%FT%T)"
echo "=== Study 1 multirun status @ ${now_utc} (${now_kst} KST) ==="

# Per-cell matrix.
echo ""
echo "Cell matrix (✓ = file present, · = pending):"
printf "  %-25s" "paper / run"
for r in 1 2 3 4 5; do printf "%6d" "$r"; done
echo ""
for p in "${PAPERS[@]}"; do
  printf "  %-25s" "$p"
  for r in 1 2 3 4 5; do
    f="${OUT_DIR}/${p}__claude-opus-4-7__bare__run-${r}.json"
    if [[ -f "$f" ]]; then
      printf "%6s" "✓"
    else
      printf "%6s" "·"
    fi
  done
  echo ""
done

# Aggregate.
done_cnt=$(ls "$OUT_DIR"/*__bare__run-[1-5].json 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "Completed: ${done_cnt}/25 cells"

# Recent activity from per-cell logs.
echo ""
echo "Most recent per-cell log writes (last 5):"
ls -lt "$LOG_DIR"/*.log 2>/dev/null | head -5 | awk '{printf "  %-12s %-10s %s\n", $6, $7" "$8, $NF}'

# Live processes.
echo ""
echo "Live processes:"
running_master=$(pgrep -af "run_study1_multirun" 2>/dev/null | wc -l | tr -d ' ')
running_cell=$(pgrep -af "run_fresh_review_cli" 2>/dev/null | wc -l | tr -d ' ')
running_claude=$(pgrep -af "claude --print" 2>/dev/null | wc -l | tr -d ' ')
echo "  multirun master:  ${running_master}"
echo "  cell runners:     ${running_cell}"
echo "  claude --print:   ${running_claude}"

# Master log tail (may lag due to Bash buffering — per-cell logs above
# are the real-time signal).
echo ""
echo "Master log tail (NB: Bash stdio buffering — per-cell logs above are live):"
tail -3 "$MASTER_LOG" 2>/dev/null | sed 's/^/  /'

# Next 5h reset boundary.
echo ""
python3 - <<'PY' | sed 's/^/  /'
import datetime as dt
ANCHOR = dt.datetime(2026, 5, 20, 18, 10, 0, tzinfo=dt.timezone.utc)
PERIOD = dt.timedelta(hours=5)
now = dt.datetime.now(dt.timezone.utc)
elapsed = (now - ANCHOR).total_seconds()
n = int(elapsed // PERIOD.total_seconds()) + 1
nxt_utc = ANCHOR + n * PERIOD
nxt_kst = nxt_utc.astimezone(dt.timezone(dt.timedelta(hours=9)))
remaining = (nxt_utc - now).total_seconds()
hh = int(remaining // 3600); mm = int((remaining % 3600) // 60); ss = int(remaining % 60)
print(f"Next 5h quota reset: {nxt_kst.strftime('%Y-%m-%d %H:%M %Z')} (in {hh}h {mm}m {ss}s)")
PY
