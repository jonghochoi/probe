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

**주입 구조 — PVI copy-branch ([60] + DynaFLIP appendix 충실 매핑).** DynaFLIP 의 VLA 통합은
[60] 의 4 요소를 그대로 따릅니다:

1. **보조 인코더** — DynaFLIP(frozen)이 카메라 뷰별 **패치 토큰 시퀀스**를 냅니다. 본 매핑은
   이를 precompute 해 batch 키 `observation.dynaflip_feature`(shape `(B, L, dim)`)로 받습니다.
2. **투영(zero-init)** — 패치 토큰을 액션 전문가 hidden 폭으로 사상하는 zero-init Linear
   (`aux_proj`).
3. **copy-branch** — 액션 전문가(`gemma_expert`)의 **학습 가능한 복사본**(`copy_expert`,
   사전학습 가중치로 초기화)이 `[aux 토큰 ; action 토큰]` 위에서 돌아 action 위치가 aux 를
   조건으로 attend 하고, 그 **layer 별 hidden** 을 포착합니다.
4. **layer-wise 주입(zero-init)** — 전문가 layer 마다 zero-init Linear `Z_i` 가 copy hidden 을
   main 전문가에 잔차 가산: $`h_i^{main} \mathrel{+}= Z_i(h_i^{copy})`$.

frozen: SigLIP·VLM·LLM·main 전문가·보조 인코더 / 학습: `aux_proj` + `copy_expert` + `Z_i`.
zero-init 투영·주입 덕분에 주입을 켜도 *학습 시작 시점엔* 정책이 베이스 $`\pi_{0.5}`$ 와
정확히 동일(identity)하고, 시각 신호가 학습으로 점진 활성화됩니다 — [60] 의 init 프로토콜
그대로입니다.

**두 주입 site (경로별 라우팅 차이 때문).** 베이스는 전문가를 경로마다 다르게 호출합니다 —
학습 joint forward 는 수동 per-layer 루프(`compute_layer_complete`)를, 추론 `denoise_step`
은 HF 의 fused `gemma_expert.model.forward` 를 씁니다. 그래서 layer-wise 주입을 두 곳에 답니다:
**학습**은 `PaliGemmaWithExpertModel.expert_layer_injector` 콜백 seam, **추론**은 main 전문가
layer 들에 건 forward hook. 각 경로는 정확히 한 메커니즘만 발화하므로 이중 주입이 없습니다.
copy-branch hidden 은 두 경로가 공유하는 `embed_suffix` override 에서 1 회 계산해 stash 합니다.

**구현 형태 — subclass-seam (foundry §C-2).** in-place 재작성이 아니라, 베이스에 동작-보존
seam(per-layer 주입 콜백 attr + 모델 팩토리)을 두고, 신규 서브클래스 모듈
`modeling_pi05_dynaflip.py` + config `configuration_pi05_dynaflip.py` 로 기여를 더한 뒤
`pi05_dynaflip` 이름으로 등록합니다. config 플래그 `inject_dynaflip` 가 기본 `False` 라 서브
클래스가 없을 때(=주입 끔)는 베이스와 바이트 단위로 동일하게 동작합니다. 등록은 generic
resolver `_get_policy_cls_from_policy_name` (`factory.py:564`) 가 자동 처리하므로 `factory.py`
수정은 불필요합니다.

**SCOPE 선언.** 이 베이스가 COVER 하는 것과 EXCLUDE 하는 것:

- **COVER** — 다운스트림 PVI copy-branch 주입 (frozen 보조 패치 토큰 → zero-init 투영 →
  copy-branch → layer-wise zero-init 잔차, Design §🔌 / analysis §3.4 / [60]).
- **EXCLUDE — DynaFLIP 사전학습 일체** (이미지·언어·3D flow 인코더, 심플렉스 정렬·TCN·actor
  손실, Eq. (1)–(7), 3D flow 데이터 파이프라인). Design §🧮~§📊 의 식·손실은 전부 *정책 루프
  밖의 별도 사전학습 stage* 이며(Design §🔌 명시) lerobot policy 좌표계 밖이라 제외합니다.
- **EXCLUDE — DynaFLIP 인코더 forward 자체.** 패치 토큰은 precompute 되어 batch 키
  `observation.dynaflip_feature` 로 공급된다고 가정합니다(아래 §🚧). 인코더 가중치는 공개
  체크포인트 `jlee-larr/dynaflip-base` 를 frozen 으로 별도 추론합니다.

---

## 🪛 변경 지점 매핑

