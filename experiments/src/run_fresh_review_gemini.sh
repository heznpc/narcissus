#!/usr/bin/env bash
# Cross-vendor Fresh x Adversarial review cell via the `gemini` CLI.
# Usage: run_fresh_review_gemini.sh <paper_id> <paper_path> <out_dir> <run_id> [model]
#
# Vendor-adapted twin of run_fresh_review_cli.sh (which targets `claude`).
# Emits the SAME canonical cell JSON schema so the existing analyzers
# (analyze_multirun.py helpers, cross-vendor comparison) work unchanged.
#
# Gemini envelope differences handled here:
#   - a "Loaded cached credentials." preamble line precedes the JSON -> strip
#   - answer text is in `.response` (not `.result`)
#   - actual model is the key under `.stats.models` (not `.modelUsage`)
#   - tokens: .stats.models.<m>.tokens.{prompt,candidates,cached,thoughts}
#   - NO usd cost field -> total_cost_usd recorded as null
#
# Only the Fresh x Adversarial condition is supported (the cross-vendor
# comparable cell). model defaults to gemini-3.1-pro-preview.

set -uo pipefail

paper_id="${1:?paper_id required}"
paper_path="${2:?paper_path required}"
out_dir="${3:?out_dir required}"
run_id="${4:?run_id required}"
model="${5:-gemini-3.1-pro-preview}"

safe_model="${model//\//_}"
out_path="${out_dir}/${paper_id}__${safe_model}__bare__run-${run_id}.json"

if [[ -f "$out_path" ]]; then
  echo "skip (exists): $out_path"; exit 0
fi
if [[ ! -f "$paper_path" ]]; then
  echo "ERROR: manuscript not found: $paper_path" >&2; exit 2
fi
mkdir -p "$out_dir"

work_dir="$(mktemp -d -t narcissus-gemini-XXXXXX)"
trap 'rm -rf "$work_dir"' EXIT

prompt_file="${work_dir}/prompt.txt"
{
  cat <<'PROMPT_HEADER'
ROLE: You have NO prior context about this manuscript, its authors, the
project, or the broader research program. Read it as if it just arrived
in your reviewer queue from a venue editor.

You are an adversarial peer reviewer of an academic manuscript.

Read for validity and rigor. Identify weaknesses, missing counter-evidence,
unstated assumptions, methodological issues, statistical concerns, and
factual problems. Be specific -- cite section labels or line ranges. You
are NOT the author. Do not soften criticism. Aim for 5-15 substantive
issues; severity in {critical, major, minor}.

Return ONLY a JSON object (NO preamble, NO Markdown code fences) with this
exact schema:
{"paper_id":"PAPER_ID_HERE","response":{"issues":[{"section":"<ref>","severity":"critical|major|minor","description":"<one-paragraph critique>","counter_evidence":"<citation/note, or null>"}],"summary":"<2-3 sentence overall assessment>"}}

MANUSCRIPT:
---
PROMPT_HEADER
  cat "$paper_path"
  echo "---"
} > "$prompt_file"
# Inject the real paper_id into the schema example.
python3 - "$prompt_file" "$paper_id" <<'PY'
import sys
p, pid = sys.argv[1], sys.argv[2]
t = open(p, encoding="utf-8").read().replace("PAPER_ID_HERE", pid)
open(p, "w", encoding="utf-8").write(t)
PY

envelope_tmp="${work_dir}/envelope.json"
err_file="${work_dir}/gemini.err"

t_start=$(date -u +%s)
gemini_rc=0
( cd "$work_dir" && gemini -p "Return ONLY the JSON object described above; no preamble, no code fences." \
    --output-format json --approval-mode plan -m "$model" \
    < "$prompt_file" > "$envelope_tmp" 2> "$err_file" ) || gemini_rc=$?
t_end=$(date -u +%s)
wall_s=$(( t_end - t_start ))

if [[ ! -s "$envelope_tmp" ]]; then
  echo "ERROR: gemini produced no envelope (rc=$gemini_rc) for $paper_id run $run_id model $model" >&2
  cat "$err_file" >&2
  exit 3
fi

set +e
python3 - "$envelope_tmp" "$out_path" "$paper_id" "$run_id" "$model" "$wall_s" <<'PY'
import json, re, sys, os, datetime as dt
envelope_path, out_path, paper_id, run_id, requested_model, wall_s = sys.argv[1:7]

