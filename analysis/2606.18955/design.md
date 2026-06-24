# Design — Motion-Focused Latent Action Enables Cross-Embodiment VLA Training from Human EgoVideos

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Motion-Focused Latent Action Enables Cross-Embodiment VLA Training from Human EgoVideos |
| 링크 | [arXiv:2606.18955](https://arxiv.org/abs/2606.18955) |
| 분석 문서 | [`analysis/2606.18955/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-24 |

---

## 🧮 데이터 계약

3단계(① VQ-VAE 코드북 → ② VLM 사전학습 → ③ 다운스트림 적응)별 텐서 계약입니다. 시간 축은 의미 단위로 표기합니다.

**① Hybrid Disentangled VQ-VAE**
- **입력 — 영상** — `frames`: $`V \in \mathbb{R}^{T \times C \times H \times W}`$, 고정 1초 간격 인접 프레임 쌍, 프레임 `224×224`. frozen DINOv2 로 공간 특징 $`F \in \mathbb{R}^{T \times N \times D}`$ 추출.
- **입력 — 마스크** — `fg_mask`: 전경(손/로봇 팔) 이진 마스크, shape `(T, H, W)` (SAM2=사람 / RoboEngine=로봇).
- **출력 — 행동 코드** — `z_q_act`: 프레임 쌍당 `K=4` 토큰, 코드북 크기 16(이산 인덱스 + 임베딩 `(K, D_code)`).
- **출력 — 배경 코드** — `z_q_bg`: 코드북 크기 16, 배경 query 수만큼의 토큰.

**② VLM 사전학습**
- **입력** — $`(I_t, I_{t+T})`$ 이미지 쌍 + 언어 지시문 `L`; frozen VQ-VAE 인코더로 타깃 토큰열 $`\mathbf{z}_{act}=\{z^{(1)},\dots,z^{(K)}\}`$, $`K=4`$.
- **출력** — VLM 어휘로 편입된 행동 토큰의 자기회귀 분포 $`P_\theta(z^{(k)} \mid z^{(<k)}, I_t, L)`$.

**③ 다운스트림 적응 (flow matching 액션 전문가)**
- **입력 — 의도** — `f_act`: VLM 마지막 transformer 층 은닉상태 집계, shape `(B, D_vlm)` (정규화·집계 연산 원문 미명시).
- **입력 — 지각** — `f_obs = DINO(I_main)` (또는 wrist 추가 시 `DINO([I_main, I_wrist])`), frozen `DINOv2-ViT-B/14-reg`.
- **입력 — proprio** — `f_proprio`: 로봇 관절 상태.
- **컨텍스트** — `F_full = Concat(f_act, f_obs, f_proprio)` (flat concat).
- **출력 — 액션** — flow matching 속도장 $`v_\theta(x_t, t, F_{full})`$ → 액션 청크 `(B, T_action, D_action)` (chunk 길이·차원 원문 미명시).

---

## 🧰 모듈 인터페이스

`file:line` 좌표 없이 호출 계약만 기록합니다(vendor-agnostic).

```python
class HybridDisentangledVQVAE:
    def encode(self, frames, fg_mask) -> tuple[Tensor, Tensor]:
        """프레임 쌍 → (z_q_act[K=4, cb=16], z_q_bg[cb=16]); frozen DINOv2 특징 + 학습 query Q_act/Q_bg, dual-path VQ."""
    def decode(self, z_act, z_bg, init_feat, mode: str) -> Tensor:
        """mask-guided 복원. mode ∈ {full, action_ablation, background_ablation}; 공유 spatial-temporal transformer 디코더."""

class LatentActionVLM:
    def predict_latent_actions(self, I_t, L) -> Tensor:
        """관측+지시문 → 행동 토큰열 자기회귀 예측(K=4). 코드북은 VLM 어휘에 편입(UniVLA 방식). backbone=Prismatic VLM."""
    def intent_embedding(self, I_main, L) -> Tensor:
        """마지막 층 은닉상태 집계 → f_act. 적응 단계엔 LoRA 어댑터로 갱신."""

class FlowMatchingActionExpert:
    def forward(self, F_full, x_t, t) -> Tensor:
        """self-attn(청크 내 시간 의존) + cross-attn(멀티모달 컨텍스트) → MLP head 가 속도장 v_theta 예측. scratch 학습."""
```

- **마스크 생성기** — SAM2(사람 손) / RoboEngine(로봇)는 외부 frozen 모듈; 동작 경로의 전경 supervision 만 제공.
- **손실 결합 계약** — ③단계는 $`L_{flow}`$ (액션) + $`\lambda_{intent} \cdot L_{intent}`$ (잠재 의도 cross-entropy) 동시 최적화(아래 📊).

---

## ⛓️ 불변식·가정

- **(가정 1)** — 고정 1초 간격 프레임 쌍은 물리적 동작에 의한 단기 시각 변화를 담고 장기 장면 드리프트는 무시한다(간격이 너무 길면 동작-배경 분리 가정이 약화).
- **(가정 2)** — 전경 마스크가 "움직이는 조작 주체(손/로봇 팔)"를 정확히 분리한다 — 동작 복원 오차는 전경 영역에서만, 배경 복원은 배경 영역에서만 계산된다. 마스크 실패 시 disentanglement 무효.
- **(가정 3)** — dual-path VQ 가 의미 격리를 강제해, 행동 코드북은 embodiment-agnostic 모션 프리미티브만 담는다 → **같은 행동이면 임베디먼트가 달라도 같은 토큰**(cross-embodiment 일관성의 수학적 핵심).
- **(가정 4)** — DINOv2 특징은 VLM 의도와 분리된 "객관적 물리 상태"를 제공한다 — 의도와 지각의 분리가 action hallucination 을 억제한다.
- **(가정 5)** — `K=4` 토큰·코드북 16 의 이산 용량은 high-level 의도엔 충분하나 고정밀 제어엔 부족(저자 명시 한계).

---

## 📊 하이퍼파라미터·손실

**① VQ-VAE (식 1)**

$$L_{\text{total}}=\lambda_{\text{recon}}L_{\text{recon}}+\lambda_{\text{vq}}L_{\text{vq}}+\lambda_{\text{commit}}L_{\text{commit}}$$

$`L_{recon}`$ = mask-guided 전경+배경+전역 특징 오차, $`L_{vq}`$ = 인코더 출력↔코드북 유클리드 거리, $`L_{commit}`$ = 인코더 출력 안정화.

**② VLM 사전학습 (식 2)**

$$L_{pre}=-\mathbb{E}_{(L,I_{t},I_{t+T})\sim\mathcal{D}}\left[\sum_{k=1}^{K}\log P_{\theta}\left(z^{(k)}\mid z^{(<k)},I_{t},L\right)\right]$$

**③ 적응 — flow matching + 의도 (식 3·4·5)**

$$F_{full}=\text{Concat}(f_{act},f_{obs},f_{proprio})$$

$$L_{flow}=\|v_{\theta}(x_{t},t,F_{full})-(a-\epsilon)\|^{2}$$

$$L_{total}=L_{flow}+\lambda_{intent}L_{intent}$$

$`a`$ = ground-truth 액션, $`\epsilon`$ = 표준 가우시안 노이즈, $`x_t`$ = flow step $`t`$ 의 노이즈 액션.

| 이름 | 값 | 출처 |
|------|----|----|
| 행동 코드북 크기 | `16` | §III-B 2 |
| 프레임 쌍당 토큰 수 `K` | `4` | §III-B 2, §III-C |
| 배경 코드북 크기 | `16` | §III-B 2 |
| 프레임 간격 | `1 s` | §III-B |
| 입력 해상도 | `224×224` | §IV |
| frozen 시각 인코더 | `DINOv2-ViT-B/14-reg` | §IV |
| VLM backbone | Prismatic VLM | §III-C |
| VLM 적응 방식 | LoRA | §III-D |
| $`\lambda_{recon} / \lambda_{vq} / \lambda_{commit}`$ | `(원문 미명시)` | §III-B 4 |
| $`\lambda_{intent}`$ | `(원문 미명시)` | §III-D, 식 5 |
| 적응 step/batch | LIBERO 30k–40k / bs128; RoboTwin 30k / bs32; 실로봇 20k / bs32 | §IV-A, §IV-B |

---

## 🎯 평가 메트릭

- **지표** — task success rate (%) · **비교 baseline** — UniVLA, villa-x, pi0, pi0-fast, RDT, ACT, Diffusion Policy, OpenVLA, SpatialVLA, LAPA.
- **벤치마크** — LIBERO 4 suite(Spatial/Object/Goal/Long), RoboTwin 2.0 10 task, 실로봇 3 task. ablation: `w/o DINO`(의도-지각 분리 검증), `Freeze`(VLM 동결 시 잠재 임베딩 중요도).
- **표현 정렬** — domain subspace 제거(logistic regression + PCA 직교투영) 후 **CKA**(token centroid bootstrap 50회). 보고치: UniVLA 0.8659 vs Ours 0.9139.
- **정성** — 혼합 데이터셋(BridgeV2+EgoDex)에서 같은 행동 → 같은 토큰(cross-embodiment 일관성).

---

## ✨ 변경 의도 (intent)

기존 latent-action VLA 가 (a) UniVLA 처럼 **언어**로 task-centric 움직임을 유도하거나 (b) Being-H0.5/H-RDT 처럼 VR 손 포즈 **라벨**에 의존하는 데 반해, 본 설계는 **물리 마스크(SAM2/RoboEngine)** 라는 외부 inductive bias 로 동작-배경을 명시 분리한 dual-path VQ-VAE 로 **라벨 없는 사람 영상**에서 순수 모션 코드북을 뽑습니다. 적응 단계에서는 "의도(VLM 은닉)"와 "지각(frozen DINOv2)"을 별도 채널로 분리(intent-perception decoupling)해 action hallucination 을 억제하고, ~50 궤적/task 로 cross-embodiment 적응을 달성합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — ③ flow matching 액션 전문가(self-attn + cross-attn + concat 컨텍스트 + 속도장 회귀)는 `pi0` / `pi05` family 와 가장 가깝습니다. 다만 ① VQ-VAE 잠재 행동 코드북 + ② VLM 잠재-토큰 사전학습 파이프라인은 vendored lerobot 에 직접 대응이 없어, 신규 모듈(latent action 인코더 + 어휘 확장 사전학습 루프)로 추가해야 합니다. `vla_jepa` 가 latent-prediction 계열로 가장 인접한 참고점.

---

## 🚧 미해결 / 잠정

- $`\lambda_{recon}/\lambda_{vq}/\lambda_{commit}/\lambda_{intent}`$ 구체 값 — 원문 미명시(가정으로 메움 필요).
- LoRA rank, 코드북 임베딩 차원 `D_code`, 배경 query 수, `f_act` 집계 연산(평균/마지막 토큰 등) — 원문 미명시.
- 액션 청크 길이 `T_action`·액션 차원 `D_action`·flow 적분 step 수 — 원문 미명시.
- 사전학습 데이터 규모(BridgeV2 / EgoDex 사용 시간·프레임 수)·VQ-VAE 학습 step — 원문 미명시.
- "intent-perception decoupling" 의 구체 융합 형태는 flat concat(식 3)로만 명시 — cross-attention 등 구조적 변형은 본문 범위 밖.
