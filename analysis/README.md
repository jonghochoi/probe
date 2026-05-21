# analysis/

주간 스카우팅(`scouting/`) · 월간 종합(`synthesis/`)과 **분리된**
산출물 경로입니다.

새 논문을 찾는 곳도, 핀 논문 묶음을 재진술하는 곳도 아닙니다. 사람이
이미 신경 쓰는 **특정 논문 한 편**(보통 `context/MASTER.md` §8 Tracked
Literature 의 핀/기준 논문)을 깊게 읽고, 그 한 편에 대한 한글 심층
분석과 **vendor-agnostic Layer 1 Design** 을 남기는 곳입니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `<arxiv-id>.md` | `/analyze-paper` 슬래시 커맨드 | arXiv id/URL 또는 PDF URL 한 편을 전문 우선으로 분석한 단일 한글 문서 |
| `<arxiv-id>_design.md` | `/analyze-paper` 슬래시 커맨드 | 위 분석에서 추출한 **Layer 1 Design** — 데이터 계약·모듈 인터페이스·불변식·하이퍼·평가 메트릭. **base 좌표 없음** (vendor-agnostic) |
| `<arxiv-id>_impl/<foundry>/impl.md` | `/foundry` 슬래시 커맨드 | 위 Design 을 한 foundry (기본 `lerobot`) 의 좌표계로 매핑한 한글 구현 가이드 |
| `<arxiv-id>_impl/<foundry>/impl.patch` | `/foundry` 슬래시 커맨드 | 같은 foundry 에 적용 가능한 unified diff (`git apply --check` 검증) |
| `<arxiv-id>_impl/<foundry>/UNMAPPABLE.md` | `/foundry` 슬래시 커맨드 | Design 이 이 foundry 의 좌표계로 매핑되지 않을 때 한 줄 사유만 남기는 파일 (impl.md/patch 대신) |
| `<arxiv-id>_verify/<foundry>.md` | `/verify` 슬래시 커맨드 | 위 impl 을 Design + 분석 문서 + foundry 코드와 정적 대조한 한글 검증 보고서 |

- 파일명: arXiv 입력은 `analysis/<arxiv-id>.md`(예: `analysis/2401.12345.md`),
  비-arXiv PDF 는 사람이 지정한 slug. Design / impl / verify 산출물은
  같은 stem 을 공유합니다.
- 다른 PROBE 산출물과 마찬가지로 **한글 단일** 문서입니다(영문 1차 파일 없음).
- 같은 논문 재실행 시 append 가 아니라 **덮어쓰는** 재생성 스냅샷입니다.
- 분석 문서 구조: (A) 형식을 갖춘 중립 논문 정리부 + (B) `context/MASTER.md`
  연동 decision-grade 함의부. 형식·이모지·용어는 `docs/STYLE_GUIDE.md`
  §5 / §4, 폼은 `analysis/_TEMPLATE.md` 를 따릅니다.
- Design 문서 구조: 9개 `##` 섹션(📄 Design 메타 · 🧮 데이터 계약 ·
  🧰 모듈 인터페이스 · ⛓️ 불변식·가정 · 📊 하이퍼파라미터·손실 ·
  🎯 평가 메트릭 · ✨ 변경 의도 · 🔌 Foundry 힌트 · 🚧 미해결 / 잠정).
  폼은 `analysis/_TEMPLATE_DESIGN.md`, 규칙은 `docs/STYLE_GUIDE.md` §6.
- 구현 가이드 구조: 6개 `##` 섹션(📄 가이드 메타 · 🧱 베이스 / 코드 좌표
  식별 · 🪛 변경 지점 매핑 · ⚙️ 핵심 변경(diff) · 🧪 실무 구현 주의 ·
  🚧 미해결 / 잠정). 폼은 `analysis/_TEMPLATE_IMPL.md`, 규칙은
  `docs/STYLE_GUIDE.md` §6 을 따릅니다.
