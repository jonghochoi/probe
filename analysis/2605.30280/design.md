# Design — Qwen-VLA: Unifying Vision-Language-Action Modeling across Tasks, Environments, and Robot Embodiments

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
| 원문 제목 (영문) | Qwen-VLA: Unifying Vision-Language-Action Modeling across Tasks, Environments, and Robot Embodiments |
| 링크 | [arXiv:2605.30280](https://arxiv.org/abs/2605.30280) |
| 분석 문서 | [`analysis/2605.30280/analysis.md`](./analysis.md) |
| 본문 확보 수준 | PDF 텍스트 (PyMuPDF 추출, 34 pages) |
| Design 생성일 | 2026-05-29 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`H` = 예측 호라이즌, `K` = 공유 채널 차원)로 기록합니다. 정확한 `H`/`K` 정수값은 본문 미명시(조작 SFT 는 `H=16`, VLN 은 웨이포인트 8개; RL 도 `H=16`).

- **입력 — 이미지 (multi-view RGB)**: shape `(B, V, 3, Himg, Wimg)` (V = 카메라 수; 뷰별 경계 토큰 `<|tag_start|> 〈image〉 <|tag_end|>` 로 감쌈, tag ∈ {`ego`, `cam_left_wrist`, `cam_right_wrist`, …}). 해상도·V 본문 미명시. T2A 단계에서는 이미지 완전 억제.
- **입력 — 언어 (embodiment prompt + instruction)**: 토큰 시퀀스. 템플릿 `"The robot is {robot_tag} with {single arm / dual arms}[, waist][, and mobile base]. The control frequency is {FPS} Hz. Please predict the next {chunk_size} control actions to execute the following task: {ori_instruction}."` 임바디먼트 정보가 모델로 들어가는 유일한 인터페이스.
- **입력 — 노이즈 행동 (flow-matching)**: `Yτ = (1−τ)Y0 + τY1`, `Y1 ~ N(0, I)`, shape `(B, H, K)`, `τ ∈ [0, 1]`.
- **출력 — 행동 텐서 `Y`**: shape `(B, H, K)`, dtype float. 제어 모드별 활성 채널 `c ≤ K`, 앞쪽 `c` 차원에 유효값·나머지 0 패딩. 채널 마스크 `M ∈ {0,1}^{H×K}`, `M[h,k]=1 ⟺ k<c 이고 h<Htask`.
- **정규화**: 데이터셋별 분위수 정규화 — 차원 `d`, 데이터셋 `k` 에서 `ãd = 2·(ad − q^k_01)/(q^k_99 − q^k_01) − 1`, `[−1,1]` 클리핑. (역정규화는 추론 시 데이터셋별 통계로 복원.)
- **행동 의미 (제어 신호 유형)**: 조작 = ∆EEF 위치 / Euler·쿼터니언 회전 / 절대 관절 / 그리퍼 / 다지손 관절. 내비 = 웨이포인트당 `(∆x, ∆y, ∆θ)`. 인간 자기중심 = 손당 손목 SE(3) 상대(이동 3 + axis-angle 회전 3) + eigengrasp 10계수 = 손당 16, 양손 32차원. 데이터셋 원래 관습 보존(공유 물리 의미로 강제 변환하지 않음).

---

## 🧰 모듈 인터페이스

base 좌표(file:line)는 여기 들어오지 않습니다. 호출 계약만 기록합니다.

```python
def vlm_backbone(images, text_tokens) -> hidden_states:
    """Qwen3.5-4B. 시각 토큰을 텍스트 스트림에 조기 융합, 하이브리드 어텐션
    (gated linear + 간헐 grouped-query softmax). 출력 = 멀티모달 은닉 상태."""

def action_expert(vlm_hidden, noisy_action_chunk, tau) -> velocity_field:
    """DiT 스타일 플로우 매칭(~1.15B, 16블록). VLM 은닉 상태와 노이즈 행동
    청크를 한 시퀀스로 concat → joint self-attention(AdaLN(tau) 조건화 +
    multi-section RoPE) → 조건부 속도장 vθ 예측."""

def action_projection_in(raw_action) -> dit_latent:
    """raw 행동 차원 → DiT 잠재 차원. Zero-Padding: 공유 MLP, dmax 로
    우측 0패딩 후 인코딩(2·h·dmax 파라미터). 임바디먼트별 헤드 없음."""

def action_projection_out(dit_latent) -> raw_action:
    """DiT 잠재 → raw 행동 차원. 각 임바디먼트는 di 차원 prefix 만 읽음."""

def value_head(vlm_hidden) -> scalar_value:
    """RL 단계 전용. VLM 은닉 상태 mean-pool → 선형 사상 스칼라.
    백본으로의 역전파 차단(stop-gradient). clipped MSE, lr 1e-4."""

def flow_to_action(vlm_hidden, prompt, num_steps) -> action_chunk:
    """추론: τ=1→0 로 몇 번의 Euler 적분 → 행동 청크. 저지연 실시간 제어."""

def flow_logprob_ppo(denoise_states, params) -> log_prob:
    """RL: probability-flow ODE → SDE 변환(스텝별 제어 노이즈 주입) →
    각 전이를 명시적 가우시안으로 → log πθ(at|st) 해석적 계산.
    기본: 롤아웃당 denoising 스텝 1개 무작위 선택(추가 DiT forward 1회)."""
```

