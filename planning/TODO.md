# Narcissus TODO

> 2026-04-04. AI Mirror 확인편향 실험 설계 + 작업 분류.

---

## Experiments (beta)

> 에이전트 팀 리서치 기반 실험 제안.

### 1. Context vs Sycophancy 분리 실험 (메커니즘 핵심)
- [ ] **4조건 비교로 Deep Session 편향의 구성 요소 분해**
  - Condition 1 (Context Only): Fresh + 이전 대화 요약 제공
  - Condition 2 (Sycophancy Only): Deep + 매 응답마다 명시적 challenge
  - Condition 3 (Full Deep): 표준 Deep Session
  - Condition 4 (Fresh): 통제
  - 각 조건에서 비판 지점 포착 수 측정
  - 결과물: "Fresh가 효과적인 이유" 정량화

### 2. 인용 위조 방향성 분석 (3모델 비교)
- [ ] **인용 위조가 무작위인가, 확인 방향으로 편향되는가?**
  - 3개 저장소의 위조 인용에 대해 Claude/GPT-4/Gemini 검증
  - 정확도 x 방향성(확인/비판) 교차 검정
  - "반대 증거를 찾아" 명시적 프롬프트 후 재시도
  - 결과물: 구조화된 방향적 환각 실증

### 3. 편향 누적 시간 곡선 (T0-T3)
- [ ] **Deep Session이 편향되는 속도 측정**
  - T0(초기), T1(1시간), T2(3시간), T3(6시간) 스냅샷
  - 각 시점에서 Fresh Session 비판 지점 포착 비교
  - 결과물: "Fresh review 스케줄링 최적 간격" 제안

### 4. 도메인 확대 사례 연구 (일반화, N=1 한계 극복)
- [ ] **5개 이상 새로운 주제에서 Fresh vs Deep 비교**
  - AI 외 도메인: 기후, 행동경제학, 교육기술, 생물다양성, 사회심리학
  - 도메인 특성(정치 민감도, 합의 수준)이 편향 강도를 조절하는가?
  - 결과물: "Narcissus 효과의 도메인 일반화" 증거

### 5. 인간 협력자 비교 (기저선)
- [ ] **AI 협력자 vs 인간 공저자의 프레이밍 강화 비교 (n=20-30쌍)**
  - "Narcissus 루프가 AI-특이적인가, 모든 협력에서 발생하는가?"
  - 결과물: Discussion "AI-specific vs universal collaboration bias"

### 6. Ploidy 프로토콜 배포 검증
- [ ] **외부 연구자 5-10명에게 Fresh review 프로토콜 적용 (4주)**
  - 최종 논문의 인용 방향성, 논쟁 균형, 비판적 깊이 blind 평가
  - 결과물: Narcissus 문제의 실용적 해결책 검증

---

## Writing Tasks

### 7. 원고 작성
- [ ] outline.md -> draft_v1.md 초고 작성
- [ ] 기존 데이터 (3-way 세션 비교, 인용 감사) 결과 섹션 작성
- [ ] Ploidy 연계 논증 작성
