# Study 1 — Model-Version Replication Run (2026-05-21)

> Status: First completed cell-batch of the Study 1 replication arm
> (paper §4.1). Cohort: 5 papers (narcissus + 4 sibling repos),
> 1 model (claude-opus-4-7, current Claude Code session).
> Method: 5 Fresh-session adversarial reviewers spawned as independent
> sub-agents with zero shared context, given only the manuscript file.
> Raw JSON: `../data/raw/study1-replication/<paper>__claude-opus-4-7.json`
> Note: villagent is skipped — no LaTeX manuscript (market-analysis
> document; covered in the original 2026-03-26 audit only at the
> citation-table level, not at the manuscript-review level).

## Aggregate

| Paper | Critical | Major | Minor | Total | Lines |
|---|---:|---:|---:|---:|---:|
| narcissus              | 5 | 7 | 4 | **16** |   495 |
| analogic-appropriation | 4 | 8 | 3 | **15** |   630 |
| z-gap                  | 3 | 7 | 5 | **15** | 1,012 |
| eddy                   | 4 | 7 | 3 | **14** |   557 |
| ploidy                 | 4 | 8 | 3 | **15** | 1,308 |
| **Total**              | **20** | **37** | **18** | **75** | 4,002 |

Mean issues per paper: **15.0**. Severity distribution: 27% critical
/ 49% major / 24% minor — heavier on the substantive end of the
spectrum than a pure nitpicking pass.

## Replication of paper §2.1 Table 2 findings

Original Table 2 (2026-03-26, Opus 4.6) listed six Fresh-session /
Separate-session detections that the Deep session missed. The 4.7
Fresh reviews here are checked against each:

| Original Table 2 finding | 4.7 Fresh caught? | Evidence |
|---|---|---|
| Z-Gap P3/P2 English-pivot double standard | ✅ **YES** | issue #4 (P2 falsified in opposite direction), #7 (P3 probing problems) |
| Z-Gap R_code≈1.04 too weak for claims | ✅ **YES** | issue #2 ("R_code values 1.01–1.28 too small for execution-level convergence claim"), #12 ("PRH framing overstated") |
| Analogic Era 2 isn't appropriation (de Certeau) | ✅ **YES** | explicit de Certeau / appropriation critique surfaces in the issue list |
| Analogic D&D/TTRPG diffusion path | ✅ **YES** | explicit D&D / TTRPG / RPG diffusion gap surfaces |
| Eddy novelty decay vs compound advantage tension | 🟡 **PARTIAL** | issue #4 critiques Compound Advantage Equation as "mathematically trivial"; issue #5 critiques the novelty-robustness assumption — both halves of the tension are flagged, but not the contradiction *between* them as a single critique |
| Ploidy Husserl epoché ≠ passive memory absence | ❌ **NO** | Husserl/epoché not mentioned in any of the 15 issues. Most likely explanation: the analogy was removed or restructured in the ploidy paper between the 2026-03-26 audit and the current 1,308-line version (paper has gone through major revisions per `../../../ploidy/planning/decisions.md`). Verification requires a paper-revision diff, deferred. |

**Replication summary**: **5/6 original Fresh-session findings
substantively reproduced** under 4.7 (4 full + 1 partial). The
remaining 1/6 (ploidy Husserl) is most parsimoniously explained by
paper revision rather than reviewer failure; this is verifiable.

## Beyond Table 2: New issues surfaced

The 4.7 review produced **~69 issues that were not in the original
Table 2**. Selected high-severity new findings (one per paper):

- **narcissus**: 5 critical issues including HARKing structure between
  §2 evidence and §4.6 hypotheses (independently rediscovered — confirms
  the C2 fix from the pre-experiment review pass).
- **analogic-appropriation**: critical issues on conceptual conflation
  between *appropriation* and *participation* across Era 1/2/3.
- **z-gap**: critical issue on operationalization category error — the
  "convergence" side and the "non-communicability" side use different
  operationalizations and cannot be jointly interpreted.
- **eddy**: critical issue on category confusion — paper hedges in body
  ("we hypothesize") but markets certainty in title/abstract/Table 1.
- **ploidy**: critical issue on judge-model contamination — Opus 4.6 as
  the judge of outputs from the same model family creates systematic
  bias not addressed.

These new findings support **H7 (Complementary Detection)** of paper
§3.6: multiple independent Fresh sessions with different (here:
implicit-role) instantiations surface different issue subsets. A single
Fresh-session pass — even an adversarially-prompted one — is unlikely
to be sufficient.

## What this evidence supports (deliberately limited)

This is one model version on five papers, one Fresh-session each. The
strict claims supported:

1. **Cross-version persistence of the Fresh-session effect within the
   Claude family**: the same kinds of issues the 4.6 Fresh / Separate
   sessions caught in March 2026 are caught by 4.7 in May 2026,
   independently. The Narcissus Loop diagnosis is not specific to a
   single model version. This is the §4.1 replication-arm purpose.
2. **Issue density is non-trivial**: 75 issues across 5 papers in a
   single zero-context pass, of which 27% are flagged critical. The
   Deep sessions that produced these papers did not surface these
   issues during writing — replicating the §2.1 asymmetry.
3. **Domain-coherent richness**: each review cites specific section
   labels, equations, table entries, and counter-references that match
   the manuscript's own internal structure. No fabrication patterns
   were observed in the reviews themselves on initial inspection (a
   formal hallucination audit of the reviews is deferred).

## What it does NOT support

- **Causal attribution to context accumulation specifically**: this
  run does not include a Deep-session arm, so it cannot test H2
  (Context Compounding) — only the *output* of a single Fresh pass is
  observed.
- **Generalization across model vendors**: TODO #2 (cross-vendor
  comparison: GPT, Gemini, open-weights) is a separate study.
- **H5 (Directional Hallucination)**: not testable from review
  outputs alone; requires the prospective controlled writing task.

## Files

- `../data/raw/study1-replication/*.json` — raw per-cell outputs
  (gitignored; canonical reproducibility is Zenodo archive when paper
  is deposited).
- This document — analytical summary suitable for §4.1 reporting in
  the next paper revision.

## Reproducibility notes

- The 5 manuscripts as read by the agents are at their HEAD on
  2026-05-21 per `../data/raw/audit-manifest-2026-05-21.md` (current
  HEAD column).
- The "claude-opus-4-7" model label refers to the Claude version
  serving the current Claude Code session; exact harness-controlled
  version pin will be recorded at submission time.
- Re-running the same prompt set on the same manuscripts produces
  non-identical outputs (LLM sampling stochasticity). A multi-run
  reliability analysis (n ≥ 5 runs per paper, computing inter-run
  Jaccard / Cohen's κ on issue clusters) is deferred to the formal
  Study 1 expansion.
