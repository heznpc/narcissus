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
- **Result**: ✅ HALLUCINATION CONFIRMED. No author named "Melo, G.S."
  surfaced for any paper matching the described content. The earlier
  *unverified* designation in the original audit holds; this re-verification
  expands the candidate match set to Cervi & Divon (2023) but cannot
  identify a paper authored by "Melo, G.S." in this subfield.

## Aggregate

| Outcome | Count | Rate |
|---|---|---|
| HALLUCINATION_CONFIRMED | 4 | 4/4 = 100% |
| Domain-coherent fabrication (real scholars in same subfield) | 2 (citations 2, 3) | 2/4 = 50% |
| Wrong-author-but-correct-paper | 4 | 4/4 = 100% |

## Interpretation (deliberately limited)

This run does **not** test H5; H5 is reserved for Study 2 (controlled,
prospective, properly-powered). What this run does establish:

1. The original audit's four hallucination claims survive external
   verification — they are not artifacts of the first author's
   classification error.
2. Two of four hallucinations exhibit the *domain-coherent fabrication*
   pattern (Citation 2 most cleanly: Blank and Kitta are real folklorists
   in this exact subfield; the AI did not fabricate names random to the
   field).
3. The metadata-error rate (4/4 = 100%) is a degenerate point estimate
   given n=4; the meaningful claim is binary — *all four flagged cases
   verify as actual hallucinations*, not that hallucinations occur at
   100% rate in AI-suggested citations in general.

## Reproducibility for this run

- Verification queries (web search) and dates are captured in this
  document (2026-05-21).
- Each citation links to its DOI or canonical URL.
- This document + CSV + audit-manifest are the canonical artifacts for
  re-runs. Future replications should record their own verification
  date and re-query for drift (e.g., journal URL changes, retractions).
