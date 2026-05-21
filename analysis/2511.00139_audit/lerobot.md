# Audit Report — End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy: VR Teleoperation Augmented by Autonomous Hand VLA Policy for Efficient Data Collection on `lerobot`

> PROBE audit 모드 산출물. 한글 단일 문서이며, sibling Design + 한
> foundry 의 impl 가이드/패치를 원천 분석 문서 (`analysis/2511.00139.md`) 와
> foundry 코드에 대조한 정적 검증 결과입니다. 코드는 실행하지
> 않습니다 (`git apply --check` 만 허용). 형식·이모지·용어 규칙은
> `docs/STYLE.md` §7 / §4 를 정확히 따릅니다. 재실행 시 이
> 파일을 덮어씁니다.

---

## 📄 검증 메타

| 항목 | 내용 |
|------|------|
| 상위 Design | [`../2511.00139_design.md`](../2511.00139_design.md) |
| Originating analysis | [`../2511.00139.md`](../2511.00139.md) |
| Foundry | `lerobot` |
| 구현 가이드 | [`../2511.00139_impl/lerobot/impl.md`](../2511.00139_impl/lerobot/impl.md) · [`../2511.00139_impl/lerobot/impl.patch`](../2511.00139_impl/lerobot/impl.patch) |
| 검증 생성일 | 2026-05-21 (`TZ=Asia/Seoul`) |
| 📚 문헌 대조 | `pass` |
| 🔍 패치 정합성 | `pass` |
| 🧪 시그니처·하이퍼파라미터 | `pass` |
| ⚖️ 종합 판정 | 이 foundry 의 구현은 Design 과 정합합니다. |

---

## 📚 문헌 대조

본 Design 은 `analysis/2511.00139.md` 외에 별도 분석 문서를 cite 하지
않습니다 (§🎯 관련 Pillar / Decision · §✨ 핀 논문 대비 델타 가 거론
하는 항목은 PROBE 의 자체 P#/D# 결정 로그 및 핀 논문이며, 별도
`analysis/<id>.md` 파일이 존재하는 항목은 없습니다). 따라서 본
체크는 originating analysis 한 건에 대한 대조로 압축됩니다.

| 분석 | 관계 | 인용 / 사유 |
|------|------|-------------|
| [`../2511.00139.md`](../2511.00139.md) | 일치 | "**Arm-Hand Feature Enhancement 모듈** — $`\pi_0`$ 백본의 공유 표현 $`z_t^{\text{share}}`$ 를 별도 MLP $`E_{\text{arm}}`$ · $`E_{\text{hand}}`$ 로 사상해 사지별 잠재 $`z_t^{\text{arm}}`$ · $`z_t^{\text{hand}}`$ 를 만들고 보조 손실로 분리 학습한다." (§🧩 핵심 기여) — 라운드 1 patch 가 보조 손실 합성까지 포함하면서 본문 인용과 1:1 매핑이 됩니다. |
| [`../2511.00139.md`](../2511.00139.md) | 일치 | "$`\pi_0`$ 의 액션 전문가를 그대로 두고 그 위에 보조 MLP/헤드만 얹는 방식이다." (§🎯 P1/D7) — impl.md §🧱 의 `pi0` 베이스 선택 근거와 동일. |
| [`../2511.00139.md`](../2511.00139.md) | 확장 | "vision encoder 만 동결한 채 $`\pi_0`$ 의 나머지(PaliGemma 포함)를 full-parameter 미세조정한다." (§✨ 델타) — impl.md §🧪 가 `freeze_vision_encoder=True` 권고로 surface. patch 는 default 미변경 (학습 config 측 책임). |
| [`../2511.00139.md`](../2511.00139.md) | 확장 | 촉각 인코더 (CAE + resultant force vector) 가 §🧩·§🔑·§⚙️ 에 핵심 기여로 명시되었으나 impl.md §🚧 #1 로 명시적 유보. 본문과 충돌 없음. |

판정: `pass` (일치 2 + 확장 2, 충돌 0).

---

## 🔍 패치 정합성

```text
$ cd /home/user/probe && git apply --check analysis/2511.00139_impl/lerobot/impl.patch
(stdout/stderr 모두 비어 있음; exit code 0)
```

판정: `pass`

---

## 🧪 시그니처·하이퍼파라미터 일치

