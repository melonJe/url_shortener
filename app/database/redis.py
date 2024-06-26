import redis

from setting_env import REDIS_HOST, REDIS_PORT, REDIS_DB

try:
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    redis_client.ping()
    print("Redis connection established.")
except redis.ConnectionError as e:
    print(f"Redis connection error: {e}")
    redis_client = None
