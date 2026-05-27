# 랜드마크 VLA lineage 매트릭스 (D19b / D22)

> PROBE D19b "VLM backbone lineage choice" + D22 "Multi-embodiment
> pretraining data" 의사결정 근거. 각 VLA 를
> *lineage 2-tuple = (VLM init) × (Further-pretrain corpus)* 로 식별하고,
> action-expert 구조 + open-weight 접근성 + 우리 stack 적용 메모를 같이
> 적어둠.
>
> v0.3 (2026-05). 공통 컬럼 표준 + 카드 schema 는
> `analysis/_catalogs/README.md` §2 참고. 상단 **scan 표** + 하단
> **per-VLA `<details>` 카드** 하이브리드 — pretrain_data 와 동일 패턴.
> **Scan 표 Source-check 컬럼은 의사결정 4-필드** (License · 총 파라미터 ·
> VLM init · Open-weight) **검증 상태** — 카드 안 부차 필드 (정확한
> control rate · evaluation 점수 등) 의 🔴/❓ 는 영향 없음 (README §2-5).
> `analysis/_catalogs/vlm.md` (VLM 후보) 와
> `analysis/_catalogs/pretrain_data.md` (데이터셋) 가 양 옆에서
> cross-reference.

---

## Scan 표

| VLA | arXiv (year) | License | Access | 총 파라미터 | Lineage 요약 | Source-check |
|---|---|---|---|---|---|---|
| [π0](#pi0) | [2410.24164](https://arxiv.org/abs/2410.24164) (2024) | Apache-2.0 ✅ | 🟢 [gh:Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | 2.6B (2.291B VLM + 0.315B AE) | PaliGemma-2B × OXE + π in-house | 🟢 verified |
| [π0.5](#pi05) | [2504.16054](https://arxiv.org/abs/2504.16054) (2025) | Apache-2.0 ✅ | 🟢 [gh:Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | ~3B (PaliGemma + hierarchical AE) | PaliGemma × π0.5 mix (web + robot) | 🟡 partial |
| [π0-FAST](#pi0-fast) | [2501.09747](https://arxiv.org/abs/2501.09747) (2025) | Apache-2.0 ✅ | 🟢 [gh:Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | 2.6B | PaliGemma-2B × OXE + π (FAST tokenizer) | 🟢 verified |
| [RT-2](#rt2) | [2307.15818](https://arxiv.org/abs/2307.15818) (2023) | Closed ❌ | 🔴 — Google DeepMind internal | 12B / 55B (PaLI-X variants) | PaLI-X × web VLM + robot co-FT | 🟢 verified |
| [OpenVLA](#openvla) | [2406.09246](https://arxiv.org/abs/2406.09246) (2024) | MIT ✅ + Llama-2 ✅¹ | 🟢 [gh:openvla/openvla](https://github.com/openvla/openvla) | 7B | Llama-2-7B + DINOv2 + SigLIP × OXE (~970k traj) | 🟢 verified |
| [Octo](#octo) | [2405.12213](https://arxiv.org/abs/2405.12213) (2024) | Apache-2.0 ✅ | 🟢 [gh:octo-models/octo](https://github.com/octo-models/octo) | 27M / 93M (Small / Base) | (no VLM init — transformer scratch) × OXE (~800k traj) | 🟢 verified |
| [GR00T N1](#groot-n1) | [2503.14734](https://arxiv.org/abs/2503.14734) (2025) | NVIDIA Research ❌ | 🟢 [gh:NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) | ~2.2B (1.34B VLM + ~0.9B AE) | Eagle-2 (1.34B VLM) × humanoid traj + human video + synthetic | 🟢 verified |
| [GR00T N1.5 / N1.7](#groot-n15) | TBD ❓ | NVIDIA Research ❌ | 🟢 [gh:NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) | TBD ❓ | Eagle-2 × GR00T v1 + additional embodiments | 🟡 partial |
| [MolmoAct](#molmoact) | [2508.07917](https://arxiv.org/abs/2508.07917) (2025) | Apache-2.0 ✅ | 🟢 [gh:allenai/MolmoAct](https://github.com/allenai/MolmoAct) | ~7B (Molmo-7B-D) | Molmo-7B-D × MolmoAct Dataset (10k Franka / 93 tasks) + OXE | 🟢 verified |
| [MolmoAct2](#molmoact2) | [2605.02881](https://arxiv.org/abs/2605.02881) (2026) | Apache-2.0 ✅ | 🟢 [gh:allenai/molmoact](https://github.com/allenai/molmoact) | ~7B (Molmo + per-layer KV) | Molmo × BimanualYAM (34.5k / 720h) + DROID-MolmoAct2 + SO100/101 | 🟢 verified |
| [MolmoBot](#molmobot) | [2603.16861](https://arxiv.org/abs/2603.16861) (2026) | Apache-2.0 ✅ | 🟢 [gh:allenai/molmospaces](https://github.com/allenai/molmospaces) | TBD (Molmo 가족) ❓ | Molmo (추정) × MolmoBot-Data (1.7M sim / Franka FR3 + RB-Y1) | 🟡 partial |
| [VLM2VLA](#vlm2vla) | [2509.22195](https://arxiv.org/abs/2509.22195) (2025) | TBD ❓ | ❓ — LoRA weights HF 대기 | 12B base + LoRA delta | Gemma-3-12B-IT (LoRA) × BridgeData v2 NL-formatted (FT only) | 🟡 partial |
| [VLA-Adapter](#vla-adapter) | [2509.09372](https://arxiv.org/abs/2509.09372) (2025) | TBD ❓ | 🟢 [gh:OpenHelix-Team/VLA-Adapter](https://github.com/OpenHelix-Team/VLA-Adapter) | 0.5B (+ adapter) | Prismatic-VLM + Qwen2.5-0.5B × LIBERO + CALVIN (adapter-only) | 🟡 partial |
| [PriorVLA](#priorvla) | [2605.10925](https://arxiv.org/abs/2605.10925) (2026) | TBD ❓ | ❓ — release 확인 필요 | 7B (OpenVLA base) + Adaptation | OpenVLA (CLIP-B/L + Llama-7B) × Prior frozen + Adaptation (RoboTwin 2.0 + LIBERO) | 🔴 unverified |
| [TwinBrainVLA](#twinbrainvla) | [2601.14133](https://arxiv.org/abs/2601.14133) (2026) | TBD ❓ | ❓ — release 확인 필요 | TBD ❓ | TBD × TBD (LIBERO / RoboCasa fine-tune) | 🔴 unverified |
| [Being-H0](#being-h0) | [2507.15597](https://arxiv.org/abs/2507.15597) (2025) | TBD ❓ | 🟢 [gh:BeingBeyond/Being-H](https://github.com/BeingBeyond/Being-H) | TBD ❓ | TBD (BeingBeyond VLM) × large-scale human videos + 3D physical alignment | 🟡 partial |
| [Being-H0.5](#being-h05) | [2601.12993](https://arxiv.org/abs/2601.12993) (2026) | Apache-2.0 ✅ | 🟢 [gh:BeingBeyond/Being-H](https://github.com/BeingBeyond/Being-H) | TBD ❓ (Qwen2.5-VL 추정) | TBD × UniHand-2.0 (~35k h × 30 embodiments / 120B tokens) | 🟡 partial |
| [Xiaomi-Robotics-0](#xiaomi-robotics-0) | [2602.12684](https://arxiv.org/abs/2602.12684) (2026) | TBD ❓ | 🟢 [gh:XiaomiRobotics/Xiaomi-Robotics-0](https://github.com/XiaomiRobotics/Xiaomi-Robotics-0) | 4.7B total | Qwen3-VL-4B-Instruct × ~200M robot timesteps (DROID + MolmoAct + in-house) + 80M+ VL | 🟡 partial |
| [Genesis AI](#genesis-ai) | — | Closed ❌ | 🔴 — undisclosed | undisclosed | undisclosed × undisclosed | 🔴 unverified |

¹ 700M MAU 미만 조건부. 자세한 조건은 각 라이선스 원문 참고.

> 각 행의 이름 링크를 클릭하면 아래 *per-VLA 카드* 의 해당 anchor 로
> 점프합니다. 카드 안의 `<details>` 를 펼치면 Architecture · Training
> data · Action representation · Inference · Eval · Open-weight ·
> Source check · Sources 8개 H4 sub-section 이 보입니다.

---

## Per-VLA 카드

### <a id="pi0"></a>π0

<details>
<summary>PaliGemma-2B × OXE + π in-house · 2.6B params · D19b v1 lineage</summary>

#### Architecture
- **VLM init**: PaliGemma-2B (2.291B params; SigLIP-So400m vision + Gemma 2B LLM)
- **Action expert**: Flow-matching head, 315M params, continuous action
- **총 파라미터**: 2.6B (2.291B VLM + 0.315B AE)
- **분리**: VLM frozen (D19a v1 ↔ PROBE 정합); action expert trainable

#### Training data
- **Further-pretrain corpus**: OXE + π in-house mix (specific composition undisclosed in paper)
- **Pretraining hours**: TBD (in-house data scale 미공개)

#### Action representation
- **space**: continuous action (flow-matching denoising)
- **dimension**: target embodiment 별 (7-DOF arm + gripper 표준 7-dim)
- **control rate**: ~50 Hz (chunked rollout)
- **token form**: continuous vector (no discrete tokenization)

#### Inference
- **latency**: ~50ms per chunk (50 Hz target)
- **GPU**: single A100 80GB (frozen VLM 덕에)
- **async**: ✗ (synchronous chunk rollout)

#### Eval
- **benchmark**: Bridge / Aloha-style real-world (paper §5)
- **score**: paper Table — folding/wiping/cleaning 등
- **OpenPi mirrors**: lerobot integration validated

#### Open-weight
- **가중치**: ✓ Apache-2.0 (openpi release)
- **코드**: ✓ [gh:Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi)
- **체크포인트 위치**: openpi repo release tags
- **license 조건**: Apache-2.0 — 상용 허용

#### Source check
- 🟢 verified: License (Apache-2.0), 2.6B param breakdown (paper §3), flow-matching AE structure (315M), OXE + π in-house mix 사실, openpi 공개
- 🟡 partial: 정확한 control rate, eval benchmark 점수
- 🔴 unverified: π in-house mix 의 정확한 sub-dataset 구성
- ❓ needs-human: paper §3 의 정확한 hyperparameter 표

#### Sources
- arXiv: [arXiv:2410.24164](https://arxiv.org/abs/2410.24164)
- 공식: [gh:Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi)
- HF: [hf:lerobot/pi0](https://huggingface.co/lerobot) (lerobot mirror 가능성)

</details>

---

### <a id="pi05"></a>π0.5

<details>
<summary>PaliGemma × π0.5 mix · hierarchical flow-matching · web + robot co-train</summary>

#### Architecture
- **VLM init**: PaliGemma (variant TBD — π0 와 동일 2B 추정)
- **Action expert**: Flow-matching head, hierarchical (high-level + low-level)
- **총 파라미터**: ~3B 추정 (π0 와 유사)
- **분리**: VLM frozen + AE trainable (D19a v1)

#### Training data
- **Further-pretrain corpus**: π0.5 mix — web pretraining + robot co-training (paper §3)
- **co-training 비율**: web : robot mix (정확 비율 paper 본문 확인 필요)

#### Action representation
- **space**: continuous action (hierarchical denoising)
- **dimension**: embodiment-별
- **control rate**: 50 Hz target
- **token form**: continuous vector

#### Inference
- **latency**: hierarchical inference 로 high-level 은 느리고 low-level 은 빠름
- **GPU**: A100 80GB
- **async**: hierarchical decomposition 으로 부분적

#### Eval
- **benchmark**: π0 와 비슷 + web 데이터 효과 비교 (paper §5)
- **score**: TBD (paper 본문 확인 필요)

#### Open-weight
- **가중치**: ✓ Apache-2.0 (openpi release)
- **코드**: ✓ openpi
- **체크포인트 위치**: openpi tags

#### Source check
- 🟢 verified: License (Apache-2.0), openpi 공개, hierarchical inference 구조
- 🟡 partial: PaliGemma variant size, web + robot mix 비율
- 🔴 unverified: 정확한 파라미터 분해, control rate, eval 점수
- ❓ needs-human: paper §3 의 co-training schedule

#### Sources
- arXiv: [arXiv:2504.16054](https://arxiv.org/abs/2504.16054)
- 공식: [gh:Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi)

</details>

---

### <a id="pi0-fast"></a>π0-FAST

<details>
<summary>π0 + FAST action tokenizer · inference-optimized variant</summary>

#### Architecture
- **VLM init**: PaliGemma-2B (π0 와 동일)
- **Action expert**: Flow-matching head + **FAST action tokenizer** (DCT-based compression)
- **총 파라미터**: 2.6B (π0 와 동일)
- **분리**: VLM frozen + AE trainable + FAST tokenizer 추가

#### Training data
- OXE + π mix (π0 와 동일 lineage)
- FAST tokenizer 만 추가 학습

#### Action representation
- **space**: discrete tokens (FAST tokenization)
- **dimension**: original action vector → DCT 압축 → discrete code
- **control rate**: ~5× faster than π0 (paper 주장)
- **token form**: discrete FAST tokens

#### Inference
- **latency**: π0 대비 ~5× 빠름 (paper §4 인용)
- **GPU**: A100 80GB
- **async**: ✓ (FAST chunked decoding)

#### Eval
- **benchmark**: π0 task 들 + latency-sensitive 환경
- **score**: paper §4 — π0 와 동급 success rate + 빠른 latency

#### Open-weight
- **가중치**: ✓ Apache-2.0
- **코드**: ✓ openpi
- **체크포인트 위치**: openpi release

#### Source check
- 🟢 verified: License, FAST tokenizer (DCT-based), inference speedup 주장
- 🟡 partial: 정확한 speedup factor (5×)
- 🔴 unverified: 정확한 token vocabulary size
- ❓ needs-human: FAST tokenizer training 의 데이터 / 시간

#### Sources
- arXiv: [arXiv:2501.09747](https://arxiv.org/abs/2501.09747)
- 공식: [gh:Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi)

</details>

---

### <a id="rt2"></a>RT-2

<details>
<summary>PaLI-X × web VLM + robot co-FT · web/robot co-FT prior retention 의 선구자</summary>

#### Architecture
- **VLM init**: PaLI-X (Google internal; 12B / 55B variants)
- **Action expert**: discrete action tokens (text encoding)
- **총 파라미터**: 12B / 55B (variants)
- **분리**: VLM full-FT (no freeze) — D20 forgetting risk

#### Training data
- **Further-pretrain corpus**: web VLM data + robot co-FT (RT-1 data + 일부 RT-2 자체)
- **co-FT 비율**: web : robot ≈ 9:1 (paper §3 추정)

#### Action representation
- **space**: discrete action tokens (text-encoded — 예: "1 128 91 241 5 101 127")
- **dimension**: 7 (6-DOF + gripper) → 256 vocab tokens
- **control rate**: ~3 Hz (text decoding 비용)
- **token form**: existing LLM vocab 의 가장 적게 쓰이는 256개 재사용

#### Inference
- **latency**: ~300ms (LLM autoregressive decoding)
- **GPU**: cloud (Google internal TPU)
- **async**: ✗

#### Eval
- **benchmark**: emergent capabilities (paper §5) — semantic generalization
- **score**: closed paper; 자체 task suite

#### Open-weight
- **가중치**: ✗ Closed
- **코드**: ✗
- **체크포인트 위치**: Google DeepMind internal

#### Source check
- 🟢 verified: License (Closed), PaLI-X base, discrete action token approach, web/robot co-FT
- 🟡 partial: 정확한 PaLI-X variant (12B vs 55B 사용 비율)
- 🔴 unverified: 정확한 co-FT 비율, control rate
- ❓ needs-human: RT-2 후속 (RT-2-X) 의 변경 사항

#### Sources
- arXiv: [arXiv:2307.15818](https://arxiv.org/abs/2307.15818)
- 공식: [web](https://robotics-transformer2.github.io/)

</details>

---

### <a id="openvla"></a>OpenVLA

<details>
<summary>Llama-2-7B + DINOv2 + SigLIP × OXE · 첫 대규모 open-weight VLA</summary>

#### Architecture
- **VLM init**: Llama-2-7B (LLM) + DINOv2 (vision) + SigLIP (vision)
- **Action expert**: Continuous action token (OFT — Optimized Fine-Tuning)
- **총 파라미터**: 7B
- **분리**: VLM full-FT (Llama-2 trainable; DINOv2 + SigLIP partially frozen)

#### Training data
- **Further-pretrain corpus**: Open X-Embodiment (~970k trajectories — paper 명시)
- **fine-tuning**: LoRA fine-tune 검증 (paper §6)

#### Action representation
- **space**: continuous action via OFT (text encoding fallback)
- **dimension**: 7 (6-DOF + gripper)
- **control rate**: ~6 Hz
- **token form**: continuous token (OFT) — RT-2 의 discrete 보다 빠름

#### Inference
- **latency**: ~150ms
- **GPU**: A100 80GB
- **async**: ✗

#### Eval
- **benchmark**: BridgeData V2, RT-1 evaluation suite
- **score**: paper §5 — RT-2-X 와 비교 우위

#### Open-weight
- **가중치**: ✓ MIT (OpenVLA code) + Llama-2 license (weights)
- **코드**: ✓ [gh:openvla/openvla](https://github.com/openvla/openvla)
- **체크포인트 위치**: HuggingFace `openvla/openvla-7b`
- **license 조건**: Llama-2 — 700M MAU 미만 상용 허용

#### Source check
- 🟢 verified: License (MIT + Llama-2), 7B param, Llama-2 + DINOv2 + SigLIP combo, OXE ~970k traj, OFT method
- 🟡 partial: 정확한 vision encoder freeze 비율
- 🔴 unverified: 정확한 control rate (paper §4 확인 필요)
- ❓ needs-human: post-release 의 OpenVLA-Mini / OpenVLA-OFT 등 변종

#### Sources
- arXiv: [arXiv:2406.09246](https://arxiv.org/abs/2406.09246)
- 공식: [gh:openvla/openvla](https://github.com/openvla/openvla)
- HF: [hf:openvla/openvla-7b](https://huggingface.co/openvla/openvla-7b)

</details>

---

### <a id="octo"></a>Octo

<details>
<summary>Transformer scratch (no VLM init) × OXE · D19b 대조군</summary>

#### Architecture
- **VLM init**: (없음 — transformer from scratch)
- **Action expert**: Diffusion transformer with action chunking
- **총 파라미터**: 27M (Small) / 93M (Base)
- **분리**: 전체 trainable (no freeze)

#### Training data
- **Further-pretrain corpus**: Open X-Embodiment (~800k trajectories — paper 명시)
- **multi-embodiment co-training**: ✓

#### Action representation
- **space**: continuous action (diffusion denoising)
- **dimension**: embodiment-별 chunked (8-step chunk 표준)
- **control rate**: ~5 Hz (chunk rate)
- **token form**: continuous chunked vector

#### Inference
- **latency**: ~50ms (diffusion inference is fast for 27M)
- **GPU**: single GPU (small enough)
- **async**: ✗

#### Eval
- **benchmark**: BridgeData V2, ALOHA, real-world transfer
- **score**: paper §5 — zero-shot transfer 성능

#### Open-weight
- **가중치**: ✓ Apache-2.0
- **코드**: ✓ [gh:octo-models/octo](https://github.com/octo-models/octo)
- **체크포인트 위치**: HuggingFace `rail-berkeley/octo-small` / `octo-base`

#### Source check
- 🟢 verified: License (Apache-2.0), 27M/93M param, no VLM init (scratch), OXE ~800k traj, diffusion transformer + chunking
- 🟡 partial: 정확한 chunk size, control rate
- 🔴 unverified: 정확한 hyperparameter 표
- ❓ needs-human: post-release 의 Octo-Large 또는 variant

#### Sources
- arXiv: [arXiv:2405.12213](https://arxiv.org/abs/2405.12213)
- 공식: [gh:octo-models/octo](https://github.com/octo-models/octo)
- HF: [hf:rail-berkeley/octo-base](https://huggingface.co/rail-berkeley/octo-base)

</details>

---

### <a id="groot-n1"></a>GR00T N1

<details>
<summary>Eagle-2 × humanoid + human video + synthetic · dual-system (System 1 + System 2)</summary>

#### Architecture
- **VLM init**: Eagle-2 (NVIDIA, 1.34B VLM portion)
- **Action expert**: Diffusion transformer (System 1 — fast loop) + System 2 (slow planning)
- **총 파라미터**: ~2.2B (1.34B VLM + ~0.9B AE)
- **분리**: System 1 = trainable AE; System 2 = VLM (partial freeze)

#### Training data
- **Further-pretrain corpus**: humanoid robot trajectories + human video + synthetic data
- **embodiment 편향**: humanoid (PROBE Sharpa hand 닿는 면 적음)

#### Action representation
- **space**: continuous action (diffusion)
- **dimension**: humanoid 양팔 + hand (variable)
- **control rate**: ~60 Hz (System 1 fast loop)
- **token form**: continuous chunked

#### Inference
- **latency**: System 1 ~16ms; System 2 ~slow planning
- **GPU**: NVIDIA datacenter
- **async**: ✓ (System 1 / System 2 dual-loop)

#### Eval
- **benchmark**: Isaac Sim humanoid tasks
- **score**: paper §5 — System 2 vs no-System 2 ablation

#### Open-weight
- **가중치**: ✓ NVIDIA Research (non-commercial)
- **코드**: ✓ [gh:NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)
- **체크포인트 위치**: NVIDIA NGC release
- **license 조건**: ❌ NVIDIA Research Preview — 비상용

#### Source check
- 🟢 verified: License (NVIDIA Research, non-commercial), Eagle-2 1.34B VLM, dual-system architecture, humanoid focus, GR00T repo open
- 🟡 partial: 정확한 AE 파라미터 (0.9B 추정), control rate
- 🔴 unverified: synthetic 데이터의 정확한 비율, human video corpus 출처
- ❓ needs-human: paper §3 의 정확한 training mix 비율

#### Sources
- arXiv: [arXiv:2503.14734](https://arxiv.org/abs/2503.14734)
- 공식: [gh:NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)

</details>

---

### <a id="groot-n15"></a>GR00T N1.5 / N1.7

<details>
<summary>GR00T N1 후속 — 추가 embodiment + 정제된 dual-system</summary>

#### Architecture
- **VLM init**: Eagle-2 (NVIDIA — N1 과 동일 추정)
- **Action expert**: Diffusion transformer (refined)
- **총 파라미터**: TBD ❓
- **분리**: N1 과 유사

#### Training data
- **Further-pretrain corpus**: GR00T v1 mix + additional embodiments (정확한 추가 데이터 미공개)

#### Action representation
- N1 과 유사 (continuous chunked)

#### Inference
- N1 과 유사

#### Eval
- TBD — 공식 release note 확인 필요

#### Open-weight
- **가중치**: ✓ NVIDIA Research (non-commercial)
- **코드**: ✓ [gh:NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)

#### Source check
- 🟡 partial: NVIDIA GR00T 가족 후속 release 사실, License 동일 추정
- 🔴 unverified: 정확한 파라미터, 추가 embodiment 목록, eval 점수
- ❓ needs-human: arXiv 또는 release note 확인 필요 (현재 official paper TBD)

#### Sources
- 공식: [gh:NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)

</details>

---

### <a id="molmoact"></a>MolmoAct

<details>
<summary>Molmo-7B-D × MolmoAct Dataset (10k Franka / 93 tasks) — 3D reasoning</summary>

#### Architecture
- **VLM init**: Molmo-7B-D (Qwen2 7B base + OpenAI CLIP vision)
- **Action expert**: Discrete token (depth + visual trace)
- **총 파라미터**: ~7B (Molmo base 그대로 사용)
- **분리**: VLM partial FT + visual trace token addition

#### Training data
- **Further-pretrain corpus**: MolmoAct Dataset (10k Franka trajectories / 93 tasks) + OXE subset
- **3D reasoning**: depth + visual trace token 으로 3D pose 학습

#### Action representation
- **space**: discrete token (depth + visual trace)
- **dimension**: TBD (visual trace 형식)
- **control rate**: TBD
- **token form**: depth + trace token (Molmo extension)

#### Inference
- TBD — Molmo 7B 추정 latency (A100)

#### Eval
- **benchmark**: real-world Franka pick-place (paper §5)
- **score**: paper §5

#### Open-weight
- **가중치**: ✓ Apache-2.0
- **코드**: ✓ [gh:allenai/MolmoAct](https://github.com/allenai/MolmoAct)
- **체크포인트 위치**: HuggingFace allenai org

#### Source check
- 🟢 verified: arXiv:2508.07917, Molmo-7B-D base, 10k Franka / 93 tasks dataset, License Apache-2.0
- 🟡 partial: depth + visual trace token 구조 (paper §3)
- 🔴 unverified: 정확한 파라미터 (frozen vs trainable 비율), control rate
- ❓ needs-human: post-release 의 MolmoAct mini / variant

#### Sources
- arXiv: [arXiv:2508.07917](https://arxiv.org/abs/2508.07917)
- 공식: [gh:allenai/MolmoAct](https://github.com/allenai/MolmoAct)
- HF: [hf:allenai/MolmoAct](https://huggingface.co/allenai)

</details>

---

### <a id="molmoact2"></a>MolmoAct2

<details>
<summary>Molmo × per-layer KV-cache + BimanualYAM (34.5k demos / 720h) — 현존 최대 open bimanual VLA</summary>

#### Architecture
- **VLM init**: Molmo (variant TBD)
- **Action expert**: Per-layer KV-cache conditioning + discrete token
- **총 파라미터**: ~7B (Molmo base)
- **분리**: VLM frozen + per-layer KV-cache 가 action conditioning 담당

#### Training data
- **Further-pretrain corpus**: data mix —
  - **BimanualYAM**: 34,500 teleoperated demos / 720h (현존 최대 open bimanual)
  - **DROID-MolmoAct2**: DROID 데이터 재가공
  - **SO100/101**: lerobot SO-ARM 데이터
  - + web data + embodied reasoning

#### Action representation
- **space**: discrete token (Molmo 가족 표준)
- **dimension**: bimanual (양팔)
- **control rate**: TBD
- **token form**: per-layer KV-cache + discrete

#### Inference
- **latency**: paper 주장 — π0.5 대비 37× 빠름 (techfastforward 보도)
- **GPU**: A100 / H100
- **async**: ✓ (per-layer KV 캐싱)

#### Eval
- **benchmark**: π0.5 비교 + bimanual tasks
- **score**: paper 주장 — π0.5 outperform

#### Open-weight
- **가중치**: ✓ Apache-2.0
- **코드**: ✓ [gh:allenai/molmoact](https://github.com/allenai/molmoact)
- **체크포인트 위치**: HuggingFace allenai

#### Source check
- 🟢 verified: arXiv:2605.02881, License Apache-2.0, BimanualYAM 34.5k/720h, π0.5 outperform 주장, per-layer KV 구조
- 🟡 partial: 정확한 data mix 비율, 37× speedup 검증
- 🔴 unverified: 정확한 파라미터, SO100/101 데이터 규모
- ❓ needs-human: paper §3 의 정확한 hyperparameter / KV-cache 구조

#### Sources
- arXiv: [arXiv:2605.02881](https://arxiv.org/abs/2605.02881)
- 공식: [gh:allenai/molmoact](https://github.com/allenai/molmoact)
- 공식 blog: [web](https://allenai.org/blog/molmoact2)

</details>

---

### <a id="molmobot"></a>MolmoBot

<details>
<summary>Molmo (추정) × MolmoBot-Data 1.7M sim — zero-shot manipulation</summary>

#### Architecture
- **VLM init**: Molmo 가족 (Molmo-7B-D 추정 — 공식 release 명시 필요)
- **Action expert**: TBD (Molmo 가족 token 추정)
- **총 파라미터**: TBD ❓
- **분리**: TBD

#### Training data
- **Further-pretrain corpus**:
  - **MolmoBot-Data**: 1.7M expert sim trajectories
  - 두 platform: Franka FR3 + Rainbow Robotics RB-Y1
  - 11K+ unique objects · 94K+ procedurally generated environments · 8 task types
  - **MolmoSpaces ecosystem**: 232k env + 48k objects + 8 task types

#### Action representation
- **space**: TBD
- **dimension**: per-platform (FR3 vs RB-Y1)
- **control rate**: TBD
- **token form**: TBD

#### Inference
- TBD — paper §5 확인 필요

#### Eval
- **benchmark**: sim + zero-shot real transfer
- **score**: paper 주장 — zero-shot real manipulation

#### Open-weight
- **가중치**: ✓ Apache-2.0 (Allen AI 표준 추정)
- **코드**: ✓ [gh:allenai/molmospaces](https://github.com/allenai/molmospaces)
- **체크포인트 위치**: TBD

#### Source check
- 🟢 verified: arXiv:2603.16861, MolmoBot-Data 1.7M sim, 11K obj / 94K env / 8 tasks, Franka FR3 + Rainbow RB-Y1, MolmoSpaces ecosystem 232k env
- 🟡 partial: License Apache-2.0 (Allen AI 표준 추정)
- 🔴 unverified: 정확한 VLM init variant, 총 파라미터, action representation
- ❓ needs-human: paper §3 의 architecture 상세

#### Sources
- arXiv: [arXiv:2603.16861](https://arxiv.org/abs/2603.16861)
- 공식 project: [web](https://allenai.github.io/MolmoBot/)
- 공식 blog: [web](https://allenai.org/blog/molmobot-robot-manipulation)
- ecosystem: [gh:allenai/molmospaces](https://github.com/allenai/molmospaces)

</details>

---

### <a id="vlm2vla"></a>VLM2VLA

<details>
<summary>Gemma-3-12B-IT (LoRA) × BridgeData v2 NL-formatted · LoRA-only path, fine-tune only</summary>

#### Architecture
- **VLM init**: Gemma-3-12B-IT (Google instruction-tuned)
- **Action expert**: Discrete NL-action token (LLM 자체가 action 출력)
- **총 파라미터**: 12B base + LoRA delta (LoRA on all linear modules)
- **분리**: Gemma full frozen + LoRA delta trainable (D20 LoRA-minimal 경로)

#### Training data
- **Further-pretrain corpus**: BridgeData v2 NL-formatted (Gemini-2.5 로 NL 변환)
- **추가 사전학습 없음** — *fine-tune only*. 이게 VLM2VLA lineage 의 정체성.

#### Action representation
- **space**: NL-style action — "move arm forward 5cm" 같은 자연어
- **dimension**: text length variable
- **control rate**: ~3-5 Hz (LLM decoding)
- **token form**: NL token (Gemma vocab)

#### Inference
- **latency**: LLM autoregressive decoding (~300ms)
- **GPU**: A100 80GB (12B)
- **async**: ✗

#### Eval
- **benchmark**: forgetting mitigation 측정 (paper §5) — 일반 VQA 성능 보존
- **score**: paper §5

#### Open-weight
- **가중치**: TBD ❓ (LoRA delta HF release 대기)
- **코드**: TBD
- **체크포인트 위치**: TBD

#### Source check
- 🟢 verified: arXiv:2509.22195, Gemma-3-12B-IT base, BridgeData v2 NL-formatted (Gemini-2.5), fine-tune only (no further pretrain), LoRA on all linear modules
- 🟡 partial: 정확한 LoRA rank, training step 수
- 🔴 unverified: License (LoRA weights 자체 release 미공개), 정확한 inference latency
- ❓ needs-human: VLM2VLA repo 공개 여부 및 license

#### Sources
- arXiv: [arXiv:2509.22195](https://arxiv.org/abs/2509.22195)

</details>

---

### <a id="vla-adapter"></a>VLA-Adapter

<details>
<summary>Prismatic-VLM + Qwen2.5-0.5B × LIBERO + CALVIN · adapter-only, 0.5B 극한</summary>

#### Architecture
- **VLM init**: Prismatic-VLM + Qwen2.5-0.5B (극소 backbone)
- **Action expert**: Bridge Attention (action-side adapter)
- **총 파라미터**: 0.5B + adapter (D20 action-side adapter 패턴)
- **분리**: VLM frozen + Bridge Attention adapter trainable

#### Training data
- **Further-pretrain corpus**: LIBERO + CALVIN benchmark (adapter-only)
- **robot 데이터 사전학습 없음** — 벤치마크 fine-tune 만

#### Action representation
- **space**: continuous via Bridge Attention
- **dimension**: 7 (LIBERO / CALVIN 표준)
- **control rate**: TBD
- **token form**: continuous (adapter output)

#### Inference
- **latency**: 0.5B 매우 빠름
- **GPU**: single consumer GPU (RTX 4090 정도)
- **async**: ✗

#### Eval
- **benchmark**: LIBERO + CALVIN
- **score**: paper §5 — minimal backbone 극한 검증

#### Open-weight
- **가중치**: TBD ❓
- **코드**: ✓ [gh:OpenHelix-Team/VLA-Adapter](https://github.com/OpenHelix-Team/VLA-Adapter)
- **체크포인트 위치**: TBD

#### Source check
- 🟢 verified: arXiv:2509.09372, Prismatic-VLM + Qwen2.5-0.5B base, Bridge Attention adapter, LIBERO + CALVIN benchmark, no robot-data pretraining
- 🟡 partial: 0.5B 극한 backbone 가용성
- 🔴 unverified: License, 정확한 adapter 구조 (Bridge Attention spec)
- ❓ needs-human: HuggingFace 가중치 release 여부

#### Sources
- arXiv: [arXiv:2509.09372](https://arxiv.org/abs/2509.09372)
- 공식: [gh:OpenHelix-Team/VLA-Adapter](https://github.com/OpenHelix-Team/VLA-Adapter)

</details>

---

### <a id="priorvla"></a>PriorVLA

<details>
<summary>OpenVLA × Prior frozen + Adaptation Expert · two-expert prior source</summary>

#### Architecture
- **VLM init**: OpenVLA (CLIP-B/L + Llama-7B)
- **Action expert**: Two-expert — Prior Expert (frozen) + Adaptation Expert (trainable)
- **총 파라미터**: 7B (OpenVLA base) + Adaptation delta
- **분리**: Prior frozen + Adaptation trainable (D20 prior-preserving adaptation 패턴)

#### Training data
- **Further-pretrain corpus**: RoboTwin 2.0 + LIBERO (task-specific Adaptation 학습)
- **Prior 는 OpenVLA 가중치 그대로 사용**

#### Action representation
- OpenVLA 와 유사 (continuous action via OFT)

#### Inference
- TBD — Two-expert 추가 비용

#### Eval
- **benchmark**: RoboTwin 2.0 + LIBERO
- **score**: paper §5 — Prior preservation 측정

#### Open-weight
- **가중치**: TBD ❓
- **코드**: TBD
- **체크포인트 위치**: TBD

#### Source check
- 🟡 partial: arXiv:2605.10925, OpenVLA base, Two-expert (Prior frozen + Adaptation), RoboTwin 2.0 + LIBERO 학습
- 🔴 unverified: License, 가중치 release, 정확한 Adaptation Expert 파라미터
- ❓ needs-human: PriorVLA repo / HF release 위치

#### Sources
- arXiv: [arXiv:2605.10925](https://arxiv.org/abs/2605.10925)

</details>

---

### <a id="twinbrainvla"></a>TwinBrainVLA

<details>
<summary>AsyMoT — frozen generalist + trainable specialist · PROBE D19a+D4 직접 analog</summary>

#### Architecture
- **VLM init**: TBD ❓ (paper 확인 필요)
- **Action expert**: AsyMoT (Asymmetric Mixture of Transformers) — frozen generalist + trainable specialist + flow-matching
- **총 파라미터**: TBD ❓
- **분리**: Generalist frozen + Specialist trainable (PROBE D19a freeze + D4 sharing 의 가장 가까운 선례)

#### Training data
- **Further-pretrain corpus**: task-specific fine-tune (LIBERO / RoboCasa)

#### Action representation
- continuous (flow-matching)

#### Inference
- TBD

#### Eval
- **benchmark**: LIBERO + RoboCasa
- **score**: TBD

#### Open-weight
- **가중치**: TBD ❓
- **코드**: TBD

#### Source check
- 🟡 partial: arXiv:2601.14133, AsyMoT 구조 (frozen generalist + trainable specialist + flow-matching)
- 🔴 unverified: VLM init 이 무엇인지, 가중치 release, eval 점수
- ❓ needs-human: TwinBrainVLA paper § architecture 상세

#### Sources
- arXiv: [arXiv:2601.14133](https://arxiv.org/abs/2601.14133)

</details>

---

### <a id="being-h0"></a>Being-H0

<details>
<summary>Large-scale human videos × 3D physical alignment · hand-focused part-level tokenization</summary>

#### Architecture
- **VLM init**: TBD ❓ (BeingBeyond 자체 VLM 추정)
- **Action expert**: Part-level motion tokenization (hand-focused)
- **총 파라미터**: TBD ❓
- **분리**: TBD

#### Training data
- **Further-pretrain corpus**: large-scale human videos + 3D physical alignment annotations

#### Action representation
- **space**: hand part tokens (finger joint level)
- **dimension**: per-hand-part
- **token form**: discrete part tokens

#### Inference
- TBD

#### Eval
- **benchmark**: hand manipulation tasks
- **score**: TBD

#### Open-weight
- **가중치**: TBD ❓
- **코드**: ✓ [gh:BeingBeyond/Being-H](https://github.com/BeingBeyond/Being-H)

#### Source check
- 🟡 partial: arXiv:2507.15597, BeingBeyond GitHub repo 공개, hand-focused part-level tokenization 사실
- 🔴 unverified: License, VLM init, 총 파라미터, 정확한 human video corpus 출처
- ❓ needs-human: Being-H GitHub config 의 정확한 model spec

#### Sources
- arXiv: [arXiv:2507.15597](https://arxiv.org/abs/2507.15597)
- 공식: [gh:BeingBeyond/Being-H](https://github.com/BeingBeyond/Being-H)

</details>

---

### <a id="being-h05"></a>Being-H0.5

<details>
<summary>Qwen2.5-VL (추정) × UniHand-2.0 (~35k h × 30 embodiments) · MoT + MoF</summary>

#### Architecture
- **VLM init**: TBD (Qwen2.5-VL 추정 — Being-H GitHub config 직접 확인 필요)
- **Action expert**: Mixture-of-Transformers (MoT) + Mixture-of-Flow (MoF)
- **총 파라미터**: TBD ❓
- **분리**: TBD

#### Training data
- **Further-pretrain corpus**: UniHand-2.0
  - ~35,000h × 30 embodiments
  - 400M+ samples / 120B tokens
  - ~16k h ego video + ~14k h robot manip + ~5k h VL
- **cross-embodiment** ✓

#### Action representation
- **space**: hand joint trajectory (22+ DOF retargetable)
- **dimension**: per-target-hand (Inspire / xhand / LEAP / Allegro / ShadowHand)
- **token form**: MoT + MoF (Mixture-of-* token)

#### Inference
- TBD

#### Eval
- **benchmark**: cross-embodiment hand manipulation
- **score**: TBD

#### Open-weight
- **가중치**: ✓ Apache-2.0 (Being-H repo 표준 추정)
- **코드**: ✓ [gh:BeingBeyond/Being-H](https://github.com/BeingBeyond/Being-H)

#### Source check
- 🟢 verified: arXiv:2601.12993, UniHand-2.0 35k h / 30 embodiments / 400M samples / 120B tokens, MoT + MoF 구조
- 🟡 partial: VLM init (Qwen2.5-VL 추정 — paper 본문에 명시 안 됨)
- 🔴 unverified: 총 파라미터, License (Apache-2.0 추정)
- ❓ needs-human: Being-H GitHub config 의 VLM backbone + 가중치 위치

#### Sources
- arXiv: [arXiv:2601.12993](https://arxiv.org/abs/2601.12993)
- 공식: [gh:BeingBeyond/Being-H](https://github.com/BeingBeyond/Being-H)

</details>

---

### <a id="xiaomi-robotics-0"></a>Xiaomi-Robotics-0

<details>
<summary>Qwen3-VL-4B-Instruct × DROID + MolmoAct + in-house · open-weight + real-time async</summary>

#### Architecture
- **VLM init**: Qwen3-VL-4B-Instruct
- **Action expert**: Continuous action (async-execution optimized)
- **총 파라미터**: **4.7B total** (Qwen3-VL 4B + AE 0.7B)
- **분리**: VLM frozen + AE trainable + async execution layer

#### Training data
- **Further-pretrain corpus**:
  - ~200M robot trajectory timesteps:
    - DROID
    - MolmoAct dataset
    - in-house cross-embodiment data
  - + 80M+ VL samples (general VL prior 보강)

#### Action representation
- **space**: continuous action
- **dimension**: cross-embodiment (variable)
- **control rate**: real-time async (paper 주장)
- **token form**: continuous chunked + async execution

#### Inference
- **latency**: real-time async (정확 수치 paper 본문)
- **GPU**: consumer GPU on-device 가능 (4.7B)
- **async**: ✓ (architecture 자체가 async-exec 최적화)

#### Eval
- **benchmark**: cross-embodiment + real-time tasks
- **score**: paper §5 — async execution 우위 측정

#### Open-weight
- **가중치**: ✓ (XiaomiRobotics GitHub release)
- **코드**: ✓ [gh:XiaomiRobotics/Xiaomi-Robotics-0](https://github.com/XiaomiRobotics/Xiaomi-Robotics-0)
- **체크포인트 위치**: TBD ❓ (HuggingFace 또는 직접 release)

#### Source check
- 🟢 verified: arXiv:2602.12684, Qwen3-VL-4B-Instruct base, 4.7B total, ~200M robot timesteps + 80M+ VL, async execution focus, Xiaomi-Robotics GitHub repo 공개
- 🟡 partial: 정확한 control rate 수치, in-house 데이터 규모
- 🔴 unverified: License (open-weight 인데 정확한 license sub-clause 미확인)
- ❓ needs-human: HuggingFace release URL, license 확정

#### Sources
- arXiv: [arXiv:2602.12684](https://arxiv.org/abs/2602.12684)
- 공식: [gh:XiaomiRobotics/Xiaomi-Robotics-0](https://github.com/XiaomiRobotics/Xiaomi-Robotics-0)

</details>

---

### <a id="genesis-ai"></a>Genesis AI

<details>
<summary>Undisclosed — VLA-only without RL · §3 antagonist 증거 (System0 necessity test)</summary>

#### Architecture
- **VLM init**: undisclosed
- **Action expert**: undisclosed (VLA-only, no explicit RL component)
- **총 파라미터**: undisclosed
- **분리**: undisclosed

#### Training data
- undisclosed

#### Action representation
- undisclosed

#### Inference
- undisclosed (real-world contact-rich dexterity 시연 영상)

#### Eval
- 시연 영상 only (no benchmark)

#### Open-weight
- **가중치**: ❌ Closed
- **코드**: ❌
- **체크포인트 위치**: 비공개

#### Source check
- 🟢 verified: Genesis AI 가 VLA-only 로 contact-rich dexterity 시연 (PROBE §3 antagonist 증거)
- 🔴 unverified: 모든 architecture / training / eval 상세 — 회사 비공개

#### Sources
- 시연 영상 / 회사 페이지 only

</details>

---

## Cross-reference 규칙

- **VLM init** 셀의 모델명은 `analysis/_catalogs/vlm.md` 의 행과 1:1 대응 —
  "PaliGemma-2B" → vlm.md PaliGemma 행, "Qwen3-VL-4B-Instruct" → vlm.md
  Qwen3-VL 행 등. vlm.md 에서 빠진 새 VLM 이 여기 등장하면 vlm.md 에 추가
  필요.
- **Training data** 카드의 데이터셋 명은 `analysis/_catalogs/pretrain_data.md`
  의 행과 1:1 대응 — "OXE" → pretrain_data.md OXE 행, "BridgeData v2" →
  BridgeData V2 행, "DROID" → DROID 행 등.
- **PROBE 적용 메모** (카드 footer / scan 표 Lineage 요약) 의 `D19/D19b/D20/
  D22/D23` 토큰은 `context/P4.md` §3 의 Decision Log 와 직접 link.

## 출처 정책

- arXiv 1차, HuggingFace papers / 공식 GitHub README 보조.
- URL 은 *반드시 resolve 검증* 된 것만 링크. 미확인은 `TBD (이유)` 또는 ❓.
- "fine-tune only, no further pretrain" 같이 lineage 의 *부재* 도 명시
  (이게 lineage 의 한 형태). 예: VLM2VLA 는 추가 사전학습이 없음 — 이게 그
  lineage 의 정체성 일부.
- 2026-05 기준; 새 VLA release 시 quarterly rebalance.
