# task-driven-harness

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](CHANGELOG.md)

Claude Code에서 **리더(메인 세션)가 `orchestration` 스킬로 사용자의 요청을 분석·계획하고, task로 나눠 서브에이전트에 분배하고, 산출물로 완료를 판정하는 하네스**다.

이 저장소에는 애플리케이션이 없다. 담고 있는 것은 하네스 구성 자체다 — 에이전트 정의 **5종**, 스킬 **17종**, 원장 스크립트 하나(`ledger.py`), 운영 규약(`CLAUDE.md`), 그리고 변경 이력(`CHANGELOG.md`). 전부 마크다운과 파이썬 표준 라이브러리로 되어 있고, 별도 플러그인이나 설정 파일(`settings.json`)에 의존하지 않는다.

- 원격: `https://github.com/ozplayground/task-driven-harness`, 기본 브랜치 `main`
- 문서 언어: 한국어

---

## 무엇을 하는 하네스인가

하네스의 축은 다섯이다 (`.claude/skills/orchestration/SKILL.md`).

- **단위는 task다.** 역할은 task의 속성이고, 순서는 task 간 의존이다. 고정된 단계(기획→설계→구현)는 없다.
- **시킨 것만 한다.** 범위를 넓히는 모든 결정은 사용자에게 돌아간다.
- **완료는 보고가 아니라 산출물로 판정한다.**
- **계획은 검증을 받는다.** 구현 투입 전에 `critic`이 계획을 비판하고, 사용자가 승인한다.
- **판단은 기록한다.** 계획·호출의 근거를 원장 `log`에 `--because`로 남긴다.

### 리더가 하는 일

메인 세션(리더)이 `orchestration` 스킬을 따라 요청을 **분석**하고(받은 것과 요구를 분리, 결손을 목록으로), task로 나눠 **계획**을 세우고, 각 task를 서브에이전트에 **분배**하고, 보고와 산출물로 **완료를 판정**한다.

산출물은 직접 만들지 않는다. 그리고 계획을 혼자 닫지 않는다 — 구현 task를 투입하기 전에 `critic`이 완료 기준이 요구를 담는지, 분할이 구조 경계와 맞는지, 전제에 근거가 있는지를 치고, 그 다음 사용자가 task 표를 승인한다.

되돌리기 어려운 구조 결정(스택, 저장소, 통신 방식, 모듈 경계)이 걸려 있으면 **분할 전에** `architect`를 부른다. 아키텍트는 조사 목록을 내고, 조사가 끝나면 결정 기록 초안과 후속 필수 설계 목록을 낸다. 확정은 사용자가 하고, task 분할은 리더가 한다.

### 완료는 증거로만 인정된다

실행자는 완료 기준마다 증거 수준을 붙인다 — **실행 검증 / 산출물 대조 / 코드 확인 / 미검증**. 이 중 앞의 둘만 완료로 친다 (`completion-evidence`). 그리고 판정은 만든 쪽이 하지 않는다. 별도 인스턴스인 `reviewer`가 산출물을 직접 확인하고 `confirmed` / `needs-fix` / `inconclusive` 하나를 내며, `confirmed`만 `done`이 된다 (`verify-loop`).

### 구현자는 설계하지 않는다

계약·설계·구조가 입력인 task에서 그 입력이 없으면, 실행자는 채워 넣지 않고 **"막힌 것: 입력 없음"**으로 보고한다. 그러면 리더가 그 입력을 만드는 task를 추가하고 의존을 건다.

---

## 요청 하나가 도는 모습

`.claude/skills/orchestration/SKILL.md`의 흐름을 요약한 것이다.

1. **분석** — 받은 것(given)과 요구(wanted)를 분리하고, 받은 문서를 적재해 **결손을 채우지 않고 목록으로** 올린다. 결손은 결정 / 계약 / 중간 산출물 셋으로 갈린다 (`references/intake.md`).
2. **계획** — 직접 모드(task 하나, 새 결정 없음, 파일 서너 개 이하)면 원장 없이 executor 하나와 reviewer 한 번으로 끝낸다. 되돌리기 어려운 구조 결정이 걸려 있으면 먼저 `architect`를 부르고, 조사를 거쳐 결정 초안과 후속 필수 설계 목록을 받는다. 그 다음 리더가 요구·결손·후속 설계를 `references/split.md`의 규칙(산출물 하나에 task 하나, 소유 경로 겹침 금지, 공유 자원은 선행 task, 의존은 입력 의존과 파일 충돌뿐)으로 task로 나눠 원장에 등록한다.
3. **비판과 승인** — 구현 task가 등록되면 투입 전에 `critic`을 한 번 던진다. 그 다음 task 표와 결정 선택지를 사용자에게 올려 승인을 받는다.
4. **분배** — 의존이 풀린 task를 한 번에 던진다. 모든 호출은 백그라운드이고, 같은 종류를 여러 번 부르면 독립 인스턴스가 뜬다.
5. **판정** — 보고가 오면 리더가 형식·소유 경로·증거 수준을 직접 확인하고, `reviewer`를 던진다. 실행자와 리뷰어는 반드시 다른 인스턴스다.
6. **루프** — `needs-fix`면 같은 실행자에게 finding ID 목록만 주어 재실행한다. 재작업은 2회까지이고, 넘으면 `blocked`로 두고 사용자에게 올린다.
7. **종료** — run 보고서를 쓰고, `_tasks/`에만 있던 가정·waive·미검증을 `docs/`로 **승격**한다. 머지·배포·삭제 같은 되돌릴 수 없는 조치는 하지 않고 제안만 한다.