| # | Foundry 위치 | 변경 종류 | Design 근거 | 요약 |
|---|--------------|-----------|-------------|------|
| 1 | `vendor/lerobot/policies/pi05/modeling_pi05.py` `PaliGemmaWithExpertModel.__init__` | 추가 (seam) | Design §🔌 / [60] | `self.expert_layer_injector = None` — per-layer 주입 콜백 attr(기본 None=무주입) |
| 2 | `vendor/lerobot/policies/pi05/modeling_pi05.py` `PaliGemmaWithExpertModel.forward` joint loop | 수정 (seam) | Design §🔌 / [60] | layer 마다 `compute_layer_complete` 직후 콜백 적용(None 이면 무변화) — 학습 경로 주입 site |
| 3 | `vendor/lerobot/policies/pi05/modeling_pi05.py` `PI05Policy.__init__` | 수정 (seam) | foundry §C-2 | 모델 생성을 `self._build_model()` 팩토리로 추출 |
| 4 | `vendor/lerobot/policies/pi05/modeling_pi05.py` `PI05Policy._build_model` | 추가 (seam) | foundry §C-2 | 기본 구현(`PI05Pytorch` 그대로 반환) |
| 5 | `vendor/lerobot/policies/pi05/configuration_pi05_dynaflip.py` | 신규 추가 | Design §📊, §🧮 | `PI05DynaflipConfig` — `inject_dynaflip`(기본 False)·`dynaflip_feature_dim=768`(패치 토큰 폭)·`dynaflip_feature_key` |
| 6 | `vendor/lerobot/policies/pi05/modeling_pi05_dynaflip.py` | 신규 추가 | Design §🔌 / analysis §3.4 / [60] | `zero_init_linear` + `PI05DynaflipPytorch`(`aux_proj`·`copy_expert`·`inject_layers`, `embed_suffix`/`_inject_expert_layer` override, 추론 forward hook) + `PI05DynaflipPolicy`(`_build_model` override, batch feature stash) |
| 7 | `vendor/lerobot/policies/pi05/__init__.py:17` | 수정 | — | 신규 config/policy import 로 `register_subclass` 발화 보장 |

좌표는 pinned commit `999e77ad…` 스냅샷 기준이며 vendor refresh 시 함께 갱신됩니다.

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다.
아래는 가장 핵심적인 hunk(주입 seam) 의 인라인 발췌입니다 (전문 인용 금지 — 패치 파일이 정본).

베이스 측 학습-경로 주입 seam (joint per-layer 루프):

```diff
--- a/vendor/lerobot/policies/pi05/modeling_pi05.py
+++ b/vendor/lerobot/policies/pi05/modeling_pi05.py
@@ class PaliGemmaWithExpertModel.forward (joint branch)
                     inputs_embeds = compute_layer_complete(
                         layer_idx, inputs_embeds, ... gemma_expert=self.gemma_expert,
                     )
 
+                # Seam: per-layer auxiliary residual injection into the expert
+                # (PVI copy-branch). Base injector is None -> identical to PI05.
+                if self.expert_layer_injector is not None:
+                    inputs_embeds = [
+                        inputs_embeds[0],
+                        self.expert_layer_injector(layer_idx, inputs_embeds[1]),
+                    ]
```

서브클래스 측 핵심(copy-branch 계산 + layer-wise zero-init 잔차):

```python
def _compute_copy_hidden(self, suffix_embs, adarms_cond):   # PI05DynaflipPytorch
    aux_emb = self.aux_proj(self._aux_tokens.to(suffix_embs.dtype))  # zero-init 투영
    full = torch.cat([aux_emb, suffix_embs], dim=1)                  # [aux ; action]
    self.copy_expert.model.forward(inputs_embeds=full, ...,          # 복사본 전문가
                                   adarms_cond=adarms_cond)          # capture hook 이 layer hidden 포착
    self._copy_hidden = [h[:, -chunk:] for h in self._copy_capture]  # action 위치만

def _inject_expert_layer(self, layer_idx, suffix_hidden):    # 학습 경로 콜백
    ch = self._copy_hidden[layer_idx]
    return suffix_hidden + self.inject_layers[layer_idx](ch)         # zero-init Z_i 잔차
# 추론 경로: main 전문가 layer 들에 건 forward hook 이 같은 Z_i(ch) 를 가산
```

`git apply --check` 결과: **통과**. 실행 검증: foundry runtime(Python 3.12, lerobot @
pinned commit)에 `-p3 --directory=src/lerobot` 로 적용 후 sibling smoke test **9 passed**.
zero-init 동작-보존을 직접 계측합니다 — `zero_init_linear` 출력이 초기화 직후 정확히
0(`count_nonzero == 0`), 가중치 섭동 후 비0. **단** copy-branch forward(attention·mask)와
per-layer 주입의 *수치* 정합은 가중치가 필요해 CPU smoke 범위 밖입니다(아래 §🚧 / foundry §G).

---

## 🧪 실무 구현 주의

