# Research Decisions Log

Records non-obvious choices with rationale. Append-only; don't rewrite history.

Format: `## YYYY-MM-DD -- <short title>` with **Context**, **Decision**, **Why**.

---

## 2026-04-19 -- Repository restructure to DDD-style layout

**Context**: Top level had TODO.md, review.md, outline.md, citation-directionality-analysis.md co-located with paper/. No .gitignore, so paper/main.aux/log/out/pdf were tracked.

**Decision**: Adopt bounded-context layout -- paper/ (domain), experiments/results/ (analysis outputs), planning/ (meta), literature/. The citation audit moves to experiments/results/ since it's a quantitative finding. Build artifacts gitignored and untracked.

**Why**: Single source of truth for the manuscript; analysis output separated from meta work; artifacts out of version control.

---

## 2026-05-21 -- Pre-experiment review fixes (C1–C7 critical)

**Context**: Pre-experiment 9-dimension review of paper + experiments + planning surfaced seven Critical issues that would invalidate either the experiment or the submission to CHI/FAccT.

**Decision**: Apply seven critical fixes in-session without further user confirmation.

- **C1 — Hearsay removal**: The "immunologist + AI coding assistant" anecdote (§3.3) was uncited public hearsay. Rewrote §3.3 to retain only the author's own observation, explicitly labeled as a single case, with systematic study deferred to future work.
- **C2 — HARKing label**: H1–H7 were derived from the §2 audit. Added an explicit "Status of these hypotheses" paragraph labeling them as exploratory (post-hoc), citing Kerr (1998). Study 1 is now labeled descriptive/estimation-only; Study 2 carries the confirmatory burden.
- **C3 — Confound caveat at presentation site**: Added an inline caveat at §2.1 (Three-Session Natural Experiment) listing the four confounded dimensions (context depth × role × prompt × timing) and explicitly framing the data as a single-program existence proof.
- **C4 — Selection criteria**: Added a paragraph stating the inclusion rule for Table 2 (every issue raised by at least one session) and acknowledging that the absence of Deep-only detections is itself consistent with the loop and cannot be independently ruled out without Study 2.
- **C5 — Anonymization + Heznpc identity**: `paper/main.tex` author block replaced with "Anonymous Author(s) / Affiliation withheld for blind review" + comment noting camera-ready identity (Heznpc). `.zenodo.json` creator changed from "Yoon, Jiyeon" to "Heznpc" per the global CLAUDE.md rule.
- **C6 — Inter-rater reliability**: Added κ ≥ 0.6 protocol to Study 1; explicitly relabeled the published audit as single-rater exploratory at the presentation site (§2.3) and at the reference-audit conclusion (§2.4).
- **C7 — Data reproducibility**: Created `experiments/data/raw/audit-manifest-2026-05-21.md` freezing current HEAD SHAs of all 5 audited repos. Documented that 2 of 3 original audit SHAs (analogic-appropriation `53e4aa9`, villagent `9a06781`) are lost to post-audit history rewrites; only z-gap `8e4e2e6` remains resolvable. Added a status note to `citation-directionality-analysis.md` pointing to the manifest.

**Why**: All seven were threshold issues. C1, C3, C4, C5, C6 would cause desk-reject at CHI/FAccT. C2 was a methodological error in framing (HARKing). C7 made the audit non-reproducible. None of the seven changes weakened the substantive claims of the paper; they tightened the evidentiary scaffold.

**Pending (Major, awaiting user decisions)**: ~~M1–M8~~ → see 2026-05-21 (Major) below.

---

## 2026-05-21 -- Pre-experiment review fixes (M1–M8 major, all per user choice)

User accepted the recommended option for all eight major items.

