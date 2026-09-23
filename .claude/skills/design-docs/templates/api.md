# 주제 API 계약 v1

| 항목 | 내용 |
|---|---|
| 이 계약을 쓰는 쪽 | 제공하는 모듈 / 부르는 모듈 |
| 참고 문서 | 이 문서가 근거로 삼은 문서. 링크로 적는다. `[요구사항 정의서](../prd/orders.md)` |

이 문서는 두 모듈이 주고받는 것을 정한다. 양쪽이 이 문서만 보고 따로 구현할 수 있어야 한다. 요청과 응답은 실제 값이 들어간 예시로 쓰고, 예시만 있고 필드 정의가 없는 응답이 없어야 한다. 없는 것은 없다고 적는다. 계약을 바꾸면 버전을 올리고 영향을 받는 곳을 적는다.

각 절 아래의 설명은 무엇을 어떻게 쓰는지에 대한 안내다. 문서를 완성할 때 지운다.

## 1. 공통 사항

모든 엔드포인트에 같이 적용되는 것을 적는다. 기본 경로, 필드 이름 표기, 날짜와 시간 형식, 인증 방식, 페이지네이션 형태, 에러 응답 형식, 멱등성 처리. 해당 없는 항목은 "없음"이라고 쓴다.

작성 예:

> - 기본 경로: `/api/v1`
> - 필드 표기: camelCase
> - 날짜·시간: ISO 8601, UTC. 예 `2026-09-20T03:00:00Z`
> - 인증: `Authorization: Bearer <JWT>`. 없으면 401
> - 페이지네이션: `?page=1&size=20`, 응답은 `{ items, total, page, size }`. size 최대 100
> - 에러 형식: `{ "error": { "code": "ORDER_NOT_FOUND", "message": "...", "details": {} } }`
> - 멱등성: 생성 요청은 `Idempotency-Key` 헤더. 같은 키로 24시간 안에 다시 오면 처음 응답을 돌려준다

## 2. 에러 코드

이 계약에서 쓰는 에러 코드를 모두 적는다. 코드마다 HTTP 상태, 언제 나오는지, `details`에 무엇이 들어가는지.

작성 예:

| 코드 | HTTP | 언제 | details |
|---|---|---|---|
| VALIDATION_FAILED | 422 | 입력 검증 실패 | 필드별 오류 목록 `[{ field, code, message }]` |
| ORDER_NOT_FOUND | 404 | 없는 주문 id | 없음 |
| PAYMENT_ALREADY_PENDING | 409 | 이미 결제 대기 중인 주문에 재시도 요청 | 없음 |

## 3. 엔드포인트

엔드포인트마다 아래 항목을 쓴다. 목적, 권한, 요청(경로·쿼리·본문 필드와 타입·필수 여부·제약), 검증 규칙, 응답(상태 코드별 예시와 필드 정의), 낼 수 있는 에러 코드.

### 3.1 GET /orders — 주문 목록

- 목적: 조건에 맞는 주문 목록을 돌려준다.
- 권한: 관리자, 담당자, 조회

요청 (쿼리):

| 필드 | 타입 | 필수 | 제약 |
|---|---|---|---|
| status | string | 아니오 | `created`, `payment_pending`, `paid`, `payment_failed` 중 하나 |
| from, to | date | 아니오 | 둘 다 있으면 from ≤ to, 최대 90일 |
| ordererName | string | 아니오 | 50자 이하, 부분 일치 |
| page, size | int | 아니오 | 1절 참조 |

응답 200:

```json
{
  "items": [
    { "id": "ord_1042", "ordererName": "김주문", "amount": 32000,
      "status": "payment_failed", "failedAt": "2026-09-20T03:00:00Z" }
  ],
  "total": 1, "page": 1, "size": 20
}
```

| 필드 | 타입 | 항상 있음 | 설명 |
|---|---|---|---|
| items[].id | string | 예 | 주문 id |
| items[].amount | int | 예 | 원 단위 |
| items[].failedAt | datetime | 아니오 | status가 payment_failed일 때만 |

에러: VALIDATION_FAILED

### 3.2 POST /orders/{id}/payment-retry — 결제 재시도 요청

- 목적: 결제 실패 주문을 결제 대기로 되돌리고 재시도 작업을 등록한다.
- 권한: 관리자, 담당자
- 요청 본문: 없음. `Idempotency-Key` 헤더 필수
- 검증: 주문 상태가 payment_failed여야 한다

응답 202:

```json
{ "id": "ord_1042", "status": "payment_pending" }
```

에러: ORDER_NOT_FOUND, PAYMENT_ALREADY_PENDING

## 4. 대조 표

이 계약이 받아내는 기능 명세의 기능과 규칙을 적는다. 어느 엔드포인트가 어느 FN·BR을 구현하는지 보이면 된다.

작성 예:

| 기능 명세 | 엔드포인트 |
|---|---|
| REQ-02 FN-01 결제 실패 목록 | GET /orders?status=payment_failed |
| REQ-02 FN-02 재시도 요청, BR-03 | POST /orders/{id}/payment-retry |

## 5. 변경 이력

| 날짜 | 변경 내용 | 영향 받는 곳 |
|---|---|---|
| | 처음 작성 | |
