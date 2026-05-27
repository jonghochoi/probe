# VLA lineage corpus 카탈로그 (further-pretrain corpus, D22)

> PROBE D22 "Multi-embodiment pretraining data" 의사결정 근거. lineage
> 2-튜플 *(초기 VLM 가중치) × (further-pretrain corpus)* 의 **두 번째 축**
> — VLM은 이미 학습된 채로 들어오고, 그 위에 VLA를 만들기 위해 *추가로
> 사전학습할 때* 쓰이는 corpus 후보를 정리한다. (파일명이 `pretrain_data`
> 였던 이유 — 단, "VLM 사전학습"이 아니라 *VLA further-pretrain* 임을
> 슬러그가 더 정확히 담도록 `lineage_corpus` 로 개명.)
>
> 각 데이터셋의 입력·출력 스키마 + 임베디먼트 메타 + 규모를 *scan 표*
> 와 *per-dataset `<details>` 카드* 의 하이브리드로 정리. PROBE 의
> dexterous hand 타깃 (Sharpa 22-DOF / xhand) 을 기준으로 hand-DOF
> 우선순위를 명시.
>
> v0.5 (2026-05). 공통 컬럼 표준 + 카드 schema 는
> `analysis/_catalogs/README.md` §2 참고. **Scan 표 마커는 의사결정
> 4-필드 (License · Scale · 데이터 유형 · Lineage 적층) 의 검증 상태**
> — 카드 안 부차 필드의 🔴/❓ 는 scan 마커에 영향 없음 (README §2-5).

---

## Scan 표

> Scan 표의 **Source-check** 컬럼은 *의사결정 4-필드* (License · Scale ·
> 데이터 유형 · Lineage 적층) 의 검증 상태만 종합한다. 카드 안의 부차
> 필드 (정확한 control rate · sub-dataset spec · 카메라 해상도 분포 등)
> 의 🔴/❓ 는 *scan 마커에 영향 없음* — `_catalogs/README.md` §2-5 참고.

