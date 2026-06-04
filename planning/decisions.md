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

---

## 2026-05-21 -- Model label correctness + cross-version replication completed

**Context**: First multirun (25 cells, 2026-05-21 morning) was launched without `--model` flag in the `claude --print` invocations. Claude Code's default model is claude-opus-4-6 (1M context), and the cells were therefore served by 4.6 while labeled "claude-opus-4-7". Discovered via the envelope's `modelUsage` key when `--output-format json` was added.

**Decision**: Relabel the 26 existing cells to 4.6 (their actual identity) and re-run a true 4.7 batch of 25 cells with explicit `--model claude-opus-4-7`. The 50-cell corpus (25 4.6 + 25 4.7) is the canonical Study 1 dataset.

- Relabeled: filenames changed from `__claude-opus-4-7__` to `__claude-opus-4-6__`; `model` field inside each JSON updated; `_relabel_note` added documenting the investigation.
- New 4.7 batch: completed in 8 wall minutes via the now model-aware multirun (`run_study1_multirun.sh 5 8 claude-opus-4-7`). 25 cells, $28.52 total, $1.14/cell average.
- Per-cell envelope captured (duration, cost, usage, modelUsage) so future label drift is detectable at write time.

**Results (analyzed via experiments/src/compare_model_versions.py)**:
- Cross-version stable-core intersection: 4/5/1/4/1 sections (narcissus / analogic / z-gap / eddy / ploidy). Structural critique magnets persist across the version boundary.
- Cross-version Jaccard mean 0.269; within-4.6 Jaccard 0.348. The gap (~0.08) is much smaller than within-version stochasticity, so the diagnosis is largely model-architecture-stable.
- Fleiss kappa: 4.6 mean 0.276, 4.7 mean 0.203. 4.7 is somewhat more variable within version on 3/5 papers; on the other 2, 4.7 is more consistent than 4.6.

**Paper updates (§4.1 and §6)**:
- §4.1 model-version replication arm subsection: replaced the prospective-only description with a "preliminary multi-run replication results" subsection reporting the cross-version Jaccard (0.27), within-version Jaccard (0.35), Fleiss kappa per version, and the structural-magnet finding.
- §6 model specificity limitation: rewrote to incorporate the actual cross-version numbers and acknowledge that the 4.7 batch had been performed.
- §6 new limitation "single-rater audit, audit-time drift": acknowledges that single-pass audit results (Table 2) reflect one draw from a noisy detection process (~35% capture rate per single pass), and that some affected rows are now "caught and acted on" rather than "caught and persisting" (e.g., the ploidy Husserl row was removed in revision and is no longer in the manuscript text).

