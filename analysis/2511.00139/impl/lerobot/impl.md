# Implementation Guide — End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy on `lerobot`

> PROBE foundry 모드 산출물 (Layer 2, foundry-specific). 한글 단일
> 문서이며, sibling Design (`analysis/2511.00139/design.md`) 을 입력으로
> 받아 한 foundry 의 좌표계 위에서 변경 지점을 매핑합니다. 형식·이모지
> ·용어 규칙은 `docs/STYLE.md` §6 / §4 를 정확히 따릅니다.
> 재실행 시 이 파일과 sibling `impl.patch` 를 덮어씁니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 | End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy: VR Teleoperation Augmented by Autonomous Hand VLA Policy for Efficient Data Collection |
| 링크 | [arXiv:2511.00139](https://arxiv.org/abs/2511.00139) |
| 상위 Design | [`../../design.md`](../../design.md) |
| Foundry | `lerobot` |
| Foundry pinned commit | `999e77ad7bc30774cccca58bd29f732a90600931` (`vendor/lerobot/README.md` 와 일치) |
| 베이스 모델 / 코드 좌표 | `pi0` (`vendor/lerobot/policies/pi0/`) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 패치 파일 | [`./impl.patch`](./impl.patch) — `git apply --check` 통과 |
| 실행 테스트 | [`./test_pi0_enhance_smoke.py`](./test_pi0_enhance_smoke.py) — `/audit §🧬` 가 설치된 foundry 에서 실행 (6 passed) |
| 가이드 생성일 | 2026-05-22 |

---

## 🧱 베이스 / 코드 좌표 식별

본 논문은 $`\pi_0`$ 백본을 그대로 사용한다고 명시합니다 (Design §🔌 foundry 힌트, §✨ 변경 의도). PaliGemma + conditional flow matching action expert 라는 구조 지문이 `vendor/lerobot/policies/pi0/` 와 정확히 일치하므로 베이스는 `pi0` 로 확정합니다 (`pi05`/`pi0_fast` 는 변형, `smolvla`/`act`/`diffusion` 은 백본 불일치).

**구현 형태 — subclass-seam.** 논문의 Arm-Hand Feature Enhancement 는 `PI0Pytorch` 의 action expert 최종 hidden state ($`z_{\text{share}}`$) 에서 분기하는 모듈입니다. vendor 의 `modeling_pi0.py` 를 in-place 로 헤집는 대신, **(1) base 에 동작-보존 seam 2개**(`PI0Pytorch._compute_suffix_out` extract-method, `PI0Policy._build_model` factory)를 내고, **(2) 그 seam 을 override 하는 신규 서브클래스 모듈** `modeling_pi0_enhance.py` (`configuration_pi0_enhance.py`) 를 추가하는 형태로 매핑합니다. 이로써 (a) base 동작과 사전학습 가중치 로딩은 불변이고 (`feature_enhancement=False` 면 vanilla pi0 와 동일 = πuni-origin), (b) 산출물이 설치 가능한 foundry 위에서 **실제 import·인스턴스화·손실 계산을 실행으로 검증**할 수 있게 됩니다 (sibling `test_pi0_enhance_smoke.py`, audit §🧬).

**SCOPE 선언.** 이 `pi0` 베이스는 논문의 **통합 정책 $`\pi_{\text{uni}}`$ 의 Arm-Hand Feature Enhancement (사지별 MLP 2개 + 보조 헤드 2개 + fused-concat main 헤드) 와 그 학습 목표 (식 9–12)** 만 COVER 합니다. 다음은 base 좌표계 밖이므로 EXCLUDE 합니다.

- **촉각 인코더 (CAE + resultant-force MLP, §3.2.2)** — `pi0` 에는 촉각 모달리티/인코더가 없음. 별도 신규 모듈이 필요하며 정책 내부 변경이 아님 — 제외.
- **LSTM admittance 정책 (§3.2.1)** — `pi0` 와 무관한 독립 부트스트랩 정책 — 제외.
- **$`\pi_{\text{hand}}`$ 의 촉각 토큰 주입 (식 4)** — 입력 모달리티 확장이라 촉각 인코더 부재와 함께 제외.
- **비축적 corrective SFT 루프 (식 14)** — 학습 오케스트레이션/데이터셋 선택 레이어이지 모델 forward 변경이 아님 — 제외.
- **VR teleoperation / shared-autonomy 데이터 수집 (§3.3)** — 코드 좌표계 밖의 하드웨어/수집 파이프라인 — 제외.

---

## 🪛 변경 지점 매핑

| # | Foundry 위치 | 변경 종류 | Design 근거 | 요약 |
|---|--------------|-----------|-------------|------|
| 1 | `vendor/lerobot/policies/pi0/modeling_pi0.py:750` | 수정 (seam) | Design §🧰 `pi_uni_main_head` 힌트 | `forward` 에서 prefix/suffix 임베딩+attention 부분을 `_compute_suffix_out` 으로 extract — 동작 보존, 서브클래스가 $`z_{\text{share}}`$ 에서 분기할 hook 제공 |
| 2 | `vendor/lerobot/policies/pi0/modeling_pi0.py:968` | 수정 (seam) | Design §🧰 | `PI0Policy.__init__` 의 모델 생성을 `_build_model` factory 로 우회 — 서브클래스가 대체 `PI0Pytorch` 를 끼울 override 지점 |
| 3 | `vendor/lerobot/policies/pi0/configuration_pi0_enhance.py` (신규) | 추가 | Design §📊, §🚧 | `PI0EnhanceConfig` — `feature_enhancement`(기본 off)·`arm_dim=6`·`aux_loss_weight=1.0` 필드 + 검증 |
| 4 | `vendor/lerobot/policies/pi0/modeling_pi0_enhance.py` (신규) | 추가 | Design §🧰 `arm_hand_feature_enhancement`·`aux_heads`·`pi_uni_main_head`, §📊 식 9–12 | `ArmHandFeatureEnhancer`(E_arm/E_hand 2-layer Mish, H_arm/H_hand/H_main) + `build_index_masks` + `compute_feature_enhancement_loss` + `PI0EnhancePytorch`/`PI0EnhancePolicy` |
| 5 | `vendor/lerobot/policies/pi0/__init__.py` | 수정 | Design §🧰 | 신규 `PI0EnhanceConfig`/`PI0EnhancePolicy` export (factory 가 등록 이름 `pi0_enhance` 로 resolve) |
| — | (촉각 인코더 · LSTM · corrective SFT) | 신규-미구현 | Design §🧰, §📊 | base 좌표계 밖 — §🧱 EXCLUDE 선언 참조, `out-of-base-scope` |

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다.
아래는 가장 핵심적인 hunk 의 인라인 발췌입니다 (전문 인용 금지 — 패치 파일이 정본).

식 9·10·11·12 를 구현하는 손실 합성 (`modeling_pi0_enhance.py`):

```python
se_main = (v_main - u_t) ** 2                       # Eq. (9) main flow loss
se_arm = ((v_arm - u_t) ** 2) * arm_mask            # Eq. (10) selective arm
se_hand = ((v_hand - u_t) ** 2) * hand_mask         # Eq. (11) selective hand
return se_main + aux_loss_weight * (se_arm + se_hand)  # Eq. (12)
```

동작-보존 seam (`modeling_pi0.py`) — `forward` 를 둘로 쪼개되 의미 불변:

```diff
-    def forward(self, images, ...):
-        """Do a full training forward pass and compute the loss."""
-        time_expanded = time[:, None, None]
+    def _compute_suffix_out(self, images, ...) -> tuple[Tensor, Tensor]:
+        """... z_share hook point ..."""
+        time_expanded = time[:, None, None]
         ...
         suffix_out = suffix_out.to(dtype=torch.float32)
+        return suffix_out, u_t
+
+    def forward(self, images, ...):
+        suffix_out, u_t = self._compute_suffix_out(images, ...)
```

`git apply --check` 결과: 통과

설계 메모 — 보조 손실은 per-element 손실 텐서 `(B, chunk, max_action_dim)` 의 해당 DoF 슬라이스에 index mask 를 곱해 가산합니다. 호출부 `PI0Policy.forward` 가 그대로 `losses[:, :, :original_action_dim].mean()` 으로 환산하므로 반환 계약(shape)을 깨지 않고 식 12 의 $`\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{main}} + \lambda(\mathcal{L}_{\text{hand}}+\mathcal{L}_{\text{arm}})`$ 가 그대로 평균됩니다. selective supervision 은 arm 을 `[0:6)`, hand 를 `[6:18)` 인덱스 마스크로 제한합니다 (padding `[18:32)` 는 양쪽 0 — autograd-safe).

---

## 🧪 실무 구현 주의

- **실행 검증** — sibling `test_pi0_enhance_smoke.py` 는 enhancer shape, index mask 의 paper 계약 (arm 6 + hand 12 = 18, max 32 padding), 손실 유한성·backprop, 식 12 의 $`\lambda{=}0`$ → main-only 환원, config 기본값/검증, factory 등록을 CPU 에서 검증합니다 (GPU·체크포인트·HF 다운로드 불필요). `/audit §🧬` 가 `scripts/ensure-foundry-runtime.sh lerobot` 로 foundry 를 pinned commit 에 설치하고 patch 를 적용한 뒤 이 테스트를 실행합니다 — round 0 기준 6 passed.
- **외부 의존성** — `google/paligemma-3b-pt-224` 백본 가중치 다운로드 필요 (base `pi0` 와 동일, smoke test 범위 밖). enhancement 모듈은 신규 파라미터이므로 SFT 시 처음부터 학습됩니다.
- **데이터셋** — 표준 `LeRobotDataset` 포맷. arm 6-DoF + hand 12-DoF 가 action 벡터의 앞 18 차원 (max_action_dim=32 패딩). DoF 정렬이 다르면 `arm_dim` 슬라이스 위치를 조정합니다.
- **평가 / 추론** — `feature_enhancement=False` (πuni-origin) 이면 base `pi0` 와 byte-동일 경로라 기존 체크포인트 호환. `True` 면 `_build_model` 이 `PI0EnhancePytorch` 를 끼웁니다.

확정된 상수 (라운드 1 에서 §🚧 → 여기로 이동):

- **default 채택 (paper-silent)** — $`\lambda = 1.0`$ (`aux_loss_weight`). paper §3.4.2 침묵 → config default + `# NOTE` 주석으로 근거 명시.
- **vendor-resolved 상수** — 공유 latent 차원 $`d_s`$ = `get_gemma_config(action_expert_variant).width`. 사지별 latent 은 `d_s//2`.
- **vendor-resolved 상수** — action chunk size $`H`$ = `chunk_size: int = 50` (`vendor/lerobot/policies/pi0/configuration_pi0.py:36`).

---

## 🚧 미해결 / 잠정

> 라운드 1 (feedback) 에서 $`\lambda`$ (paper-silent-defaultable) · $`d_s`$ · $`H`$ (vendor-resolved) 3 항목이 §🧪 실무 구현 주의 "확정된 상수" 로 이동했습니다. 아래에는 base 좌표계 밖 honest-defer 항목만 남습니다.

1. 촉각 인코더 (CAE + resultant-force MLP, §3.2.2) 는 `pi0` 좌표계 밖 — §🧱 EXCLUDE, `out-of-base-scope` (§🪛 마지막 행).
2. LSTM admittance 정책 (§3.2.1) 은 `pi0` 좌표계 밖 — §🧱 EXCLUDE, `out-of-base-scope`.
3. 비축적 corrective SFT 루프 (식 14) 는 학습 오케스트레이션 레이어로 모델 forward 변경이 아님 — §🧱 EXCLUDE, `out-of-base-scope`.
4. selective gating 임계값 $`\tau_{\text{contact}}`$ (음의 촉각 결과, §8.2.1) 은 촉각 모달리티 부재로 base 밖 — `out-of-base-scope`.

---

### 🔁 변경 사유 (feedback 모드)

- **라운드 2 (verifiable 형태로 재구성):**
  - in-place forward 수정 → **subclass-seam** 으로 전환: base 에 동작-보존 seam 2개 (`_compute_suffix_out`, `_build_model`) + 신규 `modeling_pi0_enhance.py`/`configuration_pi0_enhance.py`. 의미는 라운드 1 과 동일 (식 9–12) 하나, 산출물이 설치된 foundry 에서 **실행 검증** 가능해짐 (sibling `test_pi0_enhance_smoke.py`, audit §🧬).
  - 결과: §🪛 표가 in-place 5행 → seam 2 + 신규모듈 2 + export 1 로 재매핑. §🚧 honest-defer 4행 불변.
- **라운드 1 (입력 verify: `../../audit/lerobot.round_0.md`):**
  - 갭 `§🔎 #1` (paper-silent-defaultable, λ) → 액션 `default 채택` → 결과 `§🚧 #1 → §🧪 "default 채택 (paper-silent)" 이동`.
  - 갭 `§🔎 #2` (vendor-resolved, d_s) → 액션 `vendor 값 lift` → 결과 `§🚧 #2 → §🧪 이동`.
  - 갭 `§🔎 #3` (vendor-resolved, H) → 액션 `vendor 값 lift` → 결과 `§🚧 #3 → §🧪 이동`.
  - 갭 `§🔎 #4–#7` (out-of-base-scope) → 액션 `honest defer 유지` → 결과 `§🚧 #1–#4 로 잔존`.
