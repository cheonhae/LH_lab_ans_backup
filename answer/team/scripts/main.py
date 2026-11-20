# -*- coding: utf-8 -*-
"""① 통합 — 민원대장 확인기 (담당: ① 통합·화면, docs/design.md 1절)

실행: python scripts/main.py data/team_sample.csv [--dates data/notice_dates.csv] [--as-of 2026-11-13] [--days 7]
      [--out 결과.csv]   (--out을 줄 때만 행별 결과 CSV를 쓴다)

② 적용공고 대조(scripts/notice_version.py)와 ③ 답변 기한 확인(scripts/reply_deadline.py)을 한 번에 돌려
요약을 보여 주고, --out을 주면 행별 결과를 CSV(UTF-8 BOM)로 남긴다. 원본 CSV는 읽기만 한다. 외부로 보내지 않는다.
"""
import argparse
import csv
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import notice_version as nv  # noqa: E402  ② 기능 A
import reply_deadline as rd  # noqa: E402  ③ 기능 B


def read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def run(csv_path, dates_path, as_of, days):
    rows = read_rows(csv_path)
    if not rows:
        return rows, [], []
    return rows, nv.check_versions(rows, nv.load_posts(dates_path)), rd.check_deadlines(rows, as_of, days)


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="민원대장 확인기(적용공고 대조 + 답변 기한)")
    ap.add_argument("csv")
    ap.add_argument("--dates", default="data/notice_dates.csv")
    ap.add_argument("--as-of", default="2026-11-13", help="답변 기한을 따질 기준일(가정 5: 주간 보고일)")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--out", default="", help="행별 결과 CSV 경로(주지 않으면 화면에만 보여 줌)")
    a = ap.parse_args(argv)
    as_of = datetime.date.fromisoformat(a.as_of)

    rows, ver, dl = run(a.csv, a.dates, as_of, a.days)
    if not rows:
        print("행이 없습니다 — 민원대장 파일에 데이터 행이 있는지 확인하세요.")
        return 0
    need = [x for x in ver if x["status"] == "접수일 확인 필요"]
    bad = [x for x in ver if x["status"] == "불일치"]
    by_ver = {}
    for x in ver:
        if x["base"]:
            by_ver[x["base"]] = by_ver.get(x["base"], 0) + 1
    late = [x for x in dl if x["overdue"]]

    print(f"전체 {len(rows)}행 · 접수일 확인 필요 {len(need)}")
    print(f"[적용공고] 대조 {len(ver) - len(need)}행 · 일치 {len(ver) - len(need) - len(bad)} · 불일치 {len(bad)}")
    print("[적용공고] 기준 공고별: " + " · ".join(f"{v} {by_ver.get(v, 0)}" for v in sorted(by_ver)))
    print(f"[답변 기한] 기준일 {as_of.isoformat()} · 기한 {a.days}일 · 미답변 {len([x for x in dl if x['overdue'] is not None])} · 기한 지남 {len(late)}")
    for x in need:
        print(f"- {x['row']}행 {x['id']} 접수일 확인 필요: {x['reason']}")
    for x in bad:
        print(f"- {x['row']}행 {x['id']} 적용공고 불일치: {x['reason']}")
    for x in late:
        print(f"- {x['row']}행 {x['id']} 답변 기한 지남({x['status']}): {x['reason']}")

    if not a.out:
        print("적용 공고와 처리 지연 판단은 담당 검토 후 확정합니다.")
        return 0
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    due = {x["id"]: x for x in dl}
    with open(out, "w", encoding="utf-8-sig", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["원본행", "접수번호", "접수일", "기록 적용공고", "기준 공고", "적용공고 판정", "답변 기한", "기한 판정"])
        for x in ver:
            d = due.get(x["id"])
            judge = "" if d is None else ("접수일 확인 필요" if d["overdue"] is None else ("기한 지남" if d["overdue"] else "기한 안"))
            w.writerow([x["row"], x["id"], x["day"], x["recorded"], x["base"], x["status"], (d or {}).get("due", ""), judge])
    print(f"결과 파일: {out.as_posix()}")
    print("적용 공고와 처리 지연 판단은 담당 검토 후 확정합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
