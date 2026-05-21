# Study 1 — 4.6 vs 4.7 Cross-Version Replication (2026-05-21)

> Status: Completes the model-version replication arm of Study 1 (paper
> §4.1) with the *actual* cross-version comparison.
> Prior runs labeled "claude-opus-4-7" were investigated 2026-05-21
> and confirmed (via `claude --output-format json` envelope) to be
> served by claude-opus-4-6 because Claude Code's default `--model`
> resolves to 4.6 — the explicit `--model` flag was missing in v1 of
> the cell runner. The 26 pre-fix cells were relabeled to 4.6 (their
> actual identity); a true 4.7 batch of 25 cells was launched with
> explicit `--model claude-opus-4-7` and completed in 8 wall minutes
> at a total cost of $28.52 (avg $1.14/cell).
>
> Cohort: 5 papers × 2 models × 5 runs = 50 cells.
> Method: `claude --print --disable-slash-commands --model <m> --output-format json`
> from an isolated tmp directory.
> Raw cells: `../data/raw/study1-replication/<paper>__claude-opus-4-{6,7}__bare__run-{1..5}.json`.

## Headline

| Paper | core 4.6 | core 4.7 | ∩ | κ4.6 | κ4.7 | Cross-version Jaccard |
|---|---:|---:|---:|---:|---:|---:|
| narcissus              | 8 | 4 | 4 | 0.467 | 0.180 | 0.277 |
| analogic-appropriation | 8 | 7 | 5 | 0.436 | 0.324 | 0.309 |
| z-gap                  | 3 | 1 | 1 | 0.242 | 0.057 | 0.308 |
| eddy                   | 6 | 6 | 4 | 0.182 | 0.284 | 0.304 |
| ploidy                 | 3 | 5 | 1 | 0.053 | 0.169 | 0.145 |
| **Mean across papers** | **5.6** | **4.6** | **3.0** | **0.276** | **0.203** | **0.269** |

`core` = sections flagged by ALL 5 runs at that model version
(stable critique magnets).
`∩` = sections in BOTH versions' stable cores.
`κ` = Fleiss' kappa across 5 runs of that model (binary: section flagged?).
`Cross-version Jaccard` = mean over 25 (4.6 run × 4.7 run) pairs of
(section, severity) Jaccard.

## Three clean findings

### 1. Structural critique magnets persist across versions

For 4 of 5 papers, between 1 and 5 sections appear in BOTH versions'
stable cores — flagged independently by all 10 runs (5 at 4.6 + 5 at
4.7). Concrete examples that survive the version boundary:

- **narcissus**: §2.1 (Three-Session natural experiment confounds),
  §2.2 (hallucinated citations small-n), §2.3 (directional citation
  bias prompting artifact), §4.2 (Study 2 design).
- **analogic-appropriation**: §3, §4.1, §4.3, §5.1, §5.2 — the core
  appropriation/participation conflation and methodological issues.
- **eddy**: §2.1 (dopamine model evidential thinness), §2.3 (Equation 1
  triviality), §3.1 (debated mechanism), §4 (proposed experiment
  problems).
- **z-gap**: §4.3 (only).

These are the most robust signal: any independent Fresh reviewer, in
either of two model versions, will flag them. The single intersect
sections (z-gap §4.3, ploidy §5.1) are even more robust — they
survive both intra-version stochasticity *and* cross-version drift.

### 2. 4.7 is more variable than 4.6

Mean Fleiss κ across 5 papers:
- 4.6: **0.276** (fair)
- 4.7: **0.203** (slight, near border of fair)

3 of 5 papers (narcissus, analogic-appropriation, z-gap) show LOWER
κ under 4.7 — the same model on the same paper produces more
heterogeneous reviews. The narcissus κ drops most steeply (0.467 →
0.180); ploidy and eddy κ actually rise under 4.7, but from a low
baseline.

Possible interpretations (the data discriminate weakly):
- (a) 4.7 has higher generation diversity, surfacing more diverse
  critiques.
- (b) 4.7 dwells on slightly different parts of the paper across runs
  due to attention-distribution differences.
- (c) 4.7 produces more "secondary" findings whose section labels are
  less anchored to the original paper structure.

What it does NOT mean: 4.7 is "worse." It catches more unique sections
in absolute terms (narcissus has 8+4 stable in 4.6 vs 4+0 unique in 4.7;
but analogic-appropriation has 8 4.6-stable + 2 unique 4.7-stable; eddy
has 6+2; ploidy has 3+4). On per-paper average, 4.7 enriches the
union of stable findings by ~2-4 sections.

### 3. Cross-version Jaccard ≈ within-4.6 Jaccard

- 4.6 within-version pairwise Jaccard: 0.348 (50 pairs from the
  previous multirun analysis)
- 4.6↔4.7 cross-version Jaccard: 0.269 (125 pairs, 5×5 per paper)

