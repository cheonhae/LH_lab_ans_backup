# -*- coding: utf-8 -*-
"""③ 기능 B — 미답변 민원 답변 기한 확인 (담당: ③ 기능 B, docs/design.md 1절)

check_deadlines(rows, as_of, days=7) → 미답변(접수·처리중) 행마다 dict(row, id, day, status, due, overdue, reason)
- 답변 기한 = 접수일 + days일(달력 일수, team_decisions 가정 4). 기한 < 기준일이면 '기한 지남'.
  기한 = 기준일(기한 당일)은 지나지 않은 것으로 본다(경계).
- 접수일이 표준이 아니거나 달력에 없으면 '접수일 확인 필요'로 두고 기한을 계산하지 않는다.
- 처리상태의 띄어쓰기는 무시한다('처리 중' = 처리중).
- 기한이 지났다는 표시는 안내일 뿐, 처리 지연 여부 판단은 담당 검토 후 확정한다.
표준 라이브러리만 쓴다.
"""
import datetime
import re

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
OPEN_STATES = ("접수", "처리중")


def _day(raw):
    raw = (raw or "").strip()
    if not DATE_RE.match(raw):
        return None, f"비표준 접수일 표기 '{raw}'"
    try:
        return datetime.date.fromisoformat(raw), ""
    except ValueError:
        return None, f"달력에 없는 날짜 '{raw}'"


def check_deadlines(rows, as_of, days=7):
    out = []
    for i, r in enumerate(rows, start=2):
        state = (r.get("처리상태") or "").replace(" ", "")  # '처리 중'처럼 띄어 쓴 표기도 같은 상태로 본다(교차 검증 이슈 #9 수정)
        if state not in OPEN_STATES:
            continue
        day, why = _day(r.get("접수일"))
        item = {"row": i, "id": r.get("접수번호", ""), "day": (r.get("접수일") or "").strip(), "status": state}
        if day is None:
            item.update(due="", overdue=None, reason=why)
        else:
            due = day + datetime.timedelta(days=days)
            item.update(due=due.isoformat(), overdue=due < as_of,
                        reason=f"기한 {due.isoformat()} < 기준일 {as_of.isoformat()}" if due < as_of else "")
        out.append(item)
    return out
