# Changelog

## [0.1.1] - 2026-09-21

### Fixed

- `design-docs` — 요구사항과 기능 명세를 `docs/spec/` 한 칸에 묶던 것을 둘로 나눔. PRD는 요구사항 정의서(`docs/prd/<제품>.md`, 요구사항마다 `REQ-nn`), FSD는 기능 명세서로 요구사항마다 파일 하나(`docs/fsd/<제품>/REQ-nn-<주제>.md`), 안에서 요구사항을 기능(`FN-nn`)으로 나누고 기능마다 상세. 두 문서의 골격과 ID 체계(`REQ`·`NFR`·`FN`·`SCR`·`BR`·`MSG`) 추가. `docs/spec/` 폐지
- `spec-authoring` — PRD 절차와 FSD 절차(요구사항 → 기능 분해 → 기능별 상세)를 나누고 FSD 완성도 점검 추가
- `orchestration` — 골격이 있는 문서 task의 완료 기준에 "골격 절 전부 충족, 추적 표 누락 0"을 붙이는 규칙. PRD와 FSD는 별도 task, FSD는 REQ마다 하나. 받은 문서 판정표를 PRD/FSD 기준으로
- `critic`, `direction-review`, `frontend-work`, `README.md` — `FR` 예시를 `REQ`·`SCR` 기준으로

## [0.1.0] - 2026-09-21

초기 버전.

### Added

- `orchestration` 스킬 — 리더(메인 세션)가 쓰는 절차. 요청 분석, task 분할 계획, critic 비판과 사용자 승인, 서브에이전트 분배, 산출물 기반 완료 판정, 재작업 루프(2회 상한), 중단 재개 3경로. 참고 문서 4종(`intake`, `split`, `dispatch`, `ledger-format`)
- 원장 스크립트 `ledger.py` — task 상태 전이 강제, 동시 실행 task 간 소유 경로 겹침 검사, 승인 게이트. 파이썬 표준 라이브러리만 사용
- 에이전트 5종 — `executor`, `reviewer`, `critic`, `architect`, `investigator`
- 서브에이전트 규율 스킬 6종 — `design-docs`, `plan-and-check`, `completion-evidence`, `verify-loop`, `direction-review`, `architecture`
- 작업 스킬 6종 — `spec-authoring`, `interface-contract`, `research`, `backend-work`, `frontend-work`, `debugging`
- 선택 스킬 3종 — `git-workflow`, `ci-cd`, `bugfix-followup`
- 무인 모드 스킬 `unattended`
- 운영 규약 `CLAUDE.md`

[0.1.1]: https://github.com/ozplayground/task-driven-harness/releases/tag/v0.1.1
[0.1.0]: https://github.com/ozplayground/task-driven-harness/releases/tag/v0.1.0
