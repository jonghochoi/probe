# experiments/

주간 스카우팅(`scouting/`) · 월간 종합(`synthesis/`) · 온디맨드 분석
(`analysis/`)과 **분리된** 산출물 경로입니다.

새 논문을 찾는 곳도, 핀 논문 묶음을 재진술하는 곳도, 단일 논문을 깊게
정리하는 곳도 아닙니다. **팀 내부 가설**을 출발점으로 잡고 — 가설 +
Design (Layer 1) → foundry 별 구현 (Layer 2) → 문헌·코드 정합성 검증 —
까지의 단일 사이클을 한 폴더 안에 묶어 추적하는 곳입니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `H###.md` | `/hypothesize` 슬래시 커맨드 | Pillar 또는 `analysis/<id>` 에서 끄집어낸 falsifiable 가설의 한글 단일 문서 |
| `D###.md` | `/hypothesize` 슬래시 커맨드 | 위 가설에서 외부화한 **Layer 1 Design** — 데이터 계약·모듈 인터페이스·불변식·하이퍼·평가 메트릭. **base 좌표 없음** (vendor-agnostic) |
| `I###/<foundry>/impl.md` | `/foundry` 슬래시 커맨드 | Design 을 한 foundry (기본 `lerobot`) 의 좌표계로 매핑한 한글 구현 가이드 |
| `I###/<foundry>/impl.patch` | `/foundry` 슬래시 커맨드 | 같은 foundry 에 적용 가능한 unified diff (`git apply --check` 검증) |
| `I###/<foundry>/UNMAPPABLE.md` | `/foundry` 슬래시 커맨드 | Design 이 이 foundry 의 좌표계로 매핑되지 않을 때 한 줄 사유만 남기는 파일 |
| `V###/<foundry>.md` | `/verify` 슬래시 커맨드 | 가설·Design·패치를 문헌(`analysis/<id>.md`) + foundry 코드와 대조한 한글 검증 보고서 |
| `manifest.yaml` | 모든 슬래시 커맨드가 갱신, 사람도 채택/기각 시 직접 편집 | 라이브 아티팩트가 스캔하는 단일 메타데이터 (foundry-keyed) |

- 폴더명: `experiments/H###-<slug>/` (예: `experiments/H001-dual-token-routing/`).
  ID 는 zero-padded 3자리이며, 같은 가설의 `H###` · `D###` · `I###` ·
  `V###` 는 같은 번호를 공유합니다 (H001 → D001 → I001 → V001).
  슬러그는 `/hypothesize` 호출 시 사람이 지정하거나, 에이전트가 가설
  제목에서 kebab-case 로 유도합니다.
- 다른 PROBE 산출물과 마찬가지로 **한글 단일** 문서입니다(영문 1차 파일 없음).
- 가설 본문(`H###.md`) 과 Design (`D###.md`) 은 작성 후 불변 —
  `/foundry` 도 `/verify` 도 본문을 수정하지 않습니다(베이스 매칭 실패
  시 `H###.md` 에 추가되는 한 줄 🚧 블록쿼트만 예외). 같은 주제를 새로
  쓰고 싶다면 새 H 번호로 시작합니다.
- 구현 가이드(`I###/<foundry>/impl.md`)와 검증 보고서
  (`V###/<foundry>.md`)는 **덮어쓰는** 재생성 스냅샷입니다.
  patch (`I###/<foundry>/impl.patch`) 도 같은 가설·foundry 안에서
  재생성 시 덮어씁니다.
- 형식·이모지·용어는 `docs/STYLE_GUIDE.md` §7 / §4, 폼은 폴더 안의
  `_TEMPLATE_H.md` · `_TEMPLATE_D.md` · `_TEMPLATE_I.md` ·
  `_TEMPLATE_V.md` 를 따릅니다.
