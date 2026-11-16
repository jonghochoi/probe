# EVENTS — Conference and Submission Dates

> **Owns** the dates the reading site's first screen counts down to — the
> conferences this project follows and their submission milestones. Human-owned
> like the rest of `context/`: a row is added or corrected here and nowhere
> else. Read by `site/builder/events.py`; no agent track reads or writes it.

Each row is one date or one span. A row is entered only once its official
site states the date; a date known only from an aggregator waits. The site
prints the rows whose end has not passed, nearest first, so a past row may
stay or go.

| 시작 | 끝 | 종류 | 이름 | 장소 | 출처 |
|---|---|---|---|---|---|
| 2026-12-04 | 2026-12-04 | 마감 | RSS 2027 초록 마감 | AoE | https://roboticsconference.org/ |
| 2026-12-06 | 2026-12-09 | 학회 | Humanoids 2026 | Santa Clara | https://2026.ieee-humanoids.org/ |
| 2026-12-06 | 2026-12-12 | 학회 | NeurIPS 2026 | Sydney | https://neurips.cc/ |
| 2027-01-31 | 2027-01-31 | 발표 | ICRA 2027 결과 발표 | | https://2027.ieee-icra.org/ |
| 2027-02-05 | 2027-02-05 | 발표 | RSS 2027 1단계 결과 | | https://roboticsconference.org/ |
| 2027-05-24 | 2027-05-28 | 학회 | ICRA 2027 | Seoul · COEX | https://2027.ieee-icra.org/ |
| 2027-07-06 | 2027-07-11 | 학회 | RSS 2027 | Athens | https://roboticsconference.org/ |

`종류` is one of `학회` (the conference itself), `마감` (a submission
deadline — abstract, paper, rebuttal, camera-ready) and `발표` (a decision or
an accepted-paper list going out). `장소` may be empty; a deadline's is its
time zone. `출처` is the official page the date was read from.
