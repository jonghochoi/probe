# Audit Report — Dexterous Arm-Hand VLA via Shared Autonomy on `lerobot`

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
| 검증 생성일 | 2026-05-22 (`TZ=Asia/Seoul`) |
| 📚 문헌 대조 | `pass` |
| 🔍 패치 정합성 | `pass` |
| 🧪 시그니처·하이퍼파라미터 | `pass` |
| ⚖️ 종합 판정 | in-scope (π_uni enhancement) 정합 — 촉각/LSTM/corrective 는 base 밖 honest defer |
| 🔎 §🚧 분류 | `vendor-resolved` 2 / `paper-extractable` 0 / `paper-silent-defaultable` 1 / `paper-silent-experimental` 0 / `out-of-base-scope` 4 (다음 액션: inner step) |

---

## 📚 문헌 대조

| 분석 | 관계 | 인용 / 사유 |
|------|------|-------------|
| [`../2511.00139.md`](../2511.00139.md) | 일치 | §⚙️ 의사결정 함의: "본 논문 식 (12) 의 $`\mathcal{L}_{\text{total}}=\mathcal{L}_{\text{main}}+\lambda(\mathcal{L}_{\text{hand}}+\mathcal{L}_{\text{arm}})`$ 는 사지별 latent 를 강제 분리시키는 비용 낮은 보조 손실이다." — Design 의 enhancement + 사지별 보조 손실 매핑을 직접 뒷받침 |
| [`../2511.00139.md`](../2511.00139.md) | 일치 | §🔬 학습 셋업: "$`E_{\text{arm}}`$ · $`E_{\text{hand}}`$ 가 2-layer MLP (Mish), 보조 헤드는 single linear, 출력은 한 사지의 실제 DoF 인덱스에만 supervision 을 적용한다 (§7.3)." — patch 의 `nn.Sequential(Linear, Mish, Linear)` × 2 + single-linear aux head + selective slice 구현과 일치 |

판정: `pass`

<!-- 적어도 하나의 일치/확장 → pass. originating analysis 가 Design 의 핵심 주장(enhancement·보조손실·Mish MLP·selective supervision)을 verbatim 으로 뒷받침. -->

---

## 🔍 패치 정합성

```text
$ cd /home/user/probe && git apply --check analysis/2511.00139_impl/lerobot/impl.patch
(zero exit, 빈 출력)
```

판정: `pass` (zero exit)

---

## 🧪 시그니처·하이퍼파라미터 일치

| 항목 | 출처 | 패치 본문 | 일치 |
|------|------|-----------|------|
| `action_expert_config.width` 속성 사용 | `vendor/lerobot/policies/pi0/modeling_pi0.py:580` | `__init__` hunk `_w = action_expert_config.width` | ✅ |
| `config.max_action_dim` 속성 | `vendor/lerobot/policies/pi0/configuration_pi0.py:41` | aux/main head `nn.Linear(..., config.max_action_dim)` | ✅ |
| `nn.Mish` / `nn.Sequential` / `nn.Linear` | torch `nn` (모델 전반 사용) | enhancement 모듈 정의 | ✅ |
| `F.mse_loss(..., reduction="none")` 반환 계약 (B,chunk,dim) | `modeling_pi0.py:799` 원본 + 호출부 `:1294` | forward enhancement 분기 `losses + λ(arm_pad+hand_pad)` 동일 shape 유지 | ✅ |
| `F.pad` 슬라이스 zero-pad | torch `F` (functional) | `F.pad(arm_loss, (0, d-a))` / `F.pad(hand_loss, (a, d-a-h))` | ✅ |
| 상수 `enhancement_lambda = 1.0` | `2511.00139_design.md §📊` (λ, paper-silent default) | `configuration_pi0.py` hunk + `# NOTE` 주석 | ✅ |
| 상수 `enhancement_arm_dim = 6` / `enhancement_hand_dim = 12` | Design §🧮 데이터 계약 (arm 6-DoF / hand 12-DoF) | config hunk + forward slice `[..., :a]` / `[..., a:a+h]` | ✅ |
| `denoise_step` 추론 경로 정합 | `modeling_pi0.py:920–923` | denoise hunk가 동일 `_enhancement_main` 사용 | ✅ |

판정: `pass`

<!-- 모든 in-scope 행 ✅. out-of-base-scope 모듈 상수 (CAE filters [32,64,128],
     LSTM hidden 256, τ_contact) 는 §C 예외에 따라 본 verdict 에서 제외 —
     §🔎 out-of-base-scope 로 추적. -->

---

## 📐 식·표 일치

