# 문서 지도

이 문서는 `docs/` 아래에 어떤 문서가 있고 무엇을 위한 것인지 보여 준다. 새 문서가 생기면 리더가 이 표를 고친다. 저장소에 원래 있던 문서 규칙이 있으면 그 대응도 적는다.

각 절 아래의 설명은 무엇을 어떻게 쓰는지에 대한 안내다. 문서를 완성할 때 지운다.

## 1. 문서 목록

문서 종류 순서대로 적는다.

작성 예:

| 문서 | 경로 |
|---|---|
| 요구사항 정의서 | `docs/prd/orders.md` |
| 기능 명세서 REQ-01 주문 조회 | `docs/fsd/orders/REQ-01-order-search.md` |
| 기능 명세서 REQ-02 결제 실패 처리 | `docs/fsd/orders/REQ-02-payment-retry.md` |
| 아키텍처 | `docs/design/architecture.md` |
| 결정 기록 | `docs/decisions/` (001~008) |
| 데이터 모델 | `docs/design/data-model.md` |
| API 계약 | `docs/api/orders.md` |
| 테스트 계획 | `docs/qa/test-plan.md` |
| 로컬 실행 | `docs/dev/setup.md` |

## 2. 저장소 관례와의 대응

저장소에 이미 있던 문서 위치나 이름 규칙이 있으면, 이 표준의 어느 문서에 해당하는지 적는다. 없으면 "없음"이라고 쓴다.

작성 예:

| 저장소 관례 | 이 표준의 문서 |
|---|---|
| `doc/adr/` | `docs/decisions/` 대신 그대로 쓴다. 번호 체계도 기존 것을 따른다 |

## 3. 변경 이력

| 날짜 | 변경 내용 |
|---|---|
| | 처음 작성 |
