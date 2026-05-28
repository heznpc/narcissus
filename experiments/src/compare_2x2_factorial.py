"""2x2 factorial analysis: Context × Stance on Fresh-session reviews.

Cells (n=5 runs per paper per cell except A which is n=10):
  A: Fresh × Adversarial         — runs 1..10 of <p>__opus-4-6__bare__run-N.json
  B: Fresh × Neutral             — runs 1..5  of <p>__opus-4-6__bare__neutral__run-N.json
  C: Collaborator × Adversarial  — runs 1..5  of <p>__opus-4-6__bare__collaborator__run-N.json
  D: Collaborator × Neutral      — runs 1..5  of <p>__opus-4-6__bare__neutral__collaborator__run-N.json

Tests:
  - Main effect of CONTEXT (Fresh vs Collaborator) on issue count, severity,
    stable-core size
  - Main effect of STANCE (Adversarial vs Neutral) on same
  - INTERACTION: is the Collaborator × Adversarial cell more (or less) than
    the sum of the two main effects? This is the §3 H4 (Emergent Interaction)
    test at the model-on-itself level.

We use Cell A's runs 1..5 only for the 2x2 balanced ANOVA-style comparison
(matching n=5 in cells B, C, D); runs 6..10 from Cell A contribute extra
within-cell-A reliability data but are not used in cross-cell tests for
balance.
"""
from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from analyze_multirun import (
    OUT_DIR, PAPERS, normalize_section, fleiss_kappa, jaccard,
    issues_as_fingerprints,
)

# Map cell-name -> filename glob pattern.
CELL_PATTERNS = {
    "Fresh×Adv":         "__claude-opus-4-6__bare__run-",
    "Fresh×Neu":         "__claude-opus-4-6__bare__neutral__run-",
    "Deep×Adv":          "__claude-opus-4-6__bare__collaborator__run-",
    "Deep×Neu":          "__claude-opus-4-6__bare__neutral__collaborator__run-",
}
N_RUNS = 5   # balanced 2x2: use first 5 runs from each cell


def load_cell(paper: str, cell: str, run: int) -> dict | None:
    suffix = CELL_PATTERNS[cell]
    f = OUT_DIR / f"{paper}{suffix}{run}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def sections_for(d: dict, paper: str) -> set[str]:
    out: set[str] = set()
    for issue in d["response"]["issues"]:
        for s in normalize_section(issue.get("section", ""), paper_id=paper):
            out.add(s)
    return out


def cell_summary(paper: str, cell: str) -> dict:
    counts = []
    sev = Counter()
    runs_data = []
    cost_total = 0.0
    wall_total = 0
    for r in range(1, N_RUNS + 1):
        d = load_cell(paper, cell, r)
        if d is None:
            continue
        counts.append(len(d["response"]["issues"]))
        for issue in d["response"]["issues"]:
            sev[issue.get("severity", "unknown")] += 1
        runs_data.append((r, d))
        m = d.get("metrics", {})
        cost_total += m.get("total_cost_usd") or 0
        wall_total += m.get("wall_clock_s") or 0
    fk = fleiss_kappa(paper, runs_data) if len(runs_data) >= 2 else {"kappa": float("nan")}

    # Stable core (flagged in all N runs).
    freq: Counter[str] = Counter()
    for _, d in runs_data:
        for s in sections_for(d, paper):
            freq[s] += 1
    n_runs = len(runs_data)
    core = {s for s, k in freq.items() if k == n_runs}

    return {
        "n": n_runs,
        "issue_mean": statistics.mean(counts) if counts else float("nan"),
        "issue_sd": statistics.stdev(counts) if len(counts) > 1 else 0.0,
        "severity": dict(sev),
        "kappa": fk["kappa"],
        "stable_core": core,
        "cost_total": cost_total,
        "wall_total": wall_total,
    }


