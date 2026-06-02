# 프로젝트 컨텍스트: 범용 Dexterous Manipulation — 단기 PEFT 실험 + 장기 Genesis식 Full-Stack

> 이 문서는 별도 세션에서 정리된 의사결정 기록이다. 코딩·실험 설계 중 적응(adaptation)
> 기법 선택의 분기에서 배경지식으로 참조할 것.
> 핵심 구조: **단기(올해)는 공개 백본+시판 로봇으로 PEFT 실험**, **장기는 Genesis식 full-stack**.
> 두 시계(time-horizon)가 충돌하지 않도록 단기 실험을 "병목 진단 프로브"로 설계하는 것이 요체.
> "확정되지 않은 결정" 항목은 사용자에게 되물어 확정한 뒤 진행할 것.

---

## 0. 프로젝트 전제 (사용자 설정)

- **목표**: 범용 dexterous manipulation. **지향점은 Genesis AI** (full-stack 시스템).
- **시간 구조 (중요)**:
  - **단기 (~올해 말)**: 공개 백본(π0/OpenVLA/SmolVLA 등) + 시판 로봇으로 무언가를 돌리고 있어야 함.
    → 이 구간에서 **PEFT(VLM freeze + LoRA/adapter)가 1급 시민**.
  - **장기**: 자체 하드웨어 + 자체 데이터 엔진 확보 가능한 입장이나, 근시일 내 일 아님(시간 소요).
    → 확보 시 Genesis식 full-stack으로 무게 이동, PEFT는 부차화.
- **사용자의 단기 실용 동기**: "VLM freeze + LoRA를 일단 해보자. 똥인지 된장인지 직접 해본다.
  이 분야의 허들이 무엇인지 알아본다." → 이 동기는 타당. 단 실험의 해석 틀을 명확히 할 것(아래 4번).

---

## 1. PEFT 계보 (갱신 자유도 큰 순서)

관통 trade-off 단 하나: **갱신 자유도(표현력) ↔ 비용(메모리·저장·추론지연)**.

- (a) **Full FT**: W 전체 갱신. 자유도·비용 최대. 기준선.
- (b) **Partial/selective**: 일부 레이어/bias만 (BitFit). 가장 단순.
- (c) **Adapter** (Houlsby 2019): 레이어 사이 병목 모듈 삽입, 그것만 학습. 추론 지연 약간 추가.
- (d) **Reparameterization = LoRA 가계** (지배종): ΔW=BA 저랭크 근사, W'=W+γ·BA. 병합 시 추론 지연 0.
  - QLoRA(4bit 양자화), AdaLoRA(레이어별 rank 적응), DoRA/rsLoRA(안정성), LoRA-SP/LoRA-MoE(로보틱스 멀티태스크).
- (e) **Prompt/Prefix tuning**: 가중치 불변, 입력 측 연속 토큰만. 최고 효율이나 일반화·대규모서 약함.

**LoRA가 지배종인 이유**: 병합 가능 → 추론 지연 0 + 어댑터 모듈성이라는 특이점.
**로보틱스 함정**: VLA는 intrinsic rank가 높음(r≈128 또는 near-full). LLM(r∈{4,8})과 달리
LoRA의 효율 이점이 작다. "분포에 가깝다"가 "저랭크로 적응된다"를 보장하지 않음.

---

## 2. 두 회사의 사전학습 접근법과 차이

두 회사 모두 "사전학습 결정적" 결론 공유. **원료**와 **검증**에서 갈림.
네 소스 어디에도 PEFT/LoRA/adapter/freeze가 **적응 기법으로 등장하지 않음** (의도된 부재, 3번 참조).

### Generalist AI — "로봇 데이터 없는 사전학습"
- GEN-0: 로봇에서 phase transition 최초 보고. 1B=ossification(흡수 실패), 6B=멀티태스크 발현,
  7B+=대규모 사전학습 내재화→수천 step post-training으로 전이.
