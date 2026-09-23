---
name: orchestration
description: 리더(메인 세션)가 사용자의 요청을 분석하고, task로 나눠 계획을 세우고, 서브에이전트에 분배하고, 산출물로 완료를 판정하는 절차. 코드 구현("~만들어줘", "~구현해줘", "~고쳐줘", "~추가해줘", "최적화해줘"), 문서 작성("PRD 써줘", "FSD/기능명세 작성", "요구사항 정리", "API 스펙"), 조사·비교("조사해줘", "벤치마크해줘", "비교해줘"), 구조 결정("아키텍처 정하자", "스택 정해줘", "설계해줘"), 문서를 주고 개발을 시키는 요청("이 FSD로 프론트 만들어줘"), 그리고 후속 요청("다시 실행", "T3만 다시", "이어서 진행", "리뷰 반영해서 수정", "지금 원장 상태", "어디까지 됐어", "실패한 task 뭐야")에 반드시 이 스킬을 사용한다. 파일을 바꾸거나 산출물을 만드는 요청이면 규모와 무관하게 적용한다. 단순 질문·설명 요청과, .claude/ 아래 하네스 자체(스킬·에이전트·CLAUDE.md)를 고치는 요청은 제외한다.
---

# orchestration — 분석하고, 계획하고, 분배하고, 판정한다

이 스킬은 리더(메인 세션)가 쓴다. 리더는 사용자의 요청을 받아 **분석**하고, task로 나눠 **계획**을 세우고, 각 task를 서브에이전트에 **분배**하고, 보고와 산출물로 **완료를 판정**한다. 산출물을 직접 만들지는 않는다.

- **단위는 task다.** 만드는 것도, 비평하는 것도, 리뷰하는 것도, 재작업도 task다. 순서는 task 간 의존이다. 고정된 단계는 없다.
- **task와 task를 잇는 것은 리더다.** 어느 산출물에 비평과 리뷰를 붙일지, 지적이 나오면 재작업을 만들지, 무엇에 의존을 걸지는 리더가 원장에서 정한다. 원장은 기록하고 검사만 한다. 자동으로 생기는 task는 없다.
- **끝까지 간다.** 모르는 것은 조사·벤치마크로 알아내고, 비어 있는 결정은 아키텍트가 채우고, 막히면 원인을 고쳐 다시 돌린다. 도중에 멈춰서 사용자에게 넘기는 것은 완성이 아니다.
- **시킨 것만 한다.** 범위를 넓히는 결정은 사용자에게 돌아간다.
- **완료는 보고가 아니라 산출물로 판정한다.**
- **문서는 비평을 받는다.** 문서가 나올 때마다 critic이 내용을 비평하고 doc-reviewer가 기준을 판정한다. 둘 다 통과해야 그 문서로 다음 일을 한다.
- **계획은 검증을 받는다.** 구현 투입 전에 critic이 계획을 비판하고, 사용자가 승인한다.
- **판단은 기록한다.** 계획·호출의 근거를 원장 log에 `--because`로 남긴다.

## 실행 모드

`Agent` 도구로 서브에이전트를 던지고 결과를 받는 **팬아웃** 방식이다. 리더가 단계를 정하고, 그 단계에서 ready인 task를 한 번에 던지고, 결과를 받아 다음 단계를 던진다. 팀 구성이나 팀원 간 통신은 쓰지 않는다. 서브에이전트는 investigator만 부르고, investigator는 아무도 부르지 않는다.

task의 `agent`가 곧 호출할 서브에이전트다. 에이전트마다 자기 방법론 스킬을 갖고 시작하므로 브리프는 스킬을 지정하지 않는다.

| 에이전트 | task | 쓰는 곳 |
|---|---|---|
| `researcher` | 조사·벤치마크 | `docs/research/` |
| `architect` | 아키텍처, 결정 기록, FSD마다 설계 문서, 로컬 실행·코드 규칙. 실행 중 구조 상담 | `docs/design/architecture.md`, `docs/design/<제품>/`, `docs/decisions/`, `docs/dev/` |
| `spec-writer` | PRD, FSD, 용어집, 레퍼런스 | `docs/prd/`, `docs/fsd/`, `docs/glossary.md`, `docs/reference/` |
| `ux-designer` | UX 설계, 디자인 시스템 | `docs/design/ux.md`, `docs/design/design-system.md` |
| `contract-designer` | API 명세, 인터페이스 정의, 데이터 모델. 설계 문서에서 도출 | `docs/api/`, `docs/interface/`, `docs/design/data-model.md` |
| `security` | compliance·보안 요건 문서. 보안 검토 | `docs/compliance/`, `docs/design/security.md`. 검토는 리뷰 파일 |
| `backend-developer` | 서버 코드·테스트 | 소유 경로 |
| `frontend-developer` | 화면 코드·테스트 | 소유 경로 |
| `devops` | CI·CD·배포 설정, 배포·모니터링·런북 문서 | 소유 경로, `docs/ops/` |
| `verifier` | 테스트 계획·케이스, 통합 검증·테스트 실행 보고, e2e | `docs/qa/`, 소유 경로 |
| `critic` | 문서 비평, 계획 비판 | 비판 파일 |
| `doc-reviewer` | 문서가 완료 기준을 채웠는지 판정 | 리뷰 파일 |
| `code-reviewer` | 코드가 완료 기준을 채웠는지 판정 | 리뷰 파일 |
| `investigator` | 질문 하나에 근거 있는 답. task가 아니다 | 없음 |

