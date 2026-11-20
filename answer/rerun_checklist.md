> [가상 자료] 이 자료의 기관·인물·지구·업체·수치·연락처는 모두 실습용 가상 정보입니다. 실제 사실이 아니며 실무에 사용할 수 없습니다.

# M4 규칙 점검표(강사용 채점 기준) — 행정

| # | 확인 항목 | 기대 결과 | 확인 위치 |
|---|---|---|---|
| 0 | 흐름 | CLAUDE.md·Skill 정리 PR을 병합한 뒤 새 세션에서 재실행, CLAUDE.md 수정 PR이 동시에 두 개 열리지 않음 | PR 목록 |
| 1 | 정정 후 값 사용 | 2차 정정공고 게시일 2026. 11. 4.(수)([11]), '11. 5.' 없음 | outputs/m4/minutes.md, evidence.md |
| 2 | 잡담 제외 | [09] 날씨·감기 내용 없음 | minutes.md |
| 3 | 개인정보 제외 | 동·호수(2동 301호)·휴대전화 번호 일부 없음 | minutes.md, evidence.md |
| 4 | 근거 없는 단정 | "당첨 확실" 문장 없음 | minutes.md |
| 5 | 중복 제외 | 중복 1행 → excluded_rows.csv에 사유와 함께 | outputs/m4/excluded_rows.csv |
| 6 | 새 함정 | 신청방법 '전화'·'홈페이지'·'내방' 3행 정규화 후 포함, run_log 수정 행 기록 | outputs/m4/run_log.md |
| 7 | 집계 결과 | 유효 민원 41건, 자격·소득 18건, 미처리 14건 | outputs/m4/summary.csv |
| 8 | 대장 갱신 | FAQ 개정본 게시일 2026-11-11 → 2026-11-13, 2주 차 항목 추가 | ledger/ledger.csv |
| 9 | 영향 목록 먼저 | impact_list에 회의록 5절 FAQ 행 | outputs/m4/impact_list.md |
| 10 | CLAUDE.md 보강 | 신청방법 대응표 규칙 문장이 2절에 추가됨 | CLAUDE.md |
| 11 | Skill | admin-verify 3·4절 채움, 호출 시험 기록 | .claude/skills/admin-verify/SKILL.md |
