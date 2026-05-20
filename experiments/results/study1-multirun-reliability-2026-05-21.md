# Study 1 — Multi-Run Reliability Analysis (2026-05-21)

> Status: Completes the deferred multi-run reliability arm of Study 1
> (paper §4.1; previous results doc at
> `study1-replication-2026-05-21.md`).
> Cohort: same 5 papers (narcissus, analogic-appropriation, z-gap,
> eddy, ploidy), now reviewed by n=5 independent Fresh-session CLI
> invocations each, for 25 total cells.
> Method: `claude --print --disable-slash-commands` from an isolated
> mktemp directory (no CLAUDE.md auto-discovery) — see
> `../src/run_fresh_review_cli.sh`. Multi-run launcher and analyzer:
> `run_study1_multirun.sh`, `analyze_multirun.py`.
> Raw cells: `../data/raw/study1-replication/<paper>__claude-opus-4-7__bare__run-{1..5}.json`
> (gitignored).

## Headline numbers

| Paper | runs | issues/cell (mean ± sd) | pairwise Jaccard mean | stable sections (5/5) |
|---|---:|---:|---:|---:|
| narcissus              | 5 | 13.2 ± 0.45 | **0.372** | 8 |
| analogic-appropriation | 5 | 13.0 ± 1.00 | **0.371** | 8 |
| z-gap                  | 5 | 13.2 ± 0.45 | **0.450** | 3 |
| eddy                   | 5 | 13.0 ± 0.71 | **0.332** | 6 |
| ploidy                 | 5 | 13.4 ± 0.89 | **0.217** | 3 |
| **Aggregate (50 pairs)** | — | **13.16 ± 0.69** | **0.348** | — |

Total: **329 issues across 25 cells**. Severity distribution: 62
critical / 173 major / 94 minor (19% / 53% / 29%).

## Two clean findings (and a dirty one)

### Clean finding 1 — issue *count* is highly stable

Across all 25 cells, the per-cell issue count is **13.16 ± 0.69**. The
LLM produces a consistent *volume* of criticism regardless of run.
Variance is dominated by paper length / complexity, not by run-to-run
sampling noise. This is a meaningful baseline: any single Fresh-review
pass produces ~13 issues, predictably.

### Clean finding 2 — a stable critique *core* exists

For 4 of 5 papers, between 3 and 8 sections are flagged by **all 5
runs**. For narcissus specifically these are:

  - **§2.1** (Three-Session Natural Experiment)
  - **§2.2** (AI-Hallucinated Citation Attribution)
  - **§2.3** (Directional Citation Bias)
  - **§3** (Mechanism: The Narcissus Loop)
  - **§3.1** (Distinct from Known Biases)
  - **§3.2** (Completion Hallucination)
  - **§4.2** (Study 2)
  - **§6** (Limitations)

These are the paper's **structural critique magnets**: any
independent Fresh reviewer will surface concerns about these sections.
This is the *signal* — it overlaps strikingly with the C/M findings
from the pre-experiment review pass (HARKing, confound caveat,
Table 2 selection criteria) and with the original §2.1 Table 2
Fresh-session catches from 2026-03-26.

### Dirty finding — issue *content* is only moderately stable

Mean pairwise Jaccard across 50 run-pairs is **0.348** (median 0.361,
range 0.087–0.571). Two randomly-chosen Fresh-session reviews of
the *same paper* agree on only ~35% of their (section, severity)
fingerprints. **A single Fresh-session pass is far from a complete
audit.**

Implications:

- **H7 (Complementary Detection) is strongly supported.** §3.6 of the
  paper hypothesizes that no single Fresh session catches all problems
  and that multiple independent sessions with different stances detect
  significantly more in aggregate. The 0.348 mean Jaccard quantifies
  this: any single run misses on average ~65% of what other runs catch.
- **Quantitative claims from single runs need uncertainty quantification.**
  The original 2026-03-26 audit's specific counts (12/0 confirming
  citations, 9/11 metadata errors, 6 issues missed) come from one
  pass each. The "12/0" likely lies in the *stable core* (it's a
  structural pattern), but the specific issue selection and exact
  count could vary if repeated. Paper text should reflect this.
- **Ploidy is the lower-bound outlier (J=0.217).** Likely cause: 1,308
  lines of manuscript = large attack surface, different runs pick
  different sections to dwell on. The 3 stable sections (S1, S5.1,
  S6.5) anchor the core critique; everything else is sampled.

## Selected stable-core findings

For each paper, the modal issue at a stable section. These are
critiques that *every* Fresh run surfaces, in some wording — they
should be considered established as criticisms regardless of which
single pass is examined.

- **narcissus §2.1** — adversarial-role × context-depth confound in
  the Three-Session natural experiment; cannot isolate the effect of
  context depth from the prompt-instructed adversarial stance.
- **narcissus §2.2 / §2.3** — small-n + single-rater classification;
  the 4 hallucination cases and the 5:0 citation directionality cannot
  carry the inferential weight the paper asks of them.
- **narcissus §3 / §3.1** — the Narcissus Loop is a verbal story with
  no formal model; "emergent / super-additive" is asserted, not derived.
- **narcissus §4.2** — Study 2 design issues: power, mediator vs.
  moderator clarity, and (per multiple runs) the H3 awareness claim
  framing.
- **analogic-appropriation §3 / §4** — conceptual conflation between
  *appropriation*, *participation*, and *adaptation* across Era 1/2/3.
- **z-gap §3.2 / §5.5** — P2 result is a directional falsification,
  not just "predicted-direction failure"; framing understates the
  threat to the convergence-without-communicability thesis.
- **eddy §1.2 / §2.1 / §2.3 / §2.4 / §3.1** — title/abstract overclaim
  vs. body hedging; Equation 1 mathematical triviality; boundary
  conditions make hypothesis unfalsifiable.
- **ploidy §1 / §5.1 / §6.5** — primary hypothesis not confirmed at
  corrected significance but paper still presents Ploidy as a
  methodological contribution; Stochastic-N anomaly in Table 9;
  judge-model contamination (Opus 4.6 judging Opus-family outputs).

## What this analysis does NOT show

- **No Cohen's κ across runs.** Free-text issue descriptions don't
  yield a fixed item universe for κ. Fleiss' κ on the implicit binary
  "is this section flagged?" item would be the right next step (each
  union-section as an item, each run as a rater); deferred.
- **No semantic clustering.** Two runs flagging "§2.1" with different
  critique angles count as full agreement in the Jaccard set —
  potentially inflating agreement. A description-level embedding
  similarity would be more sensitive.
- **No content-validity check** that the stable-core findings are
  correct (vs. merely repeatedly surfaced). Multiple Fresh sessions
  agreeing on a flag does not prove the flag is right; it proves the
  paper structurally invites that flag.

## Reproducibility

```bash
# Re-run the 25 cells (or any subset that's missing):
bash experiments/src/run_study1_multirun.sh 5 8

# Status (5x5 matrix + activity + next reset):
bash experiments/src/status.sh

# Recompute analysis:
python3 experiments/src/analyze_multirun.py
```

The runner is idempotent (skips on output file existence), so reruns
only spend quota on cells that don't yet exist. A launchd watchdog
(`com.heznpc.narcissus-multirun-watchdog`) installed at
`~/Library/LaunchAgents/` relaunches the runner every 60s if it dies
between quota-reset windows.