재작업 task의 `agent`는 원래 task와 같다. 리더는 원장·notes·run 보고서를 쓴다.

모든 `Agent` 호출은 `run_in_background: true`로 던지고 알림을 받는다. 같은 에이전트를 여러 번 호출하면 독립 인스턴스가 뜬다. 동시에 도는 서브에이전트는 **5개까지**다. 의존이 풀린 것 중 5개를 던지고, 하나가 끝나면 다음을 던진다. 생성이 거부되면 그 task는 `ready`에 남겨 다음 순환에서 다시 던진다.

## 상태는 파일에 둔다

진행 상태를 대화 컨텍스트에 두지 않는다. 원장 조작은 전부 `scripts/ledger.py`로 한다.

```bash
L=.claude/skills/orchestration/scripts/ledger.py
python3 $L init <run> --request "..."
python3 $L add <run> T1 --agent contract-designer --title "..." --paths "docs/api/orders.md" --accept "기준" --because "요구 wanted 2"
python3 $L add <run> T1-C1 --agent critic --title "T1 비평" --paths "_tasks/<run>/critique/T1-r1.md" --accept "비평 파일, 결론" --target T1
python3 $L add <run> T1-R1 --agent doc-reviewer --title "T1 리뷰" --paths "_tasks/<run>/reviews/T1-r1.md" --accept "verdict" --target T1
python3 $L add <run> T1-W1 --agent contract-designer --title "T1 재작업" --paths "docs/api/orders.md" --accept "T1 기준 + F1 해소" --target T1 --fixes T1-F1 --depends T1-R1
python3 $L validate <run>     # 의존 사이클, 동시 실행 가능 task 간 경로 겹침, target·fixes 정합
python3 $L approve <run>      # 승인 뒤에만. 승인 전에는 researcher·architect·critic·doc-reviewer task만 ready가 된다
python3 $L ready <run>        # 지금 던질 수 있는 task
python3 $L brief <run> T1     # 브리프에 옮길 필드와 의존 task의 경로
python3 $L set <run> T1 running|done|failed|ready --because "..."
python3 $L finding <run> T1 add T1-F1 blocker "내용"    # 산출물을 만든 task에 기록한다
python3 $L show <run> [--paths]
```

`--because`가 판단의 근거다. `<run>`은 요청을 나타내는 짧은 kebab-case slug다.

## 흐름

### 0. 컨텍스트 확인

- 미완료 run이 있고 요청이 그 연장이면 **재개**한다. `ledger.py show`로 상태를 읽고 4단계부터 이어간다.
- 사용자가 특정 task를 지목하면("T3만 다시") 그 task에 재작업 task를 만들어 돌린다.
- 새 요청이면 새 run이다. 이전 run의 run 보고서가 있으면 먼저 읽는다. `git-workflow`대로 `develop`에서 `feature/<run>` 브랜치를 만든다.

### 1. 분석 — 받은 것과 요구

요청에서 **받은 것(given)**과 **요구(wanted)**를 분리한다. 받은 문서가 있으면 `references/intake.md`의 절차로 적재한다. 길면 investigator에게 위임한다. 빠진 것을 채우지 않고 목록으로 올린다.

결손은 세 종류다. **결정**(레벨 1)은 아키텍트에게 보낸다. 아키텍트가 조사 목록을 내고, 조사 결과로 대안을 비교해 추천하며, 유인이면 사용자가 확정하고 무인이면 critic 비평을 거쳐 리더가 확정한다. 유인이면 요구 자체(무엇을 만들지, 범위)가 모호할 때만 사용자에게 묻는다. 무인이면 그것도 묻지 않고 비슷한 제품을 조사·벤치마크해 요구를 정의하고 PRD에 근거를 적는다. 어떻게 만들지는 어느 모드에서도 사용자에게 묻지 않는다. **계약**(둘 이상의 task가 참조하는 것)은 선행 task로 만든다. **중간 산출물**은 필요하면 선행 task로 두고 사용자에게 보인다.

