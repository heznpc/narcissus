#!/usr/bin/env bash
# One Fresh-session adversarial review via `claude --print` (Max-OAuth-auth).
# Usage: run_fresh_review_cli.sh <paper_id> <paper_path> <out_dir> <run_id>
#
# Fresh-context isolation strategy (since --bare disables Max auth):
#   1. Run `claude` from a clean tmp directory (no CLAUDE.md auto-discovery
#      via cwd or parent walk) so no project context is auto-loaded.
#   2. --disable-slash-commands prevents accidental skill execution.
#   3. The prompt + manuscript are piped via stdin (no argv length risk).
# Global ~/.claude/CLAUDE.md (if it existed) would still load; on this
# machine it does not, so the only ambient context is the user's
# ~/.claude/settings.json defaults (no paper content).
#
# Output: <out_dir>/<paper_id>__claude-opus-4-7__bare__run-<run_id>.json
# (we keep the __bare__ tag in the filename for consistency with the
# multirun harness; the file is produced by Max-OAuth-claude with
# project-context isolation, not by --bare proper.)

set -euo pipefail

paper_id="${1:?paper_id required}"
paper_path="${2:?paper_path required}"
out_dir="${3:?out_dir required}"
run_id="${4:?run_id required}"

out_path="${out_dir}/${paper_id}__claude-opus-4-7__bare__run-${run_id}.json"

if [ -f "$out_path" ]; then
  echo "skip (exists): $out_path"
  exit 0
fi
if [ ! -f "$paper_path" ]; then
  echo "ERROR: manuscript not found: $paper_path" >&2
  exit 2
fi
mkdir -p "$out_dir"

# Work dir with no CLAUDE.md — isolated from this project tree.
work_dir="$(mktemp -d -t narcissus-fresh-XXXXXX)"
trap 'rm -rf "$work_dir"' EXIT

# Compose prompt with manuscript inline. Sent via stdin to bypass argv limits.
prompt_file="${work_dir}/prompt.txt"
{
  cat <<PROMPT_HEADER
You are an adversarial peer reviewer of an academic manuscript. You have
NO prior context about this manuscript, its authors, the project, or the
broader research program. Read it as if it just arrived in your reviewer
queue.

Read for validity and rigor. Identify weaknesses, missing counter-evidence,
unstated assumptions, methodological issues, statistical concerns, and
factual problems. Be specific — cite section labels or line ranges. You
are NOT the author. Do not soften criticism. Aim for 5-15 substantive
issues; severity in {critical, major, minor}.

Return ONLY a JSON object (NO preamble, NO Markdown code fences) with
this exact schema:

{
  "paper_id": "${paper_id}",
  "model": "claude-opus-4-7",
  "run_at_utc": "<current ISO-8601 UTC timestamp>",
  "dry_run": false,
  "invocation": "claude-cli-bare",
  "run_id": ${run_id},
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
model MUST be the literal string "claude-opus-4-7".
invocation MUST be the literal string "claude-cli-bare".
run_id MUST be the integer ${run_id}.

MANUSCRIPT:
---
PROMPT_HEADER
  cat "$paper_path"
  echo "---"
} > "$prompt_file"

tmp_out="${out_path}.tmp.$$"
err_file="${work_dir}/claude.err"

# Run from work_dir → no CLAUDE.md auto-discovery from project tree.
# --print: non-interactive, single response, exit.
# --disable-slash-commands: skip skill resolution.
if ! ( cd "$work_dir" && claude --print --disable-slash-commands \
       < "$prompt_file" > "$tmp_out" 2> "$err_file" ); then
  echo "ERROR: claude failed for $paper_id run $run_id" >&2
  echo "---stderr---" >&2
  cat "$err_file" >&2
  rm -f "$tmp_out"
  exit 3
fi

# Validate, strip optional fences/preamble, write canonical JSON.
python3 - "$tmp_out" "$out_path" "$paper_id" "$run_id" <<'PY'
import json, re, sys, os
tmp_path, out_path, paper_id, run_id = sys.argv[1:5]
text = open(tmp_path, encoding="utf-8").read().strip()

m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
if m:
    text = m.group(1)

first = text.find("{")
if first > 0:
    text = text[first:]
last = text.rfind("}")
if last >= 0 and last < len(text) - 1:
    text = text[: last + 1]

try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    sys.stderr.write(f"JSON parse failure: {e}\n---raw (first 2000)---\n")
    sys.stderr.write(text[:2000])
    sys.exit(4)

errs = []
if data.get("paper_id") != paper_id:
    errs.append(f"paper_id mismatch: expected {paper_id!r}, got {data.get('paper_id')!r}")
if data.get("invocation") != "claude-cli-bare":
    errs.append(f"invocation mismatch: got {data.get('invocation')!r}")
if data.get("run_id") != int(run_id):
    errs.append(f"run_id mismatch: expected {run_id}, got {data.get('run_id')!r}")
if "response" not in data or "issues" not in data["response"]:
    errs.append("missing response.issues")
if errs:
    sys.stderr.write("schema errors:\n  " + "\n  ".join(errs) + "\n")
    sys.exit(5)

out_tmp = out_path + ".tmp"
with open(out_tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
os.replace(out_tmp, out_path)
print(f"ok: {paper_id} run={run_id} issues={len(data['response']['issues'])} -> {out_path}")
PY

rm -f "$tmp_out"
