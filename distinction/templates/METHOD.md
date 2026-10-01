# METHOD — <working title of the paper>

code: <absolute path to the codebase — or leave this line out and put a `code` symlink beside this file>

<!-- Human-owned. The routine reads this file and never edits it. Section
     spine and the claim entry format: `distinction/SETUP.md` §2-2. The public
     half of the thesis is `context/MASTER.md` §1 and is pointed at, not
     repeated — the same fact in both files is one of them going stale. -->

## 0. 문제의식

<`context/MASTER.md` §1 을 가리키는 한 줄. 그 다음은 공개할 수 없는 절반만 —
어느 바구니 논문의 어느 빈자리를 치는가, 왜 지금인가, 이 논문이 없으면 어느
D# 가 공중에 떠 있는가.>

## 1. 주장

<!-- One `####` heading and one bullet per claim. `C` + a number, unique,
     never re-issued. The bullet carries the claim, its 반증 조건 and the D#
     it implements — these are what the ledger's §1 / §4 and the matrix rows
     hang off. -->

#### [C1] <claim title>
- <무엇이 참이면 방법이 작동하는가, 한 문장> · 반증: <무엇이 보이면 거짓인가> · 구현: D<id>
#### [C2] <claim title>
- …

## 2. 방법

<아키텍처 · 학습 레시피 · 데이터 — 어느 D# 를 어떻게 구현했는지, 가능한 곳마다
`path:line` 또는 `cfg:key` 앵커와 함께 (`CODEMAP.md` 의 좌표).>

## 3. 측정

| 벤치마크 | 지표 | 현재 수치 | 비교 대상 |
|---|---|---|---|
| <…> | <…> | <…> | <바구니 alias> |

## 4. 알려진 약점

<반박당할 자리. 장부의 "내 방법이 메우는가" 는 그들의 ablation 과 이 절을
맞댄다 — 솔직할수록 위협 셀이 정확해진다.>

- <약점 1 — 어느 C# 에 걸리는가>

## 5. 진행 중

- <돌고 있는 ablation, 기대값, 끝나는 날>

## 6. 외부 발화 금지

<!-- Literal strings. The lint searches every ledger, the matrix and every run
     for each bullet and refuses to pass an output that carries one. -->

- <아직 어느 출력에도 나가면 안 되는 문자열>
