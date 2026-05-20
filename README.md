Research Program: 2 (Epistemic Failure and Correction)
Status: Concept note
Relationship to other work: Companion to ploidy

# Narcissus

This is a concept note, not a finished paper.

**How AI Mirrors Amplify Researcher Confirmation Bias**

When researchers use AI assistants for real-time literature search and writing, a positive feedback loop emerges: the researcher's framing biases the AI's search, and the AI's outputs reinforce the framing. This **collaborative entrenchment** is distinct from either human confirmation bias or AI sycophancy alone — it is an emergent property of the interaction loop.

## Currently implemented

- A 5-repo citation audit (`experiments/results/citation-directionality-analysis.md`) measuring citation directionality across AI-assisted paper repositories.
- Manuscript source at `paper/main.tex` (495 lines).
- Reading notes and gap analysis under `literature/`.

## Key findings

- **100% confirming citation ratio** across 5 AI-assisted paper repositories (12 confirming, 0 challenging).
- **Directional hallucination**: AI fabricates metadata for thesis-supporting papers, never for counter-arguments.
- **Fresh sessions** (zero context) catch critical problems that Deep sessions (accumulated context) systematically miss.

## Planned

- Expand the audit beyond the initial 5 repos.
- Pair with [ploidy](../ploidy) as the architectural countermeasure (context-asymmetric debate) the empirical findings here motivate.

## Design intent

A companion concept note to ploidy: ploidy proposes an architectural countermeasure (context-asymmetric debate); narcissus supplies the empirical bias evidence that motivates it. The audit is intentionally small (n=5 repos) to make the directionality of the failure visible, not to claim a population-level effect.

## Non-goals

- Population-level claims about AI-assisted research at scale.
- A replacement for ploidy — this note documents the failure mode, not the fix.
- A tool release. This repo is manuscript + audit notes only.

## Repository structure

```
narcissus/
  paper/                      Domain -- manuscript source of truth
    main.tex
    figures/
  experiments/                Application -- evidence generation
    results/
      citation-directionality-analysis.md   Quantitative audit across 5 repos
  literature/                 Reading notes, gap analysis
  planning/                   TODO, review, decisions log
    drafts/                   outline.md (superseded)
```

## Related

Part of a research program with [ploidy](../ploidy) (context-asymmetric debate as architectural countermeasure).
