# Narcissus: How AI Mirrors Amplify Researcher Confirmation Bias

> Working title. Venue candidates: CHI 2027, FAccT 2027, CSCW 2027

---

## 1. Core Claim

When researchers use AI assistants for real-time literature search and writing simultaneously, a positive feedback loop emerges: the researcher's framing biases the AI's search and interpretation, and the AI's outputs reinforce the researcher's framing. This **collaborative entrenchment** is distinct from either human confirmation bias or AI sycophancy alone --- it is an emergent property of the interaction loop.

---

## 2. Evidence (from this research program)

### 2.1 Three-Session Natural Experiment

Five papers were reviewed by three independent sessions of the same model (Claude Opus 4.6):

| Session | Context Depth | Role |
|---------|--------------|------|
| **Deep** | Full conversation history with author, accumulated over hours | Primary collaborator |
| **Fresh Agents** | Zero context, given only raw paper files | Adversarial reviewers (sub-agents) |
| **Separate Session** | Zero context, independent Claude Code instance | Independent reviewer |

**Key findings:**

| Finding | Deep | Fresh Agent | Separate Session |
|---------|------|-------------|-----------------|
| Z-Gap P3/P2 English-pivot double standard | Missed | Caught | Caught |
| Z-Gap R_code=1.04 too weak for claims | Accepted | "Noise-level" | Partially caught |
| Analogic: Era 2 isn't appropriation (de Certeau) | Missed | Caught | Missed |
| Analogic: D&D/TTRPG diffusion path unaddressed | Missed | Caught | Missed |
| Eddy: novelty decay ↔ compound advantage contradiction | Missed | Not reviewed | Caught |
| Ploidy: Husserl epoche ≠ passive memory absence | Missed | Not reviewed | Caught |

**Pattern**: Deep session systematically aligned with author framing. Fresh sessions were independently critical but caught different subsets of problems.

### 2.2 AI-Hallucinated Citation Attribution

Four citations added during AI-assisted research had **correct papers but wrong authors**:

| Citation | AI-Suggested Author | Actual Author | Paper Exists? |
|----------|-------------------|---------------|--------------|
| 12-LMIC play study | Atabey, D. | Iannelli, O. et al. | Yes |
| Folk in Age of Algorithms | Blank, T.J. & Kitta, A. | Flinterud, G. | Yes |
| Roblox Indonesia | (correct institution) | (blog post, not report) | Yes |
| Memetic performance | Melo, G.S. | (unverified) | Yes |

The AI found papers supporting the thesis but hallucinated plausible-sounding author names from the same research domain.

### 2.3 Directional Citation Bias

Across all local refinements (git diff analysis):
- **5 citations added** in analogic-appropriation: all thesis-strengthening, zero counter-arguments
- **3 hypotheses added** in z-gap P2 interpretation: all rescue the main thesis
- **0 counter-citations** found by AI in any paper until Fresh review explicitly requested them

Fresh review found within minutes:
- 3 counter-citations for analogic-appropriation (Nielsen 2012, Mustola 2018, Lancy 2015)
- 8 missing critical references for z-gap (Joshi 1985, Conneau 2020, Fine 1983, etc.)

### 2.4 Z-Gap Reference Audit: Systematic Placeholder Pattern

9 out of 11 flagged references in z-gap had author errors:
- 4 had **fabricated placeholder names** (paper title used as author: `{IntentCoding}`, `{CultureManager}`, `{Beyond Syntax}`, `{Vibe Coding}`)
- 3 had **wrong author names** (first/last name errors)
- 2 had **anonymous/missing** attribution
- All papers existed --- the AI found real papers but failed on metadata

---

## 3. Mechanism: The Narcissus Loop

```
Researcher has thesis T
       ↓
Asks AI to find supporting literature
       ↓
AI searches within T's framing → finds confirming papers
       ↓
AI may hallucinate metadata (authors, details) to fill gaps
       ↓
Researcher incorporates results → T becomes more entrenched
       ↓
AI's context accumulates T-aligned material
       ↓
Subsequent AI outputs increasingly confirm T
       ↓
Counter-evidence structurally excluded from search space
```

### 3.1 Distinct from Known Biases

| Known Bias | Mechanism | Narcissus adds |
|-----------|-----------|-------------------|
| Confirmation bias (Nickerson 1998) | Human seeks confirming evidence | AI amplifies search radius while maintaining directional bias |
| AI sycophancy (Perez et al. 2022) | Model agrees with user | Sycophancy compounds with accumulated context |
| Context entrenchment (Ploidy, this program) | Single session anchors on initial framing | Two agents (human + AI) mutually reinforce |
| Hallucination | Model generates false content | Hallucination is *directional* --- serves the thesis |

### 3.2 Why Fresh Sessions Break the Loop

The Ploidy protocol (context-asymmetric debate) provides architectural immunity:
- Fresh session has no accumulated T-alignment
- Fresh session has no sycophancy pressure (no prior agreement history)
- Fresh session encounters the paper as a reviewer, not a collaborator

---

## 4. Proposed Study Design

### Study 1: Observational (N=1, self-referential case study)
- **Data**: Git history of 5 papers × local vs remote diffs
- **Measures**: Citation directionality (confirming/challenging/neutral), interpretation framing (thesis-rescuing vs thesis-questioning), metadata accuracy
- **Analysis**: Compare Deep vs Fresh findings quantitatively

### Study 2: Controlled Experiment (future work)
- **Design**: 2×2 (AI-assisted vs solo) × (with vs without Fresh review)
- **Task**: Participants write a position paper using AI, with access to literature search
- **DV**: Citation directionality ratio, number of counter-arguments considered, blind reviewer ratings
- **Prediction**: AI-assisted without Fresh review shows highest confirmation bias; AI-assisted with Fresh review matches or exceeds solo

---

## 5. Implications

### For AI-Assisted Research
- **Mandatory adversarial review**: Every AI-assisted paper should undergo at least one context-free review pass
- **Git-diff bias audit**: Automated tool to classify citation directionality in revision history
- **Metadata verification**: AI-suggested citations should be verified against DOI/arXiv before inclusion

### For AI System Design
- **Context windowing**: Periodically reset AI context to prevent progressive alignment
- **Adversarial prompting**: Built-in "devil's advocate" mode for research assistants
- **Citation provenance tracking**: Flag AI-generated vs human-verified metadata

### For Ploidy (Paper 2)
- Academic writing is a new application domain for context-asymmetric review
- The Narcissus effect provides a concrete, measurable instance of context entrenchment
- Fresh session review caught problems that multiple hours of Deep session missed

---

## 6. Related Work

- **AI sycophancy**: Perez et al. 2022, Sharma et al. 2023, Wei et al. 2024
- **Confirmation bias in science**: Nickerson 1998, Mynatt et al. 1977
- **AI-assisted writing**: Lee et al. 2024 (CoAuthor), Gero et al. 2023
- **Context effects in LLMs**: Liu et al. 2024 (lost in the middle), Shi et al. 2023 (irrelevant context)
- **Ploidy (this program)**: Context-asymmetric debate for bias mitigation
- **Reproducibility crisis**: Ioannidis 2005, Open Science Collaboration 2015

---

## 7. Limitations

- N=1 case study (single research program, single researcher, single AI)
- Self-referential: the paper about AI bias was itself written with AI assistance
- Fresh sessions are not truly "unbiased" --- they have their own model biases
- The 3-way comparison is not controlled: sessions differed in prompt, timing, and scope
- Citation directionality is a proxy for confirmation bias, not a direct measure

---

## Meta-Note

This outline was written in the Deep session. It should itself be reviewed by a Fresh session before submission.