run 보고서 템플릿으로 §요구를 만든다.

### 2. 계획 — task 분할

**직접 모드인가.** task 하나로 닫히고, 새 결정이 없고, 손대는 파일이 서너 개 이하. 판정 기준은 "쪼갤 것이 없는가"다. 직접 모드면 원장 없이 해당 에이전트 하나를 던지고, 리뷰어를 한 번 던지고, 증거 수준을 확인하고 끝낸다.

**보안·규제 대상인가.** 개인정보·결제·인증 정보를 다루거나, 외부 서비스를 호출하거나, 시크릿을 보관하거나, 스토어·심사 대상이면 `security` task(요건 문서)를 아키텍트 결정 초안 앞에 둔다.

**구조 결정이 필요한가.** 새 프로젝트, 새 하위 시스템, 새 외부 연동, 되돌리기 어려운 결정이 걸려 있거나 기존 구조 문서가 요구를 덮지 못하면 필요하다. 그러면 분할 전에 `architect`를 부른다(브리프는 `references/dispatch.md`). 아키텍트가 조사 목록을 내면 `researcher` task로 등록하고 승인 없이 투입한다. 조사가 전부 done이면 같은 아키텍트 인스턴스에 `SendMessage`로 조사 결과 경로를 주고 결정 초안을 받는다. 초안이 나오면 그 문서에 **critic 비평 task와 doc-reviewer 리뷰 task**를 만들어 던진다. critic 항목은 같은 아키텍트가 반박하거나 고치고, 이의가 없어질 때까지 반복한다(왕복 2회, 그 뒤는 조사 task를 추가해 근거를 만든다). 비평을 통과하지 못한 구조 문서로 task를 나누지 않는다.

**task로 나눈다.** wanted 각각이 어느 task에서 만들어지는지, 계약 결손은 어느 선행 task가 채우는지, 아키텍트의 후속 필수 설계는 어느 task인지 정한다. 규칙은 `references/split.md`. 각 task를 `--agent`와 `--because`와 함께 원장에 등록하고 `validate`한다. 이 시점의 원장에는 산출물 task만 있다. 비평·리뷰·재작업 task는 산출물이 나올 때 리더가 만든다.

### 3. 비판과 승인

산출물 task가 등록되면 투입 전에 **계획 비판 critic task**(`--target` 없이, 대상 "계획")를 만들어 던진다. 항목은 갈라서 처리한다. 형식·덮음·분할·완료 기준 문제는 리더가 계획을 고치고, 구조 결정에 관한 것은 아키텍트에게 ID를 넘겨 반박 또는 수정을 받고, 근거가 부족한 것은 조사 task를 추가한다. 요구 자체가 모호한 것은 유인이면 사용자에게, 무인이면 조사로 정한다. blocker가 있었으면 critic round 2. 왕복 2회.

그 다음 사용자에게 올린다. task 표(`split.md` 승인 형식) + 되돌리기 어려운 결정마다 대안·추천 + 비판 요약. 사용자가 결정을 고르고 표를 승인하면 `ledger.py approve`. "그냥 해"도 승인이다. 무인이면 critic 무이의를 확인하고 리더가 approve하며, 확정한 결정을 자동 결정 목록에 적는다.

### 4. 분배

**구현은 문서가 끝난 뒤에 시작한다.** 구현 task의 입력 문서(구조, 결정 기록, PRD, FSD, UX, 설계, 계약, 보안 요건)는 모두 리뷰 task가 done이고 open finding이 없어야 투입한다. 아닌 문서가 있으면 그 문서의 비평·리뷰·재작업부터 한다.

```
반복:
  ready = ledger.py ready <run>
  ready가 비고 미완료가 남아 있으면 → failed마다 원인(빈 결정, 틀린 문서, 환경 부재)을 찾아 그것을 고치는 task를 추가하고 다시 순환
  ready 중 최대 5개를 던진다. 동시에 도는 서브에이전트는 5개를 넘기지 않는다. 하나가 끝나면 그 자리에 다음 ready를 던진다. task의 agent가 subagent_type이다 (브리프는 references/dispatch.md, 내용은 ledger.py brief)
  산출물 task는 워크트리와 브랜치 feature/<run>/<task>를 만들어 준다. 재작업은 대상 task의 워크트리를 그대로 (git-workflow)
  각 task를 running으로 (--because)
  결과 알림을 기다린다 (폴링하지 않는다)
```