**Ploidy Husserl resolution (point (d) of the user's 9-dimension review)**: confirmed via grep of all branches of ploidy/paper/*.tex that "Husserl" / "epoche" / "phenomenological" has never been in the manuscript text. The original audit critique reflected the ploidy *outline* document; the active-vs-passive epoché conflation was removed before the LaTeX manuscript was first committed.

**Cost (transparency)**: 4.7 batch total $28.52 ($1.14/cell). 4.6 batch pre-envelope, estimated $8–12. Aggregate Study 1 (replication arm only): $40–50.

**Outstanding (m-level)**: 4.6 batch lacks per-cell envelope data; if needed for cost/timing reporting, the batch can be re-run with the new envelope-capturing runner (another $10 at 4.6 prices). Cross-vendor (GPT, Gemini, open-weights) remains TODO #2.

---

## 2026-05-21 -- Adversarial vs Neutral reviewer stance comparison

**Context**: The pre-experiment review added a C3 caveat to §2.1 noting that the Fresh Agents' adversarial-reviewer prompt is a confound with context depth and cannot be cleanly isolated by §2 data alone. To directly test this dimension, 25 new cells were generated 2026-05-21 with an otherwise-identical Fresh-session pipeline but a neutral reviewer prompt (5 papers × 5 runs at Opus 4.6 / `prompt_style=neutral`).

**Decision**: Add stance-comparison results to paper §2.1 caveat and §6 limitations rather than leaving the §2.1 caveat with no direct evidence.

**Method**: cell runner extended with 6th positional arg `prompt_style` (adversarial | neutral); multirun launcher passes through; output filenames distinguish via `__neutral__` suffix. Same model, same prompt-isolation regime, same JSON schema. Comparison via `experiments/src/compare_stances.py`.

**Results** (50 cells, $7.71 marginal cost for the neutral arm):
- Total per-cell issue count nearly identical: 13.16 (adv) vs 12.56 (neu), mean −5% across 5 papers (range −15% to +18%).
- Severity distribution differs SUBSTANTIALLY: critical issues drop 62→38 (−39%), major 173→147 (−15%), minor 94→129 (+37%).
- Stable-core (5/5) overlap: 14 of 19 union stable sections are in BOTH stance cores. Neutral cores are predominantly subsets of adversarial cores (e.g., narcissus 4/4, eddy 2/2, analogic 4/5).
- Mean cross-stance Jaccard: 0.267 — about the same as the cross-version Jaccard (0.269). Stance change ≈ model-version change in impact, both << run-to-run stochasticity (0.348 within-stance).
- Mean Fleiss κ within stance: 0.276 (adv) vs 0.195 (neu). Neutral is less consistent — more degrees of freedom without "find weaknesses" instruction.

**Interpretation**: adversarial framing does NOT fabricate critiques — it RE-GRADES them upward. The same structural concerns are flagged in both stances; under neutral framing many are reported as minor that under adversarial framing are reported as critical or major. The §2.1 Table 2 detection signal is robust to stance; the absolute severity tier in any single-stance audit is stance-dependent.

**Paper updates**:
- §2.1 added a new paragraph "Partial isolation of the adversarial-framing confound (2026-05-21 stance comparison)" with the numbers above and the conclusion that detection coverage is stance-robust while severity grading is not.
- §6 added a new limitation "Severity-tier stance dependence" recommending future audits report stance explicitly and aggregate across multiple stances.

**Cost transparency**: 4.6-neutral batch $7.71 ($0.31/cell). About 3.7× cheaper than 4.7-adversarial for substantially the same structural-signal information. The neutral arm completed in ~13 wall minutes (5-way parallel, no quota wall) within a single quota window.

---

## 2026-06-04 -- Opus 4.8 3-point version trend

**Context**: Opus 4.8 released (~2026-06). Same staleness/opportunity logic that motivated the 4.7 arm. Before running, did a design review (V1-V6) and fixed two blocking bugs in the cell runner (transient/permanent error split; envelope_tmp orphan) — see PR #18.

**Decision**: Add a 4.8 Fresh×Adversarial n=5 arm for a balanced 3-point trend (4.6/4.7/4.8, n=5 each, runs 1-5). 25 cells, $39.63, all model_actual=claude-opus-4-8 (exit-8 guard confirmed no fallback).

**Result (compare_3version_trend.py) — did NOT confirm the clean "stable" story**:
- No version-specific DRIFT: 4.6↔4.8 section-level Jaccard (0.28) ≈ 4.8 within-version self-agreement (0.28) → ceiling effect, not drift.
- 4.8 is a markedly HIGHER-VARIANCE single-pass reviewer: section-level within-version Jaccard 0.58 (4.6) → 0.46 (4.7) → 0.28 (4.8), monotonic. Fleiss κ 0.286 → 0.207 → 0.028.
- Partial measurement confound: 4.8 cites sections in multi-ref/prose style (1.39 sec/issue vs 4.6's 1.14); normalizer handles unevenly. Estimated minor (distinct-sections/run comparable: 11.3/13.0/12.2) but not fully separable.
- Stable-core: narcissus keeps 3 sections unanimous across all 15 runs of all 3 versions; analogic/eddy collapse to 0 (consequence of 4.8 variance, not critique disappearance).

**Reframe**: "stable central tendency, declining single-pass reliability" — NOT "model-architecture-stable." Strengthens H7 (newer models need MORE runs). Reported the inconvenient result deliberately (the paper's own thesis warns against the pull toward the cleaner confirming story; analysis ran on 4.8, the high-variance version).

**Paper updates**: §4.1 added the 3-point-trend paragraph; §6 "Model specificity" reframed to "Model specificity and version reliability" + new "Measurement validity: section-citation style is model-dependent" limitation.

**Cost**: 4.8 = $1.59/cell (~40% > 4.7's $1.14), higher output-token volume. Cumulative Study 1 envelope cohort now ~$108 across 175 cells.

---

## 2026-06-04 -- Cross-vendor arm: Gemini (TODO #2 closed as partial generalization)

**Context**: `gemini` CLI (v0.34.0) available and authenticated; user flagged it might disappear, so ran the long-deferred cross-vendor arm now. First non-Claude data point.

**Decision**: Gemini 3.1-pro-preview Fresh×Adversarial n=5 (25 cells), compared vs Claude Opus 4.6. Vendor-adapted cell runner (run_fresh_review_gemini.sh) emitting the common cell schema so existing analyzers work; minimal gemini batch runner (RPM backoff, not the Claude 5h-reset machinery, since Google quota differs).

**Measurement prerequisite**: Gemini cites sections as bare "N.M Title" (no §/Sec prefix). Extended normalize_section with a bare/separator-leading number rule (_RE_BARE_SEC) or cross-vendor Jaccard would be spuriously ~0 from format mismatch alone. Verified: Claude refs unchanged, "2024"/"p=1.0" rejected, residual "9 of 11"->S9 edge accepted.

**Results (compare_crossvendor.py)**:
- Issue count: Claude 13.2 vs Gemini 7.7 (Gemini ~40% more parsimonious).
- Within-vendor: Gemini less self-consistent (section Jaccard 0.22 vs 0.35; κ ~0.13 vs 0.29).
- Cross-vendor shared magnets (5/5 both vendors): 6 across 5 papers. narcissus shares 3 incl. §2.1 (the headline adversarial-role confound) — Gemini independently + unanimously flags it.
- Directional precision: of what Gemini flags unanimously, 100% is in Claude's core for narcissus/analogic/z-gap; eddy is §4-area agreement at finer granularity (exact-match scores 0); ploidy reached no Gemini core.
- Cross-vendor Jaccard 0.177 (least robust; ceiling + style + granularity confounds).

**Conclusion**: PARTIAL generalization concentrated on top critiques. The most consequential structural critiques are model- and vendor-robust; the long tail is model-specific. Do NOT claim universality. Dovetails with the 3-version finding: stable top-tier, vendor/version-dependent depth.

**Paper**: §6 "Model specificity" item expanded to "...and cross-vendor generalization" with the Gemini numbers and the §2.1 cross-vendor reproduction.

**Bug fixed**: ploidy run-4 hit exit 5 (stochastic JSON parse fail) and the batch bailed at 24/25; manual re-run parsed cleanly. Corrected the gemini batch failure taxonomy: output-parse failures (5/6/7) are TRANSIENT (retry, capped), only model-not-found (4)/mismatch (8) bail.

**Cost**: Gemini CLI uses Google credentials (no Claude-Max spend), reports no USD; ~26k in / ~1.3k out / ~3k thinking tokens per cell.

---

## 2026-06-04 -- Research-quality verification: corrected a verification overclaim (Melo)

**Context**: User challenged me to verify the research quality and, specifically, to second-level-verify any "ghost author / hallucination" finding before declaring it fake — citing a pattern where I report real things as false because my own search failed.

**Method**: Two-directional web verification (fetched in-session, 2026-06-04) of every checkable citation claim: (A) confirm the claimed real author exists, (B) search for a competing real paper under the "fabricated" name.

**Findings**:
- §2.2 citation 1 (12-LMIC play study): CONFIRMED. Real = Iannelli, Naderbagi et al. (Nature HSSC 2025). No "Atabey" 12-LMIC paper exists.
- §2.2 citation 2 (Folk in the Age of Algorithms): CONFIRMED. Real = Flinterud (Folklore 134(4), 2023). Blank & Kitta wrote a *different* book (Folk Culture in the Digital Age) — title-conflation. Holds.
- §2.2 citation 3 (Roblox/CfDS): PARTIAL — institution (UGM not UI) / format (blog not report), NOT an author hallucination.
- §2.2 citation 4 (Melo, memetic performance): **INDETERMINATE**. No Melo paper found across repeated searches, but absence != fabrication. The paper's own table correctly says "(unverified)".
- My own added citations (Kerr 1998, Wei 2024 arXiv 2308.03958, Lakens 2017, Faul 2007): ALL real, metadata exact (pages + arXiv IDs verified). I did not introduce ghost citations.
- Narcissus bibliography spot-check (Perez 2212.09251, Sharma 2310.13548, Liu TACL 12:157-173, Nickerson RGP 2(2):175-220): ALL real, metadata exact.

**The real defect found was in MY OWN prior work, not the paper**: experiments/results/hallucination-verification-2026-05-21.md had labeled citation 4 "HALLUCINATION CONFIRMED" and aggregated "4/4 = 100%" — converting "could not find it" into "confirmed fabricated," the exact inverse error the paper studies. The narcissus paper itself was MORE careful (table marks Melo "unverified").

**Corrections applied**:
- hallucination-verification doc + CSV: citation 4 -> INDETERMINATE; aggregate retracted from "4/4=100%" to "2 confirmed author-misattributions, 1 partial (institution/format), 1 indeterminate"; added a process-claim limit (we verify end-state authorship, not that the AI generated the name — git history partially lost).
- paper abstract + §2.2: "all four ... fabricated author names" -> "two confirmed author-misattributions, one institutional/format discrepancy, one unverifiable," with an explicit "could not find it != confirmed fabricated" note.

**Not verified this session (flagged, not asserted)**: §2.4 "9 of 11 z-gap references had author errors" — would require auditing z-gap's actual bibliography; left as the original single-rater claim (already labeled exploratory per C6).

**Why**: The paper's load-bearing hallucination examples (Flinterud, Iannelli) survive rigorous two-directional verification — they are real, not my false-positives. But a paper about directional hallucination must not itself over-label an unverifiable case as confirmed, and neither must its verification artifacts. Accuracy tightened in both directions: the confirmed cases stated as confirmed, the unverifiable case stated as unverifiable.
