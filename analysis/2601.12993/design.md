# Design — Being-H0.5: Scaling Human-Centric Robot Learning for Cross-Embodiment Generalization

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Being-H0.5: Scaling Human-Centric Robot Learning for Cross-Embodiment Generalization |
| 링크 | [arXiv:2601.12993](https://arxiv.org/abs/2601.12993) |
| 분석 문서 | [`analysis/2601.12993/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-27 |

---

## 🧮 데이터 계약

본 논문의 데이터 계약은 *unified state-action space* 로 못 박는다. 모든 embodiment 의 state·action 을 고정 차원 벡터 $`\mathbb{R}^{d}`$ 의 *semantic slot* 들로 분해한다. embodiment 별 매핑 $`\Phi_e`$ 가 raw 신호를 슬롯에 사영한다 (§5.1.1, §5.2.1).

- **입력 — vision**: `(B, V, 3, 224, 224)` RGB, V = 카메라 수 (예: wrist + 3rd-person), uint8 → float, 정규화는 backbone (InternVL-3.5) 의 image preprocessor 위임. (원문 §7.2 specialist 실험 기준).
- **입력 — text**: tokenized natural-language instruction, 길이 가변. QA-style 직렬화의 query 부분에 포함 (§5.2.1).
- **입력 — state**: `(B, T_state, d)` float, 통합 슬롯 공간. embodiment $`e`$ 의 raw state $`\mathbf{s}^{(e)}`$ 를 $`\Phi_e`$ 로 사영 후 active 슬롯에만 값을, 나머지에는 0 을 채움. 정규화는 *통계 정규화 없음* — Cartesian = world frame 기준 delta displacement, 회전 = Axis-Angle, joint = absolute radian, outlier filtering 만 적용 (§5.1.1).
- **입력 — discrete motion token (학습 시 사람 손 데이터 한정)**: codebook $`\mathbb{C}`$, 길이 `(B, T_z)` long, mask token `[MASK]` 가 비율 $`\rho`$ 로 무작위 적용 (§5.2.3).
- **출력 — action chunk**: `(B, T_action, d)` float, 동일한 통합 슬롯 공간. Rectified Flow 의 종착 분포가 raw physical magnitude 의 액션. embodiment $`e`$ 배포 시에는 inverse 매핑 $`\Phi_e^{-1}`$ 로 active 슬롯만 추출.
- **출력 — discrete motion token 예측 (보조 채널)**: `(B, T_z, |\mathbb{C}|)` logits. masked 위치에 한해 cross-entropy loss.
- **출력 — text logits**: `(B, T_text, V_vocab)` 표준 next-token 분포. VQA / motion description / planning task 의 응답에 사용.
- **시간 축** — `chunk_size` 는 본문 LIBERO 실험에서 8 (§7.2.1). `T_state` 는 proprio 의 short history (논문 본문에 정확한 길이는 명시되지 않음 — *(원문에 명시 없음 — 가정으로 메움)*).

---

## 🧰 모듈 인터페이스

```python
def slot_mapping(raw_signal: Tensor, embodiment_id: str) -> Tensor:
    """embodiment-별 raw 신호를 통합 슬롯 공간의 고정 차원 벡터로 사영"""

def mot_backbone(tokens: dict, modality_tags: Tensor) -> tuple[Tensor, Tensor]:
    """Mixture-of-Transformers: 이해 전문가와 액션 전문가가 self-attention 을 공유하며
       동일 토큰 시퀀스를 처리. (understanding_hidden, action_hidden) 반환"""

def mof_action_expert(action_hidden: Tensor, context_H: Tensor,
                      timestep: Tensor, embodiment_id: str) -> Tensor:
    """Mixture-of-Flow: foundation 층은 모두에 공유, specialized 층은 Top-K
       gating 으로 sparse 활성화. velocity v_theta(a_t; H, e) 반환"""

def mpg_gate(context_H: Tensor, action_anchor_Z: Tensor) -> tuple[Tensor, Tensor]:
    """Manifold-Preserving Gating: SWD 기반 discrepancy → reliability gate g,
       gate-before-projection 으로 H_tilde 생성 (stop-gradient 적용)"""

def uac_sample(embodiment_id: str) -> tuple[int, Tensor]:
    """Universal Async Chunking 학습 시 delay d ~ pi^(e)(d) 샘플,
       per-token timestep 벡터 t_i 반환 — prefix 는 t=1, postfix 는 t_base"""

def esa_update(grad: Tensor, embodiment_id: str) -> Tensor:
    """Embodiment-Specific Adaptation: active slot I_e 에 묶인
       adapter bank W_ESA[k] 만 업데이트, 나머지 슬롯의 gradient 는 0 으로 마스킹"""

def rectified_flow_step(a_prev: Tensor, t: float, H_tilde: Tensor) -> Tensor:
    """Euler step: a^(k+1) = a^(k) + dt * v_theta(a^(k), t^(k) | H_tilde),
       dt = 1/K, K < 10 (실시간 배포 목표)"""

def dual_thread_executor(buffer: RingBuffer) -> None:
    """Control thread = consumer (고정 주기 1/t_control), Inference thread =
       producer (asynchronous, postfix 만 buffer offset d 에 기록).
       Buffer 크기 ≥ 2 × chunk_length."""
```

- **slot_mapping** ↔ Unified State-Action Space (§5.1.1)
- **mot_backbone** ↔ Mixture-of-Transformers, BAGEL 패턴, InternVL-3.5 backbone (§5.1)
- **mof_action_expert** ↔ Mixture-of-Flow, Top-K routing (§5.1.2)
- **mpg_gate** ↔ Manifold-Preserving Gating (§5.3.2)
- **uac_sample** + **dual_thread_executor** ↔ Universal Async Chunking + dual-thread deployment (§5.3.3, §6.2, §6.3)
- **esa_update** ↔ Embodiment-Specific Adaptation (§5.3.1)
- **rectified_flow_step** ↔ §6.1 Manifold-Preserving Refinement

---

## ⛓️ 불변식·가정

- **(가정 1)** — 모든 embodiment 의 raw state·action 은 공통 *semantic slot* 들로 분해 가능하다. embodiment $`e`$ 가 차지하는 슬롯 인덱스 $`\mathcal{I}_e\subseteq\{1,\ldots,K\}`$ 가 사전에 정해진다. partial overlap 슬롯은 자동으로 파라미터를 공유한다.
- **(가정 2)** — 사람 손(MANO) 의 wrist 6-DoF 는 로봇 EEF subspace 와 *물리적으로 동등한 의미* 를 가진다. 손가락 articulation 은 reserved *fine-manipulation* 슬롯에 매핑해도 downstream 정책이 올바르게 해석한다.
- **(가정 3)** — 회전을 Axis-Angle 로 통일하고 위치를 *world frame 기준 delta displacement* 로 두면 SE(3) 매니폴드에서 smooth interpolation 이 보장된다.
- **(가정 4)** — *통계 정규화 없이 raw physical magnitude* 를 그대로 학습해도 액션 분포의 분산이 학습을 망가뜨리지 않는다. 1 radian / 10 cm 같은 *물리 단위 그대로* 가 정책에 의미 있는 신호로 들어간다.
- **(가정 5)** — Rectified Flow 의 선형 보간 경로 $`\mathbf{x}_t=(1-t)\mathbf{x}_0+t\mathbf{a}_i`$ 가 데이터 분포에 충분히 가까워 K < 10 Euler 스텝으로 high-fidelity 액션 생성이 가능하다.
- **(가정 6)** — context feature $`H`$ 가 OOD 일 때 MPG 의 SWD 게이트가 *실제로* 작아져 *prior offset 으로 빠지는 fallback* 이 학습된다 (실패 시 jitter 가 증폭됨).
- **(가정 7)** — embodiment 별 control 주기 $`\Delta t^{(e)}`$ 와 latency budget $`L^{(e)}`$ 가 *학습 시점에 알려져 있다*. 그 분포 $`\pi^{(e)}(d)`$ 가 배포 시 latency 분포와 충분히 일치한다.
- **(가정 8)** — UniHand-2.0 의 사람 영상에서 *HaWoR + MANO* 로 추정한 wrist trajectory 가 *로봇 EEF 의 valid 모션 매니폴드* 와 충분히 겹쳐, *사람 → 로봇* 정책 전이의 시발점으로 동작한다.

---

## 📊 하이퍼파라미터·손실

### 손실 식

전체 손실 (§5.2.2):

$$\mathcal{L}=\lambda_{\text{text}}\mathcal{L}_{\text{text}}+\lambda_{\text{act}}\mathcal{L}_{\text{act}}$$

텍스트 항 (§Eq. 5):

$$\mathcal{L}_{\text{text}}=-\sum_{i\in\Omega_{\text{text}}}\log p_{\theta}(y_{i}\mid\mathcal{S}_{<i})$$

액션 항 (§Eq. 6):

$$\mathcal{L}_{\text{act}}=\lambda_{1}\mathcal{L}_{\text{FM}}+\lambda_{2}\mathcal{L}_{\text{MASK}}$$

Flow-Matching (§Eq. 7):

$$\mathcal{L}_{\text{FM}}=\sum_{i\in\Omega_{\text{FM}}}\left\|v_{\theta}(\mathbf{x}_{t},t,c)-(\mathbf{a}_{i}-\mathbf{x}_{0})\right\|_{2}^{2}$$

Masked Motion Token (§Eq. 8):

$$\mathcal{L}_{\text{MASK}}=-\sum_{i\in\Omega_{\text{MASK}}}\log p_{\theta}(z_{i}\mid c)$$

Post-training UAC 손실 (§Eq. 19):

$$\mathcal{L}_{\text{UAC}}=\sum_{i\geq d}\left\|\hat{v}_{i}-v_{i}^{*}\right\|_{2}^{2}$$

MPG 게이트 식 (§Eq. 13–15):

$$\tilde{H}=H+\lambda g\,\mathbf{W}_{\text{MPG}}\mathcal{E}_{\text{obs}}(H)+\lambda\mathbf{b}_{\text{MPG}}$$

$$g=\exp(-D/\tau)\in(0,1]$$

$$D(\mu_{\hat{H}},\mu_{\hat{Z}})\approx\frac{1}{M}\sum_{m=1}^{M}\left\|\text{sort}(\theta_{m}^{\top}\hat{H})-\text{sort}(\theta_{m}^{\top}\hat{Z})\right\|_{2}^{2}$$

ESA 슬롯 마스킹 (§Eq. 12):

$$\mathbf{W}_{\text{ESA}}^{(e)}\triangleq\{\mathbf{W}_{\text{ESA}}[k]:k\in\mathcal{I}_{e}\},\qquad \Delta\mathbf{W}_{\text{ESA}}[k]=\mathbf{0}\ \ \forall k\notin\mathcal{I}_{e}$$

Rectified Flow Euler 스텝 (§Eq. 20):

$$\mathbf{a}^{(k+1)}=\mathbf{a}^{(k)}+\Delta t\cdot v_{\theta}(\mathbf{a}^{(k)},t^{(k)}\mid H),\qquad \Delta t=1/K,\ t^{(k)}=k/K$$

### 하이퍼파라미터

| 이름 | 값 | 출처 |
|------|----|----|
| Backbone | InternVL-3.5 (2B variant 평가) | §5.1, §7.2 |
| Image resolution | 224 × 224 | §7.2 |
| Camera modality | RGB only (multi-view, wrist + 3rd-person at LIBERO) | §7.2.1 |
| `chunk_size` | 8 (LIBERO) | §7.2.1 |
| `packed_seq_tokens_per_gpu` | 7,680 | §7.2.1 |
| `effective_batch_size` | 128 | §7.2.1 |
| `train_steps` (specialist) | 45,000 (LIBERO), RoboCasa 동일 budget | §7.2.1, §7.2.2 |
| `train_steps` (generalist) | ≈ 2 × specialist | §7.2.1 |
| `gpus` (LIBERO specialist) | 4 × A800 | §7.2.1 |
| `K_flow_steps` (denoising) | < 10 (실시간 배포 위해 강제) | §6.1 |
| `ring_buffer_size` | ≥ 2 × chunk length | §6.3 |
| `simulation_data_fraction` (pretraining mix) | ≤ 26 % | §3.2, Figure 3 |
| Rotation parameterization | Axis-Angle | §5.1.1 |
| Position parameterization | World-frame delta displacement | §5.1.1 |
| Joint-space convention | Absolute radian | §5.1.1 |
| Statistical normalization | **사용 안 함** (raw physical magnitude 유지) | §5.1.1 |
| Modality set $`\mathcal{M}`$ | `{vision, text, state, action}` | §5.2.1, Eq. (3) |
| 사람 손 추정기 | HaWoR (MANO) | §3.1 |
| Per-second 의미 주석 LLM | Gemini-2.5 | §3.1, §4 |
| Codebook 크기 $`|\mathbb{C}|`$ | (원문 미명시 — 사전학습된 Being-H0 tokenizer 재사용) | §5.2.3 |
| Mask ratio $`\rho`$ | (원문 미명시 — 가정으로 메움) | §5.2.3 |
| $`\lambda_{\text{text}},\lambda_{\text{act}},\lambda_1,\lambda_2`$ | (원문 미명시 — 가정으로 메움) | §5.2.2, §5.2.3 |
| MPG temperature $`\tau`$ | (원문 미명시 — 가정으로 메움) | §5.3.2, Eq. (15) |
| MPG slice 수 $`M`$ | (원문 미명시 — 가정으로 메움) | §5.3.2, Eq. (14) |
| MoF Top-K | (원문 미명시 — Top-K 라우팅이라고만 표기) | §5.1.2 |
| MoF foundation/specialized 층 비율 | (원문 미명시 — "initial layers / upper layers" 만 표기) | §5.1.2 |
| Action expert frozen layer sweep | $`\{0, \ldots\}`$ (정확한 sweep 값은 Figure 11 그래프 참조) | §7.3.1, Fig. 11 |
| Pretraining 총 자원 | ≈ 1,000 GPU-hour 레시피 공개 약속 | §1 |
| 데이터 규모 | 35,000 h / 400 M 샘플 / 120 B 토큰 (UniHand-2.0) | §1, §3 |
| Embodiment 수 | 30 (사람 손 포함 시 generalized embodiment 다수) | §1, §3, Table 1 |

---

## 🎯 평가 메트릭

- **지표** — LIBERO success rate (%) · **임계값** — task suite 별 평균 50 trial · **비교 baseline** — Diffusion Policy / OpenVLA / SpatialVLA / CoT-VLA / π0-Fast / GR00T-N1 / π0 / F1 / InternVLA-M1 / Discrete Diffusion VLA / π0.5 / OpenVLA-OFT / X-VLA / EO1.
  - Being-H0.5 specialist: **L-Spatial 99.2 / L-Object 99.6 / L-Goal 99.4 / L-Long 97.4 / Avg 98.9** (§7.2, Table 4).
  - Being-H0.5 generalist: 97.0 / 98.2 / 99.0 / 96.2 / 97.6.
- **지표** — RoboCasa Human-50 success rate (%) · **임계값** — task 당 50 trial × 5 held-out scene, 24 task. · **비교 baseline** — 3DA / DP3 / GWM / BC / GR00T-N1 / π0.5 / π0.
  - Being-H0.5 specialist 53.9 avg (Pick & Place 36 / Doors-Drawers 71.7 / Others 57.6) (§7.2.2, Table 5).
  - generalist 53.3 avg (Pick & Place 40 / Doors-Drawers 73 / Others 52).
- **지표** — 실로봇 카테고리별 success rate (Spatial / Long-horizon / Bimanual / Generalization) · **임계값** — task 당 30–60 분 시연 수집, Being-H0.5 specialist / generalist / scratch / π0.5 비교 · **비교 baseline** — π0.5 (specialist 만 평가; π0.5 는 generalist 미지원).
- **지표** — Mean Wrist Displacement Similarity (MWDS) — predicted vs ground-truth wrist displacement vector 의 cosine similarity. · **임계값** — 0–1 범위, 1 에 가까울수록 좋음. · **비교 baseline** — w/o $`\mathcal{L}_{\text{MASK}}`$.
  - Hybrid (Ours): Lab 0.33 / Wild 0.20.
  - w/o $`\mathcal{L}_{\text{MASK}}`$: Lab 0.35 / Wild 0.28. (caption 의 정성 결론과 표 수치의 정합성은 analysis 의 ⚖️ 한계 참조.)
- **지표** — Action Expert frozen-layer ablation (LIBERO 5-shot, 10 k step) · **임계값** — Figure 10/11 그래프 (성공률, MoF on/off, w/ vs w/o pretraining).
- **지표** — MPG + UAC ablation (실로봇 카테고리별 success rate 변화량) · **임계값** — long-horizon, bimanual 에서 가장 큰 손실 (Figure 12).

---

## ✨ 변경 의도 (intent)

저자들은 *cross-embodiment 일반화* 축에서 π0/π0.5 의 단일 embodiment 패턴에 정면으로 맞선다. 핵심 변경 의도는 세 줄로 요약된다. (1) 사람 손 상호작용을 *generalized embodiment* 로 정의한 *unified state-action space* 한 줄에 모든 입력 슬롯을 묶는다 — *embodiment 별 head* 의 fragmentation 이 사라진다. (2) 액션 전문가의 capacity 병목은 Mixture-of-Flow 의 *foundation/specialized 두 층 hierarchy* 로 푼다. MoE-style sparse activation 덕분에 edge 배포의 메모리·연산 요구가 절감된다. (3) deploy 시 jitter 와 latency, 이 두 실세계 변수는 *Manifold-Preserving Gating* + *Universal Async Chunking* 의 두 deployment-time 모듈로 *학습 단계에서 흡수* 한다. 그 결과 체크포인트 하나가 latency profile 이 서로 다른 실로봇 5 종에서 동시에 돈다. 결과적으로 LIBERO 98.9 / RoboCasa 53.9 와 5 embodiment 실로봇 generalist 가 specialist 에 근접한다는 수치 청구는 이 세 결정을 함께 적용해야 성립한다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — `pi0` / `pi05` 와 동계열 (flow-matching action expert + VLM backbone) 이라 *gross-skeleton 매핑* 은 가능하다. 다만 *Mixture-of-Flow 의 Top-K 라우팅* 과 *unified state-action 슬롯 매핑*, *InternVL-3.5 backbone* 은 `vendor/lerobot` 에 직접 대응되는 모듈이 없다. base 후보는 `pi05` (closest flow-matching 라인업) 이되 MoF / MPG / UAC / ESA / slot mapping 4 개 모듈은 *신규 코드 추가* 가 불가피하다. base data pipeline 은 `vendor/lerobot/datasets/` 의 LeRobotDataset 형식으로 슬롯 매핑된 통합 벡터를 새 dtype 으로 등록한다. 실제 매핑 가능 여부는 `/implement-design` 단계에서 판정한다.

---

## 🚧 미해결 / 잠정

- **Codebook 크기, masking 비율, 손실 가중치** — $`|\mathbb{C}|`$, $`\rho`$, $`\lambda_{\text{text}}, \lambda_{\text{act}}, \lambda_1, \lambda_2`$ 의 정확한 값을 원문이 명시하지 않음. 본 분석 시점에서는 GitHub release 의 config 파일을 가져오지 못해 *(원문에 명시 없음 — 가정으로 메움)*.
- **MPG 의 온도·슬라이스 수** — $`\tau`$ 와 $`M`$ 은 Eq. (14)–(15) 에 기호만 등장하고 수치는 본문에서 공개되지 않는다.
- **MoF 의 Top-K, foundation/specialized 층 비율, expert 개수** — 본문은 정성 표현만 쓰고 구체 값은 내놓지 않는다.
- **action expert frozen-layer sweep** — Figure 11 의 sweep 수치는 그래프에서 읽어야 한다. 따라서 design 차원에서는 정수 값 대신 *sweep 인자 존재* 만 기록한다.
- **`T_state` (proprio history 길이)** — context tokens $`H`$ 의 구성에 *proprio + 현재 action token* 이 들어간다는 본문 진술이 전부이고, 정작 history 길이는 어디에도 적혀 있지 않다.
- **사람 손 / 로봇 / VQA 데이터의 mixing ratio** — 시뮬레이션 비중 ≤ 26 % 만 명시될 뿐, 그 외 *사람:로봇:VQA* 의 비율은 본문 표/그림에 직접 나오지 않는다.
- **MWDS Table 8 의 표·caption 정합성** — wild 분포에서 hybrid 가 *낮은* 수치를 보이는 표 결과와 *clear drop* 이라는 caption 진술이 서로 충돌한다. 본 design 은 본문 표 수치를 그대로 옮기되, *정성 결론은 그대로 채택하지 않는다*.
- **License 정보** — 가중치 / 데이터 / 코드 라이선스가 본문에 명시되지 않음. GitHub release 의 LICENSE 와 데이터셋 라이선스 호환성은 별도 확인 필요.
