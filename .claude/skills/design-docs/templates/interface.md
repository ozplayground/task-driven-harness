# 세션 모듈 인터페이스

| 항목 | 내용 |
|---|---|
| 참고 문서 | [세션 설계](../design/agentsdk/REQ-02-session.md), [아키텍처](../design/architecture.md) |

이 문서는 라이브러리나 SDK가 밖으로 내놓는 인터페이스를 정의한다. 모듈 하나에 문서 하나다. 공개 클래스·함수·타입의 이름과 시그니처, 한 줄 목적, 인자·반환·예외의 타입까지만 적는다. 동작 설명, 내부 구조, 예시 코드, 사용 안내는 넣지 않는다. 그것은 설계 문서와 레퍼런스의 일이다. 여기 없는 것은 공개 인터페이스가 아니다.

REST API는 이 문서가 아니라 API 명세로 쓴다.

각 절 아래의 설명은 무엇을 어떻게 쓰는지에 대한 안내다. 문서를 완성할 때 지운다.

## 1. 모듈

모듈 경로와 이 모듈이 공개하는 것의 목록을 적는다. 공개 여부는 여기서 정해진다.

작성 예:

`agentsdk.session` — 세션의 생성, 실행, 종료.

| 이름 | 종류 |
|---|---|
| `Session` | 클래스 |
| `SessionConfig` | 데이터 타입 |
| `SessionState` | 열거형 |
| `open_session` | 함수 |
| `SessionClosedError` | 예외 |

## 2. 타입

데이터 타입과 열거형을 필드 단위로 적는다. 필드마다 타입과 한 줄 뜻. 기본값이 있으면 기본값.

작성 예:

`SessionConfig`

| 필드 | 타입 | 기본값 | 뜻 |
|---|---|---|---|
| `model` | `str` | 필수 | 사용할 모델 ID |
| `max_turns` | `int` | `50` | 한 세션의 최대 턴 수 |
| `tools` | `list[Tool]` | `[]` | 세션에서 쓸 수 있는 툴 |

`SessionState` — `idle`, `running`, `closed`

## 3. 클래스

클래스마다 생성 방법과 공개 메서드·속성을 적는다. 메서드마다 시그니처, 한 줄 목적, 예외. 인자 설명은 이름과 타입으로 충분하지 않을 때만 한 줄.

작성 예:

`Session`

생성: `open_session()`으로만 만든다. 직접 생성하지 않는다.

| 멤버 | 시그니처 | 목적 | 예외 |
|---|---|---|---|
| `state` | `-> SessionState` | 현재 상태 | |
| `send` | `async (message: str) -> Turn` | 메시지를 보내고 한 턴을 돈다 | `SessionClosedError` 닫힌 세션 |
| `close` | `async () -> None` | 세션을 닫고 자원을 놓는다. 두 번 불러도 된다 | |

## 4. 함수

모듈 수준 함수. 시그니처, 한 줄 목적, 예외.

작성 예:

| 함수 | 시그니처 | 목적 | 예외 |
|---|---|---|---|
| `open_session` | `async (config: SessionConfig) -> Session` | 설정으로 세션을 만들어 연다 | `ConfigError` 설정이 유효하지 않음 |

## 5. 예외

이 모듈이 던지는 예외와 상위 타입, 언제 나는지 한 줄.

작성 예:

| 예외 | 상위 | 언제 |
|---|---|---|
| `SessionClosedError` | `AgentSdkError` | 닫힌 세션에 `send` |
| `ConfigError` | `AgentSdkError` | `SessionConfig` 검증 실패 |

## 6. 변경 이력

| 날짜 | 변경 내용 |
|---|---|
| | 처음 작성 |
