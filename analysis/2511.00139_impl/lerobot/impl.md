# Implementation Guide — End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy: VR Teleoperation Augmented by Autonomous Hand VLA Policy for Efficient Data Collection on `lerobot`

> PROBE foundry 모드 산출물 (Layer 2, foundry-specific). 한글 단일
> 문서이며, sibling Design (`analysis/2511.00139_design.md`) 을
> 입력으로 받아 `lerobot` 좌표계 위에서 변경 지점을 매핑합니다.
> 형식·이모지·용어 규칙은 `docs/STYLE.md` §6 / §4 를 정확히 따릅니다.
> 재실행 시 이 파일과 sibling `impl.patch` 를 덮어씁니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 | End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy: VR Teleoperation Augmented by Autonomous Hand VLA Policy for Efficient Data Collection |
| 링크 | [arXiv:2511.00139](https://arxiv.org/abs/2511.00139) |
| 상위 Design | [`../../2511.00139_design.md`](../../2511.00139_design.md) |
| Foundry | `lerobot` |
| Foundry pinned commit | `999e77ad7bc30774cccca58bd29f732a90600931` |
| 베이스 모델 / 코드 좌표 | `pi0` — `vendor/lerobot/policies/pi0/` |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 패치 파일 | [`./impl.patch`](./impl.patch) — `git apply --check` 통과 |
| 가이드 생성일 | 2026-05-21 |

---

## 🧱 베이스 / 코드 좌표 식별

논문은 자체 모델을 **"π0 백본을 그대로 채택하고 그 위에 Arm-Hand
Feature Enhancement 를 얹는 구조" (§7.3)** 로 명시하므로, lerobot
foundry 의 6 개 vendored 정책 중 베이스는 `pi0` 가 유일한 자연 매핑
입니다. 구체적으로 PaliGemma 비전·언어 prefix 와 Gemma action expert
suffix 가 conditional flow matching 으로 액션 chunk 를 디코딩하는
파이프라인이 그대로 보존되며, 본 논문이 더하는 것은 expert 의 공유
latent ($`z_t^{\text{share}}`$) 를 받아 사지별 latent ($`z_t^{\text{arm}}`$,
$`z_t^{\text{hand}}`$) 로 쪼개고 보조 헤드를 단 뒤 main flow-matching
head 입력으로 `concat([z_share, z_arm, z_hand])` 를 흘리는 형태의
얇은 후처리 블록입니다. 따라서 패치는 `vendor/lerobot/policies/pi0/`
범위 안에서 외과적으로 완결되며, 다른 베이스 (`pi05`, `pi0_fast`,
`smolvla`, `act`, `diffusion`) 와 공유되는 모듈 (`pi_gemma.py`,
`processor/`) 은 건드리지 않습니다.

`pi05` 도 PaliGemma + flow matching 계열이라 후보였지만, 논문이
명시적으로 "$`\pi_0`$" 의 두 가지 variant 중 base 만 인용하고 §7.1
에서 vision encoder 만 동결한 full-parameter SFT 를 기준 단계로
제시하므로 `pi0` 매핑이 더 직접적입니다 (`pi05` 의 prefix-suffix
KV-share 구조는 본 논문 범위 밖).

---

## 🪛 변경 지점 매핑

| # | Foundry 위치 | 변경 종류 | Design 근거 | 요약 |
|---|--------------|-----------|-------------|------|
| 1 | `vendor/lerobot/policies/pi0/configuration_pi0.py:87` (직후) | 필드 추가 | Design §📊, §🚧 | `enhancement_enabled`, `enhancement_aux_loss_weight (λ)`, `enhancement_arm_indices`, `enhancement_hand_indices` 4 개 필드를 dataclass 끝부분에 추가. 기본값은 OFF 라 기존 동작은 변경 없음 |
| 2 | `vendor/lerobot/policies/pi0/modeling_pi0.py:554` (직전) | 클래스 추가 | Design §🧰 `arm_hand_feature_enhancement` / `aux_heads` / `pi_uni_main_head`, Design §📊 §7.3 | 새 `ArmHandFeatureEnhancement(nn.Module)` 클래스. 2-layer Mish MLP × 2 (`arm_mlp`, `hand_mlp`), 단일-linear 보조 헤드 × 2 (`aux_arm`, `aux_hand`), `main_proj` 가 fused concat 을 expert width 로 환원해 기존 `action_out_proj` 가 그대로 받음 |
| 3 | `vendor/lerobot/policies/pi0/modeling_pi0.py:585` (직후) | 수정 (init wire) | Design §🧰, Design §🚧 (잠정 dim) | `PI0Pytorch.__init__` 끝부분에서 `config.enhancement_enabled` 가 켜져 있을 때만 enhancement 모듈을 인스턴스화. OFF 면 `self.enhancement = None` |
| 4 | `vendor/lerobot/policies/pi0/modeling_pi0.py:791` 부근 | 수정 (forward) | Design §🧰 `pi_uni_main_head`, §📊 식 (9) | `PI0Pytorch.forward` 의 `suffix_out → action_out_proj` 경로에 enhancement 분기 추가. ON 시 `(fused, aux_arm, aux_hand) = enhancement(suffix_out)` → `v_t = action_out_proj(fused)`. 단 보조 손실 합성은 아직 미연결 (→ §🚧 #1) |
| 5 | `vendor/lerobot/policies/pi0/modeling_pi0.py:923` 부근 | 수정 (denoise_step) | Design §🧰 inference 일관성 | `PI0Pytorch.denoise_step` 도 동일하게 enhancement 분기 추가. 학습 시 fused latent 로 디코딩했다면 추론도 같은 경로여야 함 |
| 6 | (없음) | — | Design §🧮 §3.2.2 | 촉각 인코더 (CAE + MLP projection + fingertip-token 주입) — baseline 에 대응 없음 — 신규 추가 필요. 본 패치 범위 밖 (→ §🚧 #2) |
| 7 | (없음) | — | Design §🧰 `corrective_sft`, §📊 식 (14) | 비축적 corrective SFT 루프 — 학습 스크립트 영역이며 modeling 계층 변경 없음. 본 패치 범위 밖 (→ §🚧 #3) |
| 8 | (없음) | — | Design §🧰 `tactile_encoder` (LSTM admittance) | 자율 데이터 부트스트랩용 LSTM admittance 정책 — 모델·데이터 수집 파이프라인 영역. 본 패치 범위 밖 (→ §🚧 #4) |

📚 §🪛 의 `file:line` 은 foundry pinned commit
`999e77a…` 기준이며, 벤더 refresh 시 함께 갱신됩니다.

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다. 아래는
가장 핵심적인 hunk 발췌입니다 (전문 인용 금지 — 패치 파일이 정본).

```diff
--- a/vendor/lerobot/policies/pi0/modeling_pi0.py
+++ b/vendor/lerobot/policies/pi0/modeling_pi0.py
@@ -551,6 +551,54 @@
+class ArmHandFeatureEnhancement(nn.Module):
+    """Arm-Hand Feature Enhancement (arXiv:2511.00139, §7.3)."""
+    def __init__(self, width: int, max_action_dim: int):
+        super().__init__()
+        half = width // 2
+        self.arm_mlp  = nn.Sequential(nn.Linear(width, width), nn.Mish(),
+                                     nn.Linear(width, half),  nn.Mish())
+        self.hand_mlp = nn.Sequential(nn.Linear(width, width), nn.Mish(),
+                                     nn.Linear(width, half),  nn.Mish())
+        self.aux_arm  = nn.Linear(half, max_action_dim)
+        self.aux_hand = nn.Linear(half, max_action_dim)
+        self.main_proj = nn.Linear(width + 2 * half, width)
```

```diff
@@ -791,10 +846,16 @@
         suffix_out = suffix_out[:, -self.config.chunk_size :]
         suffix_out = suffix_out.to(dtype=torch.float32)
+        if self.enhancement is not None:
+            fused, _aux_arm, _aux_hand = self.enhancement(suffix_out)
+            v_t = self.action_out_proj(fused)
+        else:
+            ...
         return F.mse_loss(u_t, v_t, reduction="none")
```

`git apply --check` 결과: 통과.

---

## 🧪 실무 구현 주의

- **외부 의존성** — π0 백본은 HuggingFace 의 `google/paligemma-3b-pt-224`
  체크포인트와 lerobot 의 `lerobot/pi0` HF hub 모델을 통해 받습니다.
  `from_pretrained` 경로는 본 패치가 건드리지 않습니다 (state_dict 키
  매핑은 enhancement 모듈명이 새로 추가되므로 strict load 시 missing
  keys 경고가 뜨지만, 가중치는 정상적으로 새 모듈로 초기화됩니다).
- **데이터셋** — `LeRobotDataset` 의 episode metadata 에 fingertip
  tactile 채널 (`F_raw ∈ ℝ^{10×12×3}` per fingertip × 5 손가락) 을
  추가해야 §🚧 #2 (촉각 인코더) 가 의미를 갖습니다. 본 패치는 이 데이터
  스키마 변경을 포함하지 않습니다.
- **학습 하이퍼파라미터** — Design §📊 의 `train.steps=80,000`,
  `inference.control_hz=30` 은 lerobot 학습 루프 (`lerobot/scripts/
  train.py`) 의 인자로 외부에서 주입됩니다. 본 패치는 `PI0Config` 의
  optimizer/scheduler 기본값 (peak_lr 2.5e-5, cosine warmup 1k / decay
  30k) 을 그대로 둡니다 — 80k 스텝으로 늘릴 경우 `scheduler_decay_steps`
  를 80,000 으로 명시 지정해야 합니다.
- **vision encoder 동결** — Design §7.1 의 "vision encoder 만 동결한
  full-parameter SFT" 는 vendor 의 `PI0Config.freeze_vision_encoder=
  True` + `train_expert_only=False` 조합으로 곧장 표현 가능. 본 패치는
  기본값 변경을 강제하지 않으며 학습 config 에서 켭니다.
- **enhancement 활성화 방법** — `PI0Config(enhancement_enabled=True,
  enhancement_arm_indices=[0,1,2,3,4,5],
  enhancement_hand_indices=[6,7,...,17],
  enhancement_aux_loss_weight=1.0)`. arm 6-DoF + hand 12-DoF 가
  `max_action_dim=32` 패딩 안에서 어디로 매핑되는지는 데이터셋 측
  `action_feature_names` 순서에 달려 있어 학습 시 직접 지정해야
  합니다.
- **평가 / 추론** — `predict_action_chunk` 는 `denoise_step` 을 통해
  enhancement 분기를 자동으로 탑니다. RTC 추론도 동일하며 별도
  변경 없음.

---

## 🚧 미해결 / 잠정

1. **보조 손실 합성 미연결** — 본 패치는 enhancement 모듈을 forward 에
   배선만 했고 `aux_arm`, `aux_hand` 출력을 main loss 텐서에 합치지
   않습니다 (`_aux_arm`, `_aux_hand` 가 underscore 로 받힙니다).
   Design §📊 식 (10)–(12) 의 `L_total = L_main + λ(L_hand + L_arm)`
   selective-DoF supervision 을 완전히 구현하려면 `PI0Policy.forward`
   에서 model.forward 반환 시 aux 출력을 함께 받아 selective MSE 를
   `enhancement_arm_indices` / `enhancement_hand_indices` 에 한정해
   계산한 뒤 `losses` 에 가중치 `λ` 로 더해야 합니다. 본 라운드는
   `losses` 텐서 형상 (B, T, D) 의 의미를 깨지 않기 위해 보류했으며,
   다음 라운드에서 별도 hunk 로 승격 예정.
2. **촉각 인코더 (CAE + MLP projection)** — Design §3.2.2 의
   `(16,16,3)` zero-pad 후 `[32,64,128]` filter `3×3, stride 2` CAE
   (latent_dim 128 / fingertip) 와 fingertip raw 합력 `(5,3)` →
   MLP projection 모듈은 lerobot baseline 에 대응이 없으며, `pi0/`
   prefix/suffix 토큰 흐름에 새 token type 을 더해야 하므로 영향
   반경이 큽니다. 별도 hunk (신규 `tactile_encoder.py` 신설 +
   `PI0Pytorch.embed_suffix` 수정) 로 승격해야 하며 본 라운드 범위
   밖. 본문의 토큰 정렬 (state · time · action 다음 위치 vs. prefix
   끝) 이 명시되지 않아 첫 라운드부터 가정값으로 시작해야 합니다.
3. **비축적 corrective SFT 루프 (식 14)** — `π_uni^{(k+1)} =
   SFT(π_0; D_uni ∪ D^{(k)})` 는 lerobot 의 학습 스크립트 영역
   (`lerobot/scripts/train.py` 의 외부 루프) 입니다. modeling 계층
   변경 없음. 재현 시 별도 wrapper 스크립트가 필요합니다 (`pi0` 체크포인트
   초기 가중치 → corrective dataset 교체 → 새 체크포인트 → 반복).
4. **LSTM admittance 정책** — Design §3.2.1 의 hidden_dim 256,
   input_dim 39 (24 proprio + 15 tactile) LSTM 정책은 자율 데이터
   부트스트랩 단계 도구이며 lerobot 의 6 baseline 어디에도 직접
   매핑되지 않습니다. `lerobot.policies` 에 새 `lstm_admittance`
   정책을 신설하는 옵션은 본 patch 범위 밖.
5. **잠정 하이퍼파라미터** — Design §🚧 가 명시하듯 $`\lambda`$,
   $`d_s`$, action chunk $`H`$, $`τ_{\text{contact}}`$, corrective
   분류 규칙은 본문에 절대값이 없습니다. 본 패치는 $`d_s`$ =
   action_expert_config.width (Gemma 300m → `1024`), $`H`$ =
   `chunk_size=50` (`PI0Config` 기본값), $`\lambda`$ = `1.0` 으로
   가정합니다. 모두 학습 config 로 override 가능합니다.
