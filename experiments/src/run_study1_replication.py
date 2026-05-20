"""Study 1 model-version replication runner.

Iterates a (paper, model) grid:
- For each cell, spawn a Fresh-session adversarial review.
- Write the raw JSON output atomically.
- Update a JSON checkpoint after each completed cell.

Recovery semantics:
- 5h reset boundary anchored at 2026-05-21 03:10 KST (see reset_window.py).
- On quota errors (HTTP 429/529 or rate_limit/overloaded/quota/usage_limit
  signals), the runner sleeps until the next reset and retries up to
  --max-resets cycles (default 6 = ~30h).
- On non-quota errors, the failing cell is recorded and the loop continues
  to subsequent cells.
- On QuotaExhausted (--max-resets exceeded), the runner stops with exit
  code 2; the checkpoint preserves all completed cells so re-running
  picks up where it left off.

Idempotent: re-running the same command is safe at any time.

Usage:

    # Smoke test (no API key needed, no quota consumed):
    python experiments/src/run_study1_replication.py --dry-run

    # Real run (requires ANTHROPIC_API_KEY):
    python experiments/src/run_study1_replication.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterator

from api_client import QuotaExhausted
from checkpoint import Checkpoint
from fresh_review import run_one

# Paper grid: paper_id -> manuscript path, relative to --repo-root.
# Only narcissus is colocated in this repo; the other four sit in sibling
# repos under ../<repo>/paper/main.tex and require a multi-repo runner
# variant (planned, not in scope here).
PAPERS: dict[str, str] = {
    "narcissus": "paper/main.tex",
}

# Model grid: the two Claude versions in scope for the natural-experiment +
# replication design (see paper §2 and §4.1).
MODELS: list[str] = [
    "claude-opus-4-6",  # natural-experiment frontier (2026-Q1)
    "claude-opus-4-7",  # post-audit successor (2026-Q2)
]


def grid() -> Iterator[tuple[str, str, str]]:
    for paper_id, paper_path in PAPERS.items():
        for model in MODELS:
            yield paper_id, paper_path, model


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".", help="Repository root (default: cwd).")
    ap.add_argument(
        "--out",
        default="experiments/data/raw/study1-replication",
        help="Output directory for per-cell JSON files.",
    )
    ap.add_argument(
        "--state",
        default="experiments/state/study1-checkpoint.json",
        help="Checkpoint JSON path (gitignored by convention).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Use mocked responses; do not call the Anthropic API.",
    )
    ap.add_argument(
        "--max-resets",
        type=int,
        default=6,
        help="Maximum number of 5h reset cycles to ride through per cell.",
    )
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    out_dir = root / args.out
    ckpt = Checkpoint(root / args.state)

    print(f"[run] root={root}")
    print(f"[run] checkpoint={ckpt.path} (completed={ckpt.completed_count})")
    print(f"[run] dry_run={args.dry_run} max_resets={args.max_resets}")

    total = len(PAPERS) * len(MODELS)
    done = 0
    for paper_id, paper_rel, model in grid():
        key = f"{paper_id}::{model}"
        if ckpt.is_done(key):
            print(f"[run] skip (done): {key}")
            done += 1
            continue
        paper_path = root / paper_rel
        if not paper_path.exists():
            msg = f"manuscript not found: {paper_path}"
            print(f"[run] skip (missing): {key} — {msg}")
            ckpt.mark_failed(key, msg)
            continue
        print(f"[run] start: {key}")
        try:
            out_path = run_one(
                paper_id=paper_id,
                paper_path=paper_path,
                model=model,
                out_dir=out_dir,
                dry_run=args.dry_run,
            )
            ckpt.mark_done(
                key,
                {"output": str(out_path.relative_to(root))},
            )
            done += 1
            print(f"[run] done: {key} -> {out_path.relative_to(root)}")
        except QuotaExhausted as e:
            ckpt.mark_failed(key, f"quota exhausted: {e}")
            print(
                f"[run] STOP: quota retries exhausted at {key}; re-run to resume",
                file=sys.stderr,
            )
            return 2
        except Exception as e:  # noqa: BLE001
            ckpt.mark_failed(key, f"{type(e).__name__}: {e}")
            print(f"[run] FAIL: {key}: {type(e).__name__}: {e}", file=sys.stderr)
            # Continue to subsequent cells — one bad cell shouldn't block the rest.

    print(f"[run] complete: done={done}/{total} failed={len(ckpt.failed)}")
    return 0 if len(ckpt.failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
