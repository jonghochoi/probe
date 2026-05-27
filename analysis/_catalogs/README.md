# `_catalogs/` — Cross-paper lineage 카탈로그

> PROBE D19b "VLM backbone lineage choice" + D22 "Multi-embodiment
> pretraining data" 의 의사결정 근거 자료. 세 축의 enumeration 을
> 분리 관리하면서 cross-reference 규약으로 묶음. per-paper deep-dive
> (`analysis/<arxiv-id>/`) 와는 *목적이 다른* 자료이므로 별도 폴더.

---

## 1. 세 축의 정의

| 파일 | 무엇을 enumerate 하는가 | 무엇은 enumerate 하지 않는가 |
|---|---|---|
| [`vlm.md`](vlm.md) | open-weight VLM 후보 — *lineage 2-tuple 의 첫 항* | VLA (VLM 위에 action expert 쌓은 시스템), 데이터셋 |
| [`vla.md`](vla.md) | 랜드마크 VLA — `(VLM init) × (Further-pretrain corpus)` 매트릭스 | VLM 단일, 데이터셋 단일 (각 셀 값으로만 인용) |
| [`pretrain_data.md`](pretrain_data.md) | 멀티-임베디먼트 사전학습 데이터셋 — robot action / human video / mixed | 벤치마크 (LIBERO/CALVIN 등; 별도 처리 deferred) |

> *lineage 2-tuple* = `(initial weights) × (further-pretrain corpus)`. 한
> VLA 의 정체성은 *어떤 VLM 으로 시작했는지* + *그 위에 어떤 데이터로
> 추가 학습했는지* 두 항으로 정해진다. 단순 모델명("PaliGemma") 은 빈
> 껍데기 — π0 가 그 위에 OXE+π in-house 로 추가 학습한 게 *π0 의*
> lineage. 그래서 vlm.md / vla.md / pretrain_data.md 가 분리되어야 함.

---

## 2. 공통 컬럼 표준 (v0.2, 2026-05)

세 카탈로그가 공유하는 컬럼 어휘. *한 곳에서 정의하고 세 곳에서 동일하게
적용* 하기 위함.

### 2-1. License — 라이선스명 + 상용 마커

각 셀: `<라이선스 이름> <상용 마커>` 형태.

| 상용 마커 | 의미 | 예시 |
|---|---|---|
| ✅ | 상업용 가능 | `Apache-2.0 ✅` · `MIT ✅` · `CC-BY-4.0 ✅` · `Gemma ✅` |
| ✅¹ | 조건부 상업용 (700M MAU 미만 등; 표 하단 각주) | `Llama-2 ✅¹` · `Tongyi ✅¹` · `DeepSeek ✅¹` |
| ⚠️ | 특이 조건 (prohibited-use policy 등) | `Ego4D license ⚠️` |
| ❌ | 비상업용 | `CC-BY-NC-4.0 ❌` · `NVIDIA Research ❌` · `Closed ❌` |
| ❓ | 미확인 / 신규 release 대기 | `TBD ❓` |

### 2-2. Access — 다운로드 접근성 + 링크

각 셀: `<접근성 아이콘> <링크>` 형태.

| 아이콘 | 의미 |
|---|---|
| 🟢 | Open — 가입/승인 없이 다운로드 (HF public, GitHub, S3 public, 공식 project page 다운로드) |
| 🟠 | Gated — HF gating / 가입 / 약관 동의 필요 (Llama, Ego4D 류) |
| 🔴 | Closed — 다운로드 불가 (Google internal, Genesis AI 등) |
| ❓ | TBD — 미확인 또는 release 대기 |

링크 텍스트 prefix:

| Prefix | 가리키는 곳 | 예시 |
|---|---|---|
| `hf:org/name` | HuggingFace 모델 또는 데이터셋 | `[hf:rail-berkeley/bridge_v2](https://huggingface.co/datasets/rail-berkeley/bridge_v2)` |
| `gh:org/name` | GitHub 저장소 | `[gh:Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi)` |
| `web` | 공식 project page | `[web](https://droid-dataset.github.io/)` |
| `arXiv:XXXX.XXXXX` | arXiv (PROBE 표준; 변경 없음) | `[arXiv:2410.24164](https://arxiv.org/abs/2410.24164)` |

> HF 의 모델 vs 데이터셋 URL 은 prefix 가 다름 (`huggingface.co/<org>` vs
> `huggingface.co/datasets/<org>`). 링크 텍스트는 `hf:` 통일하고 URL 은
> 실제 경로 그대로 둠.

### 2-3. 데이터 유형 (pretrain_data.md 전용)

