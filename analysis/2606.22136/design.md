# Design — Wh0: Generative World Models as Scalable Sources of Egocentric Human Hand Manipulation Data

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Wh0: Generative World Models as Scalable Sources of Egocentric Human Hand Manipulation Data |
| 링크 | [arXiv:2606.22136](https://arxiv.org/abs/2606.22136) |
| 분석 문서 | [`analysis/2606.22136/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-08-02 |

---

## 🧮 데이터 계약

시간 축은 `chunk_size = 16` (미래 스텝 수), 액션 차원 `d_action = 102`, 상태 차원 `d_state = 212` 로 표기합니다. 배치 차원은 `B`.

**정책 (VITRA-style VLA)**

- **입력** — `observation.image`: shape `(B, 3, H, W)`, float. 배포 카메라의 egocentric 1인칭 뷰 1대. 해상도는 `(원문에 명시 없음 — 가정으로 메움: PaliGemma2-3B 의 기본 입력 해상도)` 이며, 원문은 "same viewpoint and resolution as the policy input" 로 **생성 데이터와 정책 입력의 해상도 일치** 만 요구합니다.
- **입력** — `observation.language`: 가변 길이 토큰 시퀀스. 단계 조건부(stage-conditioned) 자연어 지시문 1개.
- **입력** — `observation.fov`: shape `(B, 2)`, float. 2D FoV 값을 MLP 로 백본 hidden size 에 사영해 입력 시퀀스에 토큰으로 삽입.
- **입력** — `observation.state`: shape `(B, 212)`, float. 카메라 프레임 기준 손목 translation + Euler angle + 손별 15-DoF MANO 관절 회전. 통합 VITRA 공간으로 padding 되며 **사람 손 관련 차원만 활성**.
- **입력(내부)** — `cognition_token`: 학습 가능한 토큰 1개를 입력 시퀀스에 append 하고, 그 최종 hidden state 를 액션 디코더의 조건 특징으로 추출.
- **출력** — `action`: shape `(B, 16, 102)`, float. 액션 정의는 식 (1) 참조.
- **정규화** — 액션·상태 모두 **사전학습 corpus(대규모 사람 영상)에서 미리 계산된 per-joint 통계** 를 재사용합니다. 배포 로봇 데이터에서 통계를 재계산하지 않는 것이 알고리즘의 요구 사항입니다. 통계의 구체 수치는 `(원문에 명시 없음 — 외부 사전학습 산출물에 종속)`.
- **좌표계** — 모든 상태·액션은 **현재 관측** $`o_{t}`$ **의 카메라 좌표계**. 로봇 시연은 base 프레임 → 카메라 프레임 변환 후, 손목 회전을 MANO 규약에 맞게 보정하고 관절각을 MANO 공간으로 retarget 하여 동일 계약에 편입.

**데이터 생성 파이프라인 (WM-H)**

- **입력** — `workspace_image`: shape `(3, H, W)`. 배포 카메라·시점·해상도로 촬영한 실제 작업대 배경 이미지. 촬영 시 관심 영역에 사람 손 1개를 스케일 기준자로 포함.
- **입력** — `instruction`: 문자열. `pick the {adj} {noun}` 형태의 구조 템플릿으로 조립.
- **중간 산출** — `edited_first_frame`: shape `(3, H, W)`. 지정 객체가 삽입된 초기 프레임(가이드 사각형은 최종 이미지에서 제거).
- **중간 산출** — `video`: shape `(T, 3, H, W)`. `T` 및 fps 는 `(원문에 명시 없음 — 가정으로 메움)`.
- **중간 산출** — `video_ea`: 고정 간격·고정 오프셋으로 성기게 샘플된 프레임 부분집합에 대해 손 외형만 로봇 손으로 편집한 프레임들. 간격·오프셋 값은 `(원문에 명시 없음)`.
- **출력** — `hand_motion`: 프레임별 MANO 파라미터 + 손목 pose. 손목 pose 는 카메라 공간, 관절 pose 는 MANO 파라미터 공간에 유지. 이후 연속 프레임 차분을 취해 식 (1) 의 액션으로 변환.
- **출력 규모** — 50k 에피소드(영상 + 지시문 + 3D 손 포즈 주석).

---

## 🧰 모듈 인터페이스

```python
def generate_instruction(db: VocabDB, diversity_hint: str) -> str:
    """저빈도 단어를 우선 샘플링해 구조 템플릿으로 지시문 1개를 조립하고 중복을 거른다."""

def expand_vocabulary(db: VocabDB, num_nouns: int, num_adjectives: int) -> VocabDB:
    """모든 기존 단어가 최소 사용 임계치에 도달했을 때만 LLM 으로 어휘 풀을 확장한다."""

def edit_scene(workspace_image: Image, objects: list[str], guide_boxes: list[Box]) -> Image:
    """배포 작업대 배경에 지정 객체를 삽입해 video 생성용 초기 프레임을 만든다(가이드 박스 제거)."""

def describe_dynamics(first_frame: Image, instruction: str, hand: str) -> str:
    """초기 프레임 + 지시문으로부터 기대되는 손-객체 상태 변화 서술을 생성해 video prompt 에 덧붙인다."""

def generate_video(first_frame: Image, video_prompt: str) -> Video:
    """image-to-video 로 egocentric 사람 손 조작 영상을 합성한다(카메라 고정, 1인칭 top-down)."""

def edit_embodiment(video: Video, stride: int, offset: int) -> list[Image]:
    """성기게 샘플한 프레임의 손 외형만 로봇 손으로 교체한다(포즈·위치·스케일·배경·구성 보존)."""

def reconstruct_hand_motion(video: Video) -> HandMotion:
    """프레임별 손을 검출해 MANO 파라미터 + 손목 pose 를 회귀하고, 필요 시 카메라 궤적과 결합한다."""

def encode_observation(image, language, fov, state) -> CognitionFeature:
    """VLM 백본으로 관측·지시문·FoV 를 인코딩하고 cognition token 의 최종 hidden state 를 반환한다."""

def denoise_action(cognition: CognitionFeature, state, noisy_action, step: int) -> Tensor:
    """diffusion 디코더가 step 에서의 노이즈를 예측한다. 반환 shape 은 (B, 16, 102)."""

def sample_batch(sources: dict[str, Dataset], weights: dict[str, float]) -> Batch:
    """teleop / WM-H / WM-H EA 를 고정 비율로 섞어 한 배치를 구성한다(희소 원천 오버샘플링)."""
```

- **`generate_instruction` / `expand_vocabulary`** — 어휘 빈도 데이터베이스를 공유하는 이중 에이전트. 확장은 **커버리지 조건부** 로만 트리거되며, 이것이 h-index 형태의 다양성을 만드는 유일한 장치입니다.
- **`edit_scene` → `generate_video` → `edit_embodiment`** — 순차 파이프라인. `edit_embodiment` 는 `generate_video` 의 출력을 **대체하지 않고 추가** 합니다(원본 영상과 편집 프레임이 서로 다른 학습 원천 `W` / `W-EA` 로 공존).
- **`reconstruct_hand_motion`** — 파이프라인의 유일한 라벨 원천. 손실 함수와의 관계는 간접적입니다: 이 함수의 출력이 곧 식 (2) 의 supervision target 이 되므로, 재구성 오류는 검출되지 않은 채 라벨 노이즈로 전파됩니다.
- **`sample_batch`** — 학습 루프의 유일한 정합 장치. scene / embodiment alignment 는 손실 항이 아니라 **이 함수의 `weights` 와 각 원천의 생성 방식** 으로만 구현됩니다.
- **`encode_observation` / `denoise_action`** — 표준 VLM + diffusion 액션 디코더 계약. 비전 인코더는 학습 중 동결(gradient 차단), 나머지 백본과 디코더는 갱신.

---

## ⛓️ 불변식·가정

- **(가정 1) 액션은 카메라 프레임의 상대량** — 손목 translation·rotation 은 **연속 프레임 사이의 차분** 이며, 절대 world 좌표가 아닙니다. 카메라가 움직이면 같은 물리 궤적이 다른 액션으로 라벨링되므로, 생성 파이프라인이 카메라를 고정하는 것은 편의가 아니라 **계약 조건** 입니다.
- **(가정 2) 사람 손과 로봇 손이 동일 MANO 공간에서 표현 가능** — 로봇 관절 → MANO retarget 이 정보를 유의하게 잃지 않는다고 가정합니다. 15-DoF × 3 을 초과하는 자유도를 가진 손에서는 이 가정이 약화됩니다.
- **(가정 3) 정규화 통계는 사전학습 corpus 에서 온다** — 배포 데이터가 소량일 때 그 표본 통계는 신뢰할 수 없고, 재계산 시 사전학습된 액션 분포와 좌표가 어긋납니다. 이 불변식이 깨지면 사람 영상 prior 의 재사용이라는 알고리즘의 전제가 무효화됩니다.
- **(가정 4) 외형 편집이 궤적을 보존한다** — `edit_embodiment` 는 손 외형만 바꾸고 포즈·위치·객체 운동·장면 구성을 유지해야 합니다. 이것이 성립해야 `W` 와 `W-EA` 가 **같은 액션 라벨을 공유하는 두 시각적 표현** 이 됩니다. 깨지면 동일 라벨에 상충하는 시각 증거를 주는 셈이 됩니다.
- **(가정 5) 생성 영상의 손 재구성이 신뢰 가능** — 사람 손 재구성기가 실촬 영상뿐 아니라 **합성 영상** 에서도 동작해야 합니다. 파이프라인이 사람 손을 생성하는 이유가 정확히 이 가정 때문이며, 로봇 손을 직접 생성하면 이 가정을 세울 수 없습니다.
- **(가정 6) 배포 정합은 데이터 분포로만 강제된다** — 손실에 정합 항이 없으므로, 정합성은 전적으로 `sample_batch` 의 비율과 각 원천의 생성 조건에서 나옵니다. 데이터 파이프라인을 바꾸면 알고리즘 자체가 바뀝니다.
- **(가정 7) 사람 영상 사전학습된 백본이 선행 조건** — 이 데이터 레시피는 사전학습 prior 를 *활성화·정렬* 하는 촉매이지 스킬을 처음부터 가르치지 않습니다. 사람 영상 prior 가 없는 백본에서는 이득이 사라집니다(분석 문서 §📊 Table 3).

---

## 📊 하이퍼파라미터·손실

**액션 공간 정의 (식 1)**

$$a_{t}=[\Delta t^{l},\Delta r^{l},\theta_{h}^{l},\Delta t^{r},\Delta r^{r},\theta_{h}^{r}]\in\mathbb{R}^{102}$$

$`\Delta t,\Delta r\in\mathbb{R}^{3}`$ 는 연속 프레임 사이 상대 손목 translation / rotation(Euler angle), $`\theta_{h}\in\mathbb{R}^{15\times 3}`$ 는 15-DoF MANO 손 모델의 국소 프레임 관절 회전, 위첨자 $`l,r`$ 은 좌/우 손입니다.

**학습 손실 (식 2)**

$$\mathcal{L}_{\mathrm{MSE}}=\mathbb{E}_{\epsilon\sim\mathcal{N}(0,1),\,i}\left[\left\|\hat{\epsilon}_{i}-\epsilon\right\|_{2}^{2}\right]$$

$`\hat{\epsilon}_{i}`$ 는 diffusion 스텝 $`i`$ 에서 예측된 노이즈입니다. **정합 항·대조 항·정칙화 항은 없습니다** — 총 손실 = 식 (2) 단일 항.

| 이름 | 값 | 출처 |
|------|----|----|
| `backbone` | PaliGemma2-3B | §B.1 |
| `action_decoder` | DiT-B (diffusion) | §B.1 |
| `chunk_size` | `16` | §B.1 |
| `d_action` | `102` | §4, 식 (1) |
| `d_state` | `212` | §B.2 |
| `vision_encoder` | frozen | §4, §B.3 |
| `learning_rate` | $`1\times 10^{-5}`$ (백본·디코더 공통) | §4, §B.3 |
| `weight_decay` | `0.1` | §4, §B.3 |
| `betas` | $`(0.9,0.95)`$ | §B.3 |
| `grad_clip` | `1.0` | §B.3 |
| `max_steps` | `40k` | §B.3 |
| `batch_size` | `64` per GPU × 4 → `256` | §B.3 |
| `hardware (train)` | NVIDIA H200 × 4 | §B.3 |
| `diffusion_steps (train)` | `100`, squared-cosine 노이즈 스케줄 | §B.3 |
| `diffusion_repeats_per_batch` | `8` (노이즈·타임스텝 독립 재샘플) | §B.3 |
| `image_augmentation` | 없음 | §B.3 |
| `sampler.weights` | `R : W-EA : W = 0.28 : 0.04 : 0.68` | §4, §B.4 Table 5 |
| `dataset_size_ratio` | `125:1` (50k WM-H : 400 teleop) | §4 |
| `inference_sampler` | DDIM, `10` steps | §B.3 |
| `cfg_scale` | `5.0` | §B.3 |
| `hardware (infer)` | NVIDIA RTX 4090 × 1 | §B.3 |
| `generation_cost` | 1k 영상당 약 `5.44` GPU-hour | §3 |
| `optimizer` | `(원문에 명시 없음 — betas 표기로 보아 Adam 계열로 가정)` | — |
| `lr_schedule` / `warmup` | `(원문에 명시 없음)` | — |
| `image_edit_steps` / `cfg (편집)` | `(원문에 명시 없음 — "small number of steps", "low CFG scale" 로만 서술)` | §A.2, §A.4 |
| `video_length` / `fps` | `(원문에 명시 없음)` | — |
| `ea_frame_stride` / `offset` | `(원문에 명시 없음 — "fixed interval with a fixed offset")` | §A.4 |

**배포 시 규칙 (정책 외부)** — 접촉 이전 단계에서 손가락 관절이 안정 파지에 도달할 때까지 **단조 폐합(monotonic closure)** 하도록 제약하는 grasping prior 를 겁니다(§C.1). 학습 손실과 무관한 후처리이며, 비교 대상 전 방법에 동일 적용됩니다.

---

## 🎯 평가 메트릭

- **지표** — `Task Success Rate (%)` · **임계값** — 18개 실세계 다지 조작 태스크 × 태스크당 20 trial, 객체 pose·장면 무작위화, **태스크별 시연 없는 zero-shot**. 평균 + 표준편차 보고 · **비교 baseline** — teleop-only FT (VITRA `8.3±8.6`, $`\pi_{0.5}`$ `7.78±15.6`), 실촬 ego co-FT (VITRA Real Version `21.4±23.4`); 본 방법 `38.9±19.8`.
- **지표** — `Hand-Object Distance (cm)` · **임계값** — 낮을수록 좋음. 기준선은 "정책 없음(초기 pose)" `18.9±2.8`; 본 방법 `10.6±2.0` (사람 손 외형) / `9.6±1.8` (로봇 손 외형) · **비교 baseline** — teleop only `16.2±3.3`. 평가셋은 unseen 지시문(LLM 생성) + unseen 객체(이미지 편집 생성) 약 5k 에피소드, 수동 필터링 후 확정 (§C.2).
  - **지표의 성격 제한(원문 명시)** — 손목 도달 거리만 재므로 손가락 수준 손재주는 측정하지 않습니다. 낮은 거리는 성공의 **필요조건이지 충분조건이 아닙니다**. 따라서 단독 판정 지표로 쓰면 안 되며 성공률과 병기해야 합니다.
  - **외형 강건성 판정** — 동일 정책에 대해 HO(human) 과 HO(robot) 을 **둘 다** 측정하고 그 격차를 봅니다. embodiment alignment 제거 시 격차가 `10.2` 대 `13.8` (3.6) 로 벌어지고, 적용 시 `10.6` 대 `9.6` (1.0) 로 좁혀집니다.
- **지표** — `action-feature cosine similarity` · **임계값** — `(원문에 임계값 명시 없음 — 정성 비교)` · **비교 baseline** — 동일 궤적의 원본 외형 vs 편집 외형. 외형 변화에 대한 액션 특징 불변성을 직접 측정 (§5.3, Figure 6 right).
- **지표(데이터 측)** — `noun / adjective h-index` · **값** — 명사 `201`, 형용사 `117` (pick / place / grasp 지시문 전체) · **의미** — $`h`$ 개 단어가 각각 최소 $`h`$ 개 샘플에 등장. 어휘 수만 늘리는 확장을 배제하는 커버리지 지표.
- **지표(데이터 측)** — 생성 영상 품질 user study (`N=72`) · **값** — 실촬 오인율 `37.7%` (134/355), 5점 Likert 로 object correctness `3.97±1.22` / instruction alignment `4.18±1.09` / hand-object interaction `3.95±1.19` / physical plausibility `3.78±1.30` / training suitability `3.57±1.31`, 편집 전후 pose consistency `4.30±0.85` / contact preservation `4.25±0.84` · **주의** — 실촬 ceiling `5.0` 은 측정값이 아니라 가정값 (§A.5).

---

## ✨ 변경 의도 (intent)

선행 연구는 world model 을 환경 동역학 시뮬레이터, 로봇 궤적 비디오 생성기, retargeting 용 손 생성기, 또는 미래 예측 정책의 백본으로 사용해 왔습니다. 본 설계는 그 어느 것도 하지 않고 world model 을 **오프라인 데이터 공장** 으로만 씁니다 — 정책 그래프 안에 world model 이 존재하지 않으므로 추론 비용도, 예측 정확도 요구도 없습니다. 대신 데이터 원천의 두 고질적 간극을 *생성 조건* 으로 치환합니다: 배경을 실제 배포 작업대 사진으로 못 박아 scene gap 을 없애고(scene alignment), 완성된 영상의 손 외형만 로봇 손으로 편집해 embodiment gap 을 없앱니다(embodiment alignment). 액션 라벨은 생성 조건이 아니라 성숙한 사람 손 재구성기로 사후 획득하며, 이 분업 덕분에 "생성은 사람 손으로, 배포는 로봇 손으로"가 동시에 성립합니다. 학습 측 변경은 손실이 아니라 **배치 샘플링 비율과 정규화 통계의 출처** 뿐입니다 — 즉 이 설계의 알고리즘적 실체는 모델이 아니라 데이터 계약이며, 그 효과는 새 손재주를 가르치는 것이 아니라 사람 영상 사전학습이 이미 보유한 prior 를 소량 로봇 데이터가 접근 가능한 형태로 정렬해 주는 것입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정책 측은 PaliGemma 계열 VLM 백본 + 별도 액션 디코더 구조라 `pi0` / `pi05` family 가 가장 가깝지만, 액션 헤드가 flow matching 이 아니라 DDPM/DDIM noise-prediction 이므로 `diffusion` family 의 스케줄러·샘플러 요소가 섞인 하이브리드입니다. 데이터 계약(102-D MANO 액션, 212-D 상태 padding, 사전학습 corpus 통계 재사용)은 정책 코드보다 `datasets/` · `processor` 계층의 변경 지점에 가깝고, WM-H 생성 파이프라인 자체는 foundry 정책 코드 밖의 오프라인 데이터 생성 스크립트라 매핑 대상이 아닐 가능성이 높습니다.

---

## 🚧 미해결 / 잠정

- **정규화 통계의 실체** — "VITRA 가 사전 계산한 per-joint 파라미터"라고만 명시되고 수치·계산 절차가 없습니다. 외부 사전학습 산출물에 종속되므로 독립 재현 시 동일 액션 공간을 맞출 수 없습니다.
- **관측 해상도 · 영상 길이 · fps** — 원문은 "정책 입력과 동일한 시점·해상도"만 요구하고 절대 값을 주지 않습니다. 데이터 계약에서 `(원문에 명시 없음 — 가정으로 메움)` 으로 남겼습니다.
- **EA 프레임 샘플링 파라미터** — "fixed interval with a fixed offset" 이라고만 서술되어 간격·오프셋 값이 없습니다. 배치의 4% 라는 비율만 확정적입니다.
- **이미지 편집 스텝 수와 CFG scale** — "small number of steps", "low CFG scale" 로만 서술됩니다.
- **품질 필터의 부재** — §A.6 이 5개 실패 유형을 열거하지만 자동 검출·필터 단계가 명시되지 않아, 50k 중 오염 비율과 필터 통과 기준을 Layer 1 스펙으로 굳히지 못했습니다. HO 평가셋의 "수동 필터링" 기준도 마찬가지입니다.
- **`w/o embodiment alignment` ablation 의 비율 재조정** — 이 조건만 `R:W = 0.4:1` 로 다른 비율 체계를 쓰므로(§B.4 Table 5), EA 제거 단일 변인 통제가 아닙니다. 동일 비율 하 EA-only ablation 은 원문에 없습니다.
- **optimizer 종류** — betas $`(0.9,0.95)`$ 표기로 Adam 계열이 강하게 시사되지만 이름이 명시되지 않아 가정으로 남깁니다.
- **`W` 와 `W-EA` 의 라벨 공유 여부** — 편집 프레임이 원본과 동일한 액션 라벨을 그대로 쓰는지, 별도 재구성을 거치는지 원문에 명시가 없습니다. 가정 4 는 라벨 공유를 전제하지만 확증 문장은 없습니다.
