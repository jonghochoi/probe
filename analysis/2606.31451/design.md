# Design — UniTac: A Unified Multimodal Model for Cross-Sensor Tactile Understanding and Generation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | UniTac: A Unified Multimodal Model for Cross-Sensor Tactile Understanding and Generation |
| 링크 | [arXiv:2606.31451](https://arxiv.org/abs/2606.31451) |
| 분석 문서 | [`analysis/2606.31451/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-02 |

---

## 🧮 데이터 계약

- **입력 (촉각, 이해·재구성 공통)** — `tactile_video` $`V_{i}`$: 비주오택타일 비디오(접촉 프레임은 배경 프레임과의 차분으로 필터링). touch encoder 통과 후 잠재 토큰 $`\mathbf{Z}_{i}=E_{\text{touch}}(V_{i})\in\mathbb{R}^{L_{v}\times d}`$, $`d=768`$ ( $`L_{v}`$ 는 원문 미명시). 잠재는 물체 성분·센서 성분의 연접 $`\mathbf{Z}_{i}=[\mathbf{Z}_{i}^{\text{obj}},\,\mathbf{Z}_{i}^{\text{sen}}]`$ 로 취급
- **입력 (비접촉 참조)** — `noncontact_image` $`V_{i}^{\text{sen}}`$: target 센서의 비접촉 프레임 1장 → $`Z_{i}^{\text{sen}}=E_{\text{touch}}(V_{i}^{\text{sen}})`$ (SPSS 의 센서 prior 분기 조건)
- **입력 (텍스트)** — `text` $`T_{i}`$: 촉각 서술문. 이해 시 지시 프롬프트 $`\Pi_{i}`$ (물성 서술 / 센서 식별 중 택1)와 함께 MLLM 입력 시퀀스 $`X_{i}=[\texttt{<T\_VID>},\ \mathbf{Z}_{i},\ \texttt{</T\_VID>},\ \Pi_{i},\ T_{i}]`$ 구성
- **입력 (생성 쿼리)** — `touch_queries` $`\mathbf{Q}_{i}`$: 학습 가능한 쿼리 $`N=64`$ 개 → MLLM 출력 $`\mathbf{\hat{Q}}_{i}\in\mathbb{R}^{N\times d}`$
- **입력 (센서 토큰)** — `sensor_tokens` $`\mathbf{S}`$: 센서 유형당 5개의 학습 토큰 (touch encoder 소속, 768-d) → $`S^{\prime}=\mathrm{MLP}_{\text{sen}}(S)`$ 로 사영 후 조건에 연접 $`\mathbf{F}_{i}=[\mathbf{\hat{Q}}_{i};S^{\prime}]`$
- **출력 (이해)** — next-token 텍스트 (물성 서술문 / 센서 명)
- **출력 (생성, 이미지)** — `tactile_image`: `512×512` 촉각 이미지 (SANA 디코더)
- **출력 (생성, 비디오)** — `tactile_video`: 13-frame `448×448` 시퀀스 (Wan v2.2 디코더, 동일 조건화)
- **정밀도** — 전 단계 bf16 mixed precision 학습

---

## 🧰 모듈 인터페이스

```python
def touch_encoder(video: TactileVideo) -> LatentTokens:  # AnyTouch ViT-B/16
    """멀티센서 사전학습 촉각 인코더. (L_v, 768) 잠재 토큰을 반환하며,
    잠재는 [Z_obj, Z_sen] 이중 성분을 담는다. 센서 유형당 5개의
    learnable sensor token 을 내장한다."""

def mllm(seq: TokenSequence) -> TextTokens:  # Qwen-VL 2.5 (3B/7B)
    """공유 backbone. visual projector 를 tactile embedding adaptor 로
    교체해 <T_VID> … </T_VID> 로 감싼 촉각 토큰을 텍스트 스트림에 접합.
    이해: next-token prediction. 생성: (T_i, Q) -> Q_hat (N=64, 768-d)."""

def mlp_sen(sensor_tokens: Tensor) -> Tensor:
    """sensor token 을 projector 조건 공간으로 사영하는 어댑터."""

def dit_projector(x_t: Tensor, t: float, cond: Tensor) -> Tensor:  # NextDiT 24-layer
    """조건부 속도장 v_theta1(x_t | t, F). F = [Q_hat; S'].
    MLLM 의미 출력을 touch-encoder 잠재공간으로 정렬 (rectified flow)."""

def touch_decoder(x_t: Tensor, t: float, cond: Tensor) -> Tensor:  # SANA / Wan v2.2
    """조건부 속도장 v_theta2(x_t | t, F_cond). 재구성 학습 시 F_cond 는
    Bernoulli(p_drop) 로 Z_sen(비접촉) / Z_obj+sen(접촉) 중 택1.
    추론 시 SPSS: v_sen 분기와 v_obj+sen 분기를 모두 평가."""

def spss_sample(decoder, Z_sen, Z_objsen, s: float = 1.5, steps: int = 50) -> TactileSignal:
    """Sensor-Prior Sampling: v_hat = v(x|t,Z_sen) + s*[v(x|t,Z_objsen) - v(x|t,Z_sen)].
    50-step 결정적 rectified-flow 적분으로 최종 촉각 신호 복원."""
```

- **이해 경로** — `touch_encoder` → `mllm` (next-token). 생성 모듈과 독립.
- **생성 경로 (추론)** — `mllm(T, Q)` → `dit_projector` 표준 flow 적분(50 step)으로 정렬 잠재 $`\tilde{Z}_{i}^{\text{obj+sen}}`$ 생성 → `touch_decoder` 를 SPSS 로 적분해 신호 합성. projector 와 decoder 는 각각 독립적으로 학습된 두 개의 flow 모델.
- **학습 의존성** — Stage I(재구성)과 DLMC(이해)는 병렬 학습 가능(MLLM 비관여 / 관여로 분리). Stage II(정렬)는 두 단계 수렴 후.

---

## ⛓️ 불변식·가정

- (가정 1) — 촉각 잠재는 물체 성분과 센서 성분으로 분해 가능하다: $`\mathbf{Z}_{i}=[\mathbf{Z}_{i}^{\text{obj}},\,\mathbf{Z}_{i}^{\text{sen}}]`$. 이 분해가 무너지면 SPSS 의 두 분기 구분과 sensor identification 감독이 모두 무효
- (가정 2) — 비접촉 프레임은 센서 구성 정보만 담고 물체 정보를 담지 않는다 (비접촉 데이터의 의미는 센서 수준에 국한). 접촉 프레임 = 센서 구성 위에 물체 물성이 중첩된 신호
- (가정 3) — 접촉 프레임은 배경(비접촉) 프레임과의 픽셀 차분으로 식별 가능하다 (데이터 전처리 불변식)
- (가정 4) — rectified flow 의 직선 보간 경로: $`\mathbf{x}_{t}=(1-t)\,\mathbf{z}+t\,\mathbf{Z}_{i}`$ 의 목표 속도는 상수 $`\mathbf{u}_{t}=\mathbf{Z}_{i}-\mathbf{z}`$ (노이즈 스케줄 불요, 결정적 ODE 샘플링)
- (가정 5) — SPSS 가 유효하려면 decoder 가 학습 중 센서-단독 조건( $`Z^{\text{sen}}`$ )과 접촉 조건( $`Z^{\text{obj+sen}}`$ ) 모두에 노출되어야 한다 (Bernoulli $`p_{\text{drop}}`$ 조건 드롭이 이를 보장)
- (가정 6) — 센서 유형별 sensor token 이 해당 센서의 구성 분포를 대표한다 — 미학습 센서 유형에는 대응 token 이 없으므로 zero-shot 센서 일반화는 계약 밖

---

## 📊 하이퍼파라미터·손실

**손실 식 (이해, DLMC)** — next-token prediction (식 1) + 이중 감독 가중합 (식 2):

$$\mathcal{L}=-\sum_{t=2+L_{v}+|\Pi_{i}|}^{|X_{i}|-1}\log p_{\theta}(x_{i,t+1}\mid x_{i,\leq t})$$

$$\mathcal{L}_{\text{DLMC}}=\mathcal{L}_{\text{prop}}+\lambda_{\text{sen}}\,\mathcal{L}_{\text{sen}}$$

**손실 식 (생성)** — Stage I 재구성 $`L_{\text{rec}}=\big\|v_{\theta_{2}}(x_{t}\mid t,F_{i}^{\text{cond}})-u_{t}^{\ast}\big\|_{2}^{2}`$, Stage II 정렬 (식 5):

$$\mathcal{L}_{\text{align}}^{\text{RF}}=\mathbb{E}_{t\sim\mathcal{U}(0,1),\mathbf{z}\sim\mathcal{N}(0,I),\,\mathbf{Z}_{i}}\!\bigl\|v_{\theta}(\mathbf{x}_{t}|t,\mathbf{F}_{i})-(\mathbf{Z}_{i}-\mathbf{z})\bigr\|_{2}^{2}.$$

**샘플링 식 (SPSS)** — CFG 무조건 분기를 센서 prior 로 교체 (식 7):

$$\hat{v}_{\theta}(\mathbf{x}_{t}|t,\;\mathbf{Z}_{i}^{\text{obj}},\mathbf{Z}_{i}^{\text{sen}})=v_{\theta}(\mathbf{x}_{t}|t,\;\mathbf{Z}_{i}^{\text{sen}})+s\big[v_{\theta}(\mathbf{x}_{t}|t,\;\mathbf{Z}_{i}^{\text{obj}},\mathbf{Z}_{i}^{\text{sen}})-v_{\theta}(\mathbf{x}_{t}|t,\;\mathbf{Z}_{i}^{\text{sen}})\big]$$

- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | $`\lambda_{\text{sen}}`$ | 0.1 | §0.A.2, Eq. (2), Table B |
  | `touch_queries` $`N`$ | 64 | §3.2, Table D |
  | guidance scale $`s`$ | 1.5 | §0.A.3, Table E |
  | flow steps | 50 | §0.A.3 |
  | 이미지 재구성 epochs / batch | ~20 / 512 (ZeRO-1) | §0.A.2 |
  | 이미지 재구성 lr | 1e-4 → cosine 1e-5, warmup 5000 steps | §0.A.2 |
  | 비디오 재구성 batch / accum / clip | 8 / 16 / max-norm 1 (ZeRO-2) | §0.A.2 |
  | 정렬 epochs / batch / lr | 100 / 512 / 1e-4 | §0.A.2 |
  | 정밀도 / 하드웨어 | bf16 / 8×A800 80GB | §0.A.2 |
  | encoder 출력 차원 $`d`$ | 768 (ViT-B/16) | §0.A.1 |
  | sensor token 수 | 센서 유형당 5 | §0.A.1 |
  | 생성 해상도 | 이미지 512×512 · 비디오 13-frame 448×448 | §0.A.1 |
  | $`p_{\text{drop}}`$ | (원문 미명시) | Algorithm 2 |
  | $`L_{v}`$ (촉각 토큰 길이) | (원문 미명시) | §3.1 |

---

## 🎯 평가 메트릭

- **지표 (이해)** — PHYSICLEAR-Test 6개 태스크 정확도: PC · POM · PSS · Hardness · Roughness · Texture 및 Average · **임계값** — Average 66.51 (UniTac-7B) / 60.61 (UniTac-3B) · **비교 baseline** — Octopi-7B 57.31, GPT-4o 31.65, JanusPro-7B 36.29 등 (Table 1)
- **지표 (생성)** — SSIM · PSNR, 생성 60K 장 vs ground truth, 4개 센서(Digit, GelSight, GelSight Mini, Duragel) · **임계값** — 평균 0.836 SSIM / 19.93 PSNR · **비교 baseline** — TextToucher 0.816/18.65, JanusPro-7B 0.753/18.46 (Table 2)
- **지표 (생성 데이터 효용)** — 크로스-센서 grasp 분류 정확도: source-only 대비 생성 증강 후 target 센서 정확도 (Digit→GelSight 50.00→99.37%; 실데이터 상한 대비 1–2%p 이내, Table 5/F)
- **지표 (ablation 게이트)** — sensor identification 제거 시 PHYSICLEAR -3.23점, SPSS 제거(=vanilla CFG) 시 SSIM 0.836→0.817 (Table 3/E)

---

## ✨ 변경 의도 (intent)

기존 촉각 모델은 이해와 생성을 별개로 다루고 센서 도메인을 암묵적으로 뭉뚱그렸습니다. UniTac 의 차별점은 (1) 촉각 취득의 물리 과정(비접촉→접촉)을 표현 분해( $`Z^{\text{obj}}`$ / $`Z^{\text{sen}}`$ )·감독 설계(물성 서술 + 센서 식별)·샘플링(SPSS)까지 일관되게 새긴 것, (2) CFG 의 무조건 분기를 "센서 prior" 분기로 교체해 생성 궤적이 실제 센서 거동과 정합하도록 만든 것, (3) 고립된 공개 촉각 데이터셋들을 단일 대규모 코퍼스로 통합해 이해·생성을 한 backbone 에서 학습한 최초의 촉각 UMM 이라는 점입니다. prior art 대비: Touch2Touch 류 센서쌍 변환 → 임의 센서 조건부 합성, Octopi 류 이해 전용 → 이해·생성 왕복, AnyTouch 표현 학습 → 언어 접지 + 생성까지 확장.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접적 base 후보 없음: UniTac 은 action policy 가 아니라 촉각 이해·생성 UMM 이므로 lerobot 의 policy family(`pi0`/`pi05`/`act`/`diffusion` 등)와 좌표계가 겹치지 않습니다. 가장 가까운 접점은 부록의 VTLA 변형(π0.5 에 촉각 잠재/예측 촉각 잠재를 조건으로 주입, §0.B.1)이지만 이는 논문의 핵심 기여가 아닌 검증용 구성입니다.

---

## 🚧 미해결 / 잠정

- $`L_{v}`$ (촉각 잠재 토큰 길이)와 프레임 샘플링 정책이 원문에 없음 — 데이터 계약에서 shape 를 `(L_v, 768)` 로만 기록
- $`p_{\text{drop}}`$ (Stage I 조건 드롭 확률) 원문 미명시 — SPSS 전제 조건(가정 5)의 핵심 값이므로 재현 시 스윕 필요
- touch encoder 의 학습 여부가 본문 내 상충: §3.1/§3.2 는 "pretrained touch encoder" 를 채택한다고 기술하나 §0.A.2 는 재구성 단계가 "jointly optimizes the touch encoder $`E_{\text{touch}}`$ and decoder" 라고 기술 — encoder freeze 여부를 잠정 미해결로 둠
- MLLM 미세조정 범위(full FT vs PEFT)와 tactile embedding adaptor 의 구조(레이어 수·차원) 미명시
- 비디오 생성(Wan v2.2)의 학습 데이터 구성·에폭 등 상세 미명시 (이미지 설정과 "일관" 이라고만 기술)
- 텍스트-조건 생성 시 target 센서 선택 방법은 사용자가 sensor token / 비접촉 참조 이미지를 지정하는 것으로 읽히나, 명시적 인터페이스 정의는 없음
