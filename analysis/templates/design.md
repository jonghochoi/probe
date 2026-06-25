# Design — <Original English Title>

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | <Original English Title> |
| 링크 | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) |
| 분석 문서 | [`analysis/XXXX.XXXXX/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) / 전문(ar5iv) / PDF 텍스트(pdftotext) / 초록 only |
| Design 생성일 | YYYY-MM-DD |

<!-- 본문 확보 수준이 "초록 only" 이면 아래 모든 ## 섹션 본문 첫 줄에
     **(본문 미확보 — 잠정)** 를 명시합니다. 추상화가 부족해 채울 수
     없는 항목은 "(원문에 명시 없음 — 가정으로 메움)" 한 줄로 정직하게
     비워둡니다. -->

<!-- Design 적용 여부 (DESIGN APPLICABILITY gate, docs/STYLE.md §6):
     이 논문이 foundry 로 포팅 가능한 새 model/architecture/학습목표/
     알고리즘을 제안하면 ✅ 적용 — 이 메타 테이블에 `Design 적용` 행을
     넣지 않고(기본 적용) 아래 7개 섹션을 정상 작성합니다.
     순수 데이터셋 / 벤치마크·eval-harness / survey·position·study /
     non-policy tooling 이면 🚫 비대상 — 위 메타 테이블에
       | Design 적용 | 🚫 비대상 (<dataset|benchmark|survey|tooling>) |
     행을 추가하고, 아래 🧮 데이터 계약 … 🚧 미해결 7개 섹션을 전부
     지운 뒤 단 하나의 섹션만 남깁니다:

       ## 🚫 Design 비대상
       <이 논문은 foundry 로 포팅 가능한 Layer 1 알고리즘 기여가 없는
        <사유> 논문이므로 Design 을 생성하지 않습니다. 가치는 카탈로그
        라우팅(<카탈로그 토큰>) 또는 분석 문서로 전달됩니다. (해당 시)
        부수 베이스라인은 핵심 기여가 아니라 매핑 대상에서 제외합니다.>

     analysis.md 의 📄 논문 메타 `Design 적용` 행과 verdict 가 일치해야
     합니다. 분류 규칙은 .claude/prompts/analysis.txt 의 DESIGN
     APPLICABILITY gate 가 SSOT. -->

---

## 🧮 데이터 계약

<!-- 입력 / 출력 텐서의 shape · dtype · 정규화 가정. 모달리티별
     (이미지 / 액션 / proprioception / 언어) 한 줄씩. 시간 축은 절대 좌표가
     아닌 의미 단위 (`chunk_size`, `T_action`) 로 기록합니다. -->

- **입력** — `<modality>`: shape `(B, …)`, dtype, normalization
- **출력** — `<modality>`: shape `(B, …)`, dtype, normalization

---

## 🧰 모듈 인터페이스

<!-- 함수/클래스 시그니처 수준의 경계. 구현은 비워두고, 호출 계약만
     기록합니다. base 좌표 (file:line) 는 여기 들어오지 않습니다. -->

```python
def <module_name>(<args>) -> <return_type>:
    """<한 줄 책임 설명>"""
```

- 모듈별로 역할, 입력, 출력, 외부 호출 계약 (loss/optimizer 와의 관계 등)

---

## ⛓️ 불변식·가정

<!-- 깨지면 알고리즘 자체가 무효가 되는 수학적 성질. 예: "action chunk
     사이 인접 timestep 의 차분은 dataset 의 std 보다 작다" 같은 가정.
     base 와 무관한 수학적/통계적 성질이어야 합니다. -->

- (가정 1) — <한 줄 진술>
- (가정 2) — <한 줄 진술>

---

## 📊 하이퍼파라미터·손실

<!-- 식과 값. 식·기호는 verbatim. 본문에 없는 값은 "(원문 미명시)" 로. -->

- 손실 식: `L = …`
- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `<name>` | `<value>` | §X, Eq. (N) |

---

## 🎯 평가 메트릭

<!-- 채점 방식. 측정 지표명, 임계값, baseline. 가능한 한 verbatim. -->

- **지표** — `<metric>` · **임계값** — `<value/comparison>` · **비교 baseline** — `<name>`

---

## ✨ 변경 의도 (intent)

<!-- 이 알고리즘이 prior art / baseline 대비 무엇이 다른가. 한 단락. -->

---

## 🔌 Foundry 힌트 (선택)

<!-- 알려진 foundry 들에서 어디에 매핑될 가능성이 있는지 — 강제 아님.
     `/implement-design` 가 실제 매핑을 수행하므로 여기는 후보 수준의 1–2 줄만.
     foundry 별로 한 블록씩. base 후보가 분명하지 않으면 "없음". -->

- **`lerobot`** — 후보 base: `pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion` 중 어느 family 와 가까운지 한 줄.

---

## 🚧 미해결 / 잠정

<!-- 원문에 명시되지 않아 가정으로 메운 항목, 본문이 모호해 Layer 1
     스펙으로 굳히지 못한 항목. 정직하게 — 없음이면 "없음". -->

- (예) 정규화 통계의 출처가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정
