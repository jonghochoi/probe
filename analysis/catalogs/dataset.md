# 데이터셋 큐레이션 (VLA further-pretrain corpus)

![Updated](https://img.shields.io/badge/updated-2026--06--02-blue.svg)

## 🤖 Robot action

* **AgiBot World** — AgiBot G1 humanoid teleop real-world. [![arXiv](https://img.shields.io/badge/arXiv-2503.06669-b31b1b.svg)](https://arxiv.org/abs/2503.06669) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://agibot-world.com/)
  - 1M+ traj · 217 tasks
  - 양팔 7+7-DOF · hand 1 or 16~22-DOF dexterous · bimanual
  - CC-BY-NC-SA-4.0 ❌ · 적층: Genie Operator-1 (GO-1)
* **DexMimicGen** — NVIDIA GR1 humanoid sim augmented from human seed. [![arXiv](https://img.shields.io/badge/arXiv-2410.24185-b31b1b.svg)](https://arxiv.org/abs/2410.24185) [![GitHub](https://img.shields.io/badge/GitHub-Code-black)](https://github.com/NVlabs/dex-mimicgen)
  - 21K synth episodes from 60 human seed (~350× per-demo)
  - GR1 humanoid 7+7-DOF · Inspire 16-DOF per hand · bimanual sim
  - CC-BY-NC-SA-4.0 ❌ · 적층: NVIDIA 내부 GR00T mix 추정 ❓ · Robocasa
* **MolmoAct2-BimanualYAM** — Allen AI YAM bimanual rig teleop. [![arXiv](https://img.shields.io/badge/arXiv-2605.02881-b31b1b.svg)](https://arxiv.org/abs/2605.02881) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://allenai.org/blog/molmoact2)
  - 34,500 demos · 720h
  - bimanual tabletop · hand-DOF ❓ (gripper 추정)
  - Apache-2.0 ❓ · 적층: MolmoAct2
* **RoboMIND** — 다중 embodiment 큐레이션 corpus. [![arXiv](https://img.shields.io/badge/arXiv-2412.13877-b31b1b.svg)](https://arxiv.org/abs/2412.13877) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://x-humanoid-robomind.github.io/)
  - 107K traj · 479 tasks · 96 obj classes · 5K real-world failure demos
  - Franka / UR5e / AgileX dual-arm / humanoid · gripper + dual dexterous hands
  - License ❓ · 적층: 자체 baseline (외부 적층 미확인)
* **OXE** — Open X-Embodiment Collaboration (multi-institution). [![arXiv](https://img.shields.io/badge/arXiv-2310.08864-b31b1b.svg)](https://arxiv.org/abs/2310.08864) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://robotics-transformer-x.github.io/)
  - 22 robots · 527 skills · 160K tasks · 2018–2023
  - arm 6–7 DOF · gripper-only (1-DOF)
  - CC-BY-4.0 · 적층: π0 · π0.5 · π0-FAST · OpenVLA · Octo · GR00T N1 (부분) · Xiaomi-Robotics-0 (부분)
* **BridgeData V2** — UC Berkeley RAIL WidowX single-arm. [![arXiv](https://img.shields.io/badge/arXiv-2308.12952-b31b1b.svg)](https://arxiv.org/abs/2308.12952) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://rail-berkeley.github.io/bridgedata/)
  - 60,096 traj · 24 environments
  - WidowX 250 7-DOF · gripper-only (1-DOF)
  - CC-BY-SA-4.0 · 적층: VLM2VLA (NL-formatted) · OpenVLA (부분) · Octo (부분)
* **DROID** — Stanford + Berkeley Franka in-the-wild mobile cart. [![arXiv](https://img.shields.io/badge/arXiv-2403.12945-b31b1b.svg)](https://arxiv.org/abs/2403.12945) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://droid-dataset.github.io/)
  - 76K traj · 350h · 564 scenes · 84 tasks · 50 collectors / 3 continents
  - Franka Panda 7-DOF + Robotiq 2F-85 (1-DOF) · mobile cart
  - CC-BY-4.0 · 적층: Xiaomi-Robotics-0 (코어) · OpenVLA fine-tune · Universal-Policy
* **ALOHA / Mobile ALOHA** — 2× ViperX 300 leader-follower bimanual. [![arXiv](https://img.shields.io/badge/arXiv-2304.13705-b31b1b.svg)](https://arxiv.org/abs/2304.13705) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://tonyzhaozh.github.io/aloha/)
  - 50+ public HF subsets · 50 Hz
  - ViperX 300S 6-DOF × 2 · gripper-only per arm · bimanual
  - MIT · 적층: lerobot 다수 subset · ACT 계열 · π0 fine-tune · RT-X co-train · X-VLA 6-bench
* **LeRobot (aggregated)** — HuggingFace 표준 dataset format 통합. [![arXiv](https://img.shields.io/badge/arXiv-2602.22818-b31b1b.svg)](https://arxiv.org/abs/2602.22818) [![HuggingFace](https://img.shields.io/badge/HuggingFace-Model-yellow)](https://huggingface.co/lerobot) [![GitHub](https://img.shields.io/badge/GitHub-Code-black)](https://github.com/huggingface/lerobot)
  - 50+ embodiments
  - Franka · WidowX · ALOHA · SO-100 · Shadow 24-DOF subset · arm 6–7 / hand 1–24
  - Apache-2.0 · 적층: lerobot 내부 benchmark (외부 적층은 sub-subset 단위)
* **MolmoBot-Data** — Allen AI MolmoBot MuJoCo simulation. [![arXiv](https://img.shields.io/badge/arXiv-2603.16861-b31b1b.svg)](https://arxiv.org/abs/2603.16861) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://allenai.github.io/MolmoBot/) [![GitHub](https://img.shields.io/badge/GitHub-Code-black)](https://github.com/allenai/molmospaces)
  - 1.7M expert demos · 11K+ obj · 94K+ env · 8 task types
  - Franka FR3 (7-DOF) + Rainbow RB-Y1 (mobile, spec ❓) · gripper
  - Apache-2.0 ❓ · 적층: MolmoBot
* **RH20T** — SJTU MVIG contact-rich w/ wrist F/T + audio. [![arXiv](https://img.shields.io/badge/arXiv-2307.00595-b31b1b.svg)](https://arxiv.org/abs/2307.00595) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://rh20t.github.io/)
  - 110K sequences
  - Franka / UR5 / Flexiv 7-DOF + Robotiq · 6-axis wrist FT + audio (유일 tactile)
  - CC-BY-SA-4.0 · 적층: 직접 적층 없음 (OXE sub-dataset 부분 포함 가능)
* **ManiSkill 3** — SAPIEN 시뮬레이션 high-throughput. [![arXiv](https://img.shields.io/badge/arXiv-2410.00425-b31b1b.svg)](https://arxiv.org/abs/2410.00425) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://maniskill.readthedocs.io/)
  - 12 domains · 30K+ FPS · simulation only
  - Franka / UR5 / Fetch / Unitree / Allegro 16-DOF / ShadowHand 24-DOF (일부)
  - CC-BY-4.0 · 적층: PriorVLA · VLA-Adapter (LIBERO 옆 sim bench)
* **RT-1** — Google Everyday Robot teleop. [![arXiv](https://img.shields.io/badge/arXiv-2212.06817-b31b1b.svg)](https://arxiv.org/abs/2212.06817) 🔒 closed (Google internal)
  - ~130K traj · 700+ tasks
  - Google Everyday Robot 7-DOF + gripper · 1 Hz token emission
  - Closed ❌ · 적층: RT-2 (후속) · RT-X 흡수 후 OXE sub-dataset 으로 재배포
* **MolmoAct2-SO100/101** — MolmoAct2 corpus on lerobot SO-ARM. [![arXiv](https://img.shields.io/badge/arXiv-2605.02881-b31b1b.svg)](https://arxiv.org/abs/2605.02881) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://allenai.org/blog/molmoact2)
  - scale ❓
  - SO-100 / SO-101 · arm 6-DOF + 1-DOF parallel-jaw
  - License ❓ · 적층: MolmoAct2 (BimanualYAM + DROID-MolmoAct2 + SO100/101 합산 중 일부)

## 🔀 Mixed (robot + human)

* **UniHand-2.0** — BeingBeyond human-video → multi-hand retarget. [![arXiv](https://img.shields.io/badge/arXiv-2601.12993-b31b1b.svg)](https://arxiv.org/abs/2601.12993) [![GitHub](https://img.shields.io/badge/GitHub-Code-black)](https://github.com/BeingBeyond/Being-H)
  - ~35K h (ego 16K + robot 14K + VL 5K) · 400M+ samples · 120B+ tokens
  - 30 embodiments retarget (Inspire / xhand / LEAP / Allegro / ShadowHand) · hand 6–24 DOF
  - Apache-2.0 · 적층: Being-H0.5

## 👤 Human video

* **HOI4D** — PKU + 컨소시엄 4D hand-object interaction. [![arXiv](https://img.shields.io/badge/arXiv-2203.01577-b31b1b.svg)](https://arxiv.org/abs/2203.01577) [![Website](https://img.shields.io/badge/Website-Link-blue)](http://www.hoi4d.top/)
  - 4,000 seq · 800 objects · 16 categories · 2.4M RGB-D frames
  - human ego MANO hand pose · per-frame action segmentation
  - CC-BY-NC-4.0 ❓ · 적층: 직접 적층 없음 (hand-object retarget 후보)
* **ARCTIC** — ETH + MPI bimanual articulated object interaction. [![arXiv](https://img.shields.io/badge/arXiv-2204.13662-b31b1b.svg)](https://arxiv.org/abs/2204.13662) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://arctic.is.tue.mpg.de/)
  - 339 sequences · 2.1M frames · 11 articulated objects
  - bimanual MANO (51 × 2) · contact map
  - CC-BY-NC-SA-4.0 ❓ · 적층: 직접 적층 없음 (bimanual articulated retarget 후보)
* **OakInk** — ShanghaiTech intent-annotated grasp. [![arXiv](https://img.shields.io/badge/arXiv-2203.15709-b31b1b.svg)](https://arxiv.org/abs/2203.15709) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://oakink.net/)
  - 50K grasps · 100 objects · 5 intent categories
  - single-hand MANO
  - CC-BY-NC-4.0 ❓ · 적층: 직접 적층 없음 (grasp prior 후보)
* **AssemblyHands** — Meta egocentric bimanual 3D hand pose. [![arXiv](https://img.shields.io/badge/arXiv-2304.12301-b31b1b.svg)](https://arxiv.org/abs/2304.12301) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://assemblyhands.github.io/)
  - 3.0M annotated frames · 490K ego · 34 subjects · 101 toys
  - bimanual ego
  - CC-BY-4.0 · 적층: 직접 적층 없음 (bimanual ego pose prior 후보)
* **Assembly101** — TUM + Meta bimanual assembly multi-view. [![arXiv](https://img.shields.io/badge/arXiv-2203.14712-b31b1b.svg)](https://arxiv.org/abs/2203.14712) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://assembly-101.github.io/)
  - 4,321 videos · 513h · 101 toys · 18M 3D hand poses · 100K coarse + 1M fine action segments
  - 4 ego + 8 exo (12 cam) · bimanual
  - CC-BY-NC-4.0 ❓ · 적층: 직접 적층 없음 (bimanual assembly hand prior 후보)
* **Ego-Exo4D** — Meta + 컨소시엄 paired ego + multi-exo skilled task. [![arXiv](https://img.shields.io/badge/arXiv-2311.18259-b31b1b.svg)](https://arxiv.org/abs/2311.18259) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://ego-exo4d-data.org/)
  - 1,286h · 740 participants · 13 cities · 2022–2023
  - skilled human (sports / music / dance / bike repair) · narration + expert commentary
  - Ego-Exo4D license ⚠️ (gated) ❓ · 적층: 직접 적층 없음 (paired ego-exo skilled prior 후보)
* **Ego4D** — Meta + 컨소시엄 large-scale daily-life egocentric. [![arXiv](https://img.shields.io/badge/arXiv-2110.07058-b31b1b.svg)](https://arxiv.org/abs/2110.07058) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://ego4d-data.org/)
  - 3,670h · 900+ subjects · 74 locations / 9 countries · 2019–2022
  - human ego · narration (~50/hour)
  - Ego4D license ⚠️ (gated) · 적층: 직접 적층 없음 (vision/temporal/NL prior 표준)
* **Epic Kitchens 100** — Bristol/Toronto/CMU cooking egocentric. [![arXiv](https://img.shields.io/badge/arXiv-2006.13256-b31b1b.svg)](https://arxiv.org/abs/2006.13256) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://epic-kitchens.github.io/100)
  - 100h · 45 kitchens · 90K action segments · 20M frames · 700 videos
  - human cooking ego · verb-noun action label
  - CC-BY-NC-SA-4.0 · 적층: 직접 적층 없음 (cooking-task NL grounding 후보)
* **EgoExoLearn** — Shanghai AI Lab paired ego-exo. [![arXiv](https://img.shields.io/badge/arXiv-2403.16182-b31b1b.svg)](https://arxiv.org/abs/2403.16182) [![GitHub](https://img.shields.io/badge/GitHub-Code-black)](https://github.com/OpenGVLab/EgoExoLearn)
  - 120h paired
  - ego + exo · NL instruction + 시연 매칭 라벨
  - CC-BY-4.0 · 적층: 직접 적층 없음 (P2 multi-cam fuser 와 연결)
* **HoloAssist** — Microsoft mixed-reality instructor-performer paired. [![arXiv](https://img.shields.io/badge/arXiv-2309.17024-b31b1b.svg)](https://arxiv.org/abs/2309.17024) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://holoassist.github.io/)
  - 166h · 350 pairs · 20 daily-life tasks · 2022–2023
  - HoloLens 6DoF head + hand tracking · instructor-performer dialogue
  - CC-BY-4.0 · 적층: 직접 적층 없음 (task-assist + NL grounding prior 후보)