서브에이전트가 중간에 끊겨도 이어갈 수 있다. 실행자는 보고서를 진행 중에 갱신하고, 재개는 세 경로를 순서대로 쓴다: 죽은 에이전트를 메시지로 되살리기(기본) → 에이전트 기록으로 상태 복원 → 새 인스턴스에 재개 브리프(마지막 수단).

---

## 에이전트 5종

`.claude/agents/<이름>.md`. 각 파일의 frontmatter에 `name`, `description`, `tools`, `model`이 있고, 시작 시 preload할 스킬이 있는 에이전트는 `skills`를 추가로 갖는다 — 다섯 중 `investigator`만 `skills`가 없다.

| 이름 | 하는 일 | 쓸 수 있는 곳 | 다른 에이전트 호출 |
|---|---|---|---|
| `architect` | 되돌리기 어려운 구조 결정이 걸려 있을 때 분할 전에 불린다. 조사 목록, 구조·스택·횡단 규약 결정 초안, 후속 필수 설계 목록, 실행 중 구조 상담. task 분할은 하지 않는다. NFR·제약에서 시작해 결정 사슬 순서로 대안·기준·추천을 내되 **확정은 사용자가 한다** | 구조 문서·결정 기록, 자기 보고서 | `investigator` |
| `executor` | task 하나를 끝내는 범용 실행자. 고른 스킬에 따라 조사자·명세자·설계자·구현자가 된다. 소유 경로 안에서만 쓰고, 계획 → 진행 → 완료 보고를 한 파일에 남긴다 | 자기 소유 경로, 자기 보고서 | `investigator` |
| `reviewer` | 산출물이 완료 기준을 만족하는지 독립 판정. 테스트·빌드를 직접 돌리고, 소유 경로 밖 변경과 경계면 불일치를 본다. **고치지 않는다** | 리뷰 파일 하나 | `investigator` |
| `critic` | 구현 투입 **전에** 계획의 전제를 친다. 완료 기준이 요구를 담는지, 안 본 대안이 없는지, 분할이 구조 경계와 맞는지. reviewer와 반대 입장이다 — reviewer는 기준을 의심하지 않고, critic은 기준 자체를 의심한다 | 비판 파일 하나 | `investigator` |
| `investigator` | 질문 하나에 `파일:줄` 근거를 붙여 200줄 이내로 답한다. 읽기 전용이고 위임의 종착점이다 | 없음 | 없음 |

리더(메인 세션)는 이 표 전부를 부를 수 있고, 원장·notes·run 보고서를 쓴다.

---

## 스킬 17종

`.claude/skills/<이름>/SKILL.md`. 어떤 스킬을 쓸지는 브리프가 지정하지 않는다 — 리더는 요청을 보고, 서브에이전트는 자기 task를 보고 스킬 설명에서 고른다. 다만 에이전트 정의의 `skills:`에 적힌 것은 시작 시 항상 로드된다.

### 리더가 쓰는 것

| 스킬 | 한 줄 |
|---|---|
| `orchestration` | 리더가 쓰는 절차. 분석 → 계획 → 비판·승인 → 분배 → 판정. 참고 파일 4개(`intake` 적재, `split` 분할 규칙, `dispatch` 브리프 형식, `ledger-format` 원장 필드)와 `scripts/ledger.py`를 함께 갖는다 |
| `unattended` | 사용자 없이 도는 run. 토글이며 상태는 파일에 있다. "사용자에게 올린다"고 된 지점을 위임장(mandate)의 대체 규칙으로 처리하고, 위임장 밖은 질문 큐에 적고 그 결정에 의존하지 않는 task만 계속 돌린다. 배포·푸시·머지는 무인에서도 하지 않는다 |

### 서브에이전트가 시작 시 로드하는 규율

