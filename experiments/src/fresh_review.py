"""One Fresh-session review unit. Model-agnostic; dry-run safe.

The fresh-session review takes a manuscript file, submits it to a Claude
model with the adversarial-reviewer system prompt from the paper §2.1,
and writes the JSON response atomically to `out_dir/<paper>__<model>.json`.

If the output file already exists, the function is a no-op (idempotent
re-runs). On quota errors, the underlying API call is wrapped in
`call_with_retry` which sleeps until the next 5h reset.

`dry_run=True` returns a mocked response so the surrounding runner
(checkpoint store, error classification, sleep math) can be smoke-tested
without an API key or quota consumption.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

from api_client import call_with_retry

SYSTEM_PROMPT = (
    "You are an adversarial reviewer of an academic manuscript. You have no "
    "prior context about this manuscript or its authors. Read the manuscript "
    "as a critical, independent peer reviewer. Identify weaknesses in the "
    "argument, missing counter-evidence, unstated assumptions, and any "
    "factual or methodological problems. Be specific; cite line numbers or "
    "section identifiers where possible. Return your review as JSON with the "
    "schema described in the user prompt."
)

USER_PROMPT_TEMPLATE = """Please review the following manuscript. Return JSON with this schema:

{{
  "issues": [
    {{"section": "<section ref>", "severity": "critical|major|minor",
      "description": "<one-paragraph description>",
      "counter_evidence": "<citation or note, or null>"}}
  ],
  "summary": "<2-3 sentence overall assessment>"
}}

MANUSCRIPT:
---
{manuscript}
---
"""


def _mock_response(paper_id: str, model: str) -> dict[str, Any]:
    return {
        "issues": [
            {
                "section": "(mock)",
                "severity": "minor",
                "description": (
                    f"Mock review for paper={paper_id} model={model}. "
                    "Dry-run does not call the real API."
                ),
                "counter_evidence": None,
            }
        ],
        "summary": f"Mock summary for {paper_id} under {model} (dry-run).",
        "_mock": True,
    }


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def run_one(
    paper_id: str,
    paper_path: Path,
    model: str,
    out_dir: Path,
    *,
    dry_run: bool = False,
    max_tokens: int = 4096,
) -> Path:
    """Run a single Fresh-session review and write output atomically.

    Returns the path of the output file. If the file already exists, the
    function returns immediately without re-querying.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_model = model.replace("/", "_").replace(":", "_")
    out_path = out_dir / f"{paper_id}__{safe_model}.json"
    if out_path.exists():
        return out_path  # idempotent
    manuscript = paper_path.read_text(encoding="utf-8")

    if dry_run:
        resp: Any = _mock_response(paper_id, model)
    else:
        # Lazy import: dry-run must not require the dependency.
        from anthropic import Anthropic  # type: ignore

        client = Anthropic()

        def _call() -> str:
            msg = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": USER_PROMPT_TEMPLATE.format(manuscript=manuscript),
                    }
                ],
            )
            # Concatenate text blocks; ignore non-text content.
            parts = []
            for block in msg.content:
                text = getattr(block, "text", None)
                if text:
                    parts.append(text)
            return "".join(parts)

        text = call_with_retry(_call, dry_run=False)
        try:
            resp = json.loads(text)
        except json.JSONDecodeError:
            resp = {"raw": text, "_parse_error": True}

    payload = {
        "paper_id": paper_id,
        "model": model,
        "run_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "dry_run": dry_run,
        "response": resp,
    }
    _atomic_write(
        out_path,
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )
    return out_path
