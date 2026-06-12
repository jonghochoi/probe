# Validation Report — Dexterous Arm-Hand VLA via Shared Autonomy on `lerobot`

> PROBE validation 모드 산출물. 한글 단일 문서이며, sibling Design + 한
> foundry 의 impl 가이드/패치를 원천 분석 문서 (`analysis/2511.00139/analysis.md`) 와
> foundry 코드에 대조한 검증 결과입니다. 정적 체크(📚/🔍/🧪/📐) 위에
> 설치된 foundry 에서 sibling smoke test 를 실행하는 §🧬 실행 검증을
> 더합니다 (학습/추론은 돌리지 않음). 형식·이모지·용어 규칙은
> `docs/STYLE.md` §7 / §4 를 정확히 따릅니다. 재실행 시 이
> 파일을 덮어씁니다.
>
> 본 라운드는 **vendor 스냅샷 refresh (pinned commit `999e77ad` →
> `3410b40275f31d6fa66345c99cf076d36991a313`, 2026-06-12) 직후의 재검증**
> 입니다 — `vendor/lerobot/README.md` Refresh 절차 step 5.

---

## 📄 검증 메타

| 항목 | 내용 |
|------|------|
| 상위 Design | [`../design.md`](../design.md) |
| Originating analysis | [`../analysis.md`](../analysis.md) |
| Foundry | `lerobot` (pinned commit `3410b40275f31d6fa66345c99cf076d36991a313`) |
| 구현 가이드 | [`../impl/lerobot/impl.md`](../impl/lerobot/impl.md) · [`../impl/lerobot/impl.patch`](../impl/lerobot/impl.patch) · [`../impl/lerobot/test_pi0_enhance_smoke.py`](../impl/lerobot/test_pi0_enhance_smoke.py) |
| 검증 생성일 | 2026-06-12 (`TZ=Asia/Seoul`) |
| 📚 문헌 대조 | `pass` |
| 🔍 패치 정합성 | `pass` |
| 🧪 시그니처·하이퍼파라미터 | `pass` |
| 🧬 실행 검증 | `pass` |
| ⚖️ 종합 판정 | vendor refresh (`3410b40`) 후에도 in-scope (π_uni enhancement) 정합 + 실행 검증 통과 — 촉각/LSTM/corrective 는 base 밖 honest defer |
| 🔎 §🚧 분류 | `vendor-resolved` 0 / `paper-extractable` 0 / `paper-silent-defaultable` 0 / `paper-silent-experimental` 0 / `out-of-base-scope` 4 (다음 액션: honest defer — 추가 라운드 무의미) |

---

## 📚 문헌 대조

| 분석 | 관계 | 인용 / 사유 |
|------|------|-------------|
| [`../analysis.md`](../analysis.md) | 일치 | §⚙️ 의사결정 함의: "본 논문 식 (12) 의 $`\mathcal{L}_{\text{total}}=\mathcal{L}_{\text{main}}+\lambda(\mathcal{L}_{\text{hand}}+\mathcal{L}_{\text{arm}})`$ 는 사지별 latent 를 강제 분리시키는 비용 낮은 보조 손실이다." — Design 의 enhancement + 사지별 보조 손실 매핑을 직접 뒷받침 |
| [`../analysis.md`](../analysis.md) | 일치 | §🔬 학습 셋업: "$`E_{\text{arm}}`$ · $`E_{\text{hand}}`$ 가 2-layer MLP (Mish), 보조 헤드는 single linear, 출력은 한 사지의 실제 DoF 인덱스에만 supervision 을 적용한다 (§7.3)." — patch 의 `nn.Sequential(Linear, Mish, Linear)` × 2 + single-linear aux head + selective slice 구현과 일치 |

판정: `pass`

<!-- 적어도 하나의 일치/확장 → pass. originating analysis 가 Design 의 핵심 주장(enhancement·보조손실·Mish MLP·selective supervision)을 verbatim 으로 뒷받침. -->

---

## 🔍 패치 정합성

