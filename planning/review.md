# narcissus — Review (2026-04-11)

## 1. 커밋 톤이 주장을 일관되게 지지하는가?

**판정: 평가 불가 (commit 2개) — 그러나 *증거 데이터 문서가 commit 1번에 동시 import*돼 있어 self-validation이 강함.**

```
ef448d1 chore: add .zenodo.json for DOI minting                          (2026-04-07)
67995d4 Initial commit: Narcissus paper outline and citation analysis    (2026-03-28)
```

진화 패턴:
- **t=0 (3/28)**: outline.md(167줄) + citation-directionality-analysis.md(86줄) + 후속 main.tex(495줄)이 모두 들어옴. README + outline + 데이터 분석 문서 + LaTeX paper가 *동시 import*.
- **t+10 (4/7)**: Zenodo DOI minting 준비 (.zenodo.json).

톤 일관성:
- 핵심 주장(collaborative entrenchment + Narcissus Loop + Fresh ≠ Deep + architectural countermeasure)이 README → outline → citation analysis → main.tex 모든 layer에서 일치.
- **자기 portfolio 데이터를 *증거*로 사용**: 5개 paper(analogic-appropriation / z-gap / villagent / eddy / ploidy)에 대한 3-session 자연 실험. 12 confirming citations / 0 challenging / 4 directional hallucinations / 9-of-11 author misattributions를 *raw data*로 paper §2에 직접 통합.
- *통계 retraction*은 안 했지만 (meta paper에서 처리), 본 paper는 *quantification* 강조 (12/0, 9/11, 100%). 그러나 N=1 portfolio라는 한계는 §10에서 인정.
- **Companion paper 관계**: meta가 first-person reflexive account, narcissus가 third-person empirical paper. 같은 데이터의 *두 형태*. 명시적으로 §1에서 분리 언급.
- 단점: commit 2개로는 *어떤 점이 진화했는지* 알 수 없음. 또한 4/7 commit 이후 4/11까지 0 commit 정체.

## 2. 부가 서비스 품질

**판정: 부가 서비스 0개. 그러나 *Citation Directionality Analysis 데이터 문서*가 본 survey 21개 중 *raw evidence document로서 가장 가치 있음*.**

레포 구성:
- `paper/main.tex` (495줄, ~30KB) — 빌드 PDF 존재
- `outline.md` (167줄), `citation-directionality-analysis.md` (86줄)
- `README.md`, `TODO.md`, `.zenodo.json`, .gitignore

서비스 1: **`citation-directionality-analysis.md`** (86줄)
- analogic-appropriation / z-gap / villagent 3개 repo의 git diff origin/main → HEAD에서 *수동 분류*
- 12개 인용을 confirming/challenging/neutral/placeholder로 분류
- 4개 hallucinated author 명시: "Atabey → Iannelli", "Blank & Kitta → Flinterud (sole)", CFDS, Melo
- *Post-correction comparison*: counter-citation 0→6, hallucinated authors 4→0
- raw data가 코드는 아니지만 *완전히 reproducible* (git diff 명시 + 수동 분류 매트릭스)

코드/노트북/대시보드/instrument — *전무*. caching/elixir의 자동화 코드 같은 인프라는 없음.

특이점:
- TODO.md(56줄)의 6개 experiment proposal이 명료. 가장 가치 있는 것은 #1 (Context vs Sycophancy 분리 4-condition design) — collaborative entrenchment의 메커니즘 분해.
- ploidy(별도 repo)가 *architectural countermeasure*로 명시. cross-repo dependency.
- meta(별도 repo)와 *데이터 공유* 관계. *narcissus가 데이터, meta가 경험* 분리.

## 3. 고도화 가능 파트

