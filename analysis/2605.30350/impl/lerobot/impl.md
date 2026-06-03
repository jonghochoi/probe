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
| 본문 확보 수준 | 전문(arXiv HTML) |
| 패치 파일 | [`./impl.patch`](./impl.patch) — `git apply --check` 통과 |
| 실행 테스트 | [`./test_pi05_dynaflip_smoke.py`](./test_pi05_dynaflip_smoke.py) — 7 passed |
| 가이드 생성일 | 2026-06-03 |

---

## 🧱 베이스 / 코드 좌표 식별

베이스는 `pi05` (`vendor/lerobot/policies/pi05/modeling_pi05.py`) 입니다. DynaFLIP 의
다운스트림 통합은 논문이 직접 $`\pi_{0.5}`$ 에 **PVI(Plug-in Visual Injection)** 로 동역학
인식 시각 가지를 주입하는 것이며(Design §🔌 foundry 힌트, analysis §3.4), `pi05` 는 PaliGemma
+ flow-matching 액션 전문가 구조라 이 주입 대상과 1:1 로 대응합니다. 핵심 주입 지점은
`PI05Pytorch.embed_prefix` (`modeling_pi05.py:641`) 로, 여기서 SigLIP 이미지 토큰과 언어
토큰이 prefix 로 조립됩니다 — 투영된 DynaFLIP feature 를 이 prefix 에 추가 토큰으로 덧붙이는
것이 표준 PVI 패턴입니다.

**구현 형태 — subclass-seam (foundry §C-2).** in-place 재작성이 아니라, 베이스에 동작-보존
seam 두 개(prefix 토큰 hook + 모델 팩토리)를 두고, 신규 서브클래스 모듈
`modeling_pi05_dynaflip.py` + config `configuration_pi05_dynaflip.py` 로 기여를 더한 뒤
`pi05_dynaflip` 이름으로 등록합니다. config 플래그 `inject_dynaflip` 가 기본 `False` 라 서브
클래스가 없을 때(=주입 끔)는 베이스와 바이트 단위로 동일하게 동작합니다. 등록은 generic
resolver `_get_policy_cls_from_policy_name` (`factory.py:564`) 가 자동 처리하므로 `factory.py`
수정은 불필요합니다.

**SCOPE 선언.** 이 베이스가 COVER 하는 것과 EXCLUDE 하는 것:

- **COVER** — 다운스트림 PVI 주입 seam (frozen 보조 시각 feature → prefix 토큰 투영·삽입,
  Design §🔌 / analysis §3.4).
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
| 1 | `vendor/lerobot/policies/pi05/modeling_pi05.py:640` | 추가 (seam) | Design §🔌 | `PI05Pytorch._extra_prefix_embeds` hook 추가 — 기본 `None` 반환(동작 보존) |
| 2 | `vendor/lerobot/policies/pi05/modeling_pi05.py:672` | 수정 (seam) | Design §🔌 | `embed_prefix` 가 hook 결과를 prefix 토큰·마스크에 append (None 이면 무변화) |
| 3 | `vendor/lerobot/policies/pi05/modeling_pi05.py:921` | 수정 (seam) | foundry §C-2 | `PI05Policy.__init__` 의 모델 생성을 `self._build_model()` 팩토리로 추출 |
| 4 | `vendor/lerobot/policies/pi05/modeling_pi05.py:929` | 추가 (seam) | foundry §C-2 | `PI05Policy._build_model` 기본 구현 추가(`PI05Pytorch` 그대로 반환) |
| 5 | `vendor/lerobot/policies/pi05/configuration_pi05_dynaflip.py` | 신규 추가 | Design §📊, §🧮 | `PI05DynaflipConfig` — `inject_dynaflip`(기본 False)·`dynaflip_feature_dim=1536`·`dynaflip_num_tokens=1` |
| 6 | `vendor/lerobot/policies/pi05/modeling_pi05_dynaflip.py` | 신규 추가 | Design §🔌 / analysis §3.4 | `DynaflipPrefixInjector`(투영) + `PI05DynaflipPytorch`(hook override) + `PI05DynaflipPolicy`(`_build_model` override, batch feature stash) |
| 7 | `vendor/lerobot/policies/pi05/__init__.py:17` | 수정 | — | 신규 config/policy import 로 `register_subclass` 발화 보장 |

좌표는 pinned commit `999e77ad…` 스냅샷 기준이며 vendor refresh 시 함께 갱신됩니다.

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다.
아래는 가장 핵심적인 hunk(주입 seam) 의 인라인 발췌입니다 (전문 인용 금지 — 패치 파일이 정본).

