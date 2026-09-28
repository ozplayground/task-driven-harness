# task-driven-harness

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](CHANGELOG.md)

Claude Code에서 **리더(메인 세션)가 `orchestration` 스킬로 사용자의 요청을 분석·계획하고, task로 나눠 서브에이전트에 분배하고, 산출물로 완료를 판정하는 하네스**다.

이 저장소에는 애플리케이션이 없다. 담고 있는 것은 하네스 구성 자체다 — 에이전트 정의 **14종**, 스킬 **21종**, 문서 템플릿 **31종**, 원장 스크립트 하나(`ledger.py`), 설치 스크립트(`install.sh`), 대상 프로젝트용 규약(`CLAUDE.template.md`), 그리고 변경 이력(`CHANGELOG.md`). 전부 마크다운과 파이썬 표준 라이브러리로 되어 있다. 코드 task에는 ponytail·frontend-design 플러그인을, 라이브러리 문서 확인에는 context7 MCP 서버를 쓴다. 플러그인 설정은 `.claude/settings.json`에, MCP 서버는 `.mcp.json`에 있고 설치 스크립트가 대상 프로젝트에 합친다.

- 원격: `https://github.com/ozplayground/task-driven-harness`, 기본 브랜치 `main`
- 문서 언어: 한국어

---

## 무엇을 하는 하네스인가

하네스의 축은 다섯이다 (`.claude/skills/orchestration/SKILL.md`).

- **단위는 task다.** 만드는 것도, 비평·리뷰·재작업도 task다. task마다 맡는 에이전트가 하나 있고, 순서는 task 간 의존이다. task와 task를 잇는 것은 리더다. 고정된 단계(기획→설계→구현)는 없다.
- **시킨 것만 한다.** 범위를 넓히는 모든 결정은 사용자에게 돌아간다.
- **완료는 보고가 아니라 산출물로 판정한다.**
- **판정은 한 번, 재작업도 한 번.** 새 문서의 첫 판에 `critic` 비평과 `doc-reviewer` 리뷰를 각각 한 번 붙인다. 지적은 재작업 한 번으로 전부 반영하고 두 번째 판정은 없다. 원장이 두 번째 판정·재작업의 등록을 거부한다. 코드는 테스트 통과가 판정이고, 코드 리뷰·보안 검토는 사용자가 요구했거나 보안 경계 코드일 때만 붙는다.
- **구현은 구조 결정이 확정되면 시작한다.** 입력 문서의 첫 판이 있으면 그 문서의 판정이 끝나기를 기다리지 않는다. 구현 중에는 문서를 고치지 않고, 세부는 코드에서 정해 보고서에 적고, 구현이 끝나면 문서 정합 task 하나로 문서를 한 번에 맞춘다.
- **`docs/`는 최종 산출물이다.** 작업 기록(task ID, finding 번호, 라운드, 에이전트 이름)은 `_tasks/`에만 있다. `docs-lint.py`가 검사하고, 위반이 있으면 문서 task는 `done`이 되지 않는다.
- **계획은 검증을 받는다.** 구현 투입 전에 `critic`이 계획을 한 번 비판하고, 사용자가 승인한다.
- **판단은 기록한다.** 계획·호출의 근거를 원장 `log`에 `--because`로 남긴다.

### 리더가 하는 일

메인 세션(리더)이 `orchestration` 스킬을 따라 요청을 **분석**하고(받은 것과 요구를 분리, 결손을 목록으로), task로 나눠 **계획**을 세우고, 각 task를 그 task의 에이전트에 **분배**하고, 보고와 산출물로 **완료를 판정**하고, 산출물이 나오면 비평·리뷰 task를, 지적이 나오면 재작업 task를 만들어 **잇는다**.

산출물은 직접 만들지 않는다. 그리고 계획을 혼자 닫지 않는다 — 구현 task를 투입하기 전에 `critic`이 완료 기준이 요구를 담는지, 분할이 구조 경계와 맞는지, 전제에 근거가 있는지를 치고, 그 다음 사용자가 task 표를 승인한다.

