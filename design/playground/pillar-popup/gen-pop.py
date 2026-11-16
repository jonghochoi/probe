"""Data for the pillar-popup drafts: each axis's names, a draft Korean
description and its decision titles, written as assets/plpop-data.js.

usage: PROBE_REPO=<checkout> python3 gen-pop.py <built-site-dir>
"""
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(os.environ.get("PROBE_REPO", "/home/user/probe"))
sys.path.insert(0, str(REPO / "site"))
from builder.corpus import PILLAR_LABELS, PILLAR_NAMES  # noqa: E402

OUT = Path(sys.argv[1])
# Draft descriptions — the owner writes the real ones in each pillar file.
KO_DRAFT = {
    "P0": "손 조작 정책을 배우고 재는 데 쓰는 데이터와 벤치마크를 다룹니다. 로봇 시연, 사람 1인칭 영상, 사람→로봇 변환 데이터, 촉각·힘 데이터와 평가 환경을 모으고, 각각 무엇을 담았는지(감각 종류, 규모, 손 자유도, 라이선스)를 따집니다.",
    "P1": "행동을 내는 디코더를 둘 이상의 전문가로 나누는 방식을 다룹니다. 몸과 손이라는 몸의 이음매, 느린 계획과 빠른 반응이라는 시간의 이음매에서 무엇을 나누고 무엇을 공유하는지가 중심입니다.",
    "P2": "감각이 정책에 닿기 전에 일어나는 일을 다룹니다. 여러 카메라의 공간 정합, 손가락별 접촉을 어느 손가락에 귀속할지, 그리고 관측 인코더를 무엇으로 쓸지가 중심입니다.",
    "P3": "다음 상태를 예측하는 모델을 정책 스택에 들이는 방식을 다룹니다. 그 모델의 역할, 정책과 묶는 방법, 무엇을 예측할지(예측 공간), 무엇에 조건을 걸지가 중심입니다.",
    "P4": "배포 전에 정하는 것들을 다룹니다. 어떤 모델 계보에서 출발할지, 어떤 코퍼스로 미리 배울지, 어떤 순서로 학습할지, 그리고 새 과제와 새 손에 옮길 때 그 선택을 지키는 비용이 중심입니다.",
}
data = {}
for code in PILLAR_NAMES:
    text = (REPO / "context" / f"{code}.md").read_text()
    decs = [{"id": m.group(1), "title": m.group(2), "open": bool(m.group(3))}
            for m in re.finditer(r"^#### \[(D\w{3})\] (.+?) \(P\d\)( — \*\*OPEN\*\*)?$", text, re.M)]
    data[code] = {"label": PILLAR_LABELS[code], "name": PILLAR_NAMES[code],
                  "desc": KO_DRAFT[code], "decisions": decs}
(OUT / "assets" / "plpop-data.js").write_text(
    "window.PL_POP = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
print("popup data:", ", ".join(f"{k} 결정 {len(v['decisions'])}" for k, v in data.items()))