def main() -> None:
    cells = list(CELL_PATTERNS.keys())

    print("=" * 90)
    print("2x2 Factorial — Context (Fresh|Deep) × Stance (Adv|Neu) on Fresh-session reviews")
    print("=" * 90)
    print()

    # Per-paper x cell matrix of issue count (mean).
    rows = {p: {} for p in PAPERS}
    for p in PAPERS:
        for c in cells:
            rows[p][c] = cell_summary(p, c)

    # Issue count table.
    print("Issue count mean ± sd (n=5 runs per cell):")
    print(f"  {'paper':<25} " + "".join(f"{c:>14}" for c in cells))
    for p in PAPERS:
        line = f"  {p:<25} "
        for c in cells:
            s = rows[p][c]
            line += f"{s['issue_mean']:>5.1f}±{s['issue_sd']:>4.1f}    "
        print(line)
    # Marginals.
    print(f"  {'MEAN across papers':<25} " + "".join(
        f"{statistics.mean(rows[p][c]['issue_mean'] for p in PAPERS):>13.2f}" for c in cells
    ))
    print()

    # 2x2 ANOVA-like main effects + interaction on issue count, aggregated
    # across the 5 papers (treating each paper as a replicate).
    def cell_mean(c):
        return statistics.mean(rows[p][c]["issue_mean"] for p in PAPERS)

    A = cell_mean("Fresh×Adv")
    B = cell_mean("Fresh×Neu")
    C = cell_mean("Deep×Adv")
    D = cell_mean("Deep×Neu")
    # Main effect of context: ((C+D)/2) - ((A+B)/2)
    main_ctx = ((C + D) / 2) - ((A + B) / 2)
    # Main effect of stance: ((A+C)/2) - ((B+D)/2)
    main_st = ((A + C) / 2) - ((B + D) / 2)
    # Interaction: (D - C) - (B - A)   [neutral-adv difference in Deep vs Fresh]
    # Equivalent: (A + D) - (B + C)
    interaction = (A + D) - (B + C)
    print("Marginal cell means (across 5 papers):")
    print(f"  Fresh × Adversarial  (A): {A:.2f}")
    print(f"  Fresh × Neutral      (B): {B:.2f}")
    print(f"  Deep  × Adversarial  (C): {C:.2f}")
    print(f"  Deep  × Neutral      (D): {D:.2f}")
    print()
    print("Effects on issue count (per-cell mean):")
    print(f"  Main effect of CONTEXT  (Deep − Fresh):       {main_ctx:+.3f}")
    print(f"  Main effect of STANCE   (Adversarial − Neu):  {main_st:+.3f}")
    print(f"  INTERACTION  ((A+D) − (B+C)):                  {interaction:+.3f}")
    print(f"  (positive interaction = Deep×Adv produces *more* than the sum")
    print(f"   of context + stance main effects predict; consistent with the")
    print(f"   §3 H4 emergent-interaction hypothesis)")
    print()

    # Severity main-effect tally.
    print("Severity totals (sum across 5 papers × 5 runs = 25 cells/condition):")
    print(f"  {'cell':<25} {'critical':>10} {'major':>10} {'minor':>10} {'total':>10}")
    for c in cells:
        tot = Counter()
        for p in PAPERS:
            for sev, n in rows[p][c]["severity"].items():
                tot[sev] += n
        total = sum(tot.values())
        print(f"  {c:<25} {tot.get('critical',0):>10} {tot.get('major',0):>10} "
              f"{tot.get('minor',0):>10} {total:>10}")
    print()

    # Per-cell Fleiss kappa.
    print("Fleiss κ per paper × cell (n=5):")
    print(f"  {'paper':<25} " + "".join(f"{c:>14}" for c in cells))
    for p in PAPERS:
        line = f"  {p:<25} "
        for c in cells:
            line += f"{rows[p][c]['kappa']:>13.3f} "
        print(line)
    # FIX (code review #15): statistics.mean of an empty list raises
    # StatisticsError. Filter NaN, then default to NaN when empty.
    def _safe_kappa_mean(c):
        vals = [rows[p][c]['kappa'] for p in PAPERS
                if rows[p][c]['kappa'] == rows[p][c]['kappa']]
        return statistics.mean(vals) if vals else float("nan")
    print(f"  {'MEAN across papers':<25} " + "".join(
        f"{_safe_kappa_mean(c):>13.3f} " for c in cells
    ))
    print()

    # Stable-core size + cross-cell overlap.
    print("Stable-core (5/5) size per paper × cell:")
    print(f"  {'paper':<25} " + "".join(f"{c:>14}" for c in cells))
    for p in PAPERS:
        line = f"  {p:<25} "
        for c in cells:
            line += f"{len(rows[p][c]['stable_core']):>13} "
        print(line)
    print()

    # Cost.
    print("=" * 90)
    print("Cost per cell-condition (envelope-bearing only):")
    for c in cells:
        tc = sum(rows[p][c]["cost_total"] for p in PAPERS)
        tw = sum(rows[p][c]["wall_total"] for p in PAPERS)
        n = sum(rows[p][c]["n"] for p in PAPERS)
        if tc > 0:
            print(f"  {c:<25} ${tc:>7.2f} ({n} cells, ${tc/n:.4f}/cell, wall_sum={tw}s)")
        else:
            print(f"  {c:<25} (no envelope data)")
    print("=" * 90)


if __name__ == "__main__":
    main()
