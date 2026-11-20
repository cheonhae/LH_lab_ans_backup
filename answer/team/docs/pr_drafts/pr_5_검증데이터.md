> [가상 자료] 이 자료의 기관·인물·지구·업체·수치·연락처는 모두 실습용 가상 정보입니다. 실제 사실이 아니며 실무에 사용할 수 없습니다.

# PR #5 — [팀-검증데이터] 표본·기준표·수용 기준(이슈 #4)

> `/prd-build ship`이 만든 본문 초안 — 사람이 PR 본문에 붙여 넣고 Ready for review → 리뷰 짝 승인 → 리뷰한 조원이 Merge. 리뷰 짝 ③ 승인.

```text
Closes #4

## 목적
- 표본 데이터·게시일 기준표·수용 기준표·확인 스크립트

## 범위
- 한 것: data/team_sample.csv, data/notice_dates.csv, tests/acceptance.md, tests/run_acceptance.py
- 안 한 것: ②·③·①의 기능 파일

## 검증 결과 (python tests/run_acceptance.py)
| 수용 기준 | 결과 | 근거 |
|---|---|---|
| AC1~AC4·AC6 | 미실행 | ②·③·① 파일이 아직 없음(병합 순서 ④가 먼저) |
| AC5 | 미실행 | scripts/에 아직 파일 없음 |

## 미실행 확인
- 병합 전이라 다른 역할 파일이 없는 기준은 미실행 — 이유는 표에 적음

## 위험
- 없음 — 다른 역할 파일을 고치지 않음

## 되돌리는 방법
- 병합 뒤 문제가 생기면 이 PR 화면의 Revert로 되돌립니다.
```