- 손실/옵티마이저 관계: 행동 손실(플로우 매칭 MSE)은 `action_expert` 출력에, VL 손실(next-token CE)은 `vlm_backbone` 언어 헤드에 겁니다. 합동 손실 `L = λ_act·L_act + λ_vl·L_vl`. RL 단계는 `L = L_actor + cv·L_value`.

---

## ⛓️ 불변식·가정

base 와 무관한 수학적/통계적 성질:

- **(가정 1) 마스크 그래디언트 격리** — 0패딩된 채널/스텝(`M[h,k]=0`)은 그래디언트에 기여하지 않아야 합니다. 깨지면 임바디먼트별 채널 수 차이가 학습을 왜곡합니다.
- **(가정 2) 채널 단위 동등 기여** — 2단계 평균(채널 내 유효 스텝 평균 → 활성 채널 균등 평균)으로, 채널 수가 다른 임바디먼트 간에도 각 제어 차원이 동등 기여합니다.
- **(가정 3) 임바디먼트 프롬프트의 충분성** — 플랫폼별 제어 의미가 텍스트 프롬프트만으로 전달 가능하다(별도 출력 헤드·상태 입력 불필요). state-conditioning 절제(≤1.3pp)가 이 가정을 (시야 가시 조건에서) 지지.
- **(가정 4) 상대 행동 예측** — 플로우 매칭이 절대 자세가 아닌 상대 변위를 예측하므로, 명시적 현재 상태 참조 필요성이 줄어든다(state-conditioning 무용 결론의 한 근거).
- **(가정 5) 압축-해압축 가능성 (T2A)** — 언어+임바디먼트 프롬프트(소수 토큰)가 고차원 행동 궤적의 충분한 인덱스이며 시각 없이도 구조화된 행동 사전(prior)을 학습할 수 있습니다. 언어→행동 매핑이 전체 VLA 공간보다 구조적으로 저차원이라 소수 step(≈2,000)으로 수렴합니다.
- **(가정 6) 분위수 정규화의 구조 보존** — 1·99 분위수 선형 사상이 데이터셋 간 스케일 차이를 제거하되 소스 내 상대 운동 구조는 보존합니다.

---

## 📊 하이퍼파라미터·손실

식·기호 verbatim. 본문 미명시 값은 `(원문 미명시)`.

- **플로우 매칭 행동 손실** (Eq. 1–2):
  `ℓk = Σh M[h,k]·‖(vθ(Yτ,τ|o,x,e,z) − (Y1−Y0))[h,k]‖²₂ / Σh M[h,k]`,
  `L_act = E[ (1/c) Σ_{k=0}^{c−1} ℓk ]`
- **VL 손실** (Eq. 3): `L_vl = − Σi log pθ(wi | w_{<i}, o_{1:t})`
- **합동 손실** (Eq. 4): `L = λ_act·L_act + λ_vl·L_vl`
- **분위수 정규화** (Eq. 5): `ãd = 2·(ad − q^k_01)/(q^k_99 − q^k_01) − 1`, clip `[−1,1]`
- **RL** (Eq. 6–7): `L_actor = −E[min(rt·Ât, clip(rt,1−ε,1+ε)·Ât)]`, `rt = πθ(at|st)/πθ_old(at|st)`, `L = L_actor + cv·L_value`

| 이름 | 값 | 출처 |
|------|----|----|
| `λ_act` (SFT) | `1.0` (manip·nav 행동) | §4.1 |
| `λ_vl` (SFT) | `0.1` (VL next-token) | §4.1 |
| `λ_act`, `λ_vl` (pretrain) | (원문 미명시 — "gradient 크기 균형 위해 튜닝") | §2.5 |
| `H` (조작 SFT/RL action chunk) | `16` | §4.1, §4.2, §5.1.1 |
| `H` (VLN 웨이포인트) | `8` | §4.1 |
| `K` (공유 채널 차원) | (원문 미명시 정수) | §2.4 |
| 행동 전문가 파라미터 | `≈1.15B` (16 DiT 블록 × 70.8M = 1.13B) | §2.2 |
| 백본 | `Qwen3.5-4B` | §1, §2.2 |
| T2A step | `2,000` (정점; 40,000 과적합) | §5.2.1 |
| T2A 데이터 비율 | `≈20% syn + 80% real` (vision-dropped) | §5.2.1 |
| 타임스텝 분포 `p(τ)` | T2A = Sigmoid-Normal, CPT/SFT = Beta | §5.2.1 |
| projection 설계 | Zero-Padding (`2·h·dmax`) | §5.2.2, Table 10 |
| eigengrasp 차원 | 상위 `10` PCA 계수 (45→10) | §3.2.2 |
| PPO `ε` | `0.2` | §4.2 |
| GAE `γ` / `λ` | `0.99` / `0.95` | §4.2 |
| value 계수 `cv` | `1` | §4.2 |
| PPO epoch / 롤아웃 | `4` epoch/batch | §4.2 |
| actor lr / value lr | `5×10⁻⁶` / `10⁻⁴` | §4.2 |
| 병렬 환경 `N` | `128` (반복당 8,192 transition chunk) | §4.2 |
| 롤아웃/평가 온도 `τ` | `1.0` / `0.6` | §4.2 |
| RL 보상 | 희소 이진 (`R=1` 성공 / `R=0`) | §4.2 |

