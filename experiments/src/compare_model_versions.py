"""Compare 4.6 vs 4.7 Fresh-session reviews of the same 5 papers.

Builds on analyze_multirun.py. For each paper:
  - intersect/union of stable-core sections between 4.6 and 4.7
  - cross-model Jaccard (does 4.7 catch the same things as 4.6?)
  - per-version Fleiss kappa
  - cost / token comparison (only for cells that have envelope metrics)
  - new findings in 4.7 not in 4.6 (and vice versa)

Run from repo root:
    python3 experiments/src/compare_model_versions.py

Expected input:
    experiments/data/raw/study1-replication/<paper>__claude-opus-4-6__bare__run-{1..5}.json
    experiments/data/raw/study1-replication/<paper>__claude-opus-4-7__bare__run-{1..5}.json
"""
from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

# Reuse normalization + Fleiss from analyze_multirun.
import sys
sys.path.insert(0, str(Path(__file__).parent))
from analyze_multirun import (
    OUT_DIR, PAPERS, RUNS,
    normalize_section, fleiss_kappa, jaccard,
)


def load(paper: str, model: str, run: int) -> dict | None:
    f = OUT_DIR / f"{paper}__{model}__bare__run-{run}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def sections_in_run(d: dict, paper: str) -> set[str]:
    out: set[str] = set()
    for issue in d["response"]["issues"]:
        for s in normalize_section(issue.get("section", ""), paper_id=paper):
            out.add(s)
    return out


def stable_core(paper: str, model: str, threshold: int = 5) -> set[str]:
    """Sections flagged in >= threshold of the 5 runs for this (paper, model)."""
    freq: Counter[str] = Counter()
    n = 0
    for r in RUNS:
        d = load(paper, model, r)
        if d is None:
            continue
        n += 1
        for s in sections_in_run(d, paper):
            freq[s] += 1
    return {s for s, k in freq.items() if k >= threshold}


def cost_summary(paper: str, model: str) -> dict:
    """Tally cost + tokens across the 5 runs for this (paper, model)."""
    totals = {"cells": 0, "cost_usd": 0.0, "input_tokens": 0,
              "output_tokens": 0, "cache_read": 0, "cache_create": 0,
              "wall_clock_s": 0, "duration_api_ms": 0}
    for r in RUNS:
        d = load(paper, model, r)
        if d is None:
            continue
        m = d.get("metrics", {})
        u = m.get("usage", {}) or {}
        cost = m.get("total_cost_usd") or 0
        totals["cells"] += 1
        totals["cost_usd"] += cost
        totals["input_tokens"] += u.get("input_tokens") or 0
        totals["output_tokens"] += u.get("output_tokens") or 0
        totals["cache_read"] += u.get("cache_read_input_tokens") or 0
        totals["cache_create"] += u.get("cache_creation_input_tokens") or 0
        totals["wall_clock_s"] += m.get("wall_clock_s") or 0
        totals["duration_api_ms"] += m.get("duration_api_ms") or 0
    return totals


def cross_version_jaccard(paper: str) -> dict:
    """Pairwise Jaccard across model versions: for each (4.6 run, 4.7 run) pair,
    compute Jaccard on (section, severity) fingerprints.

    25 pairs per paper (5 x 5)."""
    from analyze_multirun import issues_as_fingerprints
    pairs = []
    v46_data = [(r, load(paper, "claude-opus-4-6", r)) for r in RUNS]
    v47_data = [(r, load(paper, "claude-opus-4-7", r)) for r in RUNS]
    for r46, d46 in v46_data:
        if d46 is None:
            continue
        fp46 = issues_as_fingerprints(d46, paper_id=paper)
        for r47, d47 in v47_data:
            if d47 is None:
                continue
            fp47 = issues_as_fingerprints(d47, paper_id=paper)
            pairs.append({
                "run_46": r46, "run_47": r47,
                "jaccard": jaccard(fp46, fp47),
                "intersection": len(fp46 & fp47),
                "union": len(fp46 | fp47),
            })
    if pairs:
        return {
            "pairs": pairs,
            "mean": statistics.mean(p["jaccard"] for p in pairs),
            "median": statistics.median(p["jaccard"] for p in pairs),
            "min": min(p["jaccard"] for p in pairs),
            "max": max(p["jaccard"] for p in pairs),
        }
    return {"pairs": [], "mean": float("nan"), "median": float("nan"),
            "min": float("nan"), "max": float("nan")}


