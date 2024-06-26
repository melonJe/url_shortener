from datetime import datetime

from app.database.redis import redis_client


# URL과 카운트를 캐시에 저장하는 함수
def cache_url(short_key: str, original_url: str, expires_at: datetime.date, access_count: int = 0):
    try:
        expiry_seconds = min((expires_at - datetime.now().date()).total_seconds(), 259200)
        with redis_client.pipeline() as pipe:
            pipe.setex(f"url:{short_key}", expiry_seconds, original_url)
            pipe.setex(f"count:{short_key}", expiry_seconds, access_count)
            pipe.setex(f"short:{original_url}", expiry_seconds, short_key)
            pipe.execute()
    except Exception as e:
        print(f"An error occurred while caching URL: {e}")


# 캐시에서 URL을 가져오는 함수
def fetch_url_from_cache(short_key: str) -> str | None:
    try:
        return redis_client.get(f"url:{short_key}")
    except Exception as e:
        print(f"An error occurred while fetching URL from cache: {e}")
    return None


# 캐시에서 카운트를 가져오는 함수
def fetch_count_from_cache(short_key: str) -> int | None:
    try:
        return redis_client.get(f"count:{short_key}")
    except Exception as e:
        print(f"An error occurred while fetching count from cache: {e}")
    return None
