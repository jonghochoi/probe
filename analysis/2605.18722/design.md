# Design — Dexora: Open-source VLA for High-DoF Bimanual Dexterity

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Dexora: Open-source VLA for High-DoF Bimanual Dexterity |
| 링크 | [arXiv:2605.18722](https://arxiv.org/abs/2605.18722) |
| 분석 문서 | [`analysis/2605.18722/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-29 |

---

## 🧮 데이터 계약

시간 축은 행동 청크 길이 $`L=32`$, 임베디먼트는 36-DoF(팔 6×2 + 손 12×2) 양팔·양손.

- **입력 — 관측 $`\mathbf{o}_{t}`$** : 다중 뷰 RGB(4 views) → SigLip 인코더로 조건 토큰화.
  shape `(B, N_view=4, 3, H, W)`, dtype float. (원문에 해상도·정규화 수치 명시 없음 — 가정으로 메움)
- **입력 — 언어 $`\ell`$** : 자연어 지시 → T5 인코더로 조건 토큰화.
- **입력 — 자기수용 상태 $`s_{t}`$** : 관절각 상태 벡터, shape `(B, D=36)`, dtype float.
  품질 계산 전 **차원별 min–max 정규화** 적용(§III-C). 정책 입력 시 잠재 공간 투영.
- **입력 — 노이즈 행동 $`\widetilde{\mathbf{a}}_{t:t+L-1}`$** : shape `(B, L=32, 36)`,
  디퓨전 타임스텝 $`t`$ 와 결합되어 토큰화.
- **출력 — 예측 행동 $`\widehat{\mathbf{a}}_{t:t+L-1}`$** : shape `(B, L=32, 36)`,
  36-D 관절 명령 청크. 학습 시 DDPM, 추론 시 DPMSolver++ 샘플링.
- **판별기 입력(클립 토큰)** : $`\xi_{t}=\big(s_{t},\ \mathbf{o}_{t},\ \ell,\ \mathbf{a}_{t:t+L-1},\ \widehat{\log\pi}_{t}\big)`$.
  토큰 시퀀스 `[ s_t ; a_{t:t+L-1} ; logπ_t ]` + 학습된 위치 임베딩, 언어/이미지는 조건 스트림.
- **판별기 출력** : 클립 점수 $`d(C_{k})\in(0,1]`$ (sigmoid), 에피소드 가중치 $`w_{i}`$ 로 변환.

---

## 🧰 모듈 인터페이스

```python
def quality_criteria(episode_states, dt) -> dict:
    """에피소드 상태열에서 min-max 정규화 후 중심 유한차분으로
    A_ep, J_ep(RMS 가속도·저크)를 계산. 하위 20% 교집합으로 사전선별."""

def replay_validate(episode) -> bool:
    """오픈루프 리플레이: 충돌 없이 작업 완료 시 양성(positive)."""

def logpi_proxy(pi_theta, clip) -> float:
    """동결 디퓨전 정책의 음의 디노이징 잔차 에너지 E_t를 z-score 정규화해
    log-π 대리 지표 logπ_t 산출 (식 4–5)."""

def discriminator(clip_tokens, cond_lang, cond_img) -> float:
    """얕은 트랜스포머 + 전역 평균 + MLP+sigmoid → 클립 점수 d(C_k)∈(0,1]."""

def dwbc_weight(d_score) -> float:
    """DWBC 매핑으로 보정 점수를 클립 가중치 w_i로 변환 (출처 [30])."""

def policy(s_t, o_t, ell) -> action_chunk:
    """디코더 전용 디퓨전 트랜스포머. T5/SigLip 조건 토큰을 블록에 교대 주입,
    행동 노이즈 예측 → 행동 청크 a_{t:t+L-1} (식 6)."""
```

- **품질 파이프라인** — `quality_criteria` → `replay_validate` 로 $`\mathcal{S}_{\text{high}}`$
  구성 → `logpi_proxy` 로 클립 점수 입력 보강 → `discriminator` 학습 → `dwbc_weight`.
- **정책 학습** — 시뮬 사전학습 후, `dwbc_weight` 산출물로 가중 디퓨전 손실 후학습.
- **추론** — 정책($`\pi_{\theta}`$)만 사용, 판별기는 학습 시에만 사용(§III-C Fig.5c).

---

## ⛓️ 불변식·가정

- (가정 1) 자기수용 상태는 차원별 수치 범위가 이질적이므로 품질 계산 전 **차원별
  min–max 정규화**가 선행되어야 한다(식 1–3의 전제).
- (가정 2) 품질 채점은 **에피소드 단위**여야 한다 — 청크 단위는 정지 구간이 낮은
  가속도/저크로 거짓 양성을 만든다(이동 커버리지 가드 동반).
- (가정 3) 사전학습 정책의 디노이징 잔차가 작을수록(=$`E_{t}`$ 낮음) 해당 클립을
  정책이 잘 설명한다 → $`\widehat{\log\pi}_{t}`$ 가 정책 적합성의 단조 대리 지표.
- (가정 4) 고-DoF(36-D) 행동 공간은 저-DoF 임베디먼트를 부분공간으로 포함 →
  고→저 사영은 차원 축소(잘 정의됨), 저→고 리프팅은 합성(ill-posed).
- (가정 5) PU 목적함수에서 미분류 풀 $`\mathcal{U}`$ 를 음성처럼 다뤄도 무방할 만큼
  $`\mathcal{S}_{\text{high}}`$ 가 충분히 순도 높은 양성집합이다(≈15%).

---

## 📊 하이퍼파라미터·손실

- 품질 RMS (식 2–3):
  $$A_{\text{ep}}(\tau)=\sqrt{\frac{1}{(T-6)D}\sum_{t=4}^{T-3}\sum_{k=1}^{D}a_{t,k}^{2}},\quad J_{\text{ep}}(\tau)=\sqrt{\frac{1}{(T-6)D}\sum_{t=4}^{T-3}\sum_{k=1}^{D}j_{t,k}^{2}}$$
- log-π 대리 (식 4–5):
  $$E_{t}=\frac{1}{|\mathcal{S}|\,L}\sum_{s\in\mathcal{S}}\sum_{\tau=t}^{t+L-1}\left\|\varepsilon_{\theta}\!\left(\mathbf{o}_{\tau},\,\ell,\,\mathbf{a}_{\tau:\tau+L-1},\,s_{\tau}\right)-\varepsilon\right\|_{2}^{2},\quad \widehat{\log\pi}_{t}=-\,\mathrm{zscore}(E_{t})$$
- 판별기 PU 손실 (식 7):
  $$\mathcal{L}_{D}=\eta\,\mathbb{E}_{\tau\in\mathcal{S}_{\mathrm{high}}}\!\big[-\log d(\tau)\big]+\mathbb{E}_{\tau\in\mathcal{U}}\!\big[-\log(1-d(\tau))\big]$$
- 품질 가중 디퓨전 손실 (식 8):
  $$\mathcal{L}_{\pi}=\sum_{i=1}^{L}w_{i}\;\big\|\varepsilon_{\theta}(\cdot)-\varepsilon\big\|_{2}^{2}$$

| 이름 | 값 | 출처 |
|------|----|----|
| `D` (상태 차원) | `36` | §III-C |
| 사전선별 컷 | 하위 `20%` (Acc/Jerk 각각) 교집합 ≈ `18%` | §III-C |
| 고품질 비율 $`\mathcal{S}_{\text{high}}`$ | ≈ `15%` | §III-C, D |
| PU 가중 `η` | `0.5` | §III-D, Eq.(7) |
| 점수 클립 범위 | $`d\in[0.1,0.9]`$ | §III-D |
| 행동 청크 `L` | `32` | §IV-A |
| 정책 규모 | 28 layers / hidden 1024 / 16 heads | §IV-A |
| 판별기 규모 | 12 layers / hidden 512 / 8 heads / 30M | §IV-A |
| 정책 사전학습 스텝 | `100K` | §IV-A |
| 판별기 학습 스텝 | `10K` | §IV-A |
| 옵티마이저 / 배치 / GPU | AdamW / 64 / 8× A100 | §IV-A |
| 가중치 warm-up 길이 | (원문 미명시 — "short warm-up") | §III-D |
| DWBC 점수→가중 매핑 함수형 | (원문 미명시; 참조 [30]) | §III-D |
| `K` (클립 수) / `\|S\|` (디퓨전 스텝 수) | (원문 미명시) | §III-C |

---

## 🎯 평가 메트릭

- **지표** — 작업 성공률(%) · **임계값** — 작업당 20 롤아웃 평균 · **비교 baseline** —
  DP / $`\pi_{0}`$ / GR00T N1
- 정규화 관절 가속도(Acc↓) / 저크(Jerk↓)를 지표로, 20 에피소드 평균을 임계값으로
  삼습니다(낮을수록 평활). 비교 baseline은 w/o discriminator (Table III).
- OOD 성공률은 6조건(미지 배경/조명/객체·가림·혼잡·높이)에서 20 롤아웃으로
  측정합니다 (Fig.8).
- 크로스 임베디먼트 전이 성공률은 EC-1 단팔 그리퍼 / EC-2 양팔 그리퍼 /
  EC-3 단팔 단손에서 재며, 비교 baseline은 동일 정책을 100시연 파인튜닝한 것입니다.
- **벤치마크** — 기본 작업 12개(Pick&Place·Assemble/Disassemble·Articulated),
  다지 작업 6개(Use pen·Fetch book·Cut leek·Place plates·Rough dough·Twist cap)

---

## ✨ 변경 의도 (intent)

prior art 대비 핵심 차별점은 **노이즈 텔레오퍼레이션 데이터를 손실 가중으로 다루는
데이터 품질 인지 학습**입니다. 모든 시연을 동등하게 모방하는 표준 디퓨전 정책과 달리,
운동학적 평활도(가속도·저크) + 리플레이 성공으로 고품질 양성집합을 정의합니다. 동결
정책의 디노이징 잔차 에너지를 log-π 대리로 삼아 PU 판별기를 학습합니다. 그런 다음 그
점수를 DWBC 가중치로 변환해 디퓨전 손실에 가중을 겁니다. 동시에 양팔·양손 36-DoF라는 최고
난도 임베디먼트에서 학습해 저-DoF 임베디먼트로 사영하는 "고→저" 전이 전략을 취해
기존 VLA의 "저→고" 리프팅 ill-posed 문제를 회피합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정책 본체는 조건부 디퓨전 트랜스포머(디코더 전용, T5/SigLip 조건)
  로 `diffusion`(Diffusion Policy) family 와 가장 가깝습니다. 단 다중 뷰 + 언어 조건 +
  36-D 행동 청크 + **품질 가중 손실(식 8)**이 추가 변경점입니다. 품질 가중 디퓨전
  손실과 PU 판별기·log-π 대리는 어느 baseline에도 기성으로 없어 신규 모듈로 얹어야
  합니다(plug-in: 손실 가중 텐서 $`w_{i}`$ 주입 지점).

---

## 🚧 미해결 / 잠정

- DWBC 점수→가중 매핑의 구체 함수형이 본문에 없어 참조 [30] 의존(가정으로 메움).
- 가중치 warm-up 길이("short"), 클립 수 $`K`$, 디퓨전 스텝 집합 크기 $`|\mathcal{S}|`$
  가 수치로 명시되지 않음.
- 이미지 해상도·정규화 통계, T5/SigLip 변형(크기)이 본문에 미명시.
- 실세계 데이터 규모가 초록/서론/본문 간 상충(2.92M vs 3.2M frames, 40.5h vs 177.5h)
  — Layer 1 스펙에는 본문(§III-B) 값(40.5h, 2.92M)을 채택하되 배포본 확인 필요.
- log-π 대리는 DDPM 잔차 기반 — 플로우 매칭 정책으로 옮기려면 속도장 잔차로 치환
  필요(본 논문 범위 밖, PROBE 적용 시 과제).