생성이 거부되면 `ready`로 되돌리고 다음 순환에서 다시 던진다.

### 5. 완료 판정과 잇기

보고가 오면 리더가 **직접** 확인한다. 보고문을 믿지 않는다. 보고서는 전체를 읽지 않고 "완료 기준", "막힌 것", "다음에 필요한 것" 절만 연다.

1. 보고서가 있고 완료 보고 형식을 따르는가. "다음에 필요한 것"이 비어 있으면 되묻는다
2. 변경된 파일이 소유 경로 안에 있는가(3-dot diff). 밖에 있으면 되돌리지 말고 finding으로 기록한다
3. 완료 기준마다 증거 수준이 있는가. "미검증"은 미완이다

확인이 끝나면 task를 `done`으로 옮기고 **다음 task를 만들어 잇는다.**

| 끝난 task | 리더가 만드는 task |
|---|---|
| 문서 산출물 | `critic` 비평 task + `doc-reviewer` 리뷰 task. 둘 다 `--target`. 같이 던진다. 보안·규제 대상 문서(아키텍처, 계약, 데이터 모델)면 `security` 검토 task도 |
| 코드 산출물 | `code-reviewer` 리뷰 task. 인증·시크릿·외부 호출·개인정보를 다루는 코드면 `security` 검토 task도 |
| 비평·리뷰 task (지적 있음) | 대상 task와 같은 에이전트의 재작업 task. `--target`, `--fixes`에 blocker·major ID. 재작업 뒤 리뷰 task를 round 2로 다시 |
| 비평 무이의 + 리뷰 confirmed | 산출물 브랜치를 `feature/<run>`에 머지(`git-workflow`). 이 산출물을 입력으로 쓰는 task는 이 리뷰 task에 의존을 걸어 둔다 |
| 계획 비판 | 3단계 |

리뷰 task의 finding은 대상 task에 `finding add`로 기록한다. 판정은 `confirmed` / `needs-fix` / `inconclusive` 셋뿐이다. 실행자, 리뷰어, critic은 서로 다른 인스턴스다.

### 6. 재작업 루프

재작업은 대상 task당 **2회**까지. 2회 뒤에도 needs-fix면 같은 재작업을 반복하지 않고 리더가 원인을 찾는다. 같은 지적이 두 번 왕복하면 상위 결정이 비어 있는 것이다. 그 결정을 채우는 문서(레벨 1이면 아키텍트, 레벨 2면 명세·설계 에이전트)에 재작업 task를 만들고 비평·리뷰를 거친 뒤 원래 재작업을 다시 시작한다. 기준이 모호하면 기준을 고친다. 사용자에게 올리지 않는다. 끝까지 해소되지 않은 것은 run 보고서 "문제가 있는 것"에 적는다.

round 2 리뷰는 round 1 리뷰어 인스턴스를 `SendMessage`로 재개한다. 이전 finding과 읽은 문서를 갖고 있어 해소 여부만 본다. 재작업도 원래 인스턴스를 재개한다.

### 7. 범위 확장과 "입력 없음"

- **같이 고친 버그** → 관련성 판정이 타당한지만 본다
- **요청 밖 발견** → task로 만들지 않는다. notes에 모은다
- **명세에 없어 내가 정한 것** → 레벨 3면 notes에, 레벨 1·2가 섞여 있으면 범위 이탈 finding

**"막힌 것: 입력 없음"** — 계약·설계·구조 문서가 없어 시작하지 못했다고 하면, 그 입력을 만드는 task를 추가하고 의존을 건다. 구조에 닿으면 아키텍트에게 `SendMessage`로 상담한다. 요구 범위 안이면 추가하고 notes에 적는다. 범위 밖이면 유인은 사용자에게 한 줄 확인, 무인은 질문 큐.

### 8. 종료

모든 task가 `done`이면 run 보고서를 완성하고 사용자에게 보고한다. 요구 대비 결과, 가정, 요청 밖 발견, 미검증. **승격**: 실행 쪽이 정한 것 중 레벨 1은 결정 기록으로(범위 이탈이었음을 적는다), 레벨 2는 해당 문서에 근거와 함께, 레벨 3은 보고서에 남긴다. 그 다음 `git-workflow`대로 run 보고서를 커밋하고 전체 테스트를 돌린 뒤 `feature/<run>`을 푸시하고 `develop`으로 PR을 만들어 머지하고 워크트리와 브랜치를 정리한다. 배포와 외부 전송은 하지 않고 명령을 보고서에 적어 둔다.

