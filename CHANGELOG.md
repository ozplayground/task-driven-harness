# Changelog

## [0.3.1] - 2026-09-29

0.3.0의 "재작업은 한 번, 두 번째 판정 없음"이 결함을 남긴 채 run을 끝낼 수 있어 되돌림. 막으려던 것은 한 줄 고칠 때마다 비평·리뷰가 다시 도는 판정 반복이고, 고치는 일 자체를 자르는 것이 아니다.

### Changed

- 판정은 문서마다 두 번까지. 1차는 첫 판 전체, 2차는 재작업 뒤 1차 지적의 해소 확인(같은 인스턴스 재개, 새 지적은 회귀·blocker만). 3차는 `ledger.py`가 등록을 거부한다. 2차 뒤 남은 지적은 리더가 같은 에이전트에게 되돌려 보내고 산출물을 직접 대조해 닫는다. 지적은 닫힐 때까지 고친다
- 재작업 task 등록 상한 삭제. 되돌려 보내기는 원래 인스턴스에 `SendMessage`
- 기각(`finding waive`)은 반박이 맞다고 리더가 확인한 지적에만. 안 고쳐진 지적을 넘기는 규칙 삭제. run 보고서 "알고 넘긴 리뷰 지적" 절을 "기각한 리뷰 지적"으로
- 개발이 끝난 뒤 문서를 한 번에 맞추는 정합 task에 비평·리뷰 한 번씩. 문서끼리, 문서와 코드·계약의 정합을 본다
- 지적 번호·비판 번호는 `_tasks/` 안에서만 쓴다. 사용자에게 설명할 때와 `docs/`(run 보고서 포함)에는 내용으로 쓴다. 승인 요청의 비판 요약, run 보고서 템플릿 예시에서 번호와 `_tasks/` 참조 제거
- `docs-lint.py`가 run 보고서(`docs/runs/`)도 검사한다
- critique·review 템플릿에 "2차 확인" 절과 라운드 행 복원. critic·doc-reviewer·code-reviewer·security 정의, `verify-loop`, `direction-review`, `task-execution`, `orchestration`, `dispatch`, `split`, `unattended`, README, `CLAUDE.template.md`에 반영

## [0.3.0] - 2026-09-29

agent-sdk 개발 run(2026-09-24 ~ 09-27)의 운영 피드백 반영. 만드는 일보다 판정하는 일이 아홉 배 많았고, 문서 커밋이 코드 커밋의 네 배였다. 판정 횟수를 기계적으로 묶고, `docs/`와 `_tasks/`의 경계를 스크립트로 강제한다.

### Added

- `design-docs/scripts/docs-lint.py` — `docs/` 경계 검사. task ID, finding·비판 번호, 라운드, 에이전트 이름, `_tasks/` 경로, "재작업·반영" 어휘, 템플릿 안내문 잔재, YAML 머리말, 작성자·버전 표를 위반으로, 깨진 상대 링크를 경고로 낸다. `code` 모드는 문서 참조만 있고 설명이 없는 코드 주석(`# BR-04`, `// FSD §3.2 참조`)을 잡는다
- `ledger.py set <문서 task> done`이 `docs-lint.py`를 자동으로 돌리고 위반이 있으면 done을 거부한다. `--skip-docs-check`는 `--because`와 함께만
- `ledger.py`가 같은 대상에 두 번째 판정 task(에이전트별)와 두 번째 재작업 task의 등록을 거부한다. minor finding은 `--fixes`에 넣을 수 없다
- 원장 전이 `failed → done`(중단 종료)
- `design-docs`에 "정본은 한 곳" 표 — 규칙은 문서 하나에만 적고 나머지는 링크. 옮겨 적으면 doc-reviewer의 major(정본 중복), critic의 모순 항목
- PRD 인수 조건마다 출처 표시 `(원문)` / `(보강)`. 사용자 요구는 원문 조건뿐이고, 보강 조건은 사용자에게 묻지 않고 리더가 정리한다. 추적 표에 인수 조건 열 추가
- 리더가 에이전트 종류마다 첫 호출 뒤 기록에서 정의의 스킬이 실제로 로드됐는지 확인한다
- `task-execution`에 "산출물의 경계" 절 — `docs/`에 작업 기록을 남기지 않고, 코드 주석은 그 자리에서 이해되게 쓴다
- 문서 정합 task — 모든 구현 task가 끝나면 구현 보고서의 "명세에 없어 내가 정한 것"(레벨 2)과 판정의 minor를 문서에 한 번에 옮긴다. 판정을 붙이지 않고 리더가 diff와 `docs-lint.py`로 확인
- 리더 규칙 — 대화 중에는 파일 수정·커밋·푸시를 하지 않고 답만 한다. 에이전트 보고를 사용자에게 옮기기 전에 파일로 확인한다. `add` 전에 `show`로 ID를 확인한다. 재작성 task는 사용자가 요구할 때만