| 스킬 | 한 줄 | 로드하는 에이전트 |
|---|---|---|
| `design-docs` | 문서 표준 — 모든 문서의 위치·이름·머리말·골격·승격 규칙이 여기 한 곳에 있다. 문서를 쓰는 에이전트가 시작 시 로드해 따르며, 다른 스킬은 문서의 위치를 정하지 않는다 | architect, executor, reviewer, critic |
| `plan-and-check` | 계획을 먼저 쓰고, 계획에 대고 검사한다. 시작 전 계획 표 → 진행 중 갱신 → 보고 전 자기 검증 표(계획 대비·기준 대비·범위 대비) | architect, executor, reviewer, critic |
| `completion-evidence` | 완료는 증거와 함께 적는다. 기준마다 증거 수준, 보고서 절 이름과 순서 | executor, reviewer |
| `verify-loop` | 구현 → 검사 → 수정 → 재검사. 판정 형식, finding 기록, 재작업 범위와 루프 종료 | reviewer |
| `direction-review` | 구현 투입 전에 기준을 의심한다. 비판 항목의 종류·심각도·확인 방법과, 그 항목을 처리하는 절차 | critic |
| `architecture` | 결정 사슬 순서로 정한다. 결정 범위와 조사 목록, 결정 사슬, 대안·기준·근거, 구조 문서와 결정 기록(ADR) | architect |

### 실행자가 task를 보고 고르는 작업 스킬

| 스킬 | 한 줄 |
|---|---|
| `spec-authoring` | 뒤에서 만들 사람이 결정을 내리지 않게 쓴다 — PRD, 기능 명세(FSD), 용어집, 외부 독자용 레퍼런스 |
| `interface-contract` | 계약을 먼저 확정하고, 양쪽은 계약에 대조한다 — 둘 이상의 task가 공유하는 교환 규격, API 스펙, 이벤트 형식, 에러 코드 표 |
| `research` | 주장마다 출처를, 비교에는 축을 붙인다 — 조사·벤치마크 문서. 문서가 남고 리뷰를 받는다 |
| `backend-work` | 계약대로 동작하고 명세대로 검증한다 — API·서버 로직·저장소 접근의 구현. 구조·계약·데이터 모델 설계는 하지 않는다 |
| `frontend-work` | 명세의 화면을 저장소의 방식으로 — 화면·컴포넌트·클라이언트 상태·API 호출부의 구현 |
| `debugging` | 원인을 알기 전에 고치지 않는다 — 재현 → 원인 → 최소 수정 → 증명 |

### 선택 스킬 — 요구할 때만

| 스킬 | 한 줄 |
|---|---|
| `git-workflow` | 요구할 때만 하고, 되돌릴 수 없는 것은 사람이 한다. 머지·푸시·force·히스토리 재작성은 사용자 지시 없이는 하지 않는다 |
| `ci-cd` | 요구할 때만 만들고, 로컬에서 검증 가능한 만큼만 완료로 친다. 실제 배포 실행과 시크릿 등록은 사용자가 한다 |
| `bugfix-followup` | 남은 버그를 끝에 모아 처리한다. 현재 task와 **관련 있는** 버그를 같이 고치는 것은 실행자의 기본 동작이므로 이 스킬과 무관하다 |

---

## 상태는 파일에 둔다

진행 상태를 대화 컨텍스트에 두지 않는다. 컨텍스트가 압축돼도 파일을 읽으면 복원된다. 문서는 두 뿌리로 나뉜다 (`design-docs`).

| 뿌리 | 무엇 | 수명 |
|---|---|---|
| `docs/` | 사용자가 받는 산출물과 결정 기록 (PRD·명세·조사·구조·ADR·계약·설계·QA·운영·run 보고서) | 프로젝트와 같이 |
| `_tasks/<run>/` | 이 run의 진행 기록 (`tasks.json` 원장, `notes.md`, `reports/`, `reviews/`, `critique/`) | run |

run 종료 시 리더가 `_tasks/`의 가정·waive·미검증을 `docs/`로 승격한다.

---

## 원장 — `ledger.py`

원장은 `_tasks/<run>/tasks.json` 하나이고, `.claude/skills/orchestration/scripts/ledger.py`가 그 파일을 읽고 쓰는 유일한 경로다. 손으로 JSON을 고치면 전이 규칙과 겹침 검사를 우회하게 된다. 파이썬 표준 라이브러리만 쓴다 (Python 3.11.9에서 실행 확인).

```
ledger.py init   <run> --request "요청 한 줄"
ledger.py add    <run> <id> --title T --paths a/**,b.md [--depends T1,T2]
                 [--kind code|doc|research] [--accept "기준"] [--because "근거"]
ledger.py validate <run>   # 스키마·의존 사이클·동시 실행 가능 task 간 경로 겹침
ledger.py ready  <run>     # 지금 던질 수 있는 task. 승인 전에는 research만
ledger.py set    <run> <id> <status> [--note "..."] [--because "근거"]
ledger.py finding <run> <id> add|resolve|waive <fid> [severity] ["내용"]
ledger.py reopen <run> <id> --reason "..."   # done → rework
ledger.py approve <run>    # planning → approved (사용자 승인 후)
ledger.py show   <run>     # 사람이 읽는 표
```

