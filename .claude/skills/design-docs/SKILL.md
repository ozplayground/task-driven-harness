---
name: design-docs
description: 이 프로젝트의 모든 문서가 어디에, 무슨 이름으로, 어떤 템플릿으로 존재하는지 정하는 문서 표준. 문서를 쓰거나 읽는 모든 서브에이전트(문서를 만드는 에이전트, architect, doc-reviewer, code-reviewer, critic)가 시작 시 로드한다. 조사 보고서, PRD(요구사항 정의서)·FSD(기능 명세서), 아키텍처·결정 기록, 계약, 데이터 모델, 흐름 설계, compliance, 테스트 계획, 운영 문서, run 보고서, 실행자 보고서·리뷰·비판 파일의 위치와 이름이 전부 여기 있다. 문서를 쓰는 일이 생기면 위치·이름·템플릿은 무조건 여기서 얻는다. 다른 스킬은 문서의 위치와 형식을 정하지 않는다. "이 문서 어디에 써?", "문서 구조 정리", "데이터 모델 설계해줘", "테스트 계획 써줘", "배포 절차 문서", "개인정보 요건 정리"에도 적용한다.
---

# design-docs — 문서 표준

이 스킬은 문서의 **위치·이름·참조**와 **템플릿**(문서마다 있어야 하는 절)을 정한다. `docs/`는 사람이 받는 산출물이다. 하네스가 진행을 추적하는 표식(run, task, 상태, 종류)은 문서에 남기지 않고 원장에만 둔다.

## 두 뿌리

| 뿌리 | 무엇 | 수명 | 누가 읽나 |
|---|---|---|---|
| `docs/` | 사용자가 받는 산출물과 결정 기록 | 프로젝트와 같이 | 사용자, 뒤 task, 다음 run, 다른 하네스·사람 |
| `_tasks/<run>/` | 이 run의 진행 기록 | run | 리더, 에이전트, 재개 |

## `docs/`와 `_tasks/`의 경계

`docs/`는 결정된 것을 사람에게 보고하고 공유하는 문서다. `_tasks/`는 그 결정에 이르는 진행 기록이다. 둘은 섞이지 않는다.

`docs/`에 넣지 않는 것:

- 진행 상태, 라운드, 재작업, 지적과 그 대응
- task ID, run 이름, 에이전트 이름, finding 번호, 비판 번호
- 검토 경위, 누가 언제 무엇을 고쳤는지 (변경 이력 표의 한 줄만 예외)
- 대안을 검토한 과정 (결정 기록의 "검토한 대안" 절만 예외)
- 작업 요약, "이번 라운드에서", "리뷰 반영" 같은 말
- 템플릿 안내문

`docs/` 문서는 주제 하나에 문서 하나다. 절은 템플릿의 것만 쓰고, 표는 읽는 사람이 비교할 것이 있을 때만 쓴다. 문장은 이해에 필요한 만큼 쓰고 그 이상 늘리지 않는다. 짧다고 뜻이 안 통하면 안 되고, 길다고 작업 경위가 들어가면 안 된다.

**제목.** 문서 제목은 "주제 + 문서 종류"의 명사구다. "주문 조회 설계", "세션 모듈 인터페이스", "결제 대행사 연동 조사". 작업 내용을 요약한 문장을 제목으로 쓰지 않는다. 결정 기록 제목은 결정 대상까지만: "ADR-014 bash 격리 방식". 결정 내용은 본문 첫 문장이다.

**ID.** `docs/`에서 쓰는 번호는 추적에 필요한 것만이다. 요구 `REQ`·`NFR`, 기능 `FN`, 화면 `SCR`, 결정 `ADR`, 보안 `S`, 규제 `C`, 테스트 `TC`. 이것도 문장 안에 늘어놓지 않고 표의 추적 열이나 절 제목에 둔다. 문장은 이름으로 말한다. "주문 조회 화면"이라고 쓰고 표에서 `SCR-02`를 가리킨다. task ID, finding 번호, run 이름은 `docs/`에 없다. `_tasks/`에서는 어떤 ID든 자유다.