| 아이콘 | 의미 |
|---|---|
| 🤖 Robot action | robot 의 action 라벨이 포함된 실측/시뮬 데이터 |
| 👤 Human video | robot action 없음, 인간 손/몸 행동 비디오 (VLA pre-training prior 용) |
| 🔀 Mixed | 한 데이터셋 안에 robot + human 둘 다 (UniHand-2.0 등) |

### 2-4. Scan 표 + per-dataset 카드 (pretrain_data.md 전용)

`pretrain_data.md` 는 컬럼이 많아 평면 표만으로는 가독성이 떨어진다.
Cycle 5 부터 **상단 scan 표 + 하단 per-dataset `<details>` 카드** 하이브리드.

**Scan 표 (7 컬럼)** — 한 행 한 줄:

| 데이터셋 | License | Access | 데이터 유형 | 규모 | Source-check | 우선도 |

데이터셋 이름은 카드 anchor 로 점프하는 마크다운 링크 (`[OXE](#oxe)`).
규모는 한 셀에 가장 압축된 한 줄 (예: `~970k traj / 22 robots`, `100h ego`).

**Per-dataset 카드** — H3 헤더 + `<details><summary>` + H4 8개 sub-section:

```markdown
### <a id="oxe"></a>Open X-Embodiment (OXE)

<details>
<summary>22 robots × ~970k trajectories — gripper-only baseline</summary>

#### Observations
- cameras / proprio / tactile / language

#### Actions
- space / dimension / control rate / gripper-or-finger / bimanual

#### Embodiment
- arm DOF / hand DOF / wrist / mounting

#### Annotation
- NL instruction / task intent / episode segmentation / sub-task labels

#### Scale
- trajectories / hours / storage / collection period

#### Lineage 적층
- 어떤 VLA 들이 적층

#### Source check
- 🟢 verified: <필드>
- 🟡 partial: <필드>
- 🔴 unverified: <필드>
- ❓ needs-human: <필드>

#### Sources
- arXiv: [arXiv:XXXX.XXXXX]
- 공식: [hf:...] / [gh:...] / [web]

</details>
```

H4 sub-section 순서 고정. H4 헤더는 emoji 없음 (`docs/STYLE.md` H3-plain
규칙과 동일 톤). H4 set 은 카탈로그 별로 다름:

| 카탈로그 | H4 sub-section (순서 고정) |
|---|---|
| `pretrain_data.md` | Observations · Actions · Embodiment · Annotation · Scale · Lineage 적층 · Source check · Sources |
| `vla.md` | Architecture · Training data · Action representation · Inference · Eval · Open-weight · Source check · Sources |

`<details><summary>` 는 GitHub markdown 표준 — 클릭하면 펼쳐짐. summary
한 줄에 가장 압축된 자기소개. **펼치고 닫고 UI** 가 dense 한 카드를
*scan-vs-deep-dive* 두 surface 로 분리해 가독성을 회복.

> 현재 `vlm.md` 는 평면 표 유지 — 컬럼 수가 적고 셀당 정보량도 낮아
> 카드화 효익이 상대적으로 낮음. Source-check 컬럼만 도입 (Cycle 6).
> 후속 사이클에 카드화 재검토 가능.

### 2-5. Source-check 마커

각 셀이 얼마나 검증됐는지 명시. 카드의 `#### Source check` 절에 *어느
필드가 어느 레벨인지* 줄별로 나열.

| 아이콘 | 의미 |
|---|---|
| 🟢 verified | 직접 paper / HF card / 공식 README 에서 확인됨 |
| 🟡 partial | paper 에 명시되어 있으나 사이드 추정 포함, 또는 sub-dataset 별 변동을 통합 값으로 표현 |
| 🔴 unverified | 메모리 / 훈련 지식으로 채움 (네트워크 차단 등으로 소스 직접 확인 불가). 사용자가 다음 사이클에 검증 권장 |
| ❓ needs-human | 원본 source 에 명시 부재 — 사용자가 paper 직접 내려받아 확인 필요 |

#### Scan 마커는 *의사결정 4-필드* 기준

Scan 표 7번째 컬럼의 source-check 마커는 *카드 안의 모든 필드* 를 종합한
값이 **아니다**. 한 카탈로그의 *의사결정 핵심 4 필드* 의 검증 상태만
종합한 *전반* 마커다 — 카탈로그가 "이 entity 를 채택할까" 에 영향을 주는
필드만 본다.

| 카탈로그 | 의사결정 4-필드 |
|---|---|
| `pretrain_data.md` | License · Scale · 데이터 유형 · Lineage 적층 |
| `vla.md` (도입 시) | License · 총 파라미터 · VLM init · Open-weight |
| `vlm.md` (도입 시) | License · 파라미터 · Instruction-tuning corpus · Access |

**규칙**: 위 4 필드가 *모두* 🟢 → scan 🟢. 한 필드라도 🟡 → scan 🟡. 한
필드라도 🔴 → scan 🔴. ❓ 가 있으면 보수적으로 🔴.