| 항목 | 출처 | 패치 본문 | 일치 |
|------|------|-----------|------|
| 클래스 `nn.Module` 상속 + `Tensor` 타입 힌트 | `vendor/lerobot/policies/pi0/modeling_pi0.py:27` (`from torch import Tensor, nn`) | `impl.patch` 새 `ArmHandFeatureEnhancement(nn.Module)`, `forward(z_share: Tensor)` | ✅ |
| `nn.Sequential(nn.Linear, nn.Mish, nn.Linear, nn.Mish)` 가용성 | torch 표준 (`nn.Mish` 존재) | `impl.patch` arm_mlp / hand_mlp 정의 | ✅ |
| `Tensor.index_add(-1, idx_t, src)` 시그니처 | torch 표준 (non-in-place 변종, 기능적으로 동일) | `impl.patch` forward 분기 `losses = losses.index_add(-1, arm_idx_t, lam * arm_sub)` | ✅ |
| `PI0Pytorch.__init__` 들여쓰기 / flow 일치 | `modeling_pi0.py:585-588` | `impl.patch` init wire (8-space indent 일치) | ✅ |
| `PI0Pytorch.forward` 반환 형상 `(B,T,D)` 불변 | `modeling_pi0.py:799` `F.mse_loss(u_t, v_t, reduction="none")` | `impl.patch` enhancement 분기 `losses` 도 동일 형상 (`index_add` 가 shape 보존), non-enhancement 경로는 기존 `F.mse_loss` 그대로 | ✅ |
| `PI0Pytorch.denoise_step` 반환 형상 불변 | `modeling_pi0.py:923` | `impl.patch` enhancement 분기 `action_out_proj(fused)` 반환 | ✅ |
| `field(default_factory=list)` import | `configuration_pi0.py:17` 기존 import | `impl.patch` `list[int] = field(default_factory=list)` | ✅ |
| 상수 `chunk_size = 50` (Design §📊 잠정) | `configuration_pi0.py:36` 기본값 `50` | patch 미변경 | ✅ |
| 상수 `λ = 1.0` (Design §📊·§🚧, Eq. 12) | `impl.patch` `enhancement_aux_loss_weight: float = 1.0` | `impl.patch` forward 분기에서 `lam * arm_sub`, `lam * hand_sub` 형태로 실제 사용 | ✅ |
| 상수 `train.steps = 80,000` (Design §📊) | `impl.md §🧪` "학습 config 외부 주입" | `configuration_pi0.py:100` `scheduler_decay_steps = 30_000` 기본값 미변경 | ⚠️ (Design 인용은 됐으나 학습 config 측 책임으로 위임됨이 impl.md 에 명시) |
| 상수 `CAE input (16,16,3) / filters [32,64,128] / latent 128` | impl.md §🚧 #1 명시적 유보 | patch 부재 | ⚠️ (유보 — silent-skip 아님) |
| 상수 `LSTM hidden_dim=256, input_dim=39` | impl.md §🚧 #3 명시적 유보 | patch 부재 | ⚠️ (유보) |
| import 경로 — 새 import 추가 없음 | `nn`, `Tensor`, `torch`, `F`, `field` 기존 import 만 사용 | (해당 없음) | ✅ |

판정: `pass`

근거: 시그니처 ❌ 0건, λ 가 forward 내부에서 실제 가중치로 사용되어
이전 라운드의 ⚠️ 가 ✅ 로 승격. 남은 ⚠️ 항목 (train.steps 외부 위임,
촉각 / LSTM 상수) 은 모두 impl.md §🚧 또는 §🧪 에 명시적 surface 된
유보이며 silent-skip 이 아닙니다. STYLE §7 정의상 `pass` — silent-skip
이 partial 의 트리거인데 본 라운드는 silent-skip 0 건.

---

## 📐 식·표 일치