- 호출:
  - `/analyze-paper <arXiv id | url | pdf url>` — 정식 프롬프트
    `.claude/prompts/paper-analysis.md`. cloud 에서 `curl` 로 본문을
    전문 우선 확보하되, 실패하면 ar5iv → 초록 only 로 단계적 폴백하고
    **확보 수준을 문서 헤더에 명시**합니다. 본문 미확보 시 (B) 섹션은
    잠정으로 표기합니다. 분석 문서와 Design 문서를 같은 호출에서 함께
    생성합니다 — Design 은 추상화가 부족하면 `(원문에 명시 없음 — 가정
    으로 메움)` 으로 정직하게 비웁니다. 호출 경로는 세 가지이며 모두
    동일한 슬래시 커맨드를 호출해 동일한 두 파일을 생성합니다:

    ```bash
    # (a) 로컬 인터랙티브 — repo 루트에서 Claude Code 세션을 열고,
    #     슬래시 커맨드를 입력합니다 (이어지는 턴에도 그대로 호출 가능)
    cd ~/work/probe
    claude
    > /analyze-paper 2410.07864
    > /analyze-paper https://arxiv.org/abs/2410.07864
    > /analyze-paper https://some.lab/paper.pdf
    ```

    ```bash
    # (b) 로컬 원샷 — 인터랙티브 세션 없이 한 번 실행하고 종료
    claude -p "/analyze-paper 2410.07864"
    ```

    ```text
    # (c) 웹 — claude.ai/code, 이 repo 를 attach 한 뒤 슬래시 커맨드 입력
    > /analyze-paper 2410.07864
    ```

    (a) 가 일상적인 경로, (b) 는 셸 스크립트에 끼우기 좋은 형태,
    (c) 는 브라우저만 있으면 어디서든 가능한 형태입니다. 셋 다
    **셸 CLI 가 아니라** Claude Code 의 슬래시 커맨드
    (`.claude/commands/analyze-paper.md`) 이며, `PATH` 위의
    실행 파일이 아닙니다.
  - `/foundry analysis/<id>_design.md [--foundry <name>]` — 정식 프롬프트
    `.claude/prompts/foundry.md`. 선결 조건은 `analysis/<id>.md` 와
    `analysis/<id>_design.md` 의 존재이며, Design 이 target foundry 의
    좌표계로 매핑 가능할 때만 `impl.md` + `impl.patch` 를 산출합니다.
    매핑 불가 시 `UNMAPPABLE.md` 와 `analysis/<id>.md` 말미의
    `> 🚧 매핑 불가 (<foundry>) — …` 한 줄만 추가하고 멈춥니다.
    기본 foundry 는 `lerobot` (= `vendor/lerobot/` 의 6 종 정책).
  - `/verify analysis/<id>_design.md [--foundry <name>]` — 정식 프롬프트
    `.claude/prompts/verify.md`. Design + impl 패치 + 분석 문서를
    정적으로 대조해 `<id>_verify/<foundry>.md` 를 산출합니다. 분석
    트랙은 manifest 라이프사이클이 없으므로 상태 격상은 일어나지
    않습니다 — 보고서 자체가 산출물입니다.

## 다중 foundry

`<id>_impl/` 와 `<id>_verify/` 아래의 `<foundry>` 서브폴더가 다중
foundry 를 폴더 레벨에서 수용합니다. `lerobot` 이 v0 foundry 이며,
회사 코드용 foundry 가 추후 추가되면 같은 Design 을 그대로 두고
`/foundry` 만 `--foundry <new-name>` 으로 다시 호출하면 됩니다. Design
은 한 번 만들면 여러 foundry 에서 재사용됩니다.

`context/MASTER.md` 도, `vendor/lerobot/` 도 절대 수정하지 않습니다.
핀/Decision 변경 제안은 분석 문서의 💡 컨텍스트 제안 섹션에만, vendor
스냅샷 갱신은 `vendor/lerobot/README.md` 의 절차로만 진행합니다.
