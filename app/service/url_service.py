from datetime import datetime, timedelta

from sqlalchemy import F
from sqlalchemy.orm import Session

from app.database import models
from app.database.redis import redis_client
from app.utils.cache_utils import cache_url, fetch_url_from_cache, fetch_count_from_cache
from app.utils.db_utils import fetch_url_from_db, get_existing_short_key
from app.utils.utils import standardize_url, base62_encode


def create_short_url(db: Session, original_url: str, expiry_days: int = 30) -> str:
    standardized_url = standardize_url(original_url)
    existing_short_key = get_existing_short_key(db, standardized_url)
    if existing_short_key:
        return existing_short_key

    expires_at = datetime.now().date() + timedelta(days=expiry_days)
    
    # 1. URL 정보를 먼저 데이터베이스에 저장 (short_key는 임시값 또는 null로 설정)
    db_url = models.URL(
        original_url=standardized_url,
        short_key="",  # 임시 값
        expires_at=expires_at
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # 2. 생성된 ID를 Base62로 인코딩하여 단축 키 생성
    short_key = base62_encode(db_url.id)

    # 3. 생성된 단축 키를 데이터베이스에 업데이트
    db_url.short_key = short_key
    db.commit()

    cache_url(short_key, standardized_url, expires_at)
    return short_key


def get_original_url(db: Session, short_key: str) -> str | None:
    original_url = fetch_url_from_cache(short_key)
    if original_url is None:
        db_url = fetch_url_from_db(db, short_key)
        if db_url:
            cache_url(short_key, db_url.original_url, db_url.expires_at, db_url.access_count)
            original_url = db_url.original_url
    return original_url


def increment_access_count(db: Session, short_key: str):
    # 데이터베이스의 access_count를 원자적으로 업데이트하여 경합 조건을 방지합니다.
    db.query(models.URL).filter(models.URL.short_key == short_key).update(
        {models.URL.access_count: models.URL.access_count + 1},
        synchronize_session=False
    )
    db.commit()

    # Redis 캐시의 카운트도 증가시킵니다.
    try:
        redis_client.incr(f"count:{short_key}")
    except Exception as e:
        print(f"An error occurred while incrementing access count in Redis: {e}")


def get_url_access_count(db: Session, short_key: str) -> int:
    access_count = fetch_count_from_cache(short_key)
    if access_count is None:
        db_url = fetch_url_from_db(db, short_key)
        if db_url:
            access_count = db_url.access_count
            cache_url(short_key, db_url.original_url, db_url.expires_at, db_url.access_count)
    return access_count
