# Design — Modular Sensory Stream for Integrating Physical Feedback in Vision-Language-Action Models

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Modular Sensory Stream for Integrating Physical Feedback in Vision-Language-Action Models |
| 링크 | [arXiv:2604.23272](https://arxiv.org/abs/2604.23272) |
| 분석 문서 | [`analysis/2604.23272/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

배치 차원 $`B`$, 액션 호라이즌 $`H`$, 모달리티 인덱스 $`i \in \{1,\dots,N\}`$ 를 공통 표기로 씁니다. 이 논문이 명시한 $`N=2`$ (촉각·토크) 가 기본 시나리오이지만, 프레임워크 자체는 $`N`$ 에 불가지론적입니다.

**입력 텐서**
- **시각** — `images`: shape `(B, V, 3, 224, 224)`, dtype `float32`, ImageNet 정규화 또는 base VLA 백본의 normalization 가정. $`V`$ 는 카메라 수 (논문 셋업은 3자 카메라 + 손목 카메라로 $`V=2`$).
- **언어** — `language_instruction`: token id 시퀀스, dtype `int64`, base VLM 토크나이저 가정.
- **고유수용감각** — `state` $`{\mathbf{s}}_t`$: shape `(B, d_s)`, dtype `float32`. 이 논문은 absolute joint position 모드를 쓰며, $`d_s`$ 는 robot DoF.
- **물리 모달리티 i** — `m_i` $`{\mathbf{m}}_t^{(i)}`$: shape `(B, H, d_i)`, dtype `float32`. 인스턴스화는 (a) tactile: 두 손가락 AnySkin 의 5 센싱 유닛 × 3축 = `(B, H, 30)`, (b) torque: Franka 7 관절 = `(B, H, 7)`. 정규화 방식은 본문에 명시 없음 — 가정으로 메움.
- **노이즈 액션** — `noisy_actions` $`{\mathbf{A}}_t^\tau`$: shape `(B, H, d_a)`, dtype `float32`. $`d_a`$ 는 액션 차원(joint position).
- **시점** — $`\tau`$: shape `(B,)`, $`\tau \in [0,1]`$.

**출력 텐서**
- **예측 액션 청크** — `pred_actions` $`\hat{{\mathbf{A}}}_t`$: shape `(B, H, d_a)`, dtype `float32`, 정규화는 base VLA 와 동일.
- **예측 물리 신호 i** — `pred_m_i` $`\hat{{\mathbf{m}}}_{t+1:t+H}^{(i)}`$: shape `(B, H, d_i)`, dtype `float32`. 미래 호라이즌 길이는 액션 청크와 동일 $`H`$ 로 통일.

**시간 축 의미 단위**
- `chunk_size = H` — 이 논문은 액션 청킹을 따르며, 입력 물리 윈도우 $`{\mathbf{m}}_{t-H+1:t}^{(i)}`$ 와 출력 미래 호라이즌 $`{\mathbf{m}}_{t+1:t+H}^{(i)}`$ 가 같은 길이를 공유합니다. 절대 좌표 길이는 본문 명시 없음 — 가정으로 메움.

---

## 🧰 모듈 인터페이스

구현은 비워 두고 호출 계약만 적습니다. base 좌표 (file:line) 는 `/implement-design` 단계에서 부여됩니다.

```python
def vlm_backbone(language, images) -> Tensor:
    """VLM 백본 F_θ. 시각·언어 → 통합 표현 h_t (shape (B, T_h, d_h))."""

def action_expert(noisy_actions, state, h_t, tau, modality_kv_list) -> Tensor:
    """액션 스트림 A_ψ. 사전학습된 트랜스포머 액션 전문가.
    self-attention 층은 joint cross-modal self-attention 으로 교체됨.
    modality_kv_list 는 같은 층에서 N 개 모달리티 스트림의 (K, V) 텐서들.
    리턴 — pred_actions (shape (B, H, d_a))."""

def modality_stream_i(m_i_window, h_t, noisy_actions, state, other_modality_kv_list) -> Tensor:
    """모달리티 i 의 스트림 A_φ_i. A_ψ 의 구조를 mirror 하고 무작위 초기화.
    self-attention 은 동일하게 joint cross-modal self-attention 으로 교체.
    other_modality_kv_list 는 자기 자신을 제외한 N-1 개 스트림 + 액션 스트림의 (K, V).
    리턴 — pred_m_i_future (shape (B, H, d_i))."""

def joint_cross_modal_self_attention(queries_list, keys_list, values_list) -> List[Tensor]:
    """각 스트림의 Q_i, K_i, V_i (i=0..N) 를 concatenate 해 단일 scaled dot-product
    attention 을 계산한 뒤 다시 스트림별로 split 해 돌려준다. 본 모듈이 모달리티
    사이 정보 교환의 유일 통로다."""

def flow_matching_loss_action(pred_actions, target_actions, noise) -> Tensor:
    """L_act = E_τ,ε [ ||(A_t - ε) - pred_actions||^2 ]."""

def flow_matching_loss_phys(pred_m_list, target_m_list, noise_list) -> Tensor:
    """L_phy = Σ_i E_τ,ε_i [ ||(m^(i)_{t+1:t+H} - ε_i) - pred_m_i||^2 ]."""

def total_loss(L_act, L_phy, lambda_phy) -> Tensor:
    """L = L_act + λ_phy * L_phy."""

def freeze_for_stage1(model) -> None:
    """A_ψ 와 F_θ 의 학습 파라미터를 동결하고, {A_φ_i} 의 새 파라미터만 학습 가능
    상태로 둔다. Stage 1 시작 직전 1 회 호출."""

def unfreeze_for_stage2(model) -> None:
    """A_ψ 를 다시 학습 가능 상태로 풀어 공동 미세조정 (Stage 2) 시작."""
```

**외부 호출 계약**
- 액션 청크 길이 $`H`$ 는 base VLA 의 액션 헤드 호라이즌과 일치해야 합니다.
- 옵티마이저는 한 인스턴스가 Stage 1·2 양쪽 파라미터 집합을 모두 cover 해야 합니다 (학습률 동일, 본문 표 4 verbatim).
- `joint_cross_modal_self_attention` 은 매 트랜스포머 층마다 호출되어야 합니다. 일부 층만 교체하는 변종은 본문에 명시 없음 — 가정으로 메움.

---

## ⛓️ 불변식·가정

- **(A1) 디커플 분리벽** — 모달리티 사이 정보 교환은 오직 joint cross-modal self-attention 한 통로로만 이뤄진다. 그 외 컴포넌트(MLP·LayerNorm·residual path) 는 스트림별 독립이며, 깨질 경우 그래디언트 간섭으로 학습이 불안정해진다.
- **(A2) 미러 구조** — 각 모달리티 스트림 $`\mathcal{A}_{\phi_i}`$ 는 사전학습 액션 전문가 $`\mathcal{A}_{\psi}`$ 와 *동일한* 트랜스포머 구조(층 수·hidden dim·헤드 수)를 가진다. 다른 구조에서의 작동은 본문에 명시 없음 — 가정으로 메움.
- **(A3) Stage 1 동결의 충분성** — Stage 1 학습 동안 새 모달리티 스트림의 표현이 사전학습 액션 전문가의 표현 공간과 *충분히* 정렬돼야 Stage 2 의 공동 미세조정이 안정적이다. 정량적 충분 조건은 본문에 명시 없음 — 가정으로 메움.
- **(A4) Flow-matching base 가정** — base VLA 의 액션 헤드가 conditional flow matching 으로 학습된 디퓨전 기반이어야 본 손실식이 호환된다. 단계 (action-discrete VLA, autoregressive VLA) 에 대한 일반화는 본문 범위 밖.
- **(A5) 호라이즌 통일** — 입력 물리 윈도우 길이와 미래 예측 호라이즌은 모두 $`H`$ 로 동일하다.
- **(A6) $`\lambda_{\mathrm{phy}}`$ 의 작은 값 가정** — 보조 손실 비중은 액션 학습 신호를 누르지 않을 정도로 작아야 한다 (본문은 0.1 권장, 1.0 에서 성능 저하).
- **(A7) 모달리티별 노이즈 독립성** — 각 모달리티 i 의 플로우 매칭 노이즈 $`\epsilon_i`$ 는 다른 모달리티 노이즈와 독립이며, 각 스트림이 자기 노이즈만 본다.

---

## 📊 하이퍼파라미터·손실

**손실 식**

$$\mathcal{L}_{\mathrm{act}}=\mathbb{E}_{\tau,\epsilon}\left[\left\|({\mathbf{A}}_{t}-\epsilon)-\hat{{\mathbf{A}}}_{t}\right\|^{2}\right]$$

$$\mathcal{L}_{\mathrm{phy}}=\sum_{i=1}^{N}\mathbb{E}_{\tau,\epsilon_{i}}\left[\left\|({\mathbf{m}}_{t+1:t+H}^{(i)}-\epsilon_{i})-\hat{{\mathbf{m}}}_{t+1:t+H}^{(i)}\right\|^{2}\right]$$

$$\mathcal{L}=\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{phy}}\mathcal{L}_{\mathrm{phy}}$$

Stage 1 에서는 $`\mathcal{L}_{\mathrm{phy}}`$ 만 사용하며 $`\mathcal{A}_{\psi}`$ 는 동결. Stage 2 에서는 전체 $`\mathcal{L}`$ 사용 + 전 파라미터 해제.

**하이퍼파라미터 (표 4 verbatim)**

| 이름 | 값 (GR00T N1.5 + MoSS) | 값 (π0 + MoSS) | 출처 |
|------|------|------|------|
| `lambda_phy` ($`\lambda_{\mathrm{phy}}`$) | 0.1 | 0.1 | §4.1, §B.1 / Table 5 |
| `optimizer` | AdamW | AdamW | §A.3, Table 4 |
| `beta1` ($`\beta_1`$) | 0.95 | 0.9 | Table 4 |
| `beta2` ($`\beta_2`$) | 0.999 | 0.95 | Table 4 |
| `weight_decay` | 1e-5 | 1e-10 | Table 4 |
| `learning_rate` | 1e-4 | 2.5e-5 | Table 4 |
| `lr_scheduler` | Cosine decay | Cosine decay | Table 4 |
| `warmup_iterations` | 3,000 | 1,000 | Table 4 |
| `batch_size` | 16 | 16 | Table 4 |
| `stage1_iterations` | 20,000 | 10,000 | Table 4 |
| `stage2_iterations` | 40,000 | 20,000 | Table 4 |
| `total_iterations` | 60,000 | 30,000 | §4.1, Table 4 |
| `chunk_size` ($`H`$) | (원문 미명시) | (원문 미명시) | — |
| `action_dim` ($`d_a`$) | (원문 미명시 — joint position) | (원문 미명시) | §A.1 |
| `tactile_dim` | 30 | 30 | §4.1, §A.2 |
| `torque_dim` | 7 | 7 | §4.1, §A.2 |
| `vlm_backbone_freeze` | True (GR00T 디폴트) | False (full fine-tuning) | §4.1 |

---

## 🎯 평가 메트릭

- **지표** — `success_rate (%)` (24 trial 당) · **임계값** — base VLA 대비 절대 증가 · **비교 baseline** — Tactile-VLA / ForceVLA / TA-VLA / 무어댑터 base VLA. 본 논문은 4 과제 평균과 과제별 분해 둘 다 보고합니다.
- **지표** — `avg_success_rate ± std` (4 과제 평균과 표준편차) · **임계값** — 본 논문은 GR00T + MoSS(촉각+토크) 49.0 ± 5.1, π0 + MoSS(촉각+토크) 45.9 ± 5.1 을 보고 · **비교 baseline** — 같은 백본의 무어댑터 (각각 20.8 ± 4.1, 26.1 ± 4.5).
- **지표** — `inference_latency_ms` (per action chunk) · **임계값** — base 대비 1.11× 이내 · **비교 baseline** — 무어댑터 base VLA (GR00T 21.0 ms).
- **이중 모달리티 가산성 지표** — 단일 모달리티 대비 두 모달리티 합쳤을 때의 절대 변화 (표 6 의 괄호 안 수치). MoSS 는 평균 +6.3%p, 다른 baseline 은 -6.2 ~ -12.5%p.

---

## ✨ 변경 의도 (intent)

MoSS 는 사전학습 VLA 위에 *새 물리 모달리티를 동시에 여러 개* 얹는 *적응 어댑터*입니다. 선행 어댑터(Tactile-VLA, ForceVLA, TA-VLA)는 단일 모달리티에 특화된 inline 결합이라, 두 모달리티를 합치면 표현 공간이 충돌해 오히려 성능이 떨어집니다. 저자들은 그 충돌의 뿌리를 두 가지로 진단합니다. 첫째는 단일 스트림 내부에서 일어나는 그래디언트 간섭이고, 둘째는 무작위 초기화 파라미터가 사전학습 prior 를 덮어쓰는 위험입니다. 그리고 이를 네 갈래 장치로 풀어냅니다. 모달리티별 디커플 스트림, 조인트 크로스-모달 셀프 어텐션 단일 통로, 두 단계 학습, 그리고 미래 물리 신호 예측 보조 손실입니다. 그 결과 단일 어댑터로는 닿지 못한 가산성을 얻습니다. 모달리티가 늘수록 성능이 일관되게 올라갑니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` 와 `pi0_fast` family 가 가장 가깝다. 본 논문이 직접 π0 + MoSS 실험을 보고하므로 `lerobot/policies/pi0` 의 액션 전문가 모듈 옆에 병렬 스트림을 추가하고 self-attention 층을 joint cross-modal 변종으로 교체하는 형태로 매핑할 수 있다. `smolvla` 도 동일 패턴 적용 후보. `diffusion`·`act` 는 백본이 VLM 이 아니라 적용 범위가 좁다.

---

## 🚧 미해결 / 잠정

- **액션 청크 길이 $`H`$** — 표 4 와 본문에 절대값 명시 없음. base VLA(π0, GR00T N1.5)의 디폴트 호라이즌을 따랐을 것으로 가정.
- **물리 신호 정규화 통계 출처** — tactile / torque 의 평균·표준편차 산출 방식이 본문에 명시 없음. "데이터셋 전체 통계" 로 가정.
- **joint cross-modal self-attention 적용 층 범위** — 액션 전문가의 *모든* 층에서 교체했는지, 일부 층만 교체했는지 본문 명시 없음. 모든 층 가정.
- **모달리티 스트림 깊이·헤드 수** — 액션 전문가와 동일 구조 mirror 가 본문 명시 — 단, 본문 자체가 base VLA 의 액션 전문가 정확 스펙(층 수·hidden dim)을 적시하지 않음. base VLA 명세를 따라 결정 필요.
- **Stage 1 동결 범위 — VLM 도 동결인가** — GR00T 셋업은 VLM 자체가 디폴트 동결이지만, π0 셋업의 Stage 1 에서 VLM 까지 동결되는지 명시 없음. π0 의 경우 Stage 1 도 VLM 까지 동결로 가정.
- **모달리티 인코더 (raw → token)** — AnySkin 30 차원·Franka 7 차원 벡터를 트랜스포머 입력 토큰으로 변환하는 임베딩 층 구조가 본문에 명시 없음. 단순 선형 projection 으로 가정.
- **물리 미래 예측의 노이즈 스케줄** — 미래 신호 예측도 플로우 매칭 형태인지(노이즈 $`\epsilon_i`$ 와 시점 $`\tau`$ 사용), 단순 회귀인지 본문 표기는 후자처럼 보이나 식 (5) 의 $`(\mathbf{m}-\epsilon_i)`$ 항은 전자 해석을 시사. 플로우 매칭으로 가정.
- **Plug Insertion 데이터 분량 일치** — 표 1 은 GR00T + Tactile-VLA(촉각만) 의 평균을 30.2 로 보고하지만 Plug Insertion 컬럼이 누락된 행이 있다(Table 1, 본문 verbatim). 결과 집계 시 주의.
