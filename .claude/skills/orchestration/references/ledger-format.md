# 원장 형식 — tasks.json

`scripts/ledger.py`로만 읽고 쓴다. 아래는 필드의 의미다.

```json
{
  "run": "order-page",
  "request": "주문 조회 화면과 API",
  "created": "2026-09-14 23:10",
  "status": "planning | approved | running | done",
  "given": ["docs/order-fsd.md"],
  "wanted": ["주문 조회 화면", "주문 API"],
  "gaps": [
    {"id": "G1", "kind": "decision | artifact | contract", "item": "기술 스택", "resolution": "user: Next.js + Fastify"}
  ],
  "tasks": [
    {
      "id": "T2",
      "title": "주문 API",
      "agent": "backend-developer",
      "paths": ["src/api/orders/**", "tests/api/orders.*"],
      "depends_on": ["T1-R1"],
      "acceptance": ["T1 규격대로 GET/POST /orders 동작", "tests/api/orders.test.ts 통과"],
      "status": "pending | ready | running | done | failed",
      "round": 0,
      "attempts": 1,
      "findings": [
        {"id": "T2-F1", "severity": "blocker | major | minor", "text": "...", "status": "open | resolved | waived"}
      ],
      "report": "_tasks/order-page/reports/T2.md"
    },
    {
      "id": "T2-R1",
      "title": "T2 코드 리뷰",
      "agent": "code-reviewer",
      "target": "T2",
      "round": 1,
      "paths": ["_tasks/order-page/reviews/T2-r1.md"],
      "depends_on": ["T2"],
      "acceptance": ["verdict 하나, finding마다 재현"],
      "status": "pending"
    },
    {
      "id": "T2-W1",
      "title": "T2 재작업",
      "agent": "backend-developer",
      "target": "T2",
      "fixes": ["T2-F1"],
      "round": 1,
      "paths": ["src/api/orders/**", "tests/api/orders.*"],
      "depends_on": ["T2-R1", "T2"],
      "acceptance": ["T2 완료 기준 전부", "T2-F1 해소"],
      "status": "pending"
    }
  ],
  "log": [{"at": "2026-09-14 23:12", "event": "T2 running→done", "because": "reports/T2.md 완료 기준 표 확인"}]
}
```

## 필드

| 필드 | 뜻 |
|---|---|
| `agent` | 이 task를 맡는 에이전트. 리더는 이 이름으로 `Agent`를 부른다 |
| `target` | 비평·리뷰·보안 검토·재작업이 대상으로 삼는 task. `add`가 `depends_on`에 자동으로 넣는다 |
| `fixes` | 재작업이 고칠 finding ID. 대상 task에 기록된 것이어야 하고, 전부 resolved 또는 waived여야 done이 된다 |
| `round` | 같은 대상에 같은 에이전트의 몇 번째 task인지. `add`가 센다. 산출물 task는 0 |
| `findings` | 산출물을 만든 task에 기록한다. 리뷰 task가 아니라 대상 task에 |
| `attempts` | running으로 옮긴 횟수 |

`ledger.py brief <id>`가 브리프에 옮길 필드(완료 기준, 경로, 의존 task의 산출물·보고서 경로, 대상 task의 open finding, 워크트리 경로)를 JSON으로 뽑는다.

## 상태

| task 상태 | 뜻 | 누가 바꾸나 |
|---|---|---|
| `pending` | 의존이 아직 안 풀림 | `ready` 명령이 자동으로 |
| `ready` | 지금 던질 수 있음 | `ready` 명령 |
| `running` | 에이전트가 돌고 있음 | 리더, 던진 직후 |
| `done` | 리더가 산출물을 확인함. 리뷰 통과는 리뷰 task의 done이 말한다 | 리더 |
| `failed` | 실패·중단. `ready`로 되돌려 재투입 | 리더 |

리뷰·비평·재작업은 상태가 아니라 task다. 어느 산출물이 리뷰를 통과했는지는 그 산출물을 대상으로 한 리뷰 task가 done이고 open finding이 없는 것으로 안다. 뒤 task는 그 리뷰 task에 의존을 건다.

run이 `planning`일 때 `ready`가 되는 것은 researcher, architect, critic, doc-reviewer task뿐이다.

`given`·`wanted`·`gaps`는 `init` 뒤 리더가 한 번 채워도 된다. `tasks`와 `status`는 반드시 스크립트 명령으로만 바꾼다.

## run 디렉토리의 나머지

notes는 덧붙이기만 하고 항목마다 날짜와 출처(사용자 / 리더 / T2 / critic P-C1)를 적는다. run이 끝나도 지우지 않는다.
