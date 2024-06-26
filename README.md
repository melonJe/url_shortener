# URL Shortener Service

URL Shortener Service는 긴 URL을 단축된 URL로 변환하여 관리하는 서비스입니다.

URL 단축 서비스의 목적은 동일한 웹페이지로 이동하는 다양한 형태의 URL을 표준화하여 동일한 단축 URL을 반환하는 것입니다. 이를 위해서는 URL의 파라미터와 프래그먼트를 제거하고 경로가 없을 경우 기본 경로를 설정하여 short url을 제공합니다.

## 기능

- URL 단축
- 원본 URL로 리디렉션
- URL 만료 기능
- URL 접근 통계 제공

## 데이터베이스 선택 이유

이 서비스는 PostgreSQL에 데이터를 저장하고 Redis를 이용하여 캐싱 합니다.

유저 수와 저장된 URL이 증가하면 높은 읽기 빈도가 예상되므로, 빠른 응답을 위해 Redis를 PostgreSQL과 함께 사용하여 더 나은 성능과 확장성을 확보하고자 합니다.

### PostgreSQL

- **확장성**: PostgreSQL은 대용량 데이터를 효율적으로 처리할 수 있으며, 수평 및 수직 확장이 가능합니다.

### Redis

- **고성능**: 메모리 기반 데이터 저장소로 매우 빠른 읽기/쓰기 성능을 제공합니다.
- **TTL(Time-To-Live) 지원**: 각 키에 대해 TTL을 설정할 수 있어 자동으로 만료되는 데이터를 관리하기에 적합합니다.

## 설치 및 실행 방법

### 1. 환경 설정

프로젝트를 시작하기 전에 환경 변수를 설정해야 합니다. 프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASS=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 2. 종속성 설치

프로젝트의 종속성을 설치합니다. 다음 명령을 실행하세요:

```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 설정

#### PostgreSQL

PostgreSQL를 설치하고, 데이터베이스 정보를 `.env` 파일에 업데이트합니다.

다음 sql을 통해 테이블을 생성합니다.(```init.sql```파일)

```sql
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    original_url VARCHAR NOT NULL,
    short_key VARCHAR UNIQUE NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE,
    expires_at DATE DEFAULT CURRENT_DATE + INTERVAL '30 days',
    access_count INTEGER DEFAULT 0
);

CREATE INDEX idx_urls_id ON urls (id);
CREATE INDEX idx_urls_short_key ON urls (short_key);
```

#### Redis

Redis를 설치하고, 데이터베이스 정보를 `.env` 파일에 업데이트합니다.

### 4. 서버 실행

다음 명령을 실행하여 FastAPI 서버를 시작합니다:

```bash
uvicorn app.main:app --reload --port 8000
```

서버가 실행되면 [http://localhost:8000](http://localhost:8000)에서 API에 접근할 수 있습니다.

### 5. 스케줄러 시작

애플리케이션이 시작되면 스케줄러가 자동으로 시작됩니다. 스케줄러는 만료된 URL을 삭제하고, Redis의 접근 카운트를 PostgreSQL에 동기화합니다.

## 환경 변수

애플리케이션 설정은 환경 변수를 통해 관리됩니다. `.env` 파일을 사용하여 환경 변수를 설정하고, `dotenv` 패키지를 사용하여 애플리케이션 시작 시 환경 변수를 로드합니다.

## 주의사항

`.env` 파일에는 민감한 정보(예: 데이터베이스 비밀번호)가 포함될 수 있으므로, 이 파일을 버전 관리 시스템(git 등)에 포함시키지 마세요.

## API 문서

FastAPI는 자동으로 API 문서를 생성합니다. 서버가 실행 중일 때 다음 URL에서 문서에 접근할 수 있습니다:

- [http://localhost:8000/docs](http://localhost:8000/docs) - Swagger UI
- [http://localhost:8000/redoc](http://localhost:8000/redoc) - ReDoc

## 주요 파일 및 디렉토리 구조

```
app/
├── database/
│   ├── dtos.py
│   ├── models.py
│   ├── postgres.py
│   ├── redis.py
├── service/
│   ├── url_service.py
├── utils/
│   ├── cache_utils.py
│   ├── db_utils.py
│   ├── utils.py
├── main.py
├── url_scheduler.py
test/
├── test_main.py
├── test_url_service.py
init.sql
README.md
requirements.txt
setting_env.py
```

### 주요 파일 설명

- `main.py`: FastAPI 애플리케이션의 엔트리 포인트입니다. API 엔드포인트와 서버 시작 로직을 포함합니다.
- `url_service.py`: URL 단축 및 조회 로직을 처리하는 서비스 레이어입니다.
- `url_scheduler.py`: 주기적인 작업을 처리하는 스케줄러입니다. 만료된 URL을 삭제하고, Redis의 접근 카운트를 PostgreSQL에 동기화합니다.
- `models.py`: SQLAlchemy 모델을 정의합니다.
- `postgres.py`: PostgreSQL 데이터베이스 설정을 포함합니다.
- `redis.py`: Redis 설정을 포함합니다.
- `setting_env.py`: 환경 변수를 설정합니다.

## 추가 설정

### app/main.py

```
response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
response.headers["Pragma"] = "no-cache"
```

브라우저에서 중복으로 `short_url`을 이용할 경우, 브라우저에 캐싱된 정보로 인해 서버를 거치지 않아 `count` 값이 증가하지 않습니다. 이를 해결하기 위해 브라우저나 캐시 서버가 응답을 캐시하지 않도록 지시합니다.

해당 기능이 필요하다면 주석을 해제하십시오.