되돌리기 어려운 구조 결정(스택, 저장소, 통신 방식, 모듈 경계)이 걸려 있으면 **분할 전에** `architect`를 부른다. 아키텍트는 조사 목록을 내고, 조사가 끝나면 결정 기록 초안과 후속 필수 설계 목록을 낸다. 확정은 사용자가 하고, task 분할은 리더가 한다.

### 완료는 증거로만 인정된다

만드는 에이전트는 완료 기준마다 증거 수준을 붙인다 — **실행 검증 / 산출물 대조 / 코드 확인 / 미검증**. 이 중 앞의 둘만 완료로 친다 (`completion-evidence`). 리더는 보고문을 믿지 않고 직접 확인한다. 코드면 워크트리에서 테스트·타입 검사·린트를 직접 돌리고, 문서면 `docs-lint.py`가 `set done`에서 자동으로 돈다. 판정 에이전트(`critic`, `doc-reviewer`, `code-reviewer`, `security` 검토)는 별도 인스턴스이고 `confirmed` / `needs-fix` / `inconclusive` 하나를 내며, 대상마다 한 번만 붙는다 (`verify-loop`).

### 구현자는 설계하지 않는다

구조(스택, 저장소, 통신 방식, 인증)가 문서에 없거나, 만들어야 하는 동작 자체가 어느 문서에도 없거나, 두 문서가 모순이면 구현 에이전트는 채워 넣지 않고 **"막힌 것: 입력 없음"**으로 보고한다. 그러면 리더가 그 입력을 만드는 task를 추가하고 의존을 건다. 반대로 세부 하나(계약에 없는 필드, 문구, 엣지 케이스)가 빈 것은 멈출 일이 아니다. 코드와 테스트에서 정하고 보고서에 적으면, run 끝의 문서 정합 task가 문서로 옮긴다.

### 코드 주석은 그 자리에서 이해돼야 한다

`# BR-04`, `// FSD §3.2 참조`처럼 문서 참조만 있는 주석은 주석이 아니다. 무엇을 왜 하는지 문장으로 적고, 문서 링크는 그 뒤에 참고로 둔다. `docs-lint.py code`가 참조만 있는 주석을 잡는다.

---

## 요청 하나가 도는 모습

`.claude/skills/orchestration/SKILL.md`의 흐름을 요약한 것이다.

1. **분석** — 받은 것(given)과 요구(wanted)를 분리하고, 받은 문서를 적재해 **결손을 채우지 않고 목록으로** 올린다. 결손은 결정 / 계약 / 중간 산출물 셋으로 갈린다 (`references/intake.md`).
2. **계획** — 직접 모드(task 하나, 새 결정 없음, 파일 서너 개 이하)면 원장 없이 에이전트 하나와 리뷰어 한 번으로 끝낸다. 보안·규제 대상이면 `security` 요건 task를 맨 앞에 둔다. 되돌리기 어려운 구조 결정이 걸려 있으면 먼저 `architect`를 부르고, 조사를 거쳐 결정 초안과 후속 필수 설계 목록을 받는다. 그 다음 리더가 요구·결손·후속 설계를 `references/split.md`의 규칙(산출물 하나에 task 하나, 소유 경로 겹침 금지, 공유 자원은 선행 task, 의존은 입력 의존과 파일 충돌뿐)으로 task로 나눠 원장에 등록한다.
3. **비판과 승인** — 구현 task가 등록되면 투입 전에 `critic`을 한 번 던진다. 두 번째는 없다. 그 다음 task 표와 결정 선택지를 사용자에게 올려 승인을 받는다. 사용자에게 묻는 요구는 원문에서 온 것뿐이고, PRD가 풀어 쓰며 덧붙인 `(보강)` 조건은 리더가 정리한다.
4. **분배** — 의존이 풀린 task를 동시에 5개까지 던진다. 구현 task는 구조 결정이 확정되고 입력 문서의 첫 판이 run 브랜치에 있으면 던진다. 판정 완료를 기다리지 않는다. 워크트리를 만들면 의존성 설치까지가 한 절차다. 에이전트 종류마다 첫 호출이 끝나면 기록에서 정의의 스킬이 실제로 로드됐는지 확인한다.
5. **판정과 잇기** — 보고가 오면 리더가 형식·소유 경로·증거 수준을 직접 확인하고, 코드면 테스트를 직접 돌리고, 문서면 `set done`이 `docs-lint.py`를 돌린다. done이 되면 run 브랜치에 머지하고, 문서면 `critic` 비평 task와 `doc-reviewer` 리뷰 task를 한 번씩 만들어 던진다. 코드에는 기본으로 판정을 붙이지 않는다. 사용자가 요구했으면 `code-reviewer`, 보안 경계 코드면 `security` 검토를 한 번.
6. **재작업 한 번** — 판정이 전부 끝나면 blocker·major를 모아 원래 에이전트의 재작업 task 하나를 만든다. minor(형식 지적)는 넣지 않는다. 재작업 뒤 두 번째 판정은 없다. 리더가 보고서의 ID별 설명을 파일과 대조해 finding을 닫고, 닫히지 않은 것은 waive하고 run 보고서에 적는다. 원장이 두 번째 판정·재작업의 등록을 거부한다.
7. **종료** — 구현이 끝나면 문서 정합 task 하나로 구현 보고서의 "명세에 없어 내가 정한 것"과 minor를 문서에 한 번에 옮긴다(판정 없이 리더가 diff와 `docs-lint.py`로 확인). run 보고서를 쓰고, `git-workflow`대로 run 브랜치를 푸시하고 develop으로 PR·머지한다. 배포와 외부 전송은 하지 않는다.

