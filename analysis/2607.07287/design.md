# Design — TouchWorld: A Predictive and Reactive Tactile Foundation Model for Dexterous Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TouchWorld: A Predictive and Reactive Tactile Foundation Model for Dexterous Manipulation |
| 링크 | [arXiv:2607.07287](https://arxiv.org/abs/2607.07287) |
| 분석 문서 | [`analysis/2607.07287/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-13 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`H` = nominal horizon, `W` = refinement lookahead, `k` = feedback history)로 기록합니다. 절대 좌표 아님. 아래 shape 은 Wuji 플랫폼 인스턴스(§8) 기준이며 embodiment 별로 액션 차원은 달라집니다.

- **입력 (상위 계획)** — 언어 `` $`\ell`$ ``: token 시퀀스 · 다중뷰 이미지 `` $`\mathcal{I}_{t}`$ ``: `(B, V, 3, Hc, Wc)` uint8→normalize · 상위 메모리 `` $`m_{t}`$ ``: 이전 서브태스크·서브골·실행상태의 구조화 텍스트/토큰
- **입력 (nominal 정책)** — 서브태스크 `` $`\ell_t^{\mathrm{sub}}`$ `` (텍스트) · 이미지형 촉각 `` $`\mathcal{X}_t`$ ``: `(B, T_touch, 3, Ht, Wt)` (raw 촉각→이미지 렌더/정규화) · proprio `` $`\mathbf{s}_t`$ ``: `(B, D_s)` float32 · 예측 서브골 `` $`g_t`$ ``: goal 이미지 grid 또는 tactile subgoal latent(선택)
- **출력 (nominal)** — 액션 청크 `` $`\hat{\mathbf{A}}_{t:t+H-1}`$ ``: `(B, H, D_a)` float32 (Wuji: `D_a=120`, `H=32`), 정규화는 zarr 학습셋 통계 · 컨텍스트 토큰 `` $`\mathbf{c}_t`$ ``: `(B, D_c)`
- **입력 (refinement/TRT)** — nominal lookahead `` $`\hat{\mathbf{A}}_{\tau:\tau+W-1}`$ ``: `(B, W, D_a)` (`W=16`) · proprio 히스토리 `` $`\mathbf{s}_{\tau-k:\tau}`$ ``: `(B, k+1, D_s)` · 촉각 히스토리 `` $`\mathcal{X}_{\tau-k:\tau}`$ `` (신호유형별 인코딩) · 컨텍스트 `` $`\mathbf{c}_t`$ ``
- **출력 (refinement)** — 잔차 창 `` $`\Delta\mathbf{A}_{\tau:\tau+W-1}`$ ``: `(B, W, D_res)` (Wuji: `D_res=58`, 접촉 민감 부분공간). scatter 후 나머지 `D_a - D_res` 차원은 nominal 유지 → 보정 창 `` $`\tilde{\mathbf{A}}_{\tau:\tau+W-1}`$ ``: `(B, W, D_a)`
- **World Model 타깃** — visual-tactile clip: `(B, 17, 3, 384, 224)` (2×2 관측 grid: 외부 RGB + 촉각 이미지)

---

## 🧰 모듈 인터페이스

```python
def subtask_planner(instr, images, memory) -> subtask:
    """VLM 기반 느린 semantic 계획기: 실행 서브태스크 ℓ_sub 를 반환 (LoRA-SFT VLM)."""

def tactile_world_model(instr, subtask, images, tactile) -> visual_tactile_subgoal:
    """예측 경로: 현재 서브태스크의 기대 접촉 결과(미래 visual-tactile 서브골 g_t) 생성.
       서브태스크/phase 변경 시에만 호출(event-driven refresh)."""

def visuo_tactile_policy(instr, subtask, subgoal, images, state, tactile)
        -> (nominal_chunk, context_token):
    """중간 속도 flow-matching diffusion Transformer: nominal 액션 청크 Â_{t:t+H-1} + c_t.
       촉각은 image-form 으로 vision-language 브랜치에 투입."""

def tactile_residual_transformer(nominal_lookahead, state_hist, tactile_hist, context_token)
        -> residual_window:
    """반응 경로 TRT: 접촉 민감 부분공간의 잔차 ΔA_{τ:τ+W-1} 예측 (frozen nominal 위)."""
```

- `subtask_planner` — 입력: 지시·다중뷰 이미지·메모리 / 출력: `{ℓ, ℓ_sub, r}` 중 `ℓ_sub` 만 하위 노출 / 외부 계약: 느린 semantic rate, `r`(자유형 추론)은 액션 인터페이스 밖
- `tactile_world_model` — 입력: 지시·서브태스크·이미지·촉각 / 출력: 미래 visual-tactile 서브골(이미지 grid 또는 latent) / 외부 계약: 안정 phase 는 이전 서브골 재사용, refresh 는 이벤트 구동
- `visuo_tactile_policy` — 입력: 프롬프트( $`\ell \oplus \ell_t^{\mathrm{sub}}`$ )·서브골·시각·촉각·proprio / 출력: `(Â, c_t)` / 외부 계약: flow matching 손실, 서브골 부재 시 현재 관측만으로 fallback
- `tactile_residual_transformer` — 입력: sliding lookahead·촉각/proprio 히스토리·`c_t` / 출력: 잔차 창 / 외부 계약: nominal frozen, masked MSE 손실, `D_res` 축에만 적용 후 scatter

---

## ⛓️ 불변식·가정

- (가정 1) **시간척도 분리** — 상위 계획(느림) ⊃ nominal 청크 생성(중간) ⊃ TRT 잔차 refresh(빠름)의 세 갱신율은 엄격히 nested. 데이터 로더/배포 wrapper 가 하드웨어 제어율에 맞춰 시각·촉각·proprio 히스토리를 정렬한다는 전제가 깨지면 잔차 조건화가 무효.
- (가정 2) **잔차 국소성** — 시연 고주파 액션과 nominal lookahead 의 차분(`` $`\mathbf{A}^*-\hat{\mathbf{A}}`$ ``)이 접촉 전이(slip·충격·삽입 오정렬) 근방에서 작고 국소적. 잔차가 nominal 분포를 크게 벗어나야 하면 residual 설계 전제가 붕괴.
- (가정 3) **접촉 민감 부분공간의 분리성** — 액션 `D_a` 차원 중 접촉 보정이 필요한 축(`D_res`, wrist pose + 선택 손가락 관절)이 나머지와 분리 가능하고, 나머지 축은 nominal 을 그대로 따라도 무방.
- (가정 4) **image-form 촉각의 공유 인터페이스** — 인간(EgoTouch palm pressure)·로봇 촉각을 같은 visual-tactile grid 로 변환 가능해, VLM image-language 사전학습이 촉각에도 전이됨. layout 차이가 이 변환으로 흡수된다는 가정.
- (가정 5) **서브골 예측의 하위 유용성** — Tactile World Model 의 예측 서브골이 goal context 로서 nominal 정책을 오도하지 않을 만큼 정확(예측 실패 시 current-obs fallback 이 성능을 해치지 않음).

---

## 📊 하이퍼파라미터·손실

- 피드백-보정 손실 (Eq. 9):

$$\mathcal{L}_{\mathrm{fb}}=\left\|f_{\phi}(\hat{\mathbf{A}}_{\tau:\tau+W-1},\mathbf{s}_{\tau-k:\tau},\mathcal{X}_{\tau-k:\tau},\mathbf{c}_{t})-(\mathbf{A}^{*}_{\tau:\tau+W-1}-\hat{\mathbf{A}}_{\tau:\tau+W-1})\right\|_{2}^{2}$$

- 잔차 합성 (Eq. 7–8): `` $`\Delta\mathbf{A}=f_\phi(\cdot)`$ ``, `` $`\tilde{\mathbf{A}}=\hat{\mathbf{A}}+\Delta\mathbf{A}`$ ``
- nominal 정책: flow matching (데이터-노이즈 보간 → velocity field 적분). 명시적 손실식은 원문 미명시.

| 이름 | 값 | 출처 |
|------|----|----|
| `H` (nominal horizon) | `32` | §4.1, §8 |
| `W` (refinement lookahead) | `16` | §4.1, §8 |
| `C` (commit interval / stride) | `4` (offset `{0,4,8,12}`) | §4.1, §8 |
| `D_a` (액션 차원, Wuji) | `120` (2×48 arm-hand + 9 head + 15 reserved) | §8 |
| `D_res` (잔차 부분공간) | `58` (두 wrist pose 블록 + 선택 손가락 관절) | §8 |
| TRT `d_model` / layers / heads | `512` / `8` / `8` | §8 |
| residual reg weight | `1e-4` | §8 |
| nominal: steps / batch / opt | `30000` / `32` / AdamW | §8 |
| nominal: peak/final lr, warmup | `2.5e-5` / `2.5e-6` / `1000` (cosine) | §8 |
| nominal: grad clip / precision | `1.0` / bfloat16 | §8 |
| TRT: lr / weight decay | `1e-4` / `1e-4` | §8 |
| Subtask Planner LoRA | rank `16`, alpha `32`, dropout `0.05`, lr `1e-4`, 20 ep | §8 |
| Subtask Planner 데이터 | `128,866` records | §3.1, §8 |
| World Model LoRA | rank `64`, target `{q,k,v,o,ffn.0,ffn.2}`, lr `1e-4`, 50 ep | §8 |
| World Model 데이터 | EgoTouch(사전학습) + 10h 로봇(≈1.08M frame@30FPS) | §3.2, §8 |
| World Model 클립 | 17-frame, `384×224` | §3.2, §8 |
| 베이스 모델 | Planner=Qwen3-VL-4B-Instruct, WM=Wan2.2-TI2V-5B | §3.1, §3.2 |
| 태스크당 데이터/평가 | 200 시연 / 100 rollout | §4.1 |

---

## 🎯 평가 메트릭

- **지표** — 태스크 성공률(%) · **설정** — clean / human-perturbation · **비교 baseline** — Pi-0.5, FTP-1, GR00T N1.7 (§4.3, Table 1)
- **지표(World Model)** — Temporal Contact Acc. / Contact IoU / Volumetric IoU(pressure map 임계 `` $`\tau`$ `` 이진화 후) · **비교 baseline** — persistence(current tactile copy), nearest-neighbor subgoal retrieval (§4.5, Table 2)
- **지표(Subtask Planner)** — Subtask Acc. / Execution Success / Transition F1 · **비교 baseline** — zero-shot Qwen3-VL-4B/32B, SFT w/o memory (§4.6, Table 3)

---

## ✨ 변경 의도 (intent)

기존 촉각 VLA 는 촉각을 monolithic 모델의 저주파 관측 토큰으로 붙여 느린 의미 추론·액션 생성·빠른 접촉 피드백을 한 루프에 합칩니다. TouchWorld 는 촉각을 **예측 신호(미래 visual-tactile 서브골)** 와 **반응 신호(고주파 잔차 보정)** 로 분리하고, 세 문제를 서로 다른 시간척도의 분리된 모듈에 배분합니다. 핵심 차별은 (1) 촉각 world model 로 접촉 목표를 *미리* 생성해 goal-conditioned 정책에 넣고, (2) frozen nominal VLA 위에서 접촉 민감 부분공간에만 작동하는 residual Transformer 로 국소 접촉 오류를 *온라인* 보정하며, (3) end-to-end 가 아닌 시간척도별 4단계 분리 학습으로 각 계층을 자기 감독 신호로 최적화하는 것입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — nominal 정책은 flow-matching diffusion Transformer 이므로 `pi0` / `pi05` family 와 가장 가깝습니다(액션 청크 + flow matching). refinement TRT 는 lerobot 에 직접 대응 base 가 없어(frozen policy 위 residual head) `rtc`/action-chunk 처리 주변에 신규 모듈로 얹거나 `UNMAPPABLE` 판정 가능성. Tactile World Model(별도 비디오 DiT)·Subtask Planner(VLM)는 lerobot policy 범위 밖 — 실제 매핑 가부는 `/implement-design` 가 결정.

---

## 🚧 미해결 / 잠정

- nominal flow-matching 정책의 명시적 손실식·noise 스케줄이 원문에 없어 π-계열 표준 flow matching 으로 가정.
- `D_res=58` 접촉 민감 부분공간의 축 선택 규칙(어느 손가락 관절 포함)이 §8 에 "selected hand joints" 로만 기술 — 정확 인덱스 미명시, embodiment 별 수동 지정으로 가정.
- 상위 계획 계층·refinement 의 실제 갱신 Hz(절대 rate)는 "하드웨어 제어율 의존"으로만 기술, 절대값 미명시 — 의미 단위(`H`/`W`/`C`)로만 고정.
- 이미지형 촉각 렌더링의 구체 정규화·해상도(nominal 브랜치)가 원문 미명시.
- Tactile World Model 서브골이 nominal 정책에 goal 이미지로 들어가는지 latent 로 들어가는지 "images or latents" 로 병기 — 어느 경로가 최종인지 미확정.
