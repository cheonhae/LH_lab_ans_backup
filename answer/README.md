> [가상 자료] 이 자료의 기관·인물·지구·업체·수치·연락처는 모두 실습용 가상 정보입니다. 실제 사실이 아니며 실무에 사용할 수 없습니다.

# answer/ — 행정(G) 강사 정답 폴더

| 경로 | 내용 |
|---|---|
| `m3/ledger_정정전.csv`, `m3/ledger_정정후.csv` | M3 수치 대장 정답 2벌(정정 메모 반영 전·후) |
| `m3/상급_추가정정메모.md` | M3 상급 분기용 추가 정정 메모(현장 배부) |
| `m4/` | 레포 경로 그대로: `CLAUDE.md`, `ledger/ledger.csv`(week2 항목 추가), `outputs/m4/*`, `scripts/*`, `rules/*` |
| `skill_completed/admin-verify/SKILL.md` | Skill 완성본(3·4절 채움) |
| `rerun_checklist.md` | M4 규칙 점검표(채점 기준) |
| `m5/` | M5 개인 PRD 모의 실행 결과(직접 입력판) — 민원대장 적용공고 확인기. 교육생에게 줄 파일과 강사 참고 파일은 `m5/README_보조인력.md`, 진행 순서는 `m5/_진행기록.md` |
| `team/` | M6 팀 프로젝트 모의 실행 결과(진도 도구 `prd-build`판) — 같은 PRD를 팀판으로 넓힘. 진행 순서는 `team/_진행기록.md` |

- M1~M3 모범 산출물은 `../backup/m2_start`·`m3_start`·`m4_start`에 있음.
- M5 실행 확인(`m5/`에서): `python scripts/m5_notice_check.py data/m5_sample.csv` → 일치 10 · 불일치 4 · 접수일 확인 필요 1.
- 팀 실행 확인(`team/`에서): `python tests/run_acceptance.py` → AC1~AC6 통과, 실패 0건. 두 결과물 모두 클라우드 세션 밖에서 만든 모의 실행입니다(세션 동작·소요 시간은 D-7 실측).
