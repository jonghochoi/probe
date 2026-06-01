# Design — AT-VLA: Adaptive Tactile Injection for Enhanced Feedback Reaction in Vision-Language-Action Models

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/2605.07308/analysis.md` 와
> 함께 자동 생성하며, 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | AT-VLA: Adaptive Tactile Injection for Enhanced Feedback Reaction in Vision-Language-Action Models |
| 링크 | [arXiv:2605.07308](https://arxiv.org/abs/2605.07308) |
| 분석 문서 | [`analysis/2605.07308/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

원문은 vanilla GO-1 의 입력 계약을 손대지 않고 잇되, 촉각 모달리티 하나만 추가합니다. 시간 축은 `chunk_size` (= H, action chunk 의 미래 horizon) 와 `dual_stream_ratio` (= 패스트:슬로우 추론 비) 로 표현합니다.

**입력**

- **이미지** `I = {I_h, I_r, I_l}` — head · right wrist · left wrist 3 대 카메라, shape `(B, 3, C=3, H_img, W_img)`, dtype float. vanilla VLM 의 vision preprocessor 를 따르며 정규화는 백본 표준에 위임합니다.
- **언어 명령** `L` — token id sequence, shape `(B, L_lang)`, dtype int. 언어 토크나이저는 vanilla VLM 의 표준 (원문 instantiation 기준 InternVL-2B).
- **촉각** `T` — 합력 (resultant force) 벡터 `(B, T_tac, 6)`. 6 채널 = 3D normal + 3D tangential. 정규화는 원문에 명시되지 않아 디폴트로 데이터셋 전체 평균/표준편차를 씁니다.
- **Proprioception** `S` — robot state, shape `(B, T_prop, D_state)`. 양팔 7-DoF EE pose + gripper state 등 vanilla GO-1 의 state 토큰화 계약을 변경 없이 따른다 (D_state 의 정확한 차원은 원문에 명시되지 않음).

**출력**

- **액션 청크** `A` — 양팔 14-DoF end-effector pose, shape `(B, chunk_size, 14)`. flow-matching 액션 전문가의 출력 분포는 GO-1 과 동일하게 상속합니다.
- **게이트 score** `g_t` — Tactile Gate 의 contact-state score, shape `(B, T_tac)` (또는 매 step 단일 scalar). dtype float `[0, 1]` 이고, 임계값 0.5 를 넘으면 게이트가 ON 으로 전환됩니다.

---

## 🧰 모듈 인터페이스

base 좌표 없이 함수/클래스 시그니처 수준에서 책임만 기록합니다.

```python
def tactile_encoder(T: Tensor) -> Tensor:
    """촉각 합력 6D 시퀀스를 촉각 토큰 z_T 로 매핑한다.
       경량 MLP 만으로 구성해 패스트 스트림 추론 지연을 최소화한다.
       입력 shape (B, T_tac, 6) → 출력 shape (B, T_tac, D_tac)."""

def tactile_gate(z_T: Tensor) -> Tensor:
    """촉각 토큰을 받아 contact / non-contact score 를 산출한다.
       MLP 기반 이진 분류기. BCE 손실 L_g 로 학습.
       임계값 (예: 0.5) 초과 시 다운스트림 cross-attention 의 query 가 z_T 로 전환된다.
       입력 shape (B, T_tac, D_tac) → 출력 shape (B, T_tac, 1)."""

def adaptive_cross_attention(
    z_I: Tensor, z_L: Tensor, z_S: Tensor, z_T: Tensor, gate_on: Bool,
) -> Tensor:
    """게이트 상태에 따라 query 자리를 교체하는 cross-attention.
       gate_on == False : query = z_S       (vanilla VLA 와 동일)
       gate_on == True  : query = z_T       (촉각 토큰이 attention query)
       key/value 는 항상 (z_I, z_L) 로 고정 — 사전학습된 표현 보존.
       출력은 액션 전문가의 다음 블록 입력으로 흘러간다."""

def dual_stream_scheduler(
    obs_stream: ObsStream, fast_ratio: int = 3, slow_ratio: int = 1,
) -> ActionChunk:
    """슬로우 스트림 (VLM, 시각·언어) 1 회 추론 동안 패스트 스트림 (촉각) 을
       fast_ratio 회 연속 추론한다. 슬로우 출력 latent 는 future H 스텝 동안
       cross-attention 의 key/value 로 살아남고, 패스트 출력은 매 step query 를
       갱신해 액션 청크를 산출한다. 게이트 OFF 구간에서는 두 스트림이 동일
       빈도로 작동해 vanilla VLA 와 등가."""

def action_expert(
    cross_attn_out: Tensor, action_query: Tensor,
) -> ActionChunk:
    """vanilla VLA 의 액션 전문가 (본 논문 기준 DiT). 본 모듈은 adaptive_cross_attention
       의 출력만 받기 때문에 구조 변경 없음 — 게이트 OFF 구간에서는 vanilla 그대로,
       ON 구간에서는 query 자리만 z_T 로 바뀐 동일 모듈."""

def at_vla_forward(
    I: Tensor, L: Tensor, T: Tensor, S: Tensor,
) -> Tuple[ActionChunk, Tensor]:
    """전체 forward. 게이트 score 와 액션 청크를 함께 반환한다.
       학습 시 액션 손실 L_a 와 게이트 BCE 손실 L_g 가 동시에 흐른다."""
```

