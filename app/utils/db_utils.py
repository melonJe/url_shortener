from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from app.database import models
from app.database.redis import redis_client
from app.utils.utils import standardize_url


def fetch_url_from_db(db: Session, short_key: str) -> models.URL | None:
    try:
        return db.query(models.URL).filter(models.URL.short_key == short_key).first()
    except Exception as e:
        print(f"An error occurred while fetching URL from database: {e}")
    return None



def get_existing_short_key(db: Session, original_url: str) -> str | None:
    try:
        standardized_url = standardize_url(original_url)
        cached_short_key = redis_client.get(f"short:{standardized_url}")
        if cached_short_key:
            return cached_short_key
        db_url = db.query(models.URL).filter(models.URL.original_url == standardized_url).first()
        if db_url:
            return db_url.short_key
    except Exception as e:
        print(f"An error occurred while getting existing short key: {e}")
    return None