서브에이전트가 중간에 끊겨도 이어갈 수 있다. 만드는 에이전트는 보고서를 진행 중에 갱신하고, 재개는 세 경로를 순서대로 쓴다: 죽은 에이전트를 메시지로 되살리기(기본) → 에이전트 기록으로 상태 복원 → 새 인스턴스에 재개 브리프(마지막 수단).

---

## 에이전트 14종

`.claude/agents/<이름>.md`. task 종류 하나에 에이전트 하나다. 원장의 `agent` 필드가 곧 리더가 부를 서브에이전트이고, 각 에이전트는 자기 방법론 스킬을 `skills:`로 갖고 시작한다. 브리프는 스킬을 지정하지 않는다.

### 만드는 에이전트 10종

공통으로 `task-execution`(소유 경로, 중단 대비, 재개, 발견한 버그, 조사 위임, 재작업, 보고), `plan-and-check`, `completion-evidence`, `git-workflow`를 갖는다. 문서를 쓰는 쪽은 `design-docs`와 `humanizer`도.

| 이름 | 하는 일 | 방법론 스킬 | 쓰는 곳 |
|---|---|---|---|
| `researcher` | 조사·벤치마크. 주장마다 출처, 비교에는 축 | `research` | `docs/research/` |
| `architect` | 구조·스택·횡단 규약 결정 초안, 결정 기록, FSD마다 설계 문서, 후속 필수 설계 목록, 실행 중 구조 상담. 로컬 실행·코드 규칙 문서. 확정은 사용자(무인이면 critic 비평 뒤 리더) | `architecture` | `docs/design/architecture.md`, `docs/decisions/`, `docs/dev/` |
| `spec-writer` | PRD, FSD, 용어집, 레퍼런스 | `spec-authoring` | `docs/prd/`, `docs/fsd/`, `docs/glossary.md`, `docs/reference/` |
| `ux-designer` | UX 설계, 디자인 시스템 | `ux-design`, `frontend-design`(플러그인) | `docs/design/ux.md`, `docs/design/design-system.md` |
| `contract-designer` | 설계 문서에서 REST API 명세, SDK 인터페이스 정의, 데이터 모델을 도출 | `interface-contract` | `docs/api/`, `docs/interface/`, `docs/design/data-model.md` |
| `security` | compliance·보안 요건 문서. 그리고 아키텍처·계약·데이터 모델·코드의 보안 검토 | `security-compliance` | `docs/compliance/`, `docs/design/security.md`, 리뷰 파일 |
| `backend-developer` | 서버 코드와 테스트. 레벨 3만 정한다 | `backend-work`, `debugging`, `ponytail`(플러그인) | 소유 경로 |
| `frontend-developer` | 화면 코드와 테스트. 새 화면이면 `frontend-design`도 | `frontend-work`, `debugging`, `ponytail` | 소유 경로 |
| `devops` | CI·CD·컨테이너·배포 설정, 배포·모니터링·런북 문서 | `ci-cd`, `ponytail` | 소유 경로, `docs/ops/` |
| `verifier` | 테스트 계획·케이스, 통합 검증, 테스트 실행 보고, e2e. 앱 코드는 고치지 않고 결함을 보고 | 없음 | `docs/qa/`, 소유 경로 |