- 모듈 간 호출 계약: `tactile_encoder` 의 출력은 `tactile_gate` 와 `adaptive_cross_attention` (query 후보) 양쪽으로 함께 흘러갑니다. 가중치는 단일 학습 단계에서 액션 손실과 게이트 BCE 손실의 합으로 한 번에 갱신됩니다.
- 사전학습 보존 보장: `adaptive_cross_attention` 은 key/value 가 항상 같습니다. 따라서 게이트가 학습 내내 OFF 였을 경우(즉 비접촉만 본 데이터셋), 가중치 업데이트가 vanilla VLA 와 한 비트도 어긋나지 않는다는 불변식이 성립합니다.

---

## ⛓️ 불변식·가정

- **(가정 1)** 게이트 OFF 구간의 forward / backward 그래프는 vanilla VLA 와 텐서 단위로 같다. 즉 query 자리에 항상 `z_S` 가 들어가야 하며, `z_T` 가 일부라도 섞여서는 안 된다. 이 불변식이 깨지면 원문의 "사전학습 보존" 주장 자체가 무효가 된다.
- **(가정 2)** Tactile Gate 의 label 은 에피소드 시간축에서 두 단계(contact / non-contact)로 깔끔히 나뉜다. 원문은 사람 라벨링을 전제한다. 만약 contact-rich 태스크가 다중 transient contact(예: in-hand rotation 의 finger-switching)로 잘게 쪼개진다면, BCE 라벨 정의 자체가 다중-라벨로 확장돼야 한다.
- **(가정 3)** 슬로우 스트림의 latent 출력은 future $`H`$ 스텝 동안 유효한 조건이다. action chunk 의 horizon $`H`$ 는 슬로우 스트림 한 사이클 길이보다 짧지 않다. `dual_stream_ratio = 3` 으로 두면, 적어도 패스트 스트림 3 회 분량만큼 시간상 일관성이 보장돼야 한다.
- **(가정 4)** 촉각 토큰의 차원은 사전학습 표현 공간을 흔들지 않을 만큼 작다(원문은 합력 6D → 단일 토큰 수준). 고차원 V-T 이미지(예: Sparsh feature)를 단일 토큰화 없이 시퀀스로 풀어 넣으면 본 모델 가설의 전제가 일부 무너진다(Table 3 Ex6 → Ex7 의 마진 축소).
- **(가정 5)** 액션 전문가는 query 자리 교체에 구조가 둔감하다. cross-attention 의 입력 차원 / 출력 차원이 query 종류와 무관하기 때문이다. vanilla GO-1 의 DiT cross-attention 에서는 성립하지만, 다른 액션 전문가 구조(e.g. flow-matching expert with concatenated tokens)에 이식할 때는 별도로 검증해야 한다.

---

## 📊 하이퍼파라미터·손실

- **손실 식** (§3.4)

$$\mathcal{L}=\mathcal{L}_{a}+\lambda_{1}*\mathcal{L}_{g}$$

  - $`\mathcal{L}_{a}`$ — vanilla VLA 의 액션 손실 (flow-matching, GO-1 과 동일).
  - $`\mathcal{L}_{g}`$ — Tactile Gate 의 binary cross-entropy. 라벨은 에피소드 프레임별 0 (non-contact) / 1 (contact) 사람 주석.

- **하이퍼파라미터**

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `gate_loss_weight` (`λ_1`) | `0.01` | §3.4 |
  | `gate_threshold` | `0.5` | §3.2 (예시값으로 명시) |
  | `dual_stream_ratio` (fast:slow) | `3:1` | §3.4 |
  | `closed_loop_latency` | `< 0.04 s` | §1, §3.3 |
  | `chunk_size` (`H`) | (원문에 명시 없음 — 가정으로 메움) — vanilla GO-1 기본값 상속 가정 |
  | `tactile_feature_dim` (force 6D) | `6` (3D normal + 3D tangential) | §3.1 |
  | `tactile_encoder` 구성 | 경량 MLP 다층 (구체 hidden dim 미명시) | §3.1 |
  | `tactile_gate` 구성 | MLP (구체 hidden dim 미명시) | §3.2 |
  | 시연 수 / 태스크 | `30 ~ 50` | §4.1 |
  | 평가 trial / 태스크 | `15` | §4.1 |
  | 옵티마이저 / lr / 배치 | (원문에 명시 없음 — 가정으로 메움) | — |

---

## 🎯 평가 메트릭

