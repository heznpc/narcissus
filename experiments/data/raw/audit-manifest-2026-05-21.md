# Audit Source Manifest — Frozen 2026-05-21

This manifest pins the *exact* commit SHAs of the source repositories used by
`experiments/results/citation-directionality-analysis.md`. Any re-run of the
audit must use the SHAs below as the canonical reference point. Without this
freeze, `HEAD` drift makes the audit non-reproducible (see paper §6,
"Reproducibility limitations").

## Audited repositories

| Repo | Audit-time SHA (original, 2026-03-26) | Status (2026-05-21) | Current HEAD (2026-05-21) |
|---|---|---|---|
| analogic-appropriation | `53e4aa9` | **LOST** (history rewritten by post-audit refactor + squash-merge) | `995d528` |
| z-gap                  | `8e4e2e6` | **PRESENT** in `--all` (still resolvable) | `0f6cabc` |
| villagent              | `9a06781` | **LOST** (squash-merge of pre-history) | `d01ac12` |
| eddy                   | (synced — no AI-assisted diffs flagged) | n/a | `49b7c7e` |
| ploidy                 | (synced — no AI-assisted diffs flagged) | n/a | `79d0c49` |

## Reproducibility note

The original audit was performed against `origin/main → HEAD` diffs whose SHAs
were partially recorded in `citation-directionality-analysis.md` but whose
underlying commits were subsequently squash-merged or rewritten in two of the
three audited repos. The original audit is therefore reproducible only for
z-gap (`8e4e2e6`). For analogic-appropriation and villagent, the audit's raw
diff input no longer exists in the canonical history; the *classifications*
remain (12 confirming / 0 challenging / 4 directional hallucinations) but the
underlying commits cannot be re-inspected without a backup ref.

This limitation is acknowledged in the paper's §6 (Limitations) as an
artifact-recovery constraint. Going forward (Study 1 re-classification with
two raters), the canonical reference point is the SHAs listed in the
"Current HEAD (2026-05-21)" column. Any further re-runs MUST cite a SHA
fixed against this manifest, not against `HEAD`.

## Audit subjects (paper-level)

The five papers audited:

1. **analogic-appropriation** — play appropriation, media studies / cultural
   anthropology.
2. **z-gap** — cross-linguistic LLM convergence, NLP.
3. **villagent** — agent lifecycle simulation, market analysis.
4. **eddy** — novelty decay vs. compound advantage, HCI.
5. **ploidy** — context-asymmetric debate (companion repo).

## Schema for upcoming Study 1 re-classification

The CSV at `experiments/data/raw/citations-rater-1.csv` (current single-rater
data) and a forthcoming `citations-rater-2.csv` (second blinded rater, to be
collected) will both use the schema:

```
repo,sha,citation_id,context,proposed_author,actual_author,direction,doi_verified,notes
```

- `direction` ∈ {confirming, challenging, neutral, placeholder}
- `doi_verified` ∈ {verified, hallucinated, unverified}

Cohen's κ is to be computed across the two raters per H6 specification
(Section §3, Citation directionality).
