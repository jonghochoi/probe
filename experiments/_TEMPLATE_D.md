# Design — <one-line English-friendly title>

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/hypothesize` 가 sibling `H###.md` 와
> 함께 자동 생성합니다 — 가설의 알고리즘 명세를 base 좌표계 없이
> 외부화합니다. base 매핑은 `/foundry` 단계에서 이루어집니다.
> 형식·이모지·용어 규칙은 `docs/STYLE_GUIDE.md` §7 / §4 를 정확히
> 따릅니다. 작성 후 본문은 불변 (`/foundry` 와 `/verify` 는 이 파일을
> 수정하지 않습니다). 같은 주제를 다시 다루려면 새 H 번호로 시작합니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 상위 가설 | [`H###.md`](./H###.md) |
| Pillar | `P#` |
| 관련 Decision | `D#`, `D#` |
| 관련 분석 | [`analysis/<id>.md`](../../analysis/<id>.md) (없으면 "없음") |
| 생성일 | YYYY-MM-DD (`TZ=Asia/Seoul`) |

<!-- 추상화가 부족해 채울 수 없는 항목은 "(가설에 명시 없음 — 가정으로
     메움)" 한 줄로 정직하게 비워둡니다. -->

---

## 🧮 데이터 계약

<!-- 입력 / 출력 텐서의 shape · dtype · 정규화 가정. 모달리티별
     (이미지 / 액션 / proprioception / 언어) 한 줄씩. 시간 축은 절대 좌표가
     아닌 의미 단위로 기록합니다. -->

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

---

## ⛓️ 불변식·가정

<!-- 깨지면 가설 자체가 무효가 되는 수학적/통계적 성질. base 와 무관해야
     합니다. -->

- (가정 1) — <한 줄 진술>
- (가정 2) — <한 줄 진술>

---

## 📊 하이퍼파라미터·손실

<!-- 식과 값. 식·기호는 verbatim. 가설에 없는 값은 "(가설 미명시)" 로. -->

- 손실 식: `L = …`
- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `<name>` | `<value>` | `H###.md §🧩` |

---

## 🎯 평가 메트릭

<!-- `H###.md §🔬 Falsifiable Test` 와 정합. (지표 · 임계값 · baseline)
     세 요소를 그대로 옮겨 적습니다 — 가설과 design 이 metric 정의에서
     불일치하면 안 됩니다. -->

- **지표** — `<metric>` · **임계값** — `<value/comparison>` · **비교 baseline** — `<name>`

---

## ✨ 변경 의도 (intent)

<!-- 이 가설이 prior art / baseline 대비 무엇이 다른가. 한 단락. -->

---

## 🔌 Foundry 힌트 (선택)

<!-- 알려진 foundry 들에서 어디에 매핑될 가능성이 있는지 — 강제 아님.
     `/foundry` 가 실제 매핑을 수행하므로 여기는 후보 수준의 1–2 줄만.
     base 후보가 분명하지 않으면 "없음". -->

- **`lerobot`** — 후보 base: `pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion` 중 어느 family 와 가까운지 한 줄.

---

## 🚧 미해결 / 잠정

<!-- 가설에 명시되지 않아 가정으로 메운 항목, 가설 본문이 모호해 Layer 1
     스펙으로 굳히지 못한 항목. 없음이면 "없음". -->

- (예) loss 의 가중치 `λ` 가 가설에 명시되지 않아 1.0 으로 가정
