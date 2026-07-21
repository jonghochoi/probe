# Design — UniDexTok: A Unified Dexterous Hand Tokenizer from Real Data

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | UniDexTok: A Unified Dexterous Hand Tokenizer from Real Data |
| 링크 | [arXiv:2606.10683](https://arxiv.org/abs/2606.10683) |
| 분석 문서 | [`analysis/2606.10683/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-21 |

---

## 🧮 데이터 계약

시간축은 단일 프레임(상태) 단위입니다 — 본 토크나이저는 sequence/action chunk 가 아니라 한 프레임의 손 관절 상태를 재구성합니다.

- **입력 (상태)** — `x`: shape `(B, 22)`, dtype float, radian 단위 관절 각도. 정규화 $`\tilde{x} = x / \pi`$ (고정 스케일 $`\pi`$, 데이터셋 통계 미사용). 22-D 는 UDHM active-joint 좌표(index/middle/ring 각 4-DoF, pinky 5-DoF, thumb 5-DoF).
- **입력 (조건)** — `h`: 이산 hand-type / 데이터-소스 라벨. 임베딩 `c_h`(= `h_embed`)로 사상되어 AdaLN scale·shift 를 변조.
- **표준화 전처리** — 이질적 소스 관절값을 radian 으로 변환 후 각 가용 자유도를 의미 대응 UDHM 좌표에 삽입(semantic insertion), 결측 좌표는 zero-pad. 0–255 bin 인코딩(LET-Dex / LinkerHand-Open-World) 로그는 먼저 radian 관절 각도로 변환.
- **중간 (latent)** — encoder 출력 `z_0`: shape `(B, N, C)` = `(B, 8, 512)`. VQ 투영은 $`512 \to 256`$, `K=8` 채널 그룹.
- **출력 (재구성 상태)** — `x̂`: shape `(B, 22)`, 역정규화( $`\times \pi`$ ) 후 radian 관절 각도.

---

## 🧰 모듈 인터페이스

```python
def udhm_standardize(joints_raw, source_spec) -> tuple:  # -> (x: (22,), h: int)
    """소스별 관절 로그를 UDHM 22-D active-joint 좌표 + hand-type 라벨로 표준화.
       radian 변환 → semantic insertion → zero-pad. 0-255 bin 은 먼저 radian 화."""

def udhm_forward_kinematics(dof22, bone_lengths, palm_offsets) -> keypoints:  # -> (21, 3)
    """22-DoF 벡터 → MANO-format 21-joint keypoint. 손목 고정 후 Rodrigues 축-각
       회전으로 MCP/PIP/DIP/fingertip 순차 계산."""

def udhm_inverse(keypoints) -> dof22:  # p_w = J_0; 이후 비선형 최소제곱으로 관절각 정련
    """MANO keypoint → 22-DoF. 손목은 입력에서 직접 취하고(식 1), FK 재구성이
       타깃 관절과 일치하도록 nonlinear least-squares 로 각도 정련."""

class UniDexTok:
    def encode(self, x_norm, h_embed) -> z:      # (B,22),(B,) -> (B, N=8, C=512)
        """정규화 상태를 N 개 latent 토큰으로 투영(식 3) 후 AdaLN 조건 transformer 블록."""
    def quantize(self, u) -> (q, indices):       # factorized VQ, K=8 × 32-entry
        """512→256 투영을 K=8 그룹으로 나눠 그룹별 코사인 최근접 코드 선택(식 6),
           선택 서브코드 concat. straight-through estimator."""
    def decode(self, q, h_embed) -> x_hat:       # -> (B, 22), 역정규화 포함
        """인코더 대칭. 양자화 토큰 되투영 + positional embedding + 조건 블록 →
           flatten head → x̂ (× π 역정규화)."""
```

- **인코더 `E`** — 입력 상태·hand-type 조건 → latent 토큰. DiT-style self-attention + MLP + zero-init residual gate + AdaLN.
- **양자화기 `Q`** — factorized VQ; 손실 항 `L_vq` 와 straight-through estimator 로 인코더/디코더와 결합.
- **디코더 `D`** — 양자화 토큰·hand-type 조건 → 재구성 상태. 인코더 대칭.
- **AdaLN** — `c_h` 로 $`\gamma, \beta`$ 생성해 LayerNorm 변조(식 4). encoder·decoder 양쪽에서 hand-specific 규약 흡수.

---

## ⛓️ 불변식·가정

- (가정 1) — active 좌표 수는 정확히 22 (index/middle/ring 4-DoF, pinky 5-DoF, thumb 5-DoF 합). 이 배분이 손 하드웨어와 다르면 semantic insertion 이 의미 정렬을 잃음.
- (가정 2) — 손바닥은 강체이며 thumb CMC·4개 비-thumb MCP 관절은 손목 대비 고정 offset. index·middle·ring 의 MCP–PIP–DIP–tip chain 은 손바닥에 수직인 국소 운동 평면에 놓임(공면/수직 제약).
- (가정 3) — 정규화는 고정 스케일 $`\pi`$ (데이터셋 평균/표준편차 미사용). 이로써 토큰이 특정 split 에 종속되지 않고 역정규화 후 MPJAE 가 직접 해석 가능.
- (가정 4) — 모든 관절값은 radian 표현. 서로 다른 소스의 단위(degree, 0–255 bin)는 표준화 단계에서 radian 으로 통일.
- (가정 5) — 인간 손형(anthropomorphic) 기구학 구조 전제. 비-anthropomorphic 그리퍼·soft hand·강한 mechanical coupling·underactuated 관절은 포맷 호환만 되고 tendon coupling·joint limit·compliance·actuator dynamics 는 미모델링.

---

## 📊 하이퍼파라미터·손실

**재구성 손실** — 본문은 MSE + SmoothL1 auxiliary term 결합을 서술하나, 식 (5)에는 MSE 항만 명시(SmoothL1 가중치는 `(원문에 명시 없음 — 가정으로 메움)`):

$$\mathcal{L}_{rec}=\mathrm{MSE}(\tilde{x},\hat{\tilde{x}})$$

**VQ commitment 손실** (식 7):

$$\mathcal{L}_{vq}=\beta\|\mathrm{sg}[q]-u\|_{2}^{2}+\|q-\mathrm{sg}[u]\|_{2}^{2}$$

**총 손실** (식 8):

$$\mathcal{L}=\mathcal{L}_{rec}+\mathcal{L}_{vq}$$

| 이름 | 값 | 출처 |
|------|----|----|
| `D` (상태 차원) | `22` | §3.2 |
| `N` (latent 토큰 수) | `8` | §3.2, Eq. (3) |
| `C` (채널 폭) | `512` | §3.2 |
| VQ 투영 차원 | $`512 \to 256`$ | §3.3 |
| `K` (채널 그룹 수) | `8` | §3.3 |
| 서브 코드북 크기 | `32` (그룹당) | §3.3 |
| 표현 조합 수 | `32^8` (코드 벡터 `32×8=256`) | §3.3 |
| $`\beta`$ (commitment) | `0.25` | §3.3, Eq. (7) |
| entropy regularization | 비활성화 (구현은 지원) | §3.3 |
| 정규화 스케일 | $`\pi`$ (고정) | §3.1 |
| checkpoint 선택 기준 | raw 관절 각도 MAE(deg), $`\times \pi`$ 후 | §3.3 |
| few-shot 적응 | `4,528` frames (6.2%) · `2` epochs | §4.3 |
| 데이터 분할 | train/test `80% / 20%` | §4.1 |
| optimizer / lr / batch / 하드웨어 | `(원문에 명시 없음 — 가정으로 메움)` | — |

---

## 🎯 평가 메트릭

- **지표** — `MPJAE` (Mean Per-Joint Angle Error, deg) · `MPJPE` (Mean Per-Joint Position Error, mm) · `FK Error` (fingertip 위치 오차, mm).
- **표현 품질** — 13-class 제스처(130 샘플) linear probing accuracy · KNN Top1/Top3 recall (embedding·quantized 각각).
- **임계값** — 명시적 pass 임계값 없음; baseline 대비 상대 개선으로 평가. 주 결과: MPJAE 15.63° → 0.16°, MPJPE 18.51 mm → 0.18 mm (우리 데이터셋).
- **비교 baseline** — `UniHM` (최신 cross-hand 토크나이저). 두 프로토콜: (1) DexYCB-derived retargeted test state, (2) 표준화 데이터셋 20% held-out.
- **전이 평가** — 미학습 Inspire hand RH56E2(6 active joints)로 zero-shot / few-shot MPJAE·FK error.

---

## ✨ 변경 의도 (intent)

기존 UniHM·UniDex 는 로봇 손마다 별도 hand-specific 토크나이저를 학습해 고립된 latent 공간을 만들고, 새 손이 오면 처음부터 재학습해야 했습니다. UniDexTok 의 변경 의도는 세 가지입니다 — (1) 인코더·코드북·디코더를 **모든 embodiment 가 공유**해 공통 이산 상태 공간을 만들고 미학습 손을 재학습 없이 투영(zero-shot)·소량 적응(few-shot)하게 함, (2) MANO→로봇 **retargeting 이나 시뮬레이션을 거치지 않고** 표준화된 실제 손 상태에서 직접 학습해 기하학적 mismatch·sim2real gap 을 제거함, (3) 단일 코드북의 이산 표현 정보 붕괴를 **factorized codebook**(K=8 그룹 × 32-entry)으로 회피함. 인간 손을 retargeting source 가 아니라 유효한 학습 embodiment 로 편입하는 것도 핵심 차별점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 본 기여는 정책(policy)이 아니라 손 관절 상태의 **표현/전처리·토큰화 모듈**이므로, `pi0`/`act`/`diffusion` 등 정책 family 에 직접 대응하지 않습니다. 매핑 가능성이 있는 지점은 (a) 데이터 표준화·정규화 계층(processor / transforms — UDHM standardize + $`/\pi`$ 정규화), (b) 별도의 상태 VQ 토크나이저 모듈(action tokenizer 와 유사하나 action 이 아닌 state 대상). 어느 정책 base 의 일부라기보다 그 앞단 관측/상태 파이프라인에 얹히는 형태이며, 확정 매핑은 `/implement-design` 판단.

---

## 🚧 미해결 / 잠정

- 재구성 손실의 SmoothL1 auxiliary term — 본문 서술과 식 (5) 불일치로 가중치·형태 미상. 재현 시 MSE-only 인지 MSE+SmoothL1 인지 먼저 확정 필요.
- optimizer · learning rate · batch size · 학습 하드웨어 · epoch 수(few-shot 외) — 원문 미명시.
- hand-type 임베딩 `c_h` 의 차원·초기화, AdaLN MLP 구조 — 미명시.
- transformer 블록 수·attention head 수 — 미명시(DiT-style 이라고만 서술).
- 데이터 정확한 80/20 split·프레임 수(Inspire 전체 크기는 4,528=6.2% 로 역산 가능 ≈ 73k) — split 재현 정보 부분 미공개.
