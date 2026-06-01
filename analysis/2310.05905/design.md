# Design — TAIL: Task-specific Adapters for Imitation Learning with Large Pretrained Models

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TAIL: Task-specific Adapters for Imitation Learning with Large Pretrained Models |
| 링크 | [arXiv:2310.05905](https://arxiv.org/abs/2310.05905) |
| 분석 문서 | [`analysis/2310.05905/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-28 |

---

## 🧮 데이터 계약

멀티모달 Transformer 정책의 입출력 계약입니다. 시간 축은 의미 단위(`T_obs` = 관측 토큰 시퀀스 길이, 단일 스텝 액션 출력)로 기록합니다.

- **입력** — `language_instruction`: 자연어 과제 지시 문자열 → CLIP 텍스트 인코더 토큰 임베딩 `(B, d_text)`
- **입력** — `image_obs`: RGB 관측(다중 시점, 실험에선 2 view) → CLIP 공간 인코더 임베딩 `(B, V, d_img)`
- **입력** — `state_obs`: joint state 등 저차원 상태 벡터 `(B, d_state)`, 정규화 가정은 (원문에 명시 없음 — 가정으로 메움; 데이터셋 통계 기반 표준화로 가정)
- **융합** — FiLM 층이 과제 임베딩으로 관측 토큰을 $`(\gamma,\beta)`$ 변조 → 토큰 시퀀스 `(B, T_obs, d)`
- **출력** — `action`: 단일 스텝 연속 액션 분포 `(B, d_action)`, 6-DOF 팔 + 그리퍼 연속 제어 (dtype float). `d_action` 구체값은 (원문에 명시 없음 — LIBERO 액션 차원에 의존)
- **어댑터 파라미터** — `adapter_weights` $`\mathbf{\omega}_k`$: $`|\mathbf{\omega}_k|\lll|\mathbf{\theta}|`$, base 가중치 $`\mathbf{\theta}`$ 는 동결

---

## 🧰 모듈 인터페이스

함수/클래스 시그니처 수준의 경계만 기록합니다. base 좌표(file:line)는 포함하지 않습니다.

```python
def lora_integrate(W, h_in, W_down, W_up, alpha):
    """병렬 통합 — h_out = W^T h_in + alpha * W_up^T W_down^T h_in (Eq. 2).
    W 동결, W_down∈R^{d×r}, W_up∈R^{r×k}, r≪min(d,k)."""

def bottleneck_integrate(W, h_in, W_down, W_up, phi):
    """순차 통합 — h_out = W_up^T phi(W_down^T (W^T h_in)) (Eq. 3).
    FFN 출력 뒤 직렬 삽입, phi 는 비선형 활성."""

def prefix_integrate(s, p):
    """접두 토큰 통합 — S = [p; s], p∈R^{m×d} 학습 가능 가상 토큰을
    입력 시퀀스 s∈R^{n×d} 앞에 연결."""

def tail_adapt(theta, D_k, integration_style):
    """과제 T_k 에 대해 adapter omega_k 초기화 → base theta 에 통합 →
    BC 손실(Eq. 1)을 omega_k 에 대해서만 최적화(theta 동결).
    반환: 학습된 omega_k (과제별 플러그인)."""

def tail_execute(theta, omega_j):
    """과제 T_j 실행 시 j-번째 어댑터 omega_j 만 활성화해 base 에 로드."""
```

- **통합 모듈** — 세 스타일은 base 가중치 동결 계약을 공유. LoRA는 attention $`W_Q`$/$`W_V`$ 에, Bottleneck은 attention 출력 + 중간 FFN에, Prefix는 입력 시퀀스에 작용.
- **옵티마이저 관계** — AdamW + 선형 LR 스케줄러; 학습 대상은 $`\mathbf{\omega}_k`$ + 융합 모듈 + 정책 헤드만(적응 단계). base 인코더·시간 디코더는 동결.
- **어댑터 초기화** — 이전 어댑터 가중치 + 소량 랜덤 노이즈로 초기화(연속 적응 안정화).

---

## ⛓️ 불변식·가정

- (가정 1) — 사전학습 모델은 IL 과제에 대해 낮은 내재 차원(intrinsic dimension)을 가지므로, 저랭크($`r\ll\min(d,k)`$) 재매개화가 전체 파라미터 공간만큼 효과적이다.
- (가정 2) — base 가중치 $`\mathbf{\theta}`$ 를 동결하고 어댑터 $`\mathbf{\omega}_k`$ 만 학습하면 과제 간 간섭이 없어 BWT(이전 과제 성능 변화) = 0 (망각 없음)이 보장된다.
- (가정 3) — 어댑터 파라미터 수가 base 대비 극소($`|\mathbf{\omega}_k|\lll|\mathbf{\theta}|`$, 실험상 약 1%)여서 소량 데이터에서도 과적합 저항이 강하다(Occam's razor).
- (가정 4) — base 모델 특징 품질이 충분히 높아야 어댑터가 효과를 낸다. 동결 CLIP 인코더가 그 전제이며, niche 도메인에서 인코더를 FFT하면 특징이 오염된다.
- (가정 5, 도입 모달리티 한정) — 적응 대상은 동일 모달리티 집합 안의 새 *과제*이다. 새 센서 모달리티(촉각 등) 추가는 본 가정 밖 — (원문 범위 외, 우리 스택 적용 시 검증 필요).

---

## 📊 하이퍼파라미터·손실

- 손실 식 (BC, Eq. 1):

  $$\hat{\mathbf{\theta}}=\min_{\mathbf{\theta}}\sum_{k=1}^{K}\underset{s_{t},a_{t}\sim\mathcal{D}_{k}}{\mathbb{E}}\left[\sum_{t=0}^{l_{k}}\mathcal{L}\left(\pi(a|s_{\leq t},\mathcal{T}_{k};\mathbf{\theta}),a_{k}^{t}\right)\right]$$

  TAIL에서는 $`\mathbf{\theta}`$ 대신 $`\hat{\mathbf{\theta}}=\{\mathbf{\theta},\mathbf{\omega}\}`$ 의 $`\mathbf{\omega}`$ 에 대해 최적화($`\mathbf{\theta}`$ 동결). $`\mathcal{L}`$ = MSE 또는 음의 로그가능도.

- LoRA (Eq. 2): $`h_{out}={\mathbf{W}}^{\top}h_{in}+\alpha{\mathbf{W}}_{up}^{\top}{\mathbf{W}}_{down}^{\top}h_{in}`$
- Bottleneck (Eq. 3): $`h_{out}={\mathbf{W}}_{up}^{\top}\phi\left({\mathbf{W}}_{down}^{\top}({\mathbf{W}}^{\top}h_{in})\right)`$

- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | LoRA `rank r` | `8` | §B.2 |
  | LoRA `scaling α` | `8` | §B.2 |
  | LoRA 적용 위치 | `W_Q`, `W_V` (attention 투영) | §B.2 |
  | Prefix 토큰 길이 | `30` | §B.2 |
  | Prefix 저랭크 표현 `r` | `16` | §B.2 |
  | Bottleneck size | `32` (attention 출력 + 중간 FFN) | §B.2 |
  | RoboAdapter bottleneck size | `64` (층 0,1,5,6,10,11) | §B.2 |
  | 옵티마이저 | AdamW + 선형 LR 스케줄러 | §B.3 |
  | 학습률 | `1e-4` | §B.3 |
  | 학습 에폭 | 100 (대부분 묶음) / 50 (LIBERO-10) | §5.2, §B.3 |
  | 배치 크기 | TAIL 18 / FFT·ER 14 / EWC 10 | §B.3 |
  | 시드 수 | 3 | §5.2 |
  | 학습 파라미터 비율 (LoRA) | `2.02M / 172.24M ≈ 1.17%` | Table 3 |

---

## 🎯 평가 메트릭

- **지표** — 과제 묶음별 평균 성공률(unseen 초기 상태 10 장면) · **임계값** — 높을수록 좋음 · **비교 baseline** — FFT / ER / EWC / PackNet / FPF
- **지표** — Forward Transfer $`\mathbf{F}_k`$ (새 과제 최대 성공률) · **비교** — TAIL-LoRA 0.70 vs FFT 0.48 (LIBERO-10 평균, Table 1)
- **지표** — Backward Transfer (이전 $`k-1`$ 과제 성공률 변화 평균) · **임계값** — TAIL 계열 = 0 (무망각), 관습 기법은 음수 · **출처** — Table 1
- **지표** — 학습 파라미터 비율 / GPU 메모리 감소 · **임계값** — FFT 대비 약 1% 파라미터 · **출처** — Table 3
- **지표** — 과적합 저항(circle-back 재방문 성능 드롭) · **출처** — Table 2 / §C.1

---

## ✨ 변경 의도 (intent)

선행 연구(FFT, FPF)는 전체 미세조정으로 사전학습 특징을 왜곡(망각·가소성 상실·과적합)하거나, 특징을 통째로 동결해 표현력을 잃습니다. TAIL은 언어 모델 PEFT(LoRA/Bottleneck/Prefix)를 의사결정/모방 학습으로 이식해, base 가중치를 동결한 채 과제별 소수 어댑터(약 1%)만 학습함으로써 "특징 보존 ↔ 새 과제 흡수"를 동시에 달성합니다. 핵심 차별점은 (1) 세 통합 스타일을 *연속학습* 축(망각·가소성·효율)에서 정면 비교해 LoRA의 우위를 확립한 점, (2) 통합 *위치*(어텐션 내부/주변 vs FFN 뒤)에 따라 성능이 갈리는 점을 밝힌 점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — base 후보: `pi0` / `pi05` family에 가장 가깝습니다. TAIL의 "동결 backbone + 소수 학습 어댑터" 패턴은 `pi0`의 frozen-VLM + action-expert 구조에 LoRA(attention $`W_Q`$/$`W_V`$, rank 8) 어댑터를 추가하는 형태로 매핑될 여지가 있습니다. 단, `lerobot`/openpi의 PEFT 진입점(LoRA 삽입 훅) 존재 여부는 `/implement` 단계에서 확인 필요. 평행 그리퍼 IL 골격(CLIP+GPT-2)은 `act`/`diffusion`과도 형식상 유사하나, 보존·연속학습 의도는 `pi0` 계열이 더 부합.

---

## 🚧 미해결 / 잠정

- 액션 차원 `d_action`·상태 정규화 통계가 본문에 구체 명시되지 않아 LIBERO 환경 기본값에 의존하는 것으로 가정.
- $`\phi`$(Bottleneck 비선형 활성)의 구체 종류(ReLU/GELU 등)는 본문에서 식별되지 않음(AdapterHub 기본값 추정).
- 코드 저장소 공개 URL을 본 추출에서 확인하지 못함 — 재현 시 AdapterHub + LIBERO 공개 자산 조합으로 가정.
- 새 모달리티(촉각) 추가 시 rank 8 LoRA의 표현력은 원문 범위 밖 — 우리 스택 적용 전 별도 검증 항목(분석 §⚠️ 참조).
