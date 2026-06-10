# Design — Actions as Language: Fine-Tuning VLMs into VLAs Without Catastrophic Forgetting

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Actions as Language: Fine-Tuning VLMs into VLAs Without Catastrophic Forgetting |
| 링크 | [arXiv:2509.22195](https://arxiv.org/abs/2509.22195) |
| 분석 문서 | [`analysis/2509.22195/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-28 |

---

## 🧮 데이터 계약

알고리즘의 본질은 "연속 액션을 자연어 텍스트로 재표현해 표준 VLM의 입출력(이미지-텍스트 → 텍스트)으로 환원"하는 것입니다. 별도 액션 텐서 채널은 없으며, 모든 모달리티가 토큰 시퀀스로 흐릅니다.

- **입력 (관측)** — `image`: RGB, shape `(B, H, W, 3)`, 단일 third-person 뷰(평가 셋업). VLM의 이미지 전처리 통계로 정규화(원문 명시 없음 — VLM backbone 기본 전처리 가정).
- **입력 (언어)** — `instruction L` + `subtask l_i` + `motion_plan m_i`: 텍스트 토큰 시퀀스. max sequence length `1024`.
- **출력 (액션)** — `action_chunk ā_i`: **텍스트 토큰 시퀀스**로 표현된 "리스트의 리스트". 각 내부 리스트 = 한 timestep의 DoF별 명령 `[dx, dy, dz, gripper]`. 병진 DoF만(translational), 회전 제외. 좌표 규약: `+dx` 전진 / `-dx` 후진, `+dy` 좌 / `-dy` 우, `+dz` 상 / `-dz` 하, gripper `1` 열림 / `0` 닫힘.
- **시간 축** — action chunk는 **가변 길이**(고정 `chunk_size` 아님). 한 rollout은 `N` 개 subtask로 분해되며 각 subtask가 자신의 가변 길이 chunk를 가집니다.
- **데이터 변환 계약** — 원 데이터셋 $`\mathcal{D}_{\text{rob}}=\{\tau\}`$, $`\tau=\{(o_t,a_t)\}_{t=0}^{T}`$ (상대 end-effector 위치 제어) → 자연어 데이터셋 $`\mathcal{D}_{\text{lan}}=\{\bar{\tau}\}`$, $`\bar{\tau}=\{(\bar{o}_i,l_i,m_i,\bar{a}_i)\}_{i=0}^{N-1}`$. joint angle·절대 좌표 같은 state 정보는 가정하지 않음.

---

## 🧰 모듈 인터페이스

```python
def relabel_trajectory(tau, L, annotator) -> list:
    """원 궤적 τ + 주 과제 지시 L 을 (ō_i, l_i, m_i, ā_i) 3계층 자연어
    sub-trajectory 시퀀스로 변환. annotator = Gemini 2.5; base frame
    좌표계를 프롬프트로 제공. 반환: D_lan 의 한 항목 τ̄."""

def chunk_actions(actions, single_axis_thresh=0.025, abs_thresh=0.05) -> list:
    """sub-trajectory 액션을 단일 축 임계(2.5cm)·절대 임계(5cm)로 청킹해
    더 큰 크기의 이동만 남김. 미적용 시 액션 예측이 미미해지는 경향 방지."""

def predict_subtasks(o_0, L, policy) -> list[str]:
    """초기 관측 o_0 와 지시 L 로 N 개 subtask 를 한 번에 생성, rollout
    동안 고정. p_θ(l_i | ō_i, L)."""

def plan_motion(o_i, l_i, policy) -> str:
    """현재 관측·subtask 로 방향성 motion plan 생성. p_θ(m_i | l_i, ō_i)."""

def generate_action_chunk(o_i, l_i, m_i, policy) -> list[list[float]]:
    """관측·subtask·motion plan 으로 텍스트 액션 청크 생성.
    p_θ(ā_i | m_i, l_i, ō_i). 파싱 실패 시 재시도(retry)."""

def verify(o_i, o_next, l_i, l_next, verifier) -> bool:
    """V: O×O×L×L → L. action 실행 전/후 관측과 현재/다음 subtask 로
    현재 subtask 완료 여부 판정. 재시도 또는 다음 진행 결정.
    verifier = Gemini 2.5 Pro (외부)."""
```

- **policy** — 단일 VLM(Gemma-3-12B-IT 계열) + LoRA 어댑터. 세 추론 단계(`predict_subtasks` / `plan_motion` / `generate_action_chunk`)를 모두 동일 backbone이 텍스트 생성으로 수행. 별도 액션 디코더 없음.
- **외부 호출 계약** — 학습은 표준 cross-entropy(텍스트 생성) 손실 하나; 별도 액션 손실·optimizer 분리 없음. verifier는 inference-time에만 호출되는 외부 모듈로 학습 그래프와 무관.

---

## ⛓️ 불변식·가정

- **(가정 1) 분포 근접성** — LoRA가 forgetting을 막으려면 fine-tuning 데이터가 backbone의 사전학습 표현에 충분히 가까워야 함. "actions as language" 재표현이 이 근접성을 성립시킨다는 것이 알고리즘의 핵심 전제(Fig. 3: 언어 표현 액션의 log-prob > 토큰 표현).
- **(가정 2) 수치 magnitude의 언어적 grounding** — VLM이 'move forward by 4.2 centimeters' 같은 수치를 물리 공간에 grounding할 수 있을 만큼 내재적 수 감각을 가진다는 가정.
- **(가정 3) 액션 chunk magnitude 하한** — 청킹 전 인접 timestep 차분이 너무 작으면 정책이 무의미한(negligible) 액션을 출력. 단일 축 2.5cm / 절대 5cm 임계 이상으로 청킹해야 학습이 성립.
- **(가정 4) 상대 제어 표현 가능성** — 모든 액션이 상대 end-effector 이동(병진)으로 표현되어 base frame 방향 어휘(전/후/좌/우/상/하)로 자연어화 가능. joint-space·절대 좌표는 이 가정을 깸(cross-embodiment 한계).
- **(가정 5) 위계 분해 인수분해** — 결합 분포가 $`p_\theta(\bar{a}_i,m_i,l_i|\bar{o}_i,L)=p_\theta(l_i|\bar{o}_i,L)\,p_\theta(m_i|l_i,\bar{o}_i)\,p_\theta(\bar{a}_i|m_i,l_i,\bar{o}_i)`$ 로 깔끔히 인수분해된다는 chain-rule 가정.

---

## 📊 하이퍼파라미터·손실

- **손실 식** — `L = CrossEntropy(text tokens)` (모든 linear module에 LoRA 적용한 표준 supervised fine-tuning; 별도 액션 손실 없음).
- **목적 분포** —

$$p_{\theta}(\bar{a}_{i},m_{i},l_{i}|\bar{o}_{i},L)=p_{\theta}(l_{i}|\bar{o}_{i},L)\;p_{\theta}(m_{i}|l_{i},\bar{o}_{i})\;p_{\theta}(\bar{a}_{i}|m_{i},l_{i},\bar{o}_{i})$$

- **하이퍼:**

  | 이름 | 값 | 출처 |
  |------|----|----|
  | Base model | `Gemma-3-12B-IT` | §9, Table 4 |
  | Fine-tuning method | `PEFT (LoRA)` | §9, Table 4 |
  | LoRA rank `r` | `16` | §9, Table 4 |
  | LoRA `alpha` | `32` | §9, Table 4 |
  | Target modules | `q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, gate_proj` | §9, Table 4 |
  | Precision | `bfloat16 (BF16)` | §9, Table 4 |
  | Optimizer | `AdamW` (β1=0.9, β2=0.999, ε=1e-8) | §9, Table 4 |
  | Learning rate | `5e-5` (linear decay) | §9, Table 4 |
  | Effective global batch size | `8` (per-device 1 × grad-accum 2 × 4 GPU) | §9, Table 4 |
  | Max sequence length | `1024` | §9, Table 4 |
  | Epochs | `1` | §9 |
  | 학습 자원 | 4× A100, ~300 GPU-hours | §9 |
  | 청킹 임계 (단일 축 / 절대) | `2.5 cm` / `5 cm` | §6.2 |
  | 추론 sampling | top-p `0.95`; temp = motion 0.1 / action 0.5 / subtask 0.5(ID)·1.0(OOD) | §8.4 |
  | Verifier | Gemini 2.5 Pro (외부) | §3.1.1, §8.5 |

---

## 🎯 평가 메트릭

- **지표 (멀티모달 보존)** — 다수 VQA 벤치마크(MMMU, MMStar, MME, OCRBench, MMB-en/cn, TextVQA, DocVQA, InfoVQA, AI2D, ChartQA, RealWorldQA) · **임계값** — base 모델 성능의 $`\ge 85\%`$ 유지 · **비교 baseline** — 원 backbone(Gemma-3-12B-IT), OpenVLA·ECoT(forgetting 비교군), MolmoAct· $`\pi_{0.5}`$(co-trained 비교군).
- **지표 (조작 성공률)** — 과제별 success rate(부분 점수 포함 rubric), 과제당 30 trial(다국어 90) · **비교 baseline** — OpenVLA, ECoT, ablation VLM2VLA-AT · 셋업 — 6-DoF WidowX 250S, toy kitchen, Realsense D435.
- **지표 (추론 일반화)** — ID / borderline / OOD(다국어 번역, 'Ash Ketchum' 의미 추론) 구분 평가; task decomposition 정확도(Fig. 6, 키워드 매칭). 대표 수치: Ash Ketchum 과제 VLM2VLA 60% vs VLM2VLA-AT 30%.
- **지표 (지연)** — 1 action 사이클 wall-clock: median 6.1s / mean 10.5s / std 14.3s (A100, N=30).

---

## ✨ 변경 의도 (intent)

기존 VLA는 forgetting을 *모델 쪽*에서 해결하려 했습니다 — 별도 액션 디코더(diffusion/flow), 토큰 사전 개조, 또는 web 데이터 co-training. 이들은 모두 새 파라미터를 도입하거나(사전학습 표현 교란) 값비싼 혼합 데이터 튜닝(mixture ratio)을 요구합니다. VLM2VLA는 이 forgetting의 근본 원인을 backbone 사전학습 분포와 로봇 데이터 사이의 *분포 불일치*로 봅니다. 그래서 이를 **데이터 레벨**에서 풉니다. 저수준 액션까지 자연어로 재표현해 데이터를 VLM 표현 공간에 정렬시키면 LoRA만으로 backbone을 최소 교란하며 적응합니다. 결과적으로 별도 디코더·co-training·다단계 학습 없이, model-agnostic하고 단순한 한 줄 손실(cross-entropy)로 forgetting을 회피하는 것이 핵심 차별점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 대응 base는 사실상 없습니다. lerobot의 6개 정책(`pi0`/`pi05`/`pi0_fast`/`smolvla`/`act`/`diffusion`)은 모두 **별도 연속 액션 head(flow-matching/diffusion) 또는 액션 토큰**을 전제하는데, VLM2VLA의 본질은 "액션 디코더 제거 + 자연어 액션 + 표준 LM cross-entropy"라 이 family들과 구조적으로 어긋납니다. 가장 가까운 점은 `pi0_fast`의 토큰화 액션 계열(자기회귀 텍스트 생성)이나, VLM2VLA는 token 사전 개조 대신 일반 자연어를 쓴다는 점에서 다릅니다. 매핑은 "데이터 재라벨링 파이프라인 + LoRA fine-tuning 레시피" 수준의 부분 이식에 그칩니다(최종 판정은 `/implement-design`).

---

## 🚧 미해결 / 잠정

- 이미지 정규화 통계·전처리 세부는 원문에 명시 없음 — VLM backbone(Gemma-3) 기본 이미지 전처리로 가정.
- action chunk 텍스트 직렬화의 정확한 토큰 포맷(소수 자릿수, 구분자)은 부록 예시로만 제시되고 형식 스펙으로 고정되지 않음 — 예시 기반 추정.
- verifier 프롬프트는 명시되나, base VLM을 verifier로 학습시키는 방법은 "시도했으나 신뢰 가능 수준 미달"로 미해결(저자 future work).
- cross-embodiment(joint-space 제어)로의 일반화는 가설 수준이며 본 논문에서 미검증.
- 보고된 VQA 보존율 "85% 이상"의 정확한 집계 방식(벤치마크별 가중·평균 정의)은 본문에 식으로 명시되지 않음 — 표 수치 기반 잠정.
