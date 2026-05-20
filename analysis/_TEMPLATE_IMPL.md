# Paper Reproduction Guide — <Original English Title>

> PROBE paper-reproduction 모드 산출물. 한글 단일 문서이며, `analysis/<id>.md`
> 분석 결과를 입력으로 받아 `vendor/lerobot/` 의 vanilla baseline 대비 변경
> 지점을 매핑합니다. 형식·이모지·용어 규칙은 `docs/STYLE_GUIDE.md` §6 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | <Original English Title> |
| 링크 | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) |
| 분석 문서 | [`analysis/XXXX.XXXXX.md`](./XXXX.XXXXX.md) |
| 베이스 모델 | `pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion` |
| Vendor pinned commit | `999e77a…` (`vendor/lerobot/README.md` 와 일치 필수) |
| 본문 확보 수준 | 전문(arXiv HTML) / 전문(ar5iv) / PDF 텍스트(pdftotext) / 초록 only |
| 패치 파일 | [`./XXXX.XXXXX_impl.patch`](./XXXX.XXXXX_impl.patch) — `git apply --check` <통과 / 실패> |
| 가이드 생성일 | YYYY-MM-DD |

<!-- 본문 확보 수준이 "초록 only" 이면 아래 모든 ## 섹션 본문 첫 줄에
     **(본문 미확보 — 잠정)** 를 명시합니다. 패치 검증이 실패했다면
     실패 사유를 §⚙️ 핵심 변경 (diff) 끝에 verbatim 으로 기록합니다.
     베이스 모델을 특정할 수 없다면 이 파일을 생성하지 않습니다 (분석
     문서 말미에 "재현 가이드 미생성 — 베이스 모델이 vendor 범위 밖"
     한 줄만 추가). -->

---

## 🧱 베이스 모델 식별

<!-- vendor/lerobot/policies/<base>/ 중 어느 정책을 베이스로 잡았는지,
     식별 근거는 무엇인지(논문 본문/figure 인용, 저자 명시, 구조 일치).
     1–3 문단. 근거가 약하면 "잠정 매칭" 으로 명시. -->

---

## 🪛 변경 지점 매핑

<!-- 논문이 손대는 부분을 vendor 좌표로 나열. 1행 = 1 변경 지점.
     `file:line` 좌표는 vendor pinned commit 기준이며, 좌표가 흔들리면
     재vendor 시 함께 갱신됩니다(README 의 Refreshing 절차 참조). -->

| # | Vendor 위치 | 변경 종류 | 논문 근거 | 요약 |
|---|-------------|-----------|-----------|------|
| 1 | `vendor/lerobot/policies/<base>/modeling_<base>.py:LNN–LMM` | 수정 / 추가 / 삭제 | §3.2, Eq. (4) | <한 줄 요약> |
| 2 | `vendor/lerobot/policies/<base>/configuration_<base>.py:LNN` | 필드 추가 | §A.1 표 3 | <한 줄 요약> |
| … | | | | |

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./XXXX.XXXXX_impl.patch`](./XXXX.XXXXX_impl.patch) 입니다.
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

<!-- 가이드 사용자가 실제로 reproduction 을 시도할 때 부딪힐 수 있는 부분.
     의존성(huggingface hub 모델 다운로드 포함), 데이터셋 포맷, 학습
     하이퍼파라미터, 평가 hook, 메모리/연산 비용. 모호한 추정은 (잠정). -->

- **외부 의존성** — <예: google/paligemma-3b-pt-224 다운로드 필요>
- **데이터셋** — <예: LeRobotDataset v2.1 호환, action chunk size = 50>
- **학습 하이퍼파라미터** — <논문이 명시한 값과 lerobot 기본값의 차이>
- **평가 / 추론** — <체크포인트 saving, action chunking, inference 시 num_steps>

---

## 🚧 미해결 / 잠정

<!-- 본문에 명시되지 않아 추정으로 채운 부분, 베이스와 정확히 맞지 않아
     "잠정" 으로 둔 변경 지점, 패치가 적용되지 않은 hunk 등. honesty
     원칙 그대로 — 없음이면 "없음" 으로 명시. -->

- (예) §3.3 의 새로운 loss term 은 본문 수식만 제공되어 구현은 잠정
- (예) `processor_<base>.py` 의 normalization 변경은 베이스 코드와 정확히
  매칭되지 않아 hunk 적용 실패 — 가이드 §🪛 표 #3 에 잠정 매핑만 기록
