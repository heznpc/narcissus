"""Smoke tests for reset_window.next_reset.

Run with: python experiments/src/test_reset_window.py
Exits non-zero on any assertion failure.
"""
from __future__ import annotations

import datetime as dt
import sys

from reset_window import ANCHOR_UTC, PERIOD, next_reset, seconds_until_next_reset


def _assert_eq(actual, expected, label: str) -> None:
    assert actual == expected, f"{label}: expected {expected}, got {actual}"
    print(f"  ok: {label}")


def main() -> int:
    print("test: next_reset semantics")

    # Before anchor: returns anchor.
    before = ANCHOR_UTC - dt.timedelta(hours=1)
    _assert_eq(next_reset(before), ANCHOR_UTC, "before anchor returns anchor")

    # At anchor: returns anchor + 5h (next boundary, not current).
    _assert_eq(
        next_reset(ANCHOR_UTC),
        ANCHOR_UTC + PERIOD,
        "exactly at anchor returns anchor+5h",
    )

    # 1h after anchor: next is anchor + 5h.
    one_h = ANCHOR_UTC + dt.timedelta(hours=1)
    _assert_eq(
        next_reset(one_h),
        ANCHOR_UTC + PERIOD,
        "anchor+1h returns anchor+5h",
    )

    # Exactly at anchor + 5h: returns anchor + 10h.
    boundary = ANCHOR_UTC + PERIOD
    _assert_eq(
        next_reset(boundary),
        ANCHOR_UTC + 2 * PERIOD,
        "anchor+5h returns anchor+10h",
    )

    # 4h59m after anchor: still anchor + 5h.
    almost = ANCHOR_UTC + dt.timedelta(hours=4, minutes=59)
    _assert_eq(
        next_reset(almost),
        ANCHOR_UTC + PERIOD,
        "anchor+4h59m returns anchor+5h",
    )

    # 7h after anchor: anchor + 10h.
    seven = ANCHOR_UTC + dt.timedelta(hours=7)
    _assert_eq(
        next_reset(seven),
        ANCHOR_UTC + 2 * PERIOD,
        "anchor+7h returns anchor+10h",
    )

    # KST verification: anchor in KST should be 2026-05-21 03:10.
    kst = dt.timezone(dt.timedelta(hours=9))
    anchor_kst = ANCHOR_UTC.astimezone(kst)
    assert anchor_kst.year == 2026 and anchor_kst.month == 5 and anchor_kst.day == 21
    assert anchor_kst.hour == 3 and anchor_kst.minute == 10
    print("  ok: anchor in KST = 2026-05-21 03:10")

    # seconds_until_next_reset includes jitter and is non-negative.
    s = seconds_until_next_reset(ANCHOR_UTC, jitter_seconds=15)
    assert s >= 0
    assert abs(s - (PERIOD.total_seconds() + 15)) < 1, (
        f"sleep math: expected ~{PERIOD.total_seconds()+15}s, got {s}s"
    )
    print(f"  ok: sleep at anchor = {s:.0f}s (5h + 15s jitter)")

    print("all reset_window tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
