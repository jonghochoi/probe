# Design — <Original English Title>

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/foundry` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | <Original English Title> |
| 링크 | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) |
| 분석 문서 | [`analysis/XXXX.XXXXX.md`](./XXXX.XXXXX.md) |
| 본문 확보 수준 | 전문(arXiv HTML) / 전문(ar5iv) / PDF 텍스트(pdftotext) / 초록 only |
| Design 생성일 | YYYY-MM-DD |

<!-- 본문 확보 수준이 "초록 only" 이면 아래 모든 ## 섹션 본문 첫 줄에
     **(본문 미확보 — 잠정)** 를 명시합니다. 추상화가 부족해 채울 수
     없는 항목은 "(원문에 명시 없음 — 가정으로 메움)" 한 줄로 정직하게
     비워둡니다. -->

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
     `/foundry` 가 실제 매핑을 수행하므로 여기는 후보 수준의 1–2 줄만.
     foundry 별로 한 블록씩. base 후보가 분명하지 않으면 "없음". -->

- **`lerobot`** — 후보 base: `pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion` 중 어느 family 와 가까운지 한 줄.

---

## 🚧 미해결 / 잠정

<!-- 원문에 명시되지 않아 가정으로 메운 항목, 본문이 모호해 Layer 1
     스펙으로 굳히지 못한 항목. 정직하게 — 없음이면 "없음". -->

- (예) 정규화 통계의 출처가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정