## 리더의 판단과 근거

| 판단 | 근거 |
|---|---|
| 직접 모드인가 | task 하나, 새 결정 없음, 파일 서너 개 |
| security를 먼저 부르나 | 개인정보·결제·인증·외부 호출·시크릿·심사 대상 |
| 아키텍트를 부르나 | 되돌리기 어려운 구조 결정이 걸려 있거나 기존 구조 문서가 요구를 덮지 못할 때 |
| task 분할 | `split.md`. wanted·결손·후속 필수 설계 각각이 어느 task인지 |
| 어느 에이전트인가 | 산출물 종류. 위 표 |
| 비평·리뷰·재작업을 만드나 | 5단계 표. 만들지 말지와 몇 번 돌릴지는 리더가 정하되, 문서는 비평과 리뷰 둘 다 |
| 사용자에게 올리나 | 유인: 요구 자체가 모호할 때, 범위 밖, 배포·외부 전송. 무인: 위임장 범위 밖과 배포·외부 전송뿐. 재작업이 막히거나 검증이 안 되는 것은 어느 모드에서도 리더가 원인을 고쳐 다시 돌린다 |
| 완료 | 보고 파일 + 경로 대조 + 증거 수준 + 리뷰 confirmed (+ 문서면 critic 무이의) |

**무인 모드.** "사용자에게 올리나" 지점마다 `unattended`의 대체 규칙을 쓴다. 결정이 비어 있으면 조사로 근거를 만들고 아키텍트가 추천하고 critic이 비평한 뒤 리더가 확정한다. 요구가 모호하면 비슷한 제품을 조사해 요구를 정의한다. 끝나면 무엇을 왜 정했는지 run 보고서로 전달한다.

리더가 하지 않는 것: 산출물 만들기, 구조·스택·규약 결정, 보고문만으로 완료 판정, 스킬 지정.

## 에러 핸들링

| 상황 | 처리 |
|---|---|
| 에이전트 실패·중단 | 산출물은 되돌리지 않는다. `failed`로 두고 1회 재투입. 재실패면 원인을 본다. 브리프가 틀렸으면 고쳐서, 입력 문서가 비었으면 그 문서에 재작업 task를, 환경 문제면 환경을 만드는 task를 먼저 |
| 소유 경로 밖 변경 | finding으로 기록하고 되돌리지 않는다. 완료 기준에 필요했던 것이면 소유 경로를 넓혀 원장에 적고, 아니면 그 경로를 소유한 task의 재작업으로 |
| 리뷰 `inconclusive` | 리더가 확인 가능하면 하고, 환경이 없으면 환경을 만드는 task를 추가한다. 그것도 안 되면 미검증으로 run 보고서에 |
| verifier가 결함을 보고 | 결함이 있는 경로를 소유한 task에 재작업 task. finding은 그 task에 기록 |
| 실행 중 구조 질문 | 아키텍트에게 `SendMessage` 상담. 결정 기록 추가가 필요하면 아키텍트 추천 → critic 비평 → 확정 |
| 생성 거부·과부하 | `ready`로 되돌리고 다음 순환 |
| 사용량 한도로 다중 동시 실패 | 아래 "중단과 재개" |
| 실행 중 사용자가 요구를 바꿈 | 영향받는 task를 `pending`으로 되돌리고 재계획·재승인 |
| 컨텍스트 압축 | 원장과 notes를 다시 읽고 4단계부터 재개 |

## 중단과 재개

**중단이 감지되면** 되돌리지 않는다. 해당 task를 `failed`로 옮기고 사유를 notes에 적는다. 아래 세 경로를 순서대로.

1. **죽은 에이전트를 재개한다 (기본).** `SendMessage`에 그 에이전트의 id를 준다. 원래 브리프를 다시 쓰지 않는다. 중단 사유 해소, 중단 직전 마지막 보고 문장, 이어서 할 일, 그 사이 환경이 바뀐 것만 적는다(`dispatch.md`의 재개 메시지).
2. **기록으로 상태를 복원한다.** investigator에게 그 에이전트의 기록(`~/.claude/projects/<slug>/<session>/subagents/agent-<id>.jsonl`)을 읽힌다.
3. **새 인스턴스로 다시 던진다 (마지막 수단).** 브리프에 리더가 직접 확인한 상태를 전부 적는다(`dispatch.md`의 재개 브리프).

## 참고 파일

- `references/intake.md` — 받은 문서 적재와 결손 보고
- `references/split.md` — task 분할 규칙과 승인 요청 형식
- `references/dispatch.md` — 브리프 형식
- `references/ledger-format.md` — 원장 필드 정의
