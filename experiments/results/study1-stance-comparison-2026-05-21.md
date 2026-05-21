# Study 1 — Adversarial vs Neutral Reviewer Stance (2026-05-21)

> Status: Direct empirical test of the C3 confound caveat the pre-experiment
> review pass added to paper §2.1 (the Three-Session natural experiment's
> Fresh-agent condition used explicit adversarial-reviewer instruction,
> which co-varies with context depth and cannot be isolated by the
> §2 data alone). 25 new cells were generated 2026-05-21 with an
> otherwise-identical Fresh-session pipeline but a neutral reviewer
> prompt; compared against the 25 adversarial cells already on disk
> from the previous multirun.
> Cohort: 5 papers × 1 model (claude-opus-4-6) × 2 stances × 5 runs = 50 cells.
> Raw cells: `../data/raw/study1-replication/<paper>__claude-opus-4-6__bare[__neutral]__run-{1..5}.json`.

## Headline numbers

| Paper | adv issues | neu issues | Δ% | κ adv | κ neu | Cross-stance Jaccard |
|---|---:|---:|---:|---:|---:|---:|
| narcissus              | 13.2 ± 0.4 | 11.6 ± 1.1 | −12% | 0.467 | 0.253 | 0.292 |
| analogic-appropriation | 13.0 ± 1.0 | 11.0 ± 1.0 | −15% | 0.436 | 0.323 | 0.286 |
| z-gap                  | 13.2 ± 0.4 | 13.0 ± 1.0 |  −2% | 0.242 | 0.175 | 0.305 |
| eddy                   | 13.0 ± 0.7 | 11.4 ± 0.5 | −12% | 0.182 | 0.048 | 0.256 |
| ploidy                 | 13.4 ± 0.9 | 15.8 ± 0.8 | **+18%** | 0.053 | 0.175 | 0.196 |
| **Mean** | **13.16** | **12.56** | **−5%** | **0.276** | **0.195** | **0.267** |

## The principal finding

**Adversarial framing does not fabricate critiques — it re-grades them.**
Total per-cell issue count is essentially unchanged (−5% mean across
papers, well within run-to-run variance). What changes is the *severity
distribution*:

| Severity | Adversarial (sum) | Neutral (sum) | Δ |
|---|---:|---:|---:|
| Critical | 62 | 38 | **−39%** |
| Major    | 173 | 147 | −15% |
| Minor    | 94 | 129 | **+37%** |

A roughly equivalent set of structural concerns surfaces in both
stances; under neutral framing, many of the same concerns are reported
as *minor* rather than *critical* or *major*. The adversarial prompt
does not invent issues. It elevates their stated weight.

This is good news for the §2.1 Table 2 argument and bad news for the
absolute-severity claims any single-stance audit produces.

## What this means for §2.1 (C3 confound)

The pre-experiment review pass added a C3 caveat to §2.1: *the Fresh
Agents' adversarial instruction in particular is a confound that cannot
be attributed to context depth alone.* The §2.1 framing was therefore
hedged.

This stance-comparison data lets us tighten the caveat:

- **What the adversarial framing IS doing**: inflating the severity
  weight of detected concerns. A critique that would be reported as
  *minor* by a neutral reviewer is escalated to *critical* or *major*
  by an adversarial reviewer. This is a real prompt-driven effect and
  should be acknowledged.
- **What the adversarial framing is NOT doing**: causing the
  detection of structural concerns the neutral reviewer misses. The
  stable-core overlap is high: neutral cores are mostly a subset of
  adversarial cores (e.g., narcissus 4/4 overlap, analogic 4/5,
  eddy 2/2, z-gap 2/3, ploidy 2/5; sum across 5 papers: 14 overlapping
  stable cores out of 19 total in either stance).
- **Implication**: the §2.1 Table 2 detection of "6 issues missed by
  Deep" is robust to stance — those concerns are structural and would
  have been surfaced by a Fresh reviewer regardless of prompt-stance.
  What is NOT robust is the *severity tier* assigned to each issue in
  the audit.

The clean rewriting for §2.1 is: the adversarial-framing confound
affects severity grading, not detection coverage; absolute severity
labels in §2 should be reported as stance-dependent, but the
*existence* of structural concerns at the flagged sections is robust.

## Why ploidy goes the other way (issue count +18% under neutral)

The 1,308-line ploidy manuscript is the longest in the cohort and the
adversarial reviewer in our prior runs tended to consolidate critique
into fewer broader-scope issues; the neutral reviewer reports more
fine-grained concerns. ploidy is also the only paper where neutral κ
(0.175) exceeds adversarial κ (0.053) — under adversarial framing the
model wanders more across the large attack surface; under neutral it
attends more to the explicit "report only what you would flag in real
peer review" instruction.

## Cross-stance Jaccard vs. cross-version Jaccard

The mean cross-stance Jaccard (0.267) is essentially equivalent to the
mean cross-version Jaccard (0.269) we reported in the 4.6 vs 4.7
analysis. That is, *swapping the reviewer stance changes the resulting
fingerprint about as much as swapping the model version*. Both effects
are dwarfed by run-to-run stochasticity (within-version, within-stance
Jaccard is 0.348).

Interpretation: stance and model-version are both real but secondary
sources of variability; run-to-run sampling noise is the dominant
factor. The Narcissus Loop diagnosis must rely on the *intersection*
of multiple runs / stances / versions, not on any single audit's
specific output.

## Cost transparency

- Neutral 4.6 batch (this run): **$7.7089** for 25 cells, $0.31/cell
  average, 3,244 s wall-sum (~13 min in 5-way parallel, no quota wall
  in current window).
- Adversarial 4.6 batch (previous, pre-envelope): no per-cell metrics
  captured; estimated $8–12 at 4.6 prices.
- Adversarial 4.7 batch (previous): $28.52 for 25 cells, $1.14/cell.

Per-cell, 4.6-neutral is **~3.7× cheaper than 4.7-adversarial** for
substantially the same scientific information about which sections are
structurally critique-magnets in each paper.

## What this evidence supports / does not support

**Supports**:
- §2.1 detection results are robust to the adversarial-framing confound:
  the *what is flagged* signal does not depend on prompt-stance.
- The Narcissus Loop's diagnosis is stable across one of the two largest
  identified confounds (the other being model-architecture, addressed
  by the 4.6 vs 4.7 cross-version analysis).

**Does NOT support**:
- Absolute severity-tier claims in §2 (e.g., "critical problems missed
  by Deep") are stance-dependent and should be reported as such.
- This run does not eliminate the broader confound bundle in §2.1
  (role × context-depth × prompt × timing): only the adversarial-vs-
  neutral *prompt* dimension is isolated here.

## Files

- `../data/raw/study1-replication/<paper>__claude-opus-4-6__bare__neutral__run-{1..5}.json`
  — 25 neutral cells with envelope metrics.
- This document — analytical summary.
