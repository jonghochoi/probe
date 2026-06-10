# Design — LoRA Learns Less and Forgets Less

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | LoRA Learns Less and Forgets Less |
| 링크 | [arXiv:2405.09673](https://arxiv.org/abs/2405.09673) |
| 분석 문서 | [`analysis/2405.09673/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-28 |

> 주의 — 본 논문은 새 알고리즘 제안이 아니라 LoRA vs full finetuning 의
> 통제된 비교·측정 연구입니다. 따라서 아래 Design 은 (1) LoRA
> 재매개화 자체의 계약과 (2) 학습-망각 측정 프로토콜을 Layer 1 스펙으로
> 추출합니다. 정책(policy) 데이터 계약이 아니라 PEFT 모듈 + 평가
> 프로토콜의 계약임에 유의하십시오.

---

## 🧮 데이터 계약

LoRA 는 텐서 modality 변환이 아니라 가중치 행렬에 대한 재매개화이므로,
"데이터"는 적응 대상 가중치와 측정 입력 두 종류입니다.

- **적응 대상** — `W_pretrained`: shape `(d, k)`, dtype 모델 기본(bf16/fp16), base 가중치는 **동결(no grad)**. Llama 류에서 target = self-attention `{W_q,W_k,W_v,W_o}` + FFN `{W_gate,W_up,W_down}` (전 layer).
- **학습 파라미터** — `A`: shape `(d, r)`, `B`: shape `(r, k)`, dtype 학습 정밀도. 모듈당 `d*r + r*k` 개만 학습(원래 `d*k` 대비).
- **학습 입력(IFT)** — 질문-답변 토큰 시퀀스 (Magicoder-Evol-Instruct-110K: 72.97M 토큰 / MetaMathQA: 약 103M 토큰).
- **학습 입력(CPT)** — 라벨 없는 도메인 토큰 스트림 (StarCoder-Python 20B / OpenWebMath 14.7B→20B 반복).
- **측정 입력(learning)** — HumanEval(164 문제, 문제당 50 생성) · GSM8K(test 1,319 샘플).
- **측정 입력(forgetting)** — HellaSwag · ARC-Challenge · WinoGrande (세 지표 평균).

---

## 🧰 모듈 인터페이스

함수/클래스 시그니처 수준의 경계만 기록합니다. base 좌표(file:line)는
들어오지 않습니다.

```python
def lora_reparametrize(W_pretrained, r, alpha, init="normal_zero"):
    """동결된 W_pretrained 에 저랭크 어댑터 (A, B) 를 부착한다.
    A ~ N(0,1), B = 0 으로 초기화 → 학습 시작 시 Delta = 0.
    forward: y = x @ W_pretrained + (alpha/r) * (x @ A) @ B"""
```

```python
def select_target_modules(model, scope="all"):
    """scope ∈ {"attention", "mlp", "all"}.
    "all" = attention 4행렬 + FFN 3행렬 전부. 논문 권고는 "all"."""
```

```python
def measure_learning_forgetting(checkpoint):
    """learning = HumanEval pass@1 또는 GSM8K accuracy.
    forgetting = mean(HellaSwag, ARC-Challenge, WinoGrande).
    두 값을 (learning, forgetting) Pareto 점으로 반환."""
```

```python
def svd_rank_at_variance(W_finetuned, W_pretrained, var=0.90):
    """Delta = W_finetuned - W_pretrained 의 SVD 에서
    누적 분산 var(=90%) 설명에 필요한 특이값 개수를 반환."""
```

- LoRA forward 는 옵티마이저에 `(A, B)` 파라미터만 노출(backbone grad 차단).
- 측정 모듈은 학습과 분리된 평가 하니스(Code Gen LM Eval Harness / LM Eval Harness)에 의존.

---

## ⛓️ 불변식·가정

- **(가정 1)** — `B_0 = 0` 초기화로 학습 시작 시점 `Delta = 0`, 즉 LoRA finetuned 모델은 base 모델과 정확히 동일하게 출발합니다. (망각 완화의 출발 조건)
- **(가정 2)** — base 가중치 `W_pretrained` 는 학습 내내 동결되어 prior-loss 경로가 어댑터로 한정됩니다. 어댑터 랭크 `r` 이 작을수록 base 분포에서 벗어나기가 구조적으로 어렵습니다.
- **(가정 3)** — finetuning 의 실제 가중치 변화 `Delta` 의 유효 랭크는 일반적으로 `r << d,k` 보다 훨씬 큽니다(어려운 도메인에서 10–100×). 그래서 저랭크 근사로는 어려운 신규 도메인 학습을 다 담지 못합니다.
- **(가정 4)** — 스케일 스칼라는 `gamma_r = alpha/r`. `alpha` 를 `r` 에 비례(`alpha=2r`)시키지 않으면 높은 랭크가 `alpha/r` 로 깎여 이득이 사라집니다.

---

## 📊 하이퍼파라미터·손실

- 재매개화 식: `W_finetuned = W_pretrained + Delta`, `Delta = gamma_r * A * B` (`gamma_r = alpha/r`, `A ∈ R^{d×r}`, `B ∈ R^{r×k}`).
- 학습 목적: 표준 미세조정 손실(다음 토큰 예측 cross-entropy). 본 논문은 새 loss term 을 도입하지 않음.

| 이름 | 값 | 출처 |
|------|----|----|
| `r` (rank) | 16, 64, 256 (권고 256) | §4.1, §4.7 |
| `alpha` | `2r` (= 32 / 128 / 512) | §4.1, §4.7 |
| `gamma_r` | `alpha/r` (= 2) | §2, §4.7 |
| `target_modules` | "all" (attention+MLP, 권고) | §2, §4.7 |
| `learning_rate` (LoRA) | `[1e-5, 5e-4]`, 안정 최고값 (≈ full-FT 의 10배) | §4.7 |
| `A_0` 초기화 | `N(0,1)` | §2 |
| `B_0` 초기화 | `0` | §2 |
| IFT epochs (스윕) | 1, 2, 4, 8, 16 | §4.1 |
| CPT tokens (스윕) | 0.25–20B | §4.1 |
| 비교 정규화 | weight decay `5e-5, 1e-4` / attention dropout `0.05, 0.1` | §4.5 |
| SVD 분산 임계 | 90% | §4.6 |

---

## 🎯 평가 메트릭

- **지표(learning)** — `HumanEval pass@1` (temperature=0.2, top_p=0.95, 0-shot, 50 generations) · **비교 baseline** — full finetuning.
- **지표(learning)** — `GSM8K accuracy` (temperature=0, 5-shot, pass@1, test 1,319) · **비교 baseline** — full finetuning.
- **지표(forgetting)** — `mean(HellaSwag, ARC-Challenge, WinoGrande)` (높을수록 base 능력 보존) · **비교 baseline** — full finetuning · weight decay · attention dropout.
- **지표(다양성)** — 50 생성 중 unique 출력 문자열 수(correct/incorrect 분리), distribution collapse 의 coarse proxy.
- **지표(섭동 랭크)** — `Delta` 의 90% 분산 설명 랭크 · **임계값** — 전형적 LoRA 랭크의 `10-100×`.
- **종합** — (learning, forgetting) Pareto 곡선; LoRA 랭크가 곡선 위 이동 손잡이.

---

## ✨ 변경 의도 (intent)

LoRA 를 "full finetuning 의 저렴한 근사"로 보던 통념을, 이 연구는
학습과 망각 두 축으로 갈라 반증합니다. 파라미터를 적게 학습하면 base
분포에서 덜 벗어나므로(=정규화 효과), LoRA 는 어려운 신규 도메인을
덜 배우는(특히 CPT) 대가로 source 능력을 더 보존합니다. full finetuning
의 가중치 변화도 본질적으로 고랭크라는 점을 SVD 로 보여, 저랭크
근사의 한계를 기제 수준에서 설명합니다. 결국 랭크는 근사 정확도를
정하는 값이 아니라, 학습과 망각의 trade-off 를 조절하는 손잡이입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정책 알고리즘이 아니라 PEFT 기법이므로 직접 대응하는
  policy family 는 없습니다. 적용 지점은 backbone(`pi0` / `pi05` 의
  PaliGemma VLM)에 LoRA 어댑터를 부착하는 fine-tuning 경로로, PROBE 의
  D19(d) LoRA option / D21 Stage 3 에 해당합니다. lerobot 측에 LoRA
  주입 지점이 노출되어 있는지는 `/implement-design` 가 판정합니다(없으면
  🚧 매핑 불가 가능).

---

## 🚧 미해결 / 잠정

- 본 논문은 알고리즘 제안이 아니라 비교 연구라, "데이터 계약 / 모듈
  인터페이스"는 LoRA 재매개화 + 측정 프로토콜로 재구성한 것입니다 —
  정책 입출력 텐서 계약이 아닙니다.
- 모델 규모 일반화(7B 너머)는 원문에서 future work 로 남겨, 다른 규모·
  modality 의 권고 전이는 (원문에 명시 없음 — 가정으로 메움).
- SVD 고랭크 분석은 CPT 에 대해서만 수행 — IFT 의 `Delta` 랭크 특성은
  원문 미명시.
- VLM/멀티모달·로보틱스 적용 시의 권고 값(특히 PaliGemma-2B 에서의
  r·target_modules)은 원문 범위 밖이므로 별도 ablation 으로 확인 필요.
