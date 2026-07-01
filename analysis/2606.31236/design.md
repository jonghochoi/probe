# Design — TactX: Learning Shared Tactile Representations Across Diverse Sensors

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TactX: Learning Shared Tactile Representations Across Diverse Sensors |
| 링크 | [arXiv:2606.31236](https://arxiv.org/abs/2606.31236) |
| 분석 문서 | [`analysis/2606.31236/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-01 |

---

## 🧮 데이터 계약

시간 축은 프레임 단위 quasi-static 접촉 관측이며, downstream 정책의 chunk 축과는 분리됩니다. 표현 학습기(TactX VAE)와 downstream 소비 계약을 나눠 기록합니다.

**표현 학습 (TactX encoder/decoder 학습)**

- **입력 (paired)** — 한 학습 예시는 센서 쌍 $`(i,j)`$ 의 프레임 짝 $`(x_i, x_j)`$, 같은 접촉을 두 센서가 동시 관측.
  - Daimon(vision-based) `x_D`: shape `(B, 224, 224, 3)`, float, depth+shear 채널, 이미지 정규화.
  - eFlesh(magnetic) `x_E`: shape `(B, 15)`, float, 5 magnet × 3 axis 자기장 벡터.
  - FlexiTac(resistive) `x_F`: shape `(B, 12, 16)`, float, 저항 압력 그리드.
  - 각 쌍의 한 센서에 load-time $`180^\circ`$ 회전 적용(접촉 영역 정렬용).
- **출력 (latent)** — posterior 파라미터 $`(\mu, \log\sigma^2)`$: shape `(B, 2d)` with `d=16` → 공유 latent $`z\in\mathbb{R}^{16}`$. 학습 시 $`z=\mu+\sigma\odot\epsilon`$, 추론 시 $`z=\mu`$.
- **복원 출력** — decoder $`g_i(z)`$ 는 해당 센서 native 공간 $`\mathcal{X}_i`$ 로 복원(self 및 cross 모두).

**Downstream 정책 소비 (ACT)**

- **입력** — frozen encoder 로 오프라인 계산한 $`\mu`$: shape `(B, n_finger, 16)`, per-dataset latent mean/std 로 정규화. 손가락별 MLP adapter $`16\to64\to128\to512`$ 로 손가락당 1 tactile token.
- **출력** — action chunk: `(B, chunk_size=64, action_dim)`, action/state 는 128-D 로 padding(첫 8-D만 배포 시 사용).

---

## 🧰 모듈 인터페이스

```python
def encoder_i(x_i: Tensor) -> tuple[Tensor, Tensor]:
    """센서 i 의 native 신호 x_i 를 shared latent posterior (μ, logσ²) 로 매핑.
       signal-specific backbone(ResNet-18 / MLP / residual CNN) → 512-D →
       projection head 512→512→2d (Linear-ReLU-Linear), d=16."""

def reparameterize(mu: Tensor, logvar: Tensor, training: bool) -> Tensor:
    """training: z = μ + σ⊙ε, ε~N(0,I);  inference: z = μ."""

def decoder_i(z: Tensor) -> Tensor:
    """shared latent z 를 센서 i 의 native 공간 𝒳_i 로 복원 (self/cross 공용).
       센서별 전용 (공유 decoder 없음)."""

def tactx_loss(batch_pairs, encoders, decoders, alpha_t, beta_t) -> Tensor:
    """모든 센서 쌍 (i,j) 에 대해 λ_recon·L_recon + α(t)·L_align + β(t)·L_KL 합산.
       L_recon = self+cross L1, L_align = 대칭 NT-Xent(τ=0.01), L_KL vs N(0,I)."""

def tactile_token_adapter(mu: Tensor) -> Tensor:
    """downstream: frozen μ(16-D) → MLP 16→64→128→512 → 손가락당 1 token."""
```

- **encoder_i / decoder_i** — 센서별 인스턴스(D/E/F). encoder 는 posterior 를 내고, decoder 는 self(`g_i(z_i)`)·cross(`g_i(z_j)`) 복원 양쪽에 호출됨.
- **tactx_loss** — 세 손실 항의 스케줄($`\alpha(t)`$, $`\beta(t)`$)을 시간 인자로 받아 warmup 을 반영. optimizer(Adam) 와 분리된 순수 손실 계약.
- **tactile_token_adapter** — 표현 학습과 독립. frozen encoder 출력을 정책 token 으로 변환하는 얇은 어댑터.

---

## ⛓️ 불변식·가정

- **(가정 1) Paired 동시성** — 각 쌍 $`(x_i^{(t)}, x_j^{(t)})`$ 는 *같은 물리적 접촉점*을 동시에 관측한 것이어야 함(정렬 감독의 유일한 신호원). 이 대응이 깨지면 contrastive positive 정의가 무효.
- **(가정 2) 대칭·rigid 물체** — 두 센서가 배치·국소 기하 차이가 아니라 modality 차이만으로 다른 신호를 내려면, 접촉 물체가 대칭·강체여야 한다는 가정. 비대칭 물체에서는 가정 1 이 근사적으로만 성립.
- **(가정 3) 공통 sensing 영역** — 세 센서의 active 영역이 대략 commensurate 하여 한 접촉이 모든 센서에 잡혀야 함(시각적 shortcut 제거 위해 검은색으로 외관 정합).
- **(가정 4) latent 충분성** — 16-D latent 이 downstream 제어에 필요한 접촉 기하를 담을 만큼 충분하다는 가정. 정밀 task 에서는 병목이 될 수 있음(분석 §⚖️ 한계).
- **(가정 5) 전역 일관성** — pairwise 정렬 + 공통 prior $`\mathcal{N}(0,I)`$ 가 관측되지 않은 쌍(D–F)까지 transitive 하게 일관 좌표계를 유도한다는 가정.

---

## 📊 하이퍼파라미터·손실

- 총 손실:

$$\mathcal{L}_{\textsc{TactX}}=\sum_{(i,j)}\big[\lambda_{\text{recon}}\mathcal{L}_{\text{recon}}^{(i,j)}+\alpha(t)\mathcal{L}_{\text{align}}^{(i,j)}+\beta(t)\mathcal{L}_{\text{KL}}^{(i,j)}\big]$$

- 복원 손실(self+cross, L1):

$$\mathcal{L}_{\text{recon}}=\|g_i(z_i){-}x_i\|_1+\|g_j(z_j){-}x_j\|_1+\|g_i(z_j){-}x_i\|_1+\|g_j(z_i){-}x_j\|_1$$

- 정렬 손실: 대칭 NT-Xent(InfoNCE) on L2-정규화 $`\tilde{\mu}_i=\mu_i/\|\mu_i\|_2`$
- KL 손실: 각 posterior → 공유 prior $`\mathcal{N}(0,I)`$

| 이름 | 값 | 출처 |
|------|----|----|
| latent dim $`d`$ | 16 | Appendix C, Table 5 |
| batch size | 64 | Table 5 |
| learning rate | $`1\times10^{-4}`$ (Adam, wd $`1\times10^{-4}`$) | Table 5 |
| epochs | 300 | Table 5 |
| seed | 42 | Table 5 |
| $`\lambda_{\text{recon}}`$ | 1.0 | §3, Table 5 |
| KL $`\beta`$ | $`0\to0.1`$ linear warmup(30 epoch) | §3, Table 5 |
| align $`\lambda_{\text{align}}`$ / $`\alpha(t)`$ | $`0\to1`$ warmup | §3, Table 5 |
| InfoNCE temperature $`\tau`$ | 0.01 (NT-Xent variant 0.03) | §3, Table 5 |
| projection head | $`512\to512\to2d`$ (Linear-ReLU-Linear) | Appendix B |
| downstream ACT $`\lambda_{\text{KL}}`$ | $`10\to1`$ (mode-collapse 완화) | Appendix D.2 |
| tactile adapter | MLP $`16\to64\to128\to512`$ (손가락별) | Appendix D.2 |

---

## 🎯 평가 메트릭

- **지표** — sensor-prediction accuracy(frozen latent 위 linear probe) · **임계값** — 낮을수록 좋음, 33.3% chance 근접이 이상(TactX 47.5% vs recon-only 67.5%) · **비교 baseline** — reconstruction-only / contrastive-only / L2-alignment
- **지표** — object-classification accuracy(frozen latent, 10 클래스, self/cross) · **임계값** — 높을수록 좋음(TactX self 60.8% / cross 56.2%) · **비교 baseline** — 동일 변형군
- **지표** — transitive D–F cosine similarity(E 다리 경유) · **임계값** — 높을수록(TactX 0.928 vs 0.626/0.679) · **비교 baseline** — recon-only / L2-align
- **지표** — zero-shot cross-sensor 정책 성공률(10 trial 중 성공 수, 3 run mean±std) · **임계값** — vision-only 대비 향상(평균 27.5%→45.9%) · **비교 baseline** — Vision Transfer / Binary Contact Transfer / Raw(oracle 상한)

---

## ✨ 변경 의도 (intent)

기존 cross-sensor 촉각 연구는 image-like 공통 substrate 를 공유하는 vision-based 촉각 family *내부*에서만 전이를 다뤘습니다. TactX 의 핵심 변경 의도는, **공통 입력 포맷 변환을 전혀 두지 않고**(per-sensor input transformation 없음) 광학·자기·저항 세 transduction modality 를 latent 공간에서 직접 정렬한다는 점입니다. 이를 위해 (1) paired contact 를 정렬 감독으로 쓰고, (2) contrastive alignment 로 센서 정체성을 지우되, (3) self/cross reconstruction 으로 접촉 내용을 latent 에 보존하는 세 힘을 결합합니다. 결과적으로 정책은 16-D latent token 만 보고 센서 교체는 encoder branch 교체로 흡수되어, 새 센서마다 데모 재수집·정책 재학습을 없애는 것이 목표입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — downstream 정책이 ACT 이므로 `act` family 가 직접 대응 base. TactX 자체는 정책 *앞단*의 frozen 촉각 encoder + latent-token adapter 로, `act` 의 tactile/observation 입력 경로에 얹는 전처리 모듈로 매핑 가능(raw tactile CNN token → frozen 16-D latent → MLP adapter token 교체). 단, TactX encoder/decoder 학습 루프(paired contrastive+VAE)는 lerobot 표준 policy 학습 스크립트 밖의 별도 표현-학습 스테이지라, 해당 부분은 `UNMAPPABLE` 가능성 있음 — `/implement-design` 가 판정.

---

## 🚧 미해결 / 잠정

- Daimon encoder 의 정확한 입력 채널 구성(§4.1 의 `224×224×3` depth+shear vs Appendix D.1 raw 정책의 `240×320×3` depth/deformation/shear composite)이 표현 학습과 raw 정책에서 다르게 기술됨 — 표현 학습기 입력은 `224×224×3` 으로 채택, 불일치는 원문 표기 그대로 보존.
- $`\alpha(t)`$ 의 "reconstruction-first curriculum" 구체 스케줄(ramp 형태/기간)은 본문에 "optionally ramped" 로만 기술 — (원문에 명시 없음 — 가정으로 메움: 0→1 선형 warmup 으로 가정).
- downstream `action_dim` 실제 값(128-D padding, 첫 8-D 사용)은 명시되나 task 별 원 action 차원은 명시 없음.
- paired 데이터셋·정책 데모의 공개 여부·정규화 통계 출처는 본문에 명시 없어, latent 정규화는 "per-dataset latent mean/std" 로 가정.
