# -*- coding: utf-8 -*-
"""M5 민원대장 적용공고 확인기 (가상 자료 실습용, Python 표준 라이브러리만)

실행: python scripts/m5_notice_check.py data/m5_sample.csv
      [--ledger ledger/ledger.csv] [--out outputs/m5/notice_check.csv]

하는 일
- 수치 대장(ledger/ledger.csv)에서 공고 게시일을 읽는다: v1 = 공고 번호 기준일(G-L01), v2 = G-L02, v3 = G-L13.
- 민원마다 접수일 기준으로 그날 유효한 공고(기준 공고)를 계산하고, 대장의 '적용공고' 칸과 대조한다.
  게시일 당일 접수는 새 공고를 적용한다 [가정 — 계획 5절].
- 접수일이 YYYY-MM-DD가 아니면 대조하지 않고 '접수일 확인 필요'로 따로 보여 준다(멈추지 않는다).
- 결과 표를 outputs/m5/notice_check.csv(UTF-8 BOM)에 쓴다. 원본 CSV는 읽기만 한다.
- 적용 공고 판단은 확정하지 않는다 — 담당 검토 후 확정.
"""
import argparse
import csv
import datetime
import pathlib
import re
import sys

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LEDGER_IDS = {"v1": "G-L01", "v2": "G-L02", "v3": "G-L13"}


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def posting_dates(ledger_path):
    """대장에서 공고 버전별 게시일을 읽는다. v1은 공고 번호 행의 기준일을 쓴다."""
    rows = {r["항목ID"]: r for r in read_csv(ledger_path)}
    out = {}
    for ver, lid in LEDGER_IDS.items():
        if lid not in rows:
            raise SystemExit(f"대장에 {lid}({ver} 게시일) 행이 없습니다 — ledger/ledger.csv를 확인하세요")
        r = rows[lid]
        value = r["기준일"] if ver == "v1" else r["값"]
        out[ver] = datetime.date.fromisoformat(value)
    return out


def expected_version(day, posts):
    """접수일에 유효한 공고: 게시일이 접수일 이전·당일인 것 중 가장 늦은 것."""
    valid = [v for v, d in posts.items() if d <= day]
    return max(valid, key=lambda v: posts[v]) if valid else "게시 전"


def check(rows, posts):
    result = []
    for i, r in enumerate(rows, start=2):  # 2 = 머리글 다음 첫 데이터 행(원본 파일 줄 번호)
        raw_day = (r.get("접수일") or "").strip()
        recorded = (r.get("적용공고") or "").strip()
        if not DATE_RE.match(raw_day):
            result.append([i, r.get("접수번호", ""), raw_day, recorded, "", "접수일 확인 필요", f"비표준 접수일 표기 '{raw_day}'"])
            continue
        try:
            day = datetime.date.fromisoformat(raw_day)
        except ValueError:  # 형식은 맞지만 달력에 없는 날짜(예: 11-31) — 자체 검토 발견 사항 1
            result.append([i, r.get("접수번호", ""), raw_day, recorded, "", "접수일 확인 필요", f"달력에 없는 날짜 '{raw_day}'"])
            continue
        base = expected_version(day, posts)
        if recorded == base:
            result.append([i, r["접수번호"], raw_day, recorded, base, "일치", ""])
        else:
            shown = recorded if recorded else "(빈 칸)"
            result.append([i, r["접수번호"], raw_day, shown, base, "불일치", f"기록 {shown} → 기준 {base}"])
    return result


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="민원대장 적용공고 확인기")
    ap.add_argument("csv")
    ap.add_argument("--ledger", default="ledger/ledger.csv")
    ap.add_argument("--out", default="outputs/m5/notice_check.csv")
    a = ap.parse_args()

    rows = read_csv(a.csv)
    if not rows:
        print("행이 없습니다 — 민원대장 파일에 데이터 행이 있는지 확인하세요.")
        return 0
    posts = posting_dates(a.ledger)
    result = check(rows, posts)

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8-sig", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["원본행", "접수번호", "접수일", "기록 적용공고", "기준 공고", "판정", "사유"])
        w.writerows(result)

    n_need = sum(1 for x in result if x[5] == "접수일 확인 필요")
    n_ok = sum(1 for x in result if x[5] == "일치")
    n_bad = sum(1 for x in result if x[5] == "불일치")
    by_ver = {v: sum(1 for x in result if x[4] == v) for v in posts}
    print(f"게시일 기준(대장): " + " · ".join(f"{v} {d.isoformat()}" for v, d in posts.items()))
    print(f"전체 {len(rows)}행 · 대조 {len(rows) - n_need}행 · 일치 {n_ok} · 불일치 {n_bad} · 접수일 확인 필요 {n_need}")
    print("기준 공고별: " + " · ".join(f"{v} {n}" for v, n in by_ver.items()))
    for x in result:
        if x[5] != "일치":
            print(f"- {x[0]}행 {x[1]} {x[5]}: {x[6]}")
    print(f"결과 파일: {out.as_posix()}")
    print("적용 공고 판단은 담당 검토 후 확정합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
