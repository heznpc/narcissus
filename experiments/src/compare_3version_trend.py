"""3-point version trend: Opus 4.6 / 4.7 / 4.8 on Fresh x Adversarial.

Answers the question a 2-point (4.6, 4.7) comparison cannot: is the
Narcissus Loop diagnosis model-architecture-STABLE, or does it DRIFT
with version distance?

  - flat cross-version Jaccard (4.6-4.7 ~= 4.6-4.8 ~= 4.7-4.8)  -> stable
  - monotonic decay with version distance (4.6-4.8 < 4.6-4.7)  -> drift

Design notes (design-review V4/V6):
  - All three versions use n=5 (runs 1-5) Fresh x Adversarial for a
    BALANCED trend. The 4.6 arm also has runs 6-10 on disk, but those are
    excluded here so 4.6 is not artificially advantaged.
  - The headline metric is (section, severity) Jaccard, NOT raw issue
    count. Issue count is verbosity-sensitive (4.8 cells cost ~1.5x more
    output tokens), so a raw-count comparison would conflate verbosity
    calibration with bias dynamics. Jaccard is normalized to which
    sections are flagged.

Run from repo root:
    python3 experiments/src/compare_3version_trend.py
"""
from __future__ import annotations

import json
import statistics
from collections import Counter
from itertools import combinations
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from analyze_multirun import (
    OUT_DIR, PAPERS, normalize_section, fleiss_kappa, jaccard,
    issues_as_fingerprints,
)

VERSIONS = ["claude-opus-4-6", "claude-opus-4-7", "claude-opus-4-8"]
SHORT = {"claude-opus-4-6": "4.6", "claude-opus-4-7": "4.7", "claude-opus-4-8": "4.8"}
RUNS = list(range(1, 6))   # n=5, balanced across versions


def load(paper: str, model: str, run: int) -> dict | None:
    # Fresh x Adversarial -> tag is just "bare".
    f = OUT_DIR / f"{paper}__{model}__bare__run-{run}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def runs_for(paper: str, model: str) -> list[tuple[int, dict]]:
    out = []
    for r in RUNS:
        d = load(paper, model, r)
        if d is not None:
            out.append((r, d))
    return out


def sections_in(d: dict, paper: str) -> set[str]:
    s = set()
    for issue in d["response"]["issues"]:
        for sec in normalize_section(issue.get("section", ""), paper_id=paper):
            s.add(sec)
    return s


def stable_core(paper: str, model: str) -> set[str]:
    rd = runs_for(paper, model)
    if not rd:
        return set()
    freq: Counter[str] = Counter()
    for _, d in rd:
        for sec in sections_in(d, paper):
            freq[sec] += 1
    n = len(rd)
    return {s for s, k in freq.items() if k == n}


def within_version_jaccard(paper: str, model: str) -> float:
    rd = runs_for(paper, model)
    fps = [issues_as_fingerprints(d, paper_id=paper) for _, d in rd]
    pairs = [jaccard(a, b) for a, b in combinations(fps, 2)]
    return statistics.mean(pairs) if pairs else float("nan")


def cross_version_jaccard(paper: str, m1: str, m2: str) -> float:
    rd1 = runs_for(paper, m1)
    rd2 = runs_for(paper, m2)
    fps1 = [issues_as_fingerprints(d, paper_id=paper) for _, d in rd1]
    fps2 = [issues_as_fingerprints(d, paper_id=paper) for _, d in rd2]
    pairs = [jaccard(a, b) for a in fps1 for b in fps2]
    return statistics.mean(pairs) if pairs else float("nan")


def _safe_mean(xs):
    xs = [x for x in xs if x == x]
    return statistics.mean(xs) if xs else float("nan")


