from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database import models
from app.database.redis import redis_client
from app.utils.cache_utils import cache_url, fetch_url_from_cache, fetch_count_from_cache
from app.utils.db_utils import fetch_url_from_db, is_duplicate_short_key, get_existing_short_key
from app.utils.utils import standardize_url, generate_short_key


def create_short_url(db: Session, original_url: str, expiry_days: int = 30) -> str:
    standardized_url = standardize_url(original_url)
    short_key = get_existing_short_key(db, standardized_url)
    if short_key:
        return short_key

    for _ in range(5):
        short_key = generate_short_key(standardized_url)
        if not is_duplicate_short_key(db, short_key):
            break
    else:
        raise ValueError("Failed to generate unique short key")

    expires_at = datetime.now().date() + timedelta(days=expiry_days)
    db_url = models.URL(
        original_url=standardized_url,
        short_key=short_key,
        expires_at=expires_at
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

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


def increment_access_count(short_key: str):
    try:
        redis_client.incr(f"count:{short_key}")
    except Exception as e:
        print(f"An error occurred while incrementing access count: {e}")


def get_url_access_count(db: Session, short_key: str) -> int:
    access_count = fetch_count_from_cache(short_key)
    if access_count is None:
        db_url = fetch_url_from_db(db, short_key)
        if db_url:
            access_count = db_url.access_count
            cache_url(short_key, db_url.original_url, db_url.expires_at, db_url.access_count)
    return access_count
