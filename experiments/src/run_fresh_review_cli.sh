#!/usr/bin/env bash
# One Fresh-session adversarial review via `claude --print` (Max-OAuth-auth).
# Usage: run_fresh_review_cli.sh <paper_id> <paper_path> <out_dir> <run_id> [model]
#
# `model` defaults to claude-opus-4-7. The model is passed explicitly via
# `--model`; otherwise Claude Code defaults to claude-opus-4-6 (1M context)
# — a silent default that previously caused the entire May 2026 multirun
# to be mislabeled.
#
# Fresh-context isolation:
#   1. Run `claude` from a mktemp'd tmp directory (no CLAUDE.md auto-discovery
#      via cwd or parent walk).
#   2. --disable-slash-commands prevents accidental skill execution.
#   3. The prompt + manuscript are piped via stdin (no argv length risk).
#
# Envelope capture:
#   --output-format json wraps the model response in a JSON envelope that
#   includes duration_ms, duration_api_ms, total_cost_usd, and detailed
#   usage stats (input_tokens, output_tokens, cache_creation_input_tokens,
#   cache_read_input_tokens, modelUsage per actual model). All of these
#   are recorded inside the output cell JSON under "envelope" so model
#   identity is provable and per-cell cost/time is measured, not estimated.
#
# Output: <out_dir>/<paper_id>__<model>__bare__run-<run_id>.json

set -uo pipefail

paper_id="${1:?paper_id required}"
paper_path="${2:?paper_path required}"
out_dir="${3:?out_dir required}"
run_id="${4:?run_id required}"
model="${5:-claude-opus-4-7}"
prompt_style="${6:-adversarial}"   # adversarial | neutral

# Filename uses the exact requested model + prompt style. Adversarial files
# keep the legacy '__bare__' tag (no style suffix) for back-compat with the
# already-collected corpus. Non-adversarial styles get an explicit suffix.
safe_model="${model//\//_}"
if [[ "$prompt_style" == "adversarial" ]]; then
  out_path="${out_dir}/${paper_id}__${safe_model}__bare__run-${run_id}.json"
else
  out_path="${out_dir}/${paper_id}__${safe_model}__bare__${prompt_style}__run-${run_id}.json"
fi

if [ -f "$out_path" ]; then
  echo "skip (exists): $out_path"
  exit 0
fi
if [ ! -f "$paper_path" ]; then
  echo "ERROR: manuscript not found: $paper_path" >&2
  exit 2
fi
mkdir -p "$out_dir"

work_dir="$(mktemp -d -t narcissus-fresh-XXXXXX)"
trap 'rm -rf "$work_dir"' EXIT

prompt_file="${work_dir}/prompt.txt"

if [[ "$prompt_style" == "neutral" ]]; then
  read -r -d '' STANCE_HEADER <<'NEUTRAL'
You are a peer reviewer of an academic manuscript. You have NO prior
context about this manuscript, its authors, the project, or the broader
research program. Read it as if it just arrived in your reviewer queue.

Read on its merits. Note both the manuscript's strengths and its
weaknesses; identify issues that would warrant author response (factual,
methodological, statistical, evidentiary, clarity). Be specific — cite
section labels or line ranges. You are NOT the author. Do not soften
criticism, but also do not adversarially seek faults that are not there.
Report only issues you would actually flag in a real peer review. There
is no minimum issue count; if the paper is solid in a section, do not
manufacture concerns. Severity in {critical, major, minor}.
NEUTRAL
else
  read -r -d '' STANCE_HEADER <<'ADVERSARIAL'
You are an adversarial peer reviewer of an academic manuscript. You have
NO prior context about this manuscript, its authors, the project, or the
broader research program. Read it as if it just arrived in your reviewer
queue.

Read for validity and rigor. Identify weaknesses, missing counter-evidence,
unstated assumptions, methodological issues, statistical concerns, and
factual problems. Be specific — cite section labels or line ranges. You
are NOT the author. Do not soften criticism. Aim for 5-15 substantive
issues; severity in {critical, major, minor}.
ADVERSARIAL
fi

{
  printf '%s\n\n' "$STANCE_HEADER"
  cat <<PROMPT_HEADER
Return ONLY a JSON object (NO preamble, NO Markdown code fences) with
this exact schema:

{
  "paper_id": "${paper_id}",
  "run_at_utc": "<current ISO-8601 UTC timestamp>",
  "response": {
    "issues": [
      {"section": "<ref>", "severity": "critical|major|minor",
       "description": "<one-paragraph critique>",
       "counter_evidence": "<citation/note, or null>"}
    ],
    "summary": "<2-3 sentence overall assessment>"
  }
}

paper_id MUST be the literal string "${paper_id}".
The schema fields for model / invocation / run_id are injected by the
wrapping script — DO NOT include them.

MANUSCRIPT:
---
$(cat "$paper_path")
---
PROMPT_HEADER
} > "$prompt_file"