높은 우선순위:
1. **Experiment #1 (Context vs Sycophancy 분리 4-condition)** — TODO의 가장 critical. Deep session 편향이 (a) 누적 컨텍스트 때문인지, (b) sycophancy 때문인지, (c) 둘 다인지 분리. 4-condition design으로 가능. **이게 paper의 가장 큰 약점(causal mechanism의 분리)을 해결**. 1-2주 작업.
2. **Experiment #4 (도메인 일반화)** — 5개 이상 *AI 외 도메인*(기후/행동경제학/교육기술/생물다양성/사회심리학)에서 동일 audit 반복. **N=1 portfolio limitation 직접 해결**. 본 survey 21개 paper 중 가장 중요한 후속 작업.
3. **Experiment #2 (3-LLM 비교: Claude/GPT-4/Gemini 인용 위조 방향성)** — 위조 hallucination이 *Claude-specific*인지 *LLM general*인지 결정. 4 directional hallucinations만으로는 sample이 작음.
4. **CHI 2027 / FAccT 2027 직접 submission** — venue가 명시. CHI 9월, FAccT 10월 마감. 이론적 기반 + 실증 데이터가 이미 충분.
5. **Anonymization** — main.tex이 `\author{Jiyeon Yoon}`으로 명시 비익명. CHI/FAccT는 double-blind. 익명화 필요.

