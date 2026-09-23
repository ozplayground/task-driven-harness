# 로컬 실행

| 항목 | 내용 |
|---|---|
| 확인한 환경 | 예: macOS 15 arm64 |
| 참고 문서 | 이 문서가 근거로 삼은 문서. 링크로 적는다. `[요구사항 정의서](../prd/orders.md)` |

이 문서는 처음 온 사람이 저장소를 받아 로컬에서 시스템을 띄우고 테스트를 돌리기까지의 절차다. 이 문서만 보고 따라 하면 떠야 한다. 버전은 아키텍처 문서의 스택 표와 같아야 하고, 시크릿 값은 적지 않는다.

각 절 아래의 설명은 무엇을 어떻게 쓰는지에 대한 안내다. 문서를 완성할 때 지운다.

## 1. 필요한 것

미리 설치돼 있어야 하는 도구와 버전을 적는다. 버전은 아키텍처 문서와 같은 값이고, 확인한 버전을 적는다.

작성 예:

| 항목 | 버전 | 근거 |
|---|---|---|
| Python | 3.13 이상 | 아키텍처 스택 표, ADR-006 |
| uv | 0.11 이상 | 서버 의존성 관리 |
| Node.js | 24 LTS | 아키텍처 스택 표 |
| Docker | Compose v2 | PostgreSQL 컨테이너용 |

## 2. 처음 한 번

저장소를 받은 뒤 딱 한 번 하는 일을 순서대로 명령 단위로 적는다. 설정 파일 만들기, 의존성 설치, DB 스키마 적용, 첫 계정 만들기.

작성 예:

```sh
# 1. PostgreSQL을 띄운다 (127.0.0.1:55432)
docker compose up -d --wait

# 2. 서버 의존성
cd server && uv sync

# 3. 접속 정보 파일. 값은 환경변수에 두지 않고 파일 경로만 넘긴다
mkdir -p ~/.config/orders && chmod 700 ~/.config/orders
(umask 077; echo "postgresql://orders:orders@127.0.0.1:55432/orders" > ~/.config/orders/database.url)
export ORDERS_DATABASE_URL_FILE=~/.config/orders/database.url

# 4. 스키마
uv run alembic upgrade head

# 5. 첫 관리자. 비밀번호는 프롬프트로 받는다
uv run python -m orders.cli init --email admin@example.com

# 6. 웹 의존성
cd ../web && npm ci
```

## 3. 실행

실행 단위마다 기동 명령, 필요한 설정, 떴는지 확인하는 방법을 적는다. 기동 순서도 적는다.

작성 예:

| 실행 단위 | 명령 (server/ 또는 web/에서) | 필요한 설정 | 확인 |
|---|---|---|---|
| api | `uv run uvicorn orders.api.main:app --port 8000` | `ORDERS_DATABASE_URL_FILE` | `curl localhost:8000/api/v1/health` → 200 |
| worker | `uv run python -m orders.worker` | 같음 | 로그에 "worker started" |
| web | `ORDERS_API_URL=http://localhost:8000 npm run dev` | `ORDERS_API_URL` | 브라우저에서 `localhost:3000/login` |

기동 순서: PostgreSQL → api → worker → web. 조회 화면은 api만 있으면 되고, 결제 재시도는 worker가 있어야 처리된다.

## 4. 설정 목록

환경변수와 설정 파일을 모두 적는다. 이름, 누가 쓰는지, 값의 형식, 기본값. 시크릿은 값 대신 파일 위치와 권한을 적는다.

작성 예:

| 이름 | 쓰는 곳 | 값 | 기본값 |
|---|---|---|---|
| `ORDERS_DATABASE_URL_FILE` | api, worker, alembic | 접속 URL이 든 0600 파일 경로 | 없음, 필수 |
| `ORDERS_API_URL` | web | api 주소 | `http://localhost:8000` |
| `ORDERS_PG_PORT` | docker compose | PostgreSQL 호스트 포트 | 55432 |

## 5. 테스트

테스트를 돌리는 명령과 전제를 적는다.

작성 예:

```sh
# PostgreSQL이 떠 있어야 한다
cd server && uv run pytest -q
cd web && npm test
```

## 6. 자주 막히는 곳

처음 띄울 때 흔히 막히는 지점과 해결 방법을 적는다. 없으면 이 절을 비워 둔다.

작성 예:

> 8000 포트가 이미 쓰이고 있으면 `--port 8100`으로 띄우고 `ORDERS_API_URL`도 같이 바꾼다.

## 7. 변경 이력

| 날짜 | 변경 내용 |
|---|---|
| | 처음 작성 |
