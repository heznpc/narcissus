#!/usr/bin/env bash
# Real-time status of the Study 1 multirun. No side effects.
# Usage:
#   bash experiments/src/status.sh           # shows all models on disk
#   watch -n 5 bash experiments/src/status.sh

set -uo pipefail

REPO_ROOT="/Users/ren/IdeaProjects/Paper/narcissus"
OUT_DIR="${REPO_ROOT}/experiments/data/raw/study1-replication"
LOG_DIR="${REPO_ROOT}/experiments/state/multirun-logs"
MASTER_LOG="${REPO_ROOT}/experiments/state/multirun-v2-master.log"

PAPERS=( narcissus analogic-appropriation z-gap eddy ploidy )

# Detect which models have cells on disk (macOS bash 3.2: no mapfile).
MODELS=()
while IFS= read -r line; do
  [[ -n "$line" ]] && MODELS+=( "$line" )
done < <(
  find "$OUT_DIR" -name "*__bare__run-*.json" 2>/dev/null \
    | sed -E 's|.*/||; s|^[^_]*__||; s|__bare__.*||' \
    | sort -u
)
if [[ ${#MODELS[@]} -eq 0 ]]; then
  MODELS=( claude-opus-4-7 )
fi

now_utc="$(date -u +%FT%TZ)"
now_kst="$(TZ=Asia/Seoul date +%FT%T)"
echo "=== Study 1 multirun status @ ${now_utc} (${now_kst} KST) ==="

for model in "${MODELS[@]}"; do
  echo ""
  echo "--- model=${model} ---"
  printf "  %-25s" "paper / run"
  for r in 1 2 3 4 5; do printf "%6d" "$r"; done
  echo ""
  for p in "${PAPERS[@]}"; do
    printf "  %-25s" "$p"
    for r in 1 2 3 4 5; do
      f="${OUT_DIR}/${p}__${model}__bare__run-${r}.json"
      [[ -f "$f" ]] && printf "%6s" "✓" || printf "%6s" "·"
    done
    echo ""
  done
  done_cnt=$(ls "$OUT_DIR"/*__"${model}"__bare__run-[1-5].json 2>/dev/null | wc -l | tr -d ' ')

  # Tally cost + tokens for this model from cell JSONs.
  python3 - "$OUT_DIR" "$model" <<'PY'
import json, glob, sys
out_dir, model = sys.argv[1:3]
total_cost = 0.0
total_in = total_out = total_cache_read = total_cache_create = 0
n = 0
for f in glob.glob(f"{out_dir}/*__{model}__bare__run-[1-5].json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
        m = d.get("metrics", {})
        u = m.get("usage", {})
        total_cost += m.get("total_cost_usd") or 0
        total_in += u.get("input_tokens") or 0
        total_out += u.get("output_tokens") or 0
        total_cache_read += u.get("cache_read_input_tokens") or 0
        total_cache_create += u.get("cache_creation_input_tokens") or 0
        n += 1
    except Exception:
        pass
print(f"  Completed: {n}/25 cells")
if n > 0:
    print(f"  Tokens (sum):  in={total_in:>6}  out={total_out:>6}  "
          f"cache_read={total_cache_read:>7}  cache_create={total_cache_create:>7}")
    print(f"  Cost so far:   ${total_cost:.4f}  (avg ${total_cost/n:.4f}/cell)")
PY
done

# Recent activity
echo ""
echo "Most recent per-cell log writes (last 5 across all models):"
ls -lt "$LOG_DIR"/*.log 2>/dev/null | head -5 | awk '{printf "  %-12s %-10s %s\n", $6, $7" "$8, $NF}'

# Live processes
echo ""
echo "Live processes:"
echo "  multirun masters: $(pgrep -af 'run_study1_multirun' 2>/dev/null | wc -l | tr -d ' ')"
echo "  cell runners:     $(pgrep -af 'run_fresh_review_cli' 2>/dev/null | wc -l | tr -d ' ')"
echo "  claude --print:   $(pgrep -af 'claude --print' 2>/dev/null | wc -l | tr -d ' ')"

# Master log tail
echo ""
echo "Master log tail (NB: Bash stdio buffering — per-cell logs above are live):"
tail -3 "$MASTER_LOG" 2>/dev/null | sed 's/^/  /'

# Next 5h reset
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
