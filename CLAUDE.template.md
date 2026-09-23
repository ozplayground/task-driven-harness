# 하네스: task 중심 실행

**목표:** 요구를 task로 쪼개 시킨 것만 만들고 산출물로 완료를 판정한다.

**트리거:** 파일을 바꾸거나 산출물(코드·문서·설정)을 만드는 요청은 규모와 무관하게 `orchestration` 스킬을 사용한다. 후속 요청("다시", "이어서", "T3만", "리뷰 반영")도 같다. 단순 질문·설명은 직접 답한다.

**리더:** 메인 세션. `orchestration` 스킬로 요청을 분석하고, task로 나눠 계획을 세우고, 각 task를 그 task의 에이전트에 분배하고, 산출물로 완료를 판정하고, 비평·리뷰·재작업 task를 만들어 잇는다. 산출물은 직접 만들지 않는다. run을 시작하고 끝낼 때 `git-workflow`를, 무인 모드일 때 `unattended`를, 끝에 남은 버그를 모아 처리할 때 `bugfix-followup`을 쓴다.

**에이전트:** task 종류 하나에 에이전트 하나. 만드는 쪽은 researcher, architect, spec-writer, ux-designer, contract-designer, security, backend-developer, frontend-developer, devops, verifier. 판정하는 쪽은 critic(문서 비평·계획 비판), doc-reviewer(문서 리뷰), code-reviewer(코드 리뷰), security(보안 검토). investigator는 누구나 부르는 읽기 전용 조사자. 구조 결정은 architect의 추천과 사용자의 확정으로 간다. 문서가 나올 때마다 critic이 내용을 비평하고 doc-reviewer가 기준을 판정한다. 문서의 위치·이름·템플릿은 `design-docs` 스킬 한 곳에만 있다. 리더가 `docs/` 문서(run 보고서, 문서 지도)를 쓸 때는 `humanizer`를 따른다.
