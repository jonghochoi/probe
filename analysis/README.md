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
| `<arxiv-id>_impl.md` | `/reproduce-paper` 슬래시 커맨드 | 위 분석을 입력으로 받아 `vendor/lerobot/` baseline 대비 변경 지점을 매핑한 한글 구현 가이드 |
| `<arxiv-id>_impl.patch` | `/reproduce-paper` 슬래시 커맨드 | 같은 baseline 에 적용 가능한 unified diff (`git apply --check` 검증) |

- 파일명: arXiv 입력은 `analysis/<arxiv-id>.md`(예: `analysis/2401.12345.md`),
  비-arXiv PDF 는 사람이 지정한 slug. 구현 가이드는 동일 stem 에
  `_impl.md` / `_impl.patch` 를 붙입니다.
- 다른 PROBE 산출물과 마찬가지로 **한글 단일** 문서입니다(영문 1차 파일 없음).
- 같은 논문 재실행 시 append 가 아니라 **덮어쓰는** 재생성 스냅샷입니다.
- 분석 문서 구조: (A) 형식을 갖춘 중립 논문 정리부 + (B) `context/MASTER.md`
  연동 decision-grade 함의부. 형식·이모지·용어는 `docs/STYLE_GUIDE.md`
  §5 / §4, 폼은 `analysis/_TEMPLATE.md` 를 따릅니다.
- 구현 가이드 구조: 6개 `##` 섹션(📄 가이드 메타 · 🧱 베이스 모델 식별 ·
  🪛 변경 지점 매핑 · ⚙️ 핵심 변경(diff) · 🧪 실무 구현 주의 ·
  🚧 미해결 / 잠정). 폼은 `analysis/_TEMPLATE_IMPL.md`, 규칙은
  `docs/STYLE_GUIDE.md` §6 을 따릅니다.
- 호출:
  - `/analyze-paper <arXiv id | url | pdf url>` — 정식 프롬프트
    `.claude/prompts/paper-analysis.md`. cloud 에서 `curl` 로 본문을
    전문 우선 확보하되, 실패하면 ar5iv → 초록 only 로 단계적 폴백하고
    **확보 수준을 문서 헤더에 명시**합니다. 본문 미확보 시 (B) 섹션은
    잠정으로 표기합니다.
  - `/reproduce-paper <id>` — 정식 프롬프트
    `.claude/prompts/paper-reproduction.md`. 선결 조건은
    `analysis/<id>.md` 의 존재이며, 베이스 모델이 vendor 6종(`pi0`,
    `pi05`, `pi0_fast`, `smolvla`, `act`, `diffusion`) 안에 들어올 때만
    `_impl.md` + `_impl.patch` 를 산출합니다. 범위 밖이면 분석 문서
    말미에 `> 🚧 재현 가이드 미생성 — 베이스 모델이 vendor 범위 밖입니다.`
    한 줄만 추가하고 멈춥니다.
- `context/MASTER.md` 도, `vendor/lerobot/` 도 절대 수정하지 않습니다.
  핀/Decision 변경 제안은 문서의 💡 컨텍스트 제안 섹션에만, vendor
  스냅샷 갱신은 `vendor/lerobot/README.md` 의 절차로만 진행합니다.
