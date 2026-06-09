# Design — DynaFLIP: Rethinking Robotics Perception via Tri-Modal-Dynamics Guided Representation

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
| 원문 제목 (영문) | DynaFLIP: Rethinking Robotics Perception via Tri-Modal-Dynamics Guided Representation |
| 링크 | [arXiv:2605.30350](https://arxiv.org/abs/2605.30350) |
| 분석 문서 | [`analysis/2605.30350/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-09 |

---

## 🧮 데이터 계약

사전학습은 RGB 비디오에서 파생된 image–language–3D flow 삼중쌍을 입력으로 받습니다. 시간 축은 의미 단위로 기록합니다($`H`$ = 전이 시간 간격, $`K`$ = 3D flow 윈도 길이).

- **입력 (이미지)** — $`(I_t, I_{t+H})`$: 현재·미래 프레임, shape `(B, 3, 224, 224)` ×2, float, RGB. 인코더는 DINOv2-Base (ViT-B/14), 전체 학습 가능.
- **입력 (언어)** — $`L`$: 지시문, 최대 77 토큰. frozen T5-Base 인코더 + 학습 가능 adapter.
- **입력 (3D flow)** — $`F_{t:t+K}`$: shape `(B, K, 20, 20, 3)`, float. $`20\times 20`$ 키포인트의 $`(x,y,z)`$ 궤적, $`(x,y)`$=이미지 평면 좌표 · $`z`$=기준 카메라 프레임 depth. $`K=7`$.
- **출력 (임베딩)** — $`z_I, z_L, z_F`$: 각 단위 구 위 $`\ell_2`$ 정규화 임베딩. $`z_I`$ 는 미래·현재 프레임 특징의 차분.
- **중간 특징** — $`d_t = \mathrm{CLS}(I_t) \oplus \sigma(\mathrm{Patch}(I_t)) \in \mathbb{R}^{1536}`$ (768 CLS + 768 평균풀링 patch).
- **다운스트림 출력** — 사전학습한 이미지 인코더($`f_\phi`$)를 frozen 시각 백본으로 재사용. 액션 공간·shape 는 다운스트림 정책(MLP / diffusion policy / VLA)에 따르며 사전학습 단계의 산출물이 아닙니다. 실세계 π $`_{0.5}`$ 통합 시 액션은 `action_dim=32`, `action_horizon=50` (§D.4, Table 6).

---

## 🧰 모듈 인터페이스

```python
def image_encoder(I_t, I_t_plus_H) -> z_I:
    """DINOv2-Base 로 두 프레임 인코딩, CLS⊕평균풀링(d_t) 후 MLP fusion 으로
       전이 임베딩 z_I 산출. 차분 기반이라 정적 외양이 아닌 상태 변화를 포착."""

def language_encoder(L) -> z_L:
    """frozen T5-Base + 학습 가능 adapter. EOS 토큰 풀링 후 adapter 사상."""

def flow_encoder(F_t_to_t_plus_K, sg_image_feat) -> z_F:
    """4-layer CNN(타임스텝별) + 4-layer transformer(시간 집계).
       현재 프레임 임베딩 d_t 를 stop-gradient 로 조건 토큰 prepend,
       학습 가능 temporal [CLS] 출력을 선형 사상."""

def alignment_energy(z_L, z_I, z_F, alpha) -> E:
    """삼각형 면적 A 에서 alpha * <z_L, z_F> 코사인 항을 뺀 정렬 에너지."""

def alignment_loss(batch_embeddings, negatives, tau) -> L_align:
    """매칭 삼중쌍 에너지를 negative tuple 보다 낮추는 InfoNCE 대비 손실."""

def actor_head(image_feat) -> F_hat_t:
    """단일 프레임 이미지 특징에서 3D flow 를 예측(BC 풍, MSE)."""

def pvi_inject(aux_visual_feat, frozen_action_expert_hidden) -> hidden_residual:
    """다운스트림 통합 전용. frozen 인코더 특징을 projection 후
       action expert 의 trainable copy 로 per-layer residual 을 생성해
       frozen main path hidden 에 가산. projection·injection 은 zero-init,
       trainable copy 는 사전학습 action expert 로 초기화."""
```

- **이미지 인코더** — 두 프레임 → $`z_I`$. 전체 백본 학습 가능. 다운스트림에서는 이 $`f_\phi`$ 만 frozen 백본으로 추출.
- **3D flow 인코더** — flow 시퀀스 + stop-gradient 이미지 특징 → $`z_F`$. 이미지 가지로 새는 지름길 차단이 책임.
- **정렬 에너지/손실** — 세 임베딩 → 스칼라 에너지 → 배치·negative 로 대비 손실. negative 삼중쌍 구성(배치 내 모달리티 뒤섞기)이 붕괴 방지의 핵심.
- **보조 헤드** — temporal contrastive loss(프레임 삼중)과 actor loss(3D flow 예측 MSE)는 이미지 인코더 표현 강화 보조 신호.
- **PVI 통합 모듈** — Layer 1 알고리즘 외부(다운스트림)이지만, 본 논문이 평가한 VLA 통합 계약이므로 명세에 포함. ControlNet-style side branch.

---

## ⛓️ 불변식·가정

- (가정 1) — 모든 모달리티 임베딩은 단위 구 위에 있다: $`\|z_I\|_2 = \|z_L\|_2 = \|z_F\|_2 = 1`$ ($`\Pi`$ 사영). 심플렉스 면적·코사인 항의 기하 의미가 이 정규화에 의존.
- (가정 2) — 작은 삼각형 면적 $`A`$ 가 강한 상호 정렬을 의미한다. 단 면적만으로는 기하적 모호성(일직선 배치)이 생기므로 코사인 정칙화로 반드시 보강해야 한다.
- (가정 3) — negative 삼중쌍이 없으면 정렬 에너지 $`E`$ 는 모든 임베딩이 한 점으로 붕괴할 때 최소가 된다(자명한 붕괴). 따라서 대비 프레임 없이 $`E`$ 를 직접 최소화하면 안 된다.
- (가정 4) — 이미지 전이 임베딩이 차분 $`f_\phi(I_{t+H}) - f_\phi(I_t)`$ 로 정의되어야 정적 외양이 아닌 상태 변화를 포착한다.
- (가정 5) — 3D flow 가지의 이미지 특징 조건은 stop-gradient 여야 한다. 그렇지 않으면 이미지 가지를 통한 자명한 지름길 해가 생긴다.
- (가정 6) — 3D flow 가 기준 카메라 좌표계로 변환돼 카메라 모션이 보정된 상태여야 시점 불변 운동 신호로 기능한다.
- (가정 7, PVI 통합) — projection·injection 을 zero-init 하고 trainable copy 를 사전학습 action expert 로 초기화하면, 초기 정책이 사전학습 VLA 와 동치이며 주입 신호가 학습 중 점진적으로 활성화된다(§D.4). 이 zero-init 가정이 깨지면 frozen 백본의 prior-보존 성질이 무효.

---

## 📊 하이퍼파라미터·손실

- 전체 손실: $`\mathcal{L}_{\text{DynaFLIP}} = \mathcal{L}_{\mathrm{align}} + \lambda_{\mathrm{tcn}}\mathcal{L}_{\mathrm{tcn}} + \lambda_{\mathrm{act}}\mathcal{L}_{\mathrm{act}}`$ (Eq. (7))
- 정렬 에너지: $`E = A(z_L, z_I, z_F) - \alpha\langle z_L, z_F\rangle`$ (Eq. (2))
- 삼각형 면적: $`A = \frac{1}{2}\sqrt{\langle u,u\rangle\langle v,v\rangle - \langle u,v\rangle^2}`$, $`u = z_I - z_L`$, $`v = z_F - z_L`$ (Eq. (1))
- 정렬 손실: $`\mathcal{L}_{\mathrm{align}}`$ — InfoNCE, 분자 $`\exp(-E^i/\tau)`$, 분모에 negative tuple $`\mathcal{N}(i)`$ 합산 (Eq. (3))
- Actor 손실: $`\mathcal{L}_{\mathrm{act}} = \sum_i \|\hat{F}_t^{(i)} - F_t^{(i)}\|_2^2`$ (Eq. (6))

| 이름 | 값 | 출처 |
|------|----|----|
| `lambda_tcn` ($`\lambda_{\text{tcn}}`$) | 1.0 | §D.1, Table 3 |
| `lambda_act` ($`\lambda_{\text{act}}`$) | 1.0 | §D.1, Table 3 |
| Contrastive temperature ($`\tau`$) | 0.07 | §D.1, Table 3 |
| Cosine regularization ($`\alpha`$) | 1.0 | §D.1, Table 3 |
| 3D flow temporal window ($`K`$) | 7 | §D.1, Table 3 |
| Optimizer | AdamW | §D.1, Table 3 |
| Learning rate | $`10^{-4}`$ | §D.1, Table 3 |
| Weight decay | $`10^{-2}`$ | §D.1, Table 3 |
| Batch size | 32 | §D.1, Table 3 |
| Image resolution | $`224\times 224`$ | §D.1, Table 3 |
| Brightness / contrast jitter | 0.1 / 0.1 | §D.1, Table 3 |
| Saturation / hue jitter | 0.05 / 0.02 | §D.1, Table 3 |
| 프레임 샘플링 | 클립당 5 (첫10%·끝10%·중간3) | §D.1 |
| 전이 시간 간격 ($`H`$) | (원문에 명시 없음 — 가정으로 메움) | — |
| 학습 하드웨어/기간 | 4× NVIDIA L40S · 약 4 일 | §D.1 |
| (다운스트림) π $`_{0.5}`$ peak/final lr | $`1.5\times 10^{-5}`$ / $`1.5\times 10^{-6}`$ | §D.4, Table 6 |
| (다운스트림) action dim / horizon | 32 / 50 | §D.4, Table 6 |

---

## 🎯 평가 메트릭

- **지표** — Control-relevant score ($`S_m`$, [13] 제안) · **방식** — frozen 인코더 위 경량 probe 로 관절각·EE pose·물체 6D pose/shape 예측 후 모델 간 min-max 정규화 평균 · **비교 baseline** — R3M, VC-1, LIV, DINOv2, CLIP, SigLIP (§3.1, §D.5)
- **지표** — 다운스트림 성공률(%) · **벤치마크** — MetaWorld(15 task, 25 demo), RLBench(6 task, 100 demo), LIBERO(90/Goal/Object/Spatial/Long) · **정책** — MLP(frozen probe), Diffusion Policy, VLA(π $`_{0.5}`$) (§3.1–3.4)
- **임계값/비교** — frozen LIBERO 평균 41.5%(1위), LoRA 평균 81.0%(1위) (§3.3, Table 1); MetaWorld 평균 78.9, RLBench 평균 54.0 (§D.2); ablation full 44.0 vs w/o negative tuples 18.1 (§3.5, Table 2)
- **OOD 프로토콜** — 시각·공간 교란(미관측 물체 위치·distractor) + 의미 교란(미관측 물체·지시문); 실세계 UR3, setting 당 20 rollout, 최강 baseline 대비 최대 +22.5% (§3.4, §1)

---

## ✨ 변경 의도 (intent)

기존 로봇 시각 백본(CLIP·SigLIP·DINOv2)은 정적 인식과 비전-언어 정렬만 배운 탓에 동역학 이해를 다운스트림 정책에 떠넘깁니다. DynaFLIP 은 동역학 인식을 지각 단계로 끌어올립니다 — image transition·language·3D flow 세 모달리티가 공유 공간에서 그리는 심플렉스 면적을 줄이도록 이미지 전용 인코더를 사전학습합니다. 핵심 차이는 둘입니다. 첫째, anchor 기반 쌍별 정렬 대신 higher-order 심플렉스 기하로 상호 정렬을 끌어냅니다. 둘째, 그 과정의 두 함정 — 기하적 모호성과 자명한 붕괴 — 을 각각 코사인 정칙화와 InfoNCE 대비로 막습니다. 이렇게 얻은 표현은 frozen 백본으로 여러 정책에 그대로 쓰이며, VLA 통합 시에도 백본을 동결한 채 zero-init side-branch 로만 주입해 사전학습 prior 를 보존합니다. 특히 OOD 에서 강건합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 본 논문의 산출물은 **시각 백본 사전학습**이라 단일 policy family 와 1:1 대응하지 않습니다. 두 갈래로 매핑됩니다. (1) *사전학습 stage*: 심플렉스 정렬·TCN·actor 손실은 lerobot 정책 학습 루프 밖의 별도 pretraining 으로 구현해야 하며, 표준 policy 진입점에 직접 대응되지 않습니다. (2) *다운스트림 통합*: frozen 인코더를 정책 vision backbone 으로 주입하므로 VLA 계열 `pi05`(논문이 직접 π $`_{0.5}`$ 에 PVI/ControlNet 주입) 또는 `pi0` 의 vision encoder 보조 주입 지점과 가깝습니다. PVI side-branch 의 trainable-copy + zero-init 패턴은 `pi0`/`pi05` 의 action expert 모듈에 매핑될 후보입니다. 실제 매핑은 `/implement-design` 단계에서 확인.

---

## 🚧 미해결 / 잠정

- 전이 시간 간격 $`H`$ 의 구체 값이 본문에 명시되지 않았습니다 — Table 3 에 없고 프레임 샘플링(클립당 5 프레임) 설명에서 간접 유추만 됩니다.
- MLP fusion 블록, T5 adapter, actor head, 3D motion CNN 의 정확한 차원/층 구성은 일부만 적혀(4-layer CNN·4-layer transformer) 세부 hidden 차원을 알 수 없습니다.
- negative 삼중쌍 집합 $`\mathcal{N}(i)`$ 의 크기·구성 규칙(몇 개 모달리티를 어떻게 뒤섞는지)은 정성 기술에 그쳐 정량 스펙이 없습니다.
- PVI 유사 injection 모듈의 구체 구조(projection 차원, 주입 layer 수)는 [60] PVI / [59] ControlNet 참조로 위임돼 본문에서 완전히 명세하지 않았습니다.
- 코드/가중치 공개 저장소 링크가 본문(arXiv HTML)에서 확인되지 않습니다(프로젝트 페이지만 존재).