| 참조 | 출처 | 패치 hunk / 🚧 항목 | 상태 |
|------|------|---------------------|------|
| `Eq. (2)` LSTM 사전학습 손실 | `analysis/2511.00139.md` §🔬, `2511.00139_design.md` §📊 | `impl.md §🚧 #3` | 유보 |
| `Eq. (3)` CAE 재구성 손실 | 동상 §📊 | `impl.md §🚧 #1` | 유보 |
| `Eq. (4)` $`o_t^{\text{hand}}`$ 데이터 계약 | `2511.00139_design.md` §🧮 | `impl.md §🚧 #1` (촉각 토큰 부재로 부분 유보) | 유보 |
| `Eq. (8)` $`o_t^{\text{uni}}`$ 데이터 계약 | `2511.00139_design.md` §🧮 | patch 미변경 — vendor 의 다중 카메라 + state 토큰 흐름이 이미 일반 구조라 호환 | 구현 |
| `Eq. (9)` conditional flow matching main loss | `2511.00139_design.md` §📊 | `modeling_pi0.py:750-799` 의 main loss `F.mse_loss(u_t, v_t)` — patch enhancement 분기도 동일 식 유지 | 구현 |
| `Eq. (10)` $`\mathcal{H}_{\text{arm}}(z_t^{\text{arm}})`$ aux head + 손실 | `2511.00139_design.md` §📊 | `impl.patch` aux_arm Linear + `(aux_arm.index_select - u_t.index_select)**2` MSE 합산 | 구현 |
| `Eq. (11)` $`\mathcal{H}_{\text{hand}}(z_t^{\text{hand}})`$ aux head + 손실 | 동상 | `impl.patch` aux_hand 동일 처리 | 구현 |
| `Eq. (12)` $`\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{main}} + \lambda(\mathcal{L}_{\text{hand}} + \mathcal{L}_{\text{arm}})`$ | 동상 | `impl.patch` `losses = losses.index_add(-1, idx_t, lam * sub)` 두 번 호출로 main + λ·aux 합성 | 구현 |
| `Eq. (14)` 비축적 corrective SFT | 동상 §📊 | `impl.md §🚧 #2` | 유보 |
| `Table 1` (uni vs uni-origin pick-and-place) | `analysis/2511.00139.md` §🔬·§📊 | 평가 코드 영역 — 정적 감사 범위 밖 | 유보 |
| `Table 2` (시각 차폐 robustness 21→70→90%) | 동상 | 동상 | 유보 |
| `Table 3` (Enhancement ablation 88→95, 71→81, 19→58 %p) | 동상 | enhancement 모듈 + 보조 손실 모두 `impl.patch` 에 구현, 정량 재현은 학습 후 평가 | 부분 구현 |
| `Table 4` (Shared Autonomy 110 vs Full Teleop 90 traj/h) | 동상 §🔬 | 데이터 수집 파이프라인 영역 — `impl.md §🚧 #3` 와 연결 | 유보 |
| `Fig. 16` corrective 단계별 grid 벤치 | 동상 §⚙️ | `impl.md §🚧 #2` 의 corrective 루프와 연결 | 유보 |

silent-skip (인용은 됐으나 patch hunk 도 없고 🚧 도 없음): 없음.
모든 미구현 항목은 `impl.md §🚧 #1-#4` 로 명시적 surface 됨.

---

## ⚖️ 종합 판정

- 📚 문헌 대조: `pass`
- 🔍 패치 정합성: `pass`
- 🧪 시그니처·하이퍼파라미터: `pass`

→ 이 foundry 의 구현은 Design 과 정합합니다. Arm-Hand Feature
Enhancement 의 구조적 골격 (per-limb MLP × 2, aux head × 2,
fused-concat → action_out_proj) 과 Eq. (10)-(12) 의 보조 손실 합성
(λ 가중 selective-DoF MSE 의 `index_add` 누적) 이 모두 `pi0`
좌표계에 정착했고, `git apply --check` 가 통과합니다. 남은 항목
(촉각 인코더, 비축적 corrective SFT 루프, LSTM admittance 정책,
학습/평가 정량 재현) 은 모두 impl.md §🚧 로 명시적 유보이며 본
정적 감사의 범위 밖입니다.

---

## 🚧 미해결 / 잠정

- Table 1–4 / Fig. 16 의 정량 재현은 학습·평가 코드 실행이 필요하므로
  정적 감사 범위 밖입니다. honest partial 입니다.
- 촉각 인코더 / corrective SFT / LSTM admittance / 잠정 hyperparam 은
  모두 impl.md §🚧 에 surface 되어 있어 정적 감사에서는 결론 내릴 수
  없습니다 — 후속 외부 루프 (`/analyze-paper --focus`) 가 본문 정보를
  추가로 추출해야 진행 가능.
