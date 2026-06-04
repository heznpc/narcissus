# Study 1 — Cross-Vendor: Gemini vs Claude (TODO #2, 2026-06-04)

> Status: First NON-Claude data point. Closes the long-deferred cross-vendor
> arm (TODO #2). Google Gemini 3.1-pro-preview, Fresh × Adversarial, n=5 per
> paper = 25 cells, compared against Claude Opus 4.6 (the original-audit-era
> model), n=5.
> Method: `gemini -p ... --output-format json --approval-mode plan -m
> gemini-3.1-pro-preview`, vendor-adapted cell runner emitting the common
> cell schema. Section normalizer extended to map Gemini's bare "N.M Title"
> refs (see below). Analysis: experiments/src/compare_crossvendor.py.
> Cost: Gemini CLI uses Google credentials (separate quota; no Claude-Max
> spend) and reports no USD cost; ~26k input / ~1.3k output / ~3k thinking
> tokens per cell.

## A measurement prerequisite (and its risk)

Gemini cites sections as bare numbers with titles ("2.1 Three-Session
Natural Experiment", "2. Evidence") — no §/Sec prefix. The section
normalizer required a new rule to extract leading/post-separator bare
numbers, or Gemini's refs would fall through to the verbatim fallback and
match nothing in Claude's "S2.1" space, making cross-vendor Jaccard
spuriously ~0 even on identical sections. This fix was verified not to
change Claude results and to reject false matches ("2024", "p=1.0"); one
residual edge case ("9 of 11" → S9) is accepted as rare. **This is the §6
measurement-validity limitation made concrete: cross-vendor section
overlap is only measurable after vendor-specific citation-style
normalization, and is the least trustworthy of the metrics below.**

## Results

### Issue count and within-vendor reliability

| paper | Claude n | Gemini n | Claude wJaccard | Gemini wJaccard | Claude κ | Gemini κ |
|---|---:|---:|---:|---:|---:|---:|
| narcissus | 13.2±0.4 | 8.2±1.3 | 0.372 | 0.244 | 0.467 | 0.224 |
| analogic-appropriation | 13.0±1.0 | 7.8±0.4 | 0.371 | 0.231 | 0.436 | 0.162 |
| z-gap | 13.2±0.4 | 7.0±0.0 | 0.450 | 0.352 | 0.242 | 0.167 |
| eddy | 13.0±0.7 | 7.4±0.9 | 0.336 | 0.176 | 0.231 | 0.200 |
| ploidy | 13.4±0.9 | 8.0±1.2 | 0.221 | 0.076 | 0.053 | −0.096 |
| **mean** | **13.2** | **7.7** | **0.350** | **0.216** | — | — |

Gemini is markedly **more parsimonious** (7.7 vs 13.2 issues/cell, ~58% of
Claude's volume; z-gap exactly 7.0 every run) and somewhat **less
self-consistent** in section targeting (within-vendor Jaccard 0.22 vs 0.35).
The lower issue count partly drives the lower self-consistency: fewer issues
per run → smaller section sets → more room for run-to-run variation in which
subset is covered.

### Headline: cross-vendor structural-magnet overlap

Sections flagged by ALL 5 runs of BOTH vendors:

| paper | Claude-4.6 core | Gemini core | SHARED |
|---|---|---|---|
| narcissus | S2.1, S2.2, S2.3, S3, S3.1, S3.2, S4.2, S6 (8) | S2.1, S3.1, S4.2 (3) | **S2.1, S3.1, S4.2** |
| analogic-appropriation | S2.4,S2.5,S3,S4.1,S4.2,S4.3,S5.1,S5.2 (8) | S4.3, S5.1 (2) | **S4.3, S5.1** |
| z-gap | S3.2, S4.3, S5.5 (3) | S4.3 (1) | **S4.3** |
| eddy | S1.2,S2.1,S2.3,S2.4,S3.1,S4 (6) | S4.1, S4.3 (2) | (none exact) |
| ploidy | S1, S5.1, S6.5 (3) | (none — too variable) | (none) |

**The narcissus result is the cleanest and most important**: Google Gemini
3.1, a completely independent vendor and architecture, **independently and
unanimously flags §2.1 (the Three-Session adversarial-role confound — the
paper's single most important self-identified weakness), plus §3.1
(distinct-from-known-biases) and §4.2 (Study 2 design).** That a non-Claude
model converges on the same top critiques is strong evidence those critiques
are properties of the *manuscript*, not Claude-idiosyncratic artifacts.

### Directional precision (the fairer read of the asymmetry)

Because Gemini flags ~40% fewer issues, fewer of its sections reach 5/5
unanimity, so the raw shared count understates agreement. The fairer test:
**of the sections Gemini DOES flag unanimously, what fraction are in
Claude's core?**

- narcissus: 3/3 = 100%
- analogic: 2/2 = 100%
- z-gap: 1/1 = 100%
- eddy: 0/2 — but Gemini's S4.1/S4.3 vs Claude's S4 is the **same §4 (Study
  design) critique at finer subsection granularity**; the exact-match metric
  scores it 0, substantively it is agreement.
- ploidy: Gemini reached no unanimous core (highest-variance paper for both
  vendors).

So **where Gemini reaches unanimity, it lands almost entirely inside
Claude's core.** Cross-vendor disagreement is dominated by Gemini surfacing
*fewer* magnets, not *different* ones.

### Cross-vendor Jaccard (least robust)

Mean (section,severity) cross-vendor Jaccard = 0.177, below within-Claude
(0.350) and ≈ within-Gemini (0.216) — a ceiling effect of the noisier
vendor, plus residual citation-style and granularity confounds. Reported
for completeness; the magnet/precision analysis above is the trustworthy
signal.

## Honest conclusion

The cross-vendor arm gives **partial generalization, concentrated on the
strongest critiques**:

1. The TOP structural magnets generalize across vendors. narcissus §2.1
   (the headline self-critique) is independently, unanimously reproduced by
   Gemini. Where both vendors reach unanimity they agree with ~100%
   directional precision.
2. Generalization is partial: Gemini is more parsimonious and surfaces a
   shorter critique list, so Claude's deeper core (the long tail of major/
   minor issues) is NOT fully reproduced. eddy and ploidy share no exact
   unanimous magnet.
3. This does NOT support a clean "universal across all models" claim, and we
   do not make one. It supports: *the most consequential, structural
   critiques are model- and vendor-robust; the long tail is model-specific.*
   This dovetails with the within-Claude 3-version finding (stable central
   tendency, version-dependent reliability) — now extended to: stable
   top-tier across vendors, vendor-dependent depth.

## Reflexivity

This analysis was run on Claude (the orchestrator) and framed as "does
Gemini agree with Claude's core." The symmetric framing — "of what Gemini
flags, how much is in Claude's core" (100% for 3/5 papers) — is reported
above to avoid a Claude-centric tilt. The Gemini cells are independent
subprocess invocations; no Claude context leaks into them.

## Known issue (logged, fixed for next run)

ploidy run-4 failed once with exit 5 (review JSON not parseable) and the
batch bailed at 24/25; a manual re-run parsed cleanly (10 issues),
confirming the failure was stochastic LLM-output variance, not a systematic
bug. The gemini multirun's failure taxonomy was corrected to treat output-
parse failures (exit 5/6/7) as TRANSIENT (retry, capped) rather than
deterministic-bail; only model-not-found (4) and model-mismatch (8) bail.

## Files

- `../data/raw/study1-replication/<paper>__gemini-3.1-pro-preview__bare__run-{1..5}.json` — 25 cells.
- `../src/run_fresh_review_gemini.sh`, `../src/run_gemini_multirun.sh`, `../src/compare_crossvendor.py`.
