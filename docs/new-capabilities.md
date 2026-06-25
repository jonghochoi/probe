# PROBE 확장 기능 안내 (한글)

이 문서는 PROBE에 새로 추가된 연구 기능을 **이해 목적**으로 한곳에 정리한
것이다. 포맷 규칙 문서가 아니다 — 출력 포맷은 `docs/STYLE.md`, 기여 규약은
`CLAUDE.md`가 단일 출처다.

기존 PROBE는 두 트랙이었다.

- **scouting/** — 매주 arXiv를 정찰해 pillar별로 3–5편을 점수화해 올린다 (찾기).
- **analysis/** — 사람이 고른 한 편을 한글 deep-dive + Layer 1 Design + (선택)
  foundry impl/validation으로 깊게 판다 (재현).

여기에 **누적된 분석 DB 위에서 새 가설을 세우고 검증 가능성을 따지는** 능력을
더했다. Feynman(범용 AI 리서치 CLI)에서 *패턴*만 골라 흡수했고, 런타임·배포·
텔레메트리 같은 제품 골격은 가져오지 않았다. 추가된 것은 셋이다.

1. `/hypothesize` — 분석 DB를 가로질러 가설을 합성하는 **세 번째 트랙** (신규).
2. `/audit-paper` — 논문이 자기 코드와 맞는지 보는 **재현 게이트** (신규).
3. **scouting 점수 보강** — 재현성·방법론 축 강화 (기존 트랙 개선).

그리고 Feynman의 `/compare`(논문 간 합의·불일치)는 별도 명령으로 만들지 않고
`/hypothesize`에 흡수했다(`--compare-only`).

---

## 1. `/hypothesize` — 가설 합성 트랙

### 무엇인가

누적된 `analysis/<id>/` deep-dive들을 **한 pillar 또는 한 decision 묶음
범위**로 가로질러 읽고, `context/P#.md`의 Decision Log(D1–D32)에 앵커된
**순위화된 반증 가능한 가설**을 만든다. 핵심 통찰은, deep-dive 스키마가 이미
논문별로 가설 원료를 인코딩하고 있다는 점이다:

| analysis.md 섹션 | 가설 원료로서의 역할 |
|---|---|
| `🎯 관련 Pillar / Decision` | 각 논문을 D#에 묶는 join key |
| `⚙️ 의사결정 함의` | 논문별 "D#를 …로 바꿔라" — 한 D#에 대한 함의가 **충돌하면 곧 가설** |
| `⚠️ 먼저 검증할 실패 모드` | 논문 국소 가설; 여러 편에서 **반복되면 강한 가설** |
| `✨ 핀 논문 대비 델타` | 핀 문헌과 충돌하는 지점 — 텐션 씨앗 |
| `♻️ 재현성` + `design.md` | 가설이 foundry-portable(검증 가능)인지 판정 |

즉 새 추출을 거의 하지 않는다. 한 편씩 적힌 함의를 **논문 간**으로 읽어 모순·
반복 실패모드·미시도 조합·증거 공백을 캔다.

### 6단계 루프 (0–4는 이 명령, 5는 사람)

- **Stage 0 범위** — 한 pillar/decision 묶음으로 한정. 범위 분석이 3편 미만이면
  "코퍼스 부족"으로 중단(정직). 무한정 "전부 가설화"는 거부 — 조합 폭발 방지.
- **Stage 1 코퍼스 조립** — `catalogs/analyses.md` 인덱스로 범위에 묶인 분석만
  골라 네 원료 섹션을 읽는다(전체 DB를 컨텍스트에 안 올림).
- **Stage 2 합의·불일치 매트릭스 + 텐션 마이닝** — 각 D#별로 논문들이 어디로
  미는지 + confidence를 표로, 이어 4종 텐션(모순/반복 실패모드/미시도 조합/증거
  공백)을 표면화. `--compare-only`면 여기서 멈춤.
- **Stage 3 가설 합성** — 가설마다 반드시: 반증 가능한 한 줄 주장 · D# 앵커 ·
  **≥2개 grounding 인용** · 측정 가능한 예측 효과 · 측정 프로토콜(사다리 rung
  명시) · foundry-portability 판정. 조건 미달이면 그 가설은 버린다.
- **Stage 4 순위화** — 증거 강도 × 결정 레버리지 × 검증 가능성 × 비용 역수로
  top-K. **사람이** 어느 가설을 돌릴지 고른다(PROBE는 안 고름).
- **Stage 5 실험** — *이 명령 밖*. 사람이 돌린다(아래 closed-loop 설명 참조).

### 측정 사다리 — closed-loop이 robotics에서 어려운 이유

순수 ML이면 "벤치마크 돌려 스칼라 받기"가 빠르지만, 로보틱스 VLA는
sim-to-real gap, GPU-days 비용, rollout/seed 분산, 그리고 "결정의 효과가 풀
파이프라인 학습 후에야 드러남" 때문에 **자동 closed loop이 사실상 불가능**하다.
그래서 PROBE는 측정을 단일 게이트가 아니라 사다리로 본다:

| Rung | 무엇을 보나 | 자동? | 정직한 라벨 |
|---|---|---|---|
| 0 | foundry smoke — patch 적용·build·shape | 자동 (나중에 `/validate-impl §🧬`) | `implementable` |
| 1 | proxy — param/FLOPs/latency Δ, overfit-one-batch | 자동 (나중에) | `proxy-consistent` |
| 2 | sim micro-eval — 소규모 학습·few-task | 반자동 (sim2real·분산 주의) | `indicative` |
| 3 | 풀 pretrain/finetune + multi-seed 실로봇/풀sim eval | **자동 아님 — 사람·배치** | `empirically-verified` |

**중요한 결정**: foundry-runtime의 smoke test가 자동으로 닫는 건 Rung 0–1
(=구현 가능·싸게 봐도 말이 됨)뿐이고, 이는 "**가설이 참이다**"가 아니라
"**구현 가능하다**"는 뜻이다. 둘을 같은 `verified`로 부르면 거짓 확신이 된다.
그래서 `/hypothesize`의 산출물은 *검증된 결론*이 아니라 **test-ready 실험
명세**이고, 모든 가설은 `inferred`/`unverified` 라벨로 출하된다. 진짜 경험적
검증(Rung 3)은 사람이 배치로 돌리는 **open loop**이다. 이는 PROBE 철학
("스카우트는 결정하지 않는다")과도 일치한다 — 노이즈 큰 로봇 eval로 에이전트가
keep/discard를 자동 결정하면 그 철학이 깨진다.

> 정리: Feynman `/autoresearch`의 *패턴*(hypothesize→measure→keep/discard)은
> 빌렸지만, "자율 closed loop"이라는 약속은 robotics에선 내렸다. `/hypothesize`
> = 가설 생성 + 순위화 + 실험 설계까지(tractable·자율). 측정 실행은 사람.

### 산출물

- `hypotheses/<slug>/hypotheses.md` — 범위·요약 / 🔀 합의·불일치 매트릭스 /
  ⚡ 텐션 / 💡 가설(순위·rung·라벨) / 🏆 순위 / 🚧 Decision Log 제안.
- `hypotheses/<slug>/hypotheses.provenance.md` — 읽은 분석 목록, 텐션→가설 계보,
  가설별 검증 상태.
- `--compare-only`면 `compare.md`만.

### 사용 예

```
/hypothesize P1
/hypothesize D1-D7 --top-k 3
/hypothesize P4 --compare-only
/hypothesize P1 --seed "FiLM body→hand 결합이 cross-attention보다 정밀 파지에 유리할까"
/hypothesize --seed-file notes/tactile-idea.md
```

### `--seed` — 내 가설/아이디어를 top-down 주입

기본 `/hypothesize`는 DB가 말해주는 텐션을 *발견*하는 bottom-up이다. `--seed`로
내 연구 아이디어·가설·질문을 직접 던지면, PROBE가 그걸 **1급 후보 가설**로 받아
범위 코퍼스에 대고 grounding한다:

- **≥2 grounding 인용** 확보 → 마이닝 가설과 동일하게 정식 가설로 발전(`user-seeded` 계보).
- **근거 부족(<2)** → **드롭하지 않는다**(마이닝 가설과의 유일한 예외). `exploratory ·
  ungrounded`로 정직하게 라벨링하고, 가장 가까운 분석 + "이걸 grounding하려면 먼저
  `/analyze-paper` 할 후보" 또는 "증거 공백"을 알려준다. 가짜 근거는 절대 안 붙인다.
- 시드 가설은 `--top-k`와 무관하게 **항상 표시**되고, provenance에 `user-seeded`로
  기록돼 DB 근거가 끝나고 사용자 추정이 시작되는 지점이 감사 가능하다.
- 범위(pillar) 없이 `--seed`만 주면 PROBE가 Decision Log/catalogs로 관련 pillar를
  추론하고 무엇을 골랐는지 밝힌다. 시드가 있으면 코퍼스가 얇아도(≥3편 미만) 진행하되
  그 사실을 보고한다.

상시 시드는 따로 있다 — **`context/P#.md`**(Decision Log, Hardware, Identity)가
모든 run에 깔리는 영속 컨텍스트다. `--seed`는 그 위에 얹는 run별 즉석 조향이다.

---

## 2. `/audit-paper` — 논문↔코드 재현 게이트

### 무엇인가 / 왜

논문이 **주장한** method·default·hyperparameter·metric이 **논문 자체 공식
repo**와 일치하는지 검사한다. `/reproduce-paper`로 analyze→implement→validate
라운드를 태우기 *전에* 돌리는 싼 게이트다 — 자기 코드와도 안 맞는 논문에 비싼
재현 투자를 막는다. PROBE엔 특히 잘 맞는다(이미 `vendor/lerobot` + foundry
runtime 문화가 있어 재현 가능성을 진지하게 본다).

### `/validate-impl`과의 차이 (헷갈리지 말 것)

| | `/audit-paper` (신규) | `/validate-impl` (기존) |
|---|---|---|
| 검사 대상 | 논문 주장 ↔ **논문 자체** 공식 repo | PROBE Design+patch ↔ **foundry**(`vendor/lerobot`) |
| 위치 | 재현 funnel **앞** (게이트) | 재현 funnel **뒤** (구현 검증) |
| 산출물 | `analysis/<id>/audit.md` | `analysis/<id>/validation/<foundry>.md` |

### 판정

claim별로 `✅ 일치 / ⚠️ MINOR / 🔶 MAJOR / 🔴 FATAL`(severity는 reviewer식),
이를 하나의 게이트로 롤업: `✅ 재현 추천 / ⚠️ 주의 후 재현 / 🛑 재현 비추천 /
🚫 audit 불가`. 공식 코드를 못 찾거나 못 가져오면 가짜 pass 대신 `🚫 audit 불가`.

보고서는 일치/불일치에 더해 **🕳️ 누락**(코드에 아예 없는 주장 — "다르게 구현"과
구분)과 **♻️ 재현 리스크**(주장이 맞아도 못 돌리게 만드는 것 — seed 미설정·의존성
미고정·hardcoded path·env 누락)를 별도 섹션으로 둔다. 재현 리스크가 심하면 청구가
맞아도 게이트가 `⚠️ 주의`로 내려간다. (Feynman audit의 `reproduction risks` /
`missing code` 구분을 흡수.) 📄 메타에는 `검사 N · 일치 X · 불일치 Y · 누락 Z`
카운트가 들어간다.

### 사용 예

```
/audit-paper 2605.07308
/audit-paper 2605.31486 --repo https://github.com/org/repo
```

---

## 3. scouting 점수 보강 (PaperRank 흡수)

기존 scouting은 4축(Relevance / Novelty / Reproducibility / Sim2Real)을 0–3으로
매겼는데, "재현 가능성" 축이 얕고 "방법론 견고함" 축이 없었다. Feynman PaperRank
의도(prestige + reproducibility + methodology)를 별도 명령 없이 scouting 루브릭에
흡수했다:

- **Reproducibility** — 구체 0–3 사다리: `0 paper-only · 1 partial · 2 code+data
  public · 3 official repo + data + hardware/configs (runnable)`.
- **Methodology** (신규 축) — 실험 견고함: baselines, ablations, eval 타당성,
  seeds/variance. `0 anecdotal · 1 weak · 2 solid · 3 strong & honest`.

이 둘 + Relevance가 의사결정급 축이고, 노이즈 큰 Novelty/Sim2Real보다 위로
가중한다. 효과: novelty만 높고 재현성·방법론이 없는 논문은 *결과*가 아니라
*리드*로 분류돼 digest 상단을 차지하지 않는다. (정찰 통과 임계 "모든 축 ≥2"가
한 축 더 까다로워진 셈 — 의도된 방향이다.)

---

## 4. Feynman에서 가져온 것 / 안 가져온 것 (요약)

| Feynman 기능 | PROBE 처리 |
|---|---|
| `/autoresearch` (hypothesize→measure→keep/discard) | **패턴만** → `/hypothesize` (단, 측정 실행은 사람; closed-loop 자율 주장 제외) |
| `/compare` (합의·불일치 매트릭스) | `/hypothesize`에 **흡수** (`--compare-only`) |
| `/audit` (논문↔코드) | **신규** `/audit-paper`로 흡수 |
| PaperRank (prestige+reproducibility+methodology) | scouting 루브릭에 **흡수** |
| Pi 런타임 · npm 배포 · 텔레메트리 · Modal/RunPod · alphaXiv/검색 | **안 가져옴** — PROBE의 "런타임 없는 순수 프롬프트" 정체성과 충돌. 범용 리서치는 Feynman을 옆에 두고 그대로 호출 |

---

## 5. 열린 질문 / 다음 단계

- **실험 거처** — net-new 조합 실험(단일 출처 논문 없음)을 `hypotheses/<slug>/exp/`
  로 둘지, 합성 `analysis/` id로 접을지. (현재 `/hypothesize`는 Stage 5를 돌리지
  않으므로 미정으로 둠.)
- **`/hypothesize` cadence** — 수동 전용 유지 vs 코퍼스가 충분히 커지면
  scouting처럼 pillar별 스케줄.
- **코퍼스 임계치** — 현재 범위당 ≥3편. 운영하며 조정.
- **Rung 0–1 자동화 배선** — portable 가설을 `/implement-design` +
  `/validate-impl`로 자동 흘리는 얇은 연결(Phase 2)은 가설 품질이 검증된 뒤에.
