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

# FIX (code review): require a word boundary before lone 'S' to prevent
# false-matches like 'NASA 5' -> 'S5' or 'IS 3' -> 'S3'. § and 'Sec[tion]'
# are unambiguous on their own.
_RE_SEC = re.compile(
    r"(?:\bS|§|\bSec(?:tion)?\.?\s*)\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
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
        # FIX (code review #11): capture the * (starred) marker so we can
        # skip numbering for unnumbered sections like \section*{Acknowledgments}.
        # Previously sec_n was incremented for starred sections, corrupting
        # all subsequent canonical S-numbers in the label map.
        token_re = re.compile(
            r"\\(section|subsection|subsubsection)(\*?)\{[^}]*\}"
            r"(?:\s*\\label\{sec:([a-zA-Z0-9_\-]+)\})?",
        )
        for m in token_re.finditer(text):
            level = m.group(1)
            starred = m.group(2) == "*"
            label = m.group(3)
            if starred:
                # Starred sections are unnumbered in LaTeX; don't bump counters.
                # If a label is on a starred section, we still record it but
                # under a sec:<label> form (no canonical S-number exists).
                if label:
                    labels[label.lower()] = f"sec:{label.lower()}"
                continue
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


# FIX (code review #4): model/stance/context are no longer hardcoded.
# The default is the highest-N model+stance+context available on disk for
# the legacy use case (was claude-opus-4-7 adversarial fresh). Callers can
# override.
DEFAULT_MODEL = "claude-opus-4-7"
DEFAULT_STYLE = "adversarial"
DEFAULT_CONTEXT = "fresh"


def _cell_filename(paper: str, model: str, run: int,
                   style: str = DEFAULT_STYLE,
                   context: str = DEFAULT_CONTEXT) -> str:
    """Reconstruct the canonical cell filename for the given identifiers."""
    tag = "bare"
    if style != "adversarial":
        tag = f"{tag}__{style}"
    if context != "fresh":
        tag = f"{tag}__{context}"
    return f"{paper}__{model}__{tag}__run-{run}.json"


def load_run(paper: str, run: int,
             model: str = DEFAULT_MODEL,
             style: str = DEFAULT_STYLE,
             context: str = DEFAULT_CONTEXT) -> dict | None:
    f = OUT_DIR / _cell_filename(paper, model, run, style, context)
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


def fleiss_kappa(paper_id: str, runs_data: list[tuple[int, dict]]) -> dict:
    """Fleiss' kappa across n runs treated as raters, each binary-rating
    whether each unioned section is flagged.

    For binary categories with N raters and n items:
      P_i  = proportion-of-agreement for item i across raters
      P_bar = mean of P_i over items
      Pe_bar = sum_j p_j^2 where p_j is overall proportion in category j
      kappa = (P_bar - Pe_bar) / (1 - Pe_bar)

    Returns dict with kappa, n_items, n_raters, and per-paper diagnostics.
    """
    # Item universe: union of all normalized sections across runs.
    universe: set[str] = set()
    flag_matrix: list[dict[int, bool]] = []  # row per item, col per run
    runs = sorted(runs_data, key=lambda x: x[0])
    n_raters = len(runs)
    if n_raters < 2:
        return {"kappa": float("nan"), "n_items": 0, "n_raters": n_raters,
                "reason": "need >= 2 raters"}
    # First pass: gather union of sections.
    run_sections: dict[int, set[str]] = {}
    for r, d in runs:
        secs: set[str] = set()
        for issue in d["response"]["issues"]:
            for s in normalize_section(issue.get("section", ""), paper_id=paper_id):
                secs.add(s)
        run_sections[r] = secs
        universe |= secs
    universe_list = sorted(universe)
    n_items = len(universe_list)
    if n_items == 0:
        return {"kappa": float("nan"), "n_items": 0, "n_raters": n_raters,
                "reason": "no flagged sections"}

    # Per-item agreement.
    p_i: list[float] = []
    cat_totals = {"flag": 0, "noflag": 0}
    for sec in universe_list:
        n_flag = sum(1 for r, _ in runs if sec in run_sections[r])
        n_noflag = n_raters - n_flag
        # P_i for binary: [n_flag*(n_flag-1) + n_noflag*(n_noflag-1)] / [N*(N-1)]
        agree = (n_flag * (n_flag - 1) + n_noflag * (n_noflag - 1)) / (
            n_raters * (n_raters - 1)
        )
        p_i.append(agree)
        cat_totals["flag"] += n_flag
        cat_totals["noflag"] += n_noflag

    p_bar = sum(p_i) / n_items
    total = cat_totals["flag"] + cat_totals["noflag"]
    p_flag = cat_totals["flag"] / total
    p_noflag = cat_totals["noflag"] / total
    pe_bar = p_flag * p_flag + p_noflag * p_noflag
    if abs(1 - pe_bar) < 1e-9:
        kappa = float("nan")
    else:
        kappa = (p_bar - pe_bar) / (1 - pe_bar)
    return {
        "kappa": kappa,
        "n_items": n_items,
        "n_raters": n_raters,
        "p_bar": p_bar,
        "pe_bar": pe_bar,
        "p_flag_overall": p_flag,
        "n_stable_5of5": sum(1 for sec in universe_list
                              if sum(1 for r, _ in runs if sec in run_sections[r]) == n_raters),
    }


# ---- Per-cell metrics (timing + size) --------------------------------------

def cell_metrics(paper: str) -> list[dict]:
    """Per-cell timing + size proxies (no token counts — claude --print used
    plain text mode; future runs will use --output-format json for exact)."""
    paper_paths = {
        "narcissus":               "/Users/ren/IdeaProjects/Paper/narcissus/paper/main.tex",
        "analogic-appropriation":  "/Users/ren/IdeaProjects/Paper/analogic-appropriation/paper/main.tex",
        "z-gap":                   "/Users/ren/IdeaProjects/Paper/z-gap/paper/main.tex",
        "eddy":                    "/Users/ren/IdeaProjects/Paper/eddy/paper/main.tex",
        "ploidy":                  "/Users/ren/IdeaProjects/Paper/ploidy/paper/main.tex",
    }
    rows = []
    src = Path(paper_paths.get(paper, ""))
    manuscript_chars = src.stat().st_size if src.exists() else 0
    manuscript_lines = len(src.read_text(encoding="utf-8", errors="ignore").splitlines()) if src.exists() else 0
    for r in RUNS:
        d = load_run(paper, r)
        if d is None:
            continue
        # FIX (code review #4): use the same filename-builder load_run uses,
        # so cell_metrics stays in sync if the default model/style/context
        # changes.
        cell_file = OUT_DIR / _cell_filename(paper, DEFAULT_MODEL, r)
        out_chars = cell_file.stat().st_size
        # Approximate response chars from issues + summary.
        resp = d["response"]
        response_chars = (
            len(resp.get("summary", ""))
            + sum(len(i.get("description", "")) + len(i.get("counter_evidence") or "")
                  for i in resp["issues"])
        )
        # run_at_utc from cell JSON; mtime from filesystem.
        rows.append({
            "paper": paper,
            "run": r,
            "manuscript_chars": manuscript_chars,
            "manuscript_lines": manuscript_lines,
            "response_chars": response_chars,
            "issue_count": len(resp["issues"]),
            "run_at_utc": d.get("run_at_utc", ""),
            "approx_input_tokens": manuscript_chars // 4,  # rough 4 chars/token
            "approx_output_tokens": response_chars // 4,
        })
    return rows


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
    print()

    # ---- Fleiss' kappa per paper -------------------------------------------
    print("Fleiss' kappa across 5 runs as raters (binary: section flagged?):")
    print(f"  {'paper':<25} {'n_items':>8} {'kappa':>8} {'P_bar':>8} {'Pe_bar':>8}")
    kappas = []
    for p in PAPERS:
        runs = [(r, load_run(p, r)) for r in RUNS]
        runs = [(r, d) for r, d in runs if d is not None]
        fk = fleiss_kappa(p, runs)
        kappas.append(fk["kappa"])
        if fk["kappa"] == fk["kappa"]:  # not nan
            print(f"  {p:<25} {fk['n_items']:>8} {fk['kappa']:>8.3f} "
                  f"{fk['p_bar']:>8.3f} {fk['pe_bar']:>8.3f}")
        else:
            print(f"  {p:<25} (kappa undefined: {fk.get('reason','')})")
    valid_kappas = [k for k in kappas if k == k]
    if valid_kappas:
        print(f"  {'mean across papers':<25} {'':>8} {statistics.mean(valid_kappas):>8.3f}")
    print()

    # ---- Per-cell metrics --------------------------------------------------
    import csv
    metrics_out = Path("experiments/data/raw/study1-replication/multirun-metrics.csv")
    rows = [m for p in PAPERS for m in cell_metrics(p)]
    metrics_out.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        # FIX (code review #12): rows[0].keys() raised IndexError when
        # cell_metrics returned [] for every paper (the common case for
        # 4.6-only datasets before the load_run hardcode was fixed).
        print(f"Per-cell metrics → {metrics_out} skipped (no envelope-bearing cells found for model={DEFAULT_MODEL} style={DEFAULT_STYLE} context={DEFAULT_CONTEXT})")
    else:
        with metrics_out.open("w", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for row in rows:
                w.writerow(row)
        print(f"Per-cell metrics → {metrics_out} ({len(rows)} rows)")
    print()
    print("Per-paper rough size summary (manuscript_chars / mean response_chars):")
    by_paper = defaultdict(list)
    for r in rows:
        by_paper[r["paper"]].append(r)
    for p, rs in by_paper.items():
        mc = rs[0]["manuscript_chars"]
        mlines = rs[0]["manuscript_lines"]
        rc_mean = statistics.mean(r["response_chars"] for r in rs)
        rc_sd = statistics.stdev(r["response_chars"] for r in rs) if len(rs) > 1 else 0
        in_tok = mc // 4
        out_tok = int(rc_mean // 4)
        print(f"  {p:<25} manuscript {mc:>6} chars / {mlines:>4} lines "
              f"(~{in_tok:>5} in_tok)   response mean {rc_mean:>6.0f} ± "
              f"{rc_sd:>5.0f} chars (~{out_tok:>4} out_tok)")


if __name__ == "__main__":
    main()
