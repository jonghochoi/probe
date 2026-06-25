# Implementation Guide — Dexterous Point Policy on `lerobot`

> PROBE foundry 모드 산출물 (Layer 2, foundry-specific). 한글 단일
> 문서이며, sibling Design (`analysis/2606.10614/design.md`) 을 입력으로
> 받아 `lerobot` 의 좌표계 위에서 변경 지점을 매핑합니다. 형식·이모지
> ·용어 규칙은 `docs/STYLE.md` §6 / §4 를 따릅니다.
> 재실행 시 이 파일과 sibling `impl.patch` 를 덮어씁니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 | Dexterous Point Policy: Learning Point-based Dexterous Hand Policies from Human Demonstrations |
| 링크 | [arXiv:2606.10614](https://arxiv.org/abs/2606.10614) |
| 상위 Design | [`../../design.md`](../../design.md) |
| Foundry | `lerobot` |
| Foundry pinned commit | `3410b40275f31d6fa66345c99cf076d36991a313` (`vendor/lerobot/README.md` 와 일치) |
| 베이스 모델 / 코드 좌표 | `pi05` (`vendor/lerobot/policies/pi05/`) |
| 본문 확보 수준 | PDF 텍스트(PyMuPDF) |
| 패치 파일 | [`./impl.patch`](./impl.patch) — `git apply --check` 통과 |
| 실행 테스트 | [`./test_pi05_dpphand_smoke.py`](./test_pi05_dpphand_smoke.py) — 미실행 — 런타임 미가용 (오프라인 pure-logic self-check 17 assertion 통과, §🧪) |
| 가이드 생성일 | 2026-06-25 |

---

## 🧱 베이스 / 코드 좌표 식별

베이스는 `pi05`(`vendor/lerobot/policies/pi05/`) 입니다. DPP 는 정확히 대응하는
base 가 없는 신규 아키텍처(keypoint AR transformer + contact head)이고 Design
§🔌 도 pi0 계열을 잠정 후보로 들었지만, 사용자 요청에 따라 **pi05 좌표계로
grounding** 했습니다. 본 매핑의 초점은 사용자 최우선 관심사인 **"손을 어떻게
인코딩해 (사전)학습에 넣는가 — 즉 데이터셋이 어떻게 모델 입력 토큰이 되는가"**
입니다. 이 입력측 경로는 pi05 위에 깨끗이 올라갑니다: pi05 는 state 를 prompt 에
이산화해 넣고 **연속 state projector 를 제거**한 구조라(`_fix_pytorch_state_dict_keys`
의 `state_proj` skip), DPP 의 **연속 hand-keypoint projector 토큰** 을 prefix 에
다시 들이는 것이 자연스러운 seam 입니다.

구현 형태는 **subclass-seam** 입니다. base(`modeling_pi05.py`)에 동작-보존 seam
3곳을 추가하고, 신규 서브클래스 모듈/config/processor + 등록만으로 기여를
얹었습니다(off-by-default). 따라서 sibling smoke test 로 순수 모듈의 실행 검증이
가능합니다.

**SCOPE — COVER (이 매핑이 다루는 것):**

- **$`\phi_{hand}`$ 6-keypoint(18-dim) 인코딩 → prefix 손 토큰.** 6점(wrist +
  5 fingertip, 고정 index)을 18-dim 으로 concat 해 model 차원으로 사영하는
  입력측 손 인코딩. pi05 의 (제거된) 연속 state 토큰 자리에 대응 (paper §3.3).
- **$`\phi_{contact}`$ zero-init contact fusion (fine-tuning).** binary 5-vector
  를 2-layer MLP 로 사영해 손 토큰에 가산, 마지막 linear zero-init 으로 시작
  시점 prior 비교란 (paper §3.3).
- **$`\psi_{ct}`$ contact head + Eq.(2) 복합손실 + backbone stop-gradient.**
  action-expert hidden 에서 손끝별 contact logit 예측, $`\mathcal{L}_{ct}`$ 의
  gradient 를 backbone 에서 차단.
- **데이터 계약 처리 step.** 6점 → 18-dim 변환 + contact 5-vector 검증
  (`processor_pi05_dpphand.py`) — "데이터셋이 어떻게 모델 입력이 되는가" 의
  구체 좌표.

**SCOPE — EXCLUDE (base 좌표계 밖, 제외 사유):**

- **Autoregressive keypoint rollout** — pi05 는 flow-matching 으로 action chunk
  를 **병렬** 디코딩합니다. step 단위 AR 디코더로 교체하는 것은 backbone 전면
  재작성이라 base 좌표계 밖.
- **keypoint 궤적 출력 head ($`\mathbb{R}^{6\times 3}`$)** — base 의 flow-matching
  action(`action_out_proj`)을 디코더로 **유지**합니다. 출력 표현을 keypoint 직접
  회귀로 바꾸는 것은 제외 (contact head 는 보조 head 로만 추가).
- **PointNet object geometry 토큰 + semantic 토큰 + SAM3/VLM/Depth 추출** — pi05
  의 관찰은 이미지이며 점 토큰의 importable surface 가 없습니다. 비전 파이프라인
  신규 구현 영역.
- **IK / contact-force injection 배포 루프** — 로봇 URDF·하드웨어측이라 foundry
  좌표가 없습니다 (Design §🧰 `deploy_step`).

---

## 🪛 변경 지점 매핑

| # | Foundry 위치 | 변경 종류 | Design 근거 | 요약 |
|---|--------------|-----------|-------------|------|
| 1 | `vendor/lerobot/policies/pi05/modeling_pi05.py:653–693` (`PI05Pytorch.embed_prefix`) | 수정(seam) | Design §🧰 `policy_forward`, paper §3.3 | prefix concat 직전 `_extra_prefix_tokens` hook 호출 — 손 토큰 append 지점 (동작 보존: 기본 None) |
| 2 | `vendor/lerobot/policies/pi05/modeling_pi05.py:~740` (`embed_suffix` 직후) | 추가(seam) | Design §🧰 | base hook `_extra_prefix_tokens` + `_suffix_hook` 정의 (둘 다 None 반환) |
| 3 | `vendor/lerobot/policies/pi05/modeling_pi05.py:~782` (`PI05Pytorch.forward`) | 수정(seam) | Design §🧰 `contact_head` | `suffix_out` 산출 직후 `_suffix_hook(suffix_out)` 호출 — contact head 입력 노출 |
| 4 | `vendor/lerobot/policies/pi05/modeling_pi05.py:933` (`PI05Policy.__init__`) | 수정(seam) | Design §🧰 | `PI05Pytorch(...)` → `self._build_model(config)` factory 경유 |
| 5 | `vendor/lerobot/policies/pi05/modeling_pi05.py:~941` (`PI05Policy`) | 추가(seam) | Design §🧰 | `_build_model` factory 메서드 (서브클래스가 코어 모델 교체) |
| 6 | `vendor/lerobot/policies/pi05/configuration_pi05_dpphand.py` | 신규 | Design §📊, paper §3.3 | `PI05DPPHandConfig(PI05Config)` — hand/contact 필드 + 검증, `"pi05_dpphand"` 등록 |
| 7 | `vendor/lerobot/policies/pi05/modeling_pi05_dpphand.py` | 신규 | Design §🧰, Eq.(1)(2) | `HandKeypointEncoder`($`\phi_{hand}`$/$`\phi_{contact}`$), `ContactHead`($`\psi_{ct}`$), 복합손실, 서브클래스 model/policy |
| 8 | `vendor/lerobot/policies/pi05/processor_pi05_dpphand.py` | 신규 | Design 데이터 계약, paper §3.2 | 6점→18-dim 데이터 계약 step + contact 검증 + processor factory |
| 9 | `vendor/lerobot/policies/pi05/__init__.py:17–21` | 수정 | — | 신규 심볼 export(→ config 등록 트리거) |
| 10 | `vendor/lerobot/policies/factory.py:55, ~376` | 수정 | — | `PI05DPPHandConfig` import + processor isinstance 분기(PI05Config 분기보다 **앞**) |

> 좌표는 pinned commit `3410b40` 기준이며 foundry refresh 시 함께 갱신됩니다.
> 정책/config 해석은 factory 의 generic resolver(`_get_policy_cls_from_policy_name`)
> 가 `pi05_dpphand` 를 자동 처리하므로 `get_policy_class`/`make_policy_config` 에는
> 손대지 않았습니다 — processor 라우팅만 분기가 필요(서브클래스가 부모
> `PI05Config` isinstance 에 먼저 걸리는 것을 막기 위함).

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다. 아래는 핵심 hunk 발췌입니다 (정본은 패치 파일).

**(1) 입력측 손 인코딩 seam — pi05 prefix 에 손 토큰을 들이는 지점:**

```diff
--- a/vendor/lerobot/policies/pi05/modeling_pi05.py
+++ b/vendor/lerobot/policies/pi05/modeling_pi05.py
@@ embed_prefix
         num_lang_embs = lang_emb.shape[1]
         att_masks += [0] * num_lang_embs
 
+        # DPP-hand seam: subclasses may append extra observation tokens
+        # (e.g. a hand-keypoint token) before the prefix is concatenated.
+        extra = self._extra_prefix_tokens(lang_emb)
+        if extra is not None:
+            extra_embs, extra_pad, extra_att = extra
+            embs.append(extra_embs)
+            pad_masks.append(extra_pad)
+            att_masks += extra_att
+
         embs = torch.cat(embs, dim=1)
```

**(2) $`\phi_{hand}`$ / $`\phi_{contact}`$ — 데이터(18-dim 손 벡터)가 토큰이 되는 모듈:**

```python
class HandKeypointEncoder(nn.Module):
    # phi_hand: 18 -> hidden -> width  (6 keypoints x 3D, 고정 index)
    # phi_contact: 5 -> hidden -> width, 마지막 linear zero-init
    def forward(self, hand_keypoints, contact=None):
        hand = hand_keypoints.reshape(hand_keypoints.shape[0], -1)   # (B,18)
        token = self.hand_proj(hand)
        if self.use_contact and contact is not None:
            token = token + self.contact_proj(contact)              # zero-init → 시작 시 0
        return token
```

`git apply --check` 결과: **통과**

---

## 🧪 실무 구현 주의

- **외부 의존성** — base 는 `google/paligemma-3b-pt-224` 다운로드 필요. DPP 의
  나머지 외부 모델(Sentence-BERT, PointNet, SAM3, Qwen3.5-VL, Depth-Anything-3,
  HaWoR)은 모두 **데이터 파이프라인측**이며 본 매핑의 base scope 밖(§🧱 EXCLUDE).
- **데이터셋(데이터 계약)** — LeRobotDataset 에 두 feature 를 추가합니다.
  `observation.hand_keypoints` (paper §3.2: 6점 × 3D, world frame, depth-lift,
  고정 index `(wrist, thumb, index, middle, ring, pinky)`); fine-tuning 시
  `observation.contact` (binary 5-vector, index `[thumb, index, middle, ring,
  pinky]`). 사전학습 corpus(VITRA)는 contact 가 없으므로 `use_contact_channel=
  False` 가 기본. `Pi05DPPHandKeypointProcessorStep` 이 6점을 18-dim 으로 펴고
  contact 를 검증해 모델 입력으로 전달합니다 (pipeline 의 batch-dim step 직후 삽입).
- **정규화** — paper 는 keypoint 정규화 통계를 명시하지 않습니다. 데이터 계약
  step 은 **무정규화**(world-frame metric 좌표 그대로)이며, pi05 의
  `NormalizerProcessorStep` 는 `hand_keypoints` 가 `input_features` 에 없으므로
  건드리지 않습니다 (§🚧).
- **학습 하이퍼파라미터(paper §A vs pi05 기본값)** — DPP: AdamW, lr `1e-4`,
  weight decay `1e-4`, global batch `256`, 사전학습 `100k` / fine-tuning `400k`
  step, bf16(fwd/loss)+fp32(opt), grad clip `‖g‖≤1`, $`H=16`$, $`\lambda=1`$.
  pi05 기본값은 lr `2.5e-5`, `chunk_size=50` 등이라 학습 config 에서 override
  필요. **주의: pi05 의 main action loss 는 flow-matching MSE 이며 DPP 의 L1
  keypoint loss(Eq.1)가 아닙니다** — 본 매핑은 Eq.(2)의 **복합 구조**(main +
  $`\lambda \cdot \mathcal{L}_{ct}`$, backbone stop-gradient)만 이식하고
  L1·keypoint 출력은 제외(§🧱).
- **$`w_+`$ (contact_pos_weight)** — paper §3.3 는 "positive-class weight" 만
  언급하고 값을 주지 않아 default `1.0` (paper-silent, §🚧).
- **정밀도** — `hand_encoder`/`contact_head` 파라미터는 super().__init__ 이후
  생성되어 float32 로 남습니다(pi05 가 vision/projector/layernorm 을 float32 로
  유지하는 mixed-precision 관례와 일관). 손 토큰은 append 시 prefix dtype 으로
  캐스팅됩니다. bf16 학습 시 optimizer "same dtype" 처리는 검증 필요(§🚧).
- **추론** — `PI05DPPHandPolicy.forward`/`predict_action_chunk` 가 batch 에서 손
  키포인트·contact 를 꺼내 모델에 stash 후 base 경로를 호출합니다. contact head
  출력의 sigmoid→threshold→grip offset(IK/force injection)은 배포측이라 제외.
- **오프라인 self-check (정직성 기록)** — foundry runtime 클론이 org-policy 로
  차단(GitHub→out-of-scope 미러 403)되어 **공식 smoke test 는 미실행**입니다.
  대신 순수 모듈(encoder/head/loss + 데이터 계약 함수)을 lerobot 의존성 없이
  복제해 17개 assertion 을 오프라인 통과시켰습니다: $`\phi_{contact}`$ zero-init
  불변식(contact 융합 토큰 == 비융합 토큰), stop-gradient(detach 시 backbone
  grad None), $`\lambda=0`$ 시 복합손실 == main loss, 18-dim/contact 형상 검증.
  정적 검증으로는 `git apply --check` 통과 + 6개 파일 `py_compile` 통과가 함께
  성립합니다.

---

## 🚧 미해결 / 잠정

- **실행 테스트 미실행** — `.foundry-runtime/lerobot` 빌드가 org-policy 차단으로
  실패(`huggingface/lerobot` 클론 → 세션 스코프 밖 미러 403, 재시도 금지). 따라서
  메타의 `실행 테스트` 는 `미실행 — 런타임 미가용`. 정적 근거: §🧪 의 self-check
  17 통과 + `git apply --check` 통과 + `py_compile` OK.
- **base scope 밖 제외 항목** — AR rollout, keypoint 직접 회귀 출력 head,
  PointNet object 토큰, IK·force injection 은 §🧱 EXCLUDE 로 분류. 본 매핑은
  **입력측 손 인코딩 + contact 채널**에 한정합니다 (DPP 전체 알고리즘의 부분
  매핑임을 명시).
- **keypoint 정규화 통계** — paper 미명시 → 데이터 계약 step 무정규화.
- **$`\phi_{hand}`$ MLP depth/width** — paper 는 "a hand projector" 로만 기술 →
  default 2-layer(hidden `1024`).
- **$`w_+`$ 값** — paper 미명시 → default `1.0`.
- **bf16 학습 시 hand_encoder/contact_head 파라미터 dtype** — 현재 float32 유지;
  대규모 학습에서 optimizer dtype 일관성 검증 필요.
