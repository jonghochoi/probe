# Implementation Guide — DynaFLIP: Rethinking Robotics Perception via Tri-Modal-Dynamics Guided Representation on `lerobot`

> PROBE foundry 모드 산출물 (Layer 2, foundry-specific). 한글 단일
> 문서이며, sibling Design (`analysis/2605.30350/design.md`) 을 입력으로
> 받아 한 foundry 의 좌표계 위에서 변경 지점을 매핑합니다. 형식·이모지
> ·용어 규칙은 `docs/STYLE.md` §6 / §4 를 정확히 따릅니다.
> 재실행 시 이 파일과 sibling `impl.patch` 를 덮어씁니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 | DynaFLIP: Rethinking Robotics Perception via Tri-Modal-Dynamics Guided Representation |
| 링크 | [arXiv:2605.30350](https://arxiv.org/abs/2605.30350) |
| 상위 Design | [`../design.md`](../design.md) |
| Foundry | `lerobot` |
| Foundry pinned commit | `999e77ad7bc30774cccca58bd29f732a90600931` (`vendor/lerobot/README.md` 와 일치) |
| 베이스 모델 / 코드 좌표 | `pi05` (`vendor/lerobot/policies/pi05/`) |
| 주입 메커니즘 근거 | PVI — [arXiv:2603.12772](https://arxiv.org/abs/2603.12772) (DynaFLIP §3.4 가 인용한 [60]) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 패치 파일 | [`./impl.patch`](./impl.patch) — `git apply --check` 통과 |
| 실행 테스트 | [`./test_pi05_dynaflip_smoke.py`](./test_pi05_dynaflip_smoke.py) — 9 passed |
| 가이드 생성일 | 2026-06-04 |

---

## 🧱 베이스 / 코드 좌표 식별

베이스는 `pi05` (`vendor/lerobot/policies/pi05/modeling_pi05.py`) 입니다. DynaFLIP 의
다운스트림 통합은 논문이 직접 $`\pi_{0.5}`$ 에 **PVI(plug-in visual injection, [60] =
[arXiv:2603.12772](https://arxiv.org/abs/2603.12772))** 유사 방식으로 동역학 인식 시각
feature 를 주입하는 것입니다. §3.4 원문이 주입 지점을 명시합니다 — *"an injection module
projects them into the **hidden feature space of the diffusion transformer** of π0.5"*. 즉
주입 표적은 **VLM prefix 가 아니라 액션 전문가(diffusion transformer)의 hidden 공간**입니다.
`pi05` 의 액션 전문가(`gemma_expert`)가 정확히 그 대상입니다.

핵심 주입 지점은 `PI05Pytorch.embed_suffix` (`modeling_pi05.py:683`) 로, 여기서 noisy action +
timestep 이 액션 전문가의 입력 hidden 으로 임베딩됩니다. 투영된 DynaFLIP feature 를 이
suffix hidden 에 **zero-init residual 로 가산**하는 것이 PVI 의 핵심 패턴입니다. `embed_suffix`
는 학습(`forward`, `modeling_pi05.py:737`)과 추론(`denoise_step`, `:867`) **두 경로가 공유**
하는 단일 지점이라, 여기 한 곳에 seam 을 두면 양쪽이 동시에 커버됩니다.

> **주입 위치 정정 (vs 초기 매핑).** 직전 매핑은 feature 를 `embed_prefix` 에 추가 토큰으로
> 넣었으나, [60] 본문은 주입을 **diffusion transformer hidden** 으로 명시합니다(prefix 아님).
> 본 매핑은 이를 반영해 expert-hidden zero-init residual 로 교체했습니다. zero-init 덕분에
> 주입을 켜도 *학습 시작 시점엔* 출력이 베이스와 정확히 동일(identity)하고, 학습이 진행되며
> residual 이 자라납니다 — PVI 의 zero-init 잔차 원리 그대로입니다.

**구현 형태 — subclass-seam (foundry §C-2).** in-place 재작성이 아니라, 베이스에 동작-보존
seam 두 개(expert-hidden 주입 hook + 모델 팩토리)를 두고, 신규 서브클래스 모듈
`modeling_pi05_dynaflip.py` + config `configuration_pi05_dynaflip.py` 로 기여를 더한 뒤
`pi05_dynaflip` 이름으로 등록합니다. config 플래그 `inject_dynaflip` 가 기본 `False` 라 서브
클래스가 없을 때(=주입 끔)는 베이스와 바이트 단위로 동일하게 동작합니다. 등록은 generic
resolver `_get_policy_cls_from_policy_name` (`factory.py:564`) 가 자동 처리하므로 `factory.py`
수정은 불필요합니다.

**SCOPE 선언.** 이 베이스가 COVER 하는 것과 EXCLUDE 하는 것:

- **COVER** — 다운스트림 PVI 주입 seam (frozen 보조 시각 feature → 액션 전문가 hidden 으로
  zero-init residual 투영·가산, Design §🔌 / analysis §3.4 / [60]).
- **EXCLUDE — DynaFLIP 사전학습 일체** (이미지·언어·3D flow 인코더, 심플렉스 정렬·TCN·actor
  손실, Eq. (1)–(7), 3D flow 데이터 파이프라인). Design §🧮~§📊 의 식·손실은 전부 *정책 루프
  밖의 별도 사전학습 stage* 이며(Design §🔌 명시) lerobot policy 좌표계 밖이라 제외합니다.
- **EXCLUDE — DynaFLIP 인코더 forward 자체.** feature 는 precompute 되어 batch 키
  `observation.dynaflip_feature` 로 공급된다고 가정합니다(아래 §🚧). 인코더 가중치는 공개
  체크포인트 `jlee-larr/dynaflip-base` 를 frozen 으로 별도 추론합니다.

---

## 🪛 변경 지점 매핑

| # | Foundry 위치 | 변경 종류 | Design 근거 | 요약 |
|---|--------------|-----------|-------------|------|
| 1 | `vendor/lerobot/policies/pi05/modeling_pi05.py:683` | 추가 (seam) | Design §🔌 / [60] | `PI05Pytorch._inject_expert_aux(suffix_embs)` hook 추가 — 기본 `suffix_embs` 그대로 반환(identity) |
| 2 | `vendor/lerobot/policies/pi05/modeling_pi05.py:737` | 수정 (seam) | Design §🔌 / [60] | `embed_suffix` 가 expert hidden 조립 직후 hook 을 1줄 호출 (base 는 무변화) |
| 3 | `vendor/lerobot/policies/pi05/modeling_pi05.py:921` | 수정 (seam) | foundry §C-2 | `PI05Policy.__init__` 의 모델 생성을 `self._build_model()` 팩토리로 추출 |
| 4 | `vendor/lerobot/policies/pi05/modeling_pi05.py:929` | 추가 (seam) | foundry §C-2 | `PI05Policy._build_model` 기본 구현 추가(`PI05Pytorch` 그대로 반환) |
| 5 | `vendor/lerobot/policies/pi05/configuration_pi05_dynaflip.py` | 신규 추가 | Design §📊, §🧮 | `PI05DynaflipConfig` — `inject_dynaflip`(기본 False)·`dynaflip_feature_dim=1536`·`dynaflip_feature_key` |
| 6 | `vendor/lerobot/policies/pi05/modeling_pi05_dynaflip.py` | 신규 추가 | Design §🔌 / analysis §3.4 / [60] | `DynaflipExpertInjector`(zero-init 투영) + `PI05DynaflipPytorch`(`_inject_expert_aux` override) + `PI05DynaflipPolicy`(`_build_model` override, batch feature stash) |
| 7 | `vendor/lerobot/policies/pi05/__init__.py:17` | 수정 | — | 신규 config/policy import 로 `register_subclass` 발화 보장 |

좌표는 pinned commit `999e77ad…` 스냅샷 기준이며 vendor refresh 시 함께 갱신됩니다.

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다.
아래는 가장 핵심적인 hunk(주입 seam) 의 인라인 발췌입니다 (전문 인용 금지 — 패치 파일이 정본).

```diff
--- a/vendor/lerobot/policies/pi05/modeling_pi05.py
+++ b/vendor/lerobot/policies/pi05/modeling_pi05.py
@@ class PI05Pytorch.embed_suffix
         att_masks = torch.tensor(att_masks, dtype=embs.dtype, device=embs.device)
         att_masks = att_masks[None, :].expand(bsize, len(att_masks))
 
+        # Seam: inject an auxiliary visual residual into the expert hidden
+        # states (PVI). Base returns embs unchanged -> identical to vanilla PI05.
+        embs = self._inject_expert_aux(embs)
+
         return embs, pad_masks, att_masks, adarms_cond
```

서브클래스 측 핵심(zero-init 잔차):

```python
def _inject_expert_aux(self, suffix_embs):          # PI05DynaflipPytorch
    if self.expert_injector is None or self._pending_dynaflip_feature is None:
        return suffix_embs
    feat = self._pending_dynaflip_feature
    if feat.dim() == 3:
        feat = feat.mean(dim=1)                      # (B,T,dim) -> (B,dim) 시간축 풀
    residual = self.expert_injector(feat.to(suffix_embs.dtype))  # zero-init Linear → (B, width)
    return suffix_embs + residual[:, None, :]        # 모든 action 토큰에 잔차 가산
```

`git apply --check` 결과: **통과**. 실행 검증: foundry runtime(Python 3.12, lerobot @
pinned commit)에 `-p3 --directory=src/lerobot` 로 적용 후 sibling smoke test **9 passed**.
zero-init 잔차의 동작-보존을 직접 계측합니다 — `DynaflipExpertInjector` 출력이 초기화 직후
정확히 0(`count_nonzero == 0`), 가중치 섭동 후 비0.

---

## 🧪 실무 구현 주의

- **외부 의존성** — DynaFLIP 시각 백본 가중치 `jlee-larr/dynaflip-base` (Hugging Face)
  를 frozen 으로 별도 추론합니다. PaliGemma/SigLIP 백본(`google/paligemma-…`)은 pi05 기존
  의존 그대로입니다.
- **데이터셋** — 주입 경로는 batch 에 `observation.dynaflip_feature` 키(shape `(B, 1536)`
  또는 `(B, T, 1536)`, 후자는 시간축 평균풀)를 요구합니다. DynaFLIP 인코더로 미리 계산해
  LeRobotDataset 에 보조 feature 로 동봉하거나 dataloader collate 단계에서 주입해야 합니다.
- **학습 하이퍼파라미터** — prior 보존을 위해 `freeze_vision_encoder=true`(+ 필요 시
  `train_expert_only`)로 SigLIP·VLM 을 frozen 하고, 학습 대상은 `expert_injector`(zero-init
  투영) + 액션 전문가로 한정하는 것이 [60] PVI 의 학습 분리(frozen main / trainable injector)
  그대로입니다. `inject_dynaflip=true` 로 켜고 `dynaflip_feature_dim` 을 데이터에 맞춥니다.
- **평가 / 추론** — 주입은 `embed_suffix` 안에서 일어나므로 `forward`(학습)·`denoise_step`
  (`sample_actions` 추론) 두 경로에 자동 적용됩니다 — seam 이 한 곳뿐이라 경로 간 불일치
  위험이 없습니다. 추론 시점에도 같은 batch 키로 feature 를 공급해야 하며, 전이(transition)
  입력을 쓰려면 과거 프레임 버퍼가 필요합니다(아래 §🚧).

---

## 🚧 미해결 / 잠정

- **PVI 충실도 — lightweight vs full copy-branch ([60] 확인 완료).** [60](arXiv:2603.12772)
  의 정식 PVI 는 *layer-wise* 구조입니다 — main DiT 를 frozen 한 채 학습 가능한 **copy-branch
  DiT**(사전학습 가중치 복제)를 보조 feature 로 조건화하고, 블록마다 zero-init Linear `Z_i` 로
  copy hidden 을 main 에 잔차 가산합니다($`h_i^{main}=f_i^{main}(\cdot)+Z_i(h_i^{copy})`$).
  반면 DynaFLIP §3.4 는 스스로 *"a **lightweight** visual-injection design **similar to** PVI"*
  라 적고 "project into the hidden feature space of the diffusion transformer" 로만 기술합니다.
  본 매핑은 DynaFLIP 의 lightweight 해석을 구현합니다 — **expert 입력 hidden(`embed_suffix`)
  단일 지점에 zero-init residual 1 개**. full layer-wise copy-branch 는 미구현이며, 그 이유는
  구조적입니다: lerobot 추론 경로(`denoise_step`)가 액션 전문가를 HF 의 fused
  `gemma_expert.model.forward` 로 통째 호출해 **per-layer hook 지점이 없어** 학습·추론 양쪽에
  깔끔히 layer-wise 주입을 넣을 수 없습니다. 두 경로가 공유하는 `embed_suffix` 입력단이
  유일하게 일관된 주입 지점입니다.
- **전이 시간 간격 $`H`$ 미명시.** DynaFLIP $`z_I`$ 는 두 프레임 차분이라 본래
  $`(I_t, I_{t+H})`$ 가 필요하나 $`H`$ 가 원문에 없습니다(Design §🚧). 본 매핑은 feature 를
  precompute 가정으로 우회하므로 policy 코드에서는 $`H`$ 가 드러나지 않습니다.
- **feature 공급 계약 (가정).** batch 키 `observation.dynaflip_feature` 는 본 매핑이 둔
  계약이며 upstream lerobot 에 없는 키입니다. 데이터 파이프라인에서 채워야 합니다.
- **DynaFLIP 사전학습 stage 전체는 out-of-base-scope** — 심플렉스 정렬·TCN·actor 손실·3D
  flow 인코더(Eq. (1)–(7))는 policy 좌표계 밖이라 본 패치에 포함되지 않습니다(§🧱 SCOPE).