### 판정하는 에이전트 3종과 조사자

산출물을 고치지 않는다. `Edit`이 없고 `Write`는 자기 파일 하나에만 쓴다.

| 이름 | 하는 일 | 스킬 | 쓰는 곳 |
|---|---|---|---|
| `critic` | 문서가 나올 때마다 내용을 비평한다 — 과잉 설계, 불필요한 기술, 근거 부족, 누락, 모순, 요구 대비. 구현 투입 전에는 계획을 비판한다 | `direction-review`, `design-docs`, `plan-and-check` | 비판 파일 |
| `doc-reviewer` | 문서가 완료 기준을 채웠는지 대조 판정. 템플릿 절, 입력 문서 항목, 참조 ID, 결정 레벨 | `verify-loop`, `design-docs`, `plan-and-check` | 리뷰 파일 |
| `code-reviewer` | 코드가 완료 기준을 채웠는지 판정. 테스트·빌드 직접 실행, 3-dot diff로 범위, 계약 대조, 경계면 | `verify-loop`, `git-workflow`, `completion-evidence`, `design-docs`, `plan-and-check` | 리뷰 파일 |
| `investigator` | 질문 하나에 `파일:줄` 근거를 붙여 200줄 이내로 답한다. 읽기 전용이고 누구나 부르며 위임의 종착점 | 없음 | 없음 |

재작업 task는 원래 만든 에이전트가 같은 워크트리에서 맡는다. 서브에이전트는 `investigator`만 부르고, `investigator`는 아무도 부르지 않는다. 리더(메인 세션)는 원장·notes·run 보고서를 쓴다.

라이브러리·프레임워크 문서는 context7 MCP 서버(도구 `mcp__context7__resolve-library-id`, `mcp__context7__query-docs`)로 읽는다. 모든 에이전트가 `tools`에 `mcp__context7`을 갖는다. 기억으로 API를 쓰지 않는다.

---

## 스킬 21종

`.claude/skills/<이름>/SKILL.md`. 스킬은 에이전트 정의의 `skills:`로 시작 시 로드된다. 리더는 자기 스킬을 요청을 보고 고른다.

### 리더가 쓰는 것

| 스킬 | 한 줄 |
|---|---|
| `orchestration` | 리더가 쓰는 절차. 분석 → 계획 → 비판·승인 → 분배 → 판정과 잇기 → 재작업 루프 → 종료. 참고 파일 4개(`intake` 적재, `split` 분할 규칙, `dispatch` 브리프 형식, `ledger-format` 원장 필드)와 `scripts/ledger.py` |
| `git-workflow` | GitFlow(main/develop/feature/release/hotfix)에 task마다 자기 워크트리·브랜치를 더한 것. 만드는 에이전트는 `.worktrees/<task>`에서 커밋만 하고, 리더가 3-dot diff로 검사해 run 브랜치에 머지하고, run이 끝나면 develop으로 PR·머지한다. 릴리스·핫픽스·롤백 포함. 만드는 에이전트와 code-reviewer도 로드한다 |
| `unattended` | 사용자 없이 도는 run. 토글이며 상태는 파일에 있다. 결정이 비면 조사 → 아키텍트 추천 → critic 비평 → 리더 확정. 질문 큐는 위임장 범위 밖만. 배포와 외부 전송은 무인에서도 하지 않는다 |
| `bugfix-followup` | 남은 버그를 끝에 모아 처리한다. 현재 task와 관련 있는 버그를 같이 고치는 것은 만드는 에이전트의 기본 동작이다 |

