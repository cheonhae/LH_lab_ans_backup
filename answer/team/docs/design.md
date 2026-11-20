> [가상 자료] 이 자료의 기관·인물·지구·업체·수치·연락처는 모두 실습용 가상 정보입니다. 실제 사실이 아니며 실무에 사용할 수 없습니다.

# 설계 메모 — 시연용 조(행정) 민원대장 확인기

> `/prd-build plan`이 team_plan과 함께 작성. 목적은 하나 — **두 사람이 같은 파일을 동시에 고치지 않게** 경계를 정하는 것.

## 1. 파일 경계

| 역할 | 담당 파일 (이 사람만 고친다) | 읽기만 하는 파일 |
|---|---|---|
| ① 통합·화면 | `scripts/main.py`, `README.md`, `docs/demo_script.md` | ②·③의 파일, `data/` |
| ② 기능 A | `scripts/notice_version.py` | `data/` |
| ③ 기능 B | `scripts/reply_deadline.py` | `data/` |
| ④ 검증·데이터 | `data/team_sample.csv`, `data/notice_dates.csv`, `tests/acceptance.md`, `tests/run_acceptance.py` | ②·③의 파일 |

`CLAUDE.md` 팀 규칙의 '파일 분담' 표도 이 표와 같게 맞췄습니다.

## 2. 데이터 형식

- 파일: `data/team_sample.csv` (가상, UTF-8 BOM, 첫 줄 = 열 이름, 20행)
- 열: 접수번호 | 문자 | T-01 · 접수일 | 날짜 | YYYY-MM-DD · 신청방법 | 문자 | 콜센터·온라인·방문 · 민원유형 | 문자 · 적용공고 | 문자 | v1·v2·v3(빈 칸 가능) · 처리상태 | 문자 | 접수·처리중·답변완료
- 게시일 기준표: `data/notice_dates.csv` — 버전 | 게시일 | 출처(개인 레포 수치 대장 행 번호)
- 일부러 넣은 함정: ④만 미리 앎 — 수용 기준표 AC4에 반영

## 3. 경계 (기능끼리 주고받는 것)

| 보내는 쪽 | 받는 쪽 | 주고받는 것 | 형식 |
|---|---|---|---|
| ② 기능 A | ① 통합 | 행별 대조 결과 | `check_versions(rows, posts)` → dict 목록(row·id·day·recorded·base·status·reason), `load_posts(path)` |
| ③ 기능 B | ① 통합 | 미답변 행별 기한 결과 | `check_deadlines(rows, as_of, days=7)` → dict 목록(row·id·day·status·due·overdue·reason) |
| ④ 검증 | 모두 | 수용 기준 결과 | `python tests/run_acceptance.py` → 표 + 끝 코드 |

## 4. 실행 방법

- `python scripts/main.py data/team_sample.csv` (기준일 바꾸기: `--as-of 2026-11-20`, 결과 CSV: `--out 결과.csv`)
- 수용 기준 확인: `python tests/run_acceptance.py`