상태 전이는 스크립트가 강제한다.

```
pending → ready → running → review → done
                  running → failed → ready   (재투입)
                  review  → rework → running
어느 상태에서든 → blocked (사용자 판단 대기)
```

스크립트가 기계적으로 막는 것:

- 허용되지 않은 상태 전이
- 미해소 `blocker` finding이 있는 task의 `done`
- 소유 경로가 없거나 완료 기준이 없는 task (`validate`, `approve`)
- 의존 사이클, 그리고 **동시에 돌 수 있는 두 task의 소유 경로 겹침** — 두 실행자가 같은 파일을 덮어쓰는 사고를 사전에 잡는다
- 승인 전(`planning`) 상태에서 `research` 외 task가 `ready`가 되는 것

원장 파일의 위치는 현재 작업 디렉터리 기준 `_tasks/`이고, 환경 변수 `ORCHESTRATION_ROOT`로 바꿀 수 있다.

---

## 다른 저장소에서 쓰기

1. 이 저장소의 `.claude/agents/`와 `.claude/skills/`를 대상 저장소의 `.claude/` 아래로 복사한다. 두 디렉터리가 전부다 — 설치 스크립트나 빌드 단계는 없다.
2. 대상 저장소의 `CLAUDE.md`에 트리거 규약을 넣는다. 어떤 요청에 하네스를 켜고(파일을 바꾸거나 산출물을 만드는 요청은 규모와 무관하게), 무엇을 예외로 두는지(단순 질문, 그리고 하네스 자체를 고치는 요청)를 정하는 것이 이 문단이다. 이 저장소의 `CLAUDE.md` 앞부분이 그대로 옮겨 쓸 수 있는 형태다.
3. `python3`가 있어야 한다. 외부 패키지는 필요 없다.
4. 그 다음부터는 요청만 하면 된다. 파일을 바꾸거나 산출물을 만드는 요청이면 규모와 무관하게 리더가 `orchestration`을 켜고, 원장과 `docs/`·`_tasks/`를 만든다.

대상 저장소에 이미 문서 규칙이 있으면(`documentation/`, 별도 ADR 디렉터리, 다른 머리말) **그 관례가 위다.** `design-docs`의 표준은 관례가 없을 때의 기본값이며, 대응 관계를 `notes.md`와 문서 지도에 적는다.

---

## 디렉터리 구조

```
.
├── CHANGELOG.md               # 하네스 변경 이력
├── CLAUDE.md                  # 운영 규약 + 트리거
├── README.md                  # 이 문서
├── .gitignore
└── .claude/
    ├── agents/                # 에이전트 정의 5종
    │   ├── architect.md
    │   ├── critic.md
    │   ├── executor.md
    │   ├── investigator.md
    │   └── reviewer.md
    └── skills/                # 스킬 17종
        ├── architecture/SKILL.md
        ├── backend-work/SKILL.md
        ├── bugfix-followup/SKILL.md
        ├── ci-cd/SKILL.md
        ├── completion-evidence/SKILL.md
        ├── debugging/SKILL.md
        ├── design-docs/SKILL.md
        ├── direction-review/SKILL.md
        ├── frontend-work/SKILL.md
        ├── git-workflow/SKILL.md
        ├── interface-contract/SKILL.md
        ├── orchestration/
        │   ├── SKILL.md
        │   ├── references/
        │   │   ├── dispatch.md        # 브리프 형식 (에이전트별 + 재개)
        │   │   ├── intake.md          # 받은 문서 적재와 결손 보고
        │   │   ├── ledger-format.md   # tasks.json 필드 정의와 상태 의미
        │   │   └── split.md           # task 분할 규칙, 승인 요청 형식
        │   └── scripts/
        │       └── ledger.py          # 원장 도구 (표준 라이브러리만)
        ├── plan-and-check/SKILL.md
        ├── research/SKILL.md
        ├── spec-authoring/SKILL.md
        ├── unattended/SKILL.md
        └── verify-loop/SKILL.md
```

run을 돌리면 여기에 `_tasks/<run>/`(진행 기록)과 `docs/`(산출물)가 생긴다.

---

## 하네스 자체를 고칠 때

`.claude/` 아래 파일과 `CLAUDE.md`를 고치는 요청은 `orchestration`으로 돌리지 않는다. 직접 고치고 `CHANGELOG.md`에 적는다. 실행 중인 run이 있으면 하네스 수정은 그 run이 끝난 뒤에 한다. 스킬과 에이전트 정의는 부를 때 새로 읽히므로, run 도중에 고치면 남은 호출부터 바뀐 규칙이 적용된다.