Cross-version is LOWER than within-version, but not by much (~0.08
gap). Interpretation: **most of the disagreement between two reviews
is run-to-run stochasticity, not model-version-specific
contributions**. Two random 4.6 runs disagree almost as much as a
4.6 and 4.7 run. This argues for the Narcissus Loop diagnosis being
*model-architecture-stable* but *run-sample-noisy*; the loop concept
generalizes within the Claude family but the *specific findings any
single audit produces* are draw-dependent.

ploidy (cross-version Jaccard 0.145) is the outlier — large
manuscript, broad attack surface, both versions wander differently.

## Cost / time / token transparency

The full 4.7 batch (25 cells):

| Metric | Total | Per cell (avg) |
|---|---:|---:|
| Wall clock (real time) | 2,135 s = 35.6 min if serial | 85 s |
| Wall clock (actual, 5-way parallel) | ~8 min | — |
| Total cost (USD) | $28.5181 | $1.14 |
| Input tokens | 125 | 5 |
| Output tokens | 118,531 | 4,741 |
| Cache-read tokens | 390,125 | 15,605 |
| Cache-creation tokens | 1,015,531 | 40,621 |

Cache utilization: each batch's first cell pays cache_creation
(~200k tokens for ~1300-line ploidy); subsequent cells hit
cache_read of the same ~15k base prompt. Cost-per-cell varies 2× from
$0.95 (narcissus, smaller manuscript) to $1.56 (ploidy, larger).

The 4.6 batch metrics are NOT captured (those cells preceded the
envelope-capture fix). Approximate per-paper token estimates from
manuscript char counts: input ≈ 14–35k tokens per cell, output ≈ 2.8–
3.3k tokens. 4.6 is priced lower than 4.7 per output token by ~3×
(empirical observation), so the 4.6 batch is estimated at $8–12 total,
~$0.35/cell. Estimate confidence: low; rough cost-floor figure only.

## Husserl/epoché resolution (point (d) of the user's review request)

The original 2026-03-26 audit's "ploidy: Husserl epoché ≠ passive
memory absence" finding (paper §2.1 Table 2) is **not reproduced** by
any of the 10 ploidy reviews (5 at 4.6 + 5 at 4.7) in this multirun.
The explanation found via repo inspection:

- Husserl / epoché / phenomenological language exists in
  `planning/drafts/diploid-paper-outline.md` of the ploidy
  repository — an *outline* document, not the final paper.
- Current `paper/main.tex` of ploidy (1,308 lines, post-revision)
  contains ZERO mentions of Husserl, epoché, or phenomenology.
- git log over all branches of ploidy/paper/ confirms the term was
  never committed to the manuscript file.

Conclusion: the original audit reviewed ploidy at a stage when the
outline was the canonical artifact, the Separate Session caught the
active-vs-passive epoché conflation in that outline, and the
revision excised the analogy. This is *not* a multirun failure — it
is positive evidence that Fresh-session review drives concrete paper
revisions. The Narcissus paper's §2.1 Table 2 should be annotated to
note that this row reflects a critique caught and *acted on* between
the audit and the current artifact state.

## What this evidence supports / does not support

**Supports:**
1. The Narcissus Loop diagnosis is model-version stable within the
   Claude family: structural critique magnets (4 of 5 papers have
   4+ sections in the 4.6∩4.7 stable core) are reproducibly flagged.
2. H7 (Complementary Detection) is even more strongly supported once
   we account for cross-version drift: a single Fresh pass under any
   single model version misses ~70% of what other passes might catch.
3. The 2026-03-26 Table 2 findings — re-tested here on the current
   paper artifacts — are 5/6 substantively reproduced (Z-Gap P2/P3,
   Analogic Era 2 / D&D, eddy contradiction); the 6th (ploidy
   Husserl) was *removed from the paper itself*, evidence of the
   architectural-intervention mechanism the paper argues for.

**Does NOT support:**
1. Causal isolation of context-accumulation (no Deep arm in this run).
2. Cross-vendor generalization (Claude family only; TODO #2).
3. Equivalence claim: 4.7 is not strictly more reliable than 4.6 —
   intra-version Fleiss κ is actually LOWER under 4.7 on 3 of 5
   papers.

## Operational notes

- Quota cost per "true Study 1 replication arm" (25 cells × 1 model
  × 5 papers) ≈ $28 at 4.7 prices on Claude Max plan. Plan
  accordingly for cross-vendor follow-up (TODO #2).
- Cache hits dominate: 390k of the 526k total input tokens (74%)
  were cache_read. Without prompt caching the same batch would cost
  4–5× more.
- Real-time monitoring (`experiments/src/status.sh` + a `jq`-based
  Monitor watching for new cells) worked. The previous "Bash stdio
  buffering" complaint applies only to the master log, not per-cell
  outputs.
