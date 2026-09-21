# Changelog

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

[0.1.0]: https://github.com/ozplayground/task-driven-harness/releases/tag/v0.1.0