중간 우선순위:
6. **Inter-rater reliability of citation classification** — 현재 분류가 본인 단독 (Cohen's kappa 0). 1명 reviewer가 random 30% sample을 *blind* 재분류 → kappa 보고. 이게 빠지면 reviewer가 reject.
7. **Three-session natural experiment의 *공식화***: 현재는 retrospective. *Pre-registered prospective design*으로 5개 paper × 3-session → 6개 problem detection rate를 사전 등록 + 기대 power 계산.
8. **Citation hallucination의 *유형 분류***: 현재는 4개 case. (a) 동일 도메인 fake author, (b) co-author swap, (c) entire paper fabrication, (d) URL fabrication 등 분류 schema. paper §3.
9. **Time decay curve (TODO #3)** — Deep session bias가 시간에 따라 어떻게 누적되는지 T0/T1/T2/T3 측정.
10. **Ploidy 도구 통합 worked example** — narcissus paper 본문에서 ploidy 사용으로 *문제가 발견된* 1-2 case의 trace. cross-repo 가치 강화.

낮은 우선순위:
11. References.bib 분리 정리.
12. Zenodo DOI 발급 trigger.
13. 한국어 abstract.

## 4. 학술적 / 시장 가치 (글로벌, 2026-04-11 기준)

### 학술적 가치: **상위권 (working paper 기준 top ~10%, AI methodology 영역 한정 시 top ~5%)**

차별점:
- **Collaborative entrenchment naming**: 인용 가능한 새 용어. confirmation bias + sycophancy 둘 다 *기존 분리된* 개념을 *interaction loop*으로 통합. 인용 anchor.
- **Narcissus Loop formalization**: §3의 feedback cycle이 figure로 visualize. 학술 통상 *그래프*가 인용 surface area를 늘림.
- **Empirical evidence가 매우 구체적**: 5 papers × 3 sessions × 6 issues = 30 cells의 detection matrix. 12/0 confirming citation ratio. 9/11 author error rate. 4 directional hallucinations. **숫자가 paper의 무게**를 만든다.
- **Reflexive paradox**: 본인이 collaborative entrenchment를 *이론화하면서도* 그 함정에 빠졌음을 §4.5에서 인정. self-criticism이 paper의 신뢰도 +1단계.
- **Architectural intervention**: epistemic awareness ≠ behavioral protection이라는 강한 명제. ploidy를 *공식적 countermeasure*로 제시. **단순 problem identification이 아닌 solution까지 제시**.
- **Cross-repo evidence base**: narcissus + meta + ploidy + 5 source papers가 한 연구 프로그램으로 묶임. 인용 surface area 자체 4-5배.

위험:
- **N=1 (single researcher, single LLM, single portfolio)** — 가장 큰 약점. *generalization*에 강한 한계. CHI/FAccT reviewer가 reject 가능. 이는 meta와 동일.
- **Inter-rater reliability 0** — citation classification이 본인 단독. PRISMA-style 검증 표준에 미달.
- **Anonymization 안 됨** — `\author{Jiyeon Yoon}` 명시. CHI/FAccT 표준 위반.
- **Causal mechanism 미분리**: Deep session 편향이 누적 context 때문인지 sycophancy 때문인지, 둘 다인지 분리 안 됨. TODO #1이 이를 해결할 수 있지만 미실행.
- **Time decay 데이터 부재**: collaborative entrenchment가 *언제* 시작되는지의 time course 데이터가 없음.
- **citation hallucination 4 case는 statistical power 부족**. 

게재 전망:
- *CHI 2027 Main Papers*: **realistic, 35-45%**. 시의성 + reflexive practice + architectural intervention 조합 강함. N=1이 약점.
- *FAccT 2027*: **40-50%**. AI fairness/transparency 트랙에 적합.
- *CSCW 2027 Notes/Provocations*: **50-60%**.
- *Big Data & Society*: **50-60%**.
- *AI & Society*: **50-60%**.
- *Patterns* (Cell): perspective track, 40%.
- *PLOS One*: 60-70%.

### 시장 가치: **상위 (실용 가치 매우 높음, 즉시 인용 가능)**

- **AI methodology 담론**: LLM-assisted research에 대한 *fieldnote*. 모든 AI dev tool 회사(Anthropic, OpenAI, GitHub, Cursor, Lovable)의 product 평가에 인용 가능.
- **Replication crisis 영역**: AI 시대 replication crisis 담론의 anchor. Center for Open Science, OSF, BITSS의 자연 후원자.
- **Education**: 대학원생/박사과정생의 *AI 사용 가이드*. r/AskAcademia, Higher Ed 매체 픽업 가능. *cautionary tale* 톤.
- **Tool 마케팅 (positive)**: ploidy 같은 *context-asymmetric debate* 도구의 정당화. 새로운 product category 정의 가능.
- **Peer review 정책**: 학술지의 AI-disclosure policy(NeurIPS 2024, ICLR 2025, Nature 2024)의 학술적 기반 강화.
- **언론**: NYT/Atlantic/Wired/Science Magazine이 좋아할 톤. "AI bias 연구한 학자가 AI bias에 빠졌다" 헤드라인이 viral.
- 한계: 직접 product 가치는 ploidy로 분리. 본 paper는 *학술적 정당화*에 집중.

### 종합 평점 (2026-04-11)

| 축 | 점수 | 코멘트 |
|---|---|---|
| Originality of construct | 9/10 | collaborative entrenchment + Narcissus Loop |
| Quantitative evidence | 8/10 | 12/0, 9/11, 4 dir hallucinations 명료 |
| Self-criticism | 9/10 | reflexive paradox 인정 |
| Methodological rigor | 6/10 | inter-rater reliability 부재 |
| Repo health | 5/10 | 2 commits, no tests, no automation |
| Cross-repo synthesis | 9/10 | meta/ploidy/5 source papers 통합 |
| Submission readiness | 6/10 | LaTeX 빌드 완료, anonymization 미흡 |
| Generalizability (N>1) | 3/10 | N=1 portfolio |
| Practical actionability | 9/10 | architectural intervention 명시 |
| Timing | 10/10 | LLM-assisted research 담론 정점 |
| **Overall (working paper)** | **7.5/10** | "TODO #1, #4만 추가하면 8.5+로 점프" |

핵심 격언: **"Causal mechanism 분리 (TODO #1) + 도메인 일반화 (TODO #4) 두 가지만 추가하면 CHI 2027 main track 가능."** 본 survey 21개 paper 중 *AI methodology의 가장 발전된 critique*. meta가 first-person reflexive, narcissus가 third-person empirical, ploidy가 architectural intervention의 *3-paper trilogy*를 형성. cross-repo 통합 가치가 본 survey 중 가장 강함.