| 데이터셋 | License | Access | 데이터 유형 | 규모 | Source-check | 우선도 |
|---|---|---|---|---|---|---|
| [Open X-Embodiment (OXE)](#oxe) | CC-BY-4.0 ✅ | 🟢 [web](https://robotics-transformer-x.github.io/) | 🤖 Robot action | 22 robots / 527 skills / 160266 tasks | 🟢 verified | ⭐⭐ baseline |
| [RT-1 (Robotics Transformer)](#rt1) | Closed ❌ | 🔴 — Google internal | 🤖 Robot action | ~130k traj | 🔴 unverified | ⭐ 폐쇄 |
| [BridgeData V2](#bridge-v2) | CC-BY-SA-4.0 ✅ | 🟢 [web](https://rail-berkeley.github.io/bridgedata/) | 🤖 Robot action | 60,096 traj / 24 env | 🟢 verified | ⭐⭐ 풍부 |
| [DROID](#droid) | CC-BY-4.0 ✅ | 🟢 [web](https://droid-dataset.github.io/) | 🤖 Robot action | 76k traj / 350h / 564 scenes / 84 tasks | 🟢 verified | ⭐⭐ 다양성 |
| [ManiSkill 3](#maniskill-3) | CC-BY-4.0 ✅ | 🟢 [web](https://maniskill.readthedocs.io/) | 🤖 Robot action (sim) | 12 domains / 30K+ FPS | 🟢 verified | ⭐ sim |
| [RoboMIND](#robomind) | TBD ❓ | 🟢 [web](https://x-humanoid-robomind.github.io/) | 🤖 Robot action | 107k traj / 479 tasks / 96 obj / 4 embodiments | 🟡 partial | ⭐⭐⭐ **dual-dex humanoid** |
| [AgiBot World](#agibot-world) | CC-BY-NC-SA-4.0 ❌ | 🟢 [web](https://agibot-world.com/) | 🤖 Robot action | 1M+ traj / 217 tasks | 🟢 verified | ⭐⭐⭐ **hand-DOF** |
| [DexMimicGen](#dexmimicgen) | CC-BY-NC-SA-4.0 ❌ | 🟢 [gh:NVlabs/dex-mimicgen](https://github.com/NVlabs/dex-mimicgen) | 🤖 Robot action (sim) | 21K synth / 60 human | 🟢 verified | ⭐⭐⭐ **finger sim** |
| [UniHand-2.0](#unihand-2) | Apache-2.0 ✅ | 🟢 [gh:BeingBeyond/Being-H](https://github.com/BeingBeyond/Being-H) | 🔀 Mixed | ~35,000h / 30 embodiments | 🟢 verified | ⭐⭐⭐ **human-video → hand** |
| [ALOHA / Mobile ALOHA](#aloha) | MIT ✅ | 🟢 [web](https://tonyzhaozh.github.io/aloha/) | 🤖 Robot action | TBD (50+ public HF subsets) | 🟡 partial | ⭐⭐ bimanual + high-FPS |
| [RH20T](#rh20t) | CC-BY-SA-4.0 ✅ | 🟢 [web](https://rh20t.github.io/) | 🤖 Robot action | 110K seq | 🟢 verified | ⭐ **촉각** |
| [LeRobot (aggregated)](#lerobot) | Apache-2.0 ✅ | 🟢 [hf:lerobot](https://huggingface.co/lerobot) | 🤖 Robot action | 50+ embodiments | 🟡 partial | ⭐⭐ 통합 |
| [HOI4D](#hoi4d) | CC-BY-NC-4.0 ❌ (추정) | 🟢 [web](http://www.hoi4d.top/) | 👤 Human video | 4000 seq / 800 obj / 16 cat / 2.4M RGB-D frames | 🟡 partial | ⭐⭐⭐ **hand-object 3D** |
| [ARCTIC](#arctic) | CC-BY-NC-SA-4.0 ❌ (추정) | 🟢 [web](https://arctic.is.tue.mpg.de/) | 👤 Human video | 2.1M frames bimanual | 🟡 partial | ⭐⭐⭐ **bimanual articulated** |
| [OakInk](#oakink) | CC-BY-NC-4.0 ❌ (추정) | 🟢 [web](https://oakink.net/) | 👤 Human video | 50K interactions / 100 obj from 1800 households | 🟡 partial | ⭐⭐⭐ **grasp + intent** |
| [AssemblyHands](#assemblyhands) | CC-BY-4.0 ✅ | 🟢 [web](https://assemblyhands.github.io/) | 👤 Human video | 3.0M frames / 490K ego | 🟢 verified | ⭐⭐⭐ **bimanual ego pose** |
| [Ego4D](#ego4d) | Ego4D license ⚠️ | 🟠 [web](https://ego4d-data.org/) | 👤 Human video | 3670h / 931 wearers / 74 loc · 9 countries | 🟢 verified | ⭐⭐ **VLM prior** |
| [Epic Kitchens 100](#epic-kitchens-100) | CC-BY-NC-SA-4.0 ❌ | 🟢 [web](https://epic-kitchens.github.io/100) | 👤 Human video | 100h / 20M frames / 90K actions / 700 videos / 45 env | 🟢 verified | ⭐⭐ **action label** |
| [EgoExoLearn](#egoexolearn) | CC-BY-4.0 ✅ | 🟢 [gh:OpenGVLab/EgoExoLearn](https://github.com/OpenGVLab/EgoExoLearn) | 👤 Human video | 120h paired | 🟢 verified | ⭐⭐ **ego-exo paired** |
| [MolmoAct2-BimanualYAM](#molmoact2-bimanualyam) | TBD (Apache-2.0 추정) ❓ | 🟢 [web](https://allenai.org/blog/molmoact2) | 🤖 Robot action | 34,500 demos / 720h bimanual | 🟡 partial | ⭐⭐⭐ **bimanual real** |
| [MolmoAct2-SO100/101](#molmoact2-so100-101) | TBD ❓ | 🟢 [web](https://allenai.org/blog/molmoact2) | 🤖 Robot action | TBD ❓ | 🟡 partial | ⭐ low-cost arm |
| [MolmoBot-Data](#molmobot-data) | TBD (Apache-2.0 추정) ❓ | 🟢 [web](https://allenai.org/blog/molmobot-robot-manipulation) | 🤖 Robot action (sim) | 1.7M traj / 11K+ obj / 94K+ env / 8 tasks | 🟡 partial | ⭐⭐ sim-only |
| [Ego-Exo4D](#ego-exo4d) | Ego-Exo4D license ⚠️ (추정) | 🟠 [web](https://ego-exo4d-data.org/) | 👤 Human video | 1286h paired / 740 participants / 13 cities | 🟡 partial | ⭐⭐⭐ **paired ego-exo skilled** |
| [Assembly101](#assembly101) | CC-BY-NC-4.0 ❌ (추정) | 🟢 [web](https://assembly-101.github.io/) | 👤 Human video | 4321 videos / 101 toys / 4 ego + 8 exo / 18M hand poses | 🟡 partial | ⭐⭐⭐ **bimanual assembly** |
| [HoloAssist](#holoassist) | CC-BY-4.0 ✅ | 🟠 [web](https://holoassist.github.io/) | 👤 Human video | 166h / 350 pairs | 🟢 verified | ⭐⭐ **task-assist NL** |

> 각 행의 이름 링크를 클릭하면 아래 *per-dataset 카드* 의 해당 anchor 로
> 점프합니다. 카드 안의 `<details>` 를 펼치면 Observations · Actions ·
> Embodiment · Annotation · Scale · Lineage 적층 · Source check · Sources
> 8개 H4 sub-section 이 보입니다.

---

## Per-dataset 카드

### <a id="oxe"></a>Open X-Embodiment (OXE)

<details>
<summary>22 robots × ~970k trajectories — gripper-only baseline, π0/OpenVLA/GR00T 가 공통 적층</summary>

#### Observations
- **cameras**: 1–3개 (sub-dataset 마다 상이); RGB; 보통 640×480, 1–30 Hz
- **proprio**: joint state 7–14 + gripper state 1
- **tactile**: ✗
- **language**: NL instruction (sub-dataset 마다 길이·형식 상이)

#### Actions
- **space**: EE delta pose (Cartesian) — sub-dataset 별 joint / EE 혼재 가능
- **dimension**: 7 (6-DOF + gripper)
- **control rate**: 1–30 Hz
- **gripper / finger**: 1-DOF parallel-jaw (전 sub-dataset)
- **bimanual**: ✗ (대부분 single-arm)

#### Embodiment
- 22 robots: Franka · UR · WidowX · Sawyer · Kuka iiwa · Google Robot 등
- **arm DOF**: 6–7
- **hand DOF**: **1** (gripper-only)
- **wrist**: sub-dataset 별 상이
- **mounting**: 고정대 + sub-dataset 별 외부 카메라

#### Annotation
- **NL instruction**: present (sub-dataset 별 길이 0–20 단어)
- **task intent**: ✗
- **episode segmentation**: trajectory 단위
- **sub-task labels**: ✗

#### Scale
- **skills**: **527** (verified)
- **tasks**: **160,266** (verified)
- **robots**: 22
- **institutions**: 21
- **trajectories**: TBD (paper §3.2 sub-dataset 별 분산 보고)
- **hours**: TBD
- **storage**: TBD (TFDS 전체)
- **collection period**: 2018–2023

#### Lineage 적층
π0 · π0.5 · π0-FAST · OpenVLA · Octo · GR00T N1 (부분) · Xiaomi-Robotics-0 (부분)

#### Source check
- 🟢 verified: License (CC-BY-4.0), 22 robots, 21 institutions, 527 skills (160266 tasks) — arXiv:2310.08864 abstract 직접 확인
- 🟡 partial: action space (sub-dataset 마다 상이; 통합 spec 은 RLDS), arm DOF 분포
- 🔴 unverified: 정확한 hours, storage size
- ❓ needs-human: sub-dataset 별 정확한 control rate / resolution 분포 표

#### Sources
- arXiv: [arXiv:2310.08864](https://arxiv.org/abs/2310.08864)
- 공식: [web](https://robotics-transformer-x.github.io/)
- HF mirror: [hf:jxu124/OpenX-Embodiment](https://huggingface.co/datasets/jxu124/OpenX-Embodiment) (비공식)

</details>

---

### <a id="rt1"></a>RT-1 (Robotics Transformer)

<details>
<summary>Google Everyday Robot × ~130k trajectories — gripper-only, RT-X 로 흡수</summary>

#### Observations
- **cameras**: 1 (head); RGB 320×256, ~10 Hz
- **proprio**: gripper state
- **tactile**: ✗
- **language**: NL instruction

#### Actions
- **space**: discrete action tokens (512 categorical bins)
- **dimension**: 7 → tokenized
- **control rate**: ~1 Hz (token emission)
- **gripper / finger**: 1-DOF parallel-jaw
- **bimanual**: ✗

#### Embodiment
- Google Everyday Robot (UR5e 계열 7-DOF arm + gripper)
- **arm DOF**: 7
- **hand DOF**: **1**

#### Annotation
- **NL instruction**: present
- **task intent**: ✗
- **episode segmentation**: trajectory 단위
- **sub-task labels**: ✗

#### Scale
- **trajectories**: ~130,000
- **tasks**: ~700+
- **collection period**: 2022 이전

#### Lineage 적층
RT-2 (자체 후속) · RT-X 통합 흡수 후 OXE 의 한 sub-dataset 으로 재배포

#### Source check
- 🟡 partial: trajectory / task count (paper)
- 🔴 unverified: 정확한 action token spec, control rate
- ❓ needs-human: RT-1 dataset 단독 다운로드 가능 여부 (현재 RT-X 통합 외 단독 release 미확인)

#### Sources
- arXiv: [arXiv:2212.06817](https://arxiv.org/abs/2212.06817)

</details>

---

### <a id="bridge-v2"></a>BridgeData V2

<details>
<summary>WidowX 250 × ~60k trajectories — VLM2VLA 의 NL-formatted fine-tune corpus</summary>

#### Observations
- **cameras**: 2 (외부 + wrist 옵션); RGB 1280×720 (수집 시); 보통 1 Hz
- **proprio**: joint state 7 + gripper state 1
- **tactile**: ✗
- **language**: NL instruction (VLM2VLA 의 NL-formatted 변종 존재)

#### Actions
- **space**: EE relative pose
- **dimension**: 7 (6-DOF + gripper)
- **control rate**: ~1 Hz
- **gripper / finger**: 1-DOF parallel-jaw
- **bimanual**: ✗

#### Embodiment
- WidowX 250 (7-DOF arm)
- **arm DOF**: 7
- **hand DOF**: **1**

#### Annotation
- **NL instruction**: present
- **task intent**: ✗
- **episode segmentation**: trajectory 단위
- **sub-task labels**: ✗

#### Scale
- **trajectories**: **60,096** (verified, abstract)
- **environments**: **24** (verified, abstract)
- **tasks**: ~24 categories

#### Lineage 적층
**VLM2VLA fine-tune corpus** (NL-formatted Gemini 2.5 변환) · OpenVLA (부분) · Octo (부분)

#### Source check
- 🟢 verified: License (CC-BY-SA-4.0), 데이터 유형, 60,096 trajectories, 24 environments — arXiv:2308.12952 abstract
- 🟡 partial: action space (NL instruction 호환 명시)
- 🔴 unverified: 정확한 camera count / resolution / control rate

#### Sources
- arXiv: [arXiv:2308.12952](https://arxiv.org/abs/2308.12952)
- 공식: [web](https://rail-berkeley.github.io/bridgedata/)

</details>

---

### <a id="droid"></a>DROID

<details>
<summary>Franka Panda × 564 scenes / 84 tasks — Xiaomi-Robotics-0 init corpus</summary>

#### Observations
- **cameras**: 2 ZED stereo (외부) + 1 ZED Mini (wrist); RGB ~640×480, ~7.5 Hz
- **proprio**: joint state 7 + gripper width 1
- **tactile**: ✗
- **language**: NL instruction

#### Actions
- **space**: EE relative pose 또는 joint
- **dimension**: 7~8 (6-DOF + gripper)
- **control rate**: ~5 Hz
- **gripper / finger**: 1-DOF Robotiq 2F-85
- **bimanual**: ✗

#### Embodiment
- Franka Panda 7-DOF + Robotiq 2F-85
- **arm DOF**: 7
- **hand DOF**: **1**
- **mounting**: 모바일 카트 (in-the-wild 강점)

#### Annotation
- **NL instruction**: present
- **task intent**: ✗
- **episode segmentation**: trajectory 단위
- **sub-task labels**: ✗

#### Scale
- **trajectories**: **76,000** (verified, abstract)
- **hours**: **350** (verified, abstract — "350 hours of interaction data")
- **scenes**: **564** (verified)
- **tasks**: **84** (verified)
- **data collectors**: **50** across North America, Asia, Europe over 12 months (verified, abstract)
- **collection period**: 2023

#### Lineage 적층
**Xiaomi-Robotics-0** (코어 corpus 의 한 축) · OpenVLA fine-tune · Universal-Policy

#### Source check
- 🟢 verified: License (CC-BY-4.0), 76k traj / 350h / 564 scenes / 84 tasks / 50 collectors — arXiv:2403.12945 abstract
- 🟡 partial: Franka Panda + Robotiq 2F-85 (project page 표준; abstract 미명시)
- 🔴 unverified: 정확한 ZED stereo spec, control rate (full paper 확인 필요)

#### Sources
- arXiv: [arXiv:2403.12945](https://arxiv.org/abs/2403.12945)
- 공식: [web](https://droid-dataset.github.io/)

</details>

---

### <a id="maniskill-3"></a>ManiSkill 3

<details>
<summary>SAPIEN sim × 20 task families — PriorVLA/VLA-Adapter LIBERO 옆 sim benchmark</summary>

#### Observations
- **cameras**: RGB-D ~1280×720 (시뮬 렌더)
- **proprio**: agent proprio + object state
- **tactile**: ✗ (시뮬 한정)
- **language**: NL goal description

#### Actions
- **space**: Cartesian / joint / gripper (controller 선택형)
- **dimension**: 7~14
- **control rate**: 5–10 Hz 등가
- **gripper / finger**: 1-DOF gripper (대부분) + **Allegro 16-DOF / ShadowHand 24-DOF** 일부 dexterous 태스크
- **bimanual**: ✗

#### Embodiment
- Franka · UR5 · Fetch · Unitree · **Allegro / ShadowHand (일부 dexterous 태스크)**
- **arm DOF**: 6–7
- **hand DOF**: **1 (대부분), 16~24 (dexterous 태스크)**
- **mounting**: simulation

#### Annotation
- **NL instruction**: NL goal description
- **task intent**: 20 task families
- **episode segmentation**: episode 단위 (시뮬 reset)
- **sub-task labels**: 일부

#### Scale
- **task domains**: **12** (verified — abstract: "12 distinct domains")
- **sim speed**: **30,000+ FPS** (verified — "10–1000× faster than competing platforms")
- **embodiments**: 다수 (dexterous 포함; full list paper 확인)
- **simulation only** — generative 가능

#### Lineage 적층
PriorVLA · VLA-Adapter 의 LIBERO 옆 sim benchmark

#### Source check
- 🟢 verified: License (**CC-BY-4.0**, not CC-BY-SA), simulation-only, 12 task domains, 30K+ FPS, dexterous manipulation 지원 — arXiv:2410.00425 abstract
- 🟡 partial: pointcloud/voxel observation 지원 (abstract 명시)
- 🔴 unverified: 정확한 trajectory / hour 수치 (generative 라 자체 모호)
- ❓ needs-human: 정확한 embodiment 목록 + hand-DOF 분포 (paper 본문 확인 필요)

#### Sources
- arXiv: [arXiv:2410.00425](https://arxiv.org/abs/2410.00425) (id 미검증)
- 공식: [web](https://maniskill.readthedocs.io/)

</details>

---

### <a id="robomind"></a>RoboMIND

<details>
<summary>4 embodiments × 107k trajectories / 479 tasks / 96 obj — includes humanoid w/ dual dexterous hands</summary>

#### Observations
- **cameras**: multi-view (verified; 정확한 수 paper 본문)
- **proprio**: joint state + gripper / hand state (embodiment-별)
- **tactile**: TBD
- **language**: NL instruction (linguistic task descriptions)

#### Actions
- **space**: embodiment-별 (Franka / UR5e gripper EE; humanoid dual-dex 다지)
- **dimension**: embodiment-별
- **control rate**: TBD
- **gripper / finger**: gripper (Franka / UR5e / AgileX 부분) + **dual dexterous hands** (humanoid)
- **bimanual**: ✓ (AgileX dual-arm + humanoid)

#### Embodiment
- **4 embodiments** (abstract): **Franka Emika Panda** · **UR5e** · **AgileX dual-arm robot** · **humanoid robot with dual dexterous hands** — *Tien Kung 아니라 별도 humanoid* (정정)
- **arm DOF**: 7 (Franka, UR5e); AgileX/humanoid 양팔
- **hand DOF**: **1 (gripper) + dual dexterous hands (humanoid)** ✓

#### Annotation
- **NL instruction**: ✓ linguistic task descriptions
- **task intent**: 479 tasks / 96 object classes
- **episode segmentation**: trajectory
- **sub-task labels**: 일부 (5k real-world failure demos 포함)

#### Scale
- **trajectories**: **107,000** (verified — "107k demonstration trajectories")
- **tasks**: **479** (verified — "479 diverse tasks")
- **object classes**: **96** (verified)
- **failure demos**: 5k real-world (verified, abstract)
- **embodiments**: 4

#### Lineage 적층
(자체 baseline; 외부 적층 미확인)

#### Source check
- 🟢 verified: 107k traj, 479 tasks, 96 obj, 5k failure demos, 4 embodiments (Franka / UR5e / AgileX / humanoid w/ dual-dex) — arXiv:2412.13877 abstract
- 🟡 partial: NL instruction 존재, multi-view
- 🔴 unverified: 정확한 camera count·resolution·fps, action space spec, dexterous hand 의 DOF
- ❓ needs-human: dataset card license (nonexclusive-distrib/1.0 인지 CC-BY-4.0 인지)

#### Sources
- arXiv: [arXiv:2412.13877](https://arxiv.org/abs/2412.13877)
- 공식: [web](https://x-humanoid-robomind.github.io/)

</details>

---

### <a id="agibot-world"></a>AgiBot World

<details>
<summary>AgiBot G1 humanoid × ~1M trajectories — 유일한 대규모 dexterous hand real-world</summary>

#### Observations
- **cameras**: 2~8 (head 2 + wrist 2 + 보조); RGB-D 1280×720, ~5 Hz
- **proprio**: 전신 (양팔 7+7 + hand 1 or 16+)
- **tactile**: option (일부 sub-dataset)
- **language**: NL instruction

#### Actions
- **space**: EE delta pose + gripper OR hand joint angles
- **dimension**: 7 (gripper) 또는 7 + hand-joint-N (dexterous)
- **control rate**: ~5 Hz
- **gripper / finger**: **1 (gripper) OR 16~22-DOF dexterous hand** (sub-dataset 별)
- **bimanual**: ✓ (양팔)

#### Embodiment
- AgiBot G1 humanoid (양팔 7+7 DOF)
- **arm DOF**: 7+7 = 14 양팔
- **hand DOF**: **1 OR 16~22 (xhand 옵션 포함)** ✓
- **mounting**: 휴머노이드 + 두부 헬멧 + 모바일 베이스

#### Annotation
- **NL instruction**: present
- **task intent**: 217 tasks
- **episode segmentation**: trajectory
- **sub-task labels**: 일부 (긴 task 의 단계 라벨)

#### Scale
- **trajectories**: ~1,000,000+ (Alpha + Beta)
- **tasks**: 217
- **collection period**: 2024–

#### Lineage 적층
**Genie Operator-1 (GO-1)** 자체 적층 + 일부 third-party humanoid VLA + RDT-1B 평가

#### Source check
- 🟢 verified: License **CC-BY-NC-SA-4.0** (정정, abstract 라이선스 아이콘), 1M+ trajectories, 217 tasks, "extensible from grippers to dexterous hands and visuo-tactile sensors" (abstract) — arXiv:2503.06669
- 🟡 partial: humanoid 양팔, xhand 22-DOF 옵션
- 🔴 unverified: hand-DOF subset 의 정확한 비율, tactile sub-dataset 의 spec, camera count 분포
- ❓ needs-human: 카메라 개수 / 정확한 robot 모델명 / collection period

#### Sources
- arXiv: [arXiv:2503.06669](https://arxiv.org/abs/2503.06669)
- 공식: [web](https://agibot-world.com/)

</details>

---

### <a id="dexmimicgen"></a>DexMimicGen

<details>
<summary>NVIDIA GR1 humanoid sim × 21K synth from 60 human — bimanual 16-DOF per hand</summary>

#### Observations
- **cameras**: RGB 1280×720 (시뮬), ~10 Hz
- **proprio**: joint (arm 7 + hand 16)
- **tactile**: ✗ (시뮬)
- **language**: NL goal (생성형)

#### Actions
- **space**: joint angles
- **dimension**: arm 7 + hand 16 + gripper 1 ≈ 24 per hand
- **control rate**: ~10 Hz (시뮬 step)
- **gripper / finger**: **Inspire Hand 16-DOF per hand**
- **bimanual**: ✓

#### Embodiment
- GR1 humanoid (양팔 7+7) + Inspire Hand 12~16-DOF per hand
- **arm DOF**: 7+7
- **hand DOF**: **16 per hand** (총 32 양손)
- **mounting**: 휴머노이드 + 두부 카메라

#### Annotation
- **NL instruction**: NL goal
- **task intent**: 시연 task 별 분류
- **episode segmentation**: synthetic episode

#### Scale
- **synthetic episodes**: 21,000
- **seed human demos**: 60
- **multiplier**: ~350× per-demo augmentation

#### Lineage 적층
(NVIDIA 내부 GR00T pretraining mix 의 일부 추정; 공개 적층 VLA 미확인) · Robocasa

#### Source check
- 🟢 verified: License (CC-BY-NC-SA-4.0), simulation-only, bimanual
- 🟡 partial: 21K from 60 (paper §4)
- 🔴 unverified: Inspire Hand 12 vs 16 DOF (논문/release 마다 변동), 정확한 camera spec
- ❓ needs-human: GR00T N1 / N1.5 의 적층 여부 (NVIDIA 내부 mix 일 가능성)

#### Sources
- arXiv: [arXiv:2410.24185](https://arxiv.org/abs/2410.24185)
- 공식: [gh:NVlabs/dex-mimicgen](https://github.com/NVlabs/dex-mimicgen)

</details>

---

### <a id="unihand-2"></a>UniHand-2.0

<details>
<summary>BeingBeyond × ~35k h × 30 embodiments — human-video → 22-DOF hand retarget</summary>

#### Observations
- **cameras**: egocentric RGB video (human hands); hand-object 3D
- **proprio**: human hand pose (MANO 변종)
- **tactile**: ✗
- **language**: NL instruction

#### Actions
- **space**: hand joint trajectory (retargeted)
- **dimension**: 22+ (per hand)
- **control rate**: video frame rate
- **gripper / finger**: **22-DOF humanoid hand (retarget 가능)**
- **bimanual**: 양손 ego (대부분)

#### Embodiment
- 인간 양손 → 30 embodiments retarget (UniDex 카탈로그: Inspire / xhand / LEAP / Allegro / ShadowHand 등)
- **arm DOF**: 인간 어깨~손목 (retarget 시 robot arm 7)
- **hand DOF**: **6~24** (target hand 마다)
- **mounting**: 무관 (human ego source)

#### Annotation
- **NL instruction**: present
- **task intent**: 다양 (~30 카테고리 추정)
- **episode segmentation**: clip 단위
- **sub-task labels**: 일부

#### Scale
- **hours**: ~35,000
- **breakdown**: ~16k h ego + ~14k h robot manip + ~5k h VL
- **samples**: 400M+
- **tokens**: 120B+ (Being-H0.5 모델 카드)

#### Lineage 적층
**Being-H0.5** (자체)

#### Source check
- 🟢 verified: ~35,000h, **30 distinct robotic embodiments**, cross-embodiment + VL 통합 corpus, License **Apache-2.0** (GitHub repo footer) — Being-H0.5 search 결과
- 🟡 partial: 35k h 분할 (ego + robot + VL)
- 🔴 unverified: 정확한 trajectory count 분할, NL instruction 형식
- ❓ needs-human: VLM backbone (Qwen2.5-VL 추정이지만 paper 미명시), 30 embodiments 의 정확한 목록 + 각 hand-DOF

#### Sources
- arXiv: [arXiv:2601.12993](https://arxiv.org/abs/2601.12993) (Being-H0.5 paper)
- 공식: [gh:BeingBeyond/Being-H](https://github.com/BeingBeyond/Being-H)

</details>

---

### <a id="aloha"></a>ALOHA / Mobile ALOHA

<details>
<summary>2× ViperX 300 bimanual leader-follower, 50 Hz — lerobot 의 다수 subset</summary>

#### Observations
- **cameras**: 4 (양 wrist 2 + 위 2); RGB 480×640, 50 Hz
- **proprio**: 14-DOF joint state (양팔 6 + gripper)
- **tactile**: ✗
- **language**: NL instruction (sub-subset 별)

#### Actions
- **space**: joint position absolute
- **dimension**: 14 (양팔 6+gripper 7×2); Mobile 은 +2 (base linear/angular)
- **control rate**: 50 Hz
- **gripper / finger**: 1-DOF parallel-jaw per arm
- **bimanual**: ✓

#### Embodiment
- 2× ViperX 300S (6-DOF + 1-DOF parallel gripper) leader-follower
- **arm DOF**: 6+6
- **hand DOF**: **1+1**
- **mounting**: 책상 + Mobile 은 Tracer mobile base

#### Annotation
- **NL instruction**: sub-subset 별 (lerobot 표준화)
- **task intent**: ✗
- **episode segmentation**: trajectory 단위
- **sub-task labels**: ✗

#### Scale
- **public HF subsets**: 50+
- **per-subset hours**: 1~수십 시간 분포

#### Lineage 적층
lerobot subset 의 다수 적층 · ACT 류 · π0 fine-tune · RT-X co-train · X-VLA 6-bench

#### Source check
- 🟢 verified: ViperX 300S × 2, MIT license, 50 Hz
- 🟡 partial: lerobot HF subset 수 (~50+)
- 🔴 unverified: ALOHA 본체와 Mobile ALOHA 의 데이터 합산 hour
- ❓ needs-human: 공식 ALOHA 데이터 단독 release 위치 (lerobot 미러 외)

#### Sources
- arXiv: [arXiv:2304.13705](https://arxiv.org/abs/2304.13705) (ACT) · [arXiv:2401.02117](https://arxiv.org/abs/2401.02117) (Mobile)
- 공식: [web](https://tonyzhaozh.github.io/aloha/)

</details>

---

### <a id="rh20t"></a>RH20T

<details>
<summary>SJTU MVIG × ~110K sequences — 유일한 6-axis F/T + audio robot 데이터</summary>

#### Observations
- **cameras**: multi (~8); RGB 1280×720, ~10 Hz
- **proprio**: joint state 7 + gripper 1
- **tactile**: ✓ **6-axis F/T (wrist mount)**, audio
- **language**: NL instruction

#### Actions
- **space**: EE pose
- **dimension**: 7
- **control rate**: ~10 Hz
- **gripper / finger**: 1-DOF parallel-jaw
- **bimanual**: ✗

#### Embodiment
- Franka / UR-5 / Flexiv 등 7-DOF arm + Robotiq
- **arm DOF**: 7
- **hand DOF**: **1**
- **wrist-mount FT**: ✓ (6-axis)
- **mounting**: 책상 + multi-view + wrist FT

#### Annotation
- **NL instruction**: present
- **task intent**: ✗
- **episode segmentation**: sequence
- **sub-task labels**: 일부

#### Scale
- **sequences**: ~110,000
- **contact-rich** 비율 높음

#### Lineage 적층
(tactile-aware VLA 드물어 직접 적층 미확인) · OXE sub-dataset 으로 부분 포함 가능성

#### Source check
- 🟢 verified: License (CC-BY-SA-4.0), **110,000+ contact-rich sequences**, **force/torque + audio + visual + action 통합** — arXiv:2307.00595 abstract
- 🟡 partial: "hundreds of real-world skills" 명시 (정확 task 수 abstract 미명시)
- 🔴 unverified: arm 분포 (Franka / UR-5 / Flexiv 비율), 정확한 audio spec, 카메라 수
- ❓ needs-human: tactile + force 라벨 통합 spec (paper §3)

#### Sources
- arXiv: [arXiv:2307.00595](https://arxiv.org/abs/2307.00595)
- 공식: [web](https://rh20t.github.io/)

</details>

---

### <a id="lerobot"></a>LeRobot (aggregated)

<details>
<summary>HF + community × 50+ embodiments — 표준 dataset format + 일부 ShadowHand</summary>

#### Observations
- **cameras**: standardized RGB 1–3
- **proprio**: standardized joint + gripper; optional tactile / F-T
- **tactile**: option (일부 dataset)
- **language**: NL instruction (대부분)

#### Actions
- **space**: standardized — relative pose 6 또는 joint up to 14
- **dimension**: 6~14 (embodiment 마다)
- **control rate**: embodiment 마다 상이
- **gripper / finger**: 1~24-DOF (Shadow subset 포함)
- **bimanual**: 일부 subset (ALOHA 등)

#### Embodiment
- 50+ embodiments — Franka · WidowX · ALOHA · SO-100 · **Shadow 24-DOF (일부 subset)** 등
- **arm DOF**: 6~7
- **hand DOF**: **1~24**
- **mounting**: subset 마다 상이

#### Annotation
- **NL instruction**: 대부분 present (lerobot 표준)
- **task intent**: subset 마다
- **episode segmentation**: standardized
- **sub-task labels**: ✗ (대체로)

#### Scale
- **embodiments**: 50+
- **per-subset trajectories**: 수십~수만

#### Lineage 적층
(lerobot 내부 benchmark; 외부 VLA 적층은 sub-subset 단위)

#### Source check
- 🟢 verified: License (Apache-2.0), 50+ embodiments, **arXiv:2602.22818** (Cadene et al., ICLR 2026 — 정정: 직전 ID `2404.14541` 은 다른 paper) — WebSearch 결과
- 🟡 partial: ShadowHand subset 의 정확한 수
- 🔴 unverified: 통합 trajectory 수치 (subset 마다 다름)
- ❓ needs-human: 정확한 included policy / embodiment 목록

#### Sources
- arXiv: [arXiv:2602.22818](https://arxiv.org/abs/2602.22818) (정정)
- 공식: [hf:lerobot](https://huggingface.co/lerobot) · [gh:huggingface/lerobot](https://github.com/huggingface/lerobot)

</details>

---

### <a id="hoi4d"></a>HOI4D

<details>
<summary>PKU + 컨소시엄 × 4000 sequences × 800 objects — 4D hand-object contact</summary>

#### Observations
- **cameras**: egocentric RGB-D
- **proprio**: 4D hand pose (MANO 변종)
- **tactile**: ✗
- **language**: action label (segmentation 라벨)

#### Actions
- **space**: N/A (human hand pose only; no robot action)
- **dimension**: hand pose / object pose / segmentation
- **bimanual**: 단손 위주

#### Embodiment
- **N/A** (human ego)
- hand DOF: human (MANO)

#### Annotation
- **NL instruction**: ✗ (대신 action label)
- **task intent**: 16 categories
- **episode segmentation**: per-frame action segmentation
- **sub-task labels**: ✓ (4D 접촉 annotation)

#### Scale
- **sequences**: 4,000
- **objects**: 800
- **categories**: 16

#### Lineage 적층
(직접 적층 VLA 없음 — hand-object retarget 후보)

#### Source check
- 🟢 verified: 4000 seq, 800 obj, 16 categories, **2.4M RGB-D egocentric video frames** — arXiv:2203.01577 abstract
- 🟡 partial: 3개 benchmarking task (4D segmentation / pose tracking / action segmentation) 명시
- 🔴 unverified: License (CC-BY-NC-4.0 추정 — project page 직접 확인 필요)
- ❓ needs-human: 정확한 hand-pose annotation format (MANO 등), depth resolution

#### Sources
- arXiv: [arXiv:2203.01577](https://arxiv.org/abs/2203.01577)
- 공식: [web](http://www.hoi4d.top/)

</details>

---

### <a id="arctic"></a>ARCTIC

<details>
<summary>ETH + MPI × 339 sequences × 11 objects — bimanual articulated + MANO</summary>

#### Observations
- **cameras**: multi-view RGB
- **proprio**: bimanual MANO + 3D articulated object pose
- **tactile**: contact map
- **language**: action / object label

#### Actions
- **space**: N/A (human MANO joint trajectory)
- **dimension**: MANO 양손 (51 + 51 = 102)
- **bimanual**: ✓

#### Embodiment
- **N/A** (human bimanual + 11 articulated objects: scissors · microwave · 등)
- hand DOF: human MANO

#### Annotation
- **NL instruction**: ✗
- **task intent**: 11 articulated objects
- **episode segmentation**: per-sequence
- **sub-task labels**: contact transition

#### Scale
- **sequences**: 339
- **objects**: 11 articulated

#### Lineage 적층
(직접 적층 VLA 없음 — bimanual articulated retarget 후보)

#### Source check
- 🟢 verified: **2.1M video frames**, bimanual articulated object manipulation — arXiv:2204.13662 abstract
- 🟡 partial: 11 articulated objects (이전 메모리), 339 sequences (이전 메모리; abstract 미확인)
- 🔴 unverified: License (CC-BY-NC-SA-4.0 추정 — project page 확인 필요), multi-view camera 수
- ❓ needs-human: MANO 변종, subject count, 정확한 sequence/object count

#### Sources
- arXiv: [arXiv:2204.13662](https://arxiv.org/abs/2204.13662)
- 공식: [web](https://arctic.is.tue.mpg.de/)

</details>

---

### <a id="oakink"></a>OakInk

<details>
<summary>ShanghaiTech × 50K grasps × 100 objects — intent 라벨 있는 grasp 데이터</summary>

#### Observations
- **cameras**: RGB(-D)
- **proprio**: MANO + 3D object mesh
- **tactile**: ✗
- **language**: intent label

#### Actions
- **space**: N/A (grasp pose)
- **dimension**: MANO (51)
- **bimanual**: 단손

#### Embodiment
- **N/A** (human hand + 100 objects)
- hand DOF: human MANO

#### Annotation
- **NL instruction**: ✗
- **task intent**: ✓ **5 카테고리 (hold / use / handover / lift / manipulate)**
- **episode segmentation**: per-grasp
- **sub-task labels**: grasp category

#### Scale
- **grasps**: 50,000
- **objects**: 100
- **intent categories**: 5

#### Lineage 적층
(직접 적층 VLA 없음 — grasp prior 후보)

#### Source check
- 🟢 verified: **50,000 affordance-aware + intent-oriented hand-object interactions**, **1,800 household objects (100 recorded)** — arXiv:2203.15709 abstract
- 🟡 partial: 5 intent 카테고리 (이전 메모리; abstract 미확인)
- 🔴 unverified: License (CC-BY-NC-4.0 추정 — GitHub repo 확인 필요), MANO spec 변종
- ❓ needs-human: intent taxonomy 의 정확한 정의, 카메라 spec

#### Sources
- arXiv: [arXiv:2203.15709](https://arxiv.org/abs/2203.15709)
- 공식: [web](https://oakink.net/)

</details>

---

### <a id="assemblyhands"></a>AssemblyHands

<details>
<summary>Meta × ~3M frames × 34 subjects — bimanual ego, 3D hand pose</summary>

#### Observations
- **cameras**: egocentric multi-view RGB
- **proprio**: bimanual 3D hand pose
- **tactile**: ✗
- **language**: 조립 단계 라벨 (Assembly101 from)

#### Actions
- **space**: N/A
- **dimension**: 3D hand pose 양손
- **bimanual**: ✓ ego

#### Embodiment
- **N/A** (human bimanual ego)
- hand DOF: human 3D pose

#### Annotation
- **NL instruction**: ✗ (조립 단계 라벨)
- **task intent**: 조립
- **episode segmentation**: assembly sequence
- **sub-task labels**: 조립 step

#### Scale
- **frames**: **3.0M annotated** (verified)
- **ego frames**: **490K** (verified)
- **subjects**: 34 (이전 메모리)
- **assembly toys**: 101 (Assembly101 기반, verified — abstract 명시)

#### Lineage 적층
(직접 적층 VLA 없음 — bimanual ego pose prior 후보)

#### Source check
- 🟢 verified: **3.0M annotated images (490K ego)**, **License CC-BY-4.0** (정정 — abstract 라이선스 아이콘), Assembly101 기반 — arXiv:2304.12301 abstract
- 🟡 partial: 3D hand pose (포맷 abstract 미명시)
- 🔴 unverified: 정확한 ego + exo camera 수, subject count (34 는 이전 메모리)
- ❓ needs-human: hand-pose annotation 의 정확한 format (MANO vs 3D keypoint)

#### Sources
- arXiv: [arXiv:2304.12301](https://arxiv.org/abs/2304.12301)
- 공식: [web](https://assemblyhands.github.io/)

</details>

---

### <a id="ego4d"></a>Ego4D

<details>
<summary>Meta + 컨소시엄 × ~3670h egocentric — vision/temporal/NL prior 표준</summary>

#### Observations
- **cameras**: egocentric RGB
- **proprio**: 일부 IMU / 3D head pose (subset)
- **tactile**: ✗
- **language**: narration (~50줄/시간 평균)

#### Actions
- **space**: N/A
- **dimension**: narration label
- **bimanual**: 일부 subset 의 hand 라벨

#### Embodiment
- **N/A** (human everyday ego)
- hand DOF: 일부 subset 의 hand pose

#### Annotation
- **NL instruction**: ✗ (대신 narration)
- **task intent**: 일상 활동 분류
- **episode segmentation**: per-clip
- **sub-task labels**: narration timestamp

#### Scale
- **hours**: ~3,670
- **subjects**: 900+ (74 location)
- **collection period**: 2019–2022

#### Lineage 적층
(직접 적층 VLA 없음 — vision/temporal/NL prior 표준 corpus)

#### Source check
- 🟢 verified: **3,670h**, **931 unique camera wearers**, **74 worldwide locations / 9 countries** (정정 — 이전 13 cities 가 아님), "hand-object manipulation" benchmark 존재 — arXiv:2110.07058 abstract
- 🟡 partial: stereo / synchronized multi-camera subset 존재 명시
- 🔴 unverified: 3D head pose subset 의 정확한 spec, 정확한 hand pose subset 위치
- ❓ needs-human: Ego4D license 본문 세부 조항 (가입 동의 형태)

#### Sources
- arXiv: [arXiv:2110.07058](https://arxiv.org/abs/2110.07058)
- 공식: [web](https://ego4d-data.org/)

</details>

---

### <a id="epic-kitchens-100"></a>Epic Kitchens 100

<details>
<summary>Bristol/Toronto/CMU × ~100h cooking ego — action label + hand-object</summary>

#### Observations
- **cameras**: egocentric RGB
- **proprio**: ✗ (raw video only)
- **tactile**: ✗
- **language**: verb-noun action segments

#### Actions
- **space**: N/A
- **dimension**: action label
- **bimanual**: 양손 hand-object bbox 일부

#### Embodiment
- **N/A** (human cooking ego)
- hand-object bbox + (subset) 3D

#### Annotation
- **NL instruction**: ✗ (verb-noun)
- **task intent**: cooking
- **episode segmentation**: 90K action segments
- **sub-task labels**: ✓ (segment 단위)

#### Scale
- **hours**: ~100
- **kitchens**: 45
- **action segments**: 90,000

#### Lineage 적층
(직접 적층 VLA 없음 — cooking-task NL grounding 후보)

#### Source check
- 🟢 verified: **100h / 20M frames / 90K actions / 700 variable-length videos / 45 environments**, **License CC-BY-NC-SA-4.0** (정정 — 이전 NC-4.0 에서 NC-SA-4.0 으로 abstract 라이선스 링크 확인), head-mounted camera — arXiv:2006.13256 abstract
- 🟡 partial: verb-noun action label 명시 (전체 verb/noun 클래스 수 미명시)
- 🔴 unverified: hand-object bbox vs 3D subset 의 정확한 비율, 개별 참가자 수

#### Sources
- arXiv: [arXiv:2006.13256](https://arxiv.org/abs/2006.13256)
- 공식: [web](https://epic-kitchens.github.io/100)

</details>

---

### <a id="egoexolearn"></a>EgoExoLearn

<details>
<summary>Shanghai AI Lab × ~120h paired ego-exo — P2 multi-cam fuser 와 직접 연결</summary>

#### Observations
- **cameras**: egocentric + exocentric (paired)
- **proprio**: ✗
- **tactile**: ✗
- **language**: NL instruction (시연 매칭 라벨)

#### Actions
- **space**: N/A
- **dimension**: 시연 매칭 라벨
- **bimanual**: 시나리오 마다

#### Embodiment
- **N/A** (human paired ego-exo)
- hand DOF: video 만 (annotation 없음 추정)

#### Annotation
- **NL instruction**: present
- **task intent**: 시연 매칭
- **episode segmentation**: 시연 단위
- **sub-task labels**: ego-exo 매칭

#### Scale
- **hours**: ~120
- **paired sequences**: 시연 단위 (paper §3)

#### Lineage 적층
(직접 적층 VLA 없음 — ego-exo gap 학습 prior 후보; P2 D12 multi-cam fuser 와 연결)

#### Source check
- 🟢 verified: **120h captured in daily life scenarios and specialized laboratories**, **License CC-BY-4.0** (정정 — abstract 라이선스 아이콘 확인; 이전 Apache-2.0 은 GitHub repo 라이선스이며 데이터셋 자체는 CC-BY-4.0) — arXiv:2403.16182 abstract
- 🟡 partial: paired ego + exo 명시 (정확한 매칭 단위 미명시)
- 🔴 unverified: 정확한 paired sequence 수, NL instruction 형식
- ❓ needs-human: hand-pose annotation 존재 여부

#### Sources
- arXiv: [arXiv:2403.16182](https://arxiv.org/abs/2403.16182)
- 공식: [gh:OpenGVLab/EgoExoLearn](https://github.com/OpenGVLab/EgoExoLearn)

</details>

---

### <a id="molmoact2-bimanualyam"></a>MolmoAct2-BimanualYAM

<details>
<summary>Allen AI YAM bimanual rig × 34,500 demos / 720h — 현존 최대 open bimanual robotics dataset</summary>

#### Observations
- **cameras**: TBD ❓ (multi-view RGB 추정 — YAM rig spec 미확인)
- **proprio**: TBD ❓ (bimanual joint state)
- **tactile**: TBD ❓
- **language**: NL instruction 추정 (MolmoAct2 가 NL 적층)

#### Actions
- **space**: TBD ❓ (joint 또는 EE; MolmoAct2 가 discrete depth+trace 토큰 출력)
- **dimension**: TBD ❓
- **control rate**: TBD ❓
- **gripper / finger**: TBD (bimanual; gripper 추정 — YAM rig spec 미확인)
- **bimanual**: ✓ (verified — "two robotic arms working together")

#### Embodiment
- Allen AI YAM rig (bimanual teleoperation)
- **arm DOF**: TBD ❓
- **hand DOF**: TBD ❓ (folding towel / scanning groceries / charging phone / table bussing 같은 task 라 gripper 추정)
- **mounting**: tabletop (verified — "open bimanual tabletop manipulation")

#### Annotation
- **NL instruction**: present (task spec)
- **task intent**: towel folding / grocery scanning / phone charging / table bussing (verified examples)
- **episode segmentation**: per-demonstration
- **sub-task labels**: TBD

#### Scale
- **demos**: **34,500 teleoperated demonstrations** (verified — WebSearch / techtimes / techfastforward 일치)
- **hours**: **720+** (verified — "over 720 hours of training demonstrations")
- **collection period**: ~2개월 (verified — "collected over a two-month period")
- **vs MolmoAct1**: **30× MolmoAct1 데이터 규모** (verified)

#### Lineage 적층
**MolmoAct2** (자체) — *현존 최대 open bimanual robotics dataset* (verified, techtimes/techfastforward)

#### Source check
- 🟢 verified: 34,500 demos / 720h / 2개월 / bimanual tabletop / task 예시 (towel/grocery/phone/bussing) — MolmoAct2 paper arXiv:2605.02881 + Allen AI blog (techtimes, techfastforward 보도)
- 🟡 partial: NL instruction 존재 (paper §)
- 🔴 unverified: License (Apache-2.0 또는 ODC-BY 추정 — Allen AI 표준; 직접 확인 필요), YAM rig 의 DOF/카메라/control rate
- ❓ needs-human: arXiv:2605.02881 paper §4 의 데이터셋 spec 표, HuggingFace dataset card 의 정확한 spec

#### Sources
- arXiv: [arXiv:2605.02881](https://arxiv.org/abs/2605.02881) (MolmoAct2 paper)
- 공식 blog: [web](https://allenai.org/blog/molmoact2)
- HF collection: [hf:allenai/molmoact2-datasets](https://huggingface.co/collections/allenai/molmoact2-datasets)

</details>

---

### <a id="molmoact2-so100-101"></a>MolmoAct2-SO100/101

<details>
<summary>Allen AI MolmoAct2 적층 corpus on SO-ARM (lerobot 저비용 6-DOF arm)</summary>

#### Observations
- **cameras**: TBD ❓ (SO-ARM 표준 wrist + 외부 추정; RGB)
- **proprio**: joint state ~6 + gripper 1
- **tactile**: ✗ 추정
- **language**: NL instruction 추정

#### Actions
- **space**: joint 또는 EE delta 추정
- **dimension**: ~7 (6-DOF + gripper)
- **control rate**: TBD ❓ (lerobot 표준 ~30 Hz)
- **gripper / finger**: 1-DOF parallel-jaw (SO-ARM 기본)
- **bimanual**: ✗

#### Embodiment
- SO-100 (lerobot 첫 SO-ARM) + SO-101 (개선판; HF 컬렉션에 두 변종 sub-dataset 분리 추정)
- **arm DOF**: 6
- **hand DOF**: **1** (gripper)
- **mounting**: 책상 + wrist 카메라 (lerobot 표준)

#### Annotation
- **NL instruction**: present 추정
- **task intent**: TBD ❓
- **episode segmentation**: trajectory
- **sub-task labels**: TBD ❓

#### Scale
- **trajectories**: TBD ❓
- **hours**: TBD ❓
- **sub-dataset split**: SO-100 / SO-101 (HF collection 에서 분리; 합산 여부 확인 필요)

#### Lineage 적층
**MolmoAct2** (자체) — MolmoAct2 의 data mix 의 일부 (BimanualYAM + DROID-MolmoAct2 + SO100/101 합산)

#### Source check
- 🟢 verified: MolmoAct2 data mix 에 "MolmoAct2-SO100/101 Dataset" 명시 — WebSearch (techtimes / techfastforward) + arXiv:2605.02881
- 🟡 partial: SO-ARM 플랫폼 (lerobot 표준 저비용 arm) 추정
- 🔴 unverified: 정확한 trajectory 수, license, control rate
- ❓ needs-human: SO-100 vs SO-101 의 데이터 분리/합산, HuggingFace dataset card 의 spec

#### Sources
- arXiv: [arXiv:2605.02881](https://arxiv.org/abs/2605.02881) (MolmoAct2 paper)
- HF collection: [hf:allenai/molmoact2-datasets](https://huggingface.co/collections/allenai/molmoact2-datasets)
- SO-ARM (lerobot): [hf:lerobot](https://huggingface.co/lerobot)

</details>

---

### <a id="molmobot-data"></a>MolmoBot-Data

<details>
<summary>Allen AI MolmoBot — **simulation-only** 1.7M expert demos / 94K env / 8 tasks / Franka FR3 + Rainbow RB-Y1</summary>

#### Observations
- **cameras**: 시뮬 RGB (다중 view + fully randomized cameras)
- **proprio**: agent proprio (sim 표준)
- **tactile**: ✗ (sim)
- **language**: NL instruction (task spec)

#### Actions
- **space**: joint / EE (시뮬 controller 선택형)
- **dimension**: TBD (per-platform)
- **control rate**: sim step
- **gripper / finger**: Franka FR3 gripper + Rainbow RB-Y1 (mobile manipulation 포함)
- **bimanual**: TBD (RB-Y1 humanoid 양팔 가능)

#### Embodiment
- **Franka FR3** (7-DOF arm + gripper) — verified
- **Rainbow Robotics RB-Y1** (mobile manipulation) — verified
- **arm DOF**: 7 (FR3); RB-Y1 spec TBD
- **hand DOF**: 1 (gripper, 추정 — RB-Y1 의 hand 별도 release 정보 필요)
- **mounting**: 시뮬 (Franka 책상) + mobile (RB-Y1)

#### Annotation
- **NL instruction**: present (task spec)
- **task intent**: **8 task types** (verified)
- **episode segmentation**: per-trajectory
- **sub-task labels**: TBD

#### Scale
- **trajectories**: **1.7M expert manipulation demonstrations** (verified)
- **objects**: **11,000+ unique** (verified)
- **environments**: **94,000+ procedurally generated** (verified)
- **task types**: **8** (verified)
- **simulation only** — MuJoCo + aggressive domain randomization + procedural env generation (verified)
- **base ecosystem**: MolmoSpaces (232k env / 48k objects / 8 task types)

#### Lineage 적층
**MolmoBot** (자체 — Allen AI MolmoBot 모델) — *MolmoBot 은 VLA 모델 + 데이터셋 + 시뮬 ecosystem 통합*

#### Source check
- 🟢 verified: **arXiv:2603.16861** (MolmoB0T paper, 정정 — 이전 paper ID 미확정), **1.7M trajectories / 11K+ obj / 94K+ env / 8 tasks / Franka FR3 + Rainbow RB-Y1 / sim-only / MuJoCo / domain randomization** — WebSearch (Allen AI / HPCwire 보도) + project page allenai.github.io/MolmoBot/
- 🟡 partial: NL instruction 형식, 8 task type 의 정확한 목록
- 🔴 unverified: License (Apache-2.0 추정 — Allen AI 표준; release 확인 필요), RB-Y1 의 hand spec
- ❓ needs-human: arXiv:2603.16861 paper §3 의 데이터셋 spec, HF dataset URL (현재 미확인)

#### Sources
- arXiv: [arXiv:2603.16861](https://arxiv.org/abs/2603.16861) (MolmoB0T paper, 정정)
- 공식 project: [web](https://allenai.github.io/MolmoBot/)
- 공식 blog: [web](https://allenai.org/blog/molmobot-robot-manipulation)
- ecosystem repo: [gh:allenai/molmospaces](https://github.com/allenai/molmospaces)

</details>

---

### <a id="ego-exo4d"></a>Ego-Exo4D

<details>
<summary>Meta + 컨소시엄 × ~1300h paired egocentric + exocentric — skilled task corpus</summary>

#### Observations
- **cameras**: **paired egocentric + multi-exocentric** (시연자 1인칭 + 외부 다중 view)
- **proprio**: ego head 6DoF, 일부 3D body pose (subset)
- **tactile**: ✗
- **language**: narration + expert commentary (skilled performer 의 설명)

#### Actions
- **space**: N/A (action label segmentation)
- **dimension**: narration / commentary text
- **bimanual**: 시나리오 마다 (cooking / music 등)

#### Embodiment
- **N/A** (human skilled performer ego + exo paired)
- **participants**: **740** (verified — 정정: 800+ 추정 → 740)
- **cities**: **13** (verified)
- **tasks**: sports / music / dance / bike repair (verified — 정정: 이전 cooking/health 추정은 abstract 미명시; abstract 명시 카테고리는 sports/music/dance/bike repair)

#### Annotation
- **NL instruction**: ✗ (narration + expert commentary)
- **task intent**: skilled human activities (sports · music · dance · bike repair)
- **episode segmentation**: per-take
- **sub-task labels**: 3D hand/body pose benchmark task 존재

#### Scale
- **hours**: **1,286h** (verified — 정정: 이전 ~1300h 추정에서 1286h 로 정확)
- **participants**: **740** (verified)
- **cities**: **13** (verified)
- **collection period**: 2022–2023

#### Lineage 적층
(직접 적층 VLA 없음 — paired ego-exo + skilled task prior 후보; P2 D12 multi-cam fuser 와 강하게 연결)

#### Source check
- 🟢 verified: **1,286h paired ego + exo**, **740 participants**, **13 cities**, skilled human activities (sports · music · dance · bike repair), 3D hand/body pose benchmark — arXiv:2311.18259 abstract
- 🟡 partial: cooking / health 카테고리 (abstract 미명시; full paper 확인 필요)
- 🔴 unverified: License (Ego4D 와 유사 gated 추정), 정확한 exo camera 수
- ❓ needs-human: hand pose annotation subset 의 정확한 범위, 전체 task taxonomy

#### Sources
- arXiv: [arXiv:2311.18259](https://arxiv.org/abs/2311.18259)
- 공식: [web](https://ego-exo4d-data.org/)

</details>

---

### <a id="assembly101"></a>Assembly101

<details>
<summary>TUM + Meta × ~513h / 4321 sequences — bimanual ego + 8 exo + 3D hand pose</summary>

#### Observations
- **cameras**: **paired egocentric + 8 exocentric** (multi-view)
- **proprio**: bimanual 3D hand pose annotation
- **tactile**: ✗
- **language**: assembly step annotation (verb-noun)

#### Actions
- **space**: N/A
- **dimension**: bimanual 3D hand pose + assembly step label
- **bimanual**: ✓

#### Embodiment
- **N/A** (human bimanual ego + exo paired)
- **toy assemblies**: 101 "take-apart" toy vehicles (verified)
- **subjects**: 53 (이전 메모리)

#### Annotation
- **NL instruction**: verb-noun assembly step
- **task intent**: 101 assembly tasks
- **episode segmentation**: 4,321 videos (verified)
- **sub-task labels**: ✓ **100K coarse + 1M fine-grained action segments + mistake detection** (verified)

#### Scale
- **hours**: ~513 (이전 메모리)
- **videos**: **4,321** (verified)
- **toys**: **101** (verified)
- **camera views**: **4 ego + 8 static (exo) = 12 total** (정정)
- **hand poses**: **18M 3D hand poses** (verified)
- **subjects**: 53 (이전 메모리)

#### Lineage 적층
(직접 적층 VLA 없음 — bimanual assembly hand prior 후보; PROBE 의 tool-articulation phase 에 가까운 task)

#### Source check
- 🟢 verified: **4,321 videos / 101 toy vehicles**, **4 ego + 8 static (exo) = 12 cameras** (정정 — 이전 1 ego + 8 exo 가 아니라 4 ego + 8 static), **18M 3D hand poses**, "100K coarse + 1M fine-grained action segments" + "mistake detection" task — arXiv:2203.14712 abstract
- 🟡 partial: ~513h (paper 본문 추정), 53 subjects (이전 메모리)
- 🔴 unverified: License (CC-BY-NC-4.0 추정 — project page 확인 필요), hand pose annotation format (MANO vs 3D keypoint)

#### Sources
- arXiv: [arXiv:2203.14712](https://arxiv.org/abs/2203.14712)
- 공식: [web](https://assembly-101.github.io/)

</details>

---

### <a id="holoassist"></a>HoloAssist

<details>
<summary>Microsoft × ~166h mixed-reality ego — instructor-performer paired task assist</summary>

#### Observations
- **cameras**: HoloLens mixed-reality egocentric RGB
- **proprio**: head pose (HoloLens 6DoF) + hand pose (HoloLens hand tracking)
- **tactile**: ✗
- **language**: instructor-performer 대화 + task instruction

#### Actions
- **space**: N/A (instruction + hand pose)
- **dimension**: hand pose + dialogue
- **bimanual**: 작업마다

#### Embodiment
- **N/A** (human performer wearing HoloLens, instructor remote)
- **pairs**: 350 unique instructor-performer pairs
- **tasks**: 20 daily-life 과업 (electronics 조립 등)

#### Annotation
- **NL instruction**: ✓ (instructor → performer dialogue)
- **task intent**: 20 task categories
- **episode segmentation**: session 단위
- **sub-task labels**: action / mistake / intervention timestamp

#### Scale
- **hours**: ~166
- **pairs**: 350
- **tasks**: 20
- **collection period**: 2022–2023

#### Lineage 적층
(직접 적층 VLA 없음 — task-assist + instruction-following + NL grounding prior 후보)

#### Source check
- 🟢 verified: **166h**, **350 unique instructor-performer pairs**, **License CC-BY-4.0** (정정 — 이전 Microsoft Research 비상용 추정에서 CC-BY-4.0 으로 abstract 라이선스 아이콘 확인), "conversational annotations" + instructor-performer real-time verbal guidance, mistake detection + intervention type prediction benchmark — arXiv:2309.17024 abstract
- 🟡 partial: 20 daily-life task (이전 메모리; abstract 미명시)
- 🔴 unverified: HoloLens version, hand tracking spec
- ❓ needs-human: dialogue 텍스트의 NL annotation 형식, mistake/intervention 라벨 taxonomy

#### Sources
- arXiv: [arXiv:2309.17024](https://arxiv.org/abs/2309.17024)
- 공식: [web](https://holoassist.github.io/)

</details>

---

## Hand-DOF 우선순위 (PROBE 타깃 정렬)

행이 robot-action 데이터인지 human-video 데이터인지 별도로 분류한 뒤,
PROBE Sharpa 22-DOF 타깃에 닿는 정도로 별점.

**⭐⭐⭐ PROBE-direct (hand-DOF retargetable)**
- 🤖 **AgiBot World** — 유일한 *대규모 멀티-임베디먼트 + dexterous hand*
  robot 데이터. xhand 22-DOF 옵션 포함. D22 v1 후보의 핵심 자리.
- 🤖 **DexMimicGen** — humanoid 편향이지만 *16-DOF per hand bimanual
  synthetic*. Real-to-sim-to-real 파이프라인 검증. ⚠ CC-BY-NC-SA-4.0
  비상용.
- 🤖 **MolmoAct2-BimanualYAM** — Allen AI YAM bimanual rig × ~720h.
  Hand-DOF / gripper-vs-dexterous spec 미확인이지만 *bimanual + MolmoAct2
  적층 검증* 이라는 위치가 크다. 다음 사이클 검증 우선.
- 🔀 **UniHand-2.0** — Being-H0.5 자체 구축. *human video → 22-DOF
  hand trajectory retarget*. Sharpa 호환 형식.
- 👤 **HOI4D / ARCTIC / OakInk / AssemblyHands / Assembly101** —
  robot action 은 없지만 *4D hand pose + 객체 상태* 가 잘 정렬되어 있어
  *retarget* 으로 hand prior 보강 가능. ARCTIC 는 bimanual articulated,
  OakInk 는 intent label 풍부, AssemblyHands 는 egocentric bimanual,
  Assembly101 는 1 ego + 8 exo 의 가장 정밀한 bimanual assembly. 라이선스는
  모두 NC.
- 👤 **Ego-Exo4D** — *paired egocentric + multi-exocentric* 의 가장 큰
  skilled-task corpus (~1300h, 800+ skilled performers). P2 multi-cam
  fuser + skilled-task NL grounding 두 자리에 동시 닿음.

**⭐⭐ Gripper-only / VLM-prior 보강 (간접 기여)**
- 🤖 **OXE · BridgeData V2 · DROID · RoboMIND · ALOHA · MolmoBot-Data** —
  가장 풍부한 real-world robot 데이터, 임베디먼트 다양성 6~22 robots,
  NL instruction 검증. 우리 hand 학습에는 직접 의미 작지만 *팔 / 일반
  시각 / 언어 grounding* prior 에 유효. (MolmoBot-Data 는 플랫폼 spec
  미확인이라 잠정 분류.)
- 👤 **Ego4D / Epic Kitchens 100 / EgoExoLearn / HoloAssist** —
  egocentric 인간 비디오. vision/temporal/NL prior 의 대규모 corpus.
  HoloAssist 는 instructor-performer dialogue 가 추가되어 NL grounding
  보강에 특화. Ego4D 는 gated, Epic / HoloAssist 는 NC.

**⭐ 보조**
- 🤖 **RH20T** — 6-axis force/torque 가 유일하게 포함 — *촉각* 학습의
  데이터-쪽 유일 후보. P2 D11 사전학습 deferred 와 연결.
- 🤖 **ManiSkill 3** — simulation-only, sim-to-real gap 고려.
- 🤖 **RT-1** — RT-X 로 흡수, 별도 의미 적음.
- 🤖 **MolmoAct2-SO100/101** — SO-ARM 저비용 6-DOF + gripper. PROBE 의
  Sharpa hand 와 닿는 면 적음.

---

## D22 의사결정 가이드 (현 시점 v1 결정 보조)

| 목표 | 추천 데이터셋 | 이유 |
|---|---|---|
| **Hand dexterity 학습 (robot action)** | AgiBot World + DexMimicGen + UniHand-2.0 + MolmoAct2-BimanualYAM | xhand 22-DOF + bimanual 16-DOF sim + human retarget + YAM bimanual |
| **Hand prior 보강 (human video only)** | HOI4D + ARCTIC + OakInk + AssemblyHands + Assembly101 | 4D hand pose + intent + bimanual ego/exo (모두 NC 라이선스) |
| **Embodiment 다양성** | OXE 또는 RoboMIND | 22 vs 4 robots; OXE 규모 큼, RoboMIND 큐레이션 깨끗 |
| **Real-world 안정성** | DROID + BridgeData V2 | 분산 수집 다양성 + 단일 robot 안정성 |
| **촉각 perception 단서** | RH20T + LeRobot (Shadow subset) | 6-axis F/T + 일부 dexterous |
| **NL instruction 정합** | OXE / BridgeData V2 / DROID + Epic Kitchens / Ego4D / HoloAssist | 자연어 instruction (robot) + 자연어 narration / dialogue (human ego) |
| **Multi-view / ego-exo** | Ego-Exo4D + Assembly101 + EgoExoLearn | 우리 P2 D12 multi-camera fuser 와 연결; Ego-Exo4D 는 skilled-task, Assembly101 은 1+8 정밀 view, EgoExoLearn 은 paired 매칭 |
| **Skilled / instructor-performer** | Ego-Exo4D + HoloAssist | expert commentary / dialogue 가 task intent 라벨 보강 |

---

## Cross-reference 규칙

- **lineage 적층** 절의 VLA 명은 `analysis/_catalogs/vla.md` 의 행과
  1:1 대응. 우리가 어떤 VLA 의 lineage 를 *재현/대체* 하려 한다면, 그
  VLA 가 적층한 데이터셋 조합을 이 표에서 역추적 가능.
- **Embodiment** 절의 hand-DOF 정보는 우리 hand 하드웨어 변경
  (Sharpa 22-DOF → xhand → in-house) 시 *어떤 데이터가 여전히
  호환되는가* 의 판단 근거. P2 D11 swappable sensor head 원칙과 연결.

---

## 출처 정책

- **1차**: arXiv 논문 (모델/시스템) 또는 dataset 공식 README (데이터).
- **2차**: HuggingFace dataset card.
- **3차**: 공식 GitHub README / project page.
- Source-check 마커 (🟢/🟡/🔴/❓) 는 각 카드의 `#### Source check` 절에
  *어떤 필드가 어느 레벨인지* 명시. Scan 표의 7번째 컬럼은 *전반*
  마커 — 한 필드라도 🔴 면 전체 🔴 보수적 표시.
- arXiv ID 위조 금지 (`docs/STYLE.md` §3 절대 원칙). 미확인 ID 는
  source-check 절에서 `❓ needs-human` 으로 표기.
- 2026-05 기준; 새 데이터셋 (특히 hand-DOF) 출시 시 quarterly rebalance.
