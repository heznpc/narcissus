"""Cross-vendor comparison: Claude vs Gemini on Fresh x Adversarial review.

The first NON-Claude data point (TODO #2). Tests whether the Narcissus-Loop
structural critiques generalize beyond the Claude family.

Metric robustness ladder (most -> least vendor-robust):
  1. Does the other vendor flag the SAME structural magnets (sections that
     ALL runs of a vendor agree on)? -> the headline, most robust.
  2. Issue count (coarse but vendor-neutral).
  3. Cross-vendor section-overlap Jaccard -> LEAST robust: section-citation
     style differs by vendor (handled by the normalizer's bare-number fix,
     but residual confound remains; see paper §6 measurement-validity note).

Compares Gemini-3.1-pro vs Claude Opus 4.6 (the original-audit-era model) as
the primary cross-vendor pair, n=5 each, Fresh x Adversarial.

Run from repo root:  python3 experiments/src/compare_crossvendor.py
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

CLAUDE = "claude-opus-4-6"
GEMINI = "gemini-3.1-pro-preview"
RUNS = list(range(1, 6))


def load(paper, model, run):
    f = OUT_DIR / f"{paper}__{model}__bare__run-{run}.json"
    return json.loads(f.read_text()) if f.exists() else None


def runs_for(paper, model):
    return [(r, d) for r in RUNS if (d := load(paper, model, r)) is not None]


def secset(d, paper):
    s = set()
    for i in d["response"]["issues"]:
        for x in normalize_section(i.get("section", ""), paper_id=paper):
            s.add(x)
    return s


def stable_core(paper, model):
    rd = runs_for(paper, model)
    if not rd:
        return set()
    freq = Counter()
    for _, d in rd:
        for s in secset(d, paper):
            freq[s] += 1
    return {s for s, k in freq.items() if k == len(rd)}


def within_jac(paper, model):
    fps = [issues_as_fingerprints(d, paper_id=paper) for _, d in runs_for(paper, model)]
    pr = [jaccard(a, b) for a, b in combinations(fps, 2)]
    return statistics.mean(pr) if pr else float("nan")


def cross_jac(paper):
    g = [issues_as_fingerprints(d, paper_id=paper) for _, d in runs_for(paper, GEMINI)]
    c = [issues_as_fingerprints(d, paper_id=paper) for _, d in runs_for(paper, CLAUDE)]
    pr = [jaccard(a, b) for a in g for b in c]
    return statistics.mean(pr) if pr else float("nan")


def _m(xs):
    xs = [x for x in xs if x == x]
    return statistics.mean(xs) if xs else float("nan")


def main():
    print("=" * 80)
    print("CROSS-VENDOR — Gemini-3.1-pro vs Claude-Opus-4.6, Fresh x Adversarial, n=5")
    print("=" * 80)

    # Issue count + within-vendor reliability.
    print("\nIssue count mean +/- sd, and within-vendor reliability:")
    print(f"  {'paper':<25} {'Claude n':>9} {'Gemini n':>9} {'C wJacc':>8} {'G wJacc':>8} {'C kappa':>8} {'G kappa':>8}")
    for p in PAPERS:
        cc = [len(d["response"]["issues"]) for _, d in runs_for(p, CLAUDE)]
        gc = [len(d["response"]["issues"]) for _, d in runs_for(p, GEMINI)]
        cstr = f"{statistics.mean(cc):.1f}±{(statistics.stdev(cc) if len(cc)>1 else 0):.1f}" if cc else "--"
        gstr = f"{statistics.mean(gc):.1f}±{(statistics.stdev(gc) if len(gc)>1 else 0):.1f}" if gc else "--"
        ck = fleiss_kappa(p, runs_for(p, CLAUDE)).get("kappa", float("nan"))
        gk = fleiss_kappa(p, runs_for(p, GEMINI)).get("kappa", float("nan"))
        print(f"  {p:<25} {cstr:>9} {gstr:>9} {within_jac(p,CLAUDE):>8.3f} "
              f"{within_jac(p,GEMINI):>8.3f} {ck:>8.3f} {gk:>8.3f}")

    # ===== THE HEADLINE: cross-vendor structural-magnet overlap =====
    print("\n*** Cross-vendor structural magnets (sections ALL 5 runs of BOTH vendors flag) ***")
    total_shared = 0
    for p in PAPERS:
        cc = stable_core(p, CLAUDE)
        gc = stable_core(p, GEMINI)
        shared = sorted(cc & gc)
        total_shared += len(shared)
        print(f"\n  {p}:")
        print(f"    Claude-4.6 core ({len(cc)}): {', '.join(sorted(cc)) or '(none)'}")
        print(f"    Gemini core     ({len(gc)}): {', '.join(sorted(gc)) or '(none)'}")
        print(f"    SHARED magnets  ({len(shared)}): {', '.join(shared) or '(none)'}")
    print(f"\n  Total cross-vendor shared magnets across 5 papers: {total_shared}")

    # Cross-vendor Jaccard (least robust; reported with caveat).
    print("\nCross-vendor pairwise Jaccard (section,severity — LEAST robust, style-confounded):")
    xs = []
    for p in PAPERS:
        j = cross_jac(p)
        xs.append(j)
        print(f"  {p:<25} {j:>8.3f}")
    print(f"  {'MEAN':<25} {_m(xs):>8.3f}")

    # Verdict scaffolding.
    print("\n" + "=" * 80)
    cn = _m([statistics.mean([len(d['response']['issues']) for _,d in runs_for(p,CLAUDE)]) for p in PAPERS])
    gn = _m([statistics.mean([len(d['response']['issues']) for _,d in runs_for(p,GEMINI)]) for p in PAPERS])
    cw = _m([within_jac(p, CLAUDE) for p in PAPERS])
    gw = _m([within_jac(p, GEMINI) for p in PAPERS])
    print(f"Mean issue count:   Claude {cn:.1f}  vs  Gemini {gn:.1f}")
    print(f"Mean within Jaccard: Claude {cw:.3f}  vs  Gemini {gw:.3f}")
    print(f"Mean cross-vendor Jaccard: {_m(xs):.3f}")
    print(f"Cross-vendor shared magnets (5/5 both vendors): {total_shared} across 5 papers")
    print("=" * 80)


if __name__ == "__main__":
    main()
