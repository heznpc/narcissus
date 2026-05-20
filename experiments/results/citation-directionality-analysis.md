# Citation Directionality Analysis: AI-Assisted Research Bias Quantification

> Analysis date: 2026-03-26
> Scope: git diff origin/main → HEAD (pre-correction) across 5 repos
> Method: Manual classification of every citation added in local-only commits
> **Status (2026-05-21): EXPLORATORY — single-rater. Inter-rater reliability
> not yet measured. SHAs partially lost post-audit due to history rewrites in
> 2 of 3 audited repos. See `../data/raw/audit-manifest-2026-05-21.md` for
> the frozen reference SHAs and the reproducibility note. A two-rater
> re-classification (with Cohen's κ) is scheduled as Study 1.**

---

## Summary Table

| Repo | Confirming | Challenging | Neutral | Placeholder | Ratio (C/C+Ch) |
|------|-----------|-------------|---------|-------------|-----------------|
| analogic-appropriation | 5 | 0 | 1 | 4 | **100%** |
| z-gap | 3 | 0 | 0 | 0 | **100%** |
| villagent | 4 | 0 | 0 | 0 | **100%** |
| eddy | — | — | — | — | (synced) |
| ploidy | — | — | — | — | (synced) |
| **Total** | **12** | **0** | **1** | **4** | **100%** |

**12 confirming citations, 0 challenging, across 3 repos. Zero counter-citations until Fresh review explicitly requested them.**

---

## Detailed Classification

### analogic-appropriation (commit 53e4aa9, +385 lines)

| Citation | Direction | Rationale |
|----------|-----------|-----------|
| CFDS Indonesia 2025 (Roblox study) | CONFIRMING | "non-Western perspective on Era 2 dynamics" — extends framework geographically |
| Blank & Kitta 2023 (Folk in Age of Algorithms) | CONFIRMING | "folklore in algorithmic environments" — grounds Era 3 in folklore theory |
| KADOKAWA 2026 (brainrot encyclopedias) | CONFIRMING | Strengthens "Japan's absence is substrate-specific" argument |
| Melo 2025 (memetic performance) | CONFIRMING | "ritualized agonistic-creation-peer-sharing" — directly parallels thesis |
| Atabey 2025 (12-LMIC play study) | CONFIRMING | "cross-cultural play research feasibility" — supports planned survey |
| Braun & Clarke 2006 (thematic analysis) | NEUTRAL | Methodology reference |

**Additionally: 4 of 5 confirming citations had hallucinated author attributions:**
- "Atabey" → real author Iannelli
- "Blank & Kitta" → real author Flinterud (sole)
- CFDS → blog post, not report
- Melo → author name unverified

### z-gap (commit 8e4e2e6, +76 lines)

| Citation | Direction | Rationale |
|----------|-----------|-----------|
| Wendler et al. 2024 (llamas, English-pivot) | CONFIRMING | Explains P2 failure as measurement artifact → preserves thesis |
| Wan et al. 2024 (SemCoder, execution semantics) | CONFIRMING | Description/execution distinction → P2 failure doesn't refute Z convergence |
| Wu 2025 (semantic hub, D_train) | CONFIRMING | D_train bias explains R_C < R_J → preserves thesis |

**Pattern: All 3 citations support the interpretation that P2 failure is a test-design issue, not a thesis problem. No citation considered that Z_sem itself may not converge.**

### villagent (commit 9a06781, +377 lines)

| Citation/Data | Direction | Rationale |
|---------------|-----------|-----------|
| Braintrust $800M valuation | CONFIRMING | Market validation for AI observability |
| Arize $131M funding | CONFIRMING | Market validation |
| LangChain $1.25B valuation | CONFIRMING | Market validation |
| Cursor $29.3B valuation | CONFIRMING | Market validation for developer tools |

**Market analysis document — inherently advocacy-oriented, but no competing/failing products cited.**

---

## Post-Correction Comparison

After Fresh review + explicit counter-citation search:

| Metric | Before | After |
|--------|--------|-------|
| Counter-citations in analogic | 0 | 6 (Nielsen, Mustola, Lancy, Fine, Henrich, + D&D pathway) |
| Z-gap Interpretation B (thesis-challenging) | 1 sentence | Full paragraph, equal weight |
| Z-gap P3 English-pivot caveat | 0 | Added |
| Hallucinated authors | 4 | 0 (all corrected) |

---

## Implications

1. **100% confirming citation ratio** across all AI-assisted refinements — no exceptions
2. **AI hallucination is directional**: it fabricates plausible authors for real papers that support the thesis, never for papers that challenge it
3. **The correction required explicit adversarial instruction** ("find counter-citations") — normal AI-assisted research does not produce this
4. **Fresh session found counter-citations in minutes** that Deep session never considered over hours of collaboration

This data supports the Narcissus thesis: AI-assisted real-time research creates a positive feedback loop where the researcher's framing biases the AI's search, and the AI's outputs reinforce the framing — a mirror that reflects the researcher's own thesis back as confirmation. Breaking the loop requires architectural intervention (context-free review), not behavioral intention.
