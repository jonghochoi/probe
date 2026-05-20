# Validation Report — <one-line English-friendly title>

> PROBE validate-hypothesis 모드 산출물. 한글 단일 문서이며, sibling
> `H###.md` · `I###.md` · `I###.patch` 를 문헌(`analysis/<id>.md`) 과
> vendor 코드에 대조한 정적 검증 결과입니다. 코드는 실행하지 않습니다
> (`git apply --check` 만 허용). 형식·이모지·용어 규칙은
> `docs/STYLE_GUIDE.md` §7 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 검증 메타

| 항목 | 내용 |
|------|------|
| 상위 가설 | [`H###.md`](./H###.md) |
| 구현 가이드 | [`I###.md`](./I###.md) · [`I###.patch`](./I###.patch) |
| 검증 생성일 | YYYY-MM-DD (`TZ=Asia/Seoul`) |
| 📚 문헌 대조 | `pass` / `fail` / `partial` |
| 🔍 패치 정합성 | `pass` / `fail` |
| 🧪 시그니처·하이퍼파라미터 | `pass` / `fail` / `partial` |
| ⚖️ 종합 판정 | `manifest.status` 격상 여부 (`draft → validated` / 유지) |

<!-- 4 단계 체크 중 하나라도 fail 이면 status 는 draft 로 유지됩니다.
     모두 pass 인 경우에만 manifest.status 를 validated 로 격상합니다.
     adopted / rejected 는 사람만 전이시킵니다 — 이 보고서는 절대로
     쓰지 않습니다. -->

---

## 📚 문헌 대조

<!-- manifest.related_analyses 에 나열된 각 analysis/<id>.md 에 대해
     일치 / 충돌 / 확장 / 무관 중 어느 관계인지 한 줄씩 판정합니다.
     일치·충돌 의 경우 analysis 문서에서 직접 인용 (verbatim) 한 줄을
     반드시 함께 적습니다. -->

| 분석 | 관계 | 인용 / 사유 |
|------|------|-------------|
| [`analysis/<id>.md`](../../analysis/<id>.md) | 일치 / 충돌 / 확장 / 무관 | <verbatim 인용 또는 갭 설명> |
| … | | |

판정: `pass` / `fail` / `partial`

<!-- 적어도 하나의 일치/확장 → pass. 충돌 한 줄이라도 있으면 fail.
     무관만 있거나 관련 분석이 비어 있고 가설이 paper 를 주장하면
     partial. -->

---

## 🔍 패치 정합성

<!-- `git apply --check` 결과를 verbatim 으로 기록합니다. -->

```text
$ cd /home/user/probe && git apply --check experiments/H###-*/I###.patch
<stdout/stderr verbatim, 빈 출력이면 그 사실을 적습니다>
```

판정: `pass` (zero exit) / `fail — <stderr 첫 줄 verbatim>`

<!-- manifest.implementation.apply_check 와 현재 관측이 다르면 (vendor
     refresh 이후 패치가 깨졌을 수 있음) 🚧 미해결 / 잠정 섹션에
     이 사실을 적고 현재 관측을 manifest 에 반영합니다. -->

---

## 🧪 시그니처·하이퍼파라미터 일치

<!-- 패치가 손대는 vendor 파일들의 함수/클래스 시그니처와, H###.md /
     I###.md 에서 인용된 모든 verbatim 토큰(`ε = 0.1`, `chunk_size = 50`
     등)이 패치 본문과 일치하는지 점검합니다. 코드 실행 없이 정적
     비교만 합니다. -->

| 항목 | 출처 | 패치 본문 | 일치 |
|------|------|-----------|------|
| 함수 시그니처 `forward(...)` | `vendor/lerobot/policies/<base>/modeling_<base>.py:LNN` | `patch hunk @<line>` | ✅ / ❌ / ⚠️ |
| 상수 `<name> = <value>` | `H###.md §🧩` verbatim | `patch hunk @<line>` | ✅ / ❌ / ⚠️ |
| import 경로 `<module>` | `I###.md §🪛` | `patch hunk @<line>` | ✅ / ❌ / ⚠️ |
| … | | | |

판정: `pass` / `fail` / `partial`

<!-- 모든 행 ✅ → pass. 런타임 오류를 유발할 시그니처 ❌ 한 줄이라도
     있으면 fail. 인용은 되었으나 패치에 없는 상수 ⚠️ 가 있으면 partial. -->

---

## 📐 식·표 일치

<!-- H###.md 또는 cited analysis/<id>.md 가 언급한 모든 수식(`Eq. (4)`)
     · 표(`Table 3`) 가 패치에 구현되어 있는지, 또는 I###.md §🚧 미해결
     로 명시적으로 유보되어 있는지 점검합니다. 둘 다 아닌 silent-skip
     은 partial 입니다. -->

| 참조 | 출처 | 패치 hunk / 🚧 항목 | 상태 |
|------|------|---------------------|------|
| `Eq. (4)` | `analysis/<id>.md §🔬` | `I###.patch @<line>` / `I###.md §🚧 #N` | 구현 / 유보 / silent-skip |
| `Table 3` | `H###.md §🧩` | `…` | 구현 / 유보 / silent-skip |
| … | | | |

<!-- silent-skip 항목은 §🧪 시그니처·하이퍼파라미터 판정에 partial 로
     반영됩니다 (이 섹션 자체는 manifest 의 별도 필드를 갖지 않음). -->

---

## ⚖️ 종합 판정

<!-- 세 manifest 필드 (literature · patch_consistency · signature_check)
     를 요약합니다. 모두 pass → "manifest.status 를 validated 로 격상합니다."
     하나라도 fail → "status 는 draft 로 유지합니다 — <어떤 체크가 어떤
     사유로 실패했는지> 가 해결되어야 합니다."
     mixed pass/partial → "status 는 draft 로 유지합니다 — <partial 항목>
     이 후속 정리 대상입니다." -->

- 📚 문헌 대조: `pass` / `fail` / `partial`
- 🔍 패치 정합성: `pass` / `fail`
- 🧪 시그니처·하이퍼파라미터: `pass` / `fail` / `partial`

→ <격상 / 유지 + 사유 한 줄>

---

## 🚧 미해결 / 잠정

<!-- 정적 검증으로 결론 낼 수 없어 사람의 후속 판단이 필요한 항목.
     ⚠️ vendor refresh 로 인한 manifest ↔ 현재 관측 불일치, 코드 실행이
     필요한 체크(학습/평가), 가설 본문이 너무 모호해 식·표 매핑이
     안 되는 항목 등. 없음이면 "없음" 으로 명시. -->

- (예) 가설의 §🔬 ② 체크는 실제 학습 결과 비교가 필요해 정적 검증으로 결론 불가
- (예) `manifest.implementation.apply_check` 는 `pass` 였으나 현재 재검에서 `fail` — vendor refresh 의심
