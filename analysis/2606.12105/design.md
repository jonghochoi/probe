# Design — DAM-VLA: Decoupled Asynchronous Multimodal Vision Language Action model

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DAM-VLA: Decoupled Asynchronous Multimodal Vision Language Action model |
| 링크 | [arXiv:2606.12105](https://arxiv.org/abs/2606.12105) |
| 분석 문서 | [`analysis/2606.12105/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-11 |

---

## 🧮 데이터 계약

시간 축은 절대 좌표가 아닌 **모달리티별 갱신 rate / history 길이**로 기록한다. 핵심은 제어 rate(`f_ctrl`)와 각 모달리티 갱신 rate 의 분리.

- **입력 — Visual** (`primary` + `wrist` RGB): 각 `(B, T_vis, 3, 256, 256)`, `T_vis=16` 프레임, 센서 rate 25 Hz(≈0.64 s 맥락). 학습 시 100 Hz timeline 에서 stride `S=8` 로 sparse 샘플. dtype float, ImageNet-style 정규화(원문 명시 없음 — 가정).
- **입력 — Proprioception**: `(B, T_prop, 8)`, 8-D = 7 joint position + 1 gripper state, 센서 rate 100 Hz, `T_prop=96` 샘플(≈0.96 s). action 토큰과 concat(X-VLA 방식).
- **입력 — Force/torque**: `(B, T_ft, 7)`, 7-D external joint-torque(Franka 내부 추정; 14-D 중 7-D 사용), 센서 rate 100 Hz, `T_ft=96` 샘플. EMA smoothing 후 rolling buffer 누적.
- **입력 — Language**: 토큰열, 에피소드당 1 회 인코딩(정적).
- **출력 — Action**: `(B, s, 8)`, 8-D = 7 joint position + 1 gripper, execution horizon(chunk length) $`s\in\{6,22\}`$ (각 17/8 Hz replanning @200 Hz). 정규화 통계 원문 명시 없음 — 데이터셋 평균/표준편차로 가정.

---

## 🧰 모듈 인터페이스

```python
def modality_latent_buffer(streams: dict[str, Stream]) -> dict[str, Tensor]:
    """모달리티별 latent buffer B = {Z^m}. 각 Z^m ∈ R^{N_m × d} 를
    모달리티별 rate 로 refresh; 미갱신 시 캐시 그대로 read (processed
    but not consumed)."""

def force_encoder(ft_rolling: Tensor) -> Tensor:  # -> Z_ft (N_ft × d)
    """EMA(rolling F/T buffer) → GRU → cross-attention(force registers)
    → 압축 토큰 Z_ft. 매 제어 스텝 갱신, 시각 일정과 독립."""

def visual_memory(frame_embeds: deque) -> Tensor:  # -> Z_mem (N_mem × d)
    """최근 K frame embedding → GRU → learned-query cross-attention
    → N_mem 토큰 Z_mem. sparse 갱신 사이 상수 유지."""

def gca_global(Z_l: Tensor, Z_mem: Tensor, alpha: Tensor) -> Tensor:
    """시각 메모리 전역-gate 경로 (Eq. 1). zero-init scalar alpha."""

def gca_input_gated(Z_l: Tensor, Z_ft: Tensor, W: Tensor) -> Tensor:
    """force 입력의존-gate 경로 (Eq. 2). near-closed sigmoid gate;
    pre-memory-update Z_l 을 query (Eq. 3 직교성)."""
```

- **buffer ↔ action head 계약** — action head 는 매 추론 스텝 buffer 전체를 read; action 생성이 개별 모달리티 갱신 rate 에 block 되지 않음.
- **GCA ↔ backbone 계약** — GCA 는 action expert 의 **매 4 번째 transformer 층**에만 삽입; 사전학습 self-attention 가중치 불변, 새 모달리티는 zero-init 잔차로 action 토큰에만 주입.
- **dual-pathway 순서 계약** — force 경로는 memory 갱신 *이전* 토큰 `Z_l` 을 query(Eq. 3) → 두 경로 직교, cross-modal 엉킴 방지.

---

## ⛓️ 불변식·가정

- (가정 1) — 모달리티별 정보의 **자연 갱신 rate 와 의미 horizon 이 서로 다르다**: force 100–500 Hz/밀리초, vision 3–10 Hz/초 단위. 이 가정이 깨지면(모든 모달리티가 동일 rate) 비동기 buffer 의 이득이 사라진다.
- (가정 2) — GCA gate 의 **zero/near-closed 초기화**가 성립해야 학습 초기 사전학습 표현이 보존된다(α=0, sigmoid near-closed). 비-zero 초기화는 backbone feature 를 즉시 교란.
- (가정 3) — force 경로의 **순수 가산 delta**(Eq. 3, pre-memory token query)가 두 conditioning 경로를 직교로 유지한다. force 가 memory-updated 토큰을 query 하면 시각 맥락과 접촉이 엉켜 고주파 반응성 손실.
- (가정 4) — sparse 갱신 사이 `Z_mem` 이 **상수로 유지되어도 유효**(K 프레임 요약이 단일 스냅샷보다 robust). 장면이 갱신 주기 내에 급변하면 위배.

---

## 📊 하이퍼파라미터·손실

- 시각 메모리 경로(Eq. 1) — α = 학습 스칼라, init 0:

$$Z^{(\ell+1)}=Z^{(\ell)}+\tanh(\alpha)\;\mathrm{CA}\!\bigl(\mathrm{LN}(Z^{(\ell)}),\;Z^{\mathrm{mem}}\bigr)$$

- force 경로(Eq. 2) — σ-gate near-closed init:

$$Z^{(\ell+1)}=Z^{(\ell)}+\sigma\!\bigl(W\,\bar{z}^{\mathrm{ft}}\bigr)\;\mathrm{CA}\!\bigl(\mathrm{LN}(Z^{(\ell)}),\;Z^{\mathrm{ft}}\bigr)$$

- force delta(Eq. 3) — 직교성:

$$\Delta^{\mathrm{ft}}=\mathrm{CA}\!\bigl(\mathrm{LN}(Z^{(\ell)}),\;Z^{\mathrm{ft}}\bigr)-Z^{(\ell)}$$
- 메인 손실: X-VLA backbone 의 imitation objective (원문 명시 없음 — flow/regression head 형태 미상, X-VLA 계승 가정).

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `learning_rate` | `2e-4` | Table 3 |
  | `global_batch_size` | `192` | Table 3 |
  | `training_steps` | `20,000` | Table 3 |
  | `visual_input_rate` | `25 Hz` | Table 3 |
  | `control_rate` | `100 Hz` | Table 3 |
  | `force_input_rate` | `100 Hz` | Table 3 |
  | `proprio_input_rate` | `100 Hz` | Table 3 |
  | `visual_stride S` | `8` | Table 3 |
  | `gca_insertion` | `매 4번째 action-expert 층` | Table 3 |
  | `vlm_refresh_period` | `4 추론 스텝` | §3.2, App. B |
  | `T_vis / T_prop / T_ft` | `16 / 96 / 96` | §3.2 |
  | `execution_horizon s` | `{6, 22}` (17/8 Hz @200Hz) | §4.1, App. F |
  | `K (memory buffer)` | `(원문 미명시)` | §3.2 |
  | `N_mem / N_ft / d` | `(원문 미명시)` | §3.2 |

---

## 🎯 평가 메트릭

- **지표** — task success rate(%) · **임계값** — 태스크당 15 trial 평균 · **비교 baseline** — X-VLA 25(동기), X-VLA 100(naive high-freq), X-VLA$`_{AFM}`$(concat), 그리고 ablation DAM-VLA$`_{/F/M}`$ · DAM-VLA$`_{/F}`$ · DAM-VLA$`_{/M}`$.
- **보조 지표** — SPARC(spectral arc length, 명령 평활성; 낮을수록 매끄러움), tracking lag(s, 명령↔측정 지연; 정규화 교차상관, $`\tau\in[0,0.5]\,\mathrm{s}`$), 평균 episode length(s, demo 대비).
- **핵심 결과** — full DAM-VLA 95.2% vs 최강 동기 baseline 40.95%(2 배+); GCA vs concat 분리 = 95.2 vs 54.3(RQ4).

---

## ✨ 변경 의도 (intent)

기존 VLA 가 vision-language 사전학습에서 물려받은 **단일 동기 클럭**을 버리고, 각 모달리티를 자기 센서 rate 로 갱신·기억하는 **모달리티별 latent buffer + 비동기 read** 로 대체한다. 핵심 차별점은 (1) action 생성을 가장 느린 모달리티(VLM 재인코딩)에서 분리해 제어 주파수로 연속 동작시키고, (2) 새 고주파 모달리티(force)를 flat concat 이 아니라 **gate 형태를 신호 구조에 맞춘 dual-pathway GCA**(시각=전역 gate, force=입력의존 gate)로 zero-init 잔차 주입해 사전학습 backbone 을 보존하는 것. "정보 자체가 아니라 정보가 backbone 에 *어떻게* 들어가는가" 가 성능을 좌우한다는 것이 prior art(동기 force-VLA: TA-VLA/ForceVLA2/TacVLA/FAVLA) 대비 핵심 주장.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — backbone 자체(X-VLA)는 lerobot 비포함이나, GCA dual-pathway 어댑터 + 모달리티별 buffer 는 flow-matching action expert 를 가진 `pi0` / `pi05` / `smolvla` family 위에 어댑터로 얹기 가장 자연스럽다(action expert transformer 층 사이 삽입). force/proprio buffer 는 processor/transforms 단의 비동기 입력 파이프라인으로, 데이터 포맷은 LeRobotDataset(논문도 LeRobot-style 포맷 사용)과 정합.

---

## 🚧 미해결 / 잠정

- backbone(X-VLA)의 action expert 손실 형태(flow-matching vs regression)·층수·토큰 차원 `d` 가 본문 미명시 — `/implement-design` 매핑 시 backbone 스펙에서 확정 필요.
- 메모리 buffer 길이 `K`, 압축 토큰 수 `N_mem`·`N_ft`, GCA cross-attention head 수 등 구조 하이퍼가 원문 미명시 — 가정으로 메움.
- action/force 정규화 통계 출처 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정.
- gate `W` 의 입력이 `mean_pool(Z_ft)` 스칼라라 per-finger 접촉 attribution 손실 — dexterous hand 전이 시 per-finger gate 로의 확장 여부 미해결(P2 D12 와 충돌 가능).
