# Implementation Guide — End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy on `lerobot`

> PROBE foundry 모드 산출물 (Layer 2, foundry-specific). 한글 단일
> 문서이며, sibling Design (`analysis/2511.00139_design.md`) 을 입력으로
> 받아 한 foundry 의 좌표계 위에서 변경 지점을 매핑합니다. 형식·이모지
> ·용어 규칙은 `docs/STYLE.md` §6 / §4 를 정확히 따릅니다.
> 재실행 시 이 파일과 sibling `impl.patch` 를 덮어씁니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 | End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy: VR Teleoperation Augmented by Autonomous Hand VLA Policy for Efficient Data Collection |
| 링크 | [arXiv:2511.00139](https://arxiv.org/abs/2511.00139) |
| 상위 Design | [`../../2511.00139_design.md`](../../2511.00139_design.md) |
| Foundry | `lerobot` |
| Foundry pinned commit | `999e77ad7bc30774cccca58bd29f732a90600931` (`vendor/lerobot/README.md` 와 일치) |
| 베이스 모델 / 코드 좌표 | `pi0` (`vendor/lerobot/policies/pi0/`) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 패치 파일 | [`./impl.patch`](./impl.patch) — `git apply --check` 통과 |
| 가이드 생성일 | 2026-05-22 |

---

## 🧱 베이스 / 코드 좌표 식별

본 논문은 $`\pi_0`$ 백본을 그대로 사용한다고 명시합니다 (Design §🔌 foundry 힌트, §✨ 변경 의도). PaliGemma + conditional flow matching action expert 라는 구조 지문이 `vendor/lerobot/policies/pi0/` 와 정확히 일치하므로 베이스는 `pi0` 로 확정합니다 (`pi05`/`pi0_fast` 는 변형, `smolvla`/`act`/`diffusion` 은 백본 불일치). 핵심 결합점은 `PI0Pytorch` (`modeling_pi0.py:554`) 의 action expert 출력 직후 — `forward` 가 `suffix_out` (= 공유 latent $`z_{\text{share}}`$, 차원 `action_expert_config.width`) 을 만들어 `action_out_proj` 로 액션 속도장 $`v_t`$ 를 내는 지점 (`modeling_pi0.py:791–799`) 입니다. Arm-Hand Feature Enhancement 는 바로 이 $`z_{\text{share}}`$ 를 받아 사지별 latent 로 분기시키는 모듈이므로 자연 삽입 지점이 됩니다.

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
| 1 | `vendor/lerobot/policies/pi0/configuration_pi0.py:87` | 필드 추가 | Design §📊, §🚧 | `enhancement_enabled`/`enhancement_lambda`/`enhancement_arm_dim`/`enhancement_hand_dim` 4개 config 필드 추가 (기본 off) |
| 2 | `vendor/lerobot/policies/pi0/modeling_pi0.py:585` | 추가 | Design §🧰 `arm_hand_feature_enhancement`·`aux_heads`·`pi_uni_main_head` | 사지별 2-layer Mish MLP 2개, single-linear 보조 헤드 2개, fused-concat main 헤드를 `PI0Pytorch.__init__` 에 신설 (enabled 시) |
| 3 | `vendor/lerobot/policies/pi0/modeling_pi0.py:748` | 추가 | Design §🧰 `pi_uni_main_head` | `_enhancement_main` 헬퍼 — `fused = concat([z_share, z_arm, z_hand])` → main 헤드 디코딩 |
| 4 | `vendor/lerobot/policies/pi0/modeling_pi0.py:791–799` | 수정 | Design §📊 식 9·10·11·12 | 학습 `forward` 에 enhancement 분기 추가: 메인 flow-matching 손실 + 사지별 selective 보조 손실 $`\lambda(\mathcal{L}_{\text{arm}}+\mathcal{L}_{\text{hand}})`$ 합산 |
| 5 | `vendor/lerobot/policies/pi0/modeling_pi0.py:920–923` | 수정 | Design §🧰 `pi_uni_main_head` | 추론 `denoise_step` 도 동일 fused-concat main 헤드를 타도록 분기 (학습/추론 경로 정합) |
| — | (촉각 인코더 · LSTM · corrective SFT) | 신규-미구현 | Design §🧰, §📊 | base 좌표계 밖 — §🧱 EXCLUDE 선언 참조, `out-of-base-scope` |

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다.
아래는 가장 핵심적인 hunk 의 인라인 발췌입니다 (전문 인용 금지 — 패치 파일이 정본).

```diff
--- a/vendor/lerobot/policies/pi0/modeling_pi0.py
+++ b/vendor/lerobot/policies/pi0/modeling_pi0.py
@@ -791,6 +812,24 @@
         suffix_out = suffix_out[:, -self.config.chunk_size :]
         suffix_out = suffix_out.to(dtype=torch.float32)

+        if self.config.enhancement_enabled:
+            # Eq. (9): flow-matching main loss on the fused-concat main head.
+            v_t, z_arm, z_hand = self._enhancement_main(suffix_out)
+            losses = F.mse_loss(u_t, v_t, reduction="none")
+            # Eq. (10)-(11): selective per-limb auxiliary regression, each on its own DoF slice.
+            a = self.config.enhancement_arm_dim
+            h = self.config.enhancement_hand_dim
+            arm_loss = F.mse_loss(u_t[..., :a], self.enh_aux_arm_head(z_arm)[..., :a], reduction="none")
+            hand_loss = F.mse_loss(
+                u_t[..., a : a + h], self.enh_aux_hand_head(z_hand)[..., a : a + h], reduction="none"
+            )
+            d = losses.shape[-1]
+            arm_pad = F.pad(arm_loss, (0, d - a))
+            hand_pad = F.pad(hand_loss, (a, d - a - h))
+            return losses + self.config.enhancement_lambda * (arm_pad + hand_pad)
```

`git apply --check` 결과: 통과

설계 메모 — 보조 손실은 per-element 손실 텐서 `(B, chunk, max_action_dim)` 의 해당 DoF 슬라이스에 $`\lambda`$ 를 곱해 가산합니다. 호출부 `PI0Policy.forward` (`modeling_pi0.py:1290–1307`) 가 그대로 `losses[:, :, :original_action_dim].mean()` 으로 환산하므로 반환 계약(shape)을 깨지 않고 식 12 의 $`\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{main}} + \lambda(\mathcal{L}_{\text{hand}}+\mathcal{L}_{\text{arm}})`$ 가 그대로 평균됩니다. selective supervision 은 arm 을 `[0:6]`, hand 를 `[6:18]` 인덱스 슬라이스로 제한해 구현합니다 (`F.pad` 로 zero-pad 후 가산 — autograd-safe, in-place 없음).

---

## 🧪 실무 구현 주의

- **외부 의존성** — `google/paligemma-3b-pt-224` 백본 가중치 다운로드 필요 (base `pi0` 와 동일). enhancement 모듈 (`enh_*`) 은 사전학습 가중치가 없는 신규 파라미터이므로 SFT 시 처음부터 학습됩니다.
- **데이터셋** — 표준 `LeRobotDataset` 포맷. arm 6-DoF + hand 12-DoF 가 action 벡터의 앞 18 차원을 차지한다고 가정 (max_action_dim=32 패딩). 실제 데이터셋의 DoF 정렬이 다르면 `enhancement_arm_dim`/`enhancement_hand_dim` 슬라이스 위치를 조정해야 합니다.
- **학습 하이퍼파라미터** — enhancement 는 `enhancement_enabled=True` 로만 활성화. $`\lambda`$ 기본 1.0 (paper 침묵, default 채택). 공유 latent 차원 $`d_s`$ 는 `action_expert_config.width` 로 귀속시키고 사지별 latent 은 `width//2` 로 둠 (Design §📊 `d_s/2`).
- **평가 / 추론** — `denoise_step` 도 fused-concat 경로를 타므로 학습/추론 정합. `action_out_proj` (base 경로) 는 enhancement off 일 때만 사용되어 기존 체크포인트 호환 유지.

---

## 🚧 미해결 / 잠정

1. 총 손실 보조 가중치 $`\lambda`$ 의 절대값이 본문(§3.4.2)에 없습니다 — patch 에 default `1.0` 을 도입하고 `# NOTE` 주석으로 근거를 명시했습니다 (paper-silent-defaultable).
2. 공유 latent 차원 $`d_s`$ 와 encoder/head 의 정확한 hidden width 가 §7.3 에 절대값으로 명시되지 않습니다 — `action_expert_config.width` (vendor 기본) 에 귀속시켰습니다 (vendor-resolved 후보).
3. action chunk size $`H`$ 가 본문 미명시 — vendor `pi0` 기본 `chunk_size = 50` 을 사용합니다 (vendor-resolved 후보).
4. 촉각 인코더 (CAE + resultant-force MLP, §3.2.2) 는 `pi0` 좌표계 밖 — §🧱 EXCLUDE, `out-of-base-scope` (§🪛 마지막 행).
5. LSTM admittance 정책 (§3.2.1) 은 `pi0` 좌표계 밖 — §🧱 EXCLUDE, `out-of-base-scope`.
6. 비축적 corrective SFT 루프 (식 14) 는 학습 오케스트레이션 레이어로 모델 forward 변경이 아님 — §🧱 EXCLUDE, `out-of-base-scope`.
7. selective gating 임계값 $`\tau_{\text{contact}}`$ (음의 촉각 결과, §8.2.1) 은 촉각 모달리티 부재로 base 밖 — `out-of-base-scope`.
