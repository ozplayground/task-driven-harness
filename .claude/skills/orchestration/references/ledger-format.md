# 원장 형식 — tasks.json

`scripts/ledger.py`로만 읽고 쓴다. 아래는 필드의 의미다.

```json
{
  "run": "order-page",
  "request": "주문 조회 화면과 API",
  "created": "2026-09-14 23:10",
  "status": "planning | approved | running | done | blocked",
  "given": ["docs/order-fsd.md"],
  "wanted": ["주문 조회 화면", "주문 API"],
  "gaps": [
    {"id": "G1", "kind": "decision | artifact | contract", "item": "기술 스택", "resolution": "user: Next.js + Fastify"}
  ],
  "tasks": [
    {
      "id": "T2",
      "title": "주문 API",
      "kind": "code | doc | research",
      "paths": ["src/api/orders/**", "tests/api/orders.*"],
      "depends_on": ["T1"],
      "acceptance": ["T1 규격대로 GET/POST /orders 동작", "tests/api/orders.test.ts 통과"],
      "status": "pending | ready | running | review | rework | done | failed | blocked",
      "round": 1,
      "attempts": 2,
      "findings": [
        {"id": "T2-F1", "severity": "blocker | major | minor", "text": "...", "round": 0, "status": "open | resolved | waived"}
      ],
      "report": "_tasks/order-page/reports/T2.md"
    }
  ],
  "log": [{"at": "2026-09-14 23:12", "event": "T2 running→review", "because": "reports/T2.md 도착"}]
}
```

`kind: research`인 task는 run이 `planning`이어도 `ready`가 된다.

`log`의 `because`가 리더의 호출 근거다. "어느 보고의 어느 줄 때문에".

## 상태 의미

| task 상태 | 뜻 | 누가 바꾸나 |
|---|---|---|
| `pending` | 의존이 아직 안 풀림 | `ready` 명령이 자동으로 |
| `ready` | 지금 던질 수 있음 | `ready` 명령 |
| `running` | 실행자가 돌고 있음 | 리더, 던진 직후 |
| `review` | 실행자 보고 도착, 판정 중 | 리더 |
| `rework` | needs-fix, 재실행 대기 | 리더. round가 1 오른다 |
| `done` | 리뷰어 confirmed. 미해소 blocker 없음 | 리더 |
| `failed` | 실행자 실패·중단 | 리더. 1회 재투입 가능 |
| `blocked` | 사용자 판단 필요 | 리더 |

`given`·`wanted`·`gaps`는 `init` 뒤 리더가 `python3 - <<EOF`로 한 번 채워도 된다. 이 세 필드는 전이 규칙이 없다. `tasks`와 `status`는 반드시 스크립트 명령으로만 바꾼다.

## run 디렉토리의 나머지

notes는 덧붙이기만 하고 항목마다 날짜와 출처(사용자 / 리더 / T2 실행자 / critic P-C1)를 적는다. 비판 항목의 반영/기각/사용자 판정도 여기에.

run이 끝나도 지우지 않는다. 다음 요청이 "저번 것 이어서"일 때는 run 보고서를 먼저 읽고, 원장은 그 다음이다.
