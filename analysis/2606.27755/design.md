# Design — Drop-Then-Recovery: How Redundant Are Vision-Language-Action Models?

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Drop-Then-Recovery: How Redundant Are Vision-Language-Action Models? |
| 링크 | [arXiv:2606.27755](https://arxiv.org/abs/2606.27755) |
| 분석 문서 | [`analysis/2606.27755/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-01 |

---

## 🧮 데이터 계약

DTR 은 정책 자체를 새로 정의하지 않고 **기존 VLA 위에서 동작하는 압축·분석 절차**이므로, 데이터 계약은 (a) importance profiling 입력과 (b) recovery 학습 입력 두 갈래입니다.

- **입력(profiling calibration)** — `(o, p, a)` 배치: 관측 `o`(이미지 `(B, N_cam, 3, H, W)` + proprioception `(B, D_state)`), 언어 지시 `p`(토큰 시퀀스), 시연 액션 `a`(= `a^gt`) `(B, T_action, D_action)`. calibration set 은 소규모(원문 π0.5 예시: 64 batch × size 8 = 512 sample).
- **입력(recovery fine-tune)** — downstream task 시연 데이터셋 전체(원문: LIBERO 4-suite mixed / RoboTwin 2.0 mixed 7-task). 정규화·전처리는 base 모델의 기존 recipe 를 그대로 사용(drop 효과만 분리하려는 의도).
- **출력(profiling)** — 블록별 importance 점수 $`\{I_{\text{gate}}(B_i)\}_{i=1}^{N}`$, 내림차순 정렬. 파생물: 유지 블록 인덱스 리스트(예: π0.5 18블록 Drop-9 GateProbe → `[0,1,2,3,4,5,6,8,9]`).
- **출력(dropped model)** — 언어 백본 layer 수가 $`N_L \to N_L - K`$ 로 줄어든 dense VLA. shape/dtype 은 base 와 동일하되 `num_hidden_layers`(언어)만 감소. FLOPs·메모리·latency 비례 감소.
- **정규화 가정** — 액션·관측 정규화 통계는 base 모델 것 재사용(DTR 이 새로 정의하지 않음).

---

## 🧰 모듈 인터페이스

```python
def gateprobe_importance(model, calib_loader, action_loss) -> dict[int, float]:
    """각 transformer 블록의 gate-sensitivity importance 점수 산출.
    forward pre-hook 으로 h_{i-1}, h_i 캡처 + retain_grad, 1 forward+backward.
    반환: {block_id: I_gate}, 내림차순 정렬 가능."""

def select_drop_set(scores, K) -> set[int]:
    """중요도 하위 K개 블록 인덱스 집합 S 반환 (argsort_K).
    유지 집합 = 전체 \ S."""

def drop_blocks(model, drop_set) -> Model:
    """S의 블록을 residual 단락(h_i = h_{i-1})시키고 θ_i 폐기.
    dual-stream(joint-attn) 구조면 K/V projection + input LN 은 유지,
    Q/O projection + MLP 만 제거(≈75%)."""

def recover_finetune(dropped_model, task_data, action_loss, budget) -> Model:
    """θ* = argmin_θ L_action. base 와 동일 최적화 recipe,
    compute-matched 시 budget(bsz·steps)만 drop 비율로 스케일."""
```

- **`gateprobe_importance`** — 역할: recoverability-aware 블록 랭킹. 입력: 모델 + calibration 배치 + task loss. 출력: 블록별 점수. 외부 계약: `L_action` 은 base 의 액션 손실을 그대로 사용(flow-matching / L1 / diffusion 무관), gradient 는 표준 backprop 에서 확보.
- **`select_drop_set` / `drop_blocks`** — 순수 구조 조작. loss·optimizer 와 무관하되, dropped 모델은 이후 `recover_finetune` 의 입력이 됨.
- **`recover_finetune`** — base 학습 루프 재사용. GateProbe·drop 과 분리(정적 절차 후 표준 학습).

---

## ⛓️ 불변식·가정

- **(가정 1) Residual 형태** — 모든 droppable 블록이 $`h_{i}=h_{i-1}+F_{i}(h_{i-1};\theta_{i})`$ 를 만족해야 drop = residual 단락($`h_i=h_{i-1}`$)이 성립. 이 형태가 아니면 DTR 의 "블록 통째 제거"가 정의되지 않음.
- **(가정 2) importance ≠ recoverability** — 제거 직후 큰 열화를 내는 블록이 반드시 회복 불가한 것은 아님. GateProbe 는 1차 Taylor 근사로 *즉각* loss 민감도를 재므로, recoverability 의 proxy 일 뿐 상한 보장은 아님(원문도 gradient 지표가 극단 압축에서 degrade 한다고 명시).
- **(가정 3) Task 분포 종속성** — "redundant" 는 recovery 에 쓰인 task 분포에 대해서만 성립. calibration·recovery 분포가 배포 분포와 어긋나면 잘못된 블록이 제거될 수 있음(원문 Table 10/11: dataset-specific profiling).
- **(가정 4) dual-stream 부분 제거** — joint-attention 구조에서 언어 블록의 K/V·input LN 은 cross-attention 을 위해 반드시 잔존해야 하며, recovery 중 이들이 cross-attention adapter 로 gradient 를 받는다는 가정 위에서 성능이 회복됨.

---

## 📊 하이퍼파라미터·손실

- GateProbe 점수 식:

$$I_{\text{gate}}(B_{i})=\mathbb{E}_{x\sim\mathcal{D}}\left[\left|\left\langle\frac{\partial\mathcal{L}}{\partial h_{i}},\;F_{i}(h_{i-1})\right\rangle\right|\right],\qquad F_{i}(h_{i-1})=h_{i}-h_{i-1}$$

- Drop 선택 식: $`\mathcal{S}=\mathrm{argsort}_{K}\{I(B_{i})\}_{B_{i}\in\mathcal{B}},\ \mathcal{M}_{\text{drop}}=\mathcal{M}\setminus\mathcal{S}`$
- Recovery 목표: $`\theta^{*}=\arg\min_{\theta}\mathcal{L}_{\text{action}}(\pi_{\theta}(a\mid o,p),a^{\text{gt}})`$

| 이름 | 값 | 출처 |
|------|----|----|
| `K` (drop 수, π0.5 18블록) | Drop-9 / 12 / 16 / 17 실험 | §4.4, §6.1 Table 4 |
| 언어 백본 layer 수 | 18(π0.5) / 32(OpenVLA-OFT) / 36(Lingbot) / 26(GigaBrain-0) | §Appendix A |
| calibration set | 64 batch × size 8 = 512 sample | §Appendix E, D |
| GateProbe 비용 | 1 forward + 1 backward (~24.9 s, H200) | §Appendix E Table 8 |
| recovery optimizer | AdamW | §Appendix H Table 14 |
| recovery lr (π0.5) | $`5\times10^{-5}`$ (10K warmup, then constant) | §Appendix H Table 14 |
| recovery lr (OpenVLA-OFT) | $`5\times10^{-4}`$ (decay after 30K) | §Appendix H Table 14 |
| recovery bsz / steps (π0.5, LIBERO) | 32 / 30K (baseline); compute-match 시 64 / 스케일 | §Appendix H, §6.1 Table 4 |
| recovery 방식 | π0.5 full FT / OpenVLA-OFT LoRA rank 32 | §Appendix H Table 14 |
| `L_action` | flow-matching(π0.5) / L1 regression(OpenVLA-OFT) / diffusion | §3.1, §Appendix H |
| dual-stream 제거율 | ≈75% (Q+O+MLP; K/V·LN 잔존) | §Appendix B |

---

## 🎯 평가 메트릭

- **지표** — closed-loop task success rate(%) · **비교 baseline** — full model(drop 0) 동일 recovery recipe · **판정** — dropped 모델이 recovery 후 baseline SR 을 매칭·상회하면 제거 용량은 불필요.
- **보조 지표** — Size(%)·FLOPs(%) 압축률, per-action Act. Speedup, Task Speedup(= Act. Speedup / Step Ratio, 실패 step 반영 end-to-end), Memory(GB). Step Ratio 는 총 환경 step(실패 에피소드 300-step horizon 포함) / baseline.
- **robustness 지표** — LIBERO-Plus 섭동 카테고리별 SR(Camera/Robot/Language/Light/Background/Noise/Layout), RoboTwin 2.0 Easy vs Hard 변형 SR.
- **profiling 지표 비교** — GateProbe vs Taylor/IGIA/Fisher/Hessian/CosSim/CosSim(contig.)/PPL/Magnitude 의 drop-level 별 avg SR(§4.4 Table 3).

---

## ✨ 변경 의도 (intent)

기존 layer-dropping 지표(cosine similarity, magnitude, perplexity)는 제거 직후의 *즉각 열화*만 재고 fine-tuning 후 *회복 가능성*을 예측하지 못하며, 대부분 recovery 없이 평가해 VLA 처럼 액션 오차가 long-horizon 에 누적되는 도메인에 부적합했습니다. DTR 은 "drop → recovery fine-tune" 을 controlled intervention 으로 정식화해 redundancy 를 파라미터 수가 아닌 **recovery 후 closed-loop task success** 로 재정의하고, GateProbe 는 각 블록 residual 가지의 가상 게이트 민감도(= downstream gradient 와 residual 기여의 내적)로 recoverability 를 예측하는 one-shot 지표를 제공합니다. 정적/gradient 지표가 무너지는 극단 압축 구간에서 더 나은 블록 집합을 고른다는 점이 prior art 대비 핵심 차별점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — DTR/GateProbe 는 policy 클래스가 아니라 그 위에 얹는 절차이므로, `pi0` / `pi05`(dual-stream joint-attention, K/V 잔존 처리 필요) 또는 `smolvla`(경량 VLM 백본) 계열의 transformer 블록 스택에 hook 을 걸어 profiling → drop → 기존 학습 루프로 recovery 하는 형태로 매핑될 여지가 있습니다. base 후보: `pi05`(원문 π0.5 와 가장 근접, joint-attention 특수 처리 재현 가능) 또는 `pi0`. 순수 액션 정책(`act` / `diffusion`)은 언어 백본이 없어 언어-redundancy 실험 대상은 아니나 GateProbe 자체는 임의 블록 스택에 적용 가능.

---

## 🚧 미해결 / 잠정

- GateProbe 의 calibration set 구성(샘플링 전략·크기 민감도)은 배포 분포별로 재-profiling 필요 — 원문은 dataset-specific 결과만 제시(Table 10/11), 최적 calibration 크기 스윕은 없음.
- recovery 수렴에 필요한 최소 데이터·step 량과 drop 규모의 정량 관계(회복 곡선)는 compute-matched 표(Table 4)의 이산점만 있고 연속 곡선은 미제공 — "(원문에 명시 없음)".
- diffusion/flow-matching 액션 헤드에서 $`\partial\mathcal{L}/\partial h_i`$ 를 어느 loss 시점(정규화·timestep sampling)에서 취하는지 세부는 본문에 비명시 — GateProbe 구현 시 base 의 표준 학습 loss 를 그대로 쓴다는 가정으로 메움.
- non-joint-attention 구조에서의 액션 헤드 압축은 hidden dim 축소(OpenVLA-OFT `d_h` 4096→256, Appendix C)로 별도 처리 — 블록 dropping 과 다른 축이라 통합 인터페이스는 미정.
