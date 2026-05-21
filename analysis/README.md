# analysis/

주간 스카우팅(`scouting/`) · 월간 종합(`synthesis/`)과 **분리된** 산출물
경로입니다. 새 논문을 찾는 곳도, 핀 논문 묶음을 재진술하는 곳도
아닙니다. 사람이 이미 신경 쓰는 **특정 논문 한 편** (보통
`context/MASTER.md` §8 Tracked Literature 의 핀/기준 논문) 을 깊게 읽고,
그 한 편에 대한 한글 심층 분석과 **vendor-agnostic Layer 1 Design**,
그리고 그 Design 을 한 foundry 의 좌표계로 매핑한 Layer 2 구현·검증
산출물을 남기는 곳입니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `<arxiv-id>.md` | `/analyze-paper` 슬래시 커맨드 | arXiv id/URL 또는 PDF URL 한 편을 전문 우선으로 분석한 단일 한글 문서 |
| `<arxiv-id>_design.md` | `/analyze-paper` 슬래시 커맨드 | 위 분석에서 추출한 **Layer 1 Design** — 데이터 계약·모듈 인터페이스·불변식·하이퍼·평가 메트릭. **base 좌표 없음** (vendor-agnostic) |
| `<arxiv-id>_impl/<foundry>/impl.md` | `/foundry` 슬래시 커맨드 | 위 Design 을 한 foundry (기본 `lerobot`) 의 좌표계로 매핑한 한글 구현 가이드 |
| `<arxiv-id>_impl/<foundry>/impl.patch` | `/foundry` 슬래시 커맨드 | 같은 foundry 에 적용 가능한 unified diff (`git apply --check` 검증) |
| `<arxiv-id>_impl/<foundry>/UNMAPPABLE.md` | `/foundry` 슬래시 커맨드 | Design 이 이 foundry 의 좌표계로 매핑되지 않을 때 한 줄 사유만 남기는 파일 (impl.md/patch 대신) |
| `<arxiv-id>_audit/<foundry>.md` | `/audit` 슬래시 커맨드 | 위 impl 을 Design + 분석 문서 + foundry 코드와 정적 대조한 한글 검증 보고서 |

## 📑 Index

아래 표는 `scripts/refresh-analysis-index.py` 가 자동 관리합니다 —
`/analyze-paper`, `/foundry`, `/audit` 가 자기 산출물을 커밋할 때
같이 갱신합니다. 마커 사이는 매 호출마다 멱등 재생성되므로 손으로
편집하지 마십시오. `lerobot` 컬럼은 `<id>_impl/lerobot/impl.md`
존재 시 ✅, `UNMAPPABLE.md` 존재 시 🚧 UNMAPPABLE, 둘 다 없을 때 —.
규칙은 `docs/STYLE.md` §5-7 에 정리돼 있습니다.

<!-- ANALYSIS_INDEX:START -->

