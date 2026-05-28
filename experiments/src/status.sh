#!/usr/bin/env bash
# Real-time status of the Study 1 multirun. No side effects.
# Usage:
#   bash experiments/src/status.sh           # shows all (model, stance, context) cohorts on disk
#   watch -n 5 bash experiments/src/status.sh
#
# FIX (code review #16): the previous grid only matched
# `*__${model}__bare__run-N.json` (adversarial-fresh only), so neutral /
# collaborator / 2x2 factorial cells were invisible. We now auto-detect
# every (model, stance, context) cohort on disk by filename and render a
# 5×5 grid per cohort. Cost tally pulls from cells matching that cohort
# exactly.

set -uo pipefail

REPO_ROOT="/Users/ren/IdeaProjects/Paper/narcissus"
OUT_DIR="${REPO_ROOT}/experiments/data/raw/study1-replication"
LOG_DIR="${REPO_ROOT}/experiments/state/multirun-logs"
MASTER_LOG="${REPO_ROOT}/experiments/state/multirun-v2-master.log"

PAPERS=( narcissus analogic-appropriation z-gap eddy ploidy )

# Auto-detect cohorts. A cohort is the triple (model, stance, context) that
# uniquely identifies the experimental cell. Filename grammar:
#   <paper>__<model>__bare__run-N.json                 (adv  × fresh)
#   <paper>__<model>__bare__<style>__run-N.json        (style × fresh)
#   <paper>__<model>__bare__<context>__run-N.json      (adv  × context)
#   <paper>__<model>__bare__<style>__<context>__run-N.json
COHORTS=()
_detect_cohorts() {
  python3 - "$OUT_DIR" <<'PY'
import os, re, sys
out_dir = sys.argv[1]
if not os.path.isdir(out_dir):
    sys.exit(0)
PAT = re.compile(
    r"^(?P<paper>[^_]+(?:-[^_]+)*)__"
    r"(?P<model>claude-[a-z0-9-]+)__"
    r"bare"
    r"(?:__(?P<tag1>[a-zA-Z]+))?"
    r"(?:__(?P<tag2>[a-zA-Z]+))?"
    r"__run-(?P<run>\d+)\.json$"
)
STYLES = {"adversarial", "neutral"}
CONTEXTS = {"fresh", "collaborator"}
seen = set()
for fname in os.listdir(out_dir):
    m = PAT.match(fname)
    if not m:
        continue
    tag1 = m.group("tag1") or ""
    tag2 = m.group("tag2") or ""
    style = "adversarial"
    context = "fresh"
    for t in (tag1, tag2):
        if t in STYLES:
            style = t
        elif t in CONTEXTS:
            context = t
    seen.add((m.group("model"), style, context))
for model, style, context in sorted(seen):
    print(f"{model}|{style}|{context}")
PY
}

COHORTS=()
while IFS= read -r line; do
  [[ -n "$line" ]] && COHORTS+=( "$line" )
done < <(_detect_cohorts)

if [[ ${#COHORTS[@]} -eq 0 ]]; then
  echo "(no cohorts detected on disk; checking default claude-opus-4-7/adversarial/fresh)"
  COHORTS=( "claude-opus-4-7|adversarial|fresh" )
fi

cohort_filename_tag() {
  local style="$1"
  local context="$2"
  local tag="bare"
  [[ "$style" != "adversarial" ]] && tag="${tag}__${style}"
  [[ "$context" != "fresh" ]] && tag="${tag}__${context}"
  echo "$tag"
}

now_utc="$(date -u +%FT%TZ)"
now_kst="$(TZ=Asia/Seoul date +%FT%T)"
echo "=== Study 1 multirun status @ ${now_utc} (${now_kst} KST) ==="

for cohort in "${COHORTS[@]}"; do
  IFS='|' read -r model style context <<< "$cohort"
  tag="$(cohort_filename_tag "$style" "$context")"
  label="model=${model} style=${style} ctx=${context}"
  echo ""
  echo "--- ${label} ---"
  printf "  %-25s" "paper / run"
  # Display all 10 runs (post code-review #2 extension).
  for r in 1 2 3 4 5 6 7 8 9 10; do printf "%4d" "$r"; done
  echo ""
  for p in "${PAPERS[@]}"; do
    printf "  %-25s" "$p"
    for r in 1 2 3 4 5 6 7 8 9 10; do
      f="${OUT_DIR}/${p}__${model}__${tag}__run-${r}.json"
      [[ -f "$f" ]] && printf "%4s" "✓" || printf "%4s" "·"
    done
    echo ""
  done

  # Cost tally for this exact cohort.
  python3 - "$OUT_DIR" "$model" "$tag" <<'PY'
import json, glob, sys
out_dir, model, tag = sys.argv[1:4]
total_cost = 0.0
total_in = total_out = total_cache_read = total_cache_create = 0
n = 0
for f in glob.glob(f"{out_dir}/*__{model}__{tag}__run-*.json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
        m = d.get("metrics", {})
        u = m.get("usage", {}) or {}
        total_cost += m.get("total_cost_usd") or 0
        total_in += u.get("input_tokens") or 0
        total_out += u.get("output_tokens") or 0
        total_cache_read += u.get("cache_read_input_tokens") or 0
        total_cache_create += u.get("cache_creation_input_tokens") or 0
        n += 1
    except Exception:
        pass
print(f"  Completed: {n} cells")
if n > 0 and total_cost > 0:
    print(f"  Tokens (sum):  in={total_in:>6}  out={total_out:>6}  "
          f"cache_read={total_cache_read:>7}  cache_create={total_cache_create:>7}")
    print(f"  Cost so far:   ${total_cost:.4f}  (avg ${total_cost/n:.4f}/cell)")
elif n > 0:
    print(f"  Cost / tokens: pre-envelope cells, no metrics recorded")
PY
done

# Recent activity
echo ""
echo "Most recent per-cell log writes (last 5 across all cohorts):"
ls -lt "$LOG_DIR"/*.log 2>/dev/null | head -5 | awk '{printf "  %-12s %-10s %s\n", $6, $7" "$8, $NF}'

# Live processes — use the unambiguous full script path so pgrep is less
# false-positive-prone (FIX, code review #10).
echo ""
echo "Live processes:"
echo "  multirun masters: $(pgrep -af "${REPO_ROOT}/experiments/src/run_study1_multirun.sh" 2>/dev/null | wc -l | tr -d ' ')"
echo "  cell runners:     $(pgrep -af "${REPO_ROOT}/experiments/src/run_fresh_review_cli.sh" 2>/dev/null | wc -l | tr -d ' ')"
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