- **M1 — H3 as TOST equivalence**: H3 reframed as equivalence claim against SESOI $d=0.2$ with 90% CI fully within $[-0.2, +0.2]$ required for support (Lakens 2017 cited).
- **M2 — Benjamini–Hochberg FDR**: Primary preregistered test is H4 (AI×Review interaction) at α=.05 uncorrected; H1,H2,H3,H5,H6,H7 treated as secondary family at BH-FDR q=.05.
- **M3 — Power N=128 (32/cell)**: G*Power 3.1 a priori for 2×2 ANOVA interaction, f=.25, α=.05, power=.80 (Faul et al. 2007 cited). Pre-specified expansion if Study 1's effect size estimate falls below f=.20.
- **M4 — Cell 4 as baseline**: Solo×No-review cell explicitly declared as the reference baseline. §2.3 12:0 ratio caveat-linked to Study 2 Cell 4.
- **M5 — Wei et al. 2024**: Added to bibliography and §5 sycophancy paragraph.
- **M6 — Human reviewers only**: Two faculty/post-PhD reviewers, blinded, with κ + ICC reported. LLM scoring explicitly excluded as circular.
- **M7 — IRB exempt category 2**: Common Rule §46.104(d)(2) educational-testing exemption anticipated; consent + withdrawal + de-identification specified.
- **M8 — Effect-size predictions**: Cell 2 vs. Cell 4 expected d ≈ 0.5–0.8; interaction expected η²_p ≈ 0.06–0.10 (90% CI lower bound > 0); Cell 1 vs. Cell 3 TOST equivalence within |d| ≤ 0.2.

All eight fixes are documented in-paper at the corresponding §; bibliography expanded with Kerr 1998, Wei 2024, Lakens 2017, Faul 2007.

**Minor (TODO comments only, not blocking)**: m1 biblatex/.bib migration; m2 OSF/AsPredicted preregistration; m3 hallucination 4-type typology (placeholder/wrong-author/anonymous/URL); m4 time-decay curve T0–T3; m5 dead `python src/<script>.py` reference in experiments/README.md.

---

## 2026-05-21 -- Model versioning: Opus 4.7 release handling

**Context**: Claude Opus 4.7 released 2026-Q2, after the 2026-03-26 audit was complete with Opus 4.6. Risk: paper looks dated by the time it lands at CHI/FAccT 2027. Reviewer push-back almost certain on "but newer models..."

**Decision**: Preserve the 4.6-frozen natural experiment as the historical record; add a within-Claude-family model-version replication arm to Study 1 and a model-version covariate to Study 2.

- §2 (Evidence) — Opus 4.6 retained as accurate description of the natural experiment, with a new paragraph noting 4.7 was released after the audit and that model-version generalization is treated as an empirical question in Studies 1 and 2.
- §4.1 (Study 1) — Added a "Model-version replication arm": the same five papers re-reviewed by Fresh sessions under Opus 4.7. Reports 4.6↔4.7 κ alongside the two-rater human κ.
- §4.2 (Study 2) — Added a model-version covariate: AI-assisted cells (1 and 2) split 16/16 between Opus 4.6 and Opus 4.7. Tests the three-way AI × Review × Version interaction for model-version stability of the effect.
- §6 (Limitations) — "Model specificity" entry updated: within-Claude-family stability is now in Studies 1 and 2; cross-vendor generalization (GPT, Gemini, open-weights) explicitly punted to TODO #2 as a separate study.
- planning/TODO.md #2 — Reframed from "3-model comparison" to cross-vendor focus (within-Claude-version comparison absorbed by Study 1 replication arm).

**Why**: The natural experiment's data are frozen in time and cannot be retroactively updated to 4.7; rewriting §2 would falsify the historical record. The right move is to (a) keep §2 accurate, (b) explicitly acknowledge the version gap in §6, and (c) build version replication into the prospective studies. This converts a known limitation into a planned empirical contribution.

**Cost**: Study 1 doubles in size (each paper reviewed twice — under 4.6 and 4.7). Study 2 AI-assisted cells require 32 participants each, distributed 16/16 across versions; the total N=128 design remains valid.