## 문서 목록

문서 종류마다 위치, 파일 이름, 쓰는 쪽, 템플릿이 정해져 있다.

| 위치 | 문서 | 쓰는 쪽 | 템플릿 |
|---|---|---|---|
| `docs/README.md` | 문서 지도 | 리더 | `templates/readme.md` |
| `docs/glossary.md` | 용어집 | spec-writer | `templates/glossary.md` |
| `docs/runs/<run>.md` | run 보고서 | 리더 | `templates/run-report.md` |
| `docs/mandate.md` | 위임장 — 무인 모드에서 사용자를 대신하는 결정 | 사용자 (리더가 템플릿 제공) | `templates/mandate.md` |
| `docs/decisions/NNN-<주제>.md` | 결정 기록 | architect (초안), 리더 (승격) | `templates/adr.md` |
| `docs/prd/<제품>.md` | 요구사항 정의서. 요구사항(`REQ-nn`)별 정의 | spec-writer | `templates/prd.md` |
| `docs/fsd/<제품>/<REQ-nn>-<주제>.md` | 기능 명세서. 요구사항 하나를 기능(`FN-nn`)으로 나눠 상세 명세. REQ 하나에 파일 하나 | spec-writer | `templates/fsd.md` |
| `docs/research/<주제>.md` | 조사·비교 보고서 | researcher | `templates/research.md` |
| `docs/design/architecture.md` | 구조·기술 스택·공통 규약. 저장소에 하나 | architect | `templates/architecture.md` |
| `docs/design/<제품>/<REQ-nn>-<주제>.md` | 설계. 기능 명세서 하나를 어느 구성 요소·흐름·데이터로 만드는가. FSD 하나에 하나. API 명세와 데이터 모델은 여기서 도출된다 | architect | `templates/design.md` |
| `docs/design/ux.md` | UX 설계 — 정보 구조, 내비게이션, 화면 목록·흐름, 레이아웃 골격, 상호작용 규칙, 상태 표현, 접근성 | ux-designer | `templates/ux.md` |
| `docs/design/design-system.md` | 디자인 시스템 — 색·타이포·간격, 공통 컴포넌트, 반응형, 문구 톤 | ux-designer | `templates/design-system.md` |
| `docs/design/data-model.md` | 데이터 모델 | contract-designer | `templates/data-model.md` |
| `docs/design/<주제>.md` | 흐름·모듈 설계 | contract-designer | `templates/flow.md` |
| `docs/api/<주제>.md` | REST API 명세 — 엔드포인트, 요청·응답, 에러 코드 | contract-designer | `templates/api.md` |
| `docs/interface/<모듈>.md` | 라이브러리·SDK 공개 인터페이스 정의. 시그니처와 타입까지만 | contract-designer | `templates/interface.md` |
| `docs/compliance/<주제>.md` | 규제·심사 요건(`C-nn`) | security | `templates/compliance.md` |
| `docs/design/security.md` | 위협 모델과 보안 요건(`S-nn`). 아키텍처보다 먼저 | security | `templates/security.md` |
| `docs/qa/test-plan.md` | 테스트 계획 | verifier | `templates/test-plan.md` |
| `docs/qa/<주제>.md` | 테스트 케이스 | verifier | `templates/test-cases.md` |
| `docs/qa/test-run-<날짜>.md` | 테스트 실행 보고 | verifier | `templates/test-run.md` |
| `docs/ops/deployment.md` | 배포 절차 | devops | `templates/deployment.md` |
| `docs/ops/monitoring.md` | 모니터링 | devops | `templates/monitoring.md` |
| `docs/ops/runbook.md` | 런북 | devops | `templates/runbook.md` |
| `docs/reference/<주제>.md` | 외부 독자용 레퍼런스·가이드 | spec-writer | `templates/reference.md` |
| `docs/dev/setup.md` | 로컬 실행 | architect | `templates/setup.md` |
| `docs/dev/conventions.md` | 코드 규칙 | architect | `templates/conventions.md` |
| `_tasks/<run>/tasks.json` | 원장 | 리더 (ledger.py) | 없음 |
| `_tasks/<run>/notes.md` | 결정·가정·질문·발견·비판 처리 기록 | 리더 | `templates/notes.md` |
| `_tasks/<run>/reports/<id>.md` | 보고서 (계획 → 진행 → 완료) | 산출물을 만드는 에이전트 | `templates/report.md` |
| `_tasks/<run>/reviews/<id>-r<n>.md` | 리뷰. 보안 검토는 `<id>-security-r<n>.md` | doc-reviewer, code-reviewer, security | `templates/review.md` |
| `_tasks/<run>/critique/<대상>-r<n>.md` | 비판. 대상은 문서 비평이면 그 문서를 만든 task ID, 계획 비판이면 `plan` | critic | `templates/critique.md` |
| `_tasks/unattended.json` | 무인 모드 상태 — `{"state": "on|off", "since": ..., "mandate_version": n}` | 리더 | 없음 |

