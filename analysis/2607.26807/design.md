# Design — Route by Kinematics, Act by Observation: Kinematics-Supervised Expert Routing in MoE-Augmented VLA

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Route by Kinematics, Act by Observation: Kinematics-Supervised Expert Routing in MoE-Augmented VLA |
| 링크 | [arXiv:2607.26807](https://arxiv.org/abs/2607.26807) |
| 분석 문서 | [`analysis/2607.26807/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-08-02 |

---

## 🧮 데이터 계약

알고리즘은 **오프라인 라벨링 단계**와 **온라인 학습/추론 단계**의 두 계약으로 나뉩니다. 시간 축은 의미 단위(`chunk_horizon`)로만 기록합니다.

**오프라인 — 기구학 원형 라벨링**

- **입력** — `action_chunks`: shape `(N_frames, chunk_horizon, d_action)`, float32. 원문 설정은 `chunk_horizon=50`, `d_action=14`이며 `d_action` 의 의미 구조는 `[Left Arm×6 | Left Gripper×1 | Right Arm×6 | Right Gripper×1]` 입니다. 액션 자체의 정규화 방식은 `(원문에 명시 없음 — 가정으로 메움)` — 데이터셋 표준 정규화를 그대로 쓴다고 가정합니다.
- **중간** — `descriptor`: shape `(N_frames, chunk_horizon*d_action + (chunk_horizon-1)*d_action)`. 원문 설정에서 `700 + 686 = 1386`. 위치 특징은 chunk 를 flatten, 속도 특징은 인접 스텝 차분을 flatten 한 뒤 concat 합니다.
- **중간** — `descriptor_std`: 위와 동일 shape, float32. 관절·그리퍼 간 스케일 차이를 제거하는 **feature-wise 표준화** 적용(평균/표준편차 산출 범위는 `(원문에 명시 없음 — 가정으로 메움)`; 데이터셋 전체 통계로 가정).
- **중간** — `descriptor_pca`: shape `(N_frames, pca_dim)`, `pca_dim=64`.
- **출력** — `prototype_labels`: shape `(N_frames,)`, int, 값 범위 `{1, …, K}`. 오프라인 저장되어 라우터 학습의 정답 라벨로 재사용됩니다.

**온라인 — 정책 학습 / 추론**

- **입력** — 이미지: 다중 뷰 `(B, n_cam, 3, H_img, W_img)`. 카메라 수·해상도는 `(원문에 명시 없음 — 가정으로 메움)`. 동결 SigLIP 이 비전 토큰으로 인코딩합니다.
- **입력** — 언어: 지시문 토큰 `(B, L_text)`, int. 동결 PaliGemma-2B 가 언어 토큰으로 인코딩합니다.
- **입력** — 라우팅 컨텍스트: `prefix_tokens` `(B, L_prefix, d_prefix)` + `prefix_mask` `(B, L_prefix)`. 패딩을 무시한 masked mean pooling 결과가 `c` `(B, 2048)`.
- **입력** — 프로프리오셉션: `(원문에 명시 없음 — 가정으로 메움)`. 본문은 관측을 `o=(I, ℓ)` 로만 정의하며 별도 상태 입력을 명시하지 않습니다.
- **입력(학습 전용)** — `prototype_labels` `(B,)`, int. 배치 내 각 관측에 대응하는 오프라인 원형 ID.
- **입력(학습 전용)** — 노이즈 액션 `x_t` `(B, chunk_horizon, d_action)`, 타임스텝 `t` `(B,)` ∈ (0,1).
- **출력** — 예측 속도장 `v_hat` `(B, chunk_horizon, d_action)`, float32. 정규화는 액션과 동일 좌표계.
- **출력(라우팅)** — `expert_ids` `(B, top_k)`, int + `expert_weights` `(B, top_k)`, float32, 행합 1. 이 결정은 **모든 블록에 공유**됩니다.
- **추론 출력** — `x_0` `(B, chunk_horizon, d_action)`. `T` 스텝 오일러 적분 결과.

---

## 🧰 모듈 인터페이스

```python
def build_kinematic_descriptor(action_chunks, chunk_horizon: int):
    """action chunk 를 [flatten(위치) || flatten(인접 차분=속도)] 기술자로 변환."""

def fit_kinematic_prototypes(descriptors, pca_dim: int, n_clusters: int):
    """표준화 → PCA → frame-level K-means. (labels, scaler, pca, kmeans) 반환."""

def assign_prototype_labels(descriptors, scaler, pca, kmeans):
    """학습된 변환기로 프레임별 정수 원형 ID 를 부여 (오프라인 저장용)."""

def pool_routing_context(prefix_tokens, prefix_mask):
    """유효 prefix 토큰의 masked mean pooling → 요약 벡터 c."""

def global_router(c, num_experts: int, top_k: int, temperature: float,
                  noise_std: float, training: bool):
    """c → 단일 선형층 → 로짓. 학습 시 가우시안 노이즈 주입 후 온도 softmax.
    Top-k 선택 + 재정규화. (expert_ids, expert_weights, logits) 반환."""

def moe_ffn(x, shared_ffn, expert_ffns, expert_ids, expert_weights):
    """0.5*shared_ffn(x) + 0.5*Σ_k w_k * expert_ffns[e_k](x)."""

def supervised_router_loss(router_logits, prototype_labels):
    """라우터 로짓과 오프라인 원형 라벨 간 교차엔트로피."""

def balanced_sampling_weights(prototype_labels, alpha: float):
    """w_i = n_{y_i}^{-alpha}; 복원추출 확률 p_i = w_i / Σ_j w_j."""

def flow_matching_loss(v_hat, epsilon, a_0):
    """MSE(v_hat, epsilon - a_0)."""

def denoise(x_T, velocity_fn, num_steps: int, expert_ids, expert_weights):
    """x_{t-Δt} = x_t - Δt * v_hat, Δt = 1/num_steps. 라우팅 결정은 루프 밖에서 1회."""
```

- **`build_kinematic_descriptor` / `fit_kinematic_prototypes` / `assign_prototype_labels`** — 학습 루프 밖의 전처리 파이프라인. 산출물(`prototype_labels` + 학습된 scaler/PCA/KMeans)은 데이터셋 아티팩트이며, 데이터가 바뀌면 무효화되어야 합니다. 옵티마이저·손실과 직접 상호작용하지 않습니다.
- **`pool_routing_context` + `global_router`** — 관측당 1회만 호출됩니다. 추론 시 디노이징 루프 **밖** 에서 호출되어야 하며(사전계산 단계), 루프 안에서 호출하면 논문의 "negligible additional inference cost" 전제가 깨집니다.
- **`moe_ffn`** — 액션 스트림 각 블록의 기존 FFN 호출을 대체합니다. `shared_ffn` 은 사전학습 FFN 가중치로 초기화되고 학습 대상에 포함됩니다. `expert_ffns` 는 백본과 동일 폭으로 새로 초기화됩니다.
- **`supervised_router_loss`** — 전체 손실에 `router_loss_coef` 로 가중되어 더해집니다. 라우터 로짓에만 gradient 를 흘리며, 라우터 입력이 동결 backbone 출력이면 gradient 경로는 선형층 한 층뿐입니다.
- **`balanced_sampling_weights`** — DataLoader 의 복원추출 샘플러에 전달됩니다. 손실 항이 아니라 **샘플링 계층** 의 개입이라는 점이 중요합니다 — 원문은 load-balancing 보조 손실을 일절 쓰지 않습니다.
- **`flow_matching_loss` / `denoise`** — 기존 플로우 매칭 정책과 동일 계약. KinRT 는 이 부분을 변경하지 않습니다.

---

## ⛓️ 불변식·가정

- **(가정 1) 기구학 원형 붕괴** — 데이터셋의 action chunk 기술자가 소수(`n_clusters`)의 분리 가능한 군집으로 붕괴합니다. 이 성질이 없으면 라벨 자체가 무의미해지고 알고리즘 전체가 무효가 됩니다.
- **(가정 2) expert 수 = 클러스터 수** — `num_experts == n_clusters`. expert 1개가 원형 1개를 담당한다는 대응이 설계의 전제입니다.
- **(가정 3) 관측→원형 결정 가능성** — 관측 `o` 만으로 원형 라벨 `y` 를 예측할 수 있을 만큼의 상호정보가 존재합니다. 이것이 성립하지 않으면 교차엔트로피가 다수 클래스 예측으로 붕괴합니다.
- **(가정 4) 라우팅 결정의 레이어 불변성** — "어떤 기구학 국면인가"라는 판단은 모든 블록에서 동일하게 유효하므로, 관측당 1회 결정을 전 레이어에 브로드캐스트해도 손실이 없습니다.
- **(가정 5) 관측 1개 ↔ 원형 1개** — 라벨은 프레임 단위인데 라우팅은 관측 단위입니다. 한 관측에 대응하는 chunk 가 두 원형의 경계를 걸치지 않고 하나에 지배적으로 귀속된다고 가정합니다.
- **(가정 6) shared 분기의 사전학습 유효성** — shared 분기가 사전학습 FFN 이므로 expert 수렴 전에도 유의미한 출력을 낸다고 가정합니다. 이 가정 덕분에 MoE 도입 초기 성능 붕괴가 방지됩니다.
- **(가정 7) 고정 혼합비** — shared 대 routed 비율이 학습 없이 `(1/2, 1/2)` 로 고정됩니다. 균등 사전분포로서 초기화 크기 불균형을 막는 장치이며, 학습 가능한 게이트가 아닙니다.
- **(가정 8) 선형 확률 경로** — $`x_{t}=t\cdot\varepsilon+(1-t)\,a_{0}`$ 이므로 목표 속도 $`v_{t}=\varepsilon-a_{0}`$ 가 $`t`$ 에 무관한 상수입니다.
- **(가정 9) 균일 샘플링 시계열** — 인접 액션 차분이 속도의 대리값이 되려면 시연이 일정 주기로 샘플링되어 있어야 합니다. 가변 주기 데이터에서는 속도 특징이 왜곡됩니다.
- **(가정 10) 라벨-체크포인트 결합** — 원형 라벨은 특정 데이터 혼합에 종속적입니다(원문에서도 한 클러스터가 단일 과제에 지배됨). 데이터 구성이 바뀌면 라벨과 expert 특화가 함께 무효화됩니다.

---

## 📊 하이퍼파라미터·손실

**전체 손실** — 원문은 두 손실의 결합 형태를 식으로 명시하지 않고 라우터 손실 계수만 제시합니다.

$$\mathcal{L}=\mathcal{L}_{act}+\lambda_{\text{sup}}\,\mathcal{L}_{\text{sup}}$$

**액션 손실 (식 7)**

$$\mathcal{L}_{act}=\mathbb{E}_{t,\,\varepsilon,\,a_{0}}\left\|\hat{v}_{\theta}(x_{t},t,o)-v_{t}\right\|^{2}$$

**라우터 지도 손실 (식 4)**

$$\mathcal{L}_{\text{sup}}=-\sum\nolimits_{b}y_{b}\log\hat{y_{b}}$$

**MoE FFN 합성 (식 1)**

$$\mathrm{FFN}_{\text{MoE}}(x)\!=\!\tfrac{1}{2}\,\mathrm{FFN}_{\text{shd}}(x)\!+\!\tfrac{1}{2}\sum\nolimits_{k=1}^{K}\tilde{w}_{k}\,\mathrm{FFN}_{e_{k}}(x)$$

**라우팅 확률 (식 3)**

$$p=\mathrm{softmax}((g+\eta)/\tau)$$

**기구학 기술자 (식 2)**

$$\phi_{i}=\big[\,\mathrm{vec}(a^{(i)}_{0:H})\;\big\|\;\mathrm{vec}(a^{(i)}_{1:H}-a^{(i)}_{0:H-1})\,\big]\in\mathbb{R}^{1386}$$

**균형 샘플링** — 샘플 가중치 $`w_{i}=n_{y_{i}}^{-\alpha}`$, 복원추출 확률 $`p_{i}=w_{i}/\sum_{j}w_{j}`$, 원형 단위 주변 확률:

$$P(y=k)=n_{k}^{1-\alpha}/\sum_{c}n_{c}^{1-\alpha}$$

**노이즈 액션 / 목표 속도 / 갱신 (식 5·6·8)**

$$x_{t}=t\cdot\varepsilon+(1-t)\,a_{0}$$

$$v_{t}={\partial x_{t}}/{\partial t}=\varepsilon-a_{0}$$

$$x_{t-\Delta t}=x_{t}-\Delta t\,\hat{v}_{t}$$

**하이퍼파라미터**

| 이름 | 값 | 출처 |
|------|----|----|
| `chunk_horizon` ($`H`$) | `50` | §Kinematic Archetype Clustering, §Implementation |
| `d_action` ($`D`$) | `14` (`[LeftArm×6 \| LeftGripper×1 \| RightArm×6 \| RightGripper×1]`) | §Kinematic Archetype Clustering |
| `descriptor_dim` | `1386` (`700` 위치 + `686` 속도) | §Kinematic Archetype Clustering, Eq. (2) |
| `pca_dim` | `64` | §Kinematic Archetype Clustering |
| `n_clusters` ($`K`$) | `4` (RoboTwin 기준, 데이터에서 유도) | §Kinematic Archetype Clustering |
| `num_experts` ($`N`$) | `4` | §Kinematic Archetype Clustering, §Implementation |
| `top_k` | `1` | §Implementation |
| `shared_routed_mix` | `(1/2, 1/2)` 고정 | §KinRT’s Architecture, Eq. (1) |
| `d_model` | `1024` | §KinRT’s Architecture |
| `d_mlp` | `4096` | §KinRT’s Architecture |
| `num_blocks` ($`L`$) | `18` | §KinRT’s Architecture |
| `router_context_dim` | `2048` (masked mean pooling 결과) | §Kinematics-Supervised Global Router |
| `router_head` | 단일 선형층 | §Kinematics-Supervised Global Router |
| `router_loss_coef` ($`\lambda_{\text{sup}}`$) | `0.05` | §Implementation |
| `balanced_sampling_alpha` ($`\alpha`$) | `0.5` | §Kinematics-Supervised Global Router, §Implementation |
| `router_temperature` ($`\tau`$) | `(원문 미명시)` | §Kinematics-Supervised Global Router |
| `router_noise_std` ($`\sigma`$) | `(원문 미명시)` | §Kinematics-Supervised Global Router |
| `flow_time_dist` | `Beta(1.5, 1)` | §Action Generation by Observation at Deployment |
| `denoise_steps` ($`T`$) | `(원문 미명시)` | §Action Generation by Observation at Deployment |
| `train_steps` | `10,000` | §Implementation |
| `batch_size` | `32` (유효 배치는 gradient accumulation 으로 유지) | §Implementation |
| `lora_rank` | `32` (VL backbone) / `64` (action expert) | §Implementation |
| `lora_alpha` | `1` | §Implementation |
| 보조 정규화 손실 | 없음 (load-balancing / contrastive-routing / dead-expert 전부 미사용) | §Implementation |
| optimizer / lr / schedule | `(원문 미명시)` | — |

---

## 🎯 평가 메트릭

- **지표** — `per-task success count` · **집계** — `average success count across all tasks` · **출처** — §Metrics ("For both benchmarks, we report both the per-task success count and the average success count across all tasks.")
- **시뮬레이션 프로토콜** — RoboTwin 8과제 × {clean, random} 세팅, 세팅·과제당 100회 테스트(총 1,600회). 학습은 세팅별 과제당 50 시연(총 800).
- **실세계 프로토콜** — DIYRobot 5과제, 과제당 50회 테스트(총 250회), clean 세팅만. 학습은 과제당 100 시연(총 500).
- **비교 baseline** — dense: OpenVLA / RDT-1B / π0-Full / π0-LoRA / π0.5-Full / π0.5-LoRA. MoE: Hi-MoE / AdaMoE. plug-in 변형: KinRT-OpenVLA / KinRT-Full(π0) / KinRT-LoRA(π0) / KinRT-AdaMoE.
- **참조 임계값** — RoboTwin 평균 `40.8 / 38.8` (KinRT-LoRA, clean/random), DIYRobot 평균 `35.6` (KinRT-Full). 최강 dense baseline 대비 각각 `+7.7` (23.26%), `+6.0` (20.27%).
- **분산 보고** — 없음. 시드 반복·표준편차·신뢰구간이 원문에 없으므로 `(원문에 명시 없음)`. 재현 시 다중 시드가 필요합니다.
- **누락 — 라우터 자체 지표** — 원형 예측 정확도, 클래스별 recall, expert 이용률이 원문에 보고되지 않습니다. Design 차원에서는 `router_top1_accuracy` / `expert_utilization_histogram` 을 추가 계측 지점으로 남겨 둡니다(원문 미보고이므로 재현 목표값 없음).

---

## ✨ 변경 의도 (intent)

기존 MoE-VLA 는 라우터를 손실만으로 암묵 학습시키므로, 라우터가 실제로 보는 신호(시각-언어 관측)와 expert 배정의 진짜 기준(동작 기구학의 동형성)이 어긋납니다. 게다가 그 기구학 신호는 추론 시점에 존재하지 않는다는 구조적 비대칭이 있습니다. 이 Design 은 그 비대칭을 우회하지 않고 **학습 시에만 존재하는 action 궤적을 오프라인 군집화해 정답 라벨로 제조하고, 라우터를 관측→원형 분류기로 지도 학습** 시킴으로써 정면 해결합니다. 그 결과 배포 시에는 라우터 가중치에 남은 지식만으로 관측에서 원형을 복원하므로 추가 입력이 필요 없습니다. 부수 효과로, MoE 의 고질적 load collapse 가 손실 설계 문제에서 **표준 분류의 클래스 불균형 문제** 로 치환되어 load-balancing 보조 손실 없이 리샘플링 계수 하나로 다뤄집니다. 개입 범위는 액션 스트림 FFN 과 라우터 한 층에 국한되고 백본·생성기(플로우 매칭)는 그대로이므로, 기존 플로우 매칭 VLA 위에 얹는 증분 변경으로 설계되어 있습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — `pi0` / `pi05` family 가 가장 가깝습니다. prefix(VLM) + suffix(action expert) 분리, 플로우 매칭 속도장 회귀, action chunk 예측이라는 세 전제를 이미 공유하므로, 변경은 (a) action expert 블록의 FFN 을 shared+routed 합성으로 교체, (b) prefix 출력 풀링 + 선형 라우터 추가, (c) 데이터셋 측 원형 라벨 필드 + 가중 샘플러, (d) 손실에 라우터 CE 항 추가의 네 지점에 국한될 가능성이 높습니다. `act` / `diffusion` family 는 VLM prefix 스트림이 없어 라우터 입력 계약(`pooled prefix context`)이 성립하지 않으므로 후보에서 벗어납니다.

---

## 🚧 미해결 / 잠정

- **`token-level` vs `observation-level` 라우팅 모순** — §Implementation 은 "Top-1 routing to enable one expert for each token" 으로, §Kinematics-Supervised Global Router 는 관측 단위 global routing 으로 서술합니다. 두 서술이 양립하지 않으며, 이 Design 은 방법론 절을 따라 **관측 단위 1회 라우팅** 으로 고정했습니다. 구현 시 재확인이 필요합니다.
- **`router_temperature` / `router_noise_std` 미명시** — 원문은 "we can set $`\tau`$ and $`\eta`$ accordingly" 라고만 적고 값을 주지 않습니다. 라우터 엔트로피와 expert 이용률을 직접 좌우하므로 재현 시 탐색 대상입니다.
- **`denoise_steps` 미명시** — 추론 스텝 수 $`T`$ 가 본문에 없습니다.
- **`n_clusters` 선택 절차 미명시** — `K=4` 는 RoboTwin 결과이지만, elbow / silhouette 등 선택 근거와 시드가 없습니다. `num_experts` 를 데이터에서 유도한다는 주장의 검증 절차가 비어 있습니다.
- **정규화 통계 출처** — 기술자 표준화의 평균/표준편차 산출 범위가 명시되지 않아 "데이터셋 전체 통계" 로 가정했습니다.
- **관측 정의의 범위** — 관측은 `o=(I, ℓ)` 로만 정의되며 프로프리오셉션 입력 여부가 불명확합니다. 프로프리오셉션이 있는 foundry 로 이식할 때 라우터 입력에 포함할지는 미결입니다.
- **베이스 백본 정체** — 접미사 없는 `KinRT-Full` / `KinRT-LoRA` 가 어떤 백본 위에 세워졌는지 본문에 명시가 없습니다(아키텍처 서술은 PaliGemma-2B + Gemma-300M). 헤드라인 수치의 비교 기준이 불확정입니다.
- **전체 손실 결합식 부재** — 라우터 손실 계수 `0.05` 만 주어질 뿐, 두 손실의 결합 형태·스케일 정규화 여부가 식으로 제시되지 않아 단순 가중합으로 가정했습니다.
- **원형 전이 구간 처리 미정의** — 관측 단위 hard switch 이므로 원형 경계에서의 평활화·히스테리시스·혼합 규칙이 본문에 없습니다. 결론이 예고한 "adaptive expert activation" 이 이 공백에 해당합니다.
- **추론 비용 수치 부재** — "negligible additional inference cost" 주장에 대응하는 지연시간·메모리·활성 파라미터 측정치가 없습니다.
