# Implementation Guide — <one-line English-friendly title>

> PROBE implement-hypothesis 모드 산출물. 한글 단일 문서이며, sibling
> `H###.md` 의 가설을 입력으로 받아 `vendor/lerobot/` baseline 대비
> 변경 지점을 매핑합니다. 형식·이모지·용어 규칙은 `docs/STYLE_GUIDE.md`
> §7 / §4 를 정확히 따릅니다. 재실행 시 이 파일과 `I###.patch` 를
> 덮어씁니다.

---

## 📄 가이드 메타

| 항목 | 내용 |
|------|------|
| 상위 가설 | [`H###.md`](./H###.md) |
| 베이스 모델 | `pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion` |
| Vendor pinned commit | `999e77a…` (`vendor/lerobot/README.md` 와 일치 필수) |
| 패치 파일 | [`./I###.patch`](./I###.patch) — `git apply --check` <통과 / 실패> |
| 가이드 생성일 | YYYY-MM-DD (`TZ=Asia/Seoul`) |

<!-- 베이스 모델을 특정할 수 없다면 이 파일을 생성하지 않습니다
     (sibling `H###.md` 말미에 "구현 가이드 미생성 — 베이스 모델이
     vendor 범위 밖" 한 줄만 추가). 패치 검증이 실패했다면 실패 사유를
     §⚙️ 핵심 변경 (diff) 끝에 verbatim 으로 기록합니다. -->

---

## 🧱 베이스 모델 식별

<!-- vendor/lerobot/policies/<base>/ 중 어느 정책을 베이스로 잡았는지,
     식별 근거는 무엇인지(가설의 §🧩 가설 진술 / §🔬 falsifiable test
     인용, 구조 일치). 1–3 문단. 가설이 베이스를 명시했다면 가설을
     인용하면 충분합니다. 근거가 약하면 "잠정 매칭" 으로 명시. -->

---

## 🪛 변경 지점 매핑

<!-- 가설이 손대는 부분을 vendor 좌표로 나열. 1행 = 1 변경 지점.
     `file:line` 좌표는 vendor pinned commit 기준입니다. 가설이 구체적
     코드 위치까지 짚지 못한 항목은 "위치 잠정" 으로 표기하고 §🚧 미해결
     에도 동일 항목을 적습니다. -->

| # | Vendor 위치 | 변경 종류 | 가설 근거 | 요약 |
|---|-------------|-----------|-----------|------|
| 1 | `vendor/lerobot/policies/<base>/modeling_<base>.py:LNN–LMM` | 수정 / 추가 / 삭제 | §🧩 / §🔬 ① | <한 줄 요약> |
| 2 | `vendor/lerobot/policies/<base>/configuration_<base>.py:LNN` | 필드 추가 | §🧩 | <한 줄 요약> |
| … | | | | |

---

## ⚙️ 핵심 변경 (diff)

전체 unified diff 는 [`./I###.patch`](./I###.patch) 입니다.
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

<!-- 가이드 사용자가 실제로 가설을 시도할 때 부딪힐 수 있는 부분.
     의존성, 데이터셋 포맷, 학습 하이퍼파라미터, 평가 hook, 메모리/연산
     비용. 가설 본문에 명시되지 않은 결정은 (잠정) 으로 표기. -->

- **외부 의존성** — <예: google/paligemma-3b-pt-224 다운로드 필요 / "없음">
- **데이터셋** — <예: LeRobotDataset v2.1 호환, action chunk size = 50>
- **학습 하이퍼파라미터** — <가설이 명시한 값과 lerobot 기본값의 차이>
- **평가 / 추론** — <체크포인트 saving, action chunking, inference 시 num_steps>

---

## 🚧 미해결 / 잠정

<!-- 가설 본문에 명시되지 않아 추정으로 채운 부분, 베이스와 정확히 맞지
     않아 "잠정" 으로 둔 변경 지점, 패치가 적용되지 않은 hunk 등. honesty
     원칙 그대로 — 없음이면 "없음" 으로 명시. -->

- (예) §🧩 의 새 routing 규칙은 함수 시그니처만 추정으로 추가되었으며 hyperparameter 미명시
- (예) `processor_<base>.py` 의 normalization 변경은 베이스 코드와 정확히
  매칭되지 않아 hunk 적용 실패 — §🪛 표 #3 에 잠정 매핑만 기록