| # | Analysis | arXiv | Title | Refreshed | lerobot |
|---|---|---|---|---|---|
| 1 | [`2511.00139.md`](2511.00139.md) | [`2511.00139`](https://arxiv.org/abs/2511.00139) | End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy: VR Teleoperation Augmented by Autonomous Hand VLA Policy for Efficient Data Collection | 2026-05-21 | — |

<!-- ANALYSIS_INDEX:END -->

## 호출

`/analyze-paper <arXiv id | url | pdf url>` — 정식 프롬프트는
`.claude/prompts/paper-analysis.md`. cloud 에서 `curl` 로 본문을 전문
우선 확보하되, 실패하면 ar5iv → 초록 only 로 단계적 폴백하고 **확보
수준을 문서 헤더에 명시**합니다. 본문 미확보 시 decision-grade 함의부는
잠정으로 표기합니다. 분석 문서와 Design 문서를 같은 호출에서 함께
생성합니다 — Design 은 추상화가 부족하면 `(원문에 명시 없음 — 가정으로
메움)` 으로 정직하게 비웁니다. 호출 경로는 세 가지이며 모두 같은
슬래시 커맨드를 호출해 같은 두 파일을 생성합니다:

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

(a) 가 일상적인 경로, (b) 는 셸 스크립트에 끼우기 좋은 형태, (c) 는
브라우저만 있으면 어디서든 가능한 형태입니다. 셋 다 **셸 CLI 가 아니라**
Claude Code 의 슬래시 커맨드 (`.claude/commands/analyze-paper.md`) 이며,
`PATH` 위의 실행 파일이 아닙니다.

`/foundry analysis/<id>_design.md [--foundry <name>]` — 정식 프롬프트는
`.claude/prompts/foundry.md`. 선결 조건은 `analysis/<id>.md` 와
`analysis/<id>_design.md` 의 존재이며, Design 이 target foundry 의
좌표계로 매핑 가능할 때만 `impl.md` + `impl.patch` 를 산출합니다. 매핑
불가 시 `UNMAPPABLE.md` 와 `analysis/<id>.md` 말미의 `> 🚧 매핑 불가
(<foundry>) — …` 한 줄만 추가하고 멈춥니다. 기본 foundry 는 `lerobot`
(= `vendor/lerobot/` 의 6 종 정책).

`/audit analysis/<id>_design.md [--foundry <name>]` — 정식 프롬프트는
`.claude/prompts/audit.md`. Design + impl 패치 + 분석 문서를 정적으로
대조해 `<id>_audit/<foundry>.md` 를 산출합니다. 보고서 자체가
산출물이며 상태 격상 같은 라이프사이클은 없습니다.

**다중 foundry.** `<id>_impl/` 와 `<id>_audit/` 아래의 `<foundry>`
서브폴더가 다중 foundry 를 폴더 레벨에서 수용합니다. `lerobot` 이 v0
foundry 이며, 회사 코드용 foundry 가 추후 추가되면 같은 Design 을
그대로 두고 `/foundry` 만 `--foundry <new-name>` 으로 다시 호출하면
됩니다 — Design 은 한 번 만들면 여러 foundry 에서 재사용됩니다.

## 다른 산출물·컨텍스트와의 관계

- 입력: 사람이 직접 골라 슬래시 커맨드에 넘긴 arXiv id 또는 PDF URL.
  `context/MASTER.md` §8 Tracked Literature 의 핀/기준 논문이 일반적
  대상이지만, 슬래시 커맨드는 임의의 입력을 받습니다.
- 분리: 새 논문 탐색은 `scouting/`, 핀 묶음의 서사 압축은 `synthesis/`,
  한 편 심층은 `analysis/`. `scouting/` 리포트의 ✨ 추천 논문이
  `analysis/` 의 입력으로 이어질 수 있지만 자동화는 없습니다 — 사람이
  슬래시 커맨드로 명시적으로 호출합니다.
- foundry 좌표: `<id>_impl/lerobot/` 의 패치는 `vendor/lerobot/` 의
  pinned 스냅샷 위에서만 의미가 있습니다. vendor 스냅샷 갱신은
  `vendor/lerobot/README.md` 의 절차로만 진행하며, 기존 패치는
  필요시 재생성합니다.

## 절대 규칙

- `context/MASTER.md` 도, `vendor/lerobot/` 도 **절대 수정하지 않습니다**.
  핀/Decision 변경 제안은 분석 문서의 💡 컨텍스트 제안 섹션에만,
  vendor 스냅샷 갱신은 `vendor/lerobot/README.md` 의 절차로만
  진행합니다.
- 한글 단일 문서 (영문 1차 파일 없음). 같은 논문 재실행 시 append 가
  아니라 **덮어쓰는** 재생성 스냅샷입니다.
- 분석 문서 구조는 `docs/STYLE.md` §5 + `analysis/_TEMPLATE.md`,
  Design 문서는 §6 + `analysis/_TEMPLATE_DESIGN.md`, 구현 가이드는
  §6 + `analysis/_TEMPLATE_IMPL.md`, 검증 보고서는 §6-5 +
  `analysis/_TEMPLATE_AUDIT.md` 를 정확히 따릅니다.