- GEN-1(5개월 뒤) 핵심: **사전학습에 로봇 데이터 0**. 인간 wearable로 수백만 활동 수집.
  → 적응 시 "로봇 embodiment와 task에 **동시에** 처음 적응"(분포 내 조향 아님, intrinsic rank 높은 상황).
- 사전학습 가치 ablation (로봇청소기 수리): from-scratch 2% → GEN-0 50% → GEN-1 99%.
  전체 평균: from-scratch 19% → GEN-0 파인튜닝 64%(production 미달) → GEN-1 99%(production).
- 적응 데이터: task당 ~1시간. GEN-1은 GEN-0 대비 10배 적은 데이터로 비슷한 성능 가능.

### Genesis AI (지향점) — "인간 데이터 + 하드웨어로 gap 닫기 + 시뮬레이션 평가"
- 원료: 글러브(고정밀 손+촉각) / 에고센트릭 비디오(자연 행동+다양성) / 3인칭(인터넷 스케일).
  세 소스가 quality-quantity Pareto frontier 분담. 로봇 데이터는 정렬용 소량.
- **하드웨어로 embodiment gap 닫음**: Genesis Hand 1.0 = 인간 손 1:1, 20 active back-drivable DoF,
  soft-contact 소재 → retargeting 제거, 인간 시연서 거의 무손실 전달.
  명제: "하드웨어는 모델의 하류가 아니라, 올바른 데이터를 확장 가능하게 만드는 것."
- 모델: 언어·비전·proprioception·촉각·action의 trajectory joint distribution을 flow matching으로.
- **검증 = 시뮬레이션 closed-loop** (Genesis World 1.0): 데이터 생성보다 **평가를 먼저** 품.
  - 이유: "측정할 수 있는 것만 개선 가능, 평가가 iteration의 ceiling."
  - 학습/평가 분포 분리(시뮬레이션 데이터를 사전학습에 안 씀) → 신호 오염 방지.
  - 결과: 시뮬레이션 평가가 실제 하드웨어 rollout과 **89% 상관**(Pearson 0.8996).
  - Genesis World/Nyx 렌더러/Quadrants 컴파일러는 **GitHub 공개** (genesis-world, genesis-nyx, quadrants).
- 적응 데이터: task당 ~20–30분.

### 공유 철학 — open-loop의 함정 (둘 다 강조)
- open-loop 지표(고정 데이터셋 위 action 예측 R²·MAE)는 실세계 성능 차이를 반영 못 함.
  좁은 band 들어오면 모델 간 구분 불가. **closed-loop(action이 미래 관측에 영향)가 유의미.**
- validation loss만 보면 "똥인지 된장인지" 구분 안 됨.

### 한 줄 대비
| | Generalist AI | Genesis AI (지향점) |
|---|---|---|
| 사전학습 원료 | 인간 wearable (로봇 0) | 인간 글러브+에고+3인칭 (로봇 소량) |
| embodiment gap | 모델이 적응 시 흡수 | **하드웨어로 닫음 (1:1 손)** |
| 검증 | 실세계 A/B | **시뮬레이션 closed-loop (89% 상관)** |
| 적응 데이터 | ~1시간 | ~20–30분 |

---

## 3. PEFT가 두 회사 방식에 어떻게 연관되는가

- **부재는 의도적.** 그들이 사는 효율은 PEFT의 compute/memory efficiency가 아니라 **data efficiency**.
  적응 데이터가 1시간·30분이면 full이든 LoRA든 메모리는 둘 다 감당 가능 → LoRA 병목이 1차 아님.
- **적응이 embodiment 학습 포함** → intrinsic rank 높음 → 저랭크 LoRA에 불리.
  (Genesis는 이걸 *하드웨어*로 우회: 1:1 손이면 gap이 작아 적응이 진짜 "조향"에 근접.)
