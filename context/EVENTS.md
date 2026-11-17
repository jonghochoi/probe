# EVENTS — Conference and Submission Dates

> **Owns** the dates the reading site's first screen counts down to — the
> conferences this project follows and their submission milestones. The venue
> list is human-owned; the dates are kept by the weekly follow routine
> (`.claude/prompts/follow.txt`), the one agent that writes into `context/`,
> and a person may add or correct a row by hand as well. Read by
> `site/builder/events.py`.

## Venues

The venues the routine follows, each by its official site and what it is
followed for. A person adds or drops a venue here; the routine only moves a
link to the next edition's site when the listed page itself links to it.

`범위` is `전체` for a conference — every date of the three kinds below — or
`옵션 마감` for a journal followed for one kind of date only: its deadline
for a paper that also presents at a conference in this table.

| 학회 | 공식 사이트 | 범위 |
|---|---|---|
| CoRL | https://www.corl.org/ | 전체 |
| RSS | https://roboticsconference.org/ | 전체 |
| ICRA | https://2027.ieee-icra.org/ | 전체 |
| IROS | https://2027.ieee-iros.org/ | 전체 |
| Humanoids | https://2026.ieee-humanoids.org/ | 전체 |
| NeurIPS | https://neurips.cc/ | 전체 |
| ICLR | https://iclr.cc/ | 전체 |
| ICML | https://icml.cc/ | 전체 |
| CVPR | https://cvpr.thecvf.com/ | 전체 |
| RA-L | https://www.ieee-ras.org/publications/ra-l | 옵션 마감 |

## Dates

Each row is one date or one span. A row is entered only once its official
site states the date; a date known only from an aggregator waits. The site
prints the rows whose end has not passed, nearest first, and the routine drops
a row once it has ended.

| 시작 | 끝 | 종류 | 이름 | 장소 | 출처 |
|---|---|---|---|---|---|
| 2026-11-23 | 2026-11-23 | 마감 | CVPR 2027 보충 자료 마감 | AoE | https://cvpr.thecvf.com/Conferences/2027/Dates |
| 2026-12-04 | 2026-12-04 | 마감 | RSS 2027 초록 마감 | AoE | https://roboticsconference.org/ |
| 2026-12-06 | 2026-12-09 | 학회 | Humanoids 2026 | Santa Clara | https://2026.ieee-humanoids.org/ |
| 2026-12-06 | 2026-12-12 | 학회 | NeurIPS 2026 | Sydney | https://neurips.cc/ |
| 2026-12-16 | 2026-12-16 | 발표 | ICLR 2027 결과 발표 | | https://iclr.cc/Conferences/2027/Dates |
| 2026-12-31 | 2026-12-31 | 마감 | RA-L ICRA 2027 옵션 마감 | | https://www.ieee-ras.org/publications/ra-l/ |
| 2027-01-14 | 2027-01-14 | 마감 | ICML 2027 초록 마감 | AoE | https://icml.cc/Conferences/2027/Dates |
| 2027-01-22 | 2027-01-22 | 마감 | ICML 2027 논문 마감 | AoE | https://icml.cc/Conferences/2027/Dates |
| 2027-01-31 | 2027-01-31 | 발표 | ICRA 2027 결과 발표 | | https://2027.ieee-icra.org/ |
| 2027-02-01 | 2027-02-01 | 마감 | CVPR 2027 반박 마감 | | https://cvpr.thecvf.com/Conferences/2027/Dates |
| 2027-02-05 | 2027-02-05 | 발표 | RSS 2027 1단계 결과 | | https://roboticsconference.org/ |
| 2027-02-12 | 2027-02-12 | 마감 | RSS 2027 반박 마감 | AoE | https://roboticsconference.org/ |
| 2027-02-23 | 2027-02-23 | 발표 | ICML 2027 1단계 결과 | | https://icml.cc/Conferences/2027/Dates |
| 2027-02-25 | 2027-02-25 | 발표 | CVPR 2027 결과 발표 | | https://cvpr.thecvf.com/Conferences/2027/Dates |
| 2027-02-26 | 2027-02-26 | 발표 | RSS 2027 2단계 결과 | | https://roboticsconference.org/ |
| 2027-04-16 | 2027-04-16 | 마감 | RSS 2027 논문 마감 | AoE | https://roboticsconference.org/ |
| 2027-04-19 | 2027-04-19 | 마감 | RSS 2027 보충 자료 마감 | AoE | https://roboticsconference.org/ |
| 2027-04-26 | 2027-04-30 | 학회 | ICLR 2027 | | https://iclr.cc/Conferences/2027/Dates |
| 2027-04-30 | 2027-04-30 | 발표 | RSS 2027 결과 발표 | | https://roboticsconference.org/ |
| 2027-04-30 | 2027-04-30 | 마감 | RA-L IROS 2027 옵션 마감 | | https://www.ieee-ras.org/publications/ra-l/ |
| 2027-05-03 | 2027-05-03 | 발표 | ICML 2027 결과 발표 | | https://icml.cc/Conferences/2027/Dates |
| 2027-05-14 | 2027-05-14 | 마감 | RSS 2027 카메라 레디 마감 | AoE | https://roboticsconference.org/ |
| 2027-05-24 | 2027-05-28 | 학회 | ICRA 2027 | Seoul · COEX | https://2027.ieee-icra.org/ |
| 2027-06-20 | 2027-06-25 | 학회 | CVPR 2027 | Seattle | https://cvpr.thecvf.com/ |
| 2027-06-30 | 2027-06-30 | 마감 | RA-L Humanoids 2027 옵션 마감 | | https://www.ieee-ras.org/publications/ra-l/ |
| 2027-07-06 | 2027-07-11 | 학회 | RSS 2027 | Athens | https://roboticsconference.org/ |
| 2027-07-31 | 2027-08-06 | 학회 | ICML 2027 | Rio de Janeiro · Riocentro | https://icml.cc/ |
| 2027-09-27 | 2027-10-01 | 학회 | IROS 2027 | Florence · Fortezza da Basso | https://2027.ieee-iros.org/ |

`종류` is one of `학회` (the conference itself), `마감` (a submission
deadline — abstract, paper, rebuttal, camera-ready) and `발표` (a decision or
an accepted-paper list going out). `장소` may be empty; a deadline's is its
time zone. `출처` is the official page the date was read from.

## Hosts to allow

The hosts the routine needs and the environment's network allowlist does not
let it reach — a venue's site it was refused, or the next edition's site it
will need once the current edition ends. The routine keeps this list: it adds
a host the week it finds one and drops it the week the host answers. A host
listed here is the operator's to add (`scouting/SETUP.md` §5-1); until then,
that venue's dates wait.

| 주소 | 학회 | 이유 | 처음 본 날 |
|---|---|---|---|