raw = open(envelope_path, encoding="utf-8").read()
# Strip the "Loaded cached credentials." (and any other) preamble before JSON.
i = raw.find("{")
if i < 0:
    sys.stderr.write(f"no JSON in gemini output (will retry): {raw[:300]}\n")
    sys.exit(3)
try:
    env = json.loads(raw[i:])
except (json.JSONDecodeError, ValueError) as e:
    sys.stderr.write(f"gemini envelope not parseable (will retry): {e}\n")
    sys.exit(3)

# Error detection. Gemini surfaces errors via an 'error' field or an empty
# response. Classify transient vs permanent like the claude runner.
err_obj = env.get("error")
resp_text = env.get("response", "")
if err_obj or not resp_text:
    msg = (json.dumps(err_obj) if err_obj else "empty response").lower()
    PERMANENT = ("not found", "invalid", "unsupported", "no access",
                 "have access", "permission", "unauthorized", "unknown model")
    TRANSIENT = ("overload", "rate limit", "ratelimit", "resource exhausted",
                 "quota", "429", "529", "unavailable", "deadline", "try again",
                 "internal")
    if any(k in msg for k in PERMANENT):
        sys.stderr.write(f"gemini error (PERMANENT, bail): {msg[:300]}\n"); sys.exit(4)
    sys.stderr.write(f"gemini error (TRANSIENT/empty, retry): {msg[:300]}\n"); sys.exit(3)

# Extract the review JSON from the answer text (bracket-balanced, fence-aware).
def extract(text):
    cands = []
    for pat in (r"```json\s*(\{.*?\})\s*```", r"```\s*(\{.*?\})\s*```"):
        cands += re.findall(pat, text, re.DOTALL)
    depth = 0; start = -1; in_str = False; esc = False; last = None
    for j, ch in enumerate(text):
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
            continue
        if ch == '"': in_str = True
        elif ch == "{":
            if depth == 0: start = j
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0: last = text[start:j+1]
    if last: cands.append(last)
    return cands

body = None
for cand in reversed(extract(resp_text)):
    try:
        body = json.loads(cand); break
    except json.JSONDecodeError:
        continue
if body is None:
    sys.stderr.write(f"review JSON not parseable from response (will retry): {resp_text[:300]}\n")
    sys.exit(5)

# Tolerate both {paper_id,response:{issues}} and {issues} shapes.
review = body.get("response", body)
issues = review.get("issues")
if issues is None:
    sys.stderr.write("missing response.issues\n"); sys.exit(7)

# Actual model = key under stats.models.
models = (env.get("stats", {}) or {}).get("models", {}) or {}
actual_model = next(iter(models), "unknown")
if actual_model != "unknown" and actual_model != requested_model:
    sys.stderr.write(f"MODEL MISMATCH: requested={requested_model} actual={actual_model}; refusing.\n")
    sys.exit(8)

tok = (models.get(actual_model, {}) or {}).get("tokens", {}) if actual_model != "unknown" else {}
cell = {
    "paper_id": paper_id,
    "model_requested": requested_model,
    "model_actual": actual_model,
    "prompt_style": "adversarial",
    "context_mode": "fresh",
    "vendor": "google",
    "run_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "dry_run": False,
    "invocation": "gemini-cli",
    "run_id": int(run_id),
    "response": {"issues": issues, "summary": review.get("summary", "")},
    "metrics": {
        "wall_clock_s": int(wall_s),
        "total_cost_usd": None,   # gemini CLI does not report USD cost
        "usage": {
            "input_tokens": tok.get("prompt"),
            "output_tokens": tok.get("candidates"),
            "cache_read_input_tokens": tok.get("cached"),
            "thoughts_tokens": tok.get("thoughts"),
            "total_tokens": tok.get("total"),
        },
        "modelUsage": models,
    },
}
out_tmp = out_path + ".tmp"
with open(out_tmp, "w", encoding="utf-8") as f:
    json.dump(cell, f, indent=2, ensure_ascii=False); f.write("\n")
os.replace(out_tmp, out_path)
print(f"ok: {paper_id} run={run_id} model={actual_model} issues={len(issues)} "
      f"wall={wall_s}s in_tok={tok.get('prompt')} out_tok={tok.get('candidates')} "
      f"thoughts={tok.get('thoughts')} -> {out_path}")
PY
py_exit=$?
set -uo pipefail
if (( py_exit != 0 )); then
  echo "ERROR: gemini cell validation failed (python exit=$py_exit) for $paper_id run=$run_id" >&2
  exit "$py_exit"
fi
