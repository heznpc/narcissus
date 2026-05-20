"""Compute the next 5-hour Anthropic API quota reset window.

Anchor (per local quota cadence): 2026-05-21 03:10:00 KST.
Equivalently: 2026-05-20 18:10:00 UTC.
Resets every 5 hours from the anchor.

Used by api_client.call_with_retry to decide how long to sleep when a
quota signal is received.

Run this module directly to print the current and next reset boundary:

    python experiments/src/reset_window.py
"""
from __future__ import annotations

import datetime as dt

# Anchor in UTC. KST (UTC+9): 2026-05-21 03:10 KST == 2026-05-20 18:10 UTC.
ANCHOR_UTC = dt.datetime(2026, 5, 20, 18, 10, 0, tzinfo=dt.timezone.utc)
PERIOD = dt.timedelta(hours=5)
KST = dt.timezone(dt.timedelta(hours=9), name="KST")


def next_reset(now: dt.datetime | None = None) -> dt.datetime:
    """Return the next reset boundary strictly after `now` (UTC-aware)."""
    if now is None:
        now = dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)
    if now < ANCHOR_UTC:
        return ANCHOR_UTC
    elapsed = (now - ANCHOR_UTC).total_seconds()
    period_s = PERIOD.total_seconds()
    n_periods = int(elapsed // period_s) + 1
    return ANCHOR_UTC + dt.timedelta(seconds=n_periods * period_s)


def seconds_until_next_reset(
    now: dt.datetime | None = None,
    jitter_seconds: int = 15,
) -> float:
    """Seconds to wait until the next reset, plus a small jitter.

    Jitter avoids thundering-herd reattempts the instant the quota refills.
    """
    if now is None:
        now = dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)
    delta = (next_reset(now) - now).total_seconds() + jitter_seconds
    return max(0.0, delta)


def _fmt(t: dt.datetime) -> str:
    return f"{t.astimezone(dt.timezone.utc).isoformat()} (UTC) / {t.astimezone(KST).isoformat()} (KST)"


if __name__ == "__main__":
    now = dt.datetime.now(dt.timezone.utc)
    nxt = next_reset(now)
    print(f"anchor:     {_fmt(ANCHOR_UTC)}")
    print(f"now:        {_fmt(now)}")
    print(f"next reset: {_fmt(nxt)}")
    print(f"sleep until next reset: {seconds_until_next_reset(now):.0f}s")
