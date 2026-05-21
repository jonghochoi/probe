# Implementation Guide — <Original English Title> on `<foundry>`

> PROBE foundry 모드 산출물 (Layer 2, foundry-specific). 한글 단일
> 문서이며, sibling Design (`analysis/<id>_design.md`) 을 입력으로
> 받아 한 foundry 의 좌표계 위에서 변경 지점을 매핑합니다. 형식·이모지
> ·용어 규칙은 `docs/STYLE.md` §6 / §4 를 정확히 따릅니다.
> 재실행 시 이 파일과 sibling `impl.patch` 를 덮어씁니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 | <Original English Title> |
| 링크 | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) |
| 상위 Design | [`../<id>_design.md`](../<id>_design.md) |
| Foundry | `lerobot` (또는 다른 등록된 foundry 이름) |
| Foundry pinned commit | `999e77a…` (lerobot 의 경우 `vendor/lerobot/README.md` 와 일치 필수) |
| 베이스 모델 / 코드 좌표 | `pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion` (lerobot 의 경우), 또는 foundry 별 등가물 |
| 본문 확보 수준 | 전문(arXiv HTML) / 전문(ar5iv) / PDF 텍스트(pdftotext) / 초록 only |
| 패치 파일 | [`./impl.patch`](./impl.patch) — `git apply --check` <통과 / 실패> |
| 가이드 생성일 | YYYY-MM-DD |

<!-- Design 이 이 foundry 의 좌표계로 매핑되지 않는다면 이 파일을
     생성하지 않습니다 — sibling `UNMAPPABLE.md` 와 상위 문서 말미의
     `> 🚧 매핑 불가 (<foundry>) ...` 한 줄로 대체합니다. 패치 검증이
     실패했다면 실패 사유를 §⚙️ 핵심 변경 (diff) 끝에 verbatim 으로
     기록합니다. -->

---

## 🧱 베이스 / 코드 좌표 식별

<!-- 이 foundry 안의 어떤 코드 좌표를 매핑 대상으로 잡았는지, 식별
     근거는 무엇인지 (Design 의 §🧰 모듈 인터페이스 / §✨ 변경 의도
     인용, 구조 일치). 1–3 문단. 근거가 약하면 "잠정 매칭" 으로 명시.

     lerobot 의 경우: `vendor/lerobot/policies/<base>/` 중 어느 정책을
     베이스로 잡았는지. -->

---

## 🪛 변경 지점 매핑

<!-- Design 이 손대는 부분을 foundry 좌표로 나열. 1행 = 1 변경 지점.
     `file:line` 좌표는 foundry pinned 시점 기준이며 (lerobot 의 경우
     `vendor/lerobot/README.md` 의 SHA), 좌표가 흔들리면 foundry refresh
     시 함께 갱신됩니다. -->

| # | Foundry 위치 | 변경 종류 | Design 근거 | 요약 |
|---|--------------|-----------|-------------|------|
| 1 | `vendor/lerobot/policies/<base>/modeling_<base>.py:LNN–LMM` | 수정 / 추가 / 삭제 | Design §🧰, Eq. (N) | <한 줄 요약> |
| 2 | `vendor/lerobot/policies/<base>/configuration_<base>.py:LNN` | 필드 추가 | Design §📊 | <한 줄 요약> |
| … | | | | |

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./impl.patch`](./impl.patch) 입니다.
아래는 가장 핵심적인 hunk 1–3 개의 인라인 발췌입니다 (전문 인용 금지 — 패치 파일이 정본).

```diff
--- a/vendor/lerobot/policies/<base>/modeling_<base>.py
+++ b/vendor/lerobot/policies/<base>/modeling_<base>.py
@@ -LNN,7 +LNN,11 @@
   ... 핵심 hunk 발췌 ...
```

`git apply --check` 결과: <통과 / 실패 — 사유 verbatim>

---

## 🧪 실무 구현 주의

<!-- 가이드 사용자가 실제로 이 foundry 에서 reproduction 을 할 때
     부딪힐 수 있는 부분. 의존성 (huggingface hub 모델 다운로드
     포함), 데이터셋 포맷, 학습 하이퍼파라미터, 평가 hook, 메모리/연산
     비용. 모호한 추정은 (잠정). -->

- **외부 의존성** — <예: google/paligemma-3b-pt-224 다운로드 필요>
- **데이터셋** — <예: LeRobotDataset v2.1 호환, action chunk size = 50>
- **학습 하이퍼파라미터** — <Design 이 명시한 값과 foundry 기본값의 차이>
- **평가 / 추론** — <체크포인트 saving, action chunking, inference 시 num_steps>

---

## 🚧 미해결 / 잠정

<!-- Design 에 명시되지 않아 추정으로 채운 부분, foundry 좌표와 정확히
     맞지 않아 "잠정" 으로 둔 변경 지점, 패치가 적용되지 않은 hunk 등.
     honesty 원칙 그대로 — 없음이면 "없음" 으로 명시. -->

- (예) Design §📊 의 새로운 loss term 은 식만 제공되어 구현은 잠정
- (예) `processor_<base>.py` 의 normalization 변경은 foundry 코드와 정확히
  매칭되지 않아 hunk 적용 실패 — §🪛 표 #3 에 잠정 매핑만 기록