def main() -> None:
    print("=" * 78)
    print("3-point version trend — Opus 4.6 / 4.7 / 4.8, Fresh x Adversarial, n=5")
    print("=" * 78)

    # Issue counts (reported but de-emphasized; verbosity-sensitive).
    print("\nIssue count mean +/- sd per version (NB: verbosity-sensitive — see Jaccard below):")
    print(f"  {'paper':<25} {'4.6':>12} {'4.7':>12} {'4.8':>12}")
    for p in PAPERS:
        cells = []
        for v in VERSIONS:
            rd = runs_for(p, v)
            counts = [len(d["response"]["issues"]) for _, d in rd]
            if counts:
                m = statistics.mean(counts)
                s = statistics.stdev(counts) if len(counts) > 1 else 0.0
                cells.append(f"{m:.1f}±{s:.1f}")
            else:
                cells.append("--")
        print(f"  {p:<25} {cells[0]:>12} {cells[1]:>12} {cells[2]:>12}")

    # Within-version Fleiss kappa.
    print("\nWithin-version Fleiss kappa (n=5, section-flag agreement):")
    print(f"  {'paper':<25} {'4.6':>8} {'4.7':>8} {'4.8':>8}")
    kappa_by_v = {v: [] for v in VERSIONS}
    for p in PAPERS:
        row = []
        for v in VERSIONS:
            rd = runs_for(p, v)
            fk = fleiss_kappa(p, rd) if len(rd) >= 2 else {"kappa": float("nan")}
            row.append(fk["kappa"])
            kappa_by_v[v].append(fk["kappa"])
        print(f"  {p:<25} {row[0]:>8.3f} {row[1]:>8.3f} {row[2]:>8.3f}")
    print(f"  {'MEAN':<25} " + " ".join(f"{_safe_mean(kappa_by_v[v]):>8.3f}" for v in VERSIONS))

    # Within-version Jaccard (the baseline for 'how much do two runs of the
    # SAME version agree').
    print("\nWithin-version pairwise Jaccard (n=5):")
    print(f"  {'paper':<25} {'4.6':>8} {'4.7':>8} {'4.8':>8}")
    wv_by_v = {v: [] for v in VERSIONS}
    for p in PAPERS:
        row = []
        for v in VERSIONS:
            j = within_version_jaccard(p, v)
            row.append(j)
            wv_by_v[v].append(j)
        print(f"  {p:<25} {row[0]:>8.3f} {row[1]:>8.3f} {row[2]:>8.3f}")
    print(f"  {'MEAN':<25} " + " ".join(f"{_safe_mean(wv_by_v[v]):>8.3f}" for v in VERSIONS))

    # Cross-version Jaccard — the headline.
    pair_names = [("4.6", "4.7"), ("4.6", "4.8"), ("4.7", "4.8")]
    pair_models = [
        ("claude-opus-4-6", "claude-opus-4-7"),
        ("claude-opus-4-6", "claude-opus-4-8"),
        ("claude-opus-4-7", "claude-opus-4-8"),
    ]
    print("\n*** Cross-version pairwise Jaccard (THE TREND) ***")
    print(f"  {'paper':<25} {'4.6-4.7':>9} {'4.6-4.8':>9} {'4.7-4.8':>9}")
    xv_by_pair = {pn: [] for pn in pair_names}
    for p in PAPERS:
        row = []
        for (pn, (m1, m2)) in zip(pair_names, pair_models):
            j = cross_version_jaccard(p, m1, m2)
            row.append(j)
            xv_by_pair[pn].append(j)
        print(f"  {p:<25} {row[0]:>9.3f} {row[1]:>9.3f} {row[2]:>9.3f}")
    xv_means = [(_safe_mean(xv_by_pair[pn])) for pn in pair_names]
    print(f"  {'MEAN':<25} " + " ".join(f"{m:>9.3f}" for m in xv_means))

    # Stable-core 3-way overlap.
    print("\n3-way stable-core (5/5) overlap per paper:")
    print(f"  {'paper':<25} {'|46|':>5} {'|47|':>5} {'|48|':>5} {'46n47n48':>9}")
    triple_overlap_total = 0
    union_total = 0
    for p in PAPERS:
        c6 = stable_core(p, "claude-opus-4-6")
        c7 = stable_core(p, "claude-opus-4-7")
        c8 = stable_core(p, "claude-opus-4-8")
        triple = c6 & c7 & c8
        triple_overlap_total += len(triple)
        union_total += len(c6 | c7 | c8)
        print(f"  {p:<25} {len(c6):>5} {len(c7):>5} {len(c8):>5} {len(triple):>9}")

    # Verdict.
    print("\n" + "=" * 78)
    wv_overall = _safe_mean([wv_by_v[v][i] for v in VERSIONS for i in range(len(PAPERS))])
    print(f"Mean within-version Jaccard:  {wv_overall:.3f}")
    print(f"Mean cross-version Jaccard:   4.6-4.7={xv_means[0]:.3f}  "
          f"4.6-4.8={xv_means[1]:.3f}  4.7-4.8={xv_means[2]:.3f}")
    # Is the trend flat? Compare 4.6-4.8 (max version distance) to 4.6-4.7
    # (min distance).
    if all(m == m for m in xv_means):
        spread = max(xv_means) - min(xv_means)
        far = xv_means[1]   # 4.6-4.8
        near = xv_means[0]  # 4.6-4.7
        print(f"\nTrend test (version-distance effect):")
        print(f"  near pair (4.6-4.7) = {near:.3f}")
        print(f"  far  pair (4.6-4.8) = {far:.3f}")
        print(f"  spread across all 3 cross-version pairs = {spread:.3f}")
        if spread < 0.05:
            print("  -> FLAT within 0.05: cross-version agreement does not decay with")
            print("     version distance. Strong evidence the diagnosis is")
            print("     model-architecture-STABLE across the Claude 4.x family.")
        elif far < near - 0.05:
            print("  -> DECAY: 4.6-4.8 notably below 4.6-4.7. Evidence of version DRIFT;")
            print("     the diagnosis is partially version-specific.")
        else:
            print("  -> MIXED: no clean monotonic decay but spread exceeds 0.05.")
        print(f"\n  Cross-version ({_safe_mean(xv_means):.3f}) vs within-version "
              f"({wv_overall:.3f}): gap = {wv_overall - _safe_mean(xv_means):.3f}")
        print("  (small gap => swapping versions changes findings about as much as")
        print("   re-running the same version => run-to-run noise dominates.)")
    print("=" * 78)


if __name__ == "__main__":
    main()
