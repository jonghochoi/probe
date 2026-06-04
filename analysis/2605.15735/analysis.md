# Paper Analysis — UAM: A Dual-Stream Perspective on Forgetting in VLA Training

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | UAM: A Dual-Stream Perspective on Forgetting in VLA Training |
| 저자 | Jianke Zhang, Yuanfei Luo, Yucheng Hu, Xiaoyu Chen, Yanjiang Guo, Ziyang Liu, Hongbin Xu, Tian Lan, Jianyu Chen (Tsinghua University · ByteDance Seed) |
| 링크 | [arXiv:2605.15735](https://arxiv.org/abs/2605.15735) |
| 발행일 / 버전 | 2026-05-18 · v2 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |
| 관련 Pillar | P4, P1 |
| 태그 | forgetting, vla-arch |

---

## 🧭 한 줄 요약 (TL;DR)

VLA 학습에서 다중모달 능력이 깎이는 현상(embodiment tax)을 단일 인코더 병목 문제로 진단하고, 사전학습된 생성형 모델로 초기화한 평행 Dorsal Expert + visual-dynamics 보조 손실로 의미·제어 경로를 구조 차원에서 갈라 frozen·co-training·gradient stop 없이도 VLM 능력의 95% 이상을 유지한 채 end-to-end 행동 학습을 해냅니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLM 백본을 action 데이터에 fine-tune 하는 표준 VLA 레시피가 사전학습된 다중모달 능력을 꾸준히 갉아먹는 현상(저자들이 명명한 *embodiment tax*).
- **기존 접근의 한계** — VLM freeze 는 제어 성능을 떨어뜨리고, VL co-training 은 외부 코퍼스 규모·다양성·gradient 간섭 차폐 장치에 의존합니다. 어느 쪽도 *왜* tax 가 생기는지는 드러내지 않고 증상만 피해갑니다.
- **본 논문의 가설** — 인지(ventral)와 시각운동 제어(dorsal)를 나눠 처리하는 영장류 시각 피질과 달리, 현재 VLA 는 두 요구를 단일 인코더에 강제로 통과시킵니다. 이 *표상 병목*이 망각을 부르는 인코더 차원의 원인입니다.
- **왜 지금 중요한가** — VLA 의 가치는 action head 자체가 아니라 VLM 이 가져오는 open-vocabulary 인식·공간 추론·지시 따르기 등 *복제 불가능한 사전 능력*에서 옵니다. 이를 지키지 못하는 학습 레시피는 long-tail 일반화에서 의미 지렛대를 잃습니다.

---

## 🧩 핵심 기여

- VLA fine-tuning 망각을 수치로 재는 forgetting metric $`\Delta`$ 를 정의하고, 두 backbone(Qwen2.5-7B, PaliGemma) × 세 결합(Freeze/+MoT/+MLP)에 걸쳐 *embodiment tax* 가 어느 조합에서나 나타남을 측정.
- 신경과학의 two-streams 이론을 차용해 의미·제어 경로 분리를 구조에서 풀자는 **Dorsal Expert** 가설을 내놓고, 3-expert(MoT) 매크로 아키텍처로 정형화.
- 초기화 × 입력 modality × 보조 손실 6-variant sweep 으로 Dorsal Expert 설계 공간을 통제 실험하고, **생성형 UMM(Bagel) 초기화 + visual-dynamics 손실** 조합만이 frozen probe 에서도 제어 성능을 지킨다는 결과를 확인.
- 채택된 UAM 인스턴스화는 frozen·gradient-stop·VL replay 없이 행동 데이터만으로 학습되면서도 VLM 능력의 95% 이상을 유지하고, 다양한 OOD 실세계 조작에서 비교 baseline 중 최고 평균 성공률을 달성.
- Attention 지도에서 $`E_{\text{sem}}`$ 은 의미 엔티티(What), $`E_{\text{dor}}`$ 는 로봇 팔·상호작용 경계·전역 맥락(Where/How)에 집중하는 **자발적 기능 분기**가 학습 도중 emergent 하게 떠오릅니다.

---

## 🔑 기술 키워드

- **VLA (Vision–Language–Action model)** — VLM 위에 행동 head 를 얹어 관찰·언어로부터 저수준 액션을 예측하는 정책. 본 논문에서는 fine-tuning 가설의 시험대.
- **Embodiment tax** — 행동 데이터만으로 VLA 를 학습할 때 VLM 의 일반 다중모달 능력이 꾸준히 떨어지는 비용. 저자들이 이 논문에서 처음 명명한 용어.
- **Two-streams hypothesis (Ventral/Dorsal)** — 영장류 시각 피질이 객체 인식(ventral)과 공간·운동 제어(dorsal)를 별개의 경로로 처리한다는 신경과학 가설. UAM 아키텍처의 설계 비유.
- **Dorsal Expert ($`E_{\text{dor}}`$)** — VLM 옆에 병렬로 두는 시각 전용 두 번째 경로. 제어 관련 시각 표상을 떠맡아 $`E_{\text{sem}}`$ 의 의미 능력 침식을 막는 역할.
- **Mixture-of-Transformers (MoT)** — $`\pi_0`$ 가 사용한 병렬 라우팅 기법으로, expert 별 파라미터를 분리하되 attention 마스크로 정보 교환을 허용. UAM 은 3-expert 결합 primitive 로 채택.
- **Visual-dynamics objective ($`\mathcal{L}_{\text{wm}}`$)** — 다음 시점(goal) 관찰 예측을 보조 손실로 부과해 Dorsal 경로가 *장면이 어떻게 변하는가* 라는 중간 추론을 수행하도록 강제하는 신호.
- **Unified Multimodal Model (UMM) — Bagel** — 이해와 생성을 단일 transformer 로 결합한 사전학습 모델. UAM 의 VLM 과 Dorsal 양쪽 초기화 출처.
- **Forgetting metric ($`\Delta`$)** — $`\Delta(f_{\text{VLA}})=1-\frac{S(f_{\text{VLA}})}{S(f_{\text{VLM}})}`$ 로 정의된, VLM 능력 대비 상대 손실률. 0 이면 완전 보존, 1 이면 완전 붕괴.
- **Knowledge insulation / VL co-training** — 기존 망각 완화 두 갈래(파라미터 동결 또는 VQA 데이터 보충). UAM 이 architectural separation 으로 대체하려는 대안군.

---

## 🔬 방법론

### 직관

VLA 망각의 원인은 *데이터 부족*이 아니라 *인코더 병목*이라는 진단이 출발점입니다. 표준 VLA 는 사전학습된 VLM 인코더 $`E_{\text{sem}}`$ 하나가 (i) 언어 결합 의미 표상과 (ii) 제어에 필요한 공간·동역학 시각 특징을 동시에 공급하도록 강제됩니다. Action 손실이 더 조밀하고 trajectory-driven 이라 fine-tuning 도중 의미 표상이 덮어쓰여지고, MoT 로 action expert 의 파라미터를 떼어내도 *입력 시각 특징의 출처*가 여전히 $`E_{\text{sem}}`$ 인 한 병목은 그대로 남습니다.

> "We hypothesize that this is a key source of forgetting: the encoder is a representational bottleneck through which two qualitatively different demands (semantic understanding and visuomotor control) are forced to flow." (§3.2)
> (저자들은 이 한 문장에 논문 전체의 설계 의도를 응축합니다. 망각을 데이터 문제가 아니라 인코더 병목 문제로 다시 정의하므로, 해법도 *추가 데이터*가 아닌 *추가 경로*로 향합니다.)

해법은 영장류 시각의 ventral/dorsal 분리에서 차용한 **두 번째 시각 경로**입니다. Dorsal Expert $`E_{\text{dor}}`$ 가 제어 관련 시각 표상을 떠맡으면 $`\theta_{\text{sem}}`$ 을 갱신하지 않고도 action 학습을 굴릴 수 있습니다. 다만 빈 expert 만 끼워 넣어서는 부족하다는 것이 §3.3 의 핵심 관찰입니다 — *어떤 prior 로 채우는가* 와 *어떤 보조 목표가 그 경로를 깨우는가* 가 승부를 가릅니다.

![Figure 1 — Reducing the Embodiment Tax with UAM](https://arxiv.org/html/2605.15735/fig/overview-last.png)

> "Figure 1: Reducing the Embodiment Tax with UAM. Action-only VLA fine-tuning can erode pretrained VLM capability. UAM separates semantic and control pathways through a visual-dynamics bridge, enabling end-to-end action learning while better retaining multimodal competence." (§1)
> (왼쪽: 표준 fine-tuning 이 의미 표상을 덮어써 일반화가 떨어진다는 진단. 가운데: MoT 라우팅으로 의미·제어 경로를 갈라놓은 UAM 매크로. 오른쪽: 생성형 초기화 + visual-dynamics 가 semantic-act gap 을 가장 작게 줄인다는 핵심 주장의 도해.)

### 아키텍처

표준 VLA 는 $`a_{t}=E_{\text{act}}(E_{\text{sem}}(I_{t},L;\theta_{\text{sem}});\,\theta_{\text{act}})`$ 의 직렬 형태이고, MoT 로 $`E_{\text{act}}`$ 를 떼어내도 시각 특징은 여전히 $`E_{\text{sem}}`$ 을 거칩니다. UAM 은 여기에 평행한 세 번째 expert 를 더해 다음과 같이 바꿉니다.

$$Z_{\text{sem}}=E_{\text{sem}}(I_{t},L;\theta_{\text{sem}}),\quad Z_{\text{dor}}=E_{\text{dor}}(X_{\text{dor}};\theta_{\text{dor}}),\quad a_{t}=E_{\text{act}}(Z_{\text{sem}},Z_{\text{dor}};\,\theta_{\text{act}})$$

여기서 $`X_{\text{dor}}\in\{I_{t},\,q\}`$ — Dorsal expert 입력은 원본 관찰 토큰이거나 learnable query 토큰입니다(설계 공간 축). 세 expert 는 병렬 MoT 로 묶이며, 토큰 라우팅은 인코더별로 갈리는데 ViT 가 만든 토큰은 $`E_{\text{sem}}`$ 으로, VAE 가 만든 토큰은 $`E_{\text{dor}}`$ 로 보내집니다(§9.3).

![Figure 3 — UAM and Dorsal Expert design space](https://arxiv.org/html/2605.15735/fig/method_dorsal.png)

> "Figure 3: Unified Action Model (UAM) and the Dorsal Expert design space. (Bottom) The three-expert macro-architecture: a semantic expert $`E_{\text{sem}}`$ initialized from a pretrained VLM, a Dorsal Expert $`E_{\text{dor}}`$, and an action expert $`E_{\text{act}}`$, coupled via parallel routing. (Top) The Dorsal Expert design space we explore in Sec. 3.3, varying input modality and initialization (random, VLM, generative expert with or without an auxiliary visual-dynamics objective)." (§3.2)
> (논문의 핵심 매크로. 아래 패널이 3-expert 결합 구조, 위 패널이 §3.3 의 설계 공간 sweep 이 변주하는 두 축 — 초기화 × 입력 modality + 보조 손실 — 을 같이 보여줍니다.)

채택된 UAM(Variant 3b) 인스턴스화는 VLM 과 Dorsal 양쪽을 사전학습 Bagel 가중치로 초기화하고, action 토큰은 별도의 action expert 로 라우팅하며, BagelVLA(§9.3) 의 단일 step denoising 과 dual flow-matching 결합을 그대로 따릅니다.

### 학습 목표 / 손실

Dorsal 경로를 단순 prior 컨테이너로 두는 Variant 3a 는 다음 손실만 씁니다.

$$\mathcal{L}_{\text{total}}=\mathcal{L}_{\text{act}}$$

이에 비해 UAM(Variant 3b)은 goal-observation 예측을 보조 손실로 더합니다.

$$\mathcal{L}_{\text{total}}=\mathcal{L}_{\text{act}}+\lambda\mathcal{L}_{\text{wm}}(\hat{I}_{t+1},I_{t+1})$$

> "Variant 3a performs similarly to Variant 2a across both simulation and real-world tasks, indicating that a generative prior on its own does not bring more benefits than the VLM prior. Variant 3b widens this gap substantially: it attains the highest action performance under the unfrozen setting, the smallest gap to that level under the frozen probe, and the strongest results on real-world OOD tasks." (§3.3)
> (Prior 만 바꿔서는 부족하고, *중간 추론을 시키는 보조 목표*가 더해졌을 때 비로소 Dorsal 경로가 load-bearing 해진다는 결론입니다. 본 논문 설계의 핵심 두 piece — 올바른 prior 와 그 prior 를 깨우는 목표 — 가 모두 필요하다는 주장입니다.)

Forgetting metric 정의는 다음과 같습니다.

$$\Delta(f_{\text{VLA}})\;=\;1-\frac{S(f_{\text{VLA}})}{S(f_{\text{VLM}})}$$

$`S(\cdot)`$ 은 MMMU·MME·MMBench·MathVista·MMStar·TextVQA·MM-Vet 등 표준 다중모달 이해 벤치마크 평균이며, $`f_{\text{VLM}}`$ 은 action 학습 *이전* 의 백본 점수입니다.

### 학습 셋업

> "we initialize both the VLM expert and the dorsal expert using the pre-trained Bagel checkpoint ... Subsequently, the model is trained directly for 30,000 steps on 3k demonstration trajectories collected from the ALOHA bimanual robotic system (without any co-training on additional vision-language data)." (§4)
> (대규모 embodied pre-training 단계를 건너뛰고 ALOHA 시연 3k 만으로 30k step 직접 학습합니다. 의미 보존이 *데이터 보강*이 아닌 *구조*에서 온다는 본문 주장과 맞물립니다.)

- **Backbone & 초기화**: Bagel(7B MoT) 체크포인트 → VLM expert 와 Dorsal expert 양쪽; action expert 는 2B MoT (§4 본문 Table 4 의 사이즈 표기 기준).
- **하드웨어 / 자원**: 8× A800. Calvin ABC-D effective batch 192, 30k steps; RoboTwin 16 task × 50 demo, 30k steps, action chunk 16, 3-step subsampling(effective horizon 48); real-robot 30k steps, action chunk 24, 세 시점(primary + 양손 wrist) 입력 (§12).
- **Optimizer**: Qwen 계열 LR `1e-5`, PaliGemma 계열 LR `5e-5`. FSDP + packed datasets (§12, §8).
- **데이터**: 3,000 ALOHA bimanual 시연(pick-and-place, water flower, stack cubes/bowls, pour fries, sweep rubbish, press button, drawer, wiping/inserting/hanging/plugging 등). VQA·VL co-training 미사용.
- **시뮬레이션 평가**: Calvin ABC-D 1,000 task × len 5; RoboTwin 16 task × 100 trial (unseen instructions). Real-world: task 별 20회 무작위 초기 자세.
- **Inference 비용**: 7B VLM + 7B Dorsal + 2B MoT = 1500 ms / step (Qwen7B-π0 의 1300 ms 대비 +15%, §13).

---

## 📊 실험 설정과 결과

평가는 두 축 — (i) Multimodal understanding 보존(망각 지표), (ii) Action 수행 — 으로 나눠 측정합니다(§7). UAM 의 핵심 검증은 *VL co-training 없이 action-only 학습*에도 다중모달 점수가 VLM 상한에 다가서는지였습니다.

| Method | #Params | MMMU | MME-P | MME-S | MMBench | MM-Vet | MathVista | MMStar | TextVQA |
|---|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL (7B, VLM 상한) | 7B | 58.6 | — | 2347 | 83.5 | 67.1 | 68.2 | 63.9 | 84.9 |
| BAGEL (UMM 상한) | 7B MoT | 55.3 | 1687 | 2388 | 85.0 | 67.2 | 73.1 | — | — |
| OpenVLA (action-only) | 7B | 0 | 0 | — | 0 | 0 | 0 | 0 | 0 |
| ChatVLA\* (VL co-training) | 2B | 37.4 | 1435 | — | 69.0 | — | — | 47.2 | 71.2 |
| $`\pi_{0.5}`$-base\* (VL co-training) | 2B MoT | 18.7 | 1032 | 1241 | 7.3 | — | — | — | — |
| **UAM (Ours, action-only)** | **7B MoT** | **53.7** | **1607** | **2289** | **83.7** | **63.4** | **68.2** | **61.3** | **84.2** |

\* 다중모달 reasoning 데이터를 co-training 으로 섞은 VLA. (Tab. 2)

> "the proposed UAM automatically preserves the capabilities of its original VLM backbone (with only a marginal performance drop of less than 5%), without incorporating VQA co-training or relying on gradient-blocking techniques." (§4.1, Tab. 2)
> (UAM 의 핵심 수치 주장입니다. OpenVLA 가 다중모달 능력을 *완전히* 잃고 ChatVLA· $`\pi_{0.5}`$ 가 co-training 을 쓰고도 큰 폭으로 떨어지는 반면, UAM 은 Bagel 상한 대비 평균 5% 미만 손실에 그칩니다.)

망각이 *왜* 어디서나 일어나는지에 대한 통제 측정도 별도로 제시됩니다(Tab. 3).

| VLA Arch (VLM + Action Head) | Action | VQA-AVG | MME | MMMU | MMBench |
|---|---|---|---|---|---|
| Qwen2.5-Freeze + MLP (7B+10M) | 30.12 | 74.32 | 2354 | 53.7 | 85.2 |
| Qwen2.5 + MoT (7B+1B) | 65.98 | 37.94 | 1675 | 30.46 | 23.54 |
| Qwen2.5 + MLP (7B+10M) | 71.14 | 0 | 0 | 0 | 0 |
| Paligemma-Freeze + MLP (2.3B+10M) | 22.18 | 53.18 | 1670 | 34.66 | 65.23 |
| Paligemma + MoT (2.3B+0.3B) | 70.18 | 10.83 | 400 | 6.2 | 12.00 |
| Paligemma + MLP (2.3B+10M) | 70.12 | 0 | 0 | 0 | 0 |

> "even when the action policies have largely converged, the degree of retained VLM performance varies significantly across different architectures ... while the sequential MLP head achieves comparable action accuracy to the MoT architecture, its inherent VLM capabilities are catastrophically destroyed (yielding a VQA score of 0)." (§8, Tab. 3)
> (Freeze 는 action 이 무너지고 MLP head 는 action 은 살리지만 VQA 가 0 으로 붕괴합니다. MoT 는 완화는 시키지만 여전히 큰 폭의 tax 를 냅니다 — 라우팅을 떼어 놓는 것만으로는 부족하다는 진단의 수치 근거입니다.)

OOD 일반화는 두 baseline(Qwen-$`\pi_0`$ 2-expert, Variant 2a 의 VLM-init Dorsal) 대비 실세계 ALOHA 양손 플랫폼에서 측정됩니다.

> "we observe that the model with a VLM-initialized dorsal expert (VLM-init) achieves comparable performance to the 2-expert baseline on in-domain tasks (90% vs. 87%). However, it underperforms the 2-expert model (which lacks a dorsal expert) across all other out-of-distribution (OOD) tasks." (§4.2, Fig. 5)
> (VLM 가중치를 단순 복제한 Dorsal 은 *in-domain* 만 따라잡고 OOD 에서는 오히려 baseline 보다 처집니다. 경로를 더했다는 사실보다 *그 경로가 무엇을 학습하는가* 가 본질이라는 ablation 입니다.)

표상 분석에서는 Dorsal 경로가 실제로 다른 정보를 실어 나르는지를 주의 지도로 확인합니다.

![Figure 6 — Attention maps during action generation](https://arxiv.org/html/2605.15735/fig/exp-repr.png)

> "Figure 6: Visualization of attention maps during action generation. For each task, we show the input third-view image, attention over $`E_{\text{dor}}`$ visual tokens, and $`E_{\text{sem}}`$ visual tokens. The action queries attend to different regions: attention over $`E_{\text{sem}}`$ tokens is concentrated on task-relevant semantic entities, such as target objects and goal regions, while attention over $`E_{\text{dor}}`$ tokens focuses more on the robot arm, interaction regions, and global scene context." (§4.3)
> (UAM 학습 후 명시적 grounding 감독 없이도 What/How 분기가 emergent 하게 떠오른다는 정성 증거입니다. P1 에서 우리가 노리는 Body/Hand 분리에 대해, *데이터 라벨이 아니라 architectural separation 만으로* 기능 분기를 끌어낼 선례가 됩니다.)

추론 latency 는 표준 Qwen7B-$`\pi_0`$ 대비 +15% 수준이며(1300 → 1500 ms, Tab. 4), Dorsal expert 가 single-step denoising 만 수행하므로 두 배 가까이 늘어난 파라미터에도 비용 증가가 제한된다는 주장입니다.

---

## ⚖️ 한계

- **추론·학습 비용 증가** — VLM 7B + Dorsal 7B + Action 2B 의 총 16B 규모로 $`\pi_{0.5}`$(2.6B) 대비 약 6배의 메모리 풋프린트, latency +15%. 저자도 결론(§5)에서 "the world-model-based bridge introduces additional training and inference complexity" 를 한계로 명시.
- **데이터 셋업 범위가 좁음** — 실세계 검증이 ALOHA 양손 ± 3k 시연 1종에 한정. 손가락 단위 contact-rich 조작(예: 회전, 도구 조작)이나 비양손 embodiment 로의 전이성은 입증되지 않음.
- **세부 하이퍼 비공개** — visual-dynamics 보조 손실 가중 $`\lambda`$, Dorsal 입력 토큰 수의 정확한 분포, BagelVLA 단일 step denoising 의 정확한 구성은 본문에 명시 수치가 없고 BagelVLA 인용에 의존.
- **PaliGemma 적용 제외** — UAM 실험은 Qwen2.5 + Bagel 라인업에만 적용되며, "extensive additional alignment between multimodal understanding and generation" 부담으로 PaliGemma 라인에는 의도적으로 적용하지 않음 (§9.3). 다른 VLM/UMM 조합으로의 일반성은 검증되지 않음.
- **Dorsal Expert 의 prior 의존성** — Bagel 처럼 *이해+생성 결합* 사전학습 모델이 prerequisites. 일반 비디오 backbone 이나 순수 generative model 로의 확장은 미실험.

---

## ♻️ 재현성

- **공개 자원** — Project Page: `https://cladernyjorn.github.io/Unified-Action-Model.github.io` (§Abstract 캡션). 본문에는 코드/체크포인트 공개 여부 명시 없음.
- **백본** — Bagel ([deng2025bagel] 인용) 사전학습 체크포인트 필요. BagelVLA([hu2026bagelvla]) 의 단일 step denoising 구현 의존.
- **벤치마크** — Calvin ABC-D (mees2022Calvin), RoboTwin (chen2025robotwin 16-task 서브셋), MMMU·MME·MMBench·MM-Vet·MathVista·MMStar·TextVQA. 평가 프로토콜은 §7·§12 에 비교적 상세.
- **하드웨어** — 8× A800 GPU 클러스터, ALOHA 양손 플랫폼. Sharpa 손가락 단위 tactile 등의 추가 입력은 사용하지 않음.

---

## 🎯 관련 Pillar / Decision (P# / D#)

본 논문은 **P4 (VLM Pretraining Preservation)** 의 핵심 가설을 거의 직접적으로 검증합니다. 또한 P1 의 *expert-수준 구조 분리* 와 D7 (π backbone integration) 의 partition 전략에 부수적 함의를 가집니다.

- **P4 / D19 (VLM fine-tuning range)** — 우리의 v1 은 (a) full VLM freeze + action expert. UAM 은 *frozen 없이도 의미 보존이 가능하다* 는 반증을 제시 — D19 의 deferred 옵션(LoRA, 선택적 unfreeze)에 새로운 후보로 "구조적 두 번째 경로 추가" 가 합류.
- **P4 / D20 (prior-preservation strategy)** — UAM 의 action-side adapter 는 우리의 v1 (action-side adapter = split heads, 백본 untouched) 과 *동일한 방향*이지만, 추가로 *제어 전용 시각 경로*를 더해 prior 부담을 분산. VLA-Adapter([arXiv:2509.09372]) / PriorVLA([arXiv:2605.10925]) 와는 *어떤 면을 분리하는가* 가 다름 — UAM 은 modality/처리 경로 자체를 분리.
- **P4 / D21 (staged training recipe)** — UAM 결과는 Stage 2 (VLM-freeze + action expert) 에서 발생할 일반화 손실에 대한 우회 옵션을 제시. Stage 3/4 의 *대안*으로 Dorsal-style 경로 추가를 검토할 트리거가 될 수 있음.
- **P4 / D23 (action representation × VLM preservation)** — 우리의 v1 인 continuous flow-matching head 와 정합. UAM 은 더 나아가 *시각 표상까지* 별도 expert 에 위임.
- **P1 / D4 (Body↔Hand information sharing)** — UAM 의 attention 시각화는 *MoT + 적절한 보조 손실*만으로 기능 분기가 emergent 하게 일어남을 보여줌. 우리의 FiLM v1 대비 *cross-attention deferred* 옵션의 트리거(§13.C "single-point info bottleneck") 분석에 직접 인용 가능.
- **P1 / D7 (π backbone integration)** — UAM 은 *추가 expert 를 끼우는* 방향. 우리의 (i) slice partition + FT 와는 다른 축이지만, "VLM 동결 없이도 망각 회피" 라는 결과는 우리의 P4-D19 가정과 P1-D7 의 *slice + FT* 가 충돌하지 않음을 간접적으로 지지.
- **§10 경쟁자 함의** — Genesis AI / IMCopilot 류의 VLA-only 성능 주장에 대한 새로운 증거: action-only 학습으로도 (a) 의미 보존, (b) OOD 일반화가 가능. *우리의 System0 필요성 주장*은 UAM 이 다루지 않는 **post-contact 안정화 sub-loop** 영역에서 여전히 유효(UAM 은 ALOHA pick-and-place 류만 평가).

P2 (Structured Input-Modality Binding) / P3 (System0) / P5 (Evaluation) 에는 직접적 함의가 없습니다 — UAM 은 vision-only 입력이고, contact-rich 평가나 손가락 단위 RL 을 다루지 않습니다.

---

## ✨ 핀 논문 대비 델타

P4 의 핀 라인업과 비교했을 때 — π0 ([arXiv:2410.24164]), π0.5 ([arXiv:2504.16054]), VLM2VLA ([arXiv:2509.22195]), RT-2 ([arXiv:2307.15818]), VLA-Adapter ([arXiv:2509.09372]), **PriorVLA ([arXiv:2605.10925])**, MolmoAct2 ([arXiv:2605.02881]) — 모두 *VLM 자체를 어떻게 보호할지* 에 집중합니다(freeze, LoRA, NL-action, action-side adapter, frozen-prior + 적응 expert, 또는 per-layer KV-cache). UAM 의 차별점:

- **PriorVLA 대비** — PriorVLA 는 *frozen Prior Expert + Adaptation Expert* 로 prior 자체를 동결. UAM 은 frozen 없이 (gradient stop 없음, parameter freeze 없음) *제어용 시각 경로를 별도로 만드는* 정반대 전략. PriorVLA 는 *보존*, UAM 은 *우회*.
- **VLA-Adapter 대비** — VLA-Adapter 의 Bridge Attention 은 action-side 의 token-level 연결. UAM 의 분리는 *modality 입력 분배* 수준 — ViT vs VAE 토큰이 다른 expert 로 라우팅됨.
- **MolmoAct2 대비** — MolmoAct2 의 per-layer KV-cache 는 동일 인코더 내부의 정보 격리. UAM 은 *별도 인코더*로 격리.
- **π0.5 / RT-2 대비** — co-training 으로 망각을 *대증 치료*하는 노선과 다른, *구조적 예방* 노선.

핵심 새로움은 두 가지로 정리됩니다 — (a) "embodiment tax" 의 *측정 가능한 정량화*(Tab. 2/3), (b) frozen·co-training·gradient stop 셋을 모두 거부한 채 95%+ 보존을 달성하는 *건설적* 증명. 이는 P4 의 기존 핀 어느 것도 동시에 보이지 못한 결과입니다.

---

## ⚙️ 의사결정 함의

이 논문이 (우리 셋업으로) 옳다면 다음이 바뀝니다.

- **D19 (VLM FT range)** — v1 의 (a) full freeze 가 *유일한 안전 옵션* 이 아니게 됨. 새로운 후보로 **(f) "frozen 없는 dual-pathway + 보조 dynamics loss"** 가 등재 가능. 단, 우리는 visuotactile / multi-camera fuser(P2) 가 들어오므로 입력 modality 구성이 UAM 과 달라 단순 이식은 곤란.
- **D20 (prior-preservation strategy)** — Bridge Attention/PriorVLA/LoRA-minimal 외에 *parallel visual pathway with self-supervised dynamics objective* 라는 카테고리 추가.
- **D21 (staged training recipe)** — Stage 3/4 트리거 조건의 정의가 바뀜. 현재 트리거는 "Stage 2 in-distribution plateau with generalization loss" — UAM 결과는 generalization loss 발생 *전*에도 dual-pathway 도입을 고려할 근거를 제공.
- **Config / 손실 수준 구체 변경 후보** —
  - `dorsal_expert.enabled=True`, `dorsal_expert.init=bagel|umm_pretrained` 같은 키 신설.
  - `loss.visual_dynamics.lambda` (UAM 의 $`\lambda\mathcal{L}_{\text{wm}}`$) 가 신규 하이퍼.
  - MoT routing rule: ViT 토큰 → semantic expert, VAE 토큰 → dorsal expert (우리의 P2 multi-camera fuser 는 이 매핑에서 어디로 라우팅할지 결정 필요).
  - 평가 지표 측에서는 **forgetting metric $`\Delta`$ 의 추가** — 우리 evaluation protocol(D26)에 MMBench/MMMU 1종 + 행동 성공률 동시 측정 row 를 더하는 것이 가장 싼 도입.
- **P1 함의** — UAM 의 emergent 기능 분기는 *FiLM 단일 지점*(우리의 D4 v1)의 *deferred trigger* "single-point info bottleneck (cf. MolmoAct2 per-layer KV)" 에 새로운 비교군 — *cross-attention 대신 expert-level parallel pathway* 를 deferred 옵션으로 추가하는 안.
- **무엇은 바뀌지 *않는가*** — P3 (System0) 의 필요성. UAM 은 손가락 단위 slip / 접촉 유지를 다루지 않고 ALOHA pick-and-place 류만 평가하므로, 우리의 System0 ablation 동기는 그대로 유지.

---

## ⚠️ 먼저 검증할 실패 모드

- **Bagel-grade UMM 의존성** — UAM 의 generative prior 는 *이해+생성 결합* 사전학습에서 옴. 우리가 $`\pi`$ 백본 + 별도 Dorsal 을 도입할 때, $`\pi`$ 와 Bagel 의 표상 alignment 비용이 크면 학습이 발산할 수 있음. **싼 sanity check**: 우리의 Stage 2 weight 위에 *visual-dynamics aux loss only* (Dorsal expert 미도입) 를 켜고, action 학습 30k step 동안 MMBench 1종 점수가 ≥95% 유지되는지부터 측정. 망각이 *손실 구성* 만으로 완화된다면 expert 추가 비용 없이 일부 이득 회수 가능.
- **Contact-rich 손가락 작업에서의 부적합** — UAM 의 visual-dynamics 손실은 *장면이 어떻게 변하는가* 를 학습. 손바닥 안 회전처럼 *겉보기 시각 변화가 미약한* 작업에서는 이 신호가 거의 사라질 수 있어 Dorsal 경로가 활성화되지 않을 위험. **싼 sanity check**: CALVIN/RoboTwin 류가 아닌 in-hand cube rotation(우리의 CP1) sim 에서 $`\mathcal{L}_{\text{wm}}`$ 의 magnitude 가 학습 후반에도 의미 있게 유지되는지 측정.
- **추론 latency** — 추가 7B expert 가 +15% latency. 우리의 control loop 가 시스템1 50–100 ms 영역이라면 이미 한계에 가깝다. **싼 sanity check**: 우리의 표준 action chunk size + 우리 GPU 에서 Bagel 사이즈 expert 추가 시 step latency 가 우리의 closed-loop 예산을 초과하는지부터 측정 — 초과하면 *축소된 generative expert*(예: 1–2B) 로 ablation 필요.
- **Tactile 입력과의 충돌** — UAM 은 vision-only. 우리의 P2 (tactile per-finger token) 를 어느 expert 로 라우팅할지 미정. **싼 sanity check**: tactile 토큰을 Dorsal 로 보내는 변형 vs $`E_{\text{act}}`$ 로 보내는 변형의 차이를 in-hand rotation sim 에서 한 차례 ablation — Dorsal 의 What/How 가설이 visuotactile 셋업에서도 유효한지 확인.
- **VLM-init Dorsal 의 실패 재현** — UAM 의 §4.2 는 "VLM 가중치를 그대로 복제한 Dorsal" 이 OOD 에서 *baseline 보다 나쁘다* 고 보고. 우리가 D19/D20 변형에서 비슷한 패턴을 보이는지 — 즉 *단순한 경로 추가* 가 오히려 해가 되는 영역인지 — 를 우리 데이터 분포에서도 먼저 확인할 필요.

---

## 💡 컨텍스트 제안

- **§8.4 P4 Tracked Literature 핀 교체 후보** — 현재 P4 핀 8개 중 가장 *대증적 co-training* 측면을 대표하는 항목(예: RT-2)을 UAM 으로 교체하는 안. UAM 은 (i) embodiment tax 의 정량 정의를 도입, (ii) frozen·co-training 두 갈래를 모두 거부한 첫 사례라는 점에서 P4 의 *구조적* 노선을 대표할 자격이 있음. 단 교체 결정은 maintainer 가 §8 의 "분기 quarterly rebalance" 사이클에서 검토.
- **§13 Open Items 신규 항목 후보** — "VLM/제어 경로 분리를 구조적으로 강제할 때 우리의 tactile/proprio 토큰을 어느 expert 로 라우팅할 것인가" 가 P2 ↔ P4 의 새로운 교차점으로 등장. D19 deferred trigger 의 §13.C 와 연결.
- **§10 Competitor monitoring 메모** — Tsinghua + ByteDance Seed 조합은 §9.3 의 *대형 lab 코드 릴리즈 watch* 대상에 추가할 가치. Bagel/BagelVLA 라인업이 P4 에 지속적인 영향을 줄 가능성.
- **Decision Log 변경 제안 없음** — D19~D23 어느 것도 *현 시점*에서 v1 을 바꿀 결정적 증거는 아님. UAM 결과는 *deferred trigger* 측에 후보를 더하는 정도가 적절. 정식 변경은 CP1 (4-contribution ablation) 결과를 본 뒤 판단.

context/MASTER.md 는 수정하지 않았습니다 — 위 항목은 maintainer 검토용 제안일 뿐입니다.

> 💡 base 매핑은 `/implement-design analysis/2605.15735/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