### Changed

- 판정은 문서 첫 판에 critic 비평과 doc-reviewer 리뷰 각 한 번. 전체를 한꺼번에 본다. 재작업은 한 번이고 두 번째 판정은 없다. 리더가 재작업 보고서의 ID별 설명을 파일과 대조해 finding을 닫고, 남은 것은 waive하고 run 보고서 "문제가 있는 것"에 적는다. `verify-loop`, `direction-review`, critic·doc-reviewer·code-reviewer·security 정의, critique·review 템플릿에서 round 2 절차 삭제. "이전 라운드" 절을 "다 봤는가" 절로
- 코드는 테스트·타입 검사·린트 통과가 완료 판정이고 리더가 워크트리에서 직접 돌린다. code-reviewer는 사용자가 요구했을 때, security 검토는 인증·시크릿·외부 호출·개인정보에 닿는 코드일 때만 한 번
- 구현 착수 조건 — "입력 문서의 리뷰가 모두 끝나야"에서 "구조 결정이 확정되고 입력 문서의 첫 판이 `feature/<run>`에 있으면"으로. 의존은 산출물 task에 걸고 판정 task에 걸지 않는다. 산출물 확인 뒤 바로 머지하고 판정은 머지 뒤에 돈다. 판정으로 문서가 바뀌면 구현 task에 `SendMessage`로 알린다
- 결정 기록이 확정되기 전에는 그 결정을 옮겨 적는 하위 문서 task를 던지지 않는다
- 구현 중에는 문서를 고치지 않는다. 계약에 없는 필드·문구·엣지 케이스·수치는 코드와 테스트에서 정하고 보고서에 적는다. "막힌 것"은 구조 결정 공백, 동작 자체의 부재, 문서 간 모순 셋만. `task-execution`, `backend-work`, `frontend-work`, `interface-contract`, `plan-and-check`, backend-developer·contract-designer 정의, `design-docs` 결정 레벨 표
- 형식 지적(링크, 문체, 제목, ID 표기, 볼드·번호 개수, 작업 흔적)은 전부 minor. 재작업 사유가 아니다. doc-reviewer 원칙 8~10을 minor로 내림
- 커밋 메시지의 `Task:`·`Rework:` 꼬리표 삭제. 어느 run·task의 커밋인지는 브랜치 이름과 머지 커밋이 말한다
- 워크트리를 만들면 의존성 설치(선택 의존성 포함)와 기준선 테스트까지가 한 절차
- 직접 모드에서 판정 에이전트를 붙이지 않는다. 코드면 리더가 테스트를, 문서면 `docs-lint.py`를 돌린다
- `CLAUDE.template.md`, `README.md` — 위 규칙 반영

### Fixed

- `ledger.py` — `--fixes`가 있는데 `target`이 없는 task를 `done`으로 옮기면 `KeyError`로 죽던 것

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
