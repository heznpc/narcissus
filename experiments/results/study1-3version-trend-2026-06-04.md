# Study 1 — 3-Point Version Trend: Opus 4.6 / 4.7 / 4.8 (2026-06-04)

> Status: Extends the 2-point (4.6 vs 4.7) cross-version replication to a
> 3-point trend by adding a Claude Opus 4.8 Fresh×Adversarial arm
> (released ~2026-06; verified routable, all 25 cells served
> model_actual=claude-opus-4-8). 25 cells, $39.63, 328 issues.
> Cohort: 5 papers × 3 versions × 5 runs (n=5 balanced) = 75 cells,
> all Fresh × Adversarial, Opus 4.6 / 4.7 / 4.8.
> Analysis: experiments/src/compare_3version_trend.py

## The question a 2-point comparison could not answer

With only 4.6 and 4.7, we could not distinguish "model-architecture-
stable" from "4.6 and 4.7 happen to be similar." A third point tests
whether cross-version agreement decays with version distance.

## Headline result — NOT the clean "stable" story

Adding 4.8 **complicates** the stability claim rather than cleanly
confirming it. Three findings, reported in order of confidence.

### Finding 1 — No version-specific DRIFT (ceiling effect)

Section-only cross-version Jaccard (severity stripped, the style-robust
metric):

| pair | section-only Jaccard |
|---|---:|
| 4.6 ↔ 4.7 | 0.443 |
| 4.6 ↔ 4.8 | 0.283 |
| 4.7 ↔ 4.8 | 0.297 |

The 4.6↔4.8 agreement (0.283) is **essentially equal to 4.8's own
within-version self-agreement** (0.277, below). A model cannot agree
with another version more than it agrees with itself, so the apparent
"decay" with version distance is a ceiling effect, not systematic
drift. **There is no evidence that 4.8 flags systematically different
sections than 4.6** — it just agrees with everything (including itself)
less.

### Finding 2 — 4.8 is a markedly HIGHER-VARIANCE reviewer

Section-only within-version Jaccard (how consistently a version flags
the same sections across its own 5 runs):

| version | section-only within-version Jaccard | Fleiss κ (section,severity) |
|---|---:|---:|
| 4.6 | 0.579 | 0.286 |
| 4.7 | 0.459 | 0.207 |
| 4.8 | **0.277** | **0.028** |

Monotonic decline. 4.8's run-to-run consistency in *which sections it
critiques* is roughly half of 4.6's. Each individual 4.8 review is
substantively normal (12–14 issues/cell, same as 4.6), but the *set*
of sections it chooses to dwell on is far more run-dependent.

**Partial confound (cannot be fully separated):** 4.8 uses more prose-
style, comparative, and multi-section references (1.39 sections/issue
vs 4.6's 1.14) and more non-section refs ("Whole paper", "Manuscript-
wide", "H5"). The section normalizer handles these less cleanly,
inflating 4.8's section universe and depressing its Jaccard/κ. The
distinct-sections-per-run count is comparable across versions (4.6:
11.3, 4.7: 13.0, 4.8: 12.2), so universe inflation is modest — we
estimate the style artifact accounts for perhaps 0.05–0.10 of the
~0.30 Jaccard gap, leaving most of the variance increase as real. A
clean separation would require manual re-coding of every section
reference (deferred).

### Finding 3 — Structural magnets survive, but fewer reach unanimity

3-way stable-core (sections flagged by ALL 5 runs of ALL 3 versions):

| paper | core 4.6 | core 4.7 | core 4.8 | 4.6∩4.7∩4.8 |
|---|---:|---:|---:|---:|
| narcissus | 8 | 4 | 5 | **3** |
| analogic-appropriation | 8 | 7 | 0 | 0 |
| z-gap | 3 | 1 | 1 | 1 |
| eddy | 6 | 6 | 0 | 0 |
| ploidy | 3 | 5 | 1 | 1 |

For the best-structured papers (narcissus), a hard core of 3 sections
is flagged unanimously by all 15 runs across all 3 versions — these are
the genuine structural critique magnets (narcissus §2.1, §2.2, §3-area
on inspection). For analogic and eddy, 4.8's higher variance means NO
section reaches 5/5 within 4.8, collapsing the triple-overlap to 0 —
this is a consequence of Finding 2 (4.8 self-inconsistency), not of
those critiques disappearing (they still appear in 3–4 of 5 runs).

## Reconciliation with the prior 2-point claim

The 2026-05-21 cross-version doc (4.6 vs 4.7) reported cross-version
Jaccard ≈ within-version Jaccard (gap ~0.08) and concluded "mostly
model-architecture-stable, run-to-run noise dominates." The 3-point
data **revises** this:

- The "gap is small" observation still holds (cross-version ≈ the
  noisier version's within-version), and correctly implies no
  systematic drift.
- BUT the prior framing under-stated that the *reliability itself*
  declines with version. At n=5, a single 4.8 review is a much noisier
  instrument than a single 4.6 review. "Stable diagnosis, declining
  single-pass reliability" is the accurate summary, not "stable."

## Implications for the paper

1. **§4.1 model-version arm must be reframed.** Not "the diagnosis is
   model-version stable" (too clean) but: "the *central tendency* (which
   sections are unanimously flagged) shows no systematic cross-version
   drift, but single-pass *reliability* declines monotonically from 4.6
   to 4.8, so newer models require MORE runs to reach the same
   aggregate coverage."

2. **H7 (Complementary Detection) is reinforced.** If newer models are
   higher-variance single-pass reviewers, the case for multi-run /
   multi-session aggregation gets stronger over time, not weaker.

3. **New §6 measurement-validity limitation.** Section-overlap metrics
   (κ, Jaccard, stable-core) — used throughout Study 1 and the original
   2026-03-26 audit — are sensitive to model-version section-citation
   *style*. Cross-version metric comparison is partially confounded by
   citation granularity and is not fully version-neutral without manual
   re-coding. This is itself an instance of the paper's broader thesis:
   the measuring instrument (the model) shapes the measurement.

4. **Reflexivity note retained.** This analysis was run and interpreted
   on Opus 4.8 — the highest-variance version in the cohort. The cells
   are model-pinned subprocesses (data unaffected), but the
   interpretation layer is 4.8, and 4.8 is the version this doc reports
   as least self-consistent. We report the inconvenient result rather
   than the cleaner "stable" story precisely because the paper's thesis
   predicts the pull toward the latter.

## Cost / integrity

| version | cells | cost | $/cell | model_actual integrity |
|---|---:|---:|---:|---|
| 4.6 Fresh×Adv (n=5 subset) | 25 | (pre/post-envelope) | ~$0.29 | n/a |
| 4.7 Fresh×Adv | 25 | $28.52 | $1.14 | all 4.7 |
| 4.8 Fresh×Adv | 25 | $39.63 | $1.59 | **all 25 = claude-opus-4-8** |

4.8 is ~40% more expensive per cell than 4.7 (~$1.59 vs $1.14), driven
by higher output-token volume. The exit-8 model-mismatch guard (added
in the pre-4.8 design review) confirmed all 25 cells were genuinely
served by 4.8 — no silent fallback / mislabeling.

## Files

- `../data/raw/study1-replication/<paper>__claude-opus-4-8__bare__run-{1..5}.json` — 25 cells.
- `../src/compare_3version_trend.py` — analysis.
- This document.