카드 안 `#### Source check` 절의 *부차 필드* — 정확한 control rate, sub-
dataset 별 spec, 카메라 해상도 분포 등 — 의 🔴 / ❓ 는 **scan 마커에
영향 없음**. 부차 필드는 *적층 결정 후 구현 단계* 의 디테일이라 D22
의사결정 자체에는 관여하지 않는다. 단 카드 안에서 *이 카드 전체가
얼마나 검증됐는지* 의 내부 일관성 표시로는 의미를 유지한다.

> 즉, **scan 마커** = 의사결정 4-필드의 검증 상태 (decide-or-skip).
> **카드 source check 절** = 카드 안 모든 필드의 *세분화된* 검증 상태
> (이후 사이클의 cell-level ratchet 추적). 두 트랙이 분리됨을 명시해
> *4-필드는 verified 인데 부차 필드가 unverified* 한 자연스러운 상태를
> 정직하게 표현 가능하게 함.

---

## 3. Cross-reference 규칙

| 출발 위치 | 가리키는 위치 | 예시 |
|---|---|---|
| `vla.md` "VLM init" 컬럼 | `vlm.md` 의 같은 모델명 행 | `PaliGemma-2B` → `vlm.md` PaliGemma 행 |
| `vla.md` "Further-pretrain corpus" 컬럼 | `pretrain_data.md` 의 같은 데이터셋 행 | `OXE + π in-house mix` → `pretrain_data.md` OXE 행 |
| `pretrain_data.md` "lineage 적층" 컬럼 | `vla.md` 의 같은 VLA 행 | `π0, π0.5, OpenVLA` → `vla.md` 각 VLA 행 |
| `vlm.md` "PROBE D19b 후보 메모" 의 *"X init"* 토큰 | `vla.md` 의 X VLA 행 | `Xiaomi-Robotics-0 init` → `vla.md` Xiaomi-Robotics-0 행 |

> **추가/갱신 원칙**: 새 entity 를 한 카탈로그에 등재하면, 다른 두 카탈로그의
> 관련 셀도 *같은 commit* 에서 갱신. 예: 새 VLA 를 `vla.md` 에 추가하면 그
> VLA 가 쓰는 VLM 이 `vlm.md` 에 없을 때 `vlm.md` 에도 행 추가; 그 VLA 가
> 적층한 데이터셋의 `pretrain_data.md` 의 "lineage 적층" 셀에 그 VLA 명도
> 추가.

---

## 4. 신규 entity 의사결정 트리

> 사용자가 "X 정보 추가해줘" 라고 했을 때 어느 카탈로그(들) 인지 식별.

1. **X 가 *VLM 모델 자체* 인가** (vision + language 입력, language 출력;
   action expert 없음)?
   → `vlm.md` 에 행 추가.
2. **X 가 *VLA 시스템* 인가** (VLM + action expert; robot action 출력)?
   → `vla.md` 에 행 추가. + 그 VLA 의 VLM init 이 `vlm.md` 에 없으면
   `vlm.md` 에도 추가.
3. **X 가 *데이터셋* 인가** (학습용 trajectory / video / image corpus)?
   → `pretrain_data.md` 에 행 추가. 데이터 유형 (🤖 / 👤 / 🔀) 분류.
4. **X 가 *벤치마크* 인가** (LIBERO, CALVIN, RoboCasa, RoboTwin 2.0
   같은 평가 환경)?
   → 현 카탈로그 범위 *밖*. 향후 `_catalogs/benchmarks.md` 신설 검토
   (deferred). 지금은 vla.md 의 "Further-pretrain corpus" 셀 안에 인라인
   기재만 (예: VLA-Adapter 의 `LIBERO + CALVIN (adapter-only)`).
5. **X 가 *위 어디에도 속하지 않으면*** — 카탈로그 등재 대상이 아닐 가능성
   높음 (예: 일반 자연어 모델, 전통 컴퓨터 비전 모델). 등재 안 함.

---

## 5. 운영 절차

### 5-1. 단발 업데이트 (사용자 요청 기반)

사용자가 "X 논문/데이터셋 정보 정리해줘" 라고 했을 때:

1. §4 의사결정 트리로 어느 카탈로그(들) 인지 식별.
2. 해당 카탈로그의 표 헤더 schema 에 맞춰 셀 값 채움.
   - License: §2-1 마커 형식
   - Access: §2-2 아이콘 + 링크 prefix
   - (pretrain_data 만) 데이터 유형: §2-3
   - (pretrain_data 만) 카드 schema: §2-4 의 H4 8개 sub-section 모두 채움
