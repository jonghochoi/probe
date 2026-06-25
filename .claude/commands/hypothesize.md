---
description: 누적된 analysis DB 를 한 pillar/decision 범위로 가로질러 읽어, Decision Log 에 앵커된 순위화·반증가능한 가설 + 합의·불일치 매트릭스를 생성 (읽기 전용 합성 — 실험 실행 없음). --seed 로 사용자 가설/아이디어를 top-down 주입 가능
argument-hint: <P0..P5 | D# | D#-D#> [--seed "<idea>" | --seed-file <path>] [--compare-only] [--top-k N]
---

- **실행** — `.claude/prompts/hypothesize.txt` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = 범위(pillar id 또는 decision id/range) + 옵션.
- **`--seed`** — 사용자 연구 아이디어/가설을 top-down 으로 주입. 1급 후보로 DB 에 대고 grounding; ≥2 인용이면 정식 가설, 못 찾으면 `exploratory · ungrounded` 라벨로 표면화(드롭 안 함). 범위 없이 `--seed` 만 주면 관련 pillar 를 추론하고 선택을 밝힘.
- **빈 인자 시** — 범위(`P0`–`P5` / `D#`)도 `--seed` 도 없으면 사용자에게 묻고 중단 (직접 선택 금지).
- **사전조건** — `analysis/README.md` 존재 + 범위에 묶인 분석 ≥3편. 미달이면 중단하고 "코퍼스 부족"으로 정직하게 보고.
- **경계** — 실험을 실행하지 않음. 산출물은 *검증된 결론*이 아니라 *test-ready 실험 명세*이며, 모든 가설은 `inferred`/`unverified` 라벨로 출하. 경험적 검증(Rung 3)은 사람 몫.
