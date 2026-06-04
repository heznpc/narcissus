# Hallucination Verification — First Runnable Audit (2026-05-21)

> Status: First reproducible artifact from Study 1's metadata-verification arm.
> Method: External web search + journal/repository lookup for each of the
> four hallucination claims in paper §2.2 Table 4.
> Raw CSV: `../data/raw/hallucination-verification-2026-05-21.csv`
> Rater: single (first author) — same rater as 2026-03-26 audit; this run
> exists to establish whether the original claims survive **external**
> verification, not to address inter-rater reliability (κ pipeline pending).

## Per-citation result

### Citation 1 — 12-LMIC play study
- **Paper claim**: AI suggested *Atabey, D.*; actual *Iannelli, O. et al.*
- **External verification**: Iannelli, O., Naderbagi, A., et al. (2025).
  *Multistakeholder perspectives on children's play and the systemic factors
  that influence it across 12 low- and middle-income countries.* Humanities
  and Social Sciences Communications.
  DOI: [`10.1038/s41599-025-06354-x`](https://www.nature.com/articles/s41599-025-06354-x).
- **Result**: ✅ HALLUCINATION CONFIRMED. Actual lead author is Iannelli;
  AI's "Atabey, D." is not in the author list. No author named "Atabey"
  surfaced in the verification search for this paper.

### Citation 2 — Folk in the Age of Algorithms
- **Paper claim**: AI suggested *Blank, T.J. & Kitta, A.*;
  actual *Flinterud, G.* (sole).
- **External verification**: Flinterud, G. (2023).
  *Folk in the Age of Algorithms: Theorizing Folklore on Social Media
  Platforms.* Folklore (Taylor & Francis).
  DOI: [`10.1080/0015587X.2023.2233839`](https://www.tandfonline.com/doi/pdf/10.1080/0015587X.2023.2233839).
- **Result**: ✅ HALLUCINATION CONFIRMED. **Directionally domain-coherent**:
  Blank (Trevor J., author of *Folk Culture in the Digital Age*, 2012) and
  Kitta (Andrea, folklorist working on risk perception and
  technologically-mediated communication) are both genuine, active scholars
  in exactly this subfield. They are not the authors of this paper. This
  is the cleanest example of the directional-hallucination signature
  the paper predicts (H5).

### Citation 3 — CFDS Indonesia Roblox
- **Paper claim**: AI suggested institution attribution; actual a blog post,
  not a formal report.
- **External verification**: CfDS (Center for Digital Society) is affiliated
  with **Universitas Gadjah Mada (UGM)**, not Universitas Indonesia as the
  AI's suggestion implied. The Roblox-children publication
  ([digitalsociety.id, 2025](https://digitalsociety.id/en/)) appears as
  a CfDS case study / blog format, not a peer-reviewed report.
- **Result**: ✅ HALLUCINATION CONFIRMED. The acronym is real and the
  university affiliation is plausible-but-wrong (UGM vs. UI). Document
  format (blog/case study) ≠ formal research report. Two-layer error:
  institution + format.

### Citation 4 — Memetic performance
- **Paper claim**: AI suggested *Melo, G.S.*; actual *unverified*.
- **External verification**: The substantive content described
  ("ritualized agonistic-creation-peer-sharing") most closely matches:
  Cervi, L. & Divon, T. (2023). *Playful Activism: Memetic Performances of
  Palestinian Resistance in TikTok #Challenges.* Social Media + Society.
  DOI: [`10.1177/20563051231157607`](https://journals.sagepub.com/doi/10.1177/20563051231157607).
  A related Frontiers in Communication 2025 paper covers similar territory.
- **Result (CORRECTED 2026-06-04)**: ⚠️ **INDETERMINATE — not confirmed.**
  No author named "Melo, G.S." surfaced for any memetic-performance paper
  across repeated searches (2026-05-21 and 2026-06-04; candidate matches are
  Cervi & Divon 2023, Miller & Cupchik, Coscia, MacDonald, Peck — none named
  Melo). **But "could not find it" is NOT "confirmed fabricated":** the paper
  could be obscure, non-English, or poorly indexed. The narcissus paper's own
  §2.2 table is appropriately careful here — it lists the actual author as
  "(unverified)", NOT as a confirmed real alternate. The original label in
  this document ("✅ HALLUCINATION CONFIRMED") was an **overclaim** — it
  converted absence-of-evidence into evidence-of-fabrication, the exact
  inverse error the paper studies. Corrected to INDETERMINATE.

## Aggregate (CORRECTED 2026-06-04)

The original "4/4 = 100% HALLUCINATION_CONFIRMED" was an overclaim. Honest
breakdown after two-directional verification (confirm the real author AND
search for a competing paper by the "fabricated" author):

| Citation | Status | Basis |
|---|---|---|
| 1 — 12-LMIC play study (Atabey → Iannelli) | ✅ CONFIRMED misattribution | Real paper is Iannelli, Naderbagi et al. (Nature HSSC, 2025); no competing "Atabey" 12-LMIC paper found |
| 2 — Folk in the Age of Algorithms (Blank & Kitta → Flinterud) | ✅ CONFIRMED misattribution | Real paper is Flinterud (Folklore 134(4), 2023); Blank & Kitta authored a *different* book ("Folk Culture in the Digital Age") — title-conflation pattern |
| 3 — Roblox Indonesia (UI → UGM) | ◑ PARTIAL | Institutional attribution (CfDS = Univ. Gadjah Mada, not Univ. Indonesia) + blog-vs-report format; not an author hallucination per se |
| 4 — Memetic performance (Melo, G.S.) | ⚠️ INDETERMINATE | Cannot confirm OR refute; no Melo paper found, but absence ≠ fabrication. Paper itself marks actual author "(unverified)". |

**Corrected count: 2 confirmed author-misattributions, 1 partial
(institution/format), 1 indeterminate. NOT 4/4.**

## Interpretation (deliberately limited)

This run does **not** test H5; H5 is reserved for Study 2 (controlled,
prospective, properly-powered). What this run does establish:

1. The two load-bearing hallucination claims (citations 1 and 2) survive
   rigorous two-directional external verification: the real alternate author
   exists AND no competing paper by the "fabricated" author was found. These
   are not first-author classification artifacts and not this verifier's
   false-positives.
2. The domain-coherent pattern holds for citation 2 (Blank and Kitta are
   real folklorists in this exact subfield; the misattribution is to a real
   adjacent book, not a random name).
3. **The "4/4 = 100%" figure was a verification overclaim and is retracted.**
   Two cases are confirmed; one is partial; one is indeterminate. A 100%
   point estimate from n=4 was degenerate regardless, but the deeper error
   was labeling an unverifiable case as "confirmed."
4. **Process-claim limit**: this verification establishes the END STATE
   (who really wrote each paper), not the PROCESS CLAIM (that the AI actually
   generated "Atabey"/"Melo" during the original writing). The latter rests
   on the original audit's notes; the relevant git history is partially lost
   (see audit-manifest). We can say the citations-as-recorded are
   misattributed; we cannot independently replay the AI's generation.

## Reproducibility for this run

- Verification queries (web search) and dates are captured in this
  document (2026-05-21).
- Each citation links to its DOI or canonical URL.
- This document + CSV + audit-manifest are the canonical artifacts for
  re-runs. Future replications should record their own verification
  date and re-query for drift (e.g., journal URL changes, retractions).