**에이전트는 이 표에서 자기에게 배정된 문서만 쓴다.** 브리프가 문서 이름을 부르면 위치는 여기서 찾는다. 표에 없는 문서가 필요하면 만들지 말고 보고서의 "다음에 필요한 것"에 적는다 — 종류를 늘리는 건 리더가 사용자 확인 뒤 이 표를 고쳐서 한다.

## 이름

- kebab-case 영문. 주제 하나. `orders.md`, `wearable-sync.md`
- 같은 주제는 종류 사이에서 같은 이름을 쓴다. `prd/orders.md` → `fsd/orders/REQ-03-checkout.md` → `api/orders.md`. `orders`로 전부 찾힌다
- FSD 파일명은 `REQ-nn-<주제>.md`. REQ 번호가 PRD와 같아야 한다. 설계 문서도 같은 번호와 주제로 `design/<제품>/REQ-nn-<주제>.md`
- 인터페이스 정의는 모듈 경로가 이름. `interface/session.md`
- 쪼개야 하면 `orders-sync.md`처럼 주제-하위주제
- 결정 기록은 세 자리 번호 + 주제. `decisions/004-activity-storage.md`. 번호는 만든 순서, 재사용 안 함
- 하네스 내부 파일은 task ID·라운드가 이름. 비판 파일은 `<대상>-r<n>.md`, 계획 비판은 `plan-r<n>.md`

## 문서 정보 — 모든 `docs/` 문서 공통

`docs/` 문서에는 YAML 머리말도, 작성자·작성일·버전·검토자 표도 두지 않는다. 누가 언제 만들고 검토했는지는 git 이력과 원장(`_tasks/<run>/tasks.json`)이 안다. 문서 첫머리에는 제목과 참고 문서만 있다.

| 항목 | 내용 |
|---|---|
| 참고 문서 | 이 문서가 근거로 삼은 문서의 경로. 저장소 루트 기준 |

참고 문서가 문서 사이의 사슬이다. 어느 문서에서 시작해도 참고 문서를 거슬러 올라가면 요구사항까지 닿아야 한다. 결정 기록은 상태(제안 / 확정 / 미룸 / 대체)와 확정한 사람(사용자 / 구현 에이전트의 승격 / 자동, 위임장 조항)을 더 적는다. 문서마다 그 문서에 필요한 항목(적용 대상, 저장소, 계획 문서)은 템플릿에 있다.

변경 이력은 날짜와 변경 내용 두 열이다.

## 참조

다른 문서를 언급하면 반드시 링크를 건다. 이름만 적지 않는다.

- 경로는 이 문서의 위치 기준 상대 경로다. `[요구사항 정의서](../prd/orders.md)`
- 항목을 가리킬 때는 절 앵커까지. `[REQ-03 결제 실패 재시도](../prd/orders.md#req-03-결제-실패-재시도)`. 앵커가 잡히도록 항목은 절 제목으로 쓴다
- 참고 문서 표의 경로도 링크다
- 저장소 밖은 URL
- 결정 기록은 `[ADR-004](../decisions/004-auth-model.md)`