- **지표** — sub-task progression 기반 성공률 (각 단계까지 진행한 비율) · **임계값** — vanilla VLA (GO-1) 대비 contact-rich 평균 ≥ +17%p (Ex2 ↔ Ex0) 및 dual-stream 추가 시 추가 ≥ +11%p (Ex3 ↔ Ex2) · **비교 baseline** — GO-1, π0.5, VTLA, RDP.
- **지표** — modality-agnostic 강건성 (동일 가중치, 추론 시 촉각 ON vs OFF 평균 drop) · **임계값** — vanilla VLA 와 동등 (Table 2: AT-VLA w/o. = 0.70, GO-1 = 0.68) · **비교 baseline** — GO-1, π0.5.
- **지표** — 폐루프 응답 지연 · **임계값** — `< 0.04 s` (§1) · **비교 baseline** — vanilla VLA (단일 stream 추론).
- **지표** — ablation 별 평균 성공률 (Ex0 ~ Ex7) · **임계값** — 본 논문 Table 3 의 수치를 직접 (재현 시) 참조 · **비교 baseline** — 각 ablation 의 인접 행 (component 한 개씩 추가/제거).

---

## ✨ 변경 의도 (intent)

기존 tactile-VLA 계열 연구(Tactile-VLA · TLA · TA-VLA · VTLA)는 모두 "촉각을 어떻게 잘 토큰화·정렬해 사전학습 모델이 해석하게 만들까"에 집중했고, 그 과정에서 사전학습 attention 분포가 흩어지는 부작용은 직접 짚지 않았습니다. 본 Design 은 두 결정을 학습형 게이트에 한꺼번에 위임합니다. 촉각을 언제 끼울지는 시간축에서 게이트가 판단하고, 어디에 끼울지는 cross-attention 의 query 자리 한 곳으로 좁힙니다. key/value 자리에는 항상 사전학습된 표현이 흐르고, query 만 게이트 상태에 따라 state ↔ 촉각으로 교체되므로 모듈 차원이나 구조는 바뀌지 않습니다. 이와 함께 시각·언어 슬로우 스트림과 촉각 패스트 스트림은 비동기로 분리합니다. 한 번의 시각·언어 추론 출력은 future $`H`$ 스텝 동안 잠재 조건으로 유지되고, 그 사이 촉각만 고주파로 갱신됩니다. 결과적으로 세 속성이 한 가중치에서 함께 성립합니다. 첫째 사전학습 보존(게이트 OFF 구간이 vanilla 와 등가), 둘째 접촉 반응(패스트 스트림의 0.04 s 폐루프), 셋째 학습 시 본 촉각이 추론 시 사라져도 성능이 유지되는 modality-agnostic 강건성입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` 또는 `pi05` family 가 가장 가깝습니다. 원문의 vanilla VLA 는 GO-1(DiT 액션 전문가 + VLM 백본)이라 π0 계열의 flow-matching 액션 전문가와 구조가 정렬됩니다. cross-attention query 자리 교체는 액션 전문가 forward 내부의 단일 hook 으로 표현할 수 있습니다. 단 GO-1 자체가 lerobot 표준 policy 라인에는 부재하므로, π0 / π0.5 의 액션 전문가에 (1) tactile encoder MLP, (2) tactile gate MLP, (3) adaptive cross-attention query 분기 세 모듈을 추가하는 패턴이 자연스러운 매핑 후보입니다. 데이터셋 측에서는 LeRobotDataset 의 observation key 에 `observation.tactile_force` (shape `(T, 6)`) 추가가 선결 조건입니다.

---

## 🚧 미해결 / 잠정

- `tactile_encoder` · `tactile_gate` 의 구체 hidden dimension / 깊이가 본문에 명시되지 않아 "경량 MLP" 정도로만 두었음. 첫 구현에서는 `[6 → 64 → 128]` 같은 안전한 default 를 잡아 두어야 한다.
- `chunk_size` $`H`$ 의 정확한 값이 본문에 명시되지 않아 vanilla GO-1 기본값을 상속한다고 본다. 슬로우 스트림 latent 가 살아남아야 하는 horizon 길이라 `dual_stream_ratio = 3` 과의 정합성을 함께 점검해야 한다.
- 옵티마이저 / 학습률 / 배치 크기 / 학습 step 수가 본문에 명시되지 않음. 첫 구현에서는 vanilla GO-1 의 fine-tuning 설정을 변경 없이 잇는다고 본다.
- Tactile Gate 라벨링 자동화: 원문은 사람 라벨링을 전제하지만, hardware contact 신호(촉각 에너지 임계 등)로 자동 추출이 가능한지는 다루지 않는다. 첫 구현에서는 사람 라벨 default 와 자동 라벨 옵션을 함께 검토한다.
- 임계값 0.5 의 hysteresis 처리: score 가 0.5 근처에서 빠르게 진동하면 매 step 마다 query 가 바뀌어 액션이 흔들릴 위험이 있다. 원문은 hysteresis / margin 처리를 다루지 않는다.
- 게이트 ON / OFF 전환 시 attention 출력의 discontinuity 처리: 단일 step 에서 query 가 바뀌면 cross-attention 출력 분포가 점프할 수 있고, 액션 청크 경계에서의 motion smoothness 가 보장되지 않을 가능성이 있다. 원문은 이 미시 거동을 다루지 않는다.
- `dual_stream_ratio = 3:1` 외 다른 비율의 비교, 게이트 임계값과의 상호작용, chunk_size 와의 동시 sweep 이 본문에 없다.
