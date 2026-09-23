# Changelog

## [0.2.0] - 2026-09-24

### Added

- 에이전트 14종. task 종류 하나에 에이전트 하나. 만드는 쪽 `researcher`, `architect`, `spec-writer`, `ux-designer`, `contract-designer`, `security`, `backend-developer`, `frontend-developer`, `devops`, `verifier`. 판정하는 쪽 `critic`, `doc-reviewer`, `code-reviewer`. 조사자 `investigator`. `executor`와 `reviewer`는 없앰
- `task-execution` 스킬 — 산출물을 만드는 에이전트 전부가 로드하는 공통 규칙. 시킨 것만, 워크트리와 소유 경로, 결정 레벨, 진행 중 보고서 갱신, 재개, 발견한 버그, 조사 위임, 재작업, 보고, 멈춰야 하는 신호
- `humanizer` 스킬 — 문서를 사람이 쓴 것처럼 쓰는 규칙. 문장, 넣지 않는 것, 구조, 문서 종류별 차이, 쓴 뒤 점검. 문서를 쓰는 에이전트 8개와 doc-reviewer·critic이 로드하고, doc-reviewer는 어긋나면 finding
- `security-compliance` 스킬과 `security` 템플릿(`docs/design/security.md`, 요건 번호 `S-nn`) — 데이터 분류, 적용 규제, 위협 모델, 보안 요건, 설계 강제 항목, 검증 방법. 그리고 아키텍처·계약·데이터 모델·코드·CI의 보안 검토 항목
- 문서 템플릿 31종 (`design-docs/templates/`) — 절마다 작성 안내와 작성 예가 있는 사람이 쓰는 문서 틀. FSD마다 하나 쓰는 설계 문서(`design`, architect)와 라이브러리·SDK 공개 인터페이스 정의서(`interface`) 포함. `docs/` 문서에는 YAML 머리말도 작성자·작성일·버전·검토자 표도 두지 않는다. 문서 첫머리에는 제목과 참고 문서만
- `docs/`와 `_tasks/`의 경계 — `docs/`는 결정된 것을 사람에게 보고·공유하는 문서. 진행 상태, 라운드, 지적 대응, task ID·run 이름·에이전트 이름·finding 번호, 작업 요약은 넣지 않는다. 제목은 "주제 + 문서 종류" 명사구, 추적 ID는 표와 절 제목에만, 다른 문서 언급은 상대 경로 링크. doc-reviewer가 어긋나면 finding
- 문서 순서 — PRD → (UX) → FSD → 설계 → API 명세·인터페이스·데이터 모델 → (디자인 시스템) → 구현. 계약은 설계 문서에서 도출된다
- `ux-design` 스킬 — UX 설계(역할·작업, 정보 구조, 내비게이션, 화면 목록, 흐름, 레이아웃 골격, 상호작용, 상태, 접근성)와 디자인 시스템. 문서 순서는 PRD → UX 설계 → FSD → 디자인 시스템 → 프론트엔드
- 결정 레벨 — L1 구조(architect), L2 명세·설계(spec-writer, ux-designer, contract-designer, security), L3 구현(구현 에이전트). 구현 에이전트는 L3만 정하고 L1·L2 결함은 "막힌 것"으로 올린다
- `install.sh` — 대상 프로젝트에 에이전트·스킬 복사, `CLAUDE.md` 하네스 절 삽입·갱신, `settings.json`과 `.mcp.json` 합치기, `.gitignore`. 사용자가 경로를 말하면 리더가 돌린다
- `CLAUDE.template.md` — 설치 대상 프로젝트에 들어가는 run 규칙
- `.mcp.json` — context7을 플러그인이 아니라 MCP 서버로 등록. 에이전트 `tools`는 `mcp__context7`

### Changed

- 원장 — 리뷰·비평·재작업·보안 검토는 상태가 아니라 task다. 리더가 `add`로 만들고 `--target`으로 대상을, 재작업은 `--fixes`로 고칠 finding을 가리킨다. `kind` 대신 `agent`. 상태는 `pending / ready / running / done / failed` 다섯. 고치기로 한 finding이 open이면 재작업은 done이 안 된다. `reopen` 삭제, `brief` 추가(브리프에 옮길 필드와 의존 task 경로)
- `orchestration` — 리더가 task와 task를 잇는다. 산출물이 나오면 비평·리뷰 task를, 지적이 나오면 재작업 task를 만들고, 뒤 task는 리뷰 task에 의존을 건다. 문서는 critic 비평과 doc-reviewer 판정을 통과한 뒤에만 구현에 들어간다. 무인 모드에서 결정은 사용자에게 돌리지 않고 조사 → architect → critic → 리더 순으로 정한다. 재작업 상한·inconclusive·failed 처리는 리더가 한다. 동시에 도는 서브에이전트는 5개까지. 브리프의 SKILLS 절과 종류→스킬 표 삭제. round 2 리뷰와 재작업은 원래 인스턴스를 재개한다
- `critic` — 문서가 나올 때마다 내용을 비평한다. 과잉 설계, 불필요한 기술, 근거 부족, 누락, 모순, 요구 대비. `direction-review`에 문서 종류별 확인 항목
- 리뷰 — `doc-reviewer`는 템플릿 절·입력 문서 항목·참조 ID·결정 레벨을 대조하고, `code-reviewer`는 테스트·빌드 실행과 3-dot diff, 계약 대조, 경계면을 본다. 내용 비평은 하지 않는다
- `git-workflow` — 커밋 한 줄 요약은 50자 안, 무엇이 바뀌었는지만. 경위·ID 나열 금지. GitFlow(`main`·`develop`·`feature/<run>`·`release/<version>`·`hotfix/<run>`)와 task별 worktree(`.worktrees/<task>`, `feature/<run>/<task>`). 만드는 에이전트는 자기 worktree에서만 커밋하고 머지·푸시는 리더가 한다. 재작업은 대상 task의 worktree를 그대로 쓴다. run 끝에 `gh pr create` → `gh pr checks --watch` → `gh pr merge --merge`. 커밋 메시지에 `Task: <run>/<task>`. 릴리스·핫픽스·롤백 절차
- `unattended` — 사용자에게 돌리는 대체 규칙을 없앰. 항상 멈추는 것은 배포·외부 전송뿐
- `design-docs` — 문서 목록의 쓰는 쪽을 에이전트 이름으로. `security` 행 추가. 결정 레벨 표. `decided_by`의 `executor`를 `developer`로
- `architecture`, `research`, `interface-contract`, `completion-evidence`, `plan-and-check`, `spec-authoring` — 형식 블록을 템플릿 참조로. 기술 스택은 계층마다 버전과 고른 이유, 결정 기록 번호를 적는다
- 이 저장소의 `CLAUDE.md` — 하네스 소스를 고칠 때는 run 규칙을 적용하지 않는다
- `.claude/settings.json` — 마켓플레이스(claude-plugins-official, ponytail)와 플러그인(`ponytail@ponytail`, `frontend-design@claude-plugins-official`) 설정. 설치 스크립트가 대상 프로젝트에 합친다
- `README.md` — 에이전트 14종·스킬 20종 표, 원장 명령, 설치 절, 디렉터리 구조

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

[0.2.0]: https://github.com/ozplayground/task-driven-harness/releases/tag/v0.2.0
[0.1.1]: https://github.com/ozplayground/task-driven-harness/releases/tag/v0.1.1
[0.1.0]: https://github.com/ozplayground/task-driven-harness/releases/tag/v0.1.0