ID 체계: 요구 `REQ-nn`·`NFR-nn`(PRD), FSD 안의 기능 `FN-nn`, 화면 `SCR-nn`·구성 요소 `SCR-nn-Enn`·규칙 `BR-nn`·메시지 `MSG-nn`, 결정 `ADR-nnn`, 엔티티 `E-<이름>`, 보안 요건 `S-nn`, compliance `C-nn`, 테스트 `TC-nn`. 하네스 내부: 비판 `P-Cn`, finding `<task>-Fn`.

리뷰어와 critic은 링크를 따라가 대조한다. 깨진 링크(없는 파일, 없는 앵커)와 링크 없는 문서 언급은 finding이다.

## 저장소 관례가 위

저장소에 이미 문서 규칙이 있으면(`documentation/`, ADR 디렉토리, 다른 문서 정보 형식) 그것을 따르고 `notes.md`와 `docs/README.md`에 대응을 적는다. 이 표준은 관례가 없을 때의 기본값이다.

## 템플릿

템플릿은 이 스킬의 `templates/` 폴더에 문서 종류마다 하나씩 있다. 템플릿은 그 문서의 기본 틀이다. 참고 문서 표, 그 문서가 무엇을 위한 것인지 설명하는 머리글, 번호가 붙은 절, 절마다 무엇을 어떻게 쓰는지 설명하는 안내문과 작성 예로 이루어져 있다.

새 문서는 해당 템플릿을 복사해서 시작한다. 절 아래의 안내문과 작성 예는 자기 내용으로 바꿔 쓰고, 문서를 완성할 때 안내문은 지운다. 절은 지우지 않는다. 해당하는 내용이 없으면 "해당 없음"이라고 쓰고 이유를 붙인다. 비워 두면 일부러 뺀 것인지 잊은 것인지 구분할 수 없다. 이미 있는 문서를 고칠 때도 템플릿의 절 구성을 따른다.

설계 문서 끝에는 대조 표를 둔다. 이 문서가 따르는 결정 기록과, 이 문서가 받아서 풀어내는 요구사항·기능·규칙을 적는다. 아직 정하지 못한 곳은 조사로 근거를 찾아 정한다. 근거를 찾지 못한 레벨 2 항목만 `[가정]`으로 표시하고 이유를 쓴다. 레벨 1에 닿는 것은 `[결정 필요]`로 표시하고 막힌 것으로 보고해 아키텍트가 정하게 한다.

템플릿에 없는 종류의 문서가 필요하면 새로 만들지 말고 보고서의 "다음에 필요한 것"에 적는다.

## 결정 레벨 — 무엇을 어느 문서에서 누가 정하나

문서에 빈 곳이 하나도 없을 수는 없다. 대신 결정을 세 레벨로 나눠, 어느 레벨은 반드시 문서에 있어야 하고 어느 레벨은 구현에서 정해도 되는지를 정한다.

