"""Compare adversarial vs neutral reviewer-stance Fresh sessions.

Cohort:
  - adversarial: existing 25 cells, claude-opus-4-6 (the 'adversarial'
    stance was the original cell runner's stance; relabeled to 4.6 after
    the model-label investigation).
  - neutral: new 25 cells, claude-opus-4-6, prompt_style=neutral.

For each paper, computes:
  - per-stance issue count (mean ± sd, severity distribution)
  - per-stance Fleiss kappa (n=5 runs as raters, binary section flag)
  - cross-stance Jaccard on (section, severity) fingerprints
  - stable-core (5/5) overlap between stances

Run from repo root:
    python3 experiments/src/compare_stances.py
"""
from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from analyze_multirun import (
    OUT_DIR, PAPERS, RUNS,
    normalize_section, fleiss_kappa, jaccard, issues_as_fingerprints,
)


def cell_path(paper: str, model: str, run: int, style: str) -> Path:
    if style == "adversarial":
        return OUT_DIR / f"{paper}__{model}__bare__run-{run}.json"
    return OUT_DIR / f"{paper}__{model}__bare__{style}__run-{run}.json"


def load(paper: str, model: str, run: int, style: str) -> dict | None:
    p = cell_path(paper, model, run, style)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def sections_for(d: dict, paper: str) -> set[str]:
    out: set[str] = set()
    for issue in d["response"]["issues"]:
        for s in normalize_section(issue.get("section", ""), paper_id=paper):
            out.add(s)
    return out


def stable_core(paper: str, model: str, style: str, threshold: int = 5) -> set[str]:
    freq: Counter[str] = Counter()
    n = 0
    for r in RUNS:
        d = load(paper, model, r, style)
        if d is None:
            continue
        n += 1
        for s in sections_for(d, paper):
            freq[s] += 1
    return {s for s, k in freq.items() if k >= threshold}


def per_stance_summary(paper: str, model: str, style: str) -> dict:
    runs = [(r, load(paper, model, r, style)) for r in RUNS]
    runs = [(r, d) for r, d in runs if d is not None]
    counts = [len(d["response"]["issues"]) for _, d in runs]
    sev = Counter()
    for _, d in runs:
        for issue in d["response"]["issues"]:
            sev[issue.get("severity", "unknown")] += 1
    fk = fleiss_kappa(paper, runs) if len(runs) >= 2 else {"kappa": float("nan"), "n_items": 0}
    return {
        "n_runs": len(runs),
        "issue_count_mean": statistics.mean(counts) if counts else float("nan"),
        "issue_count_stdev": statistics.stdev(counts) if len(counts) > 1 else 0.0,
        "severity": dict(sev),
        "fleiss_kappa": fk["kappa"],
        "n_items": fk["n_items"],
    }


def cross_stance_jaccard(paper: str, model: str) -> dict:
    pairs = []
    adv_data = [(r, load(paper, model, r, "adversarial")) for r in RUNS]
    neu_data = [(r, load(paper, model, r, "neutral")) for r in RUNS]
    for ra, da in adv_data:
        if da is None:
            continue
        fpa = issues_as_fingerprints(da, paper_id=paper)
        for rn, dn in neu_data:
            if dn is None:
                continue
            fpn = issues_as_fingerprints(dn, paper_id=paper)
            pairs.append({
                "adv_run": ra, "neu_run": rn,
                "jaccard": jaccard(fpa, fpn),
                "intersection": len(fpa & fpn),
                "union": len(fpa | fpn),
            })
    if pairs:
        return {
            "n_pairs": len(pairs),
            "mean": statistics.mean(p["jaccard"] for p in pairs),
            "median": statistics.median(p["jaccard"] for p in pairs),
            "min": min(p["jaccard"] for p in pairs),
            "max": max(p["jaccard"] for p in pairs),
        }
    return {"n_pairs": 0, "mean": float("nan"), "median": float("nan"),
            "min": float("nan"), "max": float("nan")}


def cost_for(paper: str, model: str, style: str) -> dict:
    total_cost = 0.0
    total_wall = 0
    total_in = 0
    total_out = 0
    n = 0
    for r in RUNS:
        d = load(paper, model, r, style)
        if d is None:
            continue
        m = d.get("metrics", {})
        u = m.get("usage", {})
        n += 1
        total_cost += m.get("total_cost_usd") or 0
        total_wall += m.get("wall_clock_s") or 0
        total_in += u.get("input_tokens") or 0
        total_out += u.get("output_tokens") or 0
    return {"cells": n, "cost": total_cost, "wall": total_wall,
            "in_tok": total_in, "out_tok": total_out}


