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
| 🧪 시그니처·하이퍼파라미터 | `partial` |
| ⚖️ 종합 판정 | 이 foundry 의 구현은 부분적으로 정합합니다 — 보조 손실 (Eq. 12) 의 λ·aux 헤드 출력이 patch 에 추가되었으나 loss 텐서로 합성되지 않아 §🚧 #1 로 유보됨. |

---

## 📚 문헌 대조

본 Design 은 `analysis/2511.00139.md` 외에 별도 분석 문서를 cite 하지
않습니다 (§🎯 관련 Pillar / Decision · §✨ 핀 논문 대비 델타 가 거론
하는 항목은 PROBE 의 자체 P#/D# 결정 로그 및 핀 논문이며, 별도
`analysis/<id>.md` 파일이 존재하는 항목은 없습니다). 따라서 본
체크는 originating analysis 한 건에 대한 대조로 압축됩니다.

| 분석 | 관계 | 인용 / 사유 |
|------|------|-------------|
| [`../2511.00139.md`](../2511.00139.md) | 일치 | "**Arm-Hand Feature Enhancement 모듈** — $`\pi_0`$ 백본의 공유 표현 $`z_t^{\text{share}}`$ 를 별도 MLP $`E_{\text{arm}}`$ · $`E_{\text{hand}}`$ 로 사상해 사지별 잠재 $`z_t^{\text{arm}}`$ · $`z_t^{\text{hand}}`$ 를 만들고 보조 손실로 분리 학습한다. 메인 헤드는 $`[z_t^{\text{share}},z_t^{\text{arm}},z_t^{\text{hand}}]`$ 융합 표현에서 통합 액션을 예측한다." (§🧩 핵심 기여) — Design §🧰 / §📊 / impl.md §🪛 #2-#5 와 동일 구조. |
| [`../2511.00139.md`](../2511.00139.md) | 일치 | "$`\pi_0`$ 의 액션 전문가를 그대로 두고 그 위에 보조 MLP/헤드만 얹는 방식이다." (§🎯 P1/D7) — impl.md §🧱 가 `pi0` 베이스 선택의 근거로 인용한 흐름과 정확히 일치. |
| [`../2511.00139.md`](../2511.00139.md) | 확장 | "vision encoder 만 동결한 채 $`\pi_0`$ 의 나머지(PaliGemma 포함)를 full-parameter 미세조정한다." (§✨ 델타) — impl.md §🧪 가 `freeze_vision_encoder=True` + `train_expert_only=False` 조합을 명시적으로 권고하는 형태로 확장. patch 는 default 값을 변경하지 않음 (학습 config 측에서 켜는 형태). |
| [`../2511.00139.md`](../2511.00139.md) | 확장 | 촉각 인코더 (CAE + resultant force vector) 가 §🧩·§🔑·§⚙️ 에 핵심 기여로 명시되었으나, impl 은 §🚧 #2 로 명시적 유보. patch 범위 밖이라는 사실을 honesty 원칙으로 surface 한 케이스 — 본문과 충돌하지 않음. |

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
| 클래스 `nn.Module` 상속 + `Tensor` 타입 힌트 | `vendor/lerobot/policies/pi0/modeling_pi0.py:27` (`from torch import Tensor, nn`) | `impl.patch @555-573` 새 `ArmHandFeatureEnhancement(nn.Module)`, `forward(z_share: Tensor)` | ✅ |
| `nn.Sequential(nn.Linear, nn.Mish, nn.Linear, nn.Mish)` 가용성 | torch ≥ 1.9 표준 (`nn.Mish` 존재), foundry import 변경 불필요 | `impl.patch @564-572` | ✅ |
| `PI0Pytorch.__init__` 끝 부분 동일 들여쓰기 & flow | `vendor/lerobot/policies/pi0/modeling_pi0.py:585-588` | `impl.patch @634-641` (init wire) — 들여쓰기 8 spaces 일치 | ✅ |
| `PI0Pytorch.forward` 반환 형상 `(B,T,D)` 불변 | `modeling_pi0.py:799` `F.mse_loss(u_t, v_t, reduction="none")` | `impl.patch @845-859` enhancement 분기도 동일 `F.mse_loss(...)` 로 회귀 | ✅ |
| `PI0Pytorch.denoise_step` 반환 형상 `(B,T,D)` 불변 | `modeling_pi0.py:923` `return self.action_out_proj(suffix_out)` | `impl.patch @981-986` enhancement 분기도 동일 형태로 회귀 | ✅ |
| `field(default_factory=list)` import 가용성 | `configuration_pi0.py:17` `from dataclasses import dataclass, field` | `impl.patch @96-97` `list[int] = field(default_factory=list)` | ✅ |
| 상수 `chunk_size = 50` (Design §📊 잠정) | `configuration_pi0.py:36` 기본값 `50` 이미 존재 | patch 변경 없음 — 기본값 그대로 사용 | ✅ |
| 상수 `train.steps = 80,000` (Design §📊) | impl.md §🧪 "학습 config 외부 주입" 으로 처리 | `configuration_pi0.py:100` `scheduler_decay_steps = 30_000` 기본값 미변경 | ⚠️ (Design 인용은 됐으나 patch 변경 없음 — 학습 config 측 책임으로 위임됨이 impl.md 에 명시) |
| 상수 `λ = 1.0` (Design §📊·§🚧, Eq. 12) | impl.patch `enhancement_aux_loss_weight: float = 1.0` 으로 추가 | `impl.patch @98` | ⚠️ (필드는 추가됐으나 `forward()` 내부에서 실제 가중치로 곱해지지 않음 — §🚧 #1) |
| 상수 `CAE input (16,16,3) / filters [32,64,128] / latent 128` (Design §📊) | 촉각 인코더 미구현 — impl.md §🚧 #2 명시적 유보 | patch 본문 부재 | ⚠️ (유보로 surface 됨, silent-skip 아님) |
| 상수 `LSTM hidden_dim=256, input_dim=39` (Design §📊) | impl.md §🚧 #4 명시적 유보 | patch 본문 부재 | ⚠️ (유보) |
| import 경로 — patch 가 새 import 추가 안 함 | (해당 없음) | `nn`, `Tensor`, `torch`, `F`, `field` 전부 기존 import | ✅ |

판정: `partial`

근거: 시그니처 ❌ 0건 (런타임 오류 유발 없음). λ 가 config 필드로
추가됐지만 forward 내부 loss 합성에 미사용 (⚠️) 인 점이 가장 결정적.
다른 ⚠️ 항목들은 impl.md §🚧 에 명시적 유보로 surface 되었으므로
silent-skip 이 아닙니다.

---

## 📐 식·표 일치

| 참조 | 출처 | 패치 hunk / 🚧 항목 | 상태 |
|------|------|---------------------|------|
| `Eq. (2)` LSTM 사전학습 손실 | `analysis/2511.00139.md` §🔬, `2511.00139_design.md` §📊 | `impl.md §🚧 #4` | 유보 |
| `Eq. (3)` CAE 재구성 손실 | 동상 §📊 | `impl.md §🚧 #2` | 유보 |
| `Eq. (4)` $`o_t^{\text{hand}}`$ 데이터 계약 | `2511.00139_design.md` §🧮 | `impl.md §🚧 #2` (촉각 토큰 부재로 부분 유보) | 유보 |
| `Eq. (8)` $`o_t^{\text{uni}}`$ 데이터 계약 | `2511.00139_design.md` §🧮 | patch 미변경 — vendor 의 다중 카메라 + state 토큰 흐름이 이미 일반 구조라 호환 (촉각 미사용 통합 계약은 그대로 적용됨) | 구현 |
| `Eq. (9)` conditional flow matching main loss | `2511.00139_design.md` §📊 | `modeling_pi0.py:750-799` 의 기존 main loss = `F.mse_loss(u_t, v_t)` — patch 가 enhancement 분기에서도 동일 식 유지 (`impl.patch @851-855`) | 구현 |
| `Eq. (10)` $`\mathcal{H}_{\text{arm}}(z_t^{\text{arm}})`$ aux head | `2511.00139_design.md` §📊 | `impl.patch @573` (`self.aux_arm = nn.Linear(half, max_action_dim)`) — 모듈은 추가됐으나 loss 합성 미연결 | 유보 (§🚧 #1) |
| `Eq. (11)` $`\mathcal{H}_{\text{hand}}(z_t^{\text{hand}})`$ aux head | 동상 | `impl.patch @574` (`self.aux_hand = ...`) — 동일 사유 | 유보 (§🚧 #1) |
| `Eq. (12)` $`\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{main}} + \lambda(\mathcal{L}_{\text{hand}} + \mathcal{L}_{\text{arm}})`$ | 동상 | λ 필드 추가됨 (`impl.patch @98`), 합성식은 `impl.md §🚧 #1` | 유보 |
| `Eq. (14)` 비축적 corrective SFT | 동상 §📊 | `impl.md §🚧 #3` | 유보 |
| `Table 1` (uni vs uni-origin pick-and-place) | `analysis/2511.00139.md` §🔬·§📊 | 평가 코드 영역 — 본 audit 범위 밖 (`docs/STYLE.md` §7 정적 감사) | 유보 |
| `Table 2` (시각 차폐 robustness 21→70→90%) | 동상 | 동상 | 유보 |
| `Table 3` (Enhancement ablation 88→95, 71→81, 19→58 %p) | 동상 | enhancement 모듈 자체는 `impl.patch` 에 구현, 정량 재현은 학습 후 평가 | 부분 구현 |
| `Table 4` (Shared Autonomy 110 vs Full Teleop 90 traj/h) | 동상 §🔬 | 데이터 수집 파이프라인 영역 — `impl.md §🚧 #4` 와 연결 | 유보 |
| `Fig. 16` corrective 단계별 grid 벤치 | 동상 §⚙️ | `impl.md §🚧 #3` 의 corrective 루프와 연결 | 유보 |

silent-skip (인용은 됐으나 patch hunk 도 없고 🚧 도 없음): 없음.
모든 미구현 항목은 `impl.md §🚧 #1-#5` 로 명시적 surface 됨.

---

## ⚖️ 종합 판정

- 📚 문헌 대조: `pass`
- 🔍 패치 정합성: `pass`
- 🧪 시그니처·하이퍼파라미터: `partial`

→ 이 foundry 의 구현은 부분적으로 정합합니다 — Arm-Hand Feature
Enhancement 의 구조적 골격 (per-limb MLP × 2, aux head × 2,
fused-concat → action_out_proj) 은 `pi0` 좌표계에 정확히 정착했고
`git apply --check` 가 통과합니다. 다만 Eq. (12) 의 보조 손실 합성
(`L_main + λ(L_hand + L_arm)`) 이 patch 내부에서 실행되지 않고
`_aux_arm` / `_aux_hand` 가 underscore 변수로 받혀 있어 §🚧 #1 로
명시적 유보 상태입니다. 다음 라운드의 자연스러운 작업은 이 항목을
patch 로 승격하는 것입니다.

---

## 🚧 미해결 / 잠정

- §🧪 의 ⚠️ 항목 중 λ 미사용 (`enhancement_aux_loss_weight` 가 dataclass
  필드로만 존재) 은 정적 감사에서는 partial 로 분류되지만, 실제 학습이
  돌면 backward pass 가 main loss 만 보게 됩니다 — 다음 라운드 우선
  과제.
- 촉각 인코더 / corrective SFT / LSTM admittance / 잠정 hyperparam
  은 모두 impl.md §🚧 에 surface 되어 있어 정적 검증 범위에서 결론
  내릴 수 없습니다 — Design 본문이 본문 미명시 상태에서는 외부 루프
  (`/analyze-paper --focus`) 가 호출되어야 진행 가능.
- Table 1–4 / Fig. 16 의 정량 재현은 학습·평가 코드 실행이 필요하므로
  정적 감사 범위 밖입니다. honest partial 입니다.