---

## 🎯 평가 메트릭

- **지표** — 시뮬 조작 성공률(%) · **비교 baseline** — π0, π0.5, GR00T N1.6, StarVLA-OFT, ABot-M0, Being-H0.5 · **수치** — LIBERO 97.9 / RoboCasa-GR1 56.7 / Simpler-WidowX 73.7 / RoboTwin-Easy 86.1 / RoboTwin-Hard 87.2 (Qwen-VLA-Instruct, Table 4)
- **지표** — 실세계 ALOHA in-domain/OOD 성공률(%) · **비교** — GR00T N1.6, π0.5, w/o-pretrain · **수치** — in-domain avg 83.6, OOD avg 76.9 (Table 5–6)
- **지표** — VLN-CE: NE↓ / OS↑ / SR↑ / SPL↑ / nDTW↑ · **수치** — R2R Val-Unseen OS 69.0·SR 57.5, RxR SR 59.6·SPL 47.8 (Table 7)
- **지표** — OOD-static SimplerEnv-OOD 성공률 avg · **수치** — 32.0 (vs π0.5 12.6, Table 8)
- **지표** — OOD-dynamic DOMINO: SR(%)↑ / MS↑ (zero-shot) · **수치** — SR 26.6 / MS 39.5 (Table 9)
- **절제 지표** — T2A 후 SFT 성공률(Simpler-WidowX, %) — 데이터 구성/예측 모드/타임스텝/학습량 스윕의 단일 종속변수(최고 71.09)

---

## ✨ 변경 의도 (intent)

선행 연구(prior art) — π0/π0.5 류의 단일 임바디먼트 전문가나 GR00T 류의 임바디먼트별 처리 — 와 달리, Qwen-VLA 는 조작·내비·자기중심 인간 동작·궤적 예측을 하나의 "행동-궤적 통합 예측" 공간으로 합칩니다. 이 공간은 고정 `H×K` 텐서 + 마스크 + Zero-Padding projection 으로 구성되며 임바디먼트 차이는 **텍스트 프롬프트라는 단일 인터페이스**로만 흡수합니다. 학습은 행동 학습을 "압축 해압축" 으로 보는 4단계 레시피입니다. 시각 없는 언어→행동 사전학습(T2A)으로 행동 사전(prior)을 먼저 심은 뒤 시각 접지(CPT)·태스크 특화(SFT)·성공 기반 정제(RL) 를 차례로 적용합니다. 그 결과 단일 일반주의 정책이 임바디먼트별 헤드·상태 입력 없이 다중 플랫폼을 다루며, 동적 조작(DOMINO) 등 미학습 분포로도 zero-shot 전이됩니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05` family 와 가장 가까움. 둘 다 "VLM 백본 + 플로우 매칭 액션 전문가" 구조를 공유하므로 액션 전문가 골격은 pi0 계열에 매핑 가능. 단 Qwen-VLA 고유 요소 — 임바디먼트 프롬프트 조건화, Zero-Padding projection, 통일 `H×K`+마스크 표현, T2A 사전 단계, 단계별 `p(τ)`, 플로우 매칭 PPO — 는 학습 레시피/데이터 계약 층의 추가이며 lerobot 의 단일 base 클래스로 직접 대응되지 않을 수 있음(여러 지점 패치 또는 부분 매핑 불가 가능성). 백본이 PaliGemma 가 아닌 Qwen3.5-4B 라는 점도 매핑 시 검토 필요.

---

## 🚧 미해결 / 잠정

- 공유 채널 차원 `K` 의 정확한 정수값 — 본문 미명시(원문에 명시 없음 — `/implement-design` 시 가정으로 메움).
- 사전학습(T2A/CPT) 단계의 `λ_act`, `λ_vl` 구체값 — 본문은 SFT 값(1.0/0.1)만 제시, 사전학습은 "gradient 균형 위해 튜닝" 으로만 기술.
- 이미지 해상도·카메라 수 `V`·정확한 뷰 태그 집합 — 본문 미명시.
- Qwen3.5-4B 의 상세 config(레이어 수, hidden, attention 비율) — 본문은 "하이브리드 어텐션" 정성 기술만 제시.
- 미니배치 내 태스크군 샘플링 비율("fixed sampling ratio") 구체값 — §2.5 에 정성 언급만, 수치 미명시.
- 추론 시 Euler 적분 스텝 수("a few Euler steps") — 정확한 정수 미명시.
- 역정규화 시 데이터셋별 분위수 통계의 저장/조회 메커니즘 — 본문 미명시(데이터셋별 통계로 가정).