3. Cross-reference 동기화 (§3) — 다른 카탈로그에서 이 entity 를 인용하는
   셀이 있으면 같이 갱신.
4. **Source-check 절 (§2-5) 채우기 필수** — 어느 필드가 paper-level
   검증됐는지 / 추정인지 / 사용자 확인 필요한지를 *반드시* 명시. 추정
   금지가 아니라 *추정임을 명시* 가 원칙. 모르는 것은 `❓ needs-human`
   으로 surface.
5. Commit: `docs(catalogs): add <entity-name> (<axis>)` 형태. 예:
   `docs(catalogs): add Gemini-Robotics-On-Device (vla)`.

### 5-2. 정기 재정렬 (quarterly rebalance)

세 카탈로그를 동시에 전수 점검:

1. **VLM**: 신규 release (Qwen4-VL, InternVL4 등) 행 추가, 라이선스
   변경 / open-weight 출시 반영, 행 정렬 (개발 우선도 또는 출시일).
2. **VLA**: 신규 landmark VLA 행 추가, `Open weights` 출시 시 ❓→🟢
   갱신, lineage 컬럼 정확도 재확인.
3. **Data**: 신규 데이터셋, hand-DOF 우선도 재계산, 라이선스 변경 반영,
   `lineage 적층` 컬럼에 새 VLA 들 추가.

Commit: `docs(catalogs): 2026-Qx rebalance` 형태. body 에 *추가/제거/
갱신* 행을 짧게 묶어서 기록.

---

## 6. 출처 정책 (3 카탈로그 공통)

- **1차**: arXiv 논문 (모델/시스템) 또는 dataset 공식 README (데이터).
- **2차**: HuggingFace model/dataset card.
- **3차**: 공식 GitHub README / project page.
- URL 은 *resolve 검증* 된 것만. 미확인 셀은 `❓` 또는 `TBD (이유)`.
- **arXiv ID 위조 금지** (`docs/STYLE.md` §3 의 PROBE 절대 원칙).
- 비상용 라이선스 (CC-BY-NC-*, NVIDIA Research, …) 는 §2-1 ❌ 마커로
  *항상* 명시.

---

## 7. 부록 — Cross-reference summary (수동 갱신)

`vlm.md` 모델별로 그 VLM 을 init 으로 쓰는 VLA 들을 역참조:

| VLM | 이 VLM 을 init 으로 쓴 VLA |
|---|---|
| PaliGemma / PaliGemma-2 | π0, π0.5, π0-FAST |
| Eagle-2 | GR00T N1, GR00T N1.5/N1.7 |
| Molmo (Molmo-7B-D) | MolmoAct (arXiv:2508.07917), MolmoAct2 (arXiv:2605.02881), MolmoBot (arXiv:2603.16861) |
| Llama-2-7B (+ DINOv2 + SigLIP) | OpenVLA |
| OpenVLA | PriorVLA |
| Qwen3-VL | Xiaomi-Robotics-0 |
| Gemma-3-12B-IT | VLM2VLA |
| Prismatic-VLM + Qwen2.5-0.5B | VLA-Adapter |
| (별도 VLM 없음) | Octo |

`pretrain_data.md` 데이터셋별로 그 데이터셋을 적층한 VLA 들을 역참조:

| 데이터셋 | 이 데이터셋을 적층한 VLA |
|---|---|
| OXE | π0, π0.5, π0-FAST, OpenVLA, Octo, GR00T N1, Xiaomi-Robotics-0 (부분) |
| BridgeData V2 | VLM2VLA, OpenVLA (부분) |
| DROID | Xiaomi-Robotics-0, OpenVLA fine-tune |
| AgiBot World | Genie Operator-1 (GO-1) |
| UniHand-2.0 | Being-H0.5 |
| MolmoAct Dataset (10k Franka traj / 93 tasks) | MolmoAct (arXiv:2508.07917) |
| MolmoAct2-BimanualYAM / -SO100/101 / DROID-MolmoAct2 | MolmoAct2 (arXiv:2605.02881) |
| MolmoBot-Data (1.7M sim + MolmoSpaces ecosystem) | MolmoBot (arXiv:2603.16861) |
| LIBERO + CALVIN | VLA-Adapter (adapter-only), PriorVLA |
| HOI4D / ARCTIC / OakInk / AssemblyHands / Assembly101 | (직접 적층 VLA 없음 — retarget 후보) |
| Ego4D / Ego-Exo4D / Epic Kitchens / EgoExoLearn / HoloAssist | (직접 적층 VLA 없음 — VLM/temporal/NL prior 후보) |

> 이 부록은 *수동 동기화* 대상. 카탈로그 행을 갱신할 때 같이 손봐야 함.
> Cycle 5+ 에서 `scripts/refresh-catalogs.py` 같은 형태로 자동화 검토.