### 만드는 에이전트의 공통 규율

| 스킬 | 한 줄 |
|---|---|
| `task-execution` | task 하나를 맡았을 때의 공통 규칙. 시킨 것만, 워크트리와 소유 경로 안에서만, 결정 레벨, 진행 중 보고서 갱신, 재개, 발견한 버그, 조사 위임, 재작업 호출, 보고 형식, 멈춰야 하는 신호 |
| `plan-and-check` | 계획을 먼저 쓰고, 계획에 대고 검사한다. 판정하는 쪽도 쓴다 |
| `completion-evidence` | 완료는 증거와 함께 적는다. 기준마다 증거 수준, 보고서 절 이름과 순서 |
| `design-docs` | 문서 표준 — 모든 문서의 위치·이름·템플릿(31종)·결정 레벨·승격 규칙, `docs/`와 `_tasks/`의 경계(docs는 결정된 것만, 작업 흔적·task ID 금지), 제목·ID·링크 규칙이 여기 한 곳에 있다 |
| `humanizer` | 문서를 사람이 쓴 것처럼. 문장 규칙, 넣지 않는 것(과장, 빈 총평, 영문 병기, 번호·볼드 남발, 이모지, 빈 칸 채우기, 자기 지칭, 작업 경위), 구조, 문서 종류별 차이, 쓴 뒤 점검. 문서를 쓰는 에이전트와 doc-reviewer·critic이 로드한다 |

### 방법론 — 에이전트마다 하나

| 스킬 | 에이전트 | 한 줄 |
|---|---|---|
| `research` | researcher | 주장마다 출처를, 비교에는 축을 |
| `architecture` | architect | 결정 사슬 순서로 정한다. 결정 범위와 조사 목록, 대안·기준·근거, 구조 문서와 결정 기록 |
| `spec-authoring` | spec-writer | 뒤에서 만들 사람이 결정을 내리지 않게 쓴다 — PRD, FSD, 용어집, 레퍼런스 |
| `ux-design` | ux-designer | 사용자의 작업에서 화면으로 — 정보 구조, 내비게이션, 화면 목록·흐름, 상호작용 규칙, 디자인 시스템 |
| `interface-contract` | contract-designer | 계약을 먼저 확정하고 양쪽은 계약에 대조한다 — 교환 규격, API, 이벤트, 에러 코드, 데이터 모델 |
| `security-compliance` | security | 데이터 분류 → 규제 → 위협 모델 → 보안 요건(`S-nn`) → 설계 강제 항목 → 검증. 그리고 대상별 보안 검토 항목 |
| `backend-work` | backend-developer | 계약대로 동작하고 명세대로 검증한다 |
| `frontend-work` | frontend-developer | 명세의 화면을 저장소의 방식으로 |
| `ci-cd` | devops | 요구할 때만 만들고, 로컬에서 검증 가능한 만큼만 완료로 친다 |
| `debugging` | backend-developer, frontend-developer | 원인을 알기 전에 고치지 않는다 — 재현 → 원인 → 최소 수정 → 증명 |

### 판정

| 스킬 | 에이전트 | 한 줄 |
|---|---|---|
| `verify-loop` | doc-reviewer, code-reviewer, security | 판정 형식, finding 기록, 재작업 한 번, 형식은 minor, 닫는 조건 |
| `direction-review` | critic | 문서 비평 여섯 종류와 문서 종류별 확인 항목, 계획 비판, 심각도, 한 번에 전부 보기, 처리 절차 |

### 플러그인

| 스킬 | 에이전트 | 한 줄 |
|---|---|---|
| `ponytail:ponytail` | backend-developer, frontend-developer, devops | 가장 단순한 구현, 불필요한 추상화·의존성 금지 |
| `frontend-design:frontend-design` | ux-designer(디자인 시스템), frontend-developer(새 화면) | 팔레트·타이포·레이아웃을 의도를 갖고 정한다 |

---

## 상태는 파일에 둔다

진행 상태를 대화 컨텍스트에 두지 않는다. 컨텍스트가 압축돼도 파일을 읽으면 복원된다. 문서는 두 뿌리로 나뉜다 (`design-docs`).