def main() -> None:
    print("=" * 78)
    print("4.6 vs 4.7 cross-version comparison")
    print("=" * 78)

    rows = []
    for p in PAPERS:
        core46 = stable_core(p, "claude-opus-4-6", threshold=5)
        core47 = stable_core(p, "claude-opus-4-7", threshold=5)
        nearcore46 = stable_core(p, "claude-opus-4-6", threshold=4)
        nearcore47 = stable_core(p, "claude-opus-4-7", threshold=4)
        cost46 = cost_summary(p, "claude-opus-4-6")
        cost47 = cost_summary(p, "claude-opus-4-7")
        # Fleiss within each version.
        f46 = [(r, load(p, "claude-opus-4-6", r)) for r in RUNS]
        f46 = [(r, d) for r, d in f46 if d is not None]
        f47 = [(r, load(p, "claude-opus-4-7", r)) for r in RUNS]
        f47 = [(r, d) for r, d in f47 if d is not None]
        k46 = fleiss_kappa(p, f46)["kappa"] if f46 else float("nan")
        k47 = fleiss_kappa(p, f47)["kappa"] if f47 else float("nan")
        cross = cross_version_jaccard(p)
        rows.append({
            "paper": p,
            "core46": sorted(core46),
            "core47": sorted(core47),
            "core_intersection": sorted(core46 & core47),
            "core_only_46": sorted(core46 - core47),
            "core_only_47": sorted(core47 - core46),
            "nearcore46_count": len(nearcore46),
            "nearcore47_count": len(nearcore47),
            "kappa46": k46, "kappa47": k47,
            "cost46": cost46, "cost47": cost47,
            "cross_version_jaccard": cross,
        })

    # Summary table.
    print(f"\n{'paper':<25} {'core 4.6':>9} {'core 4.7':>9} {'∩':>5} {'κ4.6':>7} {'κ4.7':>7} {'XJacc':>7}")
    print("-" * 78)
    for r in rows:
        xj = r["cross_version_jaccard"]["mean"]
        print(f"{r['paper']:<25} {len(r['core46']):>9} {len(r['core47']):>9} "
              f"{len(r['core_intersection']):>5} {r['kappa46']:>7.3f} "
              f"{r['kappa47']:>7.3f} {xj:>7.3f}")

    # Detail per paper.
    for r in rows:
        print(f"\n=== {r['paper']} ===")
        c46 = ", ".join(r['core46']) or "(none)"
        c47 = ", ".join(r['core47']) or "(none)"
        ci = ", ".join(r['core_intersection']) or "(none)"
        o46 = ", ".join(r['core_only_46']) or "(none)"
        o47 = ", ".join(r['core_only_47']) or "(none)"
        print(f"  4.6 stable core (5/5): {c46}")
        print(f"  4.7 stable core (5/5): {c47}")
        print(f"  4.6 ∩ 4.7:              {ci}")
        print(f"  Only in 4.6 stable:     {o46}")
        print(f"  Only in 4.7 stable:     {o47}")
        print(f"  Cross-version Jaccard: "
              f"mean={r['cross_version_jaccard']['mean']:.3f} "
              f"median={r['cross_version_jaccard']['median']:.3f} "
              f"range=[{r['cross_version_jaccard']['min']:.3f}, "
              f"{r['cross_version_jaccard']['max']:.3f}]")
        c46 = r["cost46"]; c47 = r["cost47"]
        if c46["cells"] > 0 and c46["cost_usd"] > 0:
            print(f"  4.6 cost: ${c46['cost_usd']:.4f} "
                  f"({c46['cells']} cells, avg ${c46['cost_usd']/c46['cells']:.4f})")
        elif c46["cells"] > 0:
            print(f"  4.6 cost: (no envelope data — {c46['cells']} cells pre-envelope)")
        if c47["cells"] > 0:
            print(f"  4.7 cost: ${c47['cost_usd']:.4f} "
                  f"({c47['cells']} cells, avg ${c47['cost_usd']/c47['cells']:.4f}, "
                  f"avg wall {c47['wall_clock_s']/c47['cells']:.0f}s, "
                  f"in_tok {c47['input_tokens']//max(c47['cells'],1)}, "
                  f"out_tok {c47['output_tokens']//max(c47['cells'],1)})")

    # Aggregate cost summary.
    print()
    print("=" * 78)
    print("Aggregate metrics (with envelope data only):")
    for model in ("claude-opus-4-6", "claude-opus-4-7"):
        total = {"cells": 0, "cost": 0.0, "wall": 0, "in_tok": 0, "out_tok": 0,
                 "cache_read": 0}
        for p in PAPERS:
            c = cost_summary(p, model)
            total["cells"] += c["cells"]
            total["cost"] += c["cost_usd"]
            total["wall"] += c["wall_clock_s"]
            total["in_tok"] += c["input_tokens"]
            total["out_tok"] += c["output_tokens"]
            total["cache_read"] += c["cache_read"]
        if total["cells"]:
            print(f"  {model}: {total['cells']} cells, "
                  f"${total['cost']:.4f} total, ${total['cost']/total['cells']:.4f}/cell, "
                  f"{total['wall']}s wall, in={total['in_tok']} out={total['out_tok']} "
                  f"cache_read={total['cache_read']}")
        else:
            print(f"  {model}: no envelope-bearing cells yet")
    print("=" * 78)


if __name__ == "__main__":
    main()
