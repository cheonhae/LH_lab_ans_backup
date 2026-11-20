# -*- coding: utf-8 -*-
"""② 기능 A — 적용공고 대조 (담당: ② 기능 A, docs/design.md 1절)

check_versions(rows, posts) → 행마다 dict(row, id, day, recorded, base, status, reason)
- posts: {"v1": date, "v2": date, "v3": date} — data/notice_dates.csv에서 읽는다(load_posts).
- 기준 공고 = 게시일이 접수일 이전·당일인 것 중 가장 늦은 것(게시일 당일 = 새 공고, team_decisions 가정 3).
- 접수일이 YYYY-MM-DD가 아니거나 달력에 없으면 status '접수일 확인 필요'로 두고 대조하지 않는다.
표준 라이브러리만 쓴다.
"""
import csv
import datetime
import re

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_day(raw):
    """접수일 문자열 → (date 또는 None, 사유)"""
    raw = (raw or "").strip()
    if not DATE_RE.match(raw):
        return None, f"비표준 접수일 표기 '{raw}'"
    try:
        return datetime.date.fromisoformat(raw), ""
    except ValueError:
        return None, f"달력에 없는 날짜 '{raw}'"


def load_posts(path):
    with open(path, encoding="utf-8-sig", newline="") as fp:
        return {r["버전"]: datetime.date.fromisoformat(r["게시일"]) for r in csv.DictReader(fp)}


def base_version(day, posts):
    valid = [v for v, d in posts.items() if d <= day]
    return max(valid, key=lambda v: posts[v]) if valid else "게시 전"


def check_versions(rows, posts):
    out = []
    for i, r in enumerate(rows, start=2):  # 원본 파일 줄 번호(1 = 머리글)
        recorded = (r.get("적용공고") or "").strip()
        day, why = parse_day(r.get("접수일"))
        item = {"row": i, "id": r.get("접수번호", ""), "day": (r.get("접수일") or "").strip(), "recorded": recorded}
        if day is None:
            item.update(base="", status="접수일 확인 필요", reason=why)
        else:
            base = base_version(day, posts)
            if recorded == base:
                item.update(base=base, status="일치", reason="")
            else:
                shown = recorded or "(빈 칸)"
                item.update(base=base, status="불일치", reason=f"기록 {shown} → 기준 {base}")
        out.append(item)
    return out