envelope_tmp="${out_path}.envelope.tmp.$$"
err_file="${work_dir}/claude.err"

t_start=$(date -u +%s)
if ! ( cd "$work_dir" && claude --print --disable-slash-commands \
       --model "$model" --output-format json \
       < "$prompt_file" > "$envelope_tmp" 2> "$err_file" ); then
  echo "ERROR: claude failed for $paper_id run $run_id model $model" >&2
  echo "---stderr---" >&2
  cat "$err_file" >&2
  rm -f "$envelope_tmp"
  exit 3
fi
t_end=$(date -u +%s)
wall_s=$(( t_end - t_start ))

# Parse envelope, extract response, validate schema, write canonical cell JSON.
python3 - "$envelope_tmp" "$out_path" "$paper_id" "$run_id" "$model" "$wall_s" "$prompt_style" <<'PY'
import json, re, sys, os, datetime as dt
envelope_path, out_path, paper_id, run_id, requested_model, wall_s, prompt_style = sys.argv[1:8]

envelope = json.loads(open(envelope_path, encoding="utf-8").read())

if envelope.get("is_error"):
    sys.stderr.write(f"envelope is_error=True: {envelope}\n")
    sys.exit(4)

result_text = envelope.get("result", "").strip()

# Strip optional code-fence wrap.
m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", result_text, re.DOTALL)
if m:
    result_text = m.group(1)

first = result_text.find("{")
if first > 0:
    result_text = result_text[first:]
last = result_text.rfind("}")
if last >= 0 and last < len(result_text) - 1:
    result_text = result_text[: last + 1]

try:
    body = json.loads(result_text)
except json.JSONDecodeError as e:
    sys.stderr.write(f"JSON parse failure on model response: {e}\n")
    sys.stderr.write("---raw (first 2000)---\n")
    sys.stderr.write(result_text[:2000])
    sys.exit(5)

if body.get("paper_id") != paper_id:
    sys.stderr.write(f"paper_id mismatch: expected {paper_id!r}, got {body.get('paper_id')!r}\n")
    sys.exit(6)
if "response" not in body or "issues" not in body["response"]:
    sys.stderr.write("missing response.issues\n")
    sys.exit(7)

# Identify the ACTUAL model served (vs. requested).
actual_model_keys = list(envelope.get("modelUsage", {}).keys())
if actual_model_keys:
    actual_model = actual_model_keys[0].split("[")[0]
else:
    actual_model = "unknown"

# Compose canonical cell JSON. Envelope is preserved in full for audit.
cell = {
    "paper_id": paper_id,
    "model_requested": requested_model,
    "model_actual": actual_model,
    "prompt_style": prompt_style,
    "run_at_utc": body.get("run_at_utc") or dt.datetime.now(dt.timezone.utc).isoformat(),
    "dry_run": False,
    "invocation": "claude-cli-bare",
    "run_id": int(run_id),
    "response": body["response"],
    "metrics": {
        "wall_clock_s": int(wall_s),
        "duration_ms": envelope.get("duration_ms"),
        "duration_api_ms": envelope.get("duration_api_ms"),
        "num_turns": envelope.get("num_turns"),
        "stop_reason": envelope.get("stop_reason"),
        "total_cost_usd": envelope.get("total_cost_usd"),
        "usage": envelope.get("usage", {}),
        "modelUsage": envelope.get("modelUsage", {}),
    },
}

out_tmp = out_path + ".tmp"
with open(out_tmp, "w", encoding="utf-8") as f:
    json.dump(cell, f, indent=2, ensure_ascii=False)
    f.write("\n")
os.replace(out_tmp, out_path)

n_issues = len(cell["response"]["issues"])
in_tok = envelope.get("usage", {}).get("input_tokens", "?")
out_tok = envelope.get("usage", {}).get("output_tokens", "?")
cache_read = envelope.get("usage", {}).get("cache_read_input_tokens", "?")
cost = envelope.get("total_cost_usd", "?")
print(f"ok: {paper_id} run={run_id} model={actual_model} issues={n_issues} "
      f"wall={wall_s}s api_ms={envelope.get('duration_api_ms','?')} "
      f"in_tok={in_tok} out_tok={out_tok} cache_read={cache_read} "
      f"cost=${cost} -> {out_path}")
PY

rm -f "$envelope_tmp"
