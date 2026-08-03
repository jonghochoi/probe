# Paper Analysis — RCT: A Robot-Collected Touch–Vision–Language Dataset for Tactile Generalization

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RCT: A Robot-Collected Touch–Vision–Language Dataset for Tactile Generalization |
| 저자 | Jingbo He, Michael Färber, Roberto Calandra |
| 링크 | [arXiv:2606.31694](https://arxiv.org/abs/2606.31694) · [Website](https://faerber-lab.github.io/RCT/) |
| 발행일 / 버전 | 2026-06-30 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-01 |
| 관련 Pillar | P0, P2, P3 |
| 태그 | dataset, tactile |

<!-- 본문 확보 retrieval ladder 기록 (verbatim):
  1. curl --fail "https://arxiv.org/abs/2606.31694"   → HTTP 200 (메타/초록 확보)
  2. curl --fail "https://arxiv.org/html/2606.31694"  → HTTP 200 (전문 확보, 203,885 bytes)
  참고. https://faerber-lab.github.io/RCT/ → HTTP 403 (프로젝트 페이지, 봇 차단 — 링크만 기록)
  전문(arXiv HTML) 확보이므로 figure hotlink 4장을 STYLE §5-5 형식으로 삽입.
  모든 수치/인용은 수신한 본문에서 받은 그대로이며 추론·보정·반올림하지 않음. -->

---

## 🧭 한 줄 요약 (TL;DR)

RCT 는 로봇 팔이 122종 산업용 기준 재료를 세 개의 DIGIT 촉각 센서로 눌러 수집한 touch–vision–language 데이터셋으로, 한 번의 press 를 "contact sequence"(연속 프레임)로 보존해 재료·카테고리·센서·접촉 위치·시퀀스 단위의 held-out 평가를 가능하게 하고, 이를 통해 통상적인 frame-random split 이 촉각 표현의 *일반화*를 크게 과대평가함(near-duplicate 프레임 누출)을 정량적으로 폭로합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 로봇이 open-world 물체를 조작하려면 촉각 표현이 *처음 보는 재료*로 일반화되어야 하는데, 기존 touch–vision–language 벤치마크가 이 일반화 능력을 제대로 측정하는지가 검증되지 않았습니다.
- **기존 접근의 한계** — 한 번의 press 로 얻은 프레임들은 서로 near-duplicate(연속 프레임이 `0.10 mm` 씩만 차이)라 강하게 상관되는데, frame-random split 은 같은 물리적 상호작용의 프레임을 train 과 test 양쪽에 흩뿌려 넣습니다. 모델은 새 재료로의 전이 대신 near-duplicate 관측을 검색(retrieval)하는 것으로 높은 점수를 낼 수 있습니다.
- **본 논문의 가설** — 데이터를 개별 프레임이 아니라 **contact sequence 를 독립 단위로** 저장·분할하면, 접촉 시퀀스 누출과 재료 누출을 분리해 측정할 수 있고, 그러면 "진짜 일반화"와 "누출로 인한 착시"를 구분할 수 있다는 것입니다.
- **왜 지금 중요한가** — 촉각 표현학습이 10만 단위 triplet 으로 스케일업하는 중이지만, 평가가 누출을 통제하지 않으면 스케일이 곧 일반화라는 잘못된 신호를 줄 수 있어, 지금 평가 프로토콜을 바로잡아야 후속 방법 연구가 올바른 목표를 겨냥합니다.

---

## 🧩 핵심 기여

- **RCT 데이터셋** — full contact sequence, 재료 단위 vision·language 주석, 통제된 held-out 평가용 메타데이터를 갖춘 로봇 수집 touch–vision–language 데이터셋 (`122` 재료 / `7` 카테고리 / `29,279` 프레임 / 3× DIGIT).
- **평가 프로토콜** — 재료·카테고리·센서·접촉 위치·press(시퀀스) 다섯 축의 held-out 평가 설정을 정의하고, frame-random 을 "누출을 허용하는 control" 로만 사용.
- **누출의 정량적 폭로** — frame-random split 이 contact-sequence 중복과 재료 중복을 뒤섞어 촉각 일반화를 과대평가함을 실증하고(합산 `−59.7 pp`), 공개된 TVL/HCT split 도 동일한 구조(test 시퀀스 100% 가 train 에 존재, raw-pixel NN 이 `98.3%` 로 복원)임을 외부 감사로 확인.
- **학습용 샘플링 통찰** — press 를 shallow→deep 로 균일 샘플링(uniform5)하는 것이 모든 프레임을 쓰는 것보다 데이터 1/3 으로 대조학습 성능을 끌어올림을 발견.

---

## 🔑 기술 키워드

- **Contact sequence** — 한 재료를 한 센서로 한 접촉 위치에서 한 번 누르는 동안 기록된 순서 있는 촉각 프레임들. RCT 평가·학습의 최소 독립 단위이며, "프레임이 아니라 press 가 독립 표본"이라는 이 논문의 핵심 주장이 여기서 나옵니다.
- **Held-out-material evaluation** — 학습에서 K 종 재료의 *모든* 접촉을 제거한 뒤 그 재료로 평가하는 배포-현실적 설정 — "로봇이 처음 만지는 재료를 인식할 수 있는가"를 직접 묻습니다.
- **Frame-random split** — 재료·시퀀스 중복을 허용한 채 개별 프레임을 무작위 분할하는 통상적 split. 이 논문은 이를 일반화 지표가 아니라 누출 상한(inflation) 측정용 control 로만 씁니다.
- **Contact-sequence overlap (leakage)** — 같은 press 의 near-duplicate 프레임이 train/test 에 함께 들어가 점수를 부풀리는 누출. vision 벤치마크의 near-duplicate 누출과 같은 계열입니다.
- **TVL recipe (InfoNCE alignment)** — tactile·vision·text 를 InfoNCE 로 정렬하는 TVL 의 대조학습 레시피. 이 논문은 이 레시피를 *바꾸지 않고 그대로* 쓰고 평가에만 집중합니다(방법 기여 없음의 근거).
- **DIGIT sensor** — GelSight 계열을 소형화한 vision-based 촉각 센서. RCT 는 세 개의 DIGIT 인스턴스를 회전 어댑터로 번갈아 접촉시켜 sensor-instance 전이도 평가합니다.
- **Material-level multi-positive criterion** — 한 재료당 스튜디오 사진 1장만 있어(1:다 관계) sample-level diagonal retrieval 이 부적절하므로, 같은 재료 이미지에 연결된 모든 촉각 표본을 valid positive 로 취급하는 tactile→vision 채점 규칙.
- **Separability margin** — $`m=d_{\mathrm{inter}}-d_{\mathrm{intra}}`$, 같은 재료 프레임 간 평균 거리와 다른 재료로의 평균 거리 차이. 임베딩 공간이 재료를 얼마나 잘 분리하는지의 higher-is-better 지표.
- **Uniform5 sampling** — 한 press 에서 shallow→deep 로 균일 간격 5프레임만 뽑는 학습·평가 샘플링. near-duplicate 를 줄여 대조학습을 개선하는 실용적 처방.

---

## 🔬 방법론

> 참고. 이 논문은 새 model/architecture/손실을 제안하지 않는 **데이터셋 + 평가 프로토콜** 논문입니다. 따라서 본 절은 "알고리즘"이 아니라 **데이터셋 구성·평가 프로토콜·(재사용한) 학습 셋업**을 디테일 보존 위주로 정리합니다. 학습 레시피 자체는 TVL 을 그대로 차용했습니다.

### 직관

핵심 통찰은 단순하지만 강력합니다. 로봇이 재료를 한 번 누르면(press) 센서가 점점 파고들면서 수십 장의 촉각 프레임이 연속으로 찍히는데, 이웃한 프레임끼리는 `0.10 mm` 깊이 차이밖에 안 나서 사실상 같은 사진의 near-duplicate 입니다. 그런데 흔한 평가 방식은 이 프레임들을 개별 표본처럼 무작위로 train/test 에 나눠 담습니다. 그러면 모델은 "새 재료를 이해"할 필요 없이, test 프레임과 거의 똑같은 train 프레임을 기억해내기만 하면 높은 검색 점수를 받습니다 — 일반화가 아니라 암기입니다.

RCT 의 설계 결정은 데이터를 개별 프레임이 아니라 **contact sequence**(한 재료·한 센서·한 접촉 위치에서의 한 번의 press) 단위로 저장하고, 분할도 이 단위(또는 재료·카테고리·센서·위치 단위)로 하는 것입니다. 그러면 "시퀀스 누출을 없앤 경우"와 "재료까지 처음 보는 경우"를 따로 측정할 수 있고, 통상적 frame-random 점수가 얼마나 부풀려졌는지가 드러납니다.

수집은 로봇 팔에 세 개의 DIGIT 센서를 단 회전 어댑터로 122종 산업용 기준 재료(Musterkiste 샘플 세트)를 여러 위치에서 눌러 이뤄집니다. 각 재료는 스튜디오 사진 1장과 사람이 촉각으로 고른 서술어(descriptor) 주석으로 라벨링되며, 학습은 TVL 의 대조학습 레시피를 *그대로* 씁니다. 즉 이 논문의 기여는 "무엇을 학습하는가"가 아니라 "무엇으로·어떻게 평가하는가"에 있습니다.

![Figure 1 — RCT 개요: contact sequence 를 보존하는 최초의 데이터셋](https://arxiv.org/html/2606.31694/corl_2026_template_submission/figure1_tmp.png)

> "Figure 1: The RCT dataset is the first dataset of its kind which preserves full contact sequences and enables held-out evaluation across materials, categories, sensors, contact positions, and robot presses." (§1)
> (한글 해설 — 데이터셋을 contact sequence 단위로 보존해 다섯 축의 held-out 평가를 가능케 한다는 이 논문의 뼈대를 한 장으로 보여줍니다.)

### 데이터셋 구성 (아키텍처 대응)

**수집 프로토콜.** 로봇 팔이 회전 어댑터로 세 DIGIT 센서를 번갈아 접촉 자세로 가져와 같은 재료를 세 센서 모두로 동일 프로토콜에서 기록합니다. 각 press 는 초기 접촉부터 깊은 압입까지 고정 스텝으로 샘플링됩니다.

> "Each press is sampled from initial contact to deeper indentation at fixed $`0.10\text{\,}\mathrm{mm}`$ steps, typically yielding $`15`$–$`17`$ tactile frames per contact sequence; contact force is recorded for each frame." (§3)
> (한글 해설 — 프레임 간 깊이 차가 `0.10 mm` 로 매우 작다는 이 수치가 near-duplicate 누출의 물리적 근거이며, 프레임마다 접촉 힘(force)도 함께 저장돼 별도 신호로 쓸 수 있습니다.)

**재료와 규모.** `122` 종 산업 기준 재료가 `7` 개 top-level 카테고리로 나뉩니다 — Plastic/Rubber (`33`), Paper/Cardboard (`45`), Metal (`20`), Textiles/Leather (`10`), Wood/Bamboo/Cork (`7`), Crafts (`4`), Small Items (`3`). 총 `29,279` 프레임이며 각 프레임은 재료·접촉 위치·센서·시퀀스·압입 깊이로 인덱싱됩니다. 접촉 위치는 heavy-tailed 분포(위치 1–4 는 각 `~5,800` 프레임으로 조밀, 위치 6–18 은 `~50` 프레임까지 희박)라, held-out-position 은 완전한 공간 일반화 벤치마크가 아니라 진단(diagnostic)으로 다룹니다.

**Vision·Language 모달리티.** 각 재료는 고해상도 스튜디오 사진(`2048×1536`) 1장과 재료 단위 지각 서술어로 페어링됩니다. 이미지·서술어는 *재료*를, 촉각 프레임은 *접촉 상태의 변화*를 담아 재료 정체성과 접촉 상태를 분리합니다. 한 재료당 이미지 1장(1:다)이므로 sample-level tactile→vision retrieval 은 부적절하고, 대신 material-level multi-positive 기준을 씁니다. 언어 주석은 두 명의 사람 annotator 가 독립적으로 모든 `122` 재료를 만져 고정 어휘(54 개 촉각 서술어)에서 선택하며, VLM(Gemma-3-27B) 소스도 추가합니다. 사람 간 일치는 중간 수준(Jaccard `0.294`), VLM–사람 일치는 더 낮습니다(`0.110`/`0.108`).

![Figure 2 — 한 press 의 contact sequence: 깊이에 따라 DIGIT 프레임과 힘이 함께 진화](https://arxiv.org/html/2606.31694/fig_trajectory.png)

> "Figure 2: Example of contact sequence from one robot press. DIGIT frames evolve gradually with indentation depth, while force increases over the same press. Adjacent frames are correlated observations of one physical interaction, motivating contact-sequence-aware evaluation." (§3)
> (한글 해설 — 인접 프레임이 하나의 물리적 상호작용의 상관된 관측임을 시각화해, 왜 시퀀스를 독립 단위로 삼아야 하는지를 뒷받침합니다.)

### 평가 프로토콜 (학습 목표 대응)

평가의 중심 단위는 contact sequence 이며, 다섯 개의 held-out 설정을 지원합니다(Table 2). K=20 held-out-material 이 주 설정(primary)입니다.

> "Unless stated otherwise, we use held-out-material evaluation with $`K=20`$ materials as the primary setting, since it matches the deployment question: can a robot recognize material properties for materials unseen during training?" (§4)
> (한글 해설 — 배포 현실("처음 보는 재료를 인식할 수 있는가")과 직접 정렬되는 설정을 기본값으로 삼아, frame-random 은 오직 누출 크기를 재는 control 로 격하합니다.)

프레임 밀도는 세 가지로 변주합니다 — `full`(모든 깊이, `~16` 프레임), `uniform5`(shallow→deep 균일 5프레임), `deep5`(가장 깊은 5프레임). tactile→vision 은 material-level multi-positive 로, tactile→text 는 TVL 의 soft-label 기준(text–text cosine 유사도 임계 `0.6356`)으로 채점하고, 지표는 Recall@1 / Recall@5 입니다.

재료 분리 구조는 separability margin 으로 측정합니다:

$$m=d_{\mathrm{inter}}-d_{\mathrm{intra}}$$

여기서 $`d_{\mathrm{intra}}`$ 는 같은 재료 프레임 간 평균 cosine 거리, $`d_{\mathrm{inter}}`$ 는 다른 재료로의 평균 거리입니다(higher-is-better).

### 학습·평가 셋업 (재사용)

이 논문의 방법-비대상 성격을 못 박는 문장은 다음입니다.

> "TVL applies InfoNCE-style alignment across tactile, vision, and text [2]. We use this recipe unchanged and focus on evaluation." (§2)
> (한글 해설 — 학습 레시피는 TVL 을 손대지 않고 그대로 쓰고, 기여는 데이터셋과 평가 프로토콜에 있음을 저자 스스로 명시합니다 — 그래서 Design 비대상입니다.)

학습 구성(Table 10)은 다음과 같습니다.

| Component | Setting |
|---|---|
| Tactile encoder | ViT-Base (`vit_base_patch16_224`) |
| Vision / Text encoder | OpenCLIP ViT-L/14 |
| Loss | InfoNCE across modality pairs |
| Batch size | `256` |
| Epochs / Warmup | `200` / `10` epochs |
| Base learning rate | $`1.5\times 10^{-4}`$ |
| Weight decay | `0.05` |
| Schedule | Cosine |

---

## 📊 실험 설정과 결과

**핵심 표 — 누출 계단(leakage staircase, Figure 3).**

| 조건 | tactile→text R@1 | 의미 |
|---|---|---|
| frame-random control | `80.01%` | 재료·시퀀스 중복 모두 허용 |
| held-out-contact-sequence | `62.33%` | 시퀀스 중복만 제거 (`−17.7 pp`) |
| held-out-material (K=20) | `20.35%` | 재료까지 처음 봄 (`−42.0 pp`) |

> "Recall@1 falls from $`80.01\%`$ to $`62.33\%`$. ... The second drop, from $`62.33\%`$ to $`20.35\%`$, is the material-overlap effect: contacts from materials seen during training are far easier than contacts from materials never seen before." (§5)
> (한글 해설 — 첫 낙폭은 encoder 를 고정한 채 시퀀스 중복만 없앤 순수 누출 효과(`17.7 pp`)이고, 둘째 낙폭은 재료 중복 효과(`42.0 pp`)입니다. 즉 frame-random 점수의 대부분이 일반화가 아닌 중복에서 옵니다.)

![Figure 3 — frame-random 성능의 분해: 시퀀스 누출 −17.7pp, 재료 누출 추가 −42.0pp](https://arxiv.org/html/2606.31694/fig_leakage_staircase.png)

> "Figure 3: Decomposing frame-random performance. Removing contact-sequence overlap costs $`17.7`$ pp; additionally holding out materials costs a further $`42.0`$ pp. Values are for one representative held-out split (seed 42)." (§5)
> (한글 해설 — 두 단계 낙폭을 시각적으로 분리해, "frame-random 점수 = 진짜 일반화"라는 해석이 왜 위험한지를 한눈에 보여줍니다.)

**TVL 재현 (sanity check, Table 3).** 구현이 TVL 을 제대로 재현함을 먼저 확인합니다.

> "Using the published TVL recipe [2] on SSVTP+HCT, our model reaches $`82.21\%`$ tactile$`\rightarrow`$vision Recall@1 on the combined 402-item retrieval pool, close to the $`81.7\%`$ reported in TVL [2]." (§5, Table 3)
> (한글 해설 — 재현치 `82.21%` 가 원 논문 `81.7%` 에 근접해, 이후의 누출 결론이 구현 결함이 아니라 프로토콜 효과임을 담보합니다.)

**TVL/HCT 공개 split 감사 (Table 4).** 외부 데이터에서도 같은 누출 구조가 나타납니다.

> "All $`279`$ HCT test contact sequences also appear in training (Table 4). ... In $`350/356`$ cases ($`98.3\%`$), the same-sequence neighbor is closer, with median cross/same ratio $`2.6\times`$. A training-free raw-pixel nearest-neighbor baseline therefore recovers the correct contact sequence with $`98.3\%`$ top-1 accuracy." (§5, Table 4)
> (한글 해설 — 학습 없는 raw-pixel L2 최근접 이웃만으로도 정답 시퀀스를 `98.3%` 복원 — 공개 split 이 표현학습 없이도 악용 가능함을 보여, 이 문제가 RCT 만의 인공물이 아님을 입증합니다.)

**샘플링 통찰 (Table 5 / Table 13).**

| Training density | Frames | tactile→text R@1 | tactile→vision R@1 |
|---|---|---|---|
| Full (`~16` frames/seq) | `22,576` | `62.44%` | `70.95%` |
| Deep5 | `7,055` | `59.52%` | `65.96%` |
| Uniform5 | `7,055` | **`68.18%`** | **`78.29%`** |

> "Uniform5 improves over full-density training by $`5.7`$ percentage points while using only one third of the frames, and over deep5 by $`8.7`$ points at equal data volume." (§5, Table 5)
> (한글 해설 — press 를 shallow→deep 로 골고루 덮는 것이 near-duplicate 를 조밀하게 쌓는 것보다 대조학습에 유리하며, near-duplicate 가 false negative 로 작용해 목표를 저해한다는 선행 증거와 일치합니다.)

**Held-out-material 은 여전히 어렵다 (Table 6).** RCT-only K=20 tactile→text R@1 은 `20.4%`(3 draw 평균 `25.1 ± 6.1%`), 여기에 SSVTP+HCT 를 더해도 오히려 `13.4%` 로 떨어집니다(importance sampler 가 학습 예산을 RCT 밖으로 옮기기 때문).

**임베딩 구조·downstream probe (Table 7).**

| Metric (K=20) | TVL | RCT | Random | Force |
|---|---|---|---|---|
| Separability margin | `0.048` | **`0.297`** | `0.004` | — |
| Category acc. (%) | `34.2` | **`49.8`** | `37.8` | — |
| Hard/soft acc. (%) | `52.2` | `52.2` | `45.7` | `52.6` |

> "a linear probe on RCT embeddings reaches $`49.8\%`$ on unseen materials, compared with $`34.2\%`$ for TVL and $`37.8\%`$ for a random-initialized encoder. Hard/soft prediction remains below the majority baseline for all learned representations and for force features." (§5, Table 7)
> (한글 해설 — RCT 학습 임베딩은 처음 보는 재료에서 카테고리 인식을 크게 개선하지만, binary hardness 는 모든 표현이 majority baseline 근처에 머물러 — 카테고리 수준 정보는 전이되어도 경도(hardness) 같은 미세 물성은 현 셋업에서 전이되지 않음을 보입니다.)

**Held-out sensor 는 held-out material 만큼 어렵다 (Table 15).** 접촉 위치 hold-out 은 `65.46%`(쉬움, 같은 재료를 다른 위치에서 봄)인 반면, DIGIT 센서 인스턴스 hold-out 은 `21.51%` 로 재료 hold-out(`20.35%`)만큼 어렵습니다.

> "Holding out a DIGIT sensor instance is as hard as holding out materials entirely, even though the materials themselves were seen during training." (§Appendix D, Table 15)
> (한글 해설 — 모델이 센서 인스턴스 간 물리적 공차·보정 차이를 흡수하지 못해 held-out 센서를 미지 재료처럼 취급함 — sensor-instance robustness 가 별개의 병목임을 드러냅니다.)

**시드 견고성 (Table 16).** diverse selection 은 시드 분산이 큼(`25.13 ± 6.14 pp`), category-balanced selection 이 평균을 높이고 분산을 낮춤(`29.79 ± 2.93 pp`) — 저자는 단일 draw 대신 시드 평균·표준편차 보고를 권고합니다.

**VLM 소스 선정 (Table 8/9).** 세 open VLM 중 Gemma-3-27B 가 가장 덜 templated(`101` distinct combos), 가장 lexically rich(`11.15%`), 사람 주석과 가장 근접(`26.36%` semantic sim, 사람 간 `44.43%` 의 `~59%`)이라 VLM 서술어 소스로 채택됩니다.

---

## ⚖️ 한계

- **재료·프레임 규모의 절대량** — `122` 재료·`29,279` 프레임은 통제 평가에는 충분하나 open-world 촉각 탐색에는 작습니다. 임의 곡면·기하·동적 탐색 동작을 다루지 않아, held-out-material 결론이 더 큰 물체 다양성에서도 유지될지는 미검증입니다. (저자 명시 — "designed for controlled evaluation, not exhaustive open-world tactile exploration".)
- **재료 단위 감독(supervision)의 조도(coarseness)** — 재료당 이미지 1장·재료 단위 서술어뿐이라 pose-conditioned per-frame 시각 타깃이나 frame-specific 촉각 캡션이 없습니다. 그래서 strict 1:1 tactile→vision retrieval 이 원천적으로 불가능하고 multi-positive 로 우회해야 하는데, 이는 채점 기준 선택이 결론에 영향을 줄 여지를 남깁니다.
- **경도(hardness) 예측 실패** — binary hard/soft 가 force–depth 요약 특징을 써도 majority baseline 근처입니다. 경도는 카테고리보다 미묘한 물성이고 사람 라벨의 주관 변동이 크며, scalar 요약을 linear probe 에 넣는 방식이 미지 재료의 curve-shape 단서를 담지 못한다는 것 — 즉 더 풍부한 상호작용 신호·표적 라벨·다른 probing 이 필요함을 시사합니다.
- **접촉 위치 분포의 heavy-tail** — 위치 6–18 이 `~50` 프레임까지 희박해, held-out-position 을 공간 일반화의 완전한 벤치마크가 아니라 진단으로만 쓸 수밖에 없습니다. 공간 일반화 결론의 통계적 힘이 제한됩니다.
- **누출 폭로가 "방법"으로 이어지지 않음** — 이 논문은 문제를 정확히 진단하지만(누출·held-out 어려움), held-out-material 을 실제로 끌어올리는 *방법*은 제시하지 않습니다(uniform5 는 샘플링 처방일 뿐). 남는 gap 은 후속 연구의 몫으로, 이 논문 자체는 벤치마크·진단에 머뭅니다.

---

## ♻️ 재현성

- **데이터** — 공개 예정(프로젝트 페이지 [`faerber-lab.github.io/RCT`](https://faerber-lab.github.io/RCT/), 분석 시점 봇 접근 403). 릴리스는 촉각 프레임·재료 이미지·재료 단위 서술어 주석·force 신호·contact-sequence 식별자·재료/카테고리/센서/위치 메타데이터·모든 held-out split 파일을 포함하며, split 생성·평가 스크립트는 supplementary 로 제공 예정.
- **코드** — split-generation toolkit 과 평가 스크립트가 릴리스에 포함(Table 1 "Release: Dataset and split-generation toolkit"). 학습 코드는 TVL 레시피를 그대로 차용하므로 재현 부담이 낮습니다.
- **하드웨어** — 로봇 팔 + 회전 어댑터 + 3× DIGIT(vision-based) 센서 + Musterkiste(Modulor GmbH) 재료 샘플 세트. 재료 세트가 상용 표준품이라 물리 재현 진입장벽이 상대적으로 낮은 편입니다.
- **주의점(정직)** — material-ID 불일치 1건으로 diverse-selection 모델은 `121/122` 재료로 학습됨(학습 커버리지에만 영향, held-out test 셋에는 무영향, 릴리스 메타에 수정 반영). 단일 held-out draw 는 분산이 커 시드 평균 보고가 권장됩니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(데이터/벤치마크 스카우팅 front-end)** — 가장 직접적. RCT 는 `D25`(tactile/force/torque data scouting — 희소한 접촉 모달리티 corpus 를 first-class gap 으로 스카우팅)의 정확한 대상이며(3× DIGIT + per-frame force), 동시에 held-out 평가 프로토콜을 제안하므로 `D26`(benchmark/eval scouting scope)에도 걸칩니다. 접촉 모달리티라 `D24`(priority data axis, egocentric 중심)와는 축이 다릅니다 — RCT 는 egocentric 이 아니라 robot-collected in-lab 이라 priority 축의 보조 슬롯입니다.
- **P2(관측 융합, tactile encoder 지점)** — `D11`(proprio-tactile-force token construction; swappable sensor head + common token format)과 개념적으로 맞닿습니다. RCT 의 "sensor-instance hold-out 이 material hold-out 만큼 어렵다"는 발견은 P2 의 *swappable sensor head* 설계가 왜 필요한지에 대한 강한 실증 논거입니다 — 촉각 encoder 가 센서 인스턴스 물리 공차를 흡수하지 못하면 하드웨어 교체 시 재학습이 강제됩니다.
- **P3(System0 저수준 RL 접촉 안정화)** — `System0` 는 tactile + finger-joint state 만으로 grasp/contact 를 유지하는 vision-excluded RL 모듈입니다. RCT 가 폭로한 "촉각 표현이 미지 재료로 잘 일반화되지 않는다"는 결과는, System0 의 촉각 입력이 학습 시 본 재료에 과적합될 위험을 상기시킵니다(간접 지지).
- **Identity 긴장/지지** — RCT 는 DIGIT(손끝형 vision-based) 기반이고 우리 하드웨어는 Sharpa Deform Map(vision-based, per-fingertip)이라 *modality 계열*은 겹치나 *센서 기종*이 다릅니다. RCT 데이터를 직접 학습에 쓰기보다 **평가 프로토콜 방법론**(contact-sequence 단위 held-out, 누출 감사)을 우리 촉각 encoder 평가에 이식하는 쪽이 Identity 와 정합적입니다.
- **경쟁자 함의** — P2 §5 Tracked Literature 의 촉각 계열(Sparsh tactile foundation model, TVL, ViTacFormer, SaTA, DexViTac) 대비 RCT 는 "새 encoder" 경쟁자가 아니라 이들을 *평가하는 자*입니다. 특히 TVL(우리가 참조하는 InfoNCE alignment 레시피)의 공개 split 을 직접 감사해 점수 해석에 경종을 울립니다.

---

## ✨ 핀 논문 대비 델타

- **P2 §5 핀 — Sparsh (Meta FAIR, tactile foundation model) 대비** — Sparsh 는 대규모 촉각 *표현*(pretraining)을 미는 반면, RCT 는 그 표현이 *처음 보는 재료로 일반화되는지*를 측정하는 통제 데이터셋·프로토콜입니다. 즉 델타는 "더 큰 encoder" 가 아니라 "encoder 를 정직하게 채점하는 자" — Sparsh 류 foundation model 의 보고 점수를 어떻게 해석해야 하는지에 대한 메타 레이어입니다.
- **P0 §5 핀 — RH20T (6-axis wrist F/T, 희소 tactile/torque corpus) 대비** — RH20T 는 wrist F/T + audio 를 담은 대규모 로봇 action corpus 이고, RCT 는 fingertip vision-based 촉각(DIGIT)을 재료 일반화 축으로 조직한 소규모·통제 데이터셋입니다. 델타 — RH20T 는 *task 수행 중의* 접촉 신호(scale), RCT 는 *통제된 material press* 의 접촉 시퀀스(clean held-out). 서로 대체가 아니라 보완입니다.
- **참조 프레임워크 — TVL 대비** — TVL 은 tactile–vision–language InfoNCE alignment 을 도입한 핀급 방법이고, RCT 는 TVL 레시피를 *그대로 차용*하되 그 공개 벤치마크(HCT)의 누출을 감사합니다. 진정한 새로움은 방법이 아니라 **"frame-random 점수 ≠ 촉각 일반화"라는 평가론적 발견**입니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면(그리고 재현성이 높다면) 우리 촉각 표현 평가 파이프라인에서 다음이 바뀝니다.

- **평가 split 을 `contact-sequence`(또는 재료) 단위로 강제** — 촉각 encoder 를 벤치마킹할 때 `split=frame_random` 을 *일반화 지표에서 제외*하고 `split=heldout_material` / `split=heldout_sequence` 를 기본 리포팅으로 채택. 데이터 로더에 `contact_sequence_id`(= 한 press = 재료×센서×위치)를 필수 메타 필드로 추가.
- **near-duplicate 누출 게이트** — 새 촉각 데이터셋(또는 Sharpa Deform Map 자체 수집분)을 학습에 넣기 전, `raw-pixel L2 nearest-neighbor same-sequence recovery` 를 sanity check 로 돌려 `≥ ~90%` 면 누출 경보. RCT 가 TVL/HCT 에서 `98.3%` 를 보인 그 감사를 그대로 이식.
- **학습 샘플링 기본값 = `uniform5`** — press 를 dense 하게 전부 쓰는 대신 shallow→deep 균일 K프레임 샘플링을 촉각 대조학습의 기본 sampler 로. RCT 기준 데이터 1/3 로 `+5.7 pp`.
- **센서 인스턴스 교차 평가 의무화** — P2 의 *swappable sensor head* 검증 지표로 `heldout_sensor R@1` 을 추가. RCT 가 이를 material hold-out 만큼 어렵다고 보였으므로, 센서 교체 robustness 는 별도 리포팅 항목이어야 합니다.
- **채점 기준** — 재료당 이미지 1:다 관계면 `material-level multi-positive` 를, tactile→text 는 text–text cosine soft-label(임계 `0.6356` 는 TVL 값)을 명시적 config 로.

---

## ⚠️ 먼저 검증할 실패 모드

우리 스택으로 전이가 안 될 이유를 싼 체크부터:

1. **(가장 싼 체크) 센서 기종 불일치** — RCT 는 DIGIT, 우리는 Sharpa Deform Map(해상도·응답 특성 상이). RCT 데이터를 직접 학습에 쓰려는 시도는 도메인 갭으로 즉시 실패할 개연성이 큽니다. → *데이터*가 아니라 *평가 프로토콜/감사 스크립트*만 이식하면 이 리스크는 회피됩니다. 먼저 "우리 Sharpa 촉각 데이터에 contact-sequence_id 를 붙일 수 있는가"만 확인.
2. **contact-sequence 정의의 이식성** — RCT 의 "한 press = `0.10 mm` 스텝 15–17 프레임"은 준정적(quasi-static) 압입 프로토콜 전제입니다. 우리 조작은 동적 grasp/재파지라 "press = 시퀀스" 경계가 모호할 수 있어, near-duplicate 누출의 정의 자체가 우리 데이터에서 다르게 나타날 수 있습니다. → 우리 촉각 스트림의 프레임 간 유사도 분포를 먼저 측정해 "누출 단위"가 존재하는지 확인.
3. **material-level supervision 부재** — 우리 파이프라인은 재료 라벨이 아니라 task/goal 라벨 중심이라, RCT 의 material-level multi-positive·재료 held-out 이 그대로 대응되지 않을 수 있습니다. → held-out 축을 "재료"가 아니라 "object/task instance" 로 재정의해야 하는지 판단.
4. **hardness 전이 실패의 우리 함의** — RCT 에서 binary hardness 가 majority baseline 근처라는 결과가, System0(P3) 이 tactile 로 slip/grasp 안정성을 추론하려는 설계에 직접 경고입니다. slip 은 hardness 보다 동적 신호라 다를 수 있으나, "정적 촉각 요약 → 물성 예측"이 약하다는 신호는 System0 입력 설계(정적 요약 vs 시계열) 재검토를 요구합니다. → System0 프로토타입에서 정적 tactile feature 만으로 slip 예측이 majority 를 넘는지 소규모 확인.
5. **재현성 리스크** — 데이터·스크립트가 아직 릴리스 예정(분석 시점 프로젝트 페이지 403)이라, 감사 스크립트를 이식하려면 실제 공개를 기다려야 합니다. 그전까지는 방법론(개념)만 채택하고 수치는 잠정으로 취급.

---

## 💡 컨텍스트 제안

- **P0 §5 Tracked Literature 후보 추가(제안)** — `RCT | arXiv:2606.31694 | 2026 | 🤖 robot + tactile(DIGIT)+force | Contact-sequence held-out 프로토콜 + touch-vision-language 누출 감사 (D25/D26)`. 희소 tactile 접촉 corpus(D25)이자 held-out 평가 프로토콜(D26)이라 P0 의 두 축에 동시 해당합니다.
- **P0 §D26(benchmark/eval scouting scope) — 평가 위생(hygiene) 기준 추가 제안** — "촉각 벤치마크는 contact-sequence 식별자를 노출하고 frame-random 점수와 함께 held-out 결과를 반드시 병기"를 벤치마크 채택 기준(license/usability bar, D27)에 준하는 *평가 위생 체크*로 승격하는 것을 제안합니다.
- **P2 §D11 — swappable sensor head 논거 보강(제안)** — RCT 의 held-out-sensor 결과(sensor-instance robustness 가 별개 병목)를 D11 의 "no Sharpa lock-in / common token format" 비협상 조건의 실증 근거로 §5 nearby-work 에 각주 다는 것을 제안합니다.
- context/ 파일은 수정하지 않았습니다 — 위는 모두 제안입니다.
