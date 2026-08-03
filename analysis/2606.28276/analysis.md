# Paper Analysis — SimFoundry: Modular and Automated Scene Generation for Policy Learning and Evaluation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | SimFoundry: Modular and Automated Scene Generation for Policy Learning and Evaluation |
| 저자 | Nadun Ranawaka, Josiah Wong, Wei-Lin Pai, Wei-Teng Chu, Tianyuan Dai, Masoud Moghani, Hang Yin, Yunfan Jiang, Wesley Durbano, Brandon Huynh, Yu Fang, Linxi Fan, Danfei Xu, Ruohan Zhang, Li Fei-Fei, Bowen Wen, Ajay Mandlekar, Yuke Zhu (NVIDIA · Georgia Tech · Stanford · UT Austin · U Toronto) |
| 링크 | [arXiv:2606.28276](https://arxiv.org/abs/2606.28276) · [Website](https://research.nvidia.com/labs/gear/simfoundry/) |
| 발행일 / 버전 | 2026-06-26 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-02 |
| 관련 Pillar | P0 |
| 태그 | sim2real, dataset |
| Design 적용 | 🚫 비대상 (tooling) |

<!-- 본문은 arXiv HTML(전문)로 확보. Website 링크는 논문 초록에 verbatim 으로
     명시된 프로젝트 페이지 URL 이며, 본 분석 환경에서는 네트워크 정책으로
     검증 실패: `curl -sS "https://research.nvidia.com/labs/gear/simfoundry/"`
     → `curl: (56) CONNECT tunnel failed, response 403`. GitHub / HuggingFace
     링크는 본문에 존재하지 않아 기재하지 않음. -->

---

## 🧭 한 줄 요약 (TL;DR)

단일 실세계 비디오 하나에서 sim-ready 디지털 트윈을 자동 재구성하고, 이를 object / scene / task cousins 로 확장해 정책 학습·평가 환경을 대량 생성하는 모듈러 real-to-sim 시스템입니다. 7개 조작 태스크 × 5개 정책에서 시뮬레이션 평가가 실환경 성능을 Pearson 0.911 / MMRV 0.018 로 예측하며, cousins 로 증강된 sim 데이터가 zero-shot Sim2Real (시뮬레이션-실환경 이전) 성공률을 축별 평균 17% / 21% / 40% 끌어올린다는 것이 핵심 주장입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 실환경에서의 정책 학습 데이터 수집과 정책 평가는 비용이 크고 확장이 어렵습니다. 특히 엄밀한 모델 비교에는 태스크당 수천 회의 실기 시행이 필요합니다.
- **기존 접근의 한계** — 기존 real-to-sim 시스템은 (a) 장면 재구성 자동화, (b) sim 기반 정책 평가의 실환경 상관, (c) sim 학습 정책의 실환경 전이 중 일부만 지원하며, 세 가지를 하나의 파이프라인으로 닫은 시스템이 드뭅니다. 평가 전용 시스템은 수동 튜닝 장면·단일 스텝 태스크에 머무릅니다.
- **본 논문의 가설** — 3D 재구성·생성 foundation model 들을 모듈러 파이프라인으로 조합하면, 비디오 한 편에서 물리적으로 상호작용 가능한 디지털 트윈을 자동 생성하고, affordance 를 보존하는 변형(digital cousins)으로 확장해 평가와 학습 양쪽을 함께 해결할 수 있습니다.
- **왜 지금 중요한가** — depth / segmentation / 2D-to-3D 생성 / VLM 등 구성 요소 모델의 품질이 급상승해, 각 단계를 교체 가능한 모듈로 두면 시스템 전체 재설계 없이 성능이 계속 따라 올라가는 시점입니다.
- **평가 관점의 공백** — sim 평가가 실환경 순위를 보존하는지(correlation)가 검증되지 않으면 sim 벤치마크는 의사결정 도구가 되지 못합니다. 본 논문은 상관 지표(Pearson, MMRV)를 태스크·정책 격자 전체에서 실측합니다.

---

## 🧩 핵심 기여

- **완전 자동 real-to-sim 파이프라인** — 단일 RGB 비디오 → per-object 분할·깊이 추출 → 2D-to-3D 메시 생성 → 포즈 정렬 → 관절(articulation) 생성 → 물리 파라미터 주석 → PyBullet 안정화 → IsaacLab 등으로 내보내는 3단계(Extraction–Generation–Augmentation) 시스템. 12개 재구성 장면에서 zero-shot F1 0.81–0.92, 오브젝트당 3분 튜닝으로 0.93–0.99.
- **Digital cousins 3축 증강** — 원 장면의 affordance 를 보존하며 object(형상·토폴로지·외관), scene(의미적 공간 술어 기반 재배치 + distractor), task(VLM 이 제안하는 실행 가능 태스크) 축으로 변형을 자동 생성. 세 축 모두 정책 일반화 개선을 ablation 으로 입증.
- **실환경 상관 검증된 sim 평가** — 7개 태스크 × 5개 정책 아키텍처(π0, π0.5, GR00T N1.6/N1.7, DreamZero)에서 평균 Pearson 0.911 / MMRV 0.018. SOTA 베이스라인 PolaRiS 대비 Pearson 0.59 이상 우위. 서브태스크 시작 상태 평가로 장기 태스크 상관을 0.902→0.951 로 추가 개선.
- **Sim-to-Real 학습 실증** — SimFoundry 데이터만으로 학습한 정책이 YAM Pot on Stove 99%, DROID Stack Dishware 100% zero-shot 실기 성공. sim+real co-training 은 π0.5 Store Marker 실기 성공률을 60%→92% 로 개선.
- **멀티태스크 확장** — 클러터 장면 하나에서 VLM 이 13개 태스크를 제안, sim 데모만으로 π0.5 를 finetune 해 sim 최대 31% / real 18% 개선, held-out 실기 태스크 29% 성공.

---

## 🔑 기술 키워드

- **Real-to-Sim** — 실세계 관측(비디오)에서 시뮬레이션 환경을 역으로 구축하는 방향. 본 논문의 시스템 전체가 이 방향의 자동화입니다.
- **Digital Twin** — 실장면의 기하·배치를 엄격히 복제한 sim 장면. 실환경 평가를 대신할 "복제 무대"에 해당합니다.
- **Digital Cousin** — 명시적 복제 없이 의미적·기하적 affordance 만 보존한 변형 장면. 객체 인스턴스 랜덤화의 구조화된 형태로, 본 논문에서 object / scene / task 3축으로 확장됩니다.
- **Sim-to-Real Transfer** — Sim2Real (시뮬레이션-실환경 이전). sim 에서 학습한 정책을 실기에 zero-shot 배치하는 설정이 본 논문의 학습 측 검증축입니다.
- **Pearson Correlation** — sim 평가 점수와 실환경 점수 사이의 선형 상관 계수. 1 에 가까울수록 sim 평가가 실환경 성능을 잘 예측합니다.
- **MMRV (Mean Maximum Rank Violation)** — sim 이 정책 순위를 뒤집을 때, 뒤집힌 쌍의 실환경 점수 차이 중 최대치를 평균한 지표. "순위 보존" 을 직접 측정합니다.
- **3D Gaussian Splatting** — 포토리얼 배경 재구성 표현. 전경 제거(인페인팅) 후 depth 감독으로 학습해 sim 장면의 배경 시각을 채웁니다.
- **Articulated Object Generation** — 메시 분할 + VLM 이 관절 타입·축·범위를 코드(URDF API)로 생성하고 critic VLM 이 영상으로 채점하는 actor-critic 루프.
- **MimicGen** — 소수 인간 데모를 서브태스크 단위로 이어붙여 대량 합성 궤적을 만드는 기존 데이터 증식 방법. 본 시스템의 데모 증식 엔진으로 쓰입니다.
- **Foundation Model Pipeline** — depth·분할·메시 생성·포즈·VLM 등 교체 가능한 외부 모델 슬롯( $`V_{*}`$ )의 조합으로 시스템을 구성하는 설계 원칙.

---

## 🔬 방법론

### 직관

SimFoundry 가 하려는 일은 "실험실 책상 위 장면을 스마트폰으로 한 번 찍으면, 그 장면의 물리 시뮬레이션 복제본이 자동으로 만들어지는 것" 입니다. 사람이 시뮬레이션 환경을 손으로 조립하는 대신, 이미 존재하는 강력한 지각·생성 모델들 — 깊이 추정, 분할, 이미지-투-3D 메시 생성, 포즈 추정, VLM — 을 정해진 순서로 연결해 각 물체를 하나씩 떼어내고, 3D 메시로 복원하고, 원래 자리에 되돌려 놓습니다. 물리 엔진에서 장면을 한 번 "정착" 시켜 물체끼리 겹치지 않는 안정 상태를 캐시하면, 로봇이 상호작용할 수 있는 sim-ready 장면이 완성됩니다.

복제본 하나로는 학습 데이터 다양성이 부족하므로, 시스템은 이 트윈을 세 방향으로 변형합니다. 물체를 "같은 기능의 다른 물건" 으로 바꾸고(object cousins), 배치를 의미 술어 수준에서 재배열하고(scene cousins), 그 장면에서 수행 가능한 새로운 태스크를 VLM 이 제안하게 합니다(task cousins). 변형이 affordance 를 보존하도록 VLM 이 제안·검증 루프를 돌기 때문에, 무작위 랜덤화보다 구조화된 다양성이 만들어집니다.

이렇게 만든 환경은 두 방향으로 쓰입니다. 첫째, 실기 정책들을 sim 트윈에서 평가해 실환경 성능·순위를 예측하는 real-to-sim 평가. 둘째, 소수 인간 데모를 MimicGen 으로 증식해 sim 데이터만으로(또는 소량 real 과 섞어) 정책을 학습시켜 실기에 zero-shot 배치하는 sim-to-real 학습입니다. 논문의 실험은 이 두 응용이 모두 실제로 작동함을 상관 지표와 실기 성공률로 보입니다.

핵심 설계 철학은 단일 모델이 아니라 "모듈러 조합" 입니다. 각 단계가 교체 가능한 슬롯이므로, 더 좋은 foundation model 이 나오면 그 슬롯만 갈아 끼우면 됩니다.

> "Its modular design decomposes real-to-sim construction into interchangeable components for perception, asset generation, pose alignment, articulation, physics annotation, and data generation, allowing improved foundation models to be incorporated as they become available without redesigning the full system." (§1)

(시스템의 지속 가능성을 알고리즘 혁신이 아니라 구성 요소 교체 가능성에서 찾는다는, 이 논문의 정체성을 못 박는 문장입니다.)

### 아키텍처

전체 파이프라인은 3단계입니다.

> "SimFoundry generates interactive simulated scenes through three stages, as seen in Figure 2: Extraction, which infers relevant per-object information from a video; Generation, which creates, aligns, annotates, and stabilizes sim-ready assets; and Augmentation, which produces digital cousins in the form of object, scene, and task variations." (§4)

(비디오 → per-object 정보 → sim-ready 자산 → 변형 증강의 단방향 파이프라인으로, 각 단계 출력이 다음 단계의 유일한 입력이 되는 구조입니다.)

![Figure 2 — SimFoundry 3단계 파이프라인 개요](https://arxiv.org/html/2606.28276/x2.png)

> "Figure 2: Method Overview. SimFoundry extracts per-object relevant information (segmentation masks, depth, etc.), generates 3D visual meshes via 2D-to-3D generation models, and compiles the final output scene by annotating relevant physical parameters and sanity checking the overall scene configuration in a physics simulator. SimFoundry additionally supports diverse simulated augmentations along these axes of variation on object, scene, and task: object cousins can be generated by modifying input objects in their image space and re-generating corresponding 3D meshes; scene cousins can augment the configuration of objects; and task cousins can propose viable interactions within the scene." (§3)

(한 그림이 Extraction–Generation–Augmentation 전 단계와 cousins 3축을 함께 보여 주는 시스템 다이어그램입니다.)

**Extraction (추출)** — 입력은 raw RGB 비디오 하나입니다. 대표 프레임(기본: frame 0)을 고르고 깊이를 추정해 장면 포인트클라우드를 만든 뒤, 물체를 하나씩 분할–제거–인페인팅하는 반복으로 전경을 분해합니다.

> "We first convert the input into a representative RGB frame $`\mathbf{I}_{s}\,`$ and estimate a corresponding depth map $`\mathbf{D}_{s}\,`$ using off-the-shelf depth estimation models $`V_{im2depth}`$ [90, 50]." (§4)

(단안 깊이 모델로 RGB-D 를 만들고 카메라 내부 파라미터 $`\mathbf{K}`$ 로 포인트클라우드 $`\mathbf{P}_{s}`$ 를 얻습니다. 이후 지면 평면을 분할해 시뮬레이터 월드 프레임과 정렬합니다.)

- **반복 분해** — 장면 이해 VLM $`V_{scene}`$ 이 물체를 검출하고, $`V_{seg}^{image}`$ (SAM3) 가 전경 물체를 하나씩 분할합니다. 물체마다 마스크 $`m_{i}`$ 와 RGB·깊이 픽셀을 추출한 뒤, 이미지·깊이 인페인팅으로 그 물체를 지우고 다음 물체를 검출하는 과정을 전경이 없어질 때까지 반복합니다. 출력은 per-object RGB-D crop + 마스크입니다.

**Generation (생성)** — 물체별 crop 에서 3D 메시를 생성하고 장면에 되돌려 놓습니다.

> "Given each object crop $`p_{i}^{rgb}`$ , we use $`V_{image}`$ to upsample and a 2D-to-3D mesh model $`V_{mesh}`$ to generate a visual mesh $`\mathcal{M}_{i}`$ ." (§4)

(업샘플된 crop 을 Hunyuan2.1 / TRELLIS.2 같은 이미지-투-3D 모델에 넣어 시각 메시를 만들고, 장면 RGB-D·마스크·포인트클라우드 기하에 맞춰 포즈를 정렬한 뒤 FoundationPose 류의 $`V_{pose}`$ 로 6D 포즈를 정밀화합니다.)

- **물리 주석과 안정화** — 각 메시의 충돌 기하는 CoACD 로 생성하고, 질량·마찰 같은 물리 속성은 $`V_{scene}`$ 질의로 채웁니다. 조립된 장면을 PyBullet 에 스폰해 (스텝마다 속도를 0 으로 강제하며) 물체가 정착할 때까지 시뮬레이션을 진행하고, 최종 포즈를 캐시해 이후 초기화의 물리 안정성을 보장합니다 (§E.4). 완성 장면은 IsaacLab 등 다운스트림 시뮬레이터로 내보냅니다.
- **Foundation model 슬롯 (§E.2)** — $`V_{im2depth}`$: DepthAnything3(단안)/FoundationStereo(스테레오), $`V_{seg}^{image}`$: SAM3, $`V_{scene}`$ · $`V_{articulation}`$: Gemini-Pro-3, $`V_{image}`$: Gemini-Pro-3-Image-Preview, $`V_{inpaint}^{depth}`$: PriorDepthAnything, $`V_{mesh}`$: Hunyuan2.1 / TRELLIS.2, $`V_{pose}`$: FoundationPose, $`V_{seg}^{mesh}`$: P3-SAM(또는 Segment Any Mesh / Partfield), $`V_{seg}^{video}`$: SAM2, $`V_{inpaint}^{video}`$: VOID. 모두 실행 중 교체 가능한 모듈로 선언되어 있습니다.

### 관절 객체 생성 파이프라인

서랍·전자레인지 같은 관절 물체는 별도 모듈이 처리합니다 (§E.3, Articulate Anymesh / Articulate Anything 확장). 절차는 (1) 다각도 렌더를 VLM 에 보여 관절 가능한 부품과 관절 타입(prismatic/revolute)을 나열, (2) 메시 분할 모델로 face 단위 세그먼트를 얻고 — TRELLIS.2 메시의 내부 구조까지 face-adjacency 다수결로 라벨 전파 — 과분할된 세그먼트를 색으로 구분해 다시 렌더한 뒤 VLM 이 부품별로 병합, (3) VLM 이 URDF 생성 python API 를 호출하는 코드를 작성해 관절 축·배치를 예측하는 것입니다. 생성된 URDF 로 관절을 움직인 영상을 별도의 critic VLM 이 채점하고, 임계 점수를 넘을 때까지 피드백-개선 루프를 돕니다. 마지막으로 부품 부피를 근거로 링크 질량·관절 마찰·감쇠를 VLM 이 주석합니다.

![Figure E.1 — 관절 생성 + 3DGS 배경 파이프라인](https://arxiv.org/html/2606.28276/x6.png)

> "Figure E.1: Articulation and 3DGS Background Pipeline Overview. SimFoundry generates articulated objects by first decomposing a pre-existing mesh into subsequent parts, which are then annotated with relevant joint types, locations, and ranges via a VLM. SimFoundry also can automatically generate a high-fidelity 3DGS background by first generating a synthetic video with removed foreground, extracting extrinsics, and training a 3DDGS to reconstruct the scene geometry." (§E)

(관절 생성의 actor-critic 루프와 자동 배경 재구성 파이프라인을 함께 보여 주는 부록 다이어그램입니다.)

### 배경 재구성 (3DGS) 파이프라인

전경 파이프라인은 물체 메시만 만들므로, 포토리얼 배경은 3D Gaussian Splat 으로 별도 재구성해 결합합니다 (§E.5). 두 경로를 지원합니다.

- **자동 파이프라인** — Extraction 과 같은 단일 비디오에서 전경을 비디오 분할( $`V_{seg}^{video}`$ )로 마스킹하고 2-pass 비디오 인페인팅으로 지운 뒤, DepthAnything3 로 metric depth·카메라 포즈를 청크 단위 복원(Umeyama 유사변환으로 청크 병합)하고, depth 감독( $`L1`$ depth loss + photometric loss)으로 splat 을 학습해 유도된 강체 변환으로 시뮬레이터 월드에 등록합니다. 추가 촬영·사용자 입력이 필요 없습니다.
- **수동 파이프라인** — 전경 물체를 물리적으로 치운 두 번째 비디오를 COLMAP 기반 표준 Nerfstudio 파이프라인으로 처리해 splat 을 학습하고, 인터랙티브 에디터에서 $`\mathrm{SE}(3)`$ 변환+등방 스케일로 수동 정렬합니다. 인페인팅 아티팩트가 없어 텍스처 없는 평면·실루엣에서 더 선명합니다.

자동 파이프라인의 화질을 좌우한 단일 최대 요인은 per-camera 포즈 최적화였다고 명시합니다.

> "We find this to be the single most impactful design choice for splat sharpness: without it, the splat is consistently blurry regardless of frame count, resolution, or iteration budget." (§E.5.1)

(원 스트림 포즈와 인페인팅 스트림 depth 사이의 잔여 어긋남을 카메라별 $`\mathrm{SO}(3)\!\times\!\mathbb{R}^{3}`$ 미세 보정으로 흡수하는 설계로, 프레임 수·해상도·반복 횟수보다 이 한 가지가 선명도를 결정했다는 실무적 발견입니다.) 한편 로봇 실험에서는 3DGS 의 근거리 클리핑 문제와 렌더링 지연 때문에 Scaniverse 류 앱으로 만든 메시 배경도 병용했습니다 (§C).

### 디지털 커즌 증강

용어 정의부터 원문이 명확히 구분합니다.

> "We define digital twins as being strict replicas of the geometry and object layouts of a real-world scene. In contrast, digital cousins [17, 55] are virtual scenes that maintain the semantic and geometric affordances of a real-world scene without explicitly modeling it, and serve as a form of object instance randomization." (§3)

(트윈은 "엄격한 복제", 커즌은 "affordance 만 보존한 변형" — 커즌이 구조화된 인스턴스 랜덤화라는 위치 규정이 이후 모든 학습 실험의 전제가 됩니다.)

- **Object cousins (§F.1)** — 분리된 물체 이미지 + 원 장면 이미지를 입력으로, VLM 이 (1) 물체를 grasp affordance 기준의 기능 부품(손잡이·뚜껑·몸체 등)으로 분해하고, (2) 부품별로 geometry / topology / visual appearance 3차원의 변형 후보를 제안하며 — 비현실적 변형은 금지 — (3) 이미지 생성 모델이 지정 부품만 바꾼 이미지를 합성하고, (4) VLM 이 실세계 개연성·장면 일관성을 검증해 통과한 것만 3D 메시로 재생성합니다. 프롬프트 템플릿 전문이 Fig F.1 에 공개됩니다.
- **Scene cousins (§F.2)** — 앵커 물체를 정하고 다른 물체마다 `[LeftOf, RightOf, InFrontOf, Behind, OnTopOf, Inside]` 중 공간 술어를 (복수 조합 가능하게) 샘플링해 의미 있는 대안 배치를 만듭니다. BEHAVIOR 자산 라이브러리에서 질량·부피·밀도·카테고리로 필터한 distractor 물체를 충돌 없이 추가할 수 있습니다.
- **Task cousins (§F.3)** — 재구성 장면의 2D 이미지 + 상호작용 가능 물체 목록 + 로봇 제약(그리퍼 길이, 단완/양완)을 VLM 에 주고, 초기 상태에서 의미 있는 상태 변화를 요구하는 태스크들을 술어 기반 goal 조건(OnTop, Inside, Under 등)으로 제안·컴파일하게 합니다. 산출물은 데이터 생성에 바로 쓰이는 표준화 태스크 정의 파일이며, 프롬프트 템플릿은 Fig F.2 에 공개됩니다.

### 평가 지표

sim 평가의 실환경 예측력은 두 지표로 측정합니다 (§J.2). 정책 집합 $`\Pi = {\pi_{1},\ldots,\pi_{N}}`$ 의 실환경 점수 $`x_{i}`$ 와 sim 점수 $`y_{i}`$ 에 대해, 선형 추세 보존은 Pearson 상관 (식 1):

$$\rho(\mathbf{x},\mathbf{y})=\frac{\sum_{i=1}^{N}(x_{i}-\bar{x})(y_{i}-\bar{y})}{\sqrt{\sum_{i=1}^{N}(x_{i}-\bar{x})^{2}}\sqrt{\sum_{i=1}^{N}(y_{i}-\bar{y})^{2}}}$$

순위 보존은 MMRV (식 2):

$$\mathrm{MMRV}(\mathbf{x},\mathbf{y})=\frac{1}{N}\sum_{i=1}^{N}\max_{j\in\{1,\ldots,N\}}\left[|x_{i}-x_{j}|\cdot\mathbb{1}\left(\mathbb{1}[y_{i}<y_{j}]\neq\mathbb{1}[x_{i}<x_{j}]\right)\right].$$

(MMRV 는 sim 이 두 정책의 순위를 실환경과 다르게 매길 때, 그 뒤집힌 쌍의 실환경 점수 차 최대치를 벌점으로 평균합니다 — 실환경 성능 차가 큰 정책 쌍을 뒤집을수록 크게 벌점을 받습니다.) 성공 판정은 태스크 기준 전부를 완수해야 1 인 이진 성공이며, FAQ 는 normalized reward 대신 이진 성공이 재현 충실도의 더 엄격한 검정이라고 명시합니다 (§B).

평가 프로토콜은 분산을 통제합니다.

> "For each task, we run 25 rollouts and each of the objects has a defined spatial reset distribution. The spatial distribution for each object is uniformly divided into a 5-by-5 grid, yielding 25 positions per object." (§J.1)

(물체별 5×5 격자에서 비복원 샘플링한 25개 초기 위치 + 회전을 태스크의 모든 체크포인트에 고정 적용하고, sim 과 real 은 위치의 "범위" 를 맞추되 정확한 좌표 일치는 의도적으로 피해 분포적 대응을 봅니다.)

### 학습 셋업

sim-to-real 학습 데이터는 인간 데모 소량을 MimicGen 으로 증식해 만듭니다.

> "For a given task, we first collect a small number ( $`\sim 10-15`$ ) of demonstrations via human operator-controlled JoyLo [35] systems. Then, we augment those demonstrations using MimicGen [58], both increasing the trajectory diversity (via demonstration count) as well as visual diversity by applying domain randomization: material randomization, camera pose randomization, and (specifically in the DROID setup) table height randomization." (§H.1)

(궤적 다양성은 MimicGen 증식으로, 시각 다양성은 재질·카메라 포즈·(DROID 한정) 테이블 높이의 도메인 랜덤화 (DR) 로 확보합니다.)

> "Each policy is trained with a batch size of 256, a learning rate of $`1e-5`$ , and for 10k gradient steps. In simulation, the policies are evaluated every 1k steps, and the best-performing checkpoint is evaluated in the real world." (§H.2)

(DROID 실험은 DROID 사전학습 joint-position 버전 π0 / π0.5 를 finetune 하고, 1k 스텝마다 sim 평가로 최고 체크포인트를 골라 실기에 배치합니다 — sim 평가를 체크포인트 선택기로 쓰는 실무 루프입니다. YAM 태스크는 관측 = 관절 proprioception + 상단 고정 카메라 + 손목 카메라 RGB, 액션 = N-DOF 관절 위치 + 1-DOF 그리퍼 명령의 플로우 매칭 정책을 from scratch 로 40k 스텝 학습합니다.)

---

## 📊 실험 설정과 결과

실험은 DROID(Franka 단완) 와 YAM(양완 워크셀) 두 임보디먼트, 7개 태스크(단순 pick-place, 관절 물체, 다단계, 양완, 언어 추종)에서 수행됩니다.

![Figure 4 — 태스크 구성과 real↔sim 상관 (PolaRiS 대비)](https://arxiv.org/html/2606.28276/x4.png)

> "Figure 4: Tasks and Real-to-Sim Policy Evaluation correlations. (Left) We apply SimFoundry to a DROID setup using a single Franka arm (top two rows), and a bimanual setup with two YAM arms (bottom row). Our tasks span multiple types of manipulation, including multi-step, articulated object interaction, and bimanual coordination (Clear Table not shown, more details in Appendix I). (Right) SimFoundry outperforms the state-of-the-art baseline PolaRiS [32] in simulation-based evaluation correlations. Each marker shape represents a different task from the left. Additional details in Appendix G and Figure G.1." (§5)

(오른쪽 산점도에서 SimFoundry 평가점들이 대각선(완전 일치)에 밀착하고 PolaRiS 점들은 sim 점수가 일괄 저평가되는 모습이, 아래 상관 수치의 시각적 근거입니다.)

### Real-to-Sim 평가 상관

> "As shown in Figure 4, SimFoundry evaluations closely match real-world results and preserve policy rankings, with a mean Pearson correlation of 0.911 and MMRV of 0.018 (Table G.1)." (§5.1)

(5개 정책 — π0, π0.5, GR00T N1.6/N1.7, DreamZero — 을 태스크별로 실기 25회 vs sim 25회 평가한 결과의 평균입니다.)

Table G.1 (SimFoundry, 성공률 %):

| Task | π0 Real/Sim | π0.5 Real/Sim | GR00T N1.6 Real/Sim | GR00T N1.7 Real/Sim | DreamZero Real/Sim | Pearson r ↑ | MMRV ↓ |
|---|---|---|---|---|---|---|---|
| Stack Dishware | 100 / 34 | 100 / 64 | 40 / 0 | – | – | 0.883 | 0.000 |
| Store Marker | 48 / 4 | 60 / 20 | 32 / 0 | – | – | 0.915 | 0.000 |
| Throw Away Trash | 20 / 0 | 48 / 4 | 0 / 0 | – | – | 0.910 | 0.067 |
| Serve Fruits | 0 / 4 | 72 / 80 | 4 / 20 | 40 / 32 | 8 / 12 | 0.960 | 0.016 |
| Cup in Bowl | 88 / 56 | 100 / 92 | 68 / 40 | 92 / 92 | 100 / 92 | 0.907 | 0.016 |
| Marker in Cup | 40 / 40 | 92 / 88 | 28 / 28 | 88 / 88 | 88 / 80 | 0.995 | 0.008 |
| Clear Table | 0 / 12 | 40 / 36 | 0 / 0 | 8 / 28 | 16 / 28 | 0.810 | 0.016 |

읽기: 상관은 높지만 절대값 보정(calibration)은 아닙니다 — finetune 태스크(위 3개)에서 sim 절대 성공률이 실기보다 체계적으로 낮습니다(예: Stack Dishware π0 실기 100 vs sim 34). 순위·추세 예측 도구이지 절대 성공률 예측기가 아니라는 점이 표에서 직접 읽힙니다.

**PolaRiS 대비** — 동일 정책·동일 프로토콜로 PolaRiS 재구성 장면에서 평가한 비교 (Table G.2 요약):

| Task | SimFoundry Pearson r | PolaRiS Pearson r | SimFoundry MMRV | PolaRiS MMRV |
|---|---|---|---|---|
| Stack Dishware | 0.883 | 0.500 | 0.000 | 0.200 |
| Store Marker | 0.915 | 0.822 | 0.000 | 0.053 |
| Throw Away Trash | 0.910 | – | 0.067 | 0.253 |
| Serve Fruits | 0.960 | 0.480 | 0.016 | 0.288 |
| Cup in Bowl | 0.907 | -0.396 | 0.016 | 0.280 |
| Marker in Cup | 0.995 | 0.512 | 0.008 | 0.176 |
| Clear Table | 0.810 | -0.037 | 0.016 | 0.352 |

> "We use the same protocol to evaluate the same real-world policies in PolaRiS, and find that SimFoundry has a mean Pearson correlation that is over 0.59 higher than PolaRiS." (§5.1)

(PolaRiS 에서는 대부분 정책의 sim 성공률이 0 근처로 붕괴해(특히 finetune 태스크) 상관이 무너집니다. 단, PolaRiS 장면은 저자들이 외부 도구로 직접 재구성·수정한 커스텀 환경이라는 비교 조건의 비대칭은 §J.3 에 상세히 기록되어 있습니다.)

**서브태스크 평가** — sim 의 임의 상태 리셋 능력을 활용해, 앞 서브태스크가 완료된 상태에서 시작하는 평가 프로토콜:

> "We introduce a sub-task evaluation procedure that increases policy eval correlations from a mean Pearson score of 0.90 to 0.95." (§5.1)

(Table G.3 기준 finetune 태스크 평균 Pearson 0.902→0.951. 예: Store Marker 에서 서랍이 이미 열린 상태에서 시작하면 π0.5 는 sim·real 모두에서 거의 항상 나머지를 완수 — 장기 태스크의 병목 서브태스크를 분리 진단하는 도구가 됩니다.)

### Sim-to-Real 학습

![Figure 5 — cousins 3축의 정책 성능 기여](https://arxiv.org/html/2606.28276/x5.png)

> "Figure 5: SimFoundry Data Diversity Improves Policy Performance. (A) Across multiple robot embodiments and multiple tasks, leveraging additional object cousins [17] improves direct Sim-to-Real policy transfer on the original target scene objects and additional held-out unseen objects. (B) Scene cousins improve policy performance on the original scene and allow policy transfer to cousin scenes. (C) Adding task cousins improves performance on related downstream tasks by enabling intra-task transfer. Note: Pot refers to the Pot on Stove task, Trash refers to the Throw Away Trash task and Marker is for the Store Marker task." (§5)

(cousins 3축이 각각 어떤 일반화 축(미지 물체 / 신규 배치 / 인접 태스크)을 사는지 요약하는 결과 그림입니다.)

> "Across both YAM and DROID, policies trained on SimFoundry data transfer effectively to real scenes, reaching $`99\%`$ success on Pot on Stove with YAM and $`100\%`$ success on Stack Dishware with DROID (Table G.4)." (§5.2)

(YAM 은 from-scratch 플로우 매칭 정책으로, DROID 는 π0.5-DROID 체크포인트의 sim-only finetune 으로 달성한 zero-shot 실기 수치입니다.)

**Object cousins ablation** (Table G.4, Twin vs +9 cousins, 성공률 %):

| 플랫폼 | Task | 설정 | Twin | +9 Cousins |
|---|---|---|---|---|
| YAM | Pot On Stove | Real Twin | 91 | 99 |
| YAM | Pot On Stove | Real Cousins | 14 | 64 |
| YAM | Throw Away Trash | Real Twin | 0 | 28 |
| DROID | Stack Dishware | Real Cousins | 88 | 100 |
| DROID | Store Marker | Real Twin | 4 | 20 |
| DROID | Throw Away Trash | Real Twin | 0 | 20 |

> "Adding object cousins yields a $`50`$ -point real-world gain on held-out Pot on Stove objects, and improves DROID performance in both sim and real with gains up to $`20`$ points on Throw Away Trash." (§5.2)

(각 행이 분리하는 것: Real Twin 행은 "cousins 데이터가 원 물체 성능도 올리는가" (예 — 다양성의 정규화 효과), Real Cousins 행은 "미지 실물 물체로 일반화하는가" (예 — 14→64 가 최대 사례). Table G.8 의 1/3/9 cousins 스윕은 개수 증가가 대체로 단조 개선임을 보입니다.)

**Scene cousins** (Table G.5, DROID sim, twin only vs +scene cousin): Stack Dishware-cousin 28→64, Store Marker-cousin 0→16, Throw Away Trash 8→36 / Trash-cousin 0→36.

> "Scene cousins also enable transfer to novel layouts, reaching $`16\%`$ success on Store Marker cousin scenes where the twin-only policy achieves $`0\%`$ ." (§5.2)

(트윈 배치만 본 정책은 신규 배치에서 전멸하고, 술어 기반 재배치 데이터가 이를 되살립니다 — 배치 과적합이 실재함을 보이는 대조군입니다.)

**Task cousins** (Table G.6, DROID sim, 총 데모 수 고정): Stack Dishware 80→100(+7 tasks 이후 포화), Store Marker 20→60, Throw Away Trash 8→68 (+13 tasks).

> "With the total number of demonstrations fixed, replacing some target-task data with related task-cousin demonstrations improves downstream simulation performance, especially on harder tasks: in simulation, 13 task cousins increase success on Throw Away Trash by $`60\%`$ and Store Marker by $`40\%`$ (Figure 5C)." (§5.2)

(데이터 총량을 고정한 채 타깃 태스크 데모 일부를 인접 태스크 데모로 "대체" 해도 오르므로, 이득이 단순 데이터 증가가 아니라 태스크 간 전이에서 온다는 설계입니다.)

**Co-training** (Table G.7): sim-only / real-only / co-train 비교.

> "For example, $`\pi_{0.5}`$ real-world success on Store Marker increases from $`60\%`$ to $`92\%`$ , while $`\pi_{0}`$ gains $`36\%`$ sim success on Throw Away Trash." (§5.2)

(real-only 대비 co-train 이 대부분 셀에서 우세 — 예: π0 Throw Away Trash real 20→76, π0.5 동일 태스크 real 48→96. sim 데이터가 real 데모의 대체재이자 보완재로 작동합니다.)

**멀티태스크** (Table 2, 성공률 %):

| 설정 | π0.5-DROID | π0.5-FT | π0.5-DROID-FT |
|---|---|---|---|
| Sim | 30 | 51 | 61 |
| Sim – held out | 37 | 45 | 33 |
| Real | 28 | 45 | 46 |
| Real – held out | 26 | 29 | 26 |

> "SimFoundry-finetuned policies outperform the base DROID checkpoint by up to $`31\%`$ in simulation and $`18\%`$ in the real world, and $`\pi_{0.5}`$ -FT reaches $`29\%`$ success on held-out tasks without task-specific demonstrations (Table 2)." (§5.2)

(클러터 장면 1개 → VLM 제안 13개 태스크 → 태스크당 인간 데모 10개 + MimicGen 100개로 만든 sim 데이터만으로 finetune 한 결과입니다. 사전학습 체크포인트의 기여를 묻는 FAQ 도 직접 수치를 답합니다:)

> "On Store Marker and Throw Away Trash, both checkpoints get a $`0\%`$ success rate, while for Stack Dishware, $`\pi_{0}`$ -DROID gets $`52\%`$ and $`\pi_{0.5}`$ -DROID gets $`48\%`$ success rate (improving to $`100\%`$ with sim-only finetuning)." (§B)

(어려운 태스크에서는 DROID 사전학습만으로 0% — 성능이 사전학습이 아니라 SimFoundry finetune 데이터에서 왔다는 통제 실험입니다.)

### 재구성 충실도·처리량

> "For instance, SimFoundry achieves higher F1 score (0.81–0.92) than SAM3D (0.66–0.71), lower chamfer distance and position error, showing that the pipeline recovers precise scene geometry without human input." (§5.3)

(YCB 물체 12개 장면 — 가림 난이도 Easy/Med/Hard — 에서 quasi-ground-truth 포즈 대비 3D 기하 지표 비교입니다.)

Table L.2 요약 (F1 Score ↑, 평균±표준편차):

| Difficulty | SAM3D Zero Shot | SimFoundry Zero Shot | SimFoundry Tuned (3min/Obj) |
|---|---|---|---|
| Easy | 0.71 ± 0.15 | 0.92 ± 0.071 | 0.99 ± 0.0069 |
| Medium | 0.66 ± 0.18 | 0.87 ± 0.089 | 0.97 ± 0.026 |
| Hard | 0.68 ± 0.14 | 0.81 ± 0.071 | 0.93 ± 0.049 |

> "The pipeline reconstructs objects at an average rate of roughly 5 minutes per object across diverse real-world scenes (Table L.4), and an additional 3 minutes of per-object operator tuning yields consistent gains on every metric (e.g. F1 scores rise to 0.93–0.99, as shown in Table L.2), demonstrating that fidelity can be traded against effort on demand." (§5.3)

(RTX 3090 24GB 1대 기준 처리량이며, "완전 자동 F1" 과 "물체당 3분 튜닝 F1" 사이의 갭이 시스템의 인간-노력 다이얼입니다. 배경 파이프라인 비교(Table L.6)에서는 자동 경로가 PSNR/SSIM/정렬(NCC)에서 수동 경로보다 우세하지만, 이는 자동 경로가 원 촬영 시점을 해석적으로 재현하기 때문이라고 부록이 해석합니다.)

---

## ⚖️ 한계

- **Foundation model 상속 실패 모드** — "Our system relies heavily upon off-the-shelf foundation models." (§6) 라고 저자가 명시하듯, 파이프라인의 상한과 하한이 모두 외부 모델에 묶여 있습니다. 모듈러 교체가 장점인 동시에, 어떤 단계도 자체 학습으로 개선할 수 없어 실패 진단이 "어느 슬롯의 모델 탓인가" 로 환원되는 구조적 취약점입니다.
- **폐쇄 VLM 비결정성** — 모든 VLM 이 원격 서드파티 API(Gemini-Pro-3)로 질의되어 동일 입력이 실행마다 다른 출력을 낼 수 있고, 실제로 인페인팅에서 물체가 변형·복제되는 사례를 관찰했다고 밝힙니다 (§C). 재구성 결과의 재현성이 상용 API 버전·온도에 종속된다는 뜻으로, 벤치마크 인프라로서는 뼈아픈 속성입니다.
- **탁상 평면 가정** — "Our physics-stability procedure assumes that objects rest on a single flat reference surface, which restricts the pipeline to tabletop-style scene layouts." (§C) 다층 선반·비평면 지지면은 안정화 단계가 처리하지 못하므로, 현재 증거는 탁상 조작 도메인에 한정됩니다.
- **단안 스케일·관절 분할 병목** — 단안 입력에서는 복원 기하의 스케일·형상이 실장면과 어긋날 수 있고 (§C), 관절 생성은 image-to-mesh 산출물의 3D 분할 정확도에 종속됩니다 — 내부 구조가 가려진 물체에서 특히 취약합니다.
- **배경 파이프라인 비용** — 자동 배경 경로의 2-pass 비디오 인페인팅은 단일 GPU 에서 장면당 약 90분이 소요됩니다 (§C). 멀티 GPU 병렬로 숨길 수 있다지만, "비디오 한 편이면 끝" 이라는 인상과 실제 비용 사이의 갭입니다.
- **상관 ≠ 보정 (추론된 갭)** — Table G.1 에서 finetune 태스크의 sim 절대 성공률은 실기보다 크게 낮습니다(Stack Dishware π0: real 100 vs sim 34). Pearson/MMRV 는 정책 "집합" 의 순위 신뢰도만 보장하므로, 단일 정책의 절대 성능 예측이나 소수(2–3개) 체크포인트 비교에는 통계적 근거가 얇습니다.
- **접촉 정밀도 미검증 (추론된 갭)** — 검증된 태스크는 모두 2지 그리퍼의 pick-place / 관절 물체 / 양완 협조이며, 접촉 집약적 (contact-rich) 정밀 조작·다지 조작은 등장하지 않습니다. 저자들 스스로 rendering-only 계열을 "higher-precision contact-rich tasks" 에 부적합하다고 비판하지만 (§D.1), SimFoundry 의 물리 충실도(CoACD 근사 충돌 + VLM 추정 질량·마찰)가 그 영역을 감당한다는 증거도 제시되지 않습니다.

---

## ♻️ 재현성

- **코드** — 본문에 코드 공개 언급이 없습니다. 프로젝트 페이지(https://research.nvidia.com/labs/gear/simfoundry/)가 초록에 명시되어 있으나, 본 분석 환경에서는 네트워크 정책으로 접근이 차단되어(`curl` → `CONNECT tunnel failed, response 403`) 코드 배포 여부를 확인하지 못했습니다. cousins 생성용 VLM 프롬프트 템플릿 전문은 부록 Fig F.1 / F.2 로 공개됩니다.
- **모델 의존성** — 파이프라인이 명시적으로 나열한 구성 요소: DepthAnything3, FoundationStereo, SAM3, SAM2, Gemini-Pro-3(-Image-Preview), PriorDepthAnything, Hunyuan2.1, TRELLIS.2, FoundationPose, P3-SAM, VOID, CoACD, PyBullet, IsaacLab, NerfStudio, COLMAP. 핵심 장면 이해·관절·cousins 제안이 모두 폐쇄형 Gemini API 에 걸려 있어 완전 재현은 API 접근 + 비결정성 감수를 전제합니다.
- **데이터** — 학습 데이터는 태스크당 인간 데모 10–15개(JoyLo/VR 텔레옵) + MimicGen 증식으로 생성되며, 데이터셋 자체의 공개 언급은 없습니다.
- **하드웨어** — 재구성: RTX 3090 24GB 1대(물체당 약 5분, 배경 인페인팅 약 90분/장면). 로봇: DROID(Franka Panda + ZED-2×2 + 손목 ZED-Mini), YAM 양완 워크셀(손목 RealSense D405×2 + 상단 카메라). 정책: π0 / π0.5 (DROID joint-position 체크포인트), GR00T N1.6/N1.7, DreamZero, from-scratch 플로우 매칭.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0 (VLA 데이터셋·벤치마크) — 주 pillar.** 본 논문은 방법이 아니라 평가·데이터 생성 인프라이며, P0 의 스카우팅 대상 분류 (e) "benchmarks / eval harnesses" 에 정확히 떨어집니다.
  - **D26(benchmark/eval scouting scope) — 직접 타격.** D26 v1 은 sim(ManiSkill / Isaac Lab / Robocasa)과 real(RoboArena-class) 스위트를 함께 추적하도록 정의합니다. SimFoundry 는 그 중간 지대 — "내 실험실 장면의 트윈에서 하는 sim 평가가 실기 순위를 예측한다(Pearson 0.911)" — 를 실증한 real-to-sim 평가 계열(PolaRiS, SIMPLER 후속)의 현행 최전선으로, D26 스카우팅 렌즈가 커버해야 할 하위 계열임을 확인시킵니다. IsaacLab 내보내기를 지원하므로 MASTER §4.2 의 Isaac Sim/Lab 스택과 도구 수준에서 호환됩니다.
  - **D24(priority data axis) — 간접.** SimFoundry 가 만드는 데이터는 3인칭 로봇 sim 궤적으로, D24 v1 의 우선축(egocentric 인간 비디오)이 아니라 "robot-action 보충 코퍼스" 버킷입니다. 우선순위를 흔들 증거는 아니지만, 보충 축의 생산 단가를 크게 낮추는 도구입니다.
  - **D27(license/usability bar) — 현재 미달.** 코드·데이터 공개가 확인되지 않고 핵심 단계가 폐쇄형 Gemini API 에 종속되므로, D27 의 사용성 기준으로는 지금 시점에 핀 승격이 불가합니다.
- **P3(Hand-level System0) / D18(System0 sim2real) — 건드리지 않습니다.** SimFoundry 의 sim2real 은 장면 수준(기하·배치·시각)이며, D18 이 다루는 접촉 수준(지문 점탄성 vs PhysX point contact) 갭은 범위 밖입니다. 다지 손·촉각 모달리티는 등장하지 않습니다.
- **Identity 관점** — MASTER §3.1 Vision 의 "evaluation infrastructure enabling scalable + reproducible iteration" 항목을 지지하는 인프라 증거이며, Identity 의 antagonist(보정 모듈, RL-as-core, monolithic decoder) 논쟁과는 직교합니다. 평가 대상에 world-action 모델 DreamZero 가 포함된 점은 P5 추적 문헌의 평가 방법론 참고 사항 정도입니다.

---

## ✨ 핀 논문 대비 델타

- **vs vla-eval ([arXiv:2603.13966](https://arxiv.org/abs/2603.13966), P0 §5 핀, D26)** — vla-eval 은 "이미 존재하는" 14개 sim 벤치마크의 실행·프로토콜을 표준화하는 하니스이고, 벤치마크 장면 자체는 주어진 것으로 둡니다. SimFoundry 의 델타는 반대편 절반 — 벤치마크 "장면" 을 사용자 실환경 비디오에서 자동 생성하고, 그 sim 점수가 실기 점수와 상관함을 (실기 대조 시행으로) 검증하는 것 — 입니다. 두 도구는 경쟁이 아니라 스택의 상보 층위입니다.
- **vs ManiSkill 3 ([arXiv:2410.00425](https://arxiv.org/abs/2410.00425), P0 §5 핀, D26)** — ManiSkill 3 은 수작업 큐레이션된 범용 sim 벤치마크로 "표준 태스크에서의 비교" 를 제공합니다. SimFoundry 는 "내 태스크·내 장면의 트윈" 을 만들어 배치 직전 정책 선별에 쓰는 도구라는 점에서 용도가 다릅니다 — 범용 리더보드가 아니라 lab-specific 평가 프록시입니다.
- **vs DexMimicGen ([arXiv:2410.24185](https://arxiv.org/abs/2410.24185), P0 §5 methodology base, D24)** — DexMimicGen/MimicGen 은 "주어진 sim 장면에서" 데모를 증식하는 방법입니다. SimFoundry 는 그 상류 — 장면·물체·태스크 자체의 생성과 다양화(cousins) — 를 자동화하고 MimicGen 을 내부 엔진으로 소비합니다. 데이터 스케일링 레버가 궤적 수에서 환경 다양성으로 한 단계 올라간 것이 델타입니다.

---

## ⚙️ 의사결정 함의

- **체크포인트 선별 루프 도입** — 이 논문이 맞다면, 우리 실기 평가 예산의 상당 부분을 "트윈 sim 평가로 사전 순위화 → 상위 체크포인트만 실기" 루프로 대체할 수 있습니다. 구체적으로: 학습 중 `eval_interval = 1000` gradient step 의 sim 평가(§H.2 의 1k-step 프로토콜), 평가 리셋 분포는 물체별 5×5 격자 25 rollout 고정 시드(§J.1) 를 Isaac Lab 평가 env cfg 의 reset range 로 이식하는 것입니다.
- **Phase 2 (tool articulation) 평가 인프라 후보** — MASTER §3.5 의 5-tool 평가셋을 SimFoundry 식 관절 트윈(메시 분할 + VLM 관절 생성 + critic 루프)으로 디지털화하면, 서랍·트리거류 도구의 실기 전 정책 비교가 가능해집니다. 단 아래 ⚠️ 의 접촉 충실도 검증이 선행 조건입니다.
- **보고 지표 추가** — sim 프록시 평가를 도입하는 순간부터 Pearson $`r`$ + MMRV (식 1–2) 를 우리 실기 대조 시행과 함께 보고하는 것이 표준이 되어야 합니다. 특히 장기 태스크(도구 조작 4-스텝 rubric)에는 §G.1.1 의 "선행 서브태스크 완료 상태에서 시작" 평가를 병용해 병목 서브태스크를 분리 진단합니다.
- **데이터 파이프라인** — cousins 류 환경 다양화는 P4 D22(사전학습 corpus 구성)의 corpus 가 아니라 태스크 적응 단계의 sim 보충 데이터 레버입니다. 총 데모 수 고정 하에 타깃 태스크 데모 일부를 인접 태스크 데모로 대체하는 Table G.6 프로토콜(태스크 커즌 +13개, 성공률 최대 +60%p)은 우리 finetune 데이터 믹스 설계에 바로 시험 가능한 레시피입니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 상관의 표본 크기** — Pearson/MMRV 는 태스크당 정책 5개로 계산된 값입니다. 우리가 흔히 비교하는 2–3개 체크포인트로는 상관 자체가 정의되기 어렵습니다. 도입 전에 자체 체크포인트 ≥5개로 단순 그리퍼 태스크 하나에서 $`r`$ 을 직접 재보는 것이 첫 관문입니다 (실기 25회 × 5 정책 수준의 예산).
- **접촉 충실도 갭** — 검증된 것은 2지 그리퍼 pick-place·관절·양완입니다. 22-DOF Sharpa 손의 인핸드 조작은 PhysX point contact vs 지문 점탄성 갭(MASTER §4.2 known gap, Contact-Aware Neural Dynamics 문서화)이 지배해, 트윈 평가가 손 정책 순위를 오도할 수 있습니다. 체크: 파워 그래스프 1개 태스크의 트윈을 만들어 sim/real 성공률 갭이 본 논문의 그리퍼 태스크 갭(Table G.1) 범위 안인지 확인.
- **촉각 모달리티 부재** — 트윈은 시각·기하·강체 물리만 복원합니다. Deform Map 등 촉각 관측을 입력으로 받는 우리 정책은 sim 에서 그 채널을 만들 수 없어 평가 자체가 불가능합니다. 체크: vision-only ablation 정책이 스택에 존재하는지, 아니면 촉각 채널 zero-fill 평가가 순위를 보존하는지부터 확인.
- **파이프라인 재현 불가 리스크** — 코드 미공개 + Gemini-Pro-3 API 종속(비결정성 §C)이므로, "SimFoundry 를 쓴다" 는 현재로선 "우리가 동급 파이프라인을 재조립한다" 를 뜻합니다. 체크: 프로젝트 페이지의 코드 공개 여부 확인이 다른 모든 투자보다 선행되어야 합니다.
- **탁상 평면 가정과 우리 장면** — 물리 안정화가 단일 평면 지지를 가정하므로(§C), 거치대 위 태깅 머신 같은 Phase 2 비평면 픽스처는 재구성 대상에서 이탈할 수 있습니다. 체크: 도구 1개 + 거치대 장면의 트윈 생성이 성립하는지 소규모 시도.
- **MimicGen 의 준정적 가정** — 데모 증식이 서브태스크 splicing 에 의존하므로, 연속 접촉 유지가 본질인 인핸드 회전·슬립 억제 같은 동적 구간에는 증식 자체가 성립하지 않을 수 있습니다. 체크: 우리 태스크의 rubric 이 splicing 가능한 서브태스크 경계로 분해되는지 사전 검토.

---

## 💡 컨텍스트 제안

- **D26 스카우팅 렌즈 보강 (제안)** — D26 v1 의 sim/real 스위트 추적에 "real-to-sim 트윈 평가 계열(SIMPLER → PolaRiS → SimFoundry)" 을 명시적 하위 축으로 추가하는 것을 제안합니다. 이 계열은 범용 벤치마크와 달리 lab-specific 평가 프록시라는 별도 용도를 가지며, 본 논문이 그 계열의 상관 수치 기준선(0.911/0.018)을 세웠습니다.
- **핀 교체는 보류** — P0 §5 의 vla-eval / ManiSkill 3 핀과 용도가 상보적이고, 코드 미공개로 D27 사용성 기준을 충족하지 못하므로 현 시점 핀 승격은 제안하지 않습니다. **감시 트리거**: 프로젝트 페이지에 코드/자산이 공개되는 시점에 D26 참고 문헌(비핀 methodology base)으로 재평가.
- **Decision 이동 없음** — D24 의 egocentric 우선축, D18 의 접촉 sim2real 범위를 바꿀 증거는 본 논문에 없습니다.

---

> 💡 본 논문은 Design 비대상(tooling)이라 foundry 매핑 대상이 아닙니다. 가치는 분석 문서 본문으로 전달됩니다.