- **병목이 모델 적응 층에 없음.** "조작은 순수 모델 학습 문제로 풀기 어렵고, 시스템을 바닥부터
  함께 설계하면 모델 관점의 어려운 문제가 다른 층에서 더 근본적으로 해결" (Genesis 논지).
- **그래도 PEFT는 내부 어딘가 존재할 개연성** (추정): 둘 다 사전학습 VLM/World Model을 prior로 흡수.
  거대 백본을 full 갱신할 이유 없으니 freeze/저랭크가 구현에 쓰일 것. 단 **서사의 중심이 아님**.
  → PEFT는 그들에게 "도구상자 안 흔한 렌치"이지 베팅 대상이 아니다.

---

## 4. 액션 플랜 — 단기(PEFT 프로브) → 중기(분기) → 장기(Genesis full-stack)

### 단기 (지금~올해 말): VLM freeze + LoRA를 "병목 진단 프로브"로
사용자 동기("일단 해본다, 허들 파악")는 타당. 단 **적응 기법 고르기가 아니라 병목 진단**이 목적.
실험을 3종 세트로 묶을 것:
1. **rank sweep을 1급 실험으로**: r∈{8,32,128,full}. 성능의 rank 반응을 본다.
   - 저랭크서 정체 → task가 분포 내 조향 (LoRA로 충분).
   - rank 올릴수록 계속 향상 → embodiment/분포 gap 큼 (하드웨어·데이터 층 문제).
   - **이 한 실험이 "내 병목이 모델 층이냐 시스템 층이냐"를 진단.**
2. **반드시 closed-loop 평가**: open-loop(val loss)만으론 판별 불가. 실제 로봇 또는
   최소한 perturbation 준 평가에서 성공률을 본다. (두 회사 공통 교훈)
3. **frozen vs unfrozen vision encoder A/B**: 비대칭 적응 가설 검증. 비용≈0, 정보량 큼.
- 결론은 "LoRA가 되더라"가 아니라 **"LoRA가 어디서 깨지더라"**가 수확.

### 중기 (수개월~): 단기 프로브 결과로 분기
- rank 올려도·encoder 풀어도 성능 정체 → 병목=**데이터/embodiment**. Genesis 베팅으로 무게 이동.
- 적응은 되나 closed-loop robustness 붕괴 → 병목=**평가/데이터 다양성**.
  Genesis perturbation taxonomy 소규모 도입: visual(조명·카메라·배경) /
  behavioral(미관측 조합·물체 배치) / semantic(언어 재구성·subtask 순서).

### 장기: Genesis 진짜 모방의 해자(moat)는 적응 기법이 아님
- Genesis 해자 = (a) 자체 하드웨어 1:1 손, (b) 인간 데이터 엔진(글러브), (c) 신뢰 가능한 시뮬레이션 평가.
- **(c)는 부분 공개** (Genesis World/Nyx/Quadrants GitHub). → 장기 모방의 1순위는
  LoRA 튜닝 스킬이 아니라 **closed-loop 시뮬레이션 평가 파이프라인 구축 능력**.
- 사용자는 (a)(b)를 장기 확보 가능. 그 전까지 (c) 역량을 단기부터 키우면 단기-장기가 연결됨.

### 종합 권고
단기에 VLM freeze + LoRA를 하되 **"병목 진단 프로브"로**: rank sweep + closed-loop + encoder A/B.
한 사이클로 "PEFT로 충분한 분포 내 문제냐 vs Genesis가 하드웨어·데이터로 푼 시스템 층 문제냐"를
직접 판별 → 그 결과가 중·장기 베팅 방향을 정함.

---

## 5. 코딩/실험 중 분기점별 기본 판단