| 뿌리 | 무엇 | 수명 |
|---|---|---|
| `docs/` | 사용자가 받는 산출물과 결정 기록 (PRD·FSD·조사·구조·ADR·계약·설계·QA·운영·run 보고서) | 프로젝트와 같이 |
| `_tasks/<run>/` | 이 run의 진행 기록 (`tasks.json` 원장, `notes.md`, `reports/`, `reviews/`, `critique/`) | run |

run 종료 시 리더가 `_tasks/`의 가정·waive·미검증을 `docs/`로 승격한다.

---

## 원장 — `ledger.py`

원장은 `_tasks/<run>/tasks.json` 하나이고, `.claude/skills/orchestration/scripts/ledger.py`가 그 파일을 읽고 쓰는 유일한 경로다. 파이썬 표준 라이브러리만 쓴다.

```
ledger.py init     <run> --request "요청 한 줄"
ledger.py add      <run> <id> --agent <에이전트> --title T --paths a/**,b.md
                   [--depends T1,T2] [--accept "기준"] [--because "근거"]
                   [--target T1] [--fixes T1-F1,T1-F2]
ledger.py validate <run>   # 스키마·의존 사이클·동시 실행 가능 task 간 경로 겹침·target 정합
ledger.py ready    <run>   # 지금 던질 수 있는 task. 승인 전에는 researcher·architect·critic·doc-reviewer만
ledger.py brief    <run> <id>   # 브리프에 옮길 필드와 의존 task의 경로
ledger.py set      <run> <id> <status> [--note "..."] [--because "근거"] [--skip-docs-check]
ledger.py finding  <run> <id> add|resolve|waive <fid> [severity] ["내용"]   # id = 산출물을 만든 task
ledger.py approve  <run>   # planning → approved (사용자 승인 후)
ledger.py show     <run> [--paths]
```

리뷰·비평·재작업은 상태가 아니라 task다. 리더가 `add`로 만들고 `--target`으로 대상을 가리킨다. 재작업은 `--fixes`에 고칠 finding을 적고, 전부 resolved 또는 waived여야 done이 된다. 상태는 다섯이다.

```
pending → ready → running → done
                  running → failed → ready   (재투입)
                  running → failed → done    (중단 종료)
```

스크립트가 기계적으로 막는 것:

- 허용되지 않은 상태 전이
- **같은 대상에 두 번째 판정 task(에이전트별)와 두 번째 재작업 task**
- **minor finding을 `--fixes`에 넣는 것** (형식·취향은 재작업 사유가 아니다)
- **문서 task의 `done`에서 `docs/` 경계 위반** (`docs-lint.py`를 자동으로 돌린다. `--skip-docs-check`는 `--because`와 함께만)
- 고치기로 한 finding이 open인 재작업 task의 `done`
- 대상 task와 다른 에이전트의 재작업, 대상에 없는 finding
- 소유 경로가 없거나 완료 기준이 없는 task (`validate`, `approve`)
- 의존 사이클, 그리고 **동시에 돌 수 있는 두 task의 소유 경로 겹침**
- 승인 전(`planning`) 상태에서 조사·구조·비평·문서 리뷰 외 task가 `ready`가 되는 것

원장 파일의 위치는 현재 작업 디렉터리 기준 `_tasks/`이고, 환경 변수 `ORCHESTRATION_ROOT`로 바꿀 수 있다.

## 경계 검사 — `docs-lint.py`

`.claude/skills/design-docs/scripts/docs-lint.py`. 표준 라이브러리만 쓴다.

```
docs-lint.py docs [경로…]   # docs/에 작업 기록(task ID, finding 번호, 라운드, 에이전트 이름, _tasks/ 경로, 안내문 잔재, YAML 머리말, 작성자 표)이 있으면 종료 1. 깨진 링크는 경고
docs-lint.py code [경로…]   # 문서 참조만 있고 설명이 없는 코드 주석이 있으면 종료 1
```

