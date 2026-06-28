# Design — G$`^3`$VLA: Geometric inductive bias for Vision-Language-Action Models

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | G$`^3`$VLA: Geometric inductive bias for Vision-Language-Action Models |
| 링크 | [arXiv:2606.24472](https://arxiv.org/abs/2606.24472) |
| 분석 문서 | [`analysis/2606.24472/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-28 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`V`=뷰 수, `P`=뷰당 패치 토큰 수, `H`=action horizon)로 기록합니다. $`\pi_{0}`$ 인스턴스 기준: 입력 $`224\times224`$, SigLIP $`16\times16`$ 패치 → 뷰당 `P=256` 토큰.

- **입력 — RGB**: `(B, V, 3, 224, 224)`, float, base/wrist 등 calibrated 뷰. padding 뷰는 invalid-view mask 동반.
- **입력 — intrinsics `K`**: `(B, V, 3, 3)`, float. 이미지 회전/리사이즈 컨벤션에 맞춰 보정된 행렬.
- **입력 — extrinsics `T`**: `(B, V, 4, 4)`, float, camera-to-world. PRoPE 에서 world-to-camera view 행렬로 변환.
- **입력 — proprio `s_t`**: `(B, d_s)`, float (base VLA 그대로).
- **입력 — language `l`**: 토큰 시퀀스 (base VLA 그대로).
- **입력 — view mask**: `(B, V)`, bool. 무효/padding 뷰 표시.
- **중간 — patch token `z`**: `(B, V, P, d)`, float, SigLIP 인코더 출력.
- **중간 — ray map `R^v`**: `(B, V, 2, 16, 16)` (또는 패치 그리드 정렬 형태), float, $`(K^v)^{-1}u`$ 의 앞 2채널.
- **출력 — fused token `H`**: `(B, V·P, d)`, float, 원래 VLA token 인터페이스와 동일 shape·의미.
- **출력 — action chunk**: `(B, H, d_a)`, float (base VLA action space 불변; $`\pi_{0}`$ 는 flow-matching).
- **학습 전용 출력 — point map 예측**: ray $`\hat{q}`$ `(B, V, 2, 224, 224)`, log-$`z`$ $`\hat{d}`$ `(B, V, 1, 224, 224)`. 추론 시 미생성.
- **학습 전용 target — teacher point map**: ray `(…,2,224,224)` + log-$`z`$ `(…,1,224,224)` + confidence logit `(…,1,224,224)`. offline cache.

정규화 가정: ray 좌표는 pinhole 정규화(metric depth 가정 없음, 3번째 좌표 고정 후 앞 2성분). log-$`z`$ 는 teacher 의 **local** depth scale($`d=\log z`$), global metric 재구성 아님(원문 명시).

---

## 🧰 모듈 인터페이스

```python
def ray_embedding(z: Tensor,            # (B,V,P,d) SigLIP patch tokens
                  K: Tensor,            # (B,V,3,3) intrinsics
                  ) -> Tensor:          # (B,V,P,d) intrinsic-aware tokens
    """K^{-1} 로 패치별 ray map R^v 를 만들고 zero-init projection G_phi 로
       투영해 z 에 가산 (Eq.3-4). 시작 시 항이 0 이라 사전학습 거동 보존.
       인코더 뒤·LLM 앞에서만 작동 — ViT 내부 미침투."""

def cross_view_fusion(z0: Tensor,       # (B,V,P,d) ray-augmented tokens
                      K: Tensor, T: Tensor,   # intrinsics, camera-to-world
                      view_mask: Tensor,      # (B,V) valid-view mask
                      ) -> Tensor:      # (B,V*P,d) fused tokens H
    """1) frame attention: 뷰 내부 독립 처리 (뷰-국소 구조 보존)
       2) global cross-view attention 1층: PRoPE(K,T,patch loc)를 q/k/v 투영
          위치 신호로 양방향 attend (Eq.5). invalid 뷰는 마스킹."""

def aux_point_head(H: Tensor,           # (B,V*P,d) post-fusion, pre-projector
                   ) -> tuple[Tensor, Tensor]:  # (q_hat, d_hat) @224x224
    """학습 전용 디코더. 뷰별 256 토큰을 16x16 reshape → hidden 512,
       transformer 2블록(8 head, 2D RoPE, QK-norm, MLP4, LayerScale 0.01)
       → transposed-conv 256/128/64 → bilinear 224x224, zero-init 출력 2개.
       추론 시 폐기."""

def distill_loss(q_hat, d_hat, q, d,    # 예측/타깃 ray·log-z
                 conf_logit: Tensor, tau: float = 0.1,  # confidence gate
                 ) -> Tensor:           # scalar L_distill (Eq.6-7)
    """m = 1[sigma(conf_logit) > tau] 로 hard gate, 게이트된 픽셀만
       (1/2||q_hat-q||^2 + (d_hat-d)^2) 합산, sum(m)+eps 로 정규화."""
```

- `ray_embedding` → `cross_view_fusion` → (action model) 순으로 base VLA 의 vision encoder 출력과 action expert 사이에 삽입. `aux_point_head` 는 fused token 에서 분기(학습 시만). loss 는 $`\mathcal{L}=\lambda_{\mathrm{act}}\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{distill}}\mathcal{L}_{\mathrm{distill}}`$ (Eq.8), $`\mathcal{L}_{\mathrm{act}}`$ 는 base VLA 목적함수 그대로($`\pi_{0}`$ = flow-matching).

---

## ⛓️ 불변식·가정

- (가정 1) 입력 intrinsics `K`·extrinsics `T` 가 이미지 픽셀 좌표와 정합 — 이미지 회전/리사이즈 변환을 K 에도 동일 적용해 ray 가 인코더가 보는 이미지와 일치해야 함. 깨지면 ray·PRoPE 신호가 잘못된 prior 가 됨.
- (가정 2) ray map 은 pinhole 모델로 3번째 좌표가 고정 — 앞 2성분이 metric depth 가정 없이 image-plane ray 를 정의(Eq.3 성립 조건).
- (가정 3) `G_phi` 및 보조 head 출력 head 가 zero-init — finetuning 시작 시 가산항이 0 이라 사전학습 token 분포 보존. 깨지면 Stage 2 초기에 backbone 거동이 교란.
- (가정 4) teacher confidence 가 신뢰도와 단조 — hard gate $`\sigma(c)>\tau`$ 가 "신뢰 픽셀 선택" 으로 유효하려면 confidence 가 실제 정확도와 정렬돼야 함. 깨지면 RoboTwin2.0 식 역효과(teacher < baseline).
- (가정 5) geometry-aware token 이 action 생성 경로에 직접 도달 — single-stream(token→action 직결)에서 이득 최대. cross-attention 병목(two-tower)이면 신호 감쇠(GR00T 1.5 실증).
- (가정 6) 다카메라 calibration coupling 존재 — cross-view fusion 의 가치는 뷰들이 알려진 K·T 로 기하 결합돼 있을 때 발생. 단일 뷰면 ray embedding 단독 기여만 남음.

---

## 📊 하이퍼파라미터·손실

- 결합 손실: $`\mathcal{L}=\lambda_{\mathrm{act}}\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{distill}}\mathcal{L}_{\mathrm{distill}}`$ (Eq.8), $`\mathcal{L}_{\mathrm{act}}`$ = base VLA action 목적함수(불변, $`\pi_{0}`$=flow-matching).
- 증류 손실(Eq.7):

$$\mathcal{L}_{\mathrm{distill}}=\frac{\sum_{v,u}m_{u}^{v}\!\left(\tfrac{1}{2}\lVert\hat{q}_{u}^{v}-q_{u}^{v}\rVert_{2}^{2}+(\hat{d}_{u}^{v}-d_{u}^{v})^{2}\right)}{\sum_{v,u}m_{u}^{v}+\epsilon}$$

- confidence gate(Eq.6): $`m_{u}^{v}=\mathbf{1}[\sigma(c_{u}^{v})>\tau]`$.

| 이름 | 값 | 출처 |
|------|----|----|
| `tau` (confidence gate) | `0.1` | §3.2, Eq.(6) |
| Stage 1 `steps` | `5k` | Appendix D, Table 6 |
| Stage 1 `lambda_act` | `0.1` | Table 6 |
| Stage 1 `lambda_distill` | `1.0` | Table 6 |
| Stage 1 `warmup` / `LR` | 500 steps; $`2.5\times10^{-5}\to2.5\times10^{-6}`$ | Table 6 |
| Stage 2 `steps` | `30k` | Table 6 |
| Stage 2 `lambda_act` | `1.0` | Table 6 |
| Stage 2 `lambda_distill` | `0.05` | Table 6 |
| Stage 2 `warmup` / `LR` | 1k steps; $`2.5\times10^{-5}\to2.5\times10^{-6}`$ | Table 6 |
| optimizer | AdamW, betas $`(\beta_1{=}0.9,\beta_2{=}0.95)`$, $`\epsilon{=}10^{-8}`$ | Appendix D |
| weight decay | `negligible` | Appendix D |
| grad clip | `1.0` (global) | Appendix D |
| global batch size | `32` | Appendix D |
| precision | `bfloat16` | Appendix D |
| LR schedule | `cosine decay (both stages)` | Table 6 |
| input resolution | `224×224` | Appendix A |
| patch grid / tokens | `16×16` / `256` per view | Appendix A |
| aux head hidden | `512`, transformer 2블록, 8 head, MLP ratio 4, LayerScale 0.01 | Appendix A |
| aux head upsample | transposed-conv `256,128,64` → bilinear `224×224` | Appendix A |
| `lambda_distill` (1-stage 변형) | (원문 미명시 — weak aux regularizer 로만 기술) | Appendix E |

---

## 🎯 평가 메트릭

- **지표** — task success rate (%). 시뮬은 3회 독립 평가의 산술평균(seed 7 고정, LIBERO task 당 50 rollout, chunk 의 첫 5 action 실행 후 재쿼리).
- **비교 baseline** — 동일 데이터로 finetune 한 원본 $`\pi_{0}`$ (geometric 모듈·point-map supervision 없음). 추가로 $`\pi_{0.5}`$ reproduced baseline, GR00T 1.5 baseline.
- **임계값/판정** — LIBERO 환경의 task completion 반환; RoboCasa24 는 chunk 50 action·최대 500 step 후 mean success; RoboTwin2.0 은 accepted-seed 프로토콜의 success predicate. 실로봇은 부분 점수 허용($`0, 0.5, 1^{*}, 1`$).
- **핵심 비교축** — (i) supervision 출처 GT vs $`\pi^{3}`$X, (ii) ablation w/o Ray / w/o PRoPE / 1-Stage, (iii) viewpoint ID vs OOD(unseen 카메라 뷰 11–13). G$`^3`$VLA(GT)가 LIBERO 평균 84.6→88.1(+3.5)을 baseline 대비 목표선으로 사용.

---

## ✨ 변경 의도 (intent)

기존 geometry-grounded manipulation 은 두 부류였습니다 — 명시적 3D(voxel/point cloud)로 policy 인터페이스를 바꾸거나(PerAct/Act3D), geometry 를 인코더에 distill 해 stem 을 교체(eVGGT)하는 것. G$`^3`$VLA 의 의도는 **사전학습 VLA 를 전혀 깨지 않고 기하를 더하는 어댑터** 입니다: action space·imitation 목적함수·backbone 가중치를 불변으로 두고, calibrated 카메라 기하를 (i) intrinsic ray embedding(zero-init 가산), (ii) PRoPE 기반 cross-view attention bias, (iii) 추론 시 폐기되는 보조 point-head 증류로만 token 경로에 주입합니다. 핵심 차별점은 "기하가 token 표현을 통해서만 들어가고 action model 은 그대로" 라는 비침습성과, depth 센서·수동 annotation 없이 feed-forward teacher($`\pi^{3}`$X)로 dense supervision 을 공짜로 얻는 점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` (논문 메인 인스턴스, flow-matching action expert 직결 single-stream). `pi05` 도 직접 후보(논문이 $`\pi_{0.5}`$ 검증). 삽입 지점은 vision encoder 출력 ↔ action expert 입력 사이의 token 스트림. GR00T 류 two-tower 구조는 이득 감쇠가 보고되었으므로(§4.3) lerobot 내 cross-attention 분리형 policy 는 비권장.

---

## 🚧 미해결 / 잠정

- 1-stage ablation 변형의 정확한 `lambda_distill` 값이 원문에 명시되지 않음("weak auxiliary regularizer" 로만 기술) — Appendix E.
- ray map projection `G_phi` 의 구체 구조(MLP vs conv, 차원)가 본문에 명시되지 않아 "패치 그리드로 투영하는 학습 임베딩" 수준으로만 특정.
- PRoPE 투영 변환의 정확한 형태는 원논문(Cameras as Relative Positional Encoding, [12])에 위임 — 본 논문은 K·T·patch loc 에서 q/k/v 투영을 유도한다고만 기술.
- $`\pi^{3}`$X teacher 의 정확한 버전·체크포인트, LIBERO→LeRobot 변환의 이미지 회전 컨벤션 세부는 재현 시 확정 필요(Appendix B/C 가 절차는 기술하나 수치 파라미터 일부 미상).
- `epsilon`(distill 정규화 분모)·proprio 차원 `d_s`·action 차원 `d_a` 등은 base VLA 설정을 따르며 본 논문 미명시.
