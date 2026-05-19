# analysis/

주간 스카우팅(`scouting/`) · 월간 종합(`synthesis/`)과 **분리된**
산출물 경로입니다.

새 논문을 찾는 곳도, 핀 논문 묶음을 재진술하는 곳도 아닙니다. 사람이
이미 신경 쓰는 **특정 논문 한 편**(보통 `context/MASTER.md` §8 Tracked
Literature 의 핀/기준 논문)을 깊게 읽고, 그 한 편에 대한 한글 심층
분석을 남기는 곳입니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `<arxiv-id>.md` | `/analyze-paper` 슬래시 커맨드 (필요시 수동) | arXiv id/URL 또는 PDF URL 한 편을 전문 우선으로 분석한 단일 한글 문서 |

- 파일명: arXiv 입력은 `analysis/<arxiv-id>.md`(예: `analysis/2401.12345.md`),
  비-arXiv PDF 는 사람이 지정한 slug.
- 다른 PROBE 산출물과 마찬가지로 **한글 단일** 문서입니다(영문 1차 파일 없음).
- 같은 논문 재실행 시 append 가 아니라 **덮어쓰는** 재생성 스냅샷입니다.
- 문서 구조: (A) 형식을 갖춘 중립 논문 정리부 + (B) `context/MASTER.md`
  연동 decision-grade 함의부. 형식·이모지·용어는 `docs/STYLE_GUIDE.md`
  §5 / §4, 폼은 `analysis/_TEMPLATE.md` 를 따릅니다.
- 호출: `/analyze-paper <arXiv id | url | pdf url>` (정식 프롬프트
  `.claude/prompts/paper-analysis.md`). cloud 에서 `curl` 로 본문을
  전문 우선 확보하되, 실패하면 ar5iv → 초록 only 로 단계적 폴백하고
  **확보 수준을 문서 헤더에 명시**합니다. 본문 미확보 시 (B) 섹션은
  잠정으로 표기합니다.
- `context/MASTER.md` 는 절대 수정하지 않습니다. 핀/Decision 변경
  제안은 문서의 💡 컨텍스트 제안 섹션에만 적습니다.