vendor 스냅샷이 `3410b40` 으로 wholesale refresh 된 직후의 재실행입니다.
refresh 가 가져온 `modeling_pi0.py` 상류 변경 (torch.compile 안정화,
upstream PR #3610) 은 seam 대상 `forward` 본문과 겹치지 않아 패치가
그대로 적용됩니다.

```text
$ cd /home/user/probe && git apply --check analysis/2511.00139/impl/lerobot/impl.patch
(zero exit, 빈 출력)
```

판정: `pass` (zero exit)

---

## 🧪 시그니처·하이퍼파라미터 일치

refresh 된 스냅샷 기준으로 `file:line` 앵커를 재확인했습니다 (`forward`
:750 → :762, model 생성 :968 → :960, `get_gemma_config` :315 → :323 으로
이동했으나 시그니처·본문 의미는 불변).

| 항목 | 출처 | 패치 본문 | 일치 |
|------|------|-----------|------|
| seam `PI0Pytorch._compute_suffix_out(...) -> (suffix_out, u_t)` | `vendor/lerobot/policies/pi0/modeling_pi0.py:762` (원 `forward`) | extract-method hunk — 본문 의미 불변, 반환만 추가 | ✅ |
| seam `PI0Policy._build_model(config) -> PI0Pytorch` | `modeling_pi0.py:960` (`self.model = PI0Pytorch(...)`) | factory hunk — 호출부를 `self._build_model(config)` 로 우회 | ✅ |
| `get_gemma_config(variant).width` 사용 | `vendor/lerobot/policies/pi0/modeling_pi0.py:323` | `PI0EnhancePytorch.__init__` `d_s = get_gemma_config(...).width` | ✅ |
| `config.max_action_dim` 속성 | `vendor/lerobot/policies/pi0/configuration_pi0.py:41` | `H_arm/H_hand/H_main = nn.Linear(..., config.max_action_dim)` | ✅ |
| `nn.Mish` / `nn.Sequential` / `nn.Linear` (E_arm/E_hand 2-layer Mish) | torch `nn` | `ArmHandFeatureEnhancer` 정의 | ✅ |
| 반환 계약 `(B,chunk,max_action_dim)` 유지 | `modeling_pi0.py` 원 `forward` + 호출부 `:1306` (`losses[:, :, :original_action_dim]`) | `compute_feature_enhancement_loss` 가 `(B,T,A)` 반환 — base 와 동일 shape | ✅ |
| `register_subclass("pi0_enhance")` + config_class/name 배선 | `vendor/lerobot/configs/policies.py:41` (`PreTrainedConfig` registry) | `PI0EnhanceConfig`/`PI0EnhancePolicy` (factory generic resolver) | ✅ |
| import `lerobot.utils.constants.ACTION` | `vendor/lerobot/utils/constants.py:33` | `modeling_pi0_enhance.py` import | ✅ |
| 상수 `aux_loss_weight = 1.0` | `design.md §📊` (λ, paper-silent default) | `configuration_pi0_enhance.py` + `# NOTE` 주석 | ✅ |
| 상수 `arm_dim = 6` (hand 12 → original_action_dim 18) | Design §🧮 데이터 계약 (arm 6-DoF / hand 12-DoF) | config 필드 + `build_index_masks(arm_dim, original_action_dim, A)` | ✅ |
| 상수 $`d_s`$ = `get_gemma_config(...).width` (vendor-resolved) | `vendor/lerobot/policies/pi0/modeling_pi0.py:323` | `__init__` `d_s` | ✅ |
| 상수 $`H`$ = `chunk_size = 50` (vendor-resolved) | `vendor/lerobot/policies/pi0/configuration_pi0.py:36` | base `_compute_suffix_out` 의 `self.config.chunk_size` 상속 | ✅ |

판정: `pass`

<!-- 모든 in-scope 행 ✅. seam 2개는 동작-보존 (반환 추가 / 호출 우회만).
     out-of-base-scope 모듈 상수 (CAE filters [32,64,128], LSTM hidden 256,
     τ_contact) 는 §C 예외에 따라 본 verdict 에서 제외 — §🔎 추적. -->

---

## 📐 식·표 일치

| 참조 | 출처 | 패치 hunk / 🚧 항목 | 상태 |
|------|------|---------------------|------|
| `Eq. (9)` 메인 flow matching | `analysis/2511.00139/analysis.md §🔬` | `modeling_pi0_enhance.py` `se_main = (v_main - u_t) ** 2` | 구현 |
| `Eq. (10)` 손 보조 손실 | `analysis/2511.00139/analysis.md §🔬` | `se_hand = ((v_hand - u_t) ** 2) * hand_mask` | 구현 |
| `Eq. (11)` 팔 보조 손실 | `analysis/2511.00139/analysis.md §🔬` | `se_arm = ((v_arm - u_t) ** 2) * arm_mask` | 구현 |
| `Eq. (12)` 총손실 | `design.md §📊` | `se_main + aux_loss_weight * (se_arm + se_hand)` | 구현 |
| `Eq. (2)` LSTM MSE+L2 | `analysis/2511.00139/analysis.md §🔬` | `impl.md §🚧 #2` | 유보 |
| `Eq. (3)` CAE 재구성 | `analysis/2511.00139/analysis.md §🔬` | `impl.md §🚧 #1` | 유보 |
| `Eq. (14)` 비축적 corrective | `design.md §📊` | `impl.md §🚧 #3` | 유보 |
| `Eq. (4)` / `Eq. (8)` 입력 계약 | `design.md §🧮` | `impl.md §🚧 #1` (촉각) / data layer | 유보 |
| `Table 1`–`Table 4` · `Fig. 16` | `analysis/2511.00139/analysis.md §📊` | 평가 결과 — 정적 검증 대상 아님 | 유보 |

<!-- silent-skip 없음 (모든 미구현 식은 §🚧 또는 평가 유보로 명시) → §🧪 partial 유발 없음. -->

---

## 🧬 실행 검증

런타임을 refresh 된 pin (`3410b40`) 에서 새로 빌드해 실행했습니다
(`.ready` 마커가 구 pin `999e77ad` 와 불일치 → 재빌드).

```text
$ py=$(bash scripts/ensure-foundry-runtime.sh lerobot)
$ git -C .foundry-runtime/lerobot/src rev-parse HEAD
3410b40275f31d6fa66345c99cf076d36991a313
$ git -C .foundry-runtime/lerobot/src apply -p3 --directory=src/lerobot \
      "$PWD/analysis/2511.00139/impl/lerobot/impl.patch"
$ "$py" -m pytest .../tests/test_pi0_enhance_smoke.py -q
......                                                                   [100%]
6 passed in 0.44s
```

판정: `pass` (6 passed)

<!-- subclass-seam 산출물을 refresh 된 pinned commit 의 설치된 lerobot 에
     적용하고 sibling smoke test 를 실행 — enhancer shape, paper 계약 index
     mask (arm 6 + hand 12 = 18, max 32 padding), 손실 유한성·backprop,
     식 12 의 λ=0 → main-only 환원, config 기본값/검증, factory 등록을 CPU
     에서 검증. 백본 forward (PaliGemma 가중치 필요) 는 범위 밖. -->

---

## ⚖️ 종합 판정

- 📚 문헌 대조: `pass`
- 🔍 패치 정합성: `pass`
- 🧪 시그니처·하이퍼파라미터: `pass`
- 🧬 실행 검증: `pass`

→ 이 foundry 의 구현은 vendor refresh (`999e77ad` → `3410b40`) 후에도 in-scope 범위 (π_uni Arm-Hand Feature Enhancement, 식 9–12) 에서 Design 과 정합하며 실행 검증(6 passed)을 통과합니다. 촉각 인코더·LSTM admittance·비축적 corrective SFT 는 `pi0` base 좌표계 밖이라 honest defer (`out-of-base-scope`) 로 남습니다.

---

## 🔎 §🚧 분류

| §🚧 # | 항목 한 줄 | bucket | 근거 / 다음 액션 |
|-------|------------|--------|-------------------|
| 1 | 촉각 인코더 (CAE+resultant-force MLP, §3.2.2) | `out-of-base-scope` | `impl.md §🧱` EXCLUDE 선언 + §🪛 신규-미구현 행 — `pi0` 에 촉각 모달리티 없음. outer/inner 모두 무의미 |
| 2 | LSTM admittance 정책 (§3.2.1) | `out-of-base-scope` | `impl.md §🧱` EXCLUDE — `pi0` 와 무관한 독립 정책 |
| 3 | 비축적 corrective SFT 루프 (식 14) | `out-of-base-scope` | `impl.md §🧱` EXCLUDE — 모델 forward 가 아닌 학습 오케스트레이션 레이어 |
| 4 | selective gating 임계값 τ_contact (§8.2.1) | `out-of-base-scope` | `impl.md §🧱` EXCLUDE — 촉각 모달리티 부재로 base 밖 |

<!-- zero-state 재분류 — 직전 라운드와 동일한 4 항목이 그대로 base 좌표계
     밖 honest defer 로 남습니다 (vendor refresh 는 base scope 를 바꾸지
     않음). -->

<!-- ANALYSIS_BUCKETS:START -->
- vendor-resolved:
- paper-extractable:
- paper-silent-defaultable:
- paper-silent-experimental:
- out-of-base-scope: 1,2,3,4
- focus-hint:
<!-- ANALYSIS_BUCKETS:END -->

---

## 🚧 미해결 / 잠정

- `out-of-base-scope` 4개 항목 (촉각 인코더·LSTM·corrective·τ_contact) 은 `pi0` base 좌표계 밖이라 정적 검증으로 더 진행할 수 없습니다 — 별도 foundry 또는 신규 모듈 좌표계가 필요합니다.
- enhancement 의 수렴/성능 (88.7% 등) 검증은 실제 학습이 필요해 정적 validation 으로 결론 불가.
- `impl.md` 📄 메타의 `Foundry pinned commit` 행이 구 pin `999e77ad` 를 인용한 채 남아 있습니다 (validation 은 impl 파일을 수정하지 않음). 패치 자체는 새 pin 에 정합하므로 기능 결함은 아니며, 다음 `/implement-design` 재실행 시 메타 행이 `3410b40` 으로 갱신되어야 합니다.
