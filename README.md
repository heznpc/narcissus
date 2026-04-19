# Narcissus

**How AI Mirrors Amplify Researcher Confirmation Bias**

When researchers use AI assistants for real-time literature search and writing, a positive feedback loop emerges: the researcher's framing biases the AI's search, and the AI's outputs reinforce the framing. This **collaborative entrenchment** is distinct from either human confirmation bias or AI sycophancy alone — it is an emergent property of the interaction loop.

## Key Findings

- **100% confirming citation ratio** across 5 AI-assisted paper repositories (12 confirming, 0 challenging)
- **Directional hallucination**: AI fabricates metadata for thesis-supporting papers, never for counter-arguments
- **Fresh sessions** (zero context) catch critical problems that Deep sessions (accumulated context) systematically miss

## Repository Structure

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

Part of a research program with [Ploidy](../ploidy) (context-asymmetric debate as architectural countermeasure).
