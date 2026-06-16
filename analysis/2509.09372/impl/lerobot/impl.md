# Implementation Guide — VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model on `lerobot`

> PROBE foundry 모드 산출물 (Layer 2, foundry-specific). 한글 단일
> 문서이며, sibling Design (`analysis/2509.09372/design.md`) 의 핵심 메커니즘
> (Bridge Attention) 을 `lerobot` 의 `pi05` 좌표계 위에서 매핑합니다.
> 형식·이모지·용어 규칙은 `docs/STYLE.md` §6 / §4 를 따릅니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 | VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model |
| 링크 | [arXiv:2509.09372](https://arxiv.org/abs/2509.09372) |
| 상위 Design | [`../design.md`](../design.md) |
| Foundry | `lerobot` |
| Foundry pinned commit | `3410b40275f31d6fa66345c99cf076d36991a313` (`vendor/lerobot/README.md` 와 일치) |
| 베이스 모델 / 코드 좌표 | `pi05` (PaliGemma prefix + Gemma-300m flow-matching action expert) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 패치 파일 | [`./impl.patch`](./impl.patch) — `git apply --check` 통과 |
| 실행 테스트 | [`./test_pi05_bridge_smoke.py`](./test_pi05_bridge_smoke.py) — 미실행 (런타임 미가용; `/validate-impl §🧬` 에서 실행) |
| 가이드 생성일 | 2026-06-16 |

> ⚠️ 이 가이드는 Design 전체가 아니라 **Bridge Attention 의 게이팅 부분만**
> 옮긴 **게이트 전용(gate-only)** 이식입니다. Design 의 원본 아키텍처(Qwen-VLM
> 백본 + 별도 `MLPResNet` policy, 층별 Raw/ActionQuery 주입, proprio adapter
> 스트림)는 pi0.5 의 native dual-tower attention 으로 **재해석**되었고, 나머지는
> §🚧 의 남은 작업 목록으로 둡니다.

---

## 🧱 베이스 / 코드 좌표 식별

베이스는 `vendor/lerobot/policies/pi05/` 입니다. Design §🧰 `bridge_attention`
의 본질은 action 쿼리가 조건 스트림(Raw/ActionQuery)에 attend 할 때 학습형
스칼라 `tanh(g)` 로 그 기여를 조절하는 것이며(원본
`MLPResNetBlock`: `attn_scores_adapter * ratio_g`, `gating_factor` init 0),
pi0.5 는 이미 prefix(VL)와 suffix(action expert)를 **하나의 시퀀스로 concat**
해 통합 attention 을 수행합니다(`compute_layer_complete`,
`modeling_pi05.py`). 결합 시퀀스는 `[prefix(0:P); suffix(P:)]` 순서이므로,
살아있는 cross 블록은 **suffix-query × prefix-key** =
`scores[:, :, P:, :P]` 한 곳입니다(prefix→suffix 는 prefix-LM 마스크로 이미
차단). 이 블록을 층별 `tanh(g_i)` 로 곱하는 것이 pi0.5 위의 Bridge 게이팅의
정확한 대응점입니다.

**구현 형태.** in-place 재작성이 아니라 subclass-seam 으로 매핑합니다. base
`modeling_pi05.py` 에 동작-보존 seam 4개(`_bridge_gate` 훅, `_build_paligemma_with_expert`,
`_build_model`, `compute_layer_complete` 의 선택 인자)를 추가하고, 신규
`configuration_pi05_bridge.py` / `modeling_pi05_bridge.py` + `__init__.py` export
로 `pi05_bridge` 정책을 등록합니다. `bridge_attention=False` 면 vanilla pi0.5
와 바이트 동일 동작이므로 origin-vs-bridge 는 config 플래그 하나입니다. 정책
class/이름은 `lerobot` 레지스트리 규약(`PI05BridgeConfig`/`PI05BridgePolicy`,
`modeling_pi05_bridge.py`)을 따르므로 `factory.py` 수정 없이 자동 해석되고,
프로세서도 `isinstance(cfg, PI05Config)` 분기로 pi05 프로세서를 재사용합니다.

**SCOPE.** COVER — pi0.5 action expert 의 prefix attention 게이팅(Bridge 의
게이트 성분). EXCLUDE — (1) 별도 `MLPResNet` policy 로의 expert 교체, (2) task vs
adapter 2-스트림 분리 가중, (3) 층별 Raw/ActionQuery 분리 주입, (4) proprio
adapter 스트림 — 모두 base 좌표계 밖의 대형 변경이라 §🚧 로 분리.

---

## 🪛 변경 지점 매핑

| # | Foundry 위치 | 변경 종류 | Design 근거 | 요약 |
|---|--------------|-----------|-------------|------|
| 1 | `vendor/lerobot/policies/pi05/modeling_pi05.py` (`compute_layer_complete` 직전) | 추가 | Design §🧰 `bridge_attention` | `gated_eager_attention` + `_repeat_kv` — suffix→prefix logit 블록을 softmax 전에 `tanh(g)` 로 곱 |
| 2 | `vendor/lerobot/policies/pi05/modeling_pi05.py` (`compute_layer_complete`) | 수정 | Design §🧰 | 선택 인자 `bridge_gate`/`prefix_len` 추가; `None` 이면 기존 eager 경로(동작 보존) |
| 3 | `vendor/lerobot/policies/pi05/modeling_pi05.py` (`PaliGemmaWithExpertModel.forward`) | 수정 | Design §🧰 | 레이어 루프 `enumerate` + `prefix_len` 계산 + `_bridge_gate(i)` 훅 전달 |
| 4 | `vendor/lerobot/policies/pi05/modeling_pi05.py` (`PaliGemmaWithExpertModel`) | 추가 | Design §🧰 | `_bridge_gate` 훅(base 는 `None`) |
| 5 | `vendor/lerobot/policies/pi05/modeling_pi05.py` (`PI05Pytorch`) | 추가 | — (seam) | `_build_paligemma_with_expert` seam |
| 6 | `vendor/lerobot/policies/pi05/modeling_pi05.py` (`PI05Policy`) | 추가 | — (seam) | `_build_model` seam |
| 7 | `vendor/lerobot/policies/pi05/configuration_pi05_bridge.py` | 신규 | Design §📊 | `PI05BridgeConfig`: `bridge_attention`, `bridge_gate_init` |
| 8 | `vendor/lerobot/policies/pi05/modeling_pi05_bridge.py` | 신규 | Design §🧰, §🧰 policy_forward | `PaliGemmaWithExpertModelBridge`(층별 게이트), `PI05BridgePytorch`(게이트-일관 추론), `PI05BridgePolicy` |
| 9 | `vendor/lerobot/policies/pi05/__init__.py` | 수정 | — | 신규 config/policy export |

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다. 아래는 핵심 hunk
2개 발췌입니다 (전문 인용 금지 — 패치 파일이 정본).

게이트 수식 — suffix($`P:`$)-query × prefix($`:P`$)-key logit 을 softmax 전에
$`g_i = \tanh(\text{param}_i)`$ 로 곱 (`scale[P:, :P] = g_i`):

```diff
+def gated_eager_attention(
+    module, query, key, value, attention_mask, scaling, gate, prefix_len, dropout: float = 0.0
+):
+    key_states = _repeat_kv(key, module.num_key_value_groups)
+    value_states = _repeat_kv(value, module.num_key_value_groups)
+    attn_weights = torch.matmul(query, key_states.transpose(2, 3)) * scaling
+    if prefix_len is not None and 0 < prefix_len < attn_weights.shape[-2]:
+        gate = gate.to(attn_weights.dtype)
+        scale = torch.ones(attn_weights.shape[-2], attn_weights.shape[-1], ...)
+        scale[prefix_len:, :prefix_len] = gate
+        attn_weights = attn_weights * scale
+    if attention_mask is not None:
+        attn_weights = attn_weights + attention_mask[:, :, :, : key_states.shape[-2]]
+    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query.dtype)
+    ...
```

학습 forward 는 위 게이트를 그대로 통과하지만, 추론은 pi0.5 의 KV-cache decode
(독립 expert forward — 게이트 우회)를 쓰지 않고 **임베딩된 prefix 만 캐시 후
융합 forward 재실행**해 학습/추론 게이팅을 일치시킵니다:

```diff
+    def _bridge_denoise_step(self, prefix_embs, prefix_pad_masks, prefix_att_masks, x_t, timestep):
+        suffix_embs, suffix_pad_masks, suffix_att_masks, adarms_cond = self.embed_suffix(x_t, timestep)
+        pad_masks = torch.cat([prefix_pad_masks, suffix_pad_masks], dim=1)
+        att_masks = torch.cat([prefix_att_masks, suffix_att_masks], dim=1)
+        att_2d_masks_4d = self._prepare_attention_masks_4d(make_att_2d_masks(pad_masks, att_masks))
+        (_, suffix_out), _ = self.paligemma_with_expert.forward(
+            attention_mask=att_2d_masks_4d, position_ids=..., past_key_values=None,
+            inputs_embeds=[prefix_embs, suffix_embs], use_cache=False, adarms_cond=[None, adarms_cond])
+        return self.action_out_proj(suffix_out[:, -self.config.chunk_size:].to(torch.float32))
```

`git apply --check` 결과: **통과** (pristine `vendor/lerobot/` 기준).

---

## 🧪 실무 구현 주의

- **외부 의존성** — pi0.5 와 동일. `transformers`(Gemma/PaliGemma) 필요;
  사전학습 가중치는 OpenPI 포팅 체크포인트(`PI05Policy.from_pretrained`).
- **데이터셋** — pi0.5 계약 그대로(LeRobotDataset, `chunk_size=50`, 상태/액션
  `QUANTILES` 정규화). 별도 변경 없음.
- **학습 하이퍼파라미터** — pi0.5 기본값 사용. 추가 학습 대상은 층당 스칼라
  게이트 1개(expert depth=18 → 18개)뿐. `bridge_gate_init=0.0` 이 기본(원본
  충실, init 시 브리지 무력화).
  - **warm-start 권장** — 사전학습 pi05 가중치에서 출발할 때는
    `bridge_gate_init≈4.0`(tanh≈0.999)로 두어 시작 시 vanilla pi0.5 와 거의
    동일하게 만든 뒤 게이트를 학습하게 하세요. `bridge_gates.*` 는 신규 키이므로
    `from_pretrained(..., strict=False)` 필요(잠정).
- **평가 / 추론** — `num_inference_steps`(기본 10) 만큼 융합 forward 가 재실행돼
  prefix 트랜스포머 층이 step 마다 재계산됩니다(SigLIP 비전 타워는 1회). 정확성
  우선의 연구용 경로이며, KV-cache 고속 경로는 §🚧.

---

## 🚧 미해결 / 잠정

- **KV-cache 고속 추론** — 현재 추론은 게이트 일관성을 위해 prefix 재계산. 독립
  expert decode 안에 동일 게이트를 적용하는 고속 경로는 미구현 (성능 전용,
  step-1 경로와의 출력 parity 가 합격 기준).
- **2-스트림 분리(task vs adapter)** — 원본의 self/task/adapter 3-스트림 가중
  (task `*1`, adapter `*tanh(g)`)은 미구현. 현재는 prefix 전체를 단일 브리지
  블록으로 게이트.
- **층별 Raw + ActionQuery 분리 주입** — 원본의 "전 중간층" 주입 + 학습형
  ActionQuery 토큰 미구현(현재는 pi0.5 의 층별 공유 prefix 만 사용).
- **proprio adapter 스트림** — pi0.5 가 제거한 state 토큰을 adapter 스트림으로
  재추가하는 변형 미구현.
- **`MLPResNet` expert 교체** — Gemma 트랜스포머 expert 를 원본 `MLPResNet`
  브리지 head 로 통째 교체하는 최대 변경 미구현(별도 `expert_variant`).
- **RTC 재검증** — `rtc_config.enabled` end-to-end 동작은 seam 보존만 확인,
  실제 동작 미검증.
- **L1 vs flow-matching** — 원본은 L1 회귀, 본 이식은 pi0.5 의 flow matching 유지.
