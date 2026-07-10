# Design — LAMP: Latent Motion Prior-Guided Real-World Learning for Dexterous Hand Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | LAMP: Latent Motion Prior-Guided Real-World Learning for Dexterous Hand Manipulation |
| 링크 | [arXiv:2607.06323](https://arxiv.org/abs/2607.06323) |
| 분석 문서 | [`analysis/2607.06323/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-10 |

---

## 🧮 데이터 계약

- **입력 — 이미지**: 2 RGB 뷰(front + wrist), shape `(B, 2, H, W, 3)` — 해상도·크롭은 환경 config 소관 (원문 미명시), frozen ImageNet-pretrained 인코더 전제의 ImageNet 정규화 가정
- **입력 — robot state**: `(B, 12)` float — 팔 6-D + 손 6-D 의 현재 상태
- **입력 — hand history** `H_t`: `(B, K, D_hand)` float — 최근 `K=8` 개의 **절대** hand target( `D_hand=6` ), 궤적 시작부는 첫 기록 target 으로 padding
- **출력 (BC) — arm command**: `(B, D_arm)` float, `D_arm=6` , native 팔 좌표(잠재화하지 않음)
- **출력 (BC) — latent offset** $`\Delta z_{t}`$ : `(B, d_z)` float, `d_z=2`
- **출력 (decoded) — hand target**: `(B, D_hand)` float — 절대 목표; 실행 시 환경 래퍼가 하드웨어 저수준 delta 로 변환
- **출력 (RL) — residual** $`u_{t}=(\rho_{t}^{\mathrm{arm}},\rho_{t}^{z})`$ : `(B, D_arm + d_z)` = `(B, 8)` , tanh-squashed Gaussian, 스케일 `s_arm` / `s_z` 로 가산 (값은 원문 미명시)
- **보상**: sparse binary $`r_{t}\in\{0,1\}`$ — 시각 분류기 $`p_{\mathrm{cls}}(o_{t+1})>0.90`$ 지시 함수, `r=1` 시 에피소드 종료
- **노이즈 증강**: LMPM 학습 시 hand-history std 0.01, BC 학습 시 arm-state·hand-history std 0.10

---

## 🧰 모듈 인터페이스

```python
def lmpm_encoder(hand_history) -> tuple:      # (B, K, D_hand) -> ((B, d_z), (B, d_z))
    """히스토리 조건부 Gaussian prior 통계 (mu_t, sigma_t) 를 출력. Stage 1 이후 동결."""

def lmpm_decoder(z) -> "hand_target":         # (B, d_z) -> (B, D_hand)
    """잠재 벡터를 다음 스텝 절대 hand target 으로 복원. Stage 1 이후 동결."""

def bc_policy(obs, mu, sigma) -> tuple:       # -> ((B, D_arm), (B, d_z))
    """관측 + prior 통계로 native 팔 명령과 잠재 오프셋 Δz 를 예측.
    최종 손 목표는 lmpm_decoder(mu + Δz). Stage 3 에서 동결(stop-gradient)."""

def residual_actor(obs, hand_history) -> "u": # -> (B, D_arm + d_z), tanh-squashed
    """s_t=(o_t, H_t) 에서 잔차 u_t=(ρ_arm, ρ_z) 를 샘플. SAC(RLPD) 로 학습."""

def residual_critic(obs_env_action) -> "q":   # 실행된 12-D 환경 action 위에서 학습
    """Q(s_t, u_t) — ensemble 2."""

def reward_classifier(obs) -> "logit":        # 2뷰 RGB, no proprioception
    """성공 확률 logit. sigmoid > 0.90 이 sparse reward 및 성공 판정."""
```

- **호출 계약** — 실행 action 은 $`\tilde{a}_{t}=(a_{t,\mathrm{bc}}^{\mathrm{arm}}+s_{\mathrm{arm}}\rho_{t}^{\mathrm{arm}},\,D_{\theta}(z_{t,\mathrm{bc}}+s_{z}\rho_{t}^{z}))`$ , 여기서 $`z_{t,\mathrm{bc}}=\mu_{t}+\Delta z_{t,\mathrm{bc}}`$ . 잔차는 stop-gradient 된 BC core action 에 가산됩니다.
- **버퍼 계약** — RLPD 배치는 시연 버퍼와 온라인 버퍼에서 반반 샘플( `128 + 128` ). critic-to-actor ratio 2 (critic 단독 1회 + critic·actor·temperature 1회).

---

## ⛓️ 불변식·가정

- (가정 1) — Stage 1 종료 후 인코더 $`E_{\phi}`$ ·디코더 $`D_{\theta}`$ 는 동결 — IL 과 RL 이 **동일한** 디코딩 계약을 공유해야 잔차 탐사의 국소성 주장이 성립
- (가정 2) — 손 동작의 유효 차원이 `d_z` 로 충분히 낮음(시연 hand 궤적이 저차원 manifold 를 이룸) — 깨지면 재구성 오차가 커져 인터페이스 자체가 무효
- (가정 3) — 잠재 잔차의 디코딩 결과는 시연 manifold 근방( $`\Delta\mathrm{NN}/\mathrm{Disp}`$ 가 Raw/PCA 대비 낮음) — 접촉-보존 탐사 주장의 근거
- (가정 4) — hand target 은 절대 좌표로 저장·예측되고 하드웨어 delta 변환은 환경 래퍼 소관 — 상대 명령로 바꾸면 히스토리 조건화 의미가 달라짐
- (가정 5) — BC 는 one-step 목표 예측(action chunking 없음) — 히스토리 `H_t` 갱신이 매 스텝 이루어진다는 전제
- (가정 6) — 팔 명령은 native 좌표 유지 — 과제 수준 변화(접근 방향·물체 pose·배치 기하)는 잠재 압축 대상이 아님

---

## 📊 하이퍼파라미터·손실

**손실 식** (원문 표기 verbatim):

$$\mathcal{L}_{\mathrm{prior}}=\mathbb{E}_{(H_{t},h_{t+1})}\!\left[\|D_{\theta}(z_{t})-h_{t+1}\|_{2}^{2}+\beta D_{\mathrm{KL}}\!\left(q_{\phi}(z_{t}|H_{t})\,\|\,\mathcal{N}(0,I)\right)\right]$$

$$\mathcal{L}_{\mathrm{BC}}=\|\hat{a}_{t}^{\mathrm{arm}}-a_{t}^{\mathrm{arm}}\|_{2}^{2}+\lambda_{h}\|\hat{h}_{t+1}-h_{t+1}\|_{2}^{2}+\lambda_{z}\|\Delta\hat{z}_{t}\|_{2}^{2}$$

$$\mathcal{L}_{Q}=\mathbb{E}_{\mathcal{B}}\!\left[(Q_{\omega}(s_{t},u_{t})-y_{t})^{2}\right],\quad y_{t}=r_{t}+\gamma\,\mathbb{E}_{u^{\prime}\sim\pi_{\eta}}\!\left[\bar{Q}(s_{t+1},u^{\prime})-\alpha\log\pi_{\eta}(u^{\prime}|s_{t+1})\right]$$

$$\mathcal{L}_{\pi}=\mathbb{E}_{s_{t}\sim\mathcal{B},\,u_{t}\sim\pi_{\eta}}\!\left[\alpha\log\pi_{\eta}(u_{t}|s_{t})-Q_{\omega}(s_{t},u_{t})\right]$$

$$\mathcal{L}_{\mathrm{cls}}=-\mathbb{E}_{(o,y)}\left[y\log p_{\mathrm{cls}}(o)+(1-y)\log(1-p_{\mathrm{cls}}(o))\right]$$

**하이퍼**:

| 이름 | 값 | 출처 |
|------|----|----|
| `d_z` (잠재 차원) | 2 | §B.2, Table B.1 |
| `K` (히스토리 길이) | 8 hand targets | §B.1, Table B.1 |
| `beta` (KL 가중치) | $`10^{-3}`$ | §B.2 |
| LMPM encoder/decoder | MLP width 256 | §B.2, Table B.1 |
| LMPM optimizer / batch / LR / steps | AdamW / 256 / $`2\times 10^{-3}`$ / 20k | Table B.1 |
| LMPM warmup | 500 LR steps, 2000 KL steps | Table B.1 |
| LMPM 노이즈 증강 | hand-history std 0.01 | Table B.1 |
| BC 시각 인코더 | frozen ImageNet ResNet-18 (뷰별 1개) | §B.2 |
| BC head (`CoreActionHead`) | MLP `[512, 512, 256]` | §B.2, Table B.1 |
| BC optimizer / batch / LR / steps | AdamW / 128 / $`5\times 10^{-4}`$ / 20k | Table B.1 |
| BC 노이즈 증강 | arm-state·hand-history std 0.10 | Table B.1 |
| gradient clip | 1.0 (LMPM·BC 공통) | Table B.1 |
| `lambda_h`, `lambda_z` | (원문 미명시) | 식 (6) |
| RL actor/critic | MLP `[256, 256]`, tanh, layer norm | Table B.2 |
| critic ensemble | 2 | Table B.2 |
| discount $`\gamma`$ | 0.97 | Table B.2 |
| RL batch | 256 = 온라인 128 + 시연 128 | Table B.2 |
| critic-to-actor ratio | 2 | Table B.2 |
| replay capacity | 200k transitions | Table B.2 |
| 학습 시작 | 온라인 100 전이 이후 | Table B.2 |
| network publish 간격 | 50 learner steps | Table B.2 |
| 초기 temperature $`\alpha`$ | $`10^{-2}`$ | Table B.2 |
| `s_arm`, `s_z` (잔차 스케일) | (원문 미명시) | 식 (8) |
| 온라인 RL 예산 | 과제별 20k / 30k / 40k / 25k steps | §B.3 |
| 분류기 인코더 / head | frozen SERL ResNet-10(뷰별) / Dense 256 + dropout 0.1 + LN + ReLU + Dense 1 | Table C.1 |
| 분류기 optimizer / 학습량 / 임계값 | Adam $`10^{-4}`$ / 250 epochs / 0.90 | Table C.1 |
| 시연 수 | Grasp & Place 50 · Open Drawer 20 · Pull Tissue 20 · Assemble Box 30 (9:1 분할) | §B.2 |

---

## 🎯 평가 메트릭

- **지표** — 과제당 성공률(20 evaluation episodes, 시작 pose 랜덤화) · **임계값** — 성공 판정 $`p_{\mathrm{cls}}(o)>0.90`$ (온라인 보상과 동일 규칙) · **비교 baseline** — Raw / PCA / VQ-VAE (DQ-RISE), 동일 시연·동일 파이프라인
- **보조 지표 1** — off-manifold 비율 $`\Delta\mathrm{NN}/\mathrm{Disp}`$ @ $`\mathrm{Disp}=0.2`$ (낮을수록 접촉-보존 탐사)
- **보조 지표 2** — 2차 차분 jitter $`J=\frac{1}{T-2}\sum_{t=1}^{T-2}\|a_{t+2}^{\mathrm{hand}}-2a_{t+1}^{\mathrm{hand}}+a_{t}^{\mathrm{hand}}\|_{2}`$ (과제별 Raw-IL 점수로 정규화)

---

## ✨ 변경 의도 (intent)

Raw 관절 회귀(고차원·jitter), PCA(고정 선형 좌표가 굽은 manifold 를 못 따라감), VQ 이산 코드북(코드 전환 시 명령 점프) 대비, LAMP 는 **히스토리 조건부·연속·디코딩 가능한 잠재 hand-action 공간을 IL 과 온라인 잔차 RL 이 공유**하게 만듭니다. IL 은 6-D 관절 목표 대신 2-D 오프셋만 회귀해 학습이 쉬워지고, RL 잔차는 동결 디코더를 통과하며 시연된 접촉-일관 모션의 이웃으로 구부러져 실환경 탐사가 접촉을 깨지 않습니다. 팔은 native 좌표를 유지하는 비대칭 설계로 과제 수준 변화의 표현력을 보존합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — Stage 2 BC 시각운동 정책(이미지 인코더 + MLP 헤드의 one-step 회귀)은 구조적으로 `act` / `diffusion` 계열보다 단순한 형태이며, LMPM 은 정책 앞단의 독립 VAE 모듈로 추가하는 매핑이 자연스럽습니다. 단 Stage 3 잔차 RLPD(온라인 SAC 루프·시연/온라인 이중 버퍼)는 오프라인 학습 중심 파이프라인 밖이라 매핑 불확실 — Stage 1–2 만의 부분 매핑이 현실적 후보입니다.

---

## 🚧 미해결 / 잠정

- BC 손실의 `lambda_h` , `lambda_z` 값이 본문·부록 어디에도 없음 — (원문에 명시 없음 — 가정으로 메움)
- 잔차 스케일 `s_arm` , `s_z` 값 미명시 — (원문에 명시 없음 — 가정으로 메움)
- 이미지 해상도·크롭 파라미터 미명시(환경 config 참조로만 언급)
- SAC 세부(target network 갱신률 $`\tau`$ , actor/critic LR)는 Table B.2 에 없음 — (원문에 명시 없음 — 가정으로 메움)
- 팔 명령의 파라미터화(절대 TCP pose vs delta)는 "6-D arm command"(§B.1)와 SpaceMouse TCP 병진·회전 명령(§4.1)으로만 기술 — 절대/상대 여부 원문 미확정
- 시연 데이터·수집 스크립트의 공개 여부 미명시 (코드 링크는 본문 명기, 접근성 미확인 — 분석 문서 ♻️ 참조)