- **외부 의존성** — DynaFLIP 시각 백본 가중치 `jlee-larr/dynaflip-base` (Hugging Face)
  를 frozen 으로 별도 추론합니다. PaliGemma/SigLIP 백본(`google/paligemma-…`)은 pi05 기존
  의존 그대로입니다.
- **데이터셋** — 주입 경로는 batch 에 `observation.dynaflip_feature` 키(shape `(B, L, dim)`,
  `L`=뷰×패치, `dim`=`dynaflip_feature_dim`=768)를 요구합니다. `(B, dim)` 단일 토큰도 허용
  (내부에서 `(B, 1, dim)` 으로 승격). DynaFLIP 인코더로 미리 계산해 LeRobotDataset 에 보조
  feature 로 동봉하거나 dataloader collate 단계에서 주입해야 합니다.
- **copy-branch 초기화** — `copy_expert` 는 build 시 `gemma_expert` 를 deepcopy 하고, **첫
  forward 에서 1 회** 현재(=로드된) main 전문가 가중치를 복사해 동기화합니다
  (`_maybe_sync_copy`). 즉 사전학습 $`\pi_{0.5}`$ 체크포인트를 로드한 *뒤* 첫 step 에서 copy 가
  pretrained 전문가로 초기화됩니다. copy 가중치를 담은 체크포인트에서 resume 한다면 이 lazy
  sync 를 꺼야 합니다(다운스트림에서 조정).
- **학습 하이퍼파라미터** — prior 보존을 위해 `freeze_vision_encoder=true`(+ 필요 시
  `train_expert_only`)로 SigLIP·VLM·main 전문가를 frozen 하고, 학습 대상은 `aux_proj` +
  `copy_expert` + `inject_layers` 로 한정하는 것이 [60] PVI 의 학습 분리 그대로입니다.
  `inject_dynaflip=true` 로 켜고 `dynaflip_feature_dim` 을 보조 인코더 패치 토큰 폭에 맞춥니다.
- **평가 / 추론** — copy-branch hidden 은 `embed_suffix` override 에서 계산되어 `forward`
  (학습)·`denoise_step`(추론) 두 경로에서 모두 채워지고, 학습은 콜백·추론은 forward hook 으로
  주입됩니다. 추론 시점에도 같은 batch 키로 패치 토큰을 공급해야 합니다.

---

## 🚧 미해결 / 잠정

- **검증 경계 (가중치 필요분).** weight-free CPU smoke 가 보장하는 것은 **구조·등록·zero-init
  잔차의 identity 성질**뿐입니다(9 passed). copy-branch 의 *수치* 동작 — `copy_expert` 의
  attention/mask 구성, per-layer 주입이 baseline rollout 을 zero-init 시점에 비트 단위로
  보존하는지 — 은 PaliGemma/gemma 가중치와 무거운 모델 build 가 필요해 CPU smoke 범위 밖입니다
  (foundry §G 계약과 동일하게, 백본 forward 는 원래 smoke 가 돌리지 않음). 다운스트림 weighted
  런타임에서 `inject_dynaflip` on/off 출력 동치(zero-init 시점)를 회귀 테스트로 확인하길 권장.
- **copy-branch 조건화 방식 (해석).** [60]·발췌는 copy-branch 가 보조 feature 를 조건으로 받되
  정확한 attention 형태(cross-attn k/v 치환 vs prefix self-attn)를 수치까지 못박지 않습니다.
  본 매핑은 `[aux 토큰 ; action 토큰]` 한 시퀀스의 prefix-self-attention 으로 구현했습니다 —
  action 위치가 aux 를 bidirectional prefix 로 attend. cross-attn 변형은 미채택.
- **다중 뷰 패치 토큰 집계 (가정).** 발췌는 뷰별(third-person·wrist) 패치 토큰을 말하나 집계
  규칙은 미명시입니다. 본 매핑은 뷰·패치를 한 축 `L` 로 flatten 해 batch 키로 받는다고 가정.
- **전이 시간 간격 $`H`$ 미명시.** DynaFLIP $`z_I`$ 는 두 프레임 차분이라 본래
  $`(I_t, I_{t+H})`$ 가 필요하나 $`H`$ 가 원문에 없습니다(Design §🚧). 본 매핑은 패치 토큰을
  precompute 가정으로 우회하므로 policy 코드에서는 $`H`$ 가 드러나지 않습니다.
- **feature 공급 계약 (가정).** batch 키 `observation.dynaflip_feature` 는 본 매핑이 둔
  계약이며 upstream lerobot 에 없는 키입니다. 데이터 파이프라인에서 채워야 합니다.
- **DynaFLIP 사전학습 stage 전체는 out-of-base-scope** — 심플렉스 정렬·TCN·actor 손실·3D
  flow 인코더(Eq. (1)–(7))는 policy 좌표계 밖이라 본 패치에 포함되지 않습니다(§🧱 SCOPE).