| 레벨 | 무엇 | 누가 정하나 | 어디에 적나 | 빈 곳이 있으면 |
|---|---|---|---|---|
| 1 구조 | 언어·런타임·프레임워크·저장소·인프라와 그 버전, 모듈 경계, 통신 방식, 데이터 소유권, 인증·권한 모델, 에러 형식, 외부 연동 방식, 보관·삭제 정책 | architect가 추천하고 확정한다. 유인이면 사용자가, 무인이면 critic 비평을 거쳐 리더가 확정한다 | 아키텍처 문서, 결정 기록 | 아키텍트가 조사·벤치마크 목록을 내고, 조사 결과로 대안을 비교해 추천한다. 가정으로 두지 않는다. 구현 에이전트가 정하면 범위 이탈이다 |
| 2 명세·설계 | 기능 동작, 화면과 문구, 검증 규칙, 권한 표, 상태 전이, 데이터 모델의 엔티티·필드, API 계약, 수치 한도(페이지 크기, 타임아웃, 재시도 횟수), 정보 구조·내비게이션·화면 흐름·상호작용 규칙, 색·타이포·공통 컴포넌트, 보안·규제 요건 | spec-writer, ux-designer, contract-designer, security | PRD, UX 설계, FSD, 디자인 시스템, 데이터 모델, 계약, 보안 요건, compliance | 문서를 쓰는 쪽이 조사(investigator, 조사 task)로 근거를 찾아 정하고 근거를 적는다. 근거를 찾지 못한 것만 `[가정]`으로 표시하고 이유를 쓴다. 구조에 닿는 것이면 레벨 1로 올린다. 구현 에이전트가 만나면 정하지 않고 "막힌 것"으로 올린다 |
| 3 구현 | 모듈 안의 코드 구조, 함수·변수 이름, 알고리즘(계약을 만족하는 범위 안에서), 구조 문서가 정한 스택 안에서 쓰는 보조 라이브러리, 테스트 구성 | backend-developer, frontend-developer, devops | 보고서의 "명세에 없어 내가 정한 것" | 구현 에이전트가 정하고 이유를 적는다. 문서에 없어도 된다 |

critic은 문서를 비평할 때 이 표로 누락을 잡는다. 레벨 1·2가 문서에 없으면 누락이고, 레벨 3가 문서에 있으면 과잉이다. code-reviewer는 "내가 정한 것"에 레벨 1·2가 섞여 있으면 범위 이탈로 적는다.

## 종료 시 승격 — 리더가 한다

| `_tasks/`의 것 | 어디로 |
|---|---|
| 보고서의 "명세에 없어 내가 정한 것" 중 되돌리기 어려운 것 | 새 ADR (확정한 사람: 구현 에이전트의 승격, 사용자 확인 표시) |
| 같은 것 중 레벨 2에 해당하는 것 | 해당 FSD·design 문서에 근거와 함께 옮긴다 |
| 레벨 3 | 보고서에 남긴다. 문서로 올리지 않는다 |
| 리뷰의 waive | run 보고서 §알고 넘긴 것 |
| 미검증 항목 | run 보고서 §미검증 |
| 요청 밖 발견 | run 보고서 §다음에 할 것 |
| 비판 항목의 기각 이유 | run 보고서 §결정 경위 |

## 흔한 실패

| 증상 | 원인 |
|---|---|
| 다음 run이 "왜 이렇게 돼 있지" | 가정이 보고서에서 죽음. 승격 안 함 |
| 같은 주제 문서가 두 곳에 | 이름 규칙 무시 |
| critic이 "이 결정 근거가 어디?" | 참고 문서 비어 있음 |
| 구현자가 "데이터 모델에 없는 필드를 만들었다" | 대조 표 없음 |
| compliance·보안 요건이 설계 뒤에 나옴 | 보존·삭제와 시크릿 전달이 데이터 모델과 구조를 바꾼다. 먼저다 |
| 스킬마다 다른 경로·형식 | 위치와 템플릿은 여기만. 다른 스킬은 문서 위치·형식을 정하지 않는다 |
| PRD와 FSD가 한 파일, 또는 제품 전체를 담은 FSD 하나 | 문서 종류를 섞음. PRD 하나 + REQ마다 FSD 하나, FSD 안은 기능(FN)별 |
| FSD가 요구사항 목록 수준이라 구현자가 화면·문구·기본값을 정함 | FSD 템플릿 절을 비워 둠. 빈 절은 "해당 없음 — 이유" |
| REQ에 FSD가 없거나 FSD가 어느 REQ인지 모름 | PRD 추적 표와 FSD 머리의 REQ 인용이 없음 |
| FSD가 요구사항을 기능으로 나누지 않고 요구사항 문장을 그대로 상세화함 | 기능 목록(FN)을 정하지 않음. 인수 조건이 어느 FN에 걸리는지 추적 표가 없음 |
