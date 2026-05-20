"""Inter-run reliability analysis for the Study 1 multi-run replication.

For each of the 5 papers × 5 runs:
  - tabulates how often each (normalized) section is flagged
  - pairwise Jaccard similarity on section-severity fingerprints
  - identifies stable (>=4/5) vs sometimes (2-3/5) vs rare (1/5) findings
  - per-run issue count statistics

Run from repo root:
    python3 experiments/src/analyze_multirun.py
"""
from __future__ import annotations

import json
import re
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

OUT_DIR = Path("experiments/data/raw/study1-replication")
PAPERS = ["narcissus", "analogic-appropriation", "z-gap", "eddy", "ploidy"]
RUNS = list(range(1, 6))


# ---- Section normalization -------------------------------------------------
# Maps free-text section refs to a canonical short form. The agents emit
# any of:
#   - "§2.1", "Section 2.1", "S2.1 (Three-Session)", "§2.1, Table 2"
#   - LaTeX label form: "sec:three-session", "sec:evidence"
# We normalize all of these to "S2.1" by:
#   (a) Numeric extraction via regex.
#   (b) For label form, look up the canonical S-number from each paper's
#       parsed section/subsection/label structure.

_RE_SEC = re.compile(r"(?:S|§|Sec(?:tion)?\.?\s*)\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_RE_LABEL = re.compile(r"sec:([a-zA-Z0-9_\-]+)", re.IGNORECASE)


def _build_label_index() -> dict[str, dict[str, str]]:
    """For each paper, parse \\section{...}\\label{sec:foo} → S-number mapping.

    Returns: { paper_id: { "foo": "S2.1", ... } }
    """
    paper_paths = {
        "narcissus":               "/Users/ren/IdeaProjects/Paper/narcissus/paper/main.tex",
        "analogic-appropriation":  "/Users/ren/IdeaProjects/Paper/analogic-appropriation/paper/main.tex",
        "z-gap":                   "/Users/ren/IdeaProjects/Paper/z-gap/paper/main.tex",
        "eddy":                    "/Users/ren/IdeaProjects/Paper/eddy/paper/main.tex",
        "ploidy":                  "/Users/ren/IdeaProjects/Paper/ploidy/paper/main.tex",
    }
    sec_re = re.compile(
        r"\\(section|subsection|subsubsection)\*?\{[^}]*\}.*?\\label\{sec:([a-zA-Z0-9_\-]+)\}",
        re.DOTALL,
    )
    index: dict[str, dict[str, str]] = {}
    for pid, path in paper_paths.items():
        p = Path(path)
        if not p.exists():
            index[pid] = {}
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        # We walk top-to-bottom, maintaining counters for section/subsection.
        labels: dict[str, str] = {}
        sec_n = 0
        sub_n = 0
        subsub_n = 0
        token_re = re.compile(
            r"\\(section|subsection|subsubsection)\*?\{[^}]*\}"
            r"(?:\s*\\label\{sec:([a-zA-Z0-9_\-]+)\})?",
        )
        for m in token_re.finditer(text):
            level = m.group(1)
            label = m.group(2)
            if level == "section":
                sec_n += 1
                sub_n = 0
                subsub_n = 0
                canonical = f"S{sec_n}"
            elif level == "subsection":
                sub_n += 1
                subsub_n = 0
                canonical = f"S{sec_n}.{sub_n}"
            else:  # subsubsection
                subsub_n += 1
                canonical = f"S{sec_n}.{sub_n}.{subsub_n}"
            if label:
                labels[label.lower()] = canonical
        index[pid] = labels
    return index


_LABEL_INDEX = _build_label_index()


def normalize_section(raw: str, paper_id: str = "") -> tuple[str, ...]:
    """Extract a tuple of normalized section labels from a free-text ref."""
    if not raw:
        return ("(unknown)",)
    out: set[str] = set()

    # 1. Numeric extraction.
    for h in _RE_SEC.findall(raw):
        out.add(f"S{h}")

    # 2. LaTeX label form: map to canonical via per-paper index.
    label_map = _LABEL_INDEX.get(paper_id, {})
    for h in _RE_LABEL.findall(raw):
        if h.lower() in label_map:
            out.add(label_map[h.lower()])
        else:
            # Unknown label — keep verbatim so it's at least consistent.
            out.add(f"sec:{h.lower()}")

    if out:
        return tuple(sorted(out))

    # 3. Fallback for prose-style refs.
    cleaned = raw.strip().lower()
    for prefix in ("table", "abstract", "title", "introduction", "discussion",
                   "references", "limitations", "appendix", "bibliography"):
        if prefix in cleaned:
            return (prefix.capitalize(),)
    return (raw.strip()[:40],)


def load_run(paper: str, run: int) -> dict | None:
    f = OUT_DIR / f"{paper}__claude-opus-4-7__bare__run-{run}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


# ---- Per-paper analysis ----------------------------------------------------

def issues_as_fingerprints(d: dict, paper_id: str = "") -> set[tuple[str, str]]:
    """Convert a review's issues to a set of (section_key, severity) tuples."""
    out: set[tuple[str, str]] = set()
    for issue in d["response"]["issues"]:
        secs = normalize_section(issue.get("section", ""), paper_id=paper_id)
        sev = issue.get("severity", "unknown")
        # Each section in the tuple becomes its own fingerprint entry so a
        # multi-section issue counts toward every section it mentions.
        for s in secs:
            out.add((s, sev))
    return out


def section_frequency(d_list: list[dict], paper_id: str = "") -> Counter[str]:
    """How many runs flag each section at any severity?"""
    counter: Counter[str] = Counter()
    for d in d_list:
        seen = set()
        for issue in d["response"]["issues"]:
            for s in normalize_section(issue.get("section", ""), paper_id=paper_id):
                seen.add(s)
        for s in seen:
            counter[s] += 1
    return counter


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def analyze_paper(paper: str) -> dict:
    runs = []
    for r in RUNS:
        d = load_run(paper, r)
        if d is None:
            continue
        runs.append((r, d))
    counts = [len(d["response"]["issues"]) for _, d in runs]
    sev_counts = Counter()
    for _, d in runs:
        for issue in d["response"]["issues"]:
            sev_counts[issue.get("severity", "unknown")] += 1
    fingerprints = {r: issues_as_fingerprints(d, paper_id=paper) for r, d in runs}
    section_freq = section_frequency([d for _, d in runs], paper_id=paper)
    pairwise = []
    for (r1, fp1), (r2, fp2) in combinations(fingerprints.items(), 2):
        pairwise.append({"pair": (r1, r2), "jaccard": jaccard(fp1, fp2),
                          "intersection": len(fp1 & fp2), "union": len(fp1 | fp2)})
    mean_jac = statistics.mean(p["jaccard"] for p in pairwise) if pairwise else float("nan")
    return {
        "paper": paper,
        "n_runs": len(runs),
        "issue_counts": counts,
        "issue_count_mean": statistics.mean(counts) if counts else float("nan"),
        "issue_count_stdev": statistics.stdev(counts) if len(counts) > 1 else 0.0,
        "severity_total": dict(sev_counts),
        "section_frequency": dict(section_freq),
        "pairwise_jaccard_mean": mean_jac,
        "pairwise_jaccard_per_pair": pairwise,
    }


def stability_bucket(freq: int, n_runs: int) -> str:
    if freq == n_runs:
        return "stable (all runs)"
    if freq >= n_runs - 1:
        return "near-stable"
    if freq >= n_runs // 2 + 1:
        return "sometimes"
    return "rare"


# ---- Report ----------------------------------------------------------------

def main() -> None:
    results = [analyze_paper(p) for p in PAPERS]

    print("=" * 72)
    print("Study 1 multi-run reliability analysis")
    print("=" * 72)
    print()
    print(f"{'paper':<25} {'n':>3} {'issues mean ± sd':<20} {'pairwise Jacc':>14}")
    print("-" * 72)
    for r in results:
        sd_str = f"{r['issue_count_stdev']:.2f}" if r["n_runs"] > 1 else "—"
        print(f"{r['paper']:<25} {r['n_runs']:>3} "
              f"{r['issue_count_mean']:>5.1f} ± {sd_str:<10} "
              f"{r['pairwise_jaccard_mean']:>14.3f}")
    print()

    # Severity distribution per paper.
    print("Severity totals across runs:")
    print(f"{'paper':<25} {'critical':>10} {'major':>10} {'minor':>10}")
    for r in results:
        sev = r["severity_total"]
        print(f"  {r['paper']:<23} {sev.get('critical',0):>10} "
              f"{sev.get('major',0):>10} {sev.get('minor',0):>10}")
    print()

    # Section stability per paper.
    print("Section stability (sections flagged in K-of-N runs):")
    for r in results:
        n = r["n_runs"]
        freq = r["section_frequency"]
        buckets: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for sec, k in sorted(freq.items(), key=lambda x: (-x[1], x[0])):
            buckets[stability_bucket(k, n)].append((sec, k))
        print(f"\n  {r['paper']}:")
        for bucket in ("stable (all runs)", "near-stable", "sometimes", "rare"):
            items = buckets.get(bucket, [])
            if not items:
                continue
            label = f"    {bucket} ({len(items)}):"
            secs = ", ".join(f"{s}={k}/{n}" for s, k in items[:10])
            if len(items) > 10:
                secs += f", … (+{len(items)-10} more)"
            print(f"{label} {secs}")
    print()

    # Pairwise detail per paper.
    print("Pairwise Jaccard detail (intersect / union per run pair):")
    for r in results:
        print(f"\n  {r['paper']}:")
        for p in r["pairwise_jaccard_per_pair"]:
            print(f"    runs {p['pair'][0]}↔{p['pair'][1]}: J={p['jaccard']:.3f} "
                  f"({p['intersection']}/{p['union']})")
    print()

    # Aggregate.
    all_jac = [p["jaccard"] for r in results for p in r["pairwise_jaccard_per_pair"]]
    all_counts = [c for r in results for c in r["issue_counts"]]
    print("=" * 72)
    print(f"Aggregate (all 5 papers, 10 pairs each = 50 pairs):")
    print(f"  Mean pairwise Jaccard:   {statistics.mean(all_jac):.3f}")
    print(f"  Median pairwise Jaccard: {statistics.median(all_jac):.3f}")
    print(f"  Min / Max:               {min(all_jac):.3f} / {max(all_jac):.3f}")
    print(f"  Mean issues per cell:    {statistics.mean(all_counts):.2f}")
    print(f"  Total issues (25 cells): {sum(all_counts)}")
    print("=" * 72)


if __name__ == "__main__":
    main()