`ledger.py set <문서 task> done`이 `docs` 검사를 자동으로 돌린다. 리더는 머지 전과 run 끝에 `docs/` 전체에, 코드 task를 확인할 때 소유 경로에 돌린다. 만드는 에이전트는 커밋 전에 스스로 돌린다.

---

## 다른 저장소에서 쓰기

이 저장소에서 `./install.sh <대상 저장소 경로>`를 돌린다. 이 저장소의 세션에 "여기에 설치해줘"라고 하면 리더가 대신 돌리고 결과를 확인한다. 스크립트가 하는 일은 다음과 같고, 다시 돌리면 갱신이다.

1. `.claude/agents/`와 `.claude/skills/`를 대상 저장소의 `.claude/` 아래로 복사한다 (덮어쓴다).
2. `CLAUDE.template.md`를 대상 `CLAUDE.md`로 복사한다. 이미 있으면 하네스 절만 덧붙이거나 갱신한다.
3. 이 저장소의 `.claude/settings.json`(마켓플레이스와 플러그인)을 대상 `.claude/settings.json`에 합친다.
4. 대상 `.mcp.json`에 context7 MCP 서버를 등록한다. 기존 서버와 합친다.
5. `.gitignore`에 `_tasks/`, `.worktrees/`를 넣는다.
6. git 저장소인지 확인한다. `python3`가 있어야 하고 외부 패키지는 필요 없다.

설치한 뒤 대상 저장소에서 새 세션을 열어야 하네스가 로드된다. 첫 세션에서 context7 MCP 서버 승인이 한 번 뜬다. 그 다음부터는 요청만 하면 된다.

대상 저장소에 이미 문서 규칙이 있으면(`documentation/`, 별도 ADR 디렉터리, 다른 문서 정보 형식) **그 관례가 위다.** `design-docs`의 표준은 관례가 없을 때의 기본값이며, 대응 관계를 `notes.md`와 문서 지도에 적는다.

---

## 디렉터리 구조

```
.
├── CHANGELOG.md               # 하네스 변경 이력
├── CLAUDE.md                  # 이 저장소(하네스 소스)의 규약
├── CLAUDE.template.md         # 대상 프로젝트 CLAUDE.md에 들어가는 run 규칙
├── README.md                  # 이 문서
├── install.sh                 # 대상 프로젝트에 설치·갱신
├── .mcp.json                  # context7 MCP 서버 (대상 프로젝트로 복사)
├── .gitignore
└── .claude/
    ├── agents/                # 에이전트 정의 14종
    │   ├── researcher.md  architect.md  spec-writer.md  ux-designer.md  contract-designer.md
    │   ├── security.md  backend-developer.md  frontend-developer.md  devops.md  verifier.md
    │   └── critic.md  doc-reviewer.md  code-reviewer.md  investigator.md
    └── skills/                # 스킬 20종
        ├── orchestration/
        │   ├── SKILL.md
        │   ├── references/    # dispatch, intake, ledger-format, split
        │   └── scripts/ledger.py
        ├── task-execution/SKILL.md
        ├── design-docs/SKILL.md, templates/*.md (31종)
        │   └── scripts/docs-lint.py
        ├── security-compliance/SKILL.md
        ├── architecture/  research/  spec-authoring/  ux-design/  interface-contract/
        ├── backend-work/  frontend-work/  ci-cd/  debugging/
        ├── plan-and-check/  completion-evidence/  verify-loop/  direction-review/  humanizer/
        ├── git-workflow/  unattended/  bugfix-followup/
        └── (각 SKILL.md)
```

run을 돌리면 여기에 `_tasks/<run>/`(진행 기록)과 `docs/`(산출물)가 생긴다.

---

## 하네스 자체를 고칠 때

`.claude/` 아래 파일과 `CLAUDE.md`를 고치는 요청은 `orchestration`으로 돌리지 않는다. 직접 고치고 커밋한다. `CHANGELOG.md`는 릴리스 버전이 바뀔 때만 적는다. 실행 중인 run이 있으면 하네스 수정은 그 run이 끝난 뒤에 한다. 스킬과 에이전트 정의는 부를 때 새로 읽히므로, run 도중에 고치면 남은 호출부터 바뀐 규칙이 적용된다.
