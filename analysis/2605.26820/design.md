# Design — Can VLA Models Learn from Real-World Data Continually without Forgetting?

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Can VLA Models Learn from Real-World Data Continually without Forgetting? |
| 링크 | [arXiv:2605.26820](https://arxiv.org/abs/2605.26820) |
| 분석 문서 | [`analysis/2605.26820/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-05 |

---

## 🧮 데이터 계약

이 논문이 내놓는 것은 새 모듈 아키텍처가 아니라, 기존 VLA($`\pi_{0.5}`$) 위에 얹는 **연속 학습 데이터 파이프라인 계약**입니다. 텐서 shape의 절대 좌표보다 작업 stream·버퍼·정규화 기준이라는 의미 단위를 중심에 둡니다.

- **입력 (관측)** — 멀티뷰 RGB: 손목 2 + 외부 2 카메라, 각 480 $`\times`$ 640, 30 Hz. 정규화 가정은 원문 미명시(이미지 측은 base 정책 기본값으로 가정).
- **입력 (언어)** — 작업 지시. 본문에 토큰화·임베딩 세부 미명시(base $`\pi_{0.5}`$ 표준 따름).
- **출력 (action)** — AgileX PiPER 6관절 + gripper, action horizon `T_action = 10`. action은 학습 전 정규화 통계 $`(\mu_k, \sigma_k)`$ 로 표준화.
- **작업 stream** — 순차 도착하는 $`K`$ 개 작업 $`\{T_1,\dots,T_K\}`$, 각 $`T_k`$ 는 데이터셋 $`\mathcal{D}_k`$ (본 실험 $`K=4`$, 작업당 500 trajectory).
- **replay 버퍼** — 용량 $`M = B \cdot |\mathcal{D}_k|`$ 에피소드. 본 적 있는 작업들에 균등 배분, 작업당 최소 1 에피소드 보존: $`b_{i,k}=\max(1, \lfloor M/(k-1)\rfloor)`$.
- **정규화 통계 계약 (load-bearing)** — Strategy-I(기본): 첫 작업 통계 $`(\mu_1,\sigma_1)`$ 를 stream 내내 고정. Strategy-II: 작업별 $`(\mu_k,\sigma_k)`$ (붕괴 원인). causality를 지키려면 통계는 현재 시점까지의 데이터로만 산출한다(미래 누설 금지).

---

## 🧰 모듈 인터페이스

구현 좌표(file:line)는 Layer 2(`/implement-design`)에서 채웁니다. 여기서는 연속 학습 루프의 호출 계약만 기록합니다.

```python
def build_replay_buffer(seen_datasets, buffer_ratio_B, current_task_k):
    """본 적 있는 작업들에 균등 배분해 capacity M=B·|D_k| 의 버퍼를 구성한다.
       작업당 최소 1 에피소드 보존(b_{i,k}=max(1, floor(M/(k-1))))."""
```

```python
def sample_minibatch(current_dataset, replay_buffer, replay_frequency_fr):
    """각 step: 확률 f_r 로 replay_buffer, 1-f_r 로 current_dataset 에서 추출.
       현재 작업의 유효 4000 step 보장을 위해 총 예산은 4000/(1-f_r)."""
```

```python
def freeze_normalization_stats(first_task_dataset):
    """Strategy-I: 첫 작업의 (mu_1, sigma_1) 를 산출해 stream 내내 고정 반환.
       이후 모든 작업·replay 샘플이 이 단일 기준으로 정규화된다."""
```

```python
def continual_sft_step(policy, minibatch, normalization_stats):
    """정규화된 (o, a) 배치에 NLL 손실 L_SFT 로 한 step 최적화.
       base 정책(pi_0.5)의 표준 SFT 경로를 그대로 사용."""
```

- 모듈 경계는 위 네 함수 — 버퍼 구성, 미니배치 소스 샘플링, 정규화 기준 동결, 표준 SFT step — 가 각각 담당합니다. 외부로 드러나는 계약은 하나뿐입니다. **정규화 기준은 replay와 현재 데이터 모두에 똑같이 적용**해야 한다는 것, 이것이 핵심 불변식입니다.

---

## ⛓️ 불변식·가정

- **(불변식 1) 정규화 기준 단일성** — 한 미니배치 안에서 replay 샘플과 현재 작업 샘플이 **동일한** $`(\mu,\sigma)`$ 로 정규화되어야 한다. 어기면(Strategy-II) 동일 action(예: gripper 닫힘)이 서로 다른 정규화 값으로 매핑되어 안정적 action space가 형성되지 않고 ER이 붕괴한다.
- **(불변식 2) causality** — 어떤 시점 $`k`$ 의 통계·버퍼도 미래 작업 $`\mathcal{D}_{>k}`$ 의 정보를 포함하지 않는다. global 통계를 stream 전체로 미리 계산하면 특권적 정보 누설이다.
- **(가정 1) replay 예산의 U자형 민감도** — replay 빈도 $`f_r`$ 와 버퍼 비율 $`B`$ 는 너무 작으면 보존 실패, 너무 크면 plasticity 손실의 U자형 트레이드오프를 가지며, 본 실험에서 $`B=0.2, f_r=0.2`$ 근처가 최적이다.
- **(가정 2) 작업당 유효 step 보존** — replay 도입 후에도 현재 작업이 4,000 유효 step을 받으려면 총 예산을 $`4000/(1-f_r)`$ 로 늘려야 하고, FT 수치는 이 조건에서만 유효하다.
- **(가정 3) 망각의 구조성** — 망각은 파라미터를 고르게 갉아먹지 않는다. visual similarity(예: 두 작업에 공통된 "green")와 action primitive overlap 축을 따라 일어난다.

---

## 📊 하이퍼파라미터·손실

- 손실 식 (NLL SFT, Eq. 1): $`L_{\mathrm{SFT}} = \mathbb{E}_{(o,a)\sim D}[ -\log \pi_\theta(a|o) ]`$
- 평가 지표 식:
  - 평균 점수 (Eq. 2): $`\bar\rho_K = (1/K) \sum_{i=1..K} \rho_{i,K}`$
  - 망각 (Eq. 3): $`\mathrm{NBT}_i = (1/(K-i)) \sum_{j=i+1..K} (\rho_{i,i} - \rho_{i,j})`$
  - 순방향 전이 (Eq. 4): $`\mathrm{FT}_i = \rho_{i,i}^{(\mathrm{CL})} - \rho_i^{(\mathrm{single})}`$
- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `base_policy` | $`\pi_{0.5}`$ | §4.2 |
  | `optimizer` | AdamW + cosine decay | §4.2 |
  | `peak_lr` | $`5\times 10^{-5}`$ | §4.2 |
  | `warmup_steps` | 200 | §4.2 |
  | `final_lr` | $`5\times 10^{-6}`$ | §4.2 |
  | `batch_size` | 128 | §4.2 |
  | `ema_decay` | 0.998 | §4.2 |
  | `action_horizon` | 10 | §4.2 |
  | `steps_per_task` | 4,000 (유효) | §4.2 |
  | `buffer_ratio B` | 0.2 (default; 스윕 {0.002, 0.02, 0.2}) | §5.1 |
  | `replay_frequency f_r` | 0.2 (default; 스윕 {0.05, 0.1, 0.2, 0.5}) | §5.1 |
  | `total_budget` | $`4000/(1-f_r)`$ | §5.1 |
  | `normalization` | Strategy-I (첫 작업 $`(\mu_1,\sigma_1)`$ 고정) | §4.2 |

---

## 🎯 평가 메트릭

- **지표** — `Avg.` 평균 정규화 점수(↑) · **임계값** — 기본 ER 설정에서 단일 작업 baseline의 10%p 이내 유지 · **비교 baseline** — Single-task, Joint training.
- **지표** — `NBT` Negative Backward Transfer(↓, 망각) · **임계값** — No ER의 +80.0 → 기본 ER에서 +5.0 · **비교 baseline** — Sequential FT(No Replay).
- **지표** — `FT` Forward Transfer(↑, 새 작업 전이) · **임계값** — 과도 replay($`f_r=0.5`$)에서 $`-14.7`$ 까지 음전 · **비교 baseline** — single-task 점수.
- **채점 방식** — 작업별 다단계 rubric(Stack Bowl 4 / Hang Cup 4 / Press Button 3 / Fold Towel 5 체크포인트). 원점수를 작업 최대점수로 나눠 0–100 정규화. 평균은 극단 실패를 가릴 수 있어 작업별 점수에 주로 의존.

---

## ✨ 변경 의도 (intent)

기존 연속 학습 연구는 알고리즘 설계(정규화·격리·정교한 CRL 기법)에 머물러 있었습니다. 이 논문은 **시뮬에서 실환경으로 평가를 옮기고**, 망각의 성패가 흔히 간과된 구현 요인 — replay 빈도, 버퍼 다양성, 특히 action normalization 일관성 — 에서 갈린다는 것을 보입니다. 정교한 알고리즘 없이 단순 experience replay(20% 예산)만으로 NBT를 80.0→5.0으로 낮추고, 잘 설정된 순차 학습이 joint multi-task training까지 이긴다 — 이것이 이 논문의 핵심 주장입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — base 정책으로는 `pi05` family가 직접 후보입니다(본 논문이 $`\pi_{0.5}`$ 를 그대로 사용). 단, 본 논문의 알고리즘적 산출물은 정책 아키텍처보다 **학습 루프 + 데이터 파이프라인 계약**(순차 작업 stream, replay 버퍼 샘플러, 정규화 통계 동결) 쪽에 있으므로, 매핑 대상도 policy 모듈보다 dataset / 정규화(`transforms`·normalization stats) / 학습 step 쪽입니다. `flow-matching` action head를 쓰는 `pi0`/`pi05`/`smolvla` 어디에도 동일 정규화-일관성 계약이 적용될 수 있습니다.

---

## 🚧 미해결 / 잠정

- 이미지/언어 측 정규화 가정의 구체값은 원문에 명시 없음 — 가정으로 메움(base $`\pi_{0.5}`$ 표준값).
- 버퍼에서 어떤 에피소드를 저장·축출하는지(선택 정책, FIFO/random/herding 등)는 원문에 명시 없음 — "균등 배분 + 작업당 최소 1 보존"만 확정.
- replay 미니배치 내 replay:current 혼합이 에피소드 단위인지 step 단위 샘플인지 세부는 본문 기술이 모호 — Layer 1 스펙으로 단정하지 않음.
- 총 예산 $`4000/(1-f_r)`$ 가 step 수인지 epoch 환산인지의 정확한 회계는 §5.1 서술 범위 내로만 확정.
