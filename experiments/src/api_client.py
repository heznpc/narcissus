"""Anthropic API call wrapper with 5h-reset-window-aware retry.

The Anthropic API surfaces quota / overload conditions in several forms:
- HTTP 429 (rate_limit_error)
- HTTP 529 (overloaded_error)
- Error body containing 'rate_limit', 'overloaded', 'quota', 'usage_limit',
  or 'token_budget'.

`call_with_retry` catches these, computes the next 5h reset boundary
(via reset_window.next_reset), and sleeps until then before retrying.
Non-quota errors propagate immediately so the runner can decide how to
log them. Up to `max_resets` reset cycles before giving up.
"""
from __future__ import annotations

import time
from typing import Any, Callable

from reset_window import seconds_until_next_reset

QUOTA_STATUS = {429, 529}
QUOTA_KEYWORDS = (
    "rate_limit",
    "rate limit",
    "overloaded",
    "quota",
    "usage_limit",
    "token_budget",
    "token budget",
)


class QuotaExhausted(Exception):
    """All allowed reset cycles consumed; runner should stop."""


def is_quota_error(exc: BaseException) -> bool:
    """Heuristically classify an exception as a recoverable quota signal."""
    status = (
        getattr(exc, "status_code", None)
        or getattr(exc, "status", None)
        or getattr(exc, "http_status", None)
    )
    if isinstance(status, int) and status in QUOTA_STATUS:
        return True
    msg = str(exc).lower()
    return any(k in msg for k in QUOTA_KEYWORDS)


def call_with_retry(
    fn: Callable[[], Any],
    *,
    max_resets: int = 6,
    dry_run: bool = False,
    log: Callable[[str], None] = print,
) -> Any:
    """Call `fn`, riding through quota resets.

    Up to `max_resets` resets (default 6 = ~30h) before giving up.
    """
    attempts = 0
    while True:
        try:
            return fn()
        except Exception as e:
            if not is_quota_error(e):
                raise
            attempts += 1
            if attempts > max_resets:
                raise QuotaExhausted(
                    f"Quota retries exhausted ({max_resets}); last error: {e!r}"
                )
            wait_s = seconds_until_next_reset()
            log(
                f"[api_client] quota signal (attempt {attempts}/{max_resets}): "
                f"{type(e).__name__}: {e}; sleeping {wait_s:.0f}s until next 5h reset"
            )
            if dry_run:
                # In dry-run we just simulate; cap real sleep so smoke
                # tests stay fast.
                time.sleep(min(wait_s, 2))
            else:
                time.sleep(wait_s)
            log("[api_client] resuming after reset")
