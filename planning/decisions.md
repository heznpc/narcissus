# Research Decisions Log

Records non-obvious choices with rationale. Append-only; don't rewrite history.

Format: `## YYYY-MM-DD -- <short title>` with **Context**, **Decision**, **Why**.

---

## 2026-04-19 -- Repository restructure to DDD-style layout

**Context**: Top level had TODO.md, review.md, outline.md, citation-directionality-analysis.md co-located with paper/. No .gitignore, so paper/main.aux/log/out/pdf were tracked.

**Decision**: Adopt bounded-context layout -- paper/ (domain), experiments/results/ (analysis outputs), planning/ (meta), literature/. The citation audit moves to experiments/results/ since it's a quantitative finding. Build artifacts gitignored and untracked.

**Why**: Single source of truth for the manuscript; analysis output separated from meta work; artifacts out of version control.