| 참조 | 출처 | 패치 hunk / 🚧 항목 | 상태 |
|------|------|---------------------|------|
| `Eq. (9)` 메인 flow matching | `analysis/2511.00139.md §🔬` | `impl.patch` forward hunk `v_t, z_arm, z_hand = self._enhancement_main(...)` | 구현 |
| `Eq. (10)` 손 보조 손실 | `analysis/2511.00139.md §🔬` | forward hunk `hand_loss = F.mse_loss(...)` | 구현 |
| `Eq. (11)` 팔 보조 손실 | `analysis/2511.00139.md §🔬` | forward hunk `arm_loss = F.mse_loss(...)` | 구현 |
| `Eq. (12)` 총손실 | `2511.00139_design.md §📊` | forward hunk `losses + λ(arm_pad+hand_pad)` | 구현 |
| `Eq. (2)` LSTM MSE+L2 | `analysis/2511.00139.md §🔬` | `impl.md §🚧 #5` | 유보 |
| `Eq. (3)` CAE 재구성 | `analysis/2511.00139.md §🔬` | `impl.md §🚧 #4` | 유보 |
| `Eq. (14)` 비축적 corrective | `2511.00139_design.md §📊` | `impl.md §🚧 #6` | 유보 |
| `Eq. (4)` / `Eq. (8)` 입력 계약 | `2511.00139_design.md §🧮` | `impl.md §🚧 #4` (촉각) / data layer | 유보 |
| `Table 1`–`Table 4` · `Fig. 16` | `analysis/2511.00139.md §📊` | 평가 결과 — 정적 검증 대상 아님 | 유보 |

<!-- silent-skip 없음 (모든 미구현 식은 §🚧 또는 평가 유보로 명시) → §🧪 partial 유발 없음. -->

---

## ⚖️ 종합 판정

- 📚 문헌 대조: `pass`
- 🔍 패치 정합성: `pass`
- 🧪 시그니처·하이퍼파라미터: `pass`

→ 이 foundry 의 구현은 in-scope 범위 (π_uni Arm-Hand Feature Enhancement, 식 9–12) 에서 Design 과 정합합니다. 촉각 인코더·LSTM admittance·비축적 corrective SFT 는 `pi0` base 좌표계 밖이라 honest defer (`out-of-base-scope`) 로 남습니다.

---

## 🔎 §🚧 분류

| §🚧 # | 항목 한 줄 | bucket | 근거 / 다음 액션 |
|-------|------------|--------|-------------------|
| 1 | 총손실 보조 가중치 λ 절대값 본문 미명시 | `paper-silent-defaultable` | analysis §🔬 "가중치 λ 의 절대값은 본문에 명시되어 있지 않다" — patch 가 default 1.0 + `# NOTE` 로 도입. 다음 라운드 feedback 이 §🚧→§🧪 이동 |
| 2 | 공유 latent 차원 d_s 절대값 미명시 | `vendor-resolved` | `vendor/lerobot/policies/pi0/modeling_pi0.py:580` — `action_expert_config.width` 가 d_s 를 강제 (vendor 기본). 다음 라운드가 §🧪 로 lift |
| 3 | action chunk size H 미명시 | `vendor-resolved` | `vendor/lerobot/policies/pi0/configuration_pi0.py:36` — `chunk_size: int = 50` 이 H 를 강제 |
| 4 | 촉각 인코더 (CAE+resultant-force MLP, §3.2.2) | `out-of-base-scope` | `impl.md §🧱` EXCLUDE 선언 + §🪛 신규-미구현 행 — `pi0` 에 촉각 모달리티 없음. outer/inner 모두 무의미 |
| 5 | LSTM admittance 정책 (§3.2.1) | `out-of-base-scope` | `impl.md §🧱` EXCLUDE — `pi0` 와 무관한 독립 정책 |
| 6 | 비축적 corrective SFT 루프 (식 14) | `out-of-base-scope` | `impl.md §🧱` EXCLUDE — 모델 forward 가 아닌 학습 오케스트레이션 레이어 |
| 7 | selective gating 임계값 τ_contact (§8.2.1) | `out-of-base-scope` | `impl.md §🧱` EXCLUDE — 촉각 모달리티 부재로 base 밖 |

<!-- ANALYSIS_BUCKETS:START -->
- vendor-resolved: 2,3
- paper-extractable:
- paper-silent-defaultable: 1
- paper-silent-experimental:
- out-of-base-scope: 4,5,6,7
- focus-hint:
<!-- ANALYSIS_BUCKETS:END -->

---

## 🚧 미해결 / 잠정

- `out-of-base-scope` 4개 항목 (촉각 인코더·LSTM·corrective·τ_contact) 은 `pi0` base 좌표계 밖이라 정적 검증으로 더 진행할 수 없습니다 — 별도 foundry 또는 신규 모듈 좌표계가 필요합니다.
- enhancement 의 수렴/성능 (88.7% 등) 검증은 실제 학습이 필요해 정적 audit 으로 결론 불가.