- 호출:
  - `/hypothesize <P# | analysis-slug> [slug]` — 정식 프롬프트
    `.claude/prompts/hypothesize.md`. Pillar 코드 (`P1`–`P4`) 또는 기존
    `analysis/<id>` 슬러그를 시드로 받아 falsifiable test 를 1–3개
    설계하고, 가설 + Layer 1 Design 을 같은 호출에서 함께 산출합니다
    (`experiments/H###-<slug>/{H###.md, D###.md, manifest.yaml}`).
    시드가 갭을 못 짚으면 만들지 않고 멈춥니다(가짜 가설 금지).
  - `/foundry experiments/H###-*/D###.md [--foundry <name>]` — 정식
    프롬프트 `.claude/prompts/foundry.md`. 선결 조건은 같은 폴더의
    `H###.md` + `D###.md` + `manifest.yaml` 이며, Design 이 target
    foundry 의 좌표계로 매핑 가능할 때만 `I###/<foundry>/impl.md` +
    `impl.patch` 를 산출하고 `manifest.implementation.<foundry>` 를
    갱신합니다. 매핑 불가 시 `UNMAPPABLE.md` 와 `H###.md` 말미의
    `> 🚧 매핑 불가 (<foundry>) — …` 한 줄만 추가하고 멈춥니다.
    기본 foundry 는 `lerobot`.
  - `/verify experiments/H###-*/D###.md [--foundry <name>]` — 정식
    프롬프트 `.claude/prompts/verify.md`. 4 단계 정적 체크(📚 문헌
    대조 · 🔍 패치 정합성 · 🧪 시그니처·하이퍼파라미터 · 📐 식·표
    일치)를 거쳐 `V###/<foundry>.md` 를 작성하고
    `manifest.validation.<foundry>` 를 갱신합니다. 모든 등록된 foundry
    가 세 체크를 전부 통과한 경우에만 `manifest.status` 를
    `draft → validated` 로 격상합니다. 코드는 절대 실행하지 않습니다
    (`git apply --check` 만 허용).

## 상태 전이

```
draft  ──(/verify 가 모든 등록된 foundry 에서 전부 pass)──►  validated
  │
  └──(사람이 manifest.status 직접 편집)──►  adopted  /  rejected
```

`adopted` · `rejected` 는 **사람만** 전이시킵니다. 채택 결정과 함께
`manifest.adopted:` 에 오늘 날짜를 직접 기록합니다. `context/MASTER.md`
가 사람 소유인 것과 같은 원칙입니다.

다중 foundry: 한 가설의 `implementation.<foundry>` 와
`validation.<foundry>` 는 foundry 별 dict 입니다. `lerobot` 만 통과해도
다른 등록된 foundry 가 `partial` 이면 `status` 는 `draft` 로 유지됩니다
— `validated` 격상은 **모든 등록된 foundry 가 모든 체크를 통과**할 때
입니다.

## 다른 산출물과의 관계

- `analysis/<id>.md` — `/hypothesize` 의 시드 후보 중 하나(다른 하나는
  Pillar 코드). 분석 문서의 §⚠️ 먼저 검증할 실패 모드 · §⚙️ 의사결정
  함의 · §💡 컨텍스트 제안 이 가설의 자연스러운 출발점입니다.
- `analysis/<id>_design.md` · `analysis/<id>_impl/<foundry>/*` —
  `/analyze-paper` + `/foundry` 가 만드는 *논문 재현* 결과물이며,
  `experiments/H###-*/D###.md` · `I###/<foundry>/*` 와 포맷은 거의
  같지만 출발점이 다릅니다(전자는 논문, 후자는 팀 가설).
- `vendor/lerobot/` — `lerobot` foundry 의 1 호 코드 좌표계이며, 두
  경우 모두 vendor 트리를 손대지 않고 unified diff 만 생성합니다.
  vendor snapshot 이 새로 찍히면 기존 모든 foundry=lerobot 패치가
  무효화될 수 있으므로, refresh 절차는 `vendor/lerobot/README.md` 를
  따릅니다.

`context/MASTER.md` 도, `vendor/lerobot/` 도 절대 수정하지 않습니다.
핀/Decision 변경 제안은 `H###.md` 의 💡 컨텍스트 제안 섹션에만, vendor
스냅샷 갱신은 `vendor/lerobot/README.md` 의 절차로만 진행합니다.