def main() -> None:
    print("=" * 80)
    print("Adversarial vs Neutral reviewer-stance comparison (claude-opus-4-6)")
    print("=" * 80)

    model = "claude-opus-4-6"
    rows = []
    for p in PAPERS:
        adv = per_stance_summary(p, model, "adversarial")
        neu = per_stance_summary(p, model, "neutral")
        core_adv = stable_core(p, model, "adversarial")
        core_neu = stable_core(p, model, "neutral")
        cross = cross_stance_jaccard(p, model)
        rows.append({"paper": p, "adv": adv, "neu": neu,
                     "core_adv": sorted(core_adv), "core_neu": sorted(core_neu),
                     "core_intersect": sorted(core_adv & core_neu),
                     "core_only_adv": sorted(core_adv - core_neu),
                     "core_only_neu": sorted(core_neu - core_adv),
                     "cross": cross})

    print()
    print(f"{'paper':<25} {'adv issues':>15} {'neu issues':>15} "
          f"{'Δ%':>6} {'κ adv':>7} {'κ neu':>7} {'X-Jacc':>7}")
    print("-" * 80)
    for r in rows:
        a = r["adv"]; n = r["neu"]
        adv_str = f"{a['issue_count_mean']:.1f}±{a['issue_count_stdev']:.1f}"
        neu_str = f"{n['issue_count_mean']:.1f}±{n['issue_count_stdev']:.1f}"
        # FIX (code review #13): guard against divide-by-zero when the
        # adversarial cell has zero issues (all-empty runs) or no runs.
        a_mean = a['issue_count_mean']
        if a_mean and a_mean == a_mean:  # not 0, not NaN
            delta_pct = (n['issue_count_mean'] - a_mean) / a_mean * 100
            delta_str = f"{delta_pct:>+5.0f}%"
        else:
            delta_str = "  n/a"
        print(f"{r['paper']:<25} {adv_str:>15} {neu_str:>15} "
              f"{delta_str:>6} {a['fleiss_kappa']:>7.3f} "
              f"{n['fleiss_kappa']:>7.3f} {r['cross']['mean']:>7.3f}")

    # Aggregate.
    adv_means = [r["adv"]["issue_count_mean"] for r in rows]
    neu_means = [r["neu"]["issue_count_mean"] for r in rows]
    all_xj = [p_["jaccard"] for r in rows for p_ in [
        {"jaccard": j} for j in [r["cross"]["mean"]]] if not (p_["jaccard"] != p_["jaccard"])]
    print("-" * 80)
    overall_adv = statistics.mean(adv_means) if adv_means else float("nan")
    overall_neu = statistics.mean(neu_means) if neu_means else float("nan")
    # FIX (code review #14): same divide-by-zero guard at the aggregate.
    if overall_adv and overall_adv == overall_adv:
        overall_delta_str = f"{(overall_neu - overall_adv) / overall_adv * 100:>+5.0f}%"
    else:
        overall_delta_str = "  n/a"

    def _safe_mean(values):
        clean = [v for v in values if v == v]  # filter NaN
        return statistics.mean(clean) if clean else float("nan")

    print(f"{'MEAN':<25} {overall_adv:>15.2f} {overall_neu:>15.2f} "
          f"{overall_delta_str:>6} "
          f"{_safe_mean([r['adv']['fleiss_kappa'] for r in rows]):>7.3f} "
          f"{_safe_mean([r['neu']['fleiss_kappa'] for r in rows]):>7.3f} "
          f"{_safe_mean([r['cross']['mean'] for r in rows]):>7.3f}")
    print()

    # Severity totals.
    print("Severity totals (sum across 5 runs):")
    print(f"{'paper':<25} {'adv crit':>10} {'adv maj':>10} {'adv min':>10} "
          f"{'neu crit':>10} {'neu maj':>10} {'neu min':>10}")
    for r in rows:
        a = r["adv"]["severity"]; n = r["neu"]["severity"]
        print(f"  {r['paper']:<23} "
              f"{a.get('critical',0):>10} {a.get('major',0):>10} {a.get('minor',0):>10} "
              f"{n.get('critical',0):>10} {n.get('major',0):>10} {n.get('minor',0):>10}")
    print()

    # Stable-core comparison.
    print("Stable-core (5/5 runs) per stance:")
    for r in rows:
        print(f"\n  {r['paper']}:")
        print(f"    adversarial core ({len(r['core_adv'])}): {', '.join(r['core_adv']) or '(none)'}")
        print(f"    neutral core    ({len(r['core_neu'])}): {', '.join(r['core_neu']) or '(none)'}")
        print(f"    intersection    ({len(r['core_intersect'])}): {', '.join(r['core_intersect']) or '(none)'}")
        print(f"    only-adversarial({len(r['core_only_adv'])}): {', '.join(r['core_only_adv']) or '(none)'}")
        print(f"    only-neutral    ({len(r['core_only_neu'])}): {', '.join(r['core_only_neu']) or '(none)'}")
    print()

    # Cost.
    print("=" * 80)
    print("Cost / time (envelope-bearing cells only):")
    for style in ("adversarial", "neutral"):
        total = {"cells": 0, "cost": 0.0, "wall": 0, "in_tok": 0, "out_tok": 0}
        for p in PAPERS:
            c = cost_for(p, "claude-opus-4-6", style)
            for k in total:
                total[k] += c[k]
        if total["cells"]:
            print(f"  {style:<12} cells={total['cells']:>3}  cost=${total['cost']:.4f}  "
                  f"wall_sum={total['wall']}s  out={total['out_tok']}")
        else:
            print(f"  {style:<12} no envelope-bearing cells")
    print("=" * 80)


if __name__ == "__main__":
    main()