```diff
--- a/vendor/lerobot/policies/pi05/modeling_pi05.py
+++ b/vendor/lerobot/policies/pi05/modeling_pi05.py
@@ class PI05Pytorch.embed_prefix
         num_lang_embs = lang_emb.shape[1]
         att_masks += [0] * num_lang_embs
 
+        # Seam: subclasses may append auxiliary prefix tokens (e.g. DynaFLIP
+        # PVI injection). Base ``_extra_prefix_embeds`` returns None -> identical.
+        extra = self._extra_prefix_embeds()
+        if extra is not None:
+            extra_embs, extra_mask = extra
+            embs.append(extra_embs.to(embs[0].dtype))
+            pad_masks.append(extra_mask)
+            att_masks += [0] * extra_embs.shape[1]
+
         embs = torch.cat(embs, dim=1)
```

`git apply --check` 결과: **통과**. 실행 검증: foundry runtime(Python 3.12, lerobot @
pinned commit)에 `-p3 --directory=src/lerobot` 로 적용 후 sibling smoke test **7 passed**.

---

## 🧪 실무 구현 주의

- **외부 의존성** — DynaFLIP 시각 백본 가중치 `jlee-larr/dynaflip-base` (Hugging Face)
  를 frozen 으로 별도 추론합니다. PaliGemma/SigLIP 백본(`google/paligemma-…`)은 pi05 기존
  의존 그대로입니다.
- **데이터셋** — 주입 경로는 batch 에 `observation.dynaflip_feature` 키(shape `(B, 1536)`
  또는 `(B, T, 1536)`, 후자는 시간축 평균풀)를 요구합니다. DynaFLIP 인코더로 미리 계산해
  LeRobotDataset 에 보조 feature 로 동봉하거나 dataloader collate 단계에서 주입해야 합니다.
- **학습 하이퍼파라미터** — prior 보존을 위해 `freeze_vision_encoder=true`(+ 필요 시
  `train_expert_only`)로 SigLIP·VLM 을 frozen 하고, 학습 대상은 `injector`(투영) + 액션
  전문가/projection 으로 한정하는 것이 논문의 PVI 정신입니다. `inject_dynaflip=true` 로 켜고
  `dynaflip_feature_dim`/`dynaflip_num_tokens` 를 데이터에 맞춥니다.
- **평가 / 추론** — 주입 토큰은 prefix att-mask 0(양방향)으로 들어가 `sample_actions`
  inference 경로에도 동일 적용됩니다. 추론 시점에도 같은 batch 키로 feature 를 공급해야
  하며, 전이(transition) 입력을 쓰려면 과거 프레임 버퍼가 필요합니다(아래 §🚧).

---

## 🚧 미해결 / 잠정

- **PVI injection 모듈 세부 구조 (paper-silent).** 논문은 injection 모듈의 projection
  차원·주입 layer 를 ref [60] 로 위임합니다(Design §🚧). 본 매핑은 가장 단순·동작-보존적인
  해석 — prefix 입력단에 단일 Linear 투영 토큰 삽입 — 을 채택했습니다. 특정 transformer
  layer hidden 에 주입하는 변형은 미구현(🪛 seam 만 제공).
- **주입 토큰 수 `dynaflip_num_tokens` 기본 1 (잠정).** pooled 전이 임베딩 $`z_I`$ 1 개를
  기본으로 두었습니다 — 본문 미명시.
- **전이 시간 간격 $`H`$ 미명시.** DynaFLIP $`z_I`$ 는 두 프레임 차분이라 본래
  $`(I_t, I_{t+H})`$ 가 필요하나 $`H`$ 가 원문에 없습니다(Design §🚧). 본 매핑은 feature 를
  precompute 가정으로 우회하므로 policy 코드에서는 $`H`$ 가 드러나지 않습니다.
- **feature 공급 계약 (가정).** batch 키 `observation.dynaflip_feature` 는 본 매핑이 둔
  계약이며 upstream lerobot 에 없는 키입니다. 데이터 파이프라인에서 채워야 합니다.
- **DynaFLIP 사전학습 stage 전체는 out-of-base-scope** — 심플렉스 정렬·TCN·actor 손실·3D
  flow 인코더(Eq. (1)–(7))는 policy 좌표계 밖이라 본 패치에 포함되지 않습니다(§🧱 SCOPE).
