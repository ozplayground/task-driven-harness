# task-driven-harness

## 하네스: task 중심 실행

**목표:** 요구를 task로 쪼개 시킨 것만 만들고 산출물로 완료를 판정한다.

**트리거:** 파일을 바꾸거나 산출물(코드·문서·설정)을 만드는 요청은 규모와 무관하게 `orchestration` 스킬을 사용한다. 후속 요청("다시", "이어서", "T3만", "리뷰 반영")도 같다. 단순 질문·설명은 직접 답한다.

**리더:** 메인 세션. `orchestration` 스킬로 요청을 분석하고, task로 나눠 계획을 세우고, 각 task를 서브에이전트에 분배하고, 산출물로 완료를 판정한다. 산출물은 직접 만들지 않는다.

**에이전트 5종:** executor, reviewer, investigator, architect, critic. 구조 결정은 architect의 추천과 사용자의 확정으로, 계획 검증은 critic으로 간다. 문서의 위치·이름·골격은 `design-docs` 스킬 한 곳에만 있다.

**하네스 자체를 고치는 요청**(`.claude/` 아래 파일, 이 문서)은 `orchestration`으로 돌리지 않는다. 직접 고치고 `CHANGELOG.md`에 적는다. 실행 중인 run이 있으면 하네스 수정은 그 run이 끝난 뒤에 한다.