- **"LoRA rank 뭘로?"** → 단일 값 금지. sweep(8/32/128/full)이 실험 그 자체.
- **"vision encoder 풀까?"** → 기본 동결 + frozen/unfrozen A/B로 근거 생성.
- **"action head 회귀로 충분?"** → multimodal task면 NO. continuous 생성(flow/diffusion) 고려.
- **"평가 어떻게?"** → val loss(open-loop)만으로 결론 금지. closed-loop 성공률 필수.
- **"공개 백본 뭐?"** → π0(flow, continuous, dexterity 친화) / OpenVLA(discrete token, HF PEFT 지원) /
  SmolVLA(경량). 선택은 아래 "확정 안 된 결정"과 연동.

---

## 6. 반증 조건 (가정이 깨지는 신호 — 관측되면 사용자에게 보고)

- rank 4→16→64 올려도 성능 거의 불변 → 진짜 분포 내 조향. 저랭크 LoRA 충분(권고 과잉).
- rank 올릴수록 성능 계속 향상 → 사전학습이 못 담은 것 요구. "분포에 가깝다" 전제 자체 의심.
  적응 기법 아니라 **사전학습 데이터/embodiment** 재검토 신호.
- **GEN-1식 격차(2%→99%)는 사용자 환경서 재현 안 됨**: 그 수치는 50만 시간 사전학습 산물.
  공개 백본+시판 로봇+소규모 데이터 베이스라인은 훨씬 아래서 시작. 역설적으로 사전학습이 약한 초기엔
  full FT나 데이터 추가가 LoRA 튜닝보다 더 크게 움직일 수 있음.
- "closed-loop 항상 옳다"도 비용 측면 조건부: 실제 로봇 closed-loop는 느림. Genesis World급 시뮬레이션을
  단기 구축 어려움. 단기엔 소수 실제 rollout + 수동 perturbation으로 시작. 완벽한 평가 기다리다
  실험 못 하는 게 더 나쁨.
- 동시 멀티태스크 시 negative transfer 가능. LoRA-MoE조차 멀티태스크서 표준 LoRA 일관 능가 못 함
  → 깔끔한 정답 없음, 실험으로 결정.

---

## 7. 확정되지 않은 결정 (작업 전 사용자 확인 필요)

1. **어떤 공개 백본을 베이스로?** π0(continuous/flow) vs OpenVLA(discrete/HF PEFT) vs SmolVLA(경량).
   - 다룰 task가 multimodal·고정밀이면 continuous(π0류) 우세.
   - HF PEFT 생태계로 LoRA 빨리 붙이려면 OpenVLA가 편함.
2. **어떤 시판 로봇 / end-effector?** 그리퍼 vs 다지 손. embodiment gap 크기를 직접 좌우.
   장기 자체 하드웨어(1:1 손)와의 거리도 고려.
3. **다룰 task의 action 분포가 multimodal한가?** (같은 상황 복수 정답 궤적)
   YES → action 표현(continuous) 선택이 full vs 고랭크 LoRA 논쟁보다 ceiling 좌우.

---

## 8. 참조 소스

- **GEN-0** (Generalist, 2025-11): 10B+, 270,000h 인간 wearable. phase transition(7B), 스케일링 법칙.
  generalistai.com/blog/nov-04-2025-GEN-0
- **GEN-1** (Generalist, 2026-04): 50만 시간+, 로봇 데이터 0 사전학습. mastery(신뢰성·속도·즉흥성),
  from-scratch 19%→사전학습 99%. generalistai.com/blog/apr-02-2026-GEN-1
- **GENE-26.5** (Genesis, 2026-05): 인간 데이터 사전학습 + Genesis Hand 1:1 + flow matching joint dist.
  task당 20-30분. genesis.ai/blog/gene-26-5-advancing-robotic-manipulation-to-human-level
- **Genesis World 1.0** (Genesis, 2026-05): 시뮬레이션=평가/iteration 엔진. 89% 실세계 상관, 평가 우선.
  Nyx/Quadrants. genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-...
- 보조: π0(Physical Intelligence, flow+action expert), OpenVLA(7B, discrete, HF PEFT LoRA 지원).
