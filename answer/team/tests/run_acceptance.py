# -*- coding: utf-8 -*-
"""수용 기준 확인 스크립트 — PR마다 실행합니다(이 수업에서 CI 역할).

실행: python tests/run_acceptance.py
결과: 수용 기준마다 통과 / 실패 / 미실행과 이유를 표로 보여 줍니다. 실패가 하나라도 있으면 끝 코드 1.

④ 검증·데이터 담당이 tests/acceptance.md 3절의 AC를 아래 CHECKS에 하나씩 옮겼습니다.
- 기대값은 도구를 돌리기 전에 표본을 보고 손으로 센 값입니다(acceptance.md 2절). 도구 결과를 기대값으로 옮겨 적지 않습니다.
- 아직 만들 수 없는 확인은 지우지 말고 None(미실행)을 돌려주고 이유를 적습니다.
- 표준 라이브러리만 씁니다(추가 설치 없음).
"""
import csv
import datetime
import importlib
import io
import pathlib
import sys
from contextlib import redirect_stdout

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "team_sample.csv"
DATES = ROOT / "data" / "notice_dates.csv"
AS_OF = datetime.date(2026, 11, 13)   # 가정 5: 주간 보고일
sys.path.insert(0, str(ROOT / "scripts"))

# ---- 2절 기대값(손으로 셈) ----------------------------------------------------
EXP_ROWS, EXP_NEED = 20, 1
EXP_MISMATCH = {"T-04", "T-10", "T-14", "T-17"}
EXP_BY_VER = {"v1": 2, "v2": 6, "v3": 11}
EXP_OVERDUE = {"T-02", "T-05", "T-07", "T-09", "T-11"}
TRAP_ID, BOUNDARY_ID = "T-12", "T-13"


def load_rows():
    with open(SAMPLE, encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def _mod(name):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        return None


# ---- 수용 기준 ------------------------------------------------------------
# 각 함수는 (결과, 이유)를 돌려준다. 결과 = True(통과) / False(실패) / None(미실행)

def ac1_sample_matches_expected():
    """AC1 표본을 넣으면 전체 행 수와 접수일 확인 필요 수가 2절 기대값과 같다"""
    nv = _mod("notice_version")
    if nv is None:
        return None, "scripts/notice_version.py 아직 없음(② 병합 전)"
    rows = load_rows()
    need = [x for x in nv.check_versions(rows, nv.load_posts(DATES)) if x["status"] == "접수일 확인 필요"]
    ok = len(rows) == EXP_ROWS and len(need) == EXP_NEED
    return ok, f"기대 {EXP_ROWS}행·확인 필요 {EXP_NEED} / 실제 {len(rows)}행·{len(need)}"


def ac2_version_check():
    """AC2 ② 적용공고 대조: 불일치 4건(T-04·T-10·T-14·T-17), 기준 공고별 v1 2 · v2 6 · v3 11"""
    nv = _mod("notice_version")
    if nv is None:
        return None, "scripts/notice_version.py 아직 없음(② 병합 전)"
    res = nv.check_versions(load_rows(), nv.load_posts(DATES))
    bad = {x["id"] for x in res if x["status"] == "불일치"}
    by = {}
    for x in res:
        if x["base"]:
            by[x["base"]] = by.get(x["base"], 0) + 1
    ok = bad == EXP_MISMATCH and by == EXP_BY_VER
    return ok, f"불일치 {sorted(bad)} · 기준 공고별 {by}"


def ac3_reply_deadline():
    """AC3 ③ 답변 기한: 기준일 2026-11-13·7일 → 기한 지남 5건, 기한 당일 T-13은 제외, '처리 중' 띄어쓰기도 미답변"""
    rd = _mod("reply_deadline")
    if rd is None:
        return None, "scripts/reply_deadline.py 아직 없음(③ 병합 전)"
    res = rd.check_deadlines(load_rows(), AS_OF, 7)
    late = {x["id"] for x in res if x["overdue"]}
    spaced = rd.check_deadlines([{"접수번호": "B-01", "접수일": "2026-11-02", "처리상태": "처리 중"}], AS_OF, 7)
    ok = late == EXP_OVERDUE and BOUNDARY_ID not in late and len(spaced) == 1 and spaced[0]["overdue"]
    return ok, f"기한 지남 {sorted(late)} · 경계 {BOUNDARY_ID} 제외 · 띄어쓰기 상태 {'잡힘' if spaced else '빠짐'}"


def ac4_trap_row():
    """AC4 일부러 넣은 함정 행(T-12 비표준 접수일)을 사유와 함께 따로 보여 주고, 대조·기한 계산에 넣지 않는다"""
    nv, rd = _mod("notice_version"), _mod("reply_deadline")
    if nv is None or rd is None:
        return None, "② 또는 ③ 파일 아직 없음"
    rows = load_rows()
    v = [x for x in nv.check_versions(rows, nv.load_posts(DATES)) if x["id"] == TRAP_ID]
    d = [x for x in rd.check_deadlines(rows, AS_OF, 7) if x["id"] == TRAP_ID]
    ok = bool(v) and v[0]["status"] == "접수일 확인 필요" and "비표준" in v[0]["reason"] and bool(d) and d[0]["overdue"] is None
    return ok, f"{TRAP_ID}: {v[0]['reason'] if v else '없음'}"


def ac5_no_external_send():
    """AC5 데이터를 외부로 보내지 않는다 — 결과물 파일에 외부 주소가 없는지 본다."""
    targets = [p for p in (ROOT / "tools").rglob("*") if p.is_file()] + \
              [p for p in (ROOT / "scripts").rglob("*") if p.is_file() and p.suffix == ".py"]
    hits = []
    for p in targets:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for word in ("http://", "https://", "fetch(", "XML" + "HttpRequest", "requests."):   # 문자열을 나눠 둔다(자료 금지어 검사와 겹치지 않게)
            if word in text:
                hits.append(f"{p.relative_to(ROOT)}: {word}")
    if not targets:
        return None, "tools/·scripts/에 아직 파일 없음"
    return not hits, "외부 전송 흔적 없음" if not hits else "; ".join(hits[:3])


def ac6_no_final_judgement():
    """AC6 판단을 확정하지 않는다 — 통합 출력 끝에 '담당 검토 후 확정' 문구"""
    main = _mod("main")
    if main is None:
        return None, "scripts/main.py 아직 없음(① 병합 전)"
    buf = io.StringIO()
    with redirect_stdout(buf):
        main.main([str(SAMPLE), "--dates", str(DATES)])
    text = buf.getvalue()
    return "담당 검토 후 확정" in text, "출력에 '담당 검토 후 확정' 있음" if "담당 검토 후 확정" in text else "문구 없음"


CHECKS = [
    ("AC1", ac1_sample_matches_expected),
    ("AC2", ac2_version_check),
    ("AC3", ac3_reply_deadline),
    ("AC4", ac4_trap_row),
    ("AC5", ac5_no_external_send),
    ("AC6", ac6_no_final_judgement),
]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    failed = 0
    print("| 수용 기준 | 결과 | 이유 |\n|---|---|---|")
    for name, fn in CHECKS:
        try:
            ok, why = fn()
        except Exception as e:  # noqa: BLE001 — 확인 중 오류는 실패로 본다
            ok, why = False, f"오류: {e}"
        label = "미실행" if ok is None else ("통과" if ok else "실패")
        failed += ok is False
        print(f"| {name} | {label} | {why} |")
    print(f"\n실패 {failed}건 — PR 본문 '검증 결과'에 이 표를 붙여 넣습니다.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